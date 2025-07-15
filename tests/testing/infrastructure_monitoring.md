# Infrastructure Monitoring and Observability

## Structured Logging Framework

### Crawl Failures Logger
**Purpose**: Track every failure for pattern analysis and debugging

```python
# crawl_failures.jsonl format
{
  "timestamp": "2025-07-12T10:30:45Z",
  "url": "https://broken.com/page",
  "stage": "embedding",
  "error": "IndexError: list index out of range",
  "exception_type": "IndexError",
  "retry_count": 2,
  "user_agent": "Mozilla/5.0...",
  "response_code": 200
}
```

**Implementation:**
```python
def log_crawl_failure(url, stage, error, exception_type):
    failure_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "url": url,
        "stage": stage,
        "error": str(error),
        "exception_type": exception_type.__name__ if hasattr(exception_type, '__name__') else str(exception_type),
        "retry_count": get_retry_count(url),
        "user_agent": get_current_user_agent(),
        "response_code": get_last_response_code(url)
    }
    
    with open("data/logs/crawl_failures.jsonl", "a") as f:
        f.write(json.dumps(failure_entry) + "\n")
```

### Smart Crawl Metadata Indexer
**Purpose**: Comprehensive audit trail for all processing decisions

```python
# crawl_metadata.jsonl format
{
  "url": "https://example.com/article",
  "score": 0.92,
  "category": "research", 
  "tags": ["momentum", "alpha"],
  "length": 2123,
  "embedding_id": "article_3958",
  "threshold_passed": true,
  "processing_time": 1.234,
  "extraction_method": "trafilatura",
  "model_version": "sentence-transformers-2.2.2"
}
```

### False Positive/Negative Tracker
**Purpose**: Build supervised learning dataset from user feedback

```bash
# CLI commands for manual correction
semantic_cli.py mark-false-positive --url https://foo.com --reason "off-topic content"
semantic_cli.py mark-false-negative --url https://bar.com --reason "missed financial signal"
```

**Data Structure:**
```python
# false_positives.jsonl / false_negatives.jsonl
{
  "url": "https://example.com",
  "original_score": 0.85,
  "original_tags": ["momentum", "technical"],
  "correct_category": "news",
  "correction_reason": "breaking news, not research",
  "corrected_by": "manual_review",
  "correction_timestamp": "2025-07-12T14:22:10Z"
}
```

## Performance Monitoring

### System Health Monitor
**Purpose**: Track resource usage and performance trends

```python
def monitor_system_health():
    health_metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "memory_usage_mb": psutil.virtual_memory().used / 1024 / 1024,
        "cpu_percent": psutil.cpu_percent(interval=1),
        "disk_usage_percent": psutil.disk_usage('/').percent,
        "active_processes": len(psutil.pids()),
        "chromadb_size_mb": get_chromadb_size(),
        "cache_hit_rate": calculate_cache_hit_rate(),
        "avg_crawl_time": get_average_crawl_time()
    }
    
    log_health_metrics(health_metrics)
    check_alert_thresholds(health_metrics)
    return health_metrics
```

### Embedding Failure Tracker + Retry Queue
**Purpose**: Ensure no content is lost due to transient failures

```python
# embedding_failures.jsonl
{
  "url": "https://example.com/article",
  "content_hash": "sha256_hash_of_content",
  "failure_reason": "OOM during embedding generation",
  "attempt_count": 3,
  "last_attempt": "2025-07-12T15:45:30Z",
  "content_length": 12543,
  "retry_scheduled": true
}

# CLI retry command
semantic_cli.py retry-failed-embeddings --max-attempts 3 --batch-size 10
```

## Model Health Monitoring

### Soft Label Drift Detector
**Purpose**: Passive monitoring for semantic model degradation

```python
def detect_label_drift():
    # Analyze tag frequency per category over time
    recent_tags = get_recent_tag_distribution(days=7)
    historical_tags = get_historical_tag_distribution(days=30)
    
    drift_alerts = []
    for category in recent_tags:
        for tag in recent_tags[category]:
            recent_freq = recent_tags[category][tag]
            historical_freq = historical_tags.get(category, {}).get(tag, 0)
            
            # Alert if tag frequency changes dramatically
            if recent_freq > historical_freq * 3:
                drift_alerts.append(f"Tag '{tag}' spiked in category '{category}': {historical_freq} → {recent_freq}")
    
    return drift_alerts
```

### Tag-to-Category Confusion Matrix
**Purpose**: Detect classification drift and misalignment

```python
def generate_confusion_matrix():
    """Generate weekly confusion matrix for tag-category relationships"""
    matrix = defaultdict(lambda: defaultdict(int))
    
    # Analyze recent crawl results
    recent_results = load_recent_crawl_metadata(days=7)
    
    for result in recent_results:
        category = result['category']
        for tag in result['tags']:
            matrix[tag][category] += 1
    
    # Format as readable table
    confusion_report = format_confusion_matrix(matrix)
    save_confusion_matrix(confusion_report)
    
    return confusion_report
```

## Threshold Intelligence Logging

### Model Version Logger
**Purpose**: Track all model and configuration changes for reproducibility

