#!/usr/bin/env python3
"""
Enterprise Monitoring Dashboard
Comprehensive logging, performance tracking, and alerting system for IntelForge
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import sqlite3
import argparse
from dataclasses import dataclass
import statistics
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Optional import for quantstats (requires IPython in some environments)
try:
    import quantstats as qs
    HAS_QUANTSTATS = True
except ImportError:
    HAS_QUANTSTATS = False

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@dataclass
class ScrapingEvent:
    """Structured logging event for scraping operations."""
    timestamp: str
    event_type: str  # 'start', 'success', 'failure', 'bot_detection', 'retry'
    scraper_type: str  # 'http', 'browser', 'academic'
    url: str
    status_code: Optional[int] = None
    content_length: Optional[int] = None
    execution_time: Optional[float] = None
    error_message: Optional[str] = None
    bot_detected: Optional[bool] = None
    retry_count: Optional[int] = None
    metadata: Optional[Dict] = None

class ScrapingLogger:
    """Centralized logging system for all scraping operations."""
    
    def __init__(self, db_path: str = "vault/logs/scraping_operations.db"):
        self.db_path = Path(project_root) / db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for logging."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scraping_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    scraper_type TEXT NOT NULL,
                    url TEXT NOT NULL,
                    status_code INTEGER,
                    content_length INTEGER,
                    execution_time REAL,
                    error_message TEXT,
                    bot_detected BOOLEAN,
                    retry_count INTEGER,
                    metadata TEXT
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON scraping_events(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON scraping_events(event_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_scraper_type ON scraping_events(scraper_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_bot_detected ON scraping_events(bot_detected)")
            
    def log_event(self, event: ScrapingEvent):
        """Log a scraping event to the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO scraping_events 
                (timestamp, event_type, scraper_type, url, status_code, 
                 content_length, execution_time, error_message, bot_detected, 
                 retry_count, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.timestamp, event.event_type, event.scraper_type, event.url,
                event.status_code, event.content_length, event.execution_time,
                event.error_message, event.bot_detected, event.retry_count,
                json.dumps(event.metadata) if event.metadata else None
            ))
    
    def get_recent_events(self, hours: int = 24) -> List[Dict]:
        """Get recent scraping events."""
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM scraping_events 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC
            """, (cutoff_time,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_performance_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Calculate performance metrics for the specified time period."""
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Success rates by scraper type
            success_rates = {}
            cursor = conn.execute("""
                SELECT scraper_type, 
                       COUNT(*) as total,
                       SUM(CASE WHEN event_type = 'success' THEN 1 ELSE 0 END) as successes
                FROM scraping_events 
                WHERE timestamp > ? AND event_type IN ('success', 'failure')
                GROUP BY scraper_type
            """, (cutoff_time,))
            
            for row in cursor:
                scraper_type, total, successes = row
                success_rates[scraper_type] = {
                    'total': total,
                    'successes': successes,
                    'success_rate': (successes / total * 100) if total > 0 else 0
                }
            
            # Bot detection statistics
            cursor = conn.execute("""
                SELECT COUNT(*) as bot_detections,
                       AVG(execution_time) as avg_time_with_detection
                FROM scraping_events 
                WHERE timestamp > ? AND bot_detected = 1
            """, (cutoff_time,))
            
            bot_stats = cursor.fetchone()
            
            # Average execution times
            cursor = conn.execute("""
                SELECT scraper_type, 
                       AVG(execution_time) as avg_time,
                       MIN(execution_time) as min_time,
                       MAX(execution_time) as max_time
                FROM scraping_events 
                WHERE timestamp > ? AND execution_time IS NOT NULL
                GROUP BY scraper_type
            """, (cutoff_time,))
            
            execution_times = {}
            for row in cursor:
                scraper_type, avg_time, min_time, max_time = row
                execution_times[scraper_type] = {
                    'avg_time': avg_time,
                    'min_time': min_time,
                    'max_time': max_time
                }
            
            # Error frequency
            cursor = conn.execute("""
                SELECT error_message, COUNT(*) as frequency
                FROM scraping_events 
                WHERE timestamp > ? AND event_type = 'failure' AND error_message IS NOT NULL
                GROUP BY error_message
                ORDER BY frequency DESC
                LIMIT 10
            """, (cutoff_time,))
            
            top_errors = [{'error': row[0], 'frequency': row[1]} for row in cursor]
            
            return {
                'time_period_hours': hours,
                'success_rates': success_rates,
                'bot_detection': {
                    'count': bot_stats[0] if bot_stats[0] else 0,
                    'avg_execution_time': bot_stats[1] if bot_stats[1] else 0
                },
                'execution_times': execution_times,
                'top_errors': top_errors,
                'generated_at': datetime.now().isoformat()
            }

