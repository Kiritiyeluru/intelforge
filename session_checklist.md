# Session Checklist - IntelForge

## Pre-Session Startup (3-5 minutes)

### Context Loading
- [ ] Read `docs/automation/current_task.md` - What's actively being worked on
- [ ] Read `docs/automation/next_task.md` - Planned priorities  
- [ ] Read `docs/automation/session_summary.md` - Recent progress and decisions
- [ ] Check `docs/automation/decision_log.md` - Recent architectural choices
- [ ] Review `cline_docs/currentTask.md` if exists - AI assistant context

### Environment Check
- [ ] Verify working directory: `/home/kiriti/alpha_projects/intelforge`
- [ ] Check git status - any uncommitted changes?
- [ ] Verify config files are accessible
- [ ] Check vault/ directories exist (logs/, notes/)

## During Session

### Development Work
- [ ] Update `current_task.md` when starting new work
- [ ] Log any configuration changes in `config_changelog.md`
- [ ] Document any issues in `troubleshooting_guide.md`
- [ ] Record important discoveries in `learning_log.md`
- [ ] Update `decision_log.md` for architectural choices

### Code Quality
- [ ] Follow phase_XX naming conventions
- [ ] Use existing libraries (check with find_tools_template.md first)
- [ ] Add proper error handling and logging
- [ ] Include --dry-run mode where applicable
- [ ] Externalize config to config.yaml

## End-of-Session Handover (5-10 minutes)

### Critical Documentation Updates
- [ ] **MUST DO:** Update `current_task.md` with:
  - [ ] What was accomplished this session
  - [ ] Current state of work
  - [ ] Any blockers or issues
  - [ ] Next immediate steps

- [ ] **MUST DO:** Update `next_task.md` with:
  - [ ] Reprioritized task list
  - [ ] New tasks discovered
  - [ ] Dependencies identified
  - [ ] Context needed for next developer

- [ ] **MUST DO:** Update `session_summary.md` with:
  - [ ] Session accomplishments
  - [ ] Key decisions made
  - [ ] Important discoveries
  - [ ] Updated project status

### Optional but Recommended
- [ ] Add entry to `decision_log.md` if architectural choices were made
- [ ] Update `troubleshooting_guide.md` if issues were resolved
- [ ] Add to `learning_log.md` if significant insights were gained
- [ ] Update `config_changelog.md` if configuration was modified

### Code Commit
- [ ] Stage relevant files for commit
- [ ] Write commit message using format: `phase_XX: description` or `docs: description`
- [ ] Ensure commit message is clear and descriptive
- [ ] Push to remote repository

### Final Verification
- [ ] All handover files have current dates
- [ ] No critical information exists only in your head
- [ ] Next developer can understand context in <5 minutes
- [ ] All work is properly committed and pushed

## Emergency Session End (1-2 minutes)

If session must end abruptly:

- [ ] **MINIMUM:** Update `current_task.md` with current state
- [ ] **CRITICAL:** Note any incomplete work or potential issues
- [ ] Commit work-in-progress with clear WIP message

## Checklist Validation

After each session, rate these areas (1-5 scale):

- **Context Preservation:** Could next developer continue seamlessly? ___/5
- **Decision Documentation:** Are architectural choices clear? ___/5  
- **Code Quality:** Follows IntelForge standards? ___/5
- **Documentation Currency:** All files reflect current state? ___/5

**Target:** All areas should be 4/5 or higher. If any area is 3/5 or lower, address before ending session.

## Handover Quality Indicators

**Good handover includes:**
- Clear description of what was worked on
- Specific technical decisions and why they were made
- Next steps with sufficient detail to continue
- Any gotchas or issues encountered
- Updated priority queue for next session

**Poor handover warning signs:**
- Vague descriptions ("worked on Reddit module")
- Missing rationale for technical choices
- Unclear next steps ("continue implementation")
- Outdated task priorities
- Information only in commit messages