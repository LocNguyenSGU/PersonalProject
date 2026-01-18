# AI-Powered Portfolio Personalization - Implementation Plan

**Project:** Portfolio AI Personalization System  
**Version:** 1.0 - Phase 1 (MVP)  
**Date:** January 18, 2026  
**Duration:** 2 weeks (Phase 1)

---

## Project Structure

```
portfolio/
├── backend/                          # NEW - FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app entry
│   │   ├── config.py                # Config, env vars
│   │   ├── dependencies.py          # DI (DB, LLM clients)
│   │   ├── models/                  # Pydantic models
│   │   │   ├── __init__.py
│   │   │   ├── events.py            # EventPayload schema
│   │   │   ├── segments.py          # UserSegment schema
│   │   │   └── rules.py             # PersonalizationRules schema
│   │   ├── services/                # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── ga4_service.py       # GA4 API integration
│   │   │   ├── llm_service.py       # LLM providers (Gemini, DeepSeek)
│   │   │   ├── analysis_engine.py   # Segmentation + rules generation
│   │   │   └── scheduler.py         # APScheduler jobs
│   │   ├── database/                # Database layer
│   │   │   ├── __init__.py
│   │   │   ├── db.py                # SQLAlchemy setup, Supabase connection
│   │   │   ├── migrations/          # Alembic migrations
│   │   │   │   ├── env.py
│   │   │   │   └── versions/
│   │   │   │       └── 001_initial_schema.py
│   │   │   └── models.py            # SQLAlchemy ORM models
│   │   ├── api/                     # API routes
│   │   │   ├── __init__.py
│   │   │   ├── public.py            # /api/personalization, /api/events
│   │   │   ├── admin.py             # /api/admin/* (protected)
│   │   │   └── health.py            # /health (for monitoring)
│   │   ├── auth/                    # Authentication
│   │   │   ├── __init__.py
│   │   │   └── jwt.py               # JWT token validation
│   │   ├── prompts/                 # LLM prompt templates
│   │   │   ├── __init__.py
│   │   │   ├── segment.prompt       # Segmentation prompt
│   │   │   └── rules.prompt         # Rules generation prompt
│   │   └── utils/                   # Utilities
│   │       ├── __init__.py
│   │       ├── logger.py
│   │       └── exceptions.py
│   ├── tests/                       # Unit + integration tests
│   │   ├── __init__.py
│   │   ├── test_ga4_service.py
│   │   ├── test_llm_service.py
│   │   ├── test_analysis_engine.py
│   │   └── test_api.py
│   ├── requirements.txt             # Python dependencies
│   ├── Dockerfile                   # Docker image
│   ├── docker-compose.yml           # Local dev setup
│   └── .env.example                 # Example env vars
│
├── assets/js/
│   ├── personalization.js           # MODIFIED - Apply rules to DOM
│   ├── analytics.js                 # NEW - GA4 custom event tracker
│   └── (existing files)
│
├── admin/                           # NEW - Admin dashboard
│   ├── index.html                   # Protected dashboard UI
│   ├── assets/
│   │   ├── css/dashboard.css
│   │   └── js/dashboard.js          # Dashboard logic
│   └── auth/                        # Auth UI
│       └── login.html
│
├── docs/
│   ├── plans/
│   │   ├── 2025-01-18-ai-personalization-system-design.md  # (existing)
│   │   └── 2025-01-18-implementation-plan.md               # THIS FILE
│   ├── API.md                       # API documentation
│   ├── SETUP.md                     # Setup instructions
│   └── DEPLOYMENT.md                # Deployment guide
│
├── .github/
│   ├── workflows/
│   │   └── backend-tests.yml        # NEW - CI/CD for backend
│   └── (existing)
│
└── (existing: index.html, assets, etc.)
```

---

## PHASE 1: MVP Implementation (Weeks 1-2)

### ✅ WEEK 1: Foundation & Setup

#### Task 1.1: Project Setup & Dependencies
**Objective:** Initialize FastAPI project with all dependencies  
**Effort:** 2 hours

**Sub-tasks:**
- [ ] 1.1.1 Create `/backend` directory structure
- [ ] 1.1.2 Create `requirements.txt` with:
  - fastapi, uvicorn
  - sqlalchemy, alembic (database)
  - google-analytics-data (GA4 API client)
  - google-generativeai (Gemini API)
  - httpx (HTTP client for DeepSeek)
  - python-dotenv
  - apscheduler (scheduler)
  - pydantic, pydantic-settings
  - python-jose, passlib (JWT auth)
  - pytest, pytest-asyncio (testing)
