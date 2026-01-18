"""Tests for Redis cache functionality"""
import pytest
import json
from app.cache.redis import RedisCache
from app.utils.logger import logger


@pytest.fixture
async def cache():
    """Fixture for test cache instance"""
    test_cache = RedisCache(redis_url="redis://localhost:6379/1")  # Use DB 1 for testing
    try:
        await test_cache.connect()
        # Clear test database before running test
        if test_cache.client:
            await test_cache.client.flushdb()
        yield test_cache
    finally:
        # Cleanup: clear all test keys
        if test_cache.client:
            await test_cache.client.flushdb()
            await test_cache.disconnect()


@pytest.mark.asyncio
async def test_cache_connect_disconnect(cache):
    """Test cache connection and disconnection"""
    assert cache.client is not None
    assert cache.client.connection_pool is not None


@pytest.mark.asyncio
async def test_cache_set_get_string(cache):
    """Test basic set and get with string value"""
    key = "test_key_string"
    value = "test_value"
    
    # Set value
    result = await cache.set(key, value)
    assert result is True
    
    # Get value
    retrieved = await cache.get(key)
    assert retrieved == value


@pytest.mark.asyncio
async def test_cache_set_get_dict(cache):
    """Test set and get with dictionary value"""
    key = "test_key_dict"
    value = {"name": "test_user", "segment": "ML_ENGINEER", "confidence": 0.95}
    
    # Set value
    result = await cache.set(key, value)
    assert result is True
    
    # Get value
    retrieved = await cache.get(key)
    assert retrieved == value
    assert retrieved["name"] == "test_user"
    assert retrieved["segment"] == "ML_ENGINEER"


@pytest.mark.asyncio
async def test_cache_set_get_list(cache):
    """Test set and get with list value"""
    key = "test_key_list"
    value = ["project1", "project2", "project3"]
    
    # Set value
    result = await cache.set(key, value)
    assert result is True
    
    # Get value
    retrieved = await cache.get(key)
    assert retrieved == value
    assert len(retrieved) == 3


@pytest.mark.asyncio
async def test_cache_get_nonexistent(cache):
    """Test getting non-existent key returns None"""
    key = "nonexistent_key_12345"
    retrieved = await cache.get(key)
    assert retrieved is None


@pytest.mark.asyncio
async def test_cache_set_get_with_ttl(cache):
    """Test set with TTL (time to live)"""
    import asyncio
    
    key = "test_key_ttl"
    value = {"data": "temporary"}
    
    # Set with 2 second TTL
    result = await cache.set(key, value, ttl=2)
    assert result is True
    
    # Should be available immediately
    retrieved = await cache.get(key)
    assert retrieved == value
    
    # Wait for expiration
    await asyncio.sleep(2.5)
    
    # Should be expired
    retrieved = await cache.get(key)
    assert retrieved is None


@pytest.mark.asyncio
async def test_cache_delete(cache):
    """Test deleting a key"""
    key = "test_key_delete"
    value = {"data": "to_delete"}
    
    # Set value
    await cache.set(key, value)
    retrieved = await cache.get(key)
    assert retrieved == value
    
    # Delete key
    result = await cache.delete(key)
    assert result is True
    
    # Verify deletion
    retrieved = await cache.get(key)
    assert retrieved is None


@pytest.mark.asyncio
async def test_cache_delete_nonexistent(cache):
    """Test deleting non-existent key"""
    key = "nonexistent_delete_key"
    result = await cache.delete(key)
    assert result is False


@pytest.mark.asyncio
async def test_cache_clear_pattern(cache):
    """Test clearing keys by pattern"""
    # Set multiple keys with pattern
    await cache.set("user_segment:user1", {"segment": "ML_ENGINEER"})
    await cache.set("user_segment:user2", {"segment": "FULLSTACK_DEV"})
    await cache.set("user_segment:user3", {"segment": "RECRUITER"})
    await cache.set("rules:ML_ENGINEER", {"rules": "data"})
    
    # Clear user_segment pattern
    count = await cache.clear_pattern("user_segment:*")
    assert count == 3
    
    # Verify user_segment keys are gone
    assert await cache.get("user_segment:user1") is None
    assert await cache.get("user_segment:user2") is None
    assert await cache.get("user_segment:user3") is None
    
    # Verify rules key still exists
    assert await cache.get("rules:ML_ENGINEER") is not None


@pytest.mark.asyncio
async def test_cache_user_segment_scenario(cache):
    """Test realistic user segment caching scenario"""
    user_id = "user_12345"
    cache_key = f"user_segment:{user_id}"
    
    # Simulate user segment data
    segment_data = {
        "id": 1,
        "user_pseudo_id": user_id,
        "segment": "ML_ENGINEER",
        "confidence": 0.92,
        "reasoning": "Heavy focus on ML projects",
        "xai_explanation": {"factors": ["projects", "skills"]},
        "event_summary": {"total_events": 150},
        "expires_at": "2026-01-19T00:00:00"
    }
    
    # Cache the segment
    result = await cache.set(cache_key, segment_data, ttl=86400)
    assert result is True
    
    # Retrieve and verify
    cached = await cache.get(cache_key)
    assert cached == segment_data
    assert cached["segment"] == "ML_ENGINEER"
    assert cached["confidence"] == 0.92
    
    # Update segment
    segment_data["confidence"] = 0.95
    await cache.set(cache_key, segment_data, ttl=86400)
    
    # Verify update
    cached = await cache.get(cache_key)
    assert cached["confidence"] == 0.95


@pytest.mark.asyncio
async def test_cache_handles_complex_objects(cache):
    """Test caching complex nested objects"""
    key = "complex_data"
    value = {
        "user": {
            "id": "user123",
            "name": "John Doe",
            "preferences": {
                "theme": "dark",
                "notifications": True
            }
        },
        "segments": [
            {"name": "ML_ENGINEER", "score": 0.95},
            {"name": "RECRUITER", "score": 0.15}
        ],
        "timestamps": ["2026-01-18T10:00:00", "2026-01-18T11:00:00"],
        "metrics": {
            "engagement": 0.87,
            "retention": 0.92
        }
    }
    
    # Set complex value
    result = await cache.set(key, value)
    assert result is True
    
    # Get and verify structure
    retrieved = await cache.get(key)
    assert retrieved == value
    assert retrieved["user"]["preferences"]["theme"] == "dark"
    assert len(retrieved["segments"]) == 2
    assert retrieved["metrics"]["engagement"] == 0.87


@pytest.mark.asyncio
async def test_cache_graceful_fallback_on_disconnect(cache):
    """Test cache gracefully handles operations when disconnected"""
    # Disconnect cache
    await cache.disconnect()
    cache.client = None
    
    # Operations should not raise exceptions
    result = await cache.set("test_key", "value")
    assert result is False
    
    retrieved = await cache.get("test_key")
    assert retrieved is None
    
    result = await cache.delete("test_key")
    assert result is False
    
    count = await cache.clear_pattern("*")
    assert count == 0
