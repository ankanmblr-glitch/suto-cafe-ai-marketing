"""
Weather Intelligence Agent
Real: OpenWeatherMap free tier API
Mock: Seasonal simulation for Siliguri
"""
from __future__ import annotations
import requests
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from config import config


@dataclass
class WeatherData:
    temp_c: float
    feels_like_c: float
    humidity_pct: int
    condition: str
    condition_category: str
    weather_narrative: str
    boosted_items: List[str]
    suppressed_items: List[str]
    campaign_tone: str
    emoji: str
    urgency_boost: float
    source: str  # "api" | "mock"

    def summary(self) -> str:
        return f"{self.emoji} {self.temp_c:.0f}°C, {self.condition} — {self.condition_category}"


class WeatherAgent:
    LAT, LON = 26.7271, 88.3953  # Siliguri

    def run(self) -> WeatherData:
        if config.weather_available:
            try:
                return self._fetch_live()
            except Exception:
                pass
        return self._mock()

    def _fetch_live(self) -> WeatherData:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"lat": self.LAT, "lon": self.LON,
                    "appid": config.OPENWEATHER_API_KEY, "units": "metric"},
            timeout=5
        )
        d = r.json()
        return self._classify(
            temp=d["main"]["temp"],
            humidity=d["main"]["humidity"],
            condition=d["weather"][0]["main"].lower(),
            source="api"
        )

    def _mock(self) -> WeatherData:
        month = datetime.now().month
        hour = datetime.now().hour
        if month in [3, 4, 5, 6]:
            temp, humidity, cond = 34.0, 78, "clear"
        elif month in [7, 8, 9]:
            temp, humidity, cond = 25.0, 93, "rain"
        elif month in [10, 11]:
            temp, humidity, cond = 21.0, 65, "clouds"
        else:
            temp, humidity, cond = 12.0, 58, "mist"
        return self._classify(temp, humidity, cond, source="mock")

    def _classify(self, temp: float, humidity: int, condition: str, source: str) -> WeatherData:
        if "rain" in condition or "drizzle" in condition or "thunder" in condition:
            return WeatherData(
                temp_c=temp, feels_like_c=temp - 2, humidity_pct=humidity,
                condition=condition, condition_category="rainy",
                weather_narrative="Siliguri ki baarish mein — perfect time for something warm 🍜",
                boosted_items=["Tandoori Maggi", "Hot Chocolate", "Cappuccino", "Garlic Toast", "Waffles"],
                suppressed_items=["Cold Coffee", "Ice Tea", "Smoothies"],
                campaign_tone="cozy", emoji="🌧️", urgency_boost=0.85, source=source
            )
        elif temp > 30:
            return WeatherData(
                temp_c=temp, feels_like_c=temp + 2, humidity_pct=humidity,
                condition=condition, condition_category="hot_sunny",
                weather_narrative=f"Siliguri ki garmi aaj peak pe hai — {temp:.0f}°C! Beat the heat ☀️",
                boosted_items=["Cold Coffee", "Suto Special Frappe", "Ice Tea", "Watermelon Cooler", "Nachos"],
                suppressed_items=["Hot Chocolate", "Masala Chai"],
                campaign_tone="refreshing", emoji="☀️", urgency_boost=0.9, source=source
            )
        elif temp >= 25:
            return WeatherData(
                temp_c=temp, feels_like_c=temp, humidity_pct=humidity,
                condition=condition, condition_category="warm_pleasant",
                weather_narrative=f"Perfect Siliguri weather at {temp:.0f}°C — ideal café afternoon ☕",
                boosted_items=["Brownie Frappe", "Cold Coffee", "Pizza", "Falafel Wrap", "Pasta"],
                suppressed_items=[],
                campaign_tone="energetic", emoji="🌤️", urgency_boost=0.5, source=source
            )
        elif temp >= 18:
            return WeatherData(
                temp_c=temp, feels_like_c=temp - 1, humidity_pct=humidity,
                condition=condition, condition_category="mild_pleasant",
                weather_narrative=f"North Bengal ka mausam aaj sahi hai — {temp:.0f}°C, chai weather!",
                boosted_items=["Cappuccino", "Sandwiches", "Pizza", "Brownie", "Waffles"],
                suppressed_items=[],
                campaign_tone="warm", emoji="⛅", urgency_boost=0.4, source=source
            )
        else:
            return WeatherData(
                temp_c=temp, feels_like_c=temp - 2, humidity_pct=humidity,
                condition=condition, condition_category="cold_winter",
                weather_narrative=f"Siliguri mein thand aa gayi — {temp:.0f}°C! Hot drinks calling 🥶",
                boosted_items=["Hot Chocolate", "Cappuccino", "Tandoori Maggi", "Masala Chai", "Waffles"],
                suppressed_items=["Ice Tea", "Cold Coffee", "Smoothies", "Mocktails"],
                campaign_tone="cozy", emoji="🥶", urgency_boost=0.85, source=source
            )
