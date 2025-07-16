# IntelForge Daily Operations Runbook

**Document Version**: 1.0  
**Created**: 2025-07-16  
**Status**: Production-Ready  
**Audience**: System administrators and operations team  

---

## 🚀 Overview

This runbook provides step-by-step procedures for daily IntelForge operations, monitoring, and maintenance. Follow these procedures to ensure optimal system performance and reliability.

### **Daily Operations Schedule**
- **08:00** - Morning system health check
- **09:00** - Content crawling operations
- **12:00** - Midday monitoring review
- **15:00** - Afternoon maintenance tasks
- **18:00** - Evening health check and reporting
- **Continuous** - Automated monitoring and alerting

---

## 🌅 Morning Operations (08:00)

### **Step 1: System Health Check**
```bash
# Activate environment
source venv/bin/activate

# Comprehensive health check
python scripts/cli.py health --json --strict

# Expected output: overall_status: "healthy", health_percentage: >85%
```

**Health Check Evaluation**:
- ✅ **Healthy (>85%)**: Proceed with normal operations
- ⚠️ **Degraded (70-85%)**: Investigate warnings, proceed with caution
- ❌ **Critical (<70%)**: Follow emergency procedures, do not proceed

### **Step 2: Infrastructure Verification**
```bash
# Check system resources
df -h                    # Disk space should be <80% usage
free -h                  # Memory should be <80% usage
uptime                   # Load average should be <2.0

# Check critical services
lsof -i :8091           # Dashboard should be running
tailscale status        # VPN should be active
```

### **Step 3: Dashboard Access Verification**
```bash
# Test local dashboard access
curl -I http://localhost:8091/monitoring_dashboard.html

# Expected: HTTP/1.0 200 OK

# Test mobile access (if available)
curl -I http://100.81.114.94:8091/monitoring_dashboard.html
```

### **Step 4: Log Review**
```bash
# Check for overnight errors
tail -n 100 logs/intelforge_errors.log

# Review security audit (should be clean)
tail -n 50 logs/vector_security_audit.log

# Check alert log
tail -n 20 logs/alerts.log
```

### **Step 5: Morning Report**
```bash
# Generate morning status report
python scripts/cli.py status --detailed > daily_reports/morning_$(date +%Y%m%d).txt

# Check monitoring status
cat logs/monitoring_status.json | jq '.timestamp, .health_status.status'
```

---

## 🌐 Content Crawling Operations (09:00)

### **Step 1: Prepare URL Lists**
```bash
# Verify URL lists exist and are updated
ls -la url_lists/
wc -l url_lists/daily_urls.txt
```

### **Step 2: Pre-Crawl Validation**
```bash
# Test crawling configuration
python scripts/cli.py sync --input url_lists/test_urls.txt --dry-run

# Expected: No errors, simulation successful
```

### **Step 3: Execute Daily Crawling**
```bash
# Start crawling with production settings
python scripts/cli.py sync --input url_lists/daily_urls.txt --limit-domains 50 --save-raw

# Monitor crawling progress
tail -f logs/semantic_spider.log
```

### **Step 4: Crawling Verification**
```bash
# Check crawl success rate
python scripts/cli.py health --component crawling

# Expected: success_rate > 90%

# Review crawling statistics
grep -i "summary" logs/semantic_spider.log | tail -1
```

### **Step 5: Content Quality Check**
```bash
# Check for PII detection
python scripts/cli.py health --component pii_status

# Expected: pii_detected: false

# Verify content filtering
python scripts/cli.py search --query "test" --limit 5
```

---

## 🔍 Midday Monitoring Review (12:00)

### **Step 1: Performance Metrics**
```bash
# Check system performance
python scripts/cli.py logs --component performance --tail 50

# Review TTR metrics
ls -la logs/ttr/
tail -5 logs/ttr/ttr_report_*.md
```

### **Step 2: Storage Health**
```bash
# Check vector storage
python scripts/cli.py health --component storage

# Monitor storage usage
du -sh chroma_storage/
ls -la chroma_storage_snapshot_*/
```

### **Step 3: Alert Review**
```bash
# Check for new alerts
tail -n 10 logs/alerts.log

# Review monitoring dashboard
curl -s http://localhost:8091/logs/monitoring_status.json | jq '.health_status'
```

