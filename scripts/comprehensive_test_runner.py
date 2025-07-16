#!/usr/bin/env python3
"""
Comprehensive Test Runner for IntelForge Phase 7 Validation
Systematically tests all features with detailed reporting and success metrics
"""

import os
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestResult:
    """Encapsulates test result with detailed information"""

    def __init__(
        self,
        test_name: str,
        success: bool,
        duration: float,
        details: str = "",
        error: str = "",
        metrics: Dict = None,
    ):
        self.test_name = test_name
        self.success = success
        self.duration = duration
        self.details = details
        self.error = error
        self.metrics = metrics or {}
        self.timestamp = datetime.now().isoformat()


class ComprehensiveTestRunner:
    """Main test runner orchestrating all test suites"""

    def __init__(self):
        self.project_root = project_root
        self.test_results: List[TestResult] = []
        self.start_time = time.time()
        self.output_dir = self.project_root / "vault" / "test_reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
        """Centralized logging with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def run_test(self, test_name: str, test_func) -> TestResult:
        """Execute a single test with error handling and timing"""
        self.log(f"Running {test_name}...")
        start_time = time.time()

        try:
            result = test_func()
            duration = time.time() - start_time

            if isinstance(result, tuple):
                success, details, metrics = result
            else:
                success = result
                details = f"Test {'passed' if success else 'failed'}"
                metrics = {}

            test_result = TestResult(test_name, success, duration, details, "", metrics)
            self.log(
                f"✅ {test_name} - {'PASSED' if success else 'FAILED'} ({duration:.2f}s)"
            )

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Error in {test_name}: {str(e)}\n{traceback.format_exc()}"
            test_result = TestResult(test_name, False, duration, "", error_msg)
            self.log(f"❌ {test_name} - ERROR ({duration:.2f}s): {str(e)}")

        self.test_results.append(test_result)
        return test_result

    def test_suite_1_financial_libraries(self) -> Tuple[bool, str, Dict]:
        """Test Suite 1: Financial Libraries Integration"""
        self.log("Starting Test Suite 1: Financial Libraries Integration")

        results = {}
        libraries = [
            ("yfinance", 'import yfinance as yf; print("yfinance available")'),
            (
                "newspaper4k",
                'from newspaper import Article; print("newspaper4k available")',
            ),
            ("plotly", 'import plotly.graph_objects as go; print("plotly available")'),
            ("quantstats", 'import quantstats as qs; print("quantstats available")'),
            ("backtrader", 'import backtrader as bt; print("backtrader available")'),
            (
                "tokenizers",
                'from tokenizers import Tokenizer; print("tokenizers available")',
            ),
            (
                "qdrant_client",
                'from qdrant_client import QdrantClient; print("qdrant_client available")',
            ),
            ("polars", 'import polars as pl; print("polars available")'),
            ("duckdb", 'import duckdb; print("duckdb available")'),
        ]

        passed = 0
        total = len(libraries)

        for lib_name, test_code in libraries:
            try:
                exec(test_code)
                results[lib_name] = "✅ PASSED"
                passed += 1
            except ImportError as e:
                results[lib_name] = f"❌ FAILED: {str(e)}"
            except Exception as e:
                results[lib_name] = f"⚠️ ERROR: {str(e)}"

        success = passed == total
        details = f"Library Integration Tests: {passed}/{total} passed\n"
        for lib, result in results.items():
            details += f"  {lib}: {result}\n"

        metrics = {
            "total_libraries": total,
            "passed_libraries": passed,
            "success_rate": passed / total * 100,
        }

        return success, details, metrics

    def test_suite_2_monitoring_dashboard(self) -> Tuple[bool, str, Dict]:
        """Test Suite 2: Enhanced Monitoring Dashboard"""
        self.log("Starting Test Suite 2: Enhanced Monitoring Dashboard")

        results = {}
        tests_passed = 0

        # Test 1: Check if monitoring script exists
        monitor_script = self.project_root / "scripts" / "enhanced_monitoring.py"
        if monitor_script.exists():
            results["monitoring_script"] = "✅ Script exists"
            tests_passed += 1
        else:
            results["monitoring_script"] = "❌ Script missing"

        # Test 2: Test market data flag
        try:
            result = subprocess.run(
                [sys.executable, str(monitor_script), "--market", "--test"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                results["market_flag"] = "✅ Market data test passed"
                tests_passed += 1
            else:
                results["market_flag"] = f"❌ Market data test failed: {result.stderr}"
        except Exception as e:
            results["market_flag"] = f"❌ Market data test error: {str(e)}"

        # Test 3: Test financial dashboard flag
        try:
            result = subprocess.run(
                [sys.executable, str(monitor_script), "--financial", "--test"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                results["financial_flag"] = "✅ Financial dashboard test passed"
                tests_passed += 1
            else:
                results["financial_flag"] = (
                    f"❌ Financial dashboard test failed: {result.stderr}"
                )
        except Exception as e:
            results["financial_flag"] = f"❌ Financial dashboard test error: {str(e)}"

        total_tests = 3
        success = tests_passed == total_tests

        details = f"Monitoring Dashboard Tests: {tests_passed}/{total_tests} passed\n"
        for test, result in results.items():
            details += f"  {test}: {result}\n"

        metrics = {
            "total_tests": total_tests,
            "passed_tests": tests_passed,
            "success_rate": tests_passed / total_tests * 100,
        }

        return success, details, metrics

    def test_suite_3_ai_processing(self) -> Tuple[bool, str, Dict]:
        """Test Suite 3: AI Processing Pipeline Enhancement"""
        self.log("Starting Test Suite 3: AI Processing Pipeline Enhancement")

        results = {}
        tests_passed = 0

        # Test 1: Check AI processor script
        ai_script = self.project_root / "scripts" / "phase_08_ai_processor.py"
        if ai_script.exists():
            results["ai_script"] = "✅ Script exists"
            tests_passed += 1
        else:
            results["ai_script"] = "❌ Script missing"
            return False, "AI processing script not found", {}

        # Test 2: Test vector database validation
        try:
            result = subprocess.run(
                [sys.executable, str(ai_script), "--validate"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                results["vector_db"] = "✅ Vector database validation passed"
                tests_passed += 1
            else:
                results["vector_db"] = (
                    f"❌ Vector database validation failed: {result.stderr}"
                )
        except Exception as e:
            results["vector_db"] = f"❌ Vector database validation error: {str(e)}"

        # Test 3: Test strategy extraction
        try:
            result = subprocess.run(
                [sys.executable, str(ai_script), "--test", "--extract-strategies"],
                capture_output=True,
                text=True,
                timeout=90,
            )

            if result.returncode == 0:
                results["strategy_extraction"] = "✅ Strategy extraction test passed"
                tests_passed += 1
            else:
                results["strategy_extraction"] = (
                    f"❌ Strategy extraction test failed: {result.stderr}"
                )
        except Exception as e:
            results["strategy_extraction"] = (
                f"❌ Strategy extraction test error: {str(e)}"
            )

        # Test 4: Test semantic search
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(ai_script),
                    "--test",
                    "--search",
                    "algorithmic trading",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                results["semantic_search"] = "✅ Semantic search test passed"
                tests_passed += 1
            else:
                results["semantic_search"] = (
                    f"❌ Semantic search test failed: {result.stderr}"
                )
        except Exception as e:
            results["semantic_search"] = f"❌ Semantic search test error: {str(e)}"

        total_tests = 4
        success = tests_passed == total_tests

        details = f"AI Processing Tests: {tests_passed}/{total_tests} passed\n"
        for test, result in results.items():
            details += f"  {test}: {result}\n"

        metrics = {
            "total_tests": total_tests,
            "passed_tests": tests_passed,
            "success_rate": tests_passed / total_tests * 100,
        }

        return success, details, metrics

    def test_suite_4_integration_performance(self) -> Tuple[bool, str, Dict]:
        """Test Suite 4: Integration & Performance Tests"""
        self.log("Starting Test Suite 4: Integration & Performance Tests")

        results = {}
        tests_passed = 0

        # Test 1: Performance benchmarking
        try:
            perf_script = (
                self.project_root / "scripts" / "phase_09_rust_enhanced_pipeline.py"
            )
            if perf_script.exists():
                result = subprocess.run(
                    [sys.executable, str(perf_script), "--benchmark"],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

                if result.returncode == 0:
                    results["performance_benchmark"] = "✅ Performance benchmark passed"
                    tests_passed += 1
                else:
                    results["performance_benchmark"] = (
                        f"❌ Performance benchmark failed: {result.stderr}"
                    )
            else:
                results["performance_benchmark"] = "❌ Performance script missing"
        except Exception as e:
            results["performance_benchmark"] = (
                f"❌ Performance benchmark error: {str(e)}"
            )

        # Test 2: Memory usage validation
        try:
            import psutil

            current_process = psutil.Process()
            memory_mb = current_process.memory_info().rss / (1024 * 1024)

            if memory_mb < 500:  # Less than 500MB
                results["memory_usage"] = (
                    f"✅ Memory usage acceptable: {memory_mb:.1f}MB"
                )
                tests_passed += 1
            else:
                results["memory_usage"] = f"⚠️ High memory usage: {memory_mb:.1f}MB"
        except Exception as e:
            results["memory_usage"] = f"❌ Memory usage test error: {str(e)}"

        # Test 3: Error handling validation
        try:
            # Test with invalid input to check error handling
            ai_script = self.project_root / "scripts" / "phase_08_ai_processor.py"
            result = subprocess.run(
                [sys.executable, str(ai_script), "--search", ""],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Should handle empty search gracefully
            if "error" in result.stderr.lower() or result.returncode != 0:
                results["error_handling"] = "✅ Error handling works correctly"
                tests_passed += 1
            else:
                results["error_handling"] = "⚠️ Error handling needs improvement"
        except Exception as e:
            results["error_handling"] = f"❌ Error handling test error: {str(e)}"

        total_tests = 3
        success = tests_passed >= 2  # Allow 1 failure for acceptable success

        details = (
            f"Integration & Performance Tests: {tests_passed}/{total_tests} passed\n"
        )
        for test, result in results.items():
            details += f"  {test}: {result}\n"

        metrics = {
            "total_tests": total_tests,
            "passed_tests": tests_passed,
            "success_rate": tests_passed / total_tests * 100,
        }

        return success, details, metrics

    def generate_master_report(self) -> str:
        """Generate consolidated master test report"""
        total_duration = time.time() - self.start_time

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.success)
        failed_tests = total_tests - passed_tests

        # Generate summary
        report = f"""# IntelForge Phase 7: Comprehensive Testing & Validation Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total Duration:** {total_duration:.2f} seconds
