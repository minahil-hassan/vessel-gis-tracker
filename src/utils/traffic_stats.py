from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Optional
from pymongo.collection import Collection


def _date_range_list(start: datetime, end: datetime) -> List[str]:
    """Inclusive start, exclusive end by whole days, returned as ISO yyyy-mm-dd strings."""
    days = (end.date() - start.date()).days
    return [(start.date() + timedelta(days=i)).isoformat() for i in range(days)]


def _weekday(date_iso: str) -> int:
    """0=Mon .. 6=Sun for an ISO date string."""
    return datetime.fromisoformat(date_iso).weekday()


def _six_hour_label(start_hour: int) -> str:
    """Format 6h slot label like '00–06', given UTC starting hour 0/6/12/18."""
    return f"{start_hour:02d}–{(start_hour + 6) % 24:02d}"


def compute_scoped_traffic_stats(
    db,
    start: datetime,
    end: datetime,
    scope: str = "uk",
    port_regex: Optional[str] = None,
) -> Dict:
    """
    Compute stats for AI insights using the SAME sources as your public endpoints.

    - Daily totals & weekday/weekend averages -> from `port_calls` (entry_ts)
    - Busiest 6h slot                         -> from `port_traffic` (window_start, arrivals)
    - Optional scoping by port_name regex     -> same semantics as /traffic endpoints

    Returns:
      {
        area_label,
        total_arrivals,
        busiest_date, busiest_count,
        busiest_slot_label, busiest_slot_count,
        avg_weekday_per_day, avg_weekend_per_day,
        spike_dates
      }
    """

    # -----------------------------
    # 1) Daily totals from port_calls
    # -----------------------------
    calls: Collection = db["port_calls"]

    match_calls = {"entry_ts": {"$gte": start}}
    # Your /traffic endpoints use "last N days" with lower bound only; mirror that.
    # If you want to hard-cap to "now", uncomment:
    # match_calls["entry_ts"]["$lt"] = end

    if scope == "port" and port_regex:
        match_calls["port_name"] = {"$regex": port_regex, "$options": "i"}

    pipe_calls = [
        {"$match": match_calls},
        {
            "$project": {
                "day": {"$dateToString": {"format": "%Y-%m-%d", "date": "$entry_ts"}},
                "port_name": 1,
            }
        },
        {"$group": {"_id": "$day", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
    ]

    rows_calls = list(calls.aggregate(pipe_calls, allowDiskUse=True))
    per_day = Counter({r["_id"]: int(r["count"]) for r in rows_calls})
    total_arrivals = sum(per_day.values())

    if per_day:
        busiest_date, busiest_count = max(per_day.items(), key=lambda kv: kv[1])
    else:
        busiest_date, busiest_count = "N/A", 0

    # -----------------------------
    # 2) Busiest 6h slot from port_traffic
    # -----------------------------
    traffic: Collection = db["port_traffic"]

    match_traffic = {"window_start": {"$gte": start}}
    # If you want upper bound:
    # match_traffic["window_start"]["$lt"] = end

    if scope == "port" and port_regex:
        match_traffic["port_name"] = {"$regex": port_regex, "$options": "i"}

    pipe_traffic = [
        {"$match": match_traffic},
        {
            "$project": {
                "h": {"$hour": "$window_start"},  # 0..23 UTC
                "arrivals": {"$ifNull": ["$arrivals", 0]},
            }
        },
        # `port_traffic` windows already represent 6-hour buckets starting at 0/6/12/18.
        # We can just sum by the starting hour modulo 6.
        {"$group": {"_id": {"slot_start": {"$multiply": [{"$floor": {"$divide": ["$h", 6]}}, 6]}}, 
                    "arrivals": {"$sum": "$arrivals"}}},
        {"$project": {"slot_start": "$_id.slot_start", "arrivals": 1, "_id": 0}},
        {"$sort": {"arrivals": -1}},
    ]

    slot_rows = list(traffic.aggregate(pipe_traffic, allowDiskUse=True))
    if slot_rows:
        # Pick the max summed slot across all ports
        best = max(slot_rows, key=lambda r: r["arrivals"])
        busiest_slot_start = int(best["slot_start"])
        busiest_slot_count = int(best["arrivals"])
        busiest_slot_label = _six_hour_label(busiest_slot_start)
    else:
        busiest_slot_label, busiest_slot_count = "00–06", 0

    # -----------------------------
    # 3) Weekday vs weekend averages (per day)
    # -----------------------------
    date_list = _date_range_list(start, end)
    weekday_dates = [d for d in date_list if _weekday(d) < 5]
    weekend_dates = [d for d in date_list if _weekday(d) >= 5]

    weekday_total = sum(per_day.get(d, 0) for d in weekday_dates)
    weekend_total = sum(per_day.get(d, 0) for d in weekend_dates)

    avg_weekday_per_day = round(weekday_total / max(1, len(weekday_dates)), 2)
    avg_weekend_per_day = round(weekend_total / max(1, len(weekend_dates)), 2)

    # -----------------------------
    # 4) Spike detection (> 1.25 * median)
    # -----------------------------
    counts = sorted(per_day.values())
    if counts:
        mid = len(counts) // 2
        median = counts[mid] if len(counts) % 2 == 1 else 0.5 * (counts[mid - 1] + counts[mid])
        threshold = 1.25 * median if median else 0
        spike_dates = [d for d, c in per_day.items() if c > threshold]
    else:
        spike_dates = []

    area_label = "United Kingdom" if scope == "uk" else "Selected port(s)"

    return {
        "area_label": area_label,
        "total_arrivals": int(total_arrivals),
        "busiest_date": busiest_date,
        "busiest_count": int(busiest_count),
        "busiest_slot_label": busiest_slot_label,
        "busiest_slot_count": int(busiest_slot_count),
        "avg_weekday_per_day": avg_weekday_per_day,
        "avg_weekend_per_day": avg_weekend_per_day,
        "spike_dates": spike_dates,
    }


def compute_scoped_top_ports(
    db,
    start: datetime,
    end: datetime,
    scope: str = "uk",
    port_regex: Optional[str] = None,
    top_n: int = 5,
) -> List[Dict]:
    """
    Top N ports by arrivals using `port_calls` (entry_ts), mirroring /traffic endpoints.
    For UK leaderboard cards, we intentionally compute **UK-wide** ranking (no regex),
    so Liverpool can be compared to national leaders. If you want scoped leaders,
    flip the match to include regex when scope == "port".
    """

    calls: Collection = db["port_calls"]

    # UK-wide ranking by default (to match your "Top 5 ports by traffic" section).
    match_calls = {"entry_ts": {"$gte": start}}
    # Optional strict end bound:
    # match_calls["entry_ts"]["$lt"] = end

    # If you prefer a scoped leaderboard, uncomment:
    # if scope == "port" and port_regex:
    #     match_calls["port_name"] = {"$regex": port_regex, "$options": "i"}

    pipeline = [
        {"$match": match_calls},
        {"$group": {"_id": "$port_name", "arrivals": {"$sum": 1}}},
        {"$project": {"_id": 0, "name": "$_id", "arrivals": 1}},
        {"$match": {"name": {"$ne": None}}},
        {"$sort": {"arrivals": -1}},
        {"$limit": int(top_n)},
    ]

    rows = list(calls.aggregate(pipeline, allowDiskUse=True))
    return [{"name": r["name"], "arrivals": int(r["arrivals"])} for r in rows if r.get("name")]
