# -*- coding: utf-8 -*-
"""
Suto Café — AI Marketing Platform PoC
Streamlit Dashboard: full client demo with zero paid services.
Run with:  run.bat   (Windows)  or  bash run.sh  (Mac/Linux)
"""
import os
import sys
import json
import time
import random
from datetime import datetime, date, timedelta
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

# ── Page config (must be first Streamlit call) ─────────────────────────────
st.set_page_config(
    page_title="Suto Café — AI Marketing Platform",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Imports after page config ───────────────────────────────────────────────
from config import config
from database import init_db, get_session, Campaign, DailySales, AgentRun
from agents.weather_agent import WeatherAgent
from agents.festival_agent import FestivalAgent
from agents.time_agent import TimeAgent
from agents.sales_prediction_agent import SalesPredictionAgent
from orchestrator import run_campaign_cycle

# ── Init DB once ────────────────────────────────────────────────────────────
init_db()

# ── Custom CSS — Aero Glassmorphism Theme ───────────────────────────────────
st.markdown("""
<style>
/* ── Aero Glassmorphism — Windows Aero inspired ─── */

/* Main background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #d4e8f8 0%, #c2d9f0 25%, #d8ecff 60%, #e8f4ff 100%) !important;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
}
[data-testid="stMain"] { background: transparent !important; }

/* Sidebar — frosted glass panel */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.45) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border-right: 1px solid rgba(255,255,255,0.75) !important;
    box-shadow: 4px 0 24px rgba(0,120,212,0.08) !important;
}
[data-testid="stSidebar"] * { color: #1a3a5c !important; }

/* Headings */
h1, h2, h3, h4 {
    color: #0063b1 !important;
    font-weight: 700 !important;
    text-shadow: 0 1px 3px rgba(255,255,255,0.9);
}
p, li, label { color: #1a3a5c !important; }

/* Metric cards — glass tiles */
.stMetric {
    background: rgba(255,255,255,0.55) !important;
    border-radius: 14px !important;
    padding: 14px !important;
    border: 1px solid rgba(255,255,255,0.80) !important;
    box-shadow: 0 4px 18px rgba(0,120,212,0.10),
                inset 0 1px 0 rgba(255,255,255,0.85) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
}
.stMetric label { color: #0078d4 !important; font-size: 13px; font-weight: 600; }
.stMetric [data-testid="stMetricValue"] { color: #1a3a5c !important; font-size: 26px; font-weight: 700; }
.stMetric [data-testid="stMetricDelta"] { font-size: 13px; }

/* Agent cards */
.agent-card {
    background: rgba(255,255,255,0.52);
    border-radius: 10px;
    padding: 12px 16px;
    margin: 5px 0;
    border-left: 4px solid #0078d4;
    display: flex;
    align-items: center;
    gap: 12px;
    backdrop-filter: blur(10px);
    box-shadow: 0 2px 12px rgba(0,120,212,0.08);
}
.agent-card.running { border-left-color: #f5a623; animation: pulse 1s infinite; }
.agent-card.done    { border-left-color: #107c10; }
.agent-card.idle    { border-left-color: #c8d8e8; opacity: 0.75; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.75} }

/* Channel / hashtag badges */
.channel-badge {
    display: inline-block;
    background: rgba(0,120,212,0.10);
    border: 1px solid rgba(0,120,212,0.28);
    border-radius: 12px;
    padding: 3px 10px;
    font-size: 12px;
    color: #0063b1;
    margin: 2px;
}

/* PoC info banner */
.poc-banner {
    background: rgba(0,120,212,0.07);
    border: 1px solid rgba(0,120,212,0.28);
    border-radius: 10px;
    padding: 10px 16px;
    margin-bottom: 14px;
    color: #004e8c;
    font-size: 13px;
    backdrop-filter: blur(6px);
}

/* Buttons — Aero blue gradient */
div[data-testid="stButton"] button {
    background: linear-gradient(160deg, #2196f3 0%, #0063b1 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
    box-shadow: 0 4px 14px rgba(0,120,212,0.30),
                inset 0 1px 0 rgba(255,255,255,0.22) !important;
    transition: all 0.18s ease !important;
}
div[data-testid="stButton"] button:hover {
    background: linear-gradient(160deg, #1976d2 0%, #004e8c 100%) !important;
    box-shadow: 0 6px 20px rgba(0,120,212,0.42) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab"] { color: #0078d4 !important; }
.stTabs [aria-selected="true"] {
    border-bottom-color: #0078d4 !important;
    font-weight: 700;
    color: #0063b1 !important;
}

/* Copy / post text box */
.copy-box {
    background: rgba(255,255,255,0.60);
    border: 1px solid rgba(0,120,212,0.20);
    border-radius: 10px;
    padding: 14px;
    margin: 8px 0;
    font-size: 14px;
    color: #1a3a5c;
    white-space: pre-wrap;
    line-height: 1.6;
    backdrop-filter: blur(8px);
}

/* Score badge */
.score-badge {
    display: inline-block;
    background: linear-gradient(135deg, #0078d4, #106ebe);
    color: white;
    border-radius: 8px;
    padding: 4px 12px;
    font-weight: bold;
    font-size: 18px;
    box-shadow: 0 2px 8px rgba(0,120,212,0.30);
}

/* Dataframe / tables */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* Info / warning boxes */
.stAlert { border-radius: 10px !important; backdrop-filter: blur(8px) !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ☕ Suto Café")
    st.markdown("**AI Marketing Platform**")
    st.markdown("*PoC Demo — Siliguri, WB*")
    st.divider()

    page = st.radio("Navigate", [
        "🏠 Dashboard",
        "🚀 Run Campaign",
        "📄 Content Preview",
        "📊 Analytics",
        "🎉 Festival Calendar",
        "🌤️ Weather Monitor",
        "⚙️ Settings & Info",
    ])

    st.divider()

    # Live status indicators
    st.markdown("**Agent Status**")
    agents_status = [
        ("🌤️", "Weather Agent",    "idle"),
        ("🎉", "Festival Agent",   "idle"),
        ("⏰", "Time Agent",       "idle"),
        ("🕵️", "Competitor Agent", "idle"),
        ("📈", "Sales Predictor",  "idle"),
        ("🧠", "AI CMO",           "idle"),
        ("✍️", "Copywriter",       "idle"),
        ("🎨", "Banner Agent",     "idle"),
        ("📤", "Publisher",        "idle"),
        ("📊", "Analytics Agent",  "idle"),
    ]
    for em, name, status in agents_status:
        dot = "🟢" if status == "done" else "🟡" if status == "running" else "⚫"
        st.markdown(f"{dot} {em} {name}", unsafe_allow_html=False)

    st.divider()
    llm_label = "🟢 Groq API" if config.llm_available else "🟡 Mock Mode"
    wx_label  = "🟢 Live API"  if config.weather_available else "🟡 Simulated"
    st.markdown(f"**LLM:** {llm_label}")
    st.markdown(f"**Weather:** {wx_label}")

    if config.DEMO_MODE:
        st.markdown('<div class="poc-banner">🎭 DEMO MODE — all data is realistic simulation</div>',
                    unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════
if page == "🏠 Dashboard":
    st.title("☕ Suto Café — AI Marketing Platform")
    st.markdown('<div class="poc-banner">🔬 <strong>PoC Demo</strong> — showing full platform capabilities. '
                'Replace [PoC Mock] tags with real API integrations for production.</div>',
                unsafe_allow_html=True)

    # Quick metrics from DB
    with get_session() as session:
        total_campaigns = session.query(Campaign).count()
        published = session.query(Campaign).filter(Campaign.published == True).count()
        avg_reach = session.query(Campaign).all()
        avg_reach_val = int(sum(c.mock_reach for c in avg_reach) / max(len(avg_reach), 1))
        avg_eng = sum(c.mock_engagement for c in avg_reach) / max(len(avg_reach), 1)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Campaigns Run", total_campaigns, "+1 today")
    with col2:
        st.metric("Posts Published", published * 3, f"+{published * 3} today")
    with col3:
        st.metric("Avg. Estimated Reach", f"{avg_reach_val:,}" if avg_reach_val else "—")
    with col4:
        st.metric("Avg. Engagement Rate", f"{avg_eng:.1f}%" if avg_eng else "—", "+0.3%")

    st.divider()

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.subheader("📡 Live Context Right Now")
        weather = WeatherAgent().run()
        festivals = FestivalAgent().run()
        time_ctx = TimeAgent().run()

        cx1, cx2, cx3 = st.columns(3)
        cx1.metric(f"{weather.emoji} Weather", f"{weather.temp_c:.0f}°C",
                   weather.condition_category.replace("_"," ").title())
        cx2.metric("⏰ Time Period", time_ctx.meal_period.replace("_"," ").title(),
                   f"{time_ctx.day_name}")
        cx3.metric("🎉 Festival", festivals.today_festival_display or "None today",
                   festivals.upcoming[0].display[:20] if festivals.upcoming else "")

        if weather.boosted_items:
            st.markdown("**🔥 Weather-boosted items right now:**")
            st.markdown(" ".join(f'<span class="channel-badge">{i}</span>'
                                 for i in weather.boosted_items[:5]),
                        unsafe_allow_html=True)

        st.markdown(f"*{weather.weather_narrative}*")

    with col_right:
        st.subheader("🚀 Quick Action")
        st.markdown("Run one complete autonomous campaign cycle — "
                    "all 10 agents execute in sequence.")
        if st.button("▶️ Run Campaign Now", use_container_width=True):
            st.switch_page = None
            st.session_state["goto_run"] = True
            st.rerun()

        st.divider()
        st.subheader("📅 Upcoming Festivals")
        if festivals.upcoming:
            for f in festivals.upcoming[:4]:
                urgency_tag = "🔴" if f.days_until <= 1 else "🟡" if f.days_until <= 3 else "🟢"
                st.markdown(f"{urgency_tag} **{f.display}** — {f.days_until} days")
        else:
            st.markdown("*No major festivals in the next 14 days*")

    # Recent campaigns table
    st.divider()
    st.subheader("📋 Recent Campaigns")
    with get_session() as session:
        campaigns = session.query(Campaign).order_by(Campaign.created_at.desc()).limit(8).all()
    if campaigns:
        rows = []
        for c in campaigns:
            rows.append({
                "Time": c.created_at.strftime("%d %b %H:%M") if c.created_at else "—",
                "Theme": c.theme.replace("_"," ").title() if c.theme else "—",
                "Tone": c.campaign_tone or "—",
                "Est. Reach": f"{c.mock_reach:,}" if c.mock_reach else "—",
                "Engagement": f"{c.mock_engagement:.1f}%" if c.mock_engagement else "—",
                "Status": "✅ Published" if c.published else "⏳ Pending",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No campaigns yet. Run your first campaign above!")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: RUN CAMPAIGN
# ═══════════════════════════════════════════════════════════════════════════
elif page == "🚀 Run Campaign" or st.session_state.get("goto_run"):
    if "goto_run" in st.session_state:
        del st.session_state["goto_run"]

    st.title("🚀 Autonomous Campaign Runner")
    st.markdown("Click **Run** to watch all 10 AI agents execute in real-time. "
                "Each agent analyses Siliguri context and contributes to the final campaign.")

    if st.button("▶️ Run Full Autonomous Campaign", use_container_width=True):
        st.session_state["last_result"] = None
        results = {}

        progress_bar = st.progress(0, text="Initialising agents…")
        status_container = st.container()

        total_steps = 10
        step = 0

        gen = run_campaign_cycle()
        try:
            while True:
                name, emoji, summary, result = next(gen)
                step += 1
                progress = min(step / total_steps, 1.0)
                progress_bar.progress(progress, text=f"{emoji} {name}…")
                with status_container:
                    if result is not None:
                        results[name] = result
                    color = "#4CAF50" if "Complete" in name else "#ffd700"
                    st.markdown(
                        f'<div class="agent-card done">'
                        f'<span style="font-size:22px">{emoji}</span>'
                        f'<div><strong style="color:#1a3a5c">{name}</strong>'
                        f'<br><span style="color:#0078d4;font-size:13px">{summary}</span></div>'
                        f'</div>', unsafe_allow_html=True)
                    time.sleep(0.3)
        except StopIteration as e:
            final = e.value
            if final:
                st.session_state["last_result"] = final

        progress_bar.progress(1.0, text="✅ All agents complete!")

        if st.session_state.get("last_result"):
            r = st.session_state["last_result"]
            st.success(f"🎯 Campaign **{r.campaign_id}** completed in {r.total_duration_s:.1f}s")
            col1, col2, col3 = st.columns(3)
            col1.metric("Est. Reach", f"{r.publish.reach_estimate:,}")
            col2.metric("Channels", len(r.publish.channels_published))
            col3.metric("Perf. Score", f"{r.analytics.performance_score:.1f}/10")
            st.info("👉 Go to **📄 Content Preview** to see the generated posts and banners.")

    elif st.session_state.get("last_result"):
        r = st.session_state["last_result"]
        st.success(f"Last campaign **{r.campaign_id}** is ready. See Content Preview tab.")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: CONTENT PREVIEW
# ═══════════════════════════════════════════════════════════════════════════
elif page == "📄 Content Preview":
    st.title("📄 Generated Content Preview")
    r = st.session_state.get("last_result")

    if not r:
        st.warning("No campaign run yet. Go to **🚀 Run Campaign** first.")
    else:
        brief = r.brief
        copy = r.copy
        banner = r.banner
        publish = r.publish

        # Brief overview
        st.subheader(f"📋 Campaign: {brief.theme_display}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"**Tone:** {brief.tone.title()}")
        c2.markdown(f"**Target:** {brief.target_primary.replace('_',' ').title()}")
        c3.markdown(f"**LLM:** {brief.llm_source.upper()}")

        st.markdown(f"*{brief.campaign_rationale}*")
        st.markdown("**Channels:** " + " ".join(
            f'<span class="channel-badge">{ch.title()}</span>' for ch in brief.channels),
            unsafe_allow_html=True)
        st.markdown("**Hero items:** " + " ".join(
            f'<span class="channel-badge">{i}</span>' for i in brief.hero_items),
            unsafe_allow_html=True)
        st.markdown("**Hashtags:** " + " ".join(
            f'<span class="channel-badge">{h}</span>'
            for h in (brief.hashtags_primary + brief.hashtags_local)),
            unsafe_allow_html=True)

        st.divider()

        # Banners
        st.subheader("🎨 Generated Banners")
        bc1, bc2, bc3 = st.columns(3)
        try:
            with bc1:
                st.image(Image.open(banner.square_path), caption="1:1 — Instagram Feed", use_container_width=True)
            with bc2:
                st.image(Image.open(banner.story_path),  caption="9:16 — Story / Reel Cover", use_container_width=True)
            with bc3:
                st.image(Image.open(banner.feed_path),   caption="4:5 — FB/IG Portrait Feed", use_container_width=True)
        except Exception as e:
            st.warning(f"Banner preview error: {e}")
        st.caption("⚠️ PoC banners use PIL templates. Production uses DALL-E 3 for photorealistic food photography.")

        st.divider()

        # Copy variants
        st.subheader("✍️ Generated Copy — 3 Variants per Channel")
        st.markdown(f"**AI selected Variant {copy.selected.upper()}:** *{copy.selection_reason}*")

        tab_fb, tab_ig, tab_wa = st.tabs(["📘 Facebook", "📸 Instagram", "💬 WhatsApp"])

        with tab_fb:
            for variant_key, label in [("a","A — Hindi/Emotional"), ("b","B — English/Punchy"), ("c","C — Mixed/Family")]:
                txt = copy.facebook.get(variant_key, "")
                badge = "✅ Selected" if variant_key == copy.selected else ""
                st.markdown(f"**Variant {label}** {badge}")
                st.markdown(f'<div class="copy-box">{txt}</div>', unsafe_allow_html=True)

        with tab_ig:
            for variant_key, label in [("a","A — Hindi/Emotional"), ("b","B — English/Punchy"), ("c","C — Mixed/Family")]:
                txt = copy.instagram.get(variant_key, "")
                badge = "✅ Selected" if variant_key == copy.selected else ""
                st.markdown(f"**Variant {label}** {badge}")
                st.markdown(f'<div class="copy-box">{txt}</div>', unsafe_allow_html=True)

        with tab_wa:
            for variant_key, label in [("a","A — Hindi/Emotional"), ("b","B — English/Punchy"), ("c","C — Mixed/Family")]:
                txt = copy.whatsapp.get(variant_key, "")
                badge = "✅ Selected" if variant_key == copy.selected else ""
                st.markdown(f"**Variant {label}** {badge}")
                st.markdown(f'<div class="copy-box">{txt}</div>', unsafe_allow_html=True)

        st.divider()

        # HTML Post Previews
        st.subheader("👁️ Social Media Post Previews")
        st.markdown("These are pixel-accurate HTML previews of how the posts will appear. "
                    "In production, these get published directly via the Meta Graph API.")
        for channel, path in publish.post_urls.items():
            with st.expander(f"Open {channel.title()} Preview"):
                try:
                    with open(path, encoding="utf-8") as f:
                        html_content = f.read()
                    st.components.v1.html(html_content, height=650, scrolling=True)
                    st.caption(f"Preview file: {path}")
                except Exception as ex:
                    st.warning(f"Could not load preview: {ex}")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════
elif page == "📊 Analytics":
    st.title("📊 Analytics Dashboard")

    r = st.session_state.get("last_result")

    if r:
        analytics = r.analytics
        st.subheader(f"Last Campaign: {r.campaign_id}")
        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.metric("Performance Score",
                   f"{analytics.performance_score:.1f}/10",
                   delta="above avg" if analytics.performance_score >= 6 else "below avg")
        sc2.metric("Total Reach", f"{analytics.total_reach:,}")
        sc3.metric("Engagement Rate", f"{analytics.engagement_rate:.1f}%")
        sc4.metric("Top Channel", analytics.top_performing_channel.title())

        # Channel breakdown chart
        if analytics.channel_breakdown:
            cdf = pd.DataFrame([
                {"Channel": ch.title(), "Reach": d["reach"],
                 "Engagement Rate (%)": d["engagement_rate"],
                 "Engagements": d["engagements"]}
                for ch, d in analytics.channel_breakdown.items()
            ])
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(cdf, x="Channel", y="Reach", color="Channel",
                             title="Reach by Channel",
                             color_discrete_sequence=["#0078d4","#2196f3","#42a5f5"])
                fig.update_layout(paper_bgcolor="rgba(240,248,255,0.6)", plot_bgcolor="rgba(255,255,255,0.4)",
                                  font_color="#1a3a5c", showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig2 = px.bar(cdf, x="Channel", y="Engagement Rate (%)", color="Channel",
                              title="Engagement Rate by Channel",
                              color_discrete_sequence=["#0078d4","#2196f3","#42a5f5"])
                fig2.update_layout(paper_bgcolor="rgba(240,248,255,0.6)", plot_bgcolor="rgba(255,255,255,0.4)",
                                   font_color="#1a3a5c", showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("**✅ What worked — do again:**")
            for item in analytics.do_again:
                st.markdown(f"• {item}")
        with col_r:
            st.markdown("**⚠️ What to avoid next time:**")
            for item in analytics.avoid_next_time:
                st.markdown(f"• {item}")

        st.markdown("**💡 Key Insights:**")
        for ins in analytics.insights:
            st.markdown(f"• {ins}")

        st.divider()

    # Historical performance chart (from DB)
    st.subheader("📈 Historical Sales & Footfall (Last 30 Days)")
    with get_session() as session:
        sales_rows = session.query(DailySales).order_by(DailySales.sale_date.desc()).limit(30).all()
    if sales_rows:
        df = pd.DataFrame([{
            "Date": r.sale_date, "Footfall": r.footfall,
            "Revenue (₹)": r.revenue_inr, "Top Item": r.top_item
        } for r in reversed(sales_rows)])

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Date"], y=df["Footfall"],
                                 name="Footfall", line=dict(color="#0078d4", width=2),
                                 fill="tozeroy", fillcolor="rgba(0,120,212,0.12)"))
        fig.update_layout(title="Daily Footfall — Siliguri Suto Café",
                          paper_bgcolor="rgba(240,248,255,0.6)", plot_bgcolor="rgba(255,255,255,0.4)",
                          font_color="#1a3a5c", xaxis_title="Date",
                          yaxis_title="Customers")
        st.plotly_chart(fig, use_container_width=True)

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df["Date"], y=df["Revenue (₹)"],
                              marker_color="#2196f3", name="Revenue"))
        fig2.update_layout(title="Daily Revenue (₹) — Last 30 Days",
                           paper_bgcolor="rgba(240,248,255,0.6)", plot_bgcolor="rgba(255,255,255,0.4)",
                           font_color="#1a3a5c")
        st.plotly_chart(fig2, use_container_width=True)

    # 7-day sales prediction chart
    weather = WeatherAgent().run()
    festivals = FestivalAgent().run()
    time_ctx = TimeAgent().run()
    sales_pred = SalesPredictionAgent().run(weather, festivals, time_ctx)

    st.subheader("🔮 7-Day Footfall Forecast")
    fdf = pd.DataFrame([{
        "Day": f.day_label, "Predicted Footfall": f.predicted_footfall,
        "Revenue Est. (₹)": f.predicted_revenue_inr
    } for f in sales_pred.weekly_forecast])
    fig3 = px.bar(fdf, x="Day", y="Predicted Footfall",
                  color="Predicted Footfall",
                  color_continuous_scale=["#c8dcf0","#0078d4","#003e80"],
                  title="AI-Predicted Daily Footfall — Next 7 Days")
    fig3.update_layout(paper_bgcolor="rgba(240,248,255,0.6)", plot_bgcolor="rgba(255,255,255,0.4)",
                       font_color="#1a3a5c", showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)
    st.info(f"💡 **Today's advice:** {sales_pred.promotion_advice}")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: FESTIVAL CALENDAR
# ═══════════════════════════════════════════════════════════════════════════
elif page == "🎉 Festival Calendar":
    st.title("🎉 Festival Intelligence Calendar")
    st.markdown("Upcoming festivals with campaign lead-time recommendations. "
                "The system auto-starts campaigns ahead of each festival based on importance score.")

    festivals = FestivalAgent().run()

    if festivals.today_festival:
        st.success(f"🎊 Today is **{festivals.today_festival_display}**! "
                   f"Run a campaign now for maximum impact.")

    # Load all festivals from JSON for full year view
    import json as json_mod
    data_path = os.path.join(os.path.dirname(__file__), "demo_data", "festivals.json")
    with open(data_path, encoding="utf-8") as f:
        all_fests = json_mod.load(f)

    rows = []
    today = date.today()
    for fest in all_fests:
        try:
            fdate = date(today.year, fest["month"], fest["day"])
            if fdate < today:
                fdate = date(today.year + 1, fest["month"], fest["day"])
            days_until = (fdate - today).days
        except ValueError:
            continue

        imp = fest.get("importance", 5)
        lead = {10:7,9:5,8:3,7:3,6:2,5:2,4:1,3:1,2:1,1:0}.get(imp, 1)

        urgency = ("🔴 POST NOW" if days_until == 0
                   else "🟠 Start campaign" if days_until <= lead
                   else "🟡 Prepare" if days_until <= lead + 2
                   else "🟢 Upcoming")
        rows.append({
            "Festival": fest["display"],
            "Date": fdate.strftime("%d %b %Y"),
            "Days Away": days_until,
            "Importance": "⭐" * min(imp, 5),
            "Campaign Start": f"{lead} days before",
            "Status": urgency,
            "Color": fest.get("color","#c87941"),
        })

    rows.sort(key=lambda x: x["Days Away"])
    df = pd.DataFrame(rows)
    st.dataframe(
        df[["Festival","Date","Days Away","Importance","Campaign Start","Status"]],
        use_container_width=True, hide_index=True
    )

    # Timeline chart
    st.subheader("📅 Festival Timeline — Next 180 Days")
    timeline_rows = [r for r in rows if r["Days Away"] <= 180]
    if timeline_rows:
        tdf = pd.DataFrame(timeline_rows)
        fig = px.scatter(tdf, x="Days Away", y="Festival",
                         size=[10]*len(tdf),
                         color="Importance",
                         title="Upcoming Festival Timeline",
                         color_discrete_sequence=["#42a5f5","#2196f3","#1976d2","#0d47a1","#e53935"])
        fig.update_layout(paper_bgcolor="rgba(240,248,255,0.6)", plot_bgcolor="rgba(255,255,255,0.4)",
                          font_color="#1a3a5c")
        st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: WEATHER MONITOR
# ═══════════════════════════════════════════════════════════════════════════
elif page == "🌤️ Weather Monitor":
    st.title("🌤️ Siliguri Weather Intelligence")
    st.markdown("Real-time weather → menu recommendations → campaign tone. "
                "In PoC: uses OpenWeatherMap free API or seasonal simulation.")

    weather = WeatherAgent().run()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(f"{weather.emoji} Temperature", f"{weather.temp_c:.1f}°C",
                f"Feels like {weather.feels_like_c:.1f}°C")
    col2.metric("💧 Humidity", f"{weather.humidity_pct}%")
    col3.metric("☁️ Condition", weather.condition.title())
    col4.metric("📡 Source", weather.source.upper())

    st.markdown(f"### *\"{weather.weather_narrative}\"*")
    st.markdown(f"**Campaign tone:** `{weather.tone.title() if hasattr(weather, 'tone') else weather.campaign_tone.title()}`")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**🔥 Items to FEATURE right now:**")
        for item in weather.boosted_items:
            st.markdown(f"✅ {item}")
    with col_b:
        st.markdown("**❌ Items to SUPPRESS right now:**")
        if weather.suppressed_items:
            for item in weather.suppressed_items:
                st.markdown(f"⛔ {item}")
        else:
            st.markdown("*All items perform well in this weather*")

    # Siliguri seasonal chart
    st.divider()
    st.subheader("📅 Siliguri Seasonal Weather Patterns")
    seasonal = pd.DataFrame({
        "Month": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "Avg Temp (°C)": [13,15,22,28,32,33,29,29,28,24,18,13],
        "Cold Drink Demand": [20,25,55,80,95,90,60,60,65,55,30,20],
        "Hot Drink Demand": [90,85,50,20,10,15,40,35,30,45,75,90],
        "Rainfall (mm)": [15,20,40,80,180,450,600,580,350,120,30,10],
    })
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=seasonal["Month"], y=seasonal["Avg Temp (°C)"],
                             name="Avg Temp", line=dict(color="#e53935",width=2)))
    fig.add_trace(go.Bar(x=seasonal["Month"], y=seasonal["Cold Drink Demand"],
                         name="Cold Drink Index", marker_color="rgba(0,120,212,0.50)"))
    fig.add_trace(go.Bar(x=seasonal["Month"], y=seasonal["Hot Drink Demand"],
                         name="Hot Drink Index", marker_color="rgba(229,57,53,0.38)"))
    fig.update_layout(title="Siliguri Climate × Menu Demand Index",
                      paper_bgcolor="rgba(240,248,255,0.6)", plot_bgcolor="rgba(255,255,255,0.4)",
                      font_color="#1a3a5c", barmode="overlay")
    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: SETTINGS & INFO
# ═══════════════════════════════════════════════════════════════════════════
elif page == "⚙️ Settings & Info":
    st.title("⚙️ Settings & Platform Info")

    tab1, tab2, tab3 = st.tabs(["🔑 API Configuration", "🏗️ Architecture", "📦 PoC vs Production"])

    with tab1:
        st.subheader("Current Configuration")
        st.markdown(f"- **DEMO_MODE:** `{config.DEMO_MODE}`")
        st.markdown(f"- **LLM Provider:** Groq (`{config.GROQ_MODEL}`)")
        st.markdown(f"- **Groq API Key:** `{'✅ Set' if config.GROQ_API_KEY else '❌ Not set — using mock'}`")
        st.markdown(f"- **OpenWeather API Key:** `{'✅ Set' if config.OPENWEATHER_API_KEY else '❌ Not set — using simulation'}`")
        st.markdown(f"- **Database:** SQLite at `{config.DB_PATH}`")
        st.markdown(f"- **Output directory:** `{config.OUTPUT_DIR}`")

        st.divider()
        st.subheader("Set API Keys")
        st.markdown("Edit the `.env` file in this folder:")
        st.code("""GROQ_API_KEY=your_key_here      # free at console.groq.com
OPENWEATHER_API_KEY=your_key    # free at openweathermap.org
DEMO_MODE=false                 # set true to use mock data""", language="bash")
        st.markdown("Then restart the app: `streamlit run app.py`")

    with tab2:
        st.subheader("PoC Architecture")
        st.code("""
User Browser
     │
     ▼
┌─────────────────────────────────────────────┐
│  Streamlit Dashboard (app.py)               │
│  Port 8501 — runs on your local machine     │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  Orchestrator (orchestrator.py)             │
│  Sequential agent pipeline                  │
└──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬─────────────┘
   │  │  │  │  │  │  │  │  │  │
   ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼
  W  F  T  C  S  CS Cw Ba Pu An   (Agents)
  e  e  i  o  a  S  o  n  b  a
  a  s  m  m  l  t  p  n  l  l
  t  t  e  p  e  r  y  e  i  y
  h  i      e  s  a  w  r  s  t
  e  v      t  P  t  r     h  i
  r  a      i  r  e  i     e  c
     l      t  e  g  t     r  s
            o  d  y
            r
""", language="text")

    with tab3:
        st.subheader("PoC vs Production Comparison")
        comparison = {
            "Feature": ["LLM / AI", "Weather Data", "Database", "Vector Memory",
                        "Image Generation", "Social Publishing", "Auth / Login",
                        "Deployment", "Scheduling", "Monitoring"],
            "PoC (Zero Cost)": ["Groq API free tier (llama-3.1-8b)", "OpenWeatherMap free tier",
                                "SQLite (local file)", "Keyword matching in SQLite",
                                "PIL template banners", "HTML preview files (local)",
                                "None (local access)", "Local machine (streamlit run)",
                                "Manual trigger", "Console / Streamlit"],
            "Production (Full)": ["Azure OpenAI GPT-4o", "OpenWeatherMap Professional",
                                  "Azure PostgreSQL Flexible Server", "Pinecone vector DB",
                                  "DALL-E 3 (photorealistic)", "Meta Graph API + WATI WhatsApp",
                                  "Auth0 (RBAC: Owner/Manager/Viewer)", "Azure Container Apps",
                                  "Azure Functions (every 30 min)", "Azure Monitor + App Insights"],
            "Cost Difference": ["Free → ~$45–90/mo", "Free → $40/mo",
                                "Free → $120/mo", "Free → $0–70/mo",
                                "Free → $18–24/mo", "Free → $40/mo (WATI)",
                                "Free → $23/mo (Auth0)", "Free → $50–95/mo",
                                "Free → $2–5/mo", "Free → $8–12/mo"],
        }
        st.dataframe(pd.DataFrame(comparison), use_container_width=True, hide_index=True)
        st.info("**Total PoC cost: $0/mo** → **Production cost: ~₹40,000–50,000/mo**")
