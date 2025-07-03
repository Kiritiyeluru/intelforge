# IntelForge Scraping Tools Recommendations

## Overview

This document provides comprehensive recommendations for web scraping tools and libraries based on analysis of current industry best practices, performance benchmarks, and suitability for IntelForge's algorithmic trading data acquisition needs.

## Executive Summary

**Primary Stack (Python):** selectolax + httpx + Playwright + Scrapy
**Secondary Stack (Rust):** reqwest + scraper + tokio (for performance-critical components)
**Anti-Detection:** scrapy-fake-useragent + rotating proxies + rate limiting
**Deployment:** Docker + systemd timers + PostgreSQL

## Python Tools Recommendations

### Static Content Scraping

#### **selectolax** (Primary Choice)
- **Performance**: 28x faster than BeautifulSoup (3.4s vs 95.4s for 100k operations)
- **Memory**: Minimal footprint, Cython-based with Lexbor backend
- **Use Case**: High-frequency trading data processing, large-scale HTML parsing
- **Installation**: `pip install selectolax`

#### **httpx** (Primary HTTP Client)
- **Advantages**: HTTP/2 support, native async, reduces bot detection fingerprinting
- **Performance**: Superior to requests for concurrent operations
- **Use Case**: Modern API interactions, concurrent scraping
- **Installation**: `pip install httpx`

#### **requests** (Fallback)
- **Use Case**: Simple, synchronous scraping tasks
- **Reliability**: Battle-tested, extensive documentation
- **Session Management**: Excellent cookie/session support

### Dynamic Content Scraping

#### **Playwright** (Primary Choice)
- **Performance**: 35% faster than Selenium, 20-30% lower memory usage
- **Reliability**: 91% network failure recovery vs Selenium's 72%
- **Features**: Auto-waiting, network interception, cross-browser support
- **Use Case**: JavaScript-heavy financial platforms, SPA applications
- **Installation**: `pip install playwright && playwright install`

#### **undetected-chromedriver** (Anti-Detection)
- **Success Rate**: 90-95% against standard anti-bot systems
- **Use Case**: Sites with heavy bot detection (Cloudflare, DataDome)
- **Features**: Automatic driver updates, stealth configurations
- **Installation**: `pip install undetected-chromedriver`

### Full Framework

#### **Scrapy** (Enterprise Choice)
- **Features**: Built-in concurrency, request deduplication, retry mechanisms
- **Architecture**: Asynchronous, handles thousands of concurrent requests
- **Pipeline**: Comprehensive data processing and storage pipelines
- **Use Case**: Large-scale multi-site scraping, production trading systems
- **Installation**: `pip install scrapy`

### Python Libraries Summary

| Library | Performance | Use Case | Complexity | Anti-Detection |
|---------|-------------|----------|------------|----------------|
| selectolax | Very High | Static HTML parsing | Low | None |
| httpx | High | HTTP requests | Low | Basic |
| Playwright | High | Dynamic content | Medium | Good |
| Scrapy | High | Large-scale scraping | High | Excellent |
| undetected-chromedriver | Medium | Anti-detection | Medium | Excellent |

## Rust Tools Recommendations

### High-Performance Static Scraping

#### **reqwest** (Primary HTTP Client)
- **Performance**: 2-10x faster than Python equivalents
- **Features**: Async/sync APIs, HTTP/2 support, tokio integration
- **Use Case**: High-throughput concurrent scraping
- **Installation**: `cargo add reqwest`

#### **scraper** (HTML Parsing)
- **Features**: jQuery-like syntax, CSS selectors, html5ever backend
- **Performance**: Significantly faster than Python parsers
- **Use Case**: Performance-critical HTML parsing
- **Installation**: `cargo add scraper`

#### **tokio** (Async Runtime)
- **Features**: Efficient concurrent execution, connection pooling
- **Performance**: Handles thousands of simultaneous connections
- **Use Case**: Concurrent scraping patterns, rate limiting
- **Installation**: `cargo add tokio`

### Performance Benchmarks

**Scraping 1000 financial pages:**
- Python: ~45 seconds
- Rust: ~4 seconds
- Memory usage: Rust uses 3-5x less memory

## Phase-Specific Recommendations

### Phase 1: Reddit Scraping (Current Priority)

```python
# Primary stack
- PRAW (Reddit API) - Official, rate-limited, reliable
- httpx + selectolax - For non-API scraping if needed
- Playwright - For dynamic content (rare for Reddit)

# Implementation
pip install praw httpx selectolax playwright
```

### Phase 2: GitHub Repository Mining

```python
# Primary stack
- PyGithub (GitHub API) - Official, comprehensive
- httpx + selectolax - For scraping GitHub pages
- Scrapy - For large-scale repository discovery

# Implementation
pip install PyGithub httpx selectolax scrapy
```

### Phase 3: Blog/News Scraping

```python
# Primary stack
- Scrapy - Main framework with pipelines
- Playwright - For JavaScript-heavy sites
- selectolax - For fast HTML parsing

# Implementation
pip install scrapy playwright selectolax
```

### Phase 4+: Production Scaling

```python
# Full enterprise stack
- Scrapy + middlewares for anti-detection
- PostgreSQL for structured storage
- Docker for deployment
- systemd timers for scheduling

# Additional tools
pip install scrapy-fake-useragent scrapy-rotating-proxies
```

