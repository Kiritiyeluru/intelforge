#!/usr/bin/env python3
"""
Graceful shutdown handlers for IntelForge
Implements SIGINT/SIGTERM handling with cleanup hooks and resource management
"""

import atexit
import json
import logging
import signal
import sys
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class GracefulShutdown:
    """
    Comprehensive graceful shutdown handler for IntelForge operations
    Manages cleanup hooks, resource cleanup, and proper signal handling
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.cleanup_hooks: List[Callable] = []
        self.shutdown_event = threading.Event()
        self.shutdown_initiated = False
        self.cleanup_timeout = 30  # seconds
        self.active_operations: Dict[str, Any] = {}
        self.cleanup_status = {
            "total_hooks": 0,
            "successful": 0,
            "failed": 0,
            "errors": [],
        }

        # Register signal handlers
        self._register_signal_handlers()

        # Register atexit cleanup
        atexit.register(self._emergency_cleanup)

    def _register_signal_handlers(self):
        """Register SIGINT and SIGTERM handlers"""
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            self.logger.info(
                "Graceful shutdown handlers registered for SIGINT and SIGTERM"
            )
        except (ValueError, OSError) as e:
            self.logger.warning(f"Could not register signal handlers: {e}")

    def _signal_handler(self, signum: int, frame):
        """Handle shutdown signals gracefully"""
        signal_name = "SIGINT" if signum == signal.SIGINT else "SIGTERM"
        self.logger.info(f"Received {signal_name}, initiating graceful shutdown...")

        if self.shutdown_initiated:
            self.logger.warning("Shutdown already in progress. Forcing exit...")
            sys.exit(1)

        self.shutdown_initiated = True
        self.shutdown_event.set()
        self._execute_shutdown()

    def register_cleanup_hook(self, cleanup_func: Callable, name: str = None) -> str:
        """
        Register a cleanup function to be called during shutdown

        Args:
            cleanup_func: Function to call during cleanup
            name: Optional name for the cleanup function

        Returns:
            str: Hook identifier for potential removal
        """
        hook_name = name or f"cleanup_hook_{len(self.cleanup_hooks)}"

        def wrapped_cleanup():
            try:
                self.logger.info(f"Executing cleanup hook: {hook_name}")
                cleanup_func()
                self.cleanup_status["successful"] += 1
                self.logger.info(f"Cleanup hook '{hook_name}' completed successfully")
            except Exception as e:
                self.cleanup_status["failed"] += 1
                error_msg = f"Cleanup hook '{hook_name}' failed: {str(e)}"
                self.cleanup_status["errors"].append(error_msg)
                self.logger.error(error_msg)

        self.cleanup_hooks.append(wrapped_cleanup)
        self.cleanup_status["total_hooks"] += 1
        self.logger.debug(f"Registered cleanup hook: {hook_name}")

        return hook_name

    def register_active_operation(
        self, operation_id: str, operation_data: Dict[str, Any]
    ):
        """Register an active operation for tracking during shutdown"""
        self.active_operations[operation_id] = {
            "data": operation_data,
            "start_time": time.time(),
            "status": "active",
        }
        self.logger.debug(f"Registered active operation: {operation_id}")

    def complete_operation(self, operation_id: str):
        """Mark an operation as completed"""
        if operation_id in self.active_operations:
            self.active_operations[operation_id]["status"] = "completed"
            self.active_operations[operation_id]["end_time"] = time.time()
            self.logger.debug(f"Completed operation: {operation_id}")

    def _execute_shutdown(self):
        """Execute the graceful shutdown sequence"""
        start_time = time.time()

        self.logger.info("Starting graceful shutdown sequence...")

        # 1. Stop accepting new operations
        self.logger.info("Phase 1: Stopping new operations")

        # 2. Wait for active operations to complete (with timeout)
        self.logger.info("Phase 2: Waiting for active operations to complete")
        self._wait_for_active_operations()

        # 3. Execute cleanup hooks
        self.logger.info("Phase 3: Executing cleanup hooks")
        self._execute_cleanup_hooks()

        # 4. Generate shutdown report
        shutdown_time = time.time() - start_time
        self._generate_shutdown_report(shutdown_time)

        self.logger.info(f"Graceful shutdown completed in {shutdown_time:.2f} seconds")
        sys.exit(0)

    def _wait_for_active_operations(self):
        """Wait for active operations to complete with timeout"""
        max_wait = min(self.cleanup_timeout - 5, 15)  # Reserve time for cleanup
        start_time = time.time()

        while time.time() - start_time < max_wait:
            active_ops = [
                op_id
                for op_id, op_data in self.active_operations.items()
                if op_data["status"] == "active"
            ]

            if not active_ops:
                self.logger.info("All active operations completed")
                break

            self.logger.info(
                f"Waiting for {len(active_ops)} active operations: {active_ops}"
            )
            time.sleep(1)
        else:
            active_ops = [
                op_id
                for op_id, op_data in self.active_operations.items()
                if op_data["status"] == "active"
            ]
            if active_ops:
                self.logger.warning(
                    f"Timeout waiting for operations. Force-completing: {active_ops}"
                )
                for op_id in active_ops:
                    self.active_operations[op_id]["status"] = "force_completed"

    def _execute_cleanup_hooks(self):
        """Execute all registered cleanup hooks"""
        if not self.cleanup_hooks:
            self.logger.info("No cleanup hooks to execute")
            return

        self.logger.info(f"Executing {len(self.cleanup_hooks)} cleanup hooks...")

        for hook in self.cleanup_hooks:
            try:
                hook()
            except Exception as e:
                self.logger.error(f"Cleanup hook failed: {e}")

        success_rate = (
            self.cleanup_status["successful"] / self.cleanup_status["total_hooks"]
        ) * 100
        self.logger.info(f"Cleanup hooks completed: {success_rate:.1f}% success rate")

    def _emergency_cleanup(self):
        """Emergency cleanup for atexit handling"""
        if not self.shutdown_initiated:
            self.logger.info("Emergency cleanup triggered via atexit")
            self._execute_cleanup_hooks()

    def _generate_shutdown_report(self, shutdown_time: float):
        """Generate and save shutdown report"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "shutdown_time_seconds": round(shutdown_time, 2),
            "cleanup_status": self.cleanup_status,
            "active_operations": {
                op_id: {
                    "status": op_data["status"],
                    "duration": op_data.get("end_time", time.time())
                    - op_data["start_time"],
                }
                for op_id, op_data in self.active_operations.items()
            },
            "status": (
                "SUCCESS" if self.cleanup_status["failed"] == 0 else "PARTIAL_SUCCESS"
            ),
        }

        # Save report to logs directory
        try:
            logs_dir = Path(__file__).parent.parent.parent / "logs"
            logs_dir.mkdir(exist_ok=True)

            report_file = logs_dir / f"shutdown_report_{int(time.time())}.json"
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

            self.logger.info(f"Shutdown report saved to: {report_file}")
        except Exception as e:
            self.logger.error(f"Failed to save shutdown report: {e}")

    @contextmanager
    def operation_context(self, operation_id: str, **operation_data):
        """Context manager for tracking operations during execution"""
        self.register_active_operation(operation_id, operation_data)
        try:
            if self.shutdown_event.is_set():
                raise InterruptedError(
                    "Shutdown in progress, cannot start new operation"
                )
            yield
        finally:
            self.complete_operation(operation_id)

    def is_shutdown_requested(self) -> bool:
        """Check if shutdown has been requested"""
        return self.shutdown_event.is_set()


