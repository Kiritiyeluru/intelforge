# IntelForge CLI Reference Guide

**Document Version**: 1.0
**Created**: 2025-07-16
**Status**: Production-Ready
**Audience**: Users and administrators

---

## 🚀 Overview

The IntelForge CLI provides a unified interface for semantic content curation, system monitoring, and maintenance operations. All commands are accessed through the main CLI script.

### **Basic Usage**
```bash
# Always activate virtual environment first
source venv/bin/activate

# Run CLI commands
python scripts/cli.py <command> [options]

# Get help
python scripts/cli.py --help
python scripts/cli.py <command> --help
```

---

## 📋 Core Commands

### **sync** - Semantic Content Crawling
Unified workflow for web crawling, content analysis, and vector storage.

```bash
python scripts/cli.py sync [OPTIONS]
```

#### **Options**
- `--input FILE` - Input file containing URLs to crawl
- `--limit-domains INTEGER` - Maximum number of domains to crawl
- `--save-raw` - Save raw content alongside processed data
- `--proxy-rotate` - Enable rotating proxy middleware
- `--dry-run` - Simulate crawling without storing results
- `--threshold FLOAT` - Semantic similarity threshold (default: 0.75)
- `--retries INTEGER` - Maximum retry attempts per URL (default: 3)

#### **Examples**
```bash
# Basic crawling
python scripts/cli.py sync --input urls.txt

# Production crawling with limits
python scripts/cli.py sync --input urls.txt --limit-domains 10 --save-raw

# Test crawling
python scripts/cli.py sync --input test_urls.txt --dry-run
```

#### **Output**
- Progress indicators with Rich CLI formatting
- Crawl statistics and success rates
- Vector storage snapshot creation
- Semantic analysis results

---

### **health** - System Health Monitoring
Comprehensive system health assessment and monitoring.

```bash
python scripts/cli.py health [OPTIONS]
```

#### **Options**
- `--json` - Output in JSON format
- `--strict` - Enable strict validation mode
- `--component TEXT` - Check specific component only
- `--threshold FLOAT` - Health threshold percentage (default: 85)

#### **Examples**
```bash
# Basic health check
python scripts/cli.py health

# JSON output for monitoring
python scripts/cli.py health --json --strict

# Component-specific check
python scripts/cli.py health --component storage
```

#### **Health Components**
- **System Health**: Overall system status and check results
- **Drift Status**: Semantic drift analysis and thresholds
- **Freshness Status**: Content freshness and update intervals
- **Crawl Success Rate**: Web crawling success metrics
- **PII Status**: Privacy and sensitive data detection
- **Storage Health**: Vector database and file system status

---

### **search** - Content Search
Search through curated content using semantic similarity.

```bash
python scripts/cli.py search [OPTIONS]
```

#### **Options**
- `--query TEXT` - Search query string
- `--limit INTEGER` - Maximum number of results (default: 10)
- `--threshold FLOAT` - Similarity threshold (default: 0.7)
- `--format TEXT` - Output format (table, json, csv)
- `--since DATE` - Show results since date (YYYY-MM-DD)

#### **Examples**
```bash
# Basic search
python scripts/cli.py search --query "artificial intelligence"

# Limited results with threshold
python scripts/cli.py search --query "machine learning" --limit 5 --threshold 0.8

# JSON output
python scripts/cli.py search --query "technology" --format json
```

---

### **drift-report** - Semantic Drift Analysis
Generate reports on semantic drift and content evolution.

```bash
python scripts/cli.py drift-report [OPTIONS]
```

#### **Options**
- `--format TEXT` - Output format (markdown, json, csv)
- `--period INTEGER` - Analysis period in days (default: 7)
- `--threshold FLOAT` - Drift threshold (default: 2.0)
- `--output FILE` - Output file path

#### **Examples**
```bash
# Basic drift report
python scripts/cli.py drift-report

# JSON report for last 30 days
python scripts/cli.py drift-report --format json --period 30

# Export to file
python scripts/cli.py drift-report --output drift_analysis.md
```

---

## 🔧 Maintenance Commands

### **backup** - System Backup
Create comprehensive system backups including vector data and configuration.

```bash
python scripts/cli.py backup [OPTIONS]
```

#### **Options**
- `--destination PATH` - Backup destination directory
- `--include-logs` - Include log files in backup
- `--compress` - Compress backup archives
- `--encrypt` - Encrypt backup files

#### **Examples**
```bash
# Basic backup
python scripts/cli.py backup

# Encrypted backup with logs
python scripts/cli.py backup --destination /backup/intelforge --include-logs --encrypt
```

---

### **restore** - System Restore
Restore system from backups.

```bash
python scripts/cli.py restore [OPTIONS]
```

#### **Options**
- `--source PATH` - Backup source directory or file
- `--verify` - Verify restore integrity
- `--force` - Force restore without confirmation

#### **Examples**
```bash
# Basic restore
python scripts/cli.py restore --source /backup/intelforge

# Verified restore
python scripts/cli.py restore --source backup.tar.gz --verify
```

---

### **clean** - System Cleanup
Clean temporary files and optimize storage.

```bash
python scripts/cli.py clean [OPTIONS]
```

