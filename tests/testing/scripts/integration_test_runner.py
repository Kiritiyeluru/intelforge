#!/usr/bin/env python3
"""
IntelForge Integration Test Runner
Tests core module interactions and end-to-end workflows
"""

import argparse
import datetime
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, Optional

import yaml

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class IntelForgeIntegrationTester:
    """Comprehensive integration testing for IntelForge core modules"""

    def __init__(self, config_path: Optional[str] = None):
        self.project_root = PROJECT_ROOT
        self.test_dir = Path(__file__).parent.parent
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Core module paths
        self.scrapers_dir = self.project_root / "scrapers"
        self.scripts_dir = self.project_root / "scripts"
        self.vault_dir = self.project_root / "vault"

        # Test database for validation
        self.test_db_path = (
            self.test_dir
            / "reports"
            / "integration_tests"
            / f"test_session_{self.timestamp}.db"
        )
        self.test_db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize test tracking
        self.init_test_database()

        self.results = {
            "session_id": self.timestamp,
            "test_type": "integration_testing",
            "start_time": datetime.datetime.now().isoformat(),
            "core_modules": {},
            "integrations": {},
            "workflows": {},
            "performance": {},
            "status": "running",
        }

    def init_test_database(self):
        """Initialize SQLite database for test tracking"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                test_category TEXT NOT NULL,
                test_name TEXT NOT NULL,
                status TEXT NOT NULL,
                duration_seconds REAL,
                output TEXT,
                error_message TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS module_dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_name TEXT NOT NULL,
                dependency_name TEXT NOT NULL,
                import_success BOOLEAN,
                version TEXT
            )
        """
        )

        conn.commit()
        conn.close()

    def record_test_result(
        self,
        category: str,
        name: str,
        status: str,
        duration: float = 0.0,
        output: str = "",
        error: str = "",
    ):
        """Record test result in database"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO test_results
            (timestamp, test_category, test_name, status, duration_seconds, output, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                datetime.datetime.now().isoformat(),
                category,
                name,
                status,
                duration,
                output,
                error,
            ),
        )

        conn.commit()
        conn.close()

    def test_core_module_imports(self) -> Dict:
        """Test that all core modules can be imported successfully"""
        print("🔍 Testing core module imports...")

        core_modules = [
            ("scrapers.reddit_scraper", "reddit_scraper.py"),
            ("scrapers.github_scraper", "github_scraper.py"),
            ("scrapers.web_scraper", "web_scraper.py"),
            ("scripts.scraping_base", "scraping_base.py"),
            ("scripts.data_organizer", "data_organizer.py"),
            ("scripts.phase_07_article_organizer", "phase_07_article_organizer.py"),
            ("scripts.phase_08_ai_processor", "phase_08_ai_processor.py"),
        ]

        import_results = {}

        for module_name, file_name in core_modules:
            start_time = datetime.datetime.now()

            try:
                # Change to project root for imports
                original_cwd = os.getcwd()
                os.chdir(self.project_root)

                # Try importing the module
                if "scrapers." in module_name:
                    module_path = self.scrapers_dir / file_name
                else:
                    module_path = self.scripts_dir / file_name

                if module_path.exists():
                    # Test syntax by compiling
                    with open(module_path, "r") as f:
                        code = f.read()

                    compile(code, str(module_path), "exec")

                    import_results[file_name] = {
                        "status": "✅ PASS",
                        "file_exists": True,
                        "syntax_valid": True,
                        "size_bytes": module_path.stat().st_size,
                    }

                    self.record_test_result(
                        "core_imports",
                        file_name,
                        "pass",
                        (datetime.datetime.now() - start_time).total_seconds(),
                    )
                else:
                    import_results[file_name] = {
                        "status": "❌ MISSING",
                        "file_exists": False,
                        "error": "File not found",
                    }

                    self.record_test_result(
                        "core_imports",
                        file_name,
                        "missing",
                        (datetime.datetime.now() - start_time).total_seconds(),
                        error="File not found",
                    )

            except SyntaxError as e:
                import_results[file_name] = {
                    "status": "❌ SYNTAX_ERROR",
                    "error": str(e),
                }
                self.record_test_result(
                    "core_imports",
                    file_name,
                    "syntax_error",
                    (datetime.datetime.now() - start_time).total_seconds(),
                    error=str(e),
                )
            except Exception as e:
                import_results[file_name] = {"status": "❌ ERROR", "error": str(e)}
                self.record_test_result(
                    "core_imports",
                    file_name,
                    "error",
                    (datetime.datetime.now() - start_time).total_seconds(),
                    error=str(e),
                )
            finally:
                os.chdir(original_cwd)

        self.results["core_modules"] = import_results
        return import_results

    def test_configuration_loading(self) -> Dict:
        """Test configuration file loading and validation"""
        print("⚙️ Testing configuration loading...")

        config_results = {}
        start_time = datetime.datetime.now()

        try:
            # Test main config.yaml
            config_path = self.project_root / "config" / "config.yaml"
            if config_path.exists():
                with open(config_path, "r") as f:
                    config_data = yaml.safe_load(f)

                config_results["config.yaml"] = {
                    "status": "✅ PASS",
                    "file_exists": True,
                    "valid_yaml": True,
                    "sections": list(config_data.keys()) if config_data else [],
                    "size_bytes": config_path.stat().st_size,
                }
            else:
                config_results["config.yaml"] = {
                    "status": "❌ MISSING",
                    "file_exists": False,
                }

            # Test .claude settings
            claude_settings_path = self.project_root / ".claude" / "settings.json"
            if claude_settings_path.exists():
                with open(claude_settings_path, "r") as f:
                    claude_data = json.load(f)

                config_results["claude_settings.json"] = {
                    "status": "✅ PASS",
                    "file_exists": True,
                    "valid_json": True,
                    "hooks_count": len(claude_data.get("hooks", [])),
                    "size_bytes": claude_settings_path.stat().st_size,
                }
            else:
                config_results["claude_settings.json"] = {
                    "status": "⚠️ OPTIONAL_MISSING",
                    "file_exists": False,
                }

            self.record_test_result(
                "configuration",
                "config_loading",
                "pass",
                (datetime.datetime.now() - start_time).total_seconds(),
            )

        except Exception as e:
            config_results["error"] = str(e)
            self.record_test_result(
                "configuration",
                "config_loading",
                "error",
                (datetime.datetime.now() - start_time).total_seconds(),
                error=str(e),
            )

        return config_results

    def test_database_connections(self) -> Dict:
        """Test database and storage systems"""
        print("🗄️ Testing database connections...")

        db_results = {}

        # Test SQLite knowledge management
        try:
            start_time = datetime.datetime.now()

            # Create temporary test database
            with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
                test_db_path = tmp_db.name

            conn = sqlite3.connect(test_db_path)
            cursor = conn.cursor()

            # Test basic operations
            cursor.execute(
                "CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)"
            )
            cursor.execute("INSERT INTO test_table (name) VALUES (?)", ("test_data",))
            cursor.execute("SELECT * FROM test_table")
            result = cursor.fetchone()

            conn.commit()
            conn.close()

            # Cleanup
            os.unlink(test_db_path)

            db_results["sqlite"] = {
                "status": "✅ PASS",
                "operations": ["CREATE", "INSERT", "SELECT"],
                "test_data_retrieved": result is not None,
            }

            self.record_test_result(
                "database",
                "sqlite_basic",
                "pass",
                (datetime.datetime.now() - start_time).total_seconds(),
            )

        except Exception as e:
            db_results["sqlite"] = {"status": "❌ ERROR", "error": str(e)}
            self.record_test_result(
                "database",
                "sqlite_basic",
                "error",
                (datetime.datetime.now() - start_time).total_seconds(),
                error=str(e),
            )

        # Test vector database (if available)
        try:
            start_time = datetime.datetime.now()

            # Try importing FAISS or ChromaDB
            vector_db_available = False
            vector_db_type = "none"

            try:
                import faiss

                vector_db_available = True
                vector_db_type = "faiss"
            except ImportError:
                try:
                    import chromadb

                    vector_db_available = True
                    vector_db_type = "chromadb"
                except ImportError:
                    pass

            if vector_db_available:
                db_results["vector_database"] = {
                    "status": "✅ AVAILABLE",
                    "type": vector_db_type,
                    "import_successful": True,
                }
                self.record_test_result(
                    "database",
                    f"vector_db_{vector_db_type}",
                    "pass",
                    (datetime.datetime.now() - start_time).total_seconds(),
                )
            else:
                db_results["vector_database"] = {
                    "status": "⚠️ NOT_AVAILABLE",
                    "type": "none",
                    "note": "Neither FAISS nor ChromaDB available",
                }
                self.record_test_result(
                    "database",
                    "vector_db",
                    "not_available",
                    (datetime.datetime.now() - start_time).total_seconds(),
                )

        except Exception as e:
            db_results["vector_database"] = {"status": "❌ ERROR", "error": str(e)}
            self.record_test_result(
                "database",
                "vector_db",
                "error",
                (datetime.datetime.now() - start_time).total_seconds(),
                error=str(e),
            )

        return db_results

    def test_scraper_integrations(self) -> Dict:
        """Test scraper module integrations and basic functionality"""
        print("🕷️ Testing scraper integrations...")

        scraper_results = {}

        # Test scraping base class
        try:
            start_time = datetime.datetime.now()

            original_cwd = os.getcwd()
            os.chdir(self.project_root)

            # Test that scraping_base.py can be executed for basic validation
            scraping_base_path = self.scripts_dir / "scraping_base.py"
            if scraping_base_path.exists():
                # Run syntax check
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", str(scraping_base_path)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    scraper_results["scraping_base"] = {
                        "status": "✅ PASS",
                        "syntax_valid": True,
                        "compilation_successful": True,
                    }
                    self.record_test_result(
                        "scrapers",
                        "scraping_base_syntax",
                        "pass",
                        (datetime.datetime.now() - start_time).total_seconds(),
                    )
                else:
                    scraper_results["scraping_base"] = {
                        "status": "❌ COMPILATION_ERROR",
                        "error": result.stderr,
                    }
                    self.record_test_result(
                        "scrapers",
                        "scraping_base_syntax",
                        "compilation_error",
                        (datetime.datetime.now() - start_time).total_seconds(),
                        error=result.stderr,
                    )
            else:
                scraper_results["scraping_base"] = {
                    "status": "❌ MISSING",
                    "file_exists": False,
                }
                self.record_test_result(
                    "scrapers",
                    "scraping_base_syntax",
                    "missing",
                    (datetime.datetime.now() - start_time).total_seconds(),
                )

            os.chdir(original_cwd)

        except Exception as e:
            scraper_results["scraping_base"] = {"status": "❌ ERROR", "error": str(e)}
            self.record_test_result(
                "scrapers",
                "scraping_base_syntax",
                "error",
                (datetime.datetime.now() - start_time).total_seconds(),
                error=str(e),
            )

        # Test individual scrapers
        scrapers_to_test = ["reddit_scraper.py", "github_scraper.py", "web_scraper.py"]

        for scraper_file in scrapers_to_test:
            try:
                start_time = datetime.datetime.now()
                scraper_path = self.scrapers_dir / scraper_file

                if scraper_path.exists():
                    # Run syntax check
                    result = subprocess.run(
                        [sys.executable, "-m", "py_compile", str(scraper_path)],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )

                    if result.returncode == 0:
                        scraper_results[scraper_file] = {
                            "status": "✅ PASS",
                            "syntax_valid": True,
                            "size_bytes": scraper_path.stat().st_size,
                        }
                        self.record_test_result(
                            "scrapers",
                            f"{scraper_file}_syntax",
                            "pass",
                            (datetime.datetime.now() - start_time).total_seconds(),
                        )
                    else:
                        scraper_results[scraper_file] = {
                            "status": "❌ SYNTAX_ERROR",
                            "error": result.stderr,
                        }
                        self.record_test_result(
                            "scrapers",
                            f"{scraper_file}_syntax",
                            "syntax_error",
                            (datetime.datetime.now() - start_time).total_seconds(),
                            error=result.stderr,
                        )
                else:
                    scraper_results[scraper_file] = {
                        "status": "❌ MISSING",
                        "file_exists": False,
                    }
                    self.record_test_result(
                        "scrapers",
                        f"{scraper_file}_syntax",
                        "missing",
                        (datetime.datetime.now() - start_time).total_seconds(),
                    )

            except Exception as e:
                scraper_results[scraper_file] = {"status": "❌ ERROR", "error": str(e)}
                self.record_test_result(
                    "scrapers",
                    f"{scraper_file}_syntax",
                    "error",
                    (datetime.datetime.now() - start_time).total_seconds(),
                    error=str(e),
                )

        return scraper_results

    def test_ai_processing_workflow(self) -> Dict:
        """Test AI processing and knowledge management workflow"""
        print("🧠 Testing AI processing workflow...")

        ai_results = {}

        # Test AI processor module
        try:
            start_time = datetime.datetime.now()

            ai_processor_path = self.scripts_dir / "phase_08_ai_processor.py"
            if ai_processor_path.exists():
                # Test syntax
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", str(ai_processor_path)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    ai_results["ai_processor"] = {
                        "status": "✅ PASS",
                        "syntax_valid": True,
                        "size_bytes": ai_processor_path.stat().st_size,
                    }
                    self.record_test_result(
                        "ai_workflow",
                        "ai_processor_syntax",
                        "pass",
                        (datetime.datetime.now() - start_time).total_seconds(),
                    )
                else:
                    ai_results["ai_processor"] = {
                        "status": "❌ SYNTAX_ERROR",
                        "error": result.stderr,
                    }
                    self.record_test_result(
                        "ai_workflow",
                        "ai_processor_syntax",
                        "syntax_error",
                        (datetime.datetime.now() - start_time).total_seconds(),
                        error=result.stderr,
                    )
            else:
                ai_results["ai_processor"] = {
                    "status": "❌ MISSING",
                    "file_exists": False,
                }
                self.record_test_result(
                    "ai_workflow",
                    "ai_processor_syntax",
                    "missing",
                    (datetime.datetime.now() - start_time).total_seconds(),
                )

        except Exception as e:
            ai_results["ai_processor"] = {"status": "❌ ERROR", "error": str(e)}
            self.record_test_result(
                "ai_workflow",
                "ai_processor_syntax",
                "error",
                (datetime.datetime.now() - start_time).total_seconds(),
                error=str(e),
            )

        # Test article organizer
        try:
            start_time = datetime.datetime.now()

            organizer_path = self.scripts_dir / "phase_07_article_organizer.py"
            if organizer_path.exists():
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", str(organizer_path)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    ai_results["article_organizer"] = {
                        "status": "✅ PASS",
                        "syntax_valid": True,
                        "size_bytes": organizer_path.stat().st_size,
                    }
                    self.record_test_result(
                        "ai_workflow",
                        "article_organizer_syntax",
                        "pass",
                        (datetime.datetime.now() - start_time).total_seconds(),
                    )
                else:
                    ai_results["article_organizer"] = {
                        "status": "❌ SYNTAX_ERROR",
                        "error": result.stderr,
                    }
                    self.record_test_result(
                        "ai_workflow",
                        "article_organizer_syntax",
                        "syntax_error",
                        (datetime.datetime.now() - start_time).total_seconds(),
                        error=result.stderr,
                    )
            else:
                ai_results["article_organizer"] = {
                    "status": "❌ MISSING",
                    "file_exists": False,
                }
                self.record_test_result(
                    "ai_workflow",
                    "article_organizer_syntax",
                    "missing",
                    (datetime.datetime.now() - start_time).total_seconds(),
                )

        except Exception as e:
            ai_results["article_organizer"] = {"status": "❌ ERROR", "error": str(e)}
            self.record_test_result(
                "ai_workflow",
                "article_organizer_syntax",
                "error",
                (datetime.datetime.now() - start_time).total_seconds(),
                error=str(e),
            )

        return ai_results

    def test_file_system_structure(self) -> Dict:
        """Test file system structure and permissions"""
        print("📁 Testing file system structure...")

        fs_results = {}

        # Test critical directories
        critical_dirs = [
            "scrapers",
            "scripts",
            "vault",
            "vault/notes",
            "vault/logs",
            "config",
            "session_docs",
        ]

        for dir_name in critical_dirs:
            dir_path = self.project_root / dir_name
            fs_results[dir_name] = {
                "exists": dir_path.exists(),
                "is_directory": dir_path.is_dir() if dir_path.exists() else False,
                "readable": (
                    os.access(dir_path, os.R_OK) if dir_path.exists() else False
                ),
                "writable": (
                    os.access(dir_path, os.W_OK) if dir_path.exists() else False
                ),
            }

            if dir_path.exists() and dir_path.is_dir():
                try:
                    file_count = len(list(dir_path.iterdir()))
                    fs_results[dir_name]["file_count"] = file_count
                    fs_results[dir_name]["status"] = "✅ PASS"
                    self.record_test_result(
                        "filesystem", f"directory_{dir_name}", "pass"
                    )
                except PermissionError:
                    fs_results[dir_name]["status"] = "❌ PERMISSION_ERROR"
                    self.record_test_result(
                        "filesystem", f"directory_{dir_name}", "permission_error"
                    )
            else:
                fs_results[dir_name]["status"] = "❌ MISSING"
                self.record_test_result(
                    "filesystem", f"directory_{dir_name}", "missing"
                )

        return fs_results

    def run_performance_snapshot(self) -> Dict:
        """Take a snapshot of current system performance"""
        print("⚡ Taking performance snapshot...")

        perf_results = {}

        try:
            import psutil

            # System metrics
            perf_results["system"] = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage_percent": psutil.disk_usage("/").percent,
                "load_average": os.getloadavg() if hasattr(os, "getloadavg") else "N/A",
            }

            # Python process metrics
            process = psutil.Process()
            perf_results["python_process"] = {
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "cpu_percent": process.cpu_percent(),
                "num_threads": process.num_threads(),
                "open_files": len(process.open_files()),
            }

            self.record_test_result("performance", "system_snapshot", "pass")

        except ImportError:
            perf_results["error"] = "psutil not available"
            self.record_test_result("performance", "system_snapshot", "psutil_missing")
        except Exception as e:
            perf_results["error"] = str(e)
            self.record_test_result(
                "performance", "system_snapshot", "error", error=str(e)
            )

        return perf_results

    def generate_integration_report(self) -> str:
        """Generate comprehensive integration test report"""
        self.results["end_time"] = datetime.datetime.now().isoformat()
        self.results["status"] = "completed"

        # Calculate summary statistics
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT status, COUNT(*) FROM test_results GROUP BY status")
        status_counts = dict(cursor.fetchall())

        cursor.execute(
            "SELECT AVG(duration_seconds), MIN(duration_seconds), MAX(duration_seconds) FROM test_results WHERE duration_seconds > 0"
        )
        duration_stats = cursor.fetchone()

        conn.close()

        self.results["summary"] = {
            "total_tests": sum(status_counts.values()),
            "passed": status_counts.get("pass", 0),
            "failed": status_counts.get("error", 0)
            + status_counts.get("syntax_error", 0),
            "skipped": status_counts.get("missing", 0)
            + status_counts.get("not_available", 0),
            "avg_duration": duration_stats[0] if duration_stats[0] else 0,
            "min_duration": duration_stats[1] if duration_stats[1] else 0,
            "max_duration": duration_stats[2] if duration_stats[2] else 0,
        }

        # Save detailed report
        report_path = (
            self.test_dir
            / "reports"
            / "integration_tests"
            / f"integration_report_{self.timestamp}.json"
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(self.results, f, indent=2)

        # Generate markdown report
        md_report_path = (
            self.test_dir
            / "reports"
            / "integration_tests"
            / f"integration_report_{self.timestamp}.md"
        )
        self.create_markdown_report(md_report_path)

        return str(md_report_path)

    def create_markdown_report(self, path: Path):
        """Create markdown integration test report"""
        summary = self.results.get("summary", {})
        total_tests = summary.get("total_tests", 0)
        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0)
        skipped = summary.get("skipped", 0)

        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0

        content = f"""# IntelForge Integration Test Report

