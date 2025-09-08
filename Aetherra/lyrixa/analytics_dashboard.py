#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
[TOOL] ANALYTICS DASHBOARD (#6)
==========================

Interactive dashboard for visualizing analytics and insights from the
Analytics & Insights Engine. Integrates with existing Aetherra UI components.
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime
from typing import Any, Callable

# Set up logging
logger = logging.getLogger(__name__)

# Predefine optional symbols for type checkers
AnalyticsEngine: Any = None
InsightsEngine: Any = None
create_analytics_engine: Callable[..., Any] | None = None
create_insights_engine: Callable[..., Any] | None = None
AdvancedMemoryManager: Any = None
Flask: Any = None
request: Any = None

# Try to import analytics engine
try:
    from Aetherra.lyrixa.analytics_insights_engine import (  # type: ignore  # isort: skip
        AnalyticsEngine as _AnalyticsEngine,
        InsightsEngine as _InsightsEngine,
        create_analytics_engine as _create_analytics_engine,
        create_insights_engine as _create_insights_engine,
    )

    AnalyticsEngine = _AnalyticsEngine
    InsightsEngine = _InsightsEngine
    create_analytics_engine = _create_analytics_engine
    create_insights_engine = _create_insights_engine
    ANALYTICS_ENGINE_AVAILABLE = True
    logger.info("✅ Analytics Engine available")
except ImportError as e:
    ANALYTICS_ENGINE_AVAILABLE = False
    logger.warning(f"[WARN] Analytics Engine not available: {e}")

# Try to import advanced memory integration
try:
    from Aetherra.lyrixa.memory.advanced_memory_integration import (  # type: ignore
        AdvancedMemoryManager as _AdvancedMemoryManager,
    )

    AdvancedMemoryManager = _AdvancedMemoryManager
    MEMORY_INTEGRATION_AVAILABLE = True
    logger.info("✅ Advanced Memory Integration available")
except ImportError as e:
    MEMORY_INTEGRATION_AVAILABLE = False
    logger.warning(f"[WARN] Advanced Memory Integration not available: {e}")

# Try to import Flask for web interface
try:
    from flask import (  # type: ignore  # isort: skip
        Flask as _Flask,
        request as _request,
    )

    Flask = _Flask
    request = _request
    FLASK_AVAILABLE = True
    logger.info("✅ Flask available for web interface")
except ImportError as e:
    FLASK_AVAILABLE = False
    logger.warning(f"[WARN] Flask not available: {e}")


class AnalyticsDashboard:
    """
    📊 Main Analytics Dashboard

    Provides web-based interface for viewing analytics, insights, and system performance.
    Integrates with existing Aetherra components and the Analytics & Insights Engine.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        # Dashboard configuration
        self.host = self.config.get("host", "localhost")
        self.port = self.config.get("port", 8687)  # Different from main Aetherra port
        self.debug = self.config.get("debug", False)

        # Initialize engines
        self.analytics_engine = None
        self.insights_engine = None
        self.memory_manager = None
        self.flask_app = None

        # Dashboard state
        self.dashboard_stats = {
            "requests_served": 0,
            "last_refresh": None,
            "active_sessions": 0,
            "uptime_start": datetime.now(),
        }

        # Cache for dashboard data
        self.data_cache = {}
        self.cache_timeout = self.config.get("cache_timeout", 300)  # 5 minutes

        logger.info("📊 Analytics Dashboard initialized")

    async def initialize(self):
        """Initialize all dashboard components"""

        try:
            # Initialize analytics engine
            if ANALYTICS_ENGINE_AVAILABLE and create_analytics_engine:
                self.analytics_engine = create_analytics_engine(self.config.get("analytics", {}))  # type: ignore[misc]
                logger.info("✅ Analytics Engine initialized")

                # Initialize memory manager if available
                if MEMORY_INTEGRATION_AVAILABLE and AdvancedMemoryManager:
                    self.memory_manager = AdvancedMemoryManager()  # type: ignore[call-arg]
                    # Some implementations might not be async; guard with hasattr
                    if hasattr(self.memory_manager, "initialize"):
                        maybe_coro = self.memory_manager.initialize()
                        if getattr(maybe_coro, "__await__", None):  # async
                            await maybe_coro  # type: ignore[func-returns-value]
                    logger.info("✅ Memory Manager initialized")

                # Initialize insights engine
                if create_insights_engine and self.analytics_engine:
                    self.insights_engine = create_insights_engine(
                        self.analytics_engine, self.memory_manager
                    )  # type: ignore[misc]
                    logger.info("✅ Insights Engine initialized")

            # Initialize Flask app
            if FLASK_AVAILABLE:
                self._initialize_flask_app()
                logger.info("✅ Flask web interface initialized")

            logger.info("🚀 Analytics Dashboard fully initialized")
            return True

        except Exception as e:
            logger.error(f"❌ Dashboard initialization failed: {e}")
            return False

    # ---------------- CACHE UTILITIES -----------------
    def invalidate_cache(self, cache_key: str | None = None):
        """Invalidate cached dashboard data.

        If cache_key is None all cached entries are cleared.
        """
        if cache_key is None:
            self.data_cache.clear()
        else:
            self.data_cache.pop(cache_key, None)

    @property
    def uptime_seconds(self) -> float:
        """Return dashboard uptime in seconds."""
        start = self.dashboard_stats.get("uptime_start")
        if not start:
            return 0.0
        return (datetime.now() - start).total_seconds()

    def _initialize_flask_app(self):
        """Initialize Flask web application"""
        if not (FLASK_AVAILABLE and Flask):  # Flask not available, skip web setup
            return
        self.flask_app = Flask(__name__)  # type: ignore[operator]

        # Main dashboard route
        @self.flask_app.route("/")
        async def dashboard():
            return await self._render_dashboard()

        # API routes
        @self.flask_app.route("/api/metrics")
        async def api_metrics():
            return await self._get_metrics_api()

        @self.flask_app.route("/api/insights")
        async def api_insights():
            return await self._get_insights_api()

        @self.flask_app.route("/api/performance")
        async def api_performance():
            return await self._get_performance_api()

        @self.flask_app.route("/api/health")
        async def api_health():
            return await self._get_health_api()

        # Data collection endpoint
        @self.flask_app.route("/api/collect", methods=["POST"])
        async def api_collect():
            return await self._collect_metric_api()

        # Real-time updates endpoint
        @self.flask_app.route("/api/live")
        async def api_live():
            return await self._get_live_data_api()

    async def _render_dashboard(self) -> str:
        """Render the main dashboard HTML"""

        try:
            # Get dashboard data
            dashboard_data = await self._get_dashboard_data()

            # Update stats
            self.dashboard_stats["requests_served"] += 1
            self.dashboard_stats["last_refresh"] = datetime.now().isoformat()

            # Render HTML template
            return self._get_dashboard_html_template(dashboard_data)

        except Exception as e:
            logger.error(f"Dashboard rendering failed: {e}")
            return self._get_error_html_template(str(e))

    async def _get_dashboard_data(self) -> dict[str, Any]:
        """Get comprehensive dashboard data"""

        try:
            # Check cache
            cache_key = "dashboard_data"
            if self._is_cache_valid(cache_key):
                return self.data_cache[cache_key]["data"]

            dashboard_data = {
                "timestamp": datetime.now().isoformat(),
                "dashboard_stats": self.dashboard_stats.copy(),
                "system_available": {
                    "analytics_engine": ANALYTICS_ENGINE_AVAILABLE,
                    "memory_integration": MEMORY_INTEGRATION_AVAILABLE,
                    "flask": FLASK_AVAILABLE,
                },
            }

            # Get analytics data if available
            if self.analytics_engine:
                # Get recent insights
                insights = await self.analytics_engine.get_insights(limit=10)
                dashboard_data["recent_insights"] = insights

                # Get performance snapshot
                performance = await self.analytics_engine.get_performance_snapshot()
                dashboard_data["performance_snapshot"] = performance

                # Get analytics statistics
                analytics_stats = self.analytics_engine.get_analytics_statistics()
                dashboard_data["analytics_statistics"] = analytics_stats

            # Get comprehensive insights if available
            if self.insights_engine:
                comprehensive_insights = (
                    await self.insights_engine.generate_comprehensive_insights()
                )
                dashboard_data["comprehensive_insights"] = comprehensive_insights

            # Cache the data
            self.data_cache[cache_key] = {
                "data": dashboard_data,
                "timestamp": time.time(),
            }

            return dashboard_data

        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""

        if cache_key not in self.data_cache:
            return False

        cache_entry = self.data_cache[cache_key]
        age = time.time() - cache_entry["timestamp"]

        return age < self.cache_timeout

    async def _get_metrics_api(self) -> dict[str, Any]:
        """API endpoint for metrics data"""

        try:
            if not self.analytics_engine:
                return {"error": "Analytics engine not available"}

            # Get recent metrics from database
            performance = await self.analytics_engine.get_performance_snapshot()
            return {"status": "success", "data": performance}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _get_insights_api(self) -> dict[str, Any]:
        """API endpoint for insights data"""

        try:
            if not self.analytics_engine:
                return {"error": "Analytics engine not available"}

            # Get insights with filtering
            if not (FLASK_AVAILABLE and request):  # pragma: no cover - safety
                return {"error": "Flask request context not available"}
            category = request.args.get("category")  # type: ignore[union-attr]
            min_confidence = float(request.args.get("min_confidence", 0.0))  # type: ignore[union-attr]
            limit = int(request.args.get("limit", 20))  # type: ignore[union-attr]

            insights = await self.analytics_engine.get_insights(
                category=category, min_confidence=min_confidence, limit=limit
            )

            return {"status": "success", "data": insights}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _get_performance_api(self) -> dict[str, Any]:
        """API endpoint for performance data"""

        try:
            if not self.analytics_engine:
                return {"error": "Analytics engine not available"}

            performance = await self.analytics_engine.get_performance_snapshot()
            return {"status": "success", "data": performance}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _get_health_api(self) -> dict[str, Any]:
        """API endpoint for system health"""

        try:
            health_data = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "analytics_engine": "available" if self.analytics_engine else "unavailable",
                    "insights_engine": "available" if self.insights_engine else "unavailable",
                    "memory_manager": "available" if self.memory_manager else "unavailable",
                    "dashboard": "running",
                },
                "dashboard_stats": self.dashboard_stats.copy(),
            }

            if self.analytics_engine:
                performance = await self.analytics_engine.get_performance_snapshot()
                health_data["system_health"] = performance.get("system_health", {})

            return {"status": "success", "data": health_data}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _collect_metric_api(self) -> dict[str, Any]:
        """API endpoint for collecting metrics"""

        try:
            if not self.analytics_engine:
                return {"error": "Analytics engine not available"}

            if not (FLASK_AVAILABLE and request):  # pragma: no cover - safety
                return {"status": "error", "message": "Flask request not available"}
            data = request.get_json()  # type: ignore[union-attr]
            if not data:
                return {"status": "error", "message": "No data provided"}

            # Extract metric data
            name = data.get("name")
            value = data.get("value")
            category = data.get("category", "api")
            metadata = data.get("metadata", {})

            if name is None or value is None:
                return {"status": "error", "message": "Name and value required"}

            # Collect the metric
            success = await self.analytics_engine.collect_metric(
                name=name, value=float(value), category=category, metadata=metadata
            )

            if success:
                # Invalidate cached dashboard data so new metric surfaces quickly
                self.invalidate_cache("dashboard_data")
                return {"status": "success", "message": "Metric collected"}
            else:
                return {"status": "error", "message": "Failed to collect metric"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _get_live_data_api(self) -> dict[str, Any]:
        """API endpoint for live data updates"""

        try:
            live_data = {
                "timestamp": datetime.now().isoformat(),
                "dashboard_stats": self.dashboard_stats.copy(),
            }

            if self.analytics_engine:
                # Get recent analytics statistics
                stats = self.analytics_engine.get_analytics_statistics()
                live_data["analytics_stats"] = stats

                # Get quick health check
                quick_health = await self.analytics_engine._calculate_system_health()
                live_data["health_score"] = quick_health.get("score", 0)
                live_data["health_status"] = quick_health.get("status", "unknown")

            return {"status": "success", "data": live_data}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _get_dashboard_html_template(self, data: dict[str, Any]) -> str:
        """Get the HTML template for the dashboard"""

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aetherra Analytics Dashboard</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #ffffff;
            min-height: 100vh;
        }}

        .dashboard-header {{
            text-align: center;
            margin-bottom: 30px;
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }}

        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .dashboard-card {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .card-title {{
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #64ffda;
        }}

        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #ffffff;
            margin: 10px 0;
        }}

        .metric-label {{
            font-size: 0.9em;
            color: #b0bec5;
        }}

        .insight-item {{
            background: rgba(0, 0, 0, 0.2);
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 4px solid #64ffda;
        }}

        .status-good {{ color: #4caf50; }}
        .status-warning {{ color: #ff9800; }}
        .status-error {{ color: #f44336; }}

        .refresh-button {{
            background: #64ffda;
            color: #1e3c72;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
            cursor: pointer;
            margin: 10px;
        }}

        .refresh-button:hover {{
            background: #4dd0e1;
        }}

        .json-data {{
            background: rgba(0, 0, 0, 0.3);
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
            font-size: 0.8em;
            overflow-x: auto;
            white-space: pre-wrap;
        }}

        .component-status {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            margin: 2px;
        }}

        .available {{ background: #4caf50; }}
        .unavailable {{ background: #f44336; }}
    </style>
</head>
<body>
    <div class="dashboard-header">
        <h1>🌌 Aetherra Analytics Dashboard</h1>
        <p>Advanced Analytics & Insights Engine (#6)</p>
        <button class="refresh-button" onclick="location.reload()">🔄 Refresh Dashboard</button>
        <p><small>Last updated: {data.get("timestamp", "Unknown")}</small></p>
    </div>

    <div class="dashboard-grid">
        <div class="dashboard-card">
            <div class="card-title">📊 System Status</div>
            <div class="metric-value">{self._get_system_status_display(data)}</div>
            <div class="metric-label">Overall System Health</div>

            <h4>Components:</h4>
            {self._get_component_status_html(data.get("system_available", {}))}
        </div>

        <div class="dashboard-card">
            <div class="card-title">📈 Analytics Statistics</div>
            {self._get_analytics_stats_html(data)}
        </div>

        <div class="dashboard-card">
            <div class="card-title">🎯 Recent Insights</div>
            {self._get_insights_html(data.get("recent_insights", []))}
        </div>

        <div class="dashboard-card">
            <div class="card-title">⚡ Performance Snapshot</div>
            {self._get_performance_html(data.get("performance_snapshot", {}))}
        </div>
    </div>

    <div class="dashboard-card">
        <div class="card-title">🔍 Comprehensive Insights</div>
        {self._get_comprehensive_insights_html(data.get("comprehensive_insights", {}))}
    </div>

    <div class="dashboard-card">
        <div class="card-title">🛠️ Debug Information</div>
        <div class="json-data">{json.dumps(data.get("dashboard_stats", {}), indent=2)}</div>
    </div>

    <script>
        // Auto-refresh every 5 minutes
        setTimeout(function() {{
            location.reload();
        }}, 300000);

        // Live data updates every 30 seconds
        setInterval(function() {{
            fetch('/api/live')
                .then(response => response.json())
                .then(data => {{
                    console.log('Live data update:', data);
                    // Update live elements here
                }})
                .catch(error => console.error('Live update failed:', error));
        }}, 30000);
    </script>
</body>
</html>
        """

    def _get_system_status_display(self, data: dict[str, Any]) -> str:
        """Get system status display"""

        performance = data.get("performance_snapshot", {})
        health = performance.get("system_health", {})
        status = health.get("status", "unknown")
        score = health.get("score", 0)

        status_colors = {
            "excellent": "status-good",
            "good": "status-good",
            "fair": "status-warning",
            "poor": "status-error",
            "unknown": "status-warning",
        }

        color_class = status_colors.get(status, "status-warning")
        return f'<span class="{color_class}">{status.title()} ({score}%)</span>'

    def _get_component_status_html(self, components: dict[str, bool]) -> str:
        """Get component status HTML"""

        html = ""
        for component, available in components.items():
            status_class = "available" if available else "unavailable"
            status_text = "✅" if available else "❌"
            html += f'<div class="component-status {status_class}">{status_text} {component.replace("_", " ").title()}</div>'

        return html

    def _get_analytics_stats_html(self, data: dict[str, Any]) -> str:
        """Get analytics statistics HTML"""

        stats = data.get("analytics_statistics", {})

        html = f"""
        <div class="metric-value">{stats.get("metrics_collected", 0)}</div>
        <div class="metric-label">Metrics Collected</div>

        <div class="metric-value">{stats.get("insights_generated", 0)}</div>
        <div class="metric-label">Insights Generated</div>

        <div class="metric-value">{stats.get("patterns_discovered", 0)}</div>
        <div class="metric-label">Patterns Discovered</div>
        """

        return html

    def _get_insights_html(self, insights: list[dict[str, Any]]) -> str:
        """Get insights HTML"""

        if not insights:
            return "<p>No recent insights available.</p>"

        html = ""
        for insight in insights[:5]:  # Show top 5
            confidence = insight.get("confidence", 0)
            impact = insight.get("impact_score", 0)
            html += f"""
            <div class="insight-item">
                <strong>{insight.get("category", "General").title()}</strong><br>
                {insight.get("description", "No description")}
                <br><small>Confidence: {confidence:.1%} | Impact: {impact:.1%}</small>
            </div>
            """

        return html

    def _get_performance_html(self, performance: dict[str, Any]) -> str:
        """Get performance HTML"""

        if not performance:
            return "<p>No performance data available.</p>"

        total_metrics = performance.get("total_metrics", 0)
        total_insights = performance.get("total_insights", 0)

        html = f"""
        <div class="metric-value">{total_metrics:,}</div>
        <div class="metric-label">Total Metrics</div>

        <div class="metric-value">{total_insights}</div>
        <div class="metric-label">Total Insights</div>
        """

        category_stats = performance.get("category_statistics", {})
        if category_stats:
            html += "<h4>Category Statistics:</h4>"
            for category, stats in category_stats.items():
                html += (
                    f"<p><strong>{category.title()}:</strong> {stats.get('count', 0)} metrics</p>"
                )

        return html

    def _get_comprehensive_insights_html(self, insights: dict[str, Any]) -> str:
        """Get comprehensive insights HTML"""

        if not insights or "error" in insights:
            return "<p>Comprehensive insights not available.</p>"

        summary = insights.get("summary", {})

        html = f"""
        <div class="metric-value">{summary.get("total_insights", 0)}</div>
        <div class="metric-label">Total Insights Generated</div>

        <h4>Key Findings:</h4>
        """

        key_findings = summary.get("key_findings", [])
        for finding in key_findings[:3]:  # Show top 3
            html += f'<div class="insight-item">{finding}</div>'

        html += "<h4>Priority Actions:</h4>"
        priority_actions = summary.get("priority_actions", [])
        for action in priority_actions[:3]:  # Show top 3
            html += f'<div class="insight-item">{action}</div>'

        return html

    def _get_error_html_template(self, error: str) -> str:
        """Get error page HTML template"""

        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Aetherra Analytics Dashboard - Error</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #1e3c72;
            color: white;
            padding: 50px;
            text-align: center;
        }}
        .error-container {{
            background: rgba(244, 67, 54, 0.1);
            padding: 30px;
            border-radius: 10px;
            border: 1px solid #f44336;
        }}
    </style>
