# AI-Powered Portfolio Personalization - Setup Guide

## Prerequisites

- Python 3.11+
- Supabase account (free tier OK)
- Google Cloud account for GA4 (optional for MVP)
- API keys: Gemini, DeepSeek (free credits available)

## Environment Setup

### 1. Clone/Setup Repository

```bash
cd portfolio/.worktrees/feature/ai-personalization
```

### 2. Create Python Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Configure Environment Variables

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your actual credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
GA4_PROPERTY_ID=your-ga4-property-id
GA4_CREDENTIALS_JSON=./backend/credentials.json
GEMINI_API_KEY=your-gemini-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
ADMIN_SECRET=your-super-secret-key
ENVIRONMENT=development
```

### 5. Setup Supabase Database

Visit https://supabase.com and:
1. Create new project
2. Copy project URL and anon key to .env
3. Run database migrations (see below)

### 6. Migrate Database

```bash
cd backend
alembic upgrade head
```

Or manually create tables via Supabase SQL Editor using the schema from `app/database/models.py`

## Running the Backend

### Development Mode

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Server runs at `http://localhost:8000`

Health check: `curl http://localhost:8000/health`

### Docker

```bash
docker-compose up
```

## Testing

### Run Tests

```bash
cd backend
pytest tests/ -v
```

### Manual API Testing

```bash
# Health check
curl http://localhost:8000/health

# Get personalization
curl "http://localhost:8000/api/personalization?user_id=test_user_123"

# Post event
curl -X POST http://localhost:8000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "event_name": "project_click",
    "user_pseudo_id": "test_user_123",
    "event_params": {"project_id": "proj1"},
    "event_timestamp": 1234567890
  }'
```

## Frontend Integration

### 1. Add Scripts to index.html

```html
<!-- Before closing </body> -->
<script src="assets/js/analytics.js"></script>
<script src="assets/js/personalization.js"></script>
```

### 2. Add Data Attributes to HTML Elements

For projects:
```html
<div class="project-card" data-project-id="project_ai" data-category="ai">
  ...
</div>
```

For contact buttons:
```html
<a href="..." data-contact-type="email">Email</a>
```

For skills:
```html
<span class="skill" data-skill="python">Python</span>
```

### 3. Test Frontend

Open portfolio in browser, check:
- Console for personalization logs
- Network tab for API calls to `/api/personalization`
- GA4 real-time report for events

## Troubleshooting

### Database Connection Error

```
Error: postgresql+asyncpg connection failed
```

Solution: Verify SUPABASE_URL is correct and includes database credentials

### LLM API Errors

Check that API keys are valid in .env file. Gemini free tier is generous.

### Scheduler Not Running

Check logs for errors during startup. Scheduler logs "Scheduler started" on success.

## Next Steps

1. Configure GA4 property with custom events
2. Add more event tracking to index.html
3. Implement admin dashboard (Phase 2)
4. Deploy to production (Phase 3)

## Support

- Gemini API: https://makersuite.google.com/app/apikey
- DeepSeek API: https://platform.deepseek.com
- Supabase Docs: https://supabase.com/docs
