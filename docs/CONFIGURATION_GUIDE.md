# IntelForge Configuration Guide

**Document Version**: 1.0
**Created**: 2025-07-16
**Status**: Production-Ready
**Audience**: System administrators and advanced users

---

## 🚀 Overview

IntelForge uses a hierarchical configuration system supporting multiple formats and environments. This guide covers all configuration options, best practices, and production settings.

### **Configuration Hierarchy**
1. **Environment Variables** (highest priority)
2. **Configuration Files** (JSON, YAML, TOML)
3. **Command Line Arguments**
4. **Default Values** (lowest priority)

### **Configuration Directory Structure**
```
config/
├── production.json          # Production configuration
├── development.json         # Development configuration
├── security.json           # Security settings
├── crawling.json           # Crawling configuration
├── vector_security.key     # Encryption key (secure)
└── monitoring.json         # Monitoring configuration
```

---

## 🔧 Core Configuration

### **Main Configuration File**
**File**: `config/production.json`

```json
{
  "environment": "production",
  "debug": false,
  "log_level": "INFO",
  "data_directory": "data",
  "cache_directory": "cache",
  "log_directory": "logs",
  "vector_storage": {
    "provider": "chromadb",
    "connection_string": "chroma_storage",
    "collection_name": "semantic_capture",
    "embedding_model": "all-MiniLM-L6-v2",
    "dimension": 384,
    "distance_metric": "cosine"
  },
  "crawling": {
    "concurrent_requests": 2,
    "download_delay": 5,
    "randomize_delay": 0.5,
    "timeout": 30,
    "retries": 3,
    "robots_txt_obey": true,
    "user_agent": "IntelForge/1.0.0 (+https://github.com/user/intelforge)"
  },
  "security": {
    "encryption_enabled": true,
    "pii_detection": true,
    "audit_logging": true,
    "key_file": "config/vector_security.key"
  },
  "monitoring": {
    "health_check_interval": 300,
    "alert_threshold": 85,
    "metrics_retention_days": 30
  }
}
```

---

## 🗃️ Vector Storage Configuration

### **ChromaDB Configuration**
**File**: `config/vector_storage.json`

```json
{
  "chromadb": {
    "persist_directory": "chroma_storage",
    "collection_name": "semantic_capture",
    "embedding_function": "all-MiniLM-L6-v2",
    "settings": {
      "anonymized_telemetry": false,
      "allow_reset": false,
      "is_persistent": true
    },
    "metadata": {
      "hnsw:space": "cosine",
      "hnsw:construction_ef": 200,
      "hnsw:M": 16
    }
  },
  "qdrant": {
    "url": "http://localhost:6333",
    "collection_name": "semantic_capture",
    "vector_size": 384,
    "distance": "Cosine",
    "settings": {
      "on_disk_payload": true,
      "hnsw_config": {
        "m": 16,
        "ef_construct": 200
      }
    }
  }
}
```

### **Embedding Model Configuration**
```json
{
  "embedding": {
    "model_name": "all-MiniLM-L6-v2",
    "device": "auto",
    "batch_size": 32,
    "normalize_embeddings": true,
    "cache_folder": "models",
    "trust_remote_code": false
  }
}
```

---

## 🕷️ Crawling Configuration

### **Scrapy Settings**
**File**: `config/crawling.json`

```json
{
  "scrapy": {
    "BOT_NAME": "intelforge",
    "ROBOTSTXT_OBEY": true,
    "CONCURRENT_REQUESTS": 2,
    "DOWNLOAD_DELAY": 5,
    "RANDOMIZE_DOWNLOAD_DELAY": 0.5,
    "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
    "DOWNLOAD_TIMEOUT": 30,
    "RETRY_TIMES": 3,
    "DOWNLOAD_MAXSIZE": 1048576,
    "DEPTH_LIMIT": 3,
    "CLOSESPIDER_TIMEOUT": 3600,
    "CLOSESPIDER_ITEMCOUNT": 1000,
    "CLOSESPIDER_PAGECOUNT": 5000,
    "CLOSESPIDER_ERRORCOUNT": 50,
    "AUTOTHROTTLE_ENABLED": true,
    "AUTOTHROTTLE_START_DELAY": 1,
    "AUTOTHROTTLE_MAX_DELAY": 10,
    "AUTOTHROTTLE_TARGET_CONCURRENCY": 0.8,
    "MEMUSAGE_ENABLED": true,
    "MEMUSAGE_LIMIT_MB": 2048,
    "MEMUSAGE_WARNING_MB": 1024
  },
  "middleware": {
    "scrapy_fake_useragent": {
      "enabled": true,
      "priority": 400,
      "providers": ["scrapy_fake_useragent.providers.FakeUserAgentProvider"]
    },
    "rotating_proxies": {
      "enabled": true,
      "priority": 610,
      "proxy_list": "config/proxy_list.txt"
    },
    "trafilatura": {
      "enabled": true,
      "priority": 543,
      "config": {
        "include_comments": false,
        "include_tables": true,
        "include_formatting": false
      }
    }
  }
}
```

