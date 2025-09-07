# src/api/endpoints/area_traffic.py

from fastapi import APIRouter, Query
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List

from src.database.mongo_connection import db
from src.utils.constants import SHIP_TYPE_MAP, VESSEL_TYPE_GROUPS

router = APIRouter(prefix="/area-traffic", tags=["liverpool-areas"])

@router.get("", summary="Get ship traffic by Liverpool sub-area (arrivals) with type breakdowns")
def get_area_traffic(
    days: int = Query(1, ge=1, le=30, description="Number of days to analyze (1–30, by entry time)"),
    area_name_contains: Optional[str] = Query(None, description="Case-insensitive filter on area_name")
):
    """
    Computes arrivals per Liverpool sub-area using `area_calls`.
    Joins to `vessel_details` for ship type, then returns totals, unique MMSI count,
    and breakdowns by ship type and type group.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    print(f"Cutoff: {cutoff.isoformat()}")

    match_stage: Dict[str, Any] = {"entry_ts": {"$gte": cutoff}}
    if area_name_contains:
        match_stage["area_name"] = {"$regex": area_name_contains, "$options": "i"}

    pipeline = [
        {"$match": match_stage},
        {"$lookup": {
            "from": "vessel_details",
            "localField": "mmsi",
            "foreignField": "mmsi",
            "as": "vd"
        }},
        {"$unwind": {"path": "$vd", "preserveNullAndEmptyArrays": True}},
        {"$project": {
            "_id": 0,
            "area_name": 1,
            "mmsi": 1,
            "type_code": "$vd.Type"
        }},
        {"$facet": {
            "by_area": [
                {"$group": {
                    "_id": "$area_name",
                    "total_traffic": {"$sum": 1},
                    "unique_mmsi_set": {"$addToSet": "$mmsi"}
                }}
            ],
            "by_type": [
                {"$group": {
                    "_id": {"area_name": "$area_name", "type_code": "$type_code"},
                    "count": {"$sum": 1}
                }}
            ]
        }}
    ]

    result = list(db["area_calls"].aggregate(pipeline, allowDiskUse=True))
    if not result:
        return {"traffic_data": []}

    by_area = result[0].get("by_area", [])
    by_type = result[0].get("by_type", [])

    # Build per-area containers
    traffic_data: Dict[str, Dict[str, Any]] = {}
    for row in by_area:
        area = row["_id"]
        traffic_data[area] = {
            "area_name": area,
            "total_traffic": int(row.get("total_traffic", 0)),
            "unique_mmsi_count": len(row.get("unique_mmsi_set", [])),
            "ship_types": {},
            "ship_type_groups": {}
        }

    def label_for(code) -> str:
        if code is None:
            return "Unknown"
        return SHIP_TYPE_MAP.get(code, f"Type {code}")

    # Add ship type breakdown
    for row in by_type:
        key = row["_id"]
        area = key["area_name"]
        if area not in traffic_data:
            continue
        code = key.get("type_code")
        label = label_for(code)
        traffic_data[area]["ship_types"][label] = traffic_data[area]["ship_types"].get(label, 0) + int(row["count"])

    # Add vessel type groupings
    for area, pdata in traffic_data.items():
        groups: Dict[str, int] = {}
        for label, cnt in pdata["ship_types"].items():
            group = "Other"
            for gname, labels in VESSEL_TYPE_GROUPS.items():
                if label in labels:
                    group = gname
                    break
            groups[group] = groups.get(group, 0) + cnt
        pdata["ship_type_groups"] = groups

    response = sorted(traffic_data.values(), key=lambda x: x["total_traffic"], reverse=True)
    return {"traffic_data": response}
