# IntelForge Scraping Configuration Guide

## Overview

IntelForge is currently configured as a multi-phase intelligent scraping system focused on algorithmic trading and quantitative finance research. This guide explains how to configure **what**, **where**, and **when** to scrape.

## Current Production Status

**System Status**: Production Ready (88.6% health score)
**Current Phase**: Phase 1 - Reddit Scraping (with Phase 2-3 capabilities available)
**Automation Status**: No automated scheduling active (manual execution required)

## 1. WHAT TO SCRAPE - Content Configuration

### 1.1 Target Content Types

Located in `/home/kiriti/alpha_projects/intelforge/config/config.yaml`:

```yaml
# Current target content areas
reddit:
  keywords:
    - "strategy"
    - "backtest"
    - "algorithm"
    - "bot"
    - "trading"
    - "indicator"

web:
  keywords:
    - "algorithmic trading"
    - "quantitative finance"
    - "trading strategy"
    - "backtesting"
    - "technical analysis"
    - "machine learning trading"
```

### 1.2 Content Filtering Thresholds

```yaml
# Quality thresholds
reddit:
  min_post_score: 5      # Minimum upvotes to consider
  min_comment_score: 2   # Minimum comment upvotes

# Semantic filtering (via semantic_crawler.py)
semantic_threshold: 0.75  # AI similarity threshold (0.0-1.0)
```

### 1.3 Content Freshness Rules

Located in `/home/kiriti/alpha_projects/intelforge/config/freshness_config.yaml`:

```yaml
# Time-to-live settings by content type
content_types:
  news:
    ttl_hours: 24        # Daily refresh
  research:
    ttl_hours: 168       # Weekly refresh
  documentation:
    ttl_hours: 720       # Monthly refresh
```

## 2. WHERE TO SCRAPE - Target Configuration

### 2.1 Reddit Targets

```yaml
reddit:
  subreddits:
    - "algotrading"
    - "SecurityAnalysis"
    - "investing"
    - "quantfinance"
```

### 2.2 Web Targets

```yaml
web:
  target_sites:
    - "medium.com"
    - "dev.to"
    - "towardsdatascience.com"
    - "quantstart.com"
```

### 2.3 GitHub Targets

```yaml
github:
  search_queries:
    - "algorithmic trading"
    - "quantitative finance"
    - "trading bot"
    - "backtesting"
```

### 2.4 Financial Data Targets

Located in `/home/kiriti/alpha_projects/intelforge/config/canary_targets.yaml`:

```yaml
# Financial data sources for validation
finviz_canary:
  url: "https://finviz.com/"

yahoo_finance_canary:
  url: "https://finance.yahoo.com/"
```

## 3. WHEN TO SCRAPE - Scheduling Configuration

### 3.1 Current Automation Status

**No automated scheduling is currently active.**

Available execution methods:
- Manual script execution
- Command-line interface via `run_intelforge.sh`

### 3.2 Rate Limiting Configuration

```yaml
# Rate limiting settings
reddit:
  rate_limit_delay: 2      # Seconds between API calls

web:
  rate_limit_delay: 3      # Seconds between requests

github:
  rate_limit_delay: 1      # Seconds between requests
```

### 3.3 Scraping Profiles

Located in `/home/kiriti/alpha_projects/intelforge/config/scraping_profiles.json`:

```json
{
  "financial_fast": {
    "workers": 5,
    "delay_range": [1, 3],
    "retries": 2
  },
  "financial_stealth": {
    "workers": 3,
    "delay_range": [3, 8],
    "retries": 3
  }
}
```

## 4. HOW TO CONFIGURE SCRAPING

### 4.1 Basic Configuration Steps

1. **Edit main config file:**
   ```bash
   nano /home/kiriti/alpha_projects/intelforge/config/config.yaml
   ```

2. **Add API credentials:**
   ```yaml
   reddit:
     client_id: "your_reddit_client_id"
     client_secret: "your_reddit_secret"

   github:
     access_token: "your_github_token"
   ```

