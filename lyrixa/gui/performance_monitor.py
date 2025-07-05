"""
Performance Monitor for Lyrixa AI Assistant

Provides real-time monitoring and visualization of:
- System resource usage (CPU, Memory, Disk)
- Application performance metrics
- Database performance
- API response times
- Health status indicators
"""

import logging
import sqlite3
import sys
import threading
import time
from collections import deque
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import psutil

try:
    from PySide6.QtCore import Qt, QThread, QTimer, Signal
    from PySide6.QtGui import QColor, QFont, QPalette
    from PySide6.QtWidgets import (
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QProgressBar,
        QPushButton,
        QScrollArea,
        QSplitter,
        QTableWidget,
        QTableWidgetItem,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False

    # Mock classes for when PySide6 is not available
    class QWidget:
        def __init__(self, *args, **kwargs):
            pass

        def resize(self, *args):
            pass

        def show(self):
            pass

    class Signal:
        def __init__(self, *args):
            pass

        def connect(self, *args):
            pass

        def emit(self, *args):
            pass

    class QThread:
        pass

    class QTimer:
        def __init__(self, *args):
            pass

        def start(self, *args):
            pass

        def stop(self):
            pass

    # Mock other Qt classes
    Qt = type("Qt", (), {"AlignCenter": 0, "AlignLeft": 0})
    QVBoxLayout = QHBoxLayout = QTabWidget = QLabel = QPushButton = QWidget
    QGroupBox = QProgressBar = QTableWidget = QTableWidgetItem = QWidget
    QGridLayout = QFrame = QScrollArea = QSplitter = QTextEdit = QWidget
    QFont = QColor = QPalette = QWidget

try:
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemMetrics:
    """Collect and manage system performance metrics."""

    def __init__(self, history_size: int = 100):
        self.history_size = history_size
        self.cpu_history = deque(maxlen=history_size)
        self.memory_history = deque(maxlen=history_size)
        self.disk_history = deque(maxlen=history_size)
        self.network_history = deque(maxlen=history_size)
        self.timestamps = deque(maxlen=history_size)

        # Initialize psutil process for current application
        try:
            self.process = psutil.Process()
        except Exception:
            self.process = None

    def collect_metrics(self):
        """Collect current system metrics."""
        timestamp = datetime.now()

        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=None)

            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Disk metrics
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100

            # Network metrics (bytes sent/received per second)
            network = psutil.net_io_counters()
            if self.network_history:
                prev_network = self.network_history[-1]["raw"]
                prev_time = self.timestamps[-1]
                time_diff = (timestamp - prev_time).total_seconds()

                if time_diff > 0:
                    bytes_sent_per_sec = (
                        network.bytes_sent - prev_network.bytes_sent
                    ) / time_diff
                    bytes_recv_per_sec = (
                        network.bytes_recv - prev_network.bytes_recv
                    ) / time_diff
                else:
                    bytes_sent_per_sec = 0
                    bytes_recv_per_sec = 0
            else:
                bytes_sent_per_sec = 0
                bytes_recv_per_sec = 0

            # Application-specific metrics
            app_metrics = self.get_application_metrics()

            # Store metrics
            self.cpu_history.append(
                {
                    "percent": cpu_percent,
                    "app_percent": app_metrics.get("cpu_percent", 0),
                    "timestamp": timestamp,
                }
            )

            self.memory_history.append(
                {
                    "system_percent": memory_percent,
                    "system_used": memory.used,
                    "system_total": memory.total,
                    "app_memory": app_metrics.get("memory_mb", 0),
                    "timestamp": timestamp,
                }
            )

            self.disk_history.append(
                {
                    "percent": disk_percent,
                    "used": disk.used,
                    "total": disk.total,
                    "timestamp": timestamp,
                }
            )

            self.network_history.append(
                {
                    "bytes_sent_per_sec": bytes_sent_per_sec,
                    "bytes_recv_per_sec": bytes_recv_per_sec,
                    "total_sent": network.bytes_sent,
                    "total_recv": network.bytes_recv,
                    "raw": network,
                    "timestamp": timestamp,
                }
            )

            self.timestamps.append(timestamp)

            return {
                "cpu": cpu_percent,
                "memory": memory_percent,
                "disk": disk_percent,
                "network_send": bytes_sent_per_sec,
                "network_recv": bytes_recv_per_sec,
                "app_metrics": app_metrics,
                "timestamp": timestamp,
            }

        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return None

    def get_application_metrics(self) -> Dict[str, Any]:
        """Get application-specific performance metrics."""
        metrics = {}

        if self.process:
            try:
                # CPU usage for this process
                metrics["cpu_percent"] = self.process.cpu_percent()

                # Memory usage for this process
                memory_info = self.process.memory_info()
                metrics["memory_mb"] = memory_info.rss / (1024 * 1024)  # Convert to MB

                # Number of threads
                metrics["num_threads"] = self.process.num_threads()

                # Number of file descriptors (Unix) or handles (Windows)
                try:
                    if hasattr(self.process, "num_fds"):
                        metrics["num_fds"] = self.process.num_fds()
                    else:
                        metrics["num_handles"] = self.process.num_handles()
                except Exception:
                    pass

            except Exception as e:
                logger.error(f"Error collecting application metrics: {e}")

        return metrics

    def get_health_status(self) -> str:
        """Determine overall system health status."""
        if not self.cpu_history or not self.memory_history:
            return "Unknown"

        latest_cpu = self.cpu_history[-1]["percent"]
        latest_memory = self.memory_history[-1]["system_percent"]
        latest_disk = self.disk_history[-1]["percent"] if self.disk_history else 0

        # Health thresholds
        if latest_cpu > 90 or latest_memory > 90 or latest_disk > 95:
            return "Critical"
        elif latest_cpu > 70 or latest_memory > 75 or latest_disk > 85:
            return "Warning"
        elif latest_cpu > 50 or latest_memory > 60 or latest_disk > 70:
            return "Moderate"
        else:
            return "Good"


