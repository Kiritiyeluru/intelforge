# Module-Specific Testing Guide

## Core Module Testing Requirements

### `enhanced_research_detector.py`

**Test Scenarios:**
- Input <5 docs → Ensure fallback UMAP/HDBSCAN parameters work
- Inject unrelated content and verify novelty detection accuracy
- Test with duplicate content to validate deduplication
- Edge case: Empty document set handling

**Evaluation Metrics:**
- Topic coherence score validation
- Novelty detection accuracy ≥95%
- Fallback parameter functionality verification

**Test Implementation (Enhanced with Hypothesis Property-Based Testing):**
```python
from hypothesis import given, strategies as st, settings, assume
from hypothesis.extra import pandas as pd_strategies
import pytest

@given(
    doc_count=st.integers(min_value=1, max_value=4),
    doc_content=st.lists(
        st.text(min_size=10, max_size=1000, alphabet=st.characters(whitelist_categories=['L', 'N', 'P'])),
        min_size=1, max_size=4
    )
)
@settings(max_examples=100, deadline=10000)
@pytest.mark.property
def test_small_document_set_properties(doc_count, doc_content):
    """Property-based test: Small document sets should always use fallback parameters"""
    # Ensure we have exactly the number of docs we want to test
    test_docs = doc_content[:doc_count]
    assume(len(test_docs) < 5)  # Critical assumption
    
    result = enhanced_research_detector.detect_novelty(test_docs)
    
    # Properties that should always hold for small document sets
    assert result.fallback_used == True, f"Fallback not used for {len(test_docs)} documents"
    assert result.novel_count >= 0, "Novel count should never be negative"
    assert result.novel_count <= len(test_docs), "Novel count cannot exceed total documents"
    assert result.method in ['fallback_umap', 'fallback_hdbscan'], f"Unexpected method: {result.method}"

@given(
    financial_ratio=st.floats(min_value=0.1, max_value=0.9),
    total_docs=st.integers(min_value=10, max_value=100),
    noise_level=st.floats(min_value=0.0, max_value=0.3)
)
@settings(max_examples=50, deadline=15000)
@pytest.mark.property
def test_novelty_detection_properties(financial_ratio, total_docs, noise_level):
    """Property-based test: Novelty detection should maintain accuracy invariants"""
    
    # Generate mixed document set with known proportions
    financial_count = int(total_docs * financial_ratio)
    random_count = total_docs - financial_count
    
    # Simulate financial and random docs (in practice, use actual content generators)
    financial_docs = generate_financial_content(financial_count)
    random_docs = generate_random_content(random_count, noise_level)
    mixed_docs = financial_docs + random_docs
    
    result = enhanced_research_detector.detect_novelty(mixed_docs)
    
    # Properties that should hold regardless of input composition
    assert 0.0 <= result.novel_percentage <= 1.0, "Novel percentage must be between 0 and 1"
    assert result.confidence_score >= 0.0, "Confidence score cannot be negative"
    assert len(result.novel_documents) == result.novel_count, "Novel count mismatch"
    
    # Domain-specific property: financial content should be less novel than random content
    if financial_ratio > 0.7:  # Mostly financial content
        assert result.novel_percentage < 0.5, "Mostly financial content should have low novelty"
    elif financial_ratio < 0.3:  # Mostly random content  
        assert result.novel_percentage > 0.3, "Mostly random content should have high novelty"

# Traditional test for comparison
def test_novelty_detection_baseline():
    """Baseline test with known good/bad examples"""
    mixed_docs = load_test_financial_docs(20) + load_test_random_docs(20)
    result = enhanced_research_detector.detect_novelty(mixed_docs)
    assert result.novel_percentage >= 0.4  # Expected threshold for this specific mix
```

### `intelligent_knowledge_graph.py`

**Test Scenarios:**
- Create graphs from ~100 mixed-topic documents
- Run traversal on rare queries → validate returned nodes
- Test graph connectivity and node relationship accuracy
- Performance testing with large document sets

**Evaluation Metrics:**
- Graph connectivity validation
- Traversal result relevance ≥85% for top-3 matches
- Graph construction time within acceptable limits

