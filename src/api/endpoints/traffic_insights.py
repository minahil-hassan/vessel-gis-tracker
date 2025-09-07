# # src/api/endpoints/traffic_insights.py

# from fastapi import APIRouter, Query
# from fastapi.responses import JSONResponse
# from datetime import datetime, timedelta, timezone
# from typing import Dict, Any
# from collections import Counter
# import calendar

# from src.database.mongo_connection import db
# from src.utils.constants import SHIP_TYPE_MAP, VESSEL_TYPE_GROUPS

# router = APIRouter(prefix="/traffic/summary", tags=["traffic-insights"])

# @router.get("/uk", summary="Generate a UK-wide vessel traffic text summary")
# def generate_uk_traffic_summary(days: int = Query(7, ge=1, le=90)):
#     """
#     Returns a natural language summary of UK maritime traffic for the given time window.
#     Includes busiest days, peak 6-hour slot, busiest port, and most common vessel type group.
#     """
#     cutoff = datetime.now(timezone.utc) - timedelta(days=days)

#     # Step 1: Get bucketed arrivals
#     match_stage: Dict[str, Any] = {"window_start": {"$gte": cutoff}}
#     pipeline = [
#         {"$match": match_stage},
#         {"$group": {
#             "_id": {"window_start": "$window_start", "port_name": "$port_name"},
#             "arrivals": {"$sum": "$arrivals"}
#         }},
#         {"$sort": {"_id.window_start": 1}}
#     ]
#     buckets = list(db["port_traffic"].aggregate(pipeline, allowDiskUse=True))
#     if not buckets:
#         return JSONResponse({"summary": "No traffic data available for this time window."})

#     # Step 2: Extract busiest time slot, days, ports
#     time_slot_counts = Counter()
#     day_counts = Counter()
#     port_counts = Counter()

#     for b in buckets:
#         ts = b["_id"]["window_start"]
#         slot_hour = ts.hour
#         slot_label = f"{str(slot_hour).zfill(2)}–{str((slot_hour + 6) % 24).zfill(2)}"

#         day_str = ts.date().isoformat()  # e.g. '2025-08-20'
#         day_counts[day_str] += b["arrivals"]
#         port_name = b["_id"]["port_name"]
#         time_slot_counts[slot_label] += b["arrivals"]
#         day_counts[day_str] += b["arrivals"]
#         port_counts[port_name] += b["arrivals"]

#     busiest_slot = time_slot_counts.most_common(1)[0][0]
#     sorted_days = day_counts.most_common()
#     busiest_day = sorted_days[0][0]
#     next_days = [d for d, _ in sorted_days[1:3]]
#     quietest_day = min(day_counts.items(), key=lambda x: x[1])[0]
#     busiest_port = port_counts.most_common(1)[0]

#     # Step 3: Get most common vessel type group
#     type_pipeline = [
#         {"$match": {"entry_ts": {"$gte": cutoff}}},
#         {"$lookup": {
#             "from": "vessel_details",
#             "localField": "mmsi",
#             "foreignField": "mmsi",
#             "as": "vd"
#         }},
#         {"$unwind": {"path": "$vd", "preserveNullAndEmptyArrays": True}},
#         {"$project": {"type_code": "$vd.Type"}}
#     ]

#     type_counts = {}
#     for doc in db["port_calls"].aggregate(type_pipeline, allowDiskUse=True):
#         code = doc.get("type_code")
#         label = SHIP_TYPE_MAP.get(code, f"Type {code}" if code else "Unknown")
#         type_counts[label] = type_counts.get(label, 0) + 1

#     group_counts = {}
#     for label, count in type_counts.items():
#         group = "Other / Unknown"
#         for g, subtypes in VESSEL_TYPE_GROUPS.items():
#             if label in subtypes:
#                 group = g
#                 break
#         group_counts[group] = group_counts.get(group, 0) + count

#     most_common_group = max(group_counts.items(), key=lambda x: x[1])[0]

#     # Step 4: Build summary string
#     if next_days:
#         next_phrase = f"{next_days[0]} and {next_days[1]}"
#     else:
#         next_phrase = ""

