# type: ignore
"""
🚀⚡ LYRIXA PERFORMANCE MONITOR
=============================

Advanced performance monitoring system for Lyrixa providing:
- Real-time system metrics (CPU, memory, disk, network)
- Process-specific monitoring for Lyrixa components
- Interactive charts and visualizations
- Health indicators and alerts
- Performance history and trends

This module provides both GUI and headless monitoring capabilities.
"""

import logging
import platform
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List

import psutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check Qt availability first
QT_AVAILABLE = False
MATPLOTLIB_AVAILABLE = False

try:
    from PySide6.QtCore import Qt, QThread, QTimer, Signal
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import (
        QApplication,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QProgressBar,
        QPushButton,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    QT_AVAILABLE = True
except ImportError:
    logger.warning("PySide6 not available. Using mock classes.")

try:
    import matplotlib.dates as mdates  # type: ignore
    import matplotlib.pyplot as plt  # type: ignore
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvasQTAgg as FigureCanvas,  # type: ignore
    )
    from matplotlib.figure import Figure  # type: ignore

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    logger.warning("Matplotlib not available. Chart functionality will be limited.")

# Mock classes for missing dependencies
if not QT_AVAILABLE:

    class MockWidget:
        def __init__(self, *args, **kwargs):
            pass

        def __getattr__(self, name):
            return self

        def __call__(self, *args, **kwargs):
            return self

        def setLayout(self, layout):
            pass

        def setWindowTitle(self, title):
            pass

        def setMinimumSize(self, width, height):
            pass

        def show(self):
            pass

        def hide(self):
            pass

        def update(self):
            pass

        def setStyleSheet(self, style):
            pass

        def addTab(self, widget, title):
            pass

        def setFont(self, font):
            pass

        def setAlignment(self, alignment):
            pass

        def setText(self, text):
            pass

        def text(self):
            return ""

        def clicked(self):
            return self

        def connect(self, func):
            pass

        def timeout(self):
            return self

        def start(self, interval):
            pass

        def stop(self):
            pass

        def setValue(self, value):
            pass

        def setRange(self, min_val, max_val):
            pass

        def setRowCount(self, count):
            pass

        def setColumnCount(self, count):
            pass

        def setHorizontalHeaderLabels(self, labels):
            pass

        def horizontalHeader(self):
            return self

        def setStretchLastSection(self, stretch):
            pass

        def setAlternatingRowColors(self, alternate):
            pass

        def setMaximumHeight(self, height):
            pass

        def setItem(self, row, col, item):
            pass

        def insertRow(self, row):
            pass

        def setData(self, role, value):
            pass

        def setBackground(self, color):
            pass

        def setForeground(self, color):
            pass

        def setTextAlignment(self, alignment):
            pass

        def addWidget(self, widget):
            pass

        def addStretch(self):
            pass

        def resizeColumnsToContents(self):
            pass

        def setReadOnly(self, readonly):
            pass

        def setPlainText(self, text):
            pass

        def exec(self):
            pass

    class MockSignal:
        def __init__(self, *args, **kwargs):
            pass

        def connect(self, func):
            pass

        def disconnect(self, func=None):
            pass

        def emit(self, *args, **kwargs):
            pass

    class MockThread:
        def __init__(self, *args, **kwargs):
            pass

        def start(self):
            pass

        def stop(self):
            pass

        def wait(self):
            pass

        def isRunning(self):
            return False

    class MockLayout:
        def __init__(self, *args, **kwargs):
            pass

        def addWidget(self, widget, *args, **kwargs):
            pass

        def addLayout(self, layout, *args, **kwargs):
            pass

        def addStretch(self, stretch=0):
            pass

        def setSpacing(self, spacing):
            pass

        def setContentsMargins(self, left, top, right, bottom):
            pass

    class MockFont:
        def __init__(self, *args, **kwargs):
            pass

        def setPointSize(self, size):
            pass

        def setBold(self, bold):
            pass

        Bold = 75

    class MockQt:
        AlignCenter = 0x84
        AlignLeft = 0x01
        AlignRight = 0x02

    # Assign mock classes
    QWidget = MockWidget
    QLabel = MockWidget
    QTextEdit = MockWidget
    QProgressBar = MockWidget
    QPushButton = MockWidget
    QTableWidget = MockWidget
    QTableWidgetItem = MockWidget
    QTabWidget = MockWidget
    QGroupBox = MockWidget
    QApplication = MockWidget
    QVBoxLayout = MockLayout
    QHBoxLayout = MockLayout
    Signal = MockSignal
    QThread = MockThread
    QTimer = MockWidget
    QFont = MockFont
    Qt = MockQt

