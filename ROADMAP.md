# Roadmap — Suto Café AI Marketing Platform
## PoC → MVP → Production

---

## Phase 0: PoC (Current — Zero Cost)

**Goal:** Prove all functionalities work. Show the client.
**Timeline:** Ready now
**Cost:** ₹0/month

### What's Working
- [x] Weather Intelligence Agent (real API or simulation)
- [x] Festival Intelligence Agent (all major Indian + Bengali festivals)
- [x] Time-Based Promotion Agent
- [x] Competitor Intelligence Agent (simulated)
- [x] Sales Prediction Agent (rule-based, 7-day forecast)
- [x] Content Strategy Agent — AI CMO (Groq LLM or mock)
- [x] Copywriter Agent — 3 variants × 3 channels (Groq LLM or mock)
- [x] Banner Generator Agent (PIL templates, 3 sizes)
- [x] Publishing Agent (HTML post previews for all channels)
- [x] Analytics Agent (simulated metrics + learning insights)
- [x] Streamlit Dashboard (6-page interactive UI)
- [x] SQLite database (90 days seeded sales data)
- [x] Demo/offline mode (zero API keys needed)

---

## Phase 1: MVP (Month 1 — After Client Approval)

**Goal:** Real content generation + actual social media publishing
**Timeline:** 4 weeks post-approval
**Cost:** ~₹15,000/month

### Week 1–2: Upgrade AI + Infrastructure
- [ ] Switch Groq → Azure OpenAI GPT-4o
- [ ] Deploy PostgreSQL on Azure (replace SQLite)
- [ ] Add Azure Redis cache (30-min weather TTL)
- [ ] Set up Azure Key Vault for secrets
- [ ] GitHub Actions CI/CD pipeline

### Week 3–4: Real Publishing
- [ ] Meta Graph API integration (Facebook + Instagram posts)
- [ ] WATI WhatsApp Business API integration
- [ ] Human approval flow (push notification → approve in app)
- [ ] DALL-E 3 banner generation (replace PIL templates)
- [ ] Real analytics collection from Meta API

**Month 1 Deliverable:** System publishes real posts to Suto Café's
Facebook, Instagram, and WhatsApp — with human approval before each post.

---

## Phase 2: Autonomous (Month 2–3)

**Goal:** System runs twice daily with minimal human intervention
**Timeline:** Months 2–3
**Cost:** ~₹40,000/month

### Month 2
- [ ] Azure Functions timer trigger (every 30 min)
- [ ] LangGraph orchestration (replace sequential pipeline)
- [ ] Redis checkpointing (fault tolerance)
- [ ] Auto-approve logic for low-urgency campaigns
- [ ] Real competitor monitoring (Meta Graph API)
- [ ] Pinecone vector memory (campaign performance storage)
- [ ] Next.js 14 dashboard (replace Streamlit)
- [ ] Auth0 login (Owner/Manager/Viewer roles)

### Month 3
- [ ] Sales prediction ML model (train on real POS data)
- [ ] Video generation — RunwayML Reels (7–15 sec)
- [ ] ElevenLabs voiceover (Bengali/Hindi)
- [ ] A/B copy variant selection based on real performance
- [ ] Multi-language posts (Hindi + Bengali + English per post)
- [ ] ROI dashboard (footfall correlation with campaigns)

**Month 3 Deliverable:** Fully autonomous system. Posts 2× daily
without any human input. Learning loop active. ROI visible on dashboard.

---

## Phase 3: Intelligence (Month 4–9)

**Goal:** System becomes smarter over time, expands capabilities
**Timeline:** Months 4–9
**Cost:** ~₹50,000–75,000/month

- [ ] WhatsApp chatbot (answer customer queries automatically)
- [ ] POS system integration (actual footfall data)
- [ ] Customer segmentation by purchase history
- [ ] Dynamic pricing recommendations (low footfall → push deals)
- [ ] Festival inventory warnings (alert kitchen in advance)
- [ ] Loyalty program via WhatsApp
- [ ] Google Maps / Zomato review monitoring + response
- [ ] Sentiment analysis on comments
- [ ] Competitor pricing alerts
- [ ] Automated Meta Ads boost (budget allocation by urgency)
- [ ] Full A/B testing framework at scale

---

## Phase 4: Scale (Month 10–12)

**Goal:** Platform-grade capabilities, potentially multi-location
**Timeline:** Months 10–12
**Cost:** ~₹75,000/month

- [ ] Multi-location support (if second branch opens)
- [ ] Fine-tuned GPT-4o model on Suto's own data
- [ ] Real-time dashboard with live agent thought-streams
- [ ] Advanced Reels with local music and text animations
- [ ] Email marketing integration
- [ ] Catering / event inquiry handling via WhatsApp bot
- [ ] Annual ROI report — full marketing attribution

---

## Decision Gate After PoC

After the client demo, there are three paths:

**Option A — Go full production immediately**
Subscribe to all paid accounts, deploy to Azure. Cost: ~₹40,000/month from Day 1.

**Option B — MVP first (recommended)**
Start with real publishing only (Meta API + WATI). Cost ~₹15,000/month.
Validate ROI for 4–6 weeks, then scale to full production.

**Option C — Extend PoC with real API keys only**
Keep Streamlit + SQLite, just add real social media publishing.
Cost: ~₹5,000/month (Meta API free + WATI $40 only).
Best option to show real posts to the client without cloud costs.
