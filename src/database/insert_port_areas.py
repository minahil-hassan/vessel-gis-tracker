# src/database/insert_port_areas.py

import json
from pymongo import GEOSPHERE
from pathlib import Path
import sys

from src.database.mongo_connection import get_mongo_connection
# Add the root directory to the path so `src` can be imported
sys.path.append(str(Path(__file__).resolve().parents[1]))

def insert_port_areas(filepath: str):
    """
    Loads a GeoJSON file and inserts the features into the port_areas collection in MongoDB.
    
    Args:
        filepath (str): Absolute path to the port_areas.geojson file.
    """
    db = get_mongo_connection()
    collection = db["port_areas"]

    # Load GeoJSON file
    with open(filepath, "r", encoding="utf-8") as f:
        geojson = json.load(f)

    if geojson.get("type") != "FeatureCollection" or "features" not in geojson:
        raise ValueError("Invalid GeoJSON format. Must contain 'type' = 'FeatureCollection' and 'features'.")

    # Optional: Clear existing entries
    collection.delete_many({})

    # Insert all features
    collection.insert_many(geojson["features"])
    print(f"Inserted {len(geojson['features'])} port area features.")

    # Create 2dsphere index on 'geometry' field
    collection.create_index([("geometry", GEOSPHERE)])
    print("📌 2dsphere index created on 'geometry'.")

if __name__ == "__main__":
    # Full Windows path to geojson
    geojson_path = Path(r"C:\Users\minahil\vec\vehicle-gis-platform\data\json\geojson\port_areas.geojson")

    if not geojson_path.exists():
        raise FileNotFoundError(f"GeoJSON file not found at {geojson_path}")

    insert_port_areas(str(geojson_path))
