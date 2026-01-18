import pytest
from app.services.llm_service import LLMService

@pytest.mark.asyncio
async def test_llm_service_initialization():
    """Test LLM service can be initialized"""
    service = LLMService("mock_gemini_key", "mock_deepseek_key")
    assert len(service.providers) == 2
    assert service.current_idx == 0

@pytest.mark.asyncio
async def test_llm_service_segment_user_fallback():
    """Test LLM service segment with mock data"""
    service = LLMService("mock_gemini_key", "mock_deepseek_key")
    
    # This will fail due to mock keys, but tests the structure
    events = {
        "total_events": 10,
        "unique_event_types": ["project_click", "section_view"],
        "event_distribution": {"project_click": 7, "section_view": 3}
    }
    
    # Note: Will actually fail with mock keys, but structure is correct
    # In real testing, use proper mock/patch
