# IntelForge v1.0.0 - Getting Started Guide

**Document Version**: 1.0  
**Created**: 2025-07-16  
**Status**: Production-Ready  
**Audience**: New users and system administrators  

---

## 🚀 Welcome to IntelForge

IntelForge is an enterprise-grade semantic content curation system that intelligently crawls, analyzes, and curates web content using advanced AI and vector search technologies.

### **System Overview**
- **Purpose**: Semantic web content curation with AI-powered relevance filtering
- **Architecture**: ChromaDB vector storage + Scrapy crawling + Sentence Transformers
- **Security**: Enterprise-grade encryption, PII detection, and audit logging
- **Status**: Production-Battle-Hardened (98/100 readiness score)

---

## 📋 Prerequisites

### **System Requirements**
- **Operating System**: Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.8+ (Python 3.12 recommended)
- **Memory**: 8GB RAM minimum, 16GB recommended
- **Storage**: 10GB available space
- **Network**: Internet connection for web crawling

### **Hardware Recommendations**
- **CPU**: 4+ cores for concurrent crawling
- **GPU**: NVIDIA GPU with CUDA support (optional, for acceleration)
- **Storage**: SSD preferred for vector database performance

---

## 🔧 Installation

### **Step 1: Clone and Setup**
```bash
git clone <repository-url>
cd intelforge
```

### **Step 2: Virtual Environment Setup**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment (CRITICAL: Use 'venv' not '.venv')
source venv/bin/activate

# Verify correct environment
which python
# Should show: /path/to/intelforge/venv/bin/python
```

### **Step 3: Install Dependencies**
```bash
# Install all dependencies
pip install -r requirements.txt

# Verify critical packages
pip list | grep -E "(chromadb|scrapy|sentence-transformers|typer|rich)"
```

### **Step 4: Configuration**
```bash
# Create configuration directory
mkdir -p config logs

# Generate security keys
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" > config/vector_security.key
chmod 600 config/vector_security.key
```

### **Step 5: Initial System Test**
```bash
# Test system health
python scripts/cli.py health --json --strict

# Expected output: {"overall_status": "healthy", ...}
```

---

## 🎯 Quick Start

### **Your First Crawl**
```bash
# Create a test URL list
echo "https://example.com" > test_urls.txt

# Run semantic crawling (dry run)
python scripts/cli.py sync --input test_urls.txt --dry-run

# Run actual crawling
python scripts/cli.py sync --input test_urls.txt
```

### **Check Results**
```bash
# Check system health
python scripts/cli.py health

# View crawl results
python scripts/cli.py search --query "example content"

# Generate reports
python scripts/cli.py drift-report
```

---

## 🖥️ CLI Commands Overview

### **Core Commands**
- `python scripts/cli.py sync` - Run semantic crawling and content curation
- `python scripts/cli.py health` - Check system health and status
- `python scripts/cli.py search` - Search curated content
- `python scripts/cli.py drift-report` - Generate semantic drift analysis

### **Maintenance Commands**
- `python scripts/cli.py backup` - Create system backups
- `python scripts/cli.py restore` - Restore from backups
- `python scripts/cli.py clean` - Clean temporary files

### **Common Flags**
- `--help` - Show detailed help for any command
- `--json` - Output in JSON format
- `--strict` - Enable strict validation mode
- `--dry-run` - Simulate operations without making changes

---

## 📊 Monitoring & Health

### **System Health Monitoring**
```bash
# Basic health check
python scripts/cli.py health

# Detailed health check with JSON output
python scripts/cli.py health --json --strict

# Expected health indicators:
# - Overall Status: healthy
# - System Health: 85%+ passing
# - Storage: ChromaDB and Qdrant online
# - Security: No PII detected
```

### **Web Dashboard**
- **URL**: `http://localhost:8091/monitoring_dashboard.html`
- **Mobile Access**: `http://100.81.114.94:8091/monitoring_dashboard.html` (via Tailscale)
- **Features**: Real-time health monitoring, performance metrics, alert status

