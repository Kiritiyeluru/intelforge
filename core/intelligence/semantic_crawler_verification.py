#!/usr/bin/env python3
"""
Semantic Crawler Implementation Gap Analysis Script
Checks implementation status of 6 semantic crawler improvement modules.
"""

import json
from pathlib import Path
from typing import Dict, Set

# 6 Semantic Crawler Modules and their recommended tools
SEMANTIC_MODULES = {
    "adaptive_relevance_thresholding": {
        "primary": "muzlin",
        "alternatives": [
            "pythresh",
            "cleanlab",
            "hdbscan",
            "scikit-learn",
            "bertopic",
            "semantic-text-splitter",
        ],
        "description": "Automated threshold adjustment for content filtering",
    },
    "cross_document_semantic_graph": {
        "primary": "txtai",
        "alternatives": [
            "knowledge-graph-maker",
            "graphiti",
            "pygraft",
            "haystack",
            "graphbrain",
            "pykg2vec",
            "snfpy",
        ],
        "description": "Build semantic relationships between documents",
    },
    "research_gap_detection": {
        "primary": "bertopic",
        "alternatives": ["top2vec", "cleanlab", "scikit-learn"],
        "description": "Detect novel content and research gaps",
    },
    "content_evolution_tracking": {
        "primary": "deepdiff+sentence-transformers",
        "alternatives": [
            "semantic-text-splitter",
            "difflib",
            "transformers",
            "lingua-py",
            "lakefs",
            "dvc",
        ],
        "description": "Track semantic changes in content over time",
    },
    "source_credibility_scoring": {
        "primary": "openpagerank+python-whois",
        "alternatives": [
            "domain-reputation-py",
            "ipwhois",
            "domaintools-misp",
            "virustotal-ip-rep",
            "mediarank",
        ],
        "description": "Score source authority and credibility",
    },
    "predictive_content_value": {
        "primary": "lightfm+fasttext+sentence-transformers",
        "alternatives": [
            "surprise",
            "rankify",
            "langchain",
            "ragflow",
            "txtai",
            "scikit-learn",
        ],
        "description": "Predict content value and relevance",
    },
}

# Normalize tool names for matching
TOOL_NORMALIZATIONS = {
    "sentence_transformers": "sentence-transformers",
    "scikit_learn": "scikit-learn",
    "python_whois": "python-whois",
    "ta_lib": "ta-lib",
    "deepdiff": "deepdiff",
    "fasttext": "fasttext",
    "lightfm": "lightfm",
}


def check_python_environments(env_file: Path) -> Dict[str, Set[str]]:
    """Check what semantic crawler tools are installed in Python environments"""
    installed_tools = set()

    try:
        with open(env_file, "r") as f:
            env_data = json.load(f)

        # Extract from all environments
        python_envs = env_data.get("python_environments", {})
        for env_name, env_info in python_envs.items():
            if isinstance(env_info, dict) and "installed_packages" in env_info:
                packages = env_info["installed_packages"]

                def extract_packages(obj):
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            # Tool names as keys
                            if isinstance(value, (str, dict)):
                                installed_tools.add(key.lower())
                            # Recurse into nested objects
                            if isinstance(value, dict):
                                extract_packages(value)
                    elif isinstance(obj, list):
                        for item in obj:
                            extract_packages(item)

                extract_packages(packages)

    except Exception as e:
        print(f"Error reading {env_file}: {e}")

    return {"python_environments": installed_tools}


