# IntelForge User Guide - Intelligent Content Crawling System

**Version**: 1.0.0
**Status**: Production Ready
**Last Updated**: 2025-07-17

## Table of Contents
- [Quick Start](#quick-start)
- [VSCode Integration](#vscode-integration)
- [What is IntelForge](#what-is-intelforge)
- [Core Features](#core-features)
- [How to Use IntelForge](#how-to-use-intelforge)
- [When to Scrape](#when-to-scrape)
- [What to Scrape](#what-to-scrape)
- [Advanced Usage](#advanced-usage)
- [Production Guidelines](#production-guidelines)
- [Troubleshooting](#troubleshooting)

## VSCode Integration

**✅ Ready to Use**: IntelForge includes complete VSCode integration with 13 pre-configured tasks

**Access Tasks**: `Ctrl+Shift+P` → "Tasks: Run Task" → Select IntelForge task

**Popular Tasks**:
- Health Check, System Status
- Semantic Crawling (Dry Run/Production/Stealth)
- Full Sync Workflow, Vector Snapshots
- PII Scanning, Budget Tracking

**File Location**: `.vscode/tasks.json` (already created and configured)

---

## Quick Start

### Basic Setup
```bash
# 1. Activate the environment
source venv/bin/activate

# 2. Check system health
python scripts/cli.py health

# 3. Create your URL list
echo "https://finance.yahoo.com/news/" > my_urls.txt
echo "https://www.investopedia.com/markets/" >> my_urls.txt

# 4. Run semantic crawler
python scripts/semantic_crawler.py --url-file my_urls.txt --threshold 0.75
```

### Immediate Results
- Content saved to: `/vault/notes/semantic_capture/`
- Vector embeddings stored in: `/chroma_storage/`
- Processing summary displayed in terminal

---

## What is IntelForge

IntelForge is an **AI-powered intelligence gathering system** specifically designed for:

### Primary Use Cases
- **Financial Research**: Algorithmic trading content, market analysis, quantitative finance
- **Academic Research**: Papers, reports, and educational content
- **Content Intelligence**: Semantic filtering of relevant information from the web

### Core Technology
- **AI-Powered Filtering**: Uses SentenceTransformer models for semantic analysis
- **Smart Content Selection**: Cosine similarity scoring against reference embeddings
- **Production-Grade Infrastructure**: Enterprise security, monitoring, and compliance

---

## Core Features

### 🧠 AI-Powered Content Intelligence
- **Semantic Analysis**: Understands content meaning, not just keywords
- **Relevance Scoring**: Filters content based on similarity to your interests
- **Quality Control**: Automatic language detection and content validation

### 🔒 Production-Ready Security
- **PII Detection**: Automatic removal of sensitive information
- **Robots.txt Compliance**: Respectful crawling with bypass options
- **Rate Limiting**: Prevents server overload and bans
- **Proxy Support**: Stealth crawling capabilities

### 📊 Intelligent Storage
- **Markdown Format**: Obsidian-compatible with YAML frontmatter
- **Vector Database**: Embedded content for similarity searches
- **Metadata Tracking**: Automatic tag extraction and source attribution

---

## How to Use IntelForge

### 1. Environment Setup
```bash
# Always use the correct virtual environment
source venv/bin/activate

# Verify installation
python scripts/cli.py --version
```

### 2. Create URL Lists
Create text files with URLs to crawl:

```bash
# Financial content
cat > finance_urls.txt << EOF
https://finance.yahoo.com/news/
https://www.investopedia.com/markets/
https://www.marketwatch.com/
https://seekingalpha.com/
EOF

# Research content
cat > research_urls.txt << EOF
https://arxiv.org/list/q-fin/recent
https://papers.ssrn.com/sol3/DisplayAbstractSearch.cfm
https://www.researchgate.net/
EOF
```

### 3. Basic Crawling Commands

#### Safe Testing (Recommended First)
```bash
# Dry run - no files saved, just shows what would be captured
python scripts/semantic_crawler.py --url-file finance_urls.txt --dry-run --threshold 0.75
```

#### Live Crawling
```bash
# Basic crawling with default settings
python scripts/semantic_crawler.py --url-file finance_urls.txt --threshold 0.75

# With domain filtering for focused results
python scripts/semantic_crawler.py --url-file finance_urls.txt \
  --limit-domains "finance.yahoo.com,investopedia.com" \
  --threshold 0.8
```

#### Stealth Crawling
```bash
# For sites that might block automated access
python scripts/semantic_crawler.py --url-file finance_urls.txt \
  --proxy-rotate \
  --max-retries 5 \
  --threshold 0.75
```

### 4. Understanding Results

#### Terminal Output
```
📊 SEMANTIC CRAWLER SUMMARY
═══════════════════════════
URLs processed: 5
Content captured: 3
Capture rate: 60.0%
Average similarity: 0.823
Similarity range: 0.756 - 0.891
Mode: LIVE
```

#### File Output Structure
```
vault/notes/semantic_capture/
├── 2025-07-17_finance_yahoo_com_news_article.md
├── 2025-07-17_investopedia_com_markets_guide.md
└── metadata/
    ├── finance_yahoo_com_news_article.json
    └── investopedia_com_markets_guide.json
```

---

## When to Scrape

### Optimal Timing

#### Daily Research Routine
```bash
# Morning: Market news and analysis
python scripts/semantic_crawler.py --url-file morning_news.txt --threshold 0.8

# Afternoon: Research papers and analysis
python scripts/semantic_crawler.py --url-file research_urls.txt --threshold 0.75

# Evening: Weekly reports and insights
python scripts/semantic_crawler.py --url-file weekly_reports.txt --threshold 0.7
```

#### Frequency Guidelines
- **News Sites**: 2-3 times daily (market hours)
- **Research Papers**: Weekly or bi-weekly
- **Analysis Reports**: As published (usually weekly/monthly)
- **Educational Content**: On-demand basis

### Automated Scheduling
```bash
# Create a cron job for automated crawling
# Edit with: crontab -e
# Run every 4 hours during market days
0 */4 * * 1-5 cd /home/kiriti/alpha_projects/intelforge && source venv/bin/activate && python scripts/semantic_crawler.py --url-file daily_urls.txt --threshold 0.75
```

---

## What to Scrape

### High-Value Content Types

#### 1. Financial News & Analysis ⭐⭐⭐⭐⭐
```bash
# Premium financial content
cat > finance_premium.txt << EOF
https://finance.yahoo.com/news/
https://www.marketwatch.com/investing
https://seekingalpha.com/market-news
https://www.fool.com/investing/
https://www.benzinga.com/
EOF
```

#### 2. Quantitative Research ⭐⭐⭐⭐⭐
```bash
# Research and academic content
cat > quant_research.txt << EOF
https://papers.ssrn.com/sol3/DisplayAbstractSearch.cfm?txtCriteria=algorithmic+trading
https://arxiv.org/list/q-fin/recent
https://www.quantstart.com/articles/
https://www.researchgate.net/topic/Algorithmic-Trading
EOF
```

#### 3. Technical Analysis ⭐⭐⭐⭐
```bash
# Technical analysis and trading strategies
cat > technical_analysis.txt << EOF
https://www.tradingview.com/ideas/
https://stockcharts.com/articles/
https://www.investopedia.com/technical-analysis-4689657
EOF
```

#### 4. Market Data & Reports ⭐⭐⭐
```bash
# Market reports and economic data
cat > market_reports.txt << EOF
https://www.federalreserve.gov/newsevents/pressreleases.htm
https://www.sec.gov/news/pressreleases
https://fred.stlouisfed.org/
EOF
```

### Content Quality Guidelines

#### High-Quality Sources (Threshold: 0.8-0.9)
- Academic papers and research
- Professional analysis reports
- Regulatory announcements
- Expert commentary

#### Medium-Quality Sources (Threshold: 0.7-0.8)
- Financial news articles
- Market commentary
- Educational content
- Company reports

#### Exploratory Sources (Threshold: 0.6-0.7)
- Blog posts and opinions
- Social media insights
- Forum discussions
- News aggregators

### Domain-Specific Recommendations

#### Algorithmic Trading Focus
```bash
python scripts/semantic_crawler.py --url-file algo_trading.txt \
  --limit-domains "quantstart.com,arxiv.org,papers.ssrn.com" \
  --threshold 0.85
```

#### Market Analysis Focus
```bash
python scripts/semantic_crawler.py --url-file market_analysis.txt \
  --limit-domains "marketwatch.com,seekingalpha.com,benzinga.com" \
  --threshold 0.75
```

#### Academic Research Focus
```bash
python scripts/semantic_crawler.py --url-file academic.txt \
  --limit-domains "arxiv.org,researchgate.net,ssrn.com" \
  --threshold 0.8
```

---

## Advanced Usage

### Custom Reference Embeddings
```bash
# Update reference embeddings for your specific domain
python scripts/semantic_crawler.py --regenerate-reference --url-file high_quality_samples.txt
```

### Debugging and Development
```bash
# Save raw HTML for analysis
python scripts/semantic_crawler.py --url-file test_urls.txt --save-raw --dry-run

# Ignore robots.txt for testing (use responsibly)
python scripts/semantic_crawler.py --url-file test_urls.txt --ignore-robots --dry-run
```

### Batch Processing
```bash
# Process multiple URL files
for file in finance_*.txt; do
    echo "Processing $file..."
    python scripts/semantic_crawler.py --url-file "$file" --threshold 0.75
    sleep 300  # 5-minute delay between batches
done
```

### Integration with Other Tools
```bash
# Health check before crawling
python scripts/cli.py health --json --strict
if [ $? -eq 0 ]; then
    python scripts/semantic_crawler.py --url-file urls.txt --threshold 0.75
fi

# Post-processing with IntelForge sync
python scripts/semantic_crawler.py --url-file urls.txt --threshold 0.75
python scripts/cli.py sync
```

---

## Production Guidelines

### Best Practices

#### 1. Rate Limiting & Respect
```bash
# Always use appropriate delays
python scripts/semantic_crawler.py --url-file urls.txt \
  --threshold 0.75 \
  --max-retries 3  # Don't be too aggressive
```

#### 2. Domain-Specific Configuration
```bash
# Focus on relevant domains to improve quality
python scripts/semantic_crawler.py --url-file urls.txt \
  --limit-domains "finance.yahoo.com,investopedia.com,quantstart.com" \
  --threshold 0.8
```

#### 3. Regular Monitoring
```bash
# Check system health regularly
python scripts/cli.py health

# Monitor storage usage
du -sh vault/notes/semantic_capture/
du -sh chroma_storage/
```

### Security Considerations

#### PII Protection
- System automatically detects and sanitizes personal information
- All content is processed through privacy filters
- Audit logs track all operations

#### Legal Compliance
- Robots.txt compliance enabled by default
- Rate limiting prevents server overload
- Content attribution preserved in metadata

#### Data Management
```bash
# Regular cleanup of old content
find vault/notes/semantic_capture/ -name "*.md" -mtime +30 -delete

# Backup vector database
cp -r chroma_storage/ backups/chroma_backup_$(date +%Y%m%d)
```

---

## Troubleshooting

### Common Issues

#### 1. Low Capture Rate
**Problem**: Very few URLs result in captured content

**Solutions**:
```bash
# Lower the threshold
python scripts/semantic_crawler.py --url-file urls.txt --threshold 0.6

# Check content with dry run
python scripts/semantic_crawler.py --url-file urls.txt --dry-run --threshold 0.75

# Update reference embeddings
python scripts/semantic_crawler.py --regenerate-reference --url-file good_examples.txt
```

#### 2. Access Denied Errors
**Problem**: Websites blocking automated access

**Solutions**:
```bash
# Use proxy rotation
python scripts/semantic_crawler.py --url-file urls.txt --proxy-rotate

# Respect robots.txt (default behavior)
python scripts/semantic_crawler.py --url-file urls.txt --threshold 0.75

# Check robots.txt manually
curl https://example.com/robots.txt
```

#### 3. Memory Issues
**Problem**: High memory usage with large batches

**Solutions**:
```bash
# Process smaller batches
split -l 10 large_urls.txt batch_
for batch in batch_*; do
    python scripts/semantic_crawler.py --url-file "$batch" --threshold 0.75
    sleep 60
done

# Monitor memory usage
python scripts/cli.py health
```

#### 4. Storage Issues
**Problem**: Vector database corruption or access issues

**Solutions**:
```bash
# Check system health
python scripts/cli.py health --json --strict

# Reset vector database (last resort)
rm -rf chroma_storage/
python scripts/semantic_crawler.py --url-file small_test.txt --threshold 0.75
```

### Getting Help

#### System Status
```bash
# Comprehensive system check
python scripts/cli.py health

# Check logs
tail -f logs/crawler.log

# Validate configuration
python scripts/cli.py validate-config
```

#### Debug Mode
```bash
# Verbose output for troubleshooting
python scripts/semantic_crawler.py --url-file test.txt --dry-run --verbose
```

---

## Performance Tips

### Optimization Strategies

#### 1. Threshold Tuning
- **High precision** (0.8-0.9): Very selective, fewer but higher quality results
- **Balanced** (0.7-0.8): Good mix of quality and quantity
- **Exploratory** (0.6-0.7): More content, requires manual filtering

#### 2. Domain Filtering
```bash
# Faster processing with focused domains
python scripts/semantic_crawler.py --url-file urls.txt \
  --limit-domains "trusted-site1.com,trusted-site2.com" \
  --threshold 0.75
```

#### 3. Batch Optimization
```bash
# Optimal batch size: 10-20 URLs
split -l 15 large_list.txt batch_
```

### Resource Management
- **Memory**: ~200MB per session with AI models loaded
- **Storage**: ~1-5MB per captured article
- **Processing**: ~3 URLs/second average speed

---

## Conclusion

IntelForge provides a powerful, AI-driven approach to content intelligence gathering. By following this guide, you can:

✅ **Efficiently capture** relevant financial and research content
✅ **Maintain quality** through semantic filtering
✅ **Operate safely** with built-in compliance and security
✅ **Scale effectively** with production-ready infrastructure

Start with small test batches, understand your content needs, and gradually scale up your crawling operations. The system is designed to learn and improve over time, making your intelligence gathering more effective with each use.

---

**Need Support?**
- Check system status: `python scripts/cli.py health`
- Review logs: `tail -f logs/crawler.log`
- Validate setup: `python scripts/cli.py validate-config`

**Happy Crawling!** 🚀
------------------------------------
To **start using IntelForge productively in VSCode**, especially with AI coding copilots or assistants like GitHub Copilot, CodeWhisperer, or ChatGPT extensions, here’s what the user should prompt to get meaningful help:

---

## ✅ 🔥 **Recommended VSCode AI Prompt to Start Using IntelForge**

> **Prompt**:
>
> ```
> I’m working with IntelForge, a semantic content crawler using Python. Help me:
> 1. Set up and activate the virtual environment
> 2. Run a health check
> 3. Create a basic URL list for crawling
> 4. Run a dry-run test with semantic_crawler.py
> 5. Understand the output structure (markdown, embeddings, metadata)
> ```

---

## 💡 If the user wants to go deeper, they can try these **follow-up prompts**:

### 🔍 For crawling logic:

> ```
> Explain how semantic_crawler.py scores and filters content using embeddings. Show where the cosine similarity threshold is applied and how to change it.
> ```

### 🧠 For customizing AI relevance:

> ```
> How can I improve IntelForge's relevance filtering by updating reference embeddings? Show the command and where the reference samples should go.
> ```

### ⚙️ For automation or batch runs:

> ```
> Help me write a bash script that runs IntelForge's semantic_crawler.py every 4 hours with proxy rotation and logs summaries.
> ```

### 🧪 For development/testing:

> ```
> Show me how to run the full sync pipeline from crawl to vector storage and how to skip phases like embeddings or snapshot.
> ```

---

## 🧭 If using ChatGPT Code Interpreter or Jupyter:

> ```python
> # Ask the assistant:
> What is the execution flow of semantic_crawler.py in IntelForge? Generate a diagram or step-by-step flow.
> ```

---

## Summary

Start with:

```plaintext
I’m using IntelForge to crawl semantic content. Help me initialize the system, test it on a few financial URLs, and explain the output.
```

Then use AI to:

* Understand components (`semantic_crawler.py`, embeddings, storage)
* Debug failures (no captures, low similarity)
* Automate workflows
* Extend features (e.g. add summarization or new tags)

--------------------------------------------------------------------
Here are the exact prompts you should use to start crawling and scraping with IntelForge:

  🚀 Quick Start Prompts

  1. Basic Setup Check

  Check IntelForge system status and ensure everything is working

  2. Create URL List for Crawling

  Create a URL list file with financial/trading websites for semantic crawling. Include sites like finance.yahoo.com, investopedia.com,
  marketwatch.com, and seekingalpha.com

  3. Test Crawling (Safe Mode)

  Run a dry-run test of the semantic crawler with threshold 0.75 to see what content would be captured without actually saving anything

  4. Production Crawling

  Start semantic crawling with the URL list, using threshold 0.8 for high-quality content, with domain filtering and proxy rotation enabled

  5. Monitor Results

  Show me the crawling results and system health status after the semantic crawling is complete

  📋 Step-by-Step Workflow

  Complete Workflow Prompt

  Help me set up and run IntelForge semantic crawling:

  1. Check system health
  2. Create a URL list with 10-15 high-quality financial/trading websites
  3. Run a test crawl in dry-run mode first
  4. If test looks good, run live crawling with threshold 0.8
  5. Show me the results and system status
  6. Create a backup snapshot of the vector database

  Advanced Crawling Prompt

  Set up advanced semantic crawling for financial content:

  1. Create URL lists for different content types (news, research, analysis)
  2. Run semantic crawling with domain filtering for trusted sites
  3. Use proxy rotation and stealth settings
  4. Monitor freshness and content quality
  5. Set up automated scheduling recommendations

  🎯 Ready-to-Use Commands

  When you give these prompts, I'll execute commands like:

  # System check
  python scripts/cli.py health

  # Create URL list
  echo "https://finance.yahoo.com/news/" > urls.txt

  # Test crawling
  python scripts/cli.py crawl urls.txt --dry-run --threshold 0.75

  # Live crawling
  python scripts/cli.py crawl urls.txt --threshold 0.8 --limit-domains "finance.yahoo.com,investopedia.com"

## 💡 **VSCode Integration - Ready to Use!**

**VSCode Tasks File Created**: `.vscode/tasks.json` with 13 pre-configured IntelForge tasks

**How to Access VSCode Tasks**:
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "Tasks: Run Task"
3. Select any IntelForge task from the list

**Available Tasks**:
- **IntelForge: Health Check** - System health monitoring
- **IntelForge: Health Check (JSON)** - Machine-readable health output
- **IntelForge: System Status** - Detailed system information
- **IntelForge: Semantic Crawl (Dry Run)** - Test crawling without saving
- **IntelForge: Production Crawl** - Live content crawling
- **IntelForge: Advanced Crawl (Stealth)** - Proxy rotation and stealth mode
- **IntelForge: Full Sync Workflow** - Complete crawl → embed → snapshot → archive
- **IntelForge: Create Vector Snapshot** - Backup vector database
- **IntelForge: List Snapshots** - Show available backups
- **IntelForge: Freshness Report** - Content age analytics
- **IntelForge: PII Scan** - Privacy and sensitive data detection
- **IntelForge: Budget Check** - Development time tracking
- **IntelForge: Version Info** - System version and component status

**Interactive Prompts**: Tasks will prompt you for:
- URL file path (default: `urls.txt`)
- Similarity threshold (default: `0.75`)
- Files to scan for PII

**Tasks File Location**: `.vscode/tasks.json` (✅ already created and configured)

**Quick Start with VSCode Tasks**:
1. Open IntelForge project in VSCode
2. `Ctrl+Shift+P` → "Tasks: Run Task"
3. Select "IntelForge: Health Check" to verify system
4. Select "IntelForge: Semantic Crawl (Dry Run)" to test
5. Select "IntelForge: Production Crawl" for live crawling

  🔧 Environment Setup

  Your .env file is already configured, but here's the complete template:

  PERPLEXITY_API_KEY=your_perplexity_api_key_here
  GITHUB_TOKEN=your_github_token_here

  Just say any of the prompts above and I'll start the IntelForge crawling process for you! 🚀

  The system is ready with enhanced modules enabled and all dependencies properly configured.
