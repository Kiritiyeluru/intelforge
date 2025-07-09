Here is the updated `README.md` for **IntelForge**, now with your **Simplicity Philosophy** seamlessly baked in. This version clearly communicates your purpose, prevents future over-engineering, and sets expectations for anyone (including AI) who reads or contributes to the code.

---

```markdown
# 🧠 IntelForge

_A personal AI-powered knowledge extraction system for web scraping and intelligence gathering._

---

## 🚀 Overview

**IntelForge** is a solo-developed, AI-assisted project designed to help me build a long-term, modular agent that scrapes and organizes valuable knowledge from public online sources — especially in the fields of **algorithmic trading**, **technical strategy mining**, and **financial research**.

Rather than reinventing common tools, this system wraps reliable scraping methods with minimal logic and intelligent automation — all built using AI tools like Claude or ChatGPT.

> ⚠️ This project is for **personal, non-commercial use only** and respects site TOS and robots.txt wherever applicable.

---

## 🎯 Core Objectives

### ✅ What I'm Building

- A **simple, AI-cooperative pipeline** that can:
  - Scrape content from target sources (GitHub, Reddit, Medium, PDFs, etc.)
  - Extract and summarize relevant ideas (e.g. strategies, indicators, backtests)
  - Store those insights as markdown notes for long-term use

### 💡 Why I'm Building It

- I build **alone**, from scratch, with **no formal coding background**
- I rely on **AI** to help me write, fix, and evolve the code
- I need a system that is:
  - 🧠 *Understandable by a non-CS user*
  - 🧱 *Modular and AI-regenerable*
  - 🧹 *Simple enough to maintain over years*

---

## 🧘‍♂️ Simplicity-First Development Philosophy

> “We are building a lab notebook, not a SaaS platform.”
| ❌ Don’t Use                | ✅ Use Instead                                      |
| -------------------------- | -------------------------------------------------- |
| Rebuild tools from scratch | 📦 Use trusted libraries or wrap open-source tools |
| Custom academic scrapers   | 🎓 Direct APIs: arxiv.py (1.3k⭐), paperscraper (381⭐) |
| Complex integrations       | 🔧 Simple wrappers: <200 lines vs 400+ custom code |

### 🧠 See Also:
- [♻️ Find vs Build Checklist](guidance/core_essentials/find_vs_build.md)
- [🤖 AI Prompt Template – Tool Discovery](prompts/find_tools_template.md)


## ♻️ Reuse Over Rebuild

> “If someone smarter has already built it — I’ll use it.”

IntelForge is grounded in the principle of **reusing existing libraries, tools, and open-source implementations** wherever possible. The purpose of this system is not to reinvent common scraping, summarization, or backtesting logic — it is to:
- Identify and **wrap** trusted tools
- Use AI to glue them together intelligently
- Avoid building brittle code for problems that are already solved

### ✅ Reuse Checklist for Every Phase:
- [ ] Did I search GitHub / PyPI / Reddit / arXiv before writing any custom logic?
- [ ] Is this already available as a library or CLI tool?
- [ ] Can I wrap this in a function instead of building from scratch?
- [ ] Would future AI agents benefit more from a known tool than new code?

When in doubt: **Search, evaluate, wrap — don’t rebuild.**

### 🎯 **Phase 2C Success Story** *(January 2025)*
**Challenge**: Built 400+ line custom academic scraper, violating reuse-over-rebuild principle  
**Solution**: Replaced with direct usage of production frameworks:
- `scripts/arxiv_simple.py` - Uses `lukasschwab/arxiv.py` (1.3k⭐, official API)
- `scripts/academic_research.py` - Uses `jannisborn/paperscraper` (381⭐, 5 databases)
- **Result**: <200 wrapper lines vs 400+ custom code, superior reliability

### ❌ Avoiding Unnecessary Complexity

| ❌ Don’t Use | ✅ Use Instead |
|-------------|----------------|
| `src/`, `lib/`, abstract modules | Flat script layout (1 file per phase) |
| Custom classes for everything | Named functions in a script |
| Over-abstracted configs | One `config.py` or `config.yaml` |
| Full test frameworks | Manual tests + `--dry-run` mode |
| Framework-based structure | Readable, small AI-friendly scripts |

### 🧭 Design Check Before Adding Anything:
- Would I understand this in 3 months?
- Can this live in one file instead of three?
- Would this make AI-generated fixes harder?
- Is it adding value or just structure?

If the answer is no — **keep it simple**.

---

## 📦 Planned Architecture (Phased)

| Phase | Description |
|-------|-------------|
| `phase_01_github.py` | Scrape GitHub repos (e.g., for strategy code) |
| `phase_02_reddit.py` | Extract Reddit threads/posts (e.g., r/algotrading) |
| `phase_03_blogs.py` | Scrape blog posts from Dev.to, Medium, etc. |
| `phase_04_pdfs.py` | Extract and summarize research papers and PDFs |
| `phase_05_summarizer.py` | Use GPT to auto-clean, tag, and summarize |
| `phase_06_curator.py` | Organize all outputs into markdown vault |
| `phase_07_article_organizer.py` | Auto-organize saved articles with AI-ready processing ✅ |
| `phase_08_ai_processor.py` | Semantic search with embeddings and vector database ✅ |

---

## 📁 Folder Structure

```
intelforge/
├── session_docs/            # Session management & status tracking
│   ├── CURRENT_PROJECT_PLAN.md # Comprehensive project status and current work
│   ├── session_checklist.md # Consistent workflow checklist
│   └── README.md           # Session management documentation
├── scrapers/               # All scraping modules
│   ├── phase_01_reddit.py  # Reddit scraper implementation
│   ├── phase_02_github.py  # GitHub scraper implementation
│   ├── reddit_scraper.py   # Unified Reddit scraper
│   ├── github_scraper.py   # Unified GitHub scraper
│   └── web_scraper.py      # Web/blog scraper
├── scripts/                # Utility scripts & processing
│   ├── scraping_base.py    # Base scraping framework
│   ├── scraping_scheduler.py # Automation scheduler
│   ├── data_organizer.py   # Data organization utilities
│   ├── phase_07_article_organizer.py # Auto-categorization
│   └── phase_08_ai_processor.py # AI semantic search
├── rust/                   # Rust performance optimization tools
│   ├── README.md           # Rust implementation guide and quick start
│   ├── rust_tools_recommended.md # Master Rust recommendations (uv, polars, CLI tools)
│   └── scraping_tools_recommendations.md # Performance benchmarks and technical roadmap
├── config/
│   └── config.yaml         # Centralized configuration
├── vault/
│   ├── notes/              # Saved markdown outputs
│   └── logs/               # Log files and error traces
├── knowledge_management/   # Article organization system
│   ├── intake/             # Drop folder for new articles
│   ├── articles/           # Auto-categorized articles
│   ├── docs/               # Project tracking & decisions
│   └── config/             # Categorization rules
├── prompts/
│   └── templates/          # Claude/GPT prompts for generation
├── guidance/               # Development guidance and documentation
│   ├── core_essentials/    # Find vs build, troubleshooting, tools
│   ├── development/        # Development checklists and processes
│   ├── operations/         # Config changes, maintenance plans
│   └── project_intelligence/ # Decision logs, dependency reports
└── README.md
```

---

## 🛠️ Tooling Principles

| Principle | What It Means |
|----------|----------------|
| 🔹 Flat, simple structure | Avoids overmodularization |
| 🔹 Clear prompt history | Everything AI-generated is saved |
| 🔹 Config-first design | Change behavior without editing code |
| 🔹 Test-friendly by design | Includes dry-run mode and test data |
| 🔹 Logging by default | Logs to markdown or plaintext logs |

## 🏗️ Optimized Technical Architecture

### **🚀 Advanced Scraping Repository Analysis (2024-2025)**

**Status:** Comprehensive analysis of 13 top GitHub repositories (65-2,747+ stars) completed
**Analysis Location:** [`analysis/repository_analysis/`](analysis/repository_analysis/)

### **🏆 Top-Tier Prebuilt Solutions**

#### **1. Crawl4AI** - ⭐⭐⭐⭐⭐ (HIGHEST PRIORITY)
- **Status**: Trending #1 GitHub repository (January 2025)
- **Purpose**: LLM-friendly web crawler designed for AI applications
- **Key Features**: 6x faster performance, real-time processing, AI-optimized output
- **Integration**: **IMMEDIATE** - Perfect match for IntelForge's AI-powered knowledge extraction
- **Analysis**: [`01_Crawl4AI_Analysis.md`](analysis/repository_analysis/01_Crawl4AI_Analysis.md)

#### **2. Specialized Intelligence Tools** - ⭐⭐⭐⭐⭐ (SPECIALIZED USE)
- **Toutatis** (2,747 stars) - Instagram OSINT intelligence gathering
- **twscrape** - X/Twitter GraphQL API scraper with multi-account management
- **LinkedIn Profile Scraper** (657 stars) - Professional data extraction with structured JSON output
- **Analysis Files**: [`02_twscrape_Analysis.md`](analysis/repository_analysis/02_twscrape_Analysis.md), [`03_LinkedIn_Profile_Scraper_Analysis.md`](analysis/repository_analysis/03_LinkedIn_Profile_Scraper_Analysis.md), [`04_Toutatis_OSINT_Analysis.md`](analysis/repository_analysis/04_Toutatis_OSINT_Analysis.md)

### **High-Performance Scraping Stack**

**AI-First Architecture (Based on Analysis):**
- **Crawl4AI** ⚡ - LLM-optimized crawler for RAG systems (6x faster)
- **selectolax** ⚡ - Ultra-fast HTML parsing (28x faster than BeautifulSoup)
- **httpx** ⚡ - HTTP/2 support + async capabilities for concurrent requests

**Dynamic Content (JavaScript-Heavy Sites):**
- **Playwright** ⚡ - Modern browser automation (35% faster than Selenium)
- **Patchright-Python** ⚡ - Undetected Playwright alternative (completely bypasses bot detection)

**Specialized Intelligence:**
- **PRAW** - Reddit API wrapper for r/algotrading, r/investing
- **PyGithub** - GitHub repository mining for algorithms
- **twscrape patterns** - Twitter GraphQL API techniques
- **OSINT frameworks** - Social media intelligence gathering

**AI Processing & Integration:**
- **sentence-transformers** + **faiss-cpu** - Local semantic search
- **Crawl4AI LLM integration** - Direct LLM-compatible output
- **numpy** - Numerical processing for embeddings

**Anti-Detection & Stealth (Research-Based):**
- **Patchright-Python** - Complete anti-detection for Cloudflare, Kasada, Akamai
- **scrapy-fake-useragent** - Dynamic user-agent rotation
- **Advanced proxy rotation** - 95-99% success rates for financial sites
- **Session management** - Cookie persistence and request throttling

**Data Processing:**
- **pandas** - Data cleaning and manipulation
- **polars** ⚡ - High-performance alternative (10-30x faster for large datasets)

### **🚀 High-Performance Computing Stack (✅ COMPLETE)**

### **🎯 Python 3.10 High-Performance Environment (Latest Achievement)**

**Status**: ✅ **PRODUCTION-READY** - Dual-environment system operational  
**Performance**: Institutional-grade financial computing capabilities achieved  
**Environment**: Python 3.10.18 via micromamba with seamless Python 3.12 fallback

#### **High-Performance Financial Tools (✅ OPERATIONAL)**
- **vectorbt (latest)** - Advanced backtesting framework: **794 days/second** processing
- **numba (latest)** - JIT compilation acceleration: **18.07x speedup** vs pure Python  
- **ta-lib (latest)** - Professional technical analysis: **9,047 indicators/second**
- **polars[all] (1.31.0)** - High-performance dataframes with full ecosystem
- **numpy-financial (1.0.0)** - Optimized financial calculations: **3.9M portfolios/second**

#### **Dual Environment Management**
```bash
# High-performance mode (default)
./run_intelforge.sh performance           # Python 3.10 benchmarks
./run_intelforge.sh backtest             # VectorBT backtesting