### **Content Filtering Configuration**
```json
{
  "content_filtering": {
    "language_detection": {
      "enabled": true,
      "confidence_threshold": 0.8,
      "target_language": "en"
    },
    "quality_filters": {
      "min_content_length": 100,
      "max_content_length": 50000,
      "remove_boilerplate": true,
      "semantic_threshold": 0.7
    },
    "content_types": {
      "allowed": ["text/html", "text/plain", "application/pdf"],
      "blocked": ["image/*", "video/*", "audio/*"]
    }
  }
}
```

---

## 🔐 Security Configuration

### **Security Settings**
**File**: `config/security.json`

```json
{
  "encryption": {
    "enabled": true,
    "algorithm": "fernet",
    "key_file": "config/vector_security.key",
    "key_rotation_days": 90,
    "encrypt_vectors": true,
    "encrypt_metadata": true
  },
  "pii_detection": {
    "enabled": true,
    "provider": "presidio",
    "confidence_threshold": 0.7,
    "entities": [
      "PERSON",
      "EMAIL_ADDRESS",
      "PHONE_NUMBER",
      "CREDIT_CARD",
      "SSN",
      "IP_ADDRESS"
    ],
    "anonymization": {
      "enabled": true,
      "method": "redact"
    }
  },
  "audit_logging": {
    "enabled": true,
    "log_file": "logs/vector_security_audit.log",
    "events": [
      "vector_insert",
      "vector_query",
      "vector_delete",
      "pii_detection",
      "security_violation"
    ]
  },
  "access_control": {
    "enabled": true,
    "default_permissions": "read",
    "admin_users": ["admin"],
    "rate_limiting": {
      "enabled": true,
      "requests_per_minute": 100
    }
  }
}
```

### **Network Security**
```json
{
  "network": {
    "tailscale": {
      "enabled": true,
      "dashboard_host": "100.81.114.94",
      "dashboard_port": 8091,
      "mobile_port": 8090
    },
    "ssl": {
      "enabled": false,
      "cert_file": "config/ssl/cert.pem",
      "key_file": "config/ssl/key.pem"
    },
    "cors": {
      "enabled": true,
      "origins": ["*"],
      "methods": ["GET", "POST"]
    }
  }
}
```

---

## 📊 Monitoring Configuration

### **Monitoring Settings**
**File**: `config/monitoring.json`

```json
{
  "health_checks": {
    "enabled": true,
    "interval_seconds": 300,
    "timeout_seconds": 120,
    "threshold_percentage": 85,
    "components": {
      "system_health": {
        "enabled": true,
        "checks": [
          "memory_usage",
          "disk_space",
          "cpu_usage",
          "network_connectivity"
        ]
      },
      "storage_health": {
        "enabled": true,
        "checks": [
          "chromadb_connection",
          "vector_count",
          "data_integrity"
        ]
      },
      "crawling_health": {
        "enabled": true,
        "success_rate_threshold": 90,
        "response_time_threshold": 30
      }
    }
  },
  "alerting": {
    "enabled": true,
    "cooldown_minutes": 15,
    "severity_levels": {
      "critical": {
        "threshold": 0,
        "escalation_minutes": 5
      },
      "warning": {
        "threshold": 85,
        "escalation_minutes": 15
      }
    },
    "notification_channels": {
      "log": {
        "enabled": true,
        "file": "logs/alerts.log"
      },
      "email": {
        "enabled": false,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "alerts@example.com",
        "recipients": ["admin@example.com"]
      }
    }
  },
  "metrics": {
    "enabled": true,
    "collection_interval": 60,
    "retention_days": 30,
    "export_format": "json",
    "export_directory": "logs/metrics"
  }
}
```

### **Dashboard Configuration**
```json
{
  "dashboard": {
    "enabled": true,
    "host": "0.0.0.0",
    "port": 8091,
    "refresh_interval": 30,
    "features": {
      "real_time_updates": true,
      "historical_data": true,
      "alert_notifications": true,
      "mobile_optimized": true
    },
    "authentication": {
      "enabled": false,
      "provider": "basic",
      "users": []
    }
  }
}
```

---

## 🌍 Environment Variables

