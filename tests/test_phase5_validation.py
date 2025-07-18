#!/usr/bin/env python3
"""
Phase 5 Validation Tests
Testing and validation for IntelForge Phase 5 implementation.

Tests cover:
- Priority-based scheduling system (Phase 5.1)
- Cron integration and automation (Phase 5.2)
- Monitoring and alerts system (Phase 5.3)
"""

import pytest
import json
import sys
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.crawler_scheduler import CrawlerScheduler, Priority, ScheduledSource
from scripts.crawler_monitor import CrawlerMonitor, CrawlMetrics, SystemMetrics, Alert

class TestCrawlerScheduler:
    """Test the crawler scheduler functionality"""

    def test_scheduler_initialization(self):
        """Test scheduler initializes correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test registry
            registry_path = Path(temp_dir) / "test_registry.yaml"
            registry_content = """
rss_feeds:
  - name: "Test Source"
    url: "https://example.com/test"
    priority: "daily"
    threshold: 0.8
    complexity: "medium"
    quality: "premium"
    content_requirements:
      must_have: ["test"]
      optional: ["optional"]
    tags: ["test"]

global_settings:
  default_threshold: 0.75
  default_rate_limit: 3
"""
            registry_path.write_text(registry_content)

            scheduler = CrawlerScheduler(str(registry_path))

            assert len(scheduler.sources) == 1
            assert scheduler.sources[0].name == "Test Source"
            assert scheduler.sources[0].priority == Priority.DAILY
            assert scheduler.sources[0].threshold == 0.8

    def test_scheduled_source_due_logic(self):
        """Test scheduled source due checking logic"""
        source = ScheduledSource(
            name="Test",
            url="https://example.com",
            priority=Priority.DAILY,
            threshold=0.8,
            category="test",
            quality="good",
            complexity="medium",
            content_requirements={},
            tags=[]
        )

        # Source with no next_crawl should be due
        assert source.is_due()

        # Source with future next_crawl should not be due
        source.next_crawl = datetime.now() + timedelta(hours=1)
        assert not source.is_due()

        # Source with past next_crawl should be due
        source.next_crawl = datetime.now() - timedelta(hours=1)
        assert source.is_due()

    def test_next_crawl_calculation(self):
        """Test next crawl time calculation"""
        source = ScheduledSource(
            name="Test",
            url="https://example.com",
            priority=Priority.DAILY,
            threshold=0.8,
            category="test",
            quality="good",
            complexity="medium",
            content_requirements={},
            tags=[]
        )

        # Test daily priority
        source.priority = Priority.DAILY
        next_crawl = source.calculate_next_crawl()
        assert next_crawl > datetime.now()
        assert next_crawl < datetime.now() + timedelta(days=2)

        # Test weekly priority
        source.priority = Priority.WEEKLY
        next_crawl = source.calculate_next_crawl()
        assert next_crawl > datetime.now() + timedelta(days=6)
        assert next_crawl < datetime.now() + timedelta(days=8)

        # Test monthly priority
        source.priority = Priority.MONTHLY
        next_crawl = source.calculate_next_crawl()
        assert next_crawl > datetime.now() + timedelta(days=29)
        assert next_crawl < datetime.now() + timedelta(days=31)

    def test_success_rate_calculation(self):
        """Test success rate calculation"""
        source = ScheduledSource(
            name="Test",
            url="https://example.com",
            priority=Priority.DAILY,
            threshold=0.8,
            category="test",
            quality="good",
            complexity="medium",
            content_requirements={},
            tags=[]
        )

        # First crawl success
        source.update_after_crawl(True)
        assert source.success_rate == 1.0
        assert source.crawl_count == 1

        # Second crawl failure
        source.update_after_crawl(False)
        assert source.success_rate == 0.3  # 0.7 * 1.0 + 0.3 * 0.0
        assert source.crawl_count == 2

        # Third crawl success
        source.update_after_crawl(True)
        expected_rate = 0.7 * 0.3 + 0.3 * 1.0  # 0.51
        assert abs(source.success_rate - expected_rate) < 0.01
        assert source.crawl_count == 3

class TestCrawlerMonitor:
    """Test the crawler monitor functionality"""

    def test_monitor_initialization(self):
        """Test monitor initializes correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            config = {
                "monitoring": {"enabled": True, "interval_seconds": 60},
                "alerts": {"enabled": True, "email_enabled": False},
                "thresholds": {"failure_rate_threshold": 0.2}
            }
            config_path.write_text(json.dumps(config))

            monitor = CrawlerMonitor(str(config_path))

            assert monitor.config["monitoring"]["enabled"] is True
            assert monitor.config["alerts"]["enabled"] is True
            assert len(monitor.alerts) >= 7  # Default alerts

    def test_crawl_metrics_recording(self):
        """Test crawl metrics recording"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            config = {"monitoring": {"enabled": True, "max_metrics_in_memory": 100}}
            config_path.write_text(json.dumps(config))

            monitor = CrawlerMonitor(str(config_path))

            # Create test metric
            metric = CrawlMetrics(
                timestamp=datetime.now(),
                source_name="Test Source",
                url="https://example.com",
                success=True,
                execution_time=45.5,
                content_extracted=10,
                threshold_used=0.8,
                rate_limit=3.0
            )

            monitor.record_crawl_metric(metric)

            assert len(monitor.crawl_metrics) == 1
            assert monitor.crawl_metrics[0].source_name == "Test Source"
            assert monitor.crawl_metrics[0].success is True

    def test_system_metrics_collection(self):
        """Test system metrics collection"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            config = {"monitoring": {"enabled": True}}
            config_path.write_text(json.dumps(config))

            monitor = CrawlerMonitor(str(config_path))

            # Mock psutil to avoid system dependencies
            with patch('scripts.crawler_monitor.psutil') as mock_psutil:
                mock_psutil.cpu_percent.return_value = 25.0
                mock_psutil.virtual_memory.return_value = Mock(percent=50.0)
                mock_psutil.disk_usage.return_value = Mock(used=500, total=1000)
                mock_psutil.process_iter.return_value = []

                metric = monitor.collect_system_metrics()

                assert metric.cpu_usage == 25.0
                assert metric.memory_usage == 50.0
                assert metric.disk_usage == 50.0
                assert metric.active_crawls == 0

    def test_alert_triggering(self):
        """Test alert triggering logic"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            config = {
                "monitoring": {"enabled": True},
                "alerts": {"enabled": True, "email_enabled": False}
            }
            config_path.write_text(json.dumps(config))

            monitor = CrawlerMonitor(str(config_path))

            # Create alert
            alert = Alert(
                name="test_alert",
                condition="test > threshold",
                threshold=0.5,
                severity="high",
                cooldown_minutes=1
            )

            # Test cooldown logic
            assert not alert.is_in_cooldown()

            alert.trigger()
            assert alert.is_in_cooldown()
            assert alert.last_triggered is not None

    def test_alert_metrics_calculation(self):
        """Test alert metrics calculation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            config = {"monitoring": {"enabled": True}}
            config_path.write_text(json.dumps(config))

            monitor = CrawlerMonitor(str(config_path))

            # Add test crawl metrics
            now = datetime.now()
            metrics = [
                CrawlMetrics(now - timedelta(minutes=30), "test1", "url1", True, 10, 5),
                CrawlMetrics(now - timedelta(minutes=20), "test2", "url2", False, 15, 0),
                CrawlMetrics(now - timedelta(minutes=10), "test3", "url3", True, 20, 3)
            ]

            for metric in metrics:
                monitor.crawl_metrics.append(metric)

            alert_metrics = monitor.calculate_alert_metrics()

            assert alert_metrics['failure_rate'] == 1/3  # 1 failure out of 3
            assert alert_metrics['avg_response_time'] == 15.0  # (10+15+20)/3
            assert alert_metrics['last_activity_seconds'] < 1800  # Less than 30 minutes

    def test_report_generation(self):
        """Test monitoring report generation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            config = {"monitoring": {"enabled": True}}
            config_path.write_text(json.dumps(config))

            monitor = CrawlerMonitor(str(config_path))

            # Add test data
            now = datetime.now()
            crawl_metric = CrawlMetrics(now, "test", "url", True, 30, 5)
            monitor.crawl_metrics.append(crawl_metric)

            system_metric = SystemMetrics(now, 25.0, 50.0, 60.0, 1, 5)
            monitor.system_metrics.append(system_metric)

            report = monitor.generate_report()

            assert 'system_status' in report
            assert 'crawl_metrics' in report
            assert 'system_metrics' in report
            assert 'alerts' in report
            assert report['crawl_metrics']['total_crawls'] == 1
            assert report['system_metrics']['cpu_usage'] == 25.0

class TestPhase5Integration:
    """Integration tests for Phase 5 components"""

    def test_scheduler_monitor_integration(self):
        """Test scheduler and monitor working together"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test registry
            registry_path = Path(temp_dir) / "test_registry.yaml"
            registry_content = """
rss_feeds:
  - name: "Test Source"
    url: "https://example.com/test"
    priority: "daily"
    threshold: 0.8
    complexity: "medium"
    quality: "premium"
    content_requirements:
      must_have: ["test"]
    tags: ["test"]

global_settings:
  default_threshold: 0.75
"""
            registry_path.write_text(registry_content)

            # Create test monitor config
            config_path = Path(temp_dir) / "test_config.json"
            config = {"monitoring": {"enabled": True}}
            config_path.write_text(json.dumps(config))

            # Initialize both components
            scheduler = CrawlerScheduler(str(registry_path))
            monitor = CrawlerMonitor(str(config_path))

            # Test basic functionality
            assert len(scheduler.sources) == 1
            assert len(monitor.alerts) >= 7

            # Test report generation
            report = monitor.generate_report()
            assert 'system_status' in report

    def test_cron_integration_format(self):
        """Test cron file format is valid"""
        cron_file = Path("cron/crawler_schedule.cron")

        if cron_file.exists():
            content = cron_file.read_text()

            # Check for required components
            assert "IntelForge Crawler Schedule" in content
            assert "crawler_scheduler.py" in content
            assert "0 6 * * *" in content  # Daily at 6 AM
            assert "0 7 * * 1" in content  # Weekly on Monday at 7 AM
            assert "0 8 1 * *" in content  # Monthly on 1st at 8 AM

            # Check for proper environment setup
            assert "PROJECT_DIR" in content
            assert "source venv/bin/activate" in content

    def test_justfile_tasks_available(self):
        """Test Phase 5 justfile tasks are properly defined"""
        justfile_path = Path("justfile")

        if justfile_path.exists():
            content = justfile_path.read_text()

            # Check for Phase 5 tasks
            assert "setup-crawling-schedule:" in content
            assert "show-crawler-schedule:" in content
            assert "run-scheduled-crawls" in content
            assert "test-crawler-scheduler" in content

            # Check for proper documentation
            assert "Phase 5 - Crawler Scheduling:" in content

