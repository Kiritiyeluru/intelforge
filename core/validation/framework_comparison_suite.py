#!/usr/bin/env python3
"""
Phase 3 Framework Comparison Suite
Comprehensive evaluation of multi-tool orchestration vs Botasaurus framework
"""

import asyncio
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import psutil
# Import frameworks for testing
import undetected_chromedriver as uc
from botasaurus_driver import Driver
from playwright.async_api import async_playwright
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium_stealth import stealth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FrameworkComparison:
    """Comprehensive framework comparison system"""

    def __init__(self):
        self.results_dir = Path("reports/framework_comparison")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Test URLs for comparison
        self.test_urls = [
            "https://httpbin.org/user-agent",
            "https://httpbin.org/headers",
            "https://bot.sannysoft.com/",
            "https://whatismyipaddress.com/",
            "https://example.com",
        ]

        # Warm-up URL for eliminating cold start bias
        self.warmup_url = "https://httpbin.org/"

        # Scoring configuration with documented rationale
        self.scoring_config = {
            "performance": {
                "weight": 0.25,
                "fast_threshold": 3.0,  # seconds - anything under 3s is considered fast
                "slow_threshold": 10.0,  # seconds - anything over 10s is considered slow
                "fast_score": 8,  # score for fast performance
                "medium_score": 6,  # score for medium performance
                "slow_score": 3,  # score for slow performance
                "rationale": "Performance is critical for production scraping - faster response times enable higher throughput",
            },
            "reliability": {
                "weight": 0.30,
                "excellent_threshold": 0.95,  # 95%+ success rate
                "good_threshold": 0.80,  # 80%+ success rate
                "excellent_score": 10,
                "good_score": 7,
                "poor_score": 3,
                "rationale": "Reliability is paramount - failed scrapes mean lost data and operational overhead",
            },
            "maintenance": {
                "weight": 0.25,
                "complexity_multiplier": -1,  # Lower complexity = higher score
                "base_score": 10,
                "rationale": "Lower maintenance burden allows focus on features vs infrastructure",
            },
            "integration": {
                "weight": 0.20,
                "min_score": 1,
                "max_score": 10,
                "rationale": "Easier integration reduces development time and risk of implementation issues",
            },
        }

    def _validate_page_content(self, title: str, page_source: str, url: str) -> dict:
        """Validate that page loaded successfully with explicit checks"""
        # Check title is not empty
        if not title or title.strip() == "":
            return {"valid": False, "reason": "Empty or missing title"}

        # Check page source length
        if len(page_source) < 500:  # Minimum page size
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
            "captcha",
        ]
        title_lower = title.lower()
        source_lower = page_source.lower()

        for indicator in error_indicators:
            if indicator in title_lower:
                return {"valid": False, "reason": f"Error in title: {indicator}"}
            if indicator in source_lower[:2000]:  # Check first 2K chars
                return {"valid": False, "reason": f"Error in content: {indicator}"}

        # Check for required elements based on URL
        if not self._check_required_elements(page_source, url):
            return {"valid": False, "reason": "Required page elements missing"}

        return {"valid": True, "title": title, "page_size": len(page_source)}

    def _check_required_elements(self, page_source: str, url: str) -> bool:
        """Check for required HTML elements"""
        # Basic requirement: must have <body> tag
        if "<body" not in page_source.lower():
            return False

        # URL-specific requirements
        if "httpbin" in url.lower():
            # HTTPBin should have JSON responses or HTML structure
            return "json" in page_source.lower() or "html" in page_source.lower()
        elif "bot.sannysoft" in url.lower():
            # Bot detection site should have detection results
            return len(page_source) > 5000  # Should be substantial content

        return True  # Default: basic body check passed

    def _calculate_performance_score(self, avg_time: float, config: dict) -> float:
        """Calculate performance score based on configurable thresholds"""
        if avg_time == 0:  # Failed tests
            return 0
        elif avg_time < config["fast_threshold"]:
            return config["fast_score"]
        elif avg_time < config["slow_threshold"]:
            return config["medium_score"]
        else:
            return config["slow_score"]

    def _calculate_reliability_score(self, success_rate: float, config: dict) -> float:
        """Calculate reliability score based on success rate"""
        if success_rate >= config["excellent_threshold"]:
            return config["excellent_score"]
        elif success_rate >= config["good_threshold"]:
            return config["good_score"]
        else:
            return config["poor_score"]

    def _calculate_maintenance_score(
        self, complexity_score: float, config: dict
    ) -> float:
        """Calculate maintenance score (inverse of complexity)"""
        return max(
            0,
            config["base_score"] + (complexity_score * config["complexity_multiplier"]),
        )

    def measure_performance(self, func, *args, **kwargs):
        """Measure execution time and memory usage including subprocess memory"""
        process = psutil.Process()

        def get_total_memory(proc):
            """Get total memory usage including all child processes"""
            total_memory = proc.memory_info().rss
            try:
                for child in proc.children(recursive=True):
                    try:
                        total_memory += child.memory_info().rss
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        # Child process may have terminated or access denied
                        continue
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Parent process issues
                pass
            return total_memory / 1024 / 1024  # Convert to MB

        memory_before = get_total_memory(process)

        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
        end_time = time.time()

        memory_after = get_total_memory(process)

        return {
            "execution_time": end_time - start_time,
            "memory_used": memory_after - memory_before,
            "success": success,
            "error": error,
            "result": result,
        }

    def warm_up_multi_tool(self):
        """Warm-up run for multi-tool approach to eliminate cold start bias"""
        try:
            options = ChromeOptions()
            options.add_argument("--headless")
            driver = uc.Chrome(options=options)
            stealth(
                driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )
            driver.get(self.warmup_url)
            time.sleep(1)
            driver.quit()
            logger.info("Multi-tool warm-up completed")
        except Exception as e:
            logger.warning(f"Multi-tool warm-up failed: {e}")

    def test_multi_tool_approach(self, url, skip_warmup=False):
        """Test multi-tool orchestration approach"""
        logger.info(f"Testing multi-tool approach on {url}")

        # Perform warm-up run if not skipped
        if not skip_warmup:
            self.warm_up_multi_tool()

        def multi_tool_scrape():
            # Use undetected-chromedriver with selenium-stealth
            options = ChromeOptions()
            options.add_argument("--headless")

            driver = uc.Chrome(options=options)

            # Apply selenium-stealth
            stealth(
                driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )

            try:
                driver.get(url)
                time.sleep(2)  # Wait for page load

                # Extract basic information
                title = driver.title
                user_agent = driver.execute_script("return navigator.userAgent;")
                page_source = driver.page_source
                page_source_length = len(page_source)

                # Explicit page validation checks
                validation_result = self._validate_page_content(title, page_source, url)
                if not validation_result["valid"]:
                    raise Exception(
                        f"Page validation failed: {validation_result['reason']}"
                    )

                result = {
                    "title": title,
                    "user_agent": user_agent,
                    "page_source_length": page_source_length,
                    "url": url,
                    "validation": validation_result,
                }

                return result

            finally:
                driver.quit()

        return self.measure_performance(multi_tool_scrape)

    def warm_up_botasaurus(self):
        """Warm-up run for Botasaurus approach to eliminate cold start bias"""
        try:
            driver = Driver(headless=True)
            driver.get(self.warmup_url)
            time.sleep(1)
            driver.quit()
            logger.info("Botasaurus warm-up completed")
        except Exception as e:
            logger.warning(f"Botasaurus warm-up failed: {e}")

    def test_botasaurus_approach(self, url, skip_warmup=False):
        """Test Botasaurus framework approach"""
        logger.info(f"Testing Botasaurus approach on {url}")

        # Perform warm-up run if not skipped
        if not skip_warmup:
            self.warm_up_botasaurus()

        def botasaurus_scrape():
            driver = Driver(headless=True)

            try:
                driver.get(url)
                time.sleep(2)  # Wait for page load

                # Extract basic information
                title = driver.title
                user_agent = driver.execute_script("return navigator.userAgent;")
                page_source = driver.page_source
                page_source_length = len(page_source)

                # Explicit page validation checks
                validation_result = self._validate_page_content(title, page_source, url)
                if not validation_result["valid"]:
                    raise Exception(
                        f"Page validation failed: {validation_result['reason']}"
                    )

                result = {
                    "title": title,
                    "user_agent": user_agent,
                    "page_source_length": page_source_length,
                    "url": url,
                    "validation": validation_result,
                }

                return result

            finally:
                driver.quit()

        return self.measure_performance(botasaurus_scrape)

    async def test_playwright_baseline(self, url):
        """Test Playwright as performance baseline"""
        logger.info(f"Testing Playwright baseline on {url}")

        async def playwright_scrape():
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()

                try:
                    await page.goto(url)
                    await page.wait_for_timeout(2000)  # Wait for page load

                    # Extract basic information
                    title = await page.title()
                    user_agent = await page.evaluate("navigator.userAgent")
                    content = await page.content()
                    page_source_length = len(content)

                    # Explicit page validation checks
                    validation_result = self._validate_page_content(title, content, url)
                    if not validation_result["valid"]:
                        raise Exception(
                            f"Page validation failed: {validation_result['reason']}"
                        )

                    result = {
                        "title": title,
                        "user_agent": user_agent,
                        "page_source_length": page_source_length,
                        "url": url,
                        "validation": validation_result,
                    }

                    return result

                finally:
                    await browser.close()

        process = psutil.Process()

        def get_total_memory(proc):
            """Get total memory usage including all child processes"""
            total_memory = proc.memory_info().rss
            try:
                for child in proc.children(recursive=True):
                    try:
                        total_memory += child.memory_info().rss
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            return total_memory / 1024 / 1024  # Convert to MB

        memory_before = get_total_memory(process)

        start_time = time.time()
        try:
            result = await playwright_scrape()
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
        end_time = time.time()

        memory_after = get_total_memory(process)

        return {
            "execution_time": end_time - start_time,
            "memory_used": memory_after - memory_before,
            "success": success,
            "error": error,
            "result": result,
        }

    def test_concurrent_performance(self, approach_func, max_workers=3):
        """Test concurrent scraping performance"""
        logger.info(f"Testing concurrent performance with {max_workers} workers")

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit tasks for all test URLs, skip warmup for concurrent tests to avoid conflicts
            futures = [
                executor.submit(approach_func, url, True) for url in self.test_urls
            ]

            results = []
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Concurrent task failed: {e}")
                    results.append({"success": False, "error": str(e)})

        total_time = time.time() - start_time

        return {
            "total_execution_time": total_time,
            "individual_results": results,
            "success_rate": len([r for r in results if r.get("success", False)])
            / len(results),
            "average_execution_time": sum([r.get("execution_time", 0) for r in results])
            / len(results),
            "total_memory_used": sum([r.get("memory_used", 0) for r in results]),
        }

    def analyze_maintenance_complexity(self):
        """Analyze code complexity and maintenance requirements"""

        # Multi-tool approach analysis
        multi_tool_complexity = {
            "dependencies": [
                "undetected-chromedriver",
                "selenium-stealth",
                "scrapy-rotating-proxies",
                "FlareSolverr (Docker)",
                "browserless/chrome (Docker)",
            ],
            "configuration_files": 5,
            "lines_of_code_estimate": 300,
            "update_frequency": "Multiple tools require individual updates",
            "documentation_required": "High - each tool needs separate documentation",
            "complexity_score": 7.5,  # Out of 10
            "pros": [
                "Best-of-breed tools for each function",
                "Proven individual track records",
                "Flexibility to replace individual components",
                "Community support for each tool",
            ],
            "cons": [
                "Complex orchestration logic",
                "Multiple update cycles",
                "More potential failure points",
                "Higher maintenance overhead",
            ],
        }

        # Botasaurus approach analysis
        botasaurus_complexity = {
            "dependencies": ["botasaurus", "botasaurus_driver"],
            "configuration_files": 1,
            "lines_of_code_estimate": 100,
            "update_frequency": "Single framework updates",
            "documentation_required": "Low - unified documentation",
            "complexity_score": 3.5,  # Out of 10
            "pros": [
                "Unified framework",
                "Single point of updates",
                "Comprehensive built-in capabilities",
                "Simplified configuration",
            ],
            "cons": [
                "Single point of failure",
                "Dependent on single maintainer",
                "Less flexibility for individual components",
                "Potential vendor lock-in",
            ],
        }

        return {
            "multi_tool": multi_tool_complexity,
            "botasaurus": botasaurus_complexity,
            "recommendation": "Choose based on team size and maintenance capacity",
        }

    def generate_integration_assessment(self):
        """Assess integration effort with existing IntelForge pipeline"""

        integration_analysis = {
            "existing_pipeline_components": [
                "Academic research tools (paperscraper, arxiv.py)",
                "Reddit scraper (PRAW)",
                "GitHub scraper (PyGitHub)",
                "AI processing (sentence-transformers, FAISS)",
                "Knowledge management (Obsidian output)",
                "Configuration system (config.yaml)",
            ],
            "multi_tool_integration": {
                "compatibility": "High",
                "integration_effort": "Medium",
                "changes_required": [
                    "Update scraping_base.py with new anti-detection",
                    "Configure Docker services in docker-compose.yml",
                    "Add proxy rotation configuration",
                    "Update requirements.txt with new dependencies",
                ],
                "integration_score": 7.0,
                "timeline": "2-3 days",
            },
            "botasaurus_integration": {
                "compatibility": "High",
                "integration_effort": "Low",
                "changes_required": [
                    "Replace existing browser automation with Botasaurus",
                    "Update driver initialization in base classes",
                    "Minimal configuration changes",
                ],
                "integration_score": 9.0,
                "timeline": "1 day",
            },
        }

        return integration_analysis

    async def run_comprehensive_comparison(self):
        """Run comprehensive framework comparison"""
        logger.info("Starting comprehensive framework comparison")

        results = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "test_urls": self.test_urls,
            "performance_tests": {},
            "concurrent_tests": {},
            "maintenance_analysis": {},
            "integration_assessment": {},
            "summary": {},
        }

        # Performance tests on individual URLs
        logger.info("Running individual performance tests...")
        for url in self.test_urls:
            results["performance_tests"][url] = {
                "multi_tool": self.test_multi_tool_approach(url),
                "botasaurus": self.test_botasaurus_approach(url),
                "playwright_baseline": await self.test_playwright_baseline(url),
            }

        # Concurrent performance tests
        logger.info("Running concurrent performance tests...")
        results["concurrent_tests"] = {
            "multi_tool": self.test_concurrent_performance(
                self.test_multi_tool_approach
            ),
            "botasaurus": self.test_concurrent_performance(
                self.test_botasaurus_approach
            ),
        }

        # Maintenance complexity analysis
        results["maintenance_analysis"] = self.analyze_maintenance_complexity()

        # Integration assessment
        results["integration_assessment"] = self.generate_integration_assessment()

        # Include scoring configuration for transparency
        results["scoring_configuration"] = self.scoring_config

        # Generate summary and recommendation
        results["summary"] = self.generate_comparison_summary(results)

        # Save results
        results_file = self.results_dir / f"framework_comparison_{self.session_id}.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(
            f"Comprehensive comparison complete. Results saved to {results_file}"
        )
        return results

    def generate_comparison_summary(self, results):
        """Generate comparison summary with recommendation"""

        # Calculate average performance metrics
        multi_tool_avg_time = 0
        botasaurus_avg_time = 0
        multi_tool_success = 0
        botasaurus_success = 0
        total_tests = len(results["performance_tests"])

        for url_results in results["performance_tests"].values():
            if url_results["multi_tool"]["success"]:
                multi_tool_avg_time += url_results["multi_tool"]["execution_time"]
                multi_tool_success += 1

            if url_results["botasaurus"]["success"]:
                botasaurus_avg_time += url_results["botasaurus"]["execution_time"]
                botasaurus_success += 1

        multi_tool_avg_time = (
            multi_tool_avg_time / multi_tool_success if multi_tool_success > 0 else 0
        )
        botasaurus_avg_time = (
            botasaurus_avg_time / botasaurus_success if botasaurus_success > 0 else 0
        )

        # Generate scoring matrix using configurable parameters
        perf_config = self.scoring_config["performance"]
        rel_config = self.scoring_config["reliability"]
        maint_config = self.scoring_config["maintenance"]

        scoring = {
            "performance": {
                "multi_tool": self._calculate_performance_score(
                    multi_tool_avg_time, perf_config
                ),
                "botasaurus": self._calculate_performance_score(
                    botasaurus_avg_time, perf_config
                ),
            },
            "reliability": {
                "multi_tool": self._calculate_reliability_score(
                    multi_tool_success / total_tests, rel_config
                ),
                "botasaurus": self._calculate_reliability_score(
                    botasaurus_success / total_tests, rel_config
                ),
            },
            "maintenance": {
                "multi_tool": self._calculate_maintenance_score(
                    results["maintenance_analysis"]["multi_tool"]["complexity_score"],
                    maint_config,
                ),
                "botasaurus": self._calculate_maintenance_score(
                    results["maintenance_analysis"]["botasaurus"]["complexity_score"],
                    maint_config,
                ),
            },
            "integration": {
                "multi_tool": results["integration_assessment"][
                    "multi_tool_integration"
                ]["integration_score"],
                "botasaurus": results["integration_assessment"][
                    "botasaurus_integration"
                ]["integration_score"],
            },
        }

        # Calculate weighted total scores
        multi_tool_total = sum(
            scoring[category]["multi_tool"] * self.scoring_config[category]["weight"]
            for category in scoring
        )
        botasaurus_total = sum(
            scoring[category]["botasaurus"] * self.scoring_config[category]["weight"]
            for category in scoring
        )

        # Generate recommendation
        if botasaurus_total > multi_tool_total:
            recommendation = {
                "choice": "botasaurus",
                "confidence": (
                    "high" if botasaurus_total - multi_tool_total > 5 else "medium"
                ),
                "rationale": f"Botasaurus scores {botasaurus_total:.1f} vs Multi-tool {multi_tool_total:.1f}. Better integration and maintenance profile.",
                "next_steps": [
                    "Migrate existing scrapers to Botasaurus framework",
                    "Update configuration for unified approach",
                    "Test integration with academic research tools",
                    "Document new architecture",
                ],
            }
        else:
            recommendation = {
                "choice": "multi_tool",
                "confidence": (
                    "high" if multi_tool_total - botasaurus_total > 5 else "medium"
                ),
                "rationale": f"Multi-tool scores {multi_tool_total:.1f} vs Botasaurus {botasaurus_total:.1f}. Better performance and flexibility.",
                "next_steps": [
                    "Complete multi-tool orchestration setup",
                    "Configure Docker services (FlareSolverr, browserless)",
                    "Implement proxy rotation and stealth enhancements",
                    "Create monitoring dashboard",
                ],
            }

        return {
            "performance_metrics": {
                "multi_tool_avg_time": multi_tool_avg_time,
                "botasaurus_avg_time": botasaurus_avg_time,
                "multi_tool_success_rate": multi_tool_success / total_tests,
                "botasaurus_success_rate": botasaurus_success / total_tests,
            },
            "scoring_matrix": scoring,
            "total_scores": {
                "multi_tool": multi_tool_total,
                "botasaurus": botasaurus_total,
            },
            "recommendation": recommendation,
        }


