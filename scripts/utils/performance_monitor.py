#!/usr/bin/env python3
"""
Performance monitoring for IntelForge
Implements psutil-based timing/memory monitoring with verbose flags and metrics collection
"""

import json
import logging
import threading
import time
from collections import defaultdict, deque
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import psutil


@dataclass
class PerformanceMetric:
    """Data class for performance metric tracking"""

    operation: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    cpu_percent_before: Optional[float] = None
    cpu_percent_after: Optional[float] = None
    memory_mb_before: Optional[float] = None
    memory_mb_after: Optional[float] = None
    memory_peak_mb: Optional[float] = None
    disk_io_before: Optional[Dict[str, int]] = None
    disk_io_after: Optional[Dict[str, int]] = None
    network_io_before: Optional[Dict[str, int]] = None
    network_io_after: Optional[Dict[str, int]] = None
    custom_metrics: Dict[str, Any] = None

    def __post_init__(self):
        if self.custom_metrics is None:
            self.custom_metrics = {}

    @property
    def cpu_usage_delta(self) -> Optional[float]:
        """Calculate CPU usage change during operation"""
        if self.cpu_percent_before is not None and self.cpu_percent_after is not None:
            return self.cpu_percent_after - self.cpu_percent_before
        return None

    @property
    def memory_usage_delta_mb(self) -> Optional[float]:
        """Calculate memory usage change during operation"""
        if self.memory_mb_before is not None and self.memory_mb_after is not None:
            return self.memory_mb_after - self.memory_mb_before
        return None


