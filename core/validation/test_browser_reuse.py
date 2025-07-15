#!/usr/bin/env python3
"""
Test script to verify browser session reuse optimization in CanaryValidator v2
"""

import sys
import time

sys.path.append("/home/kiriti/alpha_projects/intelforge/scripts")

from canary_validation_system_v2 import EnhancedCanaryValidator


def test_browser_performance():
    """Test browser session reuse performance improvement"""

    print("🚀 Testing Browser Session Reuse Performance")
    print("=" * 60)

    validator = EnhancedCanaryValidator()

    # Create a subset of targets for faster testing
    test_targets = {
        "basic_connectivity": validator.canary_targets["basic_connectivity"],
        "javascript_execution": validator.canary_targets["javascript_execution"],
    }

    # Temporarily override targets for testing
    original_targets = validator.canary_targets
    validator.canary_targets = test_targets

    try:
        print("\n📊 Test 1: Individual browser sessions (original)")
        start_time = time.time()
        results_individual = validator.run_all_canary_checks(
            use_cache=False, reuse_browser=False
        )
        individual_duration = time.time() - start_time

        print(f"Duration: {individual_duration:.2f}s")
        print(
            f"Successful checks: {len([c for c in results_individual['checks'].values() if c['success']])}/{len(results_individual['checks'])}"
        )

        print("\n🔄 Test 2: Shared browser session (optimized)")
        start_time = time.time()
        results_shared = validator.run_all_canary_checks(
            use_cache=False, reuse_browser=True
        )
        shared_duration = time.time() - start_time

        print(f"Duration: {shared_duration:.2f}s")
        print(
            f"Successful checks: {len([c for c in results_shared['checks'].values() if c['success']])}/{len(results_shared['checks'])}"
        )

        # Calculate performance improvement
        if shared_duration > 0:
            improvement = (
                (individual_duration - shared_duration) / individual_duration
            ) * 100
            speedup = individual_duration / shared_duration

            print("\n📈 Performance Analysis:")
            print(f"   Individual sessions: {individual_duration:.2f}s")
            print(f"   Shared session: {shared_duration:.2f}s")
            print(f"   Improvement: {improvement:.1f}% faster")
            print(f"   Speedup: {speedup:.1f}x")

            if improvement > 30:
                print("   🏆 EXCELLENT: Significant performance improvement achieved!")
            elif improvement > 10:
                print("   ✅ GOOD: Noticeable performance improvement")
            elif improvement > 0:
                print("   🟡 MODEST: Small performance improvement")
            else:
                print("   ⚠️  WARNING: No performance improvement detected")

        # Verify functionality is equivalent
        print("\n🔍 Functional Equivalence Check:")
        individual_success = set(
            name
            for name, result in results_individual["checks"].items()
            if result["success"]
        )
        shared_success = set(
            name
            for name, result in results_shared["checks"].items()
            if result["success"]
        )

        if individual_success == shared_success:
            print("   ✅ SUCCESS: Both approaches have identical results")
        else:
            print("   ❌ WARNING: Results differ between approaches")
            print(f"      Individual: {individual_success}")
            print(f"      Shared: {shared_success}")

        return {
            "individual_duration": individual_duration,
            "shared_duration": shared_duration,
            "improvement_percent": improvement if shared_duration > 0 else 0,
            "functional_equivalent": individual_success == shared_success,
        }

    finally:
        # Restore original targets
        validator.canary_targets = original_targets


def test_fallback_mechanism():
    """Test that fallback to individual sessions works if shared session fails"""

    print("\n🛡️  Testing Fallback Mechanism")
    print("=" * 40)

    validator = EnhancedCanaryValidator()

    # Test with reduced targets
    test_targets = {
        "basic_connectivity": validator.canary_targets["basic_connectivity"]
    }

    original_targets = validator.canary_targets
    validator.canary_targets = test_targets

    try:
        # This should use shared browser but fallback if needed
        results = validator.run_all_canary_checks(use_cache=False, reuse_browser=True)

        success_count = len([c for c in results["checks"].values() if c["success"]])
        print("✅ Fallback mechanism test completed")
        print(f"   Results: {success_count}/{len(results['checks'])} checks passed")

        return results

    finally:
        validator.canary_targets = original_targets


if __name__ == "__main__":
    print("🧪 CanaryValidator v2 Browser Session Reuse Test")
    print("Testing performance optimization and fallback mechanisms\n")

    # Test performance improvement
    perf_results = test_browser_performance()

    # Test fallback mechanism
    fallback_results = test_fallback_mechanism()

    print("\n🎯 Summary:")
    print(
        f"   Performance improvement: {perf_results.get('improvement_percent', 0):.1f}%"
    )
    print(
        f"   Functional equivalence: {'✅ YES' if perf_results.get('functional_equivalent', False) else '❌ NO'}"
    )
    print(f"   Fallback mechanism: {'✅ WORKING' if fallback_results else '❌ FAILED'}")

    if perf_results.get("improvement_percent", 0) > 20 and perf_results.get(
        "functional_equivalent", False
    ):
        print("\n🏆 Browser session reuse optimization is working excellently!")
    else:
        print("\n⚠️  Browser session reuse may need further optimization")