#     summary = (
#         f"The busiest day of this period was {busiest_day}"
#         + (f", followed by {next_phrase}" if next_phrase else "")
#         + f". {quietest_day} saw the least traffic, with the most vessel traffic being observed during the time slot {busiest_slot} UTC. "
#         f"The highest vessel traffic in the UK was seen at {busiest_port[0]}. "
#         f"The most common vessel type group was {most_common_group}."
#     )

#     return JSONResponse({"summary": summary})
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from collections import Counter
from src.utils.llm_summariser import generate_uk_traffic_summary_llm
from src.database.mongo_connection import db
from src.utils.constants import SHIP_TYPE_MAP, VESSEL_TYPE_GROUPS
from src.utils.llm_summariser import generate_liverpool_traffic_summary_llm

router = APIRouter(prefix="/traffic-insights", tags=["traffic-insights"])

@router.get("/uk", summary="Generate a UK-wide vessel traffic summary (LLM-ready)")
def generate_uk_traffic_summary(days: int = Query(7, ge=1, le=90)):
    """
    Returns structured UK traffic summary data and a placeholder for LLM-written natural language summary.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    # --- 1. Bucketed traffic analysis ---
    match_stage = {"window_start": {"$gte": cutoff}}
    pipeline = [
        {"$match": match_stage},
        {"$group": {
            "_id": {"window_start": "$window_start", "port_name": "$port_name"},
            "arrivals": {"$sum": "$arrivals"}
        }},
        {"$sort": {"_id.window_start": 1}}
    ]
    buckets = list(db["port_traffic"].aggregate(pipeline, allowDiskUse=True))
    if not buckets:
        return JSONResponse({"summary": "No traffic data available for this time window."})

    time_slot_counts = Counter()
    day_counts = Counter()
    port_counts = Counter()

    for b in buckets:
        ts = b["_id"]["window_start"]
        slot_hour = ts.hour
        slot_label = f"{str(slot_hour).zfill(2)}–{str((slot_hour + 6) % 24).zfill(2)}"
        day_str = ts.date().isoformat()
        port = b["_id"]["port_name"]

        time_slot_counts[slot_label] += b["arrivals"]
        day_counts[day_str] += b["arrivals"]
        port_counts[port] += b["arrivals"]

    busiest_slot = time_slot_counts.most_common(1)[0][0]
    sorted_days = day_counts.most_common()
    busiest_day = sorted_days[0][0]
    next_busy_days = [d for d, _ in sorted_days[1:3]]
    least_busy_day = min(day_counts.items(), key=lambda x: x[1])[0]
    busiest_port = port_counts.most_common(1)[0]

    # --- 2. Vessel type group analysis ---
    type_pipeline = [
        {"$match": {"entry_ts": {"$gte": cutoff}}},
        {"$lookup": {
            "from": "vessel_details",
            "localField": "mmsi",
            "foreignField": "mmsi",
            "as": "vd"
        }},
        {"$unwind": {"path": "$vd", "preserveNullAndEmptyArrays": True}},
        {"$project": {"type_code": "$vd.Type"}}
    ]
    subtype_counts = {}
    for doc in db["port_calls"].aggregate(type_pipeline, allowDiskUse=True):
        code = doc.get("type_code")
        label = SHIP_TYPE_MAP.get(code, f"Type {code}" if code else "Unknown")
        subtype_counts[label] = subtype_counts.get(label, 0) + 1

    group_counts = {}
    for label, count in subtype_counts.items():
        group = "Other / Unknown"
        for g, subtypes in VESSEL_TYPE_GROUPS.items():
            if label in subtypes:
                group = g
                break
        group_counts[group] = group_counts.get(group, 0) + count

    most_common_group = max(group_counts.items(), key=lambda x: x[1])[0]

    # --- 3. Structured insight data ---
    insight_data = {
        "days": days,
        "busiest_day": busiest_day,
        "also_busy_days": next_busy_days,
        "least_busy_day": least_busy_day,
        "peak_time_slot_utc": busiest_slot,
        "top_port": busiest_port[0],
        "most_common_vessel_group": most_common_group
    }
    summary_llm = generate_uk_traffic_summary_llm(insight_data)

    # --- 4. Placeholder for LLM summary (will be filled in later) ---
    return JSONResponse({
        "summary_llm": summary_llm,  # Will be filled by OpenAI call later
        "insight_data": insight_data
    })

@router.get("/liverpool", summary="Generate a Liverpool vessel traffic summary (LLM-ready)")
def generate_liverpool_traffic_summary(days: int = Query(7, ge=1, le=90)):
    """
    Returns structured Liverpool traffic summary data and a placeholder for LLM-written summary.
    Includes busiest days, peak 6-hour slot, busiest sub-port, and most common vessel type group.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    # ---- Liverpool ports (canonical + alias) ----
    LIV_PORT_NAMES_CANON = ["Birkenhead Dock Estate", "Port of Liverpool", "Port of Garston"]
    LIV_PORT_NAMES_ALIASES = ["Port of Gartson"]
    LIV_PORT_NAMES_ALL = LIV_PORT_NAMES_CANON + LIV_PORT_NAMES_ALIASES

    # --- 1. Bucketed traffic analysis ---
    match_stage = {
        "window_start": {"$gte": cutoff},
        "port_name": {"$in": LIV_PORT_NAMES_ALL}
    }
    pipeline = [
        {"$match": match_stage},
        {"$group": {
            "_id": {"window_start": "$window_start", "port_name": "$port_name"},
            "arrivals": {"$sum": "$arrivals"}
        }},
        {"$sort": {"_id.window_start": 1}}
    ]
    buckets = list(db["port_traffic"].aggregate(pipeline, allowDiskUse=True))
    if not buckets:
        return JSONResponse({"summary": "No Liverpool traffic data available for this time window."})

    time_slot_counts = Counter()
    day_counts = Counter()
    port_counts = Counter()

    for b in buckets:
        ts = b["_id"]["window_start"]
        slot_hour = ts.hour
        slot_label = f"{str(slot_hour).zfill(2)}–{str((slot_hour + 6) % 24).zfill(2)}"
        day_str = ts.date().isoformat()
        port = b["_id"]["port_name"]

        time_slot_counts[slot_label] += b["arrivals"]
        day_counts[day_str] += b["arrivals"]
        port_counts[port] += b["arrivals"]

    busiest_slot = time_slot_counts.most_common(1)[0][0]
    sorted_days = day_counts.most_common()
    busiest_day = sorted_days[0][0]
    next_busy_days = [d for d, _ in sorted_days[1:3]]
    least_busy_day = min(day_counts.items(), key=lambda x: x[1])[0]
    busiest_port = port_counts.most_common(1)[0]

    # --- 2. Vessel type group analysis (Liverpool only) ---
    type_pipeline = [
        {"$match": {
            "entry_ts": {"$gte": cutoff},
            "port_name": {"$in": LIV_PORT_NAMES_ALL}
        }},
        {"$lookup": {
            "from": "vessel_details",
            "localField": "mmsi",
            "foreignField": "mmsi",
            "as": "vd"
        }},
        {"$unwind": {"path": "$vd", "preserveNullAndEmptyArrays": True}},
        {"$project": {"type_code": "$vd.Type"}}
    ]

    subtype_counts = {}
    for doc in db["port_calls"].aggregate(type_pipeline, allowDiskUse=True):
        code = doc.get("type_code")
        label = SHIP_TYPE_MAP.get(code, f"Type {code}" if code else "Unknown")
        subtype_counts[label] = subtype_counts.get(label, 0) + 1

    group_counts = {}
    for label, count in subtype_counts.items():
        group = "Other / Unknown"
        for g, subtypes in VESSEL_TYPE_GROUPS.items():
            if label in subtypes:
                group = g
                break
        group_counts[group] = group_counts.get(group, 0) + count

    most_common_group = max(group_counts.items(), key=lambda x: x[1])[0]

    # --- 3. Structured insight data ---
    insight_data = {
        "days": days,
        "busiest_day": busiest_day,
        "also_busy_days": next_busy_days,
        "least_busy_day": least_busy_day,
        "peak_time_slot_utc": busiest_slot,
        "top_port": busiest_port[0],
        "most_common_vessel_group": most_common_group
    }
    summary_llm = generate_liverpool_traffic_summary_llm(insight_data)


    return JSONResponse({
        "summary_llm": summary_llm,  # Will be filled later by OpenAI call
        "insight_data": insight_data
    })
