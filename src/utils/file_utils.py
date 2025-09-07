from datetime import datetime
from pathlib import Path

def generate_timestamped_filename(base_name: str, extension: str = "json") -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.{extension}"
