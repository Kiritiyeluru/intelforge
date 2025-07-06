#!/usr/bin/env python3
"""
Module Structure Guardian Hook for IntelForge
Ensures all new Python modules follow IntelForge patterns and conventions
"""

import json
import os
import sys
import ast
from pathlib import Path
from datetime import datetime
import re

# Configure paths
HOOKS_DIR = Path(__file__).parent
PROJECT_ROOT = HOOKS_DIR.parent.parent
CLAUDE_DIR = PROJECT_ROOT / ".claude"
MODULE_PATTERNS_FILE = CLAUDE_DIR / "module_patterns.json"
DOCS_DIR = PROJECT_ROOT / "docs"
COMPLIANCE_REPORT_FILE = DOCS_DIR / "module_compliance_report.md"

# IntelForge pattern requirements
INTELFORGE_PATTERNS = {
    "phase_naming": {
        "pattern": r"^phase_\d{2}_\w+\.py$",
        "description": "Phase files must follow phase_XX_name.py format",
        "required": True
    },
    "docstring": {
        "pattern": r'"""[\s\S]*?"""',
        "description": "Module must have a docstring",
        "required": True
    },
    "cli_arguments": {
        "patterns": ["--dry-run", "--config", "argparse", "ArgumentParser"],
        "description": "Should include CLI argument parsing with --dry-run and --config",
        "required": False
    },
    "logging": {
        "patterns": ["import logging", "logging.getLogger", "logger"],
        "description": "Should use proper logging setup",
        "required": True
    },
    "error_handling": {
        "patterns": ["try:", "except", "Exception", "Error"],
        "description": "Should include error handling",
        "required": True
    },
    "config_loading": {
        "patterns": ["config.yaml", "load_config", "CONFIG"],
        "description": "Should load configuration from config.yaml",
        "required": False
    },
    "base_scraper": {
        "patterns": ["BaseScraper", "scraping_base"],
        "description": "Scrapers should inherit from BaseScraper",
        "required_for": ["scrapers/"]
    },
    "main_function": {
        "patterns": ['if __name__ == "__main__":', "main()"],
        "description": "Should have proper main function execution",
        "required": True
    },
    "obsidian_output": {
        "patterns": ["vault/notes", "markdown", "frontmatter"],
        "description": "Should output to Obsidian-compatible format",
        "required_for": ["scrapers/", "phase_"]
    }
}

def ensure_directories():
    """Create necessary directories if they don't exist"""
    CLAUDE_DIR.mkdir(exist_ok=True)
    DOCS_DIR.mkdir(exist_ok=True)

