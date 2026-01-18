/**
 * K6 performance testing script
 * 
 * Installation:
 *   brew install k6
 * 
 * Usage:
 *   # Ramp-up test
 *   k6 run backend/tests/performance.js
 *   
 *   # Constant load
 *   k6 run backend/tests/performance.js --stage 60s:10 --stage 120s:10
 *   
 *   # Generate HTML report
 *   k6 run --out html=report.html backend/tests/performance.js
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Gauge, Counter } from 'k6/metrics';

// Define custom metrics
const errorRate = new Rate('errors');
const apiDuration = new Trend('api_duration');
const activeUsers = new Gauge('active_users');
const successfulRequests = new Counter('successful_requests');

export const options = {
  // Ramping up/down virtual users
  stages: [
    { duration: '30s', target: 20 },   // Ramp up to 20 users
    { duration: '60s', target: 50 },   // Ramp to 50
    { duration: '60s', target: 50 },   // Hold at 50
    { duration: '30s', target: 0 }     // Ramp down
  ],
  
  // Thresholds - test fails if any threshold is exceeded
  thresholds: {
    'http_req_duration': ['p(95)<500', 'p(99)<1000'], // 95% under 500ms
    'errors': ['rate<0.1'], // Error rate < 10%
    'http_req_failed': ['rate<0.1']
  },
  
  ext: {
    loadimpact: {
      projectID: 3332993,
      name: 'Portfolio AI Personalization Load Test'
    }
  }
};

// Test configuration
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const ADMIN_TOKEN = __ENV.ADMIN_TOKEN || 'test-token';

export default function () {
  activeUsers.add(1);
  
  // Group 1: Public API endpoints
  group('Public API', () => {
    // Get personalization
    const personalizeRes = http.get(
      `${BASE_URL}/api/personalization?user_id=test-user-123`,
      {
        tags: { name: 'GetPersonalization' }
      }
    );
    
    const personalizeOk = check(personalizeRes, {
      'personalization status is 200': (r) => r.status === 200,
      'personalization has data': (r) => r.body.includes('rules') || r.body.includes('{}')
    });
    
    if (!personalizeOk) errorRate.add(1);
    else successfulRequests.add(1);
    apiDuration.add(personalizeRes.timings.duration, { endpoint: 'personalization' });
    
    sleep(1);
    
    // Create event
    const eventRes = http.post(
      `${BASE_URL}/api/events`,
      JSON.stringify({
        event_name: 'test_event',
        user_pseudo_id: 'test-user-123',
        event_timestamp: Date.now()
      }),
      {
        headers: { 'Content-Type': 'application/json' },
        tags: { name: 'CreateEvent' }
      }
    );
    
    const eventOk = check(eventRes, {
      'event creation status is 200-201': (r) => r.status === 200 || r.status === 201
    });
    
    if (!eventOk) errorRate.add(1);
    else successfulRequests.add(1);
    apiDuration.add(eventRes.timings.duration, { endpoint: 'events' });
    
    sleep(1);
  });
  
  // Group 2: Authenticated endpoints (admin)
  group('Admin API', () => {
    const authHeaders = {
      'Authorization': `Bearer ${ADMIN_TOKEN}`,
      'Content-Type': 'application/json'
    };
    
    // Search events
    const searchRes = http.get(
      `${BASE_URL}/api/admin/events/search?hours=24&limit=50`,
      {
        headers: authHeaders,
        tags: { name: 'SearchEvents' }
      }
    );
    
    const searchOk = check(searchRes, {
      'search status is 200': (r) => r.status === 200,
      'search returns array': (r) => r.body.includes('[') && r.body.includes(']')
    });
    
    if (!searchOk) errorRate.add(1);
    else successfulRequests.add(1);
    apiDuration.add(searchRes.timings.duration, { endpoint: 'search' });
    
    sleep(1);
    
    // Get insights
    const insightsRes = http.get(
      `${BASE_URL}/api/admin/insights`,
      {
        headers: authHeaders,
        tags: { name: 'GetInsights' }
      }
    );
    
    const insightsOk = check(insightsRes, {
      'insights status is 200': (r) => r.status === 200
    });
    
    if (!insightsOk) errorRate.add(1);
    else successfulRequests.add(1);
    apiDuration.add(insightsRes.timings.duration, { endpoint: 'insights' });
    
    sleep(1);
  });
  
  activeUsers.add(-1);
  sleep(2); // Think time between iterations
}

/**
 * Setup function runs once before the test
 */
export function setup() {
  console.log('Starting performance test...');
  
  // Verify server is up
  const res = http.get(`${BASE_URL}/health`);
  check(res, {
    'server is up': (r) => r.status === 200
  }) || console.warn('Health check failed');
  
  return { startTime: Date.now() };
}

/**
 * Teardown function runs once after the test
 */
export function teardown(data) {
  const duration = Date.now() - data.startTime;
  console.log(`Test completed in ${duration}ms`);
}