class PerformanceMonitor:
    """
    Comprehensive performance monitoring system for IntelForge
    Provides CPU, memory, disk, and network monitoring with detailed metrics
    """

    def __init__(
        self,
        enable_verbose: bool = False,
        sample_interval: float = 0.1,
        max_history: int = 1000,
        data_dir: Optional[Path] = None,
    ):

        self.enable_verbose = enable_verbose
        self.sample_interval = sample_interval
        self.max_history = max_history
        self.data_dir = (
            data_dir or Path(__file__).parent.parent.parent / "logs" / "performance"
        )
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(__name__)

        # Metrics storage
        self.metrics_history: deque = deque(maxlen=max_history)
        self.active_monitors: Dict[str, Dict[str, Any]] = {}
        self.operation_stats: Dict[str, List[PerformanceMetric]] = defaultdict(list)

        # System baseline
        self.system_baseline = self._capture_system_baseline()

        # Performance thresholds
        self.thresholds = {
            "cpu_percent_warning": 80.0,
            "cpu_percent_critical": 95.0,
            "memory_mb_warning": 1024,  # 1GB
            "memory_mb_critical": 2048,  # 2GB
            "duration_seconds_warning": 30.0,
            "duration_seconds_critical": 120.0,
        }

        # Background monitoring
        self._monitoring_active = False
        self._monitoring_thread = None

        if self.enable_verbose:
            self.logger.info(
                "Performance monitoring initialized",
                extra={"baseline": self.system_baseline, "thresholds": self.thresholds},
            )

    def _capture_system_baseline(self) -> Dict[str, Any]:
        """Capture system baseline metrics"""
        try:
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "timestamp": datetime.now().isoformat(),
                "cpu_count": cpu_count,
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "memory_percent": memory.percent,
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "disk_percent": round((disk.used / disk.total) * 100, 2),
            }
        except Exception as e:
            self.logger.error(f"Failed to capture system baseline: {e}")
            return {"error": str(e)}

    def _get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            process = psutil.Process()
            cpu_percent = process.cpu_percent()
            memory_info = process.memory_info()

            # System-wide metrics
            sys_cpu = psutil.cpu_percent()
            sys_memory = psutil.virtual_memory()

            # I/O metrics
            try:
                disk_io = (
                    psutil.disk_io_counters()._asdict()
                    if psutil.disk_io_counters()
                    else {}
                )
            except:
                disk_io = {}

            try:
                network_io = (
                    psutil.net_io_counters()._asdict()
                    if psutil.net_io_counters()
                    else {}
                )
            except:
                network_io = {}

            return {
                "timestamp": time.time(),
                "process_cpu_percent": cpu_percent,
                "process_memory_mb": round(memory_info.rss / (1024**2), 2),
                "process_memory_vms_mb": round(memory_info.vms / (1024**2), 2),
                "system_cpu_percent": sys_cpu,
                "system_memory_percent": sys_memory.percent,
                "system_memory_available_gb": round(
                    sys_memory.available / (1024**3), 2
                ),
                "disk_io": disk_io,
                "network_io": network_io,
            }
        except Exception as e:
            self.logger.error(f"Failed to get current metrics: {e}")
            return {"error": str(e)}

    @contextmanager
    def monitor_operation(self, operation_name: str, **custom_metrics):
        """
        Context manager for monitoring operation performance

        Args:
            operation_name: Name of the operation being monitored
            **custom_metrics: Additional custom metrics to track
        """
        operation_id = f"{operation_name}_{int(time.time() * 1000)}"

        if self.enable_verbose:
            self.logger.info(f"Starting performance monitoring for: {operation_name}")

        # Capture initial state
        start_metrics = self._get_current_metrics()
        start_time = datetime.now()

        metric = PerformanceMetric(
            operation=operation_name,
            start_time=start_time,
            cpu_percent_before=start_metrics.get("process_cpu_percent"),
            memory_mb_before=start_metrics.get("process_memory_mb"),
            disk_io_before=start_metrics.get("disk_io"),
            network_io_before=start_metrics.get("network_io"),
            custom_metrics=custom_metrics.copy(),
        )

        # Track peak memory usage
        peak_memory = start_metrics.get("process_memory_mb", 0)

        # Store active monitor
        self.active_monitors[operation_id] = {
            "metric": metric,
            "peak_memory": peak_memory,
            "samples": [],
        }

        try:
            yield operation_id

        except Exception as e:
            # Record exception in custom metrics
            metric.custom_metrics["exception"] = {
                "type": type(e).__name__,
                "message": str(e),
            }
            raise

        finally:
            # Capture final state
            end_metrics = self._get_current_metrics()
            end_time = datetime.now()

            # Update metric with final values
            metric.end_time = end_time
            metric.duration_seconds = (end_time - start_time).total_seconds()
            metric.cpu_percent_after = end_metrics.get("process_cpu_percent")
            metric.memory_mb_after = end_metrics.get("process_memory_mb")
            metric.memory_peak_mb = self.active_monitors[operation_id]["peak_memory"]
            metric.disk_io_after = end_metrics.get("disk_io")
            metric.network_io_after = end_metrics.get("network_io")

            # Store in history
            self.metrics_history.append(metric)
            self.operation_stats[operation_name].append(metric)

            # Clean up active monitor
            del self.active_monitors[operation_id]

            # Log performance results
            self._log_operation_results(metric)

            # Save to file if enabled
            if self.enable_verbose:
                self._save_metric_to_file(metric)

    def _log_operation_results(self, metric: PerformanceMetric):
        """Log operation performance results"""
        duration = metric.duration_seconds
        memory_delta = metric.memory_usage_delta_mb
        cpu_delta = metric.cpu_usage_delta

        # Determine log level based on thresholds
        log_level = "INFO"
        warnings = []

        if duration > self.thresholds["duration_seconds_critical"]:
            log_level = "ERROR"
            warnings.append(f"Duration exceeded critical threshold: {duration:.2f}s")
        elif duration > self.thresholds["duration_seconds_warning"]:
            log_level = "WARNING"
            warnings.append(f"Duration exceeded warning threshold: {duration:.2f}s")

        if (
            metric.memory_mb_after
            and metric.memory_mb_after > self.thresholds["memory_mb_critical"]
        ):
            log_level = "ERROR"
            warnings.append(f"Memory usage critical: {metric.memory_mb_after:.1f}MB")
        elif (
            metric.memory_mb_after
            and metric.memory_mb_after > self.thresholds["memory_mb_warning"]
        ):
            if log_level == "INFO":
                log_level = "WARNING"
            warnings.append(f"Memory usage high: {metric.memory_mb_after:.1f}MB")

        # Create log message
        message = f"Operation '{metric.operation}' completed in {duration:.2f}s"
        if memory_delta:
            message += f", memory delta: {memory_delta:+.1f}MB"
        if cpu_delta:
            message += f", CPU delta: {cpu_delta:+.1f}%"

        extra_data = {
            "operation": metric.operation,
            "duration_seconds": duration,
            "memory_mb_final": metric.memory_mb_after,
            "memory_delta_mb": memory_delta,
            "cpu_delta_percent": cpu_delta,
            "memory_peak_mb": metric.memory_peak_mb,
            "warnings": warnings,
            "performance_score": self._calculate_performance_score(metric),
        }

        # Log with appropriate level
        if log_level == "ERROR":
            self.logger.error(message, extra=extra_data)
        elif log_level == "WARNING":
            self.logger.warning(message, extra=extra_data)
        else:
            self.logger.info(message, extra=extra_data)

    def _calculate_performance_score(self, metric: PerformanceMetric) -> float:
        """
        Calculate a performance score (0-100) based on multiple factors
        Higher is better
        """
        score = 100.0

        # Duration penalty
        if metric.duration_seconds:
            if metric.duration_seconds > self.thresholds["duration_seconds_critical"]:
                score -= 40
            elif metric.duration_seconds > self.thresholds["duration_seconds_warning"]:
                score -= 20

        # Memory penalty
        if metric.memory_mb_after:
            if metric.memory_mb_after > self.thresholds["memory_mb_critical"]:
                score -= 30
            elif metric.memory_mb_after > self.thresholds["memory_mb_warning"]:
                score -= 15

        # Memory growth penalty
        memory_delta = metric.memory_usage_delta_mb
        if memory_delta and memory_delta > 100:  # More than 100MB growth
            score -= min(20, memory_delta / 50)  # Penalty increases with growth

        # Exception penalty
        if metric.custom_metrics.get("exception"):
            score -= 25

        return max(0.0, min(100.0, score))

    def _save_metric_to_file(self, metric: PerformanceMetric):
        """Save performance metric to file"""
        try:
            metrics_file = (
                self.data_dir
                / f"performance_metrics_{datetime.now().strftime('%Y%m%d')}.jsonl"
            )

            metric_dict = asdict(metric)
            # Convert datetime objects to ISO strings
            metric_dict["start_time"] = metric.start_time.isoformat()
            if metric.end_time:
                metric_dict["end_time"] = metric.end_time.isoformat()

            with open(metrics_file, "a") as f:
                f.write(json.dumps(metric_dict, default=str) + "\n")

        except Exception as e:
            self.logger.error(f"Failed to save metric to file: {e}")

    def get_operation_statistics(self, operation_name: str = None) -> Dict[str, Any]:
        """
        Get statistics for operations

        Args:
            operation_name: Specific operation name (None for all)

        Returns:
            dict: Operation statistics
        """
        if operation_name:
            metrics = self.operation_stats.get(operation_name, [])
            operations = {operation_name: metrics}
        else:
            operations = dict(self.operation_stats)

        stats = {}

        for op_name, op_metrics in operations.items():
            if not op_metrics:
                continue

            durations = [m.duration_seconds for m in op_metrics if m.duration_seconds]
            memory_usage = [m.memory_mb_after for m in op_metrics if m.memory_mb_after]
            memory_deltas = [
                m.memory_usage_delta_mb for m in op_metrics if m.memory_usage_delta_mb
            ]

            stats[op_name] = {
                "total_executions": len(op_metrics),
                "avg_duration_seconds": (
                    sum(durations) / len(durations) if durations else 0
                ),
                "max_duration_seconds": max(durations) if durations else 0,
                "min_duration_seconds": min(durations) if durations else 0,
                "avg_memory_mb": (
                    sum(memory_usage) / len(memory_usage) if memory_usage else 0
                ),
                "max_memory_mb": max(memory_usage) if memory_usage else 0,
                "avg_memory_delta_mb": (
                    sum(memory_deltas) / len(memory_deltas) if memory_deltas else 0
                ),
                "exception_count": sum(
                    1 for m in op_metrics if m.custom_metrics.get("exception")
                ),
                "avg_performance_score": sum(
                    self._calculate_performance_score(m) for m in op_metrics
                )
                / len(op_metrics),
            }

        return stats

    def start_background_monitoring(self, interval: float = 5.0):
        """Start background system monitoring"""
        if self._monitoring_active:
            self.logger.warning("Background monitoring already active")
            return

        self._monitoring_active = True

        def monitor_loop():
            while self._monitoring_active:
                try:
                    metrics = self._get_current_metrics()
                    metrics["monitoring_type"] = "background"

                    # Update peak memory for active operations
                    current_memory = metrics.get("process_memory_mb", 0)
                    for monitor_data in self.active_monitors.values():
                        if current_memory > monitor_data["peak_memory"]:
                            monitor_data["peak_memory"] = current_memory
                        monitor_data["samples"].append(metrics)

                    time.sleep(interval)

                except Exception as e:
                    self.logger.error(f"Background monitoring error: {e}")
                    time.sleep(interval)

        self._monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitoring_thread.start()

        self.logger.info(f"Started background monitoring with {interval}s interval")

    def stop_background_monitoring(self):
        """Stop background system monitoring"""
        if not self._monitoring_active:
            return

        self._monitoring_active = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5.0)

        self.logger.info("Stopped background monitoring")

    def export_performance_report(
        self, filename: Optional[str] = None, format_type: str = "json"
    ) -> Path:
        """
        Export comprehensive performance report

        Args:
            filename: Optional custom filename
            format_type: Export format ("json", "csv", "markdown")

        Returns:
            Path: Path to exported report
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.{format_type}"

        export_path = self.data_dir / filename

        # Compile report data
        report_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_operations": len(self.metrics_history),
                "monitoring_enabled": self.enable_verbose,
                "system_baseline": self.system_baseline,
            },
            "operation_statistics": self.get_operation_statistics(),
            "recent_metrics": [
                asdict(m) for m in list(self.metrics_history)[-50:]
            ],  # Last 50 operations
            "thresholds": self.thresholds,
        }

        if format_type.lower() == "json":
            with open(export_path, "w") as f:
                json.dump(report_data, f, indent=2, default=str)

        elif format_type.lower() == "markdown":
            self._export_markdown_report(export_path, report_data)

        else:
            # Default to JSON
            with open(export_path, "w") as f:
                json.dump(report_data, f, indent=2, default=str)

        self.logger.info(f"Exported performance report to {export_path}")
        return export_path

    def _export_markdown_report(self, export_path: Path, report_data: Dict[str, Any]):
        """Export performance report in Markdown format"""
        with open(export_path, "w") as f:
            f.write("# Performance Monitoring Report\n\n")
            f.write(f"**Generated:** {report_data['metadata']['generated_at']}\n")
            f.write(
                f"**Total Operations:** {report_data['metadata']['total_operations']}\n\n"
            )

            # System baseline
            baseline = report_data["metadata"]["system_baseline"]
            if "error" not in baseline:
                f.write("## System Baseline\n\n")
                f.write(f"- **CPU Count:** {baseline.get('cpu_count', 'N/A')}\n")
                f.write(
                    f"- **Memory Total:** {baseline.get('memory_total_gb', 'N/A')} GB\n"
                )
                f.write(
                    f"- **Disk Total:** {baseline.get('disk_total_gb', 'N/A')} GB\n\n"
                )

            # Operation statistics
            stats = report_data["operation_statistics"]
            if stats:
                f.write("## Operation Statistics\n\n")
                f.write(
                    "| Operation | Executions | Avg Duration (s) | Avg Memory (MB) | Performance Score |\n"
                )
                f.write(
                    "|-----------|------------|------------------|-----------------|-------------------|\n"
                )

                for op_name, op_stats in stats.items():
                    f.write(
                        f"| {op_name} | {op_stats['total_executions']} | "
                        f"{op_stats['avg_duration_seconds']:.2f} | "
                        f"{op_stats['avg_memory_mb']:.1f} | "
                        f"{op_stats['avg_performance_score']:.1f} |\n"
                    )
                f.write("\n")

            # Thresholds
            f.write("## Performance Thresholds\n\n")
            thresholds = report_data["thresholds"]
            for key, value in thresholds.items():
                f.write(f"- **{key.replace('_', ' ').title()}:** {value}\n")


# Global instance management
_global_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor(enable_verbose: bool = False) -> PerformanceMonitor:
    """Get or create the global performance monitor instance"""
    global _global_performance_monitor

    if _global_performance_monitor is None:
        _global_performance_monitor = PerformanceMonitor(enable_verbose=enable_verbose)

    return _global_performance_monitor


# Convenience functions and decorators
def monitor_performance(operation_name: str, **custom_metrics):
    """Decorator for monitoring function performance"""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            with monitor.monitor_operation(operation_name, **custom_metrics):
                return func(*args, **kwargs)

        return wrapper

    return decorator


@contextmanager
def performance_context(operation_name: str, verbose: bool = False, **custom_metrics):
    """Convenience context manager for performance monitoring"""
    monitor = get_performance_monitor(enable_verbose=verbose)
    with monitor.monitor_operation(operation_name, **custom_metrics):
        yield


# CLI integration helpers
def setup_cli_performance_monitoring(verbose: bool = False) -> PerformanceMonitor:
    """Setup performance monitoring for CLI applications"""
    monitor = get_performance_monitor(enable_verbose=verbose)

    if verbose:
        monitor.start_background_monitoring(interval=2.0)

    return monitor


# Example usage and testing
if __name__ == "__main__":
    import random

    # Example usage
    monitor = PerformanceMonitor(enable_verbose=True)
    monitor.start_background_monitoring()

    # Test operations
    @monitor_performance("data_processing", dataset_size=1000)
    def example_operation():
        # Simulate some work
        data = [random.random() for _ in range(100000)]
        result = sum(data)
        time.sleep(0.1)
        return result

    # Run test operations
    for i in range(3):
        with performance_context(f"test_operation_{i}", verbose=True, iteration=i):
            example_operation()
            time.sleep(0.05)

    # Get statistics
    stats = monitor.get_operation_statistics()
    print("Performance Statistics:")
    print(json.dumps(stats, indent=2))

    # Export report
    report_path = monitor.export_performance_report(format_type="markdown")
    print(f"Performance report exported to: {report_path}")

    # Stop monitoring
    monitor.stop_background_monitoring()

    print("Performance monitoring example completed!")