class MetricsCollector(QThread if PYSIDE6_AVAILABLE else threading.Thread):
    """Background thread for collecting performance metrics."""

    metrics_updated = Signal(dict) if PYSIDE6_AVAILABLE else None

    def __init__(self, interval: float = 2.0):
        if PYSIDE6_AVAILABLE:
            super().__init__()
        else:
            super().__init__(daemon=True)

        self.interval = interval
        self.running = False
        self.metrics = SystemMetrics()

    def start_collection(self):
        """Start metrics collection."""
        self.running = True
        self.start()

    def stop_collection(self):
        """Stop metrics collection."""
        self.running = False
        if PYSIDE6_AVAILABLE:
            self.wait()
        else:
            self.join()

    def run(self):
        """Main collection loop."""
        while self.running:
            try:
                metrics_data = self.metrics.collect_metrics()

                if metrics_data and self.metrics_updated:
                    self.metrics_updated.emit(metrics_data)

                time.sleep(self.interval)

            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                time.sleep(1)  # Short delay before retrying


class MetricsChart(QWidget if PYSIDE6_AVAILABLE else object):
    """Chart widget for displaying performance metrics."""

    def __init__(self, title: str, parent=None):
        if not PYSIDE6_AVAILABLE:
            return

        super().__init__(parent)
        self.title = title
        self.data_points = deque(maxlen=50)  # Keep last 50 data points

        self.init_ui()

    def init_ui(self):
        """Initialize chart UI."""
        layout = QVBoxLayout()

        if MATPLOTLIB_AVAILABLE:
            self.figure = Figure(figsize=(6, 3), dpi=80)
            self.canvas = FigureCanvas(self.figure)
            self.ax = self.figure.add_subplot(111)
            layout.addWidget(self.canvas)
        else:
            placeholder = QLabel(f"{self.title}\n(Requires matplotlib)")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("border: 1px solid #ccc; margin: 10px;")
            layout.addWidget(placeholder)

        self.setLayout(layout)

    def update_chart(self, value: float, timestamp: datetime):
        """Update chart with new data point."""
        if not MATPLOTLIB_AVAILABLE:
            return

        self.data_points.append((timestamp, value))

        if len(self.data_points) >= 2:
            timestamps, values = zip(*self.data_points)

            self.ax.clear()
            self.ax.plot(timestamps, values, "b-", linewidth=2)
            self.ax.set_title(self.title, fontsize=10, fontweight="bold")
            self.ax.set_ylabel("Percentage (%)")
            self.ax.grid(True, alpha=0.3)

            # Format x-axis
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

            # Set y-axis limits
            self.ax.set_ylim(0, 100)

            # Rotate x-axis labels
            plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45, ha="right")

            self.figure.tight_layout()
            self.canvas.draw()


