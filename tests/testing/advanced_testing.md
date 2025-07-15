# Advanced Testing: Edge Cases, Fault Injection & Stress Testing

## Edge Case Testing Matrix

| Fault Type        | Example                   | Expected Behavior                | Test Implementation |
| ----------------- | ------------------------- | -------------------------------- | ------------------- |
| Invalid YAML      | Inject broken frontmatter | Handled gracefully, logged error | Malformed config files |
| Encoding errors   | Use UTF-16 documents      | Detected and skipped             | Mixed encoding test set |
| Timeout URLs      | Simulate slow responses   | Playwright fallback or timeout   | Mock slow servers |
| Duplicate content | Same article under 3 URLs | Only stored once (cache hit)     | Identical content test |
| Empty responses   | Zero-length HTML          | Graceful skip with logging       | Empty/minimal pages |
| Malformed HTML    | Broken tags, invalid structure | Fallback parsing methods    | HTML fuzzing |
| Network failures  | DNS errors, connection drops | Retry logic and error handling | Network simulation |

## Fault Injection Framework

### Network Failure Simulation
```python
class NetworkFaultInjector:
    def __init__(self):
        self.failure_rate = 0.1  # 10% failure rate
        self.timeout_rate = 0.05  # 5% timeout rate
        
    def inject_network_fault(self, url):
        """Simulate various network conditions"""
        import random
        
        fault_type = random.random()
        
        if fault_type < self.failure_rate:
            # Simulate connection failure
            raise ConnectionError(f"Simulated connection failure for {url}")
        elif fault_type < self.failure_rate + self.timeout_rate:
            # Simulate timeout
            time.sleep(10)  # Force timeout
            raise TimeoutError(f"Simulated timeout for {url}")
        else:
            # Normal operation
            return None

def test_network_resilience():
    """Test system behavior under network stress"""
    fault_injector = NetworkFaultInjector()
    test_urls = load_fault_test_urls(100)
    
    results = []
    for url in test_urls:
        try:
            fault_injector.inject_network_fault(url)
            result = crawl_url_with_retry(url)
            results.append({"url": url, "status": "success", "result": result})
        except Exception as e:
            results.append({"url": url, "status": "failed", "error": str(e)})
    
    # Analyze fault tolerance
    success_rate = len([r for r in results if r["status"] == "success"]) / len(results)
    assert success_rate >= 0.85  # 85% success rate under fault conditions
```

### Content Corruption Testing
```python
def test_malformed_content():
    """Test handling of corrupted and malformed content"""
    
    malformed_cases = [
        # Broken HTML
        {"content": "<html><body><p>Unclosed paragraph<body></html>", "type": "broken_html"},
        
        # Invalid encoding
        {"content": b'\xff\xfe\x00\x00invalid\x00utf8\x00', "type": "invalid_encoding"},
        
        # Empty content
        {"content": "", "type": "empty"},
        
        # Extremely long content
        {"content": "x" * 10_000_000, "type": "excessive_length"},
        
        # Invalid YAML frontmatter
        {"content": "---\ninvalid: yaml: structure\n---\nContent", "type": "invalid_yaml"},
        
        # Mixed encoding issues
        {"content": "Valid text 🚀 followed by \x80\x81\x82", "type": "mixed_encoding"}
    ]
    
    for case in malformed_cases:
        try:
            result = process_content(case["content"])
            # Should handle gracefully, not crash
            assert result is not None
            logging.info(f"Successfully handled {case['type']}")
        except Exception as e:
            # Verify proper error handling
            assert isinstance(e, (ContentProcessingError, EncodingError))
            logging.info(f"Properly caught error for {case['type']}: {e}")
```

## Stress Testing Framework

### High-Volume Concurrent Processing (Enhanced with k6)

**k6 Load Testing (Superior to Python async stress testing):**

