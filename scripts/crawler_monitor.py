#!/usr/bin/env python3
"""
IntelForge Crawler Monitor - Phase 5.3 Implementation
Monitoring and alerting system for crawler performance and health.

This module provides comprehensive monitoring capabilities for the semantic crawler
system, including performance tracking, failure detection, and alerting.
"""

import argparse
import json
import logging
import os
import smtplib
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

# Add the project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class CrawlMetrics:
    """Metrics for a single crawl operation"""

    timestamp: datetime
    source_name: str
    url: str
    success: bool
    execution_time: float
    content_extracted: int
    error_message: Optional[str] = None
    threshold_used: float = 0.75
    rate_limit: float = 3.0

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "source_name": self.source_name,
            "url": self.url,
            "success": self.success,
            "execution_time": self.execution_time,
            "content_extracted": self.content_extracted,
            "error_message": self.error_message,
            "threshold_used": self.threshold_used,
            "rate_limit": self.rate_limit,
        }


@dataclass
class SystemMetrics:
    """System-level performance metrics"""

    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_crawls: int
    queue_size: int

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "disk_usage": self.disk_usage,
            "active_crawls": self.active_crawls,
            "queue_size": self.queue_size,
        }


@dataclass
class Alert:
    """Alert configuration and state"""

    name: str
    condition: str
    threshold: float
    severity: str  # 'low', 'medium', 'high', 'critical'
    enabled: bool = True
    cooldown_minutes: int = 30
    last_triggered: Optional[datetime] = None

    def is_in_cooldown(self) -> bool:
        """Check if alert is in cooldown period"""
        if self.last_triggered is None:
            return False
        return datetime.now() - self.last_triggered < timedelta(
            minutes=self.cooldown_minutes
        )

    def trigger(self):
        """Mark alert as triggered"""
        self.last_triggered = datetime.now()


