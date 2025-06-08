# Next Task - Session Planning

## Priority Queue for Next Coding Session

**Updated:** 2025-01-06

## High Priority - Must Complete Next

### 1. Complete Documentation Infrastructure
- **Task:** Create session_summary.md
- **Why:** Complete the three-file handover system
- **Estimated Time:** 10 minutes
- **Dependencies:** None

### 2. Create GitHub Templates
- **Task:** Set up issue and PR templates
- **Why:** Standardize task reporting and prevent inconsistent documentation
- **Estimated Time:** 20 minutes
- **Dependencies:** Understanding IntelForge workflow patterns

### 3. Set Up GitHub Projects Board
- **Task:** Create project board with defined columns and labels
- **Why:** Provide visual project tracking and automate status updates
- **Estimated Time:** 15 minutes
- **Dependencies:** GitHub repo access

## Medium Priority - Next Session Goals

### 4. Implement Phase 1 Development
- **Task:** Begin Reddit scraping module (phase_01_reddit.py)
- **Why:** Start actual IntelForge functionality development
- **Prerequisites:** 
  - Research existing Reddit scraping libraries (use find_tools_template.md)
  - Review PRAW documentation
  - Set up config.yaml structure
- **Dependencies:** Completed documentation infrastructure

### 5. Create Development Templates
- **Task:** Issue templates for research, implementation, bugs
- **Why:** Structure future development work
- **Templates Needed:**
  - Research task template
  - Implementation task template  
  - Bug report template
  - Phase completion template

## Low Priority - Future Sessions

### 6. Commit Message Automation
- **Task:** Implement commit-msg hook for phase_XX convention
- **Why:** Enforce consistent commit messaging
- **Dependencies:** Basic development workflow established

### 7. Basic GitHub Actions
- **Task:** Simple automation for project board updates
- **Why:** Reduce manual project management overhead
- **Dependencies:** Project board in active use

## Research Tasks for Next Developer

### Before Starting Phase 1:
1. **Review find_tools_template.md** to research Reddit scraping solutions
2. **Check existing PRAW usage patterns** in similar projects
3. **Review config.yaml structure** in CLAUDE.md specifications
4. **Understand Obsidian markdown format** requirements for output

### Context Needed:
- Read `current_task.md` for what was just completed
- Read `session_summary.md` for overall project status
- Check `cline_docs/` for project roadmap and current status
- Review `session_checklist.md` for workflow procedures

## Decision Points for Next Session

1. **Scope of Reddit integration:** Focus on specific subreddits or general framework?
2. **Configuration approach:** How much to put in config.yaml vs. command line args?
3. **Error handling strategy:** How to handle rate limits and API failures?
4. **Testing approach:** What testing framework to use for the modules?

## Files to Update Before Ending Next Session

- Update `current_task.md` with new active work
- Update this file (`next_task.md`) with new priorities
- Update `session_summary.md` with accomplishments
- Update relevant files in `docs/` (decision_log, troubleshooting_guide, etc.)
- Follow `session_checklist.md` for complete handover
- Commit changes with proper phase_XX: message format