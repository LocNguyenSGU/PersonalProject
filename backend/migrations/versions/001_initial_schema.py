"""Initial schema from models - analytics, segmentation, and personalization tables

Revision ID: 001
Revises:
Create Date: 2025-01-18 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create analytics_raw table
    op.create_table(
        "analytics_raw",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("ga4_event_id", sa.String(), nullable=False),
        sa.Column("event_name", sa.String(), nullable=False),
        sa.Column("user_pseudo_id", sa.String(), nullable=False),
        sa.Column(
            "event_params", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("event_timestamp", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ga4_event_id"),
    )
    op.create_index("idx_event_name", "analytics_raw", ["event_name"])
    op.create_index("idx_event_timestamp", "analytics_raw", ["event_timestamp"])
    op.create_index("idx_user_pseudo_id", "analytics_raw", ["user_pseudo_id"])

    # Create user_segments table
    op.create_table(
        "user_segments",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("user_pseudo_id", sa.String(), nullable=False),
        sa.Column("segment", sa.String(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("reasoning", sa.Text(), nullable=True),
        sa.Column(
            "xai_explanation", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column(
            "event_summary", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("analyzed_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_pseudo_id"),
    )
    op.create_index("idx_segment", "user_segments", ["segment"])
    op.create_index("idx_user_pseudo_id_seg", "user_segments", ["user_pseudo_id"])

    # Create personalization_rules table
    op.create_table(
        "personalization_rules",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("segment", sa.String(), nullable=False),
        sa.Column("priority_sections", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("featured_projects", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("highlight_skills", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column(
            "css_overrides", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("reasoning", sa.Text(), nullable=True),
        sa.Column(
            "xai_explanation", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("segment"),
    )
    op.create_index("idx_segment_rules", "personalization_rules", ["segment"])

    # Create llm_insights table
    op.create_table(
        "llm_insights",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("analysis_period", sa.String(), nullable=True),
        sa.Column("total_visitors", sa.Integer(), nullable=True),
        sa.Column(
            "segment_distribution",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("top_events", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "conversion_metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("insight_summary", sa.Text(), nullable=True),
        sa.Column(
            "recommendations", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("generated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_analysis_period", "llm_insights", ["analysis_period"])


def downgrade() -> None:
    op.drop_index("idx_analysis_period", table_name="llm_insights")
    op.drop_table("llm_insights")
    op.drop_index("idx_segment_rules", table_name="personalization_rules")
    op.drop_table("personalization_rules")
    op.drop_index("idx_segment", table_name="user_segments")
    op.drop_index("idx_user_pseudo_id_seg", table_name="user_segments")
    op.drop_table("user_segments")
    op.drop_index("idx_event_name", table_name="analytics_raw")
    op.drop_index("idx_event_timestamp", table_name="analytics_raw")
    op.drop_index("idx_user_pseudo_id", table_name="analytics_raw")
    op.drop_table("analytics_raw")
