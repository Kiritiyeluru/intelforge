# Next Task - Session Planning

## Priority Queue for Next Coding Session

**Updated:** 2025-01-06

## High Priority - Must Complete Next

### 1. ✅ Phase 1 Research (COMPLETED)
- **Task:** Research Reddit scraping solutions using find_tools_template.md
- **Why:** Follow "reuse over rebuild" principle before implementing
- **Outcome:** Decided on PRAW + Reddit2Text combination
- **Documented:** docs/decision_log.md updated with tool selection rationale

### 2. Reddit API Setup
- **Task:** Create Reddit API application and configure credentials
- **Why:** Required for PRAW library authentication
- **Estimated Time:** 15-30 minutes
- **Dependencies:** Reddit account, completed research phase
- **Output:** Updated config/config.yaml with Reddit section

### 3. Phase 1 Implementation
- **Task:** Implement phase_01_reddit.py following roadmap specifications
- **Why:** Begin actual knowledge extraction functionality
- **Estimated Time:** 1-2 hours
- **Dependencies:** Completed research and API setup
- **Output:** Working Reddit scraper with --dry-run mode

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