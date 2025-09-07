# src/database/visit_state_updater.py

import re
from datetime import timedelta
from src.database.mongo_connection import get_mongo_connection
from src.database import settings
from src.database.time_utils import now_utc, parse_mongo_ts, minutes_between


def _slug(s: str) -> str:
    """
    Create a URL/file-safe, deterministic slug from a string.

    Used to build deterministic call IDs that are stable across re-runs.
    """
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)  # replace non-alnum with hyphens
    return s.strip("-") or "unknown-port"


def _port_for_point(db, lon: float, lat: float):
    """
    Find the port polygon (from port_areas) that contains the given lon/lat.

    Uses a $geoIntersects query against a 2dsphere-indexed 'geometry' field.
    Returns one matching port feature document (or None if outside all ports).
    """
    point = {"type": "Point", "coordinates": [lon, lat]}
    return db[settings.COLL_PORT_AREAS].find_one(
    {
        "geometry": {"$geoIntersects": {"$geometry": point}},
        "properties.type": "Port"  # filter to only UK ports (including Port of Liverpool)
    },
    projection={"_id": 1, "properties.name": 1}
)



def _get_port_name(port_doc) -> str:
    """
    Extract a human-friendly port name from a port feature document.

    Falls back to the document _id if 'properties.name' is missing.
    """
    props = port_doc.get("properties") or {}
    return props.get("name") or str(port_doc.get("_id"))


def _deterministic_call_id(mmsi: int, port_name: str, entry_ts) -> str:
    """
    Build a deterministic _id for a port call document:

      'pc_{mmsi}_{slug(port_name)}_{entry_ts_isoZ}'

    Determinism guarantees idempotent writes when reprocessing data.
    """
    slug = _slug(port_name)
    et = parse_mongo_ts(entry_ts).isoformat().replace("+00:00", "Z")
    return f"pc_{mmsi}_{slug}_{et}"


def _finalize_visit(db, state_doc, exit_ts, last_coord):
    """
    Finalize a visit stored in 'visit_state' and upsert it into 'port_calls'.

    - Computes duration from 'entered_at' to provided 'exit_ts'
    - Uses deterministic _id to ensure exactly-once semantics
    - Deletes the per-MMSI state document after finalizing
    """
    entry_ts = parse_mongo_ts(state_doc["entered_at"])
    duration_min = max(0, minutes_between(entry_ts, exit_ts))
    call_id = _deterministic_call_id(state_doc["mmsi"], state_doc["port_name"], entry_ts)

    call_doc = {
        "_id": call_id,
        "mmsi": state_doc["mmsi"],
        "port_name": state_doc["port_name"],
        "entry_ts": entry_ts,
        "exit_ts": exit_ts,
        "duration_min": duration_min,
        "entry_method": "geo+status",          # provenance of detection
        "first_coord": state_doc.get("first_coord"),
        "last_coord": last_coord,
        "aggregated_window": None,             # to be filled by the aggregator job
    }

    # Upsert the call and remove the live state for this MMSI (visit complete)
    db[settings.COLL_PORT_CALLS].replace_one({"_id": call_id}, call_doc, upsert=True)
    db[settings.COLL_VISIT_STATE].delete_one({"_id": state_doc["_id"]})


def _update_state_for_inside(db, pos_doc, port_name: str):
    """
    Update (or create) the per-MMSI visit_state when a position is inside 'port_name'.

    Debouncing:
      - We accumulate 'inside_hits' with bonuses for slow SOG and 'in port' nav_status.
      - Once 'inside_hits' >= HITS_IN, we flip 'in_port=True' (confirmed inside).
    Port switching:
      - If the MMSI was previously 'in_port' at a different port, we finalize that visit
        and start a new tentative state in the new port.
    """
    mmsi = pos_doc["mmsi"]
    ts = parse_mongo_ts(pos_doc.get("timestamp_utc") or now_utc())
    coord = pos_doc.get("coordinates", {})
    sog = pos_doc.get("sog")
    nav_status = pos_doc.get("nav_status")

    state_coll = db[settings.COLL_VISIT_STATE]
    state = state_coll.find_one({"mmsi": mmsi})

    # Evidence bonuses to stabilize detection (reduce edge flicker)
    slow_bonus = 1 if (sog is not None and sog < settings.SLOW_SOG_KNOTS) else 0
    status_bonus = 1 if (nav_status == settings.NAV_STATUS_IN_PORT) else 0
    add_hits = 1 + slow_bonus + status_bonus

    if state is None:
        # First time we see this MMSI inside any port: create tentative state
        state_coll.insert_one({
            "mmsi": mmsi,
            "port_name": port_name,
            "entered_at": ts,            # initial candidate entry time
            "last_seen_ts": ts,
            "last_coord": coord,
            "first_coord": coord,        # first inside coordinate
            "in_port": False,            # becomes True when inside_hits >= HITS_IN
            "inside_hits": add_hits,
            "outside_hits": 0,
            "evidence": {
                "status_hits": 1 if status_bonus else 0,
                "slow_hits": 1 if slow_bonus else 0
            }
        })
        return

    # We have an existing state for this MMSI
    if state["port_name"] != port_name:
        # Entered a different port polygon than previously tracked
        if state.get("in_port"):
            # Finalize the previous visit (confirmed in previous port)
            _finalize_visit(db, state, ts, coord)
            # Start a new tentative state in the new port
            state_coll.insert_one({
                "mmsi": mmsi,
                "port_name": port_name,
                "entered_at": ts,
                "last_seen_ts": ts,
                "last_coord": coord,
                "first_coord": coord,
                "in_port": False,
                "inside_hits": add_hits,
                "outside_hits": 0,
                "evidence": {
                    "status_hits": 1 if status_bonus else 0,
                    "slow_hits": 1 if slow_bonus else 0
                }
            })
        else:
            # We were tentative in a different port; overwrite to the new one
            state_coll.update_one({"_id": state["_id"]}, {"$set": {
                "port_name": port_name,
                "entered_at": ts,
                "last_seen_ts": ts,
                "last_coord": coord,
                "first_coord": coord,
                "inside_hits": add_hits,
                "outside_hits": 0,
                "in_port": False
            }})
        return

    # Still in the same port: accumulate inside evidence and reset outside counter
    updates = {
        "$set": {"last_seen_ts": ts, "last_coord": coord, "outside_hits": 0},
        "$inc": {"inside_hits": add_hits},
        "$setOnInsert": {"first_coord": coord}  # no-op on existing docs
    }
    # If we were tentative and now exceed the entry threshold, confirm 'in_port'
    if not state.get("in_port") and (state.get("inside_hits", 0) + add_hits) >= settings.HITS_IN:
        updates["$set"]["in_port"] = True

    state_coll.update_one({"_id": state["_id"]}, updates)


