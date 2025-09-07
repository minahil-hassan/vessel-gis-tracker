#visit_processor_runner
import asyncio
from datetime import datetime, timezone
from src.modules.visit_processor import periodic_visit_processing  # For handling visits and port calls

async def main():
    interval_seconds = 120  # Frequency of visit processing
    print(f"[{datetime.now(timezone.utc)}] Starting visit processor runner (interval: {interval_seconds}s)...")
    try:
        while True:
            await periodic_visit_processing(interval_seconds=interval_seconds)
            await asyncio.sleep(0.1)  # Prevent tight loop
    except KeyboardInterrupt:
        print("\nVisit processor interrupted by user. Exiting cleanly.")
    except Exception as e:
        print(f"[{datetime.now(timezone.utc)}] Fatal error: {e}")

if __name__ == "__main__":
    asyncio.run(main())