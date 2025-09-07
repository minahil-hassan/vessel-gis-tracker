# # src/api/endpoints/vessel_popup.py

# from fastapi import APIRouter, HTTPException
# from fastapi.encoders import jsonable_encoder
# from src.database.mongo_connection import db
# from pymongo.collection import Collection
# from datetime import datetime, timedelta, timezone
# from geopy.distance import geodesic  # Optional fallback or debug
# import traceback
# from typing import List

# router = APIRouter()

# # Define maximum distance (30 miles ≈ 48.28 km = 48280 meters)
# MAX_DISTANCE_METERS = 48280


# def find_port_calls(
#     mmsi: int,
#     history_coll: Collection,
#     port_coll: Collection,
#     max_days: int = 10
# ) -> List[str]:
#     """
#     Identify port calls for a vessel based on low speed or moored status,
#     and proximity to ports using geospatial indexing.

#     A port call is logged when:
#     - vessel's speed is < 0.5 knots OR nav_status = 5 (moored)
#     - AND it is within 30 miles (~48.28km) of a known port

#     Args:
#         mmsi (int): MMSI of the vessel
#         history_coll (Collection): MongoDB collection of vessel positions
#         port_coll (Collection): MongoDB collection of UK ports
#         max_days (int): How far back to check in days

#     Returns:
#         List[str]: List of port names visited, deduplicated and ordered by time
#     """
#     since = datetime.now(timezone.utc) - timedelta(days=max_days)
    
#     # Build query for recent AIS records with stop-like behaviour
#     query = {
#         "mmsi": mmsi,
#         "timestamp_utc": {"$gte": since},
#         "$or": [
#             {"sog": {"$lt": 0.5}},
#             {"nav_status": 5}
#         ]
#     }

#     visited_ports = []
#     last_port = None

#     try:
#         # Fetch matching historical AIS data sorted by time
#         history = list(history_coll.find(query).sort("timestamp_utc", 1))

#         for entry in history:
#             coords = entry.get("coordinates", {}).get("coordinates")  # [lon, lat]
#             if not coords or len(coords) != 2:
#                 continue

#             # Use MongoDB geospatial query to find nearest port within 30 miles
#             port = port_coll.find_one({
#                 "location": {
#                     "$near": {
#                         "$geometry": {
#                             "type": "Point",
#                             "coordinates": coords  # GeoJSON expects [lon, lat]
#                         },
#                         "$maxDistance": MAX_DISTANCE_METERS
#                     }
#                 }
#             }, {"name": 1})  # Only return name field

#             # Add to result list if unique
#             if port:
#                 port_name = port.get("name")
#                 if port_name and port_name != last_port:
#                     visited_ports.append(port_name)
#                     last_port = port_name

#     except Exception as e:
#         print(f"[ERROR] Failed to fetch port calls for MMSI {mmsi}: {e}")
#         traceback.print_exc()

#     return visited_ports


# @router.get("/{mmsi}", summary="Get port calls in the last 10 days for a vessel")
# def get_port_calls_for_vessel(mmsi: int):
#     """
#     Endpoint: /api/vessel_popup/{mmsi}
#     Returns a list of port names visited by the vessel in the past 10 days.
#     """
#     try:
#         port_calls = find_port_calls(mmsi, db["vessel_position"], db["ports"])

#         if not port_calls:
#             # raise HTTPException(status_code=404, detail=f"No port calls found for MMSI {mmsi}")
#             return jsonable_encoder({
#                 "mmsi": mmsi,
#                 "port_calls": ["No port calls found"]
#             })
        

#         return jsonable_encoder({
#             "mmsi": mmsi,
#             "port_calls": port_calls
#         })

#     except HTTPException as he:
#         raise he  # Forward known exceptions

#     except Exception as e:
#         print(f"[ERROR] Internal error for MMSI {mmsi}: {e}")
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail="Internal Server Error")

