#!/usr/bin/env python3
"""
IntelBotDriver v2 - Production-Grade Botasaurus Wrapper with Tenacity Integration
Advanced wrapper for Botasaurus Driver with Tenacity-based retry logic,
TTR tracking, and operational intelligence.
"""

import hashlib
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from botasaurus_driver import Driver
from tenacity import (after_log, retry, retry_if_exception_type,
                      stop_after_attempt, wait_exponential)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TTRTracker:
    """Time-to-Recovery tracking system with optional Sentry integration"""

    def __init__(
        self, data_dir: str = "reports/ttr_tracking", use_sentry: bool = False
    ):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.data_dir / "ttr_sessions.json"
        self.use_sentry = use_sentry

        # Optional Sentry integration
        if use_sentry:
            try:
                import sentry_sdk

                self.sentry = sentry_sdk
                logger.info("Sentry integration enabled for TTR tracking")
            except ImportError:
                logger.warning(
                    "Sentry SDK not available, falling back to local tracking only"
                )
                self.use_sentry = False
                self.sentry = None
        else:
            self.sentry = None

    def start_operation(
        self, operation_id: str, operation_type: str, target_url: str
    ) -> Dict[str, Any]:
        """Start tracking an operation"""
        operation_data = {
            "operation_id": operation_id,
            "operation_type": operation_type,
            "target_url": target_url,
            "start_time": time.time(),
            "start_timestamp": datetime.now().isoformat(),
            "status": "in_progress",
        }
        return operation_data

    def end_operation(
        self, operation_data: Dict[str, Any], success: bool, error: Optional[str] = None
    ) -> float:
        """End tracking and calculate TTR"""
        end_time = time.time()
        ttr = end_time - operation_data["start_time"]

        operation_data.update(
            {
                "end_time": end_time,
                "end_timestamp": datetime.now().isoformat(),
                "ttr_seconds": ttr,
                "success": success,
                "error": error,
                "status": "completed",
            }
        )

        # Save to local session file
        self._save_session(operation_data)

        # Optional Sentry integration
        if self.use_sentry and self.sentry:
            try:
                self.sentry.set_tag("operation_type", operation_data["operation_type"])
                self.sentry.set_tag("target_url", operation_data["target_url"])
                self.sentry.set_measurement("ttr_seconds", ttr)
                if not success and error:
                    self.sentry.capture_message(
                        f"TTR Operation Failed: {error}", level="warning"
                    )
            except Exception as e:
                logger.warning(f"Sentry TTR logging failed: {e}")

        return ttr

    def _save_session(self, operation_data: Dict[str, Any]):
        """Save operation data to session file"""
        try:
            if self.session_file.exists():
                with open(self.session_file, "r") as f:
                    sessions = json.load(f)
            else:
                sessions = []

            sessions.append(operation_data)

            with open(self.session_file, "w") as f:
                json.dump(sessions, f, indent=2)

        except Exception as e:
            logger.warning(f"Failed to save TTR session data: {e}")


class TenacityBudgetManager:
    """Tenacity-based retry budget management with YAML configuration"""

    def __init__(self, config_file: str = "config/retry_budgets.yaml"):
        self.config_file = Path(config_file)
        self.load_config()

    def load_config(self):
        """Load retry budget configuration"""
        # Default configuration if file doesn't exist
        self.config = {
            "targets": {
                "finviz": {
                    "retry_limit": 3,
                    "cooldown_seconds": 30,
                    "budget_reset_hours": 24,
                },
                "yahoo_finance": {
                    "retry_limit": 2,
                    "cooldown_seconds": 45,
                    "budget_reset_hours": 12,
                },
                "creepjs": {
                    "retry_limit": 1,
                    "cooldown_seconds": 60,
                    "budget_reset_hours": 6,
                },
                "httpbin": {
                    "retry_limit": 5,
                    "cooldown_seconds": 5,
                    "budget_reset_hours": 1,
                },
                "default": {
                    "retry_limit": 2,
                    "cooldown_seconds": 60,
                    "budget_reset_hours": 6,
                },
            }
        }

        if self.config_file.exists():
            try:
                import yaml

                with open(self.config_file, "r") as f:
                    loaded_config = yaml.safe_load(f)
                    if "targets" in loaded_config:
                        self.config["targets"].update(loaded_config["targets"])
            except Exception as e:
                logger.warning(f"Failed to load retry budget config: {e}")

    def get_retry_decorator(self, url: str):
        """Get Tenacity retry decorator configured for specific URL"""
        domain = self._extract_domain(url)
        budget = self.config["targets"].get(domain, self.config["targets"]["default"])

        def log_retry_attempt(retry_state):
            """Callback to log retry attempts"""
            logger.warning(
                f"Retry attempt {retry_state.attempt_number} for {url} "
                f"after {retry_state.seconds_since_start:.2f}s"
            )

        return retry(
            stop=stop_after_attempt(budget["retry_limit"]),
            wait=wait_exponential(
                multiplier=1,
                min=budget["cooldown_seconds"],
                max=300,  # 5 minutes max
            ),
            retry=retry_if_exception_type((Exception,)),
            after=log_retry_attempt,
            reraise=True,
        )

    def _extract_domain(self, url: str) -> str:
        """Extract domain identifier from URL"""
        url_lower = url.lower()
        if "finviz" in url_lower:
            return "finviz"
        elif "yahoo" in url_lower and "finance" in url_lower:
            return "yahoo_finance"
        elif "creepjs" in url_lower:
            return "creepjs"
        elif "httpbin" in url_lower:
            return "httpbin"
        else:
            return "default"