```python
def log_threshold_run(threshold, pass_rate, method, config_path, seed, sample_count):
    """Enhanced version with comprehensive tracking"""
    version_info = {
        "sentence_transformers": sentence_transformers.__version__,
        "cleanlab": cleanlab.__version__,
        "txtai": txtai.__version__,
        "python_version": sys.version,
        "platform": platform.platform()
    }
    
    config_hash = hashlib.sha256(open(config_path, 'rb').read()).hexdigest()
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "method": method,
        "threshold": round(threshold, 5),
        "pass_rate": pass_rate,
        "samples": sample_count,
        "config_hash": config_hash,
        "random_seed": seed,
        "versions": version_info,
        "hardware_info": get_hardware_info()
    }
    
    with open("data/logs/threshold_logs.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
```

## Real-Time Monitoring Dashboard

### CLI Runtime Monitor
**Purpose**: Provide real-time feedback during long operations

```python
def monitor_runtime_performance(frequency_seconds=10):
    """Monitor and display runtime statistics"""
    start_time = time.time()
    last_check = start_time
    urls_processed = 0
    errors = 0
    
    while processing_active():
        current_time = time.time()
        if current_time - last_check >= frequency_seconds:
            elapsed = current_time - start_time
            memory_mb = psutil.virtual_memory().used / 1024 / 1024
            cpu_percent = psutil.cpu_percent()
            urls_per_sec = urls_processed / elapsed if elapsed > 0 else 0
            
            print(f"[{elapsed:.0f}s] RAM: {memory_mb:.0f}MB | CPU: {cpu_percent:.0f}% | URLs/sec: {urls_per_sec:.2f} | Errors: {errors}")
            
            last_check = current_time
```

### Weekly System Report Generator
**Purpose**: Automated health and performance summaries

```python
def generate_weekly_report():
    """Generate comprehensive weekly system report"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    report = {
        "report_period": f"{start_date.isoformat()} to {end_date.isoformat()}",
        "crawl_statistics": {
            "total_urls_processed": count_processed_urls(start_date, end_date),
            "success_rate": calculate_success_rate(start_date, end_date),
            "avg_processing_time": calculate_avg_processing_time(start_date, end_date),
            "top_failed_domains": get_top_failed_domains(start_date, end_date, limit=10)
        },
        "semantic_health": {
            "threshold_stability": analyze_threshold_trends(start_date, end_date),
            "tag_distribution": get_tag_distribution(start_date, end_date),
            "category_balance": get_category_distribution(start_date, end_date),
            "novelty_detection_rate": calculate_novelty_rate(start_date, end_date)
        },
        "system_performance": {
            "avg_memory_usage": get_avg_memory_usage(start_date, end_date),
            "peak_cpu_usage": get_peak_cpu_usage(start_date, end_date),
            "cache_performance": analyze_cache_performance(start_date, end_date),
            "storage_growth": calculate_storage_growth(start_date, end_date)
        },
        "recommendations": generate_performance_recommendations()
    }
    
    # Save as markdown for easy reading
    save_weekly_report_markdown(report)
    return report
```

## Alert System

### Performance Alert Thresholds
```python
ALERT_THRESHOLDS = {
    "memory_usage_mb": 1024,  # Alert if memory usage exceeds 1GB
    "cpu_percent": 80,        # Alert if CPU usage exceeds 80%
    "error_rate": 0.10,       # Alert if error rate exceeds 10%
    "avg_crawl_time": 5.0,    # Alert if average crawl time exceeds 5s
    "cache_hit_rate": 0.30,   # Alert if cache hit rate drops below 30%
    "threshold_drift": 0.20   # Alert if threshold changes by more than 20%
}

def check_alert_conditions(metrics):
    alerts = []
    for metric, threshold in ALERT_THRESHOLDS.items():
        if metric in metrics:
            if metrics[metric] > threshold:
                alerts.append(f"ALERT: {metric} = {metrics[metric]:.2f} (threshold: {threshold})")
    
    if alerts:
        send_performance_alerts(alerts)
    
    return alerts
```

### Automated Health Checks
```python
def run_automated_health_check():
    """Daily automated health verification"""
    health_report = {
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Check 1: Semantic accuracy on known URLs
    test_urls = load_golden_test_set()
    accuracy = validate_semantic_accuracy(test_urls)
    health_report["checks"]["semantic_accuracy"] = {
        "value": accuracy,
        "pass": accuracy >= 0.90,
        "threshold": 0.90
    }
    
    # Check 2: System resource usage
    memory_usage = psutil.virtual_memory().percent
    health_report["checks"]["memory_usage"] = {
        "value": memory_usage,
        "pass": memory_usage < 80,
        "threshold": 80
    }
    
    # Check 3: Recent error rate
    error_rate = calculate_recent_error_rate(hours=24)
    health_report["checks"]["error_rate"] = {
        "value": error_rate,
        "pass": error_rate < 0.05,
        "threshold": 0.05
    }
    
    overall_health = all(check["pass"] for check in health_report["checks"].values())
    health_report["overall_health"] = "PASS" if overall_health else "FAIL"
    
    save_health_check_result(health_report)
    
    if not overall_health:
        send_health_alert(health_report)
    
    return health_report
```