def check_semantic_crawler_directory(semantic_dir: Path) -> Dict[str, Set[str]]:
    """Check semantic_crawler directory for implemented modules"""
    implemented_features = set()

    if not semantic_dir.exists():
        return {"semantic_crawler_dir": set()}

    # Check for Python files that might implement the modules
    python_files = list(semantic_dir.rglob("*.py"))
    markdown_files = list(semantic_dir.rglob("*.md"))

    # Keywords to look for in files
    feature_keywords = {
        "adaptive_relevance_thresholding": [
            "threshold",
            "relevance",
            "adaptive",
            "outlier",
            "anomaly",
        ],
        "cross_document_semantic_graph": [
            "graph",
            "semantic",
            "relationship",
            "network",
            "knowledge",
        ],
        "research_gap_detection": ["gap", "novelty", "topic", "detection", "research"],
        "content_evolution_tracking": [
            "evolution",
            "tracking",
            "version",
            "diff",
            "change",
        ],
        "source_credibility_scoring": [
            "credibility",
            "authority",
            "pagerank",
            "reputation",
            "trust",
        ],
        "predictive_content_value": [
            "value",
            "prediction",
            "scoring",
            "recommendation",
            "quality",
        ],
    }

    for file_path in python_files + markdown_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().lower()

            for module, keywords in feature_keywords.items():
                if any(keyword in content for keyword in keywords):
                    implemented_features.add(module)

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    return {"semantic_crawler_dir": implemented_features}


def check_scripts_directory(scripts_dir: Path) -> Dict[str, Set[str]]:
    """Check scripts directory for semantic analysis modules"""
    script_tools = set()

    if not scripts_dir.exists():
        return {"scripts_dir": set()}

    python_files = list(scripts_dir.glob("*.py"))

    # Look for imports and usage of semantic tools
    semantic_imports = [
        "sentence_transformers",
        "transformers",
        "torch",
        "faiss",
        "bertopic",
        "deepdiff",
        "whois",
        "lightfm",
        "fasttext",
        "sklearn",
        "txtai",
    ]

    for file_path in python_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().lower()

            for tool in semantic_imports:
                if f"import {tool}" in content or f"from {tool}" in content:
                    script_tools.add(tool)

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    return {"scripts_dir": script_tools}


def analyze_module_implementation(
    all_found_tools: Set[str], all_features: Set[str]
) -> Dict[str, Dict]:
    """Analyze implementation status of each semantic module"""
    results = {}

    for module_name, module_info in SEMANTIC_MODULES.items():
        primary_tool = module_info["primary"]
        alternatives = module_info["alternatives"]
        all_tools = [primary_tool] + alternatives

        # Check which tools are available
        available_tools = []
        for tool in all_tools:
            # Normalize tool names for comparison
            normalized_tool = TOOL_NORMALIZATIONS.get(tool, tool)
            if any(
                normalized_tool.lower() in found_tool.lower()
                or found_tool.lower() in normalized_tool.lower()
                or tool.lower() in found_tool.lower()
                for found_tool in all_found_tools
            ):
                available_tools.append(tool)

        # Check if module features are implemented
        feature_implemented = module_name in all_features

        # Determine implementation status
        if primary_tool.lower() in [t.lower() for t in available_tools]:
            if feature_implemented:
                status = "✅ IMPLEMENTED"
            else:
                status = "🟡 PARTIALLY IMPLEMENTED"
        elif available_tools:
            if feature_implemented:
                status = "🟡 PARTIALLY IMPLEMENTED"
            else:
                status = "🟡 TOOLS AVAILABLE"
        else:
            status = "❌ NOT IMPLEMENTED"

        results[module_name] = {
            "status": status,
            "primary_tool": primary_tool,
            "available_tools": available_tools,
            "missing_tools": [t for t in all_tools if t not in available_tools],
            "feature_implemented": feature_implemented,
            "description": module_info["description"],
        }

    return results


