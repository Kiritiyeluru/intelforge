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
- Refer to `@guidance/core_essentials/find_vs_build.md` for decision framework
- **Check `@guidance/core_essentials/scraping_tools_recommendations.md` for vetted scraping tools and libraries**
- **NEW: Review `@analysis/repository_analysis/` for comprehensive GitHub repository analysis (13 repos, 65-2,747+ stars)**
- **✅ ENFORCED: Phase 2C successfully replaced 400+ line custom academic scraper with <200 lines using production frameworks**
- Wrap existing tools rather than reimplementing common functionality

### **🔍 Comprehensive Scraping Repository Analysis (2025)**

**Status**: **COMPLETE** - 40+ repositories analyzed with detailed evaluation and scoring
**Primary Analysis**: `@analysis/scraping_frameworks/comprehensive_repository_analysis.md`
**Research Archive**: `@analysis/scraping_frameworks/research_archive/`

#### **🏆 Top-Tier Recommendations (5/5 Stars) - Immediate Integration:**

1. **scrapy/scrapy** (52.4k stars) - Enterprise foundation, battle-tested
2. **adbar/trafilatura** (4.2k stars) - Best-in-class content extraction (F1: 0.945)
3. **scrapy-plugins/scrapy-playwright** (1.2k stars) - Superior JS handling
4. **ultrafunkamsterdam/nodriver** (2.7k stars) - Undetectable browser automation
5. **daijro/camoufox** (2.5k stars) - Maximum stealth capabilities
6. **D4Vinci/Scrapling** (5.4k stars) - High-performance adaptive scraping
7. **jannisborn/paperscraper** (381 stars) - Comprehensive academic research
8. **alirezamika/autoscraper** (6.8k stars) - Zero-config AI pattern learning
9. **jpjacobpadilla/Stealth-Requests** (268 stars) - Advanced anti-detection HTTP
10. **fhamborg/news-please** (2.3k stars) - Production-grade news crawling
11. **microsoft/playwright-python** (11.4k stars) - Enterprise browser automation

#### **🎯 Strategic Implementation Guide:**

**Phase 1: Core Foundation (Week 1-2)**
- **Primary**: scrapy + trafilatura + scrapy-playwright
- **Academic**: paperscraper + arxivscraper  
- **Anti-Detection**: Stealth-Requests for HTTP, nodriver for browser

**Phase 2: Intelligence Enhancement (Week 3-4)**
- **AI Pattern Learning**: AutoScraper for trading forums
- **News Intelligence**: news-please for financial news monitoring
- **Advanced Stealth**: Evaluate camoufox for maximum stealth needs

**Phase 3: Scale & Optimization (Week 5-6)**
- **Performance**: Scrapling for high-volume scraping
- **Specialized**: fundus for high-accuracy news extraction
- **Monitoring**: Implement detection analysis tools

#### **📈 Key Performance Metrics:**
- **Content Quality Leader**: trafilatura (F1: 0.945)
- **Speed Champion**: Scrapling (240x faster than BeautifulSoup)
- **Anti-Detection Best**: camoufox (71.5% CreepJS score)
- **Enterprise Standard**: Scrapy (52.4k stars, battle-tested)
- **Academic Coverage**: paperscraper (5 major databases)

#### **🎯 Integration Benefits for IntelForge:**
1. **Automated Intelligence**: 80% reduction in manual pattern maintenance
2. **Anti-Detection**: Access to previously blocked financial sites
3. **Quality Assurance**: Academic-grade extraction accuracy
4. **Comprehensive Coverage**: News, academic, forum, and blog content
5. **Performance**: 6x-240x speed improvements across different scenarios

**Research Sources**: Multi-platform deep research (Claude Code, ChatGPT, Perplexity)
**Analysis Confidence**: High - based on comprehensive GitHub analysis, performance benchmarks, and maintenance assessment

## Development Workflow

### Claude Code Hooks Integration

**7 Active Automation Hooks:**
- **Bash Command Logging** (PreToolUse): Logs all shell commands to `~/.claude/bash-command-log.txt`
- **Phase File Validation** (PreToolUse): Enforces `phase_XX_name.py` naming convention
- **Knowledge Auto-Organization** (PostToolUse): Auto-triggers article organizer for `intake/` files
- **Scraping Session Logger** (PostToolUse): Tracks scraping activities and performance metrics
- **Dependency Intelligence** (PostToolUse): Auto-tracks imports and updates requirements
- **Module Structure Guardian** (PostToolUse): Enforces consistent code patterns
- **Config Change Propagator** (PostToolUse): Propagates config changes automatically

**Configuration**: Located in `.claude/settings.json` → `"hooks"` section. Modify via `/hooks` command or direct file editing.

### Before Starting Any Module

