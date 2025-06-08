# 🧠 IntelForge Project Roadmap

## 🎯 Mission
Build a personal AI-powered knowledge extraction system for web scraping and intelligence gathering, focused on algorithmic trading and technical strategy mining.

## 🏗️ Architecture Philosophy
- **Simplicity First**: "We are building a lab notebook, not a SaaS platform"
- **Reuse Over Rebuild**: Use existing libraries/tools, wrap don't reinvent
- **AI-Cooperative**: Built with AI assistance, maintainable by solo developer
- **Modular Design**: One file per phase, flat structure

## 📋 Development Phases

### ✅ Phase 0: Foundation (COMPLETED)
- [x] Project structure with config.yaml
- [x] Documentation framework with session handovers
- [x] Development checklists and templates
- [x] GitHub Projects automation setup
- [x] Comprehensive session management system
- [x] Decision tracking and troubleshooting guides
- [x] Essential .claude docs creation

### 🔄 Phase 1: Reddit Scraping (CURRENT - NEXT SESSION)
**Goal**: Extract algorithmic trading strategies and discussions from Reddit
**Estimated Effort**: 2-3 coding sessions
**Dependencies**: Reddit API credentials, PRAW library research

#### Implementation Steps:
1. **Research Phase** (30-60 minutes)
   - [ ] Use `prompts/find_tools_template.md` to research Reddit scraping
   - [ ] Compare PRAW vs alternatives (requests + Reddit API)
   - [ ] Document decision in `docs/decision_log.md`

2. **Configuration Setup** (15-30 minutes)
   - [ ] Create Reddit API app at reddit.com/prefs/apps
   - [ ] Add Reddit section to `config/config.yaml`
   - [ ] Document in `docs/config_changelog.md`

3. **Core Implementation** (1-2 hours)
   - [ ] Implement `phase_01_reddit.py` using PRAW + Reddit2Text combination
   - [ ] Install dependencies: `pip install praw reddit2text`
   - [ ] Target subreddits: r/algotrading, r/SecurityAnalysis, r/investing
   - [ ] Extract: posts, comments, code snippets, author metadata
   - [ ] Use Reddit2Text for clean content formatting
   - [ ] Rate limiting: Built into PRAW (no custom delays needed)
   - [ ] Include --dry-run mode for testing

4. **Output Format** (30 minutes)
   - [ ] Generate Obsidian-compatible markdown
   - [ ] YAML frontmatter: source, date, tags, content_hash, author
   - [ ] Save to `vault/notes/reddit/`
   - [ ] Log operations to `vault/logs/reddit_YYYYMMDD.log`

5. **Testing & Validation** (30 minutes)
   - [ ] Test with --dry-run on small subreddit
   - [ ] Verify output format in Obsidian
   - [ ] Handle edge cases (deleted posts, private subreddits)
   - [ ] Update session handover files

**Success Criteria**:
- Successfully extracts 10+ posts from r/algotrading
- Generates valid Obsidian markdown with proper frontmatter
- Handles rate limits gracefully
- Includes comprehensive logging and error handling

### 🔄 Phase 2: GitHub Mining (FUTURE)
**Goal**: Mine algorithmic trading repositories for strategies and code patterns
**Estimated Effort**: 2-3 coding sessions
**Dependencies**: GitHub API token, PyGitHub library research

#### Implementation Approach:
1. **Repository Discovery**
   - Search GitHub for keywords: "algorithmic trading", "quantitative finance", "backtesting"
   - Filter: Python repos, >10 stars, active in last year
   - Target popular libraries: zipline, backtrader, freqtrade

2. **Content Extraction**
   - README files for strategy descriptions
   - Python files for implementation patterns
   - Documentation for usage examples
   - Issues/discussions for common problems

3. **Quality Filtering**
   - Skip abandoned repositories (no commits in 6+ months)
   - Prioritize repos with comprehensive documentation
   - Focus on educational/tutorial repositories

**Simplicity Focus**: Single file, minimal dependencies, clear extraction patterns

