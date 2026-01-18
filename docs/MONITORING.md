# Monitoring Guide

## Overview

The AI personalization system uses Prometheus for metrics collection and Grafana for visualization, combined with structured JSON logging for comprehensive observability.

## Architecture

```
Backend Application
  ↓
Prometheus Metrics Endpoint (/metrics)
  ↓
Prometheus Server (scrapes every 15s)
  ↓
Grafana Dashboards (visualization)
  ↓
Alerts & Notifications
```

## Starting Monitoring Services

### Option 1: Docker Compose (Development)

```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Verify services
docker-compose -f docker-compose.monitoring.yml ps
```

### Option 2: Kubernetes (Production)

```bash
# Deploy Prometheus and Grafana
kubectl apply -f k8s/monitoring/

# Port forward for access
kubectl port-forward svc/prometheus 9090:9090
kubectl port-forward svc/grafana 3000:3000
```

## Accessing Dashboards

### Prometheus

- **URL**: http://localhost:9090
- **Purpose**: View raw metrics, run PromQL queries
- **Key Pages**:
  - Status → Targets: See scrape job health
  - Graph: Query metrics with PromQL
  - Alerts: View active alerts

### Grafana

- **URL**: http://localhost:3000
- **Default Credentials**: admin / admin
- **Setup**:
  1. Add Prometheus as data source (http://prometheus:9090)
  2. Import dashboards from dashboard library
  3. Create custom dashboards for your use cases

## Key Metrics

### API Performance

**Metric**: `api_request_duration_seconds`

```promql
# Average API response time (last 5 minutes)
rate(api_request_duration_seconds_sum[5m]) / rate(api_request_duration_seconds_count[5m])

# 95th percentile response time
histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))

# Requests per second
rate(api_requests_total[1m])
```

**Targets**:
- Mean response < 200ms
- P95 response < 500ms
- Success rate > 99%

### Database Performance

**Metric**: `db_query_duration_seconds`

```promql
# Average query duration
rate(db_query_duration_seconds_sum[5m]) / rate(db_query_duration_seconds_count[5m])

# Slow queries (>1 second)
histogram_quantile(0.99, rate(db_query_duration_seconds_bucket[5m]))

# Query count by operation
sum(rate(db_queries_total[1m])) by (operation)
```

**Targets**:
- Mean query < 100ms
- P99 query < 1s
- No long-running queries (>5s)

### Cache Efficiency

**Metrics**: `cache_hits_total`, `cache_misses_total`

```promql
# Cache hit rate
cache_hits_total / (cache_hits_total + cache_misses_total)

# Cache hit trend (5 minute rolling)
rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m]))
```

**Targets**:
- Cache hit rate > 80%
- Growing hit rate over time (indicates warming)

### LLM API Performance

**Metrics**: `llm_requests_total`, `llm_request_duration_seconds`

```promql
# Average LLM response time by provider
rate(llm_request_duration_seconds_sum[5m]) by (provider) /
rate(llm_request_duration_seconds_count[5m]) by (provider)

# LLM success rate
sum(rate(llm_requests_total{status="success"}[5m])) /
sum(rate(llm_requests_total[5m])) by (provider)
```

**Targets**:
- Gemini response < 5s
- DeepSeek response < 10s
- Provider fallback working (0 errors)

### System Resources

**Metrics**: `active_db_connections`

```promql
# Database connection utilization
active_db_connections / 20  # Assuming pool_size=20

# Connection trend
rate(active_db_connections[5m])
```

**Targets**:
- Connection pool utilization < 80%
- No connection pool exhaustion

## Alert Rules

### Define in `prometheus.yml`:

```yaml
groups:
  - name: portfolio_alerts
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.95, api_request_duration_seconds_bucket) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "API latency is high"
      
      - alert: DatabaseSlowQueries
        expr: histogram_quantile(0.99, db_query_duration_seconds_bucket) > 1.0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Database queries are slow"
      
      - alert: LowCacheHitRate
        expr: (cache_hits_total / (cache_hits_total + cache_misses_total)) < 0.7
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Cache hit rate below 70%"
      
      - alert: LLMProviderError
        expr: rate(llm_requests_total{status="error"}[5m]) > 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "LLM provider errors detected"
```

## Logging

### Structured Logging Format

All logs are output as JSON with standard fields:

```json
{
  "timestamp": "2024-01-18T10:30:45.123Z",
  "level": "INFO",
  "logger": "app.services.analysis_engine",
  "message": "Segmentation completed for user",
  "module": "analysis_engine",
  "function": "segment_user",
  "line": 42,
  "user_id": "user_12345",
  "segment": "ML_ENGINEER",
  "confidence": 0.92
}
```

### Log Aggregation

#### Option 1: ELK Stack (Elasticsearch, Logstash, Kibana)

```yaml
# filebeat.yml - Ship logs to Elasticsearch
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/portfolio/*.log

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

#### Option 2: Cloud Logging (AWS CloudWatch, GCP Cloud Logging)

```python
# backend/app/utils/logger.py
import watchtower

handler = watchtower.CloudWatchLogHandler(
    log_group="/aws/portfolio/backend",
    stream_name="backend-stream"
)
logger.addHandler(handler)
```

### Searching Logs

```bash
# View recent logs
docker logs portfolio_backend -f --tail 100

# Filter by level
docker logs portfolio_backend | grep "ERROR"

# Filter by component
docker logs portfolio_backend | grep "db_query"

# With JSON parsing (requires jq)
docker logs portfolio_backend | jq 'select(.level=="ERROR")'
```

## Dashboard Examples

### API Performance Dashboard

Panels:
- Requests per second (line graph)
- Response time distribution (histogram)
- Error rate by endpoint (bar chart)
- Top slow endpoints (table)
- Request count by method (pie chart)

### Database Health Dashboard

Panels:
- Query duration by operation (line graph)
- Query count trend (area graph)
- Active connections (gauge)
- Slow query log (table)
- Index usage stats

### LLM Service Dashboard

Panels:
- Provider usage distribution (pie chart)
- Response time by provider (box plot)
- Success rate by provider (gauge)
- Fallback frequency (counter)
- Cost estimation (metric)

### Cache Analytics Dashboard

Panels:
- Hit rate trend (line graph)
- Hit vs miss distribution (pie chart)
- Memory usage (gauge)
- Top keys (table)
- Eviction rate

## Troubleshooting

### Prometheus Not Scraping Metrics

```bash
# Check Prometheus logs
docker logs prometheus

# Verify metrics endpoint
curl http://localhost:8000/metrics

# Check prometheus config
curl http://localhost:9090/api/v1/targets
```

### Grafana Connection Issues

```bash
# Verify Prometheus datasource
# Grafana → Configuration → Data Sources → Test

# Check network connectivity
docker exec grafana ping prometheus

# Check firewall rules
# Ensure port 9090 is accessible
```

### Missing Metrics

1. Verify metric names match between app and Prometheus config
2. Check metric is being incremented:
   ```python
   # In app code
   api_requests_total.labels(method="GET", endpoint="/api/test", status=200).inc()
   ```
3. Wait 30+ seconds for scrape interval
4. Refresh Prometheus UI (Ctrl+F5)

## Performance Tuning

### Prometheus Optimization

```yaml
# In prometheus.yml
global:
  scrape_interval: 15s      # Adjust based on precision needs
  evaluation_interval: 15s
  scrape_timeout: 10s       # Prevent timeout on slow targets

# Retention policy (default 15 days)
# --storage.tsdb.retention.time=30d
```

### Grafana Optimization

- Use sampling for large datasets (>100K points)
- Set appropriate refresh intervals (not <10s)
- Archive old dashboards
- Optimize dashboard queries (use aggregation)

## Backup & Recovery

### Backup Prometheus Data

```bash
# Snapshot current state
curl -X POST http://localhost:9090/api/v1/admin/tsdb/snapshot

# Archive to storage
tar -czf prometheus_backup_$(date +%Y%m%d).tar.gz /prometheus/snapshots/
```

### Backup Grafana Dashboards

```bash
# Export dashboard JSON
curl http://localhost:3000/api/dashboards/db/<dashboard-name>/json

# Or use Grafana backup tool
```

## Security

### Prometheus Security

- Restrict access to port 9090 (internal only)
- Use reverse proxy with authentication
- Enable RBAC in enterprise version

### Grafana Security

- Change default admin password immediately
- Enable authentication (LDAP, OAuth, SAML)
- Use API tokens with expiration
- Enable audit logging

### Metric Security

- Avoid logging PII in labels
- Use hashmod relabeling for user IDs if needed
- Separate public and private metrics

## Alerting

### Send Alerts to Slack

```yaml
# In prometheus.yml
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

# alertmanager.yml
route:
  receiver: 'slack'

receivers:
  - name: 'slack'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK'
        channel: '#alerts'
        text: '{{ .CommonAnnotations.summary }}'
```

### Send Alerts to Email

```yaml
receivers:
  - name: 'email'
    email_configs:
      - to: 'alerts@example.com'
        from: 'prometheus@example.com'
        smarthost: 'smtp.example.com:587'
```

## Maintenance

### Regular Tasks

- **Daily**: Review error rates and latency
- **Weekly**: Check disk space on Prometheus server
- **Monthly**: Review and optimize alert rules
- **Quarterly**: Audit dashboard usage and retire unused ones

### Metric Retention

Keep detailed metrics for 2 weeks, aggregated data for 1 year.

---

**Last Updated:** January 2026
**Next Review:** Quarterly
