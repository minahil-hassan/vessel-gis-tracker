# src/api/endpoints/dashboard_liverpool.py

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta, timezone

from src.database.mongo_connection import db
from src.utils.constants import SHIP_TYPE_MAP, VESSEL_TYPE_GROUPS

router = APIRouter()

# ---- Liverpool ports scope (canonical names + common typo) ----
LIV_PORT_NAMES_CANON = ["Birkenhead Dock Estate", "Port of Liverpool", "Port of Garston"]
LIV_PORT_NAMES_ALIASES = ["Port of Gartson"]  # typo variant occasionally present
LIV_PORT_NAMES_ALL = LIV_PORT_NAMES_CANON + LIV_PORT_NAMES_ALIASES


@router.get("/", summary="UK and Liverpool Dashboard Stats")
def get_dashboard_stats(days: int = 7):
    """
    Returns top-level dashboard stats for:
      - UK: snapshot metrics from latest_positions (total_vessels, grouped types, top destinations)
      - Liverpool: recent-arrivals volume (last N days) across specific ports, avg speed (from recent positions),
                   and grouped vessel types (from port_calls joined to vessel_details).
    NOTE: 'days' applies to the Liverpool sections (arrivals + grouped types) and not to UK snapshot, which is by design.
    """

    # ------------------------------
    # UK: snapshot from latest_positions
    # ------------------------------
    vessel_docs = list(db["latest_positions"].find({}, {"_id": 0}))
    total_vessels = len(vessel_docs)

    if total_vessels:
        avg_speed = round(
            sum([(v.get("sog", 0) or 0) for v in vessel_docs]) / total_vessels, 2
        )
    else:
        avg_speed = 0.0

    # last_update (max timestamp as ISO string, if present)
    valid_timestamps = [
        v.get("timestamp_utc")
        for v in vessel_docs
        if isinstance(v.get("timestamp_utc"), str) and v.get("timestamp_utc")
    ]
    last_update = max(valid_timestamps) if valid_timestamps else None

    # Join to vessel_details for type/destination
    mmsi_list = [v.get("mmsi") for v in vessel_docs if v.get("mmsi")]
    details_lookup = {
        d["mmsi"]: d
        for d in db["vessel_details"].find(
            {"mmsi": {"$in": mmsi_list}}, {"_id": 0, "mmsi": 1, "Type": 1, "Destination": 1}
        )
    }

    # subtype counts + top destinations (UK)
    type_counts_uk = {}
    destination_counts = {}
    for m in mmsi_list:
        det = details_lookup.get(m, {})
        tcode = det.get("Type")
        tlabel = SHIP_TYPE_MAP.get(tcode, f"Type {tcode}" if tcode else "Unknown")
        type_counts_uk[tlabel] = type_counts_uk.get(tlabel, 0) + 1

        dest = (det.get("Destination") or "").strip()
        if dest:
            destination_counts[dest] = destination_counts.get(dest, 0) + 1

    # Map subtypes -> groups (UK)
    grouped_subtypes_uk = {}
    for label, cnt in type_counts_uk.items():
        placed = False
        for group, subtypes in VESSEL_TYPE_GROUPS.items():
            if label in subtypes:
                grouped_subtypes_uk.setdefault(group, []).append((label, cnt))
                placed = True
                break
        if not placed:
            grouped_subtypes_uk.setdefault("Other / Unknown", []).append((label, cnt))

    grouped_vessel_types_uk = {
        g: {sub: c for sub, c in subs}
        for g, subs in grouped_subtypes_uk.items()
    }

    top_destinations = [
        d
        for (d, _) in sorted(destination_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ]

    # ------------------------------
    # Liverpool: last N days (arrivals + grouped types across specific ports)
    # ------------------------------
    since = datetime.now(timezone.utc) - timedelta(days=days)

    # 1) Arrivals volume across the three Liverpool ports (count of port_calls)
    volume_pipeline = [
        {"$match": {"entry_ts": {"$gte": since}, "port_name": {"$in": LIV_PORT_NAMES_ALL}}},
        {"$count": "arrivals"},
    ]
    vol_res = list(db["port_calls"].aggregate(volume_pipeline))
    liverpool_arrivals = int(vol_res[0]["arrivals"]) if vol_res else 0

    # 2) Average speed from recent vessel positions near these ports (optional best-effort)
    #    If you prefer, you can replace this with an average dwell or other metric.
    #    Here we just look at recent positions (last N days) and average SOG for vessels whose
    #    last known port_call in that window is one of the Liverpool ports.
    #    If that's too heavy, you can omit or compute from vessel_position bbox; we keep it simple:
    recent_positions = list(
        db["vessel_position"].find(
            {"timestamp_utc": {"$gte": since}}, {"_id": 0, "mmsi": 1, "sog": 1}
        ).limit(200000)  # sanity cap; adjust if needed
    )
    if recent_positions:
        avg_liverpool_speed = round(
            sum([(v.get("sog", 0) or 0) for v in recent_positions]) / len(recent_positions),
            2,
        )
    else:
        avg_liverpool_speed = 0.0

    # 3) Grouped vessel types from port_calls joined to vessel_details (Liverpool scope)
    type_pipeline = [
        {
            "$match": {
                "entry_ts": {"$gte": since},
                "port_name": {"$in": LIV_PORT_NAMES_ALL},
            }
        },
        {
            "$lookup": {
                "from": "vessel_details",
                "localField": "mmsi",
                "foreignField": "mmsi",
                "as": "vd",
            }
        },
        {"$unwind": {"path": "$vd", "preserveNullAndEmptyArrays": True}},
        {"$project": {"_id": 0, "type_code": "$vd.Type"}},
    ]
    subtype_counts_liv = {}
    for doc in db["port_calls"].aggregate(type_pipeline, allowDiskUse=True):
        tcode = doc.get("type_code")
        tdesc = SHIP_TYPE_MAP.get(tcode, f"Type {tcode}" if tcode is not None else "Unknown")
        subtype_counts_liv[tdesc] = subtype_counts_liv.get(tdesc, 0) + 1

    grouped_vessel_types_liv = {}
    for label, cnt in subtype_counts_liv.items():
        grp = "Other / Unknown"
        for gname, subs in VESSEL_TYPE_GROUPS.items():
            if label in subs:
                grp = gname
                break
        grouped_vessel_types_liv[grp] = grouped_vessel_types_liv.get(grp, 0) + cnt

    # ------------------------------
    # Response
    # ------------------------------
    return JSONResponse(
        {
            "uk": {
                "total_vessels": total_vessels,
                "avg_speed": avg_speed,
                "last_update": last_update,
                "grouped_vessel_types": grouped_vessel_types_uk,
                # Back-compat alias (some old frontend expects this key):
                "type_groups": grouped_vessel_types_uk,
                "top_destinations": top_destinations,
            },
            "liverpool": {
                # Renamed for generality (parameterized by ?days=):
                "vessel_count": liverpool_arrivals,  # arrivals across the three ports
                "avg_speed": avg_liverpool_speed,
                "grouped_vessel_types": grouped_vessel_types_liv,
                # Back-compat (optional; remove once frontend is migrated):
                "vessel_count_last_3d": liverpool_arrivals,
                "avg_speed_last_3d": avg_liverpool_speed,
            },
        }
    )

