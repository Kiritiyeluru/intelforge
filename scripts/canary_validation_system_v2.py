#!/usr/bin/env python3
"""
Enhanced Canary Validation System with Assertion-Style Checks
Lightweight validation system with improved assertion patterns and plugin architecture
for site-specific validation rules.
"""

import time
import json
import logging
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from intel_bot_driver_v2 import IntelBotDriverV2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedCanaryValidator:
    """Enhanced canary validation with assertion-style checks and plugin architecture"""

    def __init__(
        self, cache_duration_minutes: int = 30, config_file: Optional[str] = None
    ):
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        self.cache_file = Path("reports/canary_validation/canary_cache_v2.json")
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

        # Load configuration from external file if provided
        self.config_file = config_file or "config/canary_targets.yaml"
        self._load_configuration()

        # Site-specific validation rules with assertion patterns
        self.validators = {
            "basic_connectivity": self._validate_basic_connectivity,
            "javascript_execution": self._validate_javascript_execution,
            "anti_detection_basic": self._validate_anti_detection,
            "finviz_canary": self._validate_finviz,
            "yahoo_finance_canary": self._validate_yahoo_finance,
            "httpbin_canary": self._validate_httpbin,
        }

    def _load_configuration(self) -> None:
        """Load configuration from external YAML file with fallback to defaults"""
        try:
            config_path = Path(self.config_file)
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f)

                # Load canary targets from config
                if "canary_targets" in config:
                    self.canary_targets = config["canary_targets"]
                    logger.info(
                        f"Loaded {len(self.canary_targets)} targets from {config_path}"
                    )
                else:
                    logger.warning(
                        f"No 'canary_targets' section found in {config_path}, using defaults"
                    )
                    self._set_default_targets()

                # Load cache settings
                if "cache_settings" in config:
                    cache_config = config["cache_settings"]
                    if "duration_minutes" in cache_config:
                        self.cache_duration = timedelta(
                            minutes=cache_config["duration_minutes"]
                        )
                    self.cache_enabled = cache_config.get("enabled", True)
                else:
                    self.cache_enabled = True

                # Load browser settings
                if "browser_settings" in config:
                    self.browser_config = config["browser_settings"]
                else:
                    self.browser_config = {
                        "reuse_session": True,
                        "headless": True,
                        "enable_ttr_tracking": False,
                    }

            else:
                logger.warning(
                    f"Configuration file {config_path} not found, using defaults"
                )
                self._set_default_targets()
                self.cache_enabled = True
                self.browser_config = {
                    "reuse_session": True,
                    "headless": True,
                    "enable_ttr_tracking": False,
                }

        except Exception as e:
            logger.error(f"Failed to load configuration from {self.config_file}: {e}")
            logger.info("Using default configuration")
            self._set_default_targets()
            self.cache_enabled = True
            self.browser_config = {
                "reuse_session": True,
                "headless": True,
                "enable_ttr_tracking": False,
            }

    def _set_default_targets(self) -> None:
        """Set default canary targets if external config is not available"""

        # Enhanced canary targets with detailed validation rules
        self.canary_targets = {
            "basic_connectivity": {
                "url": "https://example.com",
                "timeout_seconds": 10,
                "critical": True,
                "description": "Basic internet connectivity and browser function",
                "min_content_size": 500,
                "required_elements": ["title", "body"],
                "forbidden_keywords": ["access denied", "blocked"],
            },
            "javascript_execution": {
                "url": "https://httpbin.org/headers",
                "timeout_seconds": 10,
                "critical": True,
                "description": "JavaScript execution and DOM access",
                "min_content_size": 200,
                "required_elements": ["headers"],
                "forbidden_keywords": ["error", "not found"],
            },
            "anti_detection_basic": {
                "url": "https://bot.sannysoft.com/",
                "timeout_seconds": 20,
                "critical": False,
                "description": "Basic anti-detection capabilities",
                "min_content_size": 5000,
                "required_elements": ["detection"],
                "forbidden_keywords": ["failed to load"],
            },
            "finviz_canary": {
                "url": "https://finviz.com/",
                "timeout_seconds": 30,
                "critical": False,
                "description": "Finviz accessibility and stealth check",
                "min_content_size": 10000,
                "required_elements": ["screener", "finviz"],
                "forbidden_keywords": ["access denied", "blocked", "captcha"],
            },
            "yahoo_finance_canary": {
                "url": "https://finance.yahoo.com/",
                "timeout_seconds": 30,
                "critical": False,
                "description": "Yahoo Finance accessibility and stealth check",
                "min_content_size": 8000,
                "required_elements": ["finance", "yahoo"],
                "forbidden_keywords": ["access denied", "blocked", "captcha"],
            },
            "httpbin_canary": {
                "url": "https://httpbin.org/user-agent",
                "timeout_seconds": 15,
                "critical": False,
                "description": "HTTP testing and user agent validation",
                "min_content_size": 100,
                "required_elements": ["user-agent"],
                "forbidden_keywords": ["error"],
            },
        }

    def _validate_page_content(
        self,
        target_name: str,
        url: str,
        content: str,
        title: str,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Enhanced page validation with assertion-style checks"""
        checks = []

        # Basic checks
        checks.append(("title_present", bool(title and title.strip())))
        checks.append(
            ("content_size", len(content) > config.get("min_content_size", 1000))
        )

        # Required elements check
        required_elements = config.get("required_elements", [])
        for element in required_elements:
            checks.append((f"has_{element}", element.lower() in content.lower()))

        # Forbidden keywords check
        forbidden_keywords = config.get("forbidden_keywords", [])
        content_lower = content.lower()
        title_lower = title.lower() if title else ""

        for keyword in forbidden_keywords:
            has_forbidden = keyword in content_lower or keyword in title_lower
            checks.append((f"no_{keyword.replace(' ', '_')}", not has_forbidden))

        # Site-specific validations using plugin architecture
        if target_name in self.validators:
            site_checks = self.validators[target_name](content, title, config)
            checks.extend(site_checks)

        # Evaluate all checks
        failed_checks = [name for name, passed in checks if not passed]

        return {
            "valid": len(failed_checks) == 0,
            "failed_checks": failed_checks,
            "total_checks": len(checks),
            "passed_checks": len(checks) - len(failed_checks),
            "details": {check[0]: check[1] for check in checks},
        }

    def _extract_domain(self, url: str) -> str:
        """Extract domain identifier for plugin selection"""
        url_lower = url.lower()
        if "finviz" in url_lower:
            return "finviz_canary"
        elif "yahoo" in url_lower and "finance" in url_lower:
            return "yahoo_finance_canary"
        elif "httpbin" in url_lower:
            return "httpbin_canary"
        elif "bot.sannysoft" in url_lower:
            return "anti_detection_basic"
        elif "example.com" in url_lower:
            return "basic_connectivity"
        else:
            return "default"

    # Plugin architecture for site-specific validation rules
    def _validate_basic_connectivity(
        self, content: str, title: str, config: Dict[str, Any]
    ) -> List[Tuple[str, bool]]:
        """Validation rules for basic connectivity check"""
        return [
            ("example_domain", "example" in content.lower()),
            (
                "proper_html",
                "<html>" in content.lower() or "<!doctype" in content.lower(),
            ),
        ]

    def _validate_javascript_execution(
        self, content: str, title: str, config: Dict[str, Any]
    ) -> List[Tuple[str, bool]]:
        """Validation rules for JavaScript execution check"""
        return [
            ("headers_present", "headers" in content.lower()),
            ("json_structure", "{" in content and "}" in content),
            ("user_agent_info", "user-agent" in content.lower()),
        ]

    def _validate_anti_detection(
        self, content: str, title: str, config: Dict[str, Any]
    ) -> List[Tuple[str, bool]]:
        """Validation rules for anti-detection testing"""
        return [
            ("detection_tests", "detection" in content.lower()),
            (
                "browser_info",
                "chrome" in content.lower() or "firefox" in content.lower(),
            ),
            ("no_obvious_bot_detection", "bot detected" not in content.lower()),
        ]

    def _validate_finviz(
        self, content: str, title: str, config: Dict[str, Any]
    ) -> List[Tuple[str, bool]]:
        """Validation rules for Finviz financial site"""
        return [
            ("finviz_branding", "finviz" in title.lower()),
            ("screener_functionality", "screener" in content.lower()),
            (
                "stock_data_elements",
                any(term in content.lower() for term in ["stock", "market", "ticker"]),
            ),
            (
                "no_access_restrictions",
                not any(
                    term in content.lower()
                    for term in ["access denied", "403", "forbidden"]
                ),
            ),
        ]

    def _validate_yahoo_finance(
        self, content: str, title: str, config: Dict[str, Any]
    ) -> List[Tuple[str, bool]]:
        """Validation rules for Yahoo Finance"""
        return [
            ("yahoo_branding", "yahoo" in title.lower()),
            ("finance_functionality", "finance" in content.lower()),
            (
                "market_data_elements",
                any(
                    term in content.lower()
                    for term in ["quote", "stock", "market", "dow"]
                ),
            ),
            (
                "no_access_restrictions",
                not any(
                    term in content.lower()
                    for term in ["access denied", "403", "forbidden"]
                ),
            ),
        ]

    def _validate_httpbin(
        self, content: str, title: str, config: Dict[str, Any]
    ) -> List[Tuple[str, bool]]:
        """Validation rules for HTTPBin testing service"""
        return [
            ("httpbin_service", "httpbin" in content.lower()),
            ("user_agent_data", "user-agent" in content.lower()),
            ("proper_json", "{" in content and "}" in content),
        ]

    def _load_cache(self) -> Optional[Dict[str, Any]]:
        """Load cached canary results if still valid"""
        if not self.cache_file.exists():
            return None

        try:
            with open(self.cache_file, "r") as f:
                cache_data = json.load(f)

            cache_time = datetime.fromisoformat(cache_data["timestamp"])
            if datetime.now() - cache_time < self.cache_duration:
                logger.info(
                    f"Using cached canary results (age: {datetime.now() - cache_time})"
                )
                return cache_data
            else:
                logger.info("Cached canary results expired")
                return None

        except Exception as e:
            logger.warning(f"Failed to load canary cache: {e}")
            return None

    def _save_cache(self, results: Dict[str, Any]):
        """Save canary results to cache"""
        try:
            cache_data = {"timestamp": datetime.now().isoformat(), "results": results}

            with open(self.cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)

        except Exception as e:
            logger.warning(f"Failed to save canary cache: {e}")

    def run_canary_check(
        self, target_name: str, target_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run a single enhanced canary validation check"""
        logger.info(f"Running enhanced canary check: {target_name}")

        start_time = time.time()

        try:
            with IntelBotDriverV2(headless=True, enable_ttr_tracking=False) as driver:
                # Quick page load with minimal retries
                result = driver.get(target_config["url"], validate_page=False)

                if not result["success"]:
                    return {
                        "target": target_name,
                        "success": False,
                        "error": result["error"],
                        "duration": time.time() - start_time,
                        "critical": target_config["critical"],
                    }

                # Enhanced content validation
                try:
                    page_info = driver.get_page_info()
                    title = page_info["title"]
                    content = driver.driver.page_html  # Get full page content

                    # Run enhanced validation
                    validation_result = self._validate_page_content(
                        target_name, target_config["url"], content, title, target_config
                    )

                    return {
                        "target": target_name,
                        "success": validation_result["valid"],
                        "duration": time.time() - start_time,
                        "critical": target_config["critical"],
                        "validation": validation_result,
                        "details": {
                            "page_size": len(content),
                            "title": title[:100],  # Truncated title
                            "passed_checks": validation_result["passed_checks"],
                            "total_checks": validation_result["total_checks"],
                            "failed_checks": validation_result["failed_checks"],
                        },
                    }

                except Exception as e:
                    return {
                        "target": target_name,
                        "success": False,
                        "error": f"Enhanced validation failed: {str(e)}",
                        "duration": time.time() - start_time,
                        "critical": target_config["critical"],
                    }

        except Exception as e:
            return {
                "target": target_name,
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time,
                "critical": target_config["critical"],
            }

    def _run_canary_check_with_driver(
        self, target_name: str, target_config: Dict[str, Any], driver
    ) -> Dict[str, Any]:
        """Run a single canary check using an existing driver instance"""
        start_time = time.time()

        try:
            # Quick page load with minimal retries
            result = driver.get(target_config["url"], validate_page=False)

            if not result["success"]:
                return {
                    "target": target_name,
                    "success": False,
                    "error": result["error"],
                    "duration": time.time() - start_time,
                    "critical": target_config["critical"],
                }

            # Enhanced content validation
            try:
                page_info = driver.get_page_info()
                title = page_info["title"]
                content = driver.driver.page_html  # Get full page content

                # Run enhanced validation
                validation_result = self._validate_page_content(
                    target_name, target_config["url"], content, title, target_config
                )

                return {
                    "target": target_name,
                    "success": validation_result["valid"],
                    "duration": time.time() - start_time,
                    "critical": target_config["critical"],
                    "validation": validation_result,
                    "details": {
                        "page_size": len(content),
                        "title": title[:100],  # Truncated title
                        "passed_checks": validation_result["passed_checks"],
                        "total_checks": validation_result["total_checks"],
                        "failed_checks": validation_result["failed_checks"],
                    },
                }

            except Exception as content_error:
                return {
                    "target": target_name,
                    "success": False,
                    "error": f"Content validation failed: {str(content_error)}",
                    "duration": time.time() - start_time,
                    "critical": target_config["critical"],
                }

        except Exception as e:
            return {
                "target": target_name,
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time,
                "critical": target_config["critical"],
            }

    def _log_check_result(self, target_name: str, check_result: Dict[str, Any]) -> None:
        """Log the result of a canary check"""
        status = "✅" if check_result["success"] else "❌"
        critical = "CRITICAL" if check_result["critical"] else "optional"

        # Enhanced logging with check details
        if check_result["success"] and "validation" in check_result:
            validation_info = check_result["validation"]
            logger.info(
                f"{status} {target_name} ({critical}) - {check_result['duration']:.1f}s - "
                f"{validation_info['passed_checks']}/{validation_info['total_checks']} checks passed"
            )
        else:
            logger.info(
                f"{status} {target_name} ({critical}) - {check_result['duration']:.1f}s"
            )
            if not check_result["success"] and "failed_checks" in check_result.get(
                "details", {}
            ):
                failed_checks = check_result["details"]["failed_checks"]
                logger.warning(f"   Failed checks: {', '.join(failed_checks)}")

    def run_all_canary_checks(
        self, use_cache: bool = None, reuse_browser: bool = None
    ) -> Dict[str, Any]:
        """Run all enhanced canary validation checks"""
        logger.info("Starting enhanced canary validation checks")

        # Use configuration defaults if not specified
        if use_cache is None:
            use_cache = self.cache_enabled
        if reuse_browser is None:
            reuse_browser = self.browser_config.get("reuse_session", True)

        # Check cache first
        if use_cache:
            cached_results = self._load_cache()
            if cached_results:
                return cached_results["results"]

        validation_start = time.time()
        results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "summary": {},
            "version": "v2_enhanced",
        }

        # Run all canary checks with optional browser reuse
        if reuse_browser:
            # Use shared browser session for better performance
            try:
                with IntelBotDriverV2(
                    headless=self.browser_config.get("headless", True),
                    enable_ttr_tracking=self.browser_config.get(
                        "enable_ttr_tracking", False
                    ),
                ) as shared_driver:
                    logger.info("Using shared browser session for all checks")
                    for target_name, target_config in self.canary_targets.items():
                        check_result = self._run_canary_check_with_driver(
                            target_name, target_config, shared_driver
                        )
                        results["checks"][target_name] = check_result
                        self._log_check_result(target_name, check_result)
            except Exception as e:
                logger.error(
                    f"Shared browser session failed: {e}, falling back to individual sessions"
                )
                # Fallback to individual browser sessions
                reuse_browser = False

        if not reuse_browser:
            # Use individual browser sessions (original behavior)
            logger.info("Using individual browser sessions for each check")
            for target_name, target_config in self.canary_targets.items():
                check_result = self.run_canary_check(target_name, target_config)
                results["checks"][target_name] = check_result
                self._log_check_result(target_name, check_result)

        # Generate enhanced summary
        total_checks = len(results["checks"])
        successful_checks = len([c for c in results["checks"].values() if c["success"]])
        critical_checks = [c for c in results["checks"].values() if c["critical"]]
        critical_failures = [c for c in critical_checks if not c["success"]]

        # Calculate total validation checks across all targets
        total_validation_checks = sum(
            c.get("validation", {}).get("total_checks", 0)
            for c in results["checks"].values()
            if c["success"]
        )
        total_passed_validation_checks = sum(
            c.get("validation", {}).get("passed_checks", 0)
            for c in results["checks"].values()
            if c["success"]
        )

        total_duration = time.time() - validation_start

        # Determine overall status with enhanced criteria
        if critical_failures:
            overall_status = "failed"
            ready_for_pipeline = False
        elif successful_checks == total_checks:
            overall_status = "excellent"
            ready_for_pipeline = True
        elif successful_checks / total_checks >= 0.75:
            overall_status = "good"
            ready_for_pipeline = True
        else:
            overall_status = "degraded"
            ready_for_pipeline = False

        results["summary"] = {
            "total_checks": total_checks,
            "successful_checks": successful_checks,
            "success_rate": successful_checks / total_checks,
            "critical_failures": len(critical_failures),
            "overall_status": overall_status,
            "ready_for_pipeline": ready_for_pipeline,
            "total_duration": total_duration,
            "validation_timestamp": datetime.now().isoformat(),
            "enhanced_metrics": {
                "total_validation_checks": total_validation_checks,
                "passed_validation_checks": total_passed_validation_checks,
                "validation_success_rate": (
                    total_passed_validation_checks / total_validation_checks
                )
                if total_validation_checks > 0
                else 0,
            },
        }

        # Save to cache
        self._save_cache(results)

        logger.info(
            f"Enhanced canary validation complete: {overall_status} ({successful_checks}/{total_checks} targets, "
            f"{total_passed_validation_checks}/{total_validation_checks} checks passed)"
        )
        return results

    def is_pipeline_ready(self, use_cache: bool = True) -> Tuple[bool, Dict[str, Any]]:
        """Check if system is ready for main pipeline execution"""
        results = self.run_all_canary_checks(use_cache)
        return results["summary"]["ready_for_pipeline"], results

    def get_health_status(self) -> Dict[str, Any]:
        """Get current system health status based on recent canary checks"""
        results = self.run_all_canary_checks(use_cache=True)
        summary = results["summary"]

        # Determine health level with enhanced metrics
        enhanced_metrics = summary.get("enhanced_metrics", {})
        validation_success_rate = enhanced_metrics.get("validation_success_rate", 0)

        if summary["overall_status"] == "excellent" and validation_success_rate > 0.9:
            health_level = "healthy"
        elif summary["overall_status"] == "good" and validation_success_rate > 0.75:
            health_level = "warning"
        else:
            health_level = "critical"

        return {
            "health_level": health_level,
            "success_rate": summary["success_rate"],
            "validation_success_rate": validation_success_rate,
            "critical_failures": summary["critical_failures"],
            "last_check": summary["validation_timestamp"],
            "ready_for_pipeline": summary["ready_for_pipeline"],
            "enhanced_metrics": enhanced_metrics,
            "details": results["checks"],
        }