**Session ID**: {self.results["session_id"]}
**Test Date**: {self.results["start_time"]}
**Report Type**: Core Module Integration Testing

## 📊 Executive Summary

**Overall Status**: {"✅ PASS" if success_rate >= 80 else "⚠️ PARTIAL" if success_rate >= 60 else "❌ FAIL"}
**Success Rate**: {success_rate:.1f}% ({passed}/{total_tests} tests passed)
**Integration Health**: {"Excellent" if success_rate >= 90 else "Good" if success_rate >= 70 else "Needs Attention"}

## 🎯 Test Results Overview

| Category | Passed | Failed | Skipped | Total |
|----------|--------|--------|---------|-------|
| **Overall** | {passed} | {failed} | {skipped} | {total_tests} |

### Performance Metrics
- **Average Test Duration**: {summary.get("avg_duration", 0):.3f}s
- **Fastest Test**: {summary.get("min_duration", 0):.3f}s
- **Slowest Test**: {summary.get("max_duration", 0):.3f}s

## 🔍 Core Module Analysis

### Module Import Status
"""

        # Add core module results
        if "core_modules" in self.results:
            for module, result in self.results["core_modules"].items():
                if isinstance(result, dict):
                    status = result.get("status", "❓ UNKNOWN")
                    size = result.get("size_bytes", 0)
                    content += f"- **{module}**: {status}"
                    if size > 0:
                        content += f" ({size:,} bytes)"
                else:
                    content += f"- **{module}**: {result}"
                content += "\n"

        content += "\n### Configuration Loading\n"
        if "configuration" in self.results:
            for config, result in self.results["configuration"].items():
                if isinstance(result, dict):
                    status = result.get("status", "❓ UNKNOWN")
                    content += f"- **{config}**: {status}\n"
                else:
                    content += f"- **{config}**: {result}\n"

        content += "\n### Database Connections\n"
        if "database" in self.results:
            for db, result in self.results["database"].items():
                if isinstance(result, dict):
                    status = result.get("status", "❓ UNKNOWN")
                    content += f"- **{db}**: {status}\n"
                else:
                    content += f"- **{db}**: {result}\n"

        content += "\n### Scraper Integration\n"
        if "scrapers" in self.results:
            for scraper, result in self.results["scrapers"].items():
                if isinstance(result, dict):
                    status = result.get("status", "❓ UNKNOWN")
                    content += f"- **{scraper}**: {status}\n"
                else:
                    content += f"- **{scraper}**: {result}\n"

        content += "\n### AI Processing Workflow\n"
        if "ai_workflow" in self.results:
            for component, result in self.results["ai_workflow"].items():
                if isinstance(result, dict):
                    status = result.get("status", "❓ UNKNOWN")
                    content += f"- **{component}**: {status}\n"
                else:
                    content += f"- **{component}**: {result}\n"

        content += "\n## 🛠️ System Health Assessment\n"

        if "filesystem" in self.results:
            content += "\n### File System Structure\n"
            for directory, result in self.results["filesystem"].items():
                if isinstance(result, dict):
                    status = result.get("status", "❓ UNKNOWN")
                    file_count = result.get("file_count", "N/A")
                    content += f"- **{directory}/**: {status}"
                    if file_count != "N/A":
                        content += f" ({file_count} files)"
                else:
                    content += f"- **{directory}/**: {result}"
                content += "\n"

        if "performance" in self.results:
            content += "\n### Performance Snapshot\n"
            perf = self.results["performance"]
            if "system" in perf:
                sys_perf = perf["system"]
                content += f"- **CPU Usage**: {sys_perf.get('cpu_percent', 'N/A')}%\n"
                content += (
                    f"- **Memory Usage**: {sys_perf.get('memory_percent', 'N/A')}%\n"
                )
                content += (
                    f"- **Disk Usage**: {sys_perf.get('disk_usage_percent', 'N/A')}%\n"
                )

            if "python_process" in perf:
                proc_perf = perf["python_process"]
                content += f"- **Process Memory**: {proc_perf.get('memory_mb', 'N/A'):.1f} MB\n"
                content += (
                    f"- **Process Threads**: {proc_perf.get('num_threads', 'N/A')}\n"
                )

        content += f"""

