# IntelForge Incident Response Runbook

**Document Version**: 1.0  
**Created**: 2025-07-16  
**Status**: Production-Ready  
**Audience**: System administrators and incident response team  

---

## 🚨 Overview

This runbook provides procedures for responding to IntelForge system incidents, including detection, assessment, response, and recovery. Follow these procedures to minimize downtime and ensure system reliability.

### **Incident Severity Levels**
- **Critical (P1)**: System unusable, data loss risk, security breach
- **High (P2)**: Major functionality impaired, performance severely degraded
- **Medium (P3)**: Minor functionality issues, workarounds available
- **Low (P4)**: Cosmetic issues, documentation problems

### **Response Time Targets**
- **Critical**: 5 minutes
- **High**: 15 minutes
- **Medium**: 1 hour
- **Low**: 4 hours

---

## 🔍 Incident Detection

### **Automated Detection**
```bash
# Check monitoring alerts
tail -f logs/alerts.log

# Review health check failures
python scripts/cli.py health --json --strict | jq '.overall_status'

# Monitor dashboard alerts
curl -s http://localhost:8091/logs/monitoring_status.json | jq '.health_status.status'
```

### **Manual Detection**
```bash
# System unresponsive
curl -I http://localhost:8091/monitoring_dashboard.html

# Application errors
tail -n 50 logs/intelforge_errors.log

# Performance issues
top
free -h
df -h
```

### **User Reports**
- Dashboard not accessible
- Crawling failures
- Search results empty
- System slow response

---

## 📊 Incident Assessment

### **Initial Assessment Checklist**
```bash
# 1. Check system health
python scripts/cli.py health --json --strict

# 2. Verify core services
ps aux | grep intelforge
lsof -i :8091

# 3. Check system resources
df -h
free -h
uptime

# 4. Review recent logs
tail -n 100 logs/intelforge_errors.log
tail -n 50 logs/monitoring.log
```

### **Severity Assessment Matrix**

| Impact | Urgency | Severity |
|--------|---------|----------|
| High | High | Critical (P1) |
| High | Medium | High (P2) |
| Medium | High | High (P2) |
| Medium | Medium | Medium (P3) |
| Low | Any | Low (P4) |

### **Impact Assessment**
- **High**: System unusable, multiple users affected
- **Medium**: Partial functionality, some users affected
- **Low**: Minor issues, few users affected

---

## 🚨 Critical Incidents (P1)

### **System Completely Down**

#### **Symptoms**
- Health check fails completely
- Dashboard not accessible
- All services unresponsive
- Monitoring alerts critical

#### **Response Procedure**
```bash
# Step 1: Immediate assessment (within 2 minutes)
ps aux | grep intelforge
systemctl status
df -h
free -h

# Step 2: Emergency restart (within 5 minutes)
pkill -f intelforge
source venv/bin/activate

# Step 3: Verify virtual environment
which python
pip list | grep -E "(chromadb|scrapy|typer)"

# Step 4: Restart core services
python scripts/cli.py health --json --strict

# Step 5: Start monitoring
python scripts/continuous_monitoring.py &

# Step 6: Verify dashboard
curl -I http://localhost:8091/monitoring_dashboard.html
```

#### **Recovery Verification**
```bash
# Health check must pass
python scripts/cli.py health --json --strict
# Expected: overall_status: "healthy"

# Dashboard accessible
curl -I http://localhost:8091/monitoring_dashboard.html
# Expected: HTTP/1.0 200 OK

# Monitoring active
ps aux | grep continuous_monitoring
```

---

### **Data Corruption**

#### **Symptoms**
- Vector storage errors
- Data integrity check failures
- Inconsistent search results
- Storage health failures

#### **Response Procedure**
```bash
# Step 1: Stop all operations immediately
pkill -f intelforge

# Step 2: Assess damage
python -c "
import chromadb
try:
    client = chromadb.PersistentClient(path='chroma_storage')
    collections = client.list_collections()
    print(f'Collections: {len(collections)}')
except Exception as e:
    print(f'Error: {e}')
"

# Step 3: Backup current state
cp -r chroma_storage chroma_storage_corrupted_$(date +%Y%m%d_%H%M%S)

# Step 4: Restore from latest backup
python scripts/cli.py restore --source daily_backups/$(date +%Y%m%d) --verify

# Step 5: Verify restoration
python scripts/cli.py health --component storage
```

