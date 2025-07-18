# Consolidated GitHub Repository List for Scraping Frameworks

## Overview
This document consolidates all GitHub repositories mentioned across multiple deep research analyses for web scraping frameworks. Each repository is evaluated with detailed use cases and recommendation scores (1-5 stars) based on comprehensive analysis.

## 🏆 Top-Tier Production-Ready Frameworks

### Enterprise-Grade Scraping Engines

#### **scrapy/scrapy** ⭐⭐⭐⭐⭐ (52.4k stars)
**Use Case**: Industrial-scale web scraping with enterprise features
**Strengths**: Battle-tested across thousands of companies, comprehensive ecosystem, advanced features (AutoThrottle, pipelines, middlewares)
**Best For**: Large-scale production deployments, enterprise scraping operations
**Integration**: Excellent - industry standard with professional support options
**Limitations**: Steeper learning curve, overkill for simple projects

#### **scrapy-plugins/scrapy-playwright** ⭐⭐⭐⭐⭐ (1.2k stars)
**Use Case**: JavaScript-heavy sites within Scrapy ecosystem
**Strengths**: Best-in-class JS handling, seamless Scrapy integration, multiple browser engines
**Best For**: SPAs, dynamic content, modern websites requiring browser automation
**Integration**: Perfect drop-in for existing Scrapy projects
**Limitations**: Higher resource usage than static scraping

#### **apify/crawlee-python** ⭐⭐⭐⭐ (5.8k stars)
**Use Case**: Modern async crawling with unified HTTP/browser interface
**Strengths**: Clean architecture, type-safe, AI-focused features, professional support
**Best For**: New projects, teams comfortable with modern Python patterns
**Integration**: Good but early adoption phase
**Limitations**: Smaller ecosystem compared to Scrapy, relatively new

### Content Extraction Champions

#### **adbar/trafilatura** ⭐⭐⭐⭐⭐ (4.2k stars)
**Use Case**: High-precision text extraction from web pages
**Strengths**: Benchmark leader (F1: 0.945), academic backing, used by HuggingFace/IBM/Microsoft
**Best For**: News articles, blog posts, content quality-critical applications
**Integration**: Excellent - clean API, multiple output formats
**Limitations**: Limited JS support, primarily static content

#### **AndyTheFactory/newspaper4k** ⭐⭐⭐⭐ (796 stars)
**Use Case**: Specialized news content extraction with NLP features
**Strengths**: 80+ languages, Google News integration, metadata extraction, active maintenance
**Best For**: News-focused applications, multi-language content
**Integration**: Good - well-documented API, Playwright compatibility
**Limitations**: Primarily news-focused, NLP dependencies can be heavy

#### **codelucas/newspaper** ⭐⭐⭐ (14.5k stars)
**Use Case**: Legacy news article extraction
**Strengths**: Mature codebase, large user base, established patterns
**Best For**: Existing projects using newspaper3k
**Integration**: Good but prefer newspaper4k for new projects
**Limitations**: Maintenance concerns, superseded by newspaper4k

### Academic Paper Scrapers

#### **jannisborn/paperscraper** ⭐⭐⭐⭐⭐ (381 stars)
**Use Case**: Comprehensive academic literature extraction across multiple databases
**Strengths**: PubMed/arXiv/bioRxiv/medRxiv/chemRxiv support, citation data, visualization tools
**Best For**: Systematic literature reviews, meta-analysis, comprehensive academic research
**Integration**: Excellent - clean API, pandas integration, AWS S3 support
**Limitations**: Google Scholar requires manual captcha solving

#### **Mahdisadjadi/arxivscraper** ⭐⭐⭐⭐ (312 stars)
**Use Case**: ArXiv-specific paper extraction
**Strengths**: Lightweight, direct OAI-PMH integration, reliable for arXiv
**Best For**: Physics/math/CS research, arXiv-focused projects
**Integration**: Very good - minimal dependencies, pandas compatible
**Limitations**: Single database, basic output formats

#### **jonatasgrosman/findpapers** ⭐⭐⭐⭐ (274 stars)
**Use Case**: Multi-database academic search with workflow management
**Strengths**: ACM/IEEE/Scopus/PubMed support, interactive classification, BibTeX output
**Best For**: Systematic reviews, bibliographic management, institutional research
**Integration**: Good - comprehensive CLI, workflow tools
**Limitations**: Maintenance concerns (last update Feb 2024)

