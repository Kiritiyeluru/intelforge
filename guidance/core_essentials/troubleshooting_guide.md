# Troubleshooting Guide - IntelForge

## Purpose
Document common issues and their solutions to prevent repeated problem-solving and maintain development velocity.

---

## GitHub and Git Issues

### Problem: Git remote URL incorrect after repository creation
**Symptoms:** Push fails with repository not found  
**Solution:** Update remote URL: `git remote set-url origin https://github.com/Kiritiyeluru/intelforge.git`  
**Prevention:** Double-check username in remote URL during setup  

### Problem: GitHub CLI project command not available
**Symptoms:** `gh project create` returns "unknown command"  
**Root Cause:** Older GitHub CLI version  
**Solution:** Set up project board manually via web interface at https://github.com/owner/repo/projects  
**Workaround:** Use GitHub web interface for project management until CLI is updated  

---

## Configuration Issues

### Problem: API credentials not loading
**Symptoms:** Authentication errors despite correct config.yaml  
**Common Causes:**
- YAML indentation errors
- File not in expected location
- Permissions issues on config file

**Debugging Steps:**
1. Verify config.yaml location: `config/config.yaml`
2. Check YAML syntax with: `python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"`
3. Verify file permissions: `ls -la config/config.yaml`

**Solution Template:**
```yaml
service_name:
  api_key: "your_key_here"
  setting: value
```

---

## Module Development Issues

### Problem: Import errors for custom modules
**Symptoms:** `ModuleNotFoundError` when running phase modules  
**Solution:** Ensure Python path includes project root or use absolute imports  
**Prevention:** Keep modules self-contained and avoid complex import hierarchies  

### Problem: Rate limiting causing failures
**Symptoms:** API calls failing with 429 errors  
**Solution:** Implement exponential backoff and respect API limits  
**Code Pattern:**
```python
import time
import random

def api_call_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
    raise Exception("Max retries exceeded")
```

---

## Documentation and Handover Issues

### Problem: Session context lost between developers
**Symptoms:** Next developer spends significant time understanding current state  
**Root Cause:** Incomplete handover documentation  
**Solution:** Follow session_checklist.md religiously  
**Prevention:** Set timer for handover documentation, treat as non-negotiable  

### Problem: Decision rationale unclear
**Symptoms:** Repeated discussions about already-decided architecture  
**Solution:** Document decisions in decision_log.md with alternatives and rationale  
**Template:** See decision_log.md for proper format  

---

## Environment Setup Issues

### Problem: Vault directories not created
**Symptoms:** File write errors when trying to save outputs  
**Solution:** Create required directories: `mkdir -p vault/{logs,notes}`  
**Prevention:** Include directory creation in module initialization  

### Problem: Config file missing
**Symptoms:** Application crashes on startup  
**Solution:** Copy config template: `cp config/config.yaml.template config/config.yaml`  
**Prevention:** Document config setup in README  

---

## Development Workflow Issues

### Problem: Commit message rejected by hook
**Symptoms:** Git commit fails with format error  
**Solution:** Use format: `phase_XX: description` or `docs: description`  
**Valid Examples:**
- `phase_01: implement reddit scraping with PRAW`
- `docs: update troubleshooting guide`
- `config: add reddit API settings`

### Problem: Files not following IntelForge conventions
**Symptoms:** Code doesn't match project patterns  
**Solution:** Review CLAUDE.md and existing modules for conventions  
**Key Conventions:**
- Functions over classes
- phase_XX naming for modules
- Configuration in config.yaml
- Logging to vault/logs/
- Output to vault/notes/

---

## Performance Issues

### Problem: Large output files overwhelming system
**Symptoms:** Slow file operations, disk space issues  
**Solution:** Implement pagination and file rotation  
**Prevention:** Include file size limits in configuration  

### Problem: Memory usage growing over time
**Symptoms:** Application becomes slower during long runs  
**Common Cause:** Not cleaning up large data structures  
**Solution:** Explicitly delete large variables, use generators for data processing  

---

## Template for New Issues

When you encounter a new problem:

**Problem:** [Brief description]  
**Symptoms:** [What you observe]  
**Root Cause:** [Why this happens]  
**Solution:** [Step-by-step fix]  
**Prevention:** [How to avoid in future]  
**Related Issues:** [Links to GitHub issues]  
**Date Added:** [YYYY-MM-DD]  

---

## MCP (Model Context Protocol) Issues

### Problem: MCP server installation fails
**Symptoms:** `claude mcp add` command returns errors  
**Common Causes:**
- Missing dependencies (Node.js, Python)
- Incorrect server path or name
- API key authentication issues

**Debugging Steps:**
1. Verify dependencies: `node --version && npm --version`
2. Check server installation: `which mcp-server-name`
3. Test API keys manually
4. Review Claude Code logs

**Reference:** See `docs/mcp_setup_guide.md` for complete installation guide

### Problem: MCP server not responding
**Symptoms:** Tools show as available but don't return results  
**Solution:** Check API quotas, restart Claude Code, verify server status  
**Prevention:** Monitor API usage and set up alerts for quota limits

### Problem: All MCP servers failed to connect
**Symptoms:** `/mcp` command returns "all mcp servers failed to connect"  
**Root Cause:** Outdated or broken MCP server configurations  
**Solution:** Complete MCP server reset using removal commands  

**Step-by-step fix:**
1. List current servers: `claude mcp list`
2. Remove all servers: `claude mcp remove server-name` for each
3. Verify cleanup: `claude mcp list` should show "No MCP servers configured"
4. Reinstall using updated methods

**Prevention:** Use consistent installation methods, avoid mixing approaches  

---

## Quick Reference Commands

```bash
# Check project status
git status
python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"

# Fix common directory issues
mkdir -p vault/{logs,notes}
mkdir -p config

# Verify handover files are current
ls -la docs/automation/{current_task,next_task,session_summary}.md

# Test module in dry-run mode
python phase_XX_module.py --dry-run

# Check recent commits for context
git log --oneline -10

# MCP server management
claude mcp list
claude mcp get <server_name>
claude mcp remove <server_name>
```