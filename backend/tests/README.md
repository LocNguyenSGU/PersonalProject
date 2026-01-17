# Testing Guide

## Overview

This project includes comprehensive testing:
- **Unit tests**: Individual service and component tests
- **Integration tests**: Database and API tests
- **E2E tests**: Full pipeline tests from GA4 to frontend

## Running Tests

### All Tests
```bash
cd backend
pytest tests/ -v
```

### Specific Test Files
```bash
# E2E integration tests
pytest tests/test_e2e_integration.py -v

# LLM service tests
pytest tests/test_llm_service.py -v

# GA4 service tests
pytest tests/test_ga4_service.py -v

# Analysis engine tests
pytest tests/test_analysis_engine.py -v

# API endpoint tests
pytest tests/test_api.py -v
```

### With Coverage
```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### Watch Mode (Auto-rerun on changes)
```bash
pytest-watch tests/
```

## Test Structure

```
backend/tests/
├── conftest.py                    # Pytest fixtures and configuration
├── test_e2e_integration.py        # End-to-end pipeline tests
├── test_llm_service.py            # LLM provider tests
├── test_ga4_service.py            # GA4 API tests
├── test_analysis_engine.py        # Segmentation and rules tests
└── test_api.py                    # API endpoint tests
```

## E2E Test Scenarios

### 1. Full Event Pipeline
- Event ingestion → Storage → Verification
- Tests: `test_full_event_pipeline`

### 2. User Segmentation Flow
- Events → LLM → UserSegment with xAI explanations
- Tests: `test_user_segmentation_flow`

### 3. Rules Generation Flow
- Segment → LLM → PersonalizationRules with xAI
- Tests: `test_rules_generation_flow`

### 4. API Personalization
- GET /api/personalization → Returns rules
- Tests: `test_api_personalization_endpoint`

### 5. Hourly Analysis Job
- Full scheduled job execution
- Tests: `test_hourly_analysis_job`

### 6. Admin Dashboard Data
- Admin endpoints return correct aggregated data
- Tests: `test_admin_dashboard_data_flow`

### 7. xAI Explanation Persistence
- xAI explanations saved and retrieved correctly
- Tests: `test_xai_explanation_persistence`

## Test Database

Tests use an in-memory SQLite database for speed:
- Fresh database for each test function
- No cleanup needed
- Fast execution

## Mocking Strategy

### LLM Service Mock
- Returns predictable responses
- Avoids API calls and costs
- Consistent test results

```python
@pytest.fixture
def mock_llm_service():
    class MockLLMService:
        async def segment_user(self, events):
            return {
                "segment": "ML_ENGINEER",
                "confidence": 0.85,
                ...
            }
    return MockLLMService()
```

### GA4 Service Mock (for unit tests)
- Simulates GA4 API responses
- No real API calls
- Controlled test data

## Admin Authentication Tests

Tests include JWT authentication flow:

```python
@pytest.fixture
async def admin_token(async_client):
    response = await async_client.post(
        "/api/admin/login",
        json={"username": "admin", "password": "changeme"}
    )
    return response.json()["access_token"]
```

## Common Issues

### Import Errors
If you see import errors, ensure you're in the backend directory:
```bash
cd backend
export PYTHONPATH=$PWD
pytest tests/ -v
```

### Database Errors
E2E tests use in-memory database. If you see database errors:
```bash
# Install aiosqlite
pip install aiosqlite
```

### Async Errors
Ensure pytest-asyncio is installed:
```bash
pip install pytest-asyncio
```

## CI/CD Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    cd backend
    pytest tests/ -v --cov=app
```

## Manual Testing Checklist

After running automated tests, verify manually:

### Backend
- [ ] Start server: `python -m uvicorn app.main:app --reload`
- [ ] Health check: `curl http://localhost:8000/health`
- [ ] API docs: `open http://localhost:8000/docs`

### Admin Dashboard
- [ ] Open `admin/index.html`
- [ ] Login with admin credentials
- [ ] Verify charts render
- [ ] Check xAI insights display

### Frontend
- [ ] Open portfolio in browser
- [ ] Check browser console for errors
- [ ] Verify events tracked to GA4
- [ ] Test personalization loading

## Test Coverage Goals

Target coverage: **80%+**

Key areas:
- ✅ Core services (LLM, GA4, Analysis)
- ✅ API endpoints (public + admin)
- ✅ Database models and queries
- ✅ Authentication and authorization
- ✅ xAI explanation generation

## Adding New Tests

### 1. Create test file
```python
# tests/test_new_feature.py
import pytest

@pytest.mark.asyncio
async def test_new_feature(async_session):
    # Test implementation
    pass
```

### 2. Use fixtures from conftest.py
- `async_session`: Database session
- `async_client`: HTTP client
- `admin_token`: JWT token
- `mock_llm_service`: Mocked LLM

### 3. Run new tests
```bash
pytest tests/test_new_feature.py -v
```

## Debugging Tests

### Verbose output
```bash
pytest tests/ -vv
```

### Show print statements
```bash
pytest tests/ -s
```

### Stop on first failure
```bash
pytest tests/ -x
```

### Run specific test
```bash
pytest tests/test_e2e_integration.py::test_full_event_pipeline -v
```

### Debug with pdb
```bash
pytest tests/ --pdb
```

## Performance

E2E test suite runs in ~5-10 seconds:
- In-memory database
- Mocked external APIs
- Parallel execution possible

```bash
# Run tests in parallel (requires pytest-xdist)
pytest tests/ -n auto
```