3. **Configure targets:**
   ```yaml
   # Add new subreddits
   reddit:
     subreddits:
       - "algotrading"
       - "your_new_subreddit"

   # Add new websites
   web:
     target_sites:
       - "medium.com"
       - "your_new_site.com"
   ```

### 4.2 Advanced Configuration

#### Semantic Filtering
```bash
# Run semantic crawler with custom threshold
python scripts/semantic_crawler.py --url-file urls.txt --threshold 0.85
```

#### Custom Scraping Profiles
Edit `/home/kiriti/alpha_projects/intelforge/config/scraping_profiles.json`:
```json
{
  "custom_profile": {
    "workers": 2,
    "delay_range": [5, 10],
    "retries": 5,
    "timeout": 120
  }
}
```

## 5. EXECUTION COMMANDS

### 5.1 Available Commands

```bash
# Run comprehensive tests
./scripts/run_intelforge.sh test

# Start batch scraping
./scripts/run_intelforge.sh scrape

# Run AI processing
./scripts/run_intelforge.sh ai "your search query"

# Monitor system
./scripts/run_intelforge.sh monitor

# Financial analysis
./scripts/run_intelforge.sh financial
```

### 5.2 Manual Script Execution

```bash
# Reddit scraping (Phase 1)
python scripts/scrapers/phase_01_reddit.py

# GitHub scraping (Phase 2)
python scripts/scrapers/phase_02_github.py

# Semantic crawler
python scripts/semantic_crawler.py

# Stealth scraper
python scripts/stealth_scraper.py
```

## 6. MONITORING AND LOGS

### 6.1 Log Locations

```
/home/kiriti/alpha_projects/intelforge/logs/
├── monitoring.log              # System monitoring
├── intelforge_errors.log       # Error logs
├── alerts.log                  # Alert notifications
└── production_readiness_*.json # Health reports
```

### 6.2 Recent Activity

Based on logs:
- System health: 88.6% (healthy)
- Last monitoring: 2025-07-16 13:47:26
- No recent scraping activity detected
- No automated processes running

## 7. SETUP AUTOMATION (Optional)

### 7.1 Cron Job Setup

```bash
# Add to crontab for daily scraping
crontab -e

# Add line:
0 9 * * * cd /home/kiriti/alpha_projects/intelforge && ./scripts/run_intelforge.sh scrape
```

### 7.2 Systemd Service Setup

```bash
# Create systemd service file
sudo nano /etc/systemd/system/intelforge.service
```

## 8. SECURITY CONSIDERATIONS

### 8.1 Current Security Features

- Stealth scraping capabilities
- Proxy pool support (requires manual configuration)
- Rate limiting protection
- Anti-detection measures

### 8.2 Proxy Configuration

Edit `/home/kiriti/alpha_projects/intelforge/config/proxy_pools.txt`:
```
# Add your proxy providers
http://proxy1.example.com:8080
socks5://proxy2.example.com:1080
```

## 9. TROUBLESHOOTING

### 9.1 Common Issues

1. **No scraping activity**: Check API credentials in config.yaml
2. **Rate limiting errors**: Increase delay_range in scraping profiles
3. **Health check failures**: Review monitoring.log for details

### 9.2 Debug Commands

```bash
# Check system health
python scripts/comprehensive_test_runner.py

# Validate configuration
python scripts/validate_naming.sh

# Run security scan
bash scripts/security_scan.sh
```

## 10. NEXT STEPS

To activate scraping:

1. **Configure API credentials** in config.yaml
2. **Add target URLs** to appropriate sections
3. **Set up scheduling** (cron/systemd) if desired
4. **Run initial test**: `./scripts/run_intelforge.sh test`
5. **Start scraping**: `./scripts/run_intelforge.sh scrape`

---

**Last Updated**: 2025-07-16
**System Status**: Production Ready
**Configuration Version**: 1.0
