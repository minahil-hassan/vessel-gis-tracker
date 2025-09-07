# # # src/api/endpoints/port_areas.py
from fastapi import APIRouter
from src.database.mongo_connection import db
from shapely.geometry import shape

router = APIRouter()

@router.get("/", summary="Get all port area polygons",
            response_description="GeoJSON FeatureCollection of port, terminal, dock, and facility polygons")
def get_all_port_areas():
    raw = list(db["port_areas"].find({}, {"_id":0}))
    enriched = []
    for feat in raw:
        try:
            geom = shape(feat["geometry"])
            cent = geom.centroid
            feat.setdefault("properties", {})["centroid"] = [cent.x, cent.y]
        except Exception:
            feat.setdefault("properties", {})["centroid"] = [0,0]
        enriched.append(feat)

    return {"type":"FeatureCollection", "features": enriched}
