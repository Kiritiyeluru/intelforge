#!/bin/bash

# IntelForge Comprehensive Test Suite
# Production-ready testing script with pass/fail criteria
# Part of Part 3C: CI & Production Polish implementation

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/logs/test_runs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TEST_LOG="$LOG_DIR/test_run_$TIMESTAMP.log"
REPORT_FILE="$LOG_DIR/test_report_$TIMESTAMP.md"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test suite configuration
QUICK_MODE=false
SKIP_LOAD_TESTS=false
SKIP_PERSONA_TESTS=false
VERBOSE=false
COVERAGE_THRESHOLD=75
FAIL_FAST=false

# Usage function
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

IntelForge Comprehensive Test Suite Runner

OPTIONS:
    -q, --quick         Run quick test suite only (skip load tests and full persona tests)
    -s, --skip-load     Skip load testing (k6 tests)
    -p, --skip-persona  Skip persona testing scenarios
    -v, --verbose       Enable verbose output
    -f, --fail-fast     Stop on first test failure
    -c, --coverage NUM  Set coverage threshold (default: 75)
    -h, --help          Show this help message

EXAMPLES:
    $0                  # Run full test suite
    $0 --quick          # Run quick tests only
    $0 --skip-load -v   # Skip load tests with verbose output
    $0 --coverage 80    # Set 80% coverage threshold
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -q|--quick)
            QUICK_MODE=true
            shift
            ;;
        -s|--skip-load)
            SKIP_LOAD_TESTS=true
            shift
            ;;
        -p|--skip-persona)
            SKIP_PERSONA_TESTS=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -f|--fail-fast)
            FAIL_FAST=true
            shift
            ;;
        -c|--coverage)
            COVERAGE_THRESHOLD="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$TEST_LOG"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$TEST_LOG"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$TEST_LOG"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$TEST_LOG"
}

# Test result tracking
declare -A test_results
test_count=0
passed_count=0
failed_count=0
start_time=$(date +%s)

# Function to run a test suite
run_test_suite() {
    local suite_name="$1"
    local command="$2"
    local timeout_minutes="${3:-10}"
    
    test_count=$((test_count + 1))
    log_info "Running $suite_name..."
    
    if $VERBOSE; then
        echo "Command: $command"
    fi
    
    # Run test with timeout
    if timeout "${timeout_minutes}m" bash -c "$command" >> "$TEST_LOG" 2>&1; then
        test_results["$suite_name"]="PASS"
        passed_count=$((passed_count + 1))
        log_success "$suite_name completed successfully"
    else
        test_results["$suite_name"]="FAIL"
        failed_count=$((failed_count + 1))
        log_error "$suite_name failed"
        
        if $FAIL_FAST; then
            log_error "Fail-fast mode enabled. Stopping test execution."
            exit 1
        fi
    fi
}

# Function to check dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check pip packages
    local required_packages=("pytest" "pytest-cov")
    for package in "${required_packages[@]}"; do
        if ! python3 -c "import $package" &> /dev/null; then
            log_warning "$package not found, attempting to install..."
            pip install "$package" || {
                log_error "Failed to install $package"
                exit 1
            }
        fi
    done
    
    # Check k6 for load tests
    if ! $SKIP_LOAD_TESTS && ! $QUICK_MODE; then
        if ! command -v k6 &> /dev/null; then
            log_warning "k6 not found, will skip load tests"
            SKIP_LOAD_TESTS=true
        fi
    fi
    
    log_success "Dependencies check completed"
}

# Function to setup test environment
setup_test_environment() {
    log_info "Setting up test environment..."
    
    # Create log directory
    mkdir -p "$LOG_DIR"
    
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Create test report header
    cat > "$REPORT_FILE" << EOF
# IntelForge Test Suite Report
**Generated**: $(date)
**Test Run ID**: $TIMESTAMP
**Configuration**: 
- Quick Mode: $QUICK_MODE
- Skip Load Tests: $SKIP_LOAD_TESTS  
- Skip Persona Tests: $SKIP_PERSONA_TESTS
- Coverage Threshold: $COVERAGE_THRESHOLD%
- Fail Fast: $FAIL_FAST

---

EOF
    
    log_success "Test environment setup completed"
}

# Function to run core test suites
run_core_tests() {
    log_info "=== Running Core Test Suites ==="
    
    # Health & Safety Checks
    run_test_suite "Health Contract Tests" \
        "python -m pytest tests/test_health_contract_passes.py -v" 5
    
    run_test_suite "Health Schema Validation" \
        "python -m pytest tests/test_health_schema.py -v" 5
    
    # Security Baseline
    run_test_suite "Security Baseline Tests" \
        "python -m pytest tests/security/test_security_baseline.py -v" 10
    
    # CLI Testing
    run_test_suite "CLI Regression Tests" \
        "python -m pytest tests/test_cli_regression.py -v" 15
    
    run_test_suite "CLI Workflow Tests" \
        "python -m pytest tests/test_cli_workflows.py -v" 15
}

# Function to run advanced test suites
run_advanced_tests() {
    if $QUICK_MODE; then
        log_info "Skipping advanced tests in quick mode"
        return
    fi
    
    log_info "=== Running Advanced Test Suites ==="
    
    # Performance & ML Tests
    run_test_suite "ML Component Validation" \
        "python -m pytest tests/ml/test_ml_component_validation.py -v" 15
    
    run_test_suite "Embedding Stability Tests" \
        "python -m pytest tests/ml/test_embedding_stability.py -v" 15
    
    run_test_suite "Academic Tools Integration" \
        "python -m pytest tests/integration/test_academic_tools_integration.py -v" 15
    
    # Performance regression (if hyperfine available)
    if command -v hyperfine &> /dev/null; then
        run_test_suite "Performance Regression Tests" \
            "python tests/performance/test_performance_regression.py --cli-only" 10
    else
        log_warning "hyperfine not found, skipping performance regression tests"
    fi
}