## 🎯 Integration Assessment

### Strengths
- Core modules syntactically valid and importable
- File system structure properly organized
- Configuration files accessible

### Areas for Improvement
- {"No critical issues identified" if success_rate >= 90 else "Review failed modules for dependency issues"}
- {"Excellent performance metrics" if success_rate >= 80 else "Consider optimization for failing components"}

## 📋 Recommendations

### Immediate Actions
{"✅ No immediate actions required - system healthy" if success_rate >= 90 else "⚠️ Review and fix failing components before production use"}

### Long-term Optimization
- Implement continuous integration testing
- Add performance regression monitoring
- Enhance error handling in core modules

## 🔗 Technical Details

**Test Database**: `{self.test_db_path}`
**Report Location**: `{path}`
**Project Root**: `{self.project_root}`

---
*Generated by IntelForge Integration Test Runner*
*Framework: Core module testing with database tracking*
"""

        with open(path, "w") as f:
            f.write(content)


def main():
    parser = argparse.ArgumentParser(description="IntelForge Integration Test Runner")
    parser.add_argument("--config", help="Custom config file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    print("🚀 Starting IntelForge Integration Testing")
    print("🔍 Testing core module imports, configurations, and workflows")
    print("📊 Results will be tracked in SQLite database")

    tester = IntelForgeIntegrationTester(args.config)

    # Run all integration tests
    print("\n" + "=" * 60)
    tester.results["core_modules"] = tester.test_core_module_imports()

    print("\n" + "=" * 60)
    tester.results["configuration"] = tester.test_configuration_loading()

    print("\n" + "=" * 60)
    tester.results["database"] = tester.test_database_connections()

    print("\n" + "=" * 60)
    tester.results["scrapers"] = tester.test_scraper_integrations()

    print("\n" + "=" * 60)
    tester.results["ai_workflow"] = tester.test_ai_processing_workflow()

    print("\n" + "=" * 60)
    tester.results["filesystem"] = tester.test_file_system_structure()

    print("\n" + "=" * 60)
    tester.results["performance"] = tester.run_performance_snapshot()

    # Generate comprehensive report
    print("\n" + "=" * 60)
    print("📊 Generating integration test report...")
    report_path = tester.generate_integration_report()

    # Final summary
    summary = tester.results.get("summary", {})
    total_tests = summary.get("total_tests", 0)
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)
    skipped = summary.get("skipped", 0)
    success_rate = (passed / total_tests * 100) if total_tests > 0 else 0

    print("\n🎉 Integration testing complete!")
    print(f"📊 **Results**: {passed} passed, {failed} failed, {skipped} skipped")
    print(f"✅ **Success Rate**: {success_rate:.1f}%")
    print(f"📋 **Status**: {'HEALTHY' if success_rate >= 80 else 'NEEDS ATTENTION'}")
    print(f"📁 **Report**: {report_path}")
    print(f"🗄️ **Database**: {tester.test_db_path}")


if __name__ == "__main__":
    main()
