# src/database/insert_latest_position.py
# This module handles inserting or updating the latest vessel positions in the database.
from .mongo_connection import db

def upsert_latest_position(position_doc):
    """
    Upsert a single vessel position into the latest_positions collection.
    Ensures _id is not present to avoid MongoDB WriteError.
    """
    collection = db["latest_positions"]
    mmsi = position_doc.get("mmsi")
    if mmsi is None:
        print("Warning: Skipping upsert, missing MMSI in position_doc.")
        return
    # Make a shallow copy and remove _id if present
    doc = dict(position_doc)
    doc.pop("_id", None)
    collection.update_one(
        {"mmsi": mmsi},
        {"$set": doc},
        upsert=True
    )

def upsert_latest_positions(position_list):
    """
    Upsert a list of vessel positions into the latest_positions collection.
    """
    for position in position_list:
        upsert_latest_position(position)
