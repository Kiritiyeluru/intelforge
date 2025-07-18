#!/usr/bin/env python3
"""
Structured logging system for IntelForge
Implements loguru/rich integration with JSON formatting and context tracking
"""

import json
import sys
import threading
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress
from rich.table import Table
from rich.traceback import install as install_rich_traceback


class StructuredLogger:
    """
    Advanced structured logging system for IntelForge
    Combines loguru's power with rich's beautiful formatting
    """

    def __init__(
        self,
        app_name: str = "IntelForge",
        log_level: str = "INFO",
        enable_rich: bool = True,
        enable_json: bool = True,
        log_dir: Optional[Path] = None,
    ):

        self.app_name = app_name
        self.log_level = log_level.upper()
        self.enable_rich = enable_rich
        self.enable_json = enable_json
        self.console = Console() if enable_rich else None
        self.context_stack = threading.local()
        self.session_id = f"{app_name}_{int(time.time())}"

        # Setup log directory
        self.log_dir = log_dir or Path(__file__).parent.parent.parent / "logs"
        self.log_dir.mkdir(exist_ok=True)

        # Install rich traceback for better error display
        if enable_rich:
            install_rich_traceback(show_locals=True)

        # Initialize loguru
        self._setup_loguru()

        # Track operation metrics
        self.operation_metrics = {}
        self.active_operations = {}

    def _setup_loguru(self):
        """Configure loguru with custom formatters"""
        # Remove default handler
        logger.remove()

        # Rich console handler (if enabled)
        if self.enable_rich:
            logger.add(
                RichHandler(console=self.console, rich_tracebacks=True),
                level=self.log_level,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
                enqueue=True,
                backtrace=True,
                diagnose=True,
            )
        else:
            # Standard console handler
            logger.add(
                sys.stderr,
                level=self.log_level,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
                enqueue=True,
            )

        # JSON file handler (if enabled)
        if self.enable_json:
            json_file = self.log_dir / f"{self.app_name.lower()}_structured.log"
            logger.add(
                json_file,
                level=self.log_level,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message} | {extra}",
                enqueue=True,
                rotation="10 MB",
                retention="7 days",
                compression="gz",
                serialize=True,
            )

        # Standard text file handler
        text_file = self.log_dir / f"{self.app_name.lower()}.log"
        logger.add(
            text_file,
            level=self.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            enqueue=True,
            rotation="50 MB",
            retention="14 days",
            compression="gz",
        )

        # Error-only file
        error_file = self.log_dir / f"{self.app_name.lower()}_errors.log"
        logger.add(
            error_file,
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            enqueue=True,
            rotation="10 MB",
            retention="30 days",
        )

    def _json_formatter(self, record: Dict[str, Any]) -> str:
        """Custom JSON formatter for structured logs"""
        # Get context from thread local storage
        context = getattr(self.context_stack, "context", {})

        json_record = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "logger": record["name"],
            "module": record["name"].split(".")[-1],
            "function": record["function"],
            "line": record["line"],
            "message": record["message"],
            "session_id": self.session_id,
            "thread_id": record["thread"].id,
            "process_id": record["process"].id,
            **context,  # Add context data
        }

        # Add exception info if present
        if record["exception"]:
            json_record["exception"] = {
                "type": record["exception"].type.__name__,
                "value": str(record["exception"].value),
                "traceback": record["exception"].traceback,
            }

        # Add extra fields from record
        extra = record.get("extra", {})
        if extra:
            json_record["extra"] = extra

        return json.dumps(json_record, ensure_ascii=False)

    @contextmanager
    def context(self, **kwargs):
        """Context manager for adding structured context to logs"""
        if not hasattr(self.context_stack, "context"):
            self.context_stack.context = {}

        # Store previous context
        previous_context = self.context_stack.context.copy()

        # Add new context
        self.context_stack.context.update(kwargs)

        try:
            yield
        finally:
            # Restore previous context
            self.context_stack.context = previous_context

    @contextmanager
    def operation(
        self, operation_name: str, operation_type: str = "general", **metadata
    ):
        """Context manager for tracking operations with metrics"""
        operation_id = f"{operation_name}_{int(time.time() * 1000)}"
        start_time = time.time()

        # Record operation start
        with self.context(
            operation_id=operation_id,
            operation_name=operation_name,
            operation_type=operation_type,
            **metadata,
        ):
            logger.info(
                f"Starting operation: {operation_name}",
                extra={"operation_event": "start", "operation_metadata": metadata},
            )

            self.active_operations[operation_id] = {
                "name": operation_name,
                "type": operation_type,
                "start_time": start_time,
                "metadata": metadata,
            }

            try:
                yield operation_id

                # Record successful completion
                duration = time.time() - start_time
                logger.info(
                    f"Completed operation: {operation_name} in {duration:.2f}s",
                    extra={
                        "operation_event": "complete",
                        "duration_seconds": duration,
                        "status": "success",
                    },
                )

                self._record_operation_metrics(operation_id, "success", duration)

            except Exception as e:
                # Record operation failure
                duration = time.time() - start_time
                logger.error(
                    f"Operation failed: {operation_name} after {duration:.2f}s",
                    extra={
                        "operation_event": "error",
                        "duration_seconds": duration,
                        "status": "error",
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                    },
                )

                self._record_operation_metrics(operation_id, "error", duration, str(e))
                raise

            finally:
                # Clean up active operation
                self.active_operations.pop(operation_id, None)

    def _record_operation_metrics(
        self, operation_id: str, status: str, duration: float, error: str = None
    ):
        """Record operation metrics for analysis"""
        operation_info = self.active_operations.get(operation_id, {})

        metric = {
            "operation_id": operation_id,
            "name": operation_info.get("name", "unknown"),
            "type": operation_info.get("type", "general"),
            "status": status,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat(),
            "error": error,
        }

        # Store in memory for session analysis
        operation_name = operation_info.get("name", "unknown")
        if operation_name not in self.operation_metrics:
            self.operation_metrics[operation_name] = []
        self.operation_metrics[operation_name].append(metric)

        # Write to metrics file
        metrics_file = self.log_dir / f"{self.app_name.lower()}_metrics.jsonl"
        with open(metrics_file, "a") as f:
            f.write(json.dumps(metric) + "\n")

    def log_performance_data(
        self,
        operation: str,
        execution_time: float,
        memory_usage: Optional[float] = None,
        cpu_usage: Optional[float] = None,
        **additional_metrics,
    ):
        """Log performance data in structured format"""
        perf_data = {
            "operation": operation,
            "execution_time_seconds": execution_time,
            "timestamp": datetime.now().isoformat(),
        }

        if memory_usage is not None:
            perf_data["memory_usage_mb"] = memory_usage
        if cpu_usage is not None:
            perf_data["cpu_usage_percent"] = cpu_usage

        perf_data.update(additional_metrics)

        logger.info(
            f"Performance data for {operation}",
            extra={"event_type": "performance", "performance_data": perf_data},
        )

    def create_progress_tracker(self, description: str = "Processing...") -> Progress:
        """Create a rich progress tracker"""
        if not self.enable_rich:
            return None

        return Progress(console=self.console, auto_refresh=True, refresh_per_second=10)

    def display_metrics_summary(self):
        """Display a summary of operation metrics using rich tables"""
        if not self.enable_rich or not self.operation_metrics:
            logger.info("No metrics to display")
            return

        table = Table(title="Operation Metrics Summary")
        table.add_column("Operation", style="cyan", no_wrap=True)
        table.add_column("Count", style="magenta")
        table.add_column("Success Rate", style="green")
        table.add_column("Avg Duration", style="blue")
        table.add_column("Total Time", style="yellow")

        for operation_name, metrics in self.operation_metrics.items():
            total_count = len(metrics)
            success_count = sum(1 for m in metrics if m["status"] == "success")
            success_rate = (success_count / total_count) * 100
            avg_duration = sum(m["duration_seconds"] for m in metrics) / total_count
            total_duration = sum(m["duration_seconds"] for m in metrics)

            table.add_row(
                operation_name,
                str(total_count),
                f"{success_rate:.1f}%",
                f"{avg_duration:.2f}s",
                f"{total_duration:.2f}s",
            )

        self.console.print(table)

    def get_logger(self, name: str = None):
        """Get a logger instance with the given name"""
        if name:
            return logger.bind(component=name)
        return logger

    def export_logs(
        self,
        format_type: str = "json",
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        level: Optional[str] = None,
    ) -> Path:
        """Export logs in specified format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = self.log_dir / f"export_{timestamp}.{format_type}"

        logger.info(f"Exporting logs to {export_file}")

        # This is a placeholder for log export functionality
        # In a real implementation, you would parse the structured logs
        # and filter/format them according to the parameters

        return export_file


# Global instance management
_global_logger: Optional[StructuredLogger] = None


def get_structured_logger(
    app_name: str = "IntelForge",
    log_level: str = "INFO",
    enable_rich: bool = True,
    enable_json: bool = True,
) -> StructuredLogger:
    """Get or create the global structured logger instance"""
    global _global_logger

    if _global_logger is None:
        _global_logger = StructuredLogger(
            app_name=app_name,
            log_level=log_level,
            enable_rich=enable_rich,
            enable_json=enable_json,
        )

    return _global_logger


def setup_cli_logging(verbose: bool = False, quiet: bool = False) -> StructuredLogger:
    """Setup logging for CLI applications"""
    level = "DEBUG" if verbose else "WARNING" if quiet else "INFO"

    structured_logger = get_structured_logger(
        app_name="IntelForge", log_level=level, enable_rich=True, enable_json=True
    )

    return structured_logger


# Convenience functions
def log_operation(operation_name: str, operation_type: str = "general", **metadata):
    """Decorator for logging operations"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            structured_logger = get_structured_logger()
            with structured_logger.operation(
                operation_name, operation_type, **metadata
            ):
                return func(*args, **kwargs)

        return wrapper

    return decorator


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    structured_logger = get_structured_logger(log_level="DEBUG")
    logger = structured_logger.get_logger("example")

    # Basic logging
    logger.info("Starting example operations")

    # Context logging
    with structured_logger.context(user_id="user123", session_type="demo"):
        logger.info("Processing user request")

        # Operation tracking
        with structured_logger.operation(
            "data_processing", "analysis", dataset="example"
        ):
            time.sleep(0.1)  # Simulate work
            logger.debug("Processing data...")
            logger.info("Data processing completed")

    # Performance logging
    structured_logger.log_performance_data(
        operation="example_operation",
        execution_time=0.1,
        memory_usage=50.5,
        cpu_usage=25.0,
        records_processed=100,
    )

    # Display metrics
    structured_logger.display_metrics_summary()

    logger.info("Example completed successfully")
