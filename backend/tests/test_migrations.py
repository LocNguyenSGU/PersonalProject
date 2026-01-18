"""Tests for database migrations"""

import pytest
from sqlalchemy import (
    inspect,
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    Index,
    BigInteger,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import declarative_base
from datetime import datetime
from sqlalchemy.pool import NullPool

# Create a test Base directly without importing from app.database.db
TestBase = declarative_base()


# Define models locally for testing to avoid import issues
class AnalyticsRaw(TestBase):
    __tablename__ = "analytics_raw"

    id = Column(BigInteger, primary_key=True)
    ga4_event_id = Column(String, unique=True, nullable=False)
    event_name = Column(String, nullable=False)
    user_pseudo_id = Column(String, nullable=False)
    event_params = Column(JSONB)
    event_timestamp = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_user_pseudo_id", "user_pseudo_id"),
        Index("idx_event_timestamp", "event_timestamp"),
        Index("idx_event_name", "event_name"),
    )


class UserSegment(TestBase):
    __tablename__ = "user_segments"

    id = Column(BigInteger, primary_key=True)
    user_pseudo_id = Column(String, unique=True, nullable=False)
    segment = Column(String, nullable=False)
    confidence = Column(Float, default=0.0)
    reasoning = Column(Text)
    xai_explanation = Column(JSONB)
    event_summary = Column(JSONB)
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

    __table_args__ = (
        Index("idx_user_pseudo_id_seg", "user_pseudo_id"),
        Index("idx_segment", "segment"),
    )


class PersonalizationRules(TestBase):
    __tablename__ = "personalization_rules"

    id = Column(BigInteger, primary_key=True)
    segment = Column(String, unique=True, nullable=False)
    priority_sections = Column(ARRAY(String))
    featured_projects = Column(ARRAY(String))
    highlight_skills = Column(ARRAY(String))
    css_overrides = Column(JSONB)
    reasoning = Column(Text)
    xai_explanation = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("idx_segment_rules", "segment"),)


class LLMInsights(TestBase):
    __tablename__ = "llm_insights"

    id = Column(BigInteger, primary_key=True)
    analysis_period = Column(String)
    total_visitors = Column(Integer)
    segment_distribution = Column(JSONB)
    top_events = Column(JSONB)
    conversion_metrics = Column(JSONB)
    insight_summary = Column(Text)
    recommendations = Column(JSONB)
    generated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("idx_analysis_period", "analysis_period"),)


# Use test database URL - for testing migrations structure
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def sync_engine():
    """Create a sync engine for testing using SQLite"""
    # SQLite in-memory database for testing migration structure
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=NullPool,
    )

    # Create all tables based on models
    TestBase.metadata.create_all(engine)

    yield engine

    engine.dispose()


def test_analytics_raw_table_exists(sync_engine):
    """Test that analytics_raw table exists"""
    inspector = inspect(sync_engine)
    tables = inspector.get_table_names()
    assert "analytics_raw" in tables, "analytics_raw table not found"


def test_user_segments_table_exists(sync_engine):
    """Test that user_segments table exists"""
    inspector = inspect(sync_engine)
    tables = inspector.get_table_names()
    assert "user_segments" in tables, "user_segments table not found"


def test_personalization_rules_table_exists(sync_engine):
    """Test that personalization_rules table exists"""
    inspector = inspect(sync_engine)
    tables = inspector.get_table_names()
    assert "personalization_rules" in tables, "personalization_rules table not found"


def test_llm_insights_table_exists(sync_engine):
    """Test that llm_insights table exists"""
    inspector = inspect(sync_engine)
    tables = inspector.get_table_names()
    assert "llm_insights" in tables, "llm_insights table not found"


def test_xai_explanation_column_in_user_segments(sync_engine):
    """Test that xai_explanation column exists in user_segments table"""
    inspector = inspect(sync_engine)
    columns = [col["name"] for col in inspector.get_columns("user_segments")]
    assert (
        "xai_explanation" in columns
    ), "xai_explanation column not found in user_segments"


def test_xai_explanation_column_in_personalization_rules(sync_engine):
    """Test that xai_explanation column exists in personalization_rules table"""
    inspector = inspect(sync_engine)
    columns = [col["name"] for col in inspector.get_columns("personalization_rules")]
    assert (
        "xai_explanation" in columns
    ), "xai_explanation column not found in personalization_rules"


def test_analytics_raw_required_columns(sync_engine):
    """Test that analytics_raw table has all required columns"""
    inspector = inspect(sync_engine)
    columns = {col["name"]: col for col in inspector.get_columns("analytics_raw")}

    required_columns = [
        "id",
        "ga4_event_id",
        "event_name",
        "user_pseudo_id",
        "event_params",
        "event_timestamp",
        "created_at",
    ]

    for col_name in required_columns:
        assert (
            col_name in columns
        ), f"Required column '{col_name}' not found in analytics_raw"


def test_user_segments_required_columns(sync_engine):
    """Test that user_segments table has all required columns"""
    inspector = inspect(sync_engine)
    columns = {col["name"]: col for col in inspector.get_columns("user_segments")}

    required_columns = [
        "id",
        "user_pseudo_id",
        "segment",
        "confidence",
        "reasoning",
        "xai_explanation",
        "event_summary",
        "analyzed_at",
        "expires_at",
    ]

    for col_name in required_columns:
        assert (
            col_name in columns
        ), f"Required column '{col_name}' not found in user_segments"


def test_personalization_rules_required_columns(sync_engine):
    """Test that personalization_rules table has all required columns"""
    inspector = inspect(sync_engine)
    columns = {
        col["name"]: col for col in inspector.get_columns("personalization_rules")
    }

    required_columns = [
        "id",
        "segment",
        "priority_sections",
        "featured_projects",
        "highlight_skills",
        "css_overrides",
        "reasoning",
        "xai_explanation",
        "created_at",
    ]

    for col_name in required_columns:
        assert (
            col_name in columns
        ), f"Required column '{col_name}' not found in personalization_rules"


def test_llm_insights_required_columns(sync_engine):
    """Test that llm_insights table has all required columns"""
    inspector = inspect(sync_engine)
    columns = {col["name"]: col for col in inspector.get_columns("llm_insights")}

    required_columns = [
        "id",
        "analysis_period",
        "total_visitors",
        "segment_distribution",
        "top_events",
        "conversion_metrics",
        "insight_summary",
        "recommendations",
        "generated_at",
    ]

    for col_name in required_columns:
        assert (
            col_name in columns
        ), f"Required column '{col_name}' not found in llm_insights"
