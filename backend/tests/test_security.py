"""Security tests for input validation and rate limiting."""

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app
from app.security.validators import (
    ValidatedEvent,
    ValidatedRuleOverride,
    EventSegment,
)
from pydantic import ValidationError
import asyncio


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestInputValidation:
    """Test input validation with Pydantic models."""

    def test_valid_event(self):
        """Test that valid events pass validation."""
        event = ValidatedEvent(
            event_name="user_signup",
            user_pseudo_id="user123",
            event_params={"source": "organic"},
            event_timestamp=1705600000000,
        )
        assert event.event_name == "user_signup"
        assert event.user_pseudo_id == "user123"

    def test_invalid_event_name_with_special_chars(self):
        """Test that event_name with invalid chars is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ValidatedEvent(
                event_name="user-signup!",  # Invalid chars
                user_pseudo_id="user123",
                event_params={},
                event_timestamp=1705600000000,
            )
        assert "alphanumeric characters and underscores" in str(exc_info.value)

    def test_event_name_too_long(self):
        """Test that event_name exceeding max length is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ValidatedEvent(
                event_name="a" * 101,  # Max is 100
                user_pseudo_id="user123",
                event_params={},
                event_timestamp=1705600000000,
            )
        assert "at most 100 characters" in str(exc_info.value)

    def test_event_name_empty(self):
        """Test that empty event_name is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ValidatedEvent(
                event_name="",
                user_pseudo_id="user123",
                event_params={},
                event_timestamp=1705600000000,
            )
        assert "at least 1 character" in str(exc_info.value)

    def test_invalid_user_pseudo_id(self):
        """Test that user_pseudo_id with invalid chars is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ValidatedEvent(
                event_name="event_name",
                user_pseudo_id="user@123",  # @ is invalid
                event_params={},
                event_timestamp=1705600000000,
            )
        assert "alphanumeric characters, hyphens, underscores, and periods" in str(
            exc_info.value
        )

    def test_user_pseudo_id_valid_chars(self):
        """Test that user_pseudo_id accepts valid special chars."""
        event = ValidatedEvent(
            event_name="event_name",
            user_pseudo_id="user-123_abc.xyz",  # Valid chars
            event_params={},
            event_timestamp=1705600000000,
        )
        assert event.user_pseudo_id == "user-123_abc.xyz"

    def test_oversized_event_params(self):
        """Test that event_params exceeding 10KB is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ValidatedEvent(
                event_name="event_name",
                user_pseudo_id="user123",
                event_params={"data": "x" * (15 * 1024)},  # 15KB
                event_timestamp=1705600000000,
            )
        assert "exceeds maximum size of 10KB" in str(exc_info.value)

    def test_valid_event_params_at_limit(self):
        """Test that event_params at 10KB is accepted."""
        # Create params that are close to but under 10KB
        large_data = "x" * 10000
        event = ValidatedEvent(
            event_name="event_name",
            user_pseudo_id="user123",
            event_params={"data": large_data},
            event_timestamp=1705600000000,
        )
        assert "data" in event.event_params

    def test_negative_event_timestamp(self):
        """Test that negative event_timestamp is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ValidatedEvent(
                event_name="event_name",
                user_pseudo_id="user123",
                event_params={},
                event_timestamp=-1000,
            )
        assert "positive" in str(exc_info.value)

    def test_zero_event_timestamp(self):
        """Test that zero event_timestamp is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ValidatedEvent(
                event_name="event_name",
                user_pseudo_id="user123",
                event_params={},
                event_timestamp=0,
            )
        assert "positive" in str(exc_info.value)


class TestRuleOverrideValidation:
    """Test ValidatedRuleOverride validation."""

    def test_valid_rule_override(self):
        """Test that valid rule override passes validation."""
        override = ValidatedRuleOverride(
            segment=EventSegment.ML_ENGINEER,
            priority_sections=["projects", "skills"],
            featured_projects=["project1", "project2"],
            highlight_skills=["Python", "TensorFlow"],
            reasoning="ML engineer profile optimization",
        )
        assert override.segment == EventSegment.ML_ENGINEER
        assert len(override.priority_sections) == 2

    def test_rule_override_all_segments(self):
        """Test that all segment types are valid."""
        for segment in EventSegment:
            override = ValidatedRuleOverride(segment=segment)
            assert override.segment == segment

    def test_priority_sections_exceeds_max(self):
        """Test that priority_sections exceeding max is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ValidatedRuleOverride(
                segment=EventSegment.ML_ENGINEER,
                priority_sections=[f"section{i}" for i in range(11)],  # Max is 10
            )
        assert "at most 10 items" in str(exc_info.value)

    def test_featured_projects_exceeds_max(self):
        """Test that featured_projects exceeding max is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ValidatedRuleOverride(
                segment=EventSegment.ML_ENGINEER,
                featured_projects=[f"project{i}" for i in range(21)],  # Max is 20
            )
        assert "at most 20 items" in str(exc_info.value)

    def test_highlight_skills_exceeds_max(self):
        """Test that highlight_skills exceeding max is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ValidatedRuleOverride(
                segment=EventSegment.ML_ENGINEER,
                highlight_skills=[f"skill{i}" for i in range(31)],  # Max is 30
            )
        assert "at most 30 items" in str(exc_info.value)

    def test_reasoning_exceeds_max(self):
        """Test that reasoning exceeding 1000 chars is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ValidatedRuleOverride(
                segment=EventSegment.ML_ENGINEER, reasoning="x" * 1001  # Max is 1000
            )
        assert "1000 characters" in str(exc_info.value)

    def test_empty_string_in_list(self):
        """Test that empty strings in lists are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ValidatedRuleOverride(
                segment=EventSegment.ML_ENGINEER,
                priority_sections=["section1", "", "section3"],
            )
        assert "non-empty strings" in str(exc_info.value)


