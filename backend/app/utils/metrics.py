"""Prometheus metrics definitions for monitoring"""

from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry

# Create a registry for all metrics
metrics_registry = CollectorRegistry()

# API Metrics
api_requests_total = Counter(
    name="api_requests_total",
    documentation="Total API requests",
    labelnames=["method", "endpoint", "status"],
    registry=metrics_registry
)

api_request_duration = Histogram(
    name="api_request_duration",
    documentation="API request duration in seconds",
    labelnames=["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0),
    registry=metrics_registry
)

# Database Metrics
db_queries_total = Counter(
    name="db_queries_total",
    documentation="Total database queries",
    labelnames=["operation", "table"],
    registry=metrics_registry
)

db_query_duration = Histogram(
    name="db_query_duration",
    documentation="Database query duration in seconds",
    labelnames=["operation", "table"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
    registry=metrics_registry
)

active_db_connections = Gauge(
    name="active_db_connections",
    documentation="Number of active database connections",
    registry=metrics_registry
)

# LLM Metrics
llm_requests_total = Counter(
    name="llm_requests_total",
    documentation="Total LLM API requests",
    labelnames=["provider", "status"],
    registry=metrics_registry
)

llm_request_duration = Histogram(
    name="llm_request_duration",
    documentation="LLM request duration in seconds",
    labelnames=["provider"],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0, 60.0),
    registry=metrics_registry
)

# Cache Metrics
cache_hits_total = Counter(
    name="cache_hits_total",
    documentation="Total cache hits",
    labelnames=["key_pattern"],
    registry=metrics_registry
)

cache_misses_total = Counter(
    name="cache_misses_total",
    documentation="Total cache misses",
    labelnames=["key_pattern"],
    registry=metrics_registry
)
