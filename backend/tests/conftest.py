"""
Pytest Configuration and Fixtures
Provides test database, HTTP client, and common fixtures
"""

import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.database.models import Base
from app.database.db import get_db

# Test database URL (use in-memory SQLite for speed)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def async_engine():
    """Create async engine for tests"""
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool, echo=False)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async session for tests"""
    async_session_maker = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session


@pytest.fixture(scope="function")
async def async_client(async_session) -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing API endpoints"""

    # Override database dependency
    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_events():
    """Sample event data for testing"""
    return [
        {
            "event_name": "project_click",
            "user_pseudo_id": "user_001",
            "event_params": {"project_id": "chatbot", "category": "ai"},
        },
        {
            "event_name": "skill_hover",
            "user_pseudo_id": "user_001",
            "event_params": {"skill_name": "python", "duration": 2500},
        },
        {
            "event_name": "section_view",
            "user_pseudo_id": "user_002",
            "event_params": {"section_name": "experience", "time_spent": 45},
        },
    ]


@pytest.fixture
def sample_segment_data():
    """Sample segment data for testing"""
    return {
        "user_pseudo_id": "user_001",
        "segment": "ML_ENGINEER",
        "confidence": 0.85,
        "reasoning": "Heavy ML engagement",
        "xai_explanation": {
            "what": "User clicked AI projects",
            "why": "Technical depth",
            "so_what": "ML engineer",
            "recommendation": "Show ML content",
        },
        "event_summary": {},
    }


@pytest.fixture
def sample_rules_data():
    """Sample personalization rules for testing"""
    return {
        "segment": "ML_ENGINEER",
        "priority_sections": ["projects", "skills"],
        "featured_projects": ["ai_chatbot", "ml_pipeline"],
        "highlight_skills": ["python", "tensorflow"],
        "reasoning": "ML-focused",
        "xai_explanation": {
            "what": "Prioritize AI content",
            "why": "ML segment",
            "so_what": "Better engagement",
            "recommendation": "Add ML blog",
        },
    }
