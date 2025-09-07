from src.database.mongo_connection import get_mongo_connection

def get_flag_iso_from_mmsi(mmsi):
    """
    Extract MID from MMSI and retrieve ISO flag code from MongoDB.
    
    Args:
        mmsi (int or str): Maritime Mobile Service Identity
    
    Returns:
        str: ISO code like 'gb' or None if not found
    """
    try:
        mid = int(str(mmsi)[:3])  # Get first 3 digits as MID
        db = get_mongo_connection()
        flags = db["mmsi_flags"]
        result = flags.find_one({"MID": mid})
        return result["ISO"] if result else None
    except Exception as e:
        print(f"Error resolving flag for MMSI {mmsi}: {e}")
        return None
