# IntelForge Crawl Job Planning & Scheduling Strategy

**Created**: 2025-07-19  
**Status**: Operational Planning  
**Priority**: High  

## Executive Summary

Following successful resolution of proxy middleware issues and establishment of functional crawling infrastructure, this document outlines the comprehensive job planning and scheduling strategy for IntelForge production crawling operations.

## Current Infrastructure Status

### ✅ **Operational Systems**
- **Crawling Engine**: Scrapy + Trafilatura integration functional
- **Proxy Configuration**: Disabled for public sites (stable operation)
- **Content Processing**: Semantic analysis with embeddings active
- **Storage Systems**: Qdrant vector storage + markdown files
- **Monitoring**: Comprehensive logging and reporting in place

### 📊 **Performance Baseline**
- **Success Rate**: 100% (after proxy fix)
- **Processing Speed**: ~1.75 URLs/second
- **Memory Usage**: 1.4GB peak (within 2GB limits)
- **Content Quality**: Semantic filtering with 0.75 threshold

## Target Lists Analysis

### Available Source Collections
1. **Finance Premium** (`config/targets_finance.txt`) - 35 URLs
2. **Academic Research** (`urls_academic_research.txt`) - TBD
3. **Technical Blogs** (`urls_technical_blogs.txt`) - TBD  
4. **GitHub Strategies** (`urls_github_strategies.txt`) - TBD
5. **Tier 1 Premium** (`urls_tier1_premium.txt`) - TBD

### Source Quality Assessment
- **Finance Premium**: Validated, high-quality algorithmic trading sources
- **Processing Time**: ~20 seconds for 35 URLs (baseline)
- **Content Yield**: High relevance for quantitative finance topics

## Proposed Job Schedules

### 🌙 **Nightly Operations (2:00 AM)**

#### **Primary Job: Finance Daily**
```bash
Job ID: finance-daily-2am
Schedule: 0 2 * * *
Command: /home/kiriti/alpha_projects/intelforge/cron/nightly_crawl.sh
Targets: config/targets_finance.txt
Duration: ~5 minutes
Output: crawl_ops/data_runs/YYYYMMDD/
```

**Rationale**: 
- Minimal server load at 2 AM
- Fresh daily content capture
- Established successful baseline

#### **Secondary Job: Research Weekly**
```bash
Job ID: research-weekly-2am
Schedule: 0 2 * * 1
Command: Modified nightly_crawl.sh with research targets
Targets: urls_academic_research.txt
Duration: ~15 minutes (estimated)
Output: crawl_ops/data_runs/research_YYYYMMDD/
```

### 🌅 **Morning Operations (6:00 AM)**

#### **Health Check & Status Report**
```bash
Job ID: morning-health-check
Schedule: 0 6 * * *
Command: scripts/health_check.sh && scripts/generate_daily_report.sh
Duration: ~2 minutes
Output: crawl_ops/reports/daily/health_YYYYMMDD.md
```

### 🌆 **Evening Operations (8:00 PM)**

#### **Weekly Deep Dive (Sundays)**
```bash
Job ID: weekly-comprehensive
Schedule: 0 20 * * 0
Command: scripts/comprehensive_crawl.sh
Targets: All available target lists (rotated)
Duration: ~45 minutes
Output: crawl_ops/data_runs/weekly_YYYYMMDD/
```

## Performance Profiles

### **Standard Profile (Default)**
```yaml
concurrency: 2
download_delay: 5
timeout: 30
retries: 3
threshold: 0.75
proxy_enabled: false
memory_limit: 2048MB
```

### **Fast Profile (Testing)**
```yaml
concurrency: 4
download_delay: 2
timeout: 15
retries: 2
threshold: 0.70
memory_limit: 1024MB
```

### **Thorough Profile (Research)**
```yaml
concurrency: 1
download_delay: 8
timeout: 45
retries: 5
threshold: 0.80
enhanced_validation: true
memory_limit: 3072MB
```

## Job Dependencies & Sequencing

### **Daily Workflow**
1. **02:00** - Finance daily crawl
2. **02:05** - Data validation and processing
3. **02:10** - Vector embedding and storage
4. **06:00** - Health check and status report
5. **06:05** - Performance metrics generation

### **Weekly Workflow**
1. **Sunday 20:00** - Comprehensive multi-source crawl
2. **Sunday 21:00** - Weekly performance analysis
3. **Sunday 21:30** - Target list optimization review
4. **Monday 06:00** - Weekly summary report generation

## Resource Management

### **Disk Space Planning**
- **Daily Runs**: ~50MB per run × 30 days = 1.5GB/month
- **Weekly Runs**: ~200MB per run × 4 runs = 800MB/month
- **Archive Retention**: 6 months rolling = ~14GB total
- **Cleanup Schedule**: Delete runs older than 180 days