if not MATPLOTLIB_AVAILABLE:

    class MockFigure:
        def __init__(self, *args, **kwargs):
            pass

        def add_subplot(self, *args, **kwargs):
            return MockAxes()

        def tight_layout(self):
            pass

        def clear(self):
            pass

    class MockAxes:
        def __init__(self):
            self.xaxis = MockAxis()

        def plot(self, *args, **kwargs):
            pass

        def set_title(self, title):
            pass

        def set_xlabel(self, label):
            pass

        def set_ylabel(self, label):
            pass

        def legend(self, *args, **kwargs):
            pass

        def grid(self, *args, **kwargs):
            pass

        def clear(self):
            pass

        def get_majorticklabels(self):
            return []

    class MockAxis:
        def set_major_formatter(self, formatter):
            pass

        def get_majorticklabels(self):
            return []

    class MockCanvas:
        def __init__(self, figure):
            self.figure = figure

        def draw(self):
            pass

    class MockDateFormatter:
        def __init__(self, format_str):
            pass

    class MockMdates:
        def DateFormatter(self, format_str):
            return MockDateFormatter(format_str)

    class MockPlt:
        @staticmethod
        def setp(*args, **kwargs):
            pass

    # Assign mock classes
    Figure = MockFigure
    FigureCanvas = MockCanvas
    mdates = MockMdates()
    plt = MockPlt()


