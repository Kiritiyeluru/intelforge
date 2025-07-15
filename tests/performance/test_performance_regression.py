#!/usr/bin/env python3
"""
Performance Regression Testing Framework
Uses hyperfine for statistical CLI benchmarking with baseline comparisons.
"""

import json
import subprocess
import os
import sys
import time
import platform
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import statistics

@dataclass
class PerformanceResult:
    """Performance test result data structure."""
    command: str
    mean_time: float
    std_dev: float
    min_time: float
    max_time: float
    median_time: float
    runs: int
    baseline_mean: Optional[float] = None
    baseline_stddev: Optional[float] = None
    regression_factor: Optional[float] = None
    verdict: str = "UNKNOWN"
    tolerance_factor: float = 1.5
    
    def calculate_regression(self) -> None:
        """Calculate regression factor and verdict."""
        if self.baseline_mean is None:
            self.verdict = "NO_BASELINE"
            return
            
        self.regression_factor = self.mean_time / self.baseline_mean
        
        # Determine verdict based on regression factor and tolerance
        if self.regression_factor <= (1.0 - 0.1):  # 10% improvement
            self.verdict = "✅ IMPROVED"
        elif self.regression_factor <= self.tolerance_factor:
            self.verdict = "✅ PASS"
        elif self.regression_factor <= (self.tolerance_factor * 1.5):
            self.verdict = "⚠️  DEGRADED"
        else:
            self.verdict = "❌ REGRESSED"

