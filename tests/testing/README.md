# Testing Framework for IntelForge Semantic Crawler

## Testing Philosophy

**Testing is the foundation of reliable development** - IntelForge prioritizes comprehensive testing over rapid feature addition. Every component must be tested before deployment.

## Directory Structure

```
testing/
├── README.md                    # This overview document
├── test_strategy.md            # Comprehensive testing strategy and categories
├── module_testing_guide.md     # Module-specific testing recommendations
├── performance_benchmarking.md # Rust-based performance and load testing
├── validation_metrics.md       # Success criteria and measurement framework
├── infrastructure_monitoring.md # Production monitoring and observability
├── advanced_testing.md         # Edge cases, fault injection, and stress testing
└── implementation_checklist.md # Actionable testing implementation steps
```

## Key Principles

1. **Testing First**: Test before implement, verify before deploy
2. **Semantic Accuracy**: Focus on meaning preservation, not just functionality
3. **Multi-Layer Validation**: Unit, integration, regression, and semantic testing
4. **Production Readiness**: Test real-world conditions, not just happy paths
5. **Observability**: Monitor semantic quality over time, not just uptime

## Quick Start

1. Read `test_strategy.md` for comprehensive test categories
2. Review `module_testing_guide.md` for specific testing requirements
3. Implement performance benchmarks from `performance_benchmarking.md`
4. Follow validation metrics in `validation_metrics.md`
5. Use `implementation_checklist.md` for systematic execution

## Core Testing Categories

- **Unit Tests**: pytest for isolated module validation
- **Integration Tests**: End-to-end pipeline verification
- **Performance Benchmarks**: Rust-based speed and efficiency testing
- **Semantic Accuracy**: AI model validation and drift detection
- **Regression Testing**: Snapshot comparisons for stability
- **Fault Injection**: Error handling and recovery validation

## Success Criteria

- Semantic filtering accuracy ≥90%
- False positives/negatives ≤5%
- Novel content detection ≥95%
- Crawl speed <1s/URL
- Threshold ensemble confidence ≥0.80
- Graph traversal relevance ≥85%