class SystemMetrics:
    """System metrics collector and analyzer."""

    def __init__(self):
        self.history = []
        self.max_history = 1000
        self.process = None
        self._initialize_process()

    def _initialize_process(self):
        """Initialize process monitoring."""
        try:
            self.process = psutil.Process()
        except Exception as e:
            logger.error(f"Failed to initialize process monitoring: {e}")

    def collect_metrics(self) -> Dict:
        """Collect current system metrics."""
        metrics = {
            "timestamp": datetime.now(),
            "cpu_percent": 0,
            "memory_percent": 0,
            "memory_used_mb": 0,
            "memory_available_mb": 0,
            "disk_usage_percent": 0,
            "disk_free_gb": 0,
            "network_sent_mb": 0,
            "network_recv_mb": 0,
            "process_cpu_percent": 0,
            "process_memory_mb": 0,
            "process_threads": 0,
            "platform": platform.system(),
            "python_version": platform.python_version(),
        }

        try:
            # CPU metrics
            metrics["cpu_percent"] = psutil.cpu_percent(interval=0.1)

            # Memory metrics
            memory = psutil.virtual_memory()
            metrics["memory_percent"] = memory.percent
            metrics["memory_used_mb"] = memory.used / (1024 * 1024)
            metrics["memory_available_mb"] = memory.available / (1024 * 1024)

            # Disk metrics
            disk = psutil.disk_usage("/")
            metrics["disk_usage_percent"] = disk.percent
            metrics["disk_free_gb"] = disk.free / (1024 * 1024 * 1024)

            # Network metrics
            network = psutil.net_io_counters()
            metrics["network_sent_mb"] = network.bytes_sent / (1024 * 1024)
            metrics["network_recv_mb"] = network.bytes_recv / (1024 * 1024)

            # Process-specific metrics
            if self.process:
                try:
                    metrics["process_cpu_percent"] = self.process.cpu_percent()
                    metrics["process_memory_mb"] = self.process.memory_info().rss / (
                        1024 * 1024
                    )
                    metrics["process_threads"] = self.process.num_threads()

                    # Add file descriptors count if available (Unix-like systems)
                    try:
                        if hasattr(self.process, "num_fds"):
                            metrics["num_fds"] = self.process.num_fds()  # type: ignore
                    except (AttributeError, psutil.AccessDenied):
                        pass

                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    logger.warning(f"Process monitoring error: {e}")

        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")

        # Add to history
        self.history.append(metrics)
        if len(self.history) > self.max_history:
            self.history.pop(0)

        return metrics

    def get_history(self, minutes: int = 10) -> List[Dict]:
        """Get metrics history for the specified number of minutes."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [m for m in self.history if m["timestamp"] >= cutoff_time]

    def get_average_metrics(self, minutes: int = 5) -> Dict:
        """Get average metrics over the specified time period."""
        recent_metrics = self.get_history(minutes)
        if not recent_metrics:
            return {}

        avg_metrics = {}
        numeric_keys = [
            "cpu_percent",
            "memory_percent",
            "process_cpu_percent",
            "process_memory_mb",
        ]

        for key in numeric_keys:
            values = [
                m.get(key, 0)
                for m in recent_metrics
                if isinstance(m.get(key), (int, float))
            ]
            avg_metrics[f"avg_{key}"] = sum(values) / len(values) if values else 0

        return avg_metrics


class MetricsCollectorThread(threading.Thread):  # type: ignore
    """Background thread for collecting metrics."""

    def __init__(self, metrics_collector: SystemMetrics):
        super().__init__()
        self.metrics_collector = metrics_collector
        self.running = False
        self.update_interval = 2.0  # seconds
        self.daemon = True

        # Qt signals (only available if Qt is available)
        if QT_AVAILABLE:
            self.metrics_updated = Signal(dict)  # type: ignore

    def start_collection(self):
        """Start metrics collection."""
        self.running = True
        self.start()

    def stop_collection(self):
        """Stop metrics collection."""
        self.running = False
        if hasattr(self, "wait"):
            self.wait()  # type: ignore

    def run(self):
        """Main collection loop."""
        while self.running:
            try:
                metrics = self.metrics_collector.collect_metrics()

                # Emit signal if Qt is available
                if QT_AVAILABLE and hasattr(self, "metrics_updated"):
                    self.metrics_updated.emit(metrics)  # type: ignore
                else:
                    # For non-Qt mode, just log the metrics
                    logger.info(
                        f"Metrics: CPU {metrics['cpu_percent']:.1f}%, "
                        f"Memory {metrics['memory_percent']:.1f}%"
                    )

                time.sleep(self.update_interval)

            except Exception as e:
                logger.error(f"Error in metrics collection thread: {e}")
                time.sleep(self.update_interval)


class MetricsChart(QWidget):  # type: ignore
    """Widget for displaying performance charts."""

    def __init__(self, chart_type="cpu", parent=None):
        super().__init__(parent)
        self.chart_type = chart_type
        self.metrics_history = []
        self.setup_ui()

    def setup_ui(self):
        """Set up the chart widget UI."""
        layout = QVBoxLayout()  # type: ignore

        if MATPLOTLIB_AVAILABLE and QT_AVAILABLE:
            try:
                self.figure = Figure(figsize=(6, 3), dpi=80)  # type: ignore
                self.canvas = FigureCanvas(self.figure)  # type: ignore
                layout.addWidget(self.canvas)  # type: ignore
            except Exception as e:
                logger.error(f"Error setting up matplotlib chart: {e}")
                placeholder = QLabel("Chart display error")  # type: ignore
                placeholder.setAlignment(Qt.AlignCenter)  # type: ignore
                placeholder.setStyleSheet("border: 1px solid #ccc; margin: 10px;")  # type: ignore
                layout.addWidget(placeholder)  # type: ignore
        else:
            placeholder = QLabel(
                f"{self.chart_type.upper()} Chart\n(Matplotlib not available)"
            )  # type: ignore
            placeholder.setAlignment(Qt.AlignCenter)  # type: ignore
            placeholder.setStyleSheet("border: 1px solid #ccc; margin: 10px;")  # type: ignore
            layout.addWidget(placeholder)  # type: ignore

        self.setLayout(layout)  # type: ignore

    def update_chart(self, metrics_history: List[Dict]):
        """Update the chart with new metrics data."""
        self.metrics_history = metrics_history

        if not (MATPLOTLIB_AVAILABLE and QT_AVAILABLE):
            return

        try:
            self.figure.clear()  # type: ignore
            ax = self.figure.add_subplot(111)  # type: ignore

            if self.metrics_history:
                timestamps = [m["timestamp"] for m in self.metrics_history]

                if self.chart_type == "cpu":
                    values = [m.get("cpu_percent", 0) for m in self.metrics_history]
                    ax.plot(timestamps, values, label="CPU %", color="blue")
                    ax.set_ylabel("CPU Usage (%)")
                elif self.chart_type == "memory":
                    values = [m.get("memory_percent", 0) for m in self.metrics_history]
                    ax.plot(timestamps, values, label="Memory %", color="green")
                    ax.set_ylabel("Memory Usage (%)")
                elif self.chart_type == "process":
                    cpu_values = [
                        m.get("process_cpu_percent", 0) for m in self.metrics_history
                    ]
                    ax.plot(timestamps, cpu_values, label="Process CPU %", color="red")
                    ax.set_ylabel("Process CPU (%)")

                ax.set_title(f"{self.chart_type.title()} Performance")
                ax.grid(True, alpha=0.3)
                ax.legend()

                # Format x-axis
                if timestamps:
                    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))  # type: ignore
                    # Rotate labels for better readability
                    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")  # type: ignore

            self.canvas.draw()  # type: ignore

        except Exception as e:
            logger.error(f"Error updating chart: {e}")


class HealthIndicator(QWidget):  # type: ignore
    """Widget showing system health status."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the health indicator UI."""
        layout = QVBoxLayout()  # type: ignore

        self.status_label = QLabel("🟢")  # type: ignore
        self.status_label.setFont(QFont("Arial", 20))  # type: ignore
        layout.addWidget(self.status_label)  # type: ignore

        self.text_label = QLabel("System Healthy")  # type: ignore
        self.text_label.setFont(QFont("Arial", 12, QFont.Bold))  # type: ignore
        layout.addWidget(self.text_label)  # type: ignore

        layout.addStretch()  # type: ignore
        self.setLayout(layout)  # type: ignore

    def update_health(self, metrics: Dict):
        """Update health status based on metrics."""
        try:
            cpu_percent = metrics.get("cpu_percent", 0)
            memory_percent = metrics.get("memory_percent", 0)

            # Determine health status
            if cpu_percent > 90 or memory_percent > 95:
                status = "🔴"
                text = "Critical"
                color = "#e74c3c"
            elif cpu_percent > 70 or memory_percent > 85:
                status = "🟡"
                text = "Warning"
                color = "#f39c12"
            else:
                status = "🟢"
                text = "Healthy"
                color = "#27ae60"

            self.status_label.setText(status)  # type: ignore
            self.status_label.setStyleSheet(f"color: {color};")  # type: ignore
            self.text_label.setText(text)  # type: ignore
            self.text_label.setStyleSheet(f"color: {color};")  # type: ignore

        except Exception as e:
            logger.error(f"Error updating health indicator: {e}")


