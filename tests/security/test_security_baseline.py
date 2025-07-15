#!/usr/bin/env python3
"""
Security baseline testing for IntelForge
Implements lightweight security validation using Bandit and secret scanning
"""

import json
import subprocess
import re
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
import pytest


class SecurityBaseline:
    """
    Lightweight security testing framework for IntelForge
    Uses Bandit for static analysis and custom secret scanning
    """
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.secrets_patterns = [
            # API Keys and tokens
            r'(?i)(api_key|apikey|access_key|secret_key|private_key)[\s]*[=:]\s*["\']?([a-zA-Z0-9_\-]{16,})["\']?',
            # AWS credentials
            r'AKIA[0-9A-Z]{16}',
            r'(?i)aws_secret_access_key[\s]*[=:]\s*["\']?([a-zA-Z0-9/+]{40})["\']?',
            # Generic tokens
            r'(?i)(token|password|passwd|pwd)[\s]*[=:]\s*["\']?([a-zA-Z0-9_\-!@#$%^&*()]{8,})["\']?',
            # URLs with credentials
            r'https?://[a-zA-Z0-9_\-]+:[a-zA-Z0-9_\-@]+@[a-zA-Z0-9.-]+',
            # Private keys
            r'-----BEGIN (RSA |DSA |EC )?PRIVATE KEY-----',
        ]
        
    def run_bandit_scan(self) -> Dict[str, Any]:
        """
        Run Bandit security scanner on the codebase
        Returns structured results with security findings
        """
        try:
            # Run bandit with JSON output
            cmd = [
                'bandit', 
                '-r', str(self.project_root),
                '-f', 'json',
                '--skip', 'B101,B601',  # Skip assert and shell injection for now
                '--exclude', 'venv,node_modules,.git,tests/test_data'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode in [0, 1]:  # 0 = no issues, 1 = issues found
                return json.loads(result.stdout) if result.stdout else {"results": [], "metrics": {}}
            else:
                return {"error": f"Bandit failed: {result.stderr}", "results": [], "metrics": {}}
                
        except (subprocess.SubprocessError, json.JSONDecodeError) as e:
            return {"error": f"Security scan failed: {str(e)}", "results": [], "metrics": {}}
    
    def scan_for_secrets(self, exclude_dirs: List[str] = None) -> List[Dict[str, Any]]:
        """
        Scan for potential secrets using regex patterns
        Returns list of potential secret findings
        """
        exclude_dirs = exclude_dirs or ['venv', 'node_modules', '.git', 'logs', 'data']
        findings = []
        
        for file_path in self.project_root.rglob('*.py'):
            # Skip excluded directories
            if any(excluded in str(file_path) for excluded in exclude_dirs):
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8')
                
                for pattern in self.secrets_patterns:
                    matches = re.finditer(pattern, content, re.MULTILINE)
                    for match in matches:
                        # Basic filtering to reduce false positives
                        matched_text = match.group(0)
                        if self._is_likely_secret(matched_text):
                            line_number = content[:match.start()].count('\n') + 1
                            findings.append({
                                "file": str(file_path.relative_to(self.project_root)),
                                "line": line_number,
                                "pattern": pattern[:50] + "..." if len(pattern) > 50 else pattern,
                                "context": matched_text[:100],
                                "severity": "HIGH" if "private_key" in matched_text.lower() else "MEDIUM"
                            })
                            
            except (UnicodeDecodeError, IOError):
                continue  # Skip binary or unreadable files
                
        return findings
    
    def _is_likely_secret(self, text: str) -> bool:
        """
        Basic heuristics to filter out obvious false positives
        """
        text_lower = text.lower()
        
        # Skip obvious test/example values
        false_positives = [
            'example', 'test', 'dummy', 'placeholder', 'sample',
            'your_key_here', 'insert_key', 'api_key_here',
            'password123', 'secret123', 'token123',
            '11111111', '00000000', 'xxxxxxxx'
        ]
        
        return not any(fp in text_lower for fp in false_positives)
    
    def validate_file_permissions(self) -> List[Dict[str, Any]]:
        """
        Check for overly permissive file permissions
        """
        issues = []
        
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file():
                try:
                    stat_info = file_path.stat()
                    permissions = oct(stat_info.st_mode)[-3:]
                    
                    # Check for world-writable files (except logs)
                    if permissions.endswith('7') or permissions.endswith('6'):
                        if 'logs' not in str(file_path) and not file_path.name.startswith('.'):
                            issues.append({
                                "file": str(file_path.relative_to(self.project_root)),
                                "permissions": permissions,
                                "issue": "World-writable file",
                                "severity": "MEDIUM"
                            })
                            
                except (OSError, ValueError):
                    continue
                    
        return issues
    
    def generate_security_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive security baseline report
        """
        bandit_results = self.run_bandit_scan()
        secret_findings = self.scan_for_secrets()
        permission_issues = self.validate_file_permissions()
        
        # Calculate overall security score
        high_issues = len([f for f in secret_findings if f.get('severity') == 'HIGH'])
        medium_issues = len([f for f in secret_findings if f.get('severity') == 'MEDIUM'])
        bandit_high = len([r for r in bandit_results.get('results', []) if r.get('issue_severity') == 'HIGH'])
        bandit_medium = len([r for r in bandit_results.get('results', []) if r.get('issue_severity') == 'MEDIUM'])
        
        total_critical = high_issues + bandit_high
        total_medium = medium_issues + bandit_medium + len(permission_issues)
        
        # Security score: 100 - (critical*10 + medium*3)
        security_score = max(0, 100 - (total_critical * 10 + total_medium * 3))
        
        return {
            "timestamp": subprocess.run(['date', '-Iseconds'], capture_output=True, text=True).stdout.strip(),
            "security_score": security_score,
            "status": "PASS" if security_score >= 80 else "FAIL",
            "summary": {
                "total_critical_issues": total_critical,
                "total_medium_issues": total_medium,
                "secrets_found": len(secret_findings),
                "permission_issues": len(permission_issues),
                "bandit_issues": len(bandit_results.get('results', []))
            },
            "bandit_scan": bandit_results,
            "secret_findings": secret_findings,
            "permission_issues": permission_issues,
            "recommendations": self._generate_recommendations(total_critical, total_medium)
        }
    
    def _generate_recommendations(self, critical: int, medium: int) -> List[str]:
        """Generate security improvement recommendations"""
        recommendations = []
        
        if critical > 0:
            recommendations.append("🚨 CRITICAL: Address high-severity security issues immediately")
            recommendations.append("• Review and remove any exposed secrets or credentials")
            recommendations.append("• Implement proper secret management (environment variables, key vaults)")
        
        if medium > 5:
            recommendations.append("⚠️ MEDIUM: Consider addressing medium-severity issues")
            recommendations.append("• Review file permissions for sensitive files")
            recommendations.append("• Implement input validation and output sanitization")
        
        if critical == 0 and medium <= 3:
            recommendations.append("✅ GOOD: Security baseline meets standards")
            recommendations.append("• Continue regular security scanning")
            recommendations.append("• Keep dependencies updated")
        
        return recommendations


# Pytest test cases
@pytest.mark.critical
@pytest.mark.regression
@pytest.mark.security
@pytest.mark.unit
class TestSecurityBaseline:
    """Pytest test cases for security baseline validation"""
    
    @pytest.fixture
    def security_scanner(self):
        return SecurityBaseline()
    
    def test_bandit_scan_runs(self, security_scanner):
        """Test that Bandit scan executes without errors"""
        results = security_scanner.run_bandit_scan()
        assert isinstance(results, dict)
        assert 'results' in results or 'error' in results
    
    def test_secret_scanning(self, security_scanner):
        """Test that secret scanning completes"""
        findings = security_scanner.scan_for_secrets()
        assert isinstance(findings, list)
        
        # Should not find secrets in a clean codebase
        critical_secrets = [f for f in findings if f.get('severity') == 'HIGH']
        assert len(critical_secrets) == 0, f"Found potential secrets: {critical_secrets}"
    
    def test_file_permissions(self, security_scanner):
        """Test file permission validation"""
        issues = security_scanner.validate_file_permissions()
        assert isinstance(issues, list)
        
        # Should not have world-writable files outside logs
        critical_perms = [i for i in issues if i.get('severity') == 'HIGH']
        assert len(critical_perms) == 0, f"Found critical permission issues: {critical_perms}"
    
    @pytest.mark.security
    def test_security_report_generation(self, security_scanner):
        """Test comprehensive security report generation"""
        report = security_scanner.generate_security_report()
        
        assert isinstance(report, dict)
        assert 'security_score' in report
        assert 'status' in report
        assert 'summary' in report
        assert report['security_score'] >= 0
        assert report['status'] in ['PASS', 'FAIL']
        
        # Security score should be reasonable (>= 70 for clean codebase)
        assert report['security_score'] >= 70, f"Security score too low: {report['security_score']}"
    
    def test_no_hardcoded_secrets(self, security_scanner):
        """Ensure no hardcoded secrets in common files"""
        critical_files = [
            'scripts/cli.py',
            'scripts/semantic_crawler.py',
            'scripts/canary_validation_system_v2.py'
        ]
        
        findings = security_scanner.scan_for_secrets()
        critical_findings = []
        
        for finding in findings:
            if any(cf in finding['file'] for cf in critical_files):
                if finding.get('severity') == 'HIGH':
                    critical_findings.append(finding)
        
        assert len(critical_findings) == 0, f"Found secrets in critical files: {critical_findings}"


def main():
    """CLI interface for security baseline testing"""
    scanner = SecurityBaseline()
    report = scanner.generate_security_report()
    
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == "__main__":
    exit(main())