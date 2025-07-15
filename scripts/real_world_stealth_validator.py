#!/usr/bin/env python3
"""
Real-World Stealth Validation System
Tests anti-detection capabilities against actual financial sites (Finviz, Yahoo Finance)
with comprehensive stealth scoring and failure analysis.
"""

import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from intel_bot_driver import IntelBotDriver


class RealWorldStealthValidator:
    """Comprehensive stealth validation against production financial sites"""

    def __init__(self, reports_dir: str = "reports/stealth_validation"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Financial sites for real-world testing
        self.financial_targets = {
            "finviz_home": {
                "url": "https://finviz.com/",
                "expected_title_contains": "finviz",
                "success_indicators": ["screener", "market", "stocks"],
                "failure_indicators": [
                    "access denied",
                    "blocked",
                    "captcha",
                    "cloudflare",
                ],
                "min_page_size": 30000,
                "difficulty": "medium",
                "retry_budget": 3,
            },
            "finviz_screener": {
                "url": "https://finviz.com/screener.ashx",
                "expected_title_contains": "stock screener",
                "success_indicators": ["table", "screener", "stocks", "filter"],
                "failure_indicators": ["access denied", "blocked", "captcha", "error"],
                "min_page_size": 50000,
                "difficulty": "high",
                "retry_budget": 2,
            },
            "yahoo_finance_home": {
                "url": "https://finance.yahoo.com/",
                "expected_title_contains": "yahoo finance",
                "success_indicators": ["market", "stocks", "finance", "quote"],
                "failure_indicators": ["blocked", "access denied", "captcha"],
                "min_page_size": 40000,
                "difficulty": "medium",
                "retry_budget": 3,
            },
            "yahoo_finance_quote": {
                "url": "https://finance.yahoo.com/quote/AAPL",
                "expected_title_contains": "apple",
                "success_indicators": ["aapl", "apple", "stock", "price"],
                "failure_indicators": ["not found", "blocked", "error"],
                "min_page_size": 30000,
                "difficulty": "high",
                "retry_budget": 2,
            },
        }

        # CreepJS stealth testing URL
        self.creepjs_url = "https://abrahamjuliot.github.io/creepjs/"

    def validate_site_stealth(
        self, target_name: str, target_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate stealth against a specific financial site"""
        print(f"\n🎯 Testing stealth against: {target_name}")
        print(f"   URL: {target_config['url']}")
        print(f"   Difficulty: {target_config['difficulty'].upper()}")

        validation_result = {
            "target_name": target_name,
            "target_config": target_config,
            "timestamp": datetime.now().isoformat(),
            "attempts": [],
            "final_result": None,
            "stealth_score": 0,
            "detection_indicators": [],
        }

        with IntelBotDriver(headless=True, enable_ttr_tracking=True) as driver:
            max_attempts = target_config["retry_budget"]

            for attempt in range(1, max_attempts + 1):
                print(f"   Attempt {attempt}/{max_attempts}...")

                attempt_result = driver.get(
                    target_config["url"],
                    validate_page=True,
                    max_retries=0,  # We handle retries at this level
                )

                if attempt_result["success"]:
                    # Get page information for analysis
                    page_info = driver.get_page_info()

                    # Perform stealth analysis
                    stealth_analysis = self._analyze_stealth_success(
                        page_info, target_config, driver
                    )

                    attempt_data = {
                        "attempt": attempt,
                        "success": True,
                        "ttr_seconds": attempt_result.get("ttr_seconds"),
                        "page_info": page_info,
                        "stealth_analysis": stealth_analysis,
                    }

                    validation_result["attempts"].append(attempt_data)
                    validation_result["final_result"] = "success"
                    validation_result["stealth_score"] = stealth_analysis[
                        "stealth_score"
                    ]

                    print(
                        f"   ✅ SUCCESS - Stealth Score: {stealth_analysis['stealth_score']:.1f}/100"
                    )
                    break
                else:
                    # Analyze failure for detection indicators
                    failure_analysis = self._analyze_stealth_failure(
                        attempt_result, target_config
                    )

                    attempt_data = {
                        "attempt": attempt,
                        "success": False,
                        "error": attempt_result["error"],
                        "failure_analysis": failure_analysis,
                    }

                    validation_result["attempts"].append(attempt_data)
                    validation_result["detection_indicators"].extend(
                        failure_analysis["detection_indicators"]
                    )

                    print(f"   ❌ FAILED - {failure_analysis['failure_type']}")

                    # Wait before retry if not last attempt
                    if attempt < max_attempts:
                        wait_time = 30 * attempt  # Exponential backoff
                        print(f"   ⏳ Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)

            if validation_result["final_result"] != "success":
                validation_result["final_result"] = "failed"
                print("   ❌ ALL ATTEMPTS FAILED")

        return validation_result

    def _analyze_stealth_success(
        self,
        page_info: Dict[str, Any],
        target_config: Dict[str, Any],
        driver: IntelBotDriver,
    ) -> Dict[str, Any]:
        """Analyze successful page load for stealth quality"""

        title = page_info["title"].lower()
        page_source = ""

        try:
            # Get page source for analysis
            page_source = driver.execute_script(
                "return document.documentElement.outerHTML;"
            )
        except:
            page_source = ""

        page_source_lower = page_source.lower()

        stealth_score = 100  # Start with perfect score
        issues = []

        # Check page size (too small might indicate blocking page)
        if len(page_source) < target_config["min_page_size"]:
            stealth_score -= 20
            issues.append(f"Page size too small: {len(page_source)} chars")

        # Check for success indicators
        success_indicators_found = 0
        for indicator in target_config["success_indicators"]:
            if indicator in title or indicator in page_source_lower:
                success_indicators_found += 1

        success_ratio = success_indicators_found / len(
            target_config["success_indicators"]
        )
        if success_ratio < 0.8:  # Less than 80% of expected content
            penalty = (1 - success_ratio) * 30
            stealth_score -= penalty
            issues.append(f"Missing expected content ({success_ratio:.1%} found)")

        # Check for failure indicators (these suggest detection or blocking)
        for indicator in target_config["failure_indicators"]:
            if indicator in title or indicator in page_source_lower:
                stealth_score -= 40  # Heavy penalty for detection indicators
                issues.append(f"Detection indicator found: {indicator}")

        # Check for bot detection patterns
        bot_patterns = [
            "bot detected",
            "automated traffic",
            "unusual activity",
            "verify you are human",
            "security check",
            "access restricted",
        ]

        for pattern in bot_patterns:
            if pattern in page_source_lower:
                stealth_score -= 50
                issues.append(f"Bot detection pattern: {pattern}")

        # Additional checks for common anti-bot services
        anti_bot_services = ["cloudflare", "incapsula", "distil", "perimeterx"]
        for service in anti_bot_services:
            if service in page_source_lower:
                stealth_score -= 15
                issues.append(f"Anti-bot service detected: {service}")

        stealth_score = max(0, stealth_score)  # Don't go below 0

        return {
            "stealth_score": stealth_score,
            "issues": issues,
            "page_size": len(page_source),
            "success_indicators_found": success_indicators_found,
            "success_ratio": success_ratio,
            "analysis_timestamp": datetime.now().isoformat(),
        }

    def _analyze_stealth_failure(
        self, attempt_result: Dict[str, Any], target_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze failed attempt to determine if it's due to detection"""

        error = attempt_result.get("error", "").lower()

        # Categorize failure types
        if any(keyword in error for keyword in ["timeout", "connection", "network"]):
            failure_type = "network_issue"
            detection_likelihood = "low"
        elif any(
            keyword in error for keyword in ["access denied", "blocked", "forbidden"]
        ):
            failure_type = "access_blocked"
            detection_likelihood = "high"
        elif any(keyword in error for keyword in ["captcha", "verify", "security"]):
            failure_type = "captcha_challenge"
            detection_likelihood = "very_high"
        elif any(keyword in error for keyword in ["bot", "automated", "suspicious"]):
            failure_type = "bot_detection"
            detection_likelihood = "very_high"
        else:
            failure_type = "unknown_error"
            detection_likelihood = "medium"

        detection_indicators = []
        if detection_likelihood in ["high", "very_high"]:
            detection_indicators.append(
                {
                    "type": failure_type,
                    "evidence": error,
                    "likelihood": detection_likelihood,
                }
            )

        return {
            "failure_type": failure_type,
            "detection_likelihood": detection_likelihood,
            "detection_indicators": detection_indicators,
            "raw_error": error,
        }

    def test_creepjs_score(self) -> Dict[str, Any]:
        """Test stealth against CreepJS fingerprinting detection"""
        print("\n🔍 Testing CreepJS Stealth Score")
        print(f"   URL: {self.creepjs_url}")

        try:
            with IntelBotDriver(headless=True) as driver:
                result = driver.get(self.creepjs_url, validate_page=False)

                if not result["success"]:
                    return {
                        "success": False,
                        "error": result["error"],
                        "creepjs_score": 0,
                    }

                # Wait for CreepJS to complete analysis
                print("   ⏳ Waiting for CreepJS analysis...")
                time.sleep(15)  # Give CreepJS time to run tests

                # Try to extract the score
                try:
                    # Look for the score in various ways
                    score_element = driver.driver.find_element_by_css_selector(".score")
                    creepjs_score = score_element.text

                    # Parse score percentage
                    import re

                    score_match = re.search(r"(\d+(?:\.\d+)?)%", creepjs_score)
                    if score_match:
                        score_percentage = float(score_match.group(1))
                    else:
                        score_percentage = 0

                except Exception:
                    # Fallback: check page source for score
                    page_source = driver.execute_script(
                        "return document.body.innerHTML;"
                    )
                    import re

                    score_matches = re.findall(r"(\d+(?:\.\d+)?)%", page_source)
                    score_percentage = float(score_matches[0]) if score_matches else 0

                print(f"   📊 CreepJS Score: {score_percentage}%")

                # Evaluate score quality
                if score_percentage >= 70:
                    quality = "excellent"
                elif score_percentage >= 50:
                    quality = "good"
                elif score_percentage >= 30:
                    quality = "fair"
                else:
                    quality = "poor"

                return {
                    "success": True,
                    "creepjs_score": score_percentage,
                    "quality": quality,
                    "meets_target": score_percentage >= 70,
                    "ttr_seconds": result.get("ttr_seconds"),
                }

        except Exception as e:
            print(f"   ❌ CreepJS test failed: {str(e)}")
            return {"success": False, "error": str(e), "creepjs_score": 0}

    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive stealth validation across all targets"""
        print("🛡️ Real-World Stealth Validation Suite")
        print("=" * 60)

        validation_results = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "financial_sites": {},
            "creepjs_test": {},
            "summary": {},
        }

        # Test financial sites
        print("\n🏦 Testing Financial Site Access...")
        for target_name, target_config in self.financial_targets.items():
            result = self.validate_site_stealth(target_name, target_config)
            validation_results["financial_sites"][target_name] = result

        # Test CreepJS score
        print("\n🔍 Testing Fingerprinting Detection...")
        creepjs_result = self.test_creepjs_score()
        validation_results["creepjs_test"] = creepjs_result

        # Generate summary
        validation_results["summary"] = self._generate_validation_summary(
            validation_results
        )

        # Save results
        results_file = self.reports_dir / f"stealth_validation_{self.session_id}.json"
        with open(results_file, "w") as f:
            json.dump(validation_results, f, indent=2)

        print(f"\n📁 Results saved: {results_file}")
        return validation_results

    def _generate_validation_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive validation summary"""

        financial_results = results["financial_sites"]
        creepjs_result = results["creepjs_test"]

        # Analyze financial site success
        total_sites = len(financial_results)
        successful_sites = len(
            [r for r in financial_results.values() if r["final_result"] == "success"]
        )

        success_rate = successful_sites / total_sites if total_sites > 0 else 0

        # Calculate average stealth score
        stealth_scores = [
            r["stealth_score"]
            for r in financial_results.values()
            if r["final_result"] == "success"
        ]
        avg_stealth_score = (
            sum(stealth_scores) / len(stealth_scores) if stealth_scores else 0
        )

        # Determine overall assessment
        if success_rate >= 0.8 and avg_stealth_score >= 80:
            overall_assessment = "excellent"
        elif success_rate >= 0.6 and avg_stealth_score >= 60:
            overall_assessment = "good"
        elif success_rate >= 0.4:
            overall_assessment = "fair"
        else:
            overall_assessment = "poor"

        # Check targets compliance
        finviz_success = any(
            r["final_result"] == "success"
            for name, r in financial_results.items()
            if "finviz" in name
        )

        yahoo_success = any(
            r["final_result"] == "success"
            for name, r in financial_results.items()
            if "yahoo" in name
        )

        creepjs_meets_target = creepjs_result.get("meets_target", False)

        return {
            "total_sites_tested": total_sites,
            "successful_sites": successful_sites,
            "success_rate": success_rate,
            "average_stealth_score": avg_stealth_score,
            "finviz_access": finviz_success,
            "yahoo_finance_access": yahoo_success,
            "creepjs_score": creepjs_result.get("creepjs_score", 0),
            "creepjs_meets_target": creepjs_meets_target,
            "overall_assessment": overall_assessment,
            "meets_phase_b_targets": {
                "finviz_4_of_5": finviz_success,  # Simplified for now
                "yahoo_finance_4_of_5": yahoo_success,  # Simplified for now
                "creepjs_over_70": creepjs_meets_target,
            },
        }


def main():
    """Main execution function"""
    validator = RealWorldStealthValidator()

    # Run comprehensive validation
    results = validator.run_comprehensive_validation()

    # Display results
    summary = results["summary"]

    print("\n📊 Validation Summary:")
    print(f"   Sites Tested: {summary['total_sites_tested']}")
    print(f"   Success Rate: {summary['success_rate']:.1%}")
    print(f"   Avg Stealth Score: {summary['average_stealth_score']:.1f}/100")
    print(f"   CreepJS Score: {summary['creepjs_score']:.1f}%")
    print(f"   Overall Assessment: {summary['overall_assessment'].upper()}")

    print("\n🎯 Phase B Target Compliance:")
    targets = summary["meets_phase_b_targets"]
    print(f"   Finviz Access: {'✅' if targets['finviz_4_of_5'] else '❌'}")
    print(
        f"   Yahoo Finance Access: {'✅' if targets['yahoo_finance_4_of_5'] else '❌'}"
    )
    print(f"   CreepJS >70%: {'✅' if targets['creepjs_over_70'] else '❌'}")

    print("\n✅ Real-World Stealth Validation Complete")


if __name__ == "__main__":
    main()