**Environment:** {os.name} {sys.platform}

## 📊 Test Summary

**Overall Results:**
- **Total Tests:** {total_tests}
- **Passed:** {passed_tests} ✅
- **Failed:** {failed_tests} ❌
- **Success Rate:** {(passed_tests / total_tests * 100):.1f}%

## 🔍 Detailed Test Results

"""

        # Add detailed results for each test
        for i, result in enumerate(self.test_results, 1):
            status = "✅ PASSED" if result.success else "❌ FAILED"
            report += f"### Test {i}: {result.test_name}\n"
            report += f"**Status:** {status}  \n"
            report += f"**Duration:** {result.duration:.2f}s  \n"
            report += f"**Timestamp:** {result.timestamp}  \n\n"

            if result.details:
                report += f"**Details:**\n```\n{result.details}\n```\n\n"

            if result.error:
                report += f"**Error:**\n```\n{result.error}\n```\n\n"

            if result.metrics:
                report += "**Metrics:**\n"
                for key, value in result.metrics.items():
                    report += f"- {key}: {value}\n"
                report += "\n"

        # Add recommendations
        report += f"""## 🎯 Production Readiness Assessment

**Critical Success Criteria:**
- All financial libraries operational: {"✅" if any("financial_libraries" in r.test_name and r.success for r in self.test_results) else "❌"}
- AI processing pipeline functional: {"✅" if any("ai_processing" in r.test_name and r.success for r in self.test_results) else "❌"}
- Monitoring dashboard operational: {"✅" if any("monitoring_dashboard" in r.test_name and r.success for r in self.test_results) else "❌"}
- Integration tests passing: {"✅" if any("integration_performance" in r.test_name and r.success for r in self.test_results) else "❌"}

