# src/api/endpoints/flags.py

from fastapi import APIRouter
from src.utils.flag_utils import get_flag_iso_from_mmsi

router = APIRouter()

@router.get("/api/flag/{mmsi}")
def get_flag_for_mmsi(mmsi: int):
    iso = get_flag_iso_from_mmsi(mmsi)
    if not iso:
        return {"iso": None, "url": None}
    return {
        "iso": iso,
        "url": f"https://flagcdn.com/48x36/{iso}.png"
    }