class HealthIndicator(QWidget if PYSIDE6_AVAILABLE else object):
    """Health status indicator widget."""

    def __init__(self, parent=None):
        if not PYSIDE6_AVAILABLE:
            return

        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize health indicator UI."""
        layout = QHBoxLayout()

        self.status_label = QLabel("●")
        self.status_label.setFont(QFont("Arial", 20))
        layout.addWidget(self.status_label)

        self.text_label = QLabel("Unknown")
        self.text_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.text_label)

        layout.addStretch()
        self.setLayout(layout)

        self.update_status("Unknown")

    def update_status(self, status: str):
        """Update health status display."""
        colors = {
            "Good": "#4CAF50",
            "Moderate": "#FF9800",
            "Warning": "#FF5722",
            "Critical": "#F44336",
            "Unknown": "#9E9E9E",
        }

        color = colors.get(status, "#9E9E9E")
        self.status_label.setStyleSheet(f"color: {color};")
        self.text_label.setText(status)
        self.text_label.setStyleSheet(f"color: {color};")


class MetricsTable(QWidget if PYSIDE6_AVAILABLE else object):
    """Table widget for displaying detailed metrics."""

    def __init__(self, parent=None):
        if not PYSIDE6_AVAILABLE:
            return

        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize metrics table UI."""
        layout = QVBoxLayout()

        # Header
        header_label = QLabel("📊 Detailed Metrics")
        header_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(header_label)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setMaximumHeight(300)

        layout.addWidget(self.table)
        self.setLayout(layout)

    def update_metrics(self, metrics_data: Dict[str, Any]):
        """Update table with new metrics data."""
        if not metrics_data:
            return

        # Prepare metrics for display
        display_metrics = [
            ("CPU Usage", f"{metrics_data.get('cpu', 0):.1f}%"),
            ("Memory Usage", f"{metrics_data.get('memory', 0):.1f}%"),
            ("Disk Usage", f"{metrics_data.get('disk', 0):.1f}%"),
            ("Network Send", f"{metrics_data.get('network_send', 0) / 1024:.1f} KB/s"),
            (
                "Network Receive",
                f"{metrics_data.get('network_recv', 0) / 1024:.1f} KB/s",
            ),
        ]

        # Add application metrics if available
        app_metrics = metrics_data.get("app_metrics", {})
        if app_metrics:
            display_metrics.extend(
                [
                    ("App CPU", f"{app_metrics.get('cpu_percent', 0):.1f}%"),
                    ("App Memory", f"{app_metrics.get('memory_mb', 0):.1f} MB"),
                    ("App Threads", str(app_metrics.get("num_threads", 0))),
                ]
            )

        # Update table
        self.table.setRowCount(len(display_metrics))

        for row, (metric, value) in enumerate(display_metrics):
            self.table.setItem(row, 0, QTableWidgetItem(metric))
            self.table.setItem(row, 1, QTableWidgetItem(value))

        self.table.resizeColumnsToContents()