#### **Data Recovery Steps**
1. **Assess corruption scope**
2. **Isolate corrupted data**
3. **Restore from backup**
4. **Verify data integrity**
5. **Resume operations**

---

### **Security Breach**

#### **Symptoms**
- Unauthorized access alerts
- PII detection failures
- Security audit violations
- Suspicious network activity

#### **Response Procedure**
```bash
# Step 1: Immediate isolation
pkill -f intelforge
# Block network access if needed

# Step 2: Security assessment
python scripts/cli.py security-scan --audit --vulnerabilities

# Step 3: Check for PII exposure
python scripts/cli.py security-scan --pii

# Step 4: Review audit logs
tail -n 200 logs/vector_security_audit.log

# Step 5: Change security keys
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" > config/vector_security.key.new
mv config/vector_security.key.new config/vector_security.key
chmod 600 config/vector_security.key
```

#### **Security Incident Protocol**
1. **Contain the breach**
2. **Assess the impact**
3. **Collect evidence**
4. **Notify stakeholders**
5. **Implement fixes**
6. **Monitor for recurrence**

---

## ⚠️ High Priority Incidents (P2)

### **Performance Degradation**

#### **Symptoms**
- Slow response times
- High CPU/memory usage
- Timeout errors
- Health check warnings

#### **Response Procedure**
```bash
# Step 1: Identify bottleneck
top
htop
iotop

# Step 2: Check processes
ps aux --sort=-%cpu | head -10
ps aux --sort=-%mem | head -10

# Step 3: Optimize performance
python scripts/cli.py clean --temp --cache

# Step 4: Restart services if needed
pkill -f intelforge
source venv/bin/activate
python scripts/cli.py health --json --strict
```

#### **Performance Optimization**
- Reduce concurrent operations
- Clear cache and temporary files
- Optimize database queries
- Restart services to clear memory

---

### **Storage Issues**

#### **Symptoms**
- Disk space full
- Vector storage errors
- Backup failures
- Storage health warnings

#### **Response Procedure**
```bash
# Step 1: Check disk usage
df -h
du -sh chroma_storage/
du -sh logs/

# Step 2: Emergency cleanup
python scripts/cli.py clean --logs --older-than 7
python scripts/cli.py clean --temp --cache

# Step 3: Archive old data
python scripts/cli.py backup --destination emergency_archive/$(date +%Y%m%d_%H%M%S)

# Step 4: Verify storage health
python scripts/cli.py health --component storage
```

#### **Storage Recovery**
1. **Identify storage issues**
2. **Free up space**
3. **Archive old data**
4. **Verify operations**

---

### **Crawling Failures**

#### **Symptoms**
- Low crawl success rate
- Network connectivity issues
- Proxy failures
- Robots.txt violations

#### **Response Procedure**
```bash
# Step 1: Check crawling health
python scripts/cli.py health --component crawling

# Step 2: Test connectivity
ping google.com
curl -I https://example.com

# Step 3: Check proxy configuration
cat config/proxy_list.txt
grep -i proxy logs/semantic_spider.log | tail -10

# Step 4: Test crawling
python scripts/cli.py sync --input test_urls.txt --dry-run
```

#### **Crawling Recovery**
- Verify network connectivity
- Check proxy configuration
- Adjust crawling parameters
- Test with minimal settings

---

## 🔧 Medium Priority Incidents (P3)

### **Monitoring Issues**

#### **Symptoms**
- Dashboard not updating
- Monitoring alerts not working
- Stale monitoring data
- Cron job failures

#### **Response Procedure**
```bash
# Step 1: Check monitoring process
ps aux | grep continuous_monitoring

# Step 2: Restart monitoring
pkill -f continuous_monitoring
python scripts/continuous_monitoring.py &

# Step 3: Check cron jobs
crontab -l | grep intelforge
tail -f logs/cron_monitoring.log

# Step 4: Verify dashboard
curl -I http://localhost:8091/monitoring_dashboard.html
```

---

### **Configuration Issues**

#### **Symptoms**
- Invalid configuration errors
- Service start failures
- Feature not working
- Permission errors

#### **Response Procedure**
```bash
# Step 1: Validate configuration
python scripts/cli.py validate-config

# Step 2: Check permissions
ls -la config/
chmod 600 config/vector_security.key
chmod 644 config/*.json

# Step 3: Test configuration
python scripts/cli.py test-config --environment production

# Step 4: Restart services
source venv/bin/activate
python scripts/cli.py health --json --strict
```

---

## 📝 Incident Documentation