## Anti-Detection Strategy

### Essential Components

#### **User-Agent Rotation**
```python
# scrapy-fake-useragent
pip install scrapy-fake-useragent
# Provides 2000+ real user agents with automatic rotation
```

#### **Proxy Rotation**
```python
# scrapy-rotating-proxies
pip install scrapy-rotating-proxies
# Supports datacenter and residential proxy pools
```

#### **Rate Limiting**
- **Scrapy**: Built-in autothrottle capabilities
- **Custom**: Semaphore-based request management
- **Adaptive**: Response-based throttling

### Proxy Services Comparison

| Service Type | Success Rate | Cost (Monthly) | Use Case |
|--------------|-------------|----------------|----------|
| Datacenter | 70-85% | $2.99+ | Basic scraping |
| Residential | 95-99% | $300-500 | Production systems |
| Mobile | 95-99% | $500+ | High-security sites |

### Cost Analysis

**Monthly operational costs for production:**
- Basic proxy service: $50-100
- Professional proxy service: $300-500
- CAPTCHA solving: $50-100
- Infrastructure: $100-200
- **Total**: $200-800/month

## Data Pipeline Integration

### Storage & Processing

#### **PostgreSQL** (Primary Database)
- **Features**: Time-series optimizations, bulk inserts (50k+/sec)
- **Use Case**: Structured financial data storage
- **Integration**: SQLAlchemy ORM, asyncpg for performance

#### **pandas** (Data Processing)
- **Features**: Data cleaning, transformation, analysis
- **Use Case**: ETL pipeline, data preparation
- **Alternative**: polars (10-30x faster for large datasets)

#### **Obsidian-Compatible Output**
```markdown
# Output format for vault integration
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

### ETL Patterns

**Production financial data pipeline schedule:**
- **Pre-market**: 6:00-9:30 AM data collection
- **Intraday**: Every 15 minutes processing
- **Post-market**: 4:00-8:00 PM analysis
- **Weekend**: Historical data processing

## Ubuntu/Linux Optimizations

### Deployment Strategy

#### **Docker Containerization**
```dockerfile
# Example Dockerfile for scraping agent
FROM python:3.12-slim
RUN apt-get update && apt-get install -y \
    chromium-browser \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "phase_01_reddit_scraper.py"]
```

#### **systemd Timers** (Preferred over cron)
```ini
# /etc/systemd/system/intelforge-scraper.timer
[Unit]
Description=IntelForge Scraper Timer

[Timer]
OnCalendar=*:0/15  # Every 15 minutes
Persistent=true

[Install]
WantedBy=timers.target
```

### CLI Tools Integration

#### **Essential Ubuntu Tools**
- **jq**: JSON processing for hook system
- **ripgrep**: Ultra-fast search (3-10x faster than grep)
- **fd**: Efficient file discovery
- **htop**: Process monitoring

#### **Hook System Integration**
```bash
# Example hook command using jq
jq -r '"\(.tool_input.command) - \(.tool_input.description)"' 
```

## Implementation Roadmap

### Phase 1: Foundation (Current)
1. **Setup basic Python environment**
   ```bash
   pip install praw httpx selectolax
   ```

2. **Implement Reddit scraping with PRAW**
   - Official API access
   - Rate limiting compliance
   - Error handling

3. **Add basic anti-detection**
   - User-agent rotation
   - Request delays
   - Session management

### Phase 2: Scaling
1. **Integrate Scrapy framework**
   ```bash
   pip install scrapy scrapy-fake-useragent
   ```

2. **Add database integration**
   ```bash
   pip install sqlalchemy asyncpg
   ```

3. **Implement proxy rotation**
   - Datacenter proxies for testing
   - Residential proxies for production

### Phase 3: Production
1. **Docker deployment**
   - Multi-stage builds
   - Security hardening
   - Resource limits

2. **systemd integration**
   - Service units
   - Timer scheduling
   - Logging configuration

3. **Monitoring and alerting**
   - Performance metrics
   - Error tracking
   - Resource monitoring

## Security Considerations

### Best Practices

1. **Rate Limiting**: Respect robots.txt and implement adaptive delays
2. **User-Agent Management**: Use realistic, rotating user agents
3. **Proxy Usage**: Rotate IP addresses to avoid blocks
4. **Session Handling**: Maintain persistent sessions when required
5. **Error Handling**: Graceful failure recovery
6. **Compliance**: Respect ToS and legal requirements

### Ethical Guidelines

1. **Personal Use Only**: Non-commercial research purposes
2. **Respectful Scraping**: Avoid overloading target servers
3. **Data Privacy**: Handle personal information appropriately
4. **Legal Compliance**: Adhere to relevant regulations

## Conclusion

The recommended stack prioritizes performance, reliability, and maintainability while aligning with IntelForge's simplicity-first philosophy. The phased approach allows for gradual scaling from basic API access to sophisticated anti-detection scraping.

**Key Success Factors:**
- Start with official APIs (PRAW, PyGithub)
- Implement robust error handling and retry logic
- Use Docker for consistent deployment
- Monitor performance and adjust strategies
- Maintain ethical scraping practices

This stack provides a solid foundation for building a comprehensive automated scraping agent capable of supporting sophisticated algorithmic trading data acquisition needs.