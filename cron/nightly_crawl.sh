#!/bin/bash
# IntelForge Nightly Crawler Script
# Production-ready scheduled crawler for finance targets
# Created: 2025-07-18
# Usage: Run via cron or manually for nightly data collection

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
INTELFORGE_ROOT="/home/kiriti/alpha_projects/intelforge"
VENV_PATH="$INTELFORGE_ROOT/venv"
PYTHON_PATH="$VENV_PATH/bin/python"
CLI_PATH="$INTELFORGE_ROOT/scripts/cli.py"
LOG_FILE="$INTELFORGE_ROOT/crawl_ops/logs/intelforge_nightly.log"
TARGET_FILE="$INTELFORGE_ROOT/config/targets_finance.txt"

# Date-based output directory
TODAY=$(date +%Y%m%d)
OUTPUT_DIR="$INTELFORGE_ROOT/crawl_ops/data_runs/$TODAY"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log "ERROR: $1"
    exit 1
}

# Health check function
health_check() {
    log "🔍 Running pre-flight health checks..."
    
    # Check if virtual environment exists
    if [[ ! -d "$VENV_PATH" ]]; then
        error_exit "Virtual environment not found at $VENV_PATH"
    fi
    
    # Check if Python executable exists
    if [[ ! -f "$PYTHON_PATH" ]]; then
        error_exit "Python executable not found at $PYTHON_PATH"
    fi
    
    # Check if CLI script exists
    if [[ ! -f "$CLI_PATH" ]]; then
        error_exit "CLI script not found at $CLI_PATH"
    fi
    
    # Check if target file exists
    if [[ ! -f "$TARGET_FILE" ]]; then
        error_exit "Target file not found at $TARGET_FILE"
    fi
    
    # Check if logs directory exists
    if [[ ! -d "$(dirname "$LOG_FILE")" ]]; then
        mkdir -p "$(dirname "$LOG_FILE")"
        log "📁 Created logs directory: $(dirname "$LOG_FILE")"
    fi
    
    log "✅ Pre-flight checks passed"
}

# Cleanup function for old data
cleanup_old_data() {
    log "🧹 Cleaning up old data (older than 14 days)..."
    
    # Find and remove directories older than 14 days
    find "$INTELFORGE_ROOT/data_runs" -maxdepth 1 -type d -name "[0-9]*" -mtime +14 -exec rm -rf {} + 2>/dev/null || true
    
    # Clean up old log files (keep last 30 days)
    find "$INTELFORGE_ROOT/logs" -name "intelforge_nightly.log.*" -mtime +30 -delete 2>/dev/null || true
    
    log "✅ Cleanup completed"
}

# Main crawler function
run_crawler() {
    log "🚀 Starting nightly semantic crawler..."
    log "📂 Output directory: $OUTPUT_DIR"
    log "🎯 Target file: $TARGET_FILE"
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    
    # Activate virtual environment and run crawler
    cd "$INTELFORGE_ROOT"
    
    # Export environment variables for logging
    export INTELFORGE_NIGHTLY_RUN=true
    export INTELFORGE_OUTPUT_DIR="$OUTPUT_DIR"
    
    # Run the sync command with production settings
    # Using the existing sync command from the CLI
    "$PYTHON_PATH" "$CLI_PATH" sync \
        --input "$TARGET_FILE" \
        --threshold 0.75 \
        --skip-snapshot \
        --skip-archive \
        2>&1 | tee -a "$LOG_FILE"
    
    # Check if crawler was successful
    if [[ ${PIPESTATUS[0]} -eq 0 ]]; then
        log "✅ Crawler completed successfully"
        
        # Count results
        RESULT_COUNT=$(find "$OUTPUT_DIR" -name "*.json" -type f | wc -l)
        log "📊 Results: $RESULT_COUNT files crawled"
        
        # Log disk usage
        DISK_USAGE=$(du -sh "$OUTPUT_DIR" | cut -f1)
        log "💾 Disk usage: $DISK_USAGE"
        
        return 0
    else
        error_exit "Crawler failed with exit code ${PIPESTATUS[0]}"
    fi
}

# Generate summary report
generate_summary() {
    log "📋 Generating nightly summary report..."
    
    # Create summary file
    SUMMARY_FILE="$OUTPUT_DIR/nightly_summary.txt"
    
    cat > "$SUMMARY_FILE" << EOF
IntelForge Nightly Crawl Summary
================================
Date: $(date '+%Y-%m-%d %H:%M:%S')
Target File: $TARGET_FILE
Output Directory: $OUTPUT_DIR

Results:
- Files Crawled: $(find "$OUTPUT_DIR" -name "*.json" -type f | wc -l)
- Disk Usage: $(du -sh "$OUTPUT_DIR" | cut -f1)
- Target URLs: $(wc -l < "$TARGET_FILE")

Status: SUCCESS
EOF
    
    log "📄 Summary report saved to: $SUMMARY_FILE"
}

# Main execution
main() {
    log "🌙 Starting IntelForge nightly crawl - $(date)"
    
    # Change to IntelForge directory
    cd "$INTELFORGE_ROOT"
    
    # Run health checks
    health_check
    
    # Clean up old data
    cleanup_old_data
    
    # Run the crawler
    run_crawler
    
    # Generate summary
    generate_summary
    
    log "🎉 Nightly crawl completed successfully - $(date)"
    log "📊 Next run scheduled for tomorrow at 2:00 AM"
}

# Execute main function
main "$@"