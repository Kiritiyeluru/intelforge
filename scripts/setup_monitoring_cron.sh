#!/bin/bash

# Setup script for IntelForge production monitoring cron jobs
# This script configures automated monitoring with 5-minute intervals

set -e

PROJECT_ROOT="/home/kiriti/alpha_projects/intelforge"
VENV_PATH="$PROJECT_ROOT/venv"
PYTHON_PATH="$VENV_PATH/bin/python"

echo "Setting up IntelForge production monitoring cron jobs..."

# Verify environment
if [ ! -d "$VENV_PATH" ]; then
    echo "ERROR: Virtual environment not found at $VENV_PATH"
    exit 1
fi

if [ ! -f "$PYTHON_PATH" ]; then
    echo "ERROR: Python binary not found at $PYTHON_PATH"
    exit 1
fi

# Create monitoring script wrapper
cat > "$PROJECT_ROOT/scripts/monitoring_wrapper.sh" << 'EOF'
#!/bin/bash
# Wrapper script for cron-based monitoring

# Set environment
export PATH="/home/kiriti/alpha_projects/intelforge/venv/bin:$PATH"
export PYTHONPATH="/home/kiriti/alpha_projects/intelforge"

# Change to project directory
cd /home/kiriti/alpha_projects/intelforge

# Activate virtual environment and run monitoring
source venv/bin/activate
python scripts/continuous_monitoring.py >> logs/cron_monitoring.log 2>&1
EOF

chmod +x "$PROJECT_ROOT/scripts/monitoring_wrapper.sh"

# Create cron job entries
CRON_ENTRIES=$(cat << EOF
# IntelForge Production Monitoring - Every 5 minutes
*/5 * * * * $PROJECT_ROOT/scripts/monitoring_wrapper.sh

# TTR Tracking with Alerts - Every 15 minutes
*/15 * * * * cd $PROJECT_ROOT && source venv/bin/activate && python scripts/utils/ttr_tracker.py --alert-threshold 300 >> logs/ttr_cron.log 2>&1

# Performance Monitoring - Every 10 minutes
*/10 * * * * cd $PROJECT_ROOT && source venv/bin/activate && python scripts/utils/performance_monitor.py --alert-on-threshold >> logs/performance_cron.log 2>&1

# Daily health report generation - Every day at 8:00 AM
0 8 * * * cd $PROJECT_ROOT && source venv/bin/activate && python scripts/cli.py health --json --strict > logs/daily_health_\$(date +\%Y\%m\%d).json 2>&1
EOF
)

echo "Cron job entries to add:"
echo "$CRON_ENTRIES"
echo ""

# Check if cron jobs already exist
if crontab -l 2>/dev/null | grep -q "IntelForge Production Monitoring"; then
    echo "WARNING: IntelForge monitoring cron jobs already exist"
    echo "Use 'crontab -e' to manually manage existing entries"
else
    echo "Adding cron jobs..."
    
    # Add to existing crontab
    (crontab -l 2>/dev/null; echo "$CRON_ENTRIES") | crontab -
    
    echo "✅ Cron jobs added successfully!"
fi

# Create log directories
mkdir -p "$PROJECT_ROOT/logs/cron"
mkdir -p "$PROJECT_ROOT/logs/ttr"
mkdir -p "$PROJECT_ROOT/logs/performance"

echo "✅ Monitoring setup complete!"
echo ""
echo "Monitoring capabilities:"
echo "- Health checks every 5 minutes"
echo "- TTR tracking every 15 minutes"
echo "- Performance monitoring every 10 minutes"
echo "- Daily health reports at 8:00 AM"
echo ""
echo "Log files:"
echo "- Main monitoring: logs/cron_monitoring.log"
echo "- TTR tracking: logs/ttr_cron.log"
echo "- Performance: logs/performance_cron.log"
echo "- Daily health: logs/daily_health_YYYYMMDD.json"
echo ""
echo "To view current cron jobs: crontab -l"
echo "To remove cron jobs: crontab -e"
echo "To test monitoring: $PROJECT_ROOT/scripts/monitoring_wrapper.sh"