def generate_semantic_crawler_report(
    analysis_results: Dict[str, Dict], all_found_tools: Set[str]
) -> str:
    """Generate comprehensive semantic crawler implementation report"""
    report = []
    report.append("=" * 80)
    report.append("SEMANTIC CRAWLER IMPLEMENTATION GAP ANALYSIS")
    report.append("=" * 80)
    report.append("")

    # Summary
    implemented = sum(
        1 for r in analysis_results.values() if "IMPLEMENTED" in r["status"]
    )
    partially_implemented = sum(
        1 for r in analysis_results.values() if "PARTIALLY" in r["status"]
    )
    not_implemented = sum(
        1 for r in analysis_results.values() if "NOT IMPLEMENTED" in r["status"]
    )

    report.append("📊 IMPLEMENTATION SUMMARY")
    report.append(f"   ✅ Fully Implemented: {implemented}/6 modules")
    report.append(f"   🟡 Partially Implemented: {partially_implemented}/6 modules")
    report.append(f"   ❌ Not Implemented: {not_implemented}/6 modules")
    report.append("")

    # Detailed analysis for each module
    for module_name, result in analysis_results.items():
        report.append(f"🔍 {module_name.upper().replace('_', ' ')}")
        report.append(f"   Status: {result['status']}")
        report.append(f"   Description: {result['description']}")
        report.append(f"   Primary Tool: {result['primary_tool']}")

        if result["available_tools"]:
            report.append(
                f"   ✅ Available Tools: {', '.join(result['available_tools'])}"
            )

        if result["missing_tools"]:
            report.append(f"   ❌ Missing Tools: {', '.join(result['missing_tools'])}")

        report.append(
            f"   Feature Implementation: {'Yes' if result['feature_implemented'] else 'No'}"
        )
        report.append("")

    # Recommendations
    report.append("🎯 IMPLEMENTATION RECOMMENDATIONS")
    report.append("")

    priority_order = [
        "adaptive_relevance_thresholding",
        "cross_document_semantic_graph",
        "research_gap_detection",
        "content_evolution_tracking",
        "source_credibility_scoring",
        "predictive_content_value",
    ]

    for i, module_name in enumerate(priority_order, 1):
        result = analysis_results[module_name]
        if "NOT IMPLEMENTED" in result["status"]:
            report.append(f"   {i}. Install {result['primary_tool']} for {module_name}")
        elif "PARTIALLY" in result["status"]:
            if not result["feature_implemented"]:
                report.append(
                    f"   {i}. Implement {module_name} using available {result['available_tools'][0]}"
                )
            else:
                report.append(
                    f"   {i}. Consider upgrading to {result['primary_tool']} for {module_name}"
                )

    report.append("")

    # Next steps
    report.append("📋 NEXT STEPS")
    report.append("   1. Install missing primary tools using: pip install <tool>")
    report.append("   2. Implement module features in semantic_crawler/scripts/")
    report.append("   3. Create integration tests for each module")
    report.append("   4. Update documentation with implementation details")

    return "\n".join(report)


def main():
    """Main semantic crawler verification process"""
    project_root = Path("/home/kiriti/alpha_projects/intelforge")

    print("🔍 Analyzing Semantic Crawler Implementation Status...")

    # Check different sources
    python_env_file = project_root / ".claude" / "python_environments.json"
    semantic_dir = project_root / "semantic_crawler"
    scripts_dir = project_root / "scripts"

    all_found_tools = set()
    all_features = set()

    # Check Python environments
    if python_env_file.exists():
        print("   📦 Checking Python environments...")
        env_results = check_python_environments(python_env_file)
        all_found_tools.update(env_results["python_environments"])

    # Check semantic_crawler directory
    print("   📁 Checking semantic_crawler directory...")
    semantic_results = check_semantic_crawler_directory(semantic_dir)
    all_features.update(semantic_results["semantic_crawler_dir"])

    # Check scripts directory
    print("   📜 Checking scripts directory...")
    script_results = check_scripts_directory(scripts_dir)
    all_found_tools.update(script_results["scripts_dir"])

    print(f"   Found {len(all_found_tools)} potential tools")
    print(f"   Found {len(all_features)} implemented features")

    # Analyze implementation status
    print("📊 Analyzing module implementation status...")
    analysis_results = analyze_module_implementation(all_found_tools, all_features)

    # Generate report
    report = generate_semantic_crawler_report(analysis_results, all_found_tools)

    # Save report
    report_file = project_root / "semantic_crawler_implementation_report.txt"
    with open(report_file, "w") as f:
        f.write(report)

    print(f"\n📄 Report saved to: {report_file}")
    print("\n" + report)

    # Return success status
    implemented_count = sum(
        1 for r in analysis_results.values() if "IMPLEMENTED" in r["status"]
    )
    return implemented_count >= 3  # Consider success if at least half are implemented


if __name__ == "__main__":
    main()