- [ ] 1.1.3 Create `backend/.env.example` with placeholder keys:
  ```
  SUPABASE_URL=your_supabase_url
  SUPABASE_KEY=your_supabase_key
  GA4_PROPERTY_ID=your_ga4_property_id
  GA4_CREDENTIALS_JSON=path_to_credentials.json
  GEMINI_API_KEY=your_gemini_key
  DEEPSEEK_API_KEY=your_deepseek_key
  ADMIN_SECRET=your_jwt_secret
  ENVIRONMENT=development
  ```
- [ ] 1.1.4 Create `backend/Dockerfile` for containerization
- [ ] 1.1.5 Create `backend/docker-compose.yml` for local dev (optional, first pass can skip)

**Definition of Done:**
- `requirements.txt` has all dependencies
- `docker-compose.yml` (if created) runs without errors
- `.env.example` documents all required variables

---

#### Task 1.2: Supabase Schema & Database Setup
**Objective:** Create PostgreSQL tables and Supabase connection  
**Effort:** 3 hours

**Sub-tasks:**
- [ ] 1.2.1 Create Supabase account & project (if not already done)
- [ ] 1.2.2 Create Alembic migration file `001_initial_schema.py` with SQL:
  ```sql
  CREATE TABLE analytics_raw (
    id BIGSERIAL PRIMARY KEY,
    ga4_event_id TEXT UNIQUE NOT NULL,
    event_name TEXT NOT NULL,
    user_pseudo_id TEXT NOT NULL,
    event_params JSONB,
    event_timestamp BIGINT,
    created_at TIMESTAMP DEFAULT NOW()
  );
  CREATE INDEX idx_user_pseudo_id ON analytics_raw(user_pseudo_id);
  CREATE INDEX idx_event_timestamp ON analytics_raw(event_timestamp);
  
  CREATE TABLE user_segments (
    id BIGSERIAL PRIMARY KEY,
    user_pseudo_id TEXT UNIQUE NOT NULL,
    segment TEXT NOT NULL,
    confidence FLOAT DEFAULT 0.0,
    reasoning TEXT,
    event_summary JSONB,
    analyzed_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
  );
  CREATE INDEX idx_user_pseudo_id_seg ON user_segments(user_pseudo_id);
  CREATE INDEX idx_segment ON user_segments(segment);
  
  CREATE TABLE personalization_rules (
    id BIGSERIAL PRIMARY KEY,
    segment TEXT UNIQUE NOT NULL,
    priority_sections TEXT[],
    featured_projects TEXT[],
    highlight_skills TEXT[],
    css_overrides JSONB,
    reasoning TEXT,
    created_at TIMESTAMP DEFAULT NOW()
  );
  CREATE INDEX idx_segment_rules ON personalization_rules(segment);
  
  CREATE TABLE llm_insights (
    id BIGSERIAL PRIMARY KEY,
    analysis_period DATERANGE,
    total_visitors INT,
    segment_distribution JSONB,
    top_events JSONB,
    conversion_metrics JSONB,
    insight_summary TEXT,
    recommendations JSONB,
    generated_at TIMESTAMP DEFAULT NOW()
  );
  CREATE INDEX idx_analysis_period ON llm_insights(analysis_period);
  ```
- [ ] 1.2.3 Run migrations: `alembic upgrade head`
- [ ] 1.2.4 Create `backend/app/database/db.py`:
  ```python
  from sqlalchemy import create_engine
  from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
  
  # Supabase connection string
  DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"
  
  engine = create_async_engine(DATABASE_URL, echo=True)
  ```
- [ ] 1.2.5 Create SQLAlchemy ORM models in `backend/app/database/models.py`
- [ ] 1.2.6 Test connection with simple script (verify tables exist)

**Definition of Done:**
- Tables exist in Supabase with correct schema
- SQLAlchemy models match tables
- Connection test script runs without errors

---

#### Task 1.3: FastAPI App Skeleton & Config
**Objective:** Create FastAPI entry point and configuration  
**Effort:** 2 hours

