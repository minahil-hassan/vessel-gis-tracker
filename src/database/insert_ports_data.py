# database/insert_ports_data.py

import json
import re
from .mongo_connection import db

def parse_coord(coord_str):
    # e.g., "52.2446N, 4.2658W"
    lat_str, lon_str = [x.strip() for x in coord_str.split(',')]
    lat = float(re.sub(r'[NS]', '', lat_str))
    lon = float(re.sub(r'[EW]', '', lon_str))
    if 'S' in lat_str: lat = -lat
    if 'W' in lon_str: lon = -lon
    return lat, lon

def extract_port_name(port_str):
    # e.g., "Aberaeron\nUnited Kingdom (UK)" -> "Aberaeron"
    name = port_str.split('\n')[0].strip()
    name = name.split('(')[0].strip()  # Remove country if in brackets
    return name

def transform_port_record(entry):
    name = extract_port_name(entry['Port'])
    locode = entry['LOCODE']
    lat, lon = parse_coord(entry['Coordinates'])
    return {
        "name": name,
        "locode": locode,
        "location": {
            "type": "Point",
            "coordinates": [lon, lat]
        }
    }

def insert_ports_from_file(filepath: str):
    with open(filepath, "r") as f:
        data = json.load(f)
    collection = db["ports"]
    transformed = [transform_port_record(entry) for entry in data]
    result = collection.insert_many(transformed)
    print(f"Inserted {len(result.inserted_ids)} ports into MongoDB.")

# create a 2dsphere index for spatial queries
def ensure_ports_geo_index():
    collection = db["ports"]
    collection.create_index([("location", "2dsphere")])
