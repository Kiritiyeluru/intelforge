#!/usr/bin/env python3
"""
IntelForge Fail-Fast Validation System
Provides comprehensive pre-flight checks for CLI commands to catch silent failures early.
"""

import importlib.util
import json
import socket
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
import yaml

try:
    from .claude_integrity_validator import (ClaudeIntegrityValidator,
                                             validate_claude_output_cli)

    CLAUDE_VALIDATOR_AVAILABLE = True
except ImportError:
    CLAUDE_VALIDATOR_AVAILABLE = False

try:
    from .vector_health_validator import (VectorHealthValidator,
                                          quick_vector_health_check)

    VECTOR_VALIDATOR_AVAILABLE = True
except ImportError:
    VECTOR_VALIDATOR_AVAILABLE = False


class ValidationLevel(Enum):
    """Validation severity levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ValidationResult(Enum):
    """Validation result status"""

    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIP = "skip"


@dataclass
class ValidationCheck:
    """Individual validation check result"""

    name: str
    level: ValidationLevel
    result: ValidationResult
    message: str
    details: Optional[Dict[str, Any]] = None
    fix_suggestion: Optional[str] = None


class FailFastValidator:
    """
    Comprehensive fail-fast validation system for IntelForge CLI commands.
    Detects silent failures, malformed outputs, and system inconsistencies.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.checks: List[ValidationCheck] = []

    def validate_system_health(self) -> List[ValidationCheck]:
        """Run comprehensive system health validation"""
        self.checks = []

        # Critical system checks
        self._check_python_environment()
        self._check_required_modules()
        self._check_storage_accessibility()
        self._check_system_resources()

        # Configuration validation
        self._check_config_files()
        self._check_yaml_integrity()

        # Claude/AI output integrity
        self._check_claude_output_integrity()

        # Vector store health
        self._check_vector_stores()
        self._check_embeddings_integrity()

        # Network and connectivity
        self._check_network_connectivity()

        return self.checks

    def validate_cli_readiness(self, command: str) -> List[ValidationCheck]:
        """Validate readiness for specific CLI command"""
        self.checks = []

        # Command-specific validations
        if command == "crawl":
            self._check_crawl_readiness()
        elif command == "validate":
            self._check_validation_readiness()
        elif command == "migrate":
            self._check_migration_readiness()
        elif command == "status":
            self._check_status_readiness()

        return self.checks

    def _check_python_environment(self):
        """Validate Python environment and version"""
        try:
            # Check Python version
            if sys.version_info < (3, 8):
                self.checks.append(
                    ValidationCheck(
                        name="python_version",
                        level=ValidationLevel.CRITICAL,
                        result=ValidationResult.FAIL,
                        message=f"Python {sys.version_info.major}.{sys.version_info.minor} is too old",
                        fix_suggestion="Upgrade to Python 3.8 or newer",
                    )
                )
            else:
                self.checks.append(
                    ValidationCheck(
                        name="python_version",
                        level=ValidationLevel.CRITICAL,
                        result=ValidationResult.PASS,
                        message=f"Python {sys.version_info.major}.{sys.version_info.minor} is compatible",
                    )
                )

            # Check virtual environment
            in_venv = hasattr(sys, "real_prefix") or (
                hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
            )
            if not in_venv:
                self.checks.append(
                    ValidationCheck(
                        name="virtual_environment",
                        level=ValidationLevel.HIGH,
                        result=ValidationResult.WARN,
                        message="Not running in virtual environment",
                        fix_suggestion="Use 'python -m venv venv && source venv/bin/activate'",
                    )
                )
            else:
                self.checks.append(
                    ValidationCheck(
                        name="virtual_environment",
                        level=ValidationLevel.HIGH,
                        result=ValidationResult.PASS,
                        message="Virtual environment active",
                    )
                )

        except Exception as e:
            self.checks.append(
                ValidationCheck(
                    name="python_environment",
                    level=ValidationLevel.CRITICAL,
                    result=ValidationResult.FAIL,
                    message=f"Python environment check failed: {e}",
                )
            )

    def _check_required_modules(self):
        """Check availability of required Python modules"""
        required_modules = [
            ("typer", ValidationLevel.CRITICAL),
            ("sentence_transformers", ValidationLevel.HIGH),
            ("chromadb", ValidationLevel.HIGH),
            ("qdrant_client", ValidationLevel.MEDIUM),
            ("trafilatura", ValidationLevel.HIGH),
            ("scrapy", ValidationLevel.MEDIUM),
            ("requests", ValidationLevel.HIGH),
            ("yaml", ValidationLevel.MEDIUM),
            ("psutil", ValidationLevel.MEDIUM),
        ]

        for module_name, level in required_modules:
            try:
                spec = importlib.util.find_spec(module_name)
                if spec is None:
                    self.checks.append(
                        ValidationCheck(
                            name=f"module_{module_name}",
                            level=level,
                            result=ValidationResult.FAIL,
                            message=f"Required module '{module_name}' not found",
                            fix_suggestion=f"pip install {module_name}",
                        )
                    )
                else:
                    self.checks.append(
                        ValidationCheck(
                            name=f"module_{module_name}",
                            level=level,
                            result=ValidationResult.PASS,
                            message=f"Module '{module_name}' available",
                        )
                    )
            except Exception as e:
                self.checks.append(
                    ValidationCheck(
                        name=f"module_{module_name}",
                        level=level,
                        result=ValidationResult.FAIL,
                        message=f"Error checking module '{module_name}': {e}",
                    )
                )

    def _check_storage_accessibility(self):
        """Check storage directories accessibility"""
        storage_dirs = {
            "qdrant_storage": ValidationLevel.MEDIUM,
            "chroma_storage": ValidationLevel.MEDIUM,
            "data": ValidationLevel.HIGH,
            "logs": ValidationLevel.MEDIUM,
        }

        for dir_name, level in storage_dirs.items():
            dir_path = self.project_root / dir_name
            try:
                if not dir_path.exists():
                    # Try to create directory
                    dir_path.mkdir(parents=True, exist_ok=True)
                    self.checks.append(
                        ValidationCheck(
                            name=f"storage_{dir_name}",
                            level=level,
                            result=ValidationResult.PASS,
                            message=f"Created storage directory: {dir_path}",
                        )
                    )
                else:
                    # Check write permissions
                    test_file = dir_path / ".write_test"
                    try:
                        test_file.touch()
                        test_file.unlink()
                        self.checks.append(
                            ValidationCheck(
                                name=f"storage_{dir_name}",
                                level=level,
                                result=ValidationResult.PASS,
                                message=f"Storage directory accessible: {dir_path}",
                            )
                        )
                    except PermissionError:
                        self.checks.append(
                            ValidationCheck(
                                name=f"storage_{dir_name}",
                                level=level,
                                result=ValidationResult.FAIL,
                                message=f"No write permission: {dir_path}",
                                fix_suggestion=f"chmod 755 {dir_path}",
                            )
                        )
            except Exception as e:
                self.checks.append(
                    ValidationCheck(
                        name=f"storage_{dir_name}",
                        level=level,
                        result=ValidationResult.FAIL,
                        message=f"Storage check failed for {dir_path}: {e}",
                    )
                )

    def _check_system_resources(self):
        """Check system resource availability"""
        try:
            # Memory check
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)

            if memory_gb < 2:
                self.checks.append(
                    ValidationCheck(
                        name="system_memory",
                        level=ValidationLevel.HIGH,
                        result=ValidationResult.WARN,
                        message=f"Low memory: {memory_gb:.1f}GB available",
                        fix_suggestion="Consider upgrading to at least 4GB RAM",
                    )
                )
            else:
                self.checks.append(
                    ValidationCheck(
                        name="system_memory",
                        level=ValidationLevel.HIGH,
                        result=ValidationResult.PASS,
                        message=f"Adequate memory: {memory_gb:.1f}GB available",
                    )
                )

            # Disk space check
            disk = psutil.disk_usage(str(self.project_root))
            free_gb = disk.free / (1024**3)

            if free_gb < 1:
                self.checks.append(
                    ValidationCheck(
                        name="disk_space",
                        level=ValidationLevel.HIGH,
                        result=ValidationResult.FAIL,
                        message=f"Low disk space: {free_gb:.1f}GB free",
                        fix_suggestion="Free up disk space before proceeding",
                    )
                )
            else:
                self.checks.append(
                    ValidationCheck(
                        name="disk_space",
                        level=ValidationLevel.HIGH,
                        result=ValidationResult.PASS,
                        message=f"Adequate disk space: {free_gb:.1f}GB free",
                    )
                )

        except Exception as e:
            self.checks.append(
                ValidationCheck(
                    name="system_resources",
                    level=ValidationLevel.MEDIUM,
                    result=ValidationResult.WARN,
                    message=f"Could not check system resources: {e}",
                )
            )

    def _check_config_files(self):
        """Check configuration file integrity"""
        config_files = [
            ("scripts/reference_embeddings.json", ValidationLevel.HIGH),
            ("CLAUDE.md", ValidationLevel.MEDIUM),
            ("CURRENT_IMPLEMENTATION_PLAN.md", ValidationLevel.MEDIUM),
        ]

        for file_path, level in config_files:
            full_path = self.project_root / file_path
            try:
                if not full_path.exists():
                    self.checks.append(
                        ValidationCheck(
                            name=f"config_{file_path.replace('/', '_')}",
                            level=level,
                            result=ValidationResult.WARN,
                            message=f"Config file not found: {file_path}",
                            fix_suggestion=f"Create or restore {file_path}",
                        )
                    )
                else:
                    # Check file size and readability
                    if full_path.stat().st_size == 0:
                        self.checks.append(
                            ValidationCheck(
                                name=f"config_{file_path.replace('/', '_')}",
                                level=level,
                                result=ValidationResult.FAIL,
                                message=f"Config file is empty: {file_path}",
                            )
                        )
                    else:
                        self.checks.append(
                            ValidationCheck(
                                name=f"config_{file_path.replace('/', '_')}",
                                level=level,
                                result=ValidationResult.PASS,
                                message=f"Config file valid: {file_path}",
                            )
                        )
            except Exception as e:
                self.checks.append(
                    ValidationCheck(
                        name=f"config_{file_path.replace('/', '_')}",
                        level=level,
                        result=ValidationResult.FAIL,
                        message=f"Config file check failed for {file_path}: {e}",
                    )
                )

    def _check_yaml_integrity(self):
        """Check YAML file integrity for malformed content"""
        yaml_files = list(self.project_root.rglob("*.yaml")) + list(
            self.project_root.rglob("*.yml")
        )

        for yaml_file in yaml_files[:10]:  # Limit to first 10 files
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    yaml.safe_load(f)
                self.checks.append(
                    ValidationCheck(
                        name=f"yaml_{yaml_file.name}",
                        level=ValidationLevel.MEDIUM,
                        result=ValidationResult.PASS,
                        message=f"YAML file valid: {yaml_file.name}",
                    )
                )
            except yaml.YAMLError as e:
                self.checks.append(
                    ValidationCheck(
                        name=f"yaml_{yaml_file.name}",
                        level=ValidationLevel.HIGH,
                        result=ValidationResult.FAIL,
                        message=f"YAML syntax error in {yaml_file.name}: {e}",
                        fix_suggestion=f"Fix YAML syntax in {yaml_file}",
                    )
                )
            except Exception as e:
                self.checks.append(
                    ValidationCheck(
                        name=f"yaml_{yaml_file.name}",
                        level=ValidationLevel.MEDIUM,
                        result=ValidationResult.WARN,
                        message=f"Could not check YAML file {yaml_file.name}: {e}",
                    )
                )

    def _check_claude_output_integrity(self):
        """Check Claude/AI output integrity in recent files"""
        if not CLAUDE_VALIDATOR_AVAILABLE:
            self.checks.append(
                ValidationCheck(
                    name="claude_validator_availability",
                    level=ValidationLevel.MEDIUM,
                    result=ValidationResult.SKIP,
                    message="Claude integrity validator not available",
                )
            )
            return

        # Look for recent output files that might contain Claude-generated content
        potential_claude_files = []

        # Check logs directory for recent outputs
        logs_dir = self.project_root / "logs"
        if logs_dir.exists():
            recent_logs = sorted(
                logs_dir.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True
            )[:5]
            potential_claude_files.extend(recent_logs)

        # Check data directory for recent files
        data_dir = self.project_root / "data"
        if data_dir.exists():
            recent_data = sorted(
                data_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True
            )[:3]
            potential_claude_files.extend(recent_data)

        # Check session docs for recent files
        session_docs = self.project_root / "session_docs"
        if session_docs.exists():
            recent_docs = sorted(
                session_docs.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True
            )[:3]
            potential_claude_files.extend(recent_docs)

        if not potential_claude_files:
            self.checks.append(
                ValidationCheck(
                    name="claude_output_files",
                    level=ValidationLevel.LOW,
                    result=ValidationResult.SKIP,
                    message="No recent output files found to validate",
                )
            )
            return

        try:
            claude_validator = ClaudeIntegrityValidator()
            total_files = 0
            failed_files = 0
            suspicious_files = 0

            for file_path in potential_claude_files[:10]:  # Limit to 10 files
                try:
                    integrity_checks = claude_validator.validate_file_output(file_path)
                    summary = claude_validator.get_integrity_summary(integrity_checks)

                    total_files += 1

                    if summary["status"] == "failed":
                        failed_files += 1
                    elif summary["status"] == "warning":
                        suspicious_files += 1

                except Exception:
                    # Skip files that can't be processed
                    continue

            if failed_files > 0:
                self.checks.append(
                    ValidationCheck(
                        name="claude_output_integrity",
                        level=ValidationLevel.HIGH,
                        result=ValidationResult.FAIL,
                        message=f"Found {failed_files}/{total_files} files with integrity issues",
                        details={
                            "failed_files": failed_files,
                            "total_files": total_files,
                        },
                        fix_suggestion="Review and regenerate corrupted output files",
                    )
                )
            elif suspicious_files > 0:
                self.checks.append(
                    ValidationCheck(
                        name="claude_output_integrity",
                        level=ValidationLevel.MEDIUM,
                        result=ValidationResult.WARN,
                        message=f"Found {suspicious_files}/{total_files} files with potential issues",
                        details={
                            "suspicious_files": suspicious_files,
                            "total_files": total_files,
                        },
                    )
                )
            else:
                self.checks.append(
                    ValidationCheck(
                        name="claude_output_integrity",
                        level=ValidationLevel.MEDIUM,
                        result=ValidationResult.PASS,
                        message=f"All {total_files} checked files passed integrity validation",
                    )
                )

        except Exception as e:
            self.checks.append(
                ValidationCheck(
                    name="claude_output_integrity",
                    level=ValidationLevel.MEDIUM,
                    result=ValidationResult.WARN,
                    message=f"Claude integrity check failed: {e}",
                )
            )

    def _check_vector_stores(self):
        """Check vector store health and accessibility using advanced validator"""
        if not VECTOR_VALIDATOR_AVAILABLE:
            # Fallback to basic checks
            self._check_vector_stores_basic()
            return

        try:
            vector_validator = VectorHealthValidator(self.project_root)

            # Run comprehensive vector health checks
            chromadb_checks = vector_validator.validate_chromadb_health()
            qdrant_checks = vector_validator.validate_qdrant_health()
            all_vector_checks = chromadb_checks + qdrant_checks

            # Convert vector health checks to validation checks
            critical_issues = 0
            warning_issues = 0

            for check in all_vector_checks:
                if check.status.value in ["critical", "unhealthy"]:
                    if check.level.value == "critical":
                        level = ValidationLevel.CRITICAL
                        result = ValidationResult.FAIL
                        critical_issues += 1
                    else:
                        level = ValidationLevel.HIGH
                        result = ValidationResult.FAIL
                        critical_issues += 1
                elif check.status.value == "degraded":
                    level = ValidationLevel.MEDIUM
                    result = ValidationResult.WARN
                    warning_issues += 1
                else:
                    level = ValidationLevel.MEDIUM
                    result = ValidationResult.PASS

            # Create summary validation check
            if critical_issues > 0:
                self.checks.append(
                    ValidationCheck(
                        name="vector_store_health",
                        level=ValidationLevel.HIGH,
                        result=ValidationResult.FAIL,
                        message=f"Vector store health issues: {critical_issues} critical, {warning_issues} warnings",
                        details={
                            "critical_issues": critical_issues,
                            "warning_issues": warning_issues,
                        },
                        fix_suggestion="Run 'python -m scripts.validation.vector_health_validator --verbose' for details",
                    )
                )
            elif warning_issues > 0:
                self.checks.append(
                    ValidationCheck(
                        name="vector_store_health",
                        level=ValidationLevel.MEDIUM,
                        result=ValidationResult.WARN,
                        message=f"Vector store health warnings: {warning_issues} issues found",
                        details={"warning_issues": warning_issues},
                    )
                )
            else:
                self.checks.append(
                    ValidationCheck(
                        name="vector_store_health",
                        level=ValidationLevel.MEDIUM,
                        result=ValidationResult.PASS,
                        message="Vector stores are healthy",
                    )
                )

        except Exception as e:
            self.checks.append(
                ValidationCheck(
                    name="vector_store_health",
                    level=ValidationLevel.MEDIUM,
                    result=ValidationResult.WARN,
                    message=f"Vector health check failed: {e}",
                )
            )

    def _check_vector_stores_basic(self):
        """Basic vector store checks (fallback when advanced validator unavailable)"""
        # ChromaDB check
        try:
            chroma_path = self.project_root / "chroma_storage"
            if chroma_path.exists():
                # Basic ChromaDB structure check
                db_files = list(chroma_path.rglob("*.sqlite*"))
                if db_files:
                    self.checks.append(
                        ValidationCheck(
                            name="chromadb_structure_basic",
                            level=ValidationLevel.HIGH,
                            result=ValidationResult.PASS,
                            message="ChromaDB storage structure valid",
                        )
                    )
                else:
                    self.checks.append(
                        ValidationCheck(
                            name="chromadb_structure_basic",
                            level=ValidationLevel.HIGH,
                            result=ValidationResult.WARN,
                            message="ChromaDB storage exists but appears empty",
                        )
                    )
            else:
                self.checks.append(
                    ValidationCheck(
                        name="chromadb_structure_basic",
                        level=ValidationLevel.MEDIUM,
                        result=ValidationResult.WARN,
                        message="ChromaDB storage directory not found",
                    )
                )
        except Exception as e:
            self.checks.append(
                ValidationCheck(
                    name="chromadb_structure_basic",
                    level=ValidationLevel.HIGH,
                    result=ValidationResult.FAIL,
                    message=f"ChromaDB check failed: {e}",
                )
            )

        # Qdrant check
        try:
            qdrant_path = self.project_root / "qdrant_storage"
            if qdrant_path.exists():
                collection_dirs = [d for d in qdrant_path.iterdir() if d.is_dir()]
                if collection_dirs:
                    self.checks.append(
                        ValidationCheck(
                            name="qdrant_structure_basic",
                            level=ValidationLevel.MEDIUM,
                            result=ValidationResult.PASS,
                            message=f"Qdrant storage has {len(collection_dirs)} collections",
                        )
                    )
                else:
                    self.checks.append(
                        ValidationCheck(
                            name="qdrant_structure_basic",
                            level=ValidationLevel.MEDIUM,
                            result=ValidationResult.WARN,
                            message="Qdrant storage exists but appears empty",
                        )
                    )
            else:
                self.checks.append(
                    ValidationCheck(
                        name="qdrant_structure_basic",
                        level=ValidationLevel.LOW,
                        result=ValidationResult.SKIP,
                        message="Qdrant storage directory not found (optional)",
                    )
                )
        except Exception as e:
            self.checks.append(
                ValidationCheck(
                    name="qdrant_structure_basic",
                    level=ValidationLevel.MEDIUM,
                    result=ValidationResult.WARN,
                    message=f"Qdrant check failed: {e}",
                )
            )

    def _check_embeddings_integrity(self):
        """Check embeddings file integrity and content validation"""
        embeddings_file = self.project_root / "scripts" / "reference_embeddings.json"

        try:
            if not embeddings_file.exists():
                self.checks.append(
                    ValidationCheck(
                        name="embeddings_file",
                        level=ValidationLevel.HIGH,
                        result=ValidationResult.WARN,
                        message="Reference embeddings file not found",
                        fix_suggestion="Run semantic crawler with --regenerate-reference",
                    )
                )
                return

            with open(embeddings_file, "r") as f:
                embeddings_data = json.load(f)

            # Check structure
            if not isinstance(embeddings_data, dict):
                self.checks.append(
                    ValidationCheck(
                        name="embeddings_structure",
                        level=ValidationLevel.HIGH,
                        result=ValidationResult.FAIL,
                        message="Reference embeddings file has invalid structure",
                    )
                )
                return

            # Check for empty embeddings
            empty_embeddings = 0
            total_embeddings = 0

            for key, value in embeddings_data.items():
                if isinstance(value, list):
                    total_embeddings += 1
                    if not value or all(x == 0 for x in value):
                        empty_embeddings += 1

            if empty_embeddings > 0:
                self.checks.append(
                    ValidationCheck(
                        name="embeddings_content",
                        level=ValidationLevel.HIGH,
                        result=ValidationResult.FAIL,
                        message=f"Found {empty_embeddings}/{total_embeddings} empty embeddings",
                        fix_suggestion="Regenerate reference embeddings",
                    )
                )
            else:
                self.checks.append(
                    ValidationCheck(
                        name="embeddings_content",
                        level=ValidationLevel.HIGH,
                        result=ValidationResult.PASS,
                        message=f"All {total_embeddings} embeddings valid",
                    )
                )

        except json.JSONDecodeError as e:
            self.checks.append(
                ValidationCheck(
                    name="embeddings_json",
                    level=ValidationLevel.HIGH,
                    result=ValidationResult.FAIL,
                    message=f"Reference embeddings file has invalid JSON: {e}",
                    fix_suggestion="Fix JSON syntax or regenerate file",
                )
            )
        except Exception as e:
            self.checks.append(
                ValidationCheck(
                    name="embeddings_check",
                    level=ValidationLevel.HIGH,
                    result=ValidationResult.FAIL,
                    message=f"Embeddings check failed: {e}",
                )
            )

    def _check_network_connectivity(self):
        """Check basic network connectivity for web scraping"""
        test_urls = [("google.com", 80), ("github.com", 443)]

        for host, port in test_urls:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((host, port))
                sock.close()

                if result == 0:
                    self.checks.append(
                        ValidationCheck(
                            name=f"network_{host}",
                            level=ValidationLevel.MEDIUM,
                            result=ValidationResult.PASS,
                            message=f"Network connectivity to {host} successful",
                        )
                    )
                else:
                    self.checks.append(
                        ValidationCheck(
                            name=f"network_{host}",
                            level=ValidationLevel.MEDIUM,
                            result=ValidationResult.WARN,
                            message=f"Cannot connect to {host}:{port}",
                            fix_suggestion="Check internet connection and firewall settings",
                        )
                    )
            except Exception as e:
                self.checks.append(
                    ValidationCheck(
                        name=f"network_{host}",
                        level=ValidationLevel.MEDIUM,
                        result=ValidationResult.WARN,
                        message=f"Network check failed for {host}: {e}",
                    )
                )

    def _check_crawl_readiness(self):
        """Command-specific validation for crawl command"""
        # Check scrapy and trafilatura availability
        try:
            import scrapy

            self.checks.append(
                ValidationCheck(
                    name="crawl_scrapy",
                    level=ValidationLevel.HIGH,
                    result=ValidationResult.PASS,
                    message="Scrapy available for crawling",
                )
            )
        except ImportError:
            self.checks.append(
                ValidationCheck(
                    name="crawl_scrapy",
                    level=ValidationLevel.HIGH,
                    result=ValidationResult.WARN,
                    message="Scrapy not available - fallback mode will be used",
                )
            )

        try:
            import trafilatura

            self.checks.append(
                ValidationCheck(
                    name="crawl_trafilatura",
                    level=ValidationLevel.HIGH,
                    result=ValidationResult.PASS,
                    message="Trafilatura available for content extraction",
                )
            )
        except ImportError:
            self.checks.append(
                ValidationCheck(
                    name="crawl_trafilatura",
                    level=ValidationLevel.CRITICAL,
                    result=ValidationResult.FAIL,
                    message="Trafilatura not available - crawling will fail",
                    fix_suggestion="pip install trafilatura",
                )
            )

    def _check_validation_readiness(self):
        """Command-specific validation for validate command"""
        canary_script = self.project_root / "scripts" / "canary_validation_system_v2.py"
        if not canary_script.exists():
            self.checks.append(
                ValidationCheck(
                    name="canary_validator",
                    level=ValidationLevel.CRITICAL,
                    result=ValidationResult.FAIL,
                    message="Canary validation script not found",
                    fix_suggestion="Ensure canary_validation_system_v2.py exists in scripts/",
                )
            )
        else:
            self.checks.append(
                ValidationCheck(
                    name="canary_validator",
                    level=ValidationLevel.CRITICAL,
                    result=ValidationResult.PASS,
                    message="Canary validator available",
                )
            )

    def _check_migration_readiness(self):
        """Command-specific validation for migrate command"""
        migration_script = self.project_root / "scripts" / "vector_storage_migration.py"
        if not migration_script.exists():
            self.checks.append(
                ValidationCheck(
                    name="migration_script",
                    level=ValidationLevel.CRITICAL,
                    result=ValidationResult.FAIL,
                    message="Migration script not found",
                    fix_suggestion="Ensure vector_storage_migration.py exists in scripts/",
                )
            )
        else:
            self.checks.append(
                ValidationCheck(
                    name="migration_script",
                    level=ValidationLevel.CRITICAL,
                    result=ValidationResult.PASS,
                    message="Migration script available",
                )
            )

    def _check_status_readiness(self):
        """Command-specific validation for status command"""
        # Status command should always work, but check CLI script exists
        cli_script = self.project_root / "scripts" / "cli.py"
        if not cli_script.exists():
            self.checks.append(
                ValidationCheck(
                    name="cli_script",
                    level=ValidationLevel.CRITICAL,
                    result=ValidationResult.FAIL,
                    message="CLI script not found",
                )
            )
        else:
            self.checks.append(
                ValidationCheck(
                    name="cli_script",
                    level=ValidationLevel.CRITICAL,
                    result=ValidationResult.PASS,
                    message="CLI script available",
                )
            )

    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary with pass/fail counts"""
        summary = {
            "total_checks": len(self.checks),
            "results": {"pass": 0, "fail": 0, "warn": 0, "skip": 0},
            "levels": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "overall_status": "unknown",
        }

        critical_failures = 0
        high_failures = 0

        for check in self.checks:
            summary["results"][check.result.value] += 1
            summary["levels"][check.level.value] += 1

            if check.result == ValidationResult.FAIL:
                if check.level == ValidationLevel.CRITICAL:
                    critical_failures += 1
                elif check.level == ValidationLevel.HIGH:
                    high_failures += 1

        # Determine overall status
        if critical_failures > 0:
            summary["overall_status"] = "critical_failure"
        elif high_failures > 0:
            summary["overall_status"] = "high_failure"
        elif summary["results"]["fail"] > 0:
            summary["overall_status"] = "failure"
        elif summary["results"]["warn"] > 0:
            summary["overall_status"] = "warning"
        else:
            summary["overall_status"] = "healthy"

        return summary


def cli_fail_fast_check(command: str = "general") -> bool:
    """
    Quick fail-fast check for CLI commands.
    Returns True if system is ready, False if critical issues found.
    """
    validator = FailFastValidator()

    # Run system health checks
    health_checks = validator.validate_system_health()

    # Run command-specific checks
    if command != "general":
        command_checks = validator.validate_cli_readiness(command)
        health_checks.extend(command_checks)

    # Check for critical failures
    critical_failures = [
        check
        for check in health_checks
        if check.level == ValidationLevel.CRITICAL
        and check.result == ValidationResult.FAIL
    ]

    return len(critical_failures) == 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="IntelForge Fail-Fast Validator")
    parser.add_argument("--command", default="general", help="Command to validate")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    validator = FailFastValidator()

    # Run validations
    health_checks = validator.validate_system_health()
    if args.command != "general":
        command_checks = validator.validate_cli_readiness(args.command)
        health_checks.extend(command_checks)

    validator.checks = health_checks
    summary = validator.get_summary()

    if args.json:
        # JSON output
        output = {
            "summary": summary,
            "checks": [
                {
                    "name": check.name,
                    "level": check.level.value,
                    "result": check.result.value,
                    "message": check.message,
                    "details": check.details,
                    "fix_suggestion": check.fix_suggestion,
                }
                for check in validator.checks
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        # Human-readable output
        print("🔧 IntelForge Fail-Fast Validation Report")
        print("=" * 50)
        print(f"Overall Status: {summary['overall_status'].upper()}")
        print(f"Total Checks: {summary['total_checks']}")
        print(f"✅ Pass: {summary['results']['pass']}")
        print(f"❌ Fail: {summary['results']['fail']}")
        print(f"⚠️  Warn: {summary['results']['warn']}")
        print(f"⏭️  Skip: {summary['results']['skip']}")

        if args.verbose:
            print("\n📋 Detailed Results:")
            for check in validator.checks:
                icon = {
                    ValidationResult.PASS: "✅",
                    ValidationResult.FAIL: "❌",
                    ValidationResult.WARN: "⚠️",
                    ValidationResult.SKIP: "⏭️",
                }[check.result]

                print(
                    f"{icon} [{check.level.value.upper()}] {check.name}: {check.message}"
                )
                if check.fix_suggestion and check.result in [
                    ValidationResult.FAIL,
                    ValidationResult.WARN,
                ]:
                    print(f"   💡 Fix: {check.fix_suggestion}")

        # Exit with error code if critical issues
        if summary["overall_status"] in ["critical_failure", "high_failure"]:
            sys.exit(1)
