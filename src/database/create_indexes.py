# src/database/create_indexes.py
import os
from pymongo import ASCENDING, DESCENDING, GEOSPHERE
from src.database.mongo_connection import get_mongo_connection
from src.database import settings

ALLOW_DROP = os.getenv("ALLOW_INDEX_DROP", "false").lower() == "true"

def ensure_index(coll, keys, name=None, **opts):
    """
    Create an index if needed. If an index with the same name exists but options differ:
      - drop & recreate when ALLOW_INDEX_DROP=true
      - otherwise, warn and keep the existing one
    keys must be a list of (field, direction) tuples.
    """
    existing_by_name = {ix["name"]: ix for ix in coll.list_indexes()}

    if name and name in existing_by_name:
        ix = existing_by_name[name]
        # Normalize existing key to list of tuples for comparison
        existing_key = list(ix["key"].items())
        requested_key = list(keys)

        same_key = existing_key == requested_key
        same_unique = ix.get("unique", False) == opts.get("unique", False)
        same_sparse = ix.get("sparse", False) == opts.get("sparse", False)

        if same_key and same_unique and same_sparse:
            print(f"[OK] {coll.name}.{name} already compatible. Skipping.")
            return name

        msg = (f"[WARN] {coll.name}.{name} exists with different options. "
               f"existing={{key:{existing_key}, unique:{ix.get('unique', False)}, sparse:{ix.get('sparse', False)}}} "
               f"requested={{key:{requested_key}, unique:{opts.get('unique', False)}, sparse:{opts.get('sparse', False)}}}")
        if ALLOW_DROP:
            print(msg + " Dropping & recreating (ALLOW_INDEX_DROP=true).")
            coll.drop_index(name)
        else:
            print(msg + " Leaving existing index unchanged. Set ALLOW_INDEX_DROP=true to recreate.")
            return name

    created = coll.create_index(keys, name=name, **opts)
    print(f"[CREATE] {coll.name}.{created}")
    return created

def main():
    db = get_mongo_connection()

    # 2dsphere for port polygons
    ensure_index(db[settings.COLL_PORT_AREAS], [("geometry", GEOSPHERE)], name="geometry_2dsphere")

    # latest_positions
    # Use unique=True: one latest doc per MMSI
    ensure_index(db[settings.COLL_LATEST_POSITIONS], [("mmsi", ASCENDING)], name="mmsi_1", unique=True)
    ensure_index(db[settings.COLL_LATEST_POSITIONS], [("timestamp_utc", DESCENDING)], name="ts_desc")

    # vessel_position (history)
    ensure_index(db[settings.COLL_VESSEL_POSITION], [("mmsi", ASCENDING), ("timestamp_utc", ASCENDING)], name="mmsi_ts")

    # port_visit_state
    ensure_index(db[settings.COLL_VISIT_STATE], [("mmsi", ASCENDING)], name="mmsi_unique", unique=True)
    ensure_index(db[settings.COLL_VISIT_STATE], [("last_seen_ts", ASCENDING)], name="last_seen_ts_1")
    # TTL (optional):
    # ensure_index(db[settings.COLL_VISIT_STATE], [("last_seen_ts", ASCENDING)], name="last_seen_ttl", expireAfterSeconds=7*24*3600)

    # port_calls
    ensure_index(db[settings.COLL_PORT_CALLS], [("port_name", ASCENDING), ("entry_ts", ASCENDING)], name="portname_entry")
    ensure_index(db[settings.COLL_PORT_CALLS], [("mmsi", ASCENDING), ("entry_ts", ASCENDING)], name="mmsi_entry")
    ensure_index(db[settings.COLL_PORT_CALLS], [("aggregated_window", ASCENDING)], name="agg_window_1", sparse=True)

    # port_traffic (remove if you prefer no index here)
    ensure_index(db[settings.COLL_PORT_TRAFFIC], [("port_name", ASCENDING), ("window_start", ASCENDING)],
                 name="portname_window_unique", unique=True)

    print("Indexes created/verified.")

if __name__ == "__main__":
    main()
