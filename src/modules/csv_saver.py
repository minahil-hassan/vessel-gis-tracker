"""
CSV Saver Module
-----------------
This module reads a JSON file containing AIS PositionReport data and writes it
into a clean, human-readable CSV file.
"""

import json
import csv
from typing import Optional
from pathlib import Path
from src.utils.file_utils import generate_timestamped_filename
from src.utils.constants import NAV_STATUS_MAP

def save_to_csv(filepath_json: str, filepath_csv: Optional[str] = None) -> Optional[str]:

    """
    Reads a JSON file with AIS PositionReport data and saves it to a CSV file.

    Args:
        filepath_json: Path to the input JSON file containing AIS PositionReports
        filepath_csv: Optional output path for the CSV file. If not provided, a timestamped filename will be used.

    Returns:
        Path to the generated CSV file, or None if failed.
    """
    try:
        with open(filepath_json, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Failed to read or parse {filepath_json}")
        return None

    if not data:
        print("No data to write.")
        return None

    if not filepath_csv:
        filepath_csv = generate_timestamped_filename("position_reports", "csv")

    headers = [
        "MMSI/UserID",
        "Latitude",
        "Longitude",
        "COG (°)",
        "SOG (knots)",
        "True Heading (°)",
        "Navigational Status",
        "Timestamp",
        "Position Accuracy",
        "Valid Message"
    ]

    try:
        with open(filepath_csv, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()

            for row in data:
                writer.writerow({
                    "MMSI/UserID": row.get("UserID", ""),
                    "Latitude": round(row.get("Latitude", 0.0), 5),
                    "Longitude": round(row.get("Longitude", 0.0), 5),
                    "COG (°)": row.get("Cog", ""),
                    "SOG (knots)": row.get("Sog", ""),
                    "True Heading (°)": row.get("TrueHeading", ""),
                    "Navigational Status": NAV_STATUS_MAP.get(row.get("NavigationalStatus"), "Unknown"),
                    "Timestamp": row.get("Timestamp", ""),
                    "Position Accuracy": "High" if row.get("PositionAccuracy") else "Low",
                    "Valid Message": "valid" if row.get("Valid") else "invalid"
                })

        print(f"CSV file saved to: {filepath_csv}")
        return filepath_csv

    except Exception as e:
        print(f"Error writing CSV: {e}")
        return None