### 🔄 Phase 3: Blog/Article Scraping
- [ ] Implement `phase_03_blogs.py`
- [ ] Target: Medium, Dev.to, Towards Data Science
- [ ] Extract: articles on quant finance, trading algorithms
- [ ] Clean and summarize using AI

### 🔄 Phase 4: PDF/Research Papers
- [ ] Implement `phase_04_pdfs.py`
- [ ] Target: arXiv, SSRN, academic papers
- [ ] Extract: text, figures, key findings
- [ ] AI-powered summarization and tagging

### 🔄 Phase 5: AI Summarization Hub
- [ ] Implement `phase_05_summarizer.py`
- [ ] Integration: OpenAI + Claude APIs
- [ ] Features: content categorization, duplicate detection
- [ ] Output: cleaned, tagged, interconnected notes

### 🔄 Phase 6: Knowledge Curation
- [ ] Implement `phase_06_curator.py`
- [ ] Obsidian vault management
- [ ] Automated backlinking and tagging
- [ ] Content organization by topic/source

## 🎯 Success Metrics
- Everything lives in 1-2 files per phase
- Total repo understandable in <5 minutes
- Fully manageable by solo user with AI help
- Builds personal research brain, not commercial product

## 🛠️ Tech Stack
- **Language**: Python 3.8+
- **APIs**: Reddit (PRAW), GitHub (PyGitHub), OpenAI, Anthropic Claude
- **Storage**: Local markdown files
- **Organization**: Obsidian-compatible vault structure
- **Environment**: Ubuntu Linux, local execution

## 📁 File Organization
```
intelforge/
├── phase_01_reddit.py      # Reddit scraping module
├── phase_02_github.py      # GitHub mining module  
├── phase_03_blogs.py       # Blog/article scraping
├── phase_04_pdfs.py        # PDF processing
├── phase_05_summarizer.py  # AI summarization
├── phase_06_curator.py     # Knowledge organization
├── config/
│   └── config.yaml         # Centralized configuration
├── vault/
│   ├── notes/              # Scraped content (markdown)
│   └── logs/               # Operation logs
├── cline_docs/             # AI development guidance
├── docs/                   # Decision-making guides
├── prompts/                # Reusable AI prompts
└── knowledge_docs/         # Development checklists
```

## 🎯 Immediate Next Steps (Next Session)

### Phase 1 Preparation Checklist:
1. **Research** (MUST DO FIRST)
   - [ ] Read `prompts/find_tools_template.md`
   - [ ] Research PRAW library documentation
   - [ ] Check existing Reddit scraping patterns
   - [ ] Document findings in `docs/decision_log.md`

2. **Environment Setup**
   - [ ] Create Reddit API application
   - [ ] Set up config.yaml with Reddit section
   - [ ] Create vault/notes/reddit/ directory
   - [ ] Test basic PRAW connection

3. **Session Management**
   - [ ] Update `current_task.md` with Phase 1 start
   - [ ] Follow `session_checklist.md` workflow
   - [ ] Log decisions and progress continuously

## 🚀 Development Principles for All Phases

### Simplicity-First Guidelines:
- **One file per phase** - no complex module hierarchies
- **Functions over classes** - unless classes significantly simplify
- **Configuration-driven** - externalize all settings to config.yaml
- **Fail gracefully** - comprehensive error handling and logging
- **Test early** - include --dry-run mode in every module
- **Document decisions** - capture rationale in decision_log.md

### Session Quality Standards:
- Each coding session should complete a logical unit of work
- All decisions documented with rationale
- Session handover files updated before ending
- Code tested and working before commit
- Next session priorities clearly defined

## 🔮 Future Enhancements (Post Phase 6)
- Local LLM integration (Ollama)
- Obsidian plugin development
- Automated periodic scraping (cron jobs)
- Conversational query interface
- Advanced duplicate detection
- Multi-format export capabilities

## 📊 Progress Tracking

**Current Status**: Phase 0 Complete, Phase 1 Ready to Start
**Next Milestone**: Working Reddit scraper with 10+ extracted posts
**Time Investment**: ~3-4 hours for complete Phase 1 implementation
**Success Metric**: Personal knowledge base starts accumulating content