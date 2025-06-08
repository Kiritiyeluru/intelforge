# Pull Request Template - IntelForge

## Summary

Brief description of what this PR accomplishes and why it was needed.

## Phase Information

- **Target Phase:** `phase_XX_module.py` (if applicable)
- **Type of Change:** 
  - [ ] New phase implementation
  - [ ] Enhancement to existing phase
  - [ ] Bug fix
  - [ ] Documentation update
  - [ ] Infrastructure/automation improvement

## Changes Made

### Technical Changes
- List specific code changes
- New dependencies added
- Configuration updates required

### Documentation Changes
- Updates to session handover files
- New documentation created
- Process improvements

## Testing Performed

- [ ] Manual testing with real data
- [ ] Dry-run mode testing
- [ ] Error handling validation
- [ ] Configuration file testing
- [ ] Output format verification (Obsidian compatibility)

## IntelForge Development Checklist

### Code Quality
- [ ] Followed reuse-over-rebuild principle (checked existing libraries first)
- [ ] Used functions over classes where appropriate
- [ ] Implemented graceful error handling with detailed logging
- [ ] Added --dry-run mode for safe testing (if applicable)
- [ ] Externalized configuration to config.yaml (no hardcoding)
- [ ] Generated Obsidian-compatible output with proper frontmatter

### Documentation
- [ ] Updated current_task.md with progress and decisions
- [ ] Updated next_task.md with upcoming priorities
- [ ] Updated session_summary.md with accomplishments and context
- [ ] Added/updated code comments and docstrings
- [ ] Followed commit message convention: `phase_XX: description`

### Architecture Alignment
- [ ] Module is self-contained and AI-regenerable
- [ ] Maintains lab notebook simplicity (not SaaS complexity)
- [ ] Follows phase_XX naming convention
- [ ] Compatible with solo development + AI assistance workflow
- [ ] Supports the "personal research brain" goal

### Integration
- [ ] Works with existing configuration structure
- [ ] Integrates properly with logging system (vault/logs/)
- [ ] Outputs to correct location (vault/notes/)
- [ ] Respects rate limits and ethical scraping practices
- [ ] Handles API authentication properly

## Configuration Changes

List any updates needed to `config/config.yaml`:

```yaml
# Example new configuration:
new_service:
  api_key: "your_api_key_here"
  rate_limit: 2
  enabled: true
```

## Testing Instructions

How to test this PR:

1. Update config.yaml with required settings
2. Run with --dry-run first: `python phase_XX_module.py --dry-run`
3. Verify output format in vault/notes/
4. Check logs in vault/logs/ for proper operation
5. Test error handling with invalid configuration

## Impact Assessment

### Risk Level
- [ ] Low - Minor changes, well-tested
- [ ] Medium - New functionality, some complexity
- [ ] High - Major changes, needs careful review

### Affected Systems
- [ ] Reddit integration
- [ ] GitHub integration
- [ ] AI summarization
- [ ] Configuration system
- [ ] Logging system
- [ ] Output generation
- [ ] Session handover system

## Session Context

### What Problem This Solves
Brief explanation of the issue or need this addresses.

### Decision Rationale
Why this approach was chosen over alternatives.

### Future Considerations
What should be considered in future development related to this change.

## Reviewer Notes

### Key Areas to Review
- Configuration handling
- Error scenarios
- Output format consistency
- Documentation completeness

### Known Issues
List any known limitations or issues that will be addressed in future PRs.

---

**Before merging:** Ensure all session handover files are updated and this change is properly documented for future development sessions.