#### **Options**
- `--logs` - Clean old log files
- `--cache` - Clean cache directories
- `--temp` - Clean temporary files
- `--older-than INTEGER` - Clean files older than N days

#### **Examples**
```bash
# Clean all temporary files
python scripts/cli.py clean --temp --cache

# Clean old logs
python scripts/cli.py clean --logs --older-than 30
```

---

## 📊 Monitoring Commands

### **status** - System Status
Quick system status overview.

```bash
python scripts/cli.py status [OPTIONS]
```

#### **Options**
- `--detailed` - Show detailed status information
- `--json` - JSON output format

#### **Examples**
```bash
# Quick status
python scripts/cli.py status

# Detailed status
python scripts/cli.py status --detailed
```

---

### **logs** - Log Management
View and manage system logs.

```bash
python scripts/cli.py logs [OPTIONS]
```

#### **Options**
- `--component TEXT` - Show logs for specific component
- `--level TEXT` - Log level filter (DEBUG, INFO, WARNING, ERROR)
- `--tail INTEGER` - Show last N lines
- `--follow` - Follow log output

#### **Examples**
```bash
# View error logs
python scripts/cli.py logs --level ERROR

# Follow main log
python scripts/cli.py logs --component main --follow

# Last 100 lines
python scripts/cli.py logs --tail 100
```

---

## 🔐 Security Commands

### **security-scan** - Security Analysis
Run comprehensive security scans and audits.

```bash
python scripts/cli.py security-scan [OPTIONS]
```

#### **Options**
- `--pii` - Scan for PII in stored content
- `--vulnerabilities` - Check for security vulnerabilities
- `--audit` - Generate security audit report
- `--fix` - Automatically fix detected issues

#### **Examples**
```bash
# Full security scan
python scripts/cli.py security-scan --pii --vulnerabilities --audit

# PII scan only
python scripts/cli.py security-scan --pii
```

---

## 🛠️ Advanced Options

### **Global Options**
Available for all commands:

- `--verbose` - Enable verbose output
- `--quiet` - Suppress non-error output
- `--config PATH` - Custom configuration file path
- `--log-level TEXT` - Set logging level
- `--no-color` - Disable colored output

### **Environment Variables**
- `INTELFORGE_CONFIG` - Configuration file path
- `INTELFORGE_LOG_LEVEL` - Default log level
- `INTELFORGE_DATA_DIR` - Data directory path
- `INTELFORGE_CACHE_DIR` - Cache directory path

---

## 📝 Output Formats

### **Table Format** (Default)
Human-readable tables with Rich formatting:
```
┌─────────────────────┬─────────────────────┬─────────────────────┐
│ Component           │ Status              │ Details             │
├─────────────────────┼─────────────────────┼─────────────────────┤
│ System Health       │ ✅ Healthy          │ 31/35 checks passed │
│ Storage             │ ✅ Healthy          │ ChromaDB online     │
└─────────────────────┴─────────────────────┴─────────────────────┘
```

### **JSON Format**
Structured data for programmatic use:
```json
{
  "timestamp": "2025-07-16T13:47:26.049037",
  "overall_status": "healthy",
  "components": {
    "system_health": {
      "status": "healthy",
      "checks_passed": 31,
      "total_checks": 35
    }
  }
}
```

### **CSV Format**
Comma-separated values for data analysis:
```csv
component,status,details
system_health,healthy,31/35 checks passed
storage,healthy,ChromaDB online
```

---

## 🔄 Exit Codes

Commands return standard exit codes:
- `0` - Success
- `1` - General error
- `2` - Warning (operation completed with warnings)
- `3` - Configuration error
- `4` - Network error
- `5` - Storage error

---

## 📚 Examples

### **Daily Operations**
```bash
# Morning system check
python scripts/cli.py health --json --strict

# Run content crawling
python scripts/cli.py sync --input daily_urls.txt --limit-domains 20

# Check results
python scripts/cli.py search --query "today's content" --limit 5

# Evening cleanup
python scripts/cli.py clean --temp --logs --older-than 7
```

### **Monitoring Integration**
```bash
# CI/CD health check
python scripts/cli.py health --json --strict
if [ $? -eq 0 ]; then
  echo "System healthy"
else
  echo "System unhealthy"
  exit 1
fi

# Automated backup
python scripts/cli.py backup --destination /backup/$(date +%Y%m%d) --compress
```

### **Troubleshooting**
```bash
# Diagnostic information
python scripts/cli.py status --detailed
python scripts/cli.py logs --level ERROR --tail 50
python scripts/cli.py security-scan --audit

# System recovery
python scripts/cli.py restore --source /backup/latest --verify
python scripts/cli.py health --json --strict
```

---

## 💡 Tips and Best Practices

### **Performance Optimization**
- Use `--limit-domains` for large crawling operations
- Enable `--proxy-rotate` for better crawling success
- Use `--json` output for automated processing
- Monitor health regularly with `--strict` mode

### **Security Best Practices**
- Run `security-scan` regularly
- Monitor PII detection alerts
- Use encrypted backups for sensitive data
- Check audit logs weekly

### **Maintenance Recommendations**
- Run `clean` commands weekly
- Create backups before major operations
- Monitor drift reports for content quality
- Review health checks daily

---

*This CLI reference is part of IntelForge v1.0.0 production documentation suite.*
