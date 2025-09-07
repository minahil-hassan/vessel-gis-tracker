# src/database/fix_latest_positions.py
# This script fixes the latest_positions collection by converting coordinate arrays to GeoJSON format
# and ensuring the geospatial index is created.

from mongo_connection import get_mongo_connection
from pymongo import GEOSPHERE

def convert_latest_positions_to_geojson():
    db = get_mongo_connection()
    collection = db["latest_positions"]
    count = 0

    # Find malformed coordinate fields (type: array)
    query = {"coordinates": {"$type": "array"}}
    cursor = collection.find(query)

    for doc in cursor:
        coords = doc.get("coordinates")
        if isinstance(coords, list) and len(coords) == 2:
            geojson_point = {
                "type": "Point",
                "coordinates": coords
            }
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"coordinates": geojson_point}}
            )
            count += 1

    print(f" Updated {count} documents to GeoJSON format.")

    # Create or ensure geospatial index
    collection.create_index([("coordinates", GEOSPHERE)])
    print(" 2dsphere index ensured on 'coordinates'.")

if __name__ == "__main__":
    convert_latest_positions_to_geojson()