class PerformanceMonitor:
    """Real-time performance monitoring and alerting."""
    
    def __init__(self, logger: ScrapingLogger):
        self.logger = logger
        self.thresholds = {
            'min_success_rate': 70.0,  # Minimum acceptable success rate (%)
            'max_bot_detection_rate': 30.0,  # Maximum acceptable bot detection rate (%)
            'max_avg_execution_time': 10.0,  # Maximum acceptable average execution time (seconds)
            'max_error_frequency': 5  # Maximum acceptable error frequency
        }
    
    def check_alerts(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Check for performance alerts."""
        metrics = self.logger.get_performance_metrics(hours)
        alerts = []
        
        # Check success rates
        for scraper_type, stats in metrics['success_rates'].items():
            if stats['success_rate'] < self.thresholds['min_success_rate']:
                alerts.append({
                    'type': 'low_success_rate',
                    'severity': 'warning' if stats['success_rate'] > 50 else 'critical',
                    'scraper_type': scraper_type,
                    'current_value': stats['success_rate'],
                    'threshold': self.thresholds['min_success_rate'],
                    'message': f"{scraper_type} success rate ({stats['success_rate']:.1f}%) below threshold ({self.thresholds['min_success_rate']}%)"
                })
        
        # Check bot detection rate
        total_requests = sum(stats['total'] for stats in metrics['success_rates'].values())
        if total_requests > 0:
            bot_detection_rate = (metrics['bot_detection']['count'] / total_requests) * 100
            if bot_detection_rate > self.thresholds['max_bot_detection_rate']:
                alerts.append({
                    'type': 'high_bot_detection',
                    'severity': 'warning',
                    'current_value': bot_detection_rate,
                    'threshold': self.thresholds['max_bot_detection_rate'],
                    'message': f"Bot detection rate ({bot_detection_rate:.1f}%) above threshold ({self.thresholds['max_bot_detection_rate']}%)"
                })
        
        # Check execution times
        for scraper_type, stats in metrics['execution_times'].items():
            if stats['avg_time'] > self.thresholds['max_avg_execution_time']:
                alerts.append({
                    'type': 'slow_execution',
                    'severity': 'warning',
                    'scraper_type': scraper_type,
                    'current_value': stats['avg_time'],
                    'threshold': self.thresholds['max_avg_execution_time'],
                    'message': f"{scraper_type} average execution time ({stats['avg_time']:.2f}s) above threshold ({self.thresholds['max_avg_execution_time']}s)"
                })
        
        # Check error frequency
        for error in metrics['top_errors']:
            if error['frequency'] > self.thresholds['max_error_frequency']:
                alerts.append({
                    'type': 'high_error_frequency',
                    'severity': 'warning',
                    'current_value': error['frequency'],
                    'threshold': self.thresholds['max_error_frequency'],
                    'message': f"Error '{error['error'][:50]}...' occurred {error['frequency']} times"
                })
        
        return alerts

class FinancialAnalytics:
    """Financial intelligence and market analysis integration."""
    
    def __init__(self, logger: ScrapingLogger):
        self.logger = logger
        self.market_symbols = ['SPY', 'QQQ', 'IWM', 'VIX']  # Key market indicators
        self.financial_sites = [
            'finviz.com', 'yahoo.com', 'marketwatch.com', 'bloomberg.com',
            'seekingalpha.com', 'benzinga.com', 'fool.com'
        ]
    
    def get_market_context(self) -> Dict[str, Any]:
        """Get current market context and performance."""
        try:
            market_data = {}
            for symbol in self.market_symbols:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d")
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                    change_pct = ((current_price - prev_close) / prev_close) * 100
                    
                    market_data[symbol] = {
                        'current_price': current_price,
                        'change_pct': change_pct,
                        'volume': hist['Volume'].iloc[-1],
                        'volatility': hist['Close'].pct_change().std() * 100
                    }
            
            return {
                'market_data': market_data,
                'market_sentiment': self._assess_market_sentiment(market_data),
                'retrieved_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e), 'retrieved_at': datetime.now().isoformat()}
    
    def _assess_market_sentiment(self, market_data: Dict) -> str:
        """Assess overall market sentiment based on key indicators."""
        if not market_data:
            return "UNKNOWN"
        
        spy_change = market_data.get('SPY', {}).get('change_pct', 0)
        vix_level = market_data.get('VIX', {}).get('current_price', 20)
        
        if spy_change > 1 and vix_level < 20:
            return "BULLISH"
        elif spy_change < -1 and vix_level > 25:
            return "BEARISH"
        elif abs(spy_change) < 0.5 and 15 < vix_level < 25:
            return "NEUTRAL"
        else:
            return "MIXED"
    
    def get_financial_scraping_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get financial-specific scraping performance metrics."""
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        with sqlite3.connect(self.logger.db_path) as conn:
            # Financial sites performance
            financial_performance = {}
            for site in self.financial_sites:
                cursor = conn.execute("""
                    SELECT COUNT(*) as total,
                           SUM(CASE WHEN event_type = 'success' THEN 1 ELSE 0 END) as successes,
                           AVG(execution_time) as avg_time,
                           SUM(CASE WHEN bot_detected = 1 THEN 1 ELSE 0 END) as bot_detections
                    FROM scraping_events 
                    WHERE timestamp > ? AND url LIKE ? 
                    AND event_type IN ('success', 'failure')
                """, (cutoff_time, f'%{site}%'))
                
                result = cursor.fetchone()
                if result and result[0] > 0:
                    total, successes, avg_time, bot_detections = result
                    financial_performance[site] = {
                        'total_requests': total,
                        'success_rate': (successes / total * 100) if total > 0 else 0,
                        'avg_execution_time': avg_time or 0,
                        'bot_detection_rate': (bot_detections / total * 100) if total > 0 else 0
                    }
            
            # Financial content analysis
            cursor = conn.execute("""
                SELECT COUNT(*) as financial_articles,
                       AVG(content_length) as avg_content_length
                FROM scraping_events 
                WHERE timestamp > ? 
                AND event_type = 'success' 
                AND (url LIKE '%finance%' OR url LIKE '%trading%' OR url LIKE '%market%')
                AND content_length IS NOT NULL
            """, (cutoff_time,))
            
            content_stats = cursor.fetchone()
            
            return {
                'financial_sites_performance': financial_performance,
                'content_analysis': {
                    'financial_articles_scraped': content_stats[0] if content_stats[0] else 0,
                    'avg_content_length': content_stats[1] if content_stats[1] else 0
                },
                'analysis_period_hours': hours,
                'generated_at': datetime.now().isoformat()
            }
    
    def generate_financial_dashboard_html(self, hours: int = 24) -> str:
        """Generate interactive financial dashboard HTML."""
        market_context = self.get_market_context()
        financial_metrics = self.get_financial_scraping_metrics(hours)
        
        # Create market overview chart
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Market Performance', 'Scraping Success Rates', 
                          'Execution Times', 'Bot Detection Rates'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Market performance
        if 'market_data' in market_context:
            symbols = list(market_context['market_data'].keys())
            changes = [market_context['market_data'][s].get('change_pct', 0) for s in symbols]
            colors = ['green' if x > 0 else 'red' for x in changes]
            
            fig.add_trace(
                go.Bar(x=symbols, y=changes, marker_color=colors, name="Market Change %"),
                row=1, col=1
            )
        
        # Financial sites performance
        if financial_metrics['financial_sites_performance']:
            sites = list(financial_metrics['financial_sites_performance'].keys())
            success_rates = [financial_metrics['financial_sites_performance'][s]['success_rate'] for s in sites]
            
            fig.add_trace(
                go.Bar(x=sites, y=success_rates, name="Success Rate %", marker_color='blue'),
                row=1, col=2
            )
            
            # Execution times
            exec_times = [financial_metrics['financial_sites_performance'][s]['avg_execution_time'] for s in sites]
            fig.add_trace(
                go.Scatter(x=sites, y=exec_times, mode='markers+lines', name="Avg Time (s)"),
                row=2, col=1
            )
            
            # Bot detection rates
            bot_rates = [financial_metrics['financial_sites_performance'][s]['bot_detection_rate'] for s in sites]
            fig.add_trace(
                go.Bar(x=sites, y=bot_rates, name="Bot Detection %", marker_color='orange'),
                row=2, col=2
            )
        
        fig.update_layout(
            title_text=f"Financial Intelligence Dashboard - Last {hours} Hours",
            showlegend=False,
            height=800
        )
        
        # Convert to HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>IntelForge Financial Dashboard</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .metric-card {{ 
                    display: inline-block; margin: 10px; padding: 15px; 
                    border: 1px solid #ddd; border-radius: 5px; min-width: 200px;
                }}
                .metric-value {{ font-size: 24px; font-weight: bold; }}
                .market-sentiment {{ 
                    padding: 10px; margin: 10px 0; border-radius: 5px; text-align: center;
                    font-weight: bold; font-size: 18px;
                }}
                .bullish {{ background-color: #d4edda; color: #155724; }}
                .bearish {{ background-color: #f8d7da; color: #721c24; }}
                .neutral {{ background-color: #fff3cd; color: #856404; }}
                .mixed {{ background-color: #d1ecf1; color: #0c5460; }}
            </style>
        </head>
        <body>
            <h1>🏦 IntelForge Financial Intelligence Dashboard</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="market-sentiment {market_context.get('market_sentiment', 'neutral').lower()}">
                Market Sentiment: {market_context.get('market_sentiment', 'UNKNOWN')}
            </div>
            
            <div class="metric-card">
                <div>Financial Articles Scraped</div>
                <div class="metric-value">{financial_metrics['content_analysis']['financial_articles_scraped']}</div>
            </div>
            
            <div class="metric-card">
                <div>Avg Content Length</div>
                <div class="metric-value">{financial_metrics['content_analysis']['avg_content_length']:.0f}</div>
            </div>
            
            <div id="dashboard-chart"></div>
            
            <script>
                {fig.to_json()}
                Plotly.newPlot('dashboard-chart', {fig.to_json()});
            </script>
        </body>
        </html>
        """
        
        return html_content

class MonitoringDashboard:
    """Interactive monitoring dashboard."""
    
    def __init__(self):
        self.logger = ScrapingLogger()
        self.monitor = PerformanceMonitor(self.logger)
        self.financial = FinancialAnalytics(self.logger)
    
    def generate_report(self, hours: int = 24) -> str:
        """Generate comprehensive monitoring report with financial intelligence."""
        metrics = self.logger.get_performance_metrics(hours)
        alerts = self.monitor.check_alerts(1)  # Check last hour for alerts
        financial_metrics = self.financial.get_financial_scraping_metrics(hours)
        market_context = self.financial.get_market_context()
        
        report = f"""
{'='*80}
📊 INTELFORGE FINANCIAL INTELLIGENCE DASHBOARD
{'='*80}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Time Period: Last {hours} hours

🏦 **MARKET CONTEXT**
"""
        
        # Market overview
        if 'market_data' in market_context:
            report += f"""
   Market Sentiment: {market_context.get('market_sentiment', 'UNKNOWN')}
   
   📈 Key Market Indicators:
"""
            for symbol, data in market_context['market_data'].items():
                change_icon = "📈" if data['change_pct'] > 0 else "📉" if data['change_pct'] < 0 else "➡️"
                report += f"   {change_icon} {symbol}: ${data['current_price']:.2f} ({data['change_pct']:+.2f}%)\n"
        
        report += f"\n🎯 **OVERALL PERFORMANCE SUMMARY**\n"
        
        # Overall stats
        total_requests = sum(stats['total'] for stats in metrics['success_rates'].values())
        total_successes = sum(stats['successes'] for stats in metrics['success_rates'].values())
        overall_success_rate = (total_successes / total_requests * 100) if total_requests > 0 else 0
        
        report += f"""
   Total Requests: {total_requests:,}
   Successful Requests: {total_successes:,}
   Overall Success Rate: {overall_success_rate:.1f}%
   Bot Detections: {metrics['bot_detection']['count']}
   Financial Articles Scraped: {financial_metrics['content_analysis']['financial_articles_scraped']:,}
   Avg Financial Content Length: {financial_metrics['content_analysis']['avg_content_length']:.0f} chars
"""
        
        # Success rates by scraper type
        if metrics['success_rates']:
            report += f"\n📈 **SUCCESS RATES BY SCRAPER TYPE**\n"
            for scraper_type, stats in metrics['success_rates'].items():
                status_icon = "✅" if stats['success_rate'] >= 80 else "⚠️" if stats['success_rate'] >= 60 else "❌"
                report += f"   {status_icon} {scraper_type}: {stats['success_rate']:.1f}% ({stats['successes']}/{stats['total']})\n"
        
        # Financial sites performance
        if financial_metrics['financial_sites_performance']:
            report += f"\n🏦 **FINANCIAL SITES PERFORMANCE**\n"
            for site, stats in financial_metrics['financial_sites_performance'].items():
                status_icon = "✅" if stats['success_rate'] >= 80 else "⚠️" if stats['success_rate'] >= 60 else "❌"
                bot_icon = "🛡️" if stats['bot_detection_rate'] > 0 else ""
                report += f"   {status_icon} {site}: {stats['success_rate']:.1f}% success, {stats['avg_execution_time']:.2f}s avg {bot_icon}\n"
        
        # Execution times
        if metrics['execution_times']:
            report += f"\n⚡ **EXECUTION TIMES BY SCRAPER TYPE**\n"
            for scraper_type, stats in metrics['execution_times'].items():
                report += f"   {scraper_type}: {stats['avg_time']:.2f}s avg (min: {stats['min_time']:.2f}s, max: {stats['max_time']:.2f}s)\n"
        
        # Bot detection analysis
        if metrics['bot_detection']['count'] > 0:
            report += f"\n🛡️ **BOT DETECTION ANALYSIS**\n"
            report += f"   Detection Count: {metrics['bot_detection']['count']}\n"
            if metrics['bot_detection']['avg_execution_time'] > 0:
                report += f"   Avg Time with Detection: {metrics['bot_detection']['avg_execution_time']:.2f}s\n"
        
        # Top errors
        if metrics['top_errors']:
            report += f"\n❌ **TOP ERRORS**\n"
            for i, error in enumerate(metrics['top_errors'][:5], 1):
                report += f"   {i}. {error['error'][:60]}... (x{error['frequency']})\n"
        
        # Alerts
        if alerts:
            report += f"\n🚨 **ACTIVE ALERTS ({len(alerts)})**\n"
            for alert in alerts:
                severity_icon = "🔴" if alert['severity'] == 'critical' else "🟡"
                report += f"   {severity_icon} {alert['message']}\n"
        else:
            report += f"\n✅ **NO ACTIVE ALERTS** - All systems operating normally\n"
        
        # Performance recommendations
        report += f"\n💡 **RECOMMENDATIONS**\n"
        
        if overall_success_rate < 80:
            report += "   ⚠️  Consider implementing additional anti-detection measures\n"
        if metrics['bot_detection']['count'] > total_requests * 0.2:
            report += "   🛡️  High bot detection rate - review stealth configuration\n"
        
        avg_execution_time = statistics.mean([
            stats['avg_time'] for stats in metrics['execution_times'].values()
        ]) if metrics['execution_times'] else 0
        
        if avg_execution_time > 8:
            report += "   ⚡ Consider optimizing scraper performance or reducing concurrent workers\n"
        elif avg_execution_time < 2:
            report += "   🚀 Excellent performance - consider increasing concurrent workers\n"
        
        if not alerts:
            report += "   ✅ All systems operating within acceptable parameters\n"
        
        report += f"\n{'='*80}\n"
        
        return report
    
    def start_monitoring(self, interval: int = 300):
        """Start continuous monitoring with specified interval (seconds)."""
        print(f"🔄 Starting continuous monitoring (interval: {interval}s)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                alerts = self.monitor.check_alerts(1)
                
                if alerts:
                    print(f"\n🚨 [{datetime.now().strftime('%H:%M:%S')}] {len(alerts)} alert(s) detected:")
                    for alert in alerts:
                        severity_icon = "🔴" if alert['severity'] == 'critical' else "🟡"
                        print(f"   {severity_icon} {alert['message']}")
                else:
                    print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] All systems normal")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n⏹️  Monitoring stopped")

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="Enterprise Monitoring Dashboard")
    parser.add_argument('--report', action='store_true', help='Generate performance report')
    parser.add_argument('--monitor', action='store_true', help='Start continuous monitoring')
    parser.add_argument('--hours', type=int, default=24, help='Time period for report (hours)')
    parser.add_argument('--interval', type=int, default=300, help='Monitoring interval (seconds)')
    parser.add_argument('--alerts', action='store_true', help='Check current alerts only')
    parser.add_argument('--financial', action='store_true', help='Generate financial dashboard HTML')
    parser.add_argument('--market', action='store_true', help='Get current market context only')
    
    args = parser.parse_args()
    
    dashboard = MonitoringDashboard()
    
    if args.report:
        report = dashboard.generate_report(args.hours)
        print(report)
        
        # Save report to file
        timestamp = int(time.time())
        report_file = project_root / f"vault/logs/monitoring_report_{timestamp}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"📄 Report saved to: {report_file}")
        
    elif args.monitor:
        dashboard.start_monitoring(args.interval)
        
    elif args.alerts:
        alerts = dashboard.monitor.check_alerts(1)
        if alerts:
            print(f"🚨 {len(alerts)} active alert(s):")
            for alert in alerts:
                severity_icon = "🔴" if alert['severity'] == 'critical' else "🟡"
                print(f"   {severity_icon} {alert['message']}")
        else:
            print("✅ No active alerts")
    
    elif args.financial:
        html_content = dashboard.financial.generate_financial_dashboard_html(args.hours)
        timestamp = int(time.time())
        html_file = project_root / f"vault/logs/financial_dashboard_{timestamp}.html"
        with open(html_file, 'w') as f:
            f.write(html_content)
        print(f"📊 Financial dashboard saved to: {html_file}")
        print("Open the HTML file in a browser to view the interactive dashboard")
    
    elif args.market:
        market_context = dashboard.financial.get_market_context()
        if 'error' in market_context:
            print(f"❌ Error fetching market data: {market_context['error']}")
        else:
            print(f"🏦 Market Sentiment: {market_context.get('market_sentiment', 'UNKNOWN')}")
            print(f"📈 Market Indicators:")
            for symbol, data in market_context.get('market_data', {}).items():
                change_icon = "📈" if data['change_pct'] > 0 else "📉" if data['change_pct'] < 0 else "➡️"
                print(f"   {change_icon} {symbol}: ${data['current_price']:.2f} ({data['change_pct']:+.2f}%)")
            
    else:
        print("Use --report, --monitor, --alerts, --financial, or --market")
        print("Examples:")
        print("  python monitoring_dashboard.py --report --hours 6")
        print("  python monitoring_dashboard.py --financial --hours 12")
        print("  python monitoring_dashboard.py --market")

if __name__ == "__main__":
    main()