### **Step 4: Network Connectivity**
```bash
# Test external connectivity
ping -c 3 google.com
curl -I https://example.com

# Check Tailscale status
tailscale status | head -5
```

---

## 🔧 Afternoon Maintenance (15:00)

### **Step 1: Routine Cleanup**
```bash
# Clean temporary files
python scripts/cli.py clean --temp --older-than 1

# Clean cache if needed
python scripts/cli.py clean --cache --older-than 7
```

### **Step 2: Log Rotation**
```bash
# Check log sizes
ls -lh logs/

# Rotate large logs if needed (>100MB)
if [ $(stat -c%s logs/semantic_spider.log) -gt 104857600 ]; then
    mv logs/semantic_spider.log logs/semantic_spider.log.$(date +%Y%m%d)
    touch logs/semantic_spider.log
fi
```

### **Step 3: Security Maintenance**
```bash
# Run security scan
python scripts/cli.py security-scan --audit

# Check for PII in new content
python scripts/cli.py security-scan --pii

# Review security audit log
tail -n 20 logs/vector_security_audit.log
```

### **Step 4: Performance Optimization**
```bash
# Check for performance issues
python scripts/cli.py drift-report --period 1

# Monitor memory usage
free -h
ps aux --sort=-%mem | head -5
```

---

## 🌆 Evening Operations (18:00)

### **Step 1: End-of-Day Health Check**
```bash
# Final health check
python scripts/cli.py health --json --strict

# Compare with morning health
diff daily_reports/morning_$(date +%Y%m%d).txt <(python scripts/cli.py status --detailed)
```

### **Step 2: Backup Operations**
```bash
# Create daily backup
python scripts/cli.py backup --destination daily_backups/$(date +%Y%m%d)

# Verify backup integrity
python scripts/cli.py backup --verify --source daily_backups/$(date +%Y%m%d)
```

### **Step 3: Daily Report Generation**
```bash
# Generate comprehensive daily report
cat > daily_reports/summary_$(date +%Y%m%d).md << EOF
# IntelForge Daily Report - $(date +%Y-%m-%d)

## System Health
$(python scripts/cli.py health)

## Crawling Statistics
$(grep -i "summary" logs/semantic_spider.log | tail -1)

## Storage Status
$(du -sh chroma_storage/)

## Alerts
$(tail -n 10 logs/alerts.log)

## Next Day Preparation
- [ ] URL lists updated
- [ ] System resources adequate
- [ ] No critical alerts
EOF
```

### **Step 4: Next Day Preparation**
```bash
# Prepare URL lists for tomorrow
cp url_lists/daily_urls.txt url_lists/daily_urls_$(date +%Y%m%d).txt

# Check system resources for tomorrow
df -h
free -h

# Verify automated monitoring is running
ps aux | grep continuous_monitoring
```

---

## 📊 Continuous Monitoring

### **Automated Monitoring Status**
```bash
# Check if monitoring is running
ps aux | grep continuous_monitoring

# View recent monitoring logs
tail -f logs/monitoring.log

# Check cron jobs
crontab -l | grep -i intelforge
```

### **Alert Response Procedures**

#### **Critical Alerts**
1. **Immediate response required**
2. **Check health status**: `python scripts/cli.py health --json --strict`
3. **Review error logs**: `tail -n 100 logs/intelforge_errors.log`
4. **Escalate if needed**: Contact system administrator

#### **Warning Alerts**
1. **Response within 15 minutes**
2. **Monitor for escalation**
3. **Document investigation**
4. **Implement preventive measures**

### **Dashboard Monitoring**
- **URL**: http://localhost:8091/monitoring_dashboard.html
- **Mobile**: http://100.81.114.94:8091/monitoring_dashboard.html
- **Refresh**: Every 30 seconds
- **Key Metrics**: Health percentage, storage status, alert count

---

## 📋 Weekly Tasks (Sundays)

### **Weekly Maintenance**
```bash
# Comprehensive backup
python scripts/cli.py backup --destination weekly_backups/$(date +%Y%m%d) --include-logs

# Clean old logs
python scripts/cli.py clean --logs --older-than 7

# Security audit
python scripts/cli.py security-scan --audit --vulnerabilities

# Performance report
python scripts/cli.py drift-report --period 7 --output weekly_reports/performance_$(date +%Y%m%d).md
```

