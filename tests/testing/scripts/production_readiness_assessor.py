#!/usr/bin/env python3
"""
IntelForge Production Readiness Assessment
Comprehensive evaluation of system readiness for production deployment
"""

import argparse
import datetime
import json
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Dict

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class ProductionReadinessAssessor:
    """Comprehensive production readiness assessment for IntelForge"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.test_dir = Path(__file__).parent.parent
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Assessment database
        self.assessment_db_path = (
            self.test_dir
            / "reports"
            / "production_readiness"
            / f"assessment_{self.timestamp}.db"
        )
        self.assessment_db_path.parent.mkdir(parents=True, exist_ok=True)

        # Results tracking
        self.assessment_results = {
            "session_id": self.timestamp,
            "assessment_type": "production_readiness",
            "start_time": datetime.datetime.now().isoformat(),
            "categories": {},
            "overall_score": 0,
            "readiness_level": "unknown",
            "recommendations": [],
            "blocking_issues": [],
            "status": "running",
        }

        # Assessment categories and weights
        self.assessment_categories = {
            "infrastructure": {
                "weight": 0.25,
                "description": "System infrastructure and dependencies",
            },
            "security": {
                "weight": 0.20,
                "description": "Security posture and vulnerability assessment",
            },
            "performance": {
                "weight": 0.20,
                "description": "Performance benchmarks and scalability",
            },
            "reliability": {
                "weight": 0.15,
                "description": "Error handling and fault tolerance",
            },
            "monitoring": {
                "weight": 0.10,
                "description": "Observability and monitoring capabilities",
            },
            "documentation": {
                "weight": 0.10,
                "description": "Documentation completeness and quality",
            },
        }

        # Initialize database
        self.init_assessment_database()

    def init_assessment_database(self):
        """Initialize SQLite database for assessment tracking"""
        conn = sqlite3.connect(self.assessment_db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS assessment_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                category TEXT NOT NULL,
                test_name TEXT NOT NULL,
                score REAL NOT NULL,
                max_score REAL NOT NULL,
                status TEXT NOT NULL,
                details TEXT,
                recommendations TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS readiness_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                threshold_value REAL NOT NULL,
                meets_threshold BOOLEAN NOT NULL,
                category TEXT NOT NULL
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS blocking_issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                issue_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT NOT NULL,
                resolution_required TEXT,
                category TEXT NOT NULL
            )
        """
        )

        conn.commit()
        conn.close()

    def record_assessment_result(
        self,
        category: str,
        test_name: str,
        score: float,
        max_score: float,
        status: str,
        details: str = "",
        recommendations: str = "",
    ):
        """Record assessment result in database"""
        conn = sqlite3.connect(self.assessment_db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO assessment_results
            (timestamp, category, test_name, score, max_score, status, details, recommendations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                datetime.datetime.now().isoformat(),
                category,
                test_name,
                score,
                max_score,
                status,
                details,
                recommendations,
            ),
        )

        conn.commit()
        conn.close()

    def record_blocking_issue(
        self,
        issue_type: str,
        severity: str,
        description: str,
        resolution: str,
        category: str,
    ):
        """Record blocking issue"""
        conn = sqlite3.connect(self.assessment_db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO blocking_issues
            (timestamp, issue_type, severity, description, resolution_required, category)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                datetime.datetime.now().isoformat(),
                issue_type,
                severity,
                description,
                resolution,
                category,
            ),
        )

        conn.commit()
        conn.close()

        # Add to results for immediate tracking
        self.assessment_results["blocking_issues"].append(
            {
                "type": issue_type,
                "severity": severity,
                "description": description,
                "resolution": resolution,
                "category": category,
            }
        )

    def assess_infrastructure_readiness(self) -> Dict:
        """Assess infrastructure and dependency readiness"""
        print("🏗️ Assessing infrastructure readiness...")

        infrastructure_score = 0
        max_infrastructure_score = 100

        # Check critical directories
        critical_dirs = [
            "scrapers",
            "scripts",
            "vault",
            "vault/notes",
            "vault/logs",
            "config",
            "session_docs",
        ]

        directory_score = 0
        len(critical_dirs) * 10

        for directory in critical_dirs:
            dir_path = self.project_root / directory
            if dir_path.exists() and dir_path.is_dir():
                directory_score += 10
                self.record_assessment_result(
                    "infrastructure",
                    f"directory_{directory}",
                    10,
                    10,
                    "pass",
                    f"Directory exists: {dir_path}",
                )
            else:
                self.record_blocking_issue(
                    "missing_directory",
                    "high",
                    f"Critical directory missing: {directory}",
                    "Create missing directory structure",
                    "infrastructure",
                )
                self.record_assessment_result(
                    "infrastructure",
                    f"directory_{directory}",
                    0,
                    10,
                    "fail",
                    f"Directory missing: {dir_path}",
                )

        infrastructure_score += directory_score

        # Check configuration files
        config_files = ["config/config.yaml", ".claude/settings.json"]

        config_score = 0
        len(config_files) * 10

        for config_file in config_files:
            config_path = self.project_root / config_file
            if config_path.exists():
                try:
                    if config_file.endswith(".json"):
                        with open(config_path, "r") as f:
                            json.load(f)
                    elif config_file.endswith(".yaml"):
                        import yaml

                        with open(config_path, "r") as f:
                            yaml.safe_load(f)

                    config_score += 10
                    self.record_assessment_result(
                        "infrastructure",
                        f"config_{config_file.replace('/', '_')}",
                        10,
                        10,
                        "pass",
                        f"Valid configuration: {config_path}",
                    )
                except Exception as e:
                    config_score += 5  # Partial credit for existence
                    self.record_assessment_result(
                        "infrastructure",
                        f"config_{config_file.replace('/', '_')}",
                        5,
                        10,
                        "partial",
                        f"Configuration exists but invalid: {e}",
                    )
            else:
                if "settings.json" not in config_file:  # Claude settings is optional
                    self.record_blocking_issue(
                        "missing_config",
                        "medium",
                        f"Configuration file missing: {config_file}",
                        "Create or restore configuration file",
                        "infrastructure",
                    )
                self.record_assessment_result(
                    "infrastructure",
                    f"config_{config_file.replace('/', '_')}",
                    0,
                    10,
                    "fail",
                    f"Configuration missing: {config_path}",
                )

        infrastructure_score += config_score

        # Check core modules
        core_modules = [
            "scrapers/reddit_scraper.py",
            "scrapers/github_scraper.py",
            "scrapers/web_scraper.py",
            "scripts/scraping_base.py",
            "scripts/phase_07_article_organizer.py",
            "scripts/phase_08_ai_processor.py",
        ]

        module_score = 0
        len(core_modules) * 5

        for module in core_modules:
            module_path = self.project_root / module
            if module_path.exists():
                try:
                    # Check syntax
                    with open(module_path, "r") as f:
                        code = f.read()
                    compile(code, str(module_path), "exec")

                    module_score += 5
                    self.record_assessment_result(
                        "infrastructure",
                        f"module_{module.replace('/', '_')}",
                        5,
                        5,
                        "pass",
                        f"Module syntax valid: {module_path}",
                    )
                except SyntaxError as e:
                    self.record_blocking_issue(
                        "syntax_error",
                        "high",
                        f"Syntax error in {module}: {e}",
                        "Fix syntax errors in core module",
                        "infrastructure",
                    )
                    self.record_assessment_result(
                        "infrastructure",
                        f"module_{module.replace('/', '_')}",
                        0,
                        5,
                        "fail",
                        f"Syntax error: {e}",
                    )
            else:
                self.record_blocking_issue(
                    "missing_module",
                    "high",
                    f"Core module missing: {module}",
                    "Restore or recreate missing core module",
                    "infrastructure",
                )
                self.record_assessment_result(
                    "infrastructure",
                    f"module_{module.replace('/', '_')}",
                    0,
                    5,
                    "fail",
                    f"Module missing: {module_path}",
                )

        infrastructure_score += module_score

        # Check Python environment
        python_score = 0

        try:
            # Check Python version
            if sys.version_info >= (3, 10):
                python_score += 10
                self.record_assessment_result(
                    "infrastructure",
                    "python_version",
                    10,
                    10,
                    "pass",
                    f"Python version {sys.version} is supported",
                )
            else:
                self.record_blocking_issue(
                    "python_version",
                    "high",
                    f"Python version {sys.version} is too old",
                    "Upgrade to Python 3.10 or higher",
                    "infrastructure",
                )
                self.record_assessment_result(
                    "infrastructure",
                    "python_version",
                    0,
                    10,
                    "fail",
                    f"Python version {sys.version} too old",
                )

            # Check critical packages
            critical_packages = ["sqlite3", "json", "datetime", "pathlib"]
            package_count = 0

            for package in critical_packages:
                try:
                    __import__(package)
                    package_count += 1
                except ImportError:
                    pass

            package_score = (package_count / len(critical_packages)) * 10
            python_score += package_score

            self.record_assessment_result(
                "infrastructure",
                "python_packages",
                package_score,
                10,
                "pass" if package_count == len(critical_packages) else "partial",
                f"{package_count}/{len(critical_packages)} critical packages available",
            )

        except Exception as e:
            self.record_assessment_result(
                "infrastructure",
                "python_environment",
                0,
                20,
                "error",
                f"Python environment check failed: {e}",
            )

        infrastructure_score += python_score

        # Normalize score
        infrastructure_percentage = (
            infrastructure_score / max_infrastructure_score
        ) * 100

        return {
            "score": infrastructure_percentage,
            "max_score": 100,
            "status": (
                "excellent"
                if infrastructure_percentage >= 90
                else "good" if infrastructure_percentage >= 75 else "needs_attention"
            ),
            "details": {
                "directory_score": directory_score,
                "config_score": config_score,
                "module_score": module_score,
                "python_score": python_score,
                "total_raw_score": infrastructure_score,
                "max_raw_score": max_infrastructure_score,
            },
        }

    def assess_security_readiness(self) -> Dict:
        """Assess security posture and vulnerabilities"""
        print("🔒 Assessing security readiness...")

        security_score = 0
        max_security_score = 100

        # Check for security tools installation and configuration (40 points)
        security_tools_score = 0
        max_tools_score = 40

        # Check for installed security tools
        security_tools = {
            "semgrep": "semgrep --version",
            "bandit": "bandit --version",
            "gitleaks": "gitleaks version",
            "trufflehog": "trufflehog --version",
            "osv-scanner": "osv-scanner --version",
            "safety": "safety --version",
            "checkov": "checkov --version",
        }

        tools_installed = 0
        for tool_name, version_cmd in security_tools.items():
            try:
                result = subprocess.run(
                    version_cmd.split(), capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    tools_installed += 1
                    self.record_assessment_result(
                        "security",
                        f"tool_{tool_name}",
                        5,
                        5,
                        "pass",
                        f"{tool_name} is installed and operational",
                    )
                else:
                    self.record_assessment_result(
                        "security",
                        f"tool_{tool_name}",
                        0,
                        5,
                        "missing",
                        f"{tool_name} is not installed or not working",
                    )
            except Exception as e:
                self.record_assessment_result(
                    "security",
                    f"tool_{tool_name}",
                    0,
                    5,
                    "error",
                    f"Cannot check {tool_name}: {e}",
                )

        # Score based on tools installed (7 tools total, ~5.7 points each)
        security_tools_score = (tools_installed / len(security_tools)) * max_tools_score
        security_score += security_tools_score

        # Check for security configuration files (20 points)
        config_score = 0
        max_config_score = 20

        security_configs = [
            ".pre-commit-config.yaml",
            ".gitleaks.toml",
            ".bandit",
            "scripts/security_scan.sh",
        ]

        configs_found = 0
        for config_file in security_configs:
            config_path = self.project_root / config_file
            if config_path.exists():
                configs_found += 1
                self.record_assessment_result(
                    "security",
                    f"config_{config_file.replace('.', '_').replace('/', '_')}",
                    5,
                    5,
                    "pass",
                    f"Security configuration exists: {config_file}",
                )
            else:
                self.record_assessment_result(
                    "security",
                    f"config_{config_file.replace('.', '_').replace('/', '_')}",
                    0,
                    5,
                    "missing",
                    f"Security configuration missing: {config_file}",
                )

        config_score = (configs_found / len(security_configs)) * max_config_score
        security_score += config_score

        # Check for security reports (20 points)
        reports_score = 0
        max_reports_score = 20

        reports_dir = self.project_root / "reports"
        if reports_dir.exists():
            # Look for security scan reports
            security_reports = (
                list(reports_dir.glob("**/semgrep.*"))
                + list(reports_dir.glob("**/bandit.*"))
                + list(reports_dir.glob("**/gitleaks.*"))
                + list(reports_dir.glob("**/osv.*"))
            )

            if security_reports:
                reports_score = max_reports_score
                self.record_assessment_result(
                    "security",
                    "security_reports",
                    max_reports_score,
                    max_reports_score,
                    "pass",
                    f"Security reports found: {len(security_reports)} files",
                )
            else:
                self.record_assessment_result(
                    "security",
                    "security_reports",
                    0,
                    max_reports_score,
                    "missing",
                    "No security scan reports found",
                )
        else:
            self.record_assessment_result(
                "security",
                "security_reports",
                0,
                max_reports_score,
                "missing",
                "Reports directory not found",
            )

        security_score += reports_score

        # Check for sensitive data exposure (10 points)
        exposure_score = 0
        max_exposure_score = 10

        sensitive_patterns = ["password", "secret", "api_key", "token", "private_key"]

        # Check configuration files for hardcoded secrets
        config_files = list(self.project_root.glob("**/*.json")) + list(
            self.project_root.glob("**/*.yaml")
        )

        # Exclude false positive directories and files
        exclude_dirs = [
            "profiles",
            "target",
            "node_modules",
            ".venv",
            "venv",
            "__pycache__",
            "Cache",
            "cache",
            ".cache",
            "build",
            "dist",
            ".git",
            "mcp_servers",
            "vault",  # Contains legitimate scraped data with tokens
            "reports",  # Contains security reports with example secrets
        ]

        exposure_issues = 0
        for config_file in config_files:
            # Skip hidden files, test files, and excluded directories
            if (
                config_file.name.startswith(".")
                or "test" in str(config_file)
                or any(exclude_dir in str(config_file) for exclude_dir in exclude_dirs)
            ):
                continue

            try:
                with open(config_file, "r") as f:
                    content = f.read().lower()

                for pattern in sensitive_patterns:
                    if pattern in content:
                        # Enhanced secret detection with improved pattern matching
                        # Supports base64, JWT tokens, and various formats (JSON, YAML, env)
                        import re

                        # Enhanced regex pattern for better secret detection
                        enhanced_pattern = rf'["\']?{pattern}["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_\-/+=%]{{10,}}["\']?'

                        if re.search(enhanced_pattern, content):
                            # Enhanced exclusion filters
                            exclusion_patterns = [
                                rf"\${{\s*{pattern.upper()}",  # ${API_KEY}
                                rf"\$\{{\s*{pattern}",  # ${api_key}
                                rf"env\.{pattern}",  # env.API_KEY
                                rf"process\.env\.{pattern}",  # process.env.API_KEY
                                rf"{pattern}.*here",  # placeholder patterns like "your_token_here"
                                rf"{pattern}.*placeholder",  # placeholder patterns
                                rf"{pattern}.*example",  # example patterns
                                rf"{pattern}.*todo",  # TODO patterns
                                rf"{pattern}.*replace",  # replace patterns
                            ]

                            # Check if any exclusion pattern matches
                            is_excluded = any(
                                re.search(excl_pattern, content, re.IGNORECASE)
                                for excl_pattern in exclusion_patterns
                            )

                            if not is_excluded:
                                exposure_issues += 1
                                self.record_blocking_issue(
                                    "hardcoded_secrets",
                                    "critical",
                                    f"Potential hardcoded secret in {config_file}",
                                    "Move secrets to environment variables or secure vault",
                                    "security",
                                )
                                break

            except Exception:
                pass

        # Score inversely based on exposure issues
        if exposure_issues == 0:
            exposure_score = max_exposure_score
        else:
            exposure_score = max(0, max_exposure_score - (exposure_issues * 3))

        security_score += exposure_score
        self.record_assessment_result(
            "security",
            "secret_exposure_check",
            exposure_score,
            max_exposure_score,
            "pass" if exposure_issues == 0 else "fail",
            f"Hardcoded secret issues found: {exposure_issues}",
        )

        # Check file permissions (10 points)
        permission_score = 0
        max_permission_score = 10

        sensitive_files = ["config/config.yaml", ".claude/settings.json"]

        permission_issues = 0
        for file_path in sensitive_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    # Check if file is world-readable (basic check)
                    stat_info = full_path.stat()
                    if stat_info.st_mode & 0o044:  # World or group readable
                        permission_issues += 1
                        self.record_assessment_result(
                            "security",
                            f"permissions_{file_path.replace('/', '_')}",
                            0,
                            5,
                            "warning",
                            f"File may be too permissive: {full_path}",
                        )
                    else:
                        self.record_assessment_result(
                            "security",
                            f"permissions_{file_path.replace('/', '_')}",
                            5,
                            5,
                            "pass",
                            f"File permissions acceptable: {full_path}",
                        )
                except Exception as e:
                    permission_issues += 1
                    self.record_assessment_result(
                        "security",
                        f"permissions_{file_path.replace('/', '_')}",
                        0,
                        5,
                        "error",
                        f"Cannot check permissions: {e}",
                    )

        permission_score = max(0, max_permission_score - (permission_issues * 5))
        security_score += permission_score

        # Normalize score
        security_percentage = (security_score / max_security_score) * 100

        return {
            "score": security_percentage,
            "max_score": 100,
            "status": (
                "excellent"
                if security_percentage >= 90
                else "good" if security_percentage >= 75 else "needs_attention"
            ),
            "details": {
                "security_tools_score": security_tools_score,
                "tools_installed": tools_installed,
                "config_score": config_score,
                "configs_found": configs_found,
                "reports_score": reports_score,
                "exposure_score": exposure_score,
                "exposure_issues": exposure_issues,
                "permission_score": permission_score,
                "permission_issues": permission_issues,
            },
        }

    def assess_performance_readiness(self) -> Dict:
        """Assess performance and scalability readiness"""
        print("⚡ Assessing performance readiness...")

        performance_score = 0
        max_performance_score = 100

        # Check if performance baseline exists
        baseline_file = self.test_dir / "config" / "performance_baseline.json"
        baseline_score = 0

        if baseline_file.exists():
            try:
                with open(baseline_file, "r") as f:
                    baseline_data = json.load(f)

                if baseline_data:
                    baseline_score = 25
                    self.record_assessment_result(
                        "performance",
                        "baseline_metrics",
                        25,
                        25,
                        "pass",
                        f"Performance baseline established with {len(baseline_data)} metrics",
                    )
                else:
                    baseline_score = 10
                    self.record_assessment_result(
                        "performance",
                        "baseline_metrics",
                        10,
                        25,
                        "partial",
                        "Performance baseline file exists but is empty",
                    )

            except Exception as e:
                self.record_assessment_result(
                    "performance",
                    "baseline_metrics",
                    0,
                    25,
                    "error",
                    f"Cannot read performance baseline: {e}",
                )
        else:
            self.record_assessment_result(
                "performance",
                "baseline_metrics",
                0,
                25,
                "missing",
                "No performance baseline established",
            )
            self.assessment_results["recommendations"].append(
                "Establish performance baselines by running performance regression tests"
            )

        performance_score += baseline_score

        # Check recent performance test results
        performance_reports = list(
            (self.test_dir / "reports" / "performance_regression").glob(
                "performance_report_*.md"
            )
        )
        recent_performance_score = 0

        if performance_reports:
            # Check most recent report
            latest_report = max(performance_reports, key=lambda p: p.stat().st_mtime)

            try:
                with open(latest_report, "r") as f:
                    content = f.read()

                if "✅ HEALTHY" in content:
                    recent_performance_score = 25
                    self.record_assessment_result(
                        "performance",
                        "recent_test_results",
                        25,
                        25,
                        "pass",
                        "Recent performance tests show healthy status",
                    )
                elif "⚠️" in content:
                    recent_performance_score = 15
                    self.record_assessment_result(
                        "performance",
                        "recent_test_results",
                        15,
                        25,
                        "warning",
                        "Recent performance tests show warnings",
                    )
                else:
                    recent_performance_score = 5
                    self.record_assessment_result(
                        "performance",
                        "recent_test_results",
                        5,
                        25,
                        "poor",
                        "Recent performance tests show issues",
                    )

            except Exception as e:
                self.record_assessment_result(
                    "performance",
                    "recent_test_results",
                    0,
                    25,
                    "error",
                    f"Cannot read performance report: {e}",
                )
        else:
            self.record_assessment_result(
                "performance",
                "recent_test_results",
                0,
                25,
                "missing",
                "No recent performance test results found",
            )
            self.assessment_results["recommendations"].append(
                "Run performance regression tests to establish current performance status"
            )

        performance_score += recent_performance_score

        # Check integration test results
        integration_reports = list(
            (self.test_dir / "reports" / "integration_tests").glob(
                "integration_report_*.md"
            )
        )
        integration_score = 0

        if integration_reports:
            latest_integration = max(
                integration_reports, key=lambda p: p.stat().st_mtime
            )

            try:
                with open(latest_integration, "r") as f:
                    content = f.read()

                # Extract success rate
                if "Success Rate" in content:
                    import re

                    match = re.search(r"Success Rate.*?(\d+\.?\d*)%", content)
                    if match:
                        success_rate = float(match.group(1))
                        integration_score = (success_rate / 100) * 25

                        status = (
                            "excellent"
                            if success_rate >= 95
                            else "good" if success_rate >= 85 else "needs_attention"
                        )
                        self.record_assessment_result(
                            "performance",
                            "integration_success_rate",
                            integration_score,
                            25,
                            status,
                            f"Integration test success rate: {success_rate}%",
                        )

            except Exception as e:
                self.record_assessment_result(
                    "performance",
                    "integration_success_rate",
                    0,
                    25,
                    "error",
                    f"Cannot analyze integration results: {e}",
                )
        else:
            self.record_assessment_result(
                "performance",
                "integration_success_rate",
                0,
                25,
                "missing",
                "No integration test results found",
            )

        performance_score += integration_score

        # Check end-to-end test results
        e2e_reports = list(
            (self.test_dir / "reports" / "end_to_end").glob("e2e_report_*.md")
        )
        e2e_score = 0

        if e2e_reports:
            latest_e2e = max(e2e_reports, key=lambda p: p.stat().st_mtime)

            try:
                with open(latest_e2e, "r") as f:
                    content = f.read()

                if "✅ EXCELLENT" in content:
                    e2e_score = 25
                    self.record_assessment_result(
                        "performance",
                        "e2e_test_results",
                        25,
                        25,
                        "excellent",
                        "End-to-end tests show excellent performance",
                    )
                elif "✅ GOOD" in content:
                    e2e_score = 20
                    self.record_assessment_result(
                        "performance",
                        "e2e_test_results",
                        20,
                        25,
                        "good",
                        "End-to-end tests show good performance",
                    )
                elif "⚠️" in content:
                    e2e_score = 10
                    self.record_assessment_result(
                        "performance",
                        "e2e_test_results",
                        10,
                        25,
                        "warning",
                        "End-to-end tests show performance warnings",
                    )
                else:
                    e2e_score = 5
                    self.record_assessment_result(
                        "performance",
                        "e2e_test_results",
                        5,
                        25,
                        "poor",
                        "End-to-end tests show performance issues",
                    )

            except Exception as e:
                self.record_assessment_result(
                    "performance",
                    "e2e_test_results",
                    0,
                    25,
                    "error",
                    f"Cannot analyze e2e results: {e}",
                )
        else:
            self.record_assessment_result(
                "performance",
                "e2e_test_results",
                0,
                25,
                "missing",
                "No end-to-end test results found",
            )

        performance_score += e2e_score

        # Normalize score
        performance_percentage = (performance_score / max_performance_score) * 100

        return {
            "score": performance_percentage,
            "max_score": 100,
            "status": (
                "excellent"
                if performance_percentage >= 90
                else "good" if performance_percentage >= 75 else "needs_attention"
            ),
            "details": {
                "baseline_score": baseline_score,
                "recent_performance_score": recent_performance_score,
                "integration_score": integration_score,
                "e2e_score": e2e_score,
            },
        }

    def assess_reliability_readiness(self) -> Dict:
        """Assess error handling and fault tolerance readiness"""
        print("🔧 Assessing reliability readiness...")

        reliability_score = 0
        max_reliability_score = 100

        # Check error handling in core modules
        error_handling_score = 0

        core_modules = [
            "scripts/scraping_base.py",
            "scrapers/reddit_scraper.py",
            "scrapers/github_scraper.py",
            "scripts/phase_08_ai_processor.py",
        ]

        for module in core_modules:
            module_path = self.project_root / module
            if module_path.exists():
                try:
                    with open(module_path, "r") as f:
                        content = f.read()

                    # Count error handling patterns
                    error_patterns = ["try:", "except", "catch", "finally:", "raise"]
                    pattern_count = sum(
                        content.count(pattern) for pattern in error_patterns
                    )

                    # Score based on error handling density
                    lines = content.count("\n")
                    if lines > 0:
                        error_density = pattern_count / lines
                        module_score = min(
                            12.5, error_density * 1000
                        )  # Max 12.5 points per module
                        error_handling_score += module_score

                        status = (
                            "excellent"
                            if error_density >= 0.02
                            else (
                                "good" if error_density >= 0.01 else "needs_improvement"
                            )
                        )
                        self.record_assessment_result(
                            "reliability",
                            f"error_handling_{module.replace('/', '_')}",
                            module_score,
                            12.5,
                            status,
                            f"Error handling density: {error_density:.3f}",
                        )

                except Exception as e:
                    self.record_assessment_result(
                        "reliability",
                        f"error_handling_{module.replace('/', '_')}",
                        0,
                        12.5,
                        "error",
                        f"Cannot analyze module: {e}",
                    )
            else:
                self.record_assessment_result(
                    "reliability",
                    f"error_handling_{module.replace('/', '_')}",
                    0,
                    12.5,
                    "missing",
                    f"Module not found: {module}",
                )

        reliability_score += error_handling_score

        # Check logging implementation
        logging_score = 0
        max_logging_score = 25

        code_files = list(self.project_root.glob("**/*.py"))
        logging_modules = 0

        for code_file in code_files:
            if "test" in str(code_file) or "__pycache__" in str(code_file):
                continue

            try:
                with open(code_file, "r") as f:
                    content = f.read()

                if any(
                    pattern in content
                    for pattern in ["import logging", "logger", "log."]
                ):
                    logging_modules += 1

            except Exception:
                pass

        if logging_modules > 0:
            logging_score = min(max_logging_score, logging_modules * 5)

        self.record_assessment_result(
            "reliability",
            "logging_implementation",
            logging_score,
            max_logging_score,
            (
                "good"
                if logging_modules >= 3
                else "partial" if logging_modules > 0 else "missing"
            ),
            f"Modules with logging: {logging_modules}",
        )

        reliability_score += logging_score

        # Check fault tolerance features
        fault_tolerance_score = 0
        max_fault_tolerance_score = 25

        # Look for retry mechanisms, timeouts, circuit breakers
        fault_tolerance_patterns = [
            "retry",
            "timeout",
            "circuit",
            "fallback",
            "backoff",
        ]
        fault_tolerance_found = 0

        for code_file in code_files:
            if "test" in str(code_file) or "__pycache__" in str(code_file):
                continue

            try:
                with open(code_file, "r") as f:
                    content = f.read().lower()

                for pattern in fault_tolerance_patterns:
                    if pattern in content:
                        fault_tolerance_found += 1
                        break

            except Exception:
                pass

        fault_tolerance_score = min(
            max_fault_tolerance_score, fault_tolerance_found * 3
        )

        self.record_assessment_result(
            "reliability",
            "fault_tolerance",
            fault_tolerance_score,
            max_fault_tolerance_score,
            (
                "excellent"
                if fault_tolerance_found >= 5
                else "good" if fault_tolerance_found >= 3 else "needs_improvement"
            ),
            f"Fault tolerance patterns found: {fault_tolerance_found}",
        )

        reliability_score += fault_tolerance_score

        # Normalize score
        reliability_percentage = (reliability_score / max_reliability_score) * 100

        return {
            "score": reliability_percentage,
            "max_score": 100,
            "status": (
                "excellent"
                if reliability_percentage >= 90
                else "good" if reliability_percentage >= 75 else "needs_attention"
            ),
            "details": {
                "error_handling_score": error_handling_score,
                "logging_score": logging_score,
                "fault_tolerance_score": fault_tolerance_score,
                "logging_modules": logging_modules,
                "fault_tolerance_patterns": fault_tolerance_found,
            },
        }

    def assess_monitoring_readiness(self) -> Dict:
        """Assess monitoring and observability readiness"""
        print("📊 Assessing monitoring readiness...")

        monitoring_score = 0
        max_monitoring_score = 100

        # Check for logging directories and files
        log_infrastructure_score = 0

        vault_logs = self.project_root / "vault" / "logs"
        if vault_logs.exists() and vault_logs.is_dir():
            log_files = list(vault_logs.glob("*.log")) + list(vault_logs.glob("*.txt"))
            if log_files:
                log_infrastructure_score = 30
                self.record_assessment_result(
                    "monitoring",
                    "log_infrastructure",
                    30,
                    30,
                    "pass",
                    f"Log directory exists with {len(log_files)} log files",
                )
            else:
                log_infrastructure_score = 15
                self.record_assessment_result(
                    "monitoring",
                    "log_infrastructure",
                    15,
                    30,
                    "partial",
                    "Log directory exists but no log files found",
                )
        else:
            self.record_assessment_result(
                "monitoring",
                "log_infrastructure",
                0,
                30,
                "missing",
                "Log directory structure not found",
            )

        monitoring_score += log_infrastructure_score

        # Check for metrics and reporting
        reports_score = 0

        reports_dir = self.test_dir / "reports"
        if reports_dir.exists():
            report_types = [d for d in reports_dir.iterdir() if d.is_dir()]
            reports_score = min(40, len(report_types) * 10)

            self.record_assessment_result(
                "monitoring",
                "reporting_infrastructure",
                reports_score,
                40,
                (
                    "excellent"
                    if len(report_types) >= 4
                    else "good" if len(report_types) >= 2 else "basic"
                ),
                f"Report categories available: {len(report_types)}",
            )
        else:
            self.record_assessment_result(
                "monitoring",
                "reporting_infrastructure",
                0,
                40,
                "missing",
                "No reporting infrastructure found",
            )

        monitoring_score += reports_score

        # Check for dashboard/visualization capabilities
        dashboard_score = 0

        # Look for visualization libraries in requirements or code
        viz_patterns = ["matplotlib", "plotly", "streamlit", "dash", "bokeh"]
        viz_found = 0

        code_files = list(self.project_root.glob("**/*.py"))
        for code_file in code_files:
            try:
                with open(code_file, "r") as f:
                    content = f.read()

                for pattern in viz_patterns:
                    if pattern in content:
                        viz_found += 1
                        break

            except Exception:
                pass

        dashboard_score = min(30, viz_found * 10)

        self.record_assessment_result(
            "monitoring",
            "dashboard_capabilities",
            dashboard_score,
            30,
            "excellent" if viz_found >= 3 else "good" if viz_found >= 1 else "missing",
            f"Visualization capabilities found: {viz_found}",
        )

        monitoring_score += dashboard_score

        # Normalize score
        monitoring_percentage = (monitoring_score / max_monitoring_score) * 100

        return {
            "score": monitoring_percentage,
            "max_score": 100,
            "status": (
                "excellent"
                if monitoring_percentage >= 90
                else "good" if monitoring_percentage >= 75 else "needs_attention"
            ),
            "details": {
                "log_infrastructure_score": log_infrastructure_score,
                "reports_score": reports_score,
                "dashboard_score": dashboard_score,
                "visualization_libraries": viz_found,
            },
        }

    def assess_documentation_readiness(self) -> Dict:
        """Assess documentation completeness and quality"""
        print("📚 Assessing documentation readiness...")

        documentation_score = 0
        max_documentation_score = 100

        # Check for essential documentation files
        essential_docs = ["README.md", "CLAUDE.md", "session_docs/PROJECT_STATUS.md"]

        essential_docs_score = 0

        for doc_file in essential_docs:
            doc_path = self.project_root / doc_file
            if doc_path.exists():
                try:
                    with open(doc_path, "r") as f:
                        content = f.read()

                    if len(content) > 500:  # Substantial content
                        essential_docs_score += 13.33
                        self.record_assessment_result(
                            "documentation",
                            f"essential_{doc_file.replace('/', '_')}",
                            13.33,
                            13.33,
                            "pass",
                            f"Documentation file exists with substantial content: {len(content)} chars",
                        )
                    else:
                        essential_docs_score += 6.67
                        self.record_assessment_result(
                            "documentation",
                            f"essential_{doc_file.replace('/', '_')}",
                            6.67,
                            13.33,
                            "partial",
                            f"Documentation file exists but minimal content: {len(content)} chars",
                        )

                except Exception as e:
                    self.record_assessment_result(
                        "documentation",
                        f"essential_{doc_file.replace('/', '_')}",
                        0,
                        13.33,
                        "error",
                        f"Cannot read documentation: {e}",
                    )
            else:
                if "README.md" in doc_file:
                    self.record_blocking_issue(
                        "missing_readme",
                        "medium",
                        "README.md file is missing",
                        "Create comprehensive README with project overview and setup instructions",
                        "documentation",
                    )

                self.record_assessment_result(
                    "documentation",
                    f"essential_{doc_file.replace('/', '_')}",
                    0,
                    13.33,
                    "missing",
                    f"Essential documentation missing: {doc_file}",
                )

        documentation_score += essential_docs_score

        # Check for session documentation
        session_docs_score = 0
        max_session_score = 30

        session_docs_dir = self.project_root / "session_docs"
        if session_docs_dir.exists():
            session_files = list(session_docs_dir.glob("*.md"))
            session_score = min(max_session_score, len(session_files) * 5)
            session_docs_score = session_score

            self.record_assessment_result(
                "documentation",
                "session_documentation",
                session_score,
                max_session_score,
                (
                    "excellent"
                    if len(session_files) >= 6
                    else "good" if len(session_files) >= 3 else "basic"
                ),
                f"Session documentation files: {len(session_files)}",
            )
        else:
            self.record_assessment_result(
                "documentation",
                "session_documentation",
                0,
                max_session_score,
                "missing",
                "Session documentation directory not found",
            )

        documentation_score += session_docs_score

        # Check for technical documentation
        technical_docs_score = 0
        max_technical_score = 30

        guidance_dir = self.project_root / "guidance"
        cline_docs_dir = self.project_root / "cline_docs"

        tech_doc_count = 0

        if guidance_dir.exists():
            tech_doc_count += len(list(guidance_dir.glob("**/*.md")))

        if cline_docs_dir.exists():
            tech_doc_count += len(list(cline_docs_dir.glob("**/*.md")))

        technical_docs_score = min(max_technical_score, tech_doc_count * 2)

        self.record_assessment_result(
            "documentation",
            "technical_documentation",
            technical_docs_score,
            max_technical_score,
            (
                "excellent"
                if tech_doc_count >= 15
                else "good" if tech_doc_count >= 8 else "basic"
            ),
            f"Technical documentation files: {tech_doc_count}",
        )

        documentation_score += technical_docs_score

        # Normalize score
        documentation_percentage = (documentation_score / max_documentation_score) * 100

        return {
            "score": documentation_percentage,
            "max_score": 100,
            "status": (
                "excellent"
                if documentation_percentage >= 90
                else "good" if documentation_percentage >= 75 else "needs_attention"
            ),
            "details": {
                "essential_docs_score": essential_docs_score,
                "session_docs_score": session_docs_score,
                "technical_docs_score": technical_docs_score,
                "technical_doc_count": tech_doc_count,
            },
        }

    def calculate_overall_readiness(self) -> Dict:
        """Calculate overall production readiness score"""
        print("🎯 Calculating overall production readiness...")

        overall_score = 0

        for category, results in self.assessment_results["categories"].items():
            weight = self.assessment_categories[category]["weight"]
            category_score = results["score"]
            weighted_score = category_score * weight
            overall_score += weighted_score

        # Determine readiness level
        if overall_score >= 90:
            readiness_level = "production_ready"
        elif overall_score >= 80:
            readiness_level = "near_production_ready"
        elif overall_score >= 70:
            readiness_level = "development_complete"
        elif overall_score >= 60:
            readiness_level = "needs_improvement"
        else:
            readiness_level = "not_ready"

        self.assessment_results["overall_score"] = overall_score
        self.assessment_results["readiness_level"] = readiness_level

        # Add general recommendations based on score
        if overall_score < 90:
            self.assessment_results["recommendations"].append(
                "Complete all assessment categories to achieve production readiness"
            )

        if len(self.assessment_results["blocking_issues"]) > 0:
            self.assessment_results["recommendations"].append(
                "Resolve all blocking issues before production deployment"
            )

        return {
            "overall_score": overall_score,
            "readiness_level": readiness_level,
            "blocking_issues_count": len(self.assessment_results["blocking_issues"]),
            "recommendations_count": len(self.assessment_results["recommendations"]),
        }

    def generate_readiness_report(self) -> str:
        """Generate comprehensive production readiness report"""
        self.assessment_results["end_time"] = datetime.datetime.now().isoformat()
        self.assessment_results["status"] = "completed"

        # Save detailed report
        report_path = (
            self.test_dir
            / "reports"
            / "production_readiness"
            / f"readiness_report_{self.timestamp}.json"
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(self.assessment_results, f, indent=2)

        # Generate markdown report
        md_report_path = (
            self.test_dir
            / "reports"
            / "production_readiness"
            / f"readiness_report_{self.timestamp}.md"
        )
        self.create_readiness_markdown_report(md_report_path)

        return str(md_report_path)

    def create_readiness_markdown_report(self, path: Path):
        """Create comprehensive production readiness markdown report"""
        overall = self.assessment_results

        # Map readiness levels to display
        readiness_display = {
            "production_ready": "🚀 PRODUCTION READY",
            "near_production_ready": "✅ NEAR PRODUCTION READY",
            "development_complete": "⚠️ DEVELOPMENT COMPLETE",
            "needs_improvement": "🔧 NEEDS IMPROVEMENT",
            "not_ready": "❌ NOT READY",
        }

        content = f"""# IntelForge Production Readiness Assessment

**Assessment ID**: {overall["session_id"]}
**Assessment Date**: {overall["start_time"]}
**Report Type**: Comprehensive Production Readiness Evaluation

## 📊 Executive Summary

**Overall Readiness**: {readiness_display.get(overall["readiness_level"], overall["readiness_level"])}
**Readiness Score**: {overall["overall_score"]:.1f}/100
**Blocking Issues**: {len(overall["blocking_issues"])}
**Recommendations**: {len(overall["recommendations"])}

## 🎯 Readiness Assessment Overview

| Category | Score | Weight | Weighted Score | Status |
|----------|-------|--------|----------------|--------|
"""

        # Add category results
        for category, results in overall["categories"].items():
            weight = self.assessment_categories[category]["weight"]
            weighted_score = results["score"] * weight
            status_emoji = (
                "✅"
                if results["score"] >= 90
                else "⚠️" if results["score"] >= 75 else "❌"
            )

            content += f"| **{category.replace('_', ' ').title()}** | {results['score']:.1f} | {weight:.0%} | {weighted_score:.1f} | {status_emoji} {results['status']} |\n"

        content += """

### Readiness Breakdown
- **Infrastructure**: System dependencies and core modules
- **Security**: Vulnerability assessment and secret management
- **Performance**: Benchmarks and scalability validation
- **Reliability**: Error handling and fault tolerance
- **Monitoring**: Observability and reporting capabilities
- **Documentation**: Completeness and quality assessment

## 🔍 Detailed Category Analysis

"""

        # Add detailed analysis for each category
        for category, results in overall["categories"].items():
            content += f"### {category.replace('_', ' ').title()}\n\n"
            content += f"**Score**: {results['score']:.1f}/100  \n"
            content += f"**Status**: {results['status'].replace('_', ' ').title()}  \n"
            content += f"**Description**: {self.assessment_categories[category]['description']}  \n"

            if "details" in results:
                content += "\n**Key Metrics**:\n"
                for metric, value in results["details"].items():
                    if isinstance(value, (int, float)):
                        content += (
                            f"- **{metric.replace('_', ' ').title()}**: {value:.1f}\n"
                        )
                    else:
                        content += (
                            f"- **{metric.replace('_', ' ').title()}**: {value}\n"
                        )

            content += "\n"

        # Add blocking issues
        if overall["blocking_issues"]:
            content += "## ❌ Blocking Issues\n\n"
            content += "**Critical issues that must be resolved before production deployment:**\n\n"

            for issue in overall["blocking_issues"]:
                severity_emoji = (
                    "🔴"
                    if issue["severity"] == "critical"
                    else "🟡" if issue["severity"] == "high" else "🟠"
                )
                content += f"### {severity_emoji} {issue['type'].replace('_', ' ').title()}\n\n"
                content += f"**Severity**: {issue['severity'].title()}  \n"
                content += f"**Category**: {issue['category'].title()}  \n"
                content += f"**Description**: {issue['description']}  \n"
                content += f"**Resolution Required**: {issue['resolution']}  \n\n"

        # Add recommendations
        if overall["recommendations"]:
            content += "## 📋 Recommendations\n\n"
            for i, recommendation in enumerate(overall["recommendations"], 1):
                content += f"{i}. {recommendation}\n"
            content += "\n"

        # Add readiness assessment
        content += "## 🎯 Production Readiness Assessment\n\n"

        if overall["readiness_level"] == "production_ready":
            content += """### ✅ Ready for Production
- All critical systems validated and operational
- Security posture meets production standards
- Performance benchmarks established and acceptable
- Comprehensive monitoring and documentation in place
- No blocking issues identified

**Next Steps**: Deploy to production environment with confidence
"""
        elif overall["readiness_level"] == "near_production_ready":
            content += """### ⚠️ Near Production Ready
- Core systems operational with minor improvements needed
- Most critical requirements met
- Some optimization opportunities identified
- Limited blocking issues require attention

**Next Steps**: Address remaining issues and optimize before deployment
"""
        elif overall["readiness_level"] == "development_complete":
            content += """### 🔧 Development Complete, Production Preparation Needed
- Core development work finished
- Significant production preparation required
- Multiple areas need improvement for production readiness
- Infrastructure and operational concerns need addressing

**Next Steps**: Focus on production hardening and operational readiness
"""
        elif overall["readiness_level"] == "needs_improvement":
            content += """### ❌ Needs Significant Improvement
- Core functionality present but not production-ready
- Multiple critical areas require attention
- Blocking issues must be resolved
- Substantial work needed before production consideration

**Next Steps**: Address critical issues and improve system reliability
"""
        else:
            content += """### ❌ Not Ready for Production
- Fundamental issues prevent production deployment
- Critical systems missing or non-functional
- Major security, performance, or reliability concerns
- Extensive development and testing required

**Next Steps**: Complete core development and address fundamental issues
"""

        content += f"""

## 🔗 Technical Details

**Assessment Database**: `{self.assessment_db_path}`
**Report Location**: `{path}`
**Assessment Framework**: Comprehensive production readiness evaluation

**Categories Assessed**: {len(overall["categories"])}
**Total Metrics Evaluated**: {sum(len(r.get("details", {})) for r in overall["categories"].values())}
**Assessment Duration**: {(datetime.datetime.fromisoformat(overall["end_time"]) - datetime.datetime.fromisoformat(overall["start_time"])).total_seconds():.1f} seconds

---
*Generated by IntelForge Production Readiness Assessor*
*Framework: Multi-category production readiness evaluation with weighted scoring*
"""

        with open(path, "w") as f:
            f.write(content)


def main():
    parser = argparse.ArgumentParser(
        description="IntelForge Production Readiness Assessor"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--category",
        choices=[
            "infrastructure",
            "security",
            "performance",
            "reliability",
            "monitoring",
            "documentation",
        ],
        help="Assess specific category only",
    )

    args = parser.parse_args()

    print("🚀 Starting IntelForge Production Readiness Assessment")
    print("🎯 Comprehensive evaluation across 6 critical categories")
    print("📊 Weighted scoring with blocking issue identification")

    assessor = ProductionReadinessAssessor()

    # Run assessments
    categories_to_assess = (
        [args.category]
        if args.category
        else list(assessor.assessment_categories.keys())
    )

    for category in categories_to_assess:
        print(f"\n{'=' * 80}")

        if category == "infrastructure":
            assessor.assessment_results["categories"][
                category
            ] = assessor.assess_infrastructure_readiness()
        elif category == "security":
            assessor.assessment_results["categories"][
                category
            ] = assessor.assess_security_readiness()
        elif category == "performance":
            assessor.assessment_results["categories"][
                category
            ] = assessor.assess_performance_readiness()
        elif category == "reliability":
            assessor.assessment_results["categories"][
                category
            ] = assessor.assess_reliability_readiness()
        elif category == "monitoring":
            assessor.assessment_results["categories"][
                category
            ] = assessor.assess_monitoring_readiness()
        elif category == "documentation":
            assessor.assessment_results["categories"][
                category
            ] = assessor.assess_documentation_readiness()

    # Calculate overall readiness
    print(f"\n{'=' * 80}")
    overall_results = assessor.calculate_overall_readiness()

    # Generate comprehensive report
    print(f"\n{'=' * 80}")
    print("📊 Generating production readiness assessment report...")
    report_path = assessor.generate_readiness_report()

    # Final summary
    print("\n🎉 Production readiness assessment complete!")
    print(f"🎯 **Overall Score**: {overall_results['overall_score']:.1f}/100")
    print(
        f"🚀 **Readiness Level**: {overall_results['readiness_level'].replace('_', ' ').title()}"
    )
    print(f"❌ **Blocking Issues**: {overall_results['blocking_issues_count']}")
    print(f"📋 **Recommendations**: {overall_results['recommendations_count']}")
    print(f"📁 **Report**: {report_path}")
    print(f"🗄️ **Database**: {assessor.assessment_db_path}")


if __name__ == "__main__":
    main()