# Compatibility mode
./run_intelforge.sh --python 3.12 test  # Python 3.12 fallback
```

### **🚀 Rust Performance Stack (✅ INSTALLED & VERIFIED)**

**Package Management:**
- **uv** - 40x faster than pip (proven: 0.006s vs 0.24s)
- **micromamba** - Binary-based Python environment management (90-second setup)
- **pyproject.toml** - Modern dependency management

**CLI Tools:**
- **ripgrep** - 132x faster than grep (proven: 0.014s vs 1.86s)
- **fd** - Fast find replacement
- **bat** - Enhanced cat with syntax highlighting  
- **exa** - Better ls with colors
- **bottom** - Modern htop replacement

### **Performance Benchmarks (✅ VERIFIED)**
| Tool Comparison | Performance Gain | Status |
|-----------------|------------------|--------|
| **Numba JIT vs Pure Python** | **18.07x faster** (mathematical computations) | ✅ Production |
| **TA-Lib Technical Analysis** | **9,047 indicators/sec** (8 indicators, 10K points) | ✅ Production |
| **VectorBT Backtesting** | **794 days/sec** (2K days with transaction costs) | ✅ Production |
| **Financial Calculations** | **3.9M portfolios/sec** (risk metrics, optimization) | ✅ Production |
| ripgrep vs grep | **132.7x faster** (0.014s vs 1.86s) | ✅ Proven |
| uv vs pip | **40x faster** (0.006s vs 0.24s) | ✅ Proven |
| selectolax vs BeautifulSoup | **28x faster** (3.4s vs 95.4s for 100K operations) | ✅ Ready |
| polars vs pandas | **Variable performance** (test-dependent) | ✅ Ready |

### **Performance Test Suite**
```bash
# Comprehensive performance validation
./run_intelforge.sh performance

