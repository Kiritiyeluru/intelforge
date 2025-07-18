# IntelForge Troubleshooting Guide

**Document Version**: 1.0
**Created**: 2025-07-16
**Status**: Production-Ready
**Audience**: Users, administrators, and support personnel

---

## 🚀 Overview

This comprehensive troubleshooting guide covers common issues, diagnostic procedures, and solutions for IntelForge. Follow the systematic approach for efficient problem resolution.

### **Troubleshooting Methodology**
1. **Identify**: Determine the specific issue and symptoms
2. **Diagnose**: Use diagnostic tools and logs to understand the problem
3. **Isolate**: Narrow down the root cause
4. **Resolve**: Apply appropriate solutions
5. **Verify**: Confirm the issue is resolved
6. **Document**: Record the solution for future reference

---

## 🔍 Diagnostic Tools

### **Health Check Command**
```bash
# Comprehensive health check
python scripts/cli.py health --json --strict

# Component-specific health check
python scripts/cli.py health --component storage
python scripts/cli.py health --component crawling
```

### **System Status**
```bash
# Quick system status
python scripts/cli.py status --detailed

# Process verification
ps aux | grep python | grep intelforge
```

### **Log Analysis**
```bash
# View recent errors
python scripts/cli.py logs --level ERROR --tail 50

# Follow live logs
python scripts/cli.py logs --follow

# Component-specific logs
tail -f logs/intelforge.log
tail -f logs/monitoring.log
tail -f logs/vector_security_audit.log
```

---

## 🚨 Common Issues & Solutions

### **Environment and Setup Issues**

#### **Issue: Wrong Virtual Environment**
**Symptoms**:
- Missing package errors
- Import failures
- Degraded functionality

**Diagnosis**:
```bash
# Check current environment
which python
pip list | grep -E "(chromadb|scrapy|typer)"
```

**Solution**:
```bash
# Always use the correct environment
source venv/bin/activate  # NOT .venv/bin/activate
which python  # Should show /path/to/intelforge/venv/bin/python

# Verify packages are installed
pip list | grep chromadb
pip list | grep scrapy
pip list | grep sentence-transformers
```

**Prevention**: Always run `source venv/bin/activate` before any IntelForge commands.

---

#### **Issue: Missing Dependencies**
**Symptoms**:
- ModuleNotFoundError
- Import errors
- Features not working

**Diagnosis**:
```bash
# Check for specific packages
python -c "import chromadb; print('ChromaDB available')"
python -c "import scrapy; print('Scrapy available')"
python -c "import sentence_transformers; print('Sentence Transformers available')"
```

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check for conflicts
pip check