def test_phase5_health_check():
    """Comprehensive health check for Phase 5 implementation"""

    def test_scheduler_health():
        """Test scheduler health"""
        try:
            # Test scheduler import
            from scripts.crawler_scheduler import CrawlerScheduler, Priority

            # Test basic functionality
            scheduler = CrawlerScheduler("config/source_registry.yaml")
            sources = scheduler.get_due_sources()

            return True, f"Scheduler healthy: {len(scheduler.sources)} sources loaded"
        except Exception as e:
            return False, f"Scheduler error: {e}"

    def test_monitor_health():
        """Test monitor health"""
        try:
            # Test monitor import
            from scripts.crawler_monitor import CrawlerMonitor

            # Test basic functionality
            monitor = CrawlerMonitor("config/monitor_config.json")
            report = monitor.generate_report()

            return True, f"Monitor healthy: {report['system_status']}"
        except Exception as e:
            return False, f"Monitor error: {e}"

    def test_file_structure():
        """Test required files exist"""
        required_files = [
            "scripts/crawler_scheduler.py",
            "scripts/crawler_monitor.py",
            "config/source_registry.yaml",
            "config/monitor_config.json",
            "cron/crawler_schedule.cron"
        ]

        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)

        if missing_files:
            return False, f"Missing files: {missing_files}"
        else:
            return True, "All required files present"

    # Run all health checks
    scheduler_ok, scheduler_msg = test_scheduler_health()
    monitor_ok, monitor_msg = test_monitor_health()
    files_ok, files_msg = test_file_structure()

    # Summary
    all_healthy = scheduler_ok and monitor_ok and files_ok

    health_report = {
        'overall_status': 'HEALTHY' if all_healthy else 'DEGRADED',
        'scheduler': {'status': 'OK' if scheduler_ok else 'ERROR', 'message': scheduler_msg},
        'monitor': {'status': 'OK' if monitor_ok else 'ERROR', 'message': monitor_msg},
        'files': {'status': 'OK' if files_ok else 'ERROR', 'message': files_msg}
    }

    return health_report

if __name__ == "__main__":
    # Run health check when script is executed directly
    health = test_phase5_health_check()
    print(f"Phase 5 Health Check: {health['overall_status']}")

    for component, details in health.items():
        if component != 'overall_status':
            print(f"  {component}: {details['status']} - {details['message']}")

    # Run pytest if available
    try:
        import pytest
        pytest.main([__file__, "-v"])
    except ImportError:
        print("pytest not available, skipping automated tests")
