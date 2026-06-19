"""
Content Strategy Agent (AI CMO Brain)
Uses Groq LLM (free) to synthesize all context into a campaign brief.
Falls back to smart mock if no API key.
"""
from __future__ import annotations
import json
import random
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from config import config
from agents.weather_agent import WeatherData
from agents.festival_agent import FestivalData
from agents.time_agent import TimeData
from agents.sales_prediction_agent import SalesPrediction
from agents.competitor_agent import CompetitorData


@dataclass
class CampaignBrief:
    campaign_theme: str
    theme_display: str
    hero_items: List[str]
    campaign_rationale: str
    target_primary: str
    channels: List[str]
    tone: str
    key_messages: List[str]
    local_reference: str
    hashtags_primary: List[str]
    hashtags_local: List[str]
    cta: str
    requires_human_approval: bool
    urgency_reason: str
    llm_source: str  # "groq" | "mock"

    def summary(self) -> str:
        return (f"Theme: {self.theme_display} | Items: {', '.join(self.hero_items[:2])} "
                f"| Tone: {self.tone} | Channels: {', '.join(self.channels)}")


SYSTEM_PROMPT = """You are the AI CMO for Suto Café, Siliguri, West Bengal — a modern 100% vegetarian café.
Price range ₹80–₹250. Brand voice: warm, local, youthful, Siliguri-proud.
Signature items: Suto Special Frappe, Brownie Frappe, Falafel Wrap, Tandoori Maggi, personal 8" Pizza.

Given context data, output a campaign brief as valid JSON with these exact keys:
campaign_theme (snake_case), theme_display (human readable), hero_items (list of 2-3 menu items),
campaign_rationale (1-2 sentences), target_primary (youth_20_30|families_30_45|all),
channels (list: facebook/instagram/whatsapp), tone (playful|warm|festive|urgent|cozy|refreshing),
key_messages (list of 3), local_reference (Siliguri landmark/feeling),
hashtags_primary (3-5 hashtags), hashtags_local (2-3 Siliguri hashtags),
cta (call to action string), requires_human_approval (boolean), urgency_reason (string).
Output ONLY the JSON object, no other text."""


