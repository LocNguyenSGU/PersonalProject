from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    JSONB,
    Index,
    BigInteger,
)
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
from app.database.db import Base


class AnalyticsRaw(Base):
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


class UserSegment(Base):
    __tablename__ = "user_segments"

    id = Column(BigInteger, primary_key=True)
    user_pseudo_id = Column(String, unique=True, nullable=False)
    segment = Column(
        String, nullable=False
    )  # ML_ENGINEER, FULLSTACK_DEV, RECRUITER, STUDENT, CASUAL
    confidence = Column(Float, default=0.0)
    reasoning = Column(Text)  # Brief summary
    xai_explanation = Column(
        JSONB
    )  # Full xAI explanation (what/why/so_what/recommendation)
    event_summary = Column(JSONB)
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

    __table_args__ = (
        Index("idx_user_pseudo_id_seg", "user_pseudo_id"),
        Index("idx_segment", "segment"),
    )


class PersonalizationRules(Base):
    __tablename__ = "personalization_rules"

    id = Column(BigInteger, primary_key=True)
    segment = Column(String, unique=True, nullable=False)
    priority_sections = Column(ARRAY(String))
    featured_projects = Column(ARRAY(String))
    highlight_skills = Column(ARRAY(String))
    css_overrides = Column(JSONB)
    reasoning = Column(Text)  # Brief summary
    xai_explanation = Column(JSONB)  # Full xAI explanation
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("idx_segment_rules", "segment"),)


class LLMInsights(Base):
    __tablename__ = "llm_insights"

    id = Column(BigInteger, primary_key=True)
    analysis_period = Column(String)  # ISO date range
    total_visitors = Column(Integer)
    segment_distribution = Column(JSONB)
    top_events = Column(JSONB)
    conversion_metrics = Column(JSONB)
    insight_summary = Column(Text)  # Markdown formatted
    recommendations = Column(JSONB)
    generated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("idx_analysis_period", "analysis_period"),)
