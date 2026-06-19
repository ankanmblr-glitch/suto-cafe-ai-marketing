# Suto Café — AI Marketing Platform PoC
### Autonomous AI Marketing System | Zero Budget Demo

> A fully functional proof-of-concept demonstrating all 10 AI agents
> working together to autonomously create and "publish" marketing campaigns
> for Suto Café, Siliguri, West Bengal.

---

## ⚡ Quickstart (3 steps)

```bash
# Step 1 — Setup (Windows)
setup.bat

# Step 1 — Setup (Mac/Linux)
bash setup.sh

# Step 2 — Add free API keys (or skip for demo mode)
# Edit .env and add:
#   GROQ_API_KEY=...         ← free at console.groq.com
#   OPENWEATHER_API_KEY=...  ← free at openweathermap.org
# OR just set: DEMO_MODE=true

# Step 3 — Run
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 🎭 Zero API Keys? Use Demo Mode

Set `DEMO_MODE=true` in your `.env` file. The entire platform runs
with realistic simulated data — no internet required. Perfect for offline demos.

---

## 🤖 What This PoC Demonstrates

| Agent | What It Shows | Data Source |
|---|---|---|
| 🌤️ Weather Intelligence | Siliguri weather → menu recommendations | OpenWeatherMap free / simulation |
| 🎉 Festival Intelligence | Festival countdown + campaign timing | Local JSON (no API) |
| ⏰ Time Analysis | Meal period + rush score + best post time | System clock (no API) |
| 🕵️ Competitor Monitor | Competitor alerts + differentiation | Simulated (production: Meta API) |
| 📈 Sales Prediction | 7-day footfall + revenue forecast | Rule-based model |
| 🧠 AI CMO (Content Strategy) | Full campaign brief | Groq LLM / smart mock |
| ✍️ Copywriter | 3 variants × 3 channels (FB/IG/WA) | Groq LLM / tone-aware mock |
| 🎨 Banner Generator | 3 banner sizes (1:1, 9:16, 4:5) | PIL templates |
| 📤 Publisher | HTML previews of social posts | Local file generation |
| 📊 Analytics | Performance score + learning insights | Simulated metrics |

---

## 📁 Project Structure

```
poc/
├── app.py                      ← Streamlit dashboard (run this)
├── orchestrator.py             ← Agent pipeline coordinator
├── config.py                   ← Settings from .env
├── database.py                 ← SQLite setup + seed data
├── requirements.txt
├── .env.example                ← Copy to .env and fill in keys
├── setup.bat / setup.sh        ← One-command setup
│
├── agents/
│   ├── weather_agent.py        ← OpenWeatherMap + seasonal mock
│   ├── festival_agent.py       ← 15+ Indian/Bengali festivals
│   ├── time_agent.py           ← Meal period + rush scoring
│   ├── competitor_agent.py     ← Simulated competitor intelligence
│   ├── sales_prediction_agent.py ← Rule-based footfall forecast
│   ├── content_strategy_agent.py ← AI CMO (Groq LLM)
│   ├── copywriter_agent.py     ← Multi-variant copy (Groq LLM)
│   ├── banner_agent.py         ← PIL banner generation
│   ├── publishing_agent.py     ← HTML post previews
│   └── analytics_agent.py     ← Metrics + learning insights
│
├── demo_data/
│   ├── menu.json               ← Full Suto Café menu
│   ├── festivals.json          ← Festival calendar
│   └── historical_sales.csv    ← 90 days mock sales data
│
├── output/
│   ├── banners/                ← Generated PNG banners
│   └── posts/                  ← HTML post previews
│
├── README.md                   ← This file
├── TECHNICAL_REQUIREMENTS.md   ← Tech stack + architecture
├── FUNCTIONAL_REQUIREMENTS.md  ← All 12 functional requirements
├── POC_vs_PRODUCTION.md        ← What changes when going live
└── ROADMAP.md                  ← PoC → MVP → Production plan
```

---

## 🔑 Free API Keys (Optional)

| Key | Where to Get | Takes | Free Limit |
|---|---|---|---|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | 60 seconds | 30 req/min, unlimited tokens/day |
| `OPENWEATHER_API_KEY` | [openweathermap.org/api](https://openweathermap.org/api) | 2 minutes | 60 calls/min, 1M calls/month |

Both are completely free. No credit card required.

---

## 🖥️ Dashboard Pages

1. **🏠 Dashboard** — Live Siliguri context (weather, time, festivals), recent campaigns, quick run button
2. **🚀 Run Campaign** — Watch all 10 agents execute in real-time with progress indicators
3. **📄 Content Preview** — Generated copy (all variants), banner images, interactive HTML post previews
4. **📊 Analytics** — Performance charts, 7-day sales forecast, historical footfall trends
5. **🎉 Festival Calendar** — Full-year festival timeline with campaign countdown and urgency indicators
6. **🌤️ Weather Monitor** — Current conditions, menu demand mapping, Siliguri seasonal patterns

---

## 📊 What the Client Sees

After clicking **Run Campaign**, within 30 seconds (or 5 in demo mode):

✅ Real-time agent execution log (all 10 agents)
✅ Campaign brief with theme, hero items, target audience
✅ 3 copywriting variants per channel (FB + IG + WhatsApp)
✅ 3 banner images (social-media ready sizes)
✅ Pixel-accurate HTML previews of Facebook, Instagram, WhatsApp posts
✅ Analytics report with performance score and learning insights
✅ 7-day sales forecast chart
✅ Historical performance dashboard

---

## 🚀 After Client Approval

See `ROADMAP.md` for the PoC → Production migration plan.
See `POC_vs_PRODUCTION.md` for component-by-component cost breakdown.
See `../must_have_accounts_creds.md` for all accounts to set up.

**Estimated time from approval to first real post:** 2–4 weeks.
**Estimated cost to go live:** ₹15,000/month (MVP) → ₹40,000/month (full production).
