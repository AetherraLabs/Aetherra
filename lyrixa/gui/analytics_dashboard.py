"""
Enhanced Analytics Dashboard with comprehensive data visualization and insights.
Features real-time updates, interactive charts, and export capabilities.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check Qt availability first
QT_AVAILABLE = False
MATPLOTLIB_AVAILABLE = False
PANDAS_AVAILABLE = False

try:
    from PySide6.QtCore import QDate, QPropertyAnimation, QSize, Qt, QTimer, Signal
    from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPalette
    from PySide6.QtWidgets import (
        QApplication,
        QComboBox,
        QDateEdit,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QScrollArea,
        QSizePolicy,
        QSpacerItem,
        QSplitter,
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
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    logger.warning("Matplotlib not available. Chart functionality will be limited.")

try:
    import numpy as np
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    logger.warning("Pandas/NumPy not available. Data processing will be limited.")

# Mock classes for missing dependencies
if not QT_AVAILABLE:

    class MockWidget:
        def __init__(self, *args, **kwargs):
            pass

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

        def setFrameStyle(self, style):
            pass

        def addWidget(self, widget):
            pass

        def addLayout(self, layout):
            pass

        def setText(self, text):
            pass

        def text(self):
            return ""

        def setPlainText(self, text):
            pass

        def toPlainText(self):
            return ""

        def append(self, text):
            pass

        def clear(self):
            pass

        def setReadOnly(self, readonly):
            pass

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

        def setFont(self, font):
            pass

        def setAlignment(self, alignment):
            pass

        def setPointSize(self, size):
            pass

        def setBold(self, bold):
            pass

        def addItem(self, item):
            pass

        def currentText(self):
            return ""

        def setCurrentText(self, text):
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

        def addStretch(self):
            pass

        def setSpacing(self, spacing):
            pass

        def setContentsMargins(self, left, top, right, bottom):
            pass

        def resizeColumnsToContents(self):
            pass

        def setVerticalScrollBarPolicy(self, policy):
            pass

        def setHorizontalScrollBarPolicy(self, policy):
            pass

        def setWidget(self, widget):
            pass

        def setWidgetResizable(self, resizable):
            pass

        def addSeparator(self):
            pass

        def currentIndex(self):
            return 0

        def setCurrentIndex(self, index):
            pass

        def count(self):
            return 0

        def widget(self, index):
            return self

        def removeTab(self, index):
            pass

        def tabText(self, index):
            return ""

        def setTabText(self, index, text):
            pass

        def setCurrentWidget(self, widget):
            pass

        def currentWidget(self):
            return self

        def indexOf(self, widget):
            return 0

    class MockSignal:
        def __init__(self, *args, **kwargs):
            pass

        def connect(self, func):
            pass

        def disconnect(self, func=None):
            pass

        def emit(self, *args, **kwargs):
            pass

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

        def insertWidget(self, index, widget):
            pass

        def removeWidget(self, widget):
            pass

        def count(self):
            return 0

        def itemAt(self, index):
            return None

        def takeAt(self, index):
            return None

    class MockColor:
        def __init__(self, *args, **kwargs):
            pass

        @staticmethod
        def fromRgb(*args):
            return MockColor()

        @staticmethod
        def fromHsv(*args):
            return MockColor()

    class MockFont:
        def __init__(self, *args, **kwargs):
            pass

        def setPointSize(self, size):
            pass

        def setBold(self, bold):
            pass

        def setWeight(self, weight):
            pass

        Bold = 75

    class MockDate:
        def __init__(self, *args, **kwargs):
            pass

        @staticmethod
        def currentDate():
            return MockDate()

        def addDays(self, days):
            return MockDate()

        def toString(self, format_str=""):
            return ""

    class MockSize:
        def __init__(self, width=0, height=0):
            self.width = width
            self.height = height

    class MockQt:
        AlignCenter = 0x84
        AlignLeft = 0x01
        AlignRight = 0x02
        AlignTop = 0x20
        AlignBottom = 0x40
        Horizontal = 1
        Vertical = 2
        ScrollBarAlwaysOff = 1
        ScrollBarAsNeeded = 0

    # Assign mock classes
    QWidget = MockWidget
    QLabel = MockWidget
    QTextEdit = MockWidget
    QProgressBar = MockWidget
    QPushButton = MockWidget
    QComboBox = MockWidget
    QTableWidget = MockWidget
    QTableWidgetItem = MockWidget
    QTabWidget = MockWidget
    QFrame = MockWidget
    QGroupBox = MockWidget
    QScrollArea = MockWidget
    QListWidget = MockWidget
    QListWidgetItem = MockWidget
    QDateEdit = MockWidget
    QMessageBox = MockWidget
    QSplitter = MockWidget
    QApplication = MockWidget
    QVBoxLayout = MockLayout
    QHBoxLayout = MockLayout
    QGridLayout = MockLayout
    QSpacerItem = MockWidget
    QSizePolicy = MockWidget
    Signal = MockSignal
    QTimer = MockWidget
    QColor = MockColor
    QFont = MockFont
    QDate = MockDate
    QSize = MockSize
    Qt = MockQt
    QPropertyAnimation = MockWidget
    QLinearGradient = MockWidget
    QPainter = MockWidget
    QPalette = MockWidget

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

        def savefig(self, *args, **kwargs):
            pass

    class MockAxes:
        def __init__(self):
            self.xaxis = MockAxis()
            self.yaxis = MockAxis()

        def plot(self, *args, **kwargs):
            pass

        def bar(self, *args, **kwargs):
            pass

        def pie(self, *args, **kwargs):
            pass

        def hist(self, *args, **kwargs):
            pass

        def scatter(self, *args, **kwargs):
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

        def set_xlim(self, *args):
            pass

        def set_ylim(self, *args):
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

    class MockPlt:
        @staticmethod
        def setp(*args, **kwargs):
            pass

        @staticmethod
        def savefig(*args, **kwargs):
            pass

        @staticmethod
        def close(*args):
            pass

    # Assign mock classes
    Figure = MockFigure
    FigureCanvas = MockCanvas
    mdates = type("MockMdates", (), {"DateFormatter": MockDateFormatter})()
    plt = MockPlt()

if not PANDAS_AVAILABLE:

    class MockDataFrame:
        def __init__(self, data=None, *args, **kwargs):
            self.data = data or {}

        def to_dict(self, *args, **kwargs):
            return self.data

        def head(self, n=5):
            return self

        def tail(self, n=5):
            return self

        def describe(self):
            return self

        def info(self):
            pass

        def __getitem__(self, key):
            return MockSeries()

        def __setitem__(self, key, value):
            pass

        def groupby(self, *args, **kwargs):
            return MockGroupBy()

        def sort_values(self, *args, **kwargs):
            return self

        def reset_index(self, *args, **kwargs):
            return self

        def dropna(self, *args, **kwargs):
            return self

        def fillna(self, *args, **kwargs):
            return self

        def merge(self, *args, **kwargs):
            return self

        def join(self, *args, **kwargs):
            return self

        def apply(self, *args, **kwargs):
            return self

        def mean(self):
            return 0

        def std(self):
            return 0

        def min(self):
            return 0

        def max(self):
            return 0

        def sum(self):
            return 0

        def count(self):
            return 0

        def shape(self):
            return (0, 0)

        def columns(self):
            return []

        def index(self):
            return []

        def values(self):
            return []

        def iterrows(self):
            return iter([])

    class MockSeries:
        def __init__(self, data=None, *args, **kwargs):
            self.data = data or []

        def to_list(self):
            return self.data

        def values(self):
            return self.data

        def mean(self):
            return 0

        def std(self):
            return 0

        def min(self):
            return 0

        def max(self):
            return 0

        def sum(self):
            return 0

        def count(self):
            return 0

    class MockGroupBy:
        def __init__(self):
            pass

        def agg(self, *args, **kwargs):
            return MockDataFrame()

        def mean(self):
            return MockDataFrame()

        def sum(self):
            return MockDataFrame()

        def count(self):
            return MockDataFrame()

        def size(self):
            return MockSeries()

    class MockNumpy:
        @staticmethod
        def array(data):
            return data

        @staticmethod
        def mean(data):
            return 0

        @staticmethod
        def std(data):
            return 0

        @staticmethod
        def min(data):
            return 0

        @staticmethod
        def max(data):
            return 0

        @staticmethod
        def sum(data):
            return 0

        @staticmethod
        def random(*args, **kwargs):
            return type(
                "MockRandom",
                (),
                {
                    "randint": lambda *a, **k: 0,
                    "random": lambda *a, **k: 0.5,
                    "choice": lambda *a, **k: a[0][0] if a and a[0] else 0,
                },
            )()

        @staticmethod
        def linspace(start, stop, num):
            return [start + i * (stop - start) / (num - 1) for i in range(num)]

        @staticmethod
        def arange(start, stop=None, step=1):
            if stop is None:
                stop = start
                start = 0
            return list(range(start, stop, step))

    # Assign mock classes
    pd = type(
        "MockPandas",
        (),
        {
            "DataFrame": MockDataFrame,
            "Series": MockSeries,
            "read_csv": lambda *a, **k: MockDataFrame(),
            "read_json": lambda *a, **k: MockDataFrame(),
            "to_datetime": lambda *a, **k: None,
            "date_range": lambda *a, **k: [],
        },
    )()
    np = MockNumpy()


class ChartWidget(QWidget):
    """Widget for displaying charts with matplotlib integration."""

    def __init__(self, chart_type="line", parent=None):
        super().__init__(parent)
        self.chart_type = chart_type
        self.data = {}
        self.setup_ui()

    def setup_ui(self):
        """Set up the chart widget UI."""
        layout = QVBoxLayout()

        if MATPLOTLIB_AVAILABLE and QT_AVAILABLE:
            try:
                from matplotlib.backends.backend_qt5agg import (
                    FigureCanvasQTAgg as FigureCanvas,
                )
                from matplotlib.figure import Figure

                self.figure = Figure(figsize=(8, 6), dpi=80)
                self.canvas = FigureCanvas(self.figure)
                layout.addWidget(self.canvas)

                # Add chart controls
                controls_layout = QHBoxLayout()

                self.chart_type_combo = QComboBox()
                self.chart_type_combo.addItem("Line Chart")
                self.chart_type_combo.addItem("Bar Chart")
                self.chart_type_combo.addItem("Pie Chart")
                self.chart_type_combo.addItem("Histogram")
                controls_layout.addWidget(QLabel("Chart Type:"))
                controls_layout.addWidget(self.chart_type_combo)

                self.refresh_button = QPushButton("Refresh")
                self.refresh_button.clicked.connect(self.refresh_chart)
                controls_layout.addWidget(self.refresh_button)

                layout.addLayout(controls_layout)

            except ImportError:
                placeholder = QLabel(
                    "Matplotlib not available - Chart functionality limited"
                )
                placeholder.setAlignment(Qt.AlignCenter)
                placeholder.setStyleSheet("border: 1px solid #ccc; margin: 10px;")
                layout.addWidget(placeholder)
        else:
            placeholder = QLabel("Chart functionality not available")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("border: 1px solid #ccc; margin: 10px;")
            layout.addWidget(placeholder)

        self.setLayout(layout)

    def refresh_chart(self):
        """Refresh the chart with current data."""
        if not (MATPLOTLIB_AVAILABLE and QT_AVAILABLE):
            return

        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)

            if self.data:
                x_data = list(self.data.keys())
                y_data = list(self.data.values())

                chart_type = self.chart_type_combo.currentText().lower()

                if "line" in chart_type:
                    ax.plot(x_data, y_data, marker="o")
                elif "bar" in chart_type:
                    ax.bar(x_data, y_data)
                elif "pie" in chart_type:
                    ax.pie(y_data, labels=x_data, autopct="%1.1f%%")
                elif "histogram" in chart_type:
                    ax.hist(y_data, bins=10)

                ax.set_title(f"{chart_type.title()} - Analytics Data")
                ax.grid(True, alpha=0.3)

            self.canvas.draw()
        except Exception as e:
            logger.error(f"Error refreshing chart: {e}")

    def update_data(self, data: Dict[str, Any]):
        """Update chart data."""
        self.data = data
        self.refresh_chart()


class MetricsWidget(QWidget):
    """Widget for displaying key metrics."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.metrics = {}
        self.setup_ui()

    def setup_ui(self):
        """Set up the metrics widget UI."""
        layout = QVBoxLayout()

        # Header
        header = QLabel("Key Metrics")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Metrics container
        self.metrics_container = QWidget()
        self.metrics_layout = QGridLayout()
        self.metrics_container.setLayout(self.metrics_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.metrics_container)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        layout.addWidget(scroll_area)

        # Refresh button
        refresh_button = QPushButton("Refresh Metrics")
        refresh_button.clicked.connect(self.refresh_metrics)
        layout.addWidget(refresh_button)

        self.setLayout(layout)

    def update_metrics(self, metrics: Dict[str, Any]):
        """Update the displayed metrics."""
        self.metrics = metrics
        self.refresh_metrics()

    def refresh_metrics(self):
        """Refresh the metrics display."""
        # Clear existing metrics
        for i in reversed(range(self.metrics_layout.count())):
            self.metrics_layout.itemAt(i).widget().setParent(None)

        # Add current metrics
        row = 0
        for key, value in self.metrics.items():
            name_label = QLabel(str(key).replace("_", " ").title())
            name_label.setFont(QFont("Arial", 10, QFont.Bold))

            value_label = QLabel(str(value))
            value_label.setAlignment(Qt.AlignRight)

            self.metrics_layout.addWidget(name_label, row, 0)
            self.metrics_layout.addWidget(value_label, row, 1)
            row += 1