### **Incident Report Template**
```markdown
# Incident Report - INC-YYYYMMDD-HHMMSS

## Incident Summary
- **Date/Time**: 
- **Severity**: 
- **Duration**: 
- **Impact**: 
- **Root Cause**: 

## Timeline
- **Detection**: 
- **Response**: 
- **Resolution**: 
- **Verification**: 

## Actions Taken
1. 
2. 
3. 

## Root Cause Analysis
- **Primary Cause**: 
- **Contributing Factors**: 
- **System Weaknesses**: 

## Resolution
- **Immediate Fix**: 
- **Verification Steps**: 
- **Monitoring**: 

## Prevention Measures
- **Preventive Actions**: 
- **Monitoring Improvements**: 
- **Process Changes**: 

## Lessons Learned
- **What Worked Well**: 
- **What Could Be Improved**: 
- **Follow-up Actions**: 
```

### **Post-Incident Review**
```bash
# Generate incident report
cat > incident_reports/INC-$(date +%Y%m%d_%H%M%S).md << 'EOF'
# Incident Report Template
EOF

# Collect system state
python scripts/cli.py status --detailed > incident_reports/system_state_$(date +%Y%m%d_%H%M%S).txt

# Archive logs
cp logs/intelforge_errors.log incident_reports/errors_$(date +%Y%m%d_%H%M%S).log
cp logs/monitoring.log incident_reports/monitoring_$(date +%Y%m%d_%H%M%S).log
```

---

## 📊 Escalation Procedures

### **Escalation Matrix**
| Severity | Initial Response | Escalation 1 | Escalation 2 |
|----------|------------------|--------------|--------------|
| Critical | Immediate | 15 minutes | 30 minutes |
| High | 15 minutes | 1 hour | 4 hours |
| Medium | 1 hour | 4 hours | 24 hours |
| Low | 4 hours | 24 hours | 48 hours |

### **Escalation Contacts**
- **Level 1**: System Administrator
- **Level 2**: Technical Lead
- **Level 3**: Management
- **Emergency**: 24/7 Support

### **Escalation Triggers**
- Response time targets missed
- Multiple failed resolution attempts
- Recurring incidents
- Security-related incidents

---

## 🔄 Recovery Procedures

### **Service Recovery**
```bash
# Standard recovery procedure
pkill -f intelforge
source venv/bin/activate
python scripts/cli.py health --json --strict
python scripts/continuous_monitoring.py &

# Verify recovery
python scripts/cli.py status --detailed
curl -I http://localhost:8091/monitoring_dashboard.html
```

### **Data Recovery**
```bash
# Restore from backup
python scripts/cli.py restore --source daily_backups/$(date +%Y%m%d)

# Verify integrity
python scripts/cli.py health --component storage

# Resume operations
python scripts/cli.py health --json --strict
```

### **Full System Recovery**
```bash
# Emergency full recovery
# 1. Stop all processes
pkill -f intelforge

# 2. Restore configuration
cp /backup/config/* config/

# 3. Restore data
python scripts/cli.py restore --source /backup/latest --verify

# 4. Restart services
source venv/bin/activate
python scripts/cli.py health --json --strict

# 5. Verify full functionality
python scripts/cli.py sync --input test_urls.txt --dry-run
```

---

## 📋 Incident Prevention

### **Proactive Monitoring**
- Daily health checks
- Resource usage monitoring
- Security scans
- Performance trending

### **System Hardening**
- Regular backups
- Security updates
- Configuration validation
- Capacity planning

### **Process Improvements**
- Automated testing
- Change management
- Documentation updates
- Training programs

---

## 📚 Reference Information

### **Emergency Commands**
```bash
# System status
python scripts/cli.py health --json --strict
python scripts/cli.py status --detailed

# Service management
pkill -f intelforge
ps aux | grep intelforge
lsof -i :8091

# Resource checking
df -h
free -h
top

# Log review
tail -n 100 logs/intelforge_errors.log
tail -f logs/monitoring.log
```

### **Recovery Scripts**
```bash
# Quick recovery
./scripts/emergency_recovery.sh

# Full recovery
./scripts/full_system_recovery.sh

# Health verification
./scripts/verify_recovery.sh
```

### **Contact Information**
- **System Administrator**: [Contact]
- **Technical Support**: [Contact]
- **Emergency Hotline**: [Contact]
- **Management**: [Contact]

---

*This incident response runbook is part of IntelForge v1.0.0 production documentation suite.*