class DatabaseMonitor(QWidget if PYSIDE6_AVAILABLE else object):
    """Monitor database performance and operations."""

    def __init__(self, db_path: str = None, parent=None):
        if not PYSIDE6_AVAILABLE:
            return

        super().__init__(parent)
        self.db_path = db_path or "lyrixa_anticipation.db"
        self.query_times = deque(maxlen=20)
        self.init_ui()

    def init_ui(self):
        """Initialize database monitor UI."""
        layout = QVBoxLayout()

        # Header
        header_label = QLabel("🗃️ Database Performance")
        header_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(header_label)

        # Database info
        info_layout = QVBoxLayout()

        self.db_path_label = QLabel(f"Database: {self.db_path}")
        self.db_path_label.setStyleSheet("font-family: monospace; color: #666;")
        info_layout.addWidget(self.db_path_label)

        self.db_size_label = QLabel("Size: Calculating...")
        info_layout.addWidget(self.db_size_label)

        self.query_time_label = QLabel("Avg Query Time: N/A")
        info_layout.addWidget(self.query_time_label)

        layout.addLayout(info_layout)

        # Performance test button
        test_btn = QPushButton("🔍 Test Database Performance")
        test_btn.clicked.connect(self.test_database_performance)
        layout.addWidget(test_btn)

        # Results area
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(150)
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

        self.setLayout(layout)

        # Update database info
        self.update_database_info()

    def update_database_info(self):
        """Update database information display."""
        try:
            # Get database file size
            import os

            if os.path.exists(self.db_path):
                size_bytes = os.path.getsize(self.db_path)
                size_mb = size_bytes / (1024 * 1024)
                self.db_size_label.setText(f"Size: {size_mb:.2f} MB")
            else:
                self.db_size_label.setText("Size: Database not found")

            # Update average query time
            if self.query_times:
                avg_time = sum(self.query_times) / len(self.query_times)
                self.query_time_label.setText(f"Avg Query Time: {avg_time:.3f}s")

        except Exception as e:
            logger.error(f"Error updating database info: {e}")

    def test_database_performance(self):
        """Test database performance with sample queries."""
        try:
            self.results_text.append("Testing database performance...")

            # Test connection time
            start_time = time.time()
            conn = sqlite3.connect(self.db_path)
            connection_time = time.time() - start_time

            # Test simple query
            start_time = time.time()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            query_time = time.time() - start_time

            self.query_times.append(query_time)

            # Test table sizes
            table_info = []
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                table_info.append(f"{table_name}: {count} rows")

            conn.close()

            # Display results
            results = [
                f"Connection time: {connection_time:.3f}s",
                f"Query time: {query_time:.3f}s",
                f"Tables found: {len(tables)}",
            ]
            results.extend(table_info)

            self.results_text.append("\n".join(results))
            self.results_text.append("---")

            self.update_database_info()

        except Exception as e:
            self.results_text.append(f"Error testing database: {e}")
            logger.error(f"Database test error: {e}")


