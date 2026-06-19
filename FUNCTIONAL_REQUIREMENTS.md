# Functional Requirements — Suto Café AI Marketing PoC

## Purpose
Demonstrate to the Suto Café owner that an autonomous AI marketing system can:
1. Understand Siliguri's real-time context (weather, time, festivals)
2. Generate localised, brand-consistent marketing content automatically
3. Publish across Facebook, Instagram, and WhatsApp without human input
4. Learn from campaign performance to improve over time

---

## FR-01: Weather Intelligence
**What it does:** Reads current Siliguri weather and maps it to menu items and campaign tone.

| Condition | Boosted Items | Campaign Tone |
|---|---|---|
| Hot (>30°C) | Cold Coffee, Frappes, Ice Tea, Mocktails | Refreshing |
| Rainy | Tandoori Maggi, Hot Chocolate, Cappuccino | Cozy |
| Cold (<18°C) | Hot Chocolate, Cappuccino, Masala Chai, Waffles | Warm |
| Pleasant | All items perform, Brownie Frappe, Pizza | Energetic |

**PoC:** OpenWeatherMap free API or seasonal simulation.
**Production:** Same API (Professional plan for higher call frequency).

---

## FR-02: Festival Intelligence
**What it does:** Tracks 15+ Indian and Bengali festivals, calculates days-until, and auto-starts campaigns at the right lead time.

| Importance | Lead Time | Examples |
|---|---|---|
| 10 (critical) | 7 days | Durga Puja |
| 9 (major) | 5 days | New Year, Diwali, Poila Boishakh |
| 8 (high) | 3 days | Holi, Valentine's Day, Eid |
| 5–7 (medium) | 2 days | Raksha Bandhan, Teacher's Day |
| 1–4 (low) | Same day | Rose Day, commercial events |

**PoC:** Hardcoded festival JSON — no API needed.
**Production:** Same data, auto-updated annually + Google Calendar integration.

---

## FR-03: Time-Based Promotion
**What it does:** Identifies the current meal period, rush score (0–1), and optimal post timing.

| Period | Hours | Rush Score | Recommended Items |
|---|---|---|---|
| Breakfast | 7–10 AM | 0.6 | Cappuccino, Chai, Sandwich |
| Lunch | 12–3 PM | 0.75–0.9 | Pizza, Falafel Wrap, Pasta |
| Snack | 3–7 PM | 0.8 | Frappes, Cold Coffee, Nachos |
| Dinner | 7–10 PM | 0.7–0.85 | Pizza, Burgers, Pasta |

**PoC & Production:** Pure Python — no external dependencies.

---

## FR-04: Competitor Monitoring
**What it does:** Tracks competitor cafés in Siliguri, identifies their promotions, and recommends differentiation strategies.

**PoC:** Simulated competitor alerts with realistic data.
**Production:** Meta Graph API scraping of competitor public pages + Pinecone semantic similarity to avoid copying their content.

---

## FR-05: Sales Prediction
**What it does:** Forecasts today's footfall and revenue + 7-day outlook using weather, festival, and time multipliers on historical data.

Example: Base weekday 62 customers × rain multiplier 1.08 × festival multiplier 1.2 × rush score 0.9 = **72 customers predicted**

**PoC:** Rule-based model using multipliers on seeded historical data.
**Production:** Scikit-learn GBDT model trained on 6+ months of real POS + social + weather data.

---

## FR-06: Content Strategy (AI CMO)
**What it does:** Synthesises all context signals into a structured campaign brief:
- Campaign theme and display name
- 2–3 hero menu items to feature
- Target audience (youth 20–30 or families 30–45 or all)
- Channels (Facebook / Instagram / WhatsApp)
- Campaign tone and key messages
- Local Siliguri reference (Tista River, Hill Cart Road, etc.)
- Hashtags (primary + Siliguri-local)
- Whether human approval is required

**PoC:** Groq API (llama-3.1-8b-instant, free) or smart mock.
**Production:** Azure OpenAI GPT-4o with campaign memory via Pinecone.

---

## FR-07: Social Media Copywriting
**What it does:** Generates 3 caption variants per channel, each with a distinct tone:
- **Variant A:** Hindi-heavy, emotional, hyperlocal
- **Variant B:** English-primary, punchy, youth-oriented
- **Variant C:** Mixed, story-driven, family-friendly

AI selects the best variant and explains why.

**Platforms:**
- Instagram: 3–5 sentences, 5–8 emojis, 10–15 hashtags, question CTA
- Facebook: 4–5 sentences, storytelling, 3–5 hashtags, address hint
- WhatsApp: 2–3 lines only, no hashtags, conversational, price mentioned

**PoC:** Groq API or tone-aware mock templates.
**Production:** Azure OpenAI GPT-4o with A/B performance feedback loop via Pinecone.

---

## FR-08: Banner / Visual Generation
**What it does:** Generates 3 banner sizes per campaign with on-brand visuals:
- 1:1 (1024×1024) — Instagram feed post
- 9:16 (608×1080) — Story / Reel cover
- 4:5 (820×1024) — Facebook/Instagram portrait feed

Each banner includes: gradient background in campaign tone colours, hero food emoji, theme name, hero items, Suto Café branding, and CTA on accent bar.

**PoC:** PIL/Pillow template generation — zero cost.
**Production:** DALL-E 3 photorealistic food photography + PIL post-processing for text/logo overlay.

---

## FR-09: Multi-Channel Publishing
**What it does:** Publishes approved content to all three channels.

| Channel | PoC | Production |
|---|---|---|
| Facebook | HTML preview file | Meta Graph API (pages_manage_posts) |
| Instagram | HTML preview file | Instagram Graph API (instagram_content_publish) |
| WhatsApp | HTML preview file | WATI WhatsApp Business API broadcast |

**HTML previews** in PoC are pixel-accurate renderings of exactly how posts will appear, including like/comment/share buttons and engagement numbers.

---

## FR-10: Analytics & Learning
**What it does:** After publishing, collects performance data and generates learning insights:
- Per-channel reach, impressions, engagement rate
- Performance score (0–10)
- Which copy variant performed best
- What to repeat vs avoid next campaign
- Stores in database for continuous improvement

**PoC:** Simulated metrics based on realistic engagement benchmarks.
**Production:** Meta Graph API Insights endpoint (48-hour delay for real data) + Pinecone memory storage.

---

## FR-11: Dashboard (UI)
The Streamlit dashboard provides 6 views:

| Page | What it Shows |
|---|---|
| Dashboard | Live context, quick metrics, recent campaigns |
| Run Campaign | Real-time agent execution with progress |
| Content Preview | Generated copy (all variants) + banner images + post previews |
| Analytics | Performance charts, 7-day sales forecast, historical footfall |
| Festival Calendar | Full-year festival timeline with campaign countdown |
| Weather Monitor | Current conditions + seasonal demand patterns |

---

## FR-12: Demo / Offline Mode
When `DEMO_MODE=true` (or no API keys set), the system runs entirely offline using:
- Seasonal weather simulation for Siliguri
- Pre-written smart mock responses for LLM agents
- Seeded 90-day historical sales data

This allows the full platform to be demonstrated with no internet connection and zero API costs.

---

## Non-Functional Requirements

| Requirement | PoC Target |
|---|---|
| Full cycle execution time | < 30 seconds (API) / < 5 seconds (mock) |
| Offline / no-API operation | 100% functional in demo mode |
| Single command startup | `streamlit run app.py` after setup |
| Browser compatibility | Chrome, Edge, Firefox |
| Data persistence | SQLite file survives app restarts |
| Generated assets | Banners + HTML previews saved to disk, viewable outside app |
