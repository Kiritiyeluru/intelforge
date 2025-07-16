#!/usr/bin/env python3
"""
Dependency Intelligence Hook for IntelForge
Automatically tracks and manages Python imports and dependencies
"""

import ast
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Configure paths
HOOKS_DIR = Path(__file__).parent
PROJECT_ROOT = HOOKS_DIR.parent.parent
CLAUDE_DIR = PROJECT_ROOT / ".claude"
DEPENDENCIES_FILE = CLAUDE_DIR / "dependencies.json"
REQUIREMENTS_AUTO_FILE = PROJECT_ROOT / "requirements_auto.txt"
DOCS_DIR = PROJECT_ROOT / "docs"
DEPENDENCY_REPORT_FILE = DOCS_DIR / "dependency_report.md"

# Known standard library modules (Python 3.8+)
STDLIB_MODULES = {
    "os",
    "sys",
    "json",
    "datetime",
    "pathlib",
    "collections",
    "itertools",
    "functools",
    "operator",
    "re",
    "math",
    "random",
    "time",
    "logging",
    "argparse",
    "configparser",
    "sqlite3",
    "urllib",
    "http",
    "email",
    "xml",
    "html",
    "csv",
    "pickle",
    "gzip",
    "zipfile",
    "tarfile",
    "shutil",
    "subprocess",
    "threading",
    "multiprocessing",
    "queue",
    "socket",
    "ssl",
    "hashlib",
    "hmac",
    "secrets",
    "base64",
    "binascii",
    "struct",
    "codecs",
    "locale",
    "calendar",
    "uuid",
    "enum",
    "dataclasses",
    "typing",
    "copy",
    "pprint",
    "warnings",
    "traceback",
    "inspect",
    "gc",
    "weakref",
    "types",
    "abc",
    "contextlib",
    "importlib",
}

# Known third-party packages and their PyPI names
KNOWN_PACKAGES = {
    "requests": "requests",
    "praw": "praw",
    "github": "PyGithub",
    "playwright": "playwright",
    "scrapy": "scrapy",
    "selectolax": "selectolax",
    "httpx": "httpx",
    "pandas": "pandas",
    "numpy": "numpy",
    "matplotlib": "matplotlib",
    "seaborn": "seaborn",
    "openai": "openai",
    "anthropic": "anthropic",
    "sklearn": "scikit-learn",
    "cv2": "opencv-python",
    "PIL": "Pillow",
    "yaml": "PyYAML",
    "toml": "toml",
    "click": "click",
    "typer": "typer",
    "rich": "rich",
    "tqdm": "tqdm",
    "schedule": "schedule",
    "feedparser": "feedparser",
    "beautifulsoup4": "beautifulsoup4",
    "bs4": "beautifulsoup4",
    "lxml": "lxml",
    "selenium": "selenium",
    "fake_useragent": "fake-useragent",
    "user_agent": "fake-useragent",
    "sentence_transformers": "sentence-transformers",
    "transformers": "transformers",
    "torch": "torch",
    "tensorflow": "tensorflow",
    "faiss": "faiss-cpu",
    "chromadb": "chromadb",
    "pymongo": "pymongo",
    "redis": "redis",
    "sqlalchemy": "sqlalchemy",
    "psycopg2": "psycopg2-binary",
    "mysql": "mysql-connector-python",
    "flask": "flask",
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "gunicorn": "gunicorn",
    "celery": "celery",
    "pytest": "pytest",
    "black": "black",
    "flake8": "flake8",
    "mypy": "mypy",
    "isort": "isort",
}


def ensure_directories():
    """Create necessary directories if they don't exist"""
    CLAUDE_DIR.mkdir(exist_ok=True)
    DOCS_DIR.mkdir(exist_ok=True)


