# IntelForge Project Memory

## Project Overview
**IntelForge** is a personal AI-powered knowledge extraction system for web scraping and intelligence gathering, focused on algorithmic trading and technical strategy mining. Built by a solo developer using AI assistance.

## Core Development Philosophy

### Simplicity-First Principles

- **"We are building a lab notebook, not a SaaS platform"**
- One file per phase, flat structure (no src/ directories)
- Functions over classes when possible
- Configuration-driven behavior (avoid hardcoding)
- AI-regenerable modules (small, focused, well-documented)

### Reuse-Over-Rebuild Strategy

- **ALWAYS** check for existing libraries/tools before building custom logic
- Use `@prompts/find_tools_template.md` before starting any new module
- Refer to `@docs/find_vs_build.md` for decision framework
- Wrap existing tools rather than reimplementing common functionality

## Development Workflow

### Before Starting Any Module

1. **Research existing solutions** using find_tools_template.md
2. **Follow development checklist** from `@knowledge_docs/Reusable_Development_Checklist_for_Each_Module.md`
3. **Check current roadmap** in `@cline_docs/projectRoadmap.md`
4. **Update current task** in `@cline_docs/currentTask.md`

### Session Management (CRITICAL - Always Follow)

**Before every session:**
- Read `current_task.md` - what's actively being worked on
- Read `next_task.md` - planned priorities for this session  
- Read `session_summary.md` - recent progress and key decisions
- Follow `session_checklist.md` for consistent workflow

**During development:**
- Update `current_task.md` with progress and blockers
- Log decisions in `docs/decision_log.md` with rationale
- Document solutions in `docs/troubleshooting_guide.md`
- Track config changes in `docs/config_changelog.md`

**End of every session (MANDATORY):**
- Update all three handover files: `current_task.md`, `next_task.md`, `session_summary.md`
- Follow end-of-session checklist in `session_checklist.md`
- Commit with proper phase_XX: format

### Code Structure Standards

- **Modules**: `phase_XX_description.py` (sequential numbering)
- **Configuration**: Use `@config/config.yaml` for all settings
- **Logging**: Always log to `vault/logs/` with descriptive filenames
- **Output**: Obsidian-compatible markdown in `vault/notes/`
- **Error handling**: Graceful failures with detailed error messages
- **Dry-run mode**: Include `--dry-run` flag for safe testing

### File Organization

```text
intelforge/
├── phase_XX_module.py     # Self-contained phase modules
├── config/config.yaml     # Centralized configuration
├── vault/
│   ├── notes/            # Scraped content (Obsidian format)
│   └── logs/             # Operation logs
├── cline_docs/           # AI development guidance
├── docs/                 # Decision frameworks
├── prompts/              # Reusable AI templates
└── knowledge_docs/       # Development checklists
```

## Technical Standards

### API Integration

- **Reddit**: Use PRAW library for r/algotrading, r/investing
- **GitHub**: Use PyGitHub for repository mining
- **AI Services**: OpenAI + Claude APIs for summarization
- **Rate limiting**: Implement delays and retry logic
- **Error handling**: Log failures, continue processing

### Output Format (Obsidian-Compatible)

```markdown
---
source: [reddit|github|blog|pdf]
date: YYYY-MM-DD
tags: [strategy, bollinger-bands, python]
content_hash: sha256_hash
author: username
---

# Title

Content with [[wikilinks]] and #tags
```

### Security & Privacy

- **API keys**: Store in config.yaml (gitignored)
- **Local-first**: All data stored in vault/ directory
- **Ethical scraping**: Respect robots.txt and rate limits
- **Personal use only**: Non-commercial research purposes

## Current Phase Priority

**Phase 1: Reddit Scraping** - Implement PRAW-based extraction from trading subreddits

## Development Checklist Reference

Use `@knowledge_docs/Reusable_Development_Checklist_for_Each_Module.md` for every module:

1. Reuse over rebuild
2. Clear interfaces & modularity  
3. Resilience by default
4. AI-friendliness
5. Configuration, not hardcoding
6. Testability and observability
7. Regeneration-friendly design
8. Clean exit and reset logic
9. Folder and file hygiene
10. Self-documentation

## Common Anti-Patterns to Avoid

- Building custom HTTP scrapers (use requests/praw)
- Manual RSS parsing (use feedparser)
- Custom vector stores (use FAISS/Chroma)
- Over-abstracted configs (keep simple YAML)
- Framework-based structure (prefer readable scripts)
- Complex class hierarchies (use functions)

## Success Criteria

- Everything lives in 1-2 files per phase
- Total repo understandable in <5 minutes
- Fully manageable by solo user with AI help
- Builds personal research brain, not commercial product