#### **JohnGiorgi/biorxiv-scraper** ⭐ (11 stars)
**Use Case**: bioRxiv preprint extraction (NOT RECOMMENDED)
**Strengths**: None significant
**Best For**: Historical reference only
**Integration**: Poor - abandoned project
**Limitations**: Abandoned (last update April 2023), poor documentation

#### **karthiktadepalli1/ssrn-scraper** ⭐ (11 stars)
**Use Case**: SSRN papers (NOT RECOMMENDED)
**Strengths**: None significant
**Best For**: Not recommended for any use
**Integration**: Poor - abandoned, aggressive scraping
**Limitations**: 5+ years stale, ethical concerns, high blocking risk

## 🔄 Dynamic Content & JavaScript Handling

### Anti-Detection Specialists

#### **D4Vinci/Scrapling** ⭐⭐⭐⭐⭐ (5.4k stars)
**Use Case**: High-performance adaptive scraping with multiple engines
**Strengths**: 240x faster than BeautifulSoup, auto-match for site changes, multiple fetchers
**Best For**: Sites that frequently change structure, high-volume scraping
**Integration**: Excellent - drop-in replacement for requests/BeautifulSoup
**Limitations**: Newer project, learning curve for advanced features

#### **ultrafunkamsterdam/nodriver** ⭐⭐⭐⭐⭐ (2.7k stars)
**Use Case**: Undetectable browser automation via Chrome DevTools Protocol
**Strengths**: Successor to undetected-chromedriver, excellent anti-detection, async-first
**Best For**: Sites with sophisticated bot detection, CDP-based automation
**Integration**: Very good - clean async API, well-documented
**Limitations**: Chrome-only, requires Chrome installation

#### **daijro/camoufox** ⭐⭐⭐⭐⭐ (2.5k stars)
**Use Case**: Maximum stealth browser with custom Firefox build
**Strengths**: 71.5% CreepJS score, protocol-level spoofing, lightweight (200MB RAM)
**Best For**: Maximum stealth requirements, advanced bot detection bypass
**Integration**: Good - requires custom browser build
**Limitations**: Firefox-only, complex setup, potential stability issues

#### **Vinyzu/Botright** ⭐⭐⭐⭐ (1.4k stars)
**Use Case**: Playwright-based automation with CAPTCHA solving
**Strengths**: Built-in ML CAPTCHA solving, self-healing capabilities, real browser
**Best For**: CAPTCHA-protected sites, sophisticated anti-bot systems
**Integration**: Good - Playwright-compatible API
**Limitations**: GPL license, CAPTCHA solving not 100% reliable

### Browser Automation

#### **microsoft/playwright-python** ⭐⭐⭐⭐⭐ (11.4k stars)
**Use Case**: Enterprise-grade cross-browser automation
**Strengths**: Multi-browser support, excellent documentation, Microsoft backing
**Best For**: Cross-browser testing, enterprise applications, reliable automation
**Integration**: Excellent - comprehensive API, extensive ecosystem
**Limitations**: Higher resource usage, learning curve

#### **stephanlensky/zendriver** ⭐⭐⭐⭐ (216 stars)
**Use Case**: Enhanced nodriver fork with additional features
**Strengths**: Better community engagement, bug fixes, Docker support
**Best For**: CDP automation with enhanced features over nodriver
**Integration**: Very good - compatible with nodriver, additional features
**Limitations**: Smaller community than parent project

#### **rebrowser/rebrowser-patches** ⭐⭐⭐⭐ (2.4k stars)
**Use Case**: Drop-in anti-detection patches for Playwright/Puppeteer
**Strengths**: No code changes required, comprehensive leak fixes
**Best For**: Existing Playwright/Puppeteer projects needing stealth
**Integration**: Excellent - truly drop-in replacement
**Limitations**: Requires keeping up with upstream changes

### Stealth & Bypass Tools

#### **jpjacobpadilla/Stealth-Requests** ⭐⭐⭐⭐⭐ (268 stars)
**Use Case**: Undetected HTTP requests with advanced fingerprint masking
**Strengths**: TLS fingerprint masking, intelligent headers, requests-compatible
**Best For**: HTTP-only scraping with anti-detection needs
**Integration**: Excellent - drop-in requests replacement
**Limitations**: HTTP-only (no JavaScript execution)

