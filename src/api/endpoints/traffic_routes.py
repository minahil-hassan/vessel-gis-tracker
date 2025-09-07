# src/api/traffic_routes.py
from fastapi import APIRouter, Query
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List

from src.database.mongo_connection import db
from src.utils.constants import SHIP_TYPE_MAP, VESSEL_TYPE_GROUPS


router = APIRouter(prefix="/traffic", tags=["traffic"])
# ---------- LIVERPOOL SUMMARY: arrivals + type breakdowns ----------
@router.get("", summary="Get ship traffic by port (arrivals) with type breakdowns")
def get_ship_traffic(
    days: int = Query(1, ge=1, le=30, description="Number of days to analyze (1–30, by entry time)"),
    port_name_contains: Optional[str] = Query("Port of Liverpool", description="Case-insensitive filter on port_name")
):
    """
    Computes arrivals per port using `port_calls` (entry_ts within the last N days).
    Joins to `vessel_details` for ship type, then returns totals, unique MMSI count,
    and breakdowns by ship type and type group.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    match_stage: Dict[str, Any] = {"entry_ts": {"$gte": cutoff}}
    if port_name_contains:
        match_stage["port_name"] = {"$regex": port_name_contains, "$options": "i"}

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
            "port_name": 1,
            "mmsi": 1,
            "type_code": "$vd.Type"  # may be null
        }},
        {"$facet": {
            "by_port": [
                {"$group": {
                    "_id": "$port_name",
                    "total_traffic": {"$sum": 1},
                    "unique_mmsi_set": {"$addToSet": "$mmsi"}
                }}
            ],
            "by_type": [
                {"$group": {
                    "_id": {"port_name": "$port_name", "type_code": "$type_code"},
                    "count": {"$sum": 1}
                }}
            ]
        }}
    ]

    result = list(db["port_calls"].aggregate(pipeline, allowDiskUse=True))
    if not result:
        return {"traffic_data": []}

    by_port = result[0].get("by_port", [])
    by_type = result[0].get("by_type", [])

    # Seed per-port containers
    traffic_data: Dict[str, Dict[str, Any]] = {}
    for row in by_port:
        port = row["_id"]
        traffic_data[port] = {
            "area_name": port,
            "total_traffic": int(row.get("total_traffic", 0)),
            "unique_mmsi_count": len(row.get("unique_mmsi_set", [])),
            "ship_types": {},
            "ship_type_groups": {}
        }

    # Map AIS type codes to labels
    def label_for(code) -> str:
        if code is None:
            return "Unknown"
        return SHIP_TYPE_MAP.get(code, f"Type {code}")

    # Add type breakdowns
    for row in by_type:
        key = row["_id"]
        port = key["port_name"]
        if port not in traffic_data:
            continue
        code = key.get("type_code")
        label = label_for(code)
        traffic_data[port]["ship_types"][label] = traffic_data[port]["ship_types"].get(label, 0) + int(row["count"])

    # Build group breakdowns from type labels
    for port, pdata in traffic_data.items():
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


# ---------- UK-WIDE SUMMARY: same pipeline, no port_name filter ----------
@router.get("/uk", summary="UK-wide ship traffic by port (arrivals) with type breakdowns")
def get_ship_traffic_uk(
    days: int = Query(1, ge=1, le=30, description="Number of days to analyze (1–30, by entry time)")
):
    """Same as /traffic but without port_name filtering (UK-wide)."""
    return get_ship_traffic(days=days, port_name_contains=None)


# ---------- LIVERPOOL BUCKETS: 6h time series from port_traffic ----------
@router.get("/buckets", summary="Time-bucketed arrivals (6h windows) for Liverpool ports")
def get_traffic_buckets(
    days: int = Query(7, ge=1, le=60, description="How many days back to include (1–60)"),
    port_name_contains: str = Query("Port of Liverpool", description="Case-insensitive filter on port_name")
):
    """
    Returns 6-hour buckets from `port_traffic` for charting.
    Response shape:
      {
        "bucket_hours": 6,
        "start_utc": <dt>,
        "end_utc": <dt>,
        "series": [
          { "port_name": "...", "points": [ { "t": <dt>, "arrivals": n }, ... ] },
          ...
        ]
      }
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    match_stage: Dict[str, Any] = {"window_start": {"$gte": cutoff}}
    if port_name_contains:
        match_stage["port_name"] = {"$regex": port_name_contains, "$options": "i"}

    pipeline = [
        {"$match": match_stage},
        {"$group": {
            "_id": {"port_name": "$port_name", "window_start": "$window_start"},
            "arrivals": {"$sum": "$arrivals"}
        }},
        {"$sort": {"_id.window_start": 1}}
    ]

    rows = list(db["port_traffic"].aggregate(pipeline, allowDiskUse=True))

    # Pivot into series per port
    series: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        pn = r["_id"]["port_name"]
        ws = r["_id"]["window_start"]
        cnt = int(r["arrivals"])
        series.setdefault(pn, []).append({"t": ws, "arrivals": cnt})

    result = [{"port_name": pn, "points": pts} for pn, pts in series.items()]
    result.sort(key=lambda item: sum(p["arrivals"] for p in item["points"]), reverse=True)

    return {
        "bucket_hours": 6,
        "start_utc": cutoff,
        "end_utc": datetime.now(timezone.utc),
        "series": result
    }
    


# ---------- UK-WIDE BUCKETS: same, no port_name filter ----------
@router.get("/buckets/uk", summary="Time-bucketed arrivals (6h windows) for all UK ports")
def get_traffic_buckets_uk(
    days: int = Query(7, ge=1, le=30, description="How many days back to include (1–60)")
):
    """Same as /traffic/buckets but UK-wide (no port_name filter)."""
    return get_traffic_buckets(days=days, port_name_contains=None)
