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
- **Check `@docs/scraping_tools_recommendations.md` for vetted scraping tools and libraries**
- Wrap existing tools rather than reimplementing common functionality

## Development Workflow

### Claude Code Hooks Integration

**3 Active Automation Hooks:**
- **Bash Command Logging** (PreToolUse): Logs all shell commands to `~/.claude/bash-command-log.txt`
- **Phase File Validation** (PreToolUse): Enforces `phase_XX_name.py` naming convention
- **Knowledge Auto-Organization** (PostToolUse): Auto-triggers article organizer for `intake/` files

**Configuration**: Located in `.claude/settings.json` → `"hooks"` section. Modify via `/hooks` command or direct file editing.

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
├── knowledge_management/  # Article organization system
│   ├── intake/           # Drop folder for new articles
│   ├── articles/         # Auto-categorized articles
│   ├── docs/             # Project tracking & decisions
│   └── config/           # Categorization rules
├── cline_docs/           # AI development guidance
├── docs/                 # Decision frameworks
├── prompts/              # Reusable AI templates
└── knowledge_docs/       # Development checklists
```

## Technical Standards

### Web Scraping (see `@docs/scraping_tools_recommendations.md` for details)

- **Static Content**: selectolax + httpx (high-performance)
- **Dynamic Content**: Playwright (modern, reliable)
- **Framework**: Scrapy (enterprise-scale)
- **Anti-Detection**: scrapy-fake-useragent + proxy rotation

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
**Phase 7: Knowledge Management** - Auto-organize articles with AI-ready processing pipeline ✅ COMPLETE
**Phase 8: AI Processing** - Semantic search with embeddings and vector database ✅ COMPLETE

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

## Knowledge Management System

**Auto-Organization Workflow:**
1. Save new articles to `knowledge_management/intake/`
2. Run `python phase_07_article_organizer.py` to auto-categorize
3. Articles moved to organized folders based on content analysis
4. Categories: claude_mcp, web_scraping, ai_workflows, productivity

**AI-Powered Semantic Search:**
1. Build embeddings: `python phase_08_ai_processor.py --build`
2. Search articles: `python phase_08_ai_processor.py --search "query"`
3. Uses sentence-transformers + FAISS for local vector search
4. 1,683 chunks processed, 384D embeddings, <1s search time

**Current Status:** 47 articles organized, AI search operational, 4MB vector database

## MCP Integration

**Local MCP Servers:** Refer to `@docs/Run MCP Servers In Seconds With Docker.md` - Docker MCP Toolkit is the preferred method for managing local MCP servers (one-click setup, verified catalog, centralized management).

**Remote MCP Servers:** Claude Code now supports vendor-managed remote MCP servers with OAuth authentication. No local installation required - access through Anthropic's MCP directory for integrations like Linear (project management) and Sentry (error monitoring).

**Current Setup:** 6 local MCP servers installed (Perplexity, Financial Datasets, SQLite, Puppeteer, GitHub, Brave Search). Future phases can leverage hybrid approach: local servers for development tools, remote servers for external service integrations.

**MCP Server Setup Commands:**

**Local/Stdio Servers:**
```bash
# Basic syntax
claude mcp add <name> <command> [args...]

# With environment variables
claude mcp add my-server -e API_KEY=123 -- /path/to/server arg1 arg2
```

**Remote SSE Servers:**
```bash
# Basic SSE server
claude mcp add --transport sse <name> <url>

# With custom headers
claude mcp add --transport sse api-server https://api.example.com/mcp --header "X-API-Key: your-key"
```

**Remote HTTP Servers:**
```bash
# Basic HTTP server
claude mcp add --transport http <name> <url>

# With authentication
claude mcp add --transport http secure-server https://api.example.com/mcp --header "Authorization: Bearer token"
```

**Scope Management:**
- `--scope local` (default): Personal, project-specific
- `--scope project`: Team-shared via `.mcp.json` file
- `--scope user`: Cross-project, personal

**Management Commands:**
```bash
claude mcp list                    # List all servers
claude mcp get <server-name>       # Get server details
claude mcp remove <server-name>    # Remove server
claude mcp add-json <name> '<json>' # Add from JSON config
claude mcp add-from-claude-desktop  # Import from Claude Desktop
```

**Advanced Features:**
- **Resource References:** `@server:protocol://resource/path`
- **Slash Commands:** `/mcp__servername__promptname`
- **OAuth Authentication:** Use `/mcp` command for secure connections
- **Claude as Server:** `claude mcp serve` to expose Claude tools

**Available Remote Endpoints:**
- Linear: `https://mcp.linear.app/sse` (project management)
- Sentry: `https://mcp.sentry.io/sse` (error monitoring)

**Performance Benefits:** Real-time updates via Server-Sent Events, vendor-managed scaling, eliminates local server maintenance.

## Claude Code Hooks Configuration

**Hook Configuration Process:**

1. **Via UI Interface:**
   ```bash
   # In Claude Code terminal
   /hooks
   ```
   - Select hook type (PreToolUse, PostToolUse, Notification, Stop)
   - Add matchers (tool names, file patterns)
   - Configure commands with environment variables
   - Save to User or Project settings

2. **Via Direct File Edit:**
   - Edit `.claude/settings.json` → `"hooks"` section
   - Follow JSON structure with proper escaping
   - Restart Claude Code to apply changes

3. **Hook Environment Variables:**
   - `$CLAUDE_TOOL_NAME`: Tool being used (e.g., "Bash", "Write")
   - `$CLAUDE_TOOL_INPUT`: JSON input to tool
   - `$CLAUDE_FILE_PATHS`: Space-separated file paths
   - `$CLAUDE_TOOL_OUTPUT`: Tool output (PostToolUse only)

**Security Note:** Hooks run with full user permissions. Always validate inputs and use absolute paths.
