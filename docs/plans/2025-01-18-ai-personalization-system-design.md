# AI-Powered Portfolio Personalization System - Design Document

**Date:** January 18, 2026  
**Status:** Design Approved - Ready for Implementation  
**Owner:** Nguyễn Hữu Lộc

---

## 1. Executive Summary

Build an AI-powered tracking and personalization system that:
- Tracks user behavior via GA4 custom events (10+ event types)
- Analyzes patterns using LLM (Gemini/DeepSeek) with fallback support
- Personalizes portfolio content per user segment in real-time
- Provides xAI-style insights dashboard for admin analysis

**Deployment:** Python/FastAPI backend + Supabase PostgreSQL + Static frontend

---

## 2. Architecture Overview

### 2.1 System Components

```
┌─────────────────────────────────────────────────────┐
│               FRONTEND (Static)                      │
│  - index.html (portfolio)                           │
│  - /admin (dashboard, protected)                    │
│  - GA4 custom event tracking                        │
│  - assets/js/personalization.js (apply rules)       │
└────────────────┬────────────────────────────────────┘
                 │ HTTP REST API
┌────────────────▼────────────────────────────────────┐
│          FASTAPI BACKEND (Python)                    │
│  - GA4 Service (fetch analytics)                    │
│  - LLM Service (Gemini + DeepSeek)                  │
│  - Analysis Engine (pattern detection)              │
│  - Scheduler (hourly analysis jobs)                 │
│  - REST API endpoints                               │
└────────────────┬────────────────────────────────────┘
                 │ SQL
┌────────────────▼────────────────────────────────────┐
│        SUPABASE (PostgreSQL)                         │
│  - analytics_raw (GA4 snapshots)                    │
│  - user_segments (cached classifications)           │
│  - personalization_rules (per-segment rules)        │
│  - llm_insights (admin insights + explanations)     │
└─────────────────────────────────────────────────────┘
```

### 2.2 Custom Events (GA4)

**User Behavior:**
- `project_click` (params: project_id, category)
- `skill_hover` (params: skill_name, duration)
- `section_view` (params: section_name, time_spent)
- `contact_intent` (params: contact_type)
- `language_switch` (params: from_lang, to_lang)

**Engagement:**
- `deep_read` (params: project_id, duration)
- `repeat_view` (params: item_id, view_count)
- `scroll_depth` (params: milestone: 25%/50%/75%/100%)
- `career_timeline_interact` (params: company, position)

**Intent Signals:**
- `download_resume` (if available)
- `external_link_click` (params: link_type, destination)

---

## 3. Data Flow

### 3.1 Hourly Analysis Pipeline

```
[Scheduled Job] 
  ↓
[GA4 API] → Fetch last 1h events → [analytics_raw]
  ↓
[Event Aggregation] → Group by user, compute metrics
  ↓
[LLM Segmentation] → Classify each user → [user_segments]
  ↓
[Rule Generation] → Create personalization rules per segment → [personalization_rules]
  ↓
[Insights Generation] → xAI analysis of trends → [llm_insights]
  ↓
[Cache Updated] → Frontend can fetch fresh personalization
```

### 3.2 Frontend Personalization Flow

```
User visits portfolio
  ↓
[GA4] ← Track custom events during session
  ↓
Frontend identifies GA4 client ID
  ↓
GET /api/personalization?user_id={ga4_client_id}
  ↓
Backend returns cached rules for user's segment
  ↓
Apply DOM changes (reorder sections, highlight projects, etc.)
  ↓
User sees personalized portfolio
```

---

## 4. LLM Prompting Strategy

### 4.1 Segmentation Prompt

Classify user into: ML_ENGINEER, FULLSTACK_DEV, RECRUITER, STUDENT, CASUAL

Input:
- Projects clicked
- Skills hovered
- Sections viewed
- Time metrics
- Contact intents

Output: `{segment, confidence, reasoning_xai}`

### 4.2 Personalization Rules Prompt

Generate rules optimized for each segment:
- Which sections to prioritize
- Which projects to feature
- Which skills to highlight
- Why these changes

Output: `{priority_sections, featured_projects, highlight_skills, reasoning}`

### 4.3 Admin Insights Prompt

Analyze trends with xAI explanations:
- WHAT happened (metrics)
- WHY it happened (causal reasoning)
- SO WHAT (business impact)
- RECOMMENDATION (actionable next steps)

---

## 5. Database Schema

### 5.1 analytics_raw
```sql
- id (PK)
- ga4_event_id (UNIQUE)
- event_name
- user_pseudo_id
- event_params (JSONB)
- event_timestamp
- created_at
```

### 5.2 user_segments
```sql
- id (PK)
- user_pseudo_id (UNIQUE)
- segment (ML_ENGINEER, FULLSTACK_DEV, RECRUITER, STUDENT, CASUAL)
- confidence (float)
- reasoning (text, xAI explanation)
- event_summary (JSONB)
- analyzed_at
- expires_at (24h TTL)
```

