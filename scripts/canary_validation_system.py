#!/usr/bin/env python3
"""
Canary Validation System for Pre-Flight Checks
Lightweight validation system that runs before main pipeline execution
to ensure stealth capabilities are operational.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from intel_bot_driver import IntelBotDriver

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CanaryValidator:
    """Lightweight canary validation for pre-flight stealth checks"""

    def __init__(self, cache_duration_minutes: int = 30):
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        self.cache_file = Path("reports/canary_validation/canary_cache.json")
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

        # Lightweight canary targets for quick validation
        self.canary_targets = {
            "basic_connectivity": {
                "url": "https://httpbin.org/user-agent",
                "expected_content": "user-agent",
                "timeout_seconds": 10,
                "critical": True,
                "description": "Basic internet connectivity and browser function",
            },
            "javascript_execution": {
                "url": "https://httpbin.org/headers",
                "expected_content": "headers",
                "timeout_seconds": 10,
                "critical": True,
                "description": "JavaScript execution and DOM access",
            },
            "anti_detection_basic": {
                "url": "https://bot.sannysoft.com/",
                "expected_content": "bot detection",
                "timeout_seconds": 20,
                "critical": False,
                "description": "Basic anti-detection capabilities",
            },
            "finviz_canary": {
                "url": "https://finviz.com/",
                "expected_content": "finviz",
                "timeout_seconds": 30,
                "critical": False,
                "description": "Finviz accessibility check",
            },
        }

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
        """Run a single canary validation check"""
        logger.info(f"Running canary check: {target_name}")

        start_time = time.time()

        try:
            with IntelBotDriver(headless=True, enable_ttr_tracking=False) as driver:
                # Quick page load with minimal validation
                result = driver.get(
                    target_config["url"],
                    validate_page=False,  # Skip heavy validation for speed
                    max_retries=1,  # Minimal retries for canary checks
                )

                if not result["success"]:
                    return {
                        "target": target_name,
                        "success": False,
                        "error": result["error"],
                        "duration": time.time() - start_time,
                        "critical": target_config["critical"],
                    }

                # Quick content validation
                try:
                    page_info = driver.get_page_info()
                    title = page_info["title"].lower()

                    # Check for expected content
                    expected = target_config["expected_content"].lower()
                    content_found = expected in title

                    # Basic size check
                    page_size = page_info["page_source_length"]
                    size_adequate = page_size > 1000  # Minimum viable page

                    success = content_found and size_adequate

                    return {
                        "target": target_name,
                        "success": success,
                        "duration": time.time() - start_time,
                        "critical": target_config["critical"],
                        "details": {
                            "content_found": content_found,
                            "size_adequate": size_adequate,
                            "page_size": page_size,
                            "title": page_info["title"][:100],  # Truncated title
                        },
                    }

                except Exception as e:
                    return {
                        "target": target_name,
                        "success": False,
                        "error": f"Content validation failed: {str(e)}",
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

    def run_all_canary_checks(self, use_cache: bool = True) -> Dict[str, Any]:
        """Run all canary validation checks"""
        logger.info("Starting canary validation checks")

        # Check cache first
        if use_cache:
            cached_results = self._load_cache()
            if cached_results:
                return cached_results["results"]

        validation_start = time.time()
        results = {"timestamp": datetime.now().isoformat(), "checks": {}, "summary": {}}

        # Run all canary checks
        for target_name, target_config in self.canary_targets.items():
            check_result = self.run_canary_check(target_name, target_config)
            results["checks"][target_name] = check_result

            status = "✅" if check_result["success"] else "❌"
            critical = "CRITICAL" if check_result["critical"] else "optional"

            logger.info(
                f"{status} {target_name} ({critical}) - {check_result['duration']:.1f}s"
            )

        # Generate summary
        total_checks = len(results["checks"])
        successful_checks = len([c for c in results["checks"].values() if c["success"]])
        critical_checks = [c for c in results["checks"].values() if c["critical"]]
        critical_failures = [c for c in critical_checks if not c["success"]]

        total_duration = time.time() - validation_start

        # Determine overall status
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
        }

        # Save to cache
        self._save_cache(results)

        logger.info(
            f"Canary validation complete: {overall_status} ({successful_checks}/{total_checks} passed)"
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

        # Determine health level
        if summary["overall_status"] == "excellent":
            health_level = "healthy"
        elif summary["overall_status"] == "good":
            health_level = "warning"
        else:
            health_level = "critical"

        return {
            "health_level": health_level,
            "success_rate": summary["success_rate"],
            "critical_failures": summary["critical_failures"],
            "last_check": summary["validation_timestamp"],
            "ready_for_pipeline": summary["ready_for_pipeline"],
            "details": results["checks"],
        }


class PipelineGatekeeper:
    """Pipeline execution gatekeeper using canary validation"""

    def __init__(self):
        self.canary_validator = CanaryValidator()

    def check_execution_readiness(
        self, operation_name: str = "pipeline"
    ) -> Dict[str, Any]:
        """Check if system is ready for pipeline execution"""
        logger.info(f"Checking execution readiness for: {operation_name}")

        ready, results = self.canary_validator.is_pipeline_ready()

        if ready:
            logger.info(f"✅ System ready for {operation_name} execution")
        else:
            logger.warning(f"⚠️ System not ready for {operation_name} execution")

            # Log specific issues
            failed_checks = [
                check for check in results["checks"].values() if not check["success"]
            ]

            for failed_check in failed_checks:
                criticality = "CRITICAL" if failed_check["critical"] else "OPTIONAL"
                logger.warning(
                    f"  {criticality} FAILURE: {failed_check['target']} - {failed_check.get('error', 'Unknown error')}"
                )

        return {
            "ready": ready,
            "operation": operation_name,
            "timestamp": datetime.now().isoformat(),
            "canary_results": results,
            "recommendations": self._generate_recommendations(results),
        }

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on canary results"""
        recommendations = []

        failed_checks = [
            check for check in results["checks"].values() if not check["success"]
        ]

        if not failed_checks:
            recommendations.append("All systems operational - proceed with confidence")
            return recommendations

        # Analyze failure patterns
        network_failures = [
            c for c in failed_checks if "connection" in c.get("error", "").lower()
        ]
        timeout_failures = [
            c for c in failed_checks if "timeout" in c.get("error", "").lower()
        ]
        detection_failures = [
            c
            for c in failed_checks
            if any(
                keyword in c.get("error", "").lower()
                for keyword in ["blocked", "denied", "captcha", "bot"]
            )
        ]

        if network_failures:
            recommendations.append("Check internet connectivity and DNS resolution")

        if timeout_failures:
            recommendations.append(
                "Consider increasing timeout values or checking server responsiveness"
            )

        if detection_failures:
            recommendations.append(
                "Bot detection encountered - review stealth configuration"
            )
            recommendations.append(
                "Consider using different user agents or proxy rotation"
            )

        # Critical failure recommendations
        critical_failures = [c for c in failed_checks if c["critical"]]
        if critical_failures:
            recommendations.append(
                "CRITICAL: Resolve critical failures before proceeding"
            )
            recommendations.append("Review browser configuration and network settings")

        return recommendations