**Test Implementation:**
```python
def test_graph_construction():
    docs = load_test_documents(100)
    graph = intelligent_knowledge_graph.build_graph(docs)
    assert graph.node_count == expected_nodes
    assert graph.connectivity_score >= 0.7

def test_graph_traversal():
    query = "options backtesting"
    results = graph.traverse_query(query, top_k=3)
    manual_relevance = validate_relevance(results, query)
    assert manual_relevance >= 0.85
```

### `adaptive_thresholding.py`

**Test Scenarios:**
- Feed skewed similarity scores and observe method choice
- Edge test: all identical scores or all zeros
- Test statistical, HDBSCAN, and cleanlab method selection
- Confidence score consistency validation

**Evaluation Metrics:**
- Chosen threshold vs ground truth comparison
- Confidence score consistency ≥0.80
- Method selection accuracy for different score distributions

**Test Implementation (Enhanced with Property-Based Testing):**
```python
from hypothesis import given, strategies as st, settings, assume
import numpy as np

@given(
    scores=st.lists(
        st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
        min_size=10, max_size=1000
    ),
    distribution_type=st.sampled_from(['normal', 'skewed', 'bimodal', 'uniform'])
)
@settings(max_examples=100, deadline=15000)
@pytest.mark.property
def test_threshold_method_selection_properties(scores, distribution_type):
    """Property-based test: Threshold selection should be consistent and robust"""
    
    # Transform scores based on distribution type for more realistic testing
    if distribution_type == 'skewed':
        scores = np.power(scores, 2).tolist()  # Right-skewed
    elif distribution_type == 'bimodal':
        # Create bimodal distribution
        half = len(scores) // 2
        scores = [s * 0.3 for s in scores[:half]] + [s * 0.7 + 0.3 for s in scores[half:]]
    
    # Ensure we have valid score range
    assume(len(set(scores)) > 1)  # At least some variation
    assume(max(scores) - min(scores) > 0.1)  # Meaningful spread
    
    method, threshold, confidence = adaptive_thresholding.select_method(scores)
    
    # Properties that should always hold
    assert method in ['statistical', 'hdbscan', 'cleanlab', 'ensemble'], f"Invalid method: {method}"
    assert 0.0 <= threshold <= 1.0, f"Threshold {threshold} out of valid range"
    assert 0.0 <= confidence <= 1.0, f"Confidence {confidence} out of valid range"
    
    # Method-specific properties
    if method == 'statistical':
        # Statistical method should produce reasonable thresholds
        mean_score = np.mean(scores)
        assert abs(threshold - mean_score) <= 3 * np.std(scores), "Threshold too far from statistical center"
    
    # Confidence should reflect distribution characteristics
    score_std = np.std(scores)
    if score_std < 0.1:  # Low variance
        assert confidence >= 0.8, "High confidence expected for low variance data"
    elif score_std > 0.3:  # High variance
        assert confidence <= 0.9, "Lower confidence expected for high variance data"

@given(
    base_value=st.floats(min_value=0.1, max_value=0.9),
    noise_level=st.floats(min_value=0.0, max_value=0.05),
    sample_size=st.integers(min_value=50, max_value=500)
)
@settings(max_examples=50, deadline=10000)
@pytest.mark.property
def test_edge_cases_properties(base_value, noise_level, sample_size):
    """Property-based test: Edge cases should be handled gracefully"""
    
    # Generate near-identical scores (edge case)
    identical_scores = [base_value + np.random.normal(0, noise_level) for _ in range(sample_size)]
    identical_scores = [max(0, min(1, score)) for score in identical_scores]  # Clamp to [0,1]
    
    result = adaptive_thresholding.calculate_threshold(identical_scores)
    
    # Properties for edge cases
    assert result.threshold > 0, "Threshold should be positive even for edge cases"
    assert result.threshold <= 1, "Threshold should not exceed 1"
    assert result.method in ['statistical', 'fallback'], f"Expected fallback method for edge case, got {result.method}"
    assert result.confidence >= 0.5, "Should have reasonable confidence even in edge cases"
    
    # For nearly identical scores, threshold should be close to the base value
    assert abs(result.threshold - base_value) <= 0.2, f"Threshold {result.threshold} too far from base {base_value}"

@given(
    outlier_count=st.integers(min_value=1, max_value=10),
    main_distribution_size=st.integers(min_value=90, max_value=200)
)
@settings(max_examples=30)
@pytest.mark.property
def test_outlier_robustness(outlier_count, main_distribution_size):
    """Property-based test: Threshold calculation should be robust to outliers"""
    
    # Generate main distribution
    main_scores = np.random.normal(0.6, 0.1, main_distribution_size).tolist()
    main_scores = [max(0, min(1, score)) for score in main_scores]
    
    # Add outliers
    outliers = [0.05] * (outlier_count // 2) + [0.95] * (outlier_count - outlier_count // 2)
    all_scores = main_scores + outliers
    
    result = adaptive_thresholding.calculate_threshold(all_scores)
    
    # Should not be overly influenced by outliers
    main_mean = np.mean(main_scores)
    assert abs(result.threshold - main_mean) <= 0.3, "Threshold too influenced by outliers"
    assert result.confidence >= 0.6, "Should maintain reasonable confidence despite outliers"

# Enhanced traditional tests
def test_threshold_method_selection_baseline():
    """Baseline test with known distributions"""
    # Test different known distributions
    distributions = {
        'normal': np.random.normal(0.6, 0.15, 100).tolist(),
        'uniform': np.random.uniform(0.2, 0.8, 100).tolist(),
        'bimodal': np.concatenate([np.random.normal(0.3, 0.05, 50), np.random.normal(0.7, 0.05, 50)]).tolist()
    }
    
    for dist_name, scores in distributions.items():
        scores = [max(0, min(1, s)) for s in scores]  # Clamp to valid range
        method, threshold, confidence = adaptive_thresholding.select_method(scores)
        
        assert method in ['statistical', 'hdbscan', 'cleanlab'], f"Invalid method for {dist_name}"
        assert confidence >= 0.5, f"Low confidence for {dist_name}: {confidence}"
```

