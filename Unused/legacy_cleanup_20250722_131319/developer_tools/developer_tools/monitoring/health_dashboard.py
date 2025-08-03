"""
Project Health Dashboard - Real-time system monitoring for Aetherra & Lyrixa

This module provides comprehensive health monitoring including:
- Plugin status tracking
- Error rate monitoring
- Resource usage graphs
- Memory health checks
- Performance metrics
- Proactive alerting
"""

import os
import json
import time
import psutil
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler


@dataclass
class HealthConfig:
    """Configuration for health monitoring"""
    # Monitoring intervals
    check_interval: float = 30.0  # seconds
    metric_history_size: int = 100
    alert_cooldown: int = 300  # seconds

    # Thresholds
    memory_warning_threshold: float = 80.0  # percentage
    memory_critical_threshold: float = 95.0  # percentage
    cpu_warning_threshold: float = 80.0  # percentage
    error_rate_threshold: int = 5  # errors per minute

    # Paths
    log_file: str = "health_monitor.log"
    metrics_file: str = "health_metrics.json"
    alerts_file: str = "health_alerts.json"

    # Web interface
    web_port: int = 8080
    auto_open_browser: bool = False

    # Plugins to monitor
    plugin_directories: List[str] = field(default_factory=lambda: ["plugins/", "src/plugins/"])

    # Memory monitoring
    memory_paths: List[str] = field(default_factory=lambda: ["memory_store.json", "data/memory/"])


@dataclass
class HealthMetric:
    """Individual health metric"""
    timestamp: float
    value: float
    category: str
    name: str
    status: str = "normal"  # normal, warning, critical
    details: Optional[Dict[str, Any]] = None


@dataclass
class HealthAlert:
    """Health alert notification"""
    timestamp: float
    category: str
    level: str  # warning, critical
    message: str
    details: Dict[str, Any]
    resolved: bool = False


