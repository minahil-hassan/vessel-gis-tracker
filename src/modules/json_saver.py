# json_saver.py

"""
Module for saving AIS data to a timestamped JSON file.
"""

import json
from pathlib import Path
from src.utils.file_utils import generate_timestamped_filename

# def save_to_json(data: list, output_dir: Path = Path("data/json")) -> Path:
#     """
#     Saves AIS data to a JSON file with a timestamped filename.

#     Args:
#         data: A list of AIS messages (dictionaries)
#         output_dir: Directory where the file should be saved

#     Returns:
#         Path to the saved JSON file
#     """
#     output_dir.mkdir(parents=True, exist_ok=True)
#     filepath = output_dir / generate_timestamped_filename("uk_ships_ais", "json")

#     with open(filepath, "w") as f:
#         json.dump(data, f, indent=2)

#     print(f"Saved JSON with {len(data)} entries to {filepath}")
#     return filepath

def save_to_json(data: list, base_name: str, output_dir: Path = Path("data/json")) -> Path:
    """
    Saves data to a timestamped JSON file named after base_name (e.g., vessel_position or vessel_details).

    Args:
        data: List of dicts to save
        base_name: Short tag for file (e.g. "vessel_position", "vessel_details")
        output_dir: Output directory

    Returns:
        Path to the saved file
    """
    from bson import ObjectId

    def clean_record(record):
        return {
            k: (str(v) if isinstance(v, ObjectId) else v)
            for k, v in record.items()
            if k != "_id"
        }

    output_dir.mkdir(parents=True, exist_ok=True)
    filename = generate_timestamped_filename(base_name, "json")
    filepath = output_dir / filename

    cleaned = [clean_record(d) for d in data]

    with open(filepath, "w") as f:
        json.dump(cleaned, f, indent=2)

    print(f"Saved JSON with {len(data)} entries to {filepath}")
    return filepath