# Specific high-performance tool testing  
python test_python310_performance.py
```

### **High-Performance Integration Status**
- ✅ **Python 3.10.18** - High-performance environment via micromamba
- ✅ **vectorbt** - Production-ready backtesting (794 days/sec)
- ✅ **numba** - JIT compilation operational (18x speedup)
- ✅ **ta-lib** - Professional technical analysis (9K+ indicators/sec)
- ✅ **polars[all]** - Complete high-performance dataframe ecosystem
- ✅ **Dual environments** - Seamless switching between Python 3.10/3.12
- ✅ **Production validation** - 80% test success rate with institutional capabilities

### **Data Flow Architecture**
```
Financial Sources → selectolax/httpx → Raw Data → pandas/polars → AI Processing → Obsidian Vault
     ↓                ↓                   ↓           ↓              ↓
Playwright/Stealth → Scrapy Pipelines → SQLite → sentence-transformers → Markdown
```

### **Security & Privacy Model**
- **Local-first approach** - All data stored locally in vault/ directory
- **No cloud dependencies** for core functionality
- **API credentials** in gitignored configuration files
- **Ethical scraping** - Respects robots.txt and rate limits
- **Anti-detection layers** - Multi-proxy rotation and stealth techniques
- **Personal research use only** (non-commercial)

### **📋 Implementation Roadmap (Redesigned with Comprehensive Repository Analysis)**

**🔍 Repository Analysis Complete:** [`analysis/scraping_frameworks/comprehensive_repository_analysis.md`](analysis/scraping_frameworks/comprehensive_repository_analysis.md)
- **40+ repositories analyzed** with detailed evaluation and scoring (1-5 stars)
- **Strategic implementation plan** with 4-phase integration roadmap
- **Performance benchmarks** with verified 6x-240x speed improvements
- **Production readiness assessment** with maintenance status for each tool
- **Research Archive:** [`analysis/scraping_frameworks/research_archive/`](analysis/scraping_frameworks/research_archive/) - Complete multi-platform analysis

**Phase 2A: Core Foundation (Week 1-2) - IMMEDIATE PRIORITY**
- [ ] **Primary Framework**: Scrapy + trafilatura + scrapy-playwright integration
- [ ] **Academic Research**: paperscraper + arxivscraper for comprehensive literature extraction
- [ ] **Anti-Detection Foundation**: Stealth-Requests for HTTP, nodriver for browser automation
- [ ] **Performance Baseline**: Replace existing tools with 5-star recommended alternatives

**Phase 2B: Intelligence Enhancement (Week 3-4) - HIGH VALUE**
- [ ] **AI Pattern Learning**: AutoScraper integration for trading forums and consistent site structures
- [ ] **News Intelligence**: news-please deployment for financial news monitoring
- [ ] **Advanced Stealth**: camoufox evaluation for maximum stealth requirements
- [ ] **Quality Assurance**: fundus integration for high-accuracy news extraction

**Phase 2C: Scale & Optimization (Week 5-6) - PERFORMANCE**
- [ ] **High-Volume Processing**: Scrapling integration for 240x performance improvement
- [ ] **Specialized Intelligence**: Google News scraper for trend detection
- [ ] **Detection Analysis**: Implement monitoring using antiscraping-toolkit insights
- [ ] **Advanced Browser Automation**: zendriver + rebrowser-patches for enhanced stealth

**Phase 3: Advanced Capabilities - SPECIALIZED**
- [ ] **Modern Stack Migration**: Evaluate crawlee-python for new development
- [ ] **Maximum Stealth**: camoufox + botright deployment for sophisticated anti-bot systems
- [ ] **Specialized Platforms**: WordPress, Blogger, and platform-specific scrapers as needed
- [ ] **OSINT Research**: Evaluate legal framework for advanced intelligence tools

**Phase 4: Production Hardening - ENTERPRISE**
- [ ] **Enterprise Anti-Detection**: Implementation of research-validated stealth techniques
- [ ] **Advanced Proxy Management**: Professional proxy rotation with residential IPs
- [ ] **Containerization**: Docker deployment with optimized configurations
- [ ] **Compliance Framework**: Comprehensive ethical scraping and legal compliance system

---

## 🧪 Getting Started

1. **Clone and Setup**
   ```bash
   git clone <your-private-repo>
   cd intelforge
   pip install -r requirements_scraping.txt
   ```

2. **Configure API Keys**
   ```bash
   # Create config file
   cp config/config.yaml.example config/config.yaml
   # Add your API keys to config/config.yaml
   ```

3. **Test Scrapers**
   ```bash
   # Test Reddit scraper
   python scrapers/reddit_scraper.py --dry-run --limit 5
   
   # Test GitHub scraper  
   python scrapers/github_scraper.py --dry-run --limit 5
   
   # Test web scraper
   python scrapers/web_scraper.py --dry-run --limit 5
   ```

4. **AI Processing (Optional)**
   ```bash
   # Build semantic search database
   python scripts/phase_08_ai_processor.py --build
   
   # Search your collected content
   python scripts/phase_08_ai_processor.py --search "trading strategies"
   ```

5. **Output Locations**
   - ✅ **Scraped Notes**: `vault/notes/`
   - ✅ **Operation Logs**: `vault/logs/`
   - ✅ **Organized Articles**: `knowledge_management/articles/`

---

## 🔍 Success Criteria

| ✅ What Success Looks Like                                     |
| ------------------------------------------------------------- |
| Everything lives in 1–2 files per phase                       |
| Total repo is understandable in under 5 mins                  |
| Can be fully managed by solo user with AI help                |
| Doesn’t look or feel like a commercial codebase               |
| System builds toward a personal research brain, not a product |

---

## 🧠 Development Process

### AI-Cooperative Development
* All code written using AI (Claude Code), based on saved prompts in `/prompts/`
* Every script includes docstring, inline comments, and fallback logic
* Follow **10-point development checklist** in `/guidance/development/`
* Use versioned prompt files to track module creation and fixes

### Error Handling Strategy
- **Comprehensive logging** to `vault/logs/` directory
- **Dry-run mode** for safe testing before real execution
- **Graceful failure** with detailed error messages and recovery
- **Retry logic** with exponential backoff for API failures
- **Content hashing** for duplicate detection and prevention

### Module Structure Pattern
```python
#!/usr/bin/env python3
"""
Phase X: [Description]
Purpose: [One-line purpose]
Usage: python module.py [--dry-run] [--config config.yaml]
"""

