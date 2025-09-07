# src/modules/ais_collector.py
# This module connects to the AIS WebSocket and collects data continuously.
import asyncio
import websockets
import json
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from src.database.insert_ais_data import insert_or_update_vessel_details
from src.database.insert_latest_position import upsert_latest_position
from src.modules.transform_utils import transform_position_report, transform_ship_static_data
from src.database.mongo_connection import get_mongo_connection

load_dotenv()

async def run_continuous_ais_stream():
    """
    Connects to the AIS WebSocket and listens for incoming messages.
    Transforms and inserts PositionReport and ShipStaticData into MongoDB.
    This function runs indefinitely, processing messages as they arrive.
    """
    API_KEY = os.getenv("AIS_API_KEY")
    if not API_KEY:
        raise ValueError("API key not found in .env")

    subscription = {
        "APIKey": API_KEY,
        "BoundingBoxes": [[[49.5, -11.0], [61.0, 2.0]]],  # UK region
        "FilterMessageTypes": ["PositionReport", "ShipStaticData"]
    }

    print(f"[{datetime.now(timezone.utc)}] Connecting to AIS WebSocket...")

    try:
        async with websockets.connect("wss://stream.aisstream.io/v0/stream") as ws:
            await ws.send(json.dumps(subscription))
            print(f"[{datetime.now(timezone.utc)}] Connected and streaming...")
            asyncio.create_task(snapshot_latest_positions_every_15_minutes())
            while True:
                try:
                    msg_json = await asyncio.wait_for(ws.recv(), timeout=30)
                    message = json.loads(msg_json)

                    if message.get("MessageType") == "PositionReport":
                        report = message["Message"]["PositionReport"]
                        transformed = transform_position_report(report)
                        upsert_latest_position(transformed)

                    elif message.get("MessageType") == "ShipStaticData":
                        static = message["Message"]["ShipStaticData"]
                        transformed = transform_ship_static_data(static)
                        print(f"[{datetime.now(timezone.utc)}] Inserting/updating vessel details for MMSI {transformed.get('mmsi')}")
                        insert_or_update_vessel_details([transformed])

                except asyncio.TimeoutError:
                    print(f"[{datetime.now(timezone.utc)}] Timeout - no AIS messages. Still listening...")

    except Exception as e:
        print(f"[{datetime.now(timezone.utc)}]  WebSocket connection error: {e}")

async def snapshot_latest_positions_every_15_minutes():
    """
    Background task to periodically copy all records from `latest_positions`
    into `vessel_position` every 30 minutes to build history.
    """
    db = get_mongo_connection()
    while True:
        try:
            latest_docs = list(db["latest_positions"].find())
            if latest_docs:
                for doc in latest_docs:
                    doc.pop("_id", None)
                db["vessel_position"].insert_many(latest_docs)
                print(f"[{datetime.now(timezone.utc)}] Snapshot: Inserted {len(latest_docs)} into vessel_position.")
            else:
                print(f"[{datetime.now(timezone.utc)}] Snapshot: No records to sync.")
        except Exception as e:
            print(f"[{datetime.now(timezone.utc)}] Snapshot Error: {e}")

        await asyncio.sleep(900)  # 15 minutes


