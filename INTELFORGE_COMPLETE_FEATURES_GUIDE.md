# IntelForge Complete Features Guide

**Version**: 1.0.0
**Status**: Production Ready
**Last Updated**: 2025-07-17

---

## Table of Contents

- [Core CLI Commands](#core-cli-commands)
- [Web Monitoring Dashboard](#web-monitoring-dashboard)
- [System Management Features](#system-management-features)
- [Content Analysis Tools](#content-analysis-tools)
- [Data Management & Storage](#data-management--storage)
- [Security & Compliance Features](#security--compliance-features)
- [Development & Testing Tools](#development--testing-tools)
- [Production Operations](#production-operations)

---

## Core CLI Commands

### 1. **crawl** - Smart Semantic Crawling

**Purpose**: AI-powered web scraping with intelligent content filtering

**Basic Usage**:
```bash
python scripts/cli.py crawl input_file.txt --threshold 0.75
```

**Advanced Options**:
```bash
# Production crawling with all features
python scripts/cli.py crawl finance_urls.txt \
  --threshold 0.8 \
  --limit-domains "finance.yahoo.com,investopedia.com" \
  --proxy-rotate \
  --save-raw \
  --max-retries 5

# Safe testing mode
python scripts/cli.py crawl test_urls.txt --dry-run --threshold 0.6
```

**Key Features**:
- AI-powered content relevance scoring
- Domain filtering for focused crawling
- Proxy rotation for stealth operations
- Rate limiting and retry mechanisms
- Robots.txt compliance
- Raw HTML saving for debugging

---

### 2. **sync** - Unified Workflow Execution

**Purpose**: Complete end-to-end content processing pipeline

**Basic Usage**:
```bash
python scripts/cli.py sync --input urls.txt --threshold 0.75
```

**Workflow Phases**:
1. **Crawling**: Web content extraction
2. **Embeddings**: AI-powered vector generation
3. **Snapshot**: Vector database backup
4. **Archive**: Old data cleanup

**Phase Control**:
```bash
# Skip specific phases
python scripts/cli.py sync \
  --input urls.txt \
  --skip-crawl \
  --skip-embeddings \
  --skip-snapshot

# Dry run mode
python scripts/cli.py sync --input urls.txt --dry-run
```

---

### 3. **health** - System Health Monitoring

**Purpose**: Comprehensive system status and health checks

**Basic Usage**:
```bash
# Rich terminal output
python scripts/cli.py health

# Machine-readable JSON
python scripts/cli.py health --json --strict
```

**Health Components Monitored**:
- **System Health**: Core module availability and functionality
- **Drift Status**: Semantic content drift analysis (0.5% current)
- **Freshness Status**: Content age and update intervals
- **Crawl Success Rate**: Web scraping success metrics (95.5%)
- **PII Status**: Privacy and data protection compliance
- **Storage Health**: Vector database and file system status

**CI/CD Integration**:
```bash
# Exit code 0 if healthy, 1 if issues found
python scripts/cli.py health --json --strict
```

---

### 4. **status** - Detailed System Information

**Purpose**: Deep system analysis with resource monitoring

**Features**:
```bash
# Comprehensive system overview
python scripts/cli.py status

# Include detailed health checks
python scripts/cli.py status --detailed

# JSON output for automation
python scripts/cli.py status --json

# Include semantic drift reporting
python scripts/cli.py status --drift
```

**Information Provided**:
- Module availability and versions
- Storage usage (ChromaDB, Qdrant, logs)
- Configuration files status
- System resources (memory, disk, CPU)
- Security health status
- Performance metrics

---

## Web Monitoring Dashboard

### Production Dashboard

**URL**: `http://100.81.114.94:8091/monitoring_dashboard.html`

**Features**:
- **Real-time System Health**: Live status indicators
- **Performance Metrics**: CPU, memory, disk usage
- **Crawl Statistics**: Success rates, error counts
- **Vector Storage Status**: Database health and capacity
- **Alert Management**: Threshold-based notifications
- **Historical Trends**: Performance over time

### Mobile Dashboard

**URL**: `http://100.81.114.94:8090/mobile_dashboard.html`

**Features**:
- **Mobile-optimized interface** for remote monitoring
- **Critical metrics overview**
- **Quick health status** indicators
- **Emergency alert display**
- **Tailscale network integration** for secure remote access

### Dashboard Usage

**Access via Tailscale Network**:
```bash
# Connect to monitoring network
tailscale up

# Access dashboards
curl http://100.81.114.94:8091/monitoring_dashboard.html
curl http://100.81.114.94:8090/mobile_dashboard.html
```

**Automated Monitoring**:
- **5-minute intervals**: Automated health checks
- **15-minute cooldown**: Alert system prevents spam
- **Threshold alerts**: Customizable warning levels
- **Cron job integration**: Background monitoring

---

## System Management Features

### 5. **snapshot** - Vector Storage Management

**Purpose**: Backup and restore vector databases

**Create Snapshots**:
```bash
# Auto-generated snapshot path
python scripts/cli.py snapshot create

# Custom snapshot path
python scripts/cli.py snapshot create --path ./backups/my_snapshot

# Specific collection
python scripts/cli.py snapshot create --collection financial_data
```

**Restore Operations**:
```bash
# Restore from snapshot
python scripts/cli.py snapshot restore --path ./backups/snapshot_20250717

# List available snapshots
python scripts/cli.py snapshot list
```

**Snapshot Features**:
- **ChromaDB native persistence** for reliability
- **Metadata tracking**: Creation time, record count
- **0.15s recovery time** validated
- **Automatic verification** of restored data

---

### 6. **migrate** - Storage System Migration

**Purpose**: Move data between different vector storage systems

**Supported Migrations**:
```bash
# Qdrant to ChromaDB migration
python scripts/cli.py migrate qdrant chromadb --verify

# Disable verification for faster migration
python scripts/cli.py migrate qdrant chromadb --no-verify
```

**Migration Features**:
- **Data integrity verification** after migration
- **Progress tracking** with Rich CLI
- **Rollback capability** if migration fails
- **Schema compatibility checking**

---

### 7. **freshness** - Content Freshness Tracking

**Purpose**: Monitor and analyze content age and update patterns

**Generate Reports**:
```bash
# Overall freshness report
python scripts/cli.py freshness report

# Domain-specific analysis
python scripts/cli.py freshness report --domain finance.yahoo.com

# JSON output for automation
python scripts/cli.py freshness report --format json --days 30
```

**Update Metrics**:
```bash
# Update all domain metrics
python scripts/cli.py freshness update

# Find stale content (older than 24 hours)
python scripts/cli.py freshness stale --threshold 24

# Cleanup old records (older than 30 days)
python scripts/cli.py freshness cleanup --days 30
```

**Freshness Analytics**:
- **SQLite-utils integration** for fast analytics
- **Domain-level metrics**: Success rates, average age
- **Stale URL detection**: Configurable thresholds
- **TTR (Time to Recovery) tracking**

---

## Content Analysis Tools

### 8. **pii-scan** - Privacy Protection

**Purpose**: Detect and sanitize personally identifiable information

**Scan Content**:
```bash
# Scan text content
python scripts/cli.py pii-scan --content "John Doe lives at 123 Main St"

# Scan entire files
python scripts/cli.py pii-scan --file sensitive_document.txt

# Custom risk threshold
python scripts/cli.py pii-scan --file data.txt --threshold 30.0
```

**Advanced PII Detection**:
```bash
# Use Presidio (advanced) vs basic regex
python scripts/cli.py pii-scan --file data.txt --presidio

# Save detailed report
python scripts/cli.py pii-scan --file data.txt --output pii_report.json
```

**PII Detection Features**:
- **Presidio integration** for enterprise-grade detection
- **Risk scoring**: 0-100 risk assessment
- **Entity breakdown**: Names, addresses, phone numbers, emails
- **Sanitized content preview**
- **Confidence scoring** for each detected entity

---

### 9. **validate** - Canary Testing System

**Purpose**: Validate system functionality and content quality

**Run Validations**:
```bash
# Basic validation
python scripts/cli.py validate system

# Custom configuration
python scripts/cli.py validate content --config custom_rules.yaml

# Verbose output for debugging
python scripts/cli.py validate performance --verbose
```

**Validation Types**:
- **System validation**: Core functionality checks
- **Content validation**: Quality and relevance testing
- **Performance validation**: Speed and resource usage
- **Security validation**: Compliance and safety checks

---

## Data Management & Storage

### Storage Architecture

**Vector Storage Options**:
- **ChromaDB** (Primary): `/chroma_storage/` - Fast, native persistence
- **Qdrant** (Fallback): `/qdrant_storage/` - High-performance alternative

**Content Storage**:
- **Markdown Output**: `/vault/notes/semantic_capture/` - Obsidian-compatible
- **Raw Data**: Optional HTML storage for debugging
- **Metadata**: JSON files with extraction details

**Storage Management Commands**:
```bash
# Check storage health
python scripts/cli.py status

# Create backups
python scripts/cli.py snapshot create

# Monitor usage
du -sh chroma_storage/ qdrant_storage/ vault/
```

---

## Security & Compliance Features

### Enterprise Security

**Encryption**:
- **Fernet encryption** for data at rest
- **600+ permission validations** verified
- **Restrictive file permissions** (600/700)

**Audit Trail**:
- **Structured JSON logging** for all operations
- **Vector operation auditing** with timestamps
- **Metadata sanitization** for sensitive data

**PII Protection**:
- **Automatic PII detection** during crawling
- **Content sanitization** before storage
- **Risk assessment** with configurable thresholds

**Compliance Features**:
```bash
# Security health check
python scripts/cli.py health --component security

# PII audit scan
python scripts/cli.py pii-scan --file recent_crawl.txt

# Security status in monitoring
curl http://100.81.114.94:8091/monitoring_dashboard.html
```

---

## Development & Testing Tools

### 10. **docs** - Documentation Management

**Purpose**: Create and manage documentation following IntelForge conventions

**Create Documents**:
```bash
# Create implementation document
python scripts/cli.py docs create IMP "New Feature Implementation" --priority A

# Create status report
python scripts/cli.py docs create STS "System Status Update" --priority B

# Custom output directory
python scripts/cli.py docs create TSK "Task Documentation" --output ./project_docs/
```

**Validate Naming**:
```bash
# Check all documents follow naming conventions
python scripts/cli.py docs validate

# Organize existing documents
python scripts/cli.py docs organize
```

**Document Categories**:
- **STS** (Status), **IMP** (Implementation), **ARC** (Archive)
- **TSK** (Tasks), **CFG** (Configuration), **TST** (Testing)
- **RPT** (Reports), **REF** (Reference), **LOG** (Logs)

---

### 11. **budget-check** - Development Tracking

**Purpose**: Monitor development time and budget allocation

**Check Budget Status**:
```bash
# Quick budget check
python scripts/cli.py budget-check

# Detailed budget report
python scripts/cli.py budget-check --report

# Add time entries
python scripts/cli.py budget-check --add-time "Phase1,Testing,2.5,Unit test development"
```

**Budget Features**:
- **65-hour testing framework** investment tracking
- **Phase-based budgeting** across development cycles
- **Utilization monitoring** with threshold alerts
- **Markdown report generation** for stakeholders

---

### 12. **version** - System Information

**Purpose**: Detailed version and component status

**Version Information**:
```bash
# Quick version check
python scripts/cli.py --version

# Detailed system information
python scripts/cli.py version
```

**Information Provided**:
- **Version**: v1.0.0 (Production-Battle-Hardened)
- **Build Hash**: f9f919a
- **Component Status**: Enhanced modules, ChromaDB, Security manager
- **Security Health**: Real-time security component status

---

## Production Operations

### Monitoring & Alerting

**Real-time Monitoring**:
- **Automated health checks** every 5 minutes
- **Threshold-based alerts** with customizable limits
- **Performance trending** and historical analysis
- **Mobile-friendly dashboard** for remote access

**Alert Configuration**:
```bash
# Set custom thresholds in health monitoring
python scripts/cli.py health --threshold 85

# Check budget overruns
python scripts/cli.py budget-check --warn-if-over 95
```

### Automation & Scheduling

**Cron Job Integration**:
```bash
# Automated crawling every 4 hours (market days)
0 */4 * * 1-5 cd /path/to/intelforge && source venv/bin/activate && python scripts/cli.py sync --input daily_urls.txt

# Health monitoring every hour
0 * * * * cd /path/to/intelforge && python scripts/cli.py health --json --strict
```

**Workflow Automation**:
```bash
# Complete automated workflow
python scripts/cli.py sync --input production_urls.txt --threshold 0.8
python scripts/cli.py snapshot create
python scripts/cli.py freshness update
python scripts/cli.py health --json --strict
```

### Performance Optimization

**System Metrics**:
- **Processing Speed**: ~3 URLs/second with AI models
- **Memory Usage**: ~200MB with sentence-transformers loaded
- **Recovery Time**: 0.15s vector storage recovery validated
- **Success Rate**: 95.5% crawling success rate maintained

**Optimization Commands**:
```bash
# Monitor system performance
python scripts/cli.py status --detailed

# Check resource usage
python scripts/cli.py health --component system

# Performance tuning via thresholds
python scripts/cli.py crawl urls.txt --threshold 0.9  # Higher precision
python scripts/cli.py crawl urls.txt --threshold 0.6  # Higher recall
```

---

## Quick Reference

### Daily Operations
```bash
# 1. Check system health
python scripts/cli.py health

# 2. Run content crawling
python scripts/cli.py sync --input today_urls.txt

# 3. Monitor freshness
python scripts/cli.py freshness report

# 4. Create backup
python scripts/cli.py snapshot create
```

### Troubleshooting
```bash
# 1. Detailed system status
python scripts/cli.py status --detailed

# 2. Validate system components
python scripts/cli.py validate system --verbose

# 3. Check specific issues
python scripts/cli.py pii-scan --file problem_content.txt
python scripts/cli.py freshness stale --threshold 12
```

### Production Monitoring
```bash
# 1. Web dashboard access
curl http://100.81.114.94:8091/monitoring_dashboard.html

# 2. Automated health check
python scripts/cli.py health --json --strict

# 3. Budget monitoring
python scripts/cli.py budget-check --report
```

---

## Summary

IntelForge provides a comprehensive suite of frontend features including:

✅ **12 Core CLI Commands** for all operations
✅ **Web Monitoring Dashboard** with real-time metrics
✅ **AI-Powered Content Intelligence** with semantic filtering
✅ **Enterprise Security** with PII detection and encryption
✅ **Production Operations** with automated monitoring
✅ **Data Management** with backup/restore capabilities
✅ **Development Tools** with budget tracking and documentation
✅ **Mobile Dashboard** for remote monitoring

The system is production-ready with comprehensive features for intelligent content curation, system monitoring, and enterprise-grade operations.