import logging
from pathlib import Path
from scripts.scraping_base import BaseScraper

class CustomScraper(BaseScraper):
    def scrape_content(self):
        """Core scraping logic with error handling"""
        pass

if __name__ == "__main__":
    # CLI argument parsing and execution
```

---

## 🔒 Ethics & Legal Use

* No scraping behind paywalls or logins
* Only uses official APIs or public RSS where possible
* Designed for personal research and educational purposes only

---

## ✨ Future Ideas

* Local summarization using LLMs (Ollama, LM Studio)
* Obsidian plugin for summarizing vault content
* Periodic scraping jobs + auto-digests (cron + markdown)
* GPT-based chat agent for asking:

  > “What strategies have I collected that use Z-Score + SMA?”

---

## 🤝 Collaborators & Credits

This project is personal and private, but credits go to:

* Claude + GPT (AI pair-programmers)
* The open-source community that shares knowledge publicly
* Tools like Obsidian, PRAW, and PyGitHub

## 📚 Internal Docs & Reusable Tools

| File | Purpose |
|------|---------|
| [`guidance/core_essentials/find_vs_build.md`](guidance/core_essentials/find_vs_build.md) | Helps decide whether to build from scratch or wrap existing tools |
| [`prompts/find_tools_template.md`](prompts/find_tools_template.md) | Reusable prompt template for Claude/GPT to search for prebuilt tools before coding |
| [`guidance/development/Reusable_Development_Checklist_for_Each_Module.md`](guidance/development/Reusable_Development_Checklist_for_Each_Module.md) | End-to-end checklist for building each module with AI help |
| [`guidance/core_essentials/scraping_tools_recommendations.md`](guidance/core_essentials/scraping_tools_recommendations.md) | Comprehensive scraping tools analysis and recommendations for IntelForge |
| [`guidance/operations/claude_code_hooks_maintenance_plan.md`](guidance/operations/claude_code_hooks_maintenance_plan.md) | **Long-term maintenance strategy using Claude Code hooks for automated dependency tracking, pattern enforcement, and documentation sync** |
| [`scripts/phase_07_article_organizer.py`](scripts/phase_07_article_organizer.py) | Auto-organize saved articles with AI-ready processing |
| [`scripts/phase_08_ai_processor.py`](scripts/phase_08_ai_processor.py) | Semantic search with embeddings and vector database |

### 🔍 **Advanced Scraping Repository Analysis (NEW)**

| Analysis File | Repository | Stars | Priority |
|---------------|------------|-------|----------|
| [`analysis/repository_analysis/01_Crawl4AI_Analysis.md`](analysis/repository_analysis/01_Crawl4AI_Analysis.md) | Crawl4AI | Trending #1 | **IMMEDIATE** |
| [`analysis/repository_analysis/02_twscrape_Analysis.md`](analysis/repository_analysis/02_twscrape_Analysis.md) | twscrape | Active 2025 | **SPECIALIZED** |
| [`analysis/repository_analysis/03_LinkedIn_Profile_Scraper_Analysis.md`](analysis/repository_analysis/03_LinkedIn_Profile_Scraper_Analysis.md) | LinkedIn Scraper | 657 | **SPECIALIZED** |
| [`analysis/repository_analysis/04_Toutatis_OSINT_Analysis.md`](analysis/repository_analysis/04_Toutatis_OSINT_Analysis.md) | Toutatis | 2,747 | **OSINT** |
| [`analysis/repository_analysis/05_Repository_Analysis_Summary.md`](analysis/repository_analysis/05_Repository_Analysis_Summary.md) | Summary Report | 13 repos | **STRATEGIC** |

**Analysis Scope:** Comprehensive evaluation of 13 top GitHub repositories (65-2,747+ stars) for advanced web scraping, including features, weaknesses, integration recommendations, and strategic implementation guidance.

## 🗂️ Knowledge Management System

**Current Status:** Phases 7 & 8 operational with 59 articles organized + AI search

## 🔌 MCP Server Integration

**Current Status:** Production-ready MCP ecosystem with 25+ servers available

IntelForge features a comprehensive Model Context Protocol (MCP) server infrastructure for enhanced AI capabilities:

### ✅ Core Active Servers

| Server | Type | Status | Purpose |
|--------|------|--------|---------|
| **GitHub** | Remote HTTP | ✅ Operational | Repository management, notifications, issues, PRs |
| **Filesystem** | Local | ✅ Operational | File system operations within project |
| **Memory** | Local | ✅ Operational | Knowledge graph and memory management |

### 🕷️ IntelForge MCP Server Ecosystem

**📁 Complete Setup:** [`mcp_servers/`](mcp_servers/) - Organized MCP server management system

| Category | Servers Available | Installation |
|----------|------------------|--------------|
| **🕷️ Scraping & Crawling** | 25+ servers (Puppeteer, Firecrawl, Playwright, etc.) | `./scripts/install_scraping.sh` |
| **🚀 Productivity** | 6+ servers (Git, SQLite, Everything, etc.) | `./scripts/install_productivity.sh` |
| **🔍 Search & Discovery** | 8+ servers (Brave, Tavily, Kagi, Perplexity, etc.) | Interactive installer |
| **📊 Data Processing** | 5+ servers (SQLite, PostgreSQL, Memory, etc.) | `./scripts/install.sh` |

### 🎯 Key MCP Features

**Scraping Enhancement:**
- **Anti-Bot Protection** - Scrapling Fetch, Oxylabs enterprise proxies
- **Modern Automation** - Playwright, Puppeteer with stealth features  
- **Production Scale** - Firecrawl with rate limiting and PDF processing
- **Search Integration** - Brave Search, Tavily AI-powered discovery

**Development Productivity:**
- **Repository Management** - GitHub API integration, local Git operations
- **Data Storage** - SQLite databases, persistent memory graphs
- **File Operations** - Secure filesystem access with configurable permissions

**Installation & Management:**
- **Interactive Setup** - Menu-driven installation with custom options
- **Multiple Configurations** - Pre-configured templates for different use cases
- **Health Monitoring** - Status scripts and comprehensive troubleshooting
- **Easy Maintenance** - Update, backup, and recovery scripts

### 🚀 Quick Setup

```bash
# Navigate to MCP servers directory
cd mcp_servers/

