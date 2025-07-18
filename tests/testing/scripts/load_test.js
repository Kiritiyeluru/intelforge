import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');

// Load testing configuration optimized for scraping infrastructure
export let options = {
  stages: [
    // Ramp up
    { duration: '2m', target: 10 },   // Simulate 10 concurrent scrapers
    { duration: '5m', target: 50 },   // Scale to 50 concurrent scrapers
    { duration: '2m', target: 0 },    // Ramp down
  ],

  // Performance thresholds based on IntelForge requirements
  thresholds: {
    http_req_duration: ['p(95)<5000'],  // 95% of requests under 5s
    http_req_failed: ['rate<0.05'],     // Error rate under 5%
    errors: ['rate<0.1'],               // Custom error rate under 10%
    checks: ['rate>0.95'],              // 95% of checks pass
  },
};

// Anti-detection headers (mimic real scraping)
const headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
  'Accept-Language': 'en-US,en;q=0.5',
  'Accept-Encoding': 'gzip, deflate, br',
  'DNT': '1',
  'Connection': 'keep-alive',
  'Upgrade-Insecure-Requests': '1',
};

// Test endpoints (safe for load testing)
const endpoints = [
  'https://httpbin.org/get',
  'https://httpbin.org/delay/1',
  'https://httpbin.org/html',
  'https://example.com',
];

export default function() {
  // Select random endpoint
  const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)];

  // Add realistic delay between requests (anti-detection)
  const delay = Math.random() * 2 + 1; // 1-3 seconds

  // Make request with anti-detection headers
  let response = http.get(endpoint, { headers: headers });

  // Comprehensive checks
  let success = check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 5s': (r) => r.timings.duration < 5000,
    'response time < 2s (good)': (r) => r.timings.duration < 2000,
    'response size > 0': (r) => r.body.length > 0,
    'no server errors': (r) => r.status < 500,
  });

  // Track custom error rate
  errorRate.add(!success);

  // Anti-detection: Random delay between requests
  sleep(delay);
}

// Teardown function to summarize results
export function teardown(data) {
  console.log('=== IntelForge Load Test Summary ===');
  console.log('Test completed for scraping infrastructure');
  console.log('Anti-detection headers and delays applied');
  console.log('Performance thresholds validated');
}
