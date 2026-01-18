"""
End-to-End Integration Tests
Tests full pipeline: GA4 → LLM → Analysis → API → Frontend
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select

from app.database.models import AnalyticsRaw, UserSegment, PersonalizationRules
from app.services.ga4_service import GA4Service
from app.services.llm_service import LLMService
from app.services.analysis_engine import AnalysisEngine
from app.config import settings


@pytest.mark.asyncio
async def test_full_event_pipeline(async_session, test_event_data):
    """
    Test: Event ingestion → Storage → Analysis
    Verifies events are properly saved to analytics_raw table
    """
    # Create test event
    event = AnalyticsRaw(
        ga4_event_id="test_event_123",
        event_name="project_click",
        user_pseudo_id="test_user_001",
        event_params={"project_id": "ai_chatbot", "category": "ml"},
        event_timestamp=int(datetime.utcnow().timestamp()),
        created_at=datetime.utcnow(),
    )

    async_session.add(event)
    await async_session.commit()

    # Verify event saved
    stmt = select(AnalyticsRaw).where(AnalyticsRaw.ga4_event_id == "test_event_123")
    result = await async_session.execute(stmt)
    saved_event = result.scalar_one_or_none()

    assert saved_event is not None
    assert saved_event.event_name == "project_click"
    assert saved_event.user_pseudo_id == "test_user_001"
    assert saved_event.event_params["project_id"] == "ai_chatbot"


@pytest.mark.asyncio
async def test_user_segmentation_flow(async_session, mock_llm_service):
    """
    Test: Events → LLM Segmentation → UserSegment saved
    Verifies full segmentation pipeline
    """
    # Create sample events for a user
    user_id = "test_user_segmentation"
    events = [
        AnalyticsRaw(
            ga4_event_id=f"seg_event_{i}",
            event_name=event_name,
            user_pseudo_id=user_id,
            event_params={},
            event_timestamp=int(datetime.utcnow().timestamp()),
        )
        for i, event_name in enumerate(
            [
                "project_click",
                "project_click",
                "skill_hover",
                "deep_read",
                "section_view",
            ]
        )
    ]

    for event in events:
        async_session.add(event)
    await async_session.commit()

    # Run segmentation
    from app.services.ga4_service import GA4Service

    ga4_svc = GA4Service(settings.GA4_CREDENTIALS_JSON, settings.GA4_PROPERTY_ID)

    engine = AnalysisEngine(ga4_svc, mock_llm_service, async_session)
    segment = await engine.segment_user(user_id)

    # Verify segment created
    assert segment is not None
    assert segment.user_pseudo_id == user_id
    assert segment.segment in [
        "ML_ENGINEER",
        "FULLSTACK_DEV",
        "RECRUITER",
        "STUDENT",
        "CASUAL",
    ]
    assert segment.confidence > 0
    assert segment.reasoning is not None
    assert segment.xai_explanation is not None

    # Verify xAI explanation structure
    xai = segment.xai_explanation
    assert "what" in xai
    assert "why" in xai
    assert "so_what" in xai
    assert "recommendation" in xai


@pytest.mark.asyncio
async def test_rules_generation_flow(async_session, mock_llm_service):
    """
    Test: Segment → LLM Rules Generation → PersonalizationRules saved
    """
    # Create user segment
    segment = UserSegment(
        user_pseudo_id="test_user_rules",
        segment="ML_ENGINEER",
        confidence=0.85,
        reasoning="Heavy ML engagement",
        xai_explanation={
            "what": "test",
            "why": "test",
            "so_what": "test",
            "recommendation": "test",
        },
        event_summary={},
        expires_at=datetime.utcnow() + timedelta(hours=24),
    )
    async_session.add(segment)
    await async_session.commit()

    # Generate rules
    from app.services.ga4_service import GA4Service

    ga4_svc = GA4Service(settings.GA4_CREDENTIALS_JSON, settings.GA4_PROPERTY_ID)

    engine = AnalysisEngine(ga4_svc, mock_llm_service, async_session)
    rules = await engine.generate_rules_for_segment("ML_ENGINEER")

    # Verify rules created
    assert rules is not None
    assert rules.segment == "ML_ENGINEER"
    assert isinstance(rules.priority_sections, list)
    assert isinstance(rules.featured_projects, list)
    assert isinstance(rules.highlight_skills, list)
    assert rules.reasoning is not None
    assert rules.xai_explanation is not None


@pytest.mark.asyncio
async def test_api_personalization_endpoint(async_client, async_session):
    """
    Test: GET /api/personalization → Returns rules for user
    Tests public API endpoint with full database state
    """
    # Setup: Create segment and rules
    user_id = "api_test_user"

    segment = UserSegment(
        user_pseudo_id=user_id,
        segment="FULLSTACK_DEV",
        confidence=0.9,
        reasoning="Balanced engagement",
        xai_explanation={},
        event_summary={},
        expires_at=datetime.utcnow() + timedelta(hours=24),
    )
    async_session.add(segment)

    rules = PersonalizationRules(
        segment="FULLSTACK_DEV",
        priority_sections=["projects", "skills"],
        featured_projects=["fullstack_app"],
        highlight_skills=["react", "python", "docker"],
        reasoning="Balanced tech stack",
        xai_explanation={},
    )
    async_session.add(rules)
    await async_session.commit()

    # Test API
    response = await async_client.get(f"/api/personalization?user_id={user_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["segment"] == "FULLSTACK_DEV"
    assert "priority_sections" in data["rules"]
    assert "featured_projects" in data["rules"]
    assert data["rules"]["priority_sections"] == ["projects", "skills"]


@pytest.mark.asyncio
async def test_hourly_analysis_job(async_session, mock_llm_service):
    """
    Test: Full hourly job → Segments users → Generates rules
    Simulates the scheduled analysis job
    """
    # Create events for multiple users
    users = ["hourly_user_1", "hourly_user_2"]
    for user_id in users:
        for i in range(5):
            event = AnalyticsRaw(
                ga4_event_id=f"hourly_{user_id}_{i}",
                event_name="project_click",
                user_pseudo_id=user_id,
                event_params={},
                event_timestamp=int(datetime.utcnow().timestamp()),
                created_at=datetime.utcnow(),
            )
            async_session.add(event)
    await async_session.commit()

    # Run hourly analysis
    from app.services.ga4_service import GA4Service

    ga4_svc = GA4Service(settings.GA4_CREDENTIALS_JSON, settings.GA4_PROPERTY_ID)

    engine = AnalysisEngine(ga4_svc, mock_llm_service, async_session)
    await engine.run_hourly_analysis()

    # Verify segments created
    stmt = select(UserSegment).where(UserSegment.user_pseudo_id.in_(users))
    result = await async_session.execute(stmt)
    segments = result.scalars().all()

    assert len(segments) == 2
    for segment in segments:
        assert segment.user_pseudo_id in users
        assert segment.segment is not None


@pytest.mark.asyncio
async def test_admin_dashboard_data_flow(async_client, admin_token, async_session):
    """
    Test: Admin dashboard endpoints return correct aggregated data
    """
    # Setup test data
    # Create segments
    segments_data = [
        ("dash_user_1", "ML_ENGINEER"),
        ("dash_user_2", "ML_ENGINEER"),
        ("dash_user_3", "FULLSTACK_DEV"),
    ]

    for user_id, segment_name in segments_data:
        segment = UserSegment(
            user_pseudo_id=user_id,
            segment=segment_name,
            confidence=0.8,
            reasoning="Test",
            xai_explanation={
                "what": "test",
                "why": "test",
                "so_what": "test",
                "recommendation": "test",
            },
            event_summary={},
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        async_session.add(segment)
    await async_session.commit()

    # Test segments endpoint
    response = await async_client.get(
        "/api/admin/segments", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_users"] == 3
    assert data["distribution"]["ML_ENGINEER"] == 2
    assert data["distribution"]["FULLSTACK_DEV"] == 1


@pytest.mark.asyncio
async def test_xai_explanation_persistence(async_session, mock_llm_service):
    """
    Test: xAI explanations are properly saved and retrieved
    """
    user_id = "xai_test_user"

    # Create segment with xAI explanation
    segment = UserSegment(
        user_pseudo_id=user_id,
        segment="RECRUITER",
        confidence=0.75,
        reasoning="Quick scan, contact-focused",
        xai_explanation={
            "what": "User viewed 3 projects quickly, clicked contact",
            "why": "Fast navigation indicates evaluation mode",
            "so_what": "Likely recruiter or hiring manager",
            "recommendation": "Emphasize achievements and contact info",
        },
        event_summary={},
        expires_at=datetime.utcnow() + timedelta(hours=24),
    )
    async_session.add(segment)
    await async_session.commit()

    # Retrieve and verify
    stmt = select(UserSegment).where(UserSegment.user_pseudo_id == user_id)
    result = await async_session.execute(stmt)
    saved_segment = result.scalar_one()

    assert saved_segment.xai_explanation is not None
    xai = saved_segment.xai_explanation
    assert xai["what"] == "User viewed 3 projects quickly, clicked contact"
    assert xai["why"] == "Fast navigation indicates evaluation mode"
    assert xai["so_what"] == "Likely recruiter or hiring manager"
    assert xai["recommendation"] == "Emphasize achievements and contact info"


# Fixtures
@pytest.fixture
def test_event_data():
    """Sample event data for tests"""
    return {
        "event_name": "project_click",
        "user_pseudo_id": "test_user",
        "event_params": {"project_id": "chatbot", "category": "ai"},
        "event_timestamp": int(datetime.utcnow().timestamp()),
    }


@pytest.fixture
def mock_llm_service():
    """Mock LLM service that returns predictable responses"""

    class MockLLMService:
        async def segment_user(self, events):
            return {
                "segment": "ML_ENGINEER",
                "confidence": 0.85,
                "reasoning": "Heavy ML engagement detected",
                "xai_explanation": {
                    "what": "User clicked AI projects, hovered on ML skills",
                    "why": "Technical depth indicates ML expertise",
                    "so_what": "Potential technical hire or peer",
                    "recommendation": "Prioritize ML projects and technical details",
                },
            }

        async def generate_rules(self, events, segment):
            return {
                "priority_sections": ["projects", "skills"],
                "featured_projects": ["ai_chatbot", "ml_pipeline"],
                "highlight_skills": ["python", "tensorflow", "pytorch"],
                "reasoning": "ML-focused personalization",
                "xai_explanation": {
                    "what": "Prioritizing AI projects and ML skills",
                    "why": "ML_ENGINEER segment values technical depth",
                    "so_what": "Increases engagement with relevant content",
                    "recommendation": "Add ML blog section",
                },
            }

    return MockLLMService()


@pytest.fixture
async def admin_token(async_client):
    """Get admin JWT token for authenticated tests"""
    response = await async_client.post(
        "/api/admin/login", json={"username": "admin", "password": "changeme"}
    )
    return response.json()["access_token"]