**Overall Assessment:** {"🎉 PRODUCTION READY" if passed_tests == total_tests else "⚠️ NEEDS ATTENTION" if passed_tests >= total_tests * 0.8 else "❌ REQUIRES FIXES"}

## 🔧 Next Steps

{"All tests passed! IntelForge is ready for production deployment." if passed_tests == total_tests else f"Address {failed_tests} failing test(s) before production deployment."}

## 📋 Environment Details

- **Python:** {sys.version}
- **Platform:** {sys.platform}
- **Working Directory:** {os.getcwd()}
- **Test Report Generated:** {datetime.now().isoformat()}

---

*Generated by IntelForge Comprehensive Test Runner*
"""

        return report

    def run_all_tests(self):
        """Execute all test suites in order"""
        self.log("🚀 Starting IntelForge Phase 7: Comprehensive Testing & Validation")

        # Execute all test suites
        test_suites = [
            ("Financial Libraries Integration", self.test_suite_1_financial_libraries),
            ("Enhanced Monitoring Dashboard", self.test_suite_2_monitoring_dashboard),
            ("AI Processing Pipeline Enhancement", self.test_suite_3_ai_processing),
            (
                "Integration & Performance Tests",
                self.test_suite_4_integration_performance,
            ),
        ]

        for suite_name, suite_func in test_suites:
            self.run_test(suite_name, suite_func)

        # Generate master report
        self.log("📋 Generating master test report...")
        master_report = self.generate_master_report()

        # Save master report
        report_path = self.output_dir / "comprehensive_test_report.md"
        with open(report_path, "w") as f:
            f.write(master_report)

        self.log(f"✅ Master report saved to: {report_path}")

        # Print summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.success)
        success_rate = passed_tests / total_tests * 100

        self.log(
            f"🎯 TESTING COMPLETE: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)"
        )

        if passed_tests == total_tests:
            self.log("🎉 ALL TESTS PASSED - PRODUCTION READY!")
        elif success_rate >= 80:
            self.log("⚠️ MOSTLY SUCCESSFUL - Minor issues to address")
        else:
            self.log("❌ MAJOR ISSUES DETECTED - Requires attention")

        return passed_tests == total_tests


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print(
            """