def _update_state_for_outside(db, pos_doc):
    """
    Update (or clear) the per-MMSI visit_state when a position is outside all ports.

    Debouncing:
      - If we were tentative (not 'in_port'), drop the state when outside evidence
        dominates: outside_hits >= max(2, inside_hits).
      - If we were confirmed 'in_port', finalize the visit once outside_hits >= HITS_OUT.
    """
    mmsi = pos_doc["mmsi"]
    ts = parse_mongo_ts(pos_doc.get("timestamp_utc") or now_utc())
    coord = pos_doc.get("coordinates", {})

    state_coll = db[settings.COLL_VISIT_STATE]
    state = state_coll.find_one({"mmsi": mmsi})
    if state is None:
        # Nothing to do if we don't track this MMSI yet
        return

    add_out = 1
    new_out_hits = state.get("outside_hits", 0) + add_out

    if not state.get("in_port"):
        # Tentative state: drop it if we have strong outside evidence
        if new_out_hits >= max(2, state.get("inside_hits", 0)):
            state_coll.delete_one({"_id": state["_id"]})
        else:
            # Keep accumulating outside hits (still undecided)
            state_coll.update_one({"_id": state["_id"]}, {
                "$set": {"last_seen_ts": ts, "last_coord": coord},
                "$inc": {"outside_hits": add_out}
            })
        return

    # Confirmed in_port: finalize the visit once exit threshold is met
    if new_out_hits >= settings.HITS_OUT:
        _finalize_visit(db, state, ts, coord)
    else:
        # Not enough outside evidence yet; keep tracking
        state_coll.update_one({"_id": state["_id"]}, {
            "$set": {"last_seen_ts": ts, "last_coord": coord},
            "$inc": {"outside_hits": add_out}
        })


def process_latest_positions_recent():
    """
    Live-mode driver:
      - Scans only the most recent N minutes of 'latest_positions'
      - For each record, decides 'inside' vs 'outside' relative to port polygons
      - Updates per-MMSI visit_state and finalizes visits when appropriate
    """
    db = get_mongo_connection()
    lp = db[settings.COLL_LATEST_POSITIONS]

    # Only scan a sliding recent window to keep the job fast and incremental
    since = now_utc() - timedelta(minutes=settings.LIVE_RECENT_MINUTES)
    cursor = lp.find(
        {"timestamp_utc": {"$gte": since}},
        projection={"_id": 1, "mmsi": 1, "coordinates": 1, "timestamp_utc": 1, "sog": 1, "nav_status": 1}
    ).limit(settings.SCAN_LIMIT)

    count = 0
    for doc in cursor:
        # Defensive guard against malformed or missing coordinates
        coords = (doc.get("coordinates") or {}).get("coordinates")
        if not coords or len(coords) != 2:
            continue
        lon, lat = float(coords[0]), float(coords[1])

        # Spatial test against port polygons
        port_doc = _port_for_point(db, lon, lat)
        if port_doc:
            port_name = _get_port_name(port_doc)
            _update_state_for_inside(db, doc, port_name)
        else:
            _update_state_for_outside(db, doc)
        count += 1

    print(f"[live] Processed {count} latest_positions (last {settings.LIVE_RECENT_MINUTES} min).")


def main():
    """
    Entry point for ad-hoc execution (single pass over recent positions).
    In production, run on a schedule or as a small always-on worker loop.
    """
    process_latest_positions_recent()


if __name__ == "__main__":
    main()
