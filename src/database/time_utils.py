# src/database/time_utils.py
from datetime import datetime, timezone

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def to_iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")

def parse_mongo_ts(ts) -> datetime:
    if isinstance(ts, datetime):
        return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)
    if isinstance(ts, str):
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return now_utc()

def floor_to_6h(dt: datetime) -> datetime:
    dt = parse_mongo_ts(dt)
    h = (dt.hour // 6) * 6
    return dt.replace(hour=h, minute=0, second=0, microsecond=0)

def minutes_between(a: datetime, b: datetime) -> int:
    a = parse_mongo_ts(a)
    b = parse_mongo_ts(b)
    return int(round((b - a).total_seconds() / 60.0))
