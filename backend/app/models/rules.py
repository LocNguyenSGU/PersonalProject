from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class PersonalizationRulesResponse(BaseModel):
    """Personalization rules response"""
    segment: str
    priority_sections: List[str]
    featured_projects: List[str]
    highlight_skills: List[str]
    reasoning: str
    
    class Config:
        from_attributes = True

class PersonalizationRequest(BaseModel):
    """Personalization request"""
    user_id: str
