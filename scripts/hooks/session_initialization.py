#!/usr/bin/env python3
"""
Session Initialization Hook
Ensures Claude Code reads the authoritative project plan at session start.
"""

import os
import json
from datetime import datetime
from pathlib import Path

def log_session_start():
    """Log session initialization and project plan status."""
    project_root = Path("/home/kiriti/alpha_projects/intelforge")
    
    # Paths
    current_plan = project_root / "session_docs" / "CURRENT_PROJECT_PLAN.md"
    session_config = project_root / ".claude" / "session_config.json"
    
    # Check if authoritative project plan exists
    if not current_plan.exists():
        print("❌ CRITICAL: CURRENT_PROJECT_PLAN.md not found!")
        return
    
    # Read session config
    if session_config.exists():
        with open(session_config, 'r') as f:
            config = json.load(f)
        
        current_focus = config.get("project_status", {}).get("phase", "Unknown")
        print(f"✅ Session initialized - Current focus: {current_focus}")
        print(f"📋 Authoritative project plan: {current_plan}")
        
        # Check for outdated locations
        outdated = config.get("session_initialization", {}).get("outdated_locations", [])
        for location in outdated:
            if Path(location).exists():
                print(f"⚠️  WARNING: Outdated project plan found at {location}")
    
    # Log session start
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": "session_start",
        "project_plan_location": str(current_plan),
        "status": "authoritative_plan_available"
    }
    
    # Append to session log
    session_log = project_root / ".claude" / "session_history.jsonl"
    with open(session_log, 'a') as f:
        f.write(json.dumps(log_entry) + "\n")

def validate_project_plan_read(file_path):
    """Validate that the correct project plan is being read."""
    if "session_docs/CURRENT_PROJECT_PLAN.md" in file_path:
        print("✅ Reading AUTHORITATIVE project plan - current strategic direction confirmed")
        print("📍 Location: /home/kiriti/alpha_projects/intelforge/session_docs/CURRENT_PROJECT_PLAN.md")
        print("🎯 Focus: Phase 2A - Core Foundation (Enterprise Repository Integration)")
        return True
    
    # Check for outdated references
    outdated_patterns = [
        "current_task.md",
        "next_task.md", 
        "session_summary.md"
    ]
    
    for pattern in outdated_patterns:
        if pattern in file_path and "DEPRECATED" not in file_path:
            print(f"⚠️  WARNING: Reading potentially outdated project plan: {file_path}")
            print("📋 RECOMMENDED: Read session_docs/CURRENT_PROJECT_PLAN.md instead")
            return False
    
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Called as hook with file path
        file_path = sys.argv[1]
        validate_project_plan_read(file_path)
    else:
        # Called for session initialization
        log_session_start()