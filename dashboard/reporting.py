#!/usr/bin/env python3
"""
IntelForge Automated Stakeholder Reporting System
Generates and distributes automated reports to stakeholders.
"""

import argparse
import base64
import io
import json
import logging
import os
import smtplib
import sys
import time
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import schedule
from jinja2 import Template

# Add the project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dashboard.app import DashboardAnalytics
from scripts.crawler_monitor import CrawlerMonitor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StakeholderReporter:
    """Automated reporting system for stakeholders"""

    def __init__(self, config_path: str = "config/reporting_config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.monitor = CrawlerMonitor()
        self.analytics = DashboardAnalytics(self.monitor)

        # Create reports directory
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)

    def load_config(self) -> Dict:
        """Load reporting configuration"""
        default_config = {
            "email": {
                "enabled": True,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_name": "IntelForge Analytics",
            },
            "reports": {
                "daily": {
                    "enabled": True,
                    "time": "09:00",
                    "recipients": [],
                    "include_charts": True,
                    "include_alerts": True,
                },
                "weekly": {
                    "enabled": True,
                    "day": "monday",
                    "time": "09:00",
                    "recipients": [],
                    "include_detailed_analysis": True,
                    "include_performance_trends": True,
                },
                "monthly": {
                    "enabled": True,
                    "day": 1,
                    "time": "09:00",
                    "recipients": [],
                    "include_executive_summary": True,
                    "include_recommendations": True,
                },
            },
            "formatting": {
                "company_name": "IntelForge",
                "logo_url": "",
                "theme_color": "#667eea",
                "include_raw_data": False,
            },
        }

        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    config = json.load(f)
                # Merge with defaults
                return {**default_config, **config}
            except Exception as e:
                logger.warning(f"Error loading config: {e}, using defaults")

        # Save default config
        self.save_config(default_config)
        return default_config

    def save_config(self, config: Dict):
        """Save reporting configuration"""
        try:
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def generate_daily_report(self) -> Dict[str, Any]:
        """Generate daily report data"""
        logger.info("Generating daily report...")

        # Get data from last 24 hours
        report_data = {
            "report_type": "daily",
            "generated_at": datetime.now().isoformat(),
            "period": "24 hours",
            "overview": self.analytics.get_overview_stats(),
            "performance_trends": self.analytics.get_performance_trends(1),
            "source_performance": self.analytics.get_source_performance(),
            "system_health": self.analytics.get_system_health(),
            "content_quality": self.analytics.get_content_quality_analytics(),
            "alerts": self.get_recent_alerts(hours=24),
        }

        return report_data

    def generate_weekly_report(self) -> Dict[str, Any]:
        """Generate weekly report data"""
        logger.info("Generating weekly report...")

        report_data = {
            "report_type": "weekly",
            "generated_at": datetime.now().isoformat(),
            "period": "7 days",
            "overview": self.analytics.get_overview_stats(),
            "performance_trends": self.analytics.get_performance_trends(7),
            "source_performance": self.analytics.get_source_performance(),
            "system_health": self.analytics.get_system_health(),
            "content_quality": self.analytics.get_content_quality_analytics(),
            "alerts": self.get_recent_alerts(hours=168),  # 7 days
            "detailed_analysis": self.generate_detailed_analysis(),
            "performance_summary": self.generate_performance_summary(),
        }

        return report_data

    def generate_monthly_report(self) -> Dict[str, Any]:
        """Generate monthly report data"""
        logger.info("Generating monthly report...")

        report_data = {
            "report_type": "monthly",
            "generated_at": datetime.now().isoformat(),
            "period": "30 days",
            "overview": self.analytics.get_overview_stats(),
            "performance_trends": self.analytics.get_performance_trends(30),
            "source_performance": self.analytics.get_source_performance(),
            "system_health": self.analytics.get_system_health(),
            "content_quality": self.analytics.get_content_quality_analytics(),
            "alerts": self.get_recent_alerts(hours=720),  # 30 days
            "executive_summary": self.generate_executive_summary(),
            "recommendations": self.generate_recommendations(),
            "monthly_statistics": self.generate_monthly_statistics(),
        }

        return report_data

    def get_recent_alerts(self, hours: int) -> List[Dict]:
        """Get recent alerts within specified hours"""
        try:
            alert_log_file = Path("logs/alert_log.json")
            if not alert_log_file.exists():
                return []

            with open(alert_log_file, "r") as f:
                alerts = json.load(f)

            cutoff = datetime.now() - timedelta(hours=hours)
            return [
                a for a in alerts if datetime.fromisoformat(a["timestamp"]) > cutoff
            ]
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []

    def generate_detailed_analysis(self) -> Dict[str, Any]:
        """Generate detailed performance analysis"""
        source_performance = self.analytics.get_source_performance()

        # Calculate top performers
        top_sources = sorted(
            source_performance.items(), key=lambda x: x[1]["success_rate"], reverse=True
        )[:5]

        # Calculate problem sources
        problem_sources = sorted(
            source_performance.items(), key=lambda x: x[1]["success_rate"]
        )[:3]

        return {
            "top_performing_sources": top_sources,
            "problem_sources": problem_sources,
            "total_sources": len(source_performance),
            "avg_success_rate": (
                sum(s[1]["success_rate"] for s in source_performance.items())
                / len(source_performance)
                if source_performance
                else 0
            ),
        }

    def generate_performance_summary(self) -> Dict[str, Any]:
        """Generate performance summary"""
        trends = self.analytics.get_performance_trends(7)

        if "error" in trends:
            return {"error": trends["error"]}

        avg_success_rate = (
            sum(trends["success_rates"]) / len(trends["success_rates"])
            if trends["success_rates"]
            else 0
        )
        avg_execution_time = (
            sum(trends["avg_execution_times"]) / len(trends["avg_execution_times"])
            if trends["avg_execution_times"]
            else 0
        )
        total_crawls = sum(trends["crawl_counts"])

        return {
            "avg_success_rate": avg_success_rate,
            "avg_execution_time": avg_execution_time,
            "total_crawls": total_crawls,
            "total_content_extracted": sum(trends["content_extracted"]),
        }

    def generate_executive_summary(self) -> Dict[str, Any]:
        """Generate executive summary"""
        overview = self.analytics.get_overview_stats()

        # Calculate key metrics
        uptime_percentage = 100 - (
            overview["total_alerts_24h"] * 5
        )  # Simplified calculation
        performance_score = overview["success_rate"] * 100

        return {
            "system_uptime": max(0, uptime_percentage),
            "performance_score": performance_score,
            "total_data_processed": overview["total_content_extracted"],
            "operational_efficiency": overview["success_rate"],
            "key_insights": [
                f"System achieved {performance_score:.1f}% performance score",
                f"Processed {overview['total_content_extracted']} content items",
                f"Maintained {overview['success_rate']:.1%} success rate",
            ],
        }

    def generate_recommendations(self) -> List[str]:
        """Generate system recommendations"""
        recommendations = []

        overview = self.analytics.get_overview_stats()
        system_health = self.analytics.get_system_health()

        # Performance recommendations
        if overview["success_rate"] < 0.8:
            recommendations.append(
                "Consider investigating crawler failures to improve success rate"
            )

        if not system_health.get("error"):
            current = system_health["current"]
            if current["cpu_usage"] > 70:
                recommendations.append(
                    "High CPU usage detected - consider optimizing crawl frequency"
                )
            if current["memory_usage"] > 80:
                recommendations.append(
                    "High memory usage - consider implementing memory cleanup"
                )
            if current["disk_usage"] > 85:
                recommendations.append(
                    "Disk space running low - consider implementing data archiving"
                )

        # Content quality recommendations
        if overview["total_content_extracted"] < 100:
            recommendations.append(
                "Low content extraction - review source quality and extraction rules"
            )

        return recommendations

    def generate_monthly_statistics(self) -> Dict[str, Any]:
        """Generate monthly statistics"""
        # This would typically involve more complex calculations
        # For now, returning basic stats
        return {
            "total_crawl_hours": 720,  # 30 days * 24 hours
            "estimated_data_volume": "~5GB",
            "cost_savings": "$2,500",  # Estimated vs manual data collection
            "automation_efficiency": "95%",
        }

    def create_chart_images(self, report_data: Dict[str, Any]) -> Dict[str, str]:
        """Create chart images for email reports"""
        charts = {}

        try:
            # Performance trend chart
            trends = report_data.get("performance_trends", {})
            if not trends.get("error") and trends.get("success_rates"):
                plt.figure(figsize=(10, 6))
                plt.plot(trends["success_rates"], marker="o", color="#28a745")
                plt.title("Success Rate Trend")
                plt.ylabel("Success Rate (%)")
                plt.xlabel("Time Period")
                plt.grid(True, alpha=0.3)

                # Save to base64 string
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format="png", bbox_inches="tight", dpi=150)
                img_buffer.seek(0)
                charts["success_rate_chart"] = base64.b64encode(
                    img_buffer.read()
                ).decode()
                plt.close()

            # System health chart
            system_health = report_data.get("system_health", {})
            if not system_health.get("error"):
                current = system_health["current"]

                plt.figure(figsize=(8, 6))
                metrics = ["CPU", "Memory", "Disk"]
                values = [
                    current["cpu_usage"],
                    current["memory_usage"],
                    current["disk_usage"],
                ]
                colors = ["#007bff", "#28a745", "#ffc107"]

                bars = plt.bar(metrics, values, color=colors)
                plt.title("System Resource Usage")
                plt.ylabel("Usage (%)")
                plt.ylim(0, 100)

                # Add value labels on bars
                for bar, value in zip(bars, values):
                    plt.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 1,
                        f"{value:.1f}%",
                        ha="center",
                        va="bottom",
                    )

                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format="png", bbox_inches="tight", dpi=150)
                img_buffer.seek(0)
                charts["system_health_chart"] = base64.b64encode(
                    img_buffer.read()
                ).decode()
                plt.close()

        except Exception as e:
            logger.error(f"Error creating charts: {e}")

        return charts

    def format_html_report(self, report_data: Dict[str, Any]) -> str:
        """Format report data as HTML"""

        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{{ report_type.title() }} Report - {{ company_name }}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
                .header { background: linear-gradient(135deg, {{ theme_color }} 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
                .section { background: white; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .metric { display: inline-block; margin: 10px; padding: 15px; background: #f8f9fa; border-radius: 8px; min-width: 150px; text-align: center; }
                .metric-value { font-size: 24px; font-weight: bold; color: {{ theme_color }}; }
                .metric-label { font-size: 12px; color: #666; text-transform: uppercase; }
                .status-healthy { color: #28a745; }
                .status-warning { color: #ffc107; }
                .status-critical { color: #dc3545; }
                .status-degraded { color: #fd7e14; }
                .alert-item { padding: 10px; margin: 5px 0; border-left: 4px solid; border-radius: 0 5px 5px 0; }
                .alert-critical { border-left-color: #dc3545; background-color: #f8d7da; }
                .alert-high { border-left-color: #fd7e14; background-color: #fff3cd; }
                .alert-medium { border-left-color: #ffc107; background-color: #fff3cd; }
                .alert-low { border-left-color: #17a2b8; background-color: #d1ecf1; }
                .recommendation { padding: 10px; margin: 5px 0; background: #e7f3ff; border-left: 4px solid #007bff; border-radius: 0 5px 5px 0; }
                .chart-container { text-align: center; margin: 20px 0; }
                .chart-container img { max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #f8f9fa; }
                .footer { text-align: center; color: #666; margin-top: 40px; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ report_type.title() }} Report</h1>
                <p>Generated on {{ generated_at }} | Period: {{ period }}</p>
            </div>

            <div class="section">
                <h2>📊 Overview</h2>
                <div class="metric">
                    <div class="metric-value status-{{ overview.system_status }}">{{ overview.system_status.upper() }}</div>
                    <div class="metric-label">System Status</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ overview.total_crawls_24h }}</div>
                    <div class="metric-label">Total Crawls</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ "%.1f"|format(overview.success_rate * 100) }}%</div>
                    <div class="metric-label">Success Rate</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ overview.total_content_extracted }}</div>
                    <div class="metric-label">Content Extracted</div>
                </div>
            </div>

            {% if charts.success_rate_chart %}
            <div class="section">
                <h2>📈 Performance Trends</h2>
                <div class="chart-container">
                    <img src="data:image/png;base64,{{ charts.success_rate_chart }}" alt="Success Rate Chart">
                </div>
            </div>
            {% endif %}

            {% if charts.system_health_chart %}
            <div class="section">
                <h2>🖥️ System Health</h2>
                <div class="chart-container">
                    <img src="data:image/png;base64,{{ charts.system_health_chart }}" alt="System Health Chart">
                </div>
            </div>
            {% endif %}

            {% if alerts %}
            <div class="section">
                <h2>🚨 Recent Alerts</h2>
                {% for alert in alerts[-10:] %}
                <div class="alert-item alert-{{ alert.severity }}">
                    <strong>{{ alert.alert_name }}</strong><br>
                    <small>{{ alert.timestamp }}</small>
                </div>
                {% endfor %}
            </div>
            {% endif %}

            {% if recommendations %}
            <div class="section">
                <h2>💡 Recommendations</h2>
                {% for rec in recommendations %}
                <div class="recommendation">{{ rec }}</div>
                {% endfor %}
            </div>
            {% endif %}

            <div class="footer">
                <p>This report was automatically generated by {{ company_name }} Analytics Dashboard</p>
            </div>
        </body>
        </html>
        """

        template = Template(template_str)

        # Create charts if enabled
        charts = {}
        if (
            self.config["reports"]
            .get(report_data["report_type"], {})
            .get("include_charts", False)
        ):
            charts = self.create_chart_images(report_data)

        return template.render(
            **report_data,
            charts=charts,
            company_name=self.config["formatting"]["company_name"],
            theme_color=self.config["formatting"]["theme_color"],
        )

    def send_email_report(self, report_data: Dict[str, Any], recipients: List[str]):
        """Send email report to recipients"""
        if not self.config["email"]["enabled"] or not recipients:
            logger.info("Email reporting disabled or no recipients configured")
            return

        try:
            # Generate HTML report
            html_content = self.format_html_report(report_data)

            # Create email
            msg = MIMEMultipart("alternative")
            msg["Subject"] = (
                f"{report_data['report_type'].title()} Report - {self.config['formatting']['company_name']}"
            )
            msg["From"] = (
                f"{self.config['email']['from_name']} <{self.config['email']['username']}>"
            )
            msg["To"] = ", ".join(recipients)

            # Add HTML content
            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)

            # Add JSON attachment if enabled
            if self.config["formatting"]["include_raw_data"]:
                json_data = json.dumps(report_data, indent=2)
                attachment = MIMEText(json_data)
                attachment.add_header(
                    "Content-Disposition", "attachment", filename="report_data.json"
                )
                msg.attach(attachment)

            # Send email
            with smtplib.SMTP(
                self.config["email"]["smtp_server"], self.config["email"]["smtp_port"]
            ) as server:
                server.starttls()
                server.login(
                    self.config["email"]["username"], self.config["email"]["password"]
                )
                server.send_message(msg)

            logger.info(f"Email report sent to {len(recipients)} recipients")

        except Exception as e:
            logger.error(f"Error sending email report: {e}")

    def save_report(self, report_data: Dict[str, Any]):
        """Save report to file"""
        try:
            report_type = report_data["report_type"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Save JSON report
            json_file = self.reports_dir / f"{report_type}_report_{timestamp}.json"
            with open(json_file, "w") as f:
                json.dump(report_data, f, indent=2)

            # Save HTML report
            html_content = self.format_html_report(report_data)
            html_file = self.reports_dir / f"{report_type}_report_{timestamp}.html"
            with open(html_file, "w") as f:
                f.write(html_content)

            logger.info(f"Report saved to {json_file} and {html_file}")

        except Exception as e:
            logger.error(f"Error saving report: {e}")

    def generate_and_send_report(self, report_type: str):
        """Generate and send report of specified type"""
        try:
            # Generate report data
            if report_type == "daily":
                report_data = self.generate_daily_report()
                recipients = self.config["reports"]["daily"]["recipients"]
            elif report_type == "weekly":
                report_data = self.generate_weekly_report()
                recipients = self.config["reports"]["weekly"]["recipients"]
            elif report_type == "monthly":
                report_data = self.generate_monthly_report()
                recipients = self.config["reports"]["monthly"]["recipients"]
            else:
                raise ValueError(f"Unknown report type: {report_type}")

            # Save report
            self.save_report(report_data)

            # Send email
            self.send_email_report(report_data, recipients)

            logger.info(f"Successfully generated and sent {report_type} report")

        except Exception as e:
            logger.error(f"Error generating {report_type} report: {e}")

    def schedule_reports(self):
        """Schedule automated reports"""
        logger.info("Setting up automated report scheduling...")

        # Schedule daily reports
        if self.config["reports"]["daily"]["enabled"]:
            time_str = self.config["reports"]["daily"]["time"]
            schedule.every().day.at(time_str).do(self.generate_and_send_report, "daily")
            logger.info(f"Daily reports scheduled at {time_str}")

        # Schedule weekly reports
        if self.config["reports"]["weekly"]["enabled"]:
            day = self.config["reports"]["weekly"]["day"]
            time_str = self.config["reports"]["weekly"]["time"]
            getattr(schedule.every(), day).at(time_str).do(
                self.generate_and_send_report, "weekly"
            )
            logger.info(f"Weekly reports scheduled on {day} at {time_str}")

        # Schedule monthly reports
        if self.config["reports"]["monthly"]["enabled"]:
            # Monthly scheduling is more complex, using day of month
            schedule.every().day.at(self.config["reports"]["monthly"]["time"]).do(
                self.check_monthly_report
            )
            logger.info("Monthly reports scheduled")

        logger.info("Report scheduling complete")

    def check_monthly_report(self):
        """Check if monthly report should be generated"""
        today = datetime.now().day
        target_day = self.config["reports"]["monthly"]["day"]

        if today == target_day:
            self.generate_and_send_report("monthly")

    def run_scheduler(self):
        """Run the report scheduler"""
        self.schedule_reports()

        logger.info("Starting report scheduler...")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="IntelForge Stakeholder Reporter")
    parser.add_argument(
        "--config",
        default="config/reporting_config.json",
        help="Path to reporting configuration file",
    )
    parser.add_argument(
        "--generate",
        choices=["daily", "weekly", "monthly"],
        help="Generate specific report type",
    )
    parser.add_argument(
        "--schedule", action="store_true", help="Run automated report scheduler"
    )
    parser.add_argument(
        "--test-email", action="store_true", help="Send test email report"
    )

    args = parser.parse_args()

    try:
        reporter = StakeholderReporter(args.config)

        if args.generate:
            reporter.generate_and_send_report(args.generate)
        elif args.schedule:
            reporter.run_scheduler()
        elif args.test_email:
            # Generate a daily report for testing
            report_data = reporter.generate_daily_report()
            test_recipients = ["test@example.com"]  # Replace with actual test email
            reporter.send_email_report(report_data, test_recipients)
        else:
            print("Use --generate, --schedule, or --test-email")

    except Exception as e:
        logger.error(f"Reporter error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
