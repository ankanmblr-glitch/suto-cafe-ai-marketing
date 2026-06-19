"""
Analytics Agent — tracks campaign performance and generates learning insights.
In PoC: uses simulated metrics. In production: pulls from Meta Graph API.
"""
from __future__ import annotations
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict
from config import config
from agents.publishing_agent import PublishResult
from agents.content_strategy_agent import CampaignBrief
from database import get_session, Campaign


@dataclass
class AnalyticsReport:
    campaign_id: str
    performance_score: float       # 0-10
    total_reach: int
    total_impressions: int
    engagement_rate: float         # percentage
    channel_breakdown: Dict[str, Dict]
    top_performing_channel: str
    best_copy_variant: str
    insights: List[str]
    do_again: List[str]
    avoid_next_time: List[str]
    source: str = "simulated"

    def summary(self) -> str:
        return (f"Score: {self.performance_score:.1f}/10 | "
                f"Reach: {self.total_reach:,} | "
                f"Engagement: {self.engagement_rate:.1f}%")


class AnalyticsAgent:

    def run(self, publish_result: PublishResult, brief: CampaignBrief) -> AnalyticsReport:
        # Simulate realistic metrics per channel
        channel_data = {}
        total_reach = 0
        total_eng = 0

        base_reach_map = {"facebook": (600, 2200), "instagram": (800, 3500), "whatsapp": (300, 1200)}
        base_eng_map  = {"facebook": (2.0, 5.0),  "instagram": (3.5, 8.0),  "whatsapp": (15.0, 35.0)}

        for ch in publish_result.channels_published:
            reach_range = base_reach_map.get(ch, (200, 800))
            eng_range   = base_eng_map.get(ch, (2.0, 5.0))
            reach = random.randint(*reach_range)
            impressions = int(reach * random.uniform(1.2, 1.8))
            eng_rate = random.uniform(*eng_range)
            eng_count = int(reach * eng_rate / 100)

            channel_data[ch] = {
                "reach": reach, "impressions": impressions,
                "engagement_rate": round(eng_rate, 2),
                "engagements": eng_count,
                "clicks": int(eng_count * 0.4),
                "saves": int(eng_count * 0.1) if ch == "instagram" else 0,
            }
            total_reach += reach
            total_eng += eng_count

        overall_eng = round(total_eng / max(total_reach, 1) * 100, 2)
        score = min(10.0, (overall_eng / 8) * 10)
        score = round(score * random.uniform(0.85, 1.1), 1)
        score = min(10.0, max(1.0, score))

        top_ch = max(channel_data, key=lambda c: channel_data[c]["engagement_rate"]) if channel_data else "instagram"

        insights = self._generate_insights(brief, channel_data, score)
        do_again = self._do_again(brief, score)
        avoid = self._avoid(brief, channel_data)

        # Save to DB
        self._save_to_db(publish_result.campaign_id, brief, total_reach, overall_eng)

        return AnalyticsReport(
            campaign_id=publish_result.campaign_id,
            performance_score=score,
            total_reach=total_reach,
            total_impressions=int(total_reach * 1.4),
            engagement_rate=overall_eng,
            channel_breakdown=channel_data,
            top_performing_channel=top_ch,
            best_copy_variant=publish_result.mock_post_ids.get("instagram", "b")[-1] if publish_result.mock_post_ids else "b",
            insights=insights,
            do_again=do_again,
            avoid_next_time=avoid
        )

    def _generate_insights(self, brief: CampaignBrief, channel_data: dict, score: float) -> List[str]:
        ins = []
        if score >= 7:
            ins.append(f"'{brief.tone}' tone resonated strongly — use it again for similar conditions")
        if "instagram" in channel_data and channel_data["instagram"]["engagement_rate"] > 5:
            ins.append("Instagram outperformed — prioritize Reels + Stories for next campaign")
        if "whatsapp" in channel_data and channel_data["whatsapp"]["engagement_rate"] > 20:
            ins.append("WhatsApp broadcast has high open rate — build subscriber list further")
        ins.append(f"Hero items {', '.join(brief.hero_items[:2])} drove the narrative — maintain focus")
        if brief.local_reference:
            ins.append(f"Local reference '{brief.local_reference}' adds authenticity — always include")
        return ins[:4]

    def _do_again(self, brief: CampaignBrief, score: float) -> List[str]:
        items = [
            f"{brief.tone.capitalize()} tone with local Siliguri references",
            f"2-3 hero items focus (not entire menu)",
        ]
        if score >= 6:
            items.append(f"Variant B copy style for {', '.join(brief.channels)}")
        return items

    def _avoid(self, brief: CampaignBrief, channel_data: dict) -> List[str]:
        items = []
        for ch, data in channel_data.items():
            if data["engagement_rate"] < 2.5:
                items.append(f"Avoid posting to {ch} at this time — low engagement window")
        items.append("Avoid running same theme within 3 days")
        return items

    def _save_to_db(self, campaign_id: str, brief: CampaignBrief,
                    reach: int, engagement: float):
        try:
            import json
            with get_session() as session:
                c = Campaign(
                    theme=brief.campaign_theme,
                    hero_items=json.dumps(brief.hero_items),
                    channels=json.dumps(brief.channels),
                    campaign_tone=brief.tone,
                    published=True,
                    mock_reach=reach,
                    mock_engagement=engagement
                )
                session.add(c)
                session.commit()
        except Exception:
            pass
