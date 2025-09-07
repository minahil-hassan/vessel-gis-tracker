# src/api/endpoints/ai_insights.py

import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict

from fastapi import APIRouter, Query
from dotenv import load_dotenv
from openai import OpenAI

from src.database.mongo_connection import db
from src.utils.traffic_stats import (
    compute_scoped_traffic_stats,
    compute_scoped_top_ports,
)

# ----------------------------------
# Setup
# ----------------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter(prefix="/ai-insights", tags=["ai-insights"])

# ----------------------------------
# Minimal OpenAI helper (Chat Completions, no tools, no temperature)
# ----------------------------------
def call_openai_simple(system_prompt: str, user_prompt: str, max_completion_tokens: int = 450) -> str:
    """
    Simple wrapper around chat.completions (gpt-5-mini).
    - No tools, no web search, no temperature (uses model default).
    - Returns assistant message content or a short fallback string.
    """
    try:
        resp = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_completion_tokens=max_completion_tokens,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        return f"Insight unavailable (error: {e})."

# ----------------------------------
# Endpoints
# ----------------------------------
@router.get("/summary")
async def summary_insight(
    days: int = Query(7, ge=1, le=90),
    scope: str = Query("uk", pattern="^(uk|port)$"),
    port_regex: Optional[str] = None,
):
    """
    Produces a short UK/port-area summary insight using only local data + a template.
    No external tools or web search.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    stats = compute_scoped_traffic_stats(
        db, start_date, end_date, scope=scope, port_regex=port_regex
    )
    if stats["total_arrivals"] == 0:
        return {"insight": "No traffic data available for the selected period."}

    area_label = "United Kingdom" if scope == "uk" else (stats.get("area_label") or "Selected port(s)")

    system_prompt = (
        "You are a concise, professional maritime analyst. "
        "Write clearly for non-technical stakeholders. "
        "Use the provided figures as ground truth. Do not invent data or news."
    )

    user_prompt = f"""
Write a structured report with the four sections below. Keep total under 180 words. No extra sections.

Traffic Overview
- Summarize arrivals across {area_label} between {start_date.date()} and {end_date.date()} (total {stats['total_arrivals']}).

Busiest Day & Slot
- State the busiest calendar day ({stats['busiest_date']}, {stats['busiest_count']} arrivals) and the busiest 6-hour UTC slot ({stats['busiest_slot_label']}, {stats['busiest_slot_count']} arrivals), and what that implies.

Weekday vs Weekend
- Compare average weekday per day ({stats['avg_weekday_per_day']}) versus weekend per day ({stats['avg_weekend_per_day']}) in one sentence.

Spikes & Context
- Mention notable spike dates ({", ".join(stats['spike_dates']) if stats['spike_dates'] else "None"}) and give one plausible operational explanation using generic reasoning (e.g., scheduling waves, liner calls, weather windows). Avoid external news.
""".strip()

    insight = call_openai_simple(system_prompt, user_prompt, max_completion_tokens=450)
    return {"insight": insight}


@router.get("/top-ports")
async def top_ports_insight(
    days: int = Query(7, ge=1, le=90),
    scope: str = Query("uk", pattern="^(uk|port)$"),
    port_regex: Optional[str] = None,
    include_liverpool_learnings: bool = True,
):
    """
    Produces a short analysis of the top ports leaderboard, optionally framed for Liverpool.
    No external tools or web search.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    top5 = compute_scoped_top_ports(
        db, start_date, end_date, scope=scope, port_regex=port_regex, top_n=5
    )
    if not top5:
        return {"insight": "No port traffic found for the selected period."}

    top_list = "\n".join([f"{i+1}. {p['name']} — {p['arrivals']}" for i, p in enumerate(top5)])
    liverpool = next((p for p in top5 if "liverpool" in p["name"].lower()), None)
    lpl_val = (liverpool["arrivals"] if liverpool else "N/A")

    system_prompt = (
        "You are a concise, professional maritime analyst. "
        "Write clearly for non-technical stakeholders. "
        "Use the provided figures as ground truth. Do not invent data or news."
    )

    if include_liverpool_learnings:
        user_prompt = f"""
You are advising the Port of Liverpool. Write a short comparative analysis (<180 words) of the busiest UK ports between {start_date.date()} and {end_date.date()}.
Use only the figures provided. No external news.

Top 5 ports by arrivals:
{top_list}

Liverpool arrivals: {lpl_val}

Busiest Port
- Name the busiest port and one key reason it leads (cargo mix, hub role, geography—generic reasoning only).

Comparison with Liverpool
- Compare Liverpool’s role/facilities to the leader (containers, bulk, RoRo, passengers) and state one clear delta.

Strategic Insights for Liverpool
- Provide one actionable recommendation (e.g., infrastructure, scheduling, hinterland connectivity, digital ops) grounded in generic best practice.

Contextual Factors
- Offer one plausible generic factor that can influence rankings (e.g., liner schedules, seasonality, weather windows). Avoid citing external events.
""".strip()
    else:
        user_prompt = f"""
Write a concise analysis (<180 words) explaining why the following UK ports lead between {start_date.date()} and {end_date.date()}.
Use only the figures provided. No external news.

Top 5 ports by arrivals:
{top_list}

Leaders & Roles
- Explain briefly why top ports rank highly (cargo mix, hub status, connectivity—generic reasoning only).

Operational Themes
- State one common operational theme across leaders (berth capacity, turnaround, reliability, hinterland links).

Contextual Factors
- Note one general factor that may affect rankings (seasonality, liner schedules, weather windows).

Actionable Takeaway
- Provide one practical takeaway for UK port stakeholders in a single sentence.
""".strip()

    insight = call_openai_simple(system_prompt, user_prompt, max_completion_tokens=450)
    return {"insight": insight}
