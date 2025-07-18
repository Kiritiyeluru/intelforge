#!/usr/bin/env python3
"""
Enhanced Monitoring Dashboard for IntelForge Financial Intelligence Platform
Provides real-time market data, financial analysis, and comprehensive monitoring
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class EnhancedMonitoringDashboard:
    """Enhanced monitoring dashboard with financial intelligence capabilities"""

    def __init__(self, test_mode: bool = False):
        self.test_mode = test_mode
        self.project_root = project_root
        self.reports_dir = self.project_root / "vault" / "monitoring_reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def get_market_data(self) -> Dict[str, Any]:
        """Get real-time market data for key indicators"""
        if self.test_mode:
            return {
                "SPY": {"price": 500.25, "change": 1.25, "change_pct": 0.25},
                "QQQ": {"price": 375.80, "change": 2.15, "change_pct": 0.58},
                "IWM": {"price": 220.45, "change": -0.85, "change_pct": -0.38},
                "VIX": {"price": 14.25, "change": -0.35, "change_pct": -2.4},
            }

        try:
            import yfinance as yf

            symbols = ["SPY", "QQQ", "IWM", "VIX"]
            market_data = {}

            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")

                if len(hist) >= 2:
                    current_price = hist["Close"].iloc[-1]
                    prev_price = hist["Close"].iloc[-2]
                    change = current_price - prev_price
                    change_pct = (change / prev_price) * 100

                    market_data[symbol] = {
                        "price": round(current_price, 2),
                        "change": round(change, 2),
                        "change_pct": round(change_pct, 2),
                    }

            return market_data

        except Exception as e:
            print(f"Error fetching market data: {e}")
            return {}

    def analyze_market_sentiment(self, market_data: Dict[str, Any]) -> str:
        """Analyze overall market sentiment based on key indicators"""
        if not market_data:
            return "UNKNOWN"

        positive_count = 0
        negative_count = 0

        for symbol, data in market_data.items():
            if symbol == "VIX":
                # VIX is inverse - lower is better
                if data["change"] < 0:
                    positive_count += 1
                else:
                    negative_count += 1
            else:
                if data["change"] > 0:
                    positive_count += 1
                else:
                    negative_count += 1

        if positive_count > negative_count:
            return "BULLISH"
        elif negative_count > positive_count:
            return "BEARISH"
        else:
            return "NEUTRAL"

    def generate_financial_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive financial dashboard"""
        print("🔍 Generating Financial Intelligence Dashboard...")

        # Get market data
        market_data = self.get_market_data()
        market_sentiment = self.analyze_market_sentiment(market_data)

        # Generate financial metrics
        financial_metrics = {
            "market_overview": market_data,
            "sentiment": market_sentiment,
            "timestamp": datetime.now().isoformat(),
            "dashboard_type": "financial_intelligence",
        }

        # Generate HTML dashboard if plotly available
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots

            # Create market overview chart
            symbols = list(market_data.keys())
            changes = [market_data[s]["change_pct"] for s in symbols]

            fig = make_subplots(
                rows=1, cols=1, subplot_titles=("Market Performance Today")
            )

            colors = ["green" if x > 0 else "red" for x in changes]

            fig.add_trace(
                go.Bar(
                    x=symbols,
                    y=changes,
                    marker_color=colors,
                    text=[f"{x:.2f}%" for x in changes],
                    textposition="auto",
                )
            )

            fig.update_layout(
                title="IntelForge Financial Intelligence Dashboard",
                xaxis_title="Market Indicators",
                yaxis_title="Change (%)",
                showlegend=False,
            )

            # Save dashboard
            dashboard_path = (
                self.reports_dir
                / f"financial_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            )
            fig.write_html(str(dashboard_path))

            financial_metrics["dashboard_path"] = str(dashboard_path)

        except ImportError:
            print("⚠️ Plotly not available - generating text dashboard only")

        return financial_metrics

    def generate_market_report(self) -> Dict[str, Any]:
        """Generate market-focused report"""
        print("📈 Generating Market Data Report...")

        market_data = self.get_market_data()

        market_report = {
            "report_type": "market_data",
            "timestamp": datetime.now().isoformat(),
            "market_data": market_data,
            "sentiment": self.analyze_market_sentiment(market_data),
            "summary": self._generate_market_summary(market_data),
        }

        return market_report

    def _generate_market_summary(self, market_data: Dict[str, Any]) -> str:
        """Generate human-readable market summary"""
        if not market_data:
            return "Market data unavailable"

        summary_parts = []

        for symbol, data in market_data.items():
            direction = "up" if data["change"] > 0 else "down"
            summary_parts.append(
                f"{symbol}: {data['price']} ({direction} {abs(data['change_pct']):.2f}%)"
            )

        return "; ".join(summary_parts)

    def generate_monitoring_report(self) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        print("🔍 Generating Comprehensive Monitoring Report...")

        # Basic system metrics
        monitoring_data = {
            "system_info": {
                "timestamp": datetime.now().isoformat(),
                "platform": sys.platform,
                "python_version": sys.version,
                "working_directory": str(Path.cwd()),
            },
            "project_status": {
                "project_root": str(self.project_root),
                "reports_directory": str(self.reports_dir),
                "test_mode": self.test_mode,
            },
        }

        # Add memory usage if available
        try:
            import psutil

            process = psutil.Process()
            memory_info = process.memory_info()

            monitoring_data["system_metrics"] = {
                "memory_usage_mb": round(memory_info.rss / (1024 * 1024), 2),
                "memory_usage_percent": round(process.memory_percent(), 2),
                "cpu_percent": round(process.cpu_percent(), 2),
            }
        except ImportError:
            monitoring_data["system_metrics"] = {"status": "psutil not available"}

        return monitoring_data

    def save_report(self, report_data: Dict[str, Any], report_type: str) -> Path:
        """Save report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_type}_report_{timestamp}.json"
        filepath = self.reports_dir / filename

        with open(filepath, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"✅ {report_type.title()} report saved to: {filepath}")
        return filepath


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="IntelForge Enhanced Monitoring Dashboard"
    )
    parser.add_argument(
        "--market", action="store_true", help="Generate market data report"
    )
    parser.add_argument(
        "--financial",
        action="store_true",
        help="Generate financial intelligence dashboard",
    )
    parser.add_argument(
        "--monitoring",
        action="store_true",
        help="Generate comprehensive monitoring report",
    )
    parser.add_argument(
        "--test", action="store_true", help="Run in test mode (use mock data)"
    )
    parser.add_argument("--all", action="store_true", help="Generate all reports")

    args = parser.parse_args()

    # Default to monitoring if no specific option given
    if not any([args.market, args.financial, args.monitoring, args.all]):
        args.monitoring = True

    dashboard = EnhancedMonitoringDashboard(test_mode=args.test)

    print("🚀 IntelForge Enhanced Monitoring Dashboard")
    print(f"📊 Test Mode: {'Enabled' if args.test else 'Disabled'}")
    print(f"📁 Reports Directory: {dashboard.reports_dir}")
    print()

    if args.all or args.market:
        market_report = dashboard.generate_market_report()
        dashboard.save_report(market_report, "market")

    if args.all or args.financial:
        financial_report = dashboard.generate_financial_dashboard()
        dashboard.save_report(financial_report, "financial")

    if args.all or args.monitoring:
        monitoring_report = dashboard.generate_monitoring_report()
        dashboard.save_report(monitoring_report, "monitoring")

    print("\n✅ Enhanced monitoring dashboard complete!")


if __name__ == "__main__":
    main()
