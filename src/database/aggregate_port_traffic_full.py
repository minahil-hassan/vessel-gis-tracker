"""
Populate/refresh `port_traffic` from `port_calls`.

Modes:
  1) Incremental (default): process only port_calls with aggregated_window == null.
     - Safe to run on a schedule (idempotent).
     - Sets aggregated_window on processed visits.

  2) Full rebuild: set FULL_REBUILD=true (and CONFIRM_REBUILD=YES)
     - Deletes all documents from port_traffic.
     - Recomputes arrivals for ALL port_calls (by entry_ts 6h bucket).
     - Resets aggregated_window to the recomputed window for all port_calls.

Config (env):
  - FULL_REBUILD=true|false
  - CONFIRM_REBUILD=YES      # required when FULL_REBUILD=true
  - AGG_BUCKET_HOURS=6       # bucket size; we assume 6h
"""

import os
from datetime import datetime, timezone
from pymongo import UpdateOne
from mongo_connection import get_mongo_connection
import settings
from time_utils import floor_to_6h, parse_mongo_ts

FULL_REBUILD = os.getenv("FULL_REBUILD", "false").lower() == "true"
CONFIRM = os.getenv("CONFIRM_REBUILD", "").upper() == "YES"

def _supports_date_trunc(db) -> bool:
    """
    Quick feature flag: attempt to use $dateTrunc if server >= 5.0.
    We just assume True; if the pipeline errors in your environment, you can flip this to False,
    and we'll use the Python fallback.
    """
    try:
        # No-op pipeline using $dateTrunc against empty cursor to test support
        db[settings.COLL_PORT_CALLS].aggregate([
            {"$match": {"_id": "__nonexistent__"}},
            {"$addFields": {"_probe": {"$dateTrunc": {"date": "$entry_ts", "unit": "hour", "binSize": 6}}}},
            {"$limit": 1}
        ]).close()
        return True
    except Exception:
        return False

def _python_group_and_upsert(db, filter_q):
    """
    Fallback: pull matching port_calls in a streaming cursor and group in Python.
    Works on any Mongo version, but more client-side work.
    """
    calls = db[settings.COLL_PORT_CALLS]
    traffic = db[settings.COLL_PORT_TRAFFIC]

    cursor = calls.find(filter_q, projection={"_id": 1, "port_name": 1, "entry_ts": 1})
    # buckets[(port_name, window_dt)] = count
    buckets = {}
    to_mark = []  # (id, window_dt)

    for doc in cursor:
        pn = doc["port_name"]
        ent = parse_mongo_ts(doc["entry_ts"])
        win = floor_to_6h(ent)
        key = (pn, win)
        buckets[key] = buckets.get(key, 0) + 1
        to_mark.append((doc["_id"], win))

    # upsert traffic
    for (pn, win), cnt in buckets.items():
        traffic.update_one(
            {"port_name": pn, "window_start": win},
            {"$setOnInsert": {"port_name": pn, "window_start": win},
             "$inc": {"arrivals": cnt}},
            upsert=True
        )

    # set aggregated_window
    if to_mark:
        ops = [UpdateOne({"_id": _id}, {"$set": {"aggregated_window": win}}) for _id, win in to_mark]
        for i in range(0, len(ops), 1000):
            calls.bulk_write(ops[i:i+1000], ordered=False)

    print(f"[aggregate] upserted {len(buckets)} buckets; marked {len(to_mark)} calls.")

def _server_side_group_and_upsert(db, filter_q):
    """
    Preferred: use Mongo aggregation ($dateTrunc) to group server-side by 6h windows.
    Much faster for large histories. Requires MongoDB 5.0+.
    """
    calls = db[settings.COLL_PORT_CALLS]
    traffic = db[settings.COLL_PORT_TRAFFIC]

    pipeline = [
        {"$match": filter_q},
        {"$project": {
            "port_name": 1,
            "entry_ts": 1,
            "window_start": {
                "$dateTrunc": {"date": "$entry_ts", "unit": "hour", "binSize": 6}
            }
        }},
        {"$group": {
            "_id": {"port_name": "$port_name", "window_start": "$window_start"},
            "arrivals": {"$sum": 1}
        }}
    ]

    results = list(calls.aggregate(pipeline, allowDiskUse=True))
    print(f"[aggregate] pipeline produced {len(results)} buckets.")

    # upsert into port_traffic
    for r in results:
        pn = r["_id"]["port_name"]
        win = r["_id"]["window_start"]
        cnt = r["arrivals"]
        traffic.update_one(
            {"port_name": pn, "window_start": win},
            {"$setOnInsert": {"port_name": pn, "window_start": win},
             "$inc": {"arrivals": cnt}},
            upsert=True
        )

    # set aggregated_window on processed port_calls
    # For FULL_REBUILD, mark ALL matched; for incremental, only those that were null (same filter_q)
    calls.update_many(
        filter_q,
        [{"$set": {"aggregated_window": {
            "$dateTrunc": {"date": "$entry_ts", "unit": "hour", "binSize": 6}
        }}}]
    )

def rebuild_or_incremental():
    db = get_mongo_connection()

    if FULL_REBUILD:
        if not CONFIRM:
            raise RuntimeError("Refusing to rebuild: set CONFIRM_REBUILD=YES to proceed.")
        # wipe port_traffic
        deleted = db[settings.COLL_PORT_TRAFFIC].delete_many({}).deleted_count
        print(f"[rebuild] cleared port_traffic ({deleted} docs).")
        # process ALL port_calls
        filter_q = {}  # all
    else:
        # process only unaggregated port_calls
        filter_q = {"aggregated_window": None}

    # Prefer server-side aggregation if supported
    if _supports_date_trunc(db):
        _server_side_group_and_upsert(db, filter_q)
    else:
        print("[aggregate] $dateTrunc unsupported; using Python fallback.")
        _python_group_and_upsert(db, filter_q)

    print("[aggregate] done.")

def main():
    rebuild_or_incremental()

if __name__ == "__main__":
    main()
