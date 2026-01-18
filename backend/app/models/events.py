from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class EventPayload(BaseModel):
    """Custom event payload"""

    event_name: str
    user_pseudo_id: str
    event_params: Optional[Dict[str, Any]] = None
    event_timestamp: int


class EventResponse(BaseModel):
    """Event tracking response"""

    status: str
    message: Optional[str] = None