# Interactive installation with menu options
./scripts/install.sh

# Or install specific categories
./scripts/install_scraping.sh     # Web scraping servers
./scripts/install_productivity.sh # Development servers

# Check installation status
./scripts/status.sh
```

**Configuration Templates:**
- `claude_desktop_complete.json` - Full server ecosystem
- `claude_desktop_scraping.json` - Scraping-focused setup  
- `claude_desktop_productivity.json` - Development-focused setup
- `claude_desktop_custom.json` - Custom installation options

### 📚 MCP Documentation & Resources

**Comprehensive Documentation:** All MCP server details, configurations, and troubleshooting available in [`mcp_servers/`](mcp_servers/)

**Quick Reference:**

- **Installation Guide**: [`mcp_servers/docs/installation.md`](mcp_servers/docs/installation.md)
- **Server Catalog**: [`mcp_servers/README.md`](mcp_servers/README.md) - 25+ servers categorized by use case
- **Troubleshooting**: [`mcp_servers/docs/troubleshooting.md`](mcp_servers/docs/troubleshooting.md)
- **Configuration Templates**: [`mcp_servers/config/`](mcp_servers/config/) - Ready-to-use Claude Desktop configs

**Management Commands:**

```bash
# Check all server status
./mcp_servers/scripts/status.sh