1. **Research existing solutions** using find_tools_template.md
2. **Follow development checklist** from `@knowledge_docs/Reusable_Development_Checklist_for_Each_Module.md`
3. **Check current roadmap** in `@session_docs/PROJECT_STATUS.md`
4. **Update current task** in `@session_docs/PROJECT_STATUS.md`
5. **Review maintenance strategy** in `@guidance/operations/claude_code_hooks_maintenance_plan.md` for long-term code sustainability

### Session Management (CRITICAL - Always Follow)

**🚨 MANDATORY FIRST ACTION - Before every session:**
- **READ `session_docs/PROJECT_STATUS.md` FIRST** - THIS IS THE ONLY AUTHORITATIVE PROJECT STATUS
- Check `session_docs/SESSION_HANDOVER.md` for session-specific technical notes
- Follow established session management protocols

**📍 AUTHORITATIVE PROJECT STATUS LOCATION:**
`/home/kiriti/alpha_projects/intelforge/session_docs/PROJECT_STATUS.md`

**📋 STREAMLINED DOCUMENTATION STRUCTURE:**
- `session_docs/PROJECT_STATUS.md` - Comprehensive project status and roadmap
- `session_docs/SESSION_HANDOVER.md` - Session-specific technical handover notes
- `session_docs/README.md` - Documentation overview

**During development:**
- Update `session_docs/PROJECT_STATUS.md` with progress and current focus
- Log decisions in `guidance/project_intelligence/decision_log.md` with rationale
- Document solutions in `guidance/core_essentials/troubleshooting_guide.md`
- Track config changes in `guidance/operations/config_changelog.md`

**End of every session (MANDATORY):**
- Update `session_docs/PROJECT_STATUS.md` with accomplishments and next priorities
- Create/update `session_docs/SESSION_HANDOVER.md` with technical details
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
├── session_docs/          # Session management & status tracking
│   ├── PROJECT_STATUS.md  # Comprehensive project status and roadmap
│   ├── SESSION_HANDOVER.md # Session-specific technical handover notes
│   └── README.md          # Documentation overview
├── scrapers/             # All scraping modules
│   ├── phase_01_reddit.py # Reddit scraper implementation
│   ├── phase_02_github.py # GitHub scraper implementation
│   ├── reddit_scraper.py  # Unified Reddit scraper
│   ├── github_scraper.py  # Unified GitHub scraper
│   └── web_scraper.py     # Web/blog scraper
├── scripts/              # Utility scripts & processing
│   ├── scraping_base.py   # Base scraping framework
│   ├── scraping_scheduler.py # Automation scheduler
│   ├── data_organizer.py  # Data organization utilities
│   ├── phase_07_article_organizer.py # Auto-categorization
│   └── phase_08_ai_processor.py # AI semantic search
├── rust/                 # Rust performance optimization tools
│   ├── README.md          # Rust implementation guide
│   ├── rust_tools_recommended.md # Master Rust recommendations
│   └── scraping_tools_recommendations.md # Performance benchmarks
├── analysis/             # Repository analysis and strategic intelligence
│   └── repository_analysis/ # Comprehensive GitHub repository analysis
│       ├── 01_Crawl4AI_Analysis.md # Trending #1 LLM-friendly scraper
│       ├── 02_twscrape_Analysis.md # X/Twitter GraphQL API scraper
│       ├── 03_LinkedIn_Profile_Scraper_Analysis.md # Professional data
│       ├── 04_Toutatis_OSINT_Analysis.md # Instagram intelligence
│       └── 05_Repository_Analysis_Summary.md # Strategic assessment
├── config/config.yaml    # Centralized configuration
├── vault/
│   ├── notes/            # Scraped content (Obsidian format)
│   └── logs/             # Operation logs
├── knowledge_management/ # Article organization system
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

### Web Scraping (see `@rust/scraping_tools_recommendations.md` for complete details)

- **Static Content**: selectolax + httpx (high-performance)
- **Dynamic Content**: Playwright (modern, reliable)
- **Framework**: Scrapy (enterprise-scale)
- **Anti-Detection**: scrapy-fake-useragent + proxy rotation
- **Performance Stack**: ✅ Rust tools installed with proven 40-132x performance improvements

### Rust Performance Environment (✅ COMPLETE)

- **Package Management**: uv (40x faster than pip - proven)
- **CLI Tools**: ripgrep (132x faster), fd, bat, exa, bottom
- **Development**: rustc 1.88.0, cargo 1.88.0
- **Dependencies**: selectolax, polars, httpx, playwright via pyproject.toml
- **Testing**: `scripts/rust_performance_test.py` with verified benchmarks

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

## Current Project Status

**Project Status:** Phase 2C Complete → **Pre-Built Framework Integration Achieved**  
**Current Phase:** Phase 3 Ready - Anti-Detection & Performance Optimization