# Verify installation
python scripts/cli.py health --component system
```

---

#### **Issue: GPU Not Detected**
**Symptoms**:
- CUDA not available warnings
- Slow embedding generation
- CPU-only processing

**Diagnosis**:
```bash
# Check GPU availability
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import torch; print(f'CUDA device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"
nvidia-smi
```

**Solution**:
```bash
# Verify CUDA installation
nvidia-smi

# Check PyTorch CUDA support
python -c "import torch; print(torch.version.cuda)"

# Reinstall PyTorch with CUDA (if needed)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

### **Health Check Failures**

#### **Issue: Health Check Below Threshold**
**Symptoms**:
- Health percentage < 85%
- System status "degraded"
- Multiple check failures

**Diagnosis**:
```bash
# Detailed health check
python scripts/cli.py health --json --strict | jq '.checks'

# Check specific components
python scripts/cli.py health --component system_health
python scripts/cli.py health --component storage_health
```

**Solution**:
```bash
# Address specific failures based on health check output
# Common fixes:
# 1. Restart services
# 2. Clear cache
# 3. Check disk space
# 4. Verify network connectivity

# Verify resolution
python scripts/cli.py health --json --strict
```

---

#### **Issue: Critical Health Failures**
**Symptoms**:
- Critical failures > 0
- System unusable
- Services not responding

**Diagnosis**:
```bash
# Check for critical failures
python scripts/cli.py health --json --strict | jq '.checks.system_health.details.critical_failures'

# Review error logs
python scripts/cli.py logs --level ERROR --tail 100
```

**Solution**:
```bash
# Emergency recovery procedure
# 1. Stop all processes
pkill -f intelforge

# 2. Restart services
source venv/bin/activate
python scripts/cli.py health --json --strict

# 3. Check logs for errors
tail -f logs/intelforge_errors.log
```

---

### **Crawling Issues**

#### **Issue: Crawling Failures**
**Symptoms**:
- Low crawl success rate
- Timeout errors
- Empty results

**Diagnosis**:
```bash
# Check crawl success rate
python scripts/cli.py health --component crawling

# Review crawl logs
tail -f logs/semantic_spider.log

# Test specific URL
python scripts/cli.py sync --input test_url.txt --dry-run
```

**Solution**:
```bash
# Adjust crawling settings
# 1. Increase timeout
# 2. Reduce concurrent requests
# 3. Add delays between requests
# 4. Check robots.txt compliance

# Test with conservative settings
python scripts/cli.py sync --input test_url.txt --dry-run
```

---

#### **Issue: Proxy Configuration Problems**
**Symptoms**:
- "No proxies available" errors
- Blocked requests
- Proxy middleware failures

**Diagnosis**:
```bash
# Check proxy configuration
cat config/proxy_list.txt
grep -i proxy logs/semantic_spider.log
```

**Solution**:
```bash
# Option 1: Disable proxy rotation
# Edit crawling configuration to disable rotating_proxies middleware

# Option 2: Configure proxy list
echo "http://proxy1:8080" > config/proxy_list.txt
echo "http://proxy2:8080" >> config/proxy_list.txt

# Option 3: Use without proxies (acceptable for Phase 1)
python scripts/cli.py sync --input urls.txt  # System works without proxies
```

---

### **Storage Issues**

#### **Issue: ChromaDB Connection Problems**
**Symptoms**:
- Storage health failures
- Vector operations failing
- Database not accessible

**Diagnosis**:
```bash
# Check storage health
python scripts/cli.py health --component storage

# Check ChromaDB directory
ls -la chroma_storage/
du -sh chroma_storage/

# Test direct connection
python -c "import chromadb; client = chromadb.PersistentClient(path='chroma_storage'); print(client.list_collections())"
```

**Solution**:
```bash
# Restart ChromaDB
# 1. Stop processes using ChromaDB
# 2. Check for file locks
lsof | grep chroma

# 3. Restart IntelForge
source venv/bin/activate
python scripts/cli.py health --component storage
```

---

#### **Issue: Vector Storage Full**
**Symptoms**:
- Disk space errors
- Storage operations failing
- Performance degradation

**Diagnosis**:
```bash
# Check disk space
df -h
du -sh chroma_storage/
du -sh logs/

# Check vector count
python scripts/cli.py status --detailed
```

**Solution**:
```bash
# Clean old data
python scripts/cli.py clean --older-than 30

# Archive old vectors
python scripts/cli.py backup --destination /backup/vectors/$(date +%Y%m%d)

# Monitor storage usage
watch -n 60 'df -h'
```

---

### **Security Issues**

#### **Issue: PII Detection Failures**
**Symptoms**:
- PII detected in content
- Security alerts
- Compliance violations

**Diagnosis**:
```bash
# Check PII status
python scripts/cli.py health --component pii_status

# Review security audit logs
tail -f logs/vector_security_audit.log

# Run PII scan
python scripts/cli.py security-scan --pii
```

**Solution**:
```bash
# Enable PII detection
# Verify configuration in config/security.json

# Clean detected PII
python scripts/cli.py security-scan --pii --fix

# Monitor ongoing PII detection
python scripts/cli.py health --component pii_status
```

---

#### **Issue: Encryption Key Problems**
**Symptoms**:
- Encryption failures
- Key file not found
- Decryption errors

**Diagnosis**:
```bash
# Check key file
ls -la config/vector_security.key
cat config/vector_security.key | wc -c  # Should be 44 characters

# Test encryption
python -c "from cryptography.fernet import Fernet; key = open('config/vector_security.key', 'rb').read(); f = Fernet(key); print('Key valid')"
```

**Solution**:
```bash
# Generate new key if needed
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" > config/vector_security.key
chmod 600 config/vector_security.key

# Verify key works
python scripts/cli.py health --component security
```

---

### **Monitoring Issues**

#### **Issue: Dashboard Not Accessible**
**Symptoms**:
- Dashboard won't load
- Connection refused
- Blank page

**Diagnosis**:
```bash
# Check if dashboard is running
lsof -i :8091
ps aux | grep -E "(dashboard|monitor)"

# Test local access
curl -I http://localhost:8091/monitoring_dashboard.html

# Check Tailscale status
tailscale status
```

**Solution**:
```bash
# Restart dashboard
pkill -f "python.*8091"

# Start dashboard
python3 -c "
import http.server
import socketserver
PORT = 8091
with socketserver.TCPServer(('0.0.0.0', PORT), http.server.SimpleHTTPRequestHandler) as httpd:
    print(f'Dashboard at http://localhost:{PORT}/monitoring_dashboard.html')
    httpd.serve_forever()
" &

# Verify access
curl -I http://localhost:8091/monitoring_dashboard.html
```

---

#### **Issue: Monitoring Data Not Updating**
**Symptoms**:
- Old timestamps
- Static health data
- No new alerts

**Diagnosis**:
```bash
# Check monitoring status
cat logs/monitoring_status.json | jq '.timestamp'

# Check monitoring process
ps aux | grep continuous_monitoring

# Test monitoring manually
python scripts/continuous_monitoring.py
```

**Solution**:
```bash
# Restart monitoring
pkill -f continuous_monitoring

# Run monitoring manually
python scripts/continuous_monitoring.py

# Check cron jobs
crontab -l | grep monitoring
```

---

### **Performance Issues**

#### **Issue: Slow Performance**
**Symptoms**:
- Long response times
- High CPU usage
- Memory exhaustion

**Diagnosis**:
```bash
# Check system resources
htop
free -h
df -h

# Check Python processes
ps aux | grep python | head -10

# Monitor performance
python scripts/cli.py logs --component performance
```

**Solution**:
```bash
# Optimize configuration
# 1. Reduce concurrent requests
# 2. Increase delays
# 3. Limit memory usage

# Clean up resources
python scripts/cli.py clean --temp --cache

# Restart services
pkill -f intelforge
source venv/bin/activate
```

---

#### **Issue: Memory Leaks**
**Symptoms**:
- Increasing memory usage
- System becoming unresponsive
- Out of memory errors

**Diagnosis**:
```bash
# Monitor memory usage
watch -n 5 'free -h'

# Check for memory leaks
python scripts/cli.py logs --component memory

# Process memory usage
ps aux --sort=-%mem | head -10
```

**Solution**:
```bash
# Restart services regularly
# Set up cron job for periodic restart

# Monitor memory usage
# Add memory usage alerts

# Optimize batch sizes
# Reduce concurrent operations
```

---

### **Network Issues**

#### **Issue: Network Connectivity Problems**
**Symptoms**:
- Crawling failures
- Timeout errors
- DNS resolution issues

**Diagnosis**:
```bash
# Test network connectivity
ping google.com
nslookup google.com

# Check firewall
sudo ufw status

# Test specific URLs
curl -I https://example.com
```

**Solution**:
```bash
# Check network configuration
# Verify DNS settings
# Test with different networks

# Adjust timeout settings
# Configure proxy if needed
```

---

#### **Issue: Tailscale VPN Problems**
**Symptoms**:
- Dashboard not accessible remotely
- VPN connection issues
- Device not reachable

**Diagnosis**:
```bash
# Check Tailscale status
tailscale status

# Test connectivity
ping 100.81.114.94

# Check firewall
sudo ufw status
```

**Solution**:
```bash
# Restart Tailscale
sudo systemctl restart tailscaled

# Re-authenticate
tailscale login

# Check device status
tailscale status
```

---

## 🔄 Recovery Procedures

### **Emergency Recovery**
```bash
# 1. Stop all processes
pkill -f intelforge

# 2. Backup current state
cp -r chroma_storage chroma_storage_backup_$(date +%Y%m%d_%H%M%S)

# 3. Restore from backup (if needed)
python scripts/cli.py restore --source /backup/latest

# 4. Verify system health
python scripts/cli.py health --json --strict

# 5. Restart services
source venv/bin/activate
python scripts/continuous_monitoring.py &
```

### **Data Recovery**
```bash
# Restore vector data
python scripts/cli.py restore --source /backup/vectors/latest --verify

# Restore configuration
cp /backup/config/* config/

# Verify integrity
python scripts/cli.py validate-config
python scripts/cli.py health --json --strict
```

---

## 📋 Maintenance Procedures

### **Daily Health Checks**
```bash
#!/bin/bash
# Daily health check script

echo "Daily IntelForge health check - $(date)"

# Activate environment
source venv/bin/activate

# Run health check
python scripts/cli.py health --json --strict

# Check disk space
df -h | grep -E "(/$|/home)"

# Check logs for errors
tail -n 50 logs/intelforge_errors.log

# Clean temporary files
python scripts/cli.py clean --temp --older-than 1

echo "Health check complete"
```

### **Weekly Maintenance**
```bash
#!/bin/bash
# Weekly maintenance script

echo "Weekly IntelForge maintenance - $(date)"

# Full system backup
python scripts/cli.py backup --destination /backup/weekly/$(date +%Y%m%d)

# Clean old logs
python scripts/cli.py clean --logs --older-than 7

# Security scan
python scripts/cli.py security-scan --audit

# Performance report
python scripts/cli.py drift-report --period 7 --output weekly_report.md

echo "Weekly maintenance complete"
```

---

## 💡 Best Practices

### **Prevention**
- Monitor health checks daily
- Set up automated backups
- Use appropriate resource limits
- Keep dependencies updated
- Follow security best practices

### **Documentation**
- Document all configuration changes
- Keep troubleshooting logs
- Record solutions for future reference
- Maintain runbooks for common procedures

### **Monitoring**
- Set up appropriate alerts
- Monitor resource usage
- Track performance metrics
- Review security logs regularly

---

## 🆘 Getting Help

### **Information to Collect**
When reporting issues, include:
1. **Error message**: Exact error text
2. **Health check**: Output of `python scripts/cli.py health --json --strict`
3. **System info**: OS, Python version, hardware specs
4. **Logs**: Relevant log entries from `logs/` directory
5. **Configuration**: Relevant configuration files (sanitized)
6. **Steps to reproduce**: Exact commands and procedures

### **Escalation Process**
1. **Level 1**: Check this troubleshooting guide
2. **Level 2**: Review logs and run diagnostics
3. **Level 3**: Consult system administrator
4. **Level 4**: Contact technical support

---

## 📚 Reference

### **Useful Commands**
```bash
# Quick diagnostics
python scripts/cli.py health --json --strict
python scripts/cli.py status --detailed
python scripts/cli.py logs --level ERROR --tail 50

# Process management
ps aux | grep intelforge
pkill -f intelforge
lsof -i :8091

# System resources
df -h
free -h
htop

# Network diagnostics
tailscale status
ping google.com
curl -I http://localhost:8091
```

### **Log Files**
- `logs/intelforge.log` - Main application log
- `logs/intelforge_errors.log` - Error log
- `logs/monitoring.log` - Monitoring system log
- `logs/alerts.log` - Alert notifications
- `logs/vector_security_audit.log` - Security audit log
- `logs/semantic_spider.log` - Crawling log

---

*This troubleshooting guide is part of IntelForge v1.0.0 production documentation suite.*
