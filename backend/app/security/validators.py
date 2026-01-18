"""Security validators for input validation and schema enforcement."""

from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
import json


class EventSegment(str, Enum):
    """User segment types."""
    ML_ENGINEER = "ML_ENGINEER"
    FULLSTACK_DEV = "FULLSTACK_DEV"
    RECRUITER = "RECRUITER"
    STUDENT = "STUDENT"
    CASUAL = "CASUAL"


class ValidatedEvent(BaseModel):
    """Validated event model with strict input constraints."""
    
    event_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Event name (alphanumeric + underscore)"
    )
    user_pseudo_id: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="User pseudo ID (alphanumeric + -_.)"
    )
    event_params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Event parameters (max 10KB when serialized)"
    )
    event_timestamp: int = Field(
        ...,
        description="Event timestamp in milliseconds"
    )
    
    @field_validator('event_name')
    @classmethod
    def validate_event_name(cls, v: str) -> str:
        """Validate event_name contains only alphanumeric characters and underscores."""
        if not v.replace('_', '').isalnum():
            raise ValueError(
                'event_name must contain only alphanumeric characters and underscores'
            )
        return v
    
    @field_validator('user_pseudo_id')
    @classmethod
    def validate_user_pseudo_id(cls, v: str) -> str:
        """Validate user_pseudo_id contains only allowed characters."""
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.')
        if not all(c in allowed_chars for c in v):
            raise ValueError(
                'user_pseudo_id must contain only alphanumeric characters, hyphens, underscores, and periods'
            )
        return v
    
    @field_validator('event_params')
    @classmethod
    def validate_event_params(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate event_params doesn't exceed 10KB when serialized."""
        serialized = json.dumps(v)
        size_bytes = len(serialized.encode('utf-8'))
        if size_bytes > 10240:  # 10KB = 10240 bytes
            raise ValueError(
                f'event_params exceeds maximum size of 10KB (current size: {size_bytes} bytes)'
            )
        return v
    
    @field_validator('event_timestamp')
    @classmethod
    def validate_event_timestamp(cls, v: int) -> int:
        """Validate event_timestamp is positive."""
        if v <= 0:
            raise ValueError('event_timestamp must be positive')
        return v


class ValidatedRuleOverride(BaseModel):
    """Validated rule override model for admin operations."""
    
    segment: EventSegment = Field(
        ...,
        description="User segment for the override"
    )
    priority_sections: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="Priority sections (max 10 items)"
    )
    featured_projects: List[str] = Field(
        default_factory=list,
        max_length=20,
        description="Featured projects (max 20 items)"
    )
    highlight_skills: List[str] = Field(
        default_factory=list,
        max_length=30,
        description="Highlighted skills (max 30 items)"
    )
    reasoning: str = Field(
        default="",
        max_length=1000,
        description="Reasoning for the override (max 1000 characters)"
    )
    
    @field_validator('priority_sections', 'featured_projects', 'highlight_skills')
    @classmethod
    def validate_list_items(cls, v: List[str]) -> List[str]:
        """Validate list items are non-empty strings."""
        for item in v:
            if not isinstance(item, str) or len(item.strip()) == 0:
                raise ValueError('All list items must be non-empty strings')
            if len(item) > 500:
                raise ValueError('Each list item must not exceed 500 characters')
        return v
    
    @field_validator('reasoning')
    @classmethod
    def validate_reasoning(cls, v: str) -> str:
        """Validate reasoning field."""
        if len(v.strip()) > 1000:
            raise ValueError('reasoning must not exceed 1000 characters')
        return v