### **Weekly Report**
```bash
# Generate weekly summary
cat > weekly_reports/summary_$(date +%Y%m%d).md << EOF
# IntelForge Weekly Report - Week of $(date +%Y-%m-%d)

## System Uptime
$(uptime)

## Weekly Statistics
- URLs Crawled: $(grep -c "crawled" logs/semantic_spider.log)
- Health Check Average: $(grep "Health Status" logs/monitoring.log | tail -7 | grep -o "[0-9.]*%" | awk '{sum += $1} END {print sum/NR "%"}')
- Alerts Generated: $(wc -l < logs/alerts.log)

## Storage Growth
$(du -sh chroma_storage/)

## Recommendations
- [ ] Review performance trends
- [ ] Update URL lists
- [ ] Check for system updates
EOF
```

---

## 🚨 Emergency Procedures

### **System Unresponsive**
```bash
# 1. Check system resources
top
df -h

# 2. Check IntelForge processes
ps aux | grep intelforge

# 3. Emergency restart
pkill -f intelforge
source venv/bin/activate
python scripts/cli.py health --json --strict
```

### **Storage Full**
```bash
# 1. Check disk usage
df -h
du -sh chroma_storage/

# 2. Emergency cleanup
python scripts/cli.py clean --temp --cache --older-than 1

# 3. Archive old data
python scripts/cli.py backup --destination emergency_backup/$(date +%Y%m%d_%H%M%S)
```

### **Health Check Failures**
```bash
# 1. Run detailed diagnostics
python scripts/cli.py health --json --strict

# 2. Check component health
python scripts/cli.py health --component storage
python scripts/cli.py health --component crawling

# 3. Review logs
tail -n 100 logs/intelforge_errors.log
```

---

## 📝 Documentation Requirements

### **Daily Documentation**
- Morning health check results
- Crawling statistics and issues
- Alert responses and resolutions
- System resource usage
- Backup verification

### **Incident Documentation**
- Issue description and symptoms
- Diagnostic steps taken
- Resolution applied
- Preventive measures implemented
- Follow-up actions required

### **Change Documentation**
- Configuration changes made
- Reason for changes
- Impact assessment
- Rollback procedures
- Testing results

---

## 📚 Reference Information

### **Key File Locations**
- **Configurations**: `config/`
- **Logs**: `logs/`
- **Backups**: `daily_backups/`, `weekly_backups/`
- **Reports**: `daily_reports/`, `weekly_reports/`
- **URL Lists**: `url_lists/`

### **Important Commands**
```bash
# Health check
python scripts/cli.py health --json --strict

# Crawling
python scripts/cli.py sync --input urls.txt --dry-run

# Backup
python scripts/cli.py backup --destination backup_dir

# Cleanup
python scripts/cli.py clean --temp --older-than 1

# Security
python scripts/cli.py security-scan --audit
```

### **Contact Information**
- **System Administrator**: [Contact Info]
- **Technical Support**: [Contact Info]
- **Emergency Contact**: [Contact Info]

---

## ✅ Daily Checklist

### **Morning (08:00)**
- [ ] System health check completed
- [ ] Infrastructure verification passed
- [ ] Dashboard access verified
- [ ] Log review completed
- [ ] Morning report generated

### **Crawling (09:00)**
- [ ] URL lists prepared
- [ ] Pre-crawl validation passed
- [ ] Daily crawling executed
- [ ] Crawling verification completed
- [ ] Content quality checked

### **Midday (12:00)**
- [ ] Performance metrics reviewed
- [ ] Storage health checked
- [ ] Alert review completed
- [ ] Network connectivity verified

### **Afternoon (15:00)**
- [ ] Routine cleanup completed
- [ ] Log rotation performed
- [ ] Security maintenance done
- [ ] Performance optimization checked

### **Evening (18:00)**
- [ ] End-of-day health check completed
- [ ] Backup operations performed
- [ ] Daily report generated
- [ ] Next day preparation done

---

*This daily operations runbook is part of IntelForge v1.0.0 production documentation suite.*