class CrawlerMonitor:
    """Main monitoring system for crawler operations"""

    def __init__(self, config_path: str = "config/monitor_config.json"):
        self.config_path = Path(config_path)
        self.metrics_file = Path("logs/crawler_metrics.json")
        self.alerts_file = Path("logs/alerts.json")
        self.system_metrics_file = Path("logs/system_metrics.json")

        # Create directories
        self.metrics_file.parent.mkdir(exist_ok=True)

        # Load configuration
        self.config = self.load_config()

        # Initialize alerts
        self.alerts = self.load_alerts()

        # Metrics storage
        self.crawl_metrics: List[CrawlMetrics] = []
        self.system_metrics: List[SystemMetrics] = []

        # Load historical data
        self.load_historical_data()

    def load_config(self) -> Dict:
        """Load monitoring configuration"""
        default_config = {
            "monitoring": {
                "enabled": True,
                "interval_seconds": 60,
                "retention_days": 30,
                "max_metrics_in_memory": 1000,
            },
            "alerts": {
                "enabled": True,
                "email_enabled": False,
                "email_smtp_server": "smtp.gmail.com",
                "email_port": 587,
                "email_username": "",
                "email_password": "",
                "email_recipients": [],
            },
            "thresholds": {
                "failure_rate_threshold": 0.2,
                "response_time_threshold": 300,
                "cpu_threshold": 80.0,
                "memory_threshold": 85.0,
                "disk_threshold": 90.0,
                "queue_size_threshold": 50,
            },
        }

        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                logger.warning(f"Error loading config: {e}, using defaults")

        # Save default config
        self.save_config(default_config)
        return default_config

    def save_config(self, config: Dict):
        """Save monitoring configuration"""
        try:
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def load_alerts(self) -> List[Alert]:
        """Load alert configurations"""
        default_alerts = [
            Alert("high_failure_rate", "failure_rate > threshold", 0.2, "high"),
            Alert("slow_response", "avg_response_time > threshold", 300, "medium"),
            Alert("high_cpu", "cpu_usage > threshold", 80.0, "medium"),
            Alert("high_memory", "memory_usage > threshold", 85.0, "medium"),
            Alert("high_disk", "disk_usage > threshold", 90.0, "high"),
            Alert("large_queue", "queue_size > threshold", 50, "medium"),
            Alert("crawler_down", "no_recent_activity", 3600, "critical"),
        ]

        if self.alerts_file.exists():
            try:
                with open(self.alerts_file, "r") as f:
                    alerts_data = json.load(f)

                alerts = []
                for alert_data in alerts_data:
                    alert = Alert(**alert_data)
                    if alert.last_triggered:
                        alert.last_triggered = datetime.fromisoformat(
                            alert.last_triggered
                        )
                    alerts.append(alert)

                return alerts
            except Exception as e:
                logger.warning(f"Error loading alerts: {e}, using defaults")

        self.save_alerts(default_alerts)
        return default_alerts

    def save_alerts(self, alerts: List[Alert]):
        """Save alert configurations"""
        try:
            alerts_data = []
            for alert in alerts:
                data = asdict(alert)
                if alert.last_triggered:
                    data["last_triggered"] = alert.last_triggered.isoformat()
                alerts_data.append(data)

            with open(self.alerts_file, "w") as f:
                json.dump(alerts_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving alerts: {e}")

    def load_historical_data(self):
        """Load historical metrics data"""
        # Load crawl metrics
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, "r") as f:
                    metrics_data = json.load(f)

                for metric_data in metrics_data[-100:]:  # Keep last 100 records
                    metric = CrawlMetrics(
                        timestamp=datetime.fromisoformat(metric_data["timestamp"]),
                        source_name=metric_data["source_name"],
                        url=metric_data["url"],
                        success=metric_data["success"],
                        execution_time=metric_data["execution_time"],
                        content_extracted=metric_data["content_extracted"],
                        error_message=metric_data.get("error_message"),
                        threshold_used=metric_data.get("threshold_used", 0.75),
                        rate_limit=metric_data.get("rate_limit", 3.0),
                    )
                    self.crawl_metrics.append(metric)
            except Exception as e:
                logger.warning(f"Error loading historical data: {e}")

        # Load system metrics
        if self.system_metrics_file.exists():
            try:
                with open(self.system_metrics_file, "r") as f:
                    system_data = json.load(f)

                for metric_data in system_data[-100:]:  # Keep last 100 records
                    metric = SystemMetrics(
                        timestamp=datetime.fromisoformat(metric_data["timestamp"]),
                        cpu_usage=metric_data["cpu_usage"],
                        memory_usage=metric_data["memory_usage"],
                        disk_usage=metric_data["disk_usage"],
                        active_crawls=metric_data["active_crawls"],
                        queue_size=metric_data["queue_size"],
                    )
                    self.system_metrics.append(metric)
            except Exception as e:
                logger.warning(f"Error loading system metrics: {e}")

    def record_crawl_metric(self, metric: CrawlMetrics):
        """Record a crawl operation metric"""
        self.crawl_metrics.append(metric)

        # Keep only recent metrics in memory
        max_metrics = self.config["monitoring"]["max_metrics_in_memory"]
        if len(self.crawl_metrics) > max_metrics:
            self.crawl_metrics = self.crawl_metrics[-max_metrics:]

        # Save to file
        self.save_crawl_metrics()

        # Check alerts
        self.check_alerts()

    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            # Get CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)

            # Get memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent

            # Get disk usage for project directory
            disk = psutil.disk_usage(".")
            disk_usage = (disk.used / disk.total) * 100

            # Count active crawl processes
            active_crawls = 0
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    cmdline = proc.info["cmdline"]
                    if cmdline and "semantic_crawler.py" in " ".join(cmdline):
                        active_crawls += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Estimate queue size (simplified)
            queue_size = 0
            if Path("metadata/crawler_schedule.json").exists():
                try:
                    with open("metadata/crawler_schedule.json", "r") as f:
                        schedule_data = json.load(f)
                    # Count sources that haven't been crawled recently
                    now = datetime.now()
                    for source_data in schedule_data.values():
                        if source_data.get("next_crawl"):
                            next_crawl = datetime.fromisoformat(
                                source_data["next_crawl"]
                            )
                            if next_crawl <= now:
                                queue_size += 1
                except Exception:
                    pass

            metric = SystemMetrics(
                timestamp=datetime.now(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                active_crawls=active_crawls,
                queue_size=queue_size,
            )

            self.system_metrics.append(metric)

            # Keep only recent metrics
            max_metrics = self.config["monitoring"]["max_metrics_in_memory"]
            if len(self.system_metrics) > max_metrics:
                self.system_metrics = self.system_metrics[-max_metrics:]

            self.save_system_metrics()

            return metric

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                active_crawls=0,
                queue_size=0,
            )

    def save_crawl_metrics(self):
        """Save crawl metrics to file"""
        try:
            metrics_data = [m.to_dict() for m in self.crawl_metrics]
            with open(self.metrics_file, "w") as f:
                json.dump(metrics_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving crawl metrics: {e}")

    def save_system_metrics(self):
        """Save system metrics to file"""
        try:
            metrics_data = [m.to_dict() for m in self.system_metrics]
            with open(self.system_metrics_file, "w") as f:
                json.dump(metrics_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving system metrics: {e}")

    def check_alerts(self):
        """Check all alert conditions"""
        if not self.config["alerts"]["enabled"]:
            return

        current_time = datetime.now()

        # Calculate metrics for alert checking
        metrics = self.calculate_alert_metrics()

        for alert in self.alerts:
            if not alert.enabled or alert.is_in_cooldown():
                continue

            triggered = False

            # Check different alert conditions
            if alert.name == "high_failure_rate":
                if metrics.get("failure_rate", 0) > alert.threshold:
                    triggered = True
            elif alert.name == "slow_response":
                if metrics.get("avg_response_time", 0) > alert.threshold:
                    triggered = True
            elif alert.name == "high_cpu":
                if metrics.get("cpu_usage", 0) > alert.threshold:
                    triggered = True
            elif alert.name == "high_memory":
                if metrics.get("memory_usage", 0) > alert.threshold:
                    triggered = True
            elif alert.name == "high_disk":
                if metrics.get("disk_usage", 0) > alert.threshold:
                    triggered = True
            elif alert.name == "large_queue":
                if metrics.get("queue_size", 0) > alert.threshold:
                    triggered = True
            elif alert.name == "crawler_down":
                last_activity = metrics.get("last_activity_seconds", 0)
                if last_activity > alert.threshold:
                    triggered = True

            if triggered:
                self.trigger_alert(alert, metrics)

    def calculate_alert_metrics(self) -> Dict[str, float]:
        """Calculate metrics for alert checking"""
        metrics = {}

        # Crawl metrics from last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_crawls = [m for m in self.crawl_metrics if m.timestamp > one_hour_ago]

        if recent_crawls:
            # Failure rate
            failures = [m for m in recent_crawls if not m.success]
            metrics["failure_rate"] = len(failures) / len(recent_crawls)

            # Average response time
            response_times = [m.execution_time for m in recent_crawls]
            metrics["avg_response_time"] = sum(response_times) / len(response_times)

            # Last activity
            last_crawl = max(recent_crawls, key=lambda x: x.timestamp)
            metrics["last_activity_seconds"] = (
                datetime.now() - last_crawl.timestamp
            ).total_seconds()
        else:
            metrics["failure_rate"] = 0.0
            metrics["avg_response_time"] = 0.0
            metrics["last_activity_seconds"] = 3600  # 1 hour

        # System metrics
        if self.system_metrics:
            latest_system = self.system_metrics[-1]
            metrics["cpu_usage"] = latest_system.cpu_usage
            metrics["memory_usage"] = latest_system.memory_usage
            metrics["disk_usage"] = latest_system.disk_usage
            metrics["queue_size"] = latest_system.queue_size

        return metrics

    def trigger_alert(self, alert: Alert, metrics: Dict[str, float]):
        """Trigger an alert"""
        alert.trigger()

        message = f"🚨 ALERT: {alert.name} (Severity: {alert.severity})\n"
        message += f"Condition: {alert.condition}\n"
        message += f"Threshold: {alert.threshold}\n"
        message += f"Current metrics: {metrics}\n"
        message += f"Time: {datetime.now().isoformat()}\n"

        logger.warning(message)

        # Send email if configured
        if self.config["alerts"]["email_enabled"]:
            self.send_email_alert(alert, message)

        # Save alert log
        self.log_alert(alert, message, metrics)

        # Save updated alerts
        self.save_alerts(self.alerts)

    def send_email_alert(self, alert: Alert, message: str):
        """Send email alert"""
        try:
            smtp_server = self.config["alerts"]["email_smtp_server"]
            port = self.config["alerts"]["email_port"]
            username = self.config["alerts"]["email_username"]
            password = self.config["alerts"]["email_password"]
            recipients = self.config["alerts"]["email_recipients"]

            if not all([smtp_server, username, password, recipients]):
                logger.warning("Email configuration incomplete, skipping email alert")
                return

            msg = MIMEMultipart()
            msg["From"] = username
            msg["To"] = ", ".join(recipients)
            msg["Subject"] = f"IntelForge Alert: {alert.name}"

            msg.attach(MIMEText(message, "plain"))

            with smtplib.SMTP(smtp_server, port) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)

            logger.info(f"Email alert sent for {alert.name}")

        except Exception as e:
            logger.error(f"Error sending email alert: {e}")

    def log_alert(self, alert: Alert, message: str, metrics: Dict[str, float]):
        """Log alert to file"""
        try:
            alert_log = {
                "timestamp": datetime.now().isoformat(),
                "alert_name": alert.name,
                "severity": alert.severity,
                "message": message,
                "metrics": metrics,
            }

            alert_log_file = Path("logs/alert_log.json")

            # Load existing logs
            logs = []
            if alert_log_file.exists():
                with open(alert_log_file, "r") as f:
                    logs = json.load(f)

            logs.append(alert_log)

            # Keep only recent logs
            logs = logs[-1000:]  # Keep last 1000 alerts

            with open(alert_log_file, "w") as f:
                json.dump(logs, f, indent=2)

        except Exception as e:
            logger.error(f"Error logging alert: {e}")

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_status": "healthy",
            "crawl_metrics": {},
            "system_metrics": {},
            "alerts": {},
            "recommendations": [],
        }

        # Recent crawl metrics
        recent_crawls = [
            m
            for m in self.crawl_metrics
            if m.timestamp > datetime.now() - timedelta(hours=24)
        ]

        if recent_crawls:
            successes = [m for m in recent_crawls if m.success]
            failures = [m for m in recent_crawls if not m.success]

            report["crawl_metrics"] = {
                "total_crawls": len(recent_crawls),
                "successful_crawls": len(successes),
                "failed_crawls": len(failures),
                "success_rate": (
                    len(successes) / len(recent_crawls) if recent_crawls else 0
                ),
                "avg_execution_time": sum(m.execution_time for m in recent_crawls)
                / len(recent_crawls),
                "total_content_extracted": sum(
                    m.content_extracted for m in recent_crawls
                ),
            }

            # Check if system is healthy
            if len(failures) / len(recent_crawls) > 0.2:  # >20% failure rate
                report["system_status"] = "degraded"

        # System metrics
        if self.system_metrics:
            latest_system = self.system_metrics[-1]
            report["system_metrics"] = {
                "cpu_usage": latest_system.cpu_usage,
                "memory_usage": latest_system.memory_usage,
                "disk_usage": latest_system.disk_usage,
                "active_crawls": latest_system.active_crawls,
                "queue_size": latest_system.queue_size,
            }

            # Check system health
            if (
                latest_system.cpu_usage > 80
                or latest_system.memory_usage > 85
                or latest_system.disk_usage > 90
            ):
                report["system_status"] = "degraded"

        # Alert summary
        recent_alerts = []
        alert_log_file = Path("logs/alert_log.json")
        if alert_log_file.exists():
            try:
                with open(alert_log_file, "r") as f:
                    alert_logs = json.load(f)

                # Get alerts from last 24 hours
                cutoff = datetime.now() - timedelta(hours=24)
                recent_alerts = [
                    a
                    for a in alert_logs
                    if datetime.fromisoformat(a["timestamp"]) > cutoff
                ]
            except Exception:
                pass

        report["alerts"] = {
            "total_alerts_24h": len(recent_alerts),
            "critical_alerts": len(
                [a for a in recent_alerts if a["severity"] == "critical"]
            ),
            "high_alerts": len([a for a in recent_alerts if a["severity"] == "high"]),
            "medium_alerts": len(
                [a for a in recent_alerts if a["severity"] == "medium"]
            ),
            "low_alerts": len([a for a in recent_alerts if a["severity"] == "low"]),
        }

        if recent_alerts:
            report["system_status"] = "degraded"

        # Generate recommendations
        if report["crawl_metrics"].get("success_rate", 1) < 0.8:
            report["recommendations"].append("Consider investigating crawler failures")

        if report["system_metrics"].get("cpu_usage", 0) > 70:
            report["recommendations"].append(
                "CPU usage is high, consider optimizing crawl frequency"
            )

        if report["system_metrics"].get("queue_size", 0) > 20:
            report["recommendations"].append(
                "Large queue detected, consider increasing crawl parallelism"
            )

        return report

    def run_monitoring_loop(self):
        """Run continuous monitoring loop"""
        logger.info("Starting crawler monitoring loop...")

        interval = self.config["monitoring"]["interval_seconds"]

        while True:
            try:
                # Collect system metrics
                system_metric = self.collect_system_metrics()

                # Check alerts
                self.check_alerts()

                # Log status
                logger.info(
                    f"Monitoring: CPU={system_metric.cpu_usage:.1f}% "
                    f"Memory={system_metric.memory_usage:.1f}% "
                    f"Disk={system_metric.disk_usage:.1f}% "
                    f"Active={system_metric.active_crawls} "
                    f"Queue={system_metric.queue_size}"
                )

                # Sleep until next interval
                time.sleep(interval)

            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval)

    def show_status(self):
        """Show current monitoring status"""
        report = self.generate_report()

        print("\n🖥️  IntelForge Crawler Monitoring Status")
        print("=" * 50)

        print(f"📊 System Status: {report['system_status'].upper()}")
        print(f"⏰ Report Time: {report['timestamp']}")

        print("\n🚀 Crawl Metrics (24h):")
        crawl_metrics = report["crawl_metrics"]
        if crawl_metrics:
            print(f"  Total Crawls: {crawl_metrics['total_crawls']}")
            print(f"  Success Rate: {crawl_metrics['success_rate']:.1%}")
            print(f"  Avg Execution Time: {crawl_metrics['avg_execution_time']:.1f}s")
            print(f"  Content Extracted: {crawl_metrics['total_content_extracted']}")
        else:
            print("  No crawl data available")

        print("\n💻 System Metrics:")
        system_metrics = report["system_metrics"]
        if system_metrics:
            print(f"  CPU Usage: {system_metrics['cpu_usage']:.1f}%")
            print(f"  Memory Usage: {system_metrics['memory_usage']:.1f}%")
            print(f"  Disk Usage: {system_metrics['disk_usage']:.1f}%")
            print(f"  Active Crawls: {system_metrics['active_crawls']}")
            print(f"  Queue Size: {system_metrics['queue_size']}")
        else:
            print("  No system metrics available")

        print("\n🚨 Alerts (24h):")
        alerts = report["alerts"]
        print(f"  Total Alerts: {alerts['total_alerts_24h']}")
        print(f"  Critical: {alerts['critical_alerts']}")
        print(f"  High: {alerts['high_alerts']}")
        print(f"  Medium: {alerts['medium_alerts']}")
        print(f"  Low: {alerts['low_alerts']}")

        if report["recommendations"]:
            print("\n💡 Recommendations:")
            for rec in report["recommendations"]:
                print(f"  • {rec}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="IntelForge Crawler Monitor")
    parser.add_argument(
        "--config",
        default="config/monitor_config.json",
        help="Path to monitor configuration file",
    )
    parser.add_argument(
        "--run", action="store_true", help="Run continuous monitoring loop"
    )
    parser.add_argument(
        "--status", action="store_true", help="Show current monitoring status"
    )
    parser.add_argument(
        "--collect-metrics", action="store_true", help="Collect system metrics once"
    )
    parser.add_argument(
        "--generate-report", action="store_true", help="Generate monitoring report"
    )

    args = parser.parse_args()

    try:
        monitor = CrawlerMonitor(args.config)

        if args.run:
            monitor.run_monitoring_loop()
        elif args.status:
            monitor.show_status()
        elif args.collect_metrics:
            metric = monitor.collect_system_metrics()
            print(f"System metrics collected: {metric.to_dict()}")
        elif args.generate_report:
            report = monitor.generate_report()
            print(json.dumps(report, indent=2))
        else:
            print("Use --run, --status, --collect-metrics, or --generate-report")

    except Exception as e:
        logger.error(f"Monitor error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
