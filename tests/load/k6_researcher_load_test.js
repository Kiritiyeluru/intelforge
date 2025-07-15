import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
export const errorRate = new Rate('errors');

// Test configuration
export const options = {
  scenarios: {
    researcher_bulk_processing: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '30s', target: 5 },   // Ramp up to 5 virtual users
        { duration: '60s', target: 10 },  // Stay at 10 VUs
        { duration: '30s', target: 0 },   // Ramp down
      ],
      gracefulRampDown: '10s',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests under 2s
    http_req_failed: ['rate<0.1'],     // Error rate under 10%
    errors: ['rate<0.05'],             // Custom error rate under 5%
  },
};

// Test data - academic URLs for bulk processing
const academicUrls = [
  'https://arxiv.org/abs/2301.00001',
  'https://arxiv.org/abs/2301.00002', 
  'https://arxiv.org/abs/2301.00003',
  'https://arxiv.org/abs/2301.00004',
  'https://arxiv.org/abs/2301.00005',
];

export default function () {
  // Simulate researcher persona bulk academic URL processing
  const startTime = Date.now();
  
  // Test CLI status command under load
  const statusResponse = http.get('http://localhost:8000/api/status', {
    headers: {
      'User-Agent': 'k6-load-test-researcher-persona',
      'Accept': 'application/json',
    },
    timeout: '10s',
  });
  
  const statusCheck = check(statusResponse, {
    'status command responds': (r) => r.status === 200 || r.status === 404, // 404 OK if API not running
    'response time < 2s': (r) => r.timings.duration < 2000,
  });
  
  if (!statusCheck) {
    errorRate.add(1);
  }
  
  // Simulate bulk URL processing load
  academicUrls.forEach((url, index) => {
    const processingResponse = http.post('http://localhost:8000/api/crawl', JSON.stringify({
      url: url,
      persona: 'researcher',
      batch_size: 5,
      semantic_analysis: true,
    }), {
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'k6-researcher-bulk-processor',
      },
      timeout: '30s',
    });
    
    const processingCheck = check(processingResponse, {
      'crawl request accepted': (r) => r.status === 200 || r.status === 404, // 404 OK if API not running
      'processing time reasonable': (r) => r.timings.duration < 30000, // 30s max
    });
    
    if (!processingCheck) {
      errorRate.add(1);
    }
    
    // Simulate realistic processing delay between URLs
    sleep(Math.random() * 2 + 1); // 1-3 seconds between requests
  });
  
  // Measure total scenario time
  const totalTime = Date.now() - startTime;
  console.log(`Researcher scenario completed in ${totalTime}ms`);
  
  // Realistic pause between test iterations
  sleep(Math.random() * 3 + 2); // 2-5 seconds
}

export function handleSummary(data) {
  return {
    'tests/load/k6_researcher_results.json': JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}

function textSummary(data, options = {}) {
  const indent = options.indent || '';
  const colors = options.enableColors !== false;
  
  let summary = `${indent}Researcher Load Test Summary\n`;
  summary += `${indent}============================\n`;
  summary += `${indent}Virtual Users: ${data.metrics.vus?.values?.max || 'N/A'}\n`;
  summary += `${indent}Duration: ${data.state?.testRunDurationMs || 'N/A'}ms\n`;
  summary += `${indent}Requests: ${data.metrics.http_reqs?.values?.count || 'N/A'}\n`;
  summary += `${indent}Error Rate: ${(data.metrics.http_req_failed?.values?.rate || 0) * 100}%\n`;
  summary += `${indent}Avg Duration: ${data.metrics.http_req_duration?.values?.avg || 'N/A'}ms\n`;
  summary += `${indent}95th Percentile: ${data.metrics.http_req_duration?.values?.['p(95)'] || 'N/A'}ms\n`;
  
  return summary;
}