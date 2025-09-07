# src/database/aggregate_area_traffic.py

from collections import defaultdict
from datetime import datetime
from src.database.mongo_connection import get_mongo_connection
import settings
from src.database.settings import COLL_PORT_CALLS, COLL_PORT_TRAFFIC
from src.database.time_utils import floor_to_6h, parse_mongo_ts

def aggregate_new_area_arrivals(db):
    calls = db["area_calls"]
    traffic = db["area_traffic"]

    cursor = calls.find({"aggregated_window": None}, projection={
        "_id": 1, "area_name": 1, "entry_ts": 1
    })

    buckets = defaultdict(lambda: defaultdict(int))
    ids_to_mark = []

    for doc in cursor:
        area_name = doc["area_name"]
        entry_ts = parse_mongo_ts(doc["entry_ts"])
        window_dt = floor_to_6h(entry_ts)
        window_iso = window_dt.isoformat().replace("+00:00", "Z")

        buckets[area_name][window_iso] += 1
        ids_to_mark.append((doc["_id"], window_dt))

    for area_name, windows in buckets.items():
        for window_iso, arrivals in windows.items():
            window_dt = datetime.fromisoformat(window_iso.replace("Z", "+00:00"))
            traffic.update_one(
                {"area_name": area_name, "window_start": window_dt},
                {
                    "$set": {"area_name": area_name, "window_start": window_dt},  # Ensure these fields are always set
                    "$inc": {"arrivals": arrivals}  # Increment arrivals only if the field exists
                },
                upsert=True
            )

    for _id, window_dt in ids_to_mark:
        calls.update_one({"_id": _id}, {"$set": {"aggregated_window": window_dt}})

    print(f"Aggregated {len(ids_to_mark)} area visit(s) into area_traffic.")

def main():
    db = get_mongo_connection()
    aggregate_new_area_arrivals(db)

if __name__ == "__main__":
    main()
