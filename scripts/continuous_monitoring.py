#!/usr/bin/env python3
"""
Continuous monitoring script for IntelForge production deployment.
Runs health checks, TTR tracking, and performance monitoring with alerting.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductionMonitor:
    def __init__(self):
        self.project_root = project_root
        self.health_threshold = 85  # Minimum health percentage
        self.response_time_threshold = 300  # 5 minutes in seconds
        self.alert_cooldown = 900  # 15 minutes between alerts
        self.last_alert_time = {}
        
    def run_health_check(self):
        """Run comprehensive health check and return results."""
        try:
            # Set environment to reduce logging noise
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'
            
            cmd = [
                sys.executable, "scripts/cli.py", "health", "--json", "--strict"
            ]
            
            result = subprocess.run(
                cmd, 
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120,
                env=env
            )
            
            if result.returncode == 0:
                # Extract JSON from output (skip non-JSON lines)
                output = result.stdout + result.stderr
                lines = output.strip().split('\n')
                
                # Look for JSON structure in output
                json_content = ""
                in_json = False
                brace_count = 0
                
                for line in lines:
                    line = line.strip()
                    
                    # Skip log lines
                    if ' - ' in line and (' - INFO - ' in line or ' - WARNING - ' in line or ' - ERROR - ' in line):
                        continue
                    
                    # Look for JSON start
                    if line.startswith('{') and not in_json:
                        in_json = True
                        json_content = line
                        brace_count = line.count('{') - line.count('}')
                    elif in_json:
                        json_content += "\n" + line
                        brace_count += line.count('{') - line.count('}')
                        
                        # Check if JSON is complete
                        if brace_count == 0:
                            try:
                                health_data = json.loads(json_content)
                                return health_data
                            except json.JSONDecodeError:
                                in_json = False
                                json_content = ""
                                brace_count = 0
                                continue
                
                # Fallback: look for single-line JSON
                for line in reversed(lines):
                    line = line.strip()
                    if line.startswith('{') and line.endswith('}'):
                        try:
                            health_data = json.loads(line)
                            return health_data
                        except json.JSONDecodeError:
                            continue
                
                logger.error("No valid JSON found in health check output")
                logger.debug(f"Health check output: {result.stdout}")
                logger.debug(f"Health check stderr: {result.stderr}")
                return None
            else:
                logger.error(f"Health check failed with return code {result.returncode}")
                logger.error(f"Error output: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("Health check timed out")
            return None
        except Exception as e:
            logger.error(f"Error running health check: {e}")
            return None
    
    def check_health_status(self, health_data):
        """Analyze health data and return status assessment."""
        if not health_data:
            return {"status": "critical", "message": "Health check failed"}
        
        overall_status = health_data.get("overall_status", "unknown")
        checks = health_data.get("checks", {})
        
        # Calculate health percentage
        system_health = checks.get("system_health", {})
        if isinstance(system_health, dict):
            details = system_health.get("details", {})
            if isinstance(details, dict):
                results = details.get("results", {})
                if isinstance(results, dict):
                    total = results.get("pass", 0) + results.get("fail", 0) + results.get("warn", 0)
                    passed = results.get("pass", 0)
                    health_percentage = (passed / total * 100) if total > 0 else 0
                else:
                    health_percentage = 90  # Default if structure is different
            else:
                health_percentage = 90
        else:
            health_percentage = 90
        
        # Check critical failures
        critical_failures = 0
        if isinstance(system_health, dict):
            details = system_health.get("details", {})
            if isinstance(details, dict):
                critical_failures = details.get("critical_failures", 0)
        
        # Determine status
        if critical_failures > 0:
            status = "critical"
            message = f"Critical failures detected: {critical_failures}"
        elif health_percentage < self.health_threshold:
            status = "warning"
            message = f"Health percentage below threshold: {health_percentage:.1f}%"
        elif overall_status != "healthy":
            status = "warning"
            message = f"Overall status: {overall_status}"
        else:
            status = "healthy"
            message = f"System healthy: {health_percentage:.1f}% ({overall_status})"
        
        return {
            "status": status,
            "message": message,
            "health_percentage": health_percentage,
            "overall_status": overall_status,
            "critical_failures": critical_failures
        }
    
    def send_alert(self, alert_type, message, health_data=None):
        """Send alert notification (log-based for now)."""
        alert_key = f"{alert_type}_{message[:50]}"
        current_time = time.time()
        
        # Check cooldown
        if alert_key in self.last_alert_time:
            if current_time - self.last_alert_time[alert_key] < self.alert_cooldown:
                return
        
        self.last_alert_time[alert_key] = current_time
        
        # Log alert
        logger.warning(f"🚨 ALERT [{alert_type.upper()}]: {message}")
        
        # Save alert to file
        alert_file = Path("logs/alerts.log")
        alert_file.parent.mkdir(exist_ok=True)
        
        with open(alert_file, "a") as f:
            alert_entry = {
                "timestamp": datetime.now().isoformat(),
                "type": alert_type,
                "message": message,
                "health_data": health_data
            }
            f.write(json.dumps(alert_entry) + "\n")
        
        # TODO: Add email/SMS notifications for production
        print(f"🚨 ALERT: {alert_type} - {message}")
    
    def run_ttr_tracking(self):
        """Run TTR tracking and check for SLA violations."""
        try:
            cmd = [sys.executable, "scripts/utils/ttr_tracker.py"]
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info("TTR tracking completed successfully")
                return True
            else:
                logger.error(f"TTR tracking failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error running TTR tracking: {e}")
            return False
    
    def run_performance_monitoring(self):
        """Run performance monitoring and check for degradation."""
        try:
            cmd = [sys.executable, "scripts/utils/performance_monitor.py"]
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info("Performance monitoring completed successfully")
                return True
            else:
                logger.error(f"Performance monitoring failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error running performance monitoring: {e}")
            return False
    
    def run_monitoring_cycle(self):
        """Run a complete monitoring cycle."""
        logger.info("Starting monitoring cycle...")
        
        # Run health check
        health_data = self.run_health_check()
        health_status = self.check_health_status(health_data)
        
        logger.info(f"Health Status: {health_status['message']}")
        
        # Check for alerts
        if health_status["status"] == "critical":
            self.send_alert("CRITICAL", health_status["message"], health_data)
        elif health_status["status"] == "warning":
            self.send_alert("WARNING", health_status["message"], health_data)
        
        # Run TTR tracking
        if not self.run_ttr_tracking():
            self.send_alert("TTR_FAILURE", "TTR tracking failed")
        
        # Run performance monitoring
        if not self.run_performance_monitoring():
            self.send_alert("PERFORMANCE_FAILURE", "Performance monitoring failed")
        
        # Save status to file for dashboard
        status_file = Path("logs/monitoring_status.json")
        status_file.parent.mkdir(exist_ok=True)
        
        status_data = {
            "timestamp": datetime.now().isoformat(),
            "health_status": health_status,
            "health_data": health_data,
            "monitoring_cycle": "completed"
        }
        
        with open(status_file, "w") as f:
            json.dump(status_data, f, indent=2)
        
        logger.info("Monitoring cycle completed")
        return health_status

def main():
    """Main monitoring function."""
    monitor = ProductionMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        # Continuous monitoring mode
        logger.info("Starting continuous monitoring...")
        while True:
            try:
                monitor.run_monitoring_cycle()
                time.sleep(300)  # 5 minutes
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")
                time.sleep(60)  # Wait 1 minute before retry
    else:
        # Single monitoring cycle
        status = monitor.run_monitoring_cycle()
        if status["status"] == "critical":
            sys.exit(1)
        elif status["status"] == "warning":
            sys.exit(2)
        else:
            sys.exit(0)

if __name__ == "__main__":
    main()