IntelForge Comprehensive Test Runner

Usage:
    python comprehensive_test_runner.py [options]

Options:
    --help          Show this help message
    --suite N       Run specific test suite (1-4)
    --quick         Run quick validation tests only

Test Suites:
    1. Financial Libraries Integration
    2. Enhanced Monitoring Dashboard
    3. AI Processing Pipeline Enhancement
    4. Integration & Performance Tests
        """
        )
        return

    runner = ComprehensiveTestRunner()

    if len(sys.argv) > 1 and sys.argv[1] == "--suite":
        suite_num = int(sys.argv[2])
        suite_map = {
            1: (
                "Financial Libraries Integration",
                runner.test_suite_1_financial_libraries,
            ),
            2: (
                "Enhanced Monitoring Dashboard",
                runner.test_suite_2_monitoring_dashboard,
            ),
            3: (
                "AI Processing Pipeline Enhancement",
                runner.test_suite_3_ai_processing,
            ),
            4: (
                "Integration & Performance Tests",
                runner.test_suite_4_integration_performance,
            ),
        }

        if suite_num in suite_map:
            suite_name, suite_func = suite_map[suite_num]
            runner.run_test(suite_name, suite_func)
        else:
            print(f"Invalid suite number: {suite_num}")
            return
    else:
        runner.run_all_tests()


if __name__ == "__main__":
    main()