class PerformanceRegressionTester:
    """Main performance regression testing orchestrator."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize with configuration."""
        self.project_root = Path(__file__).parent.parent.parent
        self.config_path = config_path or self.project_root / "tests/performance/performance_baseline.json"
        self.config = self._load_config()
        self.results: List[PerformanceResult] = []
        
        # Ensure output directory exists
        self.output_dir = Path(self.config["reporting"]["export_directory"])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_config(self) -> Dict[str, Any]:
        """Load performance configuration."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Config file not found: {self.config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in config: {e}")
            sys.exit(1)
    
    def _check_hyperfine(self) -> bool:
        """Check if hyperfine is available."""
        try:
            subprocess.run(['hyperfine', '--version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ hyperfine not found. Install with: cargo install hyperfine")
            return False
    
    def _run_hyperfine_benchmark(self, command: str, baseline_config: Dict[str, Any]) -> Optional[PerformanceResult]:
        """Run hyperfine benchmark for a single command."""
        try:
            # Build hyperfine command
            warmup_runs = self.config["performance_thresholds"]["warmup_runs"]
            min_runs = self.config["performance_thresholds"]["measurement_runs"]
            max_runs = self.config["performance_thresholds"]["max_runs"]
            
            hyperfine_cmd = [
                'hyperfine',
                '--warmup', str(warmup_runs),
                '--min-runs', str(min_runs),
                '--max-runs', str(max_runs),
                '--export-json', '/tmp/hyperfine_result.json',
                '--show-output',
                command
            ]
            
            print(f"🔄 Running: {command}")
            
            # Run hyperfine
            result = subprocess.run(
                hyperfine_cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=baseline_config.get("timeout_seconds", 60)
            )
            
            if result.returncode != 0:
                print(f"❌ Command failed: {result.stderr}")
                return None
            
            # Parse hyperfine JSON output
            with open('/tmp/hyperfine_result.json', 'r') as f:
                hyperfine_data = json.load(f)
            
            if not hyperfine_data.get('results'):
                print(f"❌ No results from hyperfine")
                return None
                
            bench_result = hyperfine_data['results'][0]
            
            # Create performance result
            perf_result = PerformanceResult(
                command=command,
                mean_time=bench_result['mean'],
                std_dev=bench_result['stddev'],
                min_time=bench_result['min'],
                max_time=bench_result['max'],
                median_time=bench_result['median'],
                runs=len(bench_result['times']),
                baseline_mean=baseline_config.get("baseline_mean"),
                baseline_stddev=baseline_config.get("baseline_stddev"),
                tolerance_factor=baseline_config.get("tolerance_factor", 1.5)
            )
            
            perf_result.calculate_regression()
            return perf_result
            
        except subprocess.TimeoutExpired:
            print(f"⏰ Command timed out: {command}")
            return None
        except Exception as e:
            print(f"❌ Error running benchmark: {e}")
            return None
        finally:
            # Cleanup temp file
            if os.path.exists('/tmp/hyperfine_result.json'):
                os.remove('/tmp/hyperfine_result.json')
    
    def run_cli_benchmarks(self) -> List[PerformanceResult]:
        """Run CLI command benchmarks."""
        print("🚀 Running CLI Performance Benchmarks")
        print("=" * 50)
        
        cli_results = []
        cli_commands = self.config["performance_baselines"]["cli_commands"]
        
        for test_name, config in cli_commands.items():
            print(f"\n📊 Testing: {test_name}")
            result = self._run_hyperfine_benchmark(config["command"], config)
            if result:
                cli_results.append(result)
                self._print_result_summary(result)
        
        return cli_results
    
    def run_core_operation_benchmarks(self) -> List[PerformanceResult]:
        """Run core operation benchmarks."""
        print("\n🔧 Running Core Operation Benchmarks")
        print("=" * 50)
        
        core_results = []
        core_operations = self.config["performance_baselines"]["core_operations"]
        
        for test_name, config in core_operations.items():
            print(f"\n📊 Testing: {test_name}")
            result = self._run_hyperfine_benchmark(config["command"], config)
            if result:
                core_results.append(result)
                self._print_result_summary(result)
        
        return core_results
    
    def _print_result_summary(self, result: PerformanceResult) -> None:
        """Print a summary of a single result."""
        print(f"   Mean: {result.mean_time:.3f}s ± {result.std_dev:.3f}s")
        print(f"   Range: {result.min_time:.3f}s - {result.max_time:.3f}s")
        print(f"   Runs: {result.runs}")
        if result.baseline_mean:
            print(f"   Baseline: {result.baseline_mean:.3f}s")
            print(f"   Regression: {result.regression_factor:.2f}x")
        print(f"   Verdict: {result.verdict}")
    
    def run_all_benchmarks(self) -> None:
        """Run all performance benchmarks."""
        if not self._check_hyperfine():
            return
        
        print("🎯 IntelForge Performance Regression Testing")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💻 {platform.system()} {platform.release()}")
        print(f"🐍 Python {sys.version.split()[0]}")
        print()
        
        # Run CLI benchmarks
        cli_results = self.run_cli_benchmarks()
        self.results.extend(cli_results)
        
        # Run core operation benchmarks
        core_results = self.run_core_operation_benchmarks()
        self.results.extend(core_results)
        
        # Generate reports
        self._generate_reports()
        
        # Print summary
        self._print_final_summary()
    
    def _generate_reports(self) -> None:
        """Generate performance reports in multiple formats."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON report
        json_file = self.output_dir / f"performance_regression_{timestamp}.json"
        self._generate_json_report(json_file)
        
        # Markdown report
        md_file = self.output_dir / f"performance_regression_{timestamp}.md"
        self._generate_markdown_report(md_file)
        
        # CSV report
        csv_file = self.output_dir / f"performance_regression_{timestamp}.csv"
        self._generate_csv_report(csv_file)
        
        print(f"\n📊 Reports generated:")
        print(f"   JSON: {json_file}")
        print(f"   Markdown: {md_file}")
        print(f"   CSV: {csv_file}")
    
    def _generate_json_report(self, output_file: Path) -> None:
        """Generate JSON performance report."""
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "platform": platform.system(),
                "release": platform.release(),
                "python_version": sys.version.split()[0],
                "machine": platform.machine()
            },
            "config": self.config,
            "results": [asdict(result) for result in self.results],
            "summary": self._calculate_summary_stats()
        }
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
    
    def _generate_markdown_report(self, output_file: Path) -> None:
        """Generate Markdown performance report."""
        content = [
            "# Performance Regression Test Report",
            f"",
            f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Platform**: {platform.system()} {platform.release()}",
            f"**Python**: {sys.version.split()[0]}",
            f"",
            "## Summary",
            ""
        ]
        
        summary = self._calculate_summary_stats()
        content.extend([
            f"- **Total Tests**: {summary['total_tests']}",
            f"- **Passed**: {summary['passed']} ✅",
            f"- **Improved**: {summary['improved']} 🚀",
            f"- **Degraded**: {summary['degraded']} ⚠️",
            f"- **Regressed**: {summary['regressed']} ❌",
            f"- **No Baseline**: {summary['no_baseline']}",
            "",
            "## Detailed Results",
            "",
            "| Test | Mean Time | Std Dev | Baseline | Regression | Verdict |",
            "|------|-----------|---------|----------|------------|---------|"
        ])
        
        for result in self.results:
            baseline_str = f"{result.baseline_mean:.3f}s" if result.baseline_mean else "N/A"
            regression_str = f"{result.regression_factor:.2f}x" if result.regression_factor else "N/A"
            
            content.append(
                f"| {result.command[:40]}... | {result.mean_time:.3f}s | "
                f"{result.std_dev:.3f}s | {baseline_str} | {regression_str} | {result.verdict} |"
            )
        
        with open(output_file, 'w') as f:
            f.write('\n'.join(content))
    
    def _generate_csv_report(self, output_file: Path) -> None:
        """Generate CSV performance report."""
        import csv
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Command', 'Mean_Time', 'Std_Dev', 'Min_Time', 'Max_Time', 
                'Median_Time', 'Runs', 'Baseline_Mean', 'Regression_Factor', 'Verdict'
            ])
            
            for result in self.results:
                writer.writerow([
                    result.command,
                    result.mean_time,
                    result.std_dev,
                    result.min_time,
                    result.max_time,
                    result.median_time,
                    result.runs,
                    result.baseline_mean or '',
                    result.regression_factor or '',
                    result.verdict
                ])
    
    def _calculate_summary_stats(self) -> Dict[str, int]:
        """Calculate summary statistics."""
        summary = {
            'total_tests': len(self.results),
            'passed': 0,
            'improved': 0,
            'degraded': 0,
            'regressed': 0,
            'no_baseline': 0
        }
        
        for result in self.results:
            if "IMPROVED" in result.verdict:
                summary['improved'] += 1
            elif "PASS" in result.verdict:
                summary['passed'] += 1
            elif "DEGRADED" in result.verdict:
                summary['degraded'] += 1
            elif "REGRESSED" in result.verdict:
                summary['regressed'] += 1
            elif "NO_BASELINE" in result.verdict:
                summary['no_baseline'] += 1
        
        return summary
    
    def _print_final_summary(self) -> None:
        """Print final test summary."""
        summary = self._calculate_summary_stats()
        
        print("\n🎯 Performance Testing Summary")
        print("=" * 40)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"🚀 Improved: {summary['improved']}")
        print(f"⚠️  Degraded: {summary['degraded']}")
        print(f"❌ Regressed: {summary['regressed']}")
        print(f"📊 No Baseline: {summary['no_baseline']}")
        
        # Overall verdict
        if summary['regressed'] > 0:
            print(f"\n❌ OVERALL: REGRESSION DETECTED")
            sys.exit(1)
        elif summary['degraded'] > 0:
            print(f"\n⚠️  OVERALL: PERFORMANCE DEGRADATION")
            sys.exit(1)
        else:
            print(f"\n✅ OVERALL: PERFORMANCE ACCEPTABLE")


def main():
    """Main entry point for performance regression testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="IntelForge Performance Regression Testing")
    parser.add_argument('--config', help="Path to performance configuration file")
    parser.add_argument('--cli-only', action='store_true', help="Run only CLI benchmarks")
    parser.add_argument('--core-only', action='store_true', help="Run only core operation benchmarks")
    
    args = parser.parse_args()
    
    tester = PerformanceRegressionTester(args.config)
    
    if args.cli_only:
        results = tester.run_cli_benchmarks()
        tester.results = results
        tester._generate_reports()
        tester._print_final_summary()
    elif args.core_only:
        results = tester.run_core_operation_benchmarks()
        tester.results = results
        tester._generate_reports()
        tester._print_final_summary()
    else:
        tester.run_all_benchmarks()


if __name__ == "__main__":
    main()