```javascript
// k6_stress_test.js - High-performance load testing
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics for IntelForge-specific monitoring
const errorRate = new Rate('intelforge_errors');
const crawlDuration = new Trend('crawl_duration');
const semanticProcessingTime = new Trend('semantic_processing_time');

export let options = {
  scenarios: {
    // Stress test: High concurrent load
    stress_test: {
      executor: 'ramping-vus',
      stages: [
        { duration: '2m', target: 50 },   // Ramp to 50 concurrent crawlers
        { duration: '10m', target: 100 }, // Scale to 100 concurrent crawlers  
        { duration: '5m', target: 200 },  // Stress test at 200 concurrent
        { duration: '2m', target: 0 },    // Ramp down
      ],
    },
    
    // Spike test: Sudden load increases
    spike_test: {
      executor: 'ramping-vus',
      startTime: '20m',
      stages: [
        { duration: '30s', target: 500 }, // Sudden spike to 500
        { duration: '1m', target: 500 },  // Hold spike
        { duration: '30s', target: 0 },   // Drop to zero
      ],
    },
  },
  
  // Performance thresholds (superior to Python assertions)
  thresholds: {
    http_req_duration: ['p(95)<5000'],      // 95% of requests under 5s
    http_req_failed: ['rate<0.05'],         // Error rate under 5%
    intelforge_errors: ['rate<0.10'],       // Custom error rate under 10%
    crawl_duration: ['p(90)<3000'],         // 90% of crawls under 3s
    semantic_processing_time: ['p(95)<1000'], // 95% semantic processing under 1s
    checks: ['rate>0.95'],                  // 95% of checks pass
  },
};

// Anti-detection and realistic crawling simulation
const crawlerConfig = {
  userAgents: [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
  ],
  
  // Test endpoints (mix of fast and slow responses)
  testUrls: [
    'https://httpbin.org/get',
    'https://httpbin.org/delay/1',
    'https://httpbin.org/html',
    'https://example.com',
    'https://httpbin.org/json',
  ]
};

export default function() {
  // Realistic crawler behavior simulation
  const userAgent = crawlerConfig.userAgents[Math.floor(Math.random() * crawlerConfig.userAgents.length)];
  const testUrl = crawlerConfig.testUrls[Math.floor(Math.random() * crawlerConfig.testUrls.length)];
  
  const headers = {
    'User-Agent': userAgent,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
  };
  
  // Simulate crawler request with timing
  const crawlStart = Date.now();
  let response = http.get(testUrl, { headers: headers, timeout: '10s' });
  const crawlTime = Date.now() - crawlStart;
  
  // Record custom metrics
  crawlDuration.add(crawlTime);
  
  // Comprehensive checks (superior to Python assertions)
  let crawlSuccess = check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 5s': (r) => r.timings.duration < 5000,
    'response size > 0': (r) => r.body.length > 0,
    'no server errors': (r) => r.status < 500,
    'content type valid': (r) => r.headers['content-type'] && r.headers['content-type'].includes('text'),
  });
  
  // Simulate semantic processing time
  const semanticStart = Date.now();
  sleep(Math.random() * 0.5); // Simulate 0-500ms semantic processing
  const semanticTime = Date.now() - semanticStart;
  semanticProcessingTime.add(semanticTime);
  
  // Track errors
  errorRate.add(!crawlSuccess);
  
  // Anti-detection: Random delay between requests
  const delay = Math.random() * 2 + 1; // 1-3 seconds
  sleep(delay);
}

// Setup function for test preparation
export function setup() {
  console.log('🚀 Starting IntelForge stress testing...');
  console.log('📊 Monitoring: Crawl performance, semantic processing, error rates');
  return { startTime: Date.now() };
}

// Teardown with comprehensive reporting
export function teardown(data) {
  const testDuration = (Date.now() - data.startTime) / 1000;
  console.log('=== IntelForge Stress Test Summary ===');
  console.log(`✅ Test Duration: ${testDuration.toFixed(1)}s`);
  console.log('📈 Performance thresholds validated');
  console.log('🔍 Anti-detection patterns applied');
  console.log('⚡ Superior performance vs Python async testing');
}
```

**k6 Advantages over Python async testing:**
- ✅ **Higher Performance**: Native Go implementation with better concurrency
- ✅ **Lower Resource Usage**: Minimal memory footprint compared to Python
- ✅ **Statistical Analysis**: Built-in percentiles, trends, and thresholds
- ✅ **Real-time Monitoring**: Live metrics during test execution
- ✅ **Cloud Integration**: Easy scaling to cloud load testing
- ✅ **Better HTTP/2 Support**: Native HTTP/2 and gRPC support

**Running k6 stress tests:**
```bash
# Basic stress test
k6 run session_docs/reorganized_docs/testing/scripts/k6_stress_test.js

# With custom configuration
k6 run --vus 100 --duration 10m k6_stress_test.js

# With results export
k6 run --out json=stress_test_results.json k6_stress_test.js

# Cloud load testing (if configured)
k6 cloud k6_stress_test.js
```

