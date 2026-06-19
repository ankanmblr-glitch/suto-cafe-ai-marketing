"""
Festival Intelligence Agent — pure Python, zero external dependencies.
Reads festivals.json and computes countdowns + campaign windows.
"""
from __future__ import annotations
import json
import os
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import List, Optional


@dataclass
class FestivalEntry:
    name: str
    display: str
    date: date
    days_until: int
    importance: int
    color: str
    campaign_should_start: bool
    greeting: str


@dataclass
class FestivalData:
    today_festival: Optional[str]
    today_festival_display: Optional[str]
    upcoming: List[FestivalEntry]
    active_festival: Optional[str]
    urgency: str  # immediate | high | normal | low
    source: str = "static"

    def summary(self) -> str:
        if self.today_festival:
            return f"Today is {self.today_festival_display}!"
        if self.upcoming:
            nxt = self.upcoming[0]
            return f"Next: {nxt.display} in {nxt.days_until} days"
        return "No major festivals upcoming"


class FestivalAgent:
    LEAD_TIMES = {10: 7, 9: 5, 8: 3, 7: 3, 6: 2, 5: 2, 4: 1, 3: 1, 2: 1, 1: 0}

    def __init__(self):
        data_path = os.path.join(os.path.dirname(__file__), "..", "demo_data", "festivals.json")
        with open(data_path, encoding="utf-8") as f:
            self._festivals = json.load(f)

    def run(self) -> FestivalData:
        today = date.today()
        today_festival = None
        today_festival_display = None
        upcoming: List[FestivalEntry] = []

        for fest in self._festivals:
            try:
                fdate = date(today.year, fest["month"], fest["day"])
            except ValueError:
                continue
            if fdate < today:
                try:
                    fdate = date(today.year + 1, fest["month"], fest["day"])
                except ValueError:
                    continue

            days_until = (fdate - today).days
            importance = fest.get("importance", 5)
            lead = self.LEAD_TIMES.get(importance, 1)

            greeting = fest.get("greeting_bengali") or fest.get("greeting_hindi") or f"Happy {fest['display']}!"

            if days_until == 0:
                today_festival = fest["name"]
                today_festival_display = fest["display"]

            if 0 <= days_until <= 14:
                upcoming.append(FestivalEntry(
                    name=fest["name"],
                    display=fest["display"],
                    date=fdate,
                    days_until=days_until,
                    importance=importance,
                    color=fest.get("color", "#FF8C00"),
                    campaign_should_start=days_until <= lead,
                    greeting=greeting
                ))

        upcoming.sort(key=lambda x: x.days_until)

        # Determine urgency
        if today_festival or any(f.days_until == 0 for f in upcoming):
            urgency = "immediate"
        elif any(f.days_until <= 1 and f.importance >= 8 for f in upcoming):
            urgency = "high"
        elif any(f.campaign_should_start for f in upcoming):
            urgency = "normal"
        else:
            urgency = "low"

        active = today_festival or (upcoming[0].name if upcoming and upcoming[0].campaign_should_start else None)

        return FestivalData(
            today_festival=today_festival,
            today_festival_display=today_festival_display,
            upcoming=upcoming,
            active_festival=active,
            urgency=urgency
        )
