# src/database/visit_state_updater_liverpool_areas.py

import re
from datetime import timedelta
from src.database.mongo_connection import get_mongo_connection
from src.database import settings
from src.database.time_utils import now_utc, parse_mongo_ts, minutes_between

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "unknown-area"

def _get_area_name(area_doc) -> str:
    props = area_doc.get("properties") or {}
    return props.get("name") or str(area_doc.get("_id"))

def _deterministic_area_call_id(mmsi: int, area_name: str, entry_ts) -> str:
    slug = _slug(area_name)
    et = parse_mongo_ts(entry_ts).isoformat().replace("+00:00", "Z")
    return f"ac_{mmsi}_{slug}_{et}"

def _is_liverpool_area_feature(doc) -> bool:
    props = doc.get("properties", {})
    area  = (props.get("area") or "").lower()
    ptype = (props.get("type") or "").lower()

    # allow common variants: “Steel Terminal”, “Ferry Terminal”, “Storage Facility”, etc.
    is_liverpool_area = area in {
        "liverpool dock estate",
        "birkenhead dock estate",
        "west bank lower tranmere",
    }
    is_supported_type = any(
        key in ptype
        for key in ("dock", "terminal", "facility", "facilities", "lock")
    )
    return is_liverpool_area and is_supported_type


def _area_for_point(db, lon: float, lat: float):
    point = {"type": "Point", "coordinates": [lon, lat]}
    cursor = db[settings.COLL_PORT_AREAS].find(
        {"geometry": {"$geoIntersects": {"$geometry": point}}},
        projection={"_id": 1, "properties": 1}
    )
    for doc in cursor:
        if _is_liverpool_area_feature(doc):
            # print("Found Liverpool area for point")
            return doc
    return None

def _finalize_area_visit(db, state_doc, exit_ts, last_coord):
    entry_ts = parse_mongo_ts(state_doc["entered_at"])
    duration_min = max(0, minutes_between(entry_ts, exit_ts))
    call_id = _deterministic_area_call_id(state_doc["mmsi"], state_doc["area_name"], entry_ts)

    call_doc = {
        "_id": call_id,
        "mmsi": state_doc["mmsi"],
        "area_name": state_doc["area_name"],
        "entry_ts": entry_ts,
        "exit_ts": exit_ts,
        "duration_min": duration_min,
        "entry_method": "geo+status",
        "first_coord": state_doc.get("first_coord"),
        "last_coord": last_coord,
        "aggregated_window": None,
    }

    db["area_calls"].replace_one({"_id": call_id}, call_doc, upsert=True)
    db["visit_state_areas"].delete_one({"_id": state_doc["_id"]})

# -----------------------------------------------------------------------------
# Main visit logic (state management)
# -----------------------------------------------------------------------------

def _update_area_state_inside(db, pos_doc, area_name: str):
    mmsi = pos_doc["mmsi"]
    ts = parse_mongo_ts(pos_doc.get("timestamp_utc") or now_utc())
    coord = pos_doc.get("coordinates", {})
    sog = pos_doc.get("sog")
    nav_status = pos_doc.get("nav_status")

    state_coll = db["visit_state_areas"]
    state = state_coll.find_one({"mmsi": mmsi})

    slow_bonus = 1 if (sog is not None and sog < settings.SLOW_SOG_KNOTS) else 0
    status_bonus = 1 if (nav_status == settings.NAV_STATUS_IN_PORT) else 0
    add_hits = 1 + slow_bonus + status_bonus

    if state is None:
        state_coll.insert_one({
            "mmsi": mmsi,
            "area_name": area_name,
            "entered_at": ts,
            "last_seen_ts": ts,
            "last_coord": coord,
            "first_coord": coord,
            "in_area": False,
            "inside_hits": add_hits,
            "outside_hits": 0,
            "evidence": {
                "status_hits": 1 if status_bonus else 0,
                "slow_hits": 1 if slow_bonus else 0
            }
        })
        return

    if state["area_name"] != area_name:
        if state.get("in_area"):
            _finalize_area_visit(db, state, ts, coord)
        state_coll.insert_one({
            "mmsi": mmsi,
            "area_name": area_name,
            "entered_at": ts,
            "last_seen_ts": ts,
            "last_coord": coord,
            "first_coord": coord,
            "in_area": False,
            "inside_hits": add_hits,
            "outside_hits": 0,
            "evidence": {
                "status_hits": 1 if status_bonus else 0,
                "slow_hits": 1 if slow_bonus else 0
            }
        })
        return

    updates = {
        "$set": {"last_seen_ts": ts, "last_coord": coord, "outside_hits": 0},
        "$inc": {"inside_hits": add_hits},
        "$setOnInsert": {"first_coord": coord}
    }
    if not state.get("in_area") and (state.get("inside_hits", 0) + add_hits) >= settings.HITS_IN:
        updates["$set"]["in_area"] = True

    state_coll.update_one({"_id": state["_id"]}, updates)

def _update_area_state_outside(db, pos_doc):
    mmsi = pos_doc["mmsi"]
    ts = parse_mongo_ts(pos_doc.get("timestamp_utc") or now_utc())
    coord = pos_doc.get("coordinates", {})

    state_coll = db["visit_state_areas"]
    state = state_coll.find_one({"mmsi": mmsi})
    if state is None:
        return

    add_out = 1
    new_out_hits = state.get("outside_hits", 0) + add_out

    if not state.get("in_area"):
        if new_out_hits >= max(2, state.get("inside_hits", 0)):
            state_coll.delete_one({"_id": state["_id"]})
        else:
            state_coll.update_one({"_id": state["_id"]}, {
                "$set": {"last_seen_ts": ts, "last_coord": coord},
                "$inc": {"outside_hits": add_out}
            })
        return

    if new_out_hits >= settings.HITS_OUT:
        _finalize_area_visit(db, state, ts, coord)
    else:
        state_coll.update_one({"_id": state["_id"]}, {
            "$set": {"last_seen_ts": ts, "last_coord": coord},
            "$inc": {"outside_hits": add_out}
        })

# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------

def process_latest_positions_recent():
    db = get_mongo_connection()
    lp = db[settings.COLL_LATEST_POSITIONS]

    since = now_utc() - timedelta(minutes=settings.LIVE_RECENT_MINUTES)
    cursor = lp.find(
        {"timestamp_utc": {"$gte": since}},
        projection={"_id": 1, "mmsi": 1, "coordinates": 1, "timestamp_utc": 1, "sog": 1, "nav_status": 1}
    ).limit(settings.SCAN_LIMIT)

    count = 0
    for doc in cursor:
        coords = (doc.get("coordinates") or {}).get("coordinates")
        if not coords or len(coords) != 2:
            continue
        lon, lat = float(coords[0]), float(coords[1])

        area_doc = _area_for_point(db, lon, lat)
        if area_doc:
            area_name = _get_area_name(area_doc)
            _update_area_state_inside(db, doc, area_name)
        else:
            _update_area_state_outside(db, doc)
        count += 1

    print(f"[liverpool areas] Processed {count} latest_positions (last {settings.LIVE_RECENT_MINUTES} min).")

def main():
    process_latest_positions_recent()

if __name__ == "__main__":
    main()
