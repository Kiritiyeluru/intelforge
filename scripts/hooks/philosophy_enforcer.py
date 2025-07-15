#!/usr/bin/env python3
"""
CRITICAL PHILOSOPHY ENFORCER - Zero Tolerance for Custom Code

This hook validates ALL Claude responses and tool usage against the 
REUSE OVER REBUILD philosophy. Blocks custom implementations when 
existing tools are available.

PHILOSOPHY: NEVER write custom code when existing libraries/tools exist
"""

import sys
import json
import re
import os
from pathlib import Path
from typing import Dict, List, Set

class PhilosophyEnforcer:
    """Enforces REUSE OVER REBUILD philosophy with zero tolerance"""
    
    # Keywords that indicate custom implementation attempts
    CUSTOM_CODE_INDICATORS = {
        'function definitions': [
            r'def\s+(?:scrape|extract|parse|fetch|crawl|download)_\w+',
            r'def\s+(?:http|request|get|post)_\w+',
            r'def\s+(?:beautiful_soup|selenium|requests)_\w+',
            r'class\s+\w*(?:Scraper|Parser|Crawler|Extractor)',
        ],
        'manual implementations': [
            r'BeautifulSoup\(',
            r'requests\.get\(',
            r'selenium\.',
            r'urllib\.',
            r'http\.client',
            r'socket\.',
            r'from\s+bs4\s+import',
            r'import\s+requests\b',
            r'import\s+urllib',
            r'import\s+selenium',
        ],
        'banned phrases': [
            r'let\'s\s+(?:build|create|implement|write)\s+(?:a|our|custom)',
            r'we\'ll\s+(?:build|create|implement|write)',
            r'I\'ll\s+(?:build|create|implement|write)',
            r'custom\s+(?:scraper|parser|extractor|crawler)',
            r'from\s+scratch',
            r'build\s+our\s+own',
            r'implement\s+(?:a|our)\s+custom',
        ]
    }
    
    # Approved frameworks and libraries (ALLOWED)
    APPROVED_FRAMEWORKS = {
        'scrapy', 'trafilatura', 'scrapy-playwright', 'nodriver', 
        'camoufox', 'scrapling', 'paperscraper', 'autoscraper',
        'stealth-requests', 'news-please', 'playwright-python',
        'arxiv.py', 'feedparser', 'botasaurus', 'selectolax',
        'httpx', 'polars', 'praw', 'pygithub'
    }
    
    def __init__(self):
        self.violations = []
        self.philosophy_text = self._load_philosophy()
    
    def _load_philosophy(self) -> str:
        """Load the critical philosophy text for reminders"""
        return """
🚨 CRITICAL DEVELOPMENT PHILOSOPHY - ABSOLUTE MANDATORY 🚨

ZERO TOLERANCE FOR CUSTOM CODE WHEN ALTERNATIVES EXIST:
- REUSE OVER REBUILD: NEVER write custom code when existing libraries/tools exist
- CHECK FIRST, BUILD NEVER: Always search for existing solutions before coding
- FRAMEWORK OVER CUSTOM: Use established frameworks rather than custom implementations
- TOOL RESEARCH MANDATORY: Use find_tools_template.md before any development
- PROVEN OVER NOVEL: Prefer battle-tested tools over custom logic
- WRAP, DON'T WRITE: Integrate existing tools rather than reimplementing

EVIDENCE OF SUCCESS: Phase 2C - Replaced 400+ line custom academic scraper 
with <200 lines using production frameworks. This philosophy WORKS.
"""
    
    def validate_tool_input(self, tool_name: str, tool_input: Dict) -> bool:
        """Validate tool usage against philosophy"""
        self.violations = []
        
        if tool_name in ['Write', 'Edit', 'MultiEdit']:
            content = tool_input.get('content', '') or tool_input.get('new_string', '')
            file_path = tool_input.get('file_path', '')
            
            # Skip non-Python files
            if not file_path.endswith('.py'):
                return True
                
            # Check for custom code violations
            for category, patterns in self.CUSTOM_CODE_INDICATORS.items():
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                        self.violations.append({
                            'category': category,
                            'pattern': pattern,
                            'file': file_path,
                            'severity': 'CRITICAL'
                        })
            
            # Check if approved frameworks are being used
            using_approved = any(
                framework in content.lower() 
                for framework in self.APPROVED_FRAMEWORKS
            )
            
            # If custom patterns found but no approved frameworks, BLOCK
            if self.violations and not using_approved:
                return False
                
        return True
    
    def get_violation_report(self) -> str:
        """Generate detailed violation report"""
        if not self.violations:
            return ""
            
        report = [
            "🚨 PHILOSOPHY VIOLATION DETECTED 🚨",
            "",
            "CRITICAL ERROR: Attempt to write custom code when existing tools available!",
            "",
            "VIOLATIONS FOUND:"
        ]
        
        for i, violation in enumerate(self.violations, 1):
            report.append(f"{i}. {violation['category'].upper()}")
            report.append(f"   Pattern: {violation['pattern']}")
            report.append(f"   File: {violation['file']}")
            report.append(f"   Severity: {violation['severity']}")
            report.append("")
        
        report.extend([
            "REQUIRED ACTION:",
            "1. STOP current implementation",
            "2. Research existing tools using find_tools_template.md",
            "3. Use approved frameworks from the APPROVED_FRAMEWORKS list",
            "4. Wrap existing tools instead of reimplementing",
            "",
            "APPROVED FRAMEWORKS:",
            ", ".join(sorted(self.APPROVED_FRAMEWORKS)),
            "",
            self.philosophy_text
        ])
        
        return "\n".join(report)
    
    def enforce_philosophy_reminder(self) -> str:
        """Generate philosophy reminder for every response"""
        return f"""
📋 PHILOSOPHY REMINDER: {self.philosophy_text.strip()}

✅ Before proceeding: Have you checked for existing tools/frameworks?
✅ Are you using approved frameworks instead of custom implementations?
✅ Is this the minimal wrapper approach around existing tools?
"""