### `semantic_spider.py`

**Test Scenarios:**
- Crawl batch of 100 mixed financial and non-financial URLs
- Observe filtering ratio vs expected score
- Test rate limiting and anti-detection measures
- Validate error handling for failed requests

**Evaluation Metrics:**
- Filtering accuracy ≥90%
- Crawl time per URL <1s average
- Success rate for valid URLs ≥95%

**Test Implementation:**
```python
def test_semantic_filtering():
    mixed_urls = financial_urls + non_financial_urls
    results = semantic_spider.crawl_and_filter(mixed_urls)
    
    financial_passed = sum(1 for r in results if r.url in financial_urls and r.passed)
    non_financial_blocked = sum(1 for r in results if r.url in non_financial_urls and not r.passed)
    
    accuracy = (financial_passed + non_financial_blocked) / len(mixed_urls)
    assert accuracy >= 0.90

def test_crawl_performance():
    urls = load_test_urls(100)
    start_time = time.time()
    results = semantic_spider.crawl_batch(urls)
    total_time = time.time() - start_time
    
    avg_time_per_url = total_time / len(urls)
    assert avg_time_per_url < 1.0  # Less than 1 second per URL
```

## Integration Testing

### End-to-End Pipeline Test
```python
def test_complete_semantic_pipeline():
    # Test complete workflow from URL to categorized output
    test_urls = load_validation_urls()
    
    # Execute full pipeline
    results = run_semantic_crawler(test_urls)
    
    # Validate each stage
    assert all(r.extracted_content for r in results if r.successful)
    assert all(r.semantic_score > 0 for r in results if r.successful)
    assert all(r.category in VALID_CATEGORIES for r in results if r.successful)
    assert all(len(r.tags) > 0 for r in results if r.successful)

def test_configuration_validation():
    # Test various configuration scenarios
    configs = [
        'config/test_minimal.yaml',
        'config/test_full_features.yaml',
        'config/test_performance.yaml'
    ]
    
    for config_path in configs:
        crawler = SemanticCrawler(config_path)
        assert crawler.validate_config()
        assert crawler.can_initialize()
```

## Mock Testing Strategy

### External Service Mocking
- **Mock Playwright**: Simulate browser responses
- **Mock API Calls**: Control external service responses  
- **Mock File I/O**: Test without disk dependencies
- **Mock Network**: Simulate timeouts and failures

### Test Data Generation
- **Synthetic Documents**: Generated financial content
- **Controlled Scores**: Predetermined similarity values
- **Known Failures**: URLs designed to trigger specific errors
- **Performance Baselines**: Consistent test datasets for benchmarking