class MetricsTable(QWidget):  # type: ignore
    """Widget for displaying metrics in table format."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the metrics table UI."""
        layout = QVBoxLayout()  # type: ignore

        header_label = QLabel("System Metrics")  # type: ignore
        header_label.setFont(QFont("Arial", 12, QFont.Bold))  # type: ignore
        layout.addWidget(header_label)  # type: ignore

        self.table = QTableWidget()  # type: ignore
        self.table.setColumnCount(2)  # type: ignore
        self.table.setHorizontalHeaderLabels(["Metric", "Value"])  # type: ignore
        self.table.horizontalHeader().setStretchLastSection(True)  # type: ignore
        self.table.setAlternatingRowColors(True)  # type: ignore
        self.table.setMaximumHeight(300)  # type: ignore

        layout.addWidget(self.table)  # type: ignore
        self.setLayout(layout)  # type: ignore

    def update_metrics(self, metrics: Dict):
        """Update the metrics table."""
        try:
            # Filter metrics for display
            display_metrics = {
                "CPU Usage": f"{metrics.get('cpu_percent', 0):.1f}%",
                "Memory Usage": f"{metrics.get('memory_percent', 0):.1f}%",
                "Memory Used": f"{metrics.get('memory_used_mb', 0):.1f} MB",
                "Disk Usage": f"{metrics.get('disk_usage_percent', 0):.1f}%",
                "Process CPU": f"{metrics.get('process_cpu_percent', 0):.1f}%",
                "Process Memory": f"{metrics.get('process_memory_mb', 0):.1f} MB",
                "Process Threads": str(metrics.get("process_threads", 0)),
                "Platform": metrics.get("platform", "Unknown"),
                "Python Version": metrics.get("python_version", "Unknown"),
            }

            self.table.setRowCount(len(display_metrics))  # type: ignore

            for row, (metric, value) in enumerate(display_metrics.items()):
                # Metric name
                metric_item = QTableWidgetItem(metric)  # type: ignore
                self.table.setItem(row, 0, metric_item)  # type: ignore

                # Metric value
                value_item = QTableWidgetItem(value)  # type: ignore
                self.table.setItem(row, 1, value_item)  # type: ignore

                # Color coding for critical values
                if "CPU" in metric and "%" in value:
                    try:
                        percent = float(value.replace("%", ""))
                        if percent > 80:
                            # Would need QColor for proper color coding
                            pass
                    except ValueError:
                        pass

            self.table.resizeColumnsToContents()  # type: ignore

        except Exception as e:
            logger.error(f"Error updating metrics table: {e}")


