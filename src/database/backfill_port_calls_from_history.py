# src/database/backfill_port_calls_from_history.py
"""
One-off (or occasional) script:
- Streams historical AIS from vessel_position ordered by (mmsi, timestamp_utc)
- Maintains an in-memory state per MMSI (minimal) to detect entry/exit
- Finalizes visits into port_calls
- You can run the aggregator afterwards to fill port_traffic
"""
import re
from collections import defaultdict
from datetime import datetime
from mongo_connection import get_mongo_connection
import settings
from time_utils import parse_mongo_ts, now_utc, minutes_between

def _slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "unknown-port"

def _port_for_point(db, lon: float, lat: float):
    point = {"type": "Point", "coordinates": [lon, lat]}
    return db[settings.COLL_PORT_AREAS].find_one(
        {"geometry": {"$geoIntersects": {"$geometry": point}}},
        projection={"_id": 1, "properties.name": 1}
    )

def _get_port_name(port_doc) -> str:
    props = port_doc.get("properties") or {}
    return props.get("name") or str(port_doc.get("_id"))

def _deterministic_call_id(mmsi: int, port_name: str, entry_ts) -> str:
    slug = _slug(port_name)
    et  = parse_mongo_ts(entry_ts).isoformat().replace("+00:00","Z")
    return f"pc_{mmsi}_{slug}_{et}"

def _finalize_visit(db, state, exit_ts, last_coord):
    entry_ts = parse_mongo_ts(state["entered_at"])
    duration_min = max(0, minutes_between(entry_ts, exit_ts))
    call_id = _deterministic_call_id(state["mmsi"], state["port_name"], entry_ts)
    doc = {
        "_id": call_id,
        "mmsi": state["mmsi"],
        "port_name": state["port_name"],
        "entry_ts": entry_ts,
        "exit_ts": exit_ts,
        "duration_min": duration_min,
        "entry_method": "geo+status",
        "first_coord": state.get("first_coord"),
        "last_coord": last_coord,
        "aggregated_window": None
    }
    db[settings.COLL_PORT_CALLS].replace_one({"_id": call_id}, doc, upsert=True)

def backfill():
    db = get_mongo_connection()
    coll = db[settings.COLL_VESSEL_POSITION]

    # Stream everything sorted by mmsi, timestamp_utc
    cursor = coll.find(
        {},
        projection={"_id": 0, "mmsi": 1, "coordinates": 1, "timestamp_utc": 1, "sog": 1, "nav_status": 1}
    ).sort([("mmsi", 1), ("timestamp_utc", 1)])

    # In-memory state per MMSI for the historical pass
    # state[mmsi] = { ...same shape as port_visit_state... }
    state = {}

    processed = 0
    for doc in cursor:
        mmsi = doc.get("mmsi")
        if mmsi is None:
            continue

        coords = (doc.get("coordinates") or {}).get("coordinates")
        if not coords or len(coords) != 2:
            continue
        lon, lat = float(coords[0]), float(coords[1])

        ts = parse_mongo_ts(doc.get("timestamp_utc") or now_utc())
        sog = doc.get("sog")
        nav_status = doc.get("nav_status")

        # Which port contains this point?
        port_doc = _port_for_point(db, lon, lat)
        inside_port_name = _get_port_name(port_doc) if port_doc else None

        s = state.get(mmsi)
        if s is None:
            # initialize new state for this MMSI
            state[mmsi] = {
                "mmsi": mmsi,
                "port_name": inside_port_name,
                "entered_at": ts if inside_port_name else None,
                "last_seen_ts": ts,
                "first_coord": {"type":"Point","coordinates":[lon,lat]} if inside_port_name else None,
                "last_coord": {"type":"Point","coordinates":[lon,lat]},
                "in_port": bool(inside_port_name),
                "inside_hits": 1 if inside_port_name else 0,
                "outside_hits": 0,
                "evidence": {"status_hits": 1 if nav_status == settings.NAV_STATUS_IN_PORT else 0,
                             "slow_hits": 1 if (sog is not None and sog < settings.SLOW_SOG_KNOTS) else 0}
            }
            processed += 1
            continue

        # We have an existing state for this MMSI
        s["last_seen_ts"] = ts
        s["last_coord"] = {"type":"Point","coordinates":[lon,lat]}

        if inside_port_name:
            # inside some port
            slow_bonus = 1 if (sog is not None and sog < settings.SLOW_SOG_KNOTS) else 0
            status_bonus = 1 if (nav_status == settings.NAV_STATUS_IN_PORT) else 0
            add_hits = 1 + slow_bonus + status_bonus

            if s["port_name"] is None:
                # entering a port from outside
                s["port_name"] = inside_port_name
                s["entered_at"] = ts
                s["first_coord"] = {"type":"Point","coordinates":[lon,lat]}
                s["inside_hits"] = add_hits
                s["outside_hits"] = 0
                s["in_port"] = s["inside_hits"] >= settings.HITS_IN

            elif s["port_name"] != inside_port_name:
                # switched to a different port polygon
                if s["in_port"]:
                    # finalize previous visit
                    _finalize_visit(db, s, ts, s["last_coord"])
                # start fresh in new port
                s["port_name"] = inside_port_name
                s["entered_at"] = ts
                s["first_coord"] = {"type":"Point","coordinates":[lon,lat]}
                s["inside_hits"] = add_hits
                s["outside_hits"] = 0
                s["in_port"] = s["inside_hits"] >= settings.HITS_IN
            else:
                # stayed in the same port
                s["inside_hits"] += add_hits
                s["outside_hits"] = 0
                if not s["in_port"] and s["inside_hits"] >= settings.HITS_IN:
                    s["in_port"] = True

        else:
            # outside all ports
            s["outside_hits"] += 1
            if not s["in_port"]:
                # we were tentative — drop if clearly outside longer than inside
                if s["outside_hits"] >= max(2, s["inside_hits"]):
                    # clear tentative state
                    s["port_name"] = None
                    s["entered_at"] = None
                    s["first_coord"] = None
                    s["inside_hits"] = 0
                    s["outside_hits"] = 0
            else:
                # confirmed in_port — apply exit debounce
                if s["outside_hits"] >= settings.HITS_OUT and s["entered_at"] is not None:
                    _finalize_visit(db, s, ts, s["last_coord"])
                    # reset to outside
                    s["port_name"] = None
                    s["entered_at"] = None
                    s["first_coord"] = None
                    s["in_port"] = False
                    s["inside_hits"] = 0
                    s["outside_hits"] = 0

        processed += 1
        if processed % settings.HISTORY_BATCH_SIZE == 0:
            print(f"[backfill] processed {processed} rows...")

    print(f"[backfill] done. processed {processed} rows total.")

def main():
    backfill()

if __name__ == "__main__":
    main()