# Health check with resource monitoring  
./mcp_servers/scripts/health_check.sh

# Manage Claude Desktop servers
claude mcp list                    # List active servers
claude mcp get <server-name>       # Get server details
```

### 🎯 IntelForge MCP Integration Strategy

**Phase 1: GitHub Integration (Complete)**
- ✅ Repository scraping enhancement
- ✅ Automated issue tracking for project management
- ✅ PR-based knowledge contribution workflow

**Phase 2: Planned Extensions**
- **Linear MCP** (`https://mcp.linear.app/sse`) - Project management
- **Sentry MCP** (`https://mcp.sentry.io/sse`) - Error monitoring
- **Custom MCP Servers** - Domain-specific financial data APIs

**Technical Architecture:**
```
IntelForge → Claude Code → GitHub MCP Server → GitHub API
     ↓            ↓              ↓               ↓
Scraping → AI Processing → Repository Ops → External APIs
```

### 📚 MCP Documentation

For detailed MCP server setup and management:
- **Local Setup**: `docs/Run MCP Servers In Seconds With Docker.md`
- **Remote Servers**: Use vendor-managed endpoints for external services
- **Configuration**: `.claude/settings.json` → `"mcpServers"` section

**Security Note:** MCP servers provide powerful API access. Always verify endpoints and use secure authentication methods.

