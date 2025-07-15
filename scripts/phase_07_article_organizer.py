#!/usr/bin/env python3
"""
Phase 07: Article Auto-Organizer
Automatically categorizes and moves articles from intake folder to organized structure.
"""

import shutil
import yaml
from datetime import datetime
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent
INTAKE_DIR = PROJECT_ROOT / "knowledge_management/intake"
ARTICLES_DIR = PROJECT_ROOT / "knowledge_management/articles"
CONFIG_FILE = PROJECT_ROOT / "knowledge_management/config/categories.yaml"
LOG_FILE = PROJECT_ROOT / "knowledge_management/logs/organizer.log"


def load_categories():
    """Load categorization rules from config file."""
    try:
        with open(CONFIG_FILE, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Config file not found: {CONFIG_FILE}")
        return None


def log_action(message):
    """Log organizer actions with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"

    # Ensure log directory exists
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(LOG_FILE, "a") as f:
        f.write(log_entry)
    print(log_entry.strip())


def analyze_content(file_path):
    """Analyze article title and content for categorization."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        title = Path(file_path).stem.lower()
        content_lower = content.lower()

        return title, content_lower
    except Exception as e:
        log_action(f"Error reading {file_path}: {e}")
        return "", ""


def categorize_article(title, content, categories_config):
    """Determine category based on title and content analysis."""
    if not categories_config:
        return "archived"

    # Apply rules from config
    for rule in categories_config.get("rules", []):
        if "if_title_contains" in rule:
            for keyword in rule["if_title_contains"]:
                if keyword.lower() in title:
                    return rule["assign_to"]

        if "if_content_contains" in rule:
            for keyword in rule["if_content_contains"]:
                if keyword.lower() in content:
                    return rule["assign_to"]

    # Fallback: check category keywords
    for category, config in categories_config.get("categories", {}).items():
        for keyword in config.get("keywords", []):
            if keyword.lower() in title or keyword.lower() in content:
                return category

    # Default category
    return "archived"


def move_article(source_path, category):
    """Move article to appropriate category folder."""
    target_dir = ARTICLES_DIR / category
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / Path(source_path).name

    # Handle filename conflicts
    counter = 1
    while target_path.exists():
        stem = Path(source_path).stem
        suffix = Path(source_path).suffix
        target_path = target_dir / f"{stem}_{counter}{suffix}"
        counter += 1

    shutil.move(source_path, target_path)
    return target_path


def process_intake_folder(dry_run=False):
    """Process all articles in intake folder."""
    if not INTAKE_DIR.exists():
        log_action(f"Intake directory does not exist: {INTAKE_DIR}")
        return

    categories_config = load_categories()
    if not categories_config:
        log_action("Failed to load categories config")
        return

    md_files = list(INTAKE_DIR.glob("*.md"))
    if not md_files:
        log_action("No markdown files found in intake folder")
        return

    log_action(f"Processing {len(md_files)} articles (dry_run={dry_run})")

    for file_path in md_files:
        title, content = analyze_content(file_path)
        category = categorize_article(title, content, categories_config)

        if dry_run:
            log_action(f"[DRY RUN] Would move '{file_path.name}' to '{category}'")
        else:
            try:
                target_path = move_article(file_path, category)
                log_action(f"Moved '{file_path.name}' to '{category}' -> {target_path}")
            except Exception as e:
                log_action(f"Error moving '{file_path.name}': {e}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Auto-organize articles from intake folder"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--watch", action="store_true", help="Watch intake folder for new files"
    )

    args = parser.parse_args()

    if args.watch:
        log_action("Starting file watcher mode (Ctrl+C to stop)")
        try:
            import time

            while True:
                process_intake_folder(dry_run=args.dry_run)
                time.sleep(10)  # Check every 10 seconds
        except KeyboardInterrupt:
            log_action("File watcher stopped")
    else:
        process_intake_folder(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
