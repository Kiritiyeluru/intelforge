#!/usr/bin/env python3
"""
Load Testing Orchestrator for IntelForge
Runs k6 load tests for all persona scenarios with comprehensive reporting.
"""

import subprocess
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LoadTestResult:
    """Result data for a load test execution."""
    persona: str
    test_file: str
    duration_ms: int
    success: bool
    error_message: Optional[str] = None
    metrics: Optional[Dict] = None
    k6_output: Optional[str] = None

class LoadTestOrchestrator:
    """Orchestrates k6 load tests for all persona scenarios."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.results_dir = base_path / "results"
        self.results_dir.mkdir(exist_ok=True)
        
        # Load test configurations
        self.test_configs = {
            'researcher': {
                'file': 'k6_researcher_load_test.js',
                'description': 'Bulk academic URL processing with semantic analysis',
                'expected_duration': 120,  # 2 minutes
            },
            'trader': {
                'file': 'k6_trader_load_test.js', 
                'description': 'Real-time financial data with anti-detection',
                'expected_duration': 180,  # 3 minutes
            },
            'developer': {
                'file': 'k6_developer_load_test.js',
                'description': 'CLI operations and configuration workflows',
                'expected_duration': 300,  # 5 minutes
            },
        }
    
    def run_single_test(self, persona: str, verbose: bool = False) -> LoadTestResult:
        """Run a single k6 load test for the specified persona."""
        config = self.test_configs.get(persona)
        if not config:
            raise ValueError(f"Unknown persona: {persona}")
        
        test_file = self.base_path / config['file']
        if not test_file.exists():
            raise FileNotFoundError(f"Test file not found: {test_file}")
        
        print(f"🚀 Running {persona} load test: {config['description']}")
        print(f"   Expected duration: {config['expected_duration']}s")
        
        start_time = time.time()
        
        try:
            # Run k6 test with JSON output
            cmd = [
                'k6', 'run',
                '--out', f'json={self.results_dir}/k6_{persona}_metrics.json',
                str(test_file)
            ]
            
            if verbose:
                print(f"   Command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=config['expected_duration'] + 60  # Add 60s buffer
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Load k6 metrics if available
            metrics = None
            metrics_file = self.results_dir / f"k6_{persona}_metrics.json"
            if metrics_file.exists():
                try:
                    with open(metrics_file, 'r') as f:
                        # k6 JSON output is newline-delimited, take the last summary
                        lines = f.readlines()
                        if lines:
                            metrics = json.loads(lines[-1])
                except (json.JSONDecodeError, IndexError):
                    print(f"   ⚠️  Could not parse metrics file for {persona}")
            
            success = result.returncode == 0
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {status} - Completed in {duration_ms/1000:.1f}s")
            
            if not success and verbose:
                print(f"   Error output: {result.stderr}")
            
            return LoadTestResult(
                persona=persona,
                test_file=config['file'],
                duration_ms=duration_ms,
                success=success,
                error_message=result.stderr if not success else None,
                metrics=metrics,
                k6_output=result.stdout
            )
            
        except subprocess.TimeoutExpired:
            duration_ms = int((time.time() - start_time) * 1000)
            print(f"   ❌ TIMEOUT - Test exceeded {config['expected_duration']}s limit")
            
            return LoadTestResult(
                persona=persona,
                test_file=config['file'],
                duration_ms=duration_ms,
                success=False,
                error_message=f"Timeout after {config['expected_duration']}s"
            )
        
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            print(f"   ❌ ERROR - {str(e)}")
            
            return LoadTestResult(
                persona=persona,
                test_file=config['file'],
                duration_ms=duration_ms,
                success=False,
                error_message=str(e)
            )
    
    def run_all_tests(self, verbose: bool = False) -> List[LoadTestResult]:
        """Run all persona load tests."""
        print("🎯 Starting IntelForge Load Testing Suite")
        print(f"   Test directory: {self.base_path}")
        print(f"   Results directory: {self.results_dir}")
        print()
        
        results = []
        start_time = time.time()
        
        for persona in self.test_configs.keys():
            try:
                result = self.run_single_test(persona, verbose)
                results.append(result)
            except Exception as e:
                print(f"   💥 CRITICAL ERROR running {persona} test: {e}")
                results.append(LoadTestResult(
                    persona=persona,
                    test_file=self.test_configs[persona]['file'],
                    duration_ms=0,
                    success=False,
                    error_message=str(e)
                ))
            
            # Brief pause between tests
            if persona != list(self.test_configs.keys())[-1]:
                print("   ⏸️  Pausing 10s between tests...")
                time.sleep(10)
        
        total_duration = time.time() - start_time
        
        # Generate comprehensive report
        self.generate_report(results, total_duration)
        
        return results
    
    def generate_report(self, results: List[LoadTestResult], total_duration: float):
        """Generate comprehensive load test report."""
        timestamp = datetime.now().isoformat()
        
        # Calculate summary statistics
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.success)
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Create comprehensive report
        report = {
            'timestamp': timestamp,
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'success_rate': success_rate,
                'total_duration_seconds': total_duration,
            },
            'results': [
                {
                    'persona': r.persona,
                    'test_file': r.test_file,
                    'duration_ms': r.duration_ms,
                    'success': r.success,
                    'error_message': r.error_message,
                    'has_metrics': r.metrics is not None,
                }
                for r in results
            ],
            'detailed_metrics': {
                r.persona: r.metrics for r in results if r.metrics
            }
        }
        
        # Save JSON report
        report_file = self.results_dir / f"load_test_report_{timestamp.replace(':', '-')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print()
        print("📊 Load Test Summary")
        print("===================")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Duration: {total_duration:.1f}s")
        print()
        
        # Per-test details
        for result in results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            print(f"{result.persona:>10}: {status} ({result.duration_ms/1000:.1f}s)")
            if not result.success and result.error_message:
                print(f"             Error: {result.error_message}")
        
        print()
        print(f"📁 Detailed report saved: {report_file}")
        print(f"📁 Individual metrics: {self.results_dir}/k6_*_metrics.json")
        
        # Overall assessment
        if success_rate >= 80:
            print("🎉 Load testing PASSED - System handles concurrent load well")
        elif success_rate >= 60:
            print("⚠️  Load testing PARTIAL - Some performance issues detected")
        else:
            print("🚨 Load testing FAILED - Significant performance problems")

def main():
    parser = argparse.ArgumentParser(description='Run IntelForge k6 load tests')
    parser.add_argument('--persona', choices=['researcher', 'trader', 'developer'],
                       help='Run test for specific persona only')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--test-dir', type=Path, default=Path(__file__).parent,
                       help='Directory containing k6 test files')
    
    args = parser.parse_args()
    
    orchestrator = LoadTestOrchestrator(args.test_dir)
    
    if args.persona:
        # Run single persona test
        result = orchestrator.run_single_test(args.persona, args.verbose)
        exit(0 if result.success else 1)
    else:
        # Run all tests
        results = orchestrator.run_all_tests(args.verbose)
        success_rate = sum(1 for r in results if r.success) / len(results) * 100
        exit(0 if success_rate >= 80 else 1)

if __name__ == '__main__':
    main()