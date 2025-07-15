#!/usr/bin/env python3
"""
Selective Test Runner for IntelForge
Demonstrates test tagging capabilities with different execution scenarios.
Part of Part 3B System Hardening implementation.
"""

import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Dict, Optional

class SelectiveTestRunner:
    """Run pytest with selective markers for different scenarios."""
    
    def __init__(self, test_dir: Path):
        self.test_dir = test_dir
        self.project_root = test_dir.parent
        
    def run_tests(self, markers: List[str], exclude_markers: List[str] = None, 
                  additional_args: List[str] = None, timeout: int = 300) -> Dict:
        """Run tests with specified markers."""
        
        # Build pytest command
        cmd = ['python', '-m', 'pytest']
        
        # Add marker selection
        if markers:
            marker_expr = ' or '.join(markers)
            if exclude_markers:
                exclude_expr = ' and not ' + ' and not '.join(exclude_markers)
                marker_expr = f"({marker_expr}){exclude_expr}"
            cmd.extend(['-m', marker_expr])
        
        # Add test directory
        cmd.append(str(self.test_dir))
        
        # Add additional arguments
        if additional_args:
            cmd.extend(additional_args)
        
        # Add common options
        cmd.extend([
            '-v',
            '--tb=short',
            '--maxfail=5',
            f'--timeout={timeout}',
        ])
        
        print(f"🚀 Running: {' '.join(cmd)}")
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout + 30  # Add buffer for pytest overhead
            )
            
            duration = time.time() - start_time
            success = result.returncode == 0
            
            return {
                'success': success,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'command': ' '.join(cmd),
                'returncode': result.returncode,
            }
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return {
                'success': False,
                'duration': duration,
                'stdout': '',
                'stderr': f'Test execution timed out after {timeout}s',
                'command': ' '.join(cmd),
                'returncode': 124,  # Timeout exit code
            }
    
    def run_quick_tests(self) -> Dict:
        """Run quick tests for frequent execution."""
        print("⚡ Running quick tests (< 30s expected)...")
        return self.run_tests(
            markers=['quick'],
            exclude_markers=['slow', 'load'],
            timeout=60
        )
    
    def run_regression_tests(self) -> Dict:
        """Run regression tests for core functionality."""
        print("🔄 Running regression tests...")
        return self.run_tests(
            markers=['regression'],
            exclude_markers=['load'],
            timeout=300
        )
    
    def run_critical_tests(self) -> Dict:
        """Run critical path tests that must pass."""
        print("🎯 Running critical tests...")
        return self.run_tests(
            markers=['critical'],
            exclude_markers=['slow', 'load'],
            timeout=180
        )
    
    def run_persona_tests(self) -> Dict:
        """Run persona-based user scenario tests."""
        print("🎭 Running persona tests...")
        return self.run_tests(
            markers=['persona'],
            timeout=600
        )
    
    def run_security_tests(self) -> Dict:
        """Run security baseline tests."""
        print("🔒 Running security tests...")
        return self.run_tests(
            markers=['security'],
            timeout=240
        )
    
    def run_ml_tests(self) -> Dict:
        """Run machine learning component tests."""
        print("🧠 Running ML tests...")
        return self.run_tests(
            markers=['ml'],
            timeout=300
        )
    
    def run_integration_tests(self) -> Dict:
        """Run integration tests."""
        print("🔗 Running integration tests...")
        return self.run_tests(
            markers=['integration'],
            exclude_markers=['load'],
            timeout=480
        )
    
    def run_performance_tests(self) -> Dict:
        """Run performance and load tests."""
        print("📊 Running performance tests...")
        return self.run_tests(
            markers=['performance', 'load'],
            timeout=600
        )
    
    def run_full_suite(self) -> Dict:
        """Run full test suite excluding load tests."""
        print("🎯 Running full test suite...")
        return self.run_tests(
            markers=['unit', 'integration', 'regression', 'security', 'ml', 'persona'],
            exclude_markers=['load'],
            timeout=900
        )
    
    def run_ci_tests(self) -> Dict:
        """Run CI-appropriate tests (exclude load/slow tests)."""
        print("🏗️  Running CI test suite...")
        return self.run_tests(
            markers=['regression', 'critical', 'security'],
            exclude_markers=['load', 'slow'],
            timeout=300
        )

