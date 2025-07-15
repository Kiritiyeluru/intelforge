#!/usr/bin/env python3
"""
Config Change Propagator Hook for IntelForge
Automatically propagates config.yaml changes to related files and maintains consistency
"""

import json
import sys
import yaml
from pathlib import Path
from datetime import datetime

# Configure paths
HOOKS_DIR = Path(__file__).parent
PROJECT_ROOT = HOOKS_DIR.parent.parent
CLAUDE_DIR = PROJECT_ROOT / ".claude"
CONFIG_HISTORY_FILE = CLAUDE_DIR / "config_history.json"
CONFIG_FILE = PROJECT_ROOT / "config" / "config.yaml"
ENV_EXAMPLE_FILE = PROJECT_ROOT / ".env.example"
DOCS_DIR = PROJECT_ROOT / "docs"
CONFIG_CHANGELOG_FILE = DOCS_DIR / "config_changelog.md"


def ensure_directories():
    """Create necessary directories if they don't exist"""
    CLAUDE_DIR.mkdir(exist_ok=True)
    DOCS_DIR.mkdir(exist_ok=True)


def load_config_history():
    """Load existing config history or create new structure"""
    if CONFIG_HISTORY_FILE.exists():
        try:
            with open(CONFIG_HISTORY_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    return {
        "last_updated": None,
        "changes": [],
        "current_config": {},
        "api_keys": [],
        "dependencies": [],
    }


def save_config_history(history):
    """Save config history to file"""
    history["last_updated"] = datetime.now().isoformat()

    with open(CONFIG_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def load_yaml_config(file_path):
    """Load YAML config file"""
    try:
        with open(file_path, "r") as f:
            return yaml.safe_load(f)
    except (yaml.YAMLError, IOError):
        return {}


def extract_api_keys(config):
    """Extract API key configurations from config"""
    api_keys = []

    def find_keys(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                if (
                    "api_key" in key.lower()
                    or "token" in key.lower()
                    or "secret" in key.lower()
                ):
                    api_keys.append(
                        {
                            "path": current_path,
                            "key": key,
                            "description": f"API key for {key.replace('_', ' ').title()}",
                        }
                    )
                elif isinstance(value, dict):
                    find_keys(value, current_path)

    find_keys(config)
    return api_keys


def extract_dependencies(config):
    """Extract implied dependencies from config"""
    dependencies = []

    # Check for API configurations that imply dependencies
    if "reddit" in str(config).lower():
        dependencies.append("praw")
    if "github" in str(config).lower():
        dependencies.append("PyGithub")
    if "openai" in str(config).lower():
        dependencies.append("openai")
    if "anthropic" in str(config).lower():
        dependencies.append("anthropic")
    if "selenium" in str(config).lower():
        dependencies.append("selenium")
    if "playwright" in str(config).lower():
        dependencies.append("playwright")
    if "scrapy" in str(config).lower():
        dependencies.append("scrapy")

    return list(set(dependencies))


def update_env_example(api_keys):
    """Update .env.example file with new API keys"""
    if not api_keys:
        return

    env_content = []
    env_content.append("# IntelForge Environment Variables")
    env_content.append("# Copy this file to .env and fill in your actual values")
    env_content.append(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    env_content.append("")

    for api_key in api_keys:
        env_var_name = api_key["key"].upper()
        env_content.append(f"# {api_key['description']}")
        env_content.append(f"{env_var_name}=your_{api_key['key']}_here")
        env_content.append("")

    with open(ENV_EXAMPLE_FILE, "w") as f:
        f.write("\n".join(env_content))


def detect_config_changes(old_config, new_config):
    """Detect changes between old and new config"""
    changes = []

    def compare_dicts(old, new, path=""):
        if isinstance(old, dict) and isinstance(new, dict):
            # Check for added keys
            for key in new:
                current_path = f"{path}.{key}" if path else key
                if key not in old:
                    changes.append(
                        {"type": "added", "path": current_path, "value": new[key]}
                    )
                else:
                    compare_dicts(old[key], new[key], current_path)

            # Check for removed keys
            for key in old:
                current_path = f"{path}.{key}" if path else key
                if key not in new:
                    changes.append(
                        {"type": "removed", "path": current_path, "value": old[key]}
                    )

        elif old != new:
            changes.append(
                {"type": "modified", "path": path, "old_value": old, "new_value": new}
            )

    compare_dicts(old_config, new_config)
    return changes


def update_config_changelog(changes):
    """Update config changelog with recent changes"""
    if not changes:
        return

    # Load existing changelog
    changelog_entries = []
    if CONFIG_CHANGELOG_FILE.exists():
        with open(CONFIG_CHANGELOG_FILE, "r") as f:
            changelog_entries = f.read().split("\n")

    # Add new entry
    new_entry = []
    new_entry.append(f"## {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    new_entry.append("")

    for change in changes:
        if change["type"] == "added":
            new_entry.append(f"- **Added:** `{change['path']}` = `{change['value']}`")
        elif change["type"] == "removed":
            new_entry.append(
                f"- **Removed:** `{change['path']}` (was `{change['value']}`)"
            )
        elif change["type"] == "modified":
            new_entry.append(
                f"- **Modified:** `{change['path']}` from `{change['old_value']}` to `{change['new_value']}`"
            )

    new_entry.append("")

    # Write updated changelog
    with open(CONFIG_CHANGELOG_FILE, "w") as f:
        if not changelog_entries or not any(line.strip() for line in changelog_entries):
            f.write("# Config Change Log\n\n")
        f.write("\n".join(new_entry))
        if changelog_entries:
            f.write("\n".join(changelog_entries))


def validate_config_syntax(config_path):
    """Validate YAML syntax and suggest fixes"""
    try:
        with open(config_path, "r") as f:
            yaml.safe_load(f)
        return True, []
    except yaml.YAMLError as e:
        suggestions = []
        error_str = str(e)

        if "mapping values are not allowed here" in error_str:
            suggestions.append("Check for incorrect indentation in YAML structure")
        if "found character" in error_str:
            suggestions.append("Check for special characters that need to be quoted")
        if "could not find expected" in error_str:
            suggestions.append("Check for missing quotes around string values")

        return False, suggestions


def check_scraper_targets(config):
    """Check for new scraper targets and suggest documentation updates"""
    targets = []

    # Reddit targets
    if "reddit" in config and "subreddits" in config["reddit"]:
        for sub in config["reddit"]["subreddits"]:
            targets.append(f"Reddit: r/{sub}")

    # GitHub targets
    if "github" in config and "repositories" in config["github"]:
        for repo in config["github"]["repositories"]:
            targets.append(f"GitHub: {repo}")

    # Web scraping targets
    if "web_scraping" in config and "targets" in config["web_scraping"]:
        for target in config["web_scraping"]["targets"]:
            targets.append(f"Web: {target}")

    return targets


def main():
    """Main hook execution"""
    if len(sys.argv) < 2:
        print("Usage: config_change_propagator.py <file_paths>")
        sys.exit(1)

    file_paths = sys.argv[1].split()

    # Only process if config.yaml was modified
    config_modified = any("config.yaml" in path for path in file_paths)
    if not config_modified:
        return

    ensure_directories()

    # Load config history
    history = load_config_history()

    # Load current config
    current_config = load_yaml_config(CONFIG_FILE)

    # Detect changes
    changes = detect_config_changes(history.get("current_config", {}), current_config)

    if changes:
        # Update history
        history["changes"].append(
            {"timestamp": datetime.now().isoformat(), "changes": changes}
        )

        # Keep only last 50 changes to avoid file bloat
        if len(history["changes"]) > 50:
            history["changes"] = history["changes"][-50:]

        history["current_config"] = current_config

        # Extract API keys and dependencies
        api_keys = extract_api_keys(current_config)
        dependencies = extract_dependencies(current_config)

        history["api_keys"] = api_keys
        history["dependencies"] = dependencies

        # Update related files
        update_env_example(api_keys)
        update_config_changelog(changes)

        # Save history
        save_config_history(history)

        # Validate syntax
        valid, suggestions = validate_config_syntax(CONFIG_FILE)

        # Check for new targets
        targets = check_scraper_targets(current_config)

        print(f"✓ Config changes propagated ({len(changes)} changes)")

        if not valid:
            print("⚠ Config syntax issues detected:")
            for suggestion in suggestions:
                print(f"  - {suggestion}")

        if api_keys:
            print(f"✓ Updated .env.example with {len(api_keys)} API key templates")

        if dependencies:
            print(
                f"✓ Detected {len(dependencies)} implied dependencies: {', '.join(dependencies)}"
            )

        if targets:
            print(f"✓ Found {len(targets)} scraping targets")

    else:
        print("No significant config changes detected")


if __name__ == "__main__":
    main()
