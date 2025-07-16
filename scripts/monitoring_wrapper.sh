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
