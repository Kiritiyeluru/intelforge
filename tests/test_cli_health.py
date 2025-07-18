#!/usr/bin/env python3
"""
CLI Health Contracts & Smoke Testing
Based on 'Overlooked Areas' recommendation for CLI Health Contracts

Purpose: Automated testing to ensure semantic_crawler.py doesn't crash silently
"""

import subprocess
import sys
import tempfile
import json
from pathlib import Path

def run_cli_command(command, timeout=45):
    """Run CLI command and return result"""
    try:
        # Use bash explicitly to support source command
        result = subprocess.run(
            ['bash', '-c', command],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def test_help_command():
    """Test CLI help command"""
    print("🔍 Testing --help command...")
    returncode, stdout, stderr = run_cli_command("source venv/bin/activate && python scripts/semantic_crawler.py --help", timeout=60)

    if returncode == 0:
        print("  ✅ Help command successful")
        return True
    else:
        print(f"  ❌ Help command failed: {stderr}")
        return False

def test_health_check():
    """Test CLI health check"""
    print("🔍 Testing --health-check command...")
    returncode, stdout, stderr = run_cli_command("source venv/bin/activate && python scripts/semantic_crawler.py --health-check", timeout=60)

    if returncode == 0 and "Health check completed successfully" in stdout:
        print("  ✅ Health check successful")
        return True
    else:
        print(f"  ❌ Health check failed: {stderr}")
        return False

def test_dry_run():
    """Test dry run functionality"""
    print("🔍 Testing --dry-run command...")

    # Create temporary URL file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("https://www.quantstart.com/articles/\n")
        temp_url_file = f.name

    try:
        command = f"source venv/bin/activate && python scripts/semantic_crawler.py --url-file {temp_url_file} --threshold 0.6 --dry-run"
        returncode, stdout, stderr = run_cli_command(command, timeout=90)

        if returncode == 0 and "DRY RUN" in stdout:
            print("  ✅ Dry run successful")
            return True
        else:
            print(f"  ❌ Dry run failed: {stderr}")
            return False
    finally:
        Path(temp_url_file).unlink()

def test_metadata_output():
    """Test metadata output functionality"""
    print("🔍 Testing --metadata-output command...")

    # Create temporary URL file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("https://www.quantstart.com/articles/\n")
        temp_url_file = f.name

    # Create temporary metadata file path
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_metadata_file = f.name

    try:
        command = f"source venv/bin/activate && python scripts/semantic_crawler.py --url-file {temp_url_file} --threshold 0.6 --metadata-output {temp_metadata_file} --validate-content --dry-run"
        returncode, stdout, stderr = run_cli_command(command, timeout=90)

        if returncode == 0 and "Metadata saved" in stdout:
            # Verify metadata file was created and contains valid JSON
            if Path(temp_metadata_file).exists():
                with open(temp_metadata_file, 'r') as f:
                    metadata = json.load(f)
                    if isinstance(metadata, list) and len(metadata) > 0:
                        print("  ✅ Metadata output successful")
                        return True
            print("  ❌ Metadata file not created or invalid")
            return False
        else:
            print(f"  ❌ Metadata output failed: {stderr}")
            return False
    finally:
        Path(temp_url_file).unlink()
        Path(temp_metadata_file).unlink(missing_ok=True)

def test_content_validation():
    """Test content validation functionality"""
    print("🔍 Testing --validate-content command...")

    # Create temporary URL file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("https://www.quantstart.com/articles/\n")
        temp_url_file = f.name

    try:
        command = f"source venv/bin/activate && python scripts/semantic_crawler.py --url-file {temp_url_file} --threshold 0.6 --validate-content --dry-run"
        returncode, stdout, stderr = run_cli_command(command, timeout=90)

        if returncode == 0 and "Content validation:" in stdout:
            print("  ✅ Content validation successful")
            return True
        else:
            print(f"  ❌ Content validation failed: {stderr}")
            return False
    finally:
        Path(temp_url_file).unlink()

def test_phase1_features():
    """Test Phase 1 enhanced filtering features"""
    print("🔍 Testing Phase 1 filtering features...")

    # Create temporary URL file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("https://www.quantstart.com/articles/\n")
        temp_url_file = f.name

    try:
        command = f"source venv/bin/activate && python scripts/semantic_crawler.py --url-file {temp_url_file} --threshold 0.6 --include-keywords 'strategy,backtest' --min-word-count 100 --max-word-count 50000 --content-type-filter 'article,codeblock' --dry-run"
        returncode, stdout, stderr = run_cli_command(command, timeout=90)

        if returncode == 0 and "Include keywords:" in stdout:
            print("  ✅ Phase 1 filtering successful")
            return True
        else:
            print(f"  ❌ Phase 1 filtering failed: {stderr}")
            return False
    finally:
        Path(temp_url_file).unlink()

def test_phase2_rate_limiting():
    """Test Phase 2 rate limiting and reliability features"""
    print("🔍 Testing Phase 2 rate limiting...")

    # Create temporary URL file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("https://www.quantstart.com/articles/\n")
        temp_url_file = f.name

    try:
        command = f"source venv/bin/activate && python scripts/semantic_crawler.py --url-file {temp_url_file} --threshold 0.6 --rate-limit 3 --timeout 10 --backoff-factor 2 --max-retries 2 --dry-run"
        returncode, stdout, stderr = run_cli_command(command, timeout=90)

        if returncode == 0 and "Rate limit: 3" in stdout:
            print("  ✅ Phase 2 rate limiting successful")
            return True
        else:
            print(f"  ❌ Phase 2 rate limiting failed: {stderr}")
            return False
    finally:
        Path(temp_url_file).unlink()

def test_phase2_error_recovery():
    """Test Phase 2 enhanced error recovery features"""
    print("🔍 Testing Phase 2 error recovery...")

    # Create temporary URL file with invalid URL to test error recovery
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("https://invalid-domain-for-testing-12345.com/test\n")
        temp_url_file = f.name

    try:
        command = f"source venv/bin/activate && python scripts/semantic_crawler.py --url-file {temp_url_file} --threshold 0.6 --max-retries 2 --timeout 5 --backoff-factor 1.5 --dry-run"
        returncode, stdout, stderr = run_cli_command(command, timeout=60)

        # Should fail gracefully with retry messages
        if "retry" in stdout.lower() or "failed to fetch" in stdout.lower():
            print("  ✅ Phase 2 error recovery successful")
            return True
        else:
            print(f"  ❌ Phase 2 error recovery failed: {stderr}")
            return False
    finally:
        Path(temp_url_file).unlink()

def main():
    """Run all CLI smoke tests"""
    print("🚀 Running CLI Health Contracts & Smoke Tests")
    print("="*60)

    tests = [
        ("Help Command", test_help_command),
        ("Health Check", test_health_check),
        ("Dry Run", test_dry_run),
        ("Metadata Output", test_metadata_output),
        ("Content Validation", test_content_validation),
        ("Phase 1 Features", test_phase1_features),
        ("Phase 2 Rate Limiting", test_phase2_rate_limiting),
        ("Phase 2 Error Recovery", test_phase2_error_recovery),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            failed += 1

    print("\n" + "="*60)
    print("📊 CLI SMOKE TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success rate: {(passed / (passed + failed) * 100):.1f}%")

    if failed == 0:
        print("🎉 All CLI smoke tests passed!")
        return True
    else:
        print("⚠️ Some CLI smoke tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