def test_canary_system():
    """Test the canary validation system"""
    print("🕊️ Testing Canary Validation System")
    print("=" * 50)

    # Test basic canary validation
    validator = CanaryValidator()
    results = validator.run_all_canary_checks(use_cache=False)

    print("\n📊 Canary Validation Results:")
    print(f"   Total Duration: {results['summary']['total_duration']:.1f}s")
    print(f"   Success Rate: {results['summary']['success_rate']:.1%}")
    print(f"   Overall Status: {results['summary']['overall_status'].upper()}")
    print(
        f"   Pipeline Ready: {'✅' if results['summary']['ready_for_pipeline'] else '❌'}"
    )

    # Show individual check results
    print("\n🔍 Individual Check Results:")
    for target_name, check_result in results["checks"].items():
        status = "✅" if check_result["success"] else "❌"
        critical = " (CRITICAL)" if check_result["critical"] else ""
        duration = check_result["duration"]

        print(f"   {status} {target_name}{critical} - {duration:.1f}s")

        if not check_result["success"]:
            print(f"      Error: {check_result.get('error', 'Unknown error')}")

    # Test gatekeeper
    print("\n🚪 Testing Pipeline Gatekeeper:")
    gatekeeper = PipelineGatekeeper()
    readiness = gatekeeper.check_execution_readiness("test_operation")

    print(f"   Ready: {'✅' if readiness['ready'] else '❌'}")
    print("   Recommendations:")
    for rec in readiness["recommendations"]:
        print(f"     - {rec}")

    return results


def main():
    """Main function for canary validation testing"""
    test_canary_system()

    print("\n✅ Canary Validation System Test Complete")

    # Show health status
    validator = CanaryValidator()
    health = validator.get_health_status()

    print("\n🏥 System Health Status:")
    print(f"   Health Level: {health['health_level'].upper()}")
    print(f"   Success Rate: {health['success_rate']:.1%}")
    print(f"   Critical Failures: {health['critical_failures']}")
    print(f"   Last Check: {health['last_check']}")


if __name__ == "__main__":
    main()
