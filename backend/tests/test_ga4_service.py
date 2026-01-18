import pytest
from app.services.ga4_service import GA4Service

@pytest.mark.asyncio
async def test_ga4_fetch_events_mock():
    """Test GA4 service fetch_events with mock"""
    service = GA4Service("mock_path.json", "mock_property_id")
    events = await service.fetch_events(hours=1)
    assert isinstance(events, list)

@pytest.mark.asyncio
async def test_ga4_segment_distribution_mock():
    """Test GA4 service segment distribution"""
    service = GA4Service("mock_path.json", "mock_property_id")
    distribution = await service.get_segment_distribution()
    assert isinstance(distribution, dict)
    assert "ML_ENGINEER" in distribution
