# src/database/aggregate_port_traffic.py
from collections import defaultdict
from datetime import datetime, timezone
from mongo_connection import get_mongo_connection
import settings
from time_utils import floor_to_6h, parse_mongo_ts

def aggregate_new_arrivals(db):
    calls = db[settings.COLL_PORT_CALLS]
    traffic = db[settings.COLL_PORT_TRAFFIC]

    cursor = calls.find({"aggregated_window": None}, projection={
        "_id": 1, "port_name": 1, "entry_ts": 1
    })

    # buckets[port_name][window_iso] = count
    buckets = defaultdict(lambda: defaultdict(int))
    ids_to_mark = []

    for doc in cursor:
        port_name = doc["port_name"]
        entry_ts = parse_mongo_ts(doc["entry_ts"])
        window_dt = floor_to_6h(entry_ts)
        window_iso = window_dt.isoformat().replace("+00:00", "Z")

        buckets[port_name][window_iso] += 1
        ids_to_mark.append((doc["_id"], window_dt))

    # upsert arrivals per bucket
    for port_name, windows in buckets.items():
        for window_iso, arrivals in windows.items():
            window_dt = datetime.fromisoformat(window_iso.replace("Z", "+00:00"))
            traffic.update_one(
                {"port_name": port_name, "window_start": window_dt},
                {
                    "$set": {"port_name": port_name, "window_start": window_dt},  # Ensure these fields are always set
                    "$inc": {"arrivals": arrivals}  # Increment arrivals only if the field exists
                },
                upsert=True
            )

    # mark visits as aggregated
    for _id, window_dt in ids_to_mark:
        calls.update_one({"_id": _id}, {"$set": {"aggregated_window": window_dt}})

    print(f"Aggregated {len(ids_to_mark)} visit(s) into port_traffic.")

def main():
    db = get_mongo_connection()
    aggregate_new_arrivals(db)

if __name__ == "__main__":
    main()
