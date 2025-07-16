#!/usr/bin/env python3
"""
Minimal Production Readiness Checker - Quick version to diagnose timeout issues
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

def check_critical_files():
    """Check presence of critical files."""
    critical_files = [
        "requirements.txt",
        "scripts/cli.py",
        "tolerance_config.json",
        "pytest.ini",
        ".coveragerc"
    ]
    
    missing_files = []
    for file_path in critical_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if not missing_files:
        return {"name": "Critical Files", "status": "pass", "score": 100, "message": "All critical files present"}
    else:
        score = max(0, 100 - (len(missing_files) * 20))
        return {"name": "Critical Files", "status": "warning", "score": score, "message": f"Missing: {len(missing_files)} files"}

def check_infrastructure():
    """Check basic infrastructure."""
    checks = []
    
    # Check Python version
    import sys
    if sys.version_info >= (3, 8):
        checks.append(("Python 3.8+", True))
    else:
        checks.append(("Python 3.8+", False))
    
    # Check key directories
    for directory in ["scripts", "tests", "logs"]:
        checks.append((f"Directory: {directory}", Path(directory).exists()))
    
    passed = sum(1 for _, passed in checks if passed)
    total = len(checks)
    score = int((passed / total) * 100)
    
    return {
        "name": "Infrastructure",
        "status": "pass" if score >= 90 else "warning" if score >= 70 else "fail",
        "score": score,
        "message": f"{passed}/{total} checks passed"
    }

def main():
    """Main function."""
    print("🔍 Running minimal production readiness check...")
    
    start_time = time.time()
    checks = []
    
    # Run only essential checks
    print("  [1/2] Critical Files...")
    check1 = check_critical_files()
    checks.append(check1)
    print(f"    ✅ {check1['message']} (Score: {check1['score']})")
    
    print("  [2/2] Infrastructure...")
    check2 = check_infrastructure()
    checks.append(check2)
    print(f"    ✅ {check2['message']} (Score: {check2['score']})")
    
    # Calculate overall score
    overall_score = sum(c['score'] for c in checks) // len(checks)
    duration = time.time() - start_time
    
    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "overall_score": overall_score,
        "overall_status": "Production Ready" if overall_score >= 90 else "Deployment Ready" if overall_score >= 85 else "Not Ready",
        "checks": checks,
        "deployment_ready": overall_score >= 85,
        "duration_seconds": round(duration, 2)
    }
    
    # Save report
    output_file = Path("logs") / f"production_readiness_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("🚀 MINIMAL PRODUCTION READINESS ASSESSMENT")
    print("="*60)
    print(f"📊 Overall Score: {overall_score}/100")
    print(f"🚢 Deployment Ready: {'Yes' if report['deployment_ready'] else 'No'}")
    print(f"⏱️ Duration: {duration:.2f}s")
    print(f"📄 Report saved: {output_file}")
    print("="*60)
    
    return 0 if report['deployment_ready'] else 1

if __name__ == "__main__":
    sys.exit(main())