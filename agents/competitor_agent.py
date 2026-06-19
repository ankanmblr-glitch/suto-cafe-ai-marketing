"""
Competitor Monitoring Agent — simulated data for PoC.
In production: uses web scraping + Meta Graph API for competitor pages.
"""
from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import List
from datetime import datetime


@dataclass
class CompetitorAlert:
    competitor: str
    alert_type: str
    description: str
    suto_response: str


@dataclass
class CompetitorData:
    alerts: List[CompetitorAlert]
    trending_content_type: str
    differentiation_opportunity: str
    items_to_avoid: List[str]
    source: str = "simulated"

    def summary(self) -> str:
        if self.alerts:
            return f"{len(self.alerts)} competitor alerts — {self.differentiation_opportunity}"
        return f"No major alerts — {self.differentiation_opportunity}"


class CompetitorAgent:
    COMPETITORS = ["Café XYZ Hill Cart Road", "The Coffee Corner", "Brew House Siliguri"]

    MOCK_ALERTS = [
        CompetitorAlert(
            "Café XYZ Hill Cart Road",
            "price_promo",
            "Running Buy 1 Get 1 on Cold Coffee (₹99 each) — high engagement post",
            "Counter with Suto Special Frappe uniqueness — our blend can't be replicated"
        ),
        CompetitorAlert(
            "The Coffee Corner",
            "high_engagement_post",
            "Reels of their Maggi getting 4K+ views — simple recipe video format",
            "Post behind-the-scenes of Tandoori Maggi prep — our variant is more unique"
        ),
        CompetitorAlert(
            "Brew House Siliguri",
            "festival_campaign",
            "Running festival banners but generic national templates — low local feel",
            "Go hyperlocal: use Siliguri landmarks and Bengali language for deeper connection"
        ),
    ]

    OPPORTUNITIES = [
        "Push Falafel Wrap — no competitor has it on their menu this week",
        "Brownie Frappe is trending in Siliguri searches — lead with it",
        "Competitors are using generic Reels templates — authentic behind-scenes content will stand out",
        "No competitor is running WhatsApp campaigns this week — first mover advantage",
        "Mocktail range is your exclusive — lean into it vs competitors who only serve coffee",
    ]

    def run(self) -> CompetitorData:
        # Simulate 0-2 alerts per cycle (not all every time)
        num_alerts = random.randint(0, 2)
        alerts = random.sample(self.MOCK_ALERTS, min(num_alerts, len(self.MOCK_ALERTS)))
        opp = random.choice(self.OPPORTUNITIES)

        # Items competitors just pushed (so Suto should differentiate)
        avoid = random.sample(["Cold Coffee", "Cappuccino", "Pizza"], 1)

        return CompetitorData(
            alerts=alerts,
            trending_content_type=random.choice(["short_reels", "carousel_posts", "story_polls"]),
            differentiation_opportunity=opp,
            items_to_avoid=avoid,
            source="simulated"
        )