**Sub-tasks:**
- [ ] 1.3.1 Create `backend/app/config.py`:
  ```python
  from pydantic_settings import BaseSettings
  
  class Settings(BaseSettings):
      SUPABASE_URL: str
      SUPABASE_KEY: str
      GA4_PROPERTY_ID: str
      GEMINI_API_KEY: str
      DEEPSEEK_API_KEY: str
      ADMIN_SECRET: str
      ENVIRONMENT: str = "development"
      
      class Config:
          env_file = ".env"
  
  settings = Settings()
  ```
- [ ] 1.3.2 Create `backend/app/main.py`:
  ```python
  from fastapi import FastAPI
  from fastapi.middleware.cors import CORSMiddleware
  
  app = FastAPI(title="Portfolio AI Personalization API")
  
  # CORS for frontend
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["http://localhost:3000", "https://yourdomain.com"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  
  @app.get("/health")
  async def health():
      return {"status": "ok"}
  
  if __name__ == "__main__":
      import uvicorn
      uvicorn.run(app, host="0.0.0.0", port=8000)
  ```
- [ ] 1.3.3 Create `backend/app/__init__.py`
- [ ] 1.3.4 Test: `python -m uvicorn app.main:app --reload` → visit `http://localhost:8000/health`

**Definition of Done:**
- FastAPI app starts without errors
- `/health` endpoint responds with `{"status": "ok"}`
- CORS configured for local dev

---

#### Task 1.4: GA4 Service Integration
**Objective:** Fetch analytics data from GA4  
**Effort:** 4 hours

**Sub-tasks:**
- [ ] 1.4.1 Set up Google Cloud Service Account:
  - Create project in Google Cloud Console
  - Enable Google Analytics Data API
  - Download credentials JSON → save as `backend/credentials.json`
  - Set env var: `GA4_CREDENTIALS_JSON=credentials.json`

- [ ] 1.4.2 Create `backend/app/services/ga4_service.py`:
  ```python
  from google.analytics.data_v1beta import BetaAnalyticsDataClient
  from google.analytics.data_v1beta.types import RunReportRequest
  
  class GA4Service:
      def __init__(self, credentials_path: str, property_id: str):
          self.client = BetaAnalyticsDataClient.from_service_account_file(credentials_path)
          self.property_id = property_id
      
      async def fetch_events(self, hours: int = 1) -> list:
          # Fetch GA4 events from last N hours
          # Return formatted event list
          pass
      
      async def get_segment_distribution(self) -> dict:
          # Get user counts by segment (if tracked)
          pass
  ```

- [ ] 1.4.3 Create GA4 event schema in `backend/app/models/events.py`:
  ```python
  from pydantic import BaseModel
  from datetime import datetime
  from typing import Optional, Dict, Any
  
  class EventPayload(BaseModel):
      event_name: str
      user_pseudo_id: str
      event_params: Optional[Dict[str, Any]] = None
      event_timestamp: int
  
  class EventResponse(BaseModel):
      status: str
  ```

- [ ] 1.4.4 Test script to fetch real GA4 data:
  ```python
  from app.services.ga4_service import GA4Service
  
  service = GA4Service(
      credentials_path="credentials.json",
      property_id=YOUR_GA4_PROPERTY_ID
  )
  events = await service.fetch_events(hours=24)
  print(f"Fetched {len(events)} events")
  ```

**Definition of Done:**
- GA4 Service credentials authenticated
- `fetch_events()` returns real event data from portfolio
- Test script shows event count > 0 (need some visitor traffic)

---

#### Task 1.5: LLM Service with Gemini & DeepSeek
**Objective:** Create LLM abstraction layer  
**Effort:** 4 hours