### 🎯 **LATEST ACHIEVEMENT: Phase 2C - Pre-Built Framework Integration Complete (2025)**
- **Strategic Pivot**: Replaced custom academic scraper (400+ lines) with direct usage of production frameworks
- **Academic Research**: Implemented `scripts/arxiv_simple.py` using `lukasschwab/arxiv.py` (1.3k stars, official API)
- **Multi-Database**: Implemented `scripts/academic_research.py` using `jannisborn/paperscraper` (381 stars, 5 databases)
- **Code Reduction**: 400+ custom lines → <200 wrapper lines with superior reliability
- **Philosophy Enforcement**: Perfect adherence to "reuse-over-rebuild" principle
- **Maintenance**: Framework updates now handled by original maintainers
- **Production Ready**: Academic research tools operational with Obsidian-compatible output

### ✅ **COMPLETED & OPERATIONAL**
- **Unified Scraping Framework** - Complete modular scraping system ✅ COMPLETE
- **Phase 1: Reddit Scraping** - PRAW-based extraction from trading subreddits ✅ COMPLETE  
- **Phase 2: GitHub Mining** - PyGitHub-based repository and documentation extraction ✅ COMPLETE
- **Phase 2A-2C: Enterprise Framework Migration** - Scrapy + trafilatura + pre-built academic tools ✅ COMPLETE
- **Phase 3: Web Scraping** - httpx + selectolax for blogs and articles ✅ COMPLETE
- **Phase 7: Knowledge Management** - Auto-organize articles with AI-ready processing pipeline ✅ COMPLETE
- **Phase 8: AI Processing** - Semantic search with embeddings and vector database ✅ COMPLETE
- **Rust Performance Stack** - 40-132x performance improvements with proven benchmarks ✅ COMPLETE

### 🚀 **CURRENT FOCUS: Phase 3 Ready - Anti-Detection & Performance**
**Pre-Built Framework Integration:** ✅ COMPLETE (Academic research tools operational)  
**Next:** Anti-detection capabilities with botasaurus framework  
**Priority:** READY - Install and configure botasaurus (5/5 stars) for advanced stealth  
**Secondary:** Performance optimization and concurrent processing
**Advanced:** Integration testing with protected financial sites

### 📋 **Phase 3 Implementation Plan (Next Session)**
1. **Anti-Detection Capabilities** (IMMEDIATE PRIORITY)
   - Install botasaurus framework (5/5 stars, sophisticated anti-bot)
   - Configure Cloudflare/Datadome/Turnstile bypass capabilities
   - Test against protected financial sites (Finviz, Yahoo Finance)
   - Implement human-like behavior simulation

2. **Performance Optimization** (HIGH PRIORITY)
   - Configure concurrent processing for academic research tools
   - Optimize Scrapy framework for high-volume operations
   - Validate 6x-240x performance improvements
   - Test pipeline integration with existing AI processing

3. **Integration Testing** (MEDIUM PRIORITY)
   - Test academic research tools with real queries
   - Validate anti-detection against modern systems
   - Performance benchmarking and optimization
   - Documentation of operational procedures

## New Scraping Framework Components

**Base Framework** (`scraping_base.py`):
- Unified base class with rate limiting, user-agent rotation, retry logic
- SQLite storage + Obsidian-compatible markdown output
- Robots.txt compliance and basic anti-detection
- Environment variable configuration overrides

**Specialized Scrapers**:
- `reddit_scraper.py` - PRAW + base framework for r/algotrading, r/investing
- `github_scraper.py` - PyGitHub + base framework for algorithm repositories  
- `web_scraper.py` - httpx + selectolax for Medium, Dev.to, blogs

**Automation & Organization**:
- `scraping_scheduler.py` - Python schedule library for automated runs
- `data_organizer.py` - Deduplication, organization, and analytics utilities
- `requirements_scraping.txt` - All dependencies for the framework

## Development Checklist Reference

Use `@guidance/development/Reusable_Development_Checklist_for_Each_Module.md` for every module:

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

**Current Status:** 59 articles organized, AI search operational, 4MB vector database

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

### MCP Server Installation Protocol

**CRITICAL:** After installing each MCP server, follow this comprehensive testing and documentation protocol:

#### 🔍 **Post-Installation Testing Checklist**

1. **Functionality Verification**
   ```bash
   # Test server startup
   claude mcp list
   
   # Test basic functionality
   # (Send test query to verify server responds)
   
   # Check logs for errors
   tail -f ~/.claude/logs/mcp_servers.log
   ```

2. **Performance Assessment**
   ```bash
   # Monitor resource usage during testing
   htop -p $(pgrep -f "mcp-server")
   
   # Test response times with sample queries
   time <test-command>
   
   # Check memory consumption
   ps aux | grep mcp-server | awk '{print $4, $11}'
   ```