## 🪝 Claude Code Hooks Integration

**Current Status:** Phase 1 complete - 7 automation hooks active across 6 functional categories

IntelForge leverages Claude Code's advanced hook system for automated maintenance and development intelligence:

### ✅ Phase 1 Hooks - Critical Infrastructure

| Hook Type | Trigger | Purpose |
|-----------|---------|---------|
| **Scraping Session Logger** ⭐ | PostToolUse (Bash) | Automatically tracks all scraping activities, performance metrics, and session history |
| **Dependency Intelligence** ⭐ | PostToolUse (Python files) | Auto-tracks imports, generates requirements.txt, and maintains dependency reports |
| **Module Structure Guardian** ⭐ | PostToolUse (New Python files) | Enforces IntelForge patterns, validates compliance, and suggests improvements |
| **Config Change Propagator** ⭐ | PostToolUse (config.yaml) | Propagates config changes to .env.example, docs, and validates syntax |
| **Phase File Validation** | PreToolUse (Write/Edit) | Enforces `phase_XX_name.py` naming convention |
| **Knowledge Auto-Organization** | PostToolUse (Write) | Triggers article organizer when files added to `intake/` |

### 🎯 Phase 1 Benefits

- **Zero Manual Tracking**: All scraping sessions automatically logged with metrics
- **Dependency Intelligence**: Never forget imports or requirements again
- **Pattern Enforcement**: New modules automatically follow IntelForge conventions
- **Config Consistency**: Changes propagate automatically to related files
- **Complete Audit Trail**: All operations logged for debugging and analysis