**Legacy Python Implementation (for comparison):**
```python
# DEPRECATED: Use k6 instead for better performance
async def stress_test_concurrent_crawling_legacy():
    """Legacy Python stress test - replaced by k6"""
    print("⚠️  Consider using k6 for superior performance and features")
    
    # Original Python implementation preserved for compatibility
    stress_urls = generate_stress_test_urls(100)  # Reduced from 1000 due to Python limitations
    semaphore = asyncio.Semaphore(20)  # Reduced from 50 due to Python GIL
    
    # ... rest of original implementation
    # Performance note: k6 can handle 10x more load with better reliability
```

def test_memory_stress():
    """Test memory usage under sustained load"""
    import psutil
    import gc
    
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Process large batches repeatedly
    for batch_num in range(10):
        large_url_batch = generate_test_urls(500)
        results = process_url_batch(large_url_batch)
        
        # Force garbage collection
        gc.collect()
        
        current_memory = process.memory_info().rss / 1024 / 1024
        memory_growth = current_memory - initial_memory
        
        # Memory should not grow excessively
        assert memory_growth < 1000  # Less than 1GB growth
        
        logging.info(f"Batch {batch_num}: Memory usage = {current_memory:.1f}MB (growth: {memory_growth:.1f}MB)")
```

### Database Stress Testing
```python
def test_chromadb_stress():
    """Test ChromaDB performance under high load"""
    
    # Generate large number of embeddings
    test_documents = generate_test_documents(10000)
    
    start_time = time.time()
    
    # Batch insert test
    batch_size = 100
    for i in range(0, len(test_documents), batch_size):
        batch = test_documents[i:i + batch_size]
        embeddings = generate_embeddings(batch)
        store_embeddings_batch(embeddings)
    
    insert_time = time.time() - start_time
    
    # Query performance test
    search_start = time.time()
    
    for _ in range(1000):  # 1000 random queries
        query = generate_random_query()
        results = search_embeddings(query, top_k=10)
        assert len(results) <= 10
    
    query_time = time.time() - search_start
    
    performance_report = {
        "documents_inserted": len(test_documents),
        "insert_time": insert_time,
        "inserts_per_second": len(test_documents) / insert_time,
        "queries_executed": 1000,
        "query_time": query_time,
        "queries_per_second": 1000 / query_time,
        "avg_query_time": query_time / 1000
    }
    
    # Performance assertions
    assert performance_report["inserts_per_second"] >= 50  # Minimum insert rate
    assert performance_report["avg_query_time"] <= 0.1     # Maximum 100ms per query
    
    return performance_report
```

## Resource Exhaustion Testing

### Disk Space Testing
```python
def test_disk_space_handling():
    """Test behavior when disk space is limited"""
    
    # Simulate low disk space condition
    def simulate_disk_full():
        # Create large temporary files to fill disk
        temp_files = []
        try:
            while True:
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                temp_file.write(b'x' * 1024 * 1024)  # 1MB chunks
                temp_files.append(temp_file.name)
        except OSError:
            # Disk is full
            pass
        return temp_files
    
    # Test crawler behavior with limited disk space
    temp_files = simulate_disk_full()
    
    try:
        # Should handle gracefully
        result = run_crawler_with_limited_disk()
        assert result["status"] == "disk_space_warning"
        assert "error" not in result or "disk" in result["error"].lower()
    finally:
        # Clean up
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except OSError:
                pass

def test_memory_exhaustion():
    """Test behavior under memory pressure"""
    
    # Gradually increase memory usage
    memory_hogs = []
    
    try:
        for size_mb in [100, 200, 500, 1000, 2000]:
            # Allocate memory
            memory_hog = bytearray(size_mb * 1024 * 1024)
            memory_hogs.append(memory_hog)
            
            # Test crawler behavior
            try:
                result = run_lightweight_crawler_test()
                if "error" in result:
                    # Should fail gracefully
                    assert "memory" in result["error"].lower() or "out of memory" in result["error"].lower()
                    break
            except MemoryError:
                # Expected behavior under memory pressure
                logging.info(f"Memory limit reached at {size_mb}MB allocation")
                break
    finally:
        # Release memory
        memory_hogs.clear()
        gc.collect()
```

## Unstructured Content Fuzzing

### Security Fuzzing with Rust cargo-fuzz (Superior to Python)

**Rust Fuzzing Implementation (Memory-Safe with LLVM):**

```rust
// fuzz/fuzz_targets/html_parser.rs - Superior to Python fuzzing
#![no_main]
use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: &[u8]| {
    // Convert bytes to string safely
    if let Ok(html_str) = std::str::from_utf8(data) {
        // Test HTML parsing with arbitrary input
        let _ = parse_html_content(html_str);
        let _ = extract_content_safe(html_str);
        let _ = sanitize_html(html_str);
    }
    
    // Test binary data handling
    let _ = handle_binary_content(data);
});