#### **ultrafunkamsterdam/undetected-chromedriver** ⭐⭐⭐ (9.7k stars)
**Use Case**: Legacy anti-detection ChromeDriver (superseded by nodriver)
**Strengths**: Proven track record, large user base
**Best For**: Legacy projects, specific Selenium workflows
**Integration**: Good but deprecated in favor of nodriver
**Limitations**: Superseded by nodriver, maintenance mode

#### **kaliiiiiiiiii/Selenium-Driverless** ⭐⭐⭐⭐ (643 stars)
**Use Case**: Selenium without ChromeDriver for maximum stealth
**Strengths**: Passes Cloudflare/Bet365/Turnstile, multiple contexts
**Best For**: Selenium-based projects needing enhanced stealth
**Integration**: Good - Selenium-compatible API
**Limitations**: CDP detection concerns, requires Chrome

#### **psf/requests-html** ⭐⭐ (13.8k stars)
**Use Case**: Legacy JavaScript-enabled requests (NOT RECOMMENDED)
**Strengths**: Large user base, familiar requests syntax
**Best For**: Legacy projects only
**Integration**: Poor - essentially dead project
**Limitations**: Stale (since April 2024), 236 open issues, security concerns

## 🤖 AI-Powered & Intelligent Scrapers

#### **alirezamika/autoscraper** ⭐⭐⭐⭐⭐ (6.8k stars)
**Use Case**: Zero-configuration AI pattern learning for consistent site structures
**Strengths**: Learns from examples, no CSS selectors needed, reusable models
**Best For**: Trading forums, financial sites with consistent layouts
**Integration**: Excellent - lightweight, fast, simple API
**Limitations**: Requires examples, works best with consistent structures

#### **jpjacobpadilla/Stealth-Requests** ⭐⭐⭐⭐⭐ (268 stars)
**Use Case**: Intelligent anti-detection HTTP requests (covered above in Stealth section)

#### **thalissonvs/antiscraping-toolkit** ⭐⭐⭐⭐ (158 stars)
**Use Case**: Educational resource and research tool for anti-scraping analysis
**Strengths**: Comprehensive detection mechanism analysis, server/browser-side insights
**Best For**: Understanding modern anti-bot systems, research purposes
**Integration**: Good - educational value, not production scraping
**Limitations**: Educational focus, not a scraping tool per se

#### **niespodd/browser-fingerprinting** ⭐⭐⭐⭐ (1.3k stars)
**Use Case**: Analysis and research on browser fingerprinting techniques
**Strengths**: Comprehensive anti-bot provider analysis, stealth browser comparisons
**Best For**: Research, understanding detection mechanisms
**Integration**: Good - research value for anti-detection strategies
**Limitations**: Research tool, not production scraper

## 📰 News & Blog Specialized

### Enterprise News Crawlers

#### **fhamborg/news-please** ⭐⭐⭐⭐⭐ (2.3k stars)
**Use Case**: Production-grade news crawling and extraction
**Strengths**: 8+ years mature, Scrapy+Newspaper+readability combo, enterprise storage
**Best For**: Large-scale financial news monitoring, production deployments
**Integration**: Excellent - PostgreSQL/ElasticSearch/Redis support
**Limitations**: Complex setup for simple use cases

#### **flairNLP/fundus** ⭐⭐⭐⭐ (390 stars)
**Use Case**: High-precision news extraction with academic quality
**Strengths**: 99.89% precision benchmark, 390+ pre-configured sources
**Best For**: High-accuracy financial news, research-grade extraction
**Integration**: Good - clean API, multiple output formats
**Limitations**: Limited to pre-configured news sources

#### **oxylabs/google-news-scraper** ⭐⭐⭐⭐ (1.6k stars)
**Use Case**: Google News topic discovery and trending analysis
**Strengths**: Topic-based scraping, commercial scale options, CSV output
**Best For**: Financial trend detection, news discovery workflows
**Integration**: Good - professional implementation, API options
**Limitations**: Google News focused, rate limiting concerns

### Specialized News Tools