### 📊 Generated Intelligence Files

| File | Purpose |
|------|---------|
| `.claude/scraping_history.json` | Complete scraping session history with performance metrics |
| `.claude/dependencies.json` | Live dependency map with usage tracking |
| `.claude/module_patterns.json` | IntelForge coding patterns and compliance data |
| `.claude/config_history.json` | Config change tracking and propagation history |
| `requirements_auto.txt` | Auto-generated requirements from dependency analysis |
| `guidance/project_intelligence/dependency_report.md` | Human-readable dependency and usage analysis |
| `guidance/project_intelligence/module_compliance_report.md` | Pattern compliance status and suggestions |
| `guidance/operations/config_changelog.md` | Detailed config change history |

### 🔧 Hook Configuration

Hooks are configured in `.claude/settings.json` and run automatically. Phase 1 implementation includes:

- **6 active hooks** covering critical development workflows
- **Automatic execution** on file changes and command runs
- **Intelligent filtering** to avoid false triggers
- **Error handling** with graceful fallbacks

**Configuration Location**: `.claude/settings.json` → `"hooks"` section

### 🚀 Future Phases

**Phase 2 (Planned)**: Documentation automation, session context maintenance
**Phase 3 (Planned)**: Advanced refactoring safety, knowledge base optimization

See [`guidance/operations/claude_code_hooks_maintenance_plan.md`](guidance/operations/claude_code_hooks_maintenance_plan.md) for complete strategy.

### Auto-Organization (Phase 7) ✅
**Workflow:**
1. Save new articles to `knowledge_management/intake/`
2. Run `python phase_07_article_organizer.py` to auto-categorize  
3. Articles moved to organized folders based on content analysis
4. Categories: claude_mcp, web_scraping, ai_workflows, productivity

**Commands:**
```bash
# Test organization (safe)
python phase_07_article_organizer.py --dry-run

# Organize articles once
python phase_07_article_organizer.py

# Watch continuously  
python phase_07_article_organizer.py --watch
```

### AI-Powered Semantic Search (Phase 8) ✅
**Setup:**
```bash
# Install dependencies
pip install sentence-transformers faiss-cpu numpy

# Build vector database (one-time)
python phase_08_ai_processor.py --build
```

**Search Commands:**
```bash
# Semantic search examples
python phase_08_ai_processor.py --search "MCP servers"
python phase_08_ai_processor.py --search "web scraping Python libraries"
python phase_08_ai_processor.py --search "Claude Code productivity tips"
```

**Technical Details:**
- 1,683 chunks processed from 59 articles
- 384-dimensional embeddings (sentence-transformers)
- FAISS vector database (4MB total)
- <1 second search time, 0.7-0.8+ similarity scores
- 100% local, no cloud dependencies