class ProjectHealthDashboard:
    """Comprehensive project health monitoring system"""

    def __init__(self, config: Optional[HealthConfig] = None):
        self.config = config or HealthConfig()
        self.metrics: List[HealthMetric] = []
        self.alerts: List[HealthAlert] = []
        self.is_running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.last_alert_times: Dict[str, float] = {}

        # Setup logging
        logging.basicConfig(
            filename=self.config.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Load existing data
        self._load_metrics()
        self._load_alerts()

        self.logger.info("Project Health Dashboard initialized")

    def start_monitoring(self) -> None:
        """Start continuous health monitoring"""
        if self.is_running:
            self.logger.warning("Monitoring is already running")
            return

        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()

        self.logger.info("Health monitoring started")
        print("🔄 Project Health Dashboard - Monitoring started")

    def stop_monitoring(self) -> None:
        """Stop health monitoring"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)

        self._save_metrics()
        self._save_alerts()

        self.logger.info("Health monitoring stopped")
        print("⏹️ Project Health Dashboard - Monitoring stopped")

    def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.is_running:
            try:
                # Collect all metrics
                self._collect_system_metrics()
                self._collect_memory_metrics()
                self._collect_plugin_metrics()
                self._collect_error_metrics()

                # Check for alerts
                self._check_alerts()

                # Cleanup old data
                self._cleanup_old_data()

                time.sleep(self.config.check_interval)

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.config.check_interval)

    def _collect_system_metrics(self) -> None:
        """Collect system resource metrics"""
        timestamp = time.time()

        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_status = "normal"
        if cpu_percent > self.config.cpu_warning_threshold:
            cpu_status = "warning" if cpu_percent < 95 else "critical"

        self._add_metric(HealthMetric(
            timestamp=timestamp,
            value=cpu_percent,
            category="system",
            name="cpu_usage",
            status=cpu_status,
            details={"cores": psutil.cpu_count()}
        ))

        # Memory usage
        memory = psutil.virtual_memory()
        memory_status = "normal"
        if memory.percent > self.config.memory_warning_threshold:
            memory_status = "warning" if memory.percent < self.config.memory_critical_threshold else "critical"

        self._add_metric(HealthMetric(
            timestamp=timestamp,
            value=memory.percent,
            category="system",
            name="memory_usage",
            status=memory_status,
            details={
                "total": memory.total,
                "available": memory.available,
                "used": memory.used
            }
        ))

        # Disk usage
        disk = psutil.disk_usage('.')
        disk_percent = (disk.used / disk.total) * 100
        disk_status = "normal"
        if disk_percent > 85:
            disk_status = "warning" if disk_percent < 95 else "critical"

        self._add_metric(HealthMetric(
            timestamp=timestamp,
            value=disk_percent,
            category="system",
            name="disk_usage",
            status=disk_status,
            details={
                "total": disk.total,
                "used": disk.used,
                "free": disk.free
            }
        ))

    def _collect_memory_metrics(self) -> None:
        """Collect memory store health metrics"""
        timestamp = time.time()

        for memory_path in self.config.memory_paths:
            if os.path.exists(memory_path):
                try:
                    if memory_path.endswith('.json'):
                        # JSON memory file
                        with open(memory_path, 'r', encoding='utf-8') as f:
                            memory_data = json.load(f)

                        memory_count = len(memory_data) if isinstance(memory_data, (list, dict)) else 0
                        file_size = os.path.getsize(memory_path)

                        self._add_metric(HealthMetric(
                            timestamp=timestamp,
                            value=memory_count,
                            category="memory",
                            name=f"memory_entries_{Path(memory_path).stem}",
                            status="normal",
                            details={
                                "file_size": file_size,
                                "path": memory_path
                            }
                        ))

                    elif os.path.isdir(memory_path):
                        # Memory directory
                        memory_files = [f for f in os.listdir(memory_path) if f.endswith('.json')]
                        total_size = sum(os.path.getsize(os.path.join(memory_path, f)) for f in memory_files)

                        self._add_metric(HealthMetric(
                            timestamp=timestamp,
                            value=len(memory_files),
                            category="memory",
                            name=f"memory_files_{Path(memory_path).name}",
                            status="normal",
                            details={
                                "total_size": total_size,
                                "path": memory_path
                            }
                        ))

                except Exception as e:
                    self.logger.error(f"Error collecting memory metrics for {memory_path}: {e}")

    def _collect_plugin_metrics(self) -> None:
        """Collect plugin health metrics"""
        timestamp = time.time()

        for plugin_dir in self.config.plugin_directories:
            if os.path.exists(plugin_dir):
                try:
                    plugin_files = [f for f in os.listdir(plugin_dir) if f.endswith('.py')]
                    plugin_count = len(plugin_files)

                    self._add_metric(HealthMetric(
                        timestamp=timestamp,
                        value=plugin_count,
                        category="plugins",
                        name=f"plugin_count_{Path(plugin_dir).name}",
                        status="normal",
                        details={
                            "plugin_files": plugin_files,
                            "directory": plugin_dir
                        }
                    ))

                except Exception as e:
                    self.logger.error(f"Error collecting plugin metrics for {plugin_dir}: {e}")

    def _collect_error_metrics(self) -> None:
        """Collect error rate metrics from logs"""
        timestamp = time.time()

        try:
            # Count recent errors from log file
            error_count = 0
            warning_count = 0

            if os.path.exists(self.config.log_file):
                cutoff_time = datetime.now() - timedelta(minutes=5)

                with open(self.config.log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if 'ERROR' in line:
                            try:
                                log_time_str = line.split(' - ')[0]
                                log_time = datetime.strptime(log_time_str, '%Y-%m-%d %H:%M:%S,%f')
                                if log_time > cutoff_time:
                                    error_count += 1
                            except Exception:
                                pass
                        elif 'WARNING' in line:
                            try:
                                log_time_str = line.split(' - ')[0]
                                log_time = datetime.strptime(log_time_str, '%Y-%m-%d %H:%M:%S,%f')
                                if log_time > cutoff_time:
                                    warning_count += 1
                            except Exception:
                                pass

            error_status = "normal"
            if error_count > self.config.error_rate_threshold:
                error_status = "critical"
            elif error_count > 0:
                error_status = "warning"

            self._add_metric(HealthMetric(
                timestamp=timestamp,
                value=error_count,
                category="errors",
                name="error_rate_5min",
                status=error_status,
                details={"warning_count": warning_count}
            ))

        except Exception as e:
            self.logger.error(f"Error collecting error metrics: {e}")

    def _add_metric(self, metric: HealthMetric) -> None:
        """Add a metric to the collection"""
        self.metrics.append(metric)

        # Keep only recent metrics
        if len(self.metrics) > self.config.metric_history_size:
            self.metrics = self.metrics[-self.config.metric_history_size:]

    def _check_alerts(self) -> None:
        """Check for alert conditions"""
        if not self.metrics:
            return

        recent_metrics = [m for m in self.metrics if time.time() - m.timestamp < 300]  # Last 5 minutes

        for metric in recent_metrics:
            if metric.status in ["warning", "critical"]:
                alert_key = f"{metric.category}_{metric.name}_{metric.status}"

                # Check cooldown
                if alert_key in self.last_alert_times:
                    if time.time() - self.last_alert_times[alert_key] < self.config.alert_cooldown:
                        continue

                # Create alert
                alert = HealthAlert(
                    timestamp=time.time(),
                    category=metric.category,
                    level=metric.status,
                    message=f"{metric.category.title()} {metric.name} is {metric.status}: {metric.value}",
                    details=metric.details or {}
                )

                self.alerts.append(alert)
                self.last_alert_times[alert_key] = time.time()

                self.logger.warning(f"Health Alert: {alert.message}")
                print(f"[WARN] {alert.message}")

    def _cleanup_old_data(self) -> None:
        """Remove old metrics and resolved alerts"""
        cutoff_time = time.time() - (24 * 3600)  # 24 hours

        # Clean old metrics
        self.metrics = [m for m in self.metrics if m.timestamp > cutoff_time]

        # Clean old resolved alerts
        self.alerts = [a for a in self.alerts if not a.resolved or a.timestamp > cutoff_time]

    def get_current_status(self) -> Dict[str, Any]:
        """Get current health status summary"""
        if not self.metrics:
            return {"status": "no_data", "message": "No metrics available"}

        recent_metrics = [m for m in self.metrics if time.time() - m.timestamp < 300]

        if not recent_metrics:
            return {"status": "stale", "message": "No recent metrics"}

        # Determine overall status
        critical_count = len([m for m in recent_metrics if m.status == "critical"])
        warning_count = len([m for m in recent_metrics if m.status == "warning"])

        if critical_count > 0:
            overall_status = "critical"
        elif warning_count > 0:
            overall_status = "warning"
        else:
            overall_status = "healthy"

        # Get latest metrics by category
        latest_metrics = {}
        for metric in reversed(recent_metrics):
            key = f"{metric.category}_{metric.name}"
            if key not in latest_metrics:
                latest_metrics[key] = metric

        return {
            "status": overall_status,
            "timestamp": time.time(),
            "metrics_count": len(recent_metrics),
            "critical_issues": critical_count,
            "warnings": warning_count,
            "latest_metrics": {k: {
                "value": v.value,
                "status": v.status,
                "timestamp": v.timestamp
            } for k, v in latest_metrics.items()},
            "active_alerts": len([a for a in self.alerts if not a.resolved])
        }

    def get_metrics_summary(self, category: Optional[str] = None, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary for a time period"""
        cutoff_time = time.time() - (hours * 3600)
        filtered_metrics = [m for m in self.metrics if m.timestamp > cutoff_time]

        if category:
            filtered_metrics = [m for m in filtered_metrics if m.category == category]

        if not filtered_metrics:
            return {"error": "No metrics found for the specified criteria"}

        # Group by category and name
        grouped = {}
        for metric in filtered_metrics:
            key = f"{metric.category}_{metric.name}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(metric)

        # Calculate summaries
        summaries = {}
        for key, metrics in grouped.items():
            values = [m.value for m in metrics]
            summaries[key] = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "latest": metrics[-1].value,
                "latest_status": metrics[-1].status,
                "latest_timestamp": metrics[-1].timestamp
            }

        return {
            "time_range_hours": hours,
            "total_metrics": len(filtered_metrics),
            "categories": list(set(m.category for m in filtered_metrics)),
            "summaries": summaries
        }

    def start_web_interface(self) -> str:
        """Start web-based dashboard interface"""
        try:
            # Create simple web server for dashboard
            handler = self._create_web_handler()
            httpd = HTTPServer(("localhost", self.config.web_port), handler)

            # Start server in background thread
            server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            server_thread.start()

            url = f"http://localhost:{self.config.web_port}"

            if self.config.auto_open_browser:
                webbrowser.open(url)

            self.logger.info(f"Web interface started at {url}")
            print(f"🌐 Health Dashboard available at: {url}")

            return url

        except Exception as e:
            self.logger.error(f"Failed to start web interface: {e}")
            return f"Error: {e}"

    def _create_web_handler(self):
        """Create HTTP request handler for web interface"""
        dashboard = self

        class DashboardHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/":
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(dashboard._generate_dashboard_html().encode())
                elif self.path == "/api/status":
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    status = json.dumps(dashboard.get_current_status(), indent=2)
                    self.wfile.write(status.encode())
                elif self.path.startswith("/api/metrics"):
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    metrics = json.dumps(dashboard.get_metrics_summary(), indent=2)
                    self.wfile.write(metrics.encode())
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b"Not Found")

        return DashboardHandler

    def _generate_dashboard_html(self) -> str:
        """Generate HTML for web dashboard"""
        status = self.get_current_status()

        status_color = {
            "healthy": "#28a745",
            "warning": "#ffc107",
            "critical": "#dc3545",
            "no_data": "#6c757d",
            "stale": "#6c757d"
        }.get(status.get("status", "no_data"), "#6c757d")

        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Aetherra & Lyrixa - Health Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .status-card {{ background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .status-indicator {{ width: 20px; height: 20px; border-radius: 50%; display: inline-block; margin-right: 10px; background: {status_color}; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .metric-card {{ background: white; border-radius: 10px; padding: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 2em; font-weight: bold; margin: 10px 0; }}
        .metric-name {{ color: #666; text-transform: uppercase; font-size: 0.9em; letter-spacing: 1px; }}
        .timestamp {{ color: #999; font-size: 0.9em; }}
        .refresh-btn {{ background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }}
        .refresh-btn:hover {{ background: #0056b3; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔬 Aetherra & Lyrixa Health Dashboard</h1>
        <p>Real-time project health monitoring</p>
    </div>

    <div class="status-card">
        <h2><span class="status-indicator"></span>Overall Status: {status.get('status', 'Unknown').title()}</h2>
        <p>Last updated: {datetime.fromtimestamp(status.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S') if status.get('timestamp') else 'Never'}</p>
        <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
    </div>

    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-name">Active Alerts</div>
            <div class="metric-value" style="color: #dc3545;">{status.get('active_alerts', 0)}</div>
        </div>

        <div class="metric-card">
            <div class="metric-name">Critical Issues</div>
            <div class="metric-value" style="color: #dc3545;">{status.get('critical_issues', 0)}</div>
        </div>

        <div class="metric-card">
            <div class="metric-name">Warnings</div>
            <div class="metric-value" style="color: #ffc107;">{status.get('warnings', 0)}</div>
        </div>

        <div class="metric-card">
            <div class="metric-name">Total Metrics</div>
            <div class="metric-value" style="color: #007bff;">{status.get('metrics_count', 0)}</div>
        </div>
    </div>

    <div class="status-card">
        <h3>Latest Metrics</h3>
        <div class="metric-grid">
            {self._generate_metrics_html(status.get('latest_metrics', {}))}
        </div>
    </div>

    <div class="status-card">
        <h3>API Endpoints</h3>
        <ul>
            <li><a href="/api/status">/api/status</a> - Current status JSON</li>
            <li><a href="/api/metrics">/api/metrics</a> - Metrics summary JSON</li>
        </ul>
    </div>

    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
        """

    def _generate_metrics_html(self, metrics: Dict[str, Any]) -> str:
        """Generate HTML for metrics display"""
        html = ""
        for name, data in metrics.items():
            status_color = {
                "normal": "#28a745",
                "warning": "#ffc107",
                "critical": "#dc3545"
            }.get(data.get("status", "normal"), "#6c757d")

            html += f"""
            <div class="metric-card">
                <div class="metric-name">{name.replace('_', ' ').title()}</div>
                <div class="metric-value" style="color: {status_color};">{data.get('value', 'N/A')}</div>
                <div class="timestamp">Status: {data.get('status', 'unknown')}</div>
            </div>
            """

        return html

    def _save_metrics(self) -> None:
        """Save metrics to file"""
        try:
            # Save only recent metrics to avoid huge files
            recent_metrics = [m for m in self.metrics if time.time() - m.timestamp < 86400]  # 24 hours

            data = {
                "timestamp": time.time(),
                "metrics": [
                    {
                        "timestamp": m.timestamp,
                        "value": m.value,
                        "category": m.category,
                        "name": m.name,
                        "status": m.status,
                        "details": m.details
                    }
                    for m in recent_metrics
                ]
            }

            with open(self.config.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save metrics: {e}")

    def _load_metrics(self) -> None:
        """Load metrics from file"""
        try:
            if os.path.exists(self.config.metrics_file):
                with open(self.config.metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.metrics = [
                    HealthMetric(
                        timestamp=m["timestamp"],
                        value=m["value"],
                        category=m["category"],
                        name=m["name"],
                        status=m["status"],
                        details=m.get("details")
                    )
                    for m in data.get("metrics", [])
                ]

                self.logger.info(f"Loaded {len(self.metrics)} metrics from file")

        except Exception as e:
            self.logger.error(f"Failed to load metrics: {e}")

    def _save_alerts(self) -> None:
        """Save alerts to file"""
        try:
            data = {
                "timestamp": time.time(),
                "alerts": [
                    {
                        "timestamp": a.timestamp,
                        "category": a.category,
                        "level": a.level,
                        "message": a.message,
                        "details": a.details,
                        "resolved": a.resolved
                    }
                    for a in self.alerts
                ]
            }

            with open(self.config.alerts_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save alerts: {e}")

    def _load_alerts(self) -> None:
        """Load alerts from file"""
        try:
            if os.path.exists(self.config.alerts_file):
                with open(self.config.alerts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.alerts = [
                    HealthAlert(
                        timestamp=a["timestamp"],
                        category=a["category"],
                        level=a["level"],
                        message=a["message"],
                        details=a["details"],
                        resolved=a.get("resolved", False)
                    )
                    for a in data.get("alerts", [])
                ]

                self.logger.info(f"Loaded {len(self.alerts)} alerts from file")

        except Exception as e:
            self.logger.error(f"Failed to load alerts: {e}")

    def run_health_checks(self) -> Dict[str, Any]:
        """Run comprehensive health checks and return results"""
        health_results = {
            "overall_health": "healthy",
            "timestamp": time.time(),
            "checks": {},
            "issues": []
        }

        try:
            # Get current status
            status = self.get_current_status()
            health_results["overall_health"] = status.get("status", "unknown")

            # System health checks
            if psutil:
                # CPU check
                cpu_percent = psutil.cpu_percent(interval=1)
                health_results["checks"]["cpu"] = {
                    "value": cpu_percent,
                    "status": "normal" if cpu_percent < 80 else "warning" if cpu_percent < 95 else "critical"
                }
                if cpu_percent > 95:
                    health_results["issues"].append(f"Critical CPU usage: {cpu_percent:.1f}%")

                # Memory check
                memory = psutil.virtual_memory()
                health_results["checks"]["memory"] = {
                    "value": memory.percent,
                    "status": "normal" if memory.percent < 80 else "warning" if memory.percent < 95 else "critical"
                }
                if memory.percent > 95:
                    health_results["issues"].append(f"Critical memory usage: {memory.percent:.1f}%")

                # Disk check
                disk = psutil.disk_usage('.')
                disk_percent = (disk.used / disk.total) * 100
                health_results["checks"]["disk"] = {
                    "value": disk_percent,
                    "status": "normal" if disk_percent < 85 else "warning" if disk_percent < 95 else "critical"
                }
                if disk_percent > 95:
                    health_results["issues"].append(f"Critical disk usage: {disk_percent:.1f}%")

            # Plugin directory checks
            plugin_issues = 0
            for plugin_dir in self.config.plugin_directories:
                if os.path.exists(plugin_dir):
                    try:
                        files = os.listdir(plugin_dir)
                        health_results["checks"][f"plugin_dir_{plugin_dir}"] = {
                            "status": "normal",
                            "file_count": len(files)
                        }
                    except Exception as e:
                        plugin_issues += 1
                        health_results["issues"].append(f"Plugin directory error ({plugin_dir}): {e}")
                else:
                    health_results["checks"][f"plugin_dir_{plugin_dir}"] = {
                        "status": "warning",
                        "message": "Directory not found"
                    }

            # Memory path checks
            memory_issues = 0
            for memory_path in self.config.memory_paths:
                if os.path.exists(memory_path):
                    health_results["checks"][f"memory_path_{memory_path}"] = {
                        "status": "normal",
                        "exists": True
                    }
                else:
                    memory_issues += 1
                    health_results["checks"][f"memory_path_{memory_path}"] = {
                        "status": "warning",
                        "exists": False
                    }

            # Update overall health based on issues
            if health_results["issues"]:
                health_results["overall_health"] = "critical" if any("Critical" in issue for issue in health_results["issues"]) else "warning"

        except Exception as e:
            health_results["overall_health"] = "error"
            health_results["issues"].append(f"Health check error: {e}")

        return health_results

    def generate_health_report(self) -> str:
        """Generate a comprehensive health report"""
        health_status = self.run_health_checks()
        current_status = self.get_current_status()
        metrics_summary = self.get_metrics_summary(hours=24)

        report_lines = [
            "# 🏥 Project Health Dashboard Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 📊 Overall Health Status",
            f"**Status:** {health_status['overall_health'].upper()}",
            f"**Active Alerts:** {current_status.get('active_alerts', 0)}",
            f"**Total Issues:** {len(health_status.get('issues', []))}",
            ""
        ]

        # Issues section
        if health_status.get('issues'):
            report_lines.extend([
                "## 🚨 Current Issues",
                ""
            ])
            for issue in health_status['issues']:
                report_lines.append(f"- {issue}")
            report_lines.append("")

        # System metrics
        if 'checks' in health_status:
            report_lines.extend([
                "## 💻 System Metrics",
                ""
            ])
            for check_name, check_data in health_status['checks'].items():
                status_emoji = "✅" if check_data.get('status') == 'normal' else "[WARN]" if check_data.get('status') == 'warning' else "❌"
                if 'value' in check_data:
                    report_lines.append(f"{status_emoji} **{check_name.replace('_', ' ').title()}:** {check_data['value']:.1f}%")
                else:
                    report_lines.append(f"{status_emoji} **{check_name.replace('_', ' ').title()}:** {check_data.get('message', 'OK')}")
            report_lines.append("")

        # Metrics summary
        if metrics_summary:
            report_lines.extend([
                "## 📈 24-Hour Metrics Summary",
                f"**Total Metrics:** {metrics_summary.get('total_metrics', 0)}",
                f"**Categories:** {', '.join(metrics_summary.get('categories', []))}",
                ""
            ])

        # Recent alerts
        recent_alerts = [a for a in self.alerts if time.time() - a.timestamp < 86400]  # 24 hours
        if recent_alerts:
            report_lines.extend([
                "## 🔔 Recent Alerts (24h)",
                ""
            ])
            for alert in recent_alerts[-10:]:  # Last 10 alerts
                alert_time = datetime.fromtimestamp(alert.timestamp).strftime('%H:%M:%S')
                level_emoji = "[WARN]" if alert.level == 'warning' else "❌"
                report_lines.append(f"{level_emoji} **{alert_time}** - {alert.category}: {alert.message}")
            report_lines.append("")

        # Recommendations
        report_lines.extend([
            "## 💡 Recommendations",
            ""
        ])

        if health_status['overall_health'] == 'healthy':
            report_lines.append("- ✅ System is running optimally")
        else:
            if any("CPU" in issue for issue in health_status.get('issues', [])):
                report_lines.append("- Consider optimizing CPU-intensive operations")
            if any("memory" in issue.lower() for issue in health_status.get('issues', [])):
                report_lines.append("- Review memory usage and consider cleanup")
            if any("disk" in issue.lower() for issue in health_status.get('issues', [])):
                report_lines.append("- Clean up disk space or archive old files")

        report_lines.extend([
            "- Regularly monitor the health dashboard",
            "- Set up automated alerts for critical issues",
            "- Review and update monitoring thresholds as needed",
            "",
            "---",
            f"Report generated by Aetherra Project Health Dashboard v{getattr(self, 'version', '1.0.0')}"
        ])

        return "\n".join(report_lines)


def demo_health_dashboard():
    """Demonstrate the Project Health Dashboard"""
    print("🔬 Project Health Dashboard Demo")
    print("=" * 50)

    # Create dashboard with demo config
    config = HealthConfig()
    config.check_interval = 5.0  # Check every 5 seconds for demo
    config.auto_open_browser = False

    dashboard = ProjectHealthDashboard(config)

    try:
        print("\n1. Starting health monitoring...")
        dashboard.start_monitoring()

        print("2. Waiting for initial metrics...")
        time.sleep(8)  # Wait for some metrics to be collected

        print("\n3. Current status:")
        status = dashboard.get_current_status()
        print(json.dumps(status, indent=2))

        print("\n4. Metrics summary:")
        summary = dashboard.get_metrics_summary(hours=1)
        print(json.dumps(summary, indent=2))

        print("\n5. Starting web interface...")
        url = dashboard.start_web_interface()
        print(f"Dashboard available at: {url}")

        print("\n6. Monitoring for 30 seconds...")
        time.sleep(30)

        print("\n7. Final status:")
        final_status = dashboard.get_current_status()
        print(json.dumps(final_status, indent=2))

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo error: {e}")
    finally:
        print("\n8. Stopping monitoring...")
        dashboard.stop_monitoring()
        print("✅ Demo complete!")


if __name__ == "__main__":
    demo_health_dashboard()