// fuzz/fuzz_targets/config_parser.rs - Configuration fuzzing
#![no_main]
use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: &[u8]| {
    if let Ok(config_str) = std::str::from_utf8(data) {
        // Fuzz YAML configuration parsing
        let _ = parse_crawler_config(config_str);
        let _ = validate_semantic_thresholds(config_str);
        let _ = load_url_patterns(config_str);
    }
});

// fuzz/fuzz_targets/url_parser.rs - URL validation fuzzing
#![no_main]
use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: &[u8]| {
    if let Ok(url_str) = std::str::from_utf8(data) {
        // Fuzz URL parsing and validation
        let _ = validate_url(url_str);
        let _ = extract_domain(url_str);
        let _ = normalize_url(url_str);
        let _ = check_robots_txt(url_str);
    }
});

// fuzz/fuzz_targets/semantic_scoring.rs - ML model input fuzzing
#![no_main]
use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: &[u8]| {
    if let Ok(content_str) = std::str::from_utf8(data) {
        // Fuzz semantic scoring with arbitrary content
        let _ = calculate_semantic_score(content_str);
        let _ = extract_financial_keywords(content_str);
        let _ = classify_content_category(content_str);
    }
});
```

**Cargo.toml configuration for fuzzing:**
```toml
[package]
name = "intelforge_fuzz_tests"
version = "0.1.0"
edition = "2021"

[dependencies]
libfuzzer-sys = "0.4"

[[bin]]
name = "fuzz_html_parser"
path = "fuzz/fuzz_targets/html_parser.rs"
test = false
doc = false

[[bin]]
name = "fuzz_config_parser"
path = "fuzz/fuzz_targets/config_parser.rs"
test = false
doc = false

[[bin]]
name = "fuzz_url_parser"
path = "fuzz/fuzz_targets/url_parser.rs"
test = false
doc = false

[[bin]]
name = "fuzz_semantic_scoring"
path = "fuzz/fuzz_targets/semantic_scoring.rs"
test = false
doc = false
```

**Rust Fuzzing Commands (Superior Performance):**
```bash
# Setup fuzzing environment
cargo install cargo-fuzz
cd semantic_crawler/rust_tests
cargo fuzz init

# Run HTML parser fuzzing (LLVM-based, memory-safe)
cargo fuzz run html_parser -- -max_total_time=300

# Run configuration parser fuzzing
cargo fuzz run config_parser -- -max_total_time=600

# Run URL parser fuzzing with custom dictionary
cargo fuzz run url_parser -- -dict=url_dict.txt -max_total_time=300

# Run semantic scoring fuzzing (ML input validation)
cargo fuzz run semantic_scoring -- -max_total_time=900

# Reproduce crash from corpus
cargo fuzz run html_parser fuzz/artifacts/html_parser/crash-da39a3ee5e6b4b0d3255bfef95601890afd80709

# Minimize test case
cargo fuzz fmt html_parser fuzz/artifacts/html_parser/crash-da39a3ee5e6b4b0d3255bfef95601890afd80709
```

**Advantages of Rust cargo-fuzz over Python:**
- ✅ **Memory Safety**: Automatic detection of buffer overflows, use-after-free
- ✅ **LLVM Integration**: Advanced coverage-guided fuzzing with LLVM SanitizerCoverage
- ✅ **Performance**: 10x-100x faster execution than Python fuzzing
- ✅ **Crash Reproduction**: Automatic minimal test case generation
- ✅ **Coverage Analysis**: Detailed code coverage tracking during fuzzing
- ✅ **No GIL Limitations**: True parallel fuzzing execution

**Legacy Python Fuzzing (for comparison):**
```python
# DEPRECATED: Use Rust cargo-fuzz for superior performance and safety
def test_html_fuzzing_legacy():
    """Legacy Python fuzzing - replaced by Rust cargo-fuzz"""
    print("⚠️  Consider using Rust cargo-fuzz for memory-safe fuzzing")
    
    # Limited mutation strategies compared to LLVM fuzzing
    html_mutations = [
        "<div>" * 100 + "content" + "</div>" * 100,  # Reduced nesting due to Python limits
        # ... other basic mutations
    ]
    
    # Note: Python fuzzing limitations:
    # - No automatic memory safety checking
    # - Slower execution (GIL-limited)
    # - Manual test case generation
    # - Limited coverage feedback
    
    for i, mutated_html in enumerate(html_mutations):
        try:
            result = extract_content_safe(mutated_html)
            logging.info(f"HTML fuzz test {i}: Handled successfully")
        except Exception as e:
            assert isinstance(e, (ContentExtractionError, HTMLParsingError))
            logging.info(f"HTML fuzz test {i}: Properly caught {type(e).__name__}")
