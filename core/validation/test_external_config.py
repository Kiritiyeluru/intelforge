#!/usr/bin/env python3
"""
Test script to verify external configuration support in CanaryValidator v2
"""

import sys
from pathlib import Path

import yaml

sys.path.append("/home/kiriti/alpha_projects/intelforge/scripts")

from canary_validation_system_v2 import EnhancedCanaryValidator


def test_external_config_loading():
    """Test that external YAML configuration is properly loaded"""

    print("🔧 Testing External Configuration Loading")
    print("=" * 50)

    # Test 1: Default config file (if exists)
    config_path = Path("config/canary_targets.yaml")

    if config_path.exists():
        print(f"\n✅ Found config file: {config_path}")

        # Load validator with external config
        validator = EnhancedCanaryValidator()

        print("📊 Configuration loaded:")
        print(f"   Targets: {len(validator.canary_targets)}")
        print(f"   Cache enabled: {validator.cache_enabled}")
        print(
            f"   Browser reuse: {validator.browser_config.get('reuse_session', 'unknown')}"
        )
        print(
            f"   Headless mode: {validator.browser_config.get('headless', 'unknown')}"
        )

        # Show loaded targets
        print("\n🎯 Loaded targets:")
        for target_name, config in validator.canary_targets.items():
            critical = "CRITICAL" if config.get("critical", False) else "optional"
            print(f"   - {target_name} ({critical}): {config.get('url', 'no url')}")

        return True

    else:
        print(f"❌ Config file not found: {config_path}")
        return False


def test_custom_config_file():
    """Test loading from a custom configuration file"""

    print("\n🧪 Testing Custom Configuration File")
    print("=" * 40)

    # Create a temporary test config
    test_config = {
        "canary_targets": {
            "test_target": {
                "url": "https://httpbin.org/status/200",
                "timeout_seconds": 5,
                "critical": True,
                "description": "Test target for configuration",
                "min_content_size": 50,
                "required_elements": ["status"],
                "forbidden_keywords": ["error"],
            }
        },
        "cache_settings": {"duration_minutes": 15, "enabled": False},
        "browser_settings": {
            "reuse_session": False,
            "headless": True,
            "enable_ttr_tracking": True,
        },
    }

    test_config_path = Path("test_canary_config.yaml")

    try:
        # Write test config
        with open(test_config_path, "w") as f:
            yaml.dump(test_config, f, default_flow_style=False)

        print(f"✅ Created test config: {test_config_path}")

        # Load validator with custom config
        validator = EnhancedCanaryValidator(config_file=str(test_config_path))

        print("📊 Custom configuration loaded:")
        print(f"   Targets: {len(validator.canary_targets)}")
        print(f"   Cache enabled: {validator.cache_enabled}")
        print(f"   Browser reuse: {validator.browser_config.get('reuse_session')}")
        print(f"   TTR tracking: {validator.browser_config.get('enable_ttr_tracking')}")

        # Verify settings match
        success = (
            len(validator.canary_targets) == 1
            and "test_target" in validator.canary_targets
            and not validator.cache_enabled
            and not validator.browser_config.get("reuse_session")
            and validator.browser_config.get("enable_ttr_tracking")
        )

        if success:
            print("✅ Custom configuration loaded correctly!")
        else:
            print("❌ Configuration mismatch detected")

        return success

    finally:
        # Clean up test file
        if test_config_path.exists():
            test_config_path.unlink()
            print("🧹 Cleaned up test config file")


def test_fallback_behavior():
    """Test fallback to defaults when config file is missing"""

    print("\n🛡️  Testing Fallback Behavior")
    print("=" * 35)

    # Try to load with non-existent config file
    validator = EnhancedCanaryValidator(config_file="nonexistent_config.yaml")

    print("📊 Fallback configuration:")
    print(f"   Targets: {len(validator.canary_targets)}")
    print(f"   Cache enabled: {validator.cache_enabled}")
    print(f"   Browser reuse: {validator.browser_config.get('reuse_session')}")

    # Should have default targets
    expected_defaults = [
        "basic_connectivity",
        "javascript_execution",
        "anti_detection_basic",
        "finviz_canary",
        "yahoo_finance_canary",
        "httpbin_canary",
    ]

    has_defaults = all(
        target in validator.canary_targets for target in expected_defaults
    )

    if has_defaults:
        print("✅ Fallback to defaults working correctly!")
    else:
        print("❌ Fallback behavior failed")
        print(f"   Expected: {expected_defaults}")
        print(f"   Got: {list(validator.canary_targets.keys())}")

    return has_defaults


def test_config_validation():
    """Test configuration validation and error handling"""

    print("\n🔍 Testing Configuration Validation")
    print("=" * 40)

    # Create invalid config file
    invalid_config_path = Path("invalid_config.yaml")

    try:
        # Write invalid YAML
        with open(invalid_config_path, "w") as f:
            f.write("invalid: yaml: content: [unclosed")

        print("📝 Created invalid config file")

        # Try to load - should fall back to defaults
        validator = EnhancedCanaryValidator(config_file=str(invalid_config_path))

        # Should have fallen back to defaults
        has_fallback = len(validator.canary_targets) == 6  # Default target count

        if has_fallback:
            print("✅ Error handling works - fell back to defaults")
        else:
            print("❌ Error handling failed")

        return has_fallback

    finally:
        if invalid_config_path.exists():
            invalid_config_path.unlink()


if __name__ == "__main__":
    print("🧪 CanaryValidator v2 External Configuration Test")
    print("Testing YAML configuration loading and fallback behavior\n")

    tests = [
        ("External Config Loading", test_external_config_loading),
        ("Custom Config File", test_custom_config_file),
        ("Fallback Behavior", test_fallback_behavior),
        ("Config Validation", test_config_validation),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))

    print("\n🎯 Test Summary:")
    total_tests = len(results)
    passed_tests = sum(1 for _, passed in results if passed)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")

    print(f"\n📊 Overall: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("🏆 External configuration support is working perfectly!")
    else:
        print("⚠️  Some configuration tests failed - needs investigation")