class PerformanceMonitor(QWidget):  # type: ignore
    """
    Main performance monitoring widget.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.metrics_collector = SystemMetrics()
        self.collector_thread = None
        self.setup_ui()
        self.start_monitoring()

    def setup_ui(self):
        """Set up the main UI."""
        layout = QVBoxLayout()  # type: ignore

        # Title
        title = QLabel("🚀 Lyrixa Performance Monitor")  # type: ignore
        title.setFont(QFont("Arial", 16, QFont.Bold))  # type: ignore
        title.setAlignment(Qt.AlignCenter)  # type: ignore
        layout.addWidget(title)  # type: ignore

        # Create tab widget
        self.tab_widget = QTabWidget()  # type: ignore

        # Overview tab
        self.overview_tab = self.create_overview_tab()
        self.tab_widget.addTab(self.overview_tab, "📊 Overview")  # type: ignore

        # Charts tab
        self.charts_tab = self.create_charts_tab()
        self.tab_widget.addTab(self.charts_tab, "📈 Charts")  # type: ignore

        # Details tab
        self.details_tab = self.create_details_tab()
        self.tab_widget.addTab(self.details_tab, "📋 Details")  # type: ignore

        layout.addWidget(self.tab_widget)  # type: ignore

        # Control buttons
        control_layout = QHBoxLayout()  # type: ignore

        self.start_button = QPushButton("Start Monitoring")  # type: ignore
        self.start_button.clicked.connect(self.start_monitoring)  # type: ignore
        control_layout.addWidget(self.start_button)  # type: ignore

        self.stop_button = QPushButton("Stop Monitoring")  # type: ignore
        self.stop_button.clicked.connect(self.stop_monitoring)  # type: ignore
        control_layout.addWidget(self.stop_button)  # type: ignore

        self.refresh_button = QPushButton("Refresh")  # type: ignore
        self.refresh_button.clicked.connect(self.manual_refresh)  # type: ignore
        control_layout.addWidget(self.refresh_button)  # type: ignore

        layout.addLayout(control_layout)  # type: ignore

        self.setLayout(layout)  # type: ignore

    def create_overview_tab(self):  # type: ignore
        """Create the overview tab."""
        widget = QWidget()  # type: ignore
        layout = QHBoxLayout()  # type: ignore

        # Health indicator
        health_group = QGroupBox("System Health")  # type: ignore
        health_layout = QVBoxLayout()  # type: ignore
        self.health_indicator = HealthIndicator()
        health_layout.addWidget(self.health_indicator)  # type: ignore
        health_group.setLayout(health_layout)  # type: ignore
        layout.addWidget(health_group)  # type: ignore

        # Quick metrics
        metrics_group = QGroupBox("Key Metrics")  # type: ignore
        metrics_layout = QVBoxLayout()  # type: ignore
        self.metrics_table = MetricsTable()
        metrics_layout.addWidget(self.metrics_table)  # type: ignore
        metrics_group.setLayout(metrics_layout)  # type: ignore
        layout.addWidget(metrics_group)  # type: ignore

        widget.setLayout(layout)  # type: ignore
        return widget

    def create_charts_tab(self):  # type: ignore
        """Create the charts tab."""
        widget = QWidget()  # type: ignore
        layout = QVBoxLayout()  # type: ignore

        # Chart controls
        controls_layout = QHBoxLayout()  # type: ignore
        controls_layout.addWidget(QLabel("Performance Charts"))  # type: ignore
        layout.addLayout(controls_layout)  # type: ignore

        # Charts
        charts_layout = QHBoxLayout()  # type: ignore

        self.cpu_chart = MetricsChart("cpu")
        charts_layout.addWidget(self.cpu_chart)  # type: ignore

        self.memory_chart = MetricsChart("memory")
        charts_layout.addWidget(self.memory_chart)  # type: ignore

        layout.addLayout(charts_layout)  # type: ignore

        self.process_chart = MetricsChart("process")
        layout.addWidget(self.process_chart)  # type: ignore

        widget.setLayout(layout)  # type: ignore
        return widget

    def create_details_tab(self):  # type: ignore
        """Create the details tab."""
        widget = QWidget()  # type: ignore
        layout = QVBoxLayout()  # type: ignore

        # System info
        info_text = QTextEdit()  # type: ignore
        info_text.setReadOnly(True)  # type: ignore
        info_text.setMaximumHeight(200)  # type: ignore

        system_info = f"""System Information:
