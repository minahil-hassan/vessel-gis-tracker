# # File: src/utils/popup_utils.py
# import os
# from typing import Optional, List
# from datetime import datetime, timedelta, timezone
# from pymongo.collection import Collection
# from bson.regex import Regex
# from src.database.mongo_connection import db
# from src.utils.flag_utils import get_flag_iso_from_mmsi
# from geopy.distance import geodesic

# IMAGE_DIR = "vessel_images"
# NO_IMAGE_FILENAME = "NO_IMAGE.PNG"


# def get_destination_name_from_locode(locode: str) -> Optional[str]:
#     if not locode:
#         return None
#     port_doc = db["ports"].find_one({"locode": locode}, {"name": 1})
#     return port_doc["name"] if port_doc else None

# def find_last_port(mmsi: int, history_coll: Collection, port_coll: Collection) -> Optional[str]:
#     """
#     Finds the last confirmed port visit where the vessel stopped and then departed.
#     """
#     history = list(history_coll.find(
#         {"mmsi": mmsi},
#         sort=[("timestamp_utc", -1)]
#     ))

#     for i, entry in enumerate(history):
#         sog = entry.get("sog", 99)
#         coords = entry.get("coordinates", {}).get("coordinates")
#         if sog > 0.5 or not coords:
#             continue

#         # Check proximity to port
#         for port in port_coll.find({}, {"name": 1, "location": 1}):
#             port_coords = port.get("location", {}).get("coordinates")
#             if not port_coords:
#                 continue

#             dist = geodesic((coords[1], coords[0]), (port_coords[1], port_coords[0])).km
#             if dist < 1.0:
#                 # Now check if vessel departed later
#                 for future_entry in history[:i]:  # earlier entries = later in time
#                     if future_entry.get("sog", 0) > 2.0:
#                         return port["name"]
#                 break  # didn't depart, try earlier stop

#     return None


# # def find_port_calls(mmsi: int, history_coll: Collection, port_coll: Collection, max_days: int = 10) -> List[str]:
# #     """
# #     Returns a list of past port calls based on low speed and proximity to ports.
# #     """
# #     since = datetime.now(timezone.utc) - timedelta(days=max_days)
# #     history = list(history_coll.find(
# #         {"mmsi": mmsi, "timestamp_utc": {"$gte": since}},
# #         sort=[("timestamp_utc", 1)]
# #     ))

# #     visited_ports = []
# #     last_port = None

# #     for entry in history:
# #         sog = entry.get("sog", 100)
# #         coords = entry.get("coordinates", {}).get("coordinates")
# #         if not coords or sog > 0.5:
# #             continue

# #         # check nearby ports
# #         for port in port_coll.find({}, {"name": 1, "location": 1}):
# #             port_coords = port.get("location", {}).get("coordinates")
# #             if not port_coords:
# #                 continue
# #             dist = geodesic((coords[1], coords[0]), (port_coords[1], port_coords[0])).km
# #             if dist < 1.0:
# #                 port_name = port["name"]
# #                 if port_name != last_port:
# #                     visited_ports.append(port_name)
# #                     last_port = port_name
# #                 break

# #     return visited_ports

# from datetime import datetime, timedelta, timezone
# from typing import List
# from pymongo.collection import Collection

# def find_port_calls(mmsi: int, history_coll: Collection, port_coll: Collection, max_days: int = 10) -> List[str]:
#     """
#     Optimized version: Returns a list of past port calls using MongoDB's spatial $nearSphere query.
#     Assumes 2dsphere index exists on ports.location.
#     """
#     since = datetime.now(timezone.utc) - timedelta(days=max_days)

#     # Fetch historical AIS points in ascending time order
#     history_cursor = history_coll.find(
#         {
#             "mmsi": mmsi,
#             "timestamp_utc": {"$gte": since},
#             "sog": {"$lte": 0.5}  # Consider vessel "stopped"
#         },
#         sort=[("timestamp_utc", 1)]
#     )

#     visited_ports = []
#     last_port = None

#     for entry in history_cursor:
#         coords = entry.get("coordinates", {}).get("coordinates")
#         if not coords:
#             continue

#         lon, lat = coords

#         # Use MongoDB spatial query to find nearby port (within 1km)
#         nearest_port = port_coll.find_one({
#             "location": {
#                 "$nearSphere": {
#                     "$geometry": {"type": "Point", "coordinates": [lon, lat]},
#                     "$maxDistance": 1000  # meters
#                 }
#             }
#         }, {"name": 1})

#         if nearest_port:
#             port_name = nearest_port["name"]
#             if port_name != last_port:
#                 visited_ports.append(port_name)
#                 last_port = port_name

#     return visited_ports

# File: src/utils/popup_utils.py

from typing import List
from datetime import datetime, timedelta, timezone
from pymongo.collection import Collection
from geopy.distance import geodesic

def find_port_calls(
    mmsi: int,
    history_coll: Collection,
    port_coll: Collection,
    max_days: int = 10
) -> List[str]:
    """
    Returns a list of port names that the vessel visited (stopped at) in the past `max_days`.
    
    A port call is defined as a moment when the vessel was:
    - Within 1 km of a port's location
    - And moving at a speed over ground (SOG) ≤ 0.5 knots

    Args:
        mmsi (int): MMSI of the vessel.
        history_coll (Collection): MongoDB collection with AIS position history.
        port_coll (Collection): MongoDB collection with UK ports and coordinates.
        max_days (int): How far back to look for port visits.

    Returns:
        List[str]: Ordered list of unique port names visited, in ascending time order.
    """
    since = datetime.now(timezone.utc) - timedelta(days=max_days)

    # Fetch recent AIS data for this vessel
    history = list(history_coll.find(
        {"mmsi": mmsi, "timestamp_utc": {"$gte": since}},
        sort=[("timestamp_utc", 1)]
    ))

    visited_ports = []
    last_port = None

    for entry in history:
        sog = entry.get("sog", 100)
        coords = entry.get("coordinates", {}).get("coordinates")
        if not coords or sog > 0.5:
            continue

        # Check if vessel was near any known port
        for port in port_coll.find({}, {"name": 1, "location": 1}):
            port_coords = port.get("location", {}).get("coordinates")
            if not port_coords:
                continue

            dist_km = geodesic((coords[1], coords[0]), (port_coords[1], port_coords[0])).km
            if dist_km < 1.0:
                port_name = port.get("name")
                if port_name and port_name != last_port:
                    visited_ports.append(port_name)
                    last_port = port_name
                break  # stop checking other ports for this point

    return visited_ports