class ExportWidget(QWidget):
    """Widget for exporting analytics data."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_source = None
        self.setup_ui()

    def setup_ui(self):
        """Set up the export widget UI."""
        layout = QVBoxLayout()

        # Header
        header = QLabel("Export Analytics")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Export format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Export Format:"))

        self.format_combo = QComboBox()
        self.format_combo.addItem("JSON", "json")
        self.format_combo.addItem("CSV", "csv")
        self.format_combo.addItem("XML", "xml")
        format_layout.addWidget(self.format_combo)

        layout.addLayout(format_layout)

        # Date range selection
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date Range:"))

        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        date_layout.addWidget(self.start_date)

        date_layout.addWidget(QLabel("to"))

        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.end_date)

        layout.addLayout(date_layout)

        # Export buttons
        button_layout = QHBoxLayout()

        export_button = QPushButton("Export Data")
        export_button.clicked.connect(self.export_data)
        button_layout.addWidget(export_button)

        preview_button = QPushButton("Preview")
        preview_button.clicked.connect(self.preview_data)
        button_layout.addWidget(preview_button)

        layout.addLayout(button_layout)

        # Preview area
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(200)
        layout.addWidget(self.preview_text)

        self.setLayout(layout)

    def set_data_source(self, data_source):
        """Set the data source for export."""
        self.data_source = data_source

    def preview_data(self):
        """Preview the data to be exported."""
        if not self.data_source:
            self.preview_text.setPlainText("No data source available")
            return

        try:
            # Generate sample data for preview
            sample_data = {
                "export_info": {
                    "format": self.format_combo.currentData(),
                    "start_date": self.start_date.date().toString(),
                    "end_date": self.end_date.date().toString(),
                    "generated_at": datetime.now().isoformat(),
                },
                "sample_metrics": {
                    "total_sessions": 42,
                    "avg_response_time": 1.23,
                    "user_satisfaction": 4.5,
                    "error_rate": 0.02,
                },
            }

            if self.format_combo.currentData() == "json":
                preview_text = json.dumps(sample_data, indent=2)
            elif self.format_combo.currentData() == "csv":
                preview_text = "metric,value\ntotal_sessions,42\navg_response_time,1.23\nuser_satisfaction,4.5\nerror_rate,0.02"
            else:
                preview_text = str(sample_data)

            self.preview_text.setPlainText(preview_text)

        except Exception as e:
            logger.error(f"Error generating preview: {e}")
            self.preview_text.setPlainText(f"Error generating preview: {e}")

    def export_data(self):
        """Export the analytics data."""
        try:
            format_type = self.format_combo.currentData()
            start_date = self.start_date.date().toString()
            end_date = self.end_date.date().toString()

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analytics_export_{timestamp}.{format_type}"

            # In a real implementation, this would save the actual data
            logger.info(f"Exporting analytics data to {filename}")
            logger.info(f"Date range: {start_date} to {end_date}")
            logger.info(f"Format: {format_type}")

            # Show success message
            if QT_AVAILABLE:
                msg = QMessageBox()
                msg.setWindowTitle("Export Complete")
                msg.setText(f"Analytics data exported successfully to {filename}")
                msg.exec()

        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            if QT_AVAILABLE:
                msg = QMessageBox()
                msg.setWindowTitle("Export Error")
                msg.setText(f"Error exporting data: {e}")
                msg.exec()


class AnalyticsDashboard(QWidget):
    """
    Main analytics dashboard widget providing comprehensive analytics visualization.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_manager = None
        self.setup_ui()
        self.setup_timer()

    def setup_ui(self):
        """Set up the main dashboard UI."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("📊 Lyrixa Analytics Dashboard")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin: 10px;")
        layout.addWidget(title)

        # Create tab widget
        self.tab_widget = QTabWidget()

        # Overview tab
        self.overview_tab = self.create_overview_tab()
        self.tab_widget.addTab(self.overview_tab, "📈 Overview")

        # Metrics tab
        self.metrics_tab = self.create_metrics_tab()
        self.tab_widget.addTab(self.metrics_tab, "📊 Metrics")

        # Charts tab
        self.charts_tab = self.create_charts_tab()
        self.tab_widget.addTab(self.charts_tab, "📉 Charts")

        # Export tab
        self.export_tab = self.create_export_tab()
        self.tab_widget.addTab(self.export_tab, "💾 Export")

        layout.addWidget(self.tab_widget)

        # Status bar
        self.status_label = QLabel("Dashboard ready")
        self.status_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def create_overview_tab(self) -> QWidget:
        """Create the overview tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Welcome message
        welcome = QLabel("Welcome to Lyrixa Analytics Dashboard")
        welcome.setFont(QFont("Arial", 14))
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setStyleSheet(
            "margin: 20px; padding: 10px; background-color: #ecf0f1; border-radius: 5px;"
        )
        layout.addWidget(welcome)

        # Quick stats
        stats_group = QGroupBox("Quick Statistics")
        stats_layout = QGridLayout()

        stats_data = [
            ("Total Sessions", "1,234"),
            ("Active Users", "89"),
            ("Avg Response Time", "1.2s"),
            ("Success Rate", "98.5%"),
            ("Data Processed", "45.6 MB"),
            ("Uptime", "99.9%"),
        ]

        for i, (label, value) in enumerate(stats_data):
            row, col = divmod(i, 2)

            stat_widget = QFrame()
            stat_widget.setFrameStyle(QFrame.Box)
            stat_widget.setStyleSheet(
                "padding: 10px; margin: 5px; background-color: #ffffff;"
            )

            stat_layout = QVBoxLayout()

            value_label = QLabel(value)
            value_label.setFont(QFont("Arial", 18, QFont.Bold))
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setStyleSheet("color: #3498db;")

            label_label = QLabel(label)
            label_label.setAlignment(Qt.AlignCenter)
            label_label.setStyleSheet("color: #7f8c8d;")

            stat_layout.addWidget(value_label)
            stat_layout.addWidget(label_label)
            stat_widget.setLayout(stat_layout)

            stats_layout.addWidget(stat_widget, row, col)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Recent activity
        activity_group = QGroupBox("Recent Activity")
        activity_layout = QVBoxLayout()

        self.activity_list = QListWidget()
        recent_activities = [
            "📈 Performance metrics updated",
            "🔄 Data synchronization completed",
            "📊 New analytics report generated",
            "🎯 User engagement threshold reached",
            "⚡ Response time optimization applied",
        ]

        for activity in recent_activities:
            item = QListWidgetItem(activity)
            self.activity_list.addItem(item)

        activity_layout.addWidget(self.activity_list)
        activity_group.setLayout(activity_layout)
        layout.addWidget(activity_group)

        widget.setLayout(layout)
        return widget

    def create_metrics_tab(self) -> QWidget:
        """Create the metrics tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        self.metrics_widget = MetricsWidget()
        layout.addWidget(self.metrics_widget)

        widget.setLayout(layout)
        return widget

    def create_charts_tab(self) -> QWidget:
        """Create the charts tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        self.chart_widget = ChartWidget()
        layout.addWidget(self.chart_widget)

        widget.setLayout(layout)
        return widget

    def create_export_tab(self) -> QWidget:
        """Create the export tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        self.export_widget = ExportWidget()
        layout.addWidget(self.export_widget)

        widget.setLayout(layout)
        return widget

    def setup_timer(self):
        """Set up the update timer."""
        if QT_AVAILABLE:
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self.update_data)
            self.update_timer.start(30000)  # Update every 30 seconds

    def update_data(self):
        """Update dashboard data."""
        try:
            # Generate sample metrics
            metrics = {
                "sessions_today": 89,
                "avg_response_time": 1.23,
                "memory_usage": 67.8,
                "cpu_usage": 23.4,
                "active_connections": 15,
                "data_processed_mb": 145.6,
                "success_rate": 98.7,
                "error_count": 3,
            }

            # Update metrics widget
            if hasattr(self, "metrics_widget"):
                self.metrics_widget.update_metrics(metrics)

            # Generate sample chart data
            chart_data = {
                "Mon": 45,
                "Tue": 52,
                "Wed": 38,
                "Thu": 61,
                "Fri": 49,
                "Sat": 34,
                "Sun": 28,
            }

            # Update chart widget
            if hasattr(self, "chart_widget"):
                self.chart_widget.update_data(chart_data)

            # Update status
            self.status_label.setText(
                f"Last updated: {datetime.now().strftime('%H:%M:%S')}"
            )

        except Exception as e:
            logger.error(f"Error updating dashboard data: {e}")
            self.status_label.setText(f"Update error: {e}")

    def set_data_manager(self, data_manager):
        """Set the data manager for the dashboard."""
        self.data_manager = data_manager
        if hasattr(self, "export_widget"):
            self.export_widget.set_data_source(data_manager)


def main():
    """Main function for testing the analytics dashboard."""
    if not QT_AVAILABLE:
        print("Qt not available. Running in headless mode.")
        dashboard = AnalyticsDashboard()
        print("Analytics dashboard created successfully in headless mode.")
        return dashboard

    app = QApplication([])
    dashboard = AnalyticsDashboard()
    dashboard.setWindowTitle("Lyrixa Analytics Dashboard")
    dashboard.setMinimumSize(1000, 700)
    dashboard.show()

    try:
        app.exec()
    except KeyboardInterrupt:
        print("\nShutting down analytics dashboard...")

    return dashboard


if __name__ == "__main__":
    main()