# Global instance for easy access
_global_shutdown_handler: Optional[GracefulShutdown] = None


def get_shutdown_handler(logger: Optional[logging.Logger] = None) -> GracefulShutdown:
    """Get or create the global shutdown handler instance"""
    global _global_shutdown_handler

    if _global_shutdown_handler is None:
        _global_shutdown_handler = GracefulShutdown(logger)

    return _global_shutdown_handler


def register_cleanup(cleanup_func: Callable, name: str = None) -> str:
    """Convenience function to register cleanup hooks"""
    handler = get_shutdown_handler()
    return handler.register_cleanup_hook(cleanup_func, name)


@contextmanager
def operation_tracking(operation_id: str, **operation_data):
    """Convenience context manager for operation tracking"""
    handler = get_shutdown_handler()
    with handler.operation_context(operation_id, **operation_data):
        yield


# CLI integration helpers
def setup_cli_shutdown_handling(logger: Optional[logging.Logger] = None):
    """Setup graceful shutdown for CLI applications"""
    handler = get_shutdown_handler(logger)

    # Register common CLI cleanup tasks
    handler.register_cleanup_hook(
        lambda: logging.info("CLI shutdown complete"), "cli_final_log"
    )

    return handler


def check_shutdown_requested() -> bool:
    """Check if shutdown has been requested (for periodic checks in long operations)"""
    handler = get_shutdown_handler()
    return handler.is_shutdown_requested()


# Example usage and testing
if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Example usage
    shutdown_handler = setup_cli_shutdown_handling(logger)

    # Register some example cleanup functions
    register_cleanup(lambda: print("Cleaning up temporary files..."), "temp_cleanup")
    register_cleanup(lambda: print("Closing database connections..."), "db_cleanup")

    # Simulate a long-running operation
    with operation_tracking("example_operation", type="data_processing"):
        print("Starting long operation... Press Ctrl+C to test graceful shutdown")
        try:
            for i in range(100):
                if check_shutdown_requested():
                    print("Shutdown requested, stopping operation...")
                    break
                time.sleep(0.5)
                print(f"Processing step {i+1}/100")
        except KeyboardInterrupt:
            print("KeyboardInterrupt caught - graceful shutdown should handle this")

    print("Operation completed normally")
