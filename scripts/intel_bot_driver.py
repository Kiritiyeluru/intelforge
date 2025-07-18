#!/usr/bin/env python3
"""
IntelBotDriver - Production-Grade Botasaurus Wrapper
Advanced wrapper for Botasaurus Driver with comprehensive error handling,
retry logic, TTR tracking, and operational intelligence.
"""

import hashlib
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from botasaurus_driver import Driver

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TTRTracker:
    """Time-to-Recovery tracking system for operational intelligence"""

    def __init__(self, data_dir: str = "reports/ttr_tracking"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.data_dir / "ttr_sessions.json"

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

        # Save to session file
        self._save_session(operation_data)

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


class RetryBudgetManager:
    """Intelligent retry budget management with cooldown periods"""

    def __init__(self, config_file: str = "config/retry_budgets.yaml"):
        self.config_file = Path(config_file)
        self.budget_data = {}
        self.load_config()

    def load_config(self):
        """Load retry budget configuration"""
        # Default configuration if file doesn't exist
        self.default_config = {
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
            "default": {
                "retry_limit": 2,
                "cooldown_seconds": 60,
                "budget_reset_hours": 6,
            },
        }

        if self.config_file.exists():
            try:
                import yaml

                with open(self.config_file, "r") as f:
                    config = yaml.safe_load(f)
                    self.default_config.update(config.get("targets", {}))
            except Exception as e:
                logger.warning(f"Failed to load retry budget config: {e}")

    def get_budget_for_url(self, url: str) -> Dict[str, int]:
        """Get retry budget configuration for a specific URL"""
        domain = self._extract_domain(url)
        return self.default_config.get(domain, self.default_config["default"])

    def _extract_domain(self, url: str) -> str:
        """Extract domain identifier from URL"""
        if "finviz" in url.lower():
            return "finviz"
        elif "yahoo" in url.lower() and "finance" in url.lower():
            return "yahoo_finance"
        else:
            return "default"

    def can_retry(self, url: str, current_attempts: int) -> bool:
        """Check if retry is allowed within budget"""
        budget = self.get_budget_for_url(url)
        return current_attempts < budget["retry_limit"]


class IntelBotDriver:
    """Production-grade Botasaurus wrapper with comprehensive error handling"""

    def __init__(
        self,
        headless: bool = True,
        user_data_dir: Optional[str] = None,
        screenshots_dir: str = "reports/screenshots",
        max_init_retries: int = 3,
        enable_ttr_tracking: bool = True,
    ):
        self.headless = headless
        self.user_data_dir = user_data_dir
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.max_init_retries = max_init_retries
        self.enable_ttr_tracking = enable_ttr_tracking

        # Initialize tracking systems
        self.ttr_tracker = TTRTracker() if enable_ttr_tracking else None
        self.retry_budget = RetryBudgetManager()

        # Driver state
        self.driver: Optional[Driver] = None
        self.is_initialized = False
        self.init_attempts = 0

        # Initialize driver with retry logic
        self._initialize_driver()

    def _initialize_driver(self) -> bool:
        """Initialize Botasaurus driver with retry logic"""
        while self.init_attempts < self.max_init_retries:
            try:
                self.init_attempts += 1
                logger.info(
                    f"Initializing Botasaurus driver (attempt {self.init_attempts})"
                )

                self.driver = Driver(
                    headless=self.headless, user_data_dir=self.user_data_dir
                )

                # Test basic functionality
                self.driver.execute_script("return navigator.userAgent;")

                self.is_initialized = True
                logger.info("Botasaurus driver initialized successfully")
                return True

            except Exception as e:
                logger.error(
                    f"Driver initialization failed (attempt {self.init_attempts}): {e}"
                )
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None

                if self.init_attempts >= self.max_init_retries:
                    logger.error("Max initialization retries exceeded")
                    return False

                time.sleep(2**self.init_attempts)  # Exponential backoff

        return False

    def get(
        self, url: str, validate_page: bool = True, max_retries: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Navigate to URL with comprehensive error handling and validation

        Args:
            url: Target URL
            validate_page: Whether to perform page validation
            max_retries: Override default retry budget

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

        attempt = 0
        budget_config = self.retry_budget.get_budget_for_url(url)
        max_retries = max_retries or budget_config["retry_limit"]

        while attempt <= max_retries:
            try:
                attempt += 1
                logger.info(f"Loading {url} (attempt {attempt})")

                # Ensure driver is initialized
                if not self.is_initialized:
                    if not self._initialize_driver():
                        raise Exception("Failed to initialize driver")

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

                # Success - end TTR tracking
                if self.ttr_tracker and operation_data:
                    ttr = self.ttr_tracker.end_operation(operation_data, True)
                    logger.info(f"Page load successful. TTR: {ttr:.2f}s")

                return {
                    "success": True,
                    "url": url,
                    "attempt": attempt,
                    "ttr_seconds": ttr if self.ttr_tracker else None,
                    "operation_id": operation_id,
                }

            except Exception as e:
                error_msg = str(e)
                logger.error(f"Page load failed (attempt {attempt}): {error_msg}")

                # Take screenshot on detection/error
                self._capture_failure_screenshot(url, operation_id, attempt, error_msg)

                # Check if we can retry
                if attempt > max_retries or not self.retry_budget.can_retry(
                    url, attempt
                ):
                    logger.error(f"Max retries exceeded for {url}")

                    # End TTR tracking with failure
                    if self.ttr_tracker and operation_data:
                        self.ttr_tracker.end_operation(operation_data, False, error_msg)

                    return {
                        "success": False,
                        "url": url,
                        "error": error_msg,
                        "attempts": attempt,
                        "operation_id": operation_id,
                    }

                # Wait with exponential backoff
                cooldown = budget_config["cooldown_seconds"]
                wait_time = min(cooldown * (2 ** (attempt - 1)), 300)  # Max 5 minutes
                logger.info(f"Waiting {wait_time}s before retry")
                time.sleep(wait_time)

        # This shouldn't be reached, but just in case
        return {"success": False, "url": url, "error": "Unexpected retry loop exit"}

    def _validate_page(self, url: str) -> Dict[str, Any]:
        """Validate that page loaded successfully"""
        try:
            # Check title is not empty
            title = self.driver.title
            if not title or title.strip() == "":
                return {"valid": False, "reason": "Empty or missing title"}

            # Check page source length
            page_source = self.driver.page_source
            if len(page_source) < 1000:  # Minimum page size
                return {
                    "valid": False,
                    "reason": f"Page too small: {len(page_source)} chars",
                }

            # Check for common error indicators
            error_indicators = [
                "access denied",
                "blocked",
                "error",
                "not found",
                "403",
                "404",
                "500",
            ]
            title_lower = title.lower()
            source_lower = page_source.lower()

            for indicator in error_indicators:
                if (
                    indicator in title_lower or indicator in source_lower[:2000]
                ):  # Check first 2K chars
                    return {
                        "valid": False,
                        "reason": f"Error indicator detected: {indicator}",
                    }

            # Check for required elements based on URL
            validation_rules = self._get_validation_rules(url)
            for rule in validation_rules:
                try:
                    element = self.driver.find_element_by_css_selector(rule["selector"])
                    if not element:
                        return {
                            "valid": False,
                            "reason": f"Required element missing: {rule['selector']}",
                        }
                except:
                    return {
                        "valid": False,
                        "reason": f"Required element not found: {rule['selector']}",
                    }

            return {"valid": True, "title": title, "page_size": len(page_source)}

        except Exception as e:
            return {"valid": False, "reason": f"Validation error: {str(e)}"}

    def _get_validation_rules(self, url: str) -> List[Dict[str, str]]:
        """Get URL-specific validation rules"""
        rules = []

        if "finviz" in url.lower():
            rules.append({"selector": "body", "description": "Basic page structure"})
        elif "yahoo" in url.lower():
            rules.append({"selector": "body", "description": "Basic page structure"})
        else:
            # Default validation - just check for body
            rules.append({"selector": "body", "description": "Basic page structure"})

        return rules

    def _capture_failure_screenshot(
        self, url: str, operation_id: str, attempt: int, error: str
    ):
        """Capture screenshot on failure for debugging"""
        try:
            if self.driver and self.is_initialized:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                domain = url.split("//")[-1].split("/")[0].replace(".", "_")
                filename = (
                    f"failure_{domain}_{operation_id}_attempt{attempt}_{timestamp}.png"
                )
                filepath = self.screenshots_dir / filename

                self.driver.save_screenshot(str(filepath))

                # Also save page source
                source_file = filepath.with_suffix(".html")
                with open(source_file, "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)

                logger.info(f"Failure debug data saved: {filepath}")

        except Exception as e:
            logger.warning(f"Failed to capture failure screenshot: {e}")

    def execute_script(self, script: str) -> Any:
        """Execute JavaScript with error handling"""
        if not self.is_initialized:
            raise Exception("Driver not initialized")

        try:
            return self.driver.execute_script(script)
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
                "user_agent": self.driver.execute_script("return navigator.userAgent;"),
                "page_source_length": len(self.driver.page_source),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get page info: {e}")
            raise

    def quit(self):
        """Safely quit the driver"""
        try:
            if self.driver:
                self.driver.quit()
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
def test_intel_bot_driver():
    """Test function for IntelBotDriver"""
    test_urls = ["https://httpbin.org/user-agent", "https://example.com"]

    with IntelBotDriver(headless=True) as driver:
        for url in test_urls:
            print(f"\nTesting {url}")
            result = driver.get(url)

            if result["success"]:
                page_info = driver.get_page_info()
                print(f"✅ Success: {page_info['title']}")
                print(f"   TTR: {result.get('ttr_seconds', 'N/A')}s")
                print(f"   Attempts: {result['attempt']}")
            else:
                print(f"❌ Failed: {result['error']}")


if __name__ == "__main__":
    test_intel_bot_driver()
