#!/usr/bin/env python3
"""
PHILOSOPHY REMINDER - Every Response Enforcement

This hook ensures that Claude is reminded of the critical philosophy 
before EVERY single response. Creates constant awareness of the 
REUSE OVER REBUILD principle.

EXTREME ENFORCEMENT: Philosophy displayed with every tool use.
"""

import sys
import json
import random
from datetime import datetime
from pathlib import Path

class PhilosophyReminder:
    """Generates philosophy reminders for every Claude response"""
    
    # Multiple variations to avoid habituation - CONCISE AND CLEAR
    PHILOSOPHY_VARIATIONS = [
        "🚨 REUSE OVER REBUILD: Use existing frameworks, not custom code",
        "🔍 CHECK FIRST, BUILD NEVER: Research tools before coding",
        "⚡ FRAMEWORK OVER CUSTOM: scrapy, playwright, botasaurus > custom",
        "🎯 WRAP DON'T WRITE: Integrate existing tools, don't reimplement",
        "📋 COMPLIANCE CHECK: Using approved frameworks? No custom code?"
    ]
    
    CRITICAL_REMINDERS = [
        "🚨 REMEMBER: Phase 2C success - 400+ lines → <200 lines with frameworks",
        "⚡ ENFORCE: Any custom code suggestion will be REJECTED",
        "🎯 PRIORITY: Research tools FIRST, implement SECOND",
        "🔍 VALIDATE: Does this solution use existing frameworks?",
        "📋 CHECK: Have I searched for existing tools before coding?",
    ]
    
    def __init__(self):
        self.project_root = Path("/home/kiriti/alpha_projects/intelforge")
        self.reminder_log = self.project_root / ".claude" / "philosophy_reminders.log"
    
    def get_reminder(self, tool_name: str) -> str:
        """Get randomized philosophy reminder based on tool used"""
        base_reminder = random.choice(self.PHILOSOPHY_VARIATIONS)
        critical_reminder = random.choice(self.CRITICAL_REMINDERS)
        
        # Special reminders for code-related tools
        code_tools = ['Write', 'Edit', 'MultiEdit']
        if tool_name in code_tools:
            full_reminder = f"🚨 CODE TOOL ALERT: {base_reminder} | {critical_reminder} | TOOL: {tool_name}"
        else:
            full_reminder = f"🚨 PHILOSOPHY: {base_reminder} | {critical_reminder}"
        
        # Log reminder
        self._log_reminder(tool_name)
        
        return full_reminder
    
    def _log_reminder(self, tool_name: str):
        """Log philosophy reminder occurrence"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "reminder_type": "philosophy_enforcement",
            "action": "reminder_displayed"
        }
        
        with open(self.reminder_log, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def get_extreme_reminder(self) -> str:
        """Get extreme reminder for high-risk scenarios"""
        return """
🚨🚨🚨 EXTREME PHILOSOPHY ENFORCEMENT 🚨🚨🚨

STOP! Before proceeding with ANY implementation:

1. 🔍 RESEARCH: Use find_tools_template.md
2. 📋 CHECK: Review approved frameworks list
3. ✅ VALIDATE: Is there an existing tool for this?
4. 🎯 WRAP: Use minimal wrapper around existing tools
5. ⚡ REJECT: Any custom implementation suggestions

EVIDENCE: Phase 2C - 400+ custom lines → <200 framework lines
RESULT: Superior reliability, maintainability, performance

VIOLATION = IMMEDIATE REJECTION
"""

def main():
    """Main hook execution for philosophy reminder"""
    if len(sys.argv) < 2:
        print("Usage: philosophy_reminder.py <tool_name> [extreme]")
        sys.exit(1)
    
    tool_name = sys.argv[1]
    extreme_mode = len(sys.argv) > 2 and sys.argv[2] == "extreme"
    
    reminder = PhilosophyReminder()
    
    if extreme_mode:
        print(reminder.get_extreme_reminder())
    else:
        print(reminder.get_reminder(tool_name))

if __name__ == "__main__":
    main()