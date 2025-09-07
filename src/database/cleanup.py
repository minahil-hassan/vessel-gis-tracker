# src/database/cleanup.py
# This module handles cleanup of old vessel positions from the database.
from datetime import datetime, timedelta
from src.database.mongo_connection import db
from datetime import timezone

def cleanup_old_vessel_positions(hours=6):
    """
    Deletes entries from latest_positions older than the specified number of hours.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    result = db["latest_positions"].delete_many({
        "timestamp_utc": {"$lt": cutoff.isoformat()}
    })
    print(f"[{datetime.now(timezone.utc)}] Cleanup complete. Deleted {result.deleted_count} outdated vessel positions.")
