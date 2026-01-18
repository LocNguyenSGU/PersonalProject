from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UserSegmentResponse(BaseModel):
    """User segment response"""

    user_pseudo_id: str
    segment: str
    confidence: float
    reasoning: str

    class Config:
        from_attributes = True
