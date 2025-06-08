# 🛠️ IntelForge Tech Stack

## 🎯 Core Philosophy
- **Reuse existing libraries** over custom implementation
- **Wrap reliable tools** rather than reinventing
- **AI-friendly architecture** for easy maintenance and regeneration
- **Local-first approach** for privacy and control

## 📦 Primary Dependencies

### Web Scraping & APIs
- **PRAW** - Reddit API wrapper (Phase 1)
- **PyGitHub** - GitHub API client (Phase 2)  
- **requests** - HTTP library for general web scraping
- **beautifulsoup4** - HTML parsing for blog content
- **feedparser** - RSS feed processing

### AI Integration
- **openai** - OpenAI API client (GPT-4 for summarization)
- **anthropic** - Claude API client (content analysis)
- **sentence-transformers** - Local embeddings for duplicate detection

### Data Processing
- **PyPDF2** or **pdfplumber** - PDF text extraction (Phase 4)
- **python-dateutil** - Date parsing and formatting
- **hashlib** (built-in) - Content hashing for deduplication
- **re** (built-in) - Regular expressions for text processing

### File Management
- **PyYAML** - Configuration file handling
- **pathlib** (built-in) - Modern path handling
- **json** (built-in) - Data serialization
- **logging** (built-in) - Error tracking and debugging

## 🏗️ Architecture Patterns

### Configuration Management
```yaml
# config/config.yaml structure
api_keys:
  reddit_client_id: "xxx"
  reddit_client_secret: "xxx" 
  github_token: "xxx"
  openai_api_key: "xxx"
  claude_api_key: "xxx"

paths:
  output_dir: "vault/notes/"
  log_file: "vault/logs/"
  
options:
  dry_run: true
  max_results: 10
  include_metadata: true
```

### Output Format (Obsidian-Compatible)
```markdown
---
source: reddit
subreddit: algotrading
author: username
date: 2025-06-08
tags: [strategy, bollinger-bands, python]
content_hash: sha256_hash
---

# Post Title

Content with [[wikilinks]] and #tags for Obsidian integration.
```

### Module Structure Template
```python
#!/usr/bin/env python3
"""
Phase X: [Description]
Purpose: [One-line purpose]
Usage: python phase_X_module.py [--dry-run] [--config config.yaml]
"""

import logging
import yaml
from pathlib import Path

def load_config(config_path="config/config.yaml"):
    """Load configuration with error handling"""
    
def setup_logging(log_file):
    """Initialize logging to file and console"""
    
def main_function(config):
    """Core logic with error handling and dry-run support"""
    
if __name__ == "__main__":
    # CLI argument parsing
    # Configuration loading
    # Main execution with error handling
```

## 🔧 Development Tools

### Code Quality
- **flake8** or **ruff** - Linting (if user prefers)
- **black** - Code formatting (if user prefers)
- Built-in **logging** - Error tracking and debugging

### Testing Strategy
- **Manual testing** with `--dry-run` mode
- **Mock data** for API testing without rate limits
- **Sample files** in `test_data/` directory
- No formal test framework (following simplicity principle)

### AI Development Tools
- **Saved prompts** in `/prompts/` directory
- **Development checklists** in `/knowledge_docs/`
- **Tool discovery templates** for finding existing solutions

## 💾 Data Storage

### Local File Structure
```
vault/
├── notes/
│   ├── reddit/
│   │   ├── algotrading_YYYY-MM-DD.md
│   │   └── investing_YYYY-MM-DD.md
│   ├── github/
│   │   ├── bollinger_strategies_YYYY-MM-DD.md
│   │   └── backtest_frameworks_YYYY-MM-DD.md
│   └── blogs/
│       ├── medium_quant_articles_YYYY-MM-DD.md
│       └── towards_datascience_YYYY-MM-DD.md
└── logs/
    ├── reddit_scraper.log
    ├── github_miner.log
    └── error_tracking.log
```

### Metadata Standards
- **YAML frontmatter** for structured metadata
- **Content hashing** for duplicate detection
- **Timestamp-based filenames** for versioning
- **Obsidian tags** for categorization

## 🔐 Security & Privacy

### API Key Management
- Store in `config/config.yaml` (gitignored)
- Environment variable fallback
- Never hardcode in source files

### Rate Limiting
- Built-in delays between API calls
- Respect robots.txt and terms of service
- Implement retry logic with exponential backoff

### Data Privacy
- Local-only storage (no cloud dependencies)
- Personal use only (no commercial scraping)
- Respect site terms of service

## 🚀 Performance Considerations

### Optimization Strategy
- **Lazy loading** - Only process what's needed
- **Caching** - Store API responses to avoid re-fetching
- **Batch processing** - Group API calls efficiently
- **Incremental updates** - Only fetch new content

### Resource Limits
- **GPU acceleration** available (RTX 3060) for local LLM processing
- **Memory-conscious** processing for large datasets
- **Disk space management** with automated cleanup options

## 🔄 Upgrade Path

### Phase 1: Simple Implementation
- Basic API calls and file writing
- Manual configuration and execution

### Phase 2: Enhanced Automation  
- Scheduled execution (cron jobs)
- Advanced duplicate detection
- Cross-reference linking

### Phase 3: Advanced Features
- Local LLM integration (Ollama)
- Real-time processing
- Advanced analytics and insights