def load_dependencies():
    """Load existing dependencies or create new structure"""
    if DEPENDENCIES_FILE.exists():
        try:
            with open(DEPENDENCIES_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    return {
        "last_updated": None,
        "files": {},
        "imports": {},
        "packages": {},
        "warnings": [],
    }


def save_dependencies(deps):
    """Save dependencies to file"""
    deps["last_updated"] = datetime.now().isoformat()

    with open(DEPENDENCIES_FILE, "w") as f:
        json.dump(deps, f, indent=2)


def extract_imports_from_file(file_path):
    """Extract all imports from a Python file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse the AST
        tree = ast.parse(content)

        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        {
                            "type": "import",
                            "module": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno,
                        }
                    )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(
                        {
                            "type": "from",
                            "module": module,
                            "name": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno,
                        }
                    )

        return imports

    except (SyntaxError, UnicodeDecodeError, IOError):
        return []


def get_top_level_package(module_name):
    """Get the top-level package name from a module"""
    if not module_name:
        return None
    return module_name.split(".")[0]


def classify_import(module_name):
    """Classify an import as stdlib, third-party, or local"""
    if not module_name:
        return "unknown"

    top_level = get_top_level_package(module_name)

    if top_level in STDLIB_MODULES:
        return "stdlib"
    elif top_level in KNOWN_PACKAGES:
        return "third-party"
    elif module_name.startswith(".") or top_level in ["scrapers", "scripts", "config"]:
        return "local"
    else:
        return "unknown"


def generate_requirements_auto(deps):
    """Generate automatic requirements.txt from dependencies"""
    third_party_packages = set()

    for file_path, file_info in deps["files"].items():
        for imp in file_info["imports"]:
            if imp["classification"] == "third-party":
                top_level = get_top_level_package(imp["module"])
                if top_level in KNOWN_PACKAGES:
                    third_party_packages.add(KNOWN_PACKAGES[top_level])

    # Write requirements file
    with open(REQUIREMENTS_AUTO_FILE, "w") as f:
        f.write("# Auto-generated requirements from dependency intelligence hook\n")
        f.write(f"# Generated at: {datetime.now().isoformat()}\n\n")

        for package in sorted(third_party_packages):
            f.write(f"{package}\n")


def generate_dependency_report(deps):
    """Generate human-readable dependency report"""
    report = []
    report.append("# Dependency Report")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")

    # Summary statistics
    total_files = len(deps["files"])
    total_imports = sum(len(info["imports"]) for info in deps["files"].values())

    stdlib_count = sum(
        1
        for info in deps["files"].values()
        for imp in info["imports"]
        if imp["classification"] == "stdlib"
    )
    third_party_count = sum(
        1
        for info in deps["files"].values()
        for imp in info["imports"]
        if imp["classification"] == "third-party"
    )
    local_count = sum(
        1
        for info in deps["files"].values()
        for imp in info["imports"]
        if imp["classification"] == "local"
    )

    report.append("## Summary")
    report.append(f"- **Total Python files analyzed:** {total_files}")
    report.append(f"- **Total imports:** {total_imports}")
    report.append(f"- **Standard library:** {stdlib_count}")
    report.append(f"- **Third-party packages:** {third_party_count}")
    report.append(f"- **Local imports:** {local_count}")
    report.append("")

    # Third-party packages
    if third_party_count > 0:
        report.append("## Third-Party Packages")
        packages = defaultdict(list)
        for file_path, info in deps["files"].items():
            for imp in info["imports"]:
                if imp["classification"] == "third-party":
                    top_level = get_top_level_package(imp["module"])
                    packages[top_level].append(file_path)

        for package in sorted(packages.keys()):
            pypi_name = KNOWN_PACKAGES.get(package, package)
            files = list(set(packages[package]))
            report.append(f"- **{package}** (`{pypi_name}`)")
            report.append(f"  - Used in {len(files)} files: {', '.join(files)}")
        report.append("")

    # Warnings
    if deps["warnings"]:
        report.append("## Warnings")
        for warning in deps["warnings"]:
            report.append(f"- {warning}")
        report.append("")

    # File-by-file breakdown
    report.append("## File Analysis")
    for file_path, info in sorted(deps["files"].items()):
        report.append(f"### {file_path}")
        report.append(f"- **Last analyzed:** {info['last_analyzed']}")
        report.append(f"- **Import count:** {len(info['imports'])}")

        if info["imports"]:
            stdlib_imports = [
                imp for imp in info["imports"] if imp["classification"] == "stdlib"
            ]
            third_party_imports = [
                imp for imp in info["imports"] if imp["classification"] == "third-party"
            ]
            local_imports = [
                imp for imp in info["imports"] if imp["classification"] == "local"
            ]

            if stdlib_imports:
                report.append(
                    f"- **Standard library:** {', '.join(imp['module'] for imp in stdlib_imports)}"
                )
            if third_party_imports:
                report.append(
                    f"- **Third-party:** {', '.join(imp['module'] for imp in third_party_imports)}"
                )
            if local_imports:
                report.append(
                    f"- **Local:** {', '.join(imp['module'] for imp in local_imports)}"
                )

        report.append("")

    # Write report
    with open(DEPENDENCY_REPORT_FILE, "w") as f:
        f.write("\n".join(report))


def main():
    """Main hook execution"""
    if len(sys.argv) < 2:
        print("Usage: dependency_intelligence.py <file_paths>")
        sys.exit(1)

    file_paths = sys.argv[1].split()

    ensure_directories()

    # Load existing dependencies
    deps = load_dependencies()

    # Process each file
    for file_path in file_paths:
        if not file_path.endswith(".py"):
            continue

        # Convert to relative path for consistency
        try:
            rel_path = str(Path(file_path).relative_to(PROJECT_ROOT))
        except ValueError:
            rel_path = file_path

        # Extract imports
        imports = extract_imports_from_file(file_path)

        # Classify imports
        classified_imports = []
        for imp in imports:
            classification = classify_import(imp["module"])
            imp["classification"] = classification
            classified_imports.append(imp)

        # Update dependencies
        deps["files"][rel_path] = {
            "last_analyzed": datetime.now().isoformat(),
            "imports": classified_imports,
        }

    # Generate warnings for unknown packages
    deps["warnings"] = []
    for file_path, info in deps["files"].items():
        for imp in info["imports"]:
            if imp["classification"] == "unknown":
                top_level = get_top_level_package(imp["module"])
                if top_level and top_level not in STDLIB_MODULES:
                    warning = (
                        f"Unknown package '{top_level}' in {file_path}:{imp['line']}"
                    )
                    if warning not in deps["warnings"]:
                        deps["warnings"].append(warning)

    # Save dependencies
    save_dependencies(deps)

    # Generate requirements file
    generate_requirements_auto(deps)

    # Generate report
    generate_dependency_report(deps)

    print(f"✓ Dependency intelligence updated for {len(file_paths)} files")
    if deps["warnings"]:
        print(f"⚠ {len(deps['warnings'])} warnings generated")


if __name__ == "__main__":
    main()