class ContentStrategyAgent:

    def run(self, weather: WeatherData, festivals: FestivalData,
            time_ctx: TimeData, sales: SalesPrediction,
            competitor: CompetitorData) -> CampaignBrief:
        if config.llm_available:
            try:
                return self._groq_strategy(weather, festivals, time_ctx, sales, competitor)
            except Exception as e:
                print(f"[ContentStrategy] Groq error: {e}, falling back to mock")
        return self._mock_strategy(weather, festivals, time_ctx, sales)

    def _groq_strategy(self, weather, festivals, time_ctx, sales, competitor) -> CampaignBrief:
        from groq import Groq
        client = Groq(api_key=config.GROQ_API_KEY)

        context = f"""
Current context for Suto Café:
- Weather: {weather.temp_c:.0f}°C, {weather.condition}, tone={weather.campaign_tone}
- Weather narrative: {weather.weather_narrative}
- Boosted items: {', '.join(weather.boosted_items[:4])}
- Time: {time_ctx.day_name}, {time_ctx.meal_period}, rush_score={time_ctx.rush_score:.1f}
- Today festival: {festivals.today_festival_display or 'None'}
- Upcoming: {festivals.upcoming[0].display if festivals.upcoming else 'None'} in {festivals.upcoming[0].days_until if festivals.upcoming else 0} days
- Festival urgency: {festivals.urgency}
- Predicted footfall: {sales.today_footfall}
- Promotion advice: {sales.promotion_advice}
- Competitor opp: {competitor.differentiation_opportunity}
- Avoid featuring: {', '.join(competitor.items_to_avoid)}
"""
        resp = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": context}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        data = json.loads(resp.choices[0].message.content)
        return CampaignBrief(**{k: data[k] for k in CampaignBrief.__dataclass_fields__ if k in data},
                             llm_source="groq")

    def _mock_strategy(self, weather: WeatherData, festivals: FestivalData,
                       time_ctx: TimeData, sales: SalesPrediction) -> CampaignBrief:
        # Smart mock that adapts to context
        if festivals.today_festival:
            return CampaignBrief(
                campaign_theme=f"{festivals.today_festival}_celebration",
                theme_display=f"{festivals.today_festival_display} at Suto Café",
                hero_items=["Suto Special Frappe", "Pizza", "Brownie Frappe"],
                campaign_rationale=f"Today is {festivals.today_festival_display} — biggest opportunity for footfall boost. Feature premium items.",
                target_primary="all",
                channels=["facebook", "instagram", "whatsapp"],
                tone="festive",
                key_messages=[
                    f"Celebrate {festivals.today_festival_display} with us at Suto Café",
                    "Your favourite spot in Siliguri is dressed up for the occasion",
                    "Special festive vibe, same great food & drinks"
                ],
                local_reference="Hill Cart Road festive buzz",
                hashtags_primary=[
                    "#" + (festivals.today_festival_display or "").replace(" ","").replace("'","") + "WithSuto",
                    "#SutoCafe", "#SiliguriFestival"],
                hashtags_local=["#Siliguri", "#NorthBengal", "#SiliguriFoodie"],
                cta="Come celebrate with us today! 🎉",
                requires_human_approval=True,
                urgency_reason=f"{festivals.today_festival_display} is TODAY — post immediately",
                llm_source="mock"
            )
        elif weather.condition_category == "rainy":
            return CampaignBrief(
                campaign_theme="monsoon_comfort",
                theme_display="Monsoon Comfort at Suto Café",
                hero_items=["Tandoori Maggi", "Hot Chocolate", "Cappuccino"],
                campaign_rationale="Rainy Siliguri weather drives demand for hot comfort food. Feature our signature Tandoori Maggi.",
                target_primary="all",
                channels=["instagram", "whatsapp"],
                tone="cozy",
                key_messages=[
                    "Siliguri ki baarish + Tandoori Maggi = perfect combo",
                    "Hot drinks to warm your soul on a rainy afternoon",
                    "Escape the rain, find your cozy corner at Suto"
                ],
                local_reference="Siliguri ki baarish",
                hashtags_primary=["#MonsoonVibes", "#SutoCafe", "#TandooriMaggi", "#RainyDayCafe"],
                hashtags_local=["#Siliguri", "#SiliguriFoodie", "#NorthBengalCafe"],
                cta="Come in from the rain — we're warm inside ☕",
                requires_human_approval=False,
                urgency_reason="Rain detected — comfort food demand high right now",
                llm_source="mock"
            )
        elif weather.condition_category == "hot_sunny":
            return CampaignBrief(
                campaign_theme="beat_the_heat",
                theme_display="Beat the Siliguri Heat",
                hero_items=["Suto Special Frappe", "Cold Coffee", "Watermelon Cooler"],
                campaign_rationale=f"Temperature at {weather.temp_c:.0f}°C drives strong demand for cold beverages. Feature our signature Frappe.",
                target_primary="youth_20_30",
                channels=["instagram", "facebook"],
                tone="refreshing",
                key_messages=[
                    f"Siliguri ki {weather.temp_c:.0f}°C heat? Suto Café hai na!",
                    "Suto Special Frappe — the city's coolest drink",
                    "Chill out with friends this afternoon"
                ],
                local_reference="Siliguri summer heat",
                hashtags_primary=["#BeatTheHeat", "#SutoCafe", "#SutoSpecialFrappe", "#SiliguriFrappe"],
                hashtags_local=["#Siliguri", "#SiliguriFoodie", "#NorthBengal"],
                cta="Tag a friend who needs to cool down! 🧊",
                requires_human_approval=False,
                urgency_reason=f"Peak heat at {weather.temp_c:.0f}°C — cold drinks urgency is high",
                llm_source="mock"
            )
        elif time_ctx.day_type == "weekend":
            return CampaignBrief(
                campaign_theme="weekend_hangout",
                theme_display="Weekend Hangout at Suto",
                hero_items=["Brownie Frappe", "8\" Personal Pizza", "Falafel Wrap"],
                campaign_rationale="Weekend drives social group visits. Feature shareable items and the hang-out vibe.",
                target_primary="youth_20_30",
                channels=["instagram", "facebook", "whatsapp"],
                tone="playful",
                key_messages=[
                    "Weekend plans sorted — Suto Café with your people",
                    "Our 8\" personal pizza is perfect for solo or sharing",
                    "Brownie Frappe + good company = peak weekend"
                ],
                local_reference="Siliguri weekend vibes",
                hashtags_primary=["#WeekendVibes", "#SutoCafe", "#SiliguriFoodie", "#CafeLife"],
                hashtags_local=["#Siliguri", "#SiligurWeekend", "#NorthBengalCafe"],
                cta="Where are you hanging out this weekend? 🍕",
                requires_human_approval=False,
                urgency_reason="Weekend — highest footfall days of the week",
                llm_source="mock"
            )
        else:
            return CampaignBrief(
                campaign_theme="signature_spotlight",
                theme_display="Suto Signature Spotlight",
                hero_items=["Suto Special Frappe", "Falafel Wrap", "Brownie Frappe"],
                campaign_rationale="Regular weekday — spotlight our most unique, competitor-exclusive items to drive visits.",
                target_primary="all",
                channels=["instagram", "whatsapp"],
                tone="warm",
                key_messages=[
                    "Our Falafel Wrap — the only one in Siliguri worth talking about",
                    "Suto Special Frappe: you won't find this anywhere else",
                    "Stop by anytime — we're always ready for you"
                ],
                local_reference="Your go-to spot on Hill Cart Road",
                hashtags_primary=["#SutoCafe", "#FalafelWrap", "#SutoSpecial", "#SiliguriFoodie"],
                hashtags_local=["#Siliguri", "#NorthBengal", "#SiliguriFoodie"],
                cta="Come try something different today 🥙",
                requires_human_approval=False,
                urgency_reason="Weekday — drive incremental visits with unique USPs",
                llm_source="mock"
            )
