# 📋 IntelForge Codebase Summary

## 🏗️ Project Structure Overview

```
intelforge/
├── 📄 README.MD                    # Project overview and philosophy
├── 🐍 phase_01_github.py          # GitHub scraping module (initial implementation)
├── ⚙️ config/
│   └── config.yaml                 # Centralized configuration
├── 📚 docs/
│   └── find_vs_build.md           # Decision framework for reuse vs rebuild
├── 🧠 knowledge_docs/             # Development process documentation
├── 🤖 prompts/                    # AI prompt templates
└── 🗂️ cline_docs/                # AI development guidance (this directory)
```

## 📁 Key Files Analysis

### Configuration Layer
**`config/config.yaml`** - Central configuration hub
- GitHub API settings and query parameters
- File path configurations for output and logging
- Feature flags (dry_run, logging, metadata inclusion)
- API key placeholders for secure credential management

### Development Guidance
**`docs/find_vs_build.md`** - Decision-making framework
- Systematic approach to evaluate existing tools vs custom development
- Reuse filters and anti-patterns identification
- Builds on "reuse over rebuild" philosophy

**`knowledge_docs/Reusable_Development_Checklist_for_Each_Module.md`** - Comprehensive development guide
- 10-point checklist covering reuse, modularity, resilience, AI-friendliness
- Emphasizes configuration over hardcoding
- Includes testability and regeneration-friendly design principles

**`prompts/find_tools_template.md`** - AI prompt template
- Standardized approach for tool discovery before building
- Structured format for evaluating existing solutions
- Integration with find_vs_build decision framework

### Implementation
**`phase_01_github.py`** - First implementation module
- GitHub repository scraping focused on trading strategies
- Currently implements basic structure for Bollinger Band strategy search
- Follows configured approach with dry-run capability

## 🎯 Code Philosophy Implementation

### Simplicity-First Architecture
- **Flat file structure** - Avoids over-modularization with src/ directories
- **One file per phase** - Self-contained modules with clear boundaries
- **Configuration-driven** - Behavior changes without code modifications
- **AI-regenerable** - Small, focused files that can be easily recreated

### Reuse-Over-Rebuild Patterns
- Systematic tool discovery before implementation
- Preference for wrapping existing libraries over custom logic
- Documentation emphasizes finding solutions before building
- Templates and checklists prevent reinvention

### AI-Cooperative Design
- Comprehensive documentation for context understanding
- Modular structure enabling targeted regeneration
- Clear interfaces and error handling for robust operation
- Prompt templates for consistent AI assistance

## 🔍 Current Implementation Status

### ✅ Completed Components
- **Project foundation** - README, philosophy, and decision frameworks
- **Configuration system** - YAML-based centralized settings
- **Development process** - Checklists and templates for consistent development
- **AI guidance framework** - Prompts and decision tools

### 🔄 In Progress
- **Phase 1 module** - GitHub scraping implementation
- **Documentation completion** - Final cline_docs setup

### 📋 Planned Development
- **Reddit scraping** (Phase 1) - PRAW-based r/algotrading extraction
- **Blog scraping** (Phase 3) - Medium/Dev.to content extraction  
- **PDF processing** (Phase 4) - Research paper analysis
- **AI summarization** (Phase 5) - Content cleaning and tagging
- **Knowledge curation** (Phase 6) - Obsidian vault management

## 🛠️ Technical Patterns

### Error Handling Strategy
- Comprehensive logging to vault/logs/ directory
- Dry-run mode for safe testing
- Graceful failure with detailed error messages
- Retry logic for API failures

### Data Flow Architecture
```
Source APIs → Scraping Modules → Raw Data → AI Processing → Markdown Output → Obsidian Vault
```

### File Naming Conventions
- **Modules**: `phase_XX_description.py` (sequential, descriptive)
- **Outputs**: `source_topic_YYYY-MM-DD.md` (timestamped, organized)
- **Logs**: `module_name.log` (clear traceability)
- **Configs**: Descriptive YAML with comments

## 🎯 Integration Points

### Obsidian Compatibility
- YAML frontmatter for metadata
- [[wikilink]] syntax for cross-references
- #tag system for categorization
- Structured folder hierarchy

### AI Service Integration
- OpenAI API for content summarization
- Claude API for content analysis
- Planned local LLM support (Ollama)
- Batch processing for cost efficiency

### External Tool Dependencies
- **PRAW** for Reddit API access
- **PyGitHub** for repository mining
- **requests/beautifulsoup4** for web scraping
- **PyPDF2** for document processing

## 🔐 Security & Privacy Model

### Local-First Approach
- All data stored locally in vault/ directory
- No cloud dependencies for core functionality
- Private repository with personal use focus
- API credentials in gitignored configuration

### Ethical Scraping Guidelines
- Respects robots.txt and terms of service
- Rate limiting to avoid service disruption
- Personal research use only (non-commercial)
- Public data sources with proper attribution

## 📈 Scalability Considerations

### Modular Expansion
- Each phase as independent module
- Clear interfaces for chaining operations
- Configuration-driven behavior modification
- AI-assisted module generation and maintenance

### Performance Optimization
- Incremental processing to avoid re-work
- Content hashing for duplicate detection
- Lazy loading and memory-conscious design
- Local GPU available for intensive processing (RTX 3060)