# src/api/endpoints/vessel_popup.py

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from src.database.mongo_connection import db
from pymongo.collection import Collection
from datetime import datetime, timezone
import traceback
from typing import List

router = APIRouter()

# ---------------------------------------------------------------------
# New: Pull “port calls” from materialised collections instead of
#      recomputing with $near each request.
# ---------------------------------------------------------------------

def _dedupe_consecutive(names: List[str]) -> List[str]:
    """Remove only *consecutive* duplicates while preserving order."""
    out = []
    last = None
    for n in names:
        if not n:
            continue
        if n != last:
            out.append(n)
            last = n
    return out


def find_port_calls_from_materialised(
    mmsi: int,
    calls_coll: Collection,
    visit_state_coll: Collection,
    limit: int = 6,
    include_active: bool = False
) -> List[str]:
    """
    Return up to the last `limit` port names for the vessel (MMSI), using the
    new materialised collections.

    Source of truth:
      - Completed visits from `port_calls` (one doc per entry→exit).
      - Optionally prepend an in-progress visit from `port_visit_state`
        (if include_active=True and in_port=True).

    Output:
      - List[str] of port names in chronological order (oldest → newest),
        deduping only *consecutive* repeats.
    """
    # 1) Fetch recent completed calls (newest first) from `port_calls`
    #    We sort by `exit_ts` desc (fallback to `entry_ts` if exit missing).
    #    Project only what we need for speed.
    pipeline = [
        {"$match": {"mmsi": mmsi}},
        {"$sort": {"exit_ts": -1, "entry_ts": -1}},
        {"$limit": max(limit * 3, limit)},  # over-fetch a bit to allow dedupe
        {"$project": {"_id": 0, "port_name": 1, "entry_ts": 1, "exit_ts": 1}},
    ]
    recent = list(calls_coll.aggregate(pipeline))

    # 2) Build a reverse-chron list of names (newest → oldest)
    names_desc = [doc.get("port_name") for doc in recent if doc.get("port_name")]

    # 3) Optionally include an active (in-progress) visit at the *end* of the
    #    descending list (i.e., as the "newest" item), then we'll reverse later.
    if include_active:
        active = visit_state_coll.find_one(
            {"mmsi": mmsi, "in_port": True},
            projection={"_id": 0, "port_name": 1, "entered_at": 1}
        )
        if active and active.get("port_name"):
            # Only append if it's different from the latest completed call name
            if not names_desc or active["port_name"] != names_desc[0]:
                names_desc.insert(0, active["port_name"])

    # 4) Reverse to chronological order (oldest → newest) to match the old API’s feel
    names_chrono = list(reversed(names_desc))

    # 5) Dedup ONLY consecutive repeats (to mimic old behavior)
    names_dedup = _dedupe_consecutive(names_chrono)

    # 6) Take only the last `limit` in chronological order
    #    (If more than limit, drop the oldest extras.)
    if len(names_dedup) > limit:
        names_dedup = names_dedup[-limit:]

    return names_dedup


@router.get("/{mmsi}", summary="Get port calls in the last 10 days for a vessel (materialised)")
def get_port_calls_for_vessel(mmsi: int):
    """
    Endpoint: /api/vessel_popup/{mmsi}
    Returns a list of up to the last 6 port names visited by the vessel
    using the new materialised collections (completed visits in `port_calls`).
    """
    try:
        # Collections
        coll_calls = db["port_calls"]
        coll_state = db["port_visit_state"]

        port_calls = find_port_calls_from_materialised(
            mmsi=mmsi,
            calls_coll=coll_calls,
            visit_state_coll=coll_state,
            limit=6,
            include_active=False  # keep backward-compatible semantics: completed only
        )

        if not port_calls:
            return jsonable_encoder({"mmsi": mmsi, "port_calls": ["No port calls found"]})

        return jsonable_encoder({"mmsi": mmsi, "port_calls": port_calls})

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"[ERROR] Internal error for MMSI {mmsi}: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")

