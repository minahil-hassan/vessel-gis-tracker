# src/api/endpoints/vessels.py
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from src.database.mongo_connection import db
from datetime import datetime, timezone, timedelta
from src.utils.constants import SHIP_TYPE_MAP
router = APIRouter()


@router.get(
    "/",
    summary="Get all latest vessel positions",
    response_description="GeoJSON FeatureCollection of latest vessel positions"
)

def get_all_latest_vessel_positions():
    """
    Returns a GeoJSON FeatureCollection of vessels seen in the last 12 hours,
    enriched with static metadata like name, type, callsign, and destination.
    """

   # Define the cutoff time (vessels seen in last 5 days)
    cutoff_time = datetime.now(timezone.utc) - timedelta(days=5)

    # Query dynamic position data from 'latest_positions'
    
    vessel_docs = list(db["latest_positions"].find(
        {"timestamp_utc": {"$gte": cutoff_time}},
        {"_id": 0}
    ))

    
    # Build lookup for static vessel details from 'vessel_details'
   
    static_details_lookup = {
        doc["mmsi"]: doc
        for doc in db["vessel_details"].find(
            {}, {"_id": 0, "mmsi": 1, "Callsign": 1, "Name": 1, "Type": 1, "Destination": 1}
        )
    }

  
    # Build GeoJSON FeatureCollection
   
    features = []

    for v in vessel_docs:
        coords_obj = v.get("coordinates")
        if not coords_obj or coords_obj.get("type") != "Point" or "coordinates" not in coords_obj:
            continue  # skip invalid entries

        coords = coords_obj["coordinates"]
        mmsi = v.get("mmsi")

        # Lookup static metadata
        detail = static_details_lookup.get(mmsi, {})

        # Ship type mapping with fallback
        ship_type_raw = detail.get("Type")
        ship_type_label = SHIP_TYPE_MAP.get(
            ship_type_raw,
            f"Type {ship_type_raw}" if ship_type_raw is not None else "Unknown"
        )

        # Build feature
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": coords
            },
            "properties": {
                "mmsi": mmsi,
                "name": detail.get("Name"),
                "callsign": detail.get("Callsign"),
                "type": ship_type_label,
                "destination": detail.get("Destination"),

                "sog": v.get("sog"),
                "cog": v.get("cog"),              # from dynamic collection
                "heading": v.get("heading"),      # from dynamic collection
                "rot": v.get("rot"),              # Rate of Turn
                "nav_status": v.get("nav_status"),
                "timestamp": v.get("timestamp_utc")
            }
        }
        features.append(feature)

   
    # Return GeoJSON
   
    return {
        "type": "FeatureCollection",
        "features": features
    }





