# src/api/endpoints/ports.py
# this file defines the API endpoint for retrieving port data
from fastapi import APIRouter
from src.database.mongo_connection import db

router = APIRouter()

@router.get("/", summary="Get all ports", response_description="List of ports")
def get_all_ports():
    ports = list(db["ports"].find({}, {"_id": 0}))  # Exclude _id for frontend
    # Optionally format as GeoJSON FeatureCollection for Mapbox
    features = [{
        "type": "Feature",
        "geometry": port["location"],
        "properties": {k: v for k, v in port.items() if k != "location"}
    } for port in ports]
    return {"type": "FeatureCollection", "features": features}
