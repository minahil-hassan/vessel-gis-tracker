# """
# vehicle-gis-platform/ais_stream_runner.py

# Runs long-lived AIS background tasks:
#   1) Live AIS WebSocket collector
#   2) Periodic DB cleanup of stale 'latest_positions'
#   3) (Optional) Visit-state processing

# Designed to shut down cleanly on SIGINT/SIGTERM (Ctrl+C in Git Bash/WSL).
# """

# import asyncio
# import signal
# from datetime import datetime, timezone

# # Your project modules live under ./src, and PYTHONPATH is set in start.sh
# from src.modules.ais_collector import run_continuous_ais_stream
# from src.database.cleanup import cleanup_old_vessel_positions
# from src.modules.visit_processor import periodic_visit_processing


# # Global shutdown event toggled by signal handlers
# _shutdown = asyncio.Event()


# def _install_signal_handlers(loop: asyncio.AbstractEventLoop) -> None:
#     """
#     Ensure SIGINT/SIGTERM stop the runner. On Windows, add_signal_handler may
#     not be implemented; fall back to signal.signal.
#     """
#     def _set_shutdown(*_args):
#         _shutdown.set()

#     for sig in (signal.SIGINT, signal.SIGTERM):
#         try:
#             loop.add_signal_handler(sig, _shutdown.set)
#         except NotImplementedError:
#             # Windows CPython without Proactor can hit this path
#             signal.signal(sig, _set_shutdown)


# async def periodic_cleanup_task(*, interval_minutes: int = 60, hours: int = 6) -> None:
#     """
#     Periodically delete stale entries from 'latest_positions'.
#     Wakes early and exits when shutdown is requested.
#     """
#     print(f"[{datetime.now(timezone.utc)}] cleanup task started (every {interval_minutes}m, prune>{hours}h)")
#     while not _shutdown.is_set():
#         # Sleep in a way that can be interrupted by shutdown
#         try:
#             await asyncio.wait_for(_shutdown.wait(), timeout=interval_minutes * 60)
#         except asyncio.TimeoutError:
#             pass  # timeout -> run cleanup
#         if _shutdown.is_set():
#             break

#         try:
#             cleanup_old_vessel_positions(hours=hours)
#             print(f"[{datetime.now(timezone.utc)}] cleanup completed.")
#         except Exception as e:
#             print(f"[{datetime.now(timezone.utc)}] cleanup error: {e}")


# async def visits_task(*, interval_seconds: int = 120) -> None:
#     """
#     Wrap visit processing to make it cooperative with cancellation.
#     """
#     print(f"[{datetime.now(timezone.utc)}] visit processing task started (every {interval_seconds}s)")
#     try:
#         # Run your existing processor which sleeps internally; we gate by shutdown.
#         while not _shutdown.is_set():
#             await periodic_visit_processing(interval_seconds=interval_seconds)
#             # If the internal function returns, short delay prevents tight loop
#             await asyncio.sleep(0.1)
#     except asyncio.CancelledError:
#         # Graceful exit on cancellation
#         pass
#     except Exception as e:
#         print(f"[{datetime.now(timezone.utc)}] visit processing error: {e}")


# async def ais_stream_task() -> None:
#     """
#     Run the live AIS stream. If your collector function is long-running and
#     internally awaits, cancellation will propagate cleanly.
#     """
#     print(f"[{datetime.now(timezone.utc)}] AIS stream task starting…")
#     try:
#         await run_continuous_ais_stream()
#     except asyncio.CancelledError:
#         pass
#     except Exception as e:
#         print(f"[{datetime.now(timezone.utc)}] AIS stream error: {e}")


# async def main() -> None:
#     """
#     Entry point that starts all services and waits for a shutdown signal.
#     """
#     print(f"[{datetime.now(timezone.utc)}] Starting AIS services (collector + cleanup + visits)…")
#     loop = asyncio.get_running_loop()
#     _install_signal_handlers(loop)

#     tasks = [
#         asyncio.create_task(ais_stream_task(), name="ais_stream"),
#         asyncio.create_task(periodic_cleanup_task(interval_minutes=60, hours=6), name="cleanup"),
#         asyncio.create_task(visits_task(interval_seconds=120), name="visits"),
#     ]

#     # Wait until a signal arrives
#     await _shutdown.wait()

#     # Graceful cancellation of child tasks
#     for t in tasks:
#         t.cancel()
#     for t in tasks:
#         try:
#             await t
#         except asyncio.CancelledError:
#             pass

#     print(f"[{datetime.now(timezone.utc)}] AIS services stopped.")


# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         # Fallback if signals aren’t wired
#         pass

# src/ais_stream_runner.py
# This script runs the AIS data collector and periodically (every hour) cleans up old vessel positions.

import asyncio
from datetime import datetime, timezone
from src.modules.ais_collector import run_continuous_ais_stream #for listening to AIS data
from src.database.cleanup import cleanup_old_vessel_positions #for deleting old vessel positions

async def periodic_cleanup_task(interval_minutes=60, hours=24):
    """
    Periodically delete stale entries from the latest_positions collection.
    """
    while True:
        await asyncio.sleep(interval_minutes * 60)
        print(f"[{datetime.now(timezone.utc)}] Running cleanup task to remove old entries...")
        try:
            cleanup_old_vessel_positions(hours=hours)
        except Exception as e:
            print(f"[{datetime.now(timezone.utc)}] Cleanup error: {e}")

async def main():
    # Launch the cleanup task in the background
    asyncio.create_task(periodic_cleanup_task(interval_minutes=60, hours=6))

    # Start AIS stream collector (runs forever)
    await run_continuous_ais_stream()

if __name__ == "__main__":
    try:
        print(f"[{datetime.now(timezone.utc)}] Starting AIS stream runner with cleanup...")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCollector interrupted by user. Exiting cleanly.")
    except Exception as e:
        print(f"[{datetime.now(timezone.utc)}] Fatal error: {e}")