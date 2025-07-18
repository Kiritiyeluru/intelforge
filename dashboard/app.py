#!/usr/bin/env python3
"""
IntelForge Analytics Dashboard
Web-based dashboard for monitoring crawler performance and generating reports.
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

from flask import Flask, jsonify, render_template, request, send_file
from flask_cors import CORS

# Add the project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.crawler_monitor import CrawlerMonitor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize monitoring system
monitor = CrawlerMonitor()


class DashboardAnalytics:
    """Analytics engine for dashboard data processing"""

    def __init__(self, crawler_monitor: CrawlerMonitor):
        self.monitor = crawler_monitor

    def get_overview_stats(self) -> Dict[str, Any]:
        """Get high-level overview statistics"""
        report = self.monitor.generate_report()

        return {
            "system_status": report["system_status"],
            "total_crawls_24h": report["crawl_metrics"].get("total_crawls", 0),
            "success_rate": report["crawl_metrics"].get("success_rate", 0),
            "avg_execution_time": report["crawl_metrics"].get("avg_execution_time", 0),
            "total_content_extracted": report["crawl_metrics"].get(
                "total_content_extracted", 0
            ),
            "active_crawls": report["system_metrics"].get("active_crawls", 0),
            "queue_size": report["system_metrics"].get("queue_size", 0),
            "total_alerts_24h": report["alerts"].get("total_alerts_24h", 0),
        }

    def get_performance_trends(self, days: int = 7) -> Dict[str, Any]:
        """Get performance trends over specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)

        # Filter metrics by date
        crawl_metrics = [
            m for m in self.monitor.crawl_metrics if m.timestamp > cutoff_date
        ]
        system_metrics = [
            m for m in self.monitor.system_metrics if m.timestamp > cutoff_date
        ]

        if not crawl_metrics:
            return {"error": "No data available for specified period"}

        # Group by hour for visualization
        hourly_data = {}
        for metric in crawl_metrics:
            hour_key = metric.timestamp.replace(minute=0, second=0, microsecond=0)
            if hour_key not in hourly_data:
                hourly_data[hour_key] = {
                    "total_crawls": 0,
                    "successful_crawls": 0,
                    "total_execution_time": 0,
                    "total_content": 0,
                }

            hourly_data[hour_key]["total_crawls"] += 1
            if metric.success:
                hourly_data[hour_key]["successful_crawls"] += 1
            hourly_data[hour_key]["total_execution_time"] += metric.execution_time
            hourly_data[hour_key]["total_content"] += metric.content_extracted

        # Convert to time series
        timestamps = sorted(hourly_data.keys())
        success_rates = []
        avg_execution_times = []
        crawl_counts = []
        content_extracted = []

        for ts in timestamps:
            data = hourly_data[ts]
            success_rate = (
                data["successful_crawls"] / data["total_crawls"]
                if data["total_crawls"] > 0
                else 0
            )
            avg_time = (
                data["total_execution_time"] / data["total_crawls"]
                if data["total_crawls"] > 0
                else 0
            )

            success_rates.append(success_rate * 100)
            avg_execution_times.append(avg_time)
            crawl_counts.append(data["total_crawls"])
            content_extracted.append(data["total_content"])

        return {
            "timestamps": [ts.isoformat() for ts in timestamps],
            "success_rates": success_rates,
            "avg_execution_times": avg_execution_times,
            "crawl_counts": crawl_counts,
            "content_extracted": content_extracted,
        }

    def get_source_performance(self) -> Dict[str, Any]:
        """Get performance metrics grouped by source"""
        source_stats = {}

        for metric in self.monitor.crawl_metrics:
            source = metric.source_name
            if source not in source_stats:
                source_stats[source] = {
                    "total_crawls": 0,
                    "successful_crawls": 0,
                    "total_execution_time": 0,
                    "total_content": 0,
                    "last_crawl": None,
                }

            stats = source_stats[source]
            stats["total_crawls"] += 1
            if metric.success:
                stats["successful_crawls"] += 1
            stats["total_execution_time"] += metric.execution_time
            stats["total_content"] += metric.content_extracted

            if stats["last_crawl"] is None or metric.timestamp > stats["last_crawl"]:
                stats["last_crawl"] = metric.timestamp

        # Calculate derived metrics
        for source, stats in source_stats.items():
            stats["success_rate"] = (
                stats["successful_crawls"] / stats["total_crawls"]
                if stats["total_crawls"] > 0
                else 0
            )
            stats["avg_execution_time"] = (
                stats["total_execution_time"] / stats["total_crawls"]
                if stats["total_crawls"] > 0
                else 0
            )
            stats["avg_content_per_crawl"] = (
                stats["total_content"] / stats["total_crawls"]
                if stats["total_crawls"] > 0
                else 0
            )
            if stats["last_crawl"]:
                stats["last_crawl"] = stats["last_crawl"].isoformat()

        return source_stats

    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health metrics"""
        if not self.monitor.system_metrics:
            return {"error": "No system metrics available"}

        latest = self.monitor.system_metrics[-1]

        # Get recent metrics for trend analysis
        recent_metrics = self.monitor.system_metrics[-10:]  # Last 10 readings

        cpu_trend = [m.cpu_usage for m in recent_metrics]
        memory_trend = [m.memory_usage for m in recent_metrics]
        disk_trend = [m.disk_usage for m in recent_metrics]

        return {
            "current": {
                "cpu_usage": latest.cpu_usage,
                "memory_usage": latest.memory_usage,
                "disk_usage": latest.disk_usage,
                "active_crawls": latest.active_crawls,
                "queue_size": latest.queue_size,
                "timestamp": latest.timestamp.isoformat(),
            },
            "trends": {
                "cpu_usage": cpu_trend,
                "memory_usage": memory_trend,
                "disk_usage": disk_trend,
            },
            "health_status": self._calculate_health_status(latest),
        }

    def _calculate_health_status(self, metrics) -> str:
        """Calculate overall health status"""
        if (
            metrics.cpu_usage > 90
            or metrics.memory_usage > 90
            or metrics.disk_usage > 95
        ):
            return "critical"
        elif (
            metrics.cpu_usage > 80
            or metrics.memory_usage > 85
            or metrics.disk_usage > 90
        ):
            return "warning"
        else:
            return "healthy"

    def get_content_quality_analytics(self) -> Dict[str, Any]:
        """Analyze content quality trends"""
        if not self.monitor.crawl_metrics:
            return {"error": "No crawl metrics available"}

        # Group by day for quality analysis
        daily_quality = {}
        for metric in self.monitor.crawl_metrics:
            day_key = metric.timestamp.date()
            if day_key not in daily_quality:
                daily_quality[day_key] = {
                    "total_crawls": 0,
                    "total_content": 0,
                    "successful_crawls": 0,
                    "avg_threshold": 0,
                    "threshold_sum": 0,
                }

            stats = daily_quality[day_key]
            stats["total_crawls"] += 1
            stats["total_content"] += metric.content_extracted
            stats["threshold_sum"] += metric.threshold_used

            if metric.success:
                stats["successful_crawls"] += 1

        # Calculate quality metrics
        dates = sorted(daily_quality.keys())
        content_per_crawl = []
        quality_scores = []

        for date in dates:
            stats = daily_quality[date]
            avg_content = (
                stats["total_content"] / stats["total_crawls"]
                if stats["total_crawls"] > 0
                else 0
            )
            avg_threshold = (
                stats["threshold_sum"] / stats["total_crawls"]
                if stats["total_crawls"] > 0
                else 0
            )

            content_per_crawl.append(avg_content)
            quality_scores.append(avg_threshold)

        return {
            "dates": [d.isoformat() for d in dates],
            "content_per_crawl": content_per_crawl,
            "quality_scores": quality_scores,
            "total_content_extracted": sum(
                stats["total_content"] for stats in daily_quality.values()
            ),
        }


# Initialize analytics engine
analytics = DashboardAnalytics(monitor)


@app.route("/")
def dashboard():
    """Main dashboard page"""
    return render_template("dashboard.html")


@app.route("/api/overview")
def api_overview():
    """API endpoint for overview statistics"""
    try:
        stats = analytics.get_overview_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting overview stats: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/performance-trends")
def api_performance_trends():
    """API endpoint for performance trends"""
    try:
        days = request.args.get("days", 7, type=int)
        trends = analytics.get_performance_trends(days)
        return jsonify(trends)
    except Exception as e:
        logger.error(f"Error getting performance trends: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/source-performance")
def api_source_performance():
    """API endpoint for source performance metrics"""
    try:
        performance = analytics.get_source_performance()
        return jsonify(performance)
    except Exception as e:
        logger.error(f"Error getting source performance: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/system-health")
def api_system_health():
    """API endpoint for system health metrics"""
    try:
        health = analytics.get_system_health()
        return jsonify(health)
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/content-quality")
def api_content_quality():
    """API endpoint for content quality analytics"""
    try:
        quality = analytics.get_content_quality_analytics()
        return jsonify(quality)
    except Exception as e:
        logger.error(f"Error getting content quality: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/alerts")
def api_alerts():
    """API endpoint for recent alerts"""
    try:
        alert_log_file = Path("logs/alert_log.json")
        if not alert_log_file.exists():
            return jsonify([])

        with open(alert_log_file, "r") as f:
            alerts = json.load(f)

        # Get recent alerts
        cutoff = datetime.now() - timedelta(hours=24)
        recent_alerts = [
            a for a in alerts if datetime.fromisoformat(a["timestamp"]) > cutoff
        ]

        return jsonify(recent_alerts)
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/report/generate")
def api_generate_report():
    """Generate comprehensive report"""
    try:
        report = monitor.generate_report()

        # Add additional analytics
        report["performance_trends"] = analytics.get_performance_trends(7)
        report["source_performance"] = analytics.get_source_performance()
        report["content_quality"] = analytics.get_content_quality_analytics()

        return jsonify(report)
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/report/download")
def api_download_report():
    """Download report as JSON file"""
    try:
        report = monitor.generate_report()

        # Save report to temporary file
        report_file = Path("logs/dashboard_report.json")
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        return send_file(
            report_file,
            as_attachment=True,
            download_name=f'crawler_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
        )
    except Exception as e:
        logger.error(f"Error downloading report: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Create templates directory if it doesn't exist
    templates_dir = Path("dashboard/templates")
    templates_dir.mkdir(exist_ok=True)

    app.run(host="0.0.0.0", port=5000, debug=True)