**Sub-tasks:**
- [ ] 1.5.1 Create `backend/app/services/llm_service.py`:
  ```python
  from abc import ABC, abstractmethod
  from typing import Dict, Any
  
  class LLMProvider(ABC):
      @abstractmethod
      async def generate(self, prompt: str, context: Dict[str, Any]) -> str:
          pass
  
  class GeminiProvider(LLMProvider):
      def __init__(self, api_key: str):
          import google.generativeai as genai
          genai.configure(api_key=api_key)
          self.model = genai.GenerativeModel("gemini-2.0-flash")
      
      async def generate(self, prompt: str, context: Dict[str, Any]) -> str:
          # Call Gemini API
          pass
  
  class DeepSeekProvider(LLMProvider):
      def __init__(self, api_key: str):
          self.api_key = api_key
          self.base_url = "https://api.deepseek.com/v1"
      
      async def generate(self, prompt: str, context: Dict[str, Any]) -> str:
          # Call DeepSeek API via httpx
          pass
  
  class LLMService:
      def __init__(self, gemini_key: str, deepseek_key: str):
          self.providers = [
              GeminiProvider(gemini_key),
              DeepSeekProvider(deepseek_key)
          ]
          self.current_idx = 0
      
      async def generate_with_fallback(self, prompt: str, context: Dict[str, Any]) -> str:
          # Try each provider with fallback logic
          pass
  ```

- [ ] 1.5.2 Create prompt templates in `backend/app/prompts/`:
  - `segment.prompt` - User segmentation prompt
  - `rules.prompt` - Personalization rules prompt

- [ ] 1.5.3 Test with mock data:
  ```python
  service = LLMService(gemini_key="...", deepseek_key="...")
  
  result = await service.generate_with_fallback(
      prompt="Segment this user: ...",
      context={...}
  )
  print(result)
  ```

**Definition of Done:**
- LLM Service initializes without errors
- Test generates response from Gemini (free tier)
- Fallback logic verifiable (mock DeepSeek call)

---

### ✅ WEEK 2: Core Logic & API

#### Task 2.1: Analysis Engine (Segmentation & Rules)
**Objective:** Core business logic for analyzing users and generating rules  
**Effort:** 4 hours

**Sub-tasks:**
- [ ] 2.1.1 Create `backend/app/services/analysis_engine.py`:
  ```python
  from app.services.ga4_service import GA4Service
  from app.services.llm_service import LLMService
  from app.database.db import get_db
  from app.database.models import UserSegment, PersonalizationRules
  
  class AnalysisEngine:
      def __init__(self, ga4_svc: GA4Service, llm_svc: LLMService, db_session):
          self.ga4 = ga4_svc
          self.llm = llm_svc
          self.db = db_session
      
      async def segment_user(self, user_pseudo_id: str) -> UserSegment:
          # 1. Fetch user's events
          # 2. Aggregate metrics
          # 3. Call LLM to classify
          # 4. Save to DB with TTL
          pass
      
      async def generate_rules_for_segment(self, segment: str) -> PersonalizationRules:
          # 1. Aggregate sample events for segment
          # 2. Call LLM to generate rules
          # 3. Save to DB
          pass
      
      async def run_hourly_analysis(self):
          # Called by scheduler:
          # 1. Fetch last 1h of GA4 events
          # 2. Group by user
          # 3. Segment each user
          # 4. Update rules per segment
          pass
  ```

- [ ] 2.1.2 Create test data generator for testing without real GA4 data:
  ```python
  def mock_user_events() -> Dict[str, Any]:
      return {
          "user_pseudo_id": "user_123",
          "projects_clicked": ["project_ai", "project_fullstack"],
          "skills_hovered": ["python", "react", "llm"],
          "sections_viewed": ["projects", "skills"],
          "time_spent": 300,  # seconds
          "contact_intent": True
      }
  ```

- [ ] 2.1.3 Test segmentation with mock data

**Definition of Done:**
- `segment_user()` returns `UserSegment` object
- `generate_rules_for_segment()` returns `PersonalizationRules` object
- Data saved to Supabase correctly

---

#### Task 2.2: Pydantic Models (Schemas)
**Objective:** Define all API request/response schemas  
**Effort:** 2 hours

**Sub-tasks:**
- [ ] 2.2.1 Update `backend/app/models/segments.py`:
  ```python
  from pydantic import BaseModel
  from typing import Optional, Dict, Any
  from datetime import datetime
  
  class UserSegmentResponse(BaseModel):
      user_pseudo_id: str
      segment: str
      confidence: float
      reasoning: str
      
      class Config:
          from_attributes = True
  ```

- [ ] 2.2.2 Create `backend/app/models/rules.py`:
  ```python
  from pydantic import BaseModel
  from typing import List, Optional, Dict, Any
  
  class PersonalizationRulesResponse(BaseModel):
      segment: str
      priority_sections: List[str]
      featured_projects: List[str]
      highlight_skills: List[str]
      reasoning: str
      
      class Config:
          from_attributes = True
  
  class PersonalizationRequest(BaseModel):
      user_id: str  # GA4 client ID
  ```

