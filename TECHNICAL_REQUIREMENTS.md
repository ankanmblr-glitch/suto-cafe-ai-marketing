# Technical Requirements — Suto Café AI Marketing PoC

## System Overview

A locally-runnable, single-machine AI marketing platform that demonstrates the full autonomous campaign pipeline for Suto Café, Siliguri. All features work at zero cost using free tiers and open-source tools.

---

## Tech Stack (PoC)

| Layer | Technology | Version | Cost |
|---|---|---|---|
| UI Dashboard | Streamlit | ≥ 1.32 | Free |
| LLM (Content Generation) | Groq API — llama-3.1-8b-instant | Latest | Free (30 req/min) |
| Weather API | OpenWeatherMap | Free tier | Free (60 calls/min) |
| Database | SQLite via SQLAlchemy | ≥ 2.0 | Free |
| Image Generation | PIL / Pillow (template banners) | ≥ 10.2 | Free |
| Data Visualization | Plotly | ≥ 5.18 | Free |
| Data Processing | Pandas | ≥ 2.0 | Free |
| HTTP Client | Requests / HTTPX | Latest | Free |
| Config Management | python-dotenv | Latest | Free |
| Runtime | Python | 3.11+ | Free |

---

## Runtime Requirements

- **OS:** Windows 10/11, macOS 12+, or Ubuntu 20+
- **Python:** 3.11 or higher
- **RAM:** 4 GB minimum (8 GB recommended)
- **Disk:** 500 MB free (for venv + SQLite + generated assets)
- **Network:** Required only for Groq API and OpenWeatherMap calls
- **Browser:** Any modern browser (Chrome, Edge, Firefox) for Streamlit UI

---

## Agent Architecture

### Pipeline (Sequential, Synchronous)
```
START
  ↓
WeatherAgent         → Siliguri weather context
  ↓
FestivalAgent        → Upcoming festivals + countdown
  ↓
TimeAgent            → Meal period, rush score, day type
  ↓
CompetitorAgent      → Competitor intelligence (simulated in PoC)
  ↓
SalesPredictionAgent → Footfall + revenue forecast (rule-based)
  ↓
ContentStrategyAgent → Campaign brief (GPT-4 class via Groq)
  ↓
CopywriterAgent      → 3 copy variants × 3 channels (Groq LLM)
  ↓
BannerAgent          → 3 banner images (PIL templates)
  ↓
PublishingAgent      → HTML post previews (production: Meta API + WATI)
  ↓
AnalyticsAgent       → Performance metrics + learning insights
  ↓
END  → Results stored in SQLite, previews saved to output/
```

### State Management
- Each agent returns a typed Python dataclass
- Orchestrator passes state between agents as function arguments
- All results persisted to SQLite after each cycle
- Session state in Streamlit holds last campaign for preview

---

## Data Storage

### SQLite Tables
| Table | Purpose |
|---|---|
| `campaigns` | Campaign records with copy, theme, metrics |
| `agent_runs` | Execution log per agent (name, duration, status) |
| `daily_sales` | Historical sales data (seeded: 90 days) |

### File Output
| Directory | Contents |
|---|---|
| `output/banners/` | PIL-generated PNG banner images (3 per campaign) |
| `output/posts/` | HTML post previews (Facebook, Instagram, WhatsApp) |

---

## API Integrations (PoC)

### Groq API (LLM)
- **Endpoint:** `https://api.groq.com/openai/v1`
- **Model:** `llama-3.1-8b-instant`
- **Used by:** ContentStrategyAgent, CopywriterAgent
- **Fallback:** Smart pre-written mock responses (no API key needed)
- **Rate limit:** 30 requests/minute (free tier) — sufficient for PoC

### OpenWeatherMap (Weather)
- **Endpoint:** `api.openweathermap.org/data/2.5/weather`
- **Params:** `lat=26.7271&lon=88.3953` (Siliguri coordinates)
- **Fallback:** Month-based seasonal simulation

---

## Security (PoC)
- All API keys stored in `.env` file (never hardcoded)
- `.env` excluded from git via `.gitignore`
- No authentication required (local machine only)
- No PII collected or stored

---

## Performance Targets (PoC)

| Metric | Target | Actual |
|---|---|---|
| Full cycle time (mock mode) | < 5 seconds | ~2–3 seconds |
| Full cycle time (Groq API) | < 30 seconds | ~8–15 seconds |
| Streamlit page load | < 2 seconds | ~1 second |
| Banner generation (PIL) | < 3 seconds | ~1–2 seconds |