### **Memory Usage Optimization**
- **Base System**: 500MB
- **Crawl Job**: 1.4GB peak
- **Buffer**: 1GB safety margin
- **Total Required**: 3GB (well within system limits)

### **Bandwidth Considerations**
- **Finance Daily**: ~35 pages × 200KB = 7MB/day
- **Research Weekly**: ~100 pages × 300KB = 30MB/week
- **Monthly Total**: ~350MB (negligible for most connections)

## Monitoring & Alerting Strategy

### **Success Metrics**
- **Job Completion Rate**: >95%
- **Content Quality Score**: >0.75 average
- **Processing Time**: <10 minutes for daily jobs
- **Error Rate**: <5%

### **Alert Conditions**
```yaml
critical:
  - job_failure_rate > 50%
  - memory_usage > 90%
  - disk_free < 1GB
  
warning:
  - job_failure_rate > 20%
  - memory_usage > 75%
  - content_quality < 0.65
  
info:
  - new_high_quality_sources_found
  - performance_improvement_detected
```

### **Notification Channels**
- **Log Files**: All events to `crawl_ops/logs/`
- **Daily Reports**: Automated summary generation
- **Status Dashboard**: Real-time JSON status files

## Failure Recovery Procedures

### **Job Failure Recovery**
1. **Automatic Retry**: Built into cron job script
2. **Fallback Targets**: Reduced target list for degraded performance
3. **Emergency Mode**: Manual execution with minimal settings
4. **Escalation**: Document failure in lessons learned

### **Resource Exhaustion**
1. **Disk Space**: Trigger emergency cleanup of old runs
2. **Memory**: Reduce concurrency, increase delays
3. **Network**: Switch to smaller target lists
4. **System Load**: Reschedule jobs to off-peak hours

## Implementation Timeline

### **Phase 1: Immediate (Complete)**
- ✅ Basic nightly finance crawl operational
- ✅ Health monitoring and reporting
- ✅ Lessons learned documentation system

### **Phase 2: Week 1**
- 📋 Install comprehensive cron schedule
- 📋 Create job templates for different profiles
- 📋 Implement automated daily reporting
- 📋 Set up disk cleanup automation

### **Phase 3: Week 2-4**
- 📋 Add research and technical blog crawling
- 📋 Implement performance optimization
- 📋 Create comprehensive weekly reporting
- 📋 Develop target list management automation

### **Phase 4: Month 2+**
- 📋 Advanced semantic analysis integration
- 📋 Automated source discovery and validation
- 📋 Performance-based scheduling optimization
- 📋 Integration with external monitoring systems

## Command Reference

### **Manual Operations**
```bash
# Run immediate finance crawl
/home/kiriti/alpha_projects/intelforge/cron/nightly_crawl.sh

# Run with different target list
TARGET_FILE="/path/to/other_targets.txt" nightly_crawl.sh

# Test run (dry run mode)
scripts/cli.py sync --input config/targets_finance.txt --dry-run

# Health check
scripts/cli.py health --json
```

### **Schedule Management**
```bash
# Install all schedules
crontab /home/kiriti/alpha_projects/intelforge/crawl_ops/schedules/master_schedule.cron

# Backup current crontab
crontab -l > crawl_ops/schedules/cron_backup_$(date +%Y%m%d).txt

# View active jobs
crontab -l | grep intelforge
```

### **Monitoring Commands**
```bash
# Check last run status
cat crawl_ops/status/last_run_summary.json

# View recent performance
tail -f crawl_ops/logs/intelforge_nightly.log

# Generate health report
scripts/generate_health_report.sh
```

## Success Criteria

### **Operational Excellence**
- **Availability**: 99.5% uptime for scheduled jobs
- **Reliability**: <5% job failure rate
- **Performance**: Consistent processing times
- **Quality**: Maintained content relevance scores

### **Business Value**
- **Data Coverage**: Complete daily finance intelligence
- **Timeliness**: Fresh content within 6 hours of publication
- **Accuracy**: High-quality semantic filtering
- **Scalability**: Ready for additional source integration

## Review & Optimization

### **Weekly Reviews**
- Performance metrics analysis
- Target list effectiveness evaluation
- Resource utilization optimization
- Schedule adjustment recommendations

### **Monthly Reviews**
- Strategic source additions/removals
- Infrastructure capacity planning
- Technology upgrade assessments
- Process improvement implementations

---

**Next Actions:**
1. Implement Phase 2 cron schedules
2. Create job template scripts
3. Set up automated reporting
4. Begin weekly comprehensive crawling tests