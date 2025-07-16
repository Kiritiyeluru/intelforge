#!/usr/bin/env python3
"""
Scraping Session Logger Hook for IntelForge
Automatically tracks all scraping activities and performance metrics
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Configure paths
HOOKS_DIR = Path(__file__).parent
PROJECT_ROOT = HOOKS_DIR.parent.parent
CLAUDE_DIR = PROJECT_ROOT / ".claude"
SCRAPING_HISTORY_FILE = CLAUDE_DIR / "scraping_history.json"
VAULT_LOGS_DIR = PROJECT_ROOT / "vault" / "logs"


def ensure_directories():
    """Create necessary directories if they don't exist"""
    CLAUDE_DIR.mkdir(exist_ok=True)
    VAULT_LOGS_DIR.mkdir(parents=True, exist_ok=True)


def load_scraping_history():
    """Load existing scraping history or create new"""
    if SCRAPING_HISTORY_FILE.exists():
        try:
            with open(SCRAPING_HISTORY_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    return {
        "sessions": [],
        "summary": {
            "total_sessions": 0,
            "total_items_scraped": 0,
            "total_errors": 0,
            "last_update": None,
        },
    }


def save_scraping_history(history):
    """Save scraping history to file"""
    history["summary"]["last_update"] = datetime.now().isoformat()

    with open(SCRAPING_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def parse_tool_input(tool_input_str):
    """Parse the tool input JSON string"""
    try:
        return json.loads(tool_input_str)
    except json.JSONDecodeError:
        return {"command": tool_input_str, "description": ""}


def parse_tool_output(tool_output_str):
    """Parse tool output for scraping metrics"""
    if not tool_output_str:
        return {}

    metrics = {}

    # Look for common scraping output patterns
    patterns = {
        "items_scraped": r"(?:scraped|found|collected|processed)\s+(\d+)",
        "errors": r"(?:error|failed|exception)\s*:?\s*(\d+)",
        "duration": r"(?:completed in|took|duration)\s+(\d+(?:\.\d+)?)\s*(?:seconds?|s)",
        "rate_limit": r"rate\s+limit|429|too many requests",
        "success": r"(?:success|completed|finished|done)",
    }

    output_lower = tool_output_str.lower()

    for key, pattern in patterns.items():
        if key == "rate_limit":
            metrics[key] = bool(re.search(pattern, output_lower))
        elif key == "success":
            metrics[key] = bool(re.search(pattern, output_lower))
        else:
            match = re.search(pattern, output_lower)
            if match:
                if key == "duration":
                    metrics[key] = float(match.group(1))
                else:
                    metrics[key] = int(match.group(1))

    return metrics


def identify_scraper_type(command):
    """Identify which scraper is being run"""
    if "reddit" in command.lower():
        return "reddit"
    elif "github" in command.lower():
        return "github"
    elif "web" in command.lower():
        return "web"
    elif "phase_01" in command:
        return "reddit"
    elif "phase_02" in command:
        return "github"
    elif "phase_03" in command:
        return "web"
    else:
        return "unknown"


def extract_dry_run_flag(command):
    """Check if this was a dry run"""
    return "--dry-run" in command or "--dry_run" in command


def main():
    """Main hook execution"""
    if len(sys.argv) < 3:
        print("Usage: scraping_session_logger.py <tool_input> <tool_output>")
        sys.exit(1)

    tool_input_str = sys.argv[1]
    tool_output_str = sys.argv[2]

    ensure_directories()

    # Parse inputs
    tool_input = parse_tool_input(tool_input_str)
    command = tool_input.get("command", "")

    # Only process if this looks like a scraping command
    scraping_keywords = ["python scrapers/", "python phase_", "python scripts/phase_"]
    if not any(keyword in command for keyword in scraping_keywords):
        return

    # Extract session information
    session_info = {
        "timestamp": datetime.now().isoformat(),
        "command": command,
        "scraper_type": identify_scraper_type(command),
        "dry_run": extract_dry_run_flag(command),
        "description": tool_input.get("description", ""),
        "metrics": parse_tool_output(tool_output_str),
        "raw_output_length": len(tool_output_str) if tool_output_str else 0,
    }

    # Load and update history
    history = load_scraping_history()
    history["sessions"].append(session_info)

    # Update summary
    history["summary"]["total_sessions"] += 1
    if session_info["metrics"].get("items_scraped"):
        history["summary"]["total_items_scraped"] += session_info["metrics"][
            "items_scraped"
        ]
    if session_info["metrics"].get("errors"):
        history["summary"]["total_errors"] += session_info["metrics"]["errors"]

    # Keep only last 100 sessions to avoid file bloat
    if len(history["sessions"]) > 100:
        history["sessions"] = history["sessions"][-100:]

    # Save updated history
    save_scraping_history(history)

    # Log to daily file for detailed tracking
    today = datetime.now().strftime("%Y-%m-%d")
    daily_log_file = VAULT_LOGS_DIR / f"scraping_activity_{today}.log"

    with open(daily_log_file, "a") as f:
        f.write(
            f"[{session_info['timestamp']}] {session_info['scraper_type']}: {command}\n"
        )
        if session_info["metrics"]:
            f.write(f"  Metrics: {json.dumps(session_info['metrics'])}\n")
        f.write(f"  Dry run: {session_info['dry_run']}\n\n")

    print(
        f"✓ Scraping session logged: {session_info['scraper_type']} ({'dry-run' if session_info['dry_run'] else 'live'})"
    )


if __name__ == "__main__":
    main()