def main():
    """Main hook execution"""
    if len(sys.argv) < 3:
        print("Usage: philosophy_enforcer.py <tool_name> <tool_input_json>")
        sys.exit(1)
    
    tool_name = sys.argv[1]
    tool_input_raw = sys.argv[2]
    
    try:
        tool_input = json.loads(tool_input_raw)
    except json.JSONDecodeError:
        print("Error: Invalid JSON input")
        sys.exit(1)
    
    enforcer = PhilosophyEnforcer()
    
    # Validate against philosophy
    is_valid = enforcer.validate_tool_input(tool_name, tool_input)
    
    if not is_valid:
        # Write violation to file that Claude might read
        violation_file = Path("/home/kiriti/alpha_projects/intelforge/.claude/PHILOSOPHY_VIOLATION_ALERT.md")
        violation_message = f"""# 🚨 PHILOSOPHY VIOLATION DETECTED 🚨

**CRITICAL: Custom code detected when approved frameworks should be used!**

## REUSE OVER REBUILD PRINCIPLE VIOLATED

- ❌ **BLOCKED**: Custom scrapers, manual requests, BeautifulSoup implementations
- ✅ **APPROVED**: scrapy, trafilatura, playwright, botasaurus, paperscraper

## EVIDENCE
Phase 2C: 400+ custom lines → <200 framework lines

## ACTION REQUIRED
1. Research existing tools using find_tools_template.md
2. Use approved frameworks only
3. Implement minimal wrapper approach

{enforcer.get_violation_report()}

**🚨 PLEASE USE APPROVED FRAMEWORKS INSTEAD OF CUSTOM CODE 🚨**
"""
        
        with open(violation_file, "w") as f:
            f.write(violation_message)
            
        print("🚨 PHILOSOPHY VIOLATION - See .claude/PHILOSOPHY_VIOLATION_ALERT.md")
        # Exit with error to prevent the action
        sys.exit(1)
    
    # Always print philosophy reminder
    print(enforcer.enforce_philosophy_reminder())
    
    print("✅ Philosophy compliance validated - proceeding with approved approach")

if __name__ == "__main__":
    main()