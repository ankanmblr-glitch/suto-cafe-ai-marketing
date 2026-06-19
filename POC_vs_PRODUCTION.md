# PoC vs Production Comparison
## Suto Café AI Marketing Platform

This document maps every PoC component to its production equivalent,
with cost, timeline, and migration effort for each.

---

## Architecture Comparison

| Aspect | PoC (Zero Cost) | Production (Full) |
|---|---|---|
| Deployment | Local machine, 1 command | Azure Container Apps (2 containers) |
| Orchestration | Sequential Python functions | LangGraph with Redis checkpointing |
| Scheduling | Manual trigger | Azure Functions timer (every 30 min) |
| Auth | None (local) | Auth0 PKCE (Owner/Manager/Viewer RBAC) |
| Frontend | Streamlit | Next.js 14 + React 18 + shadcn/ui |
| Monitoring | Console output | Azure Monitor + Application Insights |

---

## Component-by-Component Breakdown

### 1. LLM / AI Content Generation
| | PoC | Production |
|---|---|---|
| Provider | Groq API (free tier) | Azure OpenAI |
| Models | llama-3.1-8b-instant | GPT-4o (copy) + GPT-4o-mini (classification) |
| Context window | 8,192 tokens | 128K tokens |
| Rate limit | 30 req/min | Dedicated capacity (50K TPM) |
| Cost | $0/month | $45–90/month |
| Migration effort | Swap `groq` for `openai` SDK, 1 line change | Low |

### 2. Weather Data
| | PoC | Production |
|---|---|---|
| Provider | OpenWeatherMap (free tier) | OpenWeatherMap (Professional) |
| Call frequency | Manual (per campaign run) | Every 30 minutes (Azure Function timer) |
| Cost | $0/month | $40/month |
| Migration effort | Add paid API key, enable caching | Very low |

### 3. Database
| | PoC | Production |
|---|---|---|
| System | SQLite (local file) | Azure PostgreSQL Flexible Server |
| Schema | Same (SQLAlchemy models) | Same + Alembic migrations |
| HA / Backup | None | Zone-redundant HA, 14-day backup |
| Cost | $0/month | $120/month |
| Migration effort | Run `alembic upgrade head` once | Low |

### 4. Image / Banner Generation
| | PoC | Production |
|---|---|---|
| Method | PIL template banners | DALL-E 3 photorealistic food photography |
| Quality | Functional for demo | Professional food photography quality |
| Sizes | Same 3 sizes (1:1, 9:16, 4:5) | Same |
| Post-processing | PIL text overlay | PIL text + logo + price tags |
| Cost | $0/month | $18–24/month |
| Migration effort | Replace BannerAgent._draw_banner() with DALL-E API call | Low |

### 5. Social Media Publishing
| | PoC | Production |
|---|---|---|
| Facebook | HTML preview file | Meta Graph API (pages_manage_posts) |
| Instagram | HTML preview file | Instagram Graph API (instagram_content_publish) |
| WhatsApp | HTML preview file | WATI WhatsApp Business API |
| Approval flow | Not needed (no real publishing) | Push notification → owner approves in app |
| Cost | $0/month | $40/month (WATI) |
| Migration effort | Replace PublishingAgent.run() with API calls | Medium |

### 6. Vector Memory (Campaign Learning)
| | PoC | Production |
|---|---|---|
| System | Keyword matching in SQLite | Pinecone vector database |
| Embeddings | None (rule-based similarity) | text-embedding-ada-002 (1536-dim) |
| Use cases | — | Avoid repeating campaigns, find best performing themes |
| Cost | $0/month | $0–70/month |
| Migration effort | Add Pinecone client + embedding calls to AnalyticsAgent | Medium |

### 7. Cache
| | PoC | Production |
|---|---|---|
| System | Python dict (in-memory) | Azure Redis Cache |
| TTL | Per-session only | 30-min weather cache, 1-hour strategy cache |
| Cost | $0/month | $65/month |
| Migration effort | Replace dict with Redis client calls | Low |

### 8. Competitor Monitoring
| | PoC | Production |
|---|---|---|
| Method | Simulated mock data | Meta Graph API (public page scraping) + Pinecone similarity |
| Frequency | Every campaign cycle | Twice daily (8 AM + 6 PM) |
| Cost | $0/month | Included in Meta API free tier |
| Migration effort | Replace CompetitorAgent mock with real API calls | High |

### 9. Video Generation (Reels)
| | PoC | Production |
|---|---|---|
| Method | Not implemented in PoC | RunwayML API (image-to-video) |
| Voiceover | Not implemented | ElevenLabs Bengali/Hindi voice |
| Duration | — | 7–15 second Reels |
| Cost | $0/month | $35 (RunwayML) + $5 (ElevenLabs) |
| Migration effort | Add VideoGeneratorAgent (new) | High |

---

## Migration Checklist (PoC → Production)

### Low Effort (< 1 day each)
- [ ] Swap Groq SDK for Azure OpenAI SDK
- [ ] Enable weather caching (30-min TTL)
- [ ] Switch SQLite to PostgreSQL connection string
- [ ] Add Auth0 JWT middleware to API

### Medium Effort (1–3 days each)
- [ ] Build PublishingAgent with Meta Graph API integration
- [ ] Add WATI WhatsApp broadcast integration
- [ ] Add Pinecone for vector memory in AnalyticsAgent
- [ ] Build human approval push notification flow
- [ ] Set up GitHub Actions CI/CD pipeline

### High Effort (1–2 weeks each)
- [ ] Build Next.js 14 frontend to replace Streamlit
- [ ] Set up LangGraph orchestration with Redis checkpointing
- [ ] Deploy to Azure Container Apps (using main.bicep)
- [ ] Implement real competitor monitoring via Meta API
- [ ] Add VideoGeneratorAgent (RunwayML + ElevenLabs)
- [ ] Train ML sales prediction model on real POS data

---

## Total Cost Summary

| Phase | Monthly Cost (INR) | Monthly Cost (USD) |
|---|---|---|
| **PoC (this document)** | **₹0** | **$0** |
| MVP / Staging (Month 1–3) | ~₹15,000 | ~$180 |
| Production Launch | ~₹40,000–50,000 | ~$471–639 |
| At Scale | ~₹58,000–75,000 | ~$700–900 |
