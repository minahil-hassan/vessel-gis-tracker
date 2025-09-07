# src/scripts/convert_coordinates_to_geojson.py
# This script converts vessel position coordinates from plain arrays to GeoJSON format
# and ensures the geospatial index is created.

from mongo_connection import get_mongo_connection
from pymongo import GEOSPHERE

def convert_vessel_position_coordinates():
    db = get_mongo_connection()
    collection = db["vessel_position"]
    count = 0

    # Find docs where coordinates is a plain array, not GeoJSON
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

    print(f"Updated {count} documents to GeoJSON format.")

    # Ensure geospatial index exists
    collection.create_index([("coordinates", GEOSPHERE)])
    print("2dsphere index created on 'coordinates'.")

if __name__ == "__main__":
    convert_vessel_position_coordinates()