#### **the-dataface/Newspaper-Scrapers** ⭐⭐⭐ (179 stars)
**Use Case**: Pre-built scrapers for 14 major US news outlets
**Strengths**: Site-specific optimization, MongoDB/CSV output
**Best For**: US-focused news scraping, specific publisher requirements
**Integration**: Good - ready-to-use scrapers
**Limitations**: Limited to 14 sources, potentially stale configurations

#### **tule2236/News-Scraping-with-Scrapy** ⭐⭐⭐ (30 stars)
**Use Case**: Reuters-focused financial news scraper
**Strengths**: Financial news optimization, date-based URL generation
**Best For**: Reuters-specific financial news datasets
**Integration**: Good - Scrapy-based, compact data format
**Limitations**: Single source, potentially outdated

#### **free-news-api/news-crawlers** ⭐⭐⭐⭐ (18 stars)
**Use Case**: Comparative analysis and benchmarking of news crawlers
**Strengths**: Evaluation framework, integration examples, guidance
**Best For**: Choosing between news scraping solutions
**Integration**: Very good - helps with tool selection
**Limitations**: Analysis tool, not production scraper

### RSS & Feed Processing

#### **le1nux/crawly** ⭐⭐⭐ (27 stars)
**Use Case**: RSS feed monitoring and automated article collection
**Strengths**: Interval-based checking, CSV storage, comprehensive logging
**Best For**: RSS-based news monitoring, automated content discovery
**Integration**: Good - configurable intervals, CSV output
**Limitations**: RSS-only, simple storage options

#### **KenMwaura1/daily-news-scraper** ⭐⭐ (8 stars)
**Use Case**: Automated daily news with SMS notifications
**Strengths**: Scheduled execution, SMS integration, multiple sources
**Best For**: Personal news monitoring, notification workflows
**Integration**: Fair - Africa's Talking SMS dependency
**Limitations**: Region-specific, limited sources

#### **binsarjr/news-scraper** ⭐⭐ (6 stars)
**Use Case**: Indonesian news outlets scraper
**Strengths**: Multi-source Indonesian news, keyword/date filtering
**Best For**: Indonesian market research, regional content
**Integration**: Fair - Poetry setup, CSV/JSON output
**Limitations**: Indonesia-specific, limited broader applicability

## 📝 Blog & General Content

### Platform-Specific Tools

#### **SomilGumber/wpextractor** ⭐⭐⭐ (15 stars)
**Use Case**: WordPress blog post extraction
**Strengths**: Automatic WordPress detection, JSON output, simple CLI
**Best For**: WordPress-focused content extraction
**Integration**: Good - simple CLI, scriptable
**Limitations**: WordPress-only, basic functionality

#### **dimitarOnGithub/blogger-scrapper** ⭐⭐⭐ (10 stars)
**Use Case**: Google Blogger platform scraper
**Strengths**: Atom/RSS feed support, multiple output formats
**Best For**: Blogger platform content, feed-based extraction
**Integration**: Good - multiple export options
**Limitations**: Blogger-specific, limited features

### Universal Content Tools

#### **readability-lxml** ⭐⭐⭐ (PyPI package)
**Use Case**: Clean article text extraction using Arc90's algorithm
**Strengths**: Proven readability algorithm, command-line and Python API
**Best For**: Content cleaning, readable text extraction
**Integration**: Good - established library, clean API
**Limitations**: Basic compared to modern alternatives like trafilatura

## 🏗️ Legacy & Reference Tools

#### **RISJbot** ⭐⭐ (73 stars)
**Use Case**: Academic research news framework (research-grade only)
**Strengths**: Many pre-written spiders for major news sites, fallback parser
**Best For**: Academic reference, research understanding
**Integration**: Fair - moderately structured, limited CI/tests
**Limitations**: Research-grade only, limited polish, not production-ready

#### **Mechanical News** ⭐ (8 stars)
**Use Case**: Scrapy + Flask news application framework (NOT RECOMMENDED)
**Strengths**: Full-stack application example (Scrapy + Flask + database)
**Best For**: Historical reference only
**Integration**: Poor - academic project, GPL license, low activity
**Limitations**: Abandoned project, niche academic use

## 📊 Strategic Evaluation Summary

