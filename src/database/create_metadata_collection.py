# src/database/create_vessel_collections_metadata.py

from datetime import datetime
from mongo_connection import get_mongo_connection

def create_vessel_collections_metadata():
    """
    Creates metadata documents describing each MongoDB collection
    used in the AIS vessel tracking system. This metadata will be stored
    in the 'vessel_collections_metadata' collection for reference and documentation.
    """

    db = get_mongo_connection()
    metadata_col = db["vessel_collections_metadata"]

    metadata_docs = [
        {
            "collection_name": "latest_positions",
            "description": "Holds the most recent AIS position report for each vessel, identified by MMSI.",
            "data_source": "Real-time AIS via WebSocket from https://aisstream.io/",
            "update_frequency": "Real-time - every 30 seconds (updated per new PositionReport message per vessel)",
            "author": "Minahil Tariq",
            "created_at": datetime.utcnow()
        },
        {
            "collection_name": "vessel_position",
            "description": "Stores historical AIS position reports for all vessels, with full message content and timestamps.",
            "data_source": "Real-time AIS via WebSocket from https://aisstream.io/",
            "update_frequency": "Every 30 minutes - snapshot of latest_positions",
            "author": "Minahil Tariq",
            "created_at": datetime.utcnow()
        },
        {
            "collection_name": "vessel_details",
            "description": "Static metadata for vessels that is unlikely to change after a journey starts (e.g., name, type, dimensions, IMO, callsign, destination).",
            "data_source": "Static AIS messages via WebSocket from https://aisstream.io/",
            "update_frequency": "Updated on new ShipStaticData messages or when new MMSI appears",
            "author": "Minahil Tariq",
            "created_at": datetime.utcnow()
        },
        {
            "collection_name": "ports",
            "description": "Geospatial dataset of UK ports with location coordinates and LOCODEs.",
            "data_source": "https://www.vesselfinder.com/ports?country=gb and UN/LOCODE database",
            "update_frequency": "One-time import, manually updated when new port data available",
            "author": "Minahil Tariq",
            "created_at": datetime.utcnow()
        },
        {
            "collection_name": "port_areas",
            "description": "GeoJSON polygons defining port boundaries and dock, terminal, facility boundaries within major UK ports.",
            "data_source": "Custom-created using geojson.io and clustering AIS data (DBSCAN + convex hull).",
            "update_frequency": "Manually updated as new boundaries are digitised",
            "author": "Minahil Tariq",
            "created_at": datetime.utcnow()
        },
        {
            "collection_name": "port_calls",
            "description": "Records vessel arrivals and departures at ports (entry→exit events). Derived from AIS visit detection pipeline.",
            "data_source": "Derived from vessel_position and ports collections",
            "update_frequency": "Real-time via visit_state_updater pipeline",
            "author": "Minahil Tariq",
            "created_at": datetime.utcnow()
        },
        {
            "collection_name": "visit_state",
            "description": "Ephemeral state store tracking whether a vessel is currently in a port, used to debounce entry/exit detection.",
            "data_source": "Derived from vessel_position with point-in-polygon checks against ports",
            "update_frequency": "Updated continuously in real-time",
            "author": "Minahil Tariq",
            "created_at": datetime.utcnow()
        },
        {
            "collection_name": "visit_state_areas",
            "description": "Ephemeral state store tracking whether a vessel is currently inside a dock/terminal polygon (sub-port level).",
            "data_source": "Derived from vessel_position with point-in-polygon checks against port_areas",
            "update_frequency": "Updated continuously in real-time",
            "author": "Minahil Tariq",
            "created_at": datetime.utcnow()
        },
        {
            "collection_name": "area_calls",
            "description": "Records vessel arrivals and departures for dock/terminal areas (entry→exit events).",
            "data_source": "Derived from vessel_position and port_areas collections",
            "update_frequency": "Real-time via visit_state_areas pipeline",
            "author": "Minahil Tariq",
            "created_at": datetime.utcnow()
        },
        {
            "collection_name": "area_traffic",
            "description": "Aggregated vessel traffic statistics per dock/terminal, binned into 6-hour or daily buckets.",
            "data_source": "Aggregated from area_calls collection",
            "update_frequency": "Every 6 hours",
            "author": "Minahil Tariq",
            "created_at": datetime.utcnow()
        },
        {
            "collection_name": "port_traffic",
            "description": "Aggregated vessel traffic statistics per port, binned into 6-hour or daily buckets.",
            "data_source": "Aggregated from port_calls collection",
            "update_frequency": "Every 6 hours",
            "author": "Minahil Tariq",
            "created_at": datetime.utcnow()
        }
    ]

    result = metadata_col.insert_many(metadata_docs)
    print(f"Inserted {len(result.inserted_ids)} metadata documents into 'vessel_collections_metadata'")

if __name__ == "__main__":
    create_vessel_collections_metadata()
