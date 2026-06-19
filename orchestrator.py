"""
Campaign Orchestrator — coordinates all agents in sequence.
Yields (step_name, status, result) tuples for real-time Streamlit display.
In production this uses LangGraph with Redis checkpointing.
"""
from __future__ import annotations
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Generator, Tuple, Any, Optional

from agents.weather_agent import WeatherAgent, WeatherData
from agents.festival_agent import FestivalAgent, FestivalData
from agents.time_agent import TimeAgent, TimeData
from agents.sales_prediction_agent import SalesPredictionAgent, SalesPrediction
from agents.competitor_agent import CompetitorAgent, CompetitorData
from agents.content_strategy_agent import ContentStrategyAgent, CampaignBrief
from agents.copywriter_agent import CopywriterAgent, CopyVariants
from agents.banner_agent import BannerAgent, BannerResult
from agents.publishing_agent import PublishingAgent, PublishResult
from agents.analytics_agent import AnalyticsAgent, AnalyticsReport
from database import init_db, get_session, AgentRun


@dataclass
class CampaignCycleResult:
    campaign_id: str
    weather: WeatherData
    festivals: FestivalData
    time_ctx: TimeData
    sales: SalesPrediction
    competitor: CompetitorData
    brief: CampaignBrief
    copy: CopyVariants
    banner: BannerResult
    publish: PublishResult
    analytics: AnalyticsReport
    total_duration_s: float
    started_at: datetime


StepResult = Tuple[str, str, str, Any]  # (agent_name, emoji, summary, result_object)


def run_campaign_cycle() -> Generator[StepResult, None, CampaignCycleResult]:
    """
    Generator that runs all agents in sequence.
    Yields (agent_name, emoji, summary, result) after each step.
    Returns the full CampaignCycleResult at the end.

    Usage in Streamlit:
        gen = run_campaign_cycle()
        for name, emoji, summary, result in gen:
            st.write(f"{emoji} {name}: {summary}")
        final = gen.return_value  # not directly accessible with for-loop
    """
    init_db()
    started = datetime.now()
    t0 = time.time()

    # ── 1. Weather ───────────────────────────────────────────────
    yield ("Initialising", "🚀", "Starting autonomous marketing cycle…", None)
    t = time.time()
    weather = WeatherAgent().run()
    _log_run("WeatherAgent", time.time() - t, weather.summary())
    yield ("Weather Intelligence", "🌤️", weather.summary(), weather)

    # ── 2. Festival ──────────────────────────────────────────────
    t = time.time()
    festivals = FestivalAgent().run()
    _log_run("FestivalAgent", time.time() - t, festivals.summary())
    yield ("Festival Intelligence", "🎉", festivals.summary(), festivals)

    # ── 3. Time context ──────────────────────────────────────────
    t = time.time()
    time_ctx = TimeAgent().run()
    _log_run("TimeAgent", time.time() - t, time_ctx.summary())
    yield ("Time Analysis", "⏰", time_ctx.summary(), time_ctx)

    # ── 4. Competitor ────────────────────────────────────────────
    t = time.time()
    competitor = CompetitorAgent().run()
    _log_run("CompetitorAgent", time.time() - t, competitor.summary())
    yield ("Competitor Monitor", "🕵️", competitor.summary(), competitor)

    # ── 5. Sales prediction ──────────────────────────────────────
    t = time.time()
    sales = SalesPredictionAgent().run(weather, festivals, time_ctx)
    _log_run("SalesPredictionAgent", time.time() - t, sales.summary())
    yield ("Sales Prediction", "📈", sales.summary(), sales)

    # ── 6. Content strategy (AI CMO) ─────────────────────────────
    t = time.time()
    brief = ContentStrategyAgent().run(weather, festivals, time_ctx, sales, competitor)
    _log_run("ContentStrategyAgent", time.time() - t, brief.summary())
    yield ("Content Strategy (AI CMO)", "🧠", brief.summary(), brief)

    # ── 7. Copywriter ────────────────────────────────────────────
    t = time.time()
    copy = CopywriterAgent().run(brief)
    _log_run("CopywriterAgent", time.time() - t,
             f"3 variants × 3 channels | LLM: {copy.llm_source}")
    yield ("Copywriter", "✍️",
           f"Generated 3 variants per channel via {copy.llm_source}", copy)

    # ── 8. Banner generator ──────────────────────────────────────
    t = time.time()
    banner = BannerAgent().run(brief)
    _log_run("BannerAgent", time.time() - t, f"3 banners saved → {len(banner.all_paths)} files")
    yield ("Banner Generator", "🎨", f"3 banner sizes created (1:1, 9:16, 4:5)", banner)

    # ── 9. Publishing ────────────────────────────────────────────
    t = time.time()
    publish = PublishingAgent().run(brief, copy, banner)
    _log_run("PublishingAgent", time.time() - t, publish.summary())
    yield ("Publishing", "📤", publish.summary(), publish)

    # ── 10. Analytics ────────────────────────────────────────────
    t = time.time()
    analytics = AnalyticsAgent().run(publish, brief)
    _log_run("AnalyticsAgent", time.time() - t, analytics.summary())
    yield ("Analytics & Learning", "📊", analytics.summary(), analytics)

    total = round(time.time() - t0, 2)
    yield ("✅ Complete", "🎯",
           f"Full cycle done in {total}s | Campaign: {publish.campaign_id}", None)

    return CampaignCycleResult(
        campaign_id=publish.campaign_id,
        weather=weather, festivals=festivals, time_ctx=time_ctx,
        sales=sales, competitor=competitor, brief=brief,
        copy=copy, banner=banner, publish=publish, analytics=analytics,
        total_duration_s=total, started_at=started
    )


def _log_run(agent: str, duration: float, summary: str):
    try:
        with get_session() as session:
            session.add(AgentRun(
                agent_name=agent,
                status="success",
                duration_ms=int(duration * 1000),
                output_summary=summary[:200]
            ))
            session.commit()
    except Exception:
        pass
