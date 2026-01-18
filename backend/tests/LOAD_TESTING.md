# Load & Performance Testing

Comprehensive testing suite for validating the AI personalization system under load.

## Tools Overview

### 1. Locust (Python-based)

**Best for:**
- Distributed load testing
- Detailed reporting
- Complex user scenarios
- Integration with CI/CD

**Installation:**
```bash
pip install locust
```

**Basic Usage:**
```bash
# With UI
locust -f backend/tests/load_test.py

# Headless
locust -f backend/tests/load_test.py \
  --headless \
  -u 100 \
  -r 10 \
  --run-time 60s \
  --host=http://localhost:8000
```

**Scenarios:**

```bash
# Baseline (smoke test)
locust -f backend/tests/load_test.py \
  -u 10 -r 2 --run-time 60s

# Normal load
locust -f backend/tests/load_test.py \
  -u 50 -r 5 --run-time 300s

# Stress test
locust -f backend/tests/load_test.py \
  -u 200 -r 20 --run-time 600s

# Spike test
locust -f backend/tests/load_test.py \
  -u 500 -r 100 --run-time 120s
```

**Output CSV Reports:**
```bash
locust -f backend/tests/load_test.py \
  --headless \
  -u 100 \
  -r 10 \
  --run-time 120s \
  --csv=reports/load_test
```

### 2. K6 (JavaScript/Go-based)

**Best for:**
- Fast execution
- CI/CD integration
- Cloud testing (Grafana Cloud)
- VU-based testing

**Installation:**
```bash
brew install k6
```

**Basic Usage:**
```bash
# Run default stages
k6 run backend/tests/performance.js

# Custom configuration
k6 run backend/tests/performance.js \
  --vus 100 \
  --duration 5m

# Generate HTML report
k6 run --out html=reports/performance.html \
  backend/tests/performance.js

# Cloud test (requires Grafana Cloud account)
k6 cloud backend/tests/performance.js
```

**Environment Variables:**
```bash
BASE_URL=http://localhost:8000 \
ADMIN_TOKEN=your-token \
k6 run backend/tests/performance.js
```

## Test Scenarios

### Baseline Test
- **Users:** 10
- **Duration:** 60s
- **Purpose:** Smoke test, verify endpoints work
- **Expected:** All endpoints return 200, <100ms latency

### Normal Load
- **Users:** 50
- **Duration:** 5 minutes
- **Purpose:** Typical production load
- **Expected:** 95th percentile <500ms, <1% errors

### Stress Test
- **Users:** 200
- **Duration:** 10 minutes
- **Purpose:** Find breaking point
- **Expected:** Identify when performance degrades

### Spike Test
- **Users:** 500 (sudden)
- **Duration:** 2 minutes
- **Purpose:** Handle traffic spikes
- **Expected:** System remains stable or degrades gracefully

## Metrics to Track

### K6 Metrics

```javascript
// Built-in
- http_req_duration: Response time
- http_req_failed: Failed requests
- http_reqs: Total requests
- vus: Virtual users

// Custom
- errorRate: Percentage of errors
- apiDuration: API call duration by endpoint
- activeUsers: Currently active users
- successfulRequests: Total successful requests
```

### Locust Metrics

- Response times (min, avg, max, median)
- Request count per second
- Failure rate
- Response time percentiles (50th, 95th, 99th)

## Thresholds

Success criteria for automated tests:

```javascript
thresholds: {
  'http_req_duration': [
    'p(95)<500',    // 95% of requests under 500ms
    'p(99)<1000'    // 99% under 1000ms
  ],
  'errors': ['rate<0.1'],           // < 10% errors
  'http_req_failed': ['rate<0.1']   // < 10% failed requests
}
```

## Running in CI/CD

### GitHub Actions Example

```yaml
name: Load Test

on: [schedule, workflow_dispatch]

jobs:
  load-test:
    runs-on: ubuntu-latest
    
    services:
      backend:
        image: portfolio-backend
        options: >-
          --health-cmd="curl -f http://localhost:8000/health"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Install K6
        run: sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69 && echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6-stable.list && sudo apt-get update && sudo apt-get install k6
      
      - name: Run K6 Load Test
        run: |
          k6 run backend/tests/performance.js \
            --out html=reports/performance.html
        env:
          BASE_URL: http://localhost:8000
      
      - name: Upload Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: load-test-report
          path: reports/
```

## Analysis

### K6 Report Analysis

Look for:
1. **Response Times:** Are 95th/99th percentiles acceptable?
2. **Error Rate:** Is it below threshold?
3. **Throughput:** How many requests/sec can system handle?
4. **Resource Usage:** CPU, memory, database connections
5. **Bottlenecks:** Which endpoints are slowest?

### Locust Report Analysis

Check CSV files for:
- Response time distributions
- Failure patterns
- Throughput degradation over time
- Endpoint-specific performance

## Optimization Tips

If tests fail:

1. **High Response Times**
   - Add database indexing
   - Implement caching (Redis)
   - Optimize queries
   - Add connection pooling

2. **High Error Rate**
   - Check logs for exceptions
   - Verify database connectivity
   - Check resource limits (file descriptors, etc.)
   - Look for race conditions

3. **Low Throughput**
   - Increase server resources
   - Add load balancing
   - Implement async processing
   - Reduce lock contention

## Debugging

### K6 Debugging
```bash
# Verbose output
k6 run --verbose backend/tests/performance.js

# With breakpoints
k6 run --loglevel debug backend/tests/performance.js
```

### Locust Debugging
```python
# Add logging
import logging
logging.basicConfig(level=logging.DEBUG)

# In task:
print(f"Response: {response.status_code}")
print(response.content)
```

## Resources

- [K6 Documentation](https://k6.io/docs/)
- [Locust Documentation](https://docs.locust.io/)
- [Load Testing Best Practices](https://www.perfmatrix.com/load-testing-best-practices/)