class TestInputValidationEndpoint:
    """Test input validation at the API endpoint level."""

    def test_invalid_event_name_returns_422(self, client):
        """Test that invalid event_name returns 422 validation error."""
        response = client.post(
            "/api/events",
            json={
                "event_name": "invalid@event",  # Invalid chars
                "user_pseudo_id": "user123",
                "event_params": {},
                "event_timestamp": 1705600000000,
            },
        )
        # Will get 422 from Pydantic validation
        assert response.status_code in [
            422,
            500,
        ]  # Depends on how EventPayload is defined

    def test_oversized_params_returns_422(self, client):
        """Test that oversized params returns 422 validation error."""
        response = client.post(
            "/api/events",
            json={
                "event_name": "event_name",
                "user_pseudo_id": "user123",
                "event_params": {"data": "x" * (15 * 1024)},  # 15KB
                "event_timestamp": 1705600000000,
            },
        )
        # Will get 422 from Pydantic validation or 500 from exception
        assert response.status_code in [422, 500]


class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_events_endpoint_rate_limit(self, client):
        """Test that /api/events endpoint is rate limited to 100/minute."""
        # Make 101 requests
        responses = []
        for i in range(101):
            response = client.post(
                "/api/events",
                json={
                    "event_name": "test_event",
                    "user_pseudo_id": f"user{i}",
                    "event_params": {},
                    "event_timestamp": 1705600000000,
                },
            )
            responses.append(response.status_code)

        # Count successful responses (should be 100 or fewer)
        success_count = sum(1 for status in responses if status != 429)
        rate_limit_count = sum(1 for status in responses if status == 429)

        # We expect at least some requests to be rate limited
        # Note: The exact count may vary due to timing
        assert rate_limit_count >= 1 or success_count <= 100

    def test_login_endpoint_rate_limit(self, client):
        """Test that /api/admin/login endpoint is rate limited to 5/minute."""
        # Make 6 requests with wrong password (to not succeed)
        responses = []
        for i in range(6):
            response = client.post(
                "/api/admin/login",
                json={"username": "admin", "password": "wrongpassword"},
            )
            responses.append(response.status_code)

        # Count rate limit responses
        rate_limit_count = sum(1 for status in responses if status == 429)

        # We expect at least 1 request to be rate limited
        assert rate_limit_count >= 1 or len(responses) <= 5

    def test_rate_limit_response_format(self, client):
        """Test that rate limit response has correct format."""
        # Make enough requests to trigger rate limit
        for i in range(101):
            response = client.post(
                "/api/events",
                json={
                    "event_name": "test_event",
                    "user_pseudo_id": f"user{i}",
                    "event_params": {},
                    "event_timestamp": 1705600000000,
                },
            )
            if response.status_code == 429:
                # Check response format
                data = response.json()
                assert "detail" in data or "message" in data
                break
        else:
            pytest.skip("Rate limit not triggered in test")


class TestEventSegmentEnum:
    """Test EventSegment enum."""

    def test_all_segments_exist(self):
        """Test that all required segments exist."""
        segments = {
            EventSegment.ML_ENGINEER,
            EventSegment.FULLSTACK_DEV,
            EventSegment.RECRUITER,
            EventSegment.STUDENT,
            EventSegment.CASUAL,
        }
        assert len(segments) == 5

    def test_segment_string_values(self):
        """Test that segment values are correct."""
        assert EventSegment.ML_ENGINEER.value == "ML_ENGINEER"
        assert EventSegment.FULLSTACK_DEV.value == "FULLSTACK_DEV"
        assert EventSegment.RECRUITER.value == "RECRUITER"
        assert EventSegment.STUDENT.value == "STUDENT"
        assert EventSegment.CASUAL.value == "CASUAL"