def print_result_summary(name: str, result: Dict):
    """Print a formatted summary of test results."""
    status = "✅ PASS" if result['success'] else "❌ FAIL"
    duration = result['duration']
    
    print(f"\n{name}: {status} ({duration:.1f}s)")
    
    if not result['success']:
        print(f"   Return code: {result['returncode']}")
        if result['stderr']:
            # Show first few lines of error
            error_lines = result['stderr'].split('\n')[:3]
            for line in error_lines:
                if line.strip():
                    print(f"   Error: {line.strip()}")
    
    # Show test count from stdout if available
    stdout = result['stdout']
    if 'collected' in stdout:
        for line in stdout.split('\n'):
            if 'collected' in line or 'passed' in line or 'failed' in line:
                print(f"   {line.strip()}")
                break

def main():
    """Main entry point for selective test execution."""
    parser = argparse.ArgumentParser(description='Run IntelForge tests selectively')
    parser.add_argument('--suite', choices=[
        'quick', 'regression', 'critical', 'persona', 'security', 
        'ml', 'integration', 'performance', 'full', 'ci'
    ], help='Test suite to run')
    parser.add_argument('--custom-markers', nargs='+', 
                       help='Custom markers to run (e.g., health cli)')
    parser.add_argument('--exclude', nargs='+',
                       help='Markers to exclude (e.g., slow load)')
    parser.add_argument('--list-markers', action='store_true',
                       help='List available markers')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show commands without running')
    
    args = parser.parse_args()
    
    test_dir = Path(__file__).parent.parent / 'tests'
    runner = SelectiveTestRunner(test_dir)
    
    if args.list_markers:
        print("Available pytest markers:")
        print("========================")
        markers = [
            'unit', 'integration', 'performance', 'scraping', 'slow', 'api',
            'regression', 'security', 'load', 'persona', 'ml', 'drift',
            'cli', 'health', 'quick', 'full', 'critical', 'optional'
        ]
        for marker in sorted(markers):
            print(f"  {marker}")
        print("\nExample usage:")
        print("  python scripts/run_selective_tests.py --suite quick")
        print("  python scripts/run_selective_tests.py --custom-markers health cli")
        print("  python scripts/run_selective_tests.py --custom-markers regression --exclude slow")
        return 0
    
    if args.custom_markers:
        print(f"🎯 Running custom marker selection: {', '.join(args.custom_markers)}")
        result = runner.run_tests(
            markers=args.custom_markers,
            exclude_markers=args.exclude
        )
        print_result_summary("Custom Test Suite", result)
        return 0 if result['success'] else 1
    
    if not args.suite:
        print("❌ Please specify --suite or --custom-markers")
        print("Use --help for available options")
        return 1
    
    # Run specific test suite
    suite_runners = {
        'quick': runner.run_quick_tests,
        'regression': runner.run_regression_tests,
        'critical': runner.run_critical_tests,
        'persona': runner.run_persona_tests,
        'security': runner.run_security_tests,
        'ml': runner.run_ml_tests,
        'integration': runner.run_integration_tests,
        'performance': runner.run_performance_tests,
        'full': runner.run_full_suite,
        'ci': runner.run_ci_tests,
    }
    
    runner_func = suite_runners[args.suite]
    result = runner_func()
    
    print_result_summary(f"{args.suite.title()} Test Suite", result)
    
    # Return appropriate exit code
    return 0 if result['success'] else 1

if __name__ == '__main__':
    exit(main())