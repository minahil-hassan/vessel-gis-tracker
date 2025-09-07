"""
Normalize ONLY the `coordinates` field in `vessel_position` to GeoJSON Point.
- If `coordinates` is a 2-item list/tuple [lon, lat], convert it to:
    {"type": "Point", "coordinates": [lon, lat]}
- If it's already a GeoJSON Point dict, leave it.
- No swapping, no timestamp changes, no field removals.

Run first with DRY_RUN=true to preview, then DRY_RUN=false to apply.
"""

import os
from typing import Any, Tuple, Optional

from pymongo import UpdateOne
from src.database.mongo_connection import get_mongo_connection

DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "5000"))

def _extract_pair(x: Any) -> Optional[Tuple[float, float]]:
    """Return (lon, lat) if x is a 2-item list/tuple of numbers; else None."""
    if isinstance(x, (list, tuple)) and len(x) == 2:
        try:
            return float(x[0]), float(x[1])
        except Exception:
            return None
    return None

def _is_geojson_point(x: Any) -> bool:
    """True if x looks like {"type":"Point","coordinates":[lon,lat]}."""
    if not isinstance(x, dict):
        return False
    if x.get("type") != "Point":
        return False
    coords = x.get("coordinates")
    return isinstance(coords, (list, tuple)) and len(coords) == 2

def normalize_coords_only():
    db = get_mongo_connection()
    coll = db["vessel_position"]

    scanned = 0
    candidates = 0
    updated = 0
    skipped_bad_list = 0

    ops = []

    # Project only what we need for speed
    cursor = coll.find(
        {},
        projection={"_id": 1, "coordinates": 1},
        no_cursor_timeout=True,
    )

    try:
        for doc in cursor:
            scanned += 1
            _id = doc["_id"]
            coords = doc.get("coordinates")

            # Already a proper GeoJSON Point -> skip
            if _is_geojson_point(coords):
                continue

            # If it's a 2-item list/tuple -> convert
            pair = _extract_pair(coords)
            if pair is None:
                # not a list/tuple we know; leave as-is
                skipped_bad_list += 1
                continue

            candidates += 1
            lon, lat = pair
            geo = {"type": "Point", "coordinates": [lon, lat]}

            if not DRY_RUN:
                ops.append(UpdateOne({"_id": _id}, {"$set": {"coordinates": geo}}))

                if len(ops) >= BATCH_SIZE:
                    coll.bulk_write(ops, ordered=False)
                    updated += len(ops)
                    ops.clear()

        if not DRY_RUN and ops:
            coll.bulk_write(ops, ordered=False)
            updated += len(ops)

    finally:
        cursor.close()

    mode = "APPLIED"
    print(
        f"[normalize_coords_only:{mode}] scanned={scanned}, "
        f"list_candidates={candidates}, updated={updated}, skipped_nonlist_or_unusable={skipped_bad_list}"
    )

if __name__ == "__main__":
    normalize_coords_only()
