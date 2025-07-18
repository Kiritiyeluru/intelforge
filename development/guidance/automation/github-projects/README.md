# GitHub Projects Automation for IntelForge

## Why We Are Doing This

Keeping track of project status, progress, and next steps manually is time-consuming and error-prone. Updates to roadmaps and status documents often lag behind actual development activity, causing confusion and inefficiency. **Documentation decay has been a critical issue that has led to burning previous repositories.**

By leveraging GitHub Projects and lightweight automation, we aim to:

- Automate status tracking directly linked to GitHub issues, pull requests, and commits
- Maintain a live, interactive project board that reflects real-time progress
- Reduce manual overhead in updating documentation and roadmaps
- **Prevent documentation rot through consistent session handovers**
- Ensure structured project management aligned with IntelForge's phase-based development
- Support solo development with AI assistance through clear context preservation

## What We Are Doing

- Setting up a GitHub Projects board tailored to IntelForge's phase-based workflow
- Creating session handover documentation (current_task.md, next_task.md, session_summary.md)
- Defining issue and pull request templates to standardize task reporting
- Implementing lightweight commit message conventions aligned with phase_XX naming
- Creating automated session context preservation
- Documenting the process for maintaining and extending the automation

## Session Handover System

### Three Critical Files for Context Preservation

1. **current_task.md** - What is actively being worked on right now
   - Current phase/module being developed
   - Specific implementation details and decisions made
   - Blockers or issues encountered
   - Next immediate steps

2. **next_task.md** - What should be tackled in the next session
   - Prioritized backlog items
   - Dependencies and prerequisites
   - Research tasks needed
   - Testing and validation steps

3. **session_summary.md** - High-level progress and context
   - What was accomplished in recent sessions
   - Key decisions and architectural choices
   - Important learnings and discoveries
   - Updated project status

### Commit Message Convention

Follow IntelForge's phase-based structure:
```
phase_XX: brief description of change

Examples:
phase_01: implement reddit scraping with PRAW
phase_02: add GitHub repository mining logic
docs: update session handover documentation
config: add new API key configurations
```

## How to Continue and Maintain

- **Before each coding session**: Read current_task.md, next_task.md, session_summary.md
- **During development**: Update current_task.md with progress and decisions
- **End of session**: Update all three handover files before stopping
- Use the provided issue and PR templates for all new tasks and changes
- Follow the commit message conventions to maintain phase tracking
- Monitor the GitHub Projects board for real-time status updates
- Document any changes to the automation setup in this folder

## GitHub Projects Board Structure

**Columns:**
- **Backlog** - Planned features and research tasks
- **Research** - Active investigation and tool discovery
- **In Progress** - Current development work (limit: 1-2 items)
- **Testing** - Implementation complete, needs validation
- **Done** - Completed and verified

**Labels:**
- `phase-01`, `phase-02`, etc. - Track which phase the work belongs to
- `research` - Investigation and tool discovery tasks
- `implementation` - Coding and development work
- `documentation` - Updates to docs and handover files
- `bug` - Issues and fixes
- `enhancement` - Improvements to existing functionality

This setup will evolve as the project grows, so maintaining clear documentation and consistent practices is essential for long-term success and preventing the documentation decay that has plagued previous projects.