def load_module_patterns():
    """Load existing module patterns or create new structure"""
    if MODULE_PATTERNS_FILE.exists():
        try:
            with open(MODULE_PATTERNS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    
    return {
        "last_updated": None,
        "files": {},
        "patterns": INTELFORGE_PATTERNS,
        "compliance_summary": {
            "total_files": 0,
            "compliant_files": 0,
            "non_compliant_files": 0
        }
    }

def save_module_patterns(patterns):
    """Save module patterns to file"""
    patterns["last_updated"] = datetime.now().isoformat()
    
    with open(MODULE_PATTERNS_FILE, 'w') as f:
        json.dump(patterns, f, indent=2)

def analyze_file_content(file_path):
    """Analyze file content for pattern compliance"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse AST for structural analysis
        try:
            tree = ast.parse(content)
            has_functions = any(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))
            has_classes = any(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
            has_main_guard = '__name__ == "__main__"' in content
        except SyntaxError:
            has_functions = False
            has_classes = False
            has_main_guard = False
        
        return {
            "content": content,
            "has_functions": has_functions,
            "has_classes": has_classes,
            "has_main_guard": has_main_guard,
            "line_count": len(content.splitlines())
        }
    
    except (IOError, UnicodeDecodeError):
        return None

def check_pattern_compliance(file_path, content_info, patterns):
    """Check if file complies with IntelForge patterns"""
    if not content_info:
        return {"compliant": False, "errors": ["Could not read file"]}
    
    content = content_info["content"]
    file_name = Path(file_path).name
    rel_path = str(Path(file_path).relative_to(PROJECT_ROOT))
    
    compliance = {"compliant": True, "errors": [], "warnings": [], "suggestions": []}
    
    for pattern_name, pattern_config in patterns.items():
        required = pattern_config.get("required", False)
        required_for = pattern_config.get("required_for", [])
        
        # Check if this pattern is required for this file
        if required_for and not any(req in rel_path for req in required_for):
            continue
        
        # Check specific patterns
        if pattern_name == "phase_naming":
            if rel_path.startswith("phase_") and not re.match(pattern_config["pattern"], file_name):
                compliance["errors"].append(f"File name doesn't follow phase_XX_name.py pattern: {file_name}")
                compliance["compliant"] = False
        
        elif pattern_name == "docstring":
            if not re.search(pattern_config["pattern"], content):
                if required:
                    compliance["errors"].append("Missing module docstring")
                    compliance["compliant"] = False
                else:
                    compliance["warnings"].append("Missing module docstring")
        
        elif pattern_name == "main_function":
            if not content_info["has_main_guard"]:
                if required:
                    compliance["errors"].append("Missing if __name__ == '__main__': guard")
                    compliance["compliant"] = False
                else:
                    compliance["warnings"].append("Missing if __name__ == '__main__': guard")
        
        else:
            # Check for pattern presence
            pattern_found = False
            if isinstance(pattern_config.get("patterns"), list):
                for pattern in pattern_config["patterns"]:
                    if pattern in content:
                        pattern_found = True
                        break
            elif "pattern" in pattern_config:
                pattern_found = bool(re.search(pattern_config["pattern"], content))
            
            if not pattern_found:
                if required:
                    compliance["errors"].append(f"Missing {pattern_config['description']}")
                    compliance["compliant"] = False
                else:
                    compliance["warnings"].append(f"Missing {pattern_config['description']}")
    
    # Add suggestions based on file type
    if rel_path.startswith("scrapers/") or "phase_" in rel_path:
        if "BaseScraper" not in content:
            compliance["suggestions"].append("Consider inheriting from BaseScraper for consistency")
        if "config.yaml" not in content:
            compliance["suggestions"].append("Consider loading configuration from config.yaml")
    
    return compliance

def generate_compliance_report(patterns_data):
    """Generate human-readable compliance report"""
    report = []
    report.append("# Module Compliance Report")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Summary
    summary = patterns_data["compliance_summary"]
    report.append("## Summary")
    report.append(f"- **Total files analyzed:** {summary['total_files']}")
    report.append(f"- **Compliant files:** {summary['compliant_files']}")
    report.append(f"- **Non-compliant files:** {summary['non_compliant_files']}")
    if summary['total_files'] > 0:
        compliance_rate = (summary['compliant_files'] / summary['total_files']) * 100
        report.append(f"- **Compliance rate:** {compliance_rate:.1f}%")
    report.append("")
    
    # Pattern definitions
    report.append("## IntelForge Patterns")
    for pattern_name, pattern_config in patterns_data["patterns"].items():
        report.append(f"### {pattern_name}")
        report.append(f"- **Description:** {pattern_config['description']}")
        report.append(f"- **Required:** {'Yes' if pattern_config.get('required', False) else 'No'}")
        if pattern_config.get("required_for"):
            report.append(f"- **Required for:** {', '.join(pattern_config['required_for'])}")
        report.append("")
    
    # File-by-file analysis
    report.append("## File Analysis")
    for file_path, file_info in sorted(patterns_data["files"].items()):
        compliance = file_info.get("compliance", {})
        report.append(f"### {file_path}")
        report.append(f"- **Status:** {'✅ Compliant' if compliance.get('compliant', False) else '❌ Non-compliant'}")
        report.append(f"- **Last checked:** {file_info.get('last_analyzed', 'Never')}")
        
        if compliance.get("errors"):
            report.append("- **Errors:**")
            for error in compliance["errors"]:
                report.append(f"  - {error}")
        
        if compliance.get("warnings"):
            report.append("- **Warnings:**")
            for warning in compliance["warnings"]:
                report.append(f"  - {warning}")
        
        if compliance.get("suggestions"):
            report.append("- **Suggestions:**")
            for suggestion in compliance["suggestions"]:
                report.append(f"  - {suggestion}")
        
        report.append("")
    
    # Write report
    with open(COMPLIANCE_REPORT_FILE, 'w') as f:
        f.write('\n'.join(report))

def main():
    """Main hook execution"""
    if len(sys.argv) < 2:
        print("Usage: module_structure_guardian.py <file_paths>")
        sys.exit(1)
    
    file_paths = sys.argv[1].split()
    
    ensure_directories()
    
    # Load existing patterns
    patterns_data = load_module_patterns()
    
    # Process each file
    for file_path in file_paths:
        if not file_path.endswith('.py'):
            continue
        
        # Convert to relative path for consistency
        try:
            rel_path = str(Path(file_path).relative_to(PROJECT_ROOT))
        except ValueError:
            rel_path = file_path
        
        # Analyze file
        content_info = analyze_file_content(file_path)
        compliance = check_pattern_compliance(file_path, content_info, INTELFORGE_PATTERNS)
        
        # Update patterns data
        patterns_data["files"][rel_path] = {
            "last_analyzed": datetime.now().isoformat(),
            "compliance": compliance,
            "file_info": {
                "line_count": content_info.get("line_count", 0) if content_info else 0,
                "has_functions": content_info.get("has_functions", False) if content_info else False,
                "has_classes": content_info.get("has_classes", False) if content_info else False
            }
        }
        
        # Print immediate feedback
        if compliance["compliant"]:
            print(f"✅ {rel_path} - Compliant with IntelForge patterns")
        else:
            print(f"❌ {rel_path} - Non-compliant ({len(compliance['errors'])} errors)")
            for error in compliance["errors"]:
                print(f"  - {error}")
    
    # Update summary
    total_files = len(patterns_data["files"])
    compliant_files = sum(1 for info in patterns_data["files"].values() 
                         if info.get("compliance", {}).get("compliant", False))
    
    patterns_data["compliance_summary"] = {
        "total_files": total_files,
        "compliant_files": compliant_files,
        "non_compliant_files": total_files - compliant_files
    }
    
    # Save patterns
    save_module_patterns(patterns_data)
    
    # Generate report
    generate_compliance_report(patterns_data)
    
    print(f"✓ Module structure validation completed for {len(file_paths)} files")

if __name__ == "__main__":
    main()