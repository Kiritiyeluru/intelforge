#!/usr/bin/env python3
"""
IntelForge Production Readiness Checker
Part of Part 3C: CI & Production Polish implementation

Comprehensive production readiness assessment with scoring and recommendations.
"""

import json
import os
import sys
import subprocess
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import tempfile


@dataclass
class ReadinessCheck:
    """Individual readiness check result."""
    name: str
    status: str  # "pass", "fail", "warning", "skip"
    score: int  # 0-100
    message: str
    details: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None


@dataclass
class ReadinessReport:
    """Complete production readiness report."""
    timestamp: str
    overall_score: int
    overall_status: str
    checks: List[ReadinessCheck]
    recommendations: List[str]
    deployment_ready: bool
    summary: Dict[str, Any]


class ProductionReadinessChecker:
    """Main production readiness assessment engine."""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.checks: List[ReadinessCheck] = []
        self.start_time = time.time()
        
        # Scoring weights
        self.weights = {
            "critical": 25,
            "security": 20,
            "testing": 20,
            "performance": 15,
            "documentation": 10,
            "infrastructure": 10
        }
        
        # Thresholds
        self.thresholds = {
            "deployment_ready": 85,
            "production_ready": 90,
            "enterprise_ready": 95
        }
    
    def run_command(self, command: List[str], timeout: int = 30, capture_output: bool = True) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr."""
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", f"Command timed out after {timeout}s"
        except Exception as e:
            return 1, "", str(e)
    
    def check_critical_files(self) -> ReadinessCheck:
        """Check presence and validity of critical project files."""
        critical_files = [
            "requirements.txt",
            "scripts/cli.py",
            "tolerance_config.json",
            "pytest.ini",
            ".coveragerc"
        ]
        
        missing_files = []
        invalid_files = []
        
        for file_path in critical_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
            else:
                # Basic validation
                if file_path.endswith('.json'):
                    try:
                        with open(full_path) as f:
                            json.load(f)
                    except json.JSONDecodeError:
                        invalid_files.append(f"{file_path} (invalid JSON)")
        
        if not missing_files and not invalid_files:
            return ReadinessCheck(
                name="Critical Files",
                status="pass",
                score=100,
                message="All critical files present and valid"
            )
        else:
            score = max(0, 100 - (len(missing_files) * 20) - (len(invalid_files) * 15))
            recommendations = []
            if missing_files:
                recommendations.append(f"Create missing files: {', '.join(missing_files)}")
            if invalid_files:
                recommendations.append(f"Fix invalid files: {', '.join(invalid_files)}")
            
            return ReadinessCheck(
                name="Critical Files",
                status="fail" if score < 50 else "warning",
                score=score,
                message=f"Missing: {len(missing_files)}, Invalid: {len(invalid_files)}",
                details={"missing": missing_files, "invalid": invalid_files},
                recommendations=recommendations
            )
    
    def check_security_baseline(self) -> ReadinessCheck:
        """Check security baseline and vulnerability status."""
        # Check if security tests exist and pass
        security_test_file = self.project_root / "tests/security/test_security_baseline.py"
        if not security_test_file.exists():
            return ReadinessCheck(
                name="Security Baseline",
                status="fail",
                score=0,
                message="Security tests not found",
                recommendations=["Implement security baseline tests"]
            )
        
        # Run security tests
        exit_code, stdout, stderr = self.run_command([
            "python", "-m", "pytest", 
            "tests/security/test_security_baseline.py", 
            "-v", "--tb=short"
        ], timeout=60)
        
        if exit_code == 0:
            return ReadinessCheck(
                name="Security Baseline",
                status="pass",
                score=100,
                message="Security tests pass"
            )
        else:
            return ReadinessCheck(
                name="Security Baseline",
                status="fail",
                score=30,
                message="Security tests failed",
                details={"stdout": stdout, "stderr": stderr},
                recommendations=[
                    "Fix security test failures",
                    "Review security scanning results",
                    "Address identified vulnerabilities"
                ]
            )
    
    def check_test_coverage(self) -> ReadinessCheck:
        """Check test coverage and quality."""
        coverage_analyzer = self.project_root / "scripts/coverage_analyzer.py"
        if not coverage_analyzer.exists():
            return ReadinessCheck(
                name="Test Coverage",
                status="warning",
                score=50,
                message="Coverage analyzer not found",
                recommendations=["Implement coverage analysis tools"]
            )
        
        # Run coverage analysis
        exit_code, stdout, stderr = self.run_command([
            "python", str(coverage_analyzer), "--quick"
        ], timeout=120)
        
        if exit_code == 0:
            # Try to extract coverage percentage from output
            coverage_percent = 0
            coverage_file = self.project_root / "coverage.json"
            if coverage_file.exists():
                try:
                    with open(coverage_file) as f:
                        data = json.load(f)
                        coverage_percent = data.get("totals", {}).get("percent_covered", 0)
                except (json.JSONDecodeError, KeyError):
                    pass
            
            if coverage_percent >= 80:
                status = "pass"
                score = min(100, int(coverage_percent))
            elif coverage_percent >= 70:
                status = "warning"
                score = int(coverage_percent)
            else:
                status = "fail"
                score = max(30, int(coverage_percent))
            
            return ReadinessCheck(
                name="Test Coverage",
                status=status,
                score=score,
                message=f"Coverage: {coverage_percent:.1f}%",
                details={"coverage_percent": coverage_percent},
                recommendations=["Improve test coverage to 80%+"] if coverage_percent < 80 else []
            )
        else:
            return ReadinessCheck(
                name="Test Coverage",
                status="fail",
                score=20,
                message="Coverage analysis failed",
                recommendations=["Fix coverage analysis execution"]
            )
    
    def check_performance_benchmarks(self) -> ReadinessCheck:
        """Check performance benchmark status."""
        perf_test_file = self.project_root / "tests/performance/test_performance_regression.py"
        if not perf_test_file.exists():
            return ReadinessCheck(
                name="Performance Benchmarks",
                status="warning",
                score=60,
                message="Performance tests not found",
                recommendations=["Implement performance regression tests"]
            )
        
        # Check if hyperfine is available
        exit_code, _, _ = self.run_command(["which", "hyperfine"])
        if exit_code != 0:
            return ReadinessCheck(
                name="Performance Benchmarks",
                status="warning",
                score=40,
                message="hyperfine not available",
                recommendations=["Install hyperfine for performance testing"]
            )
        
        # Run quick performance test
        exit_code, stdout, stderr = self.run_command([
            "python", str(perf_test_file), "--cli-only"
        ], timeout=60)
        
        if exit_code == 0:
            return ReadinessCheck(
                name="Performance Benchmarks",
                status="pass",
                score=100,
                message="Performance tests pass"
            )
        else:
            return ReadinessCheck(
                name="Performance Benchmarks",
                status="fail",
                score=30,
                message="Performance tests failed",
                recommendations=["Address performance regressions"]
            )
    
    def check_cli_functionality(self) -> ReadinessCheck:
        """Check CLI functionality and health."""
        # Test basic CLI commands
        cli_commands = [
            (["python", "-m", "scripts.cli", "--help"], "CLI help"),
            (["python", "-m", "scripts.cli", "status", "--json"], "Status command"),
        ]
        
        failed_commands = []
        for command, description in cli_commands:
            exit_code, _, stderr = self.run_command(command, timeout=30)
            if exit_code != 0:
                failed_commands.append(description)
        
        if not failed_commands:
            return ReadinessCheck(
                name="CLI Functionality",
                status="pass",
                score=100,
                message="All CLI commands working"
            )
        else:
            score = max(20, 100 - (len(failed_commands) * 30))
            return ReadinessCheck(
                name="CLI Functionality",
                status="fail" if score < 50 else "warning",
                score=score,
                message=f"{len(failed_commands)} CLI commands failed",
                details={"failed_commands": failed_commands},
                recommendations=["Fix failing CLI commands"]
            )
    
    def check_documentation(self) -> ReadinessCheck:
        """Check documentation completeness."""
        required_docs = [
            "README.md",
            "CURRENT_IMPLEMENTATION_PLAN.md",
        ]
        
        missing_docs = []
        for doc in required_docs:
            if not (self.project_root / doc).exists():
                missing_docs.append(doc)
        
        # Check for session docs
        session_docs_dir = self.project_root / "session_docs"
        has_session_docs = session_docs_dir.exists() and any(session_docs_dir.iterdir())
        
        score = 100
        if missing_docs:
            score -= len(missing_docs) * 20
        if not has_session_docs:
            score -= 10
        
        if score >= 80:
            status = "pass"
        elif score >= 60:
            status = "warning"
        else:
            status = "fail"
        
        recommendations = []
        if missing_docs:
            recommendations.append(f"Create missing documentation: {', '.join(missing_docs)}")
        if not has_session_docs:
            recommendations.append("Add session documentation")
        
        return ReadinessCheck(
            name="Documentation",
            status=status,
            score=max(0, score),
            message=f"Missing: {len(missing_docs)} docs",
            recommendations=recommendations
        )
    
    def check_infrastructure_health(self) -> ReadinessCheck:
        """Check infrastructure and environment health."""
        health_checks = []
        
        # Check Python version
        exit_code, stdout, _ = self.run_command(["python", "--version"])
        if exit_code == 0 and "3." in stdout:
            health_checks.append(("Python 3.x", True))
        else:
            health_checks.append(("Python 3.x", False))
        
        # Check pip packages
        required_packages = ["pytest", "loguru", "rich", "typer"]
        for package in required_packages:
            exit_code, _, _ = self.run_command(["python", "-c", f"import {package}"])
            health_checks.append((f"Package: {package}", exit_code == 0))
        
        # Check directory structure
        required_dirs = ["scripts", "tests", "logs"]
        for directory in required_dirs:
            dir_path = self.project_root / directory
            health_checks.append((f"Directory: {directory}", dir_path.exists()))
        
        passed_checks = sum(1 for _, passed in health_checks if passed)
        total_checks = len(health_checks)
        score = int((passed_checks / total_checks) * 100)
        
        if score >= 90:
            status = "pass"
        elif score >= 70:
            status = "warning"
        else:
            status = "fail"
        
        failed_items = [name for name, passed in health_checks if not passed]
        recommendations = [f"Fix: {item}" for item in failed_items] if failed_items else []
        
        return ReadinessCheck(
            name="Infrastructure Health",
            status=status,
            score=score,
            message=f"{passed_checks}/{total_checks} checks passed",
            details={"checks": dict(health_checks)},
            recommendations=recommendations
        )
    
    def check_budget_status(self) -> ReadinessCheck:
        """Check project budget and time tracking status."""
        budget_tracker = self.project_root / "scripts/budget_tracker.py"
        budget_file = self.project_root / "tests/BUDGET_TRACKER.json"
        
        if not budget_tracker.exists():
            return ReadinessCheck(
                name="Budget Tracking",
                status="warning",
                score=70,
                message="Budget tracker not found",
                recommendations=["Implement budget tracking system"]
            )
        
        # Run budget check
        exit_code, stdout, stderr = self.run_command([
            "python", "-m", "scripts.cli", "budget-check"
        ], timeout=30)
        
        if exit_code == 0:
            # Parse budget status from output
            over_budget = "over budget" in stdout.lower() or "exceeded" in stdout.lower()
            
            if over_budget:
                return ReadinessCheck(
                    name="Budget Tracking",
                    status="warning",
                    score=60,
                    message="Project over budget",
                    recommendations=["Review budget allocation and scope"]
                )
            else:
                return ReadinessCheck(
                    name="Budget Tracking",
                    status="pass",
                    score=100,
                    message="Budget within limits"
                )
        else:
            return ReadinessCheck(
                name="Budget Tracking",
                status="fail",
                score=30,
                message="Budget check failed",
                recommendations=["Fix budget tracking system"]
            )
    
    def calculate_overall_score(self) -> Tuple[int, str]:
        """Calculate overall readiness score and status."""
        if not self.checks:
            return 0, "No checks performed"
        
        # Weight checks by category
        category_scores = {
            "critical": [],
            "security": [],
            "testing": [],
            "performance": [],
            "documentation": [],
            "infrastructure": []
        }
        
        # Categorize checks
        check_categories = {
            "Critical Files": "critical",
            "CLI Functionality": "critical",
            "Security Baseline": "security",
            "Test Coverage": "testing",
            "Performance Benchmarks": "performance",
            "Documentation": "documentation",
            "Infrastructure Health": "infrastructure",
            "Budget Tracking": "infrastructure"
        }
        
        for check in self.checks:
            category = check_categories.get(check.name, "infrastructure")
            category_scores[category].append(check.score)
        
        # Calculate weighted average
        total_weighted_score = 0
        total_weight = 0
        
        for category, weight in self.weights.items():
            scores = category_scores[category]
            if scores:
                avg_score = sum(scores) / len(scores)
                total_weighted_score += avg_score * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0, "No valid checks"
        
        overall_score = int(total_weighted_score / total_weight)
        
        # Determine status
        if overall_score >= self.thresholds["enterprise_ready"]:
            status = "Enterprise Ready"
        elif overall_score >= self.thresholds["production_ready"]:
            status = "Production Ready"
        elif overall_score >= self.thresholds["deployment_ready"]:
            status = "Deployment Ready"
        else:
            status = "Not Ready"
        
        return overall_score, status
    
    def generate_recommendations(self) -> List[str]:
        """Generate overall recommendations based on check results."""
        recommendations = []
        
        # Collect all check recommendations
        for check in self.checks:
            if check.recommendations:
                recommendations.extend(check.recommendations)
        
        # Add overall recommendations
        failed_checks = [c for c in self.checks if c.status == "fail"]
        warning_checks = [c for c in self.checks if c.status == "warning"]
        
        if failed_checks:
            recommendations.append(f"Address {len(failed_checks)} failing checks before deployment")
        
        if warning_checks:
            recommendations.append(f"Review {len(warning_checks)} warning checks for production optimization")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations
    
    def run_all_checks(self) -> ReadinessReport:
        """Run all production readiness checks."""
        print("🔍 Running production readiness checks...")
        
        # Define all checks
        check_methods = [
            self.check_critical_files,
            self.check_security_baseline,
            self.check_test_coverage,
            self.check_performance_benchmarks,
            self.check_cli_functionality,
            self.check_documentation,
            self.check_infrastructure_health,
            self.check_budget_status
        ]
        
        # Run each check
        for i, check_method in enumerate(check_methods, 1):
            print(f"  [{i}/{len(check_methods)}] {check_method.__name__.replace('check_', '').replace('_', ' ').title()}...")
            try:
                check_result = check_method()
                self.checks.append(check_result)
                
                # Status indicator
                status_icon = {
                    "pass": "✅",
                    "warning": "⚠️",
                    "fail": "❌",
                    "skip": "⏭️"
                }.get(check_result.status, "❓")
                
                print(f"    {status_icon} {check_result.message} (Score: {check_result.score})")
                
            except Exception as e:
                error_check = ReadinessCheck(
                    name=check_method.__name__.replace('check_', '').replace('_', ' ').title(),
                    status="fail",
                    score=0,
                    message=f"Check failed: {str(e)}",
                    recommendations=[f"Fix check execution error: {str(e)}"]
                )
                self.checks.append(error_check)
                print(f"    ❌ Check failed: {str(e)}")
        
        # Calculate overall results
        overall_score, overall_status = self.calculate_overall_score()
        recommendations = self.generate_recommendations()
        deployment_ready = overall_score >= self.thresholds["deployment_ready"]
        
        # Generate summary
        duration = time.time() - self.start_time
        pass_count = len([c for c in self.checks if c.status == "pass"])
        warning_count = len([c for c in self.checks if c.status == "warning"])
        fail_count = len([c for c in self.checks if c.status == "fail"])
        
        summary = {
            "total_checks": len(self.checks),
            "passed": pass_count,
            "warnings": warning_count,
            "failed": fail_count,
            "duration_seconds": round(duration, 2),
            "check_details": {check.name: check.score for check in self.checks}
        }
        
        return ReadinessReport(
            timestamp=datetime.now().isoformat(),
            overall_score=overall_score,
            overall_status=overall_status,
            checks=self.checks,
            recommendations=recommendations,
            deployment_ready=deployment_ready,
            summary=summary
        )
    
    def save_report(self, report: ReadinessReport, output_file: Optional[Path] = None) -> Path:
        """Save report to JSON file."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.project_root / "logs" / f"production_readiness_{timestamp}.json"
        
        # Ensure logs directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict for JSON serialization
        report_dict = asdict(report)
        
        with open(output_file, 'w') as f:
            json.dump(report_dict, f, indent=2)
        
        return output_file
    
    def print_summary(self, report: ReadinessReport):
        """Print human-readable summary."""
        print("\n" + "="*60)
        print("🚀 PRODUCTION READINESS ASSESSMENT")
        print("="*60)
        
        # Overall status
        status_icon = {
            "Enterprise Ready": "🏆",
            "Production Ready": "✅",
            "Deployment Ready": "🟡",
            "Not Ready": "❌"
        }.get(report.overall_status, "❓")
        
        print(f"\n{status_icon} Overall Status: {report.overall_status}")
        print(f"📊 Overall Score: {report.overall_score}/100")
        print(f"🚢 Deployment Ready: {'Yes' if report.deployment_ready else 'No'}")
        
        # Summary stats
        print(f"\n📈 Check Summary:")
        print(f"  • Total Checks: {report.summary['total_checks']}")
        print(f"  • Passed: {report.summary['passed']} ✅")
        print(f"  • Warnings: {report.summary['warnings']} ⚠️")
        print(f"  • Failed: {report.summary['failed']} ❌")
        print(f"  • Duration: {report.summary['duration_seconds']}s")
        
        # Key recommendations
        if report.recommendations:
            print(f"\n💡 Key Recommendations:")
            for i, rec in enumerate(report.recommendations[:5], 1):
                print(f"  {i}. {rec}")
            if len(report.recommendations) > 5:
                print(f"  ... and {len(report.recommendations) - 5} more")
        
        # Deployment verdict
        print(f"\n{'='*60}")
        if report.deployment_ready:
            print("🎉 READY FOR DEPLOYMENT!")
            print("All critical checks passed. System is production-ready.")
        else:
            print("⚠️  NOT READY FOR DEPLOYMENT")
            print("Critical issues found. Address recommendations before deploying.")
        print("="*60)


def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="IntelForge Production Readiness Checker")
    parser.add_argument("--output", "-o", type=Path, help="Output JSON file path")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    parser.add_argument("--json-only", action="store_true", help="Output JSON only")
    parser.add_argument("--summary-only", action="store_true", help="Show summary only")
    
    args = parser.parse_args()
    
    # Initialize checker
    checker = ProductionReadinessChecker(args.project_root)
    
    # Run assessment
    report = checker.run_all_checks()
    
    # Save report
    output_file = checker.save_report(report, args.output)
    
    if args.json_only:
        # Output JSON to stdout
        print(json.dumps(asdict(report), indent=2))
    else:
        # Print summary
        if not args.summary_only:
            checker.print_summary(report)
        
        print(f"\n📄 Detailed report saved: {output_file}")
    
    # Exit with appropriate code
    sys.exit(0 if report.deployment_ready else 1)


if __name__ == "__main__":
    main()