### 🏆 **Top Tier (5/5 Stars) - Immediate Integration**
1. **scrapy/scrapy** - Enterprise foundation, battle-tested
2. **adbar/trafilatura** - Best-in-class content extraction
3. **scrapy-plugins/scrapy-playwright** - Superior JS handling
4. **ultrafunkamsterdam/nodriver** - Undetectable browser automation
5. **daijro/camoufox** - Maximum stealth capabilities
6. **D4Vinci/Scrapling** - High-performance adaptive scraping
7. **jannisborn/paperscraper** - Comprehensive academic research
8. **alirezamika/autoscraper** - Zero-config AI pattern learning
9. **jpjacobpadilla/Stealth-Requests** - Advanced anti-detection HTTP
10. **fhamborg/news-please** - Production-grade news crawling
11. **microsoft/playwright-python** - Enterprise browser automation

### 🎯 **High Value (4/5 Stars) - Strategic Implementation**
- **apify/crawlee-python** - Modern architecture, early adoption
- **AndyTheFactory/newspaper4k** - Specialized news extraction
- **Mahdisadjadi/arxivscraper** - ArXiv-focused research
- **jonatasgrosman/findpapers** - Multi-database academic search
- **Vinyzu/Botright** - CAPTCHA-solving browser automation
- **stephanlensky/zendriver** - Enhanced nodriver fork
- **rebrowser/rebrowser-patches** - Drop-in anti-detection patches
- **kaliiiiiiiiii/Selenium-Driverless** - Enhanced Selenium stealth
- **flairNLP/fundus** - High-precision news extraction
- **oxylabs/google-news-scraper** - Google News trend analysis
- **thalissonvs/antiscraping-toolkit** - Anti-bot research
- **niespodd/browser-fingerprinting** - Detection analysis

### ⚠️ **Limited Use (3/5 Stars) - Specific Scenarios**
- **codelucas/newspaper** - Legacy news extraction
- **ultrafunkamsterdam/undetected-chromedriver** - Superseded by nodriver
- Various specialized tools for specific platforms

### ❌ **Not Recommended (1-2/5 Stars)**
- **psf/requests-html** - Abandoned project
- **JohnGiorgi/biorxiv-scraper** - Abandoned, poor documentation
- **karthiktadepalli1/ssrn-scraper** - Ethical concerns, abandoned

## 🚀 **IntelForge Implementation Strategy**

### **Phase 1: Core Foundation (Week 1-2)**
- **Primary**: scrapy + trafilatura + scrapy-playwright
- **Academic**: paperscraper + arxivscraper
- **Anti-Detection**: Stealth-Requests for HTTP, nodriver for browser

### **Phase 2: Intelligence Enhancement (Week 3-4)**
- **AI Pattern Learning**: AutoScraper for trading forums
- **News Intelligence**: news-please for financial news monitoring
- **Advanced Stealth**: Evaluate camoufox for maximum stealth needs

### **Phase 3: Scale & Optimization (Week 5-6)**
- **Performance**: Scrapling for high-volume scraping
- **Specialized**: fundus for high-accuracy news extraction
- **Monitoring**: Implement detection analysis tools

### **Phase 4: Advanced Capabilities**
- **Modern Stack**: Evaluate crawlee-python migration
- **Enhanced Anti-Detection**: camoufox + botright for sophisticated sites
- **Specialized Tools**: Platform-specific scrapers as needed

## 📈 **Key Performance Metrics**
- **Content Quality Leader**: trafilatura (F1: 0.945)
- **Speed Champion**: Scrapling (240x faster than BeautifulSoup)
- **Anti-Detection Best**: camoufox (71.5% CreepJS score)
- **Enterprise Standard**: Scrapy (52.4k stars, battle-tested)
- **Academic Coverage**: paperscraper (5 major databases)

## 🎯 **Integration Benefits for IntelForge**
1. **Automated Intelligence**: 80% reduction in manual pattern maintenance
2. **Anti-Detection**: Access to previously blocked financial sites
3. **Quality Assurance**: Academic-grade extraction accuracy
4. **Comprehensive Coverage**: News, academic, forum, and blog content
5. **Performance**: 6x-240x speed improvements across different scenarios

**Total Repositories Analyzed**: 40+ frameworks and tools
**Recommendation Confidence**: High - based on comprehensive GitHub analysis, performance benchmarks, and maintenance assessment
**Research Sources**: Multi-platform deep research (Claude Code, ChatGPT, Perplexity)
**Last Updated**: January 2025 - Current GitHub statistics and maintenance status
