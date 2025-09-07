from datetime import datetime, timedelta
from typing import Dict
from openai import OpenAI

client = OpenAI()  
def format_liverpool_prompt(insight_data: Dict) -> str:
    days = insight_data["days"]
    end_date = datetime.now().date()
    start_date = (datetime.now() - timedelta(days=days)).date()

    return f"""You are a concise maritime data analyst writing for the Port of Liverpool dashboard.
Write a clear, non-technical summary of vessel traffic between {start_date} and {end_date}.
Use only the provided figures as ground truth. Be specific and limit your response to 180 words.

Include the following:

1. **Busiest Day** – State which day saw the most vessel traffic and compare it to other busy days.
2. **Quietest Day** – Mention the least busy day and how it contrasts.
3. **Peak Slot** – Indicate which 6-hour time slot had the highest concentration of vessel movements.
4. **Top Sub-Port** – Identify which Liverpool port area handled the most traffic.
5. **Vessel Type Insight** – Highlight the most common vessel group and what this suggests about operational focus.
6. **Operational Signal** – Provide one general insight Liverpool Port managers could act on (e.g., berth use, vessel mix, or coordination).
7. **Actionable Takeaway** – End with a useful takeaway for the Liverpool port team. What can Liverpool learn from ports with higher traffic like Southampton port and London port? Which infrastructure improvement would be most useful considering the data available?

Use simple, structured language and do not include any external references or speculation."""

def format_uk_prompt(insight_data: Dict) -> str:
    days = insight_data["days"]
    end_date = datetime.now().date()
    start_date = (datetime.now() - timedelta(days=days)).date()

    return f"""You are a professional maritime data analyst providing a national UK port summary.
Use only the figures provided. The reporting window is from {start_date} to {end_date}.
Keep your summary under 180 words and write clearly for port operators and decision-makers.

Cover the following sections:

1. **Busiest Port** – Identify the most active UK port and suggest one generic reason why it leads (e.g., location, cargo mix).
2. **Common Vessel Type** – State which vessel type group dominated and what this implies.
3. **Operational Theme** – Point out one shared operational pattern across active ports (e.g., turnaround time, reliability). What are the port facilities and capacities at the busiest port that differ from the Port of Liverpool?
4. **Contextual Factor** – Suggest one general influence on rankings (e.g., weather, schedules, seasonality).
5. **Actionable Takeaway** – End with one useful insight for UK port stakeholders.

Avoid external news or assumptions. Use structured, factual language with a concise tone."""


def generate_uk_traffic_summary_llm(insight_data: Dict) -> str:
    prompt = format_uk_prompt(insight_data)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

def generate_liverpool_traffic_summary_llm(insight_data: Dict) -> str:
    prompt = format_liverpool_prompt(insight_data)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()