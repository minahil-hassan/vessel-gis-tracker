# src/modules/transform_utils.py

from datetime import datetime
from datetime import timezone

def transform_position_report(raw_report: dict) -> dict:
    """
    Converts a raw AIS PositionReport message into schema-aligned MongoDB format
    for `latest_positions`, using GeoJSON for coordinates.
    """
    lon = raw_report.get("Longitude")
    lat = raw_report.get("Latitude")

    return {
        "mmsi": raw_report.get("UserID"),
        "timestamp_utc": datetime.now(timezone.utc),
        "coordinates": {
            "type": "Point",
            "coordinates": [lon, lat]
        },
        "sog": raw_report.get("Sog"),
        "cog": raw_report.get("Cog"),
        "heading": raw_report.get("TrueHeading"),
        "nav_status": raw_report.get("NavigationalStatus"),
        "rot": raw_report.get("RateOfTurn"),
        "position_accuracy": raw_report.get("PositionAccuracy"),
        "raim": raw_report.get("Raim"),
        "valid": raw_report.get("Valid"),
        "message_id": raw_report.get("MessageID"),
        "communication_state": raw_report.get("CommunicationState"),
        "repeat_indicator": raw_report.get("RepeatIndicator"),
        "special_manoeuvre": raw_report.get("SpecialManoeuvreIndicator"),
        "spare": raw_report.get("Spare"),
        "timestamp_raw": raw_report.get("Timestamp"),
        "source": "ais-websocket"
    }


def clean_string(value):
    return value.strip() if isinstance(value, str) else value

def transform_ship_static_data(raw: dict) -> dict:
    """
    Converts raw ShipStaticData message into MongoDB document aligned with `vessel_details` schema.
    """
    return {
    "mmsi": raw.get("UserID"),
    "AisVersion": raw.get("AisVersion"),
    "ImoNumber": raw.get("ImoNumber"),
    "Name": clean_string(raw.get("Name")),
    "Callsign": clean_string(raw.get("CallSign")),
    "Destination": clean_string(raw.get("Destination")),
    "Dte": raw.get("Dte"),
    "Eta": {
        "Day": raw.get("Eta", {}).get("Day"),
        "Hour": raw.get("Eta", {}).get("Hour"),
        "Minute": raw.get("Eta", {}).get("Minute"),
        "Month": raw.get("Eta", {}).get("Month")
    },
    "Dimension": {
        "ToBow": raw.get("Dimension", {}).get("A"),
        "ToStern": raw.get("Dimension", {}).get("B"),
        "ToPort": raw.get("Dimension", {}).get("C"),
        "ToStarboard": raw.get("Dimension", {}).get("D")
    },
    "Type": raw.get("Type"),
    "draught": raw.get("MaximumStaticDraught"),
    "last_updated": datetime.utcnow().isoformat()
}