- [ ] 2.2.3 Create `backend/app/models/insights.py` (for Phase 2, skip for now)

**Definition of Done:**
- All Pydantic models defined
- Models match database schema
- FastAPI can serialize/deserialize without errors

---

#### Task 2.3: REST API - Public Endpoints
**Objective:** Create `/api/personalization` and `/api/events` endpoints  
**Effort:** 3 hours

**Sub-tasks:**
- [ ] 2.3.1 Create `backend/app/api/public.py`:
  ```python
  from fastapi import APIRouter, Query, HTTPException
  from app.models.rules import PersonalizationRequest, PersonalizationRulesResponse
  from app.models.events import EventPayload, EventResponse
  from app.services.ga4_service import GA4Service
  from app.database.db import get_db
  
  router = APIRouter(prefix="/api", tags=["public"])
  
  @router.post("/events", response_model=EventResponse)
  async def track_event(event: EventPayload):
      """Fallback event tracking endpoint"""
      # Validate and save event to analytics_raw
      pass
  
  @router.get("/personalization", response_model=PersonalizationRulesResponse)
  async def get_personalization(user_id: str = Query(...)):
      """Get personalization rules for user's segment"""
      # 1. Look up user_segments table
      # 2. Get rules for segment from personalization_rules
      # 3. Return rules
      pass
  ```

- [ ] 2.3.2 Register router in `backend/app/main.py`:
  ```python
  from app.api import public
  
  app.include_router(public.router)
  ```

- [ ] 2.3.3 Test endpoints:
  ```bash
  # GET personalization
  curl "http://localhost:8000/api/personalization?user_id=user_123"
  
  # POST event
  curl -X POST "http://localhost:8000/api/events" \
    -H "Content-Type: application/json" \
    -d '{"event_name": "project_click", "user_pseudo_id": "user_123", ...}'
  ```

**Definition of Done:**
- Both endpoints callable without errors
- `/api/personalization` returns rules (from DB or mock data)
- `/api/events` accepts and stores events

---

#### Task 2.4: Scheduler - Hourly Analysis Job
**Objective:** Set up APScheduler for hourly data processing  
**Effort:** 3 hours

**Sub-tasks:**
- [ ] 2.4.1 Create `backend/app/services/scheduler.py`:
  ```python
  from apscheduler.schedulers.asyncio import AsyncIOScheduler
  from app.services.ga4_service import GA4Service
  from app.services.llm_service import LLMService
  from app.services.analysis_engine import AnalysisEngine
  from app.database.db import get_db
  
  scheduler = AsyncIOScheduler()
  
  async def hourly_analysis_job():
      """Runs every hour"""
      try:
          # 1. Initialize services
          # 2. Run analysis_engine.run_hourly_analysis()
          # 3. Log results
          pass
      except Exception as e:
          logger.error(f"Analysis job failed: {e}")
  
  def start_scheduler():
      scheduler.add_job(hourly_analysis_job, 'interval', hours=1)
      scheduler.start()
  ```

- [ ] 2.4.2 Integrate scheduler into `backend/app/main.py`:
  ```python
  from app.services.scheduler import start_scheduler
  
  @app.on_event("startup")
  async def startup_event():
      start_scheduler()
  ```

- [ ] 2.4.3 Create manual trigger endpoint for testing (remove in production):
  ```python
  @app.post("/api/admin/trigger-analysis")
  async def trigger_analysis():
      """Manually trigger analysis job (dev only)"""
      await hourly_analysis_job()
      return {"status": "analysis triggered"}
  ```

**Definition of Done:**
- Scheduler starts without errors on app startup
- Manual trigger endpoint works (hit it to test analysis)
- Job logs appear in stdout

---

#### Task 2.5: Frontend Integration - Personalization Script
**Objective:** Create JS script to apply personalization rules to DOM  
**Effort:** 3 hours