### **Core Environment Variables**
```bash
# Application settings
export INTELFORGE_ENV=production
export INTELFORGE_DEBUG=false
export INTELFORGE_LOG_LEVEL=INFO

# Directories
export INTELFORGE_CONFIG_DIR=/path/to/config
export INTELFORGE_DATA_DIR=/path/to/data
export INTELFORGE_LOG_DIR=/path/to/logs

# Vector storage
export INTELFORGE_VECTOR_PROVIDER=chromadb
export INTELFORGE_VECTOR_CONNECTION=chroma_storage
export INTELFORGE_EMBEDDING_MODEL=all-MiniLM-L6-v2

# Security
export INTELFORGE_ENCRYPTION_ENABLED=true
export INTELFORGE_PII_DETECTION=true
export INTELFORGE_AUDIT_LOGGING=true

# Monitoring
export INTELFORGE_HEALTH_CHECK_INTERVAL=300
export INTELFORGE_ALERT_THRESHOLD=85
export INTELFORGE_DASHBOARD_PORT=8091

# Crawling
export INTELFORGE_CONCURRENT_REQUESTS=2
export INTELFORGE_DOWNLOAD_DELAY=5
export INTELFORGE_ROBOTS_TXT_OBEY=true
```

### **GPU Configuration**
```bash
# GPU settings
export CUDA_VISIBLE_DEVICES=0
export INTELFORGE_USE_GPU=true
export INTELFORGE_GPU_MEMORY_LIMIT=4096

# Model caching
export INTELFORGE_MODEL_CACHE_DIR=/path/to/models
export TRANSFORMERS_CACHE=/path/to/transformers
export HF_HOME=/path/to/huggingface
```

---

## 🚀 Production Configuration

### **Production Best Practices**
1. **Security**: Enable encryption, PII detection, and audit logging
2. **Performance**: Optimize concurrent requests and memory usage
3. **Monitoring**: Set up comprehensive health checks and alerting
4. **Backup**: Configure automated backups and retention policies
5. **Logging**: Set appropriate log levels and rotation

### **Production Configuration Template**
```json
{
  "environment": "production",
  "debug": false,
  "log_level": "INFO",
  "vector_storage": {
    "provider": "chromadb",
    "connection_string": "chroma_storage",
    "collection_name": "semantic_capture_prod"
  },
  "crawling": {
    "concurrent_requests": 4,
    "download_delay": 3,
    "timeout": 30,
    "robots_txt_obey": true
  },
  "security": {
    "encryption_enabled": true,
    "pii_detection": true,
    "audit_logging": true
  },
  "monitoring": {
    "health_check_interval": 300,
    "alert_threshold": 90,
    "metrics_retention_days": 90
  }
}
```

---

## 🔧 Advanced Configuration

### **Custom Pipelines**
```json
{
  "pipelines": {
    "content_processing": {
      "enabled": true,
      "steps": [
        "language_detection",
        "quality_filtering",
        "semantic_analysis",
        "vector_generation"
      ]
    },
    "security_scanning": {
      "enabled": true,
      "steps": [
        "pii_detection",
        "content_sanitization",
        "vulnerability_scan"
      ]
    }
  }
}
```

### **Plugin Configuration**
```json
{
  "plugins": {
    "content_extractors": {
      "trafilatura": {
        "enabled": true,
        "priority": 1
      },
      "newspaper3k": {
        "enabled": false,
        "priority": 2
      }
    },
    "vector_providers": {
      "chromadb": {
        "enabled": true,
        "priority": 1
      },
      "qdrant": {
        "enabled": false,
        "priority": 2
      }
    }
  }
}
```

---

## 📝 Configuration Validation

### **Validation Command**
```bash
# Validate configuration
python scripts/cli.py validate-config

# Validate specific configuration file
python scripts/cli.py validate-config --file config/production.json

# Test configuration
python scripts/cli.py test-config --environment production
```

### **Configuration Schema**
Configuration files are validated against JSON schemas located in `schemas/` directory.

---

## 🛠️ Troubleshooting Configuration

### **Common Issues**

#### **Configuration File Not Found**
```bash
# Check configuration directory
ls -la config/

# Use environment variable
export INTELFORGE_CONFIG_DIR=/path/to/config

# Specify config file
python scripts/cli.py --config config/production.json
```

#### **Invalid Configuration Values**
```bash
# Validate configuration
python scripts/cli.py validate-config

# Check logs for configuration errors
tail -f logs/intelforge.log | grep -i config
```

#### **Permission Issues**
```bash
# Check file permissions
ls -la config/
chmod 600 config/vector_security.key
chmod 644 config/*.json
```

---

## 💡 Configuration Tips

### **Development vs Production**
- Use separate configuration files for different environments
- Enable debug logging in development
- Use stricter security settings in production
- Adjust performance settings based on hardware

### **Security Considerations**
- Keep security keys in separate files with restricted permissions
- Use environment variables for sensitive values
- Enable audit logging for compliance
- Regularly rotate encryption keys

### **Performance Tuning**
- Adjust concurrent requests based on target websites
- Configure appropriate timeouts and retries
- Optimize memory usage for large datasets
- Use GPU acceleration when available

---

*This configuration guide is part of IntelForge v1.0.0 production documentation suite.*