### 5.3 personalization_rules
```sql
- id (PK)
- segment (UNIQUE)
- priority_sections (TEXT[])
- featured_projects (TEXT[])
- highlight_skills (TEXT[])
- css_overrides (JSONB, optional)
- reasoning (text)
- created_at
```

### 5.4 llm_insights
```sql
- id (PK)
- analysis_period (DATERANGE)
- total_visitors (INT)
- segment_distribution (JSONB)
- top_events (JSONB)
- conversion_metrics (JSONB)
- insight_summary (TEXT, markdown)
- recommendations (JSONB)
- generated_at
```

---

## 6. API Endpoints

### 6.1 Public Endpoints

**POST /api/events**
- Fallback for custom event tracking
- Body: `{event_name, user_id, params}`

**GET /api/personalization?user_id={id}**
- Returns cached rules for user's segment
- Response: `{segment, rules, cache_ttl}`

### 6.2 Admin Endpoints (JWT Protected)

**GET /api/admin/dashboard**
- Returns dashboard data
- Response: `{total_visitors, segments, top_events, conversion_rate, insights_narrative, recommendations, last_updated}`

**GET /api/admin/segments**
- Detailed breakdown per segment

**GET /api/admin/events?hours=24**
- Raw event stream (searchable, paginated)

**POST /api/admin/rules**
- Manually override auto-generated rules
- Body: `{segment, rules_override}`

---

## 7. Error Handling & Resilience

### 7.1 GA4 Failures
- Retry with exponential backoff
- Fall back to cached events if API unreachable
- Alert admin if credentials expired

### 7.2 LLM Failures
- Provider fallback chain: Gemini → DeepSeek → heuristic fallback
- Graceful degradation (use rule-based segmentation if all LLMs fail)
- Retry with different model if rate limited

### 7.3 Database Failures
- Connection pooling + pre-ping verification
- Automatic retry with backoff
- Graceful error responses (site still works without personalization)

### 7.4 Frontend Failures
- If `/api/personalization` fails, site renders normally (no personalization)
- Events still tracked via GA4 (SDK-based)

---

## 8. Performance & Optimization

### 8.1 Caching Strategy
- Browser cache: Personalization rules 1 hour
- Database cache: TTL 24 hours for user segments
- Materialized views for common admin queries

### 8.2 Cost Optimization
- LLM: ~$0.10/hour (Gemini free tier + DeepSeek)
- GA4 API: 1 call/hour (within free quota)
- Supabase: Free tier (500K rows/month)
- Infrastructure: $5-10/month VPS or $1/month Cloud Run

---

## 9. Implementation Phases

### Phase 1: MVP (Weeks 1-2)
- [ ] FastAPI project setup
- [ ] Supabase database setup
- [ ] GA4 integration (basic events)
- [ ] LLM service (Gemini only)
- [ ] Hourly scheduler job
- [ ] Basic personalization (priority_sections)
- [ ] `/api/personalization` endpoint

### Phase 2: Enhanced Features (Weeks 3-4)
- [ ] Full custom event tracking (all 10+ events)
- [ ] LLM provider fallback (DeepSeek)
- [ ] xAI explanations
- [ ] Admin dashboard UI (basic)
- [ ] Event search/filter

### Phase 3: Polish & Deploy (Weeks 5-6)
- [ ] Error handling + resilience testing
- [ ] Performance optimization
- [ ] Admin dashboard full featured
- [ ] Documentation
- [ ] Production deployment

---

## 10. Success Criteria

- [ ] Portfolio loads without personalization if API fails
- [ ] Segmentation confidence > 70% for ≥80% of users
- [ ] Personalization API response < 200ms (cached)
- [ ] Admin dashboard shows xAI explanations (not just metrics)
- [ ] LLM provider fallback works (tested manually)
- [ ] Coverage: 10+ custom events tracked reliably
- [ ] Cost < $20/month (all services combined)

---

## 11. Technical Decisions

| Decision | Choice | Reasoning |
|----------|--------|-----------|
| Backend | Python/FastAPI | Data processing strength, LLM libraries, async support |
| Database | Supabase PostgreSQL | Managed, free tier generous, good for analytics |
| LLM Provider | Gemini + DeepSeek | Free tier (Gemini), cost-effective (DeepSeek), flexible abstraction |
| Caching | Periodic refresh (hourly) | Fast for users, cost-effective, acceptable staleness |
| Deployment | Docker + VPS/Cloud Run | Simple, portable, low cost |
| Event Tracking | GA4 + Fallback API | Industry standard + fallback for SDK failures |

---

## 12. Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| LLM rate limits | Analytics blocked | Provider fallback + cached results |
| GA4 API quota | No new data | Use historical cache, alert admin |
| Database outage | No personalization | Frontend graceful degradation |
| Cold start latency | Slow API | Pre-warm connections, use materialized views |
| Privacy concerns | User trust | Transparent xAI explanations, no PII storage |

---

## 13. Future Enhancements

- Real-time personalization (if needed)
- A/B testing framework
- Custom segment rules (no-code UI)
- Multi-portfolio support
- Mobile app personalization
- Predictive analytics (next actions)

---

**Next Steps:** Start Phase 1 implementation. Create implementation plan with detailed code tasks.
