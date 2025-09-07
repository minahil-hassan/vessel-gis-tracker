# src/api/endpoints/vessel_history.py
# This file defines the API endpoint for retrieving historical AIS data for vessels.
"""
Module: vessel_history.py
Path: src/api/endpoints/vessel_history.py

Description:
This module defines a FastAPI endpoint that retrieves historical AIS data (position reports) 
for a vessel given its MMSI (Maritime Mobile Service Identity). It supports filtering by 
time range and limiting the number of returned records.

Endpoint:
GET /vessel_history/{mmsi}

Query Parameters:
- limit (int, optional): Maximum number of records to return (default: 500)
- start_time (datetime, optional): ISO 8601 start time filter
- end_time (datetime, optional): ISO 8601 end time filter

MongoDB Collection:
- vessel_position: Stores historical AIS position reports with fields like mmsi, timestamp_utc, coordinates, sog, cog, etc.

Response Format:
{
    "mmsi": 123456789,
    "trajectory": [
        {
            "mmsi": 123456789,
            "timestamp_utc": "2025-07-01T14:32:00Z",
            "coordinates": { "type": "Point", "coordinates": [-3.01, 53.45] },
            "sog": 12.5,
            ...
        },
        ...
    ]
}

Raises:
- HTTPException 404 if no records found for the given MMSI and time filters.

Usage Example:
GET /vessel_history/123456789?start_time=2025-07-01T00:00:00Z&end_time=2025-07-10T23:59:59Z&limit=100

Notes:
- Designed for integration with frontend map-based trajectory visualisation.
- Ensure that MongoDB index on `mmsi` and `timestamp_utc` exists for performance.
"""

from fastapi import APIRouter, HTTPException, Query
from pymongo import ASCENDING
from typing import Optional
from datetime import datetime
from src.database.mongo_connection import get_mongo_connection

router = APIRouter()
db = get_mongo_connection()

@router.get("/{mmsi}", summary="Get full historical AIS positions for a vessel by MMSI")

async def get_vessel_history(
    mmsi: int,
    limit: int = Query(500, description="Maximum number of AIS records to return"),
    start_time: Optional[datetime] = Query(None, description="Optional start time (ISO format)"),
    end_time: Optional[datetime] = Query(None, description="Optional end time (ISO format)")
):
    """
    Returns full historical AIS data from 'vessel_position' for a given vessel MMSI,
    sorted by timestamp_utc ascending.
    """
    query = {"mmsi": mmsi}
    if start_time or end_time:
        query["timestamp_utc"] = {}
        if start_time:
            query["timestamp_utc"]["$gte"] = start_time
        if end_time:
            query["timestamp_utc"]["$lte"] = end_time

    cursor = (
        db.vessel_position
        .find(query, {"_id": 0})  # exclude _id for cleaner frontend use
        .sort("timestamp_utc", ASCENDING)
        .limit(limit)
    )

    results = list(cursor)

    if not results:
        raise HTTPException(status_code=404, detail=f"No AIS history found for MMSI {mmsi}")

    return {
        "mmsi": mmsi,
        "trajectory": results
    }
