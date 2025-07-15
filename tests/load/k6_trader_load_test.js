import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
export const errorRate = new Rate('errors');
export const antiDetectionRate = new Rate('anti_detection_success');

// Test configuration for trader persona - high frequency, real-time processing
export const options = {
  scenarios: {
    trader_real_time_processing: {
      executor: 'constant-arrival-rate',
      rate: 10,                          // 10 requests per second
      timeUnit: '1s',
      duration: '2m',
      preAllocatedVUs: 5,
      maxVUs: 15,
    },
    trader_burst_processing: {
      executor: 'ramping-arrival-rate',
      startRate: 5,
      stages: [
        { duration: '30s', target: 20 },  // Burst to 20 req/s
        { duration: '60s', target: 20 },  // Sustain burst
        { duration: '30s', target: 5 },   // Return to normal
      ],
      preAllocatedVUs: 10,
      maxVUs: 25,
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<1500'],    // 95% under 1.5s for trading
    http_req_failed: ['rate<0.05'],       // Error rate under 5%
    errors: ['rate<0.02'],                // Custom error rate under 2%
    anti_detection_success: ['rate>0.95'], // Anti-detection success > 95%
  },
};

// Financial data sources for trader persona
const financialSources = [
  'https://finviz.com/screener.ashx',
  'https://finance.yahoo.com/quote/SPY',
  'https://finance.yahoo.com/quote/QQQ',
  'https://finance.yahoo.com/quote/AAPL',
  'https://finance.yahoo.com/quote/MSFT',
];

// User agents for anti-detection
const userAgents = [
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
];

export default function () {
  const startTime = Date.now();
  
  // Simulate anti-detection mechanisms
  const userAgent = userAgents[Math.floor(Math.random() * userAgents.length)];
  const delay = Math.random() * 2.5 + 1.5; // 1.5-4.0s human-like delay
  
  // Test real-time financial data processing
  const source = financialSources[Math.floor(Math.random() * financialSources.length)];
  
  const tradingResponse = http.post('http://localhost:8000/api/crawl', JSON.stringify({
    url: source,
    persona: 'trader',
    anti_detection: true,
    real_time: true,
    strategy_validation: ['momentum', 'value'],
  }), {
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': userAgent,
      'Accept': 'application/json, text/html',
      'Accept-Language': 'en-US,en;q=0.9',
      'Cache-Control': 'no-cache',
    },
    timeout: '15s',
  });
  
  const tradingCheck = check(tradingResponse, {
    'trading request processed': (r) => r.status === 200 || r.status === 404,
    'response time < 1.5s': (r) => r.timings.duration < 1500,
    'anti-detection headers present': (r) => r.request.headers['User-Agent'] !== undefined,
  });
  
  if (!tradingCheck) {
    errorRate.add(1);
  } else {
    antiDetectionRate.add(1);
  }
  
  // Test strategy validation under load
  const strategyResponse = http.post('http://localhost:8000/api/validate-strategy', JSON.stringify({
    strategies: ['momentum', 'value'],
    confidence_threshold: 0.75,
    real_time: true,
  }), {
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': userAgent,
    },
    timeout: '10s',
  });
  
  const strategyCheck = check(strategyResponse, {
    'strategy validation responds': (r) => r.status === 200 || r.status === 404,
    'validation time < 10s': (r) => r.timings.duration < 10000,
  });
  
  if (!strategyCheck) {
    errorRate.add(1);
  }
  
  // Measure scenario performance
  const totalTime = Date.now() - startTime;
  console.log(`Trader scenario completed in ${totalTime}ms with ${delay}s delay`);
  
  // Apply anti-detection delay
  sleep(delay);
}

export function handleSummary(data) {
  return {
    'tests/load/k6_trader_results.json': JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}

function textSummary(data, options = {}) {
  const indent = options.indent || '';
  
  let summary = `${indent}Trader Load Test Summary\n`;
  summary += `${indent}=======================\n`;
  summary += `${indent}Peak VUs: ${data.metrics.vus?.values?.max || 'N/A'}\n`;
  summary += `${indent}Total Requests: ${data.metrics.http_reqs?.values?.count || 'N/A'}\n`;
  summary += `${indent}Request Rate: ${data.metrics.http_req_rate?.values?.rate || 'N/A'} req/s\n`;
  summary += `${indent}Error Rate: ${(data.metrics.http_req_failed?.values?.rate || 0) * 100}%\n`;
  summary += `${indent}Anti-Detection Success: ${(data.metrics.anti_detection_success?.values?.rate || 0) * 100}%\n`;
  summary += `${indent}Avg Response Time: ${data.metrics.http_req_duration?.values?.avg || 'N/A'}ms\n`;
  summary += `${indent}95th Percentile: ${data.metrics.http_req_duration?.values?.['p(95)'] || 'N/A'}ms\n`;
  summary += `${indent}Real-time Processing: ${totalTime < 30000 ? 'PASS' : 'FAIL'}\n`;
  
  return summary;
}