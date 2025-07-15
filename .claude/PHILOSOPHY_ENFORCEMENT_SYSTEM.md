# EXTREME PHILOSOPHY ENFORCEMENT SYSTEM

## 🚨 CRITICAL OVERVIEW
This system implements **ZERO TOLERANCE** enforcement of the "REUSE OVER REBUILD" philosophy through multiple validation layers that ensure Claude NEVER overlooks or forgets the critical development principles.

## 🎯 ENFORCEMENT LAYERS

### Layer 1: Global CLAUDE.md Files
- **Global**: `/home/kiriti/.claude/CLAUDE.md` (ALL projects)
- **Project**: `/home/kiriti/alpha_projects/intelforge/.claude/CLAUDE.md` (IntelForge only)
- **Authority**: Highest precedence - read at session start
- **Content**: Philosophy prominently placed at the top with urgent formatting

### Layer 2: Session Initialization Enforcement
- **File**: `scripts/hooks/session_initialization.py`
- **Trigger**: Every session start via Notification hook
- **Action**: Displays large, unmissable philosophy reminder
- **Logging**: Records enforcement in `.claude/philosophy_enforcement.log`

### Layer 3: Universal Philosophy Reminders
- **File**: `scripts/hooks/philosophy_reminder.py`
- **Trigger**: EVERY tool use (PreToolUse: "*")
- **Action**: Displays randomized philosophy reminders
- **Features**:
  - 5 different reminder variations to avoid habituation
  - Special alerts for code-related tools (Write, Edit, MultiEdit)
  - Boxed format for maximum visibility
  - Timestamp and tool context

### Layer 4: Code Validation Enforcement
- **File**: `scripts/hooks/philosophy_enforcer.py`
- **Trigger**: All code writing tools (Write, Edit, MultiEdit)
- **Action**: Scans code for custom implementation patterns
- **Blocking**: **TERMINATES** execution if violations found
- **Features**:
  - Regex pattern matching for custom code indicators
  - Approved frameworks whitelist validation
  - Detailed violation reports
  - Complete action blocking with error exit

## 🔍 DETECTION PATTERNS

### Blocked Custom Code Patterns
```regex
# Function definitions
def\s+(?:scrape|extract|parse|fetch|crawl|download)_\w+
class\s+\w*(?:Scraper|Parser|Crawler|Extractor)

# Manual implementations  
BeautifulSoup\(
requests\.get\(
selenium\.
urllib\.

# Banned phrases
let's\s+(?:build|create|implement|write)\s+(?:a|our|custom)
custom\s+(?:scraper|parser|extractor|crawler)
from\s+scratch
```

### Approved Frameworks (ALLOWED)
```
scrapy, trafilatura, scrapy-playwright, nodriver, camoufox, 
scrapling, paperscraper, autoscraper, stealth-requests, 
news-please, playwright-python, arxiv.py, feedparser, 
botasaurus, selectolax, httpx, polars, praw, pygithub
```

## 🎛️ HOOK CONFIGURATION

### settings.json Configuration
```json
"hooks": {
  "PreToolUse": [
    {
      "matcher": "*",
      "hooks": [{"command": "philosophy_reminder.py"}]
    },
    {
      "matcher": "Write|Edit|MultiEdit", 
      "hooks": [{"command": "philosophy_enforcer.py"}]
    }
  ],
  "Notification": [
    {
      "matcher": "session_start",
      "hooks": [{"command": "session_initialization.py"}]
    }
  ]
}
```

## 🚨 VIOLATION HANDLING

### When Violations Are Detected:
1. **Immediate Termination**: Hook exits with error code 1
2. **Detailed Report**: Shows exact patterns and files
3. **Action Guidance**: Required steps to fix violation
4. **Philosophy Reminder**: Full philosophy text displayed
5. **Logging**: Violation logged for review

### Violation Report Example:
```
🚨 PHILOSOPHY VIOLATION - ACTION BLOCKED 🚨

VIOLATIONS FOUND:
1. MANUAL IMPLEMENTATIONS
   Pattern: requests\.get\(
   File: custom_scraper.py
   Severity: CRITICAL

REQUIRED ACTION:
1. STOP current implementation
2. Research existing tools using find_tools_template.md
3. Use approved frameworks
4. Wrap existing tools instead of reimplementing
```

## 📊 MONITORING & LOGGING

### Log Files:
- `.claude/philosophy_enforcement.log` - Session start enforcements
- `.claude/philosophy_reminders.log` - All reminder occurrences
- `.claude/bash-command-log.txt` - Command history for review

### Metrics Tracked:
- Reminder frequency per session
- Violation detection rate
- Tool usage patterns
- Philosophy compliance trends

## 🎯 EFFECTIVENESS FEATURES

### Anti-Habituation Measures:
- **Randomized Reminders**: 5 different variations
- **Dynamic Content**: Tool-specific messages
- **Visual Prominence**: Boxed format with emojis
- **Contextual Alerts**: Enhanced messages for code tools

### Extreme Enforcement Mode:
```bash
# Activate extreme mode for high-risk scenarios
philosophy_reminder.py Write extreme
```

### Progressive Enforcement:
1. **Gentle**: Standard reminders for all tools
2. **Moderate**: Enhanced alerts for code tools
3. **Extreme**: Blocking enforcement with violation details
4. **Nuclear**: Session initialization philosophy display

## 🔧 MAINTENANCE

### Regular Tasks:
- Review violation logs monthly
- Update pattern detection for new frameworks
- Add new approved frameworks to whitelist
- Refresh reminder variations to maintain effectiveness

### Configuration Updates:
- Modify patterns in `philosophy_enforcer.py`
- Add frameworks to `APPROVED_FRAMEWORKS` set
- Update reminder variations in `philosophy_reminder.py`
- Adjust hook triggers in `settings.json`

## 📈 SUCCESS METRICS

### Measurable Outcomes:
- **Zero custom implementations** in new code
- **100% framework usage** for scraping tasks
- **Immediate violation detection** before code execution
- **Consistent philosophy adherence** across sessions

### Evidence of Success:
- Phase 2C: 400+ line custom scraper → <200 lines with frameworks
- Superior reliability and maintainability
- Reduced development time
- Better performance characteristics

## 🚀 DEPLOYMENT STATUS

✅ **ACTIVE**: All enforcement layers operational
✅ **TESTED**: Violation detection and blocking verified
✅ **LOGGED**: All enforcement actions tracked
✅ **EXTREME**: Maximum possible automation without human intervention

This system ensures **ABSOLUTE COMPLIANCE** with the REUSE OVER REBUILD philosophy through multiple redundant enforcement mechanisms.