Platform: {platform.system()} {platform.release()}
Architecture: {platform.architecture()[0]}
Processor: {platform.processor()}
Python Version: {platform.python_version()}
CPU Count: {psutil.cpu_count()}
Boot Time: {datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")}
"""
        info_text.setPlainText(system_info)  # type: ignore
        layout.addWidget(info_text)  # type: ignore

        # Detailed metrics table
        self.detailed_table = MetricsTable()
        layout.addWidget(self.detailed_table)  # type: ignore

        widget.setLayout(layout)  # type: ignore
        return widget

    def start_monitoring(self):
        """Start performance monitoring."""
        try:
            if (
                self.collector_thread
                and hasattr(self.collector_thread, "running")
                and self.collector_thread.running
            ):
                return

            self.collector_thread = MetricsCollectorThread(self.metrics_collector)

            if QT_AVAILABLE and hasattr(self.collector_thread, "metrics_updated"):
                self.collector_thread.metrics_updated.connect(self.update_displays)  # type: ignore

            self.collector_thread.start_collection()

            self.start_button.setText("Monitoring...")  # type: ignore
            logger.info("Performance monitoring started")

        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")

    def stop_monitoring(self):
        """Stop performance monitoring."""
        try:
            if self.collector_thread:
                self.collector_thread.stop_collection()
                self.collector_thread = None

            self.start_button.setText("Start Monitoring")  # type: ignore
            logger.info("Performance monitoring stopped")

        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")

    def manual_refresh(self):
        """Manually refresh metrics."""
        try:
            metrics = self.metrics_collector.collect_metrics()
            self.update_displays(metrics)
        except Exception as e:
            logger.error(f"Error refreshing metrics: {e}")

    def update_displays(self, metrics: Dict):
        """Update all display widgets with new metrics."""
        try:
            # Update health indicator
            self.health_indicator.update_health(metrics)

            # Update metrics tables
            self.metrics_table.update_metrics(metrics)
            self.detailed_table.update_metrics(metrics)

            # Update charts with history
            history = self.metrics_collector.get_history(10)  # Last 10 minutes
            if hasattr(self, "cpu_chart"):
                self.cpu_chart.update_chart(history)
            if hasattr(self, "memory_chart"):
                self.memory_chart.update_chart(history)
            if hasattr(self, "process_chart"):
                self.process_chart.update_chart(history)

        except Exception as e:
            logger.error(f"Error updating displays: {e}")

    def closeEvent(self, event):  # type: ignore
        """Handle widget close event."""
        self.stop_monitoring()
        event.accept()  # type: ignore


def main():
    """Main function for testing the performance monitor."""
    if not QT_AVAILABLE:
        print("Qt not available. Running in headless mode.")
        monitor = PerformanceMonitor()
        print("Performance monitor created successfully in headless mode.")

        # Run a simple monitoring loop for demonstration
        try:
            for i in range(5):
                metrics = monitor.metrics_collector.collect_metrics()
                print(
                    f"Sample {i + 1}: CPU {metrics['cpu_percent']:.1f}%, Memory {metrics['memory_percent']:.1f}%"
                )
                time.sleep(2)
        except KeyboardInterrupt:
            print("\nStopping headless monitoring...")

        return monitor

    app = QApplication([])  # type: ignore
    monitor = PerformanceMonitor()
    monitor.setWindowTitle("Lyrixa Performance Monitor")  # type: ignore
    monitor.setMinimumSize(1000, 600)  # type: ignore
    monitor.show()  # type: ignore

    try:
        app.exec()  # type: ignore
    except KeyboardInterrupt:
        print("\nShutting down performance monitor...")
    finally:
        monitor.stop_monitoring()

    return monitor


if __name__ == "__main__":
    main()