class IntelBotDriverV2:
    """Production-grade Botasaurus wrapper with Tenacity retry logic"""

    def __init__(
        self,
        headless: bool = True,
        profile: Optional[str] = None,
        screenshots_dir: str = "reports/screenshots",
        max_init_retries: int = 3,
        enable_ttr_tracking: bool = True,
        use_sentry: bool = False,
    ):
        self.headless = headless
        self.profile = profile
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.max_init_retries = max_init_retries
        self.enable_ttr_tracking = enable_ttr_tracking

        # Initialize tracking systems
        self.ttr_tracker = (
            TTRTracker(use_sentry=use_sentry) if enable_ttr_tracking else None
        )
        self.retry_manager = TenacityBudgetManager()

        # Driver state
        self.driver: Optional[Driver] = None
        self.is_initialized = False
        self.init_attempts = 0

        # Initialize driver with retry logic
        self._initialize_driver()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=1, max=10),
        after=after_log(logger, logging.WARNING),
    )
    def _initialize_driver(self) -> bool:
        """Initialize Botasaurus driver with Tenacity retry logic"""
        try:
            logger.info("Initializing Botasaurus driver")

            self.driver = Driver(headless=self.headless, profile=self.profile)

            # Test basic functionality
            self.driver.run_js("return navigator.userAgent;")

            self.is_initialized = True
            logger.info("Botasaurus driver initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Driver initialization failed: {e}")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
            raise  # Re-raise for Tenacity to handle

    def get(self, url: str, validate_page: bool = True) -> Dict[str, Any]:
        """
        Navigate to URL with Tenacity-based retry logic

        Args:
            url: Target URL
            validate_page: Whether to perform page validation

        Returns:
            Dict with operation results and metadata
        """
        operation_id = hashlib.md5(f"{url}_{time.time()}".encode()).hexdigest()[:8]

        # Start TTR tracking
        operation_data = None
        if self.ttr_tracker:
            operation_data = self.ttr_tracker.start_operation(
                operation_id, "page_load", url
            )

        try:
            # Get retry decorator for this URL
            retry_decorator = self.retry_manager.get_retry_decorator(url)

            # Create the actual page load function
            @retry_decorator
            def _attempt_page_load():
                # Ensure driver is initialized
                if not self.is_initialized:
                    self._initialize_driver()

                # Navigate to URL
                self.driver.get(url)
                time.sleep(2)  # Wait for page load

                # Validate page if requested
                if validate_page:
                    validation_result = self._validate_page(url)
                    if not validation_result["valid"]:
                        raise Exception(
                            f"Page validation failed: {validation_result['reason']}"
                        )

                return True

            # Execute the retry logic
            _attempt_page_load()

            # Success - end TTR tracking
            ttr = None
            if self.ttr_tracker and operation_data:
                ttr = self.ttr_tracker.end_operation(operation_data, True)
                logger.info(f"Page load successful. TTR: {ttr:.2f}s")

            return {
                "success": True,
                "url": url,
                "ttr_seconds": ttr,
                "operation_id": operation_id,
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Page load failed after all retries: {error_msg}")

            # Take screenshot on final failure
            self._capture_failure_screenshot(url, operation_id, "final", error_msg)

            # End TTR tracking with failure
            if self.ttr_tracker and operation_data:
                self.ttr_tracker.end_operation(operation_data, False, error_msg)

            return {
                "success": False,
                "url": url,
                "error": error_msg,
                "operation_id": operation_id,
            }

    def _validate_page(self, url: str) -> Dict[str, Any]:
        """Enhanced page validation with assertion-style checks"""
        try:
            # Basic checks
            title = self.driver.title
            page_source = self.driver.page_html

            checks = []

            # Title validation
            checks.append(("title_present", bool(title and title.strip())))

            # Content size validation
            min_content_size = 1000
            checks.append(("content_size", len(page_source) > min_content_size))

            # Site-specific validations
            if "finviz" in url.lower():
                checks.append(("finviz_elements", "screener" in page_source.lower()))
                checks.append(
                    (
                        "finviz_table",
                        ".table-dark-row" in page_source
                        or "table" in page_source.lower(),
                    )
                )

            elif "yahoo" in url.lower() and "finance" in url.lower():
                checks.append(
                    ("yahoo_finance_elements", "finance" in page_source.lower())
                )
                checks.append(
                    (
                        "yahoo_content",
                        "stock" in page_source.lower()
                        or "quote" in page_source.lower(),
                    )
                )

            elif "httpbin" in url.lower():
                checks.append(
                    (
                        "httpbin_elements",
                        any(
                            term in page_source.lower()
                            for term in ["user-agent", "headers", "httpbin"]
                        ),
                    )
                )

            # Error indicator checks
            error_indicators = [
                "access denied",
                "blocked",
                "captcha",
                "forbidden",
                "403",
                "404",
                "500",
            ]
            title_lower = title.lower() if title else ""
            source_lower = page_source.lower()[:2000]  # First 2K chars

            has_error_indicators = any(
                indicator in title_lower or indicator in source_lower
                for indicator in error_indicators
            )
            checks.append(("no_error_indicators", not has_error_indicators))

            # Evaluate all checks
            failed_checks = [name for name, passed in checks if not passed]

            if failed_checks:
                return {
                    "valid": False,
                    "reason": f"Failed checks: {', '.join(failed_checks)}",
                    "failed_checks": failed_checks,
                    "total_checks": len(checks),
                }

            return {
                "valid": True,
                "title": title,
                "page_size": len(page_source),
                "passed_checks": len(checks),
            }

        except Exception as e:
            return {"valid": False, "reason": f"Validation error: {str(e)}"}

    def _capture_failure_screenshot(
        self, url: str, operation_id: str, attempt: str, error: str
    ):
        """Capture screenshot on failure for debugging"""
        try:
            if self.driver and self.is_initialized:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                domain = url.split("//")[-1].split("/")[0].replace(".", "_")
                filename = f"failure_{domain}_{operation_id}_{attempt}_{timestamp}.png"
                filepath = self.screenshots_dir / filename

                self.driver.save_screenshot(str(filepath))

                # Also save page source
                source_file = filepath.with_suffix(".html")
                with open(source_file, "w", encoding="utf-8") as f:
                    f.write(self.driver.page_html)

                logger.info(f"Failure debug data saved: {filepath}")

        except Exception as e:
            logger.warning(f"Failed to capture failure screenshot: {e}")

    def execute_script(self, script: str) -> Any:
        """Execute JavaScript with error handling"""
        if not self.is_initialized:
            raise Exception("Driver not initialized")

        try:
            return self.driver.run_js(script)
        except Exception as e:
            logger.error(f"Script execution failed: {e}")
            raise

    def get_page_info(self) -> Dict[str, Any]:
        """Get comprehensive page information"""
        if not self.is_initialized:
            raise Exception("Driver not initialized")

        try:
            return {
                "title": self.driver.title,
                "url": self.driver.current_url,
                "user_agent": self.driver.run_js("return navigator.userAgent;"),
                "page_source_length": len(self.driver.page_html),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get page info: {e}")
            raise

    def quit(self):
        """Safely quit the driver"""
        try:
            if self.driver:
                self.driver.close()
                logger.info("Driver quit successfully")
        except Exception as e:
            logger.warning(f"Error during driver quit: {e}")
        finally:
            self.driver = None
            self.is_initialized = False

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.quit()


# Convenience function for quick testing
def test_intel_bot_driver_v2():
    """Test function for IntelBotDriverV2"""
    test_urls = ["https://httpbin.org/user-agent", "https://example.com"]

    print("Testing IntelBotDriverV2 with Tenacity retry logic")

    with IntelBotDriverV2(headless=True, use_sentry=False) as driver:
        for url in test_urls:
            print(f"\nTesting {url}")
            result = driver.get(url)

            if result["success"]:
                page_info = driver.get_page_info()
                print(f"✅ Success: {page_info['title']}")
                print(f"   TTR: {result.get('ttr_seconds', 'N/A')}s")
            else:
                print(f"❌ Failed: {result['error']}")


if __name__ == "__main__":
    test_intel_bot_driver_v2()
