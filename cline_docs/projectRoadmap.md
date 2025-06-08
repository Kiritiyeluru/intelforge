# 🧠 IntelForge Project Roadmap

## 🎯 Mission
Build a personal AI-powered knowledge extraction system for web scraping and intelligence gathering, focused on algorithmic trading and technical strategy mining.

## 🏗️ Architecture Philosophy
- **Simplicity First**: "We are building a lab notebook, not a SaaS platform"
- **Reuse Over Rebuild**: Use existing libraries/tools, wrap don't reinvent
- **AI-Cooperative**: Built with AI assistance, maintainable by solo developer
- **Modular Design**: One file per phase, flat structure

## 📋 Development Phases

### ✅ Phase 0: Foundation (CURRENT)
- [x] Project structure with config.yaml
- [x] Documentation framework
- [x] Development checklists and templates
- [ ] Essential .claude docs creation

### 🔄 Phase 1: Reddit Scraping (NEXT)
- [ ] Implement `phase_01_reddit.py` using PRAW
- [ ] Target: r/algotrading, r/SecurityAnalysis, r/investing
- [ ] Extract: posts, comments, code snippets
- [ ] Output: Obsidian-compatible markdown with metadata

### 🔄 Phase 2: GitHub Mining
- [ ] Implement `phase_02_github.py` using PyGitHub
- [ ] Search: trading strategies, indicators, backtesting repos
- [ ] Extract: README, code samples, documentation
- [ ] Filter: Python repos with >10 stars, recent activity

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

## 🔮 Future Enhancements
- Local LLM integration (Ollama)
- Obsidian plugin development
- Automated periodic scraping (cron jobs)
- Conversational query interface
- Advanced duplicate detection
- Multi-format export capabilities