</head>
<body>
    <div class="error-container">
        <h1>❌ Dashboard Error</h1>
        <p>The analytics dashboard encountered an error:</p>
        <pre>{error}</pre>
        <button onclick="location.reload()">🔄 Retry</button>
    </div>
</body>
</html>
        """

    def run(self):
        """Run the dashboard server"""

        if not FLASK_AVAILABLE:
            logger.error("❌ Flask not available - cannot run web dashboard")
            return False

        if not self.flask_app:
            logger.error("❌ Flask app not initialized")
            return False

        try:
            logger.info(f"🚀 Starting Analytics Dashboard on http://{self.host}:{self.port}")
            self.flask_app.run(host=self.host, port=self.port, debug=self.debug, threaded=True)
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start dashboard server: {e}")
            return False

    async def collect_system_metrics(self):
        """Collect metrics about the dashboard itself"""

        if not self.analytics_engine:
            return

        try:
            # Collect dashboard metrics
            uptime = (datetime.now() - self.dashboard_stats["uptime_start"]).total_seconds()

            await self.analytics_engine.collect_metric("dashboard_uptime", uptime, "dashboard")

            await self.analytics_engine.collect_metric(
                "dashboard_requests",
                self.dashboard_stats["requests_served"],
                "dashboard",
            )

            await self.analytics_engine.collect_metric(
                "dashboard_active_sessions",
                self.dashboard_stats["active_sessions"],
                "dashboard",
            )

            # Uptime metric cached update invalidation for freshness
            self.invalidate_cache("dashboard_data")

        except Exception as e:
            logger.error(f"Failed to collect dashboard metrics: {e}")


# Convenience function
def create_analytics_dashboard(config: dict[str, Any] | None = None) -> AnalyticsDashboard:
    """Create and return an analytics dashboard instance"""
    return AnalyticsDashboard(config)


__all__ = ["AnalyticsDashboard", "create_analytics_dashboard"]