**Sub-tasks:**
- [ ] 2.5.1 Create `assets/js/personalization.js`:
  ```javascript
  class PersonalizationManager {
      constructor(apiUrl = '/api') {
          this.apiUrl = apiUrl;
      }
      
      async init() {
          try {
              // 1. Get GA4 client ID
              const userId = await this.getGA4ClientId();
              
              // 2. Fetch rules
              const response = await fetch(
                  `${this.apiUrl}/personalization?user_id=${userId}`
              );
              const { rules, segment } = await response.json();
              
              // 3. Apply rules
              this.applyRules(rules);
              this.trackPersonalization(segment);
          } catch (error) {
              console.warn('Personalization failed, showing default', error);
          }
      }
      
      getGA4ClientId() {
          return new Promise((resolve) => {
              gtag('event', 'page_view', {
                  'send_page_view': false,
                  'callback': function() {
                      gtag('get', 'client_id', function(clientId) {
                          resolve(clientId);
                      });
                  }
              });
          });
      }
      
      applyRules(rules) {
          // Reorder sections based on priority_sections
          // Highlight featured projects
          // Emphasize skills
          // See detailed implementation in Task 3.2
      }
      
      trackPersonalization(segment) {
          gtag('event', 'personalization_applied', {
              'segment': segment
          });
      }
  }
  
  // Initialize on page load
  document.addEventListener('DOMContentLoaded', () => {
      const pm = new PersonalizationManager();
      pm.init();
  });
  ```

- [ ] 2.5.2 Add script tag to `index.html`:
  ```html
  <script src="assets/js/personalization.js"></script>
  ```

- [ ] 2.5.3 Test in browser:
  - Open DevTools Network tab
  - Verify `/api/personalization` call succeeds
  - Check console for errors

**Definition of Done:**
- Script loads without errors
- `/api/personalization` request visible in Network tab
- Response contains valid rules object

---

#### Task 2.6: Custom Event Tracking - Analytics Script
**Objective:** Create GA4 event tracker utility  
**Effort:** 2 hours

**Sub-tasks:**
- [ ] 2.6.1 Create `assets/js/analytics.js`:
  ```javascript
  const AnalyticsTracker = {
      // Utility to send custom events to GA4
      
      trackProjectClick(projectId, category) {
          gtag('event', 'project_click', {
              'project_id': projectId,
              'category': category,
              'timestamp': Date.now()
          });
      },
      
      trackSectionView(sectionName, duration) {
          gtag('event', 'section_view', {
              'section_name': sectionName,
              'time_spent': duration,
              'timestamp': Date.now()
          });
      },
      
      trackContactIntent(contactType) {
          gtag('event', 'contact_intent', {
              'contact_type': contactType,
              'timestamp': Date.now()
          });
      },
      
      // ... more event methods ...
  };
  
  // Usage:
  // AnalyticsTracker.trackProjectClick('project_ai', 'ai');
  ```

- [ ] 2.6.2 Add script to `index.html` before personalization.js:
  ```html
  <script src="assets/js/analytics.js"></script>
  <script src="assets/js/personalization.js"></script>
  ```

- [ ] 2.6.3 Add event listeners to existing HTML elements:
  ```javascript
  // In index.html or via JavaScript:
  document.querySelectorAll('.project-card').forEach(card => {
      card.addEventListener('click', (e) => {
          const projectId = card.dataset.projectId;
          const category = card.dataset.category;
          AnalyticsTracker.trackProjectClick(projectId, category);
      });
  });
  ```

**Definition of Done:**
- Analytics.js loads without errors
- Event methods callable (test in console)
- Events appear in GA4 real-time report

---

#### Task 2.7: Documentation & Testing
**Objective:** Document setup and test Phase 1  
**Effort:** 3 hours

**Sub-tasks:**
- [ ] 2.7.1 Create `docs/SETUP.md`:
  - Python version requirements
  - Supabase setup steps
  - GA4 setup steps
  - Environment variables
  - Running locally: `python -m uvicorn app.main:app --reload`

- [ ] 2.7.2 Create `docs/API.md`:
  - Endpoint documentation
  - Request/response examples
  - Error codes

- [ ] 2.7.3 Create unit tests in `backend/tests/`:
  - `test_ga4_service.py` - Mock GA4 calls
  - `test_llm_service.py` - Mock LLM calls
  - `test_analysis_engine.py` - Mock analysis
  - `test_api.py` - API endpoint tests

- [ ] 2.7.4 Run tests:
  ```bash
  pytest backend/tests/ -v
  ```

