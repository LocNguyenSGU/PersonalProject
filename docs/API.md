# API Documentation

## Public Endpoints

### Health Check

**GET** `/health`

Check if service is running.

**Response:**
```json
{
  "status": "ok",
  "service": "portfolio-ai-personalization"
}
```

### Get Personalization Rules

**GET** `/api/personalization?user_id={user_id}`

Get personalization rules for a user based on their segment.

**Query Parameters:**
- `user_id` (required): GA4 client ID or user identifier

**Response:**
```json
{
  "segment": "ML_ENGINEER",
  "priority_sections": ["projects", "skills", "experience"],
  "featured_projects": ["project_ai", "project_nlp"],
  "highlight_skills": ["python", "transformers", "llm"],
  "reasoning": "User heavily clicked AI/ML projects"
}
```

**Segments:**
- `ML_ENGINEER`: Heavy AI/ML project focus
- `FULLSTACK_DEV`: Balanced frontend/backend interest
- `RECRUITER`: Quick scan, contact-focused
- `STUDENT`: Exploratory, long session time
- `CASUAL`: Brief visit, no clear pattern

### Track Custom Event

**POST** `/api/events`

Send custom event for tracking (fallback to GA4 SDK).

**Body:**
```json
{
  "event_name": "project_click",
  "user_pseudo_id": "GA4_CLIENT_ID",
  "event_params": {
    "project_id": "proj1",
    "category": "ai"
  },
  "event_timestamp": 1705600000
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Event tracked"
}
```

**Supported Event Names:**
- `project_click`
- `skill_hover`
- `section_view`
- `contact_intent`
- `language_switch`
- `deep_read`
- `repeat_view`
- `scroll_depth`
- `career_timeline_interact`
- `download_resume`
- `external_link_click`

## Admin Endpoints

(Will be implemented in Phase 2)

### Dashboard

**GET** `/api/admin/dashboard`

Get analytics dashboard data (protected).

### Segments Breakdown

**GET** `/api/admin/segments`

Get detailed per-segment statistics (protected).

### Raw Events

**GET** `/api/admin/events?hours=24`

Get raw event stream (protected).

### Manual Trigger

**POST** `/api/admin/trigger-analysis`

Manually trigger hourly analysis job (dev only).

## Error Responses

### 404 Not Found
```json
{
  "detail": "Not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["query", "user_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to get personalization"
}
```

## Example Usage

### JavaScript

```javascript
// Get personalization for current user
const userId = "GA4_CLIENT_ID";
const response = await fetch(`/api/personalization?user_id=${userId}`);
const { segment, priority_sections, featured_projects } = await response.json();

// Apply rules
applyPersonalization({ segment, priority_sections, featured_projects });

// Track event
await fetch('/api/events', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    event_name: 'project_click',
    user_pseudo_id: userId,
    event_params: { project_id: 'proj1' },
    event_timestamp: Date.now()
  })
});
```

### cURL

```bash
# Get personalization
curl "http://localhost:8000/api/personalization?user_id=user_123"

# Track event
curl -X POST http://localhost:8000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "event_name": "project_click",
    "user_pseudo_id": "user_123",
    "event_params": {"project_id": "proj1"},
    "event_timestamp": 1705600000
  }'
```

## Rate Limiting

Currently no rate limits. Will be added in Phase 3 for production.

## Authentication

Public endpoints: No authentication required.

Admin endpoints: JWT token required (coming Phase 2).

## CORS

Allowed origins (configurable in `.env`):
- http://localhost:3000
- http://localhost:8080
- http://localhost:5500
- https://yourdomain.com
