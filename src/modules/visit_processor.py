#src/modules/visit_processor.py
import asyncio
from datetime import datetime, timezone

# Port-level visit processing and traffic aggregation
from src.database.visit_state_updater import process_latest_positions_recent as process_port_visits

# Liverpool dock/terminal/area visit processing and traffic aggregation
from src.database.visit_state_updater_liverpool_areas import process_latest_positions_recent as process_area_visits

async def periodic_visit_processing(interval_seconds=120):
    """
    Periodically runs live vessel visit detection and traffic aggregation:
    - For all UK ports (type = "Port" in port_areas)
    - For Liverpool sub-areas (e.g., docks, terminals, locks)

    This function should be run as a background task alongside AIS streaming.
    """
    while True:
        try:
            print(f"[{datetime.now(timezone.utc)}] [Visit Processor] Starting live visit detection cycle...")

            # UK port-level visits and aggregation
            process_port_visits()

            # Liverpool area-level visits and aggregation
            process_area_visits()

            print(f"[{datetime.now(timezone.utc)}] [Visit Processor] Visit detection and aggregation complete.")

        except Exception as e:
            print(f"[{datetime.now(timezone.utc)}] [Visit Processor] Error: {e}")

        await asyncio.sleep(interval_seconds)
