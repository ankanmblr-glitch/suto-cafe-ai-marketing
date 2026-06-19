"""
Sales Prediction Agent — rule-based model (no ML libraries).
Uses weather × time × festival multipliers on historical baseline.
"""
from __future__ import annotations
import csv
import os
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Dict
from agents.weather_agent import WeatherData
from agents.festival_agent import FestivalData
from agents.time_agent import TimeData


@dataclass
class DayForecast:
    date: date
    day_label: str
    predicted_footfall: int
    predicted_revenue_inr: int
    confidence: str
    drivers: List[str]


@dataclass
class SalesPrediction:
    today_footfall: int
    today_revenue_inr: int
    today_top_items: List[str]
    weekly_forecast: List[DayForecast]
    promotion_advice: str
    source: str = "rule_based"

    def summary(self) -> str:
        return (f"Today: ~{self.today_footfall} customers, "
                f"₹{self.today_revenue_inr:,} revenue — {self.promotion_advice}")


class SalesPredictionAgent:
    BASE_WEEKDAY = 62
    BASE_WEEKEND = 85
    AVG_BILL = 230

    WEATHER_MULT = {
        "rainy": 1.08,       # comfort food spikes
        "hot_sunny": 1.15,   # cold drinks surge
        "warm_pleasant": 1.0,
        "mild_pleasant": 1.05,
        "cold_winter": 1.12, # hot beverages surge
    }

    FESTIVAL_MULT = {
        10: 1.5, 9: 1.35, 8: 1.2, 7: 1.15, 6: 1.08, 5: 1.05
    }

    def run(self, weather: WeatherData, festivals: FestivalData, time_ctx: TimeData) -> SalesPrediction:
        # Today's prediction
        base = self.BASE_WEEKEND if time_ctx.day_type == "weekend" else self.BASE_WEEKDAY
        w_mult = self.WEATHER_MULT.get(weather.condition_category, 1.0)
        f_mult = 1.0
        fest_drivers = []

        if festivals.active_festival and festivals.upcoming:
            importance = festivals.upcoming[0].importance if festivals.upcoming else 5
            f_mult = self.FESTIVAL_MULT.get(importance, 1.0)
            fest_drivers.append(f"{festivals.upcoming[0].display} season")

        rush_mult = 0.8 + time_ctx.rush_score * 0.4
        today_footfall = int(base * w_mult * f_mult * rush_mult)
        today_revenue = int(today_footfall * self.AVG_BILL)

        # Determine top items
        top_items = weather.boosted_items[:3] or time_ctx.items_for_period[:3]

        # Promotion advice
        if today_footfall > 90:
            advice = "High traffic expected — post early to build anticipation"
        elif today_footfall < 45:
            advice = "Quiet day — push a deal to drive walk-ins (e.g. combo offer)"
        elif festivals.active_festival:
            advice = f"Festival momentum! Seed excitement for {festivals.active_festival}"
        else:
            advice = "Normal day — feature your signature items"

        # 7-day forecast
        weekly = []
        for i in range(7):
            d = date.today() + timedelta(days=i)
            is_wknd = d.weekday() >= 5
            day_base = self.BASE_WEEKEND if is_wknd else self.BASE_WEEKDAY
            drivers = []
            day_f_mult = f_mult if i < 3 else 1.0
            drivers.append(f"{'Weekend' if is_wknd else 'Weekday'} baseline")
            if day_f_mult > 1.0:
                drivers.extend(fest_drivers)
            footfall = int(day_base * w_mult * day_f_mult)
            weekly.append(DayForecast(
                date=d,
                day_label=d.strftime("%a %d"),
                predicted_footfall=footfall,
                predicted_revenue_inr=int(footfall * self.AVG_BILL),
                confidence="medium",
                drivers=drivers
            ))

        return SalesPrediction(
            today_footfall=today_footfall,
            today_revenue_inr=today_revenue,
            today_top_items=top_items,
            weekly_forecast=weekly,
            promotion_advice=advice
        )
