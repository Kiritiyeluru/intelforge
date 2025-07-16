#!/bin/bash
set -e

echo "🔐 Running comprehensive security scan..."

# Create reports directory if it doesn't exist
mkdir -p reports

# Activate virtual environment
source .venv/bin/activate 2>/dev/null || echo "Virtual environment not found, using system Python"

# SAST Analysis
echo "1. Running Semgrep (SAST)..."
semgrep --config=auto --json --output=reports/semgrep.json . || true

echo "2. Running Bandit (Python SAST)..."
bandit -r ./scrapers ./scripts -f json -o reports/bandit.json 2>/dev/null || true

# Secret Detection
echo "3. Running Gitleaks (Git history)..."
~/.local/bin/gitleaks git --report-format json --report-path reports/gitleaks.json . || true

echo "4. Running truffleHog (live files)..."
~/.local/bin/trufflehog filesystem . --json > reports/trufflehog.json 2>/dev/null || true

# Dependency Scanning
echo "5. Running OSV-Scanner (dependencies)..."
~/.local/bin/osv-scanner -r . --format json --output reports/osv.json 2>/dev/null || true

echo "6. Running Safety (Python dependencies)..."
safety check --json --output reports/safety.json 2>/dev/null || true

echo "7. Running Cargo Audit (Rust dependencies)..."
if [ -f "Cargo.toml" ]; then
    ~/.cargo/bin/cargo audit --json > reports/cargo-audit.json 2>/dev/null || true
else
    echo "No Cargo.toml found, skipping Rust audit"
    echo '{"vulnerabilities": [], "warnings": [], "summary": "No Rust dependencies found"}' > reports/cargo-audit.json
fi

# Infrastructure Scanning
echo "8. Running Checkov (Infrastructure)..."
checkov -d . --output json > reports/checkov.json 2>/dev/null || true

# Generate summary
echo "9. Generating security summary..."
python3 -c "
import json
import os
from pathlib import Path

def count_issues(file_path, key_path):
    try:
        with open(file_path) as f:
            data = json.load(f)

        # Navigate through key path
        current = data
        for key in key_path:
            if isinstance(current, list):
                return len(current)
            current = current.get(key, [])

        return len(current) if isinstance(current, list) else 0
    except:
        return 0

# Count issues from each tool
counts = {
    'Semgrep': count_issues('reports/semgrep.json', ['results']),
    'Bandit': count_issues('reports/bandit.json', ['results']),
    'Gitleaks': count_issues('reports/gitleaks.json', []),
    'truffleHog': count_issues('reports/trufflehog.json', []),
    'OSV-Scanner': count_issues('reports/osv.json', ['results']),
    'Safety': count_issues('reports/safety.json', ['vulnerabilities']),
    'Cargo Audit': count_issues('reports/cargo-audit.json', ['vulnerabilities']),
    'Checkov': count_issues('reports/checkov.json', ['results', 'failed_checks'])
}

print('\\n📊 Security Scan Summary:')
print('=' * 40)
total_issues = 0
for tool, count in counts.items():
    print(f'{tool:15}: {count:4} issues')
    total_issues += count
print('=' * 40)
print(f'Total Issues    : {total_issues:4}')

# Create summary file
with open('reports/security_summary.json', 'w') as f:
    json.dump({
        'total_issues': total_issues,
        'tool_counts': counts,
        'scan_timestamp': '$(date -Iseconds)'
    }, f, indent=2)
"

echo "✅ Security scan completed! Reports in reports/ directory"
echo "📈 Summary saved to reports/security_summary.json"