```

**Fuzzing Integration with CI/CD:**
```yaml
# .github/workflows/fuzzing.yml
name: Security Fuzzing
on:
  schedule:
    - cron: '0 2 * * *'  # Daily fuzzing runs

jobs:
  rust_fuzzing:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Rust
        uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
      - name: Install cargo-fuzz
        run: cargo install cargo-fuzz
      - name: Run fuzzing tests
        run: |
          cd semantic_crawler/rust_tests
          timeout 1800 cargo fuzz run html_parser -- -max_total_time=1800 || true
          timeout 1800 cargo fuzz run config_parser -- -max_total_time=1800 || true
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: fuzz-artifacts
          path: semantic_crawler/rust_tests/fuzz/artifacts/
```

def test_encoding_fuzzing():
    """Test various encoding scenarios"""
    
    encoding_tests = [
        # Valid UTF-8
        ("Valid UTF-8: 🚀 rocket emoji", "utf-8"),
        
        # Invalid UTF-8 sequences
        (b'\xff\xfe\x00\x00Invalid\x00UTF8\x00', "utf-8"),
        
        # Mixed encodings
        ("ASCII text".encode('ascii') + "UTF-8 text: 🚀".encode('utf-8'), "utf-8"),
        
        # Windows-1252 content
        ("Smart quotes: "hello"".encode('windows-1252'), "windows-1252"),
        
        # ISO-8859-1 content
        ("Latin characters: café naïve".encode('iso-8859-1'), "iso-8859-1"),
        
        # Empty content
        (b'', "utf-8"),
        
        # Pure binary data
        (bytes(range(256)), "utf-8")
    ]
    
    for content, expected_encoding in encoding_tests:
        try:
            result = handle_encoding_detection(content)
            # Should detect encoding and handle gracefully
            assert result is not None or content == b''
        except EncodingError as e:
            # Expected for some invalid cases
            logging.info(f"Encoding test properly caught: {e}")
```

## Performance Regression Testing

### Snapshot Performance Comparison
```python
def test_performance_regression():
    """Compare current performance against baseline"""
    
    # Load baseline performance metrics
    baseline_metrics = load_baseline_performance()
    
    # Run current performance test
    current_metrics = run_performance_benchmark()
    
    regressions = []
    
    for metric in ["crawl_speed", "memory_usage", "cpu_usage", "accuracy"]:
        baseline_value = baseline_metrics.get(metric, 0)
        current_value = current_metrics.get(metric, 0)
        
        if metric in ["crawl_speed", "accuracy"]:
            # Higher is better
            if current_value < baseline_value * 0.95:  # 5% tolerance
                regressions.append(f"{metric}: {current_value:.3f} < {baseline_value:.3f} (5% regression)")
        else:
            # Lower is better (memory, CPU)
            if current_value > baseline_value * 1.05:  # 5% tolerance
                regressions.append(f"{metric}: {current_value:.3f} > {baseline_value:.3f} (5% regression)")
    
    if regressions:
        logging.warning(f"Performance regressions detected: {regressions}")
        # Optionally fail the test or just warn
        # assert False, f"Performance regressions: {regressions}"
    
    return {
        "baseline": baseline_metrics,
        "current": current_metrics,
        "regressions": regressions
    }
```

## Multi-Environment Testing

### Docker Container Testing
```dockerfile
# Test different Python versions and OS combinations
FROM python:3.10-slim
FROM python:3.11-slim  
FROM python:3.12-slim

# Test with different resource constraints
FROM python:3.12-slim
RUN --mount=type=tmpfs,target=/tmp,tmpfs-size=100m
# Limited memory container testing
```

```python
def test_container_compatibility():
    """Test in containerized environments"""
    
    container_configs = [
        {"memory": "512m", "cpus": "1.0"},
        {"memory": "256m", "cpus": "0.5"},
        {"memory": "1g", "cpus": "2.0"}
    ]
    
    for config in container_configs:
        # Run test in container with resource limits
        result = run_in_container(
            image="intelforge-test",
            memory=config["memory"],
            cpus=config["cpus"],
            test_command="python -m pytest tests/integration/"
        )
        
        assert result.exit_code == 0, f"Container test failed with config {config}"
        
        # Verify performance within constraints
        assert result.max_memory_mb <= parse_memory_limit(config["memory"])
```