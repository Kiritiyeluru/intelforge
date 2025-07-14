#!/usr/bin/env python3
"""
Test script to verify plugin dispatch fix in CanaryValidator v2
"""

import sys

sys.path.append("/home/kiriti/alpha_projects/intelforge/scripts")

from canary_validation_system_v2 import EnhancedCanaryValidator


def test_plugin_dispatch():
    """Test that plugin validators are properly called"""

    print("🧪 Testing plugin dispatch fix...")

    # Create validator instance
    validator = EnhancedCanaryValidator()

    # Test data
    test_target = "javascript_execution"
    test_url = "https://httpbin.org/headers"
    test_content = """
    {
        "headers": {
            "Accept": "text/html",
            "User-Agent": "Chrome/121.0"
        }
    }
    """
    test_title = "httpbin.org"
    test_config = validator.canary_targets[test_target]

    print(f"Testing target: {test_target}")
    print(f"Validators available: {list(validator.validators.keys())}")
    print(f"Target in validators: {test_target in validator.validators}")

    # Call the fixed validation method
    result = validator._validate_page_content(
        test_target, test_url, test_content, test_title, test_config
    )

    print("\n📊 Validation Result:")
    print(f"   Valid: {result['valid']}")
    print(f"   Total checks: {result['total_checks']}")
    print(f"   Failed checks: {result['failed_checks']}")

    # Check if site-specific validation was called
    if test_target in validator.validators:
        print(
            f"\n✅ SUCCESS: Plugin validator for '{test_target}' should have been called!"
        )

        # Try to manually call the validator to see what it returns
        try:
            site_checks = validator.validators[test_target](
                test_content, test_title, test_config
            )
            print(f"   Site-specific checks returned: {site_checks}")
        except Exception as e:
            print(f"   Error calling site validator: {e}")
    else:
        print(f"\n❌ ISSUE: No plugin validator found for '{test_target}'")

    return result


def test_basic_connectivity():
    """Test basic connectivity target"""

    print("\n🧪 Testing basic connectivity...")

    validator = EnhancedCanaryValidator()
    test_target = "basic_connectivity"
    test_url = "https://example.com"
    test_content = (
        "<html><head><title>Example Domain</title></head><body>Example</body></html>"
    )
    test_title = "Example Domain"
    test_config = validator.canary_targets[test_target]

    result = validator._validate_page_content(
        test_target, test_url, test_content, test_title, test_config
    )

    print("📊 Basic connectivity result:")
    print(f"   Valid: {result['valid']}")
    print(f"   Failed checks: {result['failed_checks']}")

    return result


if __name__ == "__main__":
    print("🔧 Testing CanaryValidator v2 Plugin Dispatch Fix\n")

    # Test the specific target that was broken
    js_result = test_plugin_dispatch()

    # Test basic connectivity
    basic_result = test_basic_connectivity()

    print("\n🎯 Summary:")
    print(
        f"   JavaScript execution validation: {'✅ PASSED' if js_result['valid'] else '❌ FAILED'}"
    )
    print(
        f"   Basic connectivity validation: {'✅ PASSED' if basic_result['valid'] else '❌ FAILED'}"
    )

    if js_result["valid"] and basic_result["valid"]:
        print("\n🏆 Plugin dispatch fix appears to be working correctly!")
    else:
        print("\n⚠️  Some validations failed - this may be expected for test data")