### **Log Files**
- **Main Log**: `logs/intelforge.log`
- **Error Log**: `logs/intelforge_errors.log`
- **Monitoring Log**: `logs/monitoring.log`
- **Security Audit**: `logs/vector_security_audit.log`

---

## 🔐 Security

### **Security Features**
- **Encryption**: Fernet-based encryption for vector data at rest
- **PII Detection**: Automatic detection and sanitization of sensitive information
- **Audit Logging**: Comprehensive security event tracking
- **Access Control**: Role-based permissions framework

### **Security Best Practices**
1. **Keep security keys secure**: `config/vector_security.key` should be readable only by the system user
2. **Regular updates**: Keep dependencies updated for security patches
3. **Monitor logs**: Check `logs/vector_security_audit.log` regularly
4. **Network security**: Use Tailscale VPN for remote access

---

## 🛠️ Troubleshooting

### **Common Issues**

#### **Issue: Wrong Virtual Environment**
```bash
# Problem: Using .venv instead of venv
# Solution: Always use the correct environment
source venv/bin/activate
which python  # Should show venv/bin/python
```

#### **Issue: Missing Dependencies**
```bash
# Problem: Package not found errors
# Solution: Verify and reinstall dependencies
pip list | grep chromadb
pip install -r requirements.txt
```

#### **Issue: GPU Not Detected**
```bash
# Problem: CUDA not available
# Solution: Verify GPU setup
python -c "import torch; print(torch.cuda.is_available())"
```

#### **Issue: Port Already in Use**
```bash
# Problem: Dashboard port conflicts
# Solution: Check and kill existing processes
lsof -i :8091
sudo kill -9 <process_id>
```

### **Health Check Failures**
- **Health < 85%**: Review failed checks in JSON output
- **Critical Failures**: Immediate investigation required
- **Storage Issues**: Check ChromaDB and disk space
- **Network Issues**: Verify internet connectivity

---

## 📚 Next Steps

### **For Users**
1. **Read CLI Reference**: `docs/CLI_REFERENCE.md` - Comprehensive command documentation
2. **Configuration Guide**: `docs/CONFIGURATION_GUIDE.md` - Advanced configuration options
3. **Troubleshooting Guide**: `docs/TROUBLESHOOTING.md` - Detailed problem resolution

### **For Administrators**
1. **Operational Runbooks**: `docs/runbooks/` - Daily operations and maintenance
2. **Deployment Guide**: `PRODUCTION_DEPLOYMENT_PLAN.md` - Production deployment procedures
3. **System Status**: `INTELFORGE_SYSTEM_STATUS.md` - Current system status and capabilities

### **For Developers**
1. **Technical Documentation**: `docs/TECHNICAL_REFERENCE.md` - System architecture and APIs
2. **Development Guide**: `docs/DEVELOPMENT.md` - Development environment setup
3. **API Reference**: `docs/API_REFERENCE.md` - Programmatic interface documentation

---

## 🆘 Support

### **Getting Help**
- **Documentation**: Check `docs/` directory for comprehensive guides
- **Logs**: Review log files in `logs/` directory for error details
- **Health Check**: Run `python scripts/cli.py health --json --strict` for system diagnosis

### **Reporting Issues**
1. **Check logs**: Review relevant log files
2. **Run health check**: Include health check output
3. **Document steps**: Provide exact commands and error messages
4. **System info**: Include OS, Python version, and hardware details

---

## 🎉 Conclusion

You're now ready to use IntelForge for semantic content curation! The system is production-ready with enterprise-grade security and monitoring.

**Key Reminders**:
- Always use `source venv/bin/activate` before running commands
- Monitor system health via dashboard or CLI
- Check logs regularly for any issues
- Keep security keys secure and updated

For detailed information on specific topics, refer to the comprehensive documentation in the `docs/` directory.

---

*This guide is part of IntelForge v1.0.0 production documentation suite.*