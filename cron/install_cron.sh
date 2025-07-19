#!/bin/bash
# IntelForge Cron Installation Script
# Installs the nightly crawler cron job safely
# Created: 2025-07-18

set -euo pipefail

# Configuration
INTELFORGE_ROOT="/home/kiriti/alpha_projects/intelforge"
CRON_SCRIPT="$INTELFORGE_ROOT/cron/nightly_crawl.sh"
CRON_LOG="$INTELFORGE_ROOT/logs/nightly_cron.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Check if running as the correct user
check_user() {
    if [[ "$USER" != "kiriti" ]]; then
        error "This script must be run as user 'kiriti'"
    fi
}

# Check if cron service is running
check_cron_service() {
    if ! systemctl is-active --quiet cron; then
        warning "Cron service is not running. Starting it..."
        sudo systemctl start cron
        sudo systemctl enable cron
        success "Cron service started and enabled"
    else
        success "Cron service is running"
    fi
}

# Backup existing crontab
backup_crontab() {
    log "📋 Backing up existing crontab..."
    
    BACKUP_FILE="$INTELFORGE_ROOT/cron/crontab_backup_$(date +%Y%m%d_%H%M%S).txt"
    
    if crontab -l > "$BACKUP_FILE" 2>/dev/null; then
        success "Existing crontab backed up to: $BACKUP_FILE"
    else
        log "No existing crontab to backup"
        touch "$BACKUP_FILE"
    fi
}

# Install cron job
install_cron_job() {
    log "⚙️  Installing nightly crawler cron job..."
    
    # Create temporary crontab file
    TEMP_CRON=$(mktemp)
    
    # Get existing crontab (if any)
    crontab -l > "$TEMP_CRON" 2>/dev/null || true
    
    # Check if our cron job already exists
    if grep -q "nightly_crawl.sh" "$TEMP_CRON"; then
        warning "IntelForge cron job already exists. Removing old version..."
        grep -v "nightly_crawl.sh" "$TEMP_CRON" > "$TEMP_CRON.new"
        mv "$TEMP_CRON.new" "$TEMP_CRON"
    fi
    
    # Add our cron job
    cat >> "$TEMP_CRON" << EOF

# IntelForge Nightly Crawler - Runs every day at 2:00 AM
# Added by install_cron.sh on $(date)
0 2 * * * $CRON_SCRIPT >> $CRON_LOG 2>&1

EOF
    
    # Install the new crontab
    if crontab "$TEMP_CRON"; then
        success "Cron job installed successfully"
        log "📅 Scheduled to run daily at 2:00 AM"
    else
        error "Failed to install cron job"
    fi
    
    # Clean up
    rm -f "$TEMP_CRON"
}

# Verify installation
verify_installation() {
    log "🔍 Verifying installation..."
    
    # Check if cron job is installed
    if crontab -l | grep -q "nightly_crawl.sh"; then
        success "Cron job is properly installed"
    else
        error "Cron job installation verification failed"
    fi
    
    # Check if script is executable
    if [[ -x "$CRON_SCRIPT" ]]; then
        success "Crawler script is executable"
    else
        error "Crawler script is not executable"
    fi
    
    # Check if logs directory exists
    if [[ -d "$(dirname "$CRON_LOG")" ]]; then
        success "Logs directory exists"
    else
        mkdir -p "$(dirname "$CRON_LOG")"
        success "Created logs directory"
    fi
}

# Display next run information
show_next_run() {
    log "📊 Cron job information:"
    echo
    echo "Script Location: $CRON_SCRIPT"
    echo "Log Location: $CRON_LOG"
    echo "Schedule: Daily at 2:00 AM"
    echo "Next Run: $(date -d 'tomorrow 2:00' '+%Y-%m-%d %H:%M:%S')"
    echo
    echo "📋 To view current crontab:"
    echo "  crontab -l"
    echo
    echo "📋 To manually run the crawler:"
    echo "  $CRON_SCRIPT"
    echo
    echo "📋 To view logs:"
    echo "  tail -f $CRON_LOG"
    echo
    echo "📋 To remove the cron job:"
    echo "  crontab -e  # then delete the IntelForge lines"
}

# Main execution
main() {
    log "🚀 Installing IntelForge nightly crawler cron job..."
    
    # Run checks
    check_user
    check_cron_service
    
    # Backup and install
    backup_crontab
    install_cron_job
    
    # Verify installation
    verify_installation
    
    # Show information
    show_next_run
    
    success "IntelForge nightly crawler cron job installed successfully!"
    log "🌙 The crawler will run automatically every night at 2:00 AM"
}

# Execute main function
main "$@"