- [ ] 2.7.5 Manual testing checklist:
  - [ ] Start backend: `python -m uvicorn app.main:app --reload`
  - [ ] Health check: `curl http://localhost:8000/health`
  - [ ] Get personalization: `curl http://localhost:8000/api/personalization?user_id=test_user`
  - [ ] Post event: `curl -X POST http://localhost:8000/api/events -H "Content-Type: application/json" -d '...'`
  - [ ] Check Supabase: Verify data in tables
  - [ ] Open portfolio: Check console for errors
  - [ ] Trigger analysis: `curl -X POST http://localhost:8000/api/admin/trigger-analysis`
  - [ ] Check scheduler logs

**Definition of Done:**
- All manual tests pass
- Unit tests run successfully
- Documentation complete and accurate
- No console errors on portfolio

---

## Success Metrics - Phase 1

✅ **Completion Criteria:**

1. **Backend:**
   - [ ] FastAPI app runs without errors
   - [ ] Supabase schema created and connected
   - [ ] GA4 Service fetches real data
   - [ ] LLM Service (Gemini) generates responses
   - [ ] Scheduler runs hourly analysis job
   - [ ] All API endpoints respond correctly

2. **Frontend:**
   - [ ] Personalization script loads
   - [ ] Custom events tracked to GA4
   - [ ] No console errors

3. **Data Pipeline:**
   - [ ] Raw GA4 events saved to `analytics_raw` table
   - [ ] User segments computed and saved to `user_segments`
   - [ ] Personalization rules generated and saved
   - [ ] Rules fetched via API

4. **Documentation:**
   - [ ] Setup instructions complete
   - [ ] API documentation complete
   - [ ] Tests passing

**Target:** Complete by end of Week 2

---

## Notes & Warnings

### ⚠️ Important Considerations

1. **GA4 Credentials:** Keep `credentials.json` in `.gitignore`, add to `.env`
2. **LLM Costs:** Gemini free tier is generous, monitor DeepSeek quota
3. **Testing Data:** If portfolio has low traffic, use mock data for initial testing
4. **Deployment:** Phase 1 is local/dev only; Phase 3 covers production

### 🔄 Transition to Phase 2

Once Phase 1 is complete:
- Add more custom events (currently just basic placeholders)
- Implement admin dashboard UI
- Add DeepSeek as primary provider
- Add xAI explanations to insights
- Handle edge cases (rate limits, timeouts)

---

## File Checklist (Start of Implementation)

Create these files/directories:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    (Task 1.3)
│   ├── config.py                  (Task 1.3)
│   ├── dependencies.py            (Task 1.3)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── events.py              (Task 1.4)
│   │   ├── segments.py            (Task 2.2)
│   │   └── rules.py               (Task 2.2)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ga4_service.py         (Task 1.4)
│   │   ├── llm_service.py         (Task 1.5)
│   │   ├── analysis_engine.py     (Task 2.1)
│   │   └── scheduler.py           (Task 2.4)
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db.py                  (Task 1.2)
│   │   ├── models.py              (Task 1.2)
│   │   └── migrations/
│   │       ├── env.py
│   │       └── versions/
│   │           └── 001_initial_schema.py  (Task 1.2)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── public.py              (Task 2.3)
│   │   ├── admin.py               (Phase 2)
│   │   └── health.py              (Task 1.3)
│   ├── auth/
│   │   ├── __init__.py
│   │   └── jwt.py                 (Phase 2)
│   ├── prompts/
│   │   ├── segment.prompt         (Task 1.5)
│   │   └── rules.prompt           (Task 1.5)
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       └── exceptions.py
├── tests/
│   ├── __init__.py
│   ├── test_ga4_service.py        (Task 2.7)
│   ├── test_llm_service.py        (Task 2.7)
│   ├── test_analysis_engine.py    (Task 2.7)
│   └── test_api.py                (Task 2.7)
├── requirements.txt               (Task 1.1)
├── .env.example                   (Task 1.1)
├── Dockerfile                     (Task 1.1)
└── docker-compose.yml             (Task 1.1)

assets/js/
├── personalization.js             (Task 2.5)
├── analytics.js                   (Task 2.6)
└── (existing files)

docs/
├── SETUP.md                       (Task 2.7)
├── API.md                         (Task 2.7)
└── plans/
    └── 2025-01-18-implementation-plan.md  (THIS FILE)
```

---

**Plan created:** January 18, 2026  
**Ready to execute:** ✅ Yes
