#database/insert_ais_data.py
import json
from datetime import datetime
from .mongo_connection import db
from datetime import timezone
from datetime import timedelta


def transform_ais_record(record):
    lon = record.get("Longitude", None)
    lat = record.get("Latitude", None)
    return {
        "mmsi": record.get("UserID"),
        "timestamp_utc": datetime.now(timezone.utc),
        "coordinates": {
            "type": "Point",
            "coordinates": [lon, lat]
        },
        "sog": record.get("Sog"),
        "cog": record.get("Cog"),
        "heading": record.get("TrueHeading"),
        "nav_status": record.get("NavigationalStatus"),
        "rot": record.get("RateOfTurn"),
        "position_accuracy": record.get("PositionAccuracy"),
        "raim": record.get("Raim"),
        "valid": record.get("Valid"),
        "message_id": record.get("MessageID"),
        "communication_state": record.get("CommunicationState"),
        "repeat_indicator": record.get("RepeatIndicator"),
        "special_manoeuvre": record.get("SpecialManoeuvreIndicator"),
        "spare": record.get("Spare"),
        "timestamp_raw": record.get("Timestamp"),
        "source": "ais-websocket"
    }

def insert_ais_from_file(filepath: str):
    with open(filepath, "r") as f:
        data = json.load(f)
    collection = db["vessel_position"]
    transformed = [transform_ais_record(entry) for entry in data]
    result = collection.insert_many(transformed)
    print(f"Inserted {len(result.inserted_ids)} AIS records.")


def insert_ais_batch(data_list):
    collection = db["vessel_position"]

    if not data_list:
        print("No position data to insert.")
        return

    print("Sample data to insert:", data_list[0])
    
    try:
        result = collection.insert_many(data_list)
        print(f"Inserted {len(result.inserted_ids)} position reports.")
    except Exception as e:
        print("Error inserting position reports:", e)



def insert_or_update_vessel_details(details_list):
    collection = db["vessel_details"]
    for doc in details_list:
        if doc.get("mmsi"):
            collection.update_one(
                {"mmsi": doc["mmsi"]},
                {"$set": doc},
                upsert=True
            )
    # print(f"Inserted {len(details_list)} vessel_details records.")

