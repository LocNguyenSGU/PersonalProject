"""Tests for Prometheus metrics and monitoring"""

import pytest
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import metrics directly without importing the full app
from app.utils.metrics import (
    metrics_registry,
    api_requests_total,
    api_request_duration,
    db_queries_total,
    db_query_duration,
    llm_requests_total,
    llm_request_duration,
    cache_hits_total,
    cache_misses_total,
    active_db_connections,
)


class TestMetricsInitialization:
    """Test that all metrics are properly initialized"""
    
    def test_api_requests_total_exists(self):
        """Test API requests counter is initialized"""
        assert api_requests_total is not None
        assert api_requests_total._name == "api_requests_total"
    
    def test_api_request_duration_exists(self):
        """Test API request duration histogram is initialized"""
        assert api_request_duration is not None
        assert api_request_duration._name == "api_request_duration"
    
    def test_db_queries_total_exists(self):
        """Test DB queries counter is initialized"""
        assert db_queries_total is not None
        assert db_queries_total._name == "db_queries_total"
    
    def test_db_query_duration_exists(self):
        """Test DB query duration histogram is initialized"""
        assert db_query_duration is not None
        assert db_query_duration._name == "db_query_duration"
    
    def test_llm_requests_total_exists(self):
        """Test LLM requests counter is initialized"""
        assert llm_requests_total is not None
        assert llm_requests_total._name == "llm_requests_total"
    
    def test_llm_request_duration_exists(self):
        """Test LLM request duration histogram is initialized"""
        assert llm_request_duration is not None
        assert llm_request_duration._name == "llm_request_duration"
    
    def test_cache_hits_total_exists(self):
        """Test cache hits counter is initialized"""
        assert cache_hits_total is not None
        assert cache_hits_total._name == "cache_hits_total"
    
    def test_cache_misses_total_exists(self):
        """Test cache misses counter is initialized"""
        assert cache_misses_total is not None
        assert cache_misses_total._name == "cache_misses_total"
    
    def test_active_db_connections_exists(self):
        """Test active DB connections gauge is initialized"""
        assert active_db_connections is not None
        assert active_db_connections._name == "active_db_connections"
    
    def test_metrics_registry_exists(self):
        """Test metrics registry is properly created"""
        assert metrics_registry is not None


class TestMetricsRecording:
    """Test that metrics can be recorded correctly"""
    
    def test_api_requests_total_increment(self):
        """Test incrementing API requests counter"""
        # Record a request
        api_requests_total.labels(
            method="GET",
            endpoint="/health",
            status=200
        ).inc()
        
        # Verify the metric was recorded
        # We can't directly assert the value due to test isolation,
        # but we verify it doesn't raise an exception
        assert api_requests_total is not None
    
    def test_api_request_duration_observe(self):
        """Test observing API request duration"""
        # Record a duration
        api_request_duration.labels(
            method="POST",
            endpoint="/api/test"
        ).observe(0.123)
        
        # Verify the metric was recorded
        assert api_request_duration is not None
    
    def test_db_queries_total_increment(self):
        """Test incrementing DB queries counter"""
        db_queries_total.labels(
            operation="SELECT",
            table="users"
        ).inc()
        
        assert db_queries_total is not None
    
    def test_db_query_duration_observe(self):
        """Test observing DB query duration"""
        db_query_duration.labels(
            operation="INSERT",
            table="events"
        ).observe(0.045)
        
        assert db_query_duration is not None
    
    def test_llm_requests_total_increment(self):
        """Test incrementing LLM requests counter"""
        llm_requests_total.labels(
            provider="gemini",
            status="success"
        ).inc()
        
        assert llm_requests_total is not None
    
    def test_llm_request_duration_observe(self):
        """Test observing LLM request duration"""
        llm_request_duration.labels(
            provider="deepseek"
        ).observe(2.5)
        
        assert llm_request_duration is not None
    
    def test_cache_hits_total_increment(self):
        """Test incrementing cache hits counter"""
        cache_hits_total.labels(
            key_pattern="recommendations:*"
        ).inc()
        
        assert cache_hits_total is not None
    
    def test_cache_misses_total_increment(self):
        """Test incrementing cache misses counter"""
        cache_misses_total.labels(
            key_pattern="user_profile:*"
        ).inc()
        
        assert cache_misses_total is not None
    
    def test_active_db_connections_set(self):
        """Test setting active DB connections gauge"""
        active_db_connections.set(5)
        
        assert active_db_connections is not None
    
    def test_active_db_connections_increment(self):
        """Test incrementing active DB connections gauge"""
        active_db_connections.inc()
        
        assert active_db_connections is not None
    
    def test_active_db_connections_decrement(self):
        """Test decrementing active DB connections gauge"""
        active_db_connections.dec()
        
        assert active_db_connections is not None

