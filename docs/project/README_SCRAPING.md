# IntelForge Scraping Framework

A simple, modular scraping framework for personal algorithmic trading research. Built with a simplicity-first philosophy for solo developers.

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements_scraping.txt

# Set up API credentials (optional but recommended)
cp config/config.yaml.example config/config.yaml
# Edit config.yaml with your API keys
```

### Basic Usage

```bash
# Reddit scraper - extract from trading subreddits
python reddit_scraper.py --dry-run --subreddit algotrading --limit 5

# GitHub scraper - find trading algorithm repositories  
python github_scraper.py --dry-run --query "algorithmic trading python" --limit 5

# Web scraper - extract articles from blogs
python web_scraper.py --dry-run --site medium.com --limit 3

# Run all scrapers once
python scraping_scheduler.py --once --test

# View scraped data statistics
python data_organizer.py --action stats
```

## 📁 Framework Components

### Core Files

- **`scraping_base.py`** - Unified base class with common functionality
- **`config/config.yaml`** - Centralized configuration for all scrapers
- **`requirements_scraping.txt`** - All required Python packages

### Scrapers

- **`reddit_scraper.py`** - PRAW-based Reddit scraper for trading subreddits
- **`github_scraper.py`** - PyGitHub-based repository and documentation extractor
- **`web_scraper.py`** - httpx + selectolax based web article scraper

### Utilities

- **`scraping_scheduler.py`** - Automated scheduling with Python schedule library
- **`data_organizer.py`** - Data management, deduplication, and analytics

## 🎯 Key Features

### Base Framework
- ✅ **Rate Limiting** - Respectful delays between requests
- ✅ **User-Agent Rotation** - Avoids basic bot detection
- ✅ **Retry Logic** - Automatic retry with exponential backoff
- ✅ **Robots.txt Compliance** - Respects site crawling policies
- ✅ **Duplicate Detection** - Content-based deduplication

### Storage & Output
- ✅ **SQLite Database** - Structured storage for querying
- ✅ **Markdown Files** - Obsidian-compatible with YAML frontmatter
- ✅ **Organized Structure** - Auto-organized by source and date

### Configuration
- ✅ **YAML-based** - Single config file for all settings
- ✅ **Environment Overrides** - Use environment variables for sensitive data
- ✅ **Dry-run Mode** - Test without saving data

## 📊 Data Organization

### Directory Structure
```
vault/
├── notes/
│   ├── reddit/        # Reddit posts and comments
│   ├── github/        # Repository documentation
│   └── web/           # Blog articles and news
├── logs/              # Scraper operation logs
└── scraped_data.db    # SQLite database
```

### Output Format
Each scraped item creates:
1. **Database entry** - Structured data in SQLite
2. **Markdown file** - Human-readable with metadata

Example markdown output:
```markdown
---
source: reddit
url: https://reddit.com/r/algotrading/...
title: "My Bollinger Bands Strategy"
date: 2025-07-04T10:30:00
content_hash: sha256...
tags: [algo-trading, research, reddit]
subreddit: algotrading
author: trader123
score: 45
---

# My Bollinger Bands Strategy

**Original Post:**
Here's my strategy for using Bollinger Bands...

**Top Comments:**
**experienced_trader** (score: 12):
Great strategy! I've been using similar approach...
```

## 🤖 Automation

### Scheduling Options

**Option 1: Python Scheduler (Recommended)**
```bash
# Run as daemon with built-in scheduling
python scraping_scheduler.py --daemon

# Generate crontab entries for system cron
python scraping_scheduler.py --crontab
```

**Option 2: Manual Cron Setup**
```bash
# Daily Reddit scraping at 9 AM
0 9 * * * cd /path/to/intelforge && python reddit_scraper.py

# Weekly GitHub scraping on Mondays at 10 AM  
0 10 * * 1 cd /path/to/intelforge && python github_scraper.py

# Daily web scraping at 2 PM
0 14 * * * cd /path/to/intelforge && python web_scraper.py
```

### Data Management
```bash
# View statistics
python data_organizer.py --action stats

# Remove duplicates
python data_organizer.py --action cleanup

# Organize files by date
python data_organizer.py --action organize

# Generate content index
python data_organizer.py --action index

# Search content
python data_organizer.py --action search --query "bollinger bands"

# Backup database
python data_organizer.py --action backup
```

## 🔧 Configuration

### Required API Keys (Optional)

**Reddit API** (for higher rate limits):
1. Go to https://www.reddit.com/prefs/apps
2. Create a new app (script type)
3. Add credentials to config.yaml or environment variables

**GitHub API** (for higher rate limits):
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with repo read permissions
3. Add to config.yaml or environment variables

### Environment Variables
```bash
# Reddit
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"

# GitHub  
export GITHUB_TOKEN="your_github_token"

# Framework settings
export INTELFORGE_DRY_RUN="true"
export INTELFORGE_VERBOSE="true"
```

## 🛡️ Ethical Scraping

This framework follows ethical scraping practices:

- ✅ **Rate Limiting** - Delays between requests to avoid overloading servers
- ✅ **Robots.txt Compliance** - Checks and respects robots.txt files
- ✅ **Official APIs** - Uses official APIs (Reddit PRAW, GitHub PyGitHub) when available
- ✅ **Personal Use** - Designed for non-commercial research purposes
- ✅ **Respectful User-Agents** - Identifies itself properly in requests

## 🔍 Troubleshooting

### Common Issues

**No data scraped:**
- Check API credentials in config.yaml
- Run with `--dry-run` to test without saving
- Check logs in `vault/logs/` for errors

**Rate limiting errors:**
- Increase delays in config.yaml
- Check API rate limit status
- Use official APIs instead of scraping when possible

**Import errors:**
- Install requirements: `pip install -r requirements_scraping.txt`
- Check Python version (3.8+ recommended)

### Debug Mode
```bash
# Enable verbose logging
export INTELFORGE_VERBOSE="true"

# Run specific scraper with dry-run
python reddit_scraper.py --dry-run --limit 1

# Check framework logs
tail -f vault/logs/reddit_*.log
```

## 📈 Performance

**Typical Performance** (personal use):
- Reddit: ~20 posts/minute
- GitHub: ~10 repositories/minute  
- Web: ~5 articles/minute

**Designed for:**
- Personal research (not commercial scraping)
- Daily/weekly automated runs
- Quality over quantity (curated, relevant content)

## 🎯 Next Steps

1. **Test the framework** with small limits
2. **Configure API keys** for better rate limits
3. **Set up automation** with the scheduler
4. **Customize target sources** in config.yaml
5. **Integrate with your workflow** (Obsidian, note-taking, etc.)

## 📝 Development

Built following IntelForge's simplicity-first philosophy:
- One file per component
- Configuration-driven behavior
- Functions over classes when possible
- AI-regenerable modules
- Comprehensive error handling

Total implementation time: ~5 hours
Maintainable by solo developer with AI assistance.