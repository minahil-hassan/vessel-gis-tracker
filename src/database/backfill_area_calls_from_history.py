# src/database/backfill_area_calls_from_history.py

"""
One-off or scheduled backfill for Liverpool dock/terminal/facility visits.

- Streams vessel_position ordered by (mmsi, timestamp_utc)
- Matches only Liverpool sub-areas: type ∈ {Dock, Terminal, Facilities, Lock}
- Finalizes visits to area_calls
- Use aggregate_area_traffic.py to generate area_traffic buckets afterwards
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
    return s.strip("-") or "unknown-area"


def _is_liverpool_area(doc) -> bool:
    props = doc.get("properties", {})
    area = props.get("area", "").lower()
    type_field = props.get("type", "").lower()

    # Check if the area is one of the Liverpool dock estates
    is_liverpool_area = area in {
        "liverpool dock estate",
        "birkenhead dock estate",
        "west bank lower tranmere"
    }

    # Check if the type contains the word "terminal" or matches other valid types
    is_valid_type = "terminal" in type_field or type_field in {
        "dock", "facilities", "lock"
    }

    return is_liverpool_area and is_valid_type


def _area_for_point(db, lon: float, lat: float):
    point = {"type": "Point", "coordinates": [lon, lat]}
    cursor = db[settings.COLL_PORT_AREAS].find(
        {"geometry": {"$geoIntersects": {"$geometry": point}}},
        projection={"_id": 1, "properties": 1}
    )
    for doc in cursor:
        if _is_liverpool_area(doc):
            return doc
    return None


def _get_area_name(area_doc) -> str:
    props = area_doc.get("properties") or {}
    return props.get("name") or str(area_doc.get("_id"))


def _deterministic_area_call_id(mmsi: int, area_name: str, entry_ts) -> str:
    slug = _slug(area_name)
    et = parse_mongo_ts(entry_ts).isoformat().replace("+00:00", "Z")
    return f"ac_{mmsi}_{slug}_{et}"


def _finalize_area_visit(db, state, exit_ts, last_coord):
    entry_ts = parse_mongo_ts(state["entered_at"])
    duration_min = max(0, minutes_between(entry_ts, exit_ts))
    call_id = _deterministic_area_call_id(state["mmsi"], state["area_name"], entry_ts)
    doc = {
        "_id": call_id,
        "mmsi": state["mmsi"],
        "area_name": state["area_name"],
        "entry_ts": entry_ts,
        "exit_ts": exit_ts,
        "duration_min": duration_min,
        "entry_method": "geo+status",
        "first_coord": state.get("first_coord"),
        "last_coord": last_coord,
        "aggregated_window": None
    }
    db["area_calls"].replace_one({"_id": call_id}, doc, upsert=True)


def backfill_area_calls():
    db = get_mongo_connection()
    coll = db[settings.COLL_VESSEL_POSITION]

    cursor = coll.find(
        {},
        projection={"_id": 0, "mmsi": 1, "coordinates": 1, "timestamp_utc": 1, "sog": 1, "nav_status": 1}
    ).sort([("mmsi", 1), ("timestamp_utc", 1)])

    state = {}
    processed = 0

    for doc in cursor:
        mmsi = doc.get("mmsi")
        coords = (doc.get("coordinates") or {}).get("coordinates")
        if mmsi is None or not coords or len(coords) != 2:
            continue

        lon, lat = float(coords[0]), float(coords[1])
        ts = parse_mongo_ts(doc.get("timestamp_utc") or now_utc())
        sog = doc.get("sog")
        nav_status = doc.get("nav_status")

        area_doc = _area_for_point(db, lon, lat)
        inside_area_name = _get_area_name(area_doc) if area_doc else None

        s = state.get(mmsi)
        if s is None:
            state[mmsi] = {
                "mmsi": mmsi,
                "area_name": inside_area_name,
                "entered_at": ts if inside_area_name else None,
                "last_seen_ts": ts,
                "first_coord": {"type": "Point", "coordinates": [lon, lat]} if inside_area_name else None,
                "last_coord": {"type": "Point", "coordinates": [lon, lat]},
                "in_area": bool(inside_area_name),
                "inside_hits": 1 if inside_area_name else 0,
                "outside_hits": 0,
                "evidence": {
                    "status_hits": 1 if nav_status == settings.NAV_STATUS_IN_PORT else 0,
                    "slow_hits": 1 if (sog is not None and sog < settings.SLOW_SOG_KNOTS) else 0
                }
            }
            processed += 1
            continue

        # Update live state
        s["last_seen_ts"] = ts
        s["last_coord"] = {"type": "Point", "coordinates": [lon, lat]}

        if inside_area_name:
            slow_bonus = 1 if (sog is not None and sog < settings.SLOW_SOG_KNOTS) else 0
            status_bonus = 1 if (nav_status == settings.NAV_STATUS_IN_PORT) else 0
            add_hits = 1 + slow_bonus + status_bonus

            if s["area_name"] is None:
                s["area_name"] = inside_area_name
                s["entered_at"] = ts
                s["first_coord"] = {"type": "Point", "coordinates": [lon, lat]}
                s["inside_hits"] = add_hits
                s["outside_hits"] = 0
                s["in_area"] = s["inside_hits"] >= settings.HITS_IN

            elif s["area_name"] != inside_area_name:
                if s["in_area"]:
                    _finalize_area_visit(db, s, ts, s["last_coord"])
                s["area_name"] = inside_area_name
                s["entered_at"] = ts
                s["first_coord"] = {"type": "Point", "coordinates": [lon, lat]}
                s["inside_hits"] = add_hits
                s["outside_hits"] = 0
                s["in_area"] = s["inside_hits"] >= settings.HITS_IN
            else:
                s["inside_hits"] += add_hits
                s["outside_hits"] = 0
                if not s["in_area"] and s["inside_hits"] >= settings.HITS_IN:
                    s["in_area"] = True

        else:
            s["outside_hits"] += 1
            if not s["in_area"]:
                if s["outside_hits"] >= max(2, s["inside_hits"]):
                    s["area_name"] = None
                    s["entered_at"] = None
                    s["first_coord"] = None
                    s["inside_hits"] = 0
                    s["outside_hits"] = 0
            else:
                if s["outside_hits"] >= settings.HITS_OUT and s["entered_at"] is not None:
                    _finalize_area_visit(db, s, ts, s["last_coord"])
                    s["area_name"] = None
                    s["entered_at"] = None
                    s["first_coord"] = None
                    s["in_area"] = False
                    s["inside_hits"] = 0
                    s["outside_hits"] = 0

        processed += 1
        if processed % settings.HISTORY_BATCH_SIZE == 0:
            print(f"[area_backfill] Processed {processed} records...")

    print(f"[area_backfill] Done. Total processed: {processed}")


if __name__ == "__main__":
    backfill_area_calls()