async def main():
    """Main execution function"""
    comparison = FrameworkComparison()

    print("🔬 Starting Phase 3 Framework Comparison Suite")
    print("=" * 60)

    # Run comprehensive comparison
    results = await comparison.run_comprehensive_comparison()

    # Display results
    print("\n📊 Performance Comparison Results:")
    summary = results["summary"]

    print("\n⏱️ Average Execution Times:")
    print(
        f"   Multi-tool approach: {summary['performance_metrics']['multi_tool_avg_time']:.2f}s"
    )
    print(
        f"   Botasaurus approach: {summary['performance_metrics']['botasaurus_avg_time']:.2f}s"
    )

    print("\n✅ Success Rates:")
    print(
        f"   Multi-tool approach: {summary['performance_metrics']['multi_tool_success_rate']:.1%}"
    )
    print(
        f"   Botasaurus approach: {summary['performance_metrics']['botasaurus_success_rate']:.1%}"
    )

    print("\n🏆 Total Scores (Weighted):")
    print(f"   Multi-tool approach: {summary['total_scores']['multi_tool']:.2f}/10.0")
    print(f"   Botasaurus approach: {summary['total_scores']['botasaurus']:.2f}/10.0")

    # Show scoring breakdown
    print("\n📊 Scoring Breakdown:")
    scoring_matrix = summary["scoring_matrix"]
    scoring_config = results["scoring_configuration"]

    for category in scoring_matrix:
        weight = scoring_config[category]["weight"]
        rationale = scoring_config[category]["rationale"]

        print(f"\n   {category.title()} (Weight: {weight:.0%}):")
        print(f"     Rationale: {rationale}")
        print(f"     Multi-tool: {scoring_matrix[category]['multi_tool']:.1f}")
        print(f"     Botasaurus: {scoring_matrix[category]['botasaurus']:.1f}")

    print("\n🎯 Recommendation:")
    rec = summary["recommendation"]
    print(f"   Choice: {rec['choice'].upper()}")
    print(f"   Confidence: {rec['confidence'].upper()}")
    print(f"   Rationale: {rec['rationale']}")

    print("\n📋 Next Steps:")
    for i, step in enumerate(rec["next_steps"], 1):
        print(f"   {i}. {step}")

    print(
        f"\n📁 Detailed results: {comparison.results_dir}/framework_comparison_{comparison.session_id}.json"
    )
    print("\n✅ Framework Comparison Suite - COMPLETE")


if __name__ == "__main__":
    asyncio.run(main())