# Function to run persona tests
run_persona_tests() {
    if $SKIP_PERSONA_TESTS || $QUICK_MODE; then
        log_info "Skipping persona tests"
        return
    fi
    
    log_info "=== Running Persona Test Suites ==="
    
    run_test_suite "Researcher Persona Tests" \
        "python -m pytest tests/persona/test_researcher_scenario.py -v --tb=short" 20
    
    run_test_suite "Trader Persona Tests" \
        "python -m pytest tests/persona/test_trader_scenario.py -v --tb=short" 20
    
    run_test_suite "Developer Persona Tests" \
        "python -m pytest tests/persona/test_developer_scenario.py -v --tb=short" 20
    
    run_test_suite "E2E Workflow Templates" \
        "python -m pytest tests/persona/test_e2e_workflow_templates.py -v --tb=short" 25
}

# Function to run load tests
run_load_tests() {
    if $SKIP_LOAD_TESTS || $QUICK_MODE; then
        log_info "Skipping load tests"
        return
    fi
    
    log_info "=== Running Load Test Suites ==="
    
    run_test_suite "Load Testing Suite" \
        "python tests/load/run_load_tests.py --suite quick" 15
}

# Function to run coverage analysis
run_coverage_analysis() {
    log_info "=== Running Coverage Analysis ==="
    
    local coverage_cmd="python scripts/coverage_analyzer.py"
    if $QUICK_MODE; then
        coverage_cmd="$coverage_cmd --quick"
    else
        coverage_cmd="$coverage_cmd --full"
    fi
    
    run_test_suite "Coverage Analysis" "$coverage_cmd" 10
    
    # Check coverage threshold
    if [ -f "coverage.json" ]; then
        local coverage_percent
        coverage_percent=$(python3 -c "
import json
with open('coverage.json') as f:
    data = json.load(f)
    print(int(data['totals']['percent_covered']))
" 2>/dev/null || echo "0")
        
        if [ "$coverage_percent" -ge "$COVERAGE_THRESHOLD" ]; then
            log_success "Coverage $coverage_percent% meets threshold of $COVERAGE_THRESHOLD%"
        else
            log_error "Coverage $coverage_percent% below threshold of $COVERAGE_THRESHOLD%"
            test_results["Coverage Threshold"]="FAIL"
            failed_count=$((failed_count + 1))
        fi
    fi
}

# Function to generate final report
generate_report() {
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local duration_formatted=$(printf "%02d:%02d:%02d" $((duration/3600)) $((duration%3600/60)) $((duration%60)))
    
    log_info "=== Generating Test Report ==="
    
    # Add results to report
    cat >> "$REPORT_FILE" << EOF
## Test Results Summary

**Total Tests**: $test_count
**Passed**: $passed_count
**Failed**: $failed_count
**Success Rate**: $(( passed_count * 100 / test_count ))%
**Duration**: $duration_formatted

## Individual Test Results

| Test Suite | Result | Status |
|------------|--------|--------|
EOF
    
    # Add individual results
    for suite in "${!test_results[@]}"; do
        local status="${test_results[$suite]}"
        local icon="❌"
        if [ "$status" = "PASS" ]; then
            icon="✅"
        fi
        echo "| $suite | $status | $icon |" >> "$REPORT_FILE"
    done
    
    # Add overall verdict
    cat >> "$REPORT_FILE" << EOF

## Overall Verdict

EOF
    
    if [ $failed_count -eq 0 ]; then
        echo "🎉 **ALL TESTS PASSED** - Production Ready!" >> "$REPORT_FILE"
        log_success "All tests passed! IntelForge is production ready."
    else
        echo "⚠️ **$failed_count TEST(S) FAILED** - Review required" >> "$REPORT_FILE"
        log_error "$failed_count test suite(s) failed. Review required before production deployment."
    fi
    
    # Add configuration info
    cat >> "$REPORT_FILE" << EOF

## Configuration Details
- Coverage Threshold: $COVERAGE_THRESHOLD%
- Quick Mode: $QUICK_MODE
- Load Tests: $([ "$SKIP_LOAD_TESTS" = "true" ] && echo "Skipped" || echo "Included")
- Persona Tests: $([ "$SKIP_PERSONA_TESTS" = "true" ] && echo "Skipped" || echo "Included")

## Log Files
- Detailed Log: \`$TEST_LOG\`
- Report File: \`$REPORT_FILE\`

---
*Generated by IntelForge Test Suite v1.0*
EOF
    
    log_info "Test report generated: $REPORT_FILE"
}

# Function to cleanup
cleanup() {
    log_info "Cleaning up test environment..."
    # Add any cleanup tasks here
    log_success "Cleanup completed"
}

# Main execution function
main() {
    log_info "Starting IntelForge Comprehensive Test Suite"
    log_info "Test Run ID: $TIMESTAMP"
    
    # Setup
    setup_test_environment
    check_dependencies
    
    # Run test suites
    run_core_tests
    run_advanced_tests
    run_persona_tests
    run_load_tests
    run_coverage_analysis
    
    # Generate report and cleanup
    generate_report
    cleanup
    
    # Exit with appropriate code
    if [ $failed_count -eq 0 ]; then
        log_success "Test suite completed successfully!"
        exit 0
    else
        log_error "Test suite completed with failures!"
        exit 1
    fi
}

# Trap for cleanup on exit
trap cleanup EXIT

# Run main function
main "$@"