class EnhancedPipelineGatekeeper:
    """Enhanced pipeline execution gatekeeper with detailed recommendations"""

    def __init__(self):
        self.canary_validator = EnhancedCanaryValidator()

    def check_execution_readiness(
        self, operation_name: str = "pipeline"
    ) -> Dict[str, Any]:
        """Check if system is ready for pipeline execution with enhanced analysis"""
        logger.info(f"Checking execution readiness for: {operation_name}")

        ready, results = self.canary_validator.is_pipeline_ready()

        if ready:
            logger.info(f"✅ System ready for {operation_name} execution")
        else:
            logger.warning(f"⚠️ System not ready for {operation_name} execution")

            # Log specific issues with enhanced detail
            failed_checks = [
                check for check in results["checks"].values() if not check["success"]
            ]

            for failed_check in failed_checks:
                criticality = "CRITICAL" if failed_check["critical"] else "OPTIONAL"
                logger.warning(
                    f"  {criticality} FAILURE: {failed_check['target']} - {failed_check.get('error', 'Unknown error')}"
                )

                # Log detailed validation failures
                if (
                    "details" in failed_check
                    and "failed_checks" in failed_check["details"]
                ):
                    failed_validations = failed_check["details"]["failed_checks"]
                    logger.warning(
                        f"    Failed validations: {', '.join(failed_validations)}"
                    )

        return {
            "ready": ready,
            "operation": operation_name,
            "timestamp": datetime.now().isoformat(),
            "canary_results": results,
            "recommendations": self._generate_enhanced_recommendations(results),
        }

    def _generate_enhanced_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate enhanced recommendations based on detailed canary results"""
        recommendations = []

        failed_checks = [
            check for check in results["checks"].values() if not check["success"]
        ]

        if not failed_checks:
            enhanced_metrics = results["summary"].get("enhanced_metrics", {})
            validation_rate = enhanced_metrics.get("validation_success_rate", 0)

            if validation_rate >= 0.95:
                recommendations.append(
                    "Excellent system health - all validations passed"
                )
            elif validation_rate >= 0.85:
                recommendations.append(
                    "Good system health - minor validation issues detected"
                )
            else:
                recommendations.append(
                    "System operational but with validation concerns"
                )

            recommendations.append("Proceed with pipeline execution")
            return recommendations

        # Analyze failure patterns with enhanced detail
        network_failures = []
        timeout_failures = []
        detection_failures = []
        validation_failures = []

        for check in failed_checks:
            error = check.get("error", "").lower()

            if "connection" in error or "network" in error:
                network_failures.append(check)
            elif "timeout" in error:
                timeout_failures.append(check)
            elif any(
                keyword in error for keyword in ["blocked", "denied", "captcha", "bot"]
            ):
                detection_failures.append(check)
            elif "validation failed" in error:
                validation_failures.append(check)

        # Generate specific recommendations
        if network_failures:
            recommendations.append(
                "NETWORK: Check internet connectivity and DNS resolution"
            )
            recommendations.append(
                f"  Affected targets: {', '.join([c['target'] for c in network_failures])}"
            )

        if timeout_failures:
            recommendations.append(
                "PERFORMANCE: Consider increasing timeout values or checking server responsiveness"
            )
            recommendations.append(
                f"  Slow targets: {', '.join([c['target'] for c in timeout_failures])}"
            )

        if detection_failures:
            recommendations.append(
                "STEALTH: Bot detection encountered - review anti-detection configuration"
            )
            recommendations.append(
                f"  Detected on: {', '.join([c['target'] for c in detection_failures])}"
            )
            recommendations.append(
                "  Consider: Different user agents, proxy rotation, or stealth browser settings"
            )

        if validation_failures:
            recommendations.append("VALIDATION: Content validation issues detected")
            for check in validation_failures:
                if "details" in check and "failed_checks" in check["details"]:
                    failed_validations = check["details"]["failed_checks"]
                    recommendations.append(
                        f"  {check['target']}: {', '.join(failed_validations[:3])}{'...' if len(failed_validations) > 3 else ''}"
                    )

        # Critical failure recommendations
        critical_failures = [c for c in failed_checks if c["critical"]]
        if critical_failures:
            recommendations.append(
                "CRITICAL: Resolve critical failures before proceeding with main pipeline"
            )
            recommendations.append(
                "  Review browser configuration, network settings, and stealth capabilities"
            )

        return recommendations


def test_enhanced_canary_system():
    """Test the enhanced canary validation system"""
    print("🕊️✨ Testing Enhanced Canary Validation System")
    print("=" * 60)

    # Test enhanced canary validation
    validator = EnhancedCanaryValidator()
    results = validator.run_all_canary_checks(use_cache=False)

    print("\n📊 Enhanced Canary Validation Results:")
    print(f"   Total Duration: {results['summary']['total_duration']:.1f}s")
    print(f"   Target Success Rate: {results['summary']['success_rate']:.1%}")

    enhanced_metrics = results["summary"].get("enhanced_metrics", {})
    if enhanced_metrics:
        print(
            f"   Validation Success Rate: {enhanced_metrics.get('validation_success_rate', 0):.1%}"
        )
        print(
            f"   Total Validation Checks: {enhanced_metrics.get('total_validation_checks', 0)}"
        )

    print(f"   Overall Status: {results['summary']['overall_status'].upper()}")
    print(
        f"   Pipeline Ready: {'✅' if results['summary']['ready_for_pipeline'] else '❌'}"
    )

    # Show individual check results with enhanced detail
    print("\n🔍 Detailed Check Results:")
    for target_name, check_result in results["checks"].items():
        status = "✅" if check_result["success"] else "❌"
        critical = " (CRITICAL)" if check_result["critical"] else ""
        duration = check_result["duration"]

        print(f"   {status} {target_name}{critical} - {duration:.1f}s")

        if check_result["success"] and "validation" in check_result:
            validation = check_result["validation"]
            print(
                f"      Validation: {validation['passed_checks']}/{validation['total_checks']} checks passed"
            )
        elif not check_result["success"]:
            print(f"      Error: {check_result.get('error', 'Unknown error')}")
            if "details" in check_result and "failed_checks" in check_result["details"]:
                failed_checks = check_result["details"]["failed_checks"]
                print(
                    f"      Failed validations: {', '.join(failed_checks[:3])}{'...' if len(failed_checks) > 3 else ''}"
                )

    # Test enhanced gatekeeper
    print("\n🚪 Testing Enhanced Pipeline Gatekeeper:")
    gatekeeper = EnhancedPipelineGatekeeper()
    readiness = gatekeeper.check_execution_readiness("enhanced_test_operation")

    print(f"   Ready: {'✅' if readiness['ready'] else '❌'}")
    print("   Enhanced Recommendations:")
    for rec in readiness["recommendations"]:
        print(f"     - {rec}")

    return results


def main():
    """Main function for enhanced canary validation testing"""
    test_enhanced_canary_system()

    print("\n✅ Enhanced Canary Validation System Test Complete")

    # Show enhanced health status
    validator = EnhancedCanaryValidator()
    health = validator.get_health_status()

    print("\n🏥 Enhanced System Health Status:")
    print(f"   Health Level: {health['health_level'].upper()}")
    print(f"   Target Success Rate: {health['success_rate']:.1%}")
    print(f"   Validation Success Rate: {health.get('validation_success_rate', 0):.1%}")
    print(f"   Critical Failures: {health['critical_failures']}")
    print(f"   Last Check: {health['last_check']}")


if __name__ == "__main__":
    main()
