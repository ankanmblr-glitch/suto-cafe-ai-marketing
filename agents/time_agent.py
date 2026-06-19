"""
Time-Based Promotion Agent — pure Python.
Analyzes current time → meal period, rush score, best posting window.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TimeData:
    hour: int
    day_name: str
    day_type: str          # weekday | weekend
    meal_period: str       # breakfast | brunch | lunch | snack | dinner | late_night
    rush_score: float      # 0.0 - 1.0
    post_now: bool         # True if now is a good time to post
    best_post_time: str    # e.g. "7:30 PM"
    items_for_period: list
    period_headline: str

    def summary(self) -> str:
        return f"{self.day_name} {self.meal_period} (rush: {self.rush_score:.0%}) — post at {self.best_post_time}"


class TimeAgent:
    PERIOD_ITEMS = {
        "breakfast":   ["Cappuccino", "Masala Chai", "Paneer Sandwich", "Waffles"],
        "brunch":      ["Cold Coffee", "Veg Burger", "Pizza", "Brownie Frappe"],
        "lunch":       ["Pizza", "Falafel Wrap", "Pasta", "Paneer Sandwich"],
        "snack":       ["Cold Coffee", "Suto Special Frappe", "Nachos", "Chocolate Brownie"],
        "dinner":      ["Pizza", "Pasta", "Falafel Wrap", "Veg Burger"],
        "late_night":  ["Hot Chocolate", "Cappuccino", "Waffles", "Brownie"],
        "off_hours":   ["Suto Special Frappe", "Cappuccino"],
    }

    PERIOD_HEADLINES = {
        "breakfast":  "Start your morning right ☕",
        "brunch":     "Weekend brunch done right 🥞",
        "lunch":      "Lunch break? We've got you 🍕",
        "snack":      "Your 5 o'clock craving, sorted 😋",
        "dinner":     "Dinner for one, two, or the whole crew 🍝",
        "late_night": "Late night bites & sips 🌙",
        "off_hours":  "Come visit us today ☕",
    }

    def run(self) -> TimeData:
        now = datetime.now()
        h = now.hour
        day_name = now.strftime("%A")
        is_weekend = now.weekday() >= 5
        day_type = "weekend" if is_weekend else "weekday"

        if 7 <= h < 10:
            period, rush = "breakfast", 0.6
        elif 10 <= h < 12:
            period, rush = "brunch", 0.5 if is_weekend else 0.3
        elif 12 <= h < 15:
            period, rush = "lunch", 0.9 if is_weekend else 0.75
        elif 15 <= h < 19:
            period, rush = "snack", 0.8
        elif 19 <= h < 22:
            period, rush = "dinner", 0.85 if is_weekend else 0.7
        elif 22 <= h <= 23:
            period, rush = "late_night", 0.45
        else:
            period, rush = "off_hours", 0.1

        # Weekends get +15% rush
        if is_weekend:
            rush = min(1.0, rush * 1.15)

        # Best time to post is 45 min before rush peak
        if period == "lunch":
            best = "11:15 AM"
        elif period == "snack":
            best = "4:30 PM"
        elif period == "dinner":
            best = "6:15 PM"
        else:
            best = f"{(h + 1) % 24}:00 {'AM' if (h+1) < 12 else 'PM'}"

        post_now = rush >= 0.5

        return TimeData(
            hour=h,
            day_name=day_name,
            day_type=day_type,
            meal_period=period,
            rush_score=rush,
            post_now=post_now,
            best_post_time=best,
            items_for_period=self.PERIOD_ITEMS.get(period, []),
            period_headline=self.PERIOD_HEADLINES.get(period, "Come visit us ☕")
        )