class PerformanceMonitor(QWidget if PYSIDE6_AVAILABLE else object):
    """
    Comprehensive performance monitor for Lyrixa AI Assistant.

    Provides real-time monitoring and visualization of:
    - System resource usage
    - Application performance
    - Database operations
    - Health status indicators
    """

    # Signals
    performance_alert = Signal(str, str) if PYSIDE6_AVAILABLE else None

    def __init__(self, parent=None):
        if not PYSIDE6_AVAILABLE:
            logger.warning(
                "PySide6 not available. Performance monitor will not function."
            )
            return

        super().__init__(parent)
        self.metrics_collector = MetricsCollector()
        self.alert_thresholds = {"cpu": 85.0, "memory": 90.0, "disk": 95.0}

        self.init_ui()
        self.start_monitoring()

        logger.info("Performance Monitor initialized successfully")

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("⚡ Performance Monitor")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title_label)

        # Health indicator
        self.health_indicator = HealthIndicator()
        header_layout.addWidget(self.health_indicator)

        header_layout.addStretch()

        # Control buttons
        self.start_btn = QPushButton("▶ Start")
        self.start_btn.clicked.connect(self.start_monitoring)
        header_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏸ Stop")
        self.stop_btn.clicked.connect(self.stop_monitoring)
        header_layout.addWidget(self.stop_btn)

        layout.addLayout(header_layout)

        # Main content area
        main_splitter = QSplitter(Qt.Horizontal)

        # Left panel - Charts
        charts_widget = QWidget()
        charts_layout = QVBoxLayout()

        # Resource usage charts
        self.cpu_chart = MetricsChart("CPU Usage")
        charts_layout.addWidget(self.cpu_chart)

        self.memory_chart = MetricsChart("Memory Usage")
        charts_layout.addWidget(self.memory_chart)

        charts_widget.setLayout(charts_layout)
        main_splitter.addWidget(charts_widget)

        # Right panel - Details and database
        details_widget = QWidget()
        details_layout = QVBoxLayout()

        # Metrics table
        self.metrics_table = MetricsTable()
        details_layout.addWidget(self.metrics_table)

        # Database monitor
        self.database_monitor = DatabaseMonitor()
        details_layout.addWidget(self.database_monitor)

        details_widget.setLayout(details_layout)
        main_splitter.addWidget(details_widget)

        # Set splitter proportions
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 1)

        layout.addWidget(main_splitter)

        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #6c757d; font-style: italic;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def start_monitoring(self):
        """Start performance monitoring."""
        try:
            if not self.metrics_collector.running:
                self.metrics_collector.metrics_updated.connect(self.update_displays)
                self.metrics_collector.start_collection()

                self.start_btn.setEnabled(False)
                self.stop_btn.setEnabled(True)
                self.status_label.setText("Monitoring active")

                logger.info("Performance monitoring started")
        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
            self.status_label.setText(f"Error starting monitoring: {e}")

    def stop_monitoring(self):
        """Stop performance monitoring."""
        try:
            if self.metrics_collector.running:
                self.metrics_collector.stop_collection()

                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.status_label.setText("Monitoring stopped")

                logger.info("Performance monitoring stopped")
        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")
            self.status_label.setText(f"Error stopping monitoring: {e}")

    def update_displays(self, metrics_data: Dict[str, Any]):
        """Update all display components with new metrics."""
        try:
            timestamp = metrics_data["timestamp"]

            # Update charts
            self.cpu_chart.update_chart(metrics_data["cpu"], timestamp)
            self.memory_chart.update_chart(metrics_data["memory"], timestamp)

            # Update metrics table
            self.metrics_table.update_metrics(metrics_data)

            # Update health indicator
            health_status = self.metrics_collector.metrics.get_health_status()
            self.health_indicator.update_status(health_status)

            # Check for performance alerts
            self.check_performance_alerts(metrics_data)

            # Update status
            self.status_label.setText(f"Last update: {timestamp.strftime('%H:%M:%S')}")

        except Exception as e:
            logger.error(f"Error updating displays: {e}")

    def check_performance_alerts(self, metrics_data: Dict[str, Any]):
        """Check for performance threshold violations."""
        try:
            alerts = []

            # Check CPU usage
            if metrics_data["cpu"] > self.alert_thresholds["cpu"]:
                alerts.append(f"High CPU usage: {metrics_data['cpu']:.1f}%")

            # Check memory usage
            if metrics_data["memory"] > self.alert_thresholds["memory"]:
                alerts.append(f"High memory usage: {metrics_data['memory']:.1f}%")

            # Check disk usage
            if metrics_data["disk"] > self.alert_thresholds["disk"]:
                alerts.append(f"High disk usage: {metrics_data['disk']:.1f}%")

            # Emit alerts
            for alert in alerts:
                if self.performance_alert:
                    self.performance_alert.emit("Performance Warning", alert)
                logger.warning(f"Performance alert: {alert}")

        except Exception as e:
            logger.error(f"Error checking performance alerts: {e}")

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self.metrics_collector.metrics.collect_metrics()

    def set_alert_thresholds(
        self, cpu: float = None, memory: float = None, disk: float = None
    ):
        """Set custom alert thresholds."""
        if cpu is not None:
            self.alert_thresholds["cpu"] = cpu
        if memory is not None:
            self.alert_thresholds["memory"] = memory
        if disk is not None:
            self.alert_thresholds["disk"] = disk

        logger.info(f"Alert thresholds updated: {self.alert_thresholds}")

    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            if hasattr(self, "metrics_collector") and self.metrics_collector:
                if (
                    hasattr(self.metrics_collector, "running")
                    and self.metrics_collector.running
                ):
                    self.metrics_collector.stop_collection()
        except Exception:
            pass  # Ignore cleanup errors

    def closeEvent(self, event):
        """Handle close event properly."""
        if PYSIDE6_AVAILABLE:
            try:
                self.stop_monitoring()
            except Exception:
                pass
            super().closeEvent(event)

        logger.info("Performance Monitor initialized successfully")


# Example usage
if __name__ == "__main__":
    if PYSIDE6_AVAILABLE:
        from PySide6.QtWidgets import QApplication

        app = QApplication(sys.argv)

        monitor = PerformanceMonitor()
        monitor.show()
        monitor.resize(1000, 700)

        sys.exit(app.exec())
    else:
        print("PySide6 is required to run the Performance Monitor")