3. **Integration Testing**
   - Test with existing IntelForge workflows
   - Verify compatibility with current scraping pipeline
   - Test chunking/processing capabilities if applicable
   - Validate output format (Markdown, JSON, etc.)

#### 📋 **Installation Documentation Template**

**MANDATORY:** Create detailed installation documentation for each server in `mcp_servers/docs/installations/`:

**File:** `mcp_servers/docs/installations/[server-name]_installation.md`

```markdown
# [Server Name] Installation Documentation

## Installation Details
- **Installation Date**: [Date]
- **Installation Method**: [git clone / npm install / pip install]
- **Dependencies**: [List all dependencies]
- **Configuration Location**: [Path to config files]

## Choices Made & Rationale
- **Transport Type**: [stdio/http/sse] - Why this choice?
- **Storage Location**: [Path] - Why this directory structure?
- **API Keys**: [Required keys] - How obtained and stored
- **Performance Settings**: [Key settings] - Rationale for values

## Installation Process
1. **Preparation Steps**
   - Dependencies installed
   - Directory structure created
   - API keys obtained

2. **Installation Commands**
   ```bash
   [Exact commands used]
   ```

3. **Configuration Steps**
   ```bash
   [Configuration commands and file edits]
   ```

4. **Testing & Verification**
   ```bash
   [Commands used to verify installation]
   ```

## Lessons Learned
- **Challenges Encountered**: [Issues faced during installation]
- **Solutions Applied**: [How challenges were resolved]
- **Time Investment**: [Actual time spent on installation]
- **Performance Observations**: [Initial performance notes]

## Integration Notes
- **IntelForge Compatibility**: [How it integrates with existing workflow]
- **Optimal Use Cases**: [Best scenarios for this server]
- **Limitations Discovered**: [Any limitations or constraints]
- **Future Optimization**: [Potential improvements identified]

## Configuration Files
- **Claude Code Config**: [Exact configuration added]
- **Server Settings**: [Custom settings applied]
- **Environment Variables**: [Required env vars and values]

## Troubleshooting Guide
- **Common Issues**: [Problems likely to occur]
- **Solutions**: [How to resolve each issue]
- **Debug Commands**: [Useful debugging commands]

## Performance Metrics
- **Startup Time**: [Seconds to initialize]
- **Memory Usage**: [RAM consumption]
- **Response Time**: [Average query response time]
- **Throughput**: [Requests per minute if applicable]

## Maintenance Requirements
- **Update Process**: [How to update this server]
- **Backup Needs**: [What needs backing up]
- **Monitoring**: [What to monitor for health]
```

#### 🎯 **Quality Standards**

**Each installation must meet these criteria:**
- ✅ Server starts successfully and responds to test queries
- ✅ Integration with Claude Code verified
- ✅ Performance within acceptable ranges (startup <30s, response <5s)
- ✅ Complete documentation created with all sections filled
- ✅ Troubleshooting guide tested with common issues
- ✅ Integration with existing IntelForge workflow verified

#### 📊 **Post-Installation Actions**

1. **Update Master Documentation**
   - Add server to `mcp_servers/README.md` status table
   - Update installation scripts if needed
   - Add to recommended configurations

2. **Integration Testing**
   - Test with existing scraping workflows
   - Verify content processing pipeline if applicable
   - Update knowledge management system if relevant

3. **Performance Optimization**
   - Tune configuration settings based on testing
   - Document optimal settings in server_configs.yaml
   - Set up monitoring if needed

**ENFORCEMENT:** No MCP server installation is considered complete until full documentation and testing protocol is finished. This ensures maintainable, reliable infrastructure for IntelForge.

## Claude Code Hooks Configuration

**Current Status:** 7 automation hooks active across 6 functional categories

**Active Hooks:**
- **Bash Command Logging**: Logs all shell commands for debugging (PreToolUse)
- **Phase File Validation**: Enforces naming conventions (PreToolUse)
- **Knowledge Auto-Organization**: Auto-triggers article organizer (PostToolUse)
- **Scraping Session Logger**: Tracks scraping activities and performance metrics (PostToolUse)
- **Dependency Intelligence**: Auto-tracks imports and updates requirements (PostToolUse)  
- **Module Structure Guardian**: Enforces consistent code patterns (PostToolUse)
- **Config Change Propagator**: Propagates config changes automatically (PostToolUse)

**🎯 Next-Level Automation:** See `@guidance/operations/claude_code_hooks_maintenance_plan.md` for comprehensive long-term maintenance strategy including:
- **Dependency Intelligence**: Auto-track imports and update requirements
- **Module Structure Guardian**: Enforce consistent code patterns
- **Documentation Sync Engine**: Keep docs automatically updated
- **Refactoring Impact Analyzer**: Safe refactoring with change analysis

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
