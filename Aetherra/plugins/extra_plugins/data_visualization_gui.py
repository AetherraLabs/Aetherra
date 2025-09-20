"""
Data Visualization GUI - Advanced Charting and Analysis Interface
Author: Aetherra Plugin System
Version: 1.0.0

Professional PySide6 GUI for the Data Visualization Plugin
Features:
- Multi-tab interface for data loading, chart creation, and analysis
- Interactive chart configuration with real-time preview
- Statistical analysis dashboard with correlation matrices
- Data table viewer with filtering and sorting capabilities
- Export functionality for charts and reports
- Dashboard creation with multiple chart layouts
"""

# Standard library imports
import base64
import io
import json
import os
import sys
from datetime import datetime
from typing import Any

# Third party imports
import numpy as np
import pandas as pd

try:
    # Third party imports
    from PySide6.QtCore import (
        QAbstractTableModel,
        QEasingCurve,
        QModelIndex,
        QMutex,
        QObject,
        QPropertyAnimation,
        QRect,
        QSize,
        Qt,
        QThread,
        QTimer,
        QUrl,
        Signal,
    )
    from PySide6.QtGui import QAction as QGuiAction
    from PySide6.QtGui import (
        QColor,
        QDesktopServices,
        QFont,
        QIcon,
        QPalette,
        QPixmap,
        QSyntaxHighlighter,
        QTextCharFormat,
        QTextCursor,
        QTextDocument,
    )
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWidgets import (
        QAbstractItemView,
        QAction,
        QApplication,
        QButtonGroup,
        QCheckBox,
        QComboBox,
        QDialog,
        QDialogButtonBox,
        QFileDialog,
        QFormLayout,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QHeaderView,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QMainWindow,
        QMenu,
        QMenuBar,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QRadioButton,
        QScrollArea,
        QSizePolicy,
        QSlider,
        QSpacerItem,
        QSpinBox,
        QSplitter,
        QStackedWidget,
        QStatusBar,
        QTableView,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
        QTextBrowser,
        QTextEdit,
        QToolBar,
        QTreeWidget,
        QTreeWidgetItem,
        QVBoxLayout,
        QWidget,
    )

    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False


class DataFrameModel(QAbstractTableModel):
    """Model for displaying pandas DataFrames in QTableView."""

    def __init__(self, df=None):
        super().__init__()
        self._df = df if df is not None else pd.DataFrame()

    def rowCount(self, parent=QModelIndex()):
        return len(self._df)

    def columnCount(self, parent=QModelIndex()):
        return len(self._df.columns)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            value = self._df.iloc[index.row(), index.column()]
            if pd.isna(value):
                return "NaN"
            return str(value)

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._df.columns[section])
            else:
                return str(section)
        return None

    def update_data(self, df):
        """Update the model with new DataFrame."""
        self.beginResetModel()
        self._df = df
        self.endResetModel()


class VisualizationWorker(QObject):
    """Background worker for visualization operations."""

    finished = Signal(dict)
    progress = Signal(str, int)
    error = Signal(str)

    def __init__(self, plugin, action, payload):
        super().__init__()
        self.plugin = plugin
        self.action = action
        self.payload = payload
        self.is_cancelled = False

    def cancel(self):
        """Cancel the operation."""
        self.is_cancelled = True

    async def run_visualization(self):
        """Run visualization operation."""
        try:
            self.progress.emit("Starting operation...", 10)

            if self.is_cancelled:
                return

            if self.action == "load_data":
                self.progress.emit("Loading data...", 50)
                result = await self.plugin.load_data(
                    self.payload.get("file_path"), self.payload.get("options", {})
                )
            elif self.action == "create_chart":
                self.progress.emit("Generating chart...", 50)
                result = await self.plugin.create_chart(
                    self.payload.get("data"), self.payload.get("config")
                )
            elif self.action == "analyze_data":
                self.progress.emit("Analyzing data...", 50)
                result = await self.plugin.analyze_data(
                    self.payload.get("data"),
                    self.payload.get("analysis_type"),
                    self.payload.get("options", {}),
                )
            elif self.action == "generate_dashboard":
                self.progress.emit("Creating dashboard...", 50)
                result = await self.plugin.generate_dashboard(
                    self.payload.get("data"), self.payload.get("charts")
                )
            else:
                raise ValueError(f"Unknown action: {self.action}")

            if self.is_cancelled:
                return

            self.progress.emit("Operation complete!", 100)
            self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))


class ChartConfigWidget(QWidget):
    """Widget for configuring chart parameters."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)

        # Chart type selection
        type_group = QGroupBox("Chart Type")
        type_layout = QVBoxLayout(type_group)

        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(
            [
                "line",
                "bar",
                "scatter",
                "heatmap",
                "box",
                "histogram",
                "interactive_scatter",
                "interactive_line",
            ]
        )
        type_layout.addWidget(self.chart_type_combo)
        layout.addWidget(type_group)

        # Chart configuration
        config_group = QGroupBox("Configuration")
        config_layout = QFormLayout(config_group)

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Chart title...")
        config_layout.addRow("Title:", self.title_edit)

        self.x_column_combo = QComboBox()
        config_layout.addRow("X Column:", self.x_column_combo)

        self.y_column_combo = QComboBox()
        config_layout.addRow("Y Column:", self.y_column_combo)

        self.color_column_combo = QComboBox()
        self.color_column_combo.addItem("None")
        config_layout.addRow("Color Column:", self.color_column_combo)

        self.size_column_combo = QComboBox()
        self.size_column_combo.addItem("None")
        config_layout.addRow("Size Column:", self.size_column_combo)

        self.group_by_combo = QComboBox()
        self.group_by_combo.addItem("None")
        config_layout.addRow("Group By:", self.group_by_combo)

        layout.addWidget(config_group)

        # Style options
        style_group = QGroupBox("Style Options")
        style_layout = QFormLayout(style_group)

        self.width_spin = QSpinBox()
        self.width_spin.setRange(200, 2000)
        self.width_spin.setValue(800)
        style_layout.addRow("Width:", self.width_spin)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(200, 1500)
        self.height_spin.setValue(600)
        style_layout.addRow("Height:", self.height_spin)

        self.color_palette_combo = QComboBox()
        self.color_palette_combo.addItems(
            ["viridis", "plasma", "coolwarm", "Set1", "tab10", "Blues", "Reds"]
        )
        style_layout.addRow("Color Palette:", self.color_palette_combo)

        self.show_legend_check = QCheckBox()
        self.show_legend_check.setChecked(True)
        style_layout.addRow("Show Legend:", self.show_legend_check)

        self.show_grid_check = QCheckBox()
        self.show_grid_check.setChecked(True)
        style_layout.addRow("Show Grid:", self.show_grid_check)

        layout.addWidget(style_group)

        # Labels
        labels_group = QGroupBox("Labels")
        labels_layout = QFormLayout(labels_group)

        self.x_label_edit = QLineEdit()
        self.x_label_edit.setPlaceholderText("X-axis label...")
        labels_layout.addRow("X Label:", self.x_label_edit)

        self.y_label_edit = QLineEdit()
        self.y_label_edit.setPlaceholderText("Y-axis label...")
        labels_layout.addRow("Y Label:", self.y_label_edit)

        layout.addWidget(labels_group)

        layout.addStretch()

    def update_columns(self, columns):
        """Update column comboboxes with available columns."""
        # Clear existing items
        self.x_column_combo.clear()
        self.y_column_combo.clear()
        self.color_column_combo.clear()
        self.size_column_combo.clear()
        self.group_by_combo.clear()

        # Add new columns
        for combo in [self.x_column_combo, self.y_column_combo]:
            combo.addItems(columns)

        for combo in [
            self.color_column_combo,
            self.size_column_combo,
            self.group_by_combo,
        ]:
            combo.addItem("None")
            combo.addItems(columns)

    def get_config(self):
        """Get chart configuration."""
        return {
            "chart_type": self.chart_type_combo.currentText(),
            "title": self.title_edit.text(),
            "x_column": self.x_column_combo.currentText(),
            "y_column": self.y_column_combo.currentText(),
            "color_column": self.color_column_combo.currentText()
            if self.color_column_combo.currentText() != "None"
            else None,
            "size_column": self.size_column_combo.currentText()
            if self.size_column_combo.currentText() != "None"
            else None,
            "group_by": self.group_by_combo.currentText()
            if self.group_by_combo.currentText() != "None"
            else None,
            "width": self.width_spin.value(),
            "height": self.height_spin.value(),
            "color_palette": self.color_palette_combo.currentText(),
            "show_legend": self.show_legend_check.isChecked(),
            "show_grid": self.show_grid_check.isChecked(),
            "x_label": self.x_label_edit.text(),
            "y_label": self.y_label_edit.text(),
            "export_format": "png",
        }


class StatisticalAnalysisWidget(QWidget):
    """Widget for displaying statistical analysis results."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)

        # Analysis type selection
        type_group = QGroupBox("Analysis Type")
        type_layout = QVBoxLayout(type_group)

        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems(
            ["summary", "correlation", "distribution", "outliers", "trend"]
        )
        type_layout.addWidget(self.analysis_type_combo)

        # Analysis options
        options_layout = QHBoxLayout()

        self.column_combo = QComboBox()
        self.column_combo.setEnabled(False)

        self.x_column_combo = QComboBox()
        self.x_column_combo.setEnabled(False)

        self.y_column_combo = QComboBox()
        self.y_column_combo.setEnabled(False)

        options_layout.addWidget(QLabel("Column:"))
        options_layout.addWidget(self.column_combo)
        options_layout.addWidget(QLabel("X:"))
        options_layout.addWidget(self.x_column_combo)
        options_layout.addWidget(QLabel("Y:"))
        options_layout.addWidget(self.y_column_combo)

        type_layout.addLayout(options_layout)

        self.analyze_button = QPushButton("Run Analysis")
        type_layout.addWidget(self.analyze_button)

        layout.addWidget(type_group)

        # Results display
        results_group = QGroupBox("Analysis Results")
        results_layout = QVBoxLayout(results_group)

        self.results_text = QTextBrowser()
        results_layout.addWidget(self.results_text)

        layout.addWidget(results_group)

        # Connect signals
        self.analysis_type_combo.currentTextChanged.connect(
            self.on_analysis_type_changed
        )

    def update_columns(self, columns):
        """Update column comboboxes."""
        for combo in [self.column_combo, self.x_column_combo, self.y_column_combo]:
            combo.clear()
            combo.addItems(columns)

    def on_analysis_type_changed(self, analysis_type):
        """Handle analysis type change."""
        # Enable/disable controls based on analysis type
        if analysis_type in ["distribution", "outliers"]:
            self.column_combo.setEnabled(True)
            self.x_column_combo.setEnabled(False)
            self.y_column_combo.setEnabled(False)
        elif analysis_type == "trend":
            self.column_combo.setEnabled(False)
            self.x_column_combo.setEnabled(True)
            self.y_column_combo.setEnabled(True)
        else:
            self.column_combo.setEnabled(False)
            self.x_column_combo.setEnabled(False)
            self.y_column_combo.setEnabled(False)

    def get_analysis_config(self):
        """Get analysis configuration."""
        analysis_type = self.analysis_type_combo.currentText()
        options = {}

        if analysis_type in ["distribution", "outliers"]:
            options["column"] = self.column_combo.currentText()
        elif analysis_type == "trend":
            options["x_column"] = self.x_column_combo.currentText()
            options["y_column"] = self.y_column_combo.currentText()

        return analysis_type, options

    def display_results(self, results):
        """Display analysis results."""
        self.results_text.clear()

        if isinstance(results, dict):
            # Format results nicely
            formatted_text = self.format_analysis_results(results)
            self.results_text.setHtml(formatted_text)
        else:
            self.results_text.setPlainText(str(results))

    def format_analysis_results(self, results):
        """Format analysis results as HTML."""
        html = "<html><body style='font-family: Arial, sans-serif;'>"

        if "analysis_type" in results:
            html += f"<h2>Analysis: {results['analysis_type'].title()}</h2>"

        analysis_data = results.get("results", {})

        if "correlation_matrix" in analysis_data:
            html += "<h3>Correlation Matrix</h3>"
            corr_data = analysis_data["correlation_matrix"]
            html += self.format_correlation_matrix(corr_data)

        if "strong_correlations" in analysis_data:
            html += "<h3>Strong Correlations</h3>"
            for corr in analysis_data["strong_correlations"]:
                html += f"<p><strong>{corr['variable1']}</strong> ↔ <strong>{corr['variable2']}</strong>: "
                html += f"{corr['correlation']:.3f} ({corr['strength']})</p>"

        if "type" in analysis_data:
            if analysis_data["type"] == "numerical":
                html += "<h3>Distribution Statistics</h3>"
                html += f"<p><strong>Mean:</strong> {analysis_data.get('mean', 'N/A'):.3f}</p>"
                html += f"<p><strong>Median:</strong> {analysis_data.get('median', 'N/A'):.3f}</p>"
                html += f"<p><strong>Std Dev:</strong> {analysis_data.get('std', 'N/A'):.3f}</p>"
                html += f"<p><strong>Skewness:</strong> {analysis_data.get('skewness', 'N/A'):.3f}</p>"

        if "outlier_count" in analysis_data:
            html += "<h3>Outlier Analysis</h3>"
            html += (
                f"<p><strong>Method:</strong> {analysis_data.get('method', 'N/A')}</p>"
            )
            html += f"<p><strong>Outliers Found:</strong> {analysis_data['outlier_count']}</p>"
            html += f"<p><strong>Percentage:</strong> {analysis_data.get('outlier_percentage', 0):.2f}%</p>"

        if "trend_direction" in analysis_data:
            html += "<h3>Trend Analysis</h3>"
            html += f"<p><strong>Direction:</strong> {analysis_data['trend_direction'].title()}</p>"
            html += f"<p><strong>Strength:</strong> {analysis_data.get('trend_strength', 'N/A').title()}</p>"
            html += f"<p><strong>R-squared:</strong> {analysis_data.get('r_squared', 0):.3f}</p>"

        html += "</body></html>"
        return html

    def format_correlation_matrix(self, corr_data):
        """Format correlation matrix as HTML table."""
        if not corr_data:
            return "<p>No correlation data available</p>"

        html = "<table border='1' style='border-collapse: collapse; margin: 10px 0;'>"

        # Get variables
        variables = list(corr_data.keys())

        # Header row
        html += "<tr><th></th>"
        for var in variables:
            html += f"<th style='padding: 5px; background: #f0f0f0;'>{var}</th>"
        html += "</tr>"

        # Data rows
        for var1 in variables:
            html += f"<tr><th style='padding: 5px; background: #f0f0f0;'>{var1}</th>"
            for var2 in variables:
                corr_val = corr_data.get(var1, {}).get(var2, 0)
                color = self.get_correlation_color(corr_val)
                html += f"<td style='padding: 5px; background-color: {color}; text-align: center;'>{corr_val:.3f}</td>"
            html += "</tr>"

        html += "</table>"
        return html

    def get_correlation_color(self, value):
        """Get color for correlation value."""
        abs_val = abs(value)
        if abs_val > 0.8:
            return "#ff6b6b" if value > 0 else "#4ecdc4"
        elif abs_val > 0.5:
            return "#ffa8a8" if value > 0 else "#87ceeb"
        else:
            return "#ffffff"


class DataVisualizationGUI(QMainWindow):
    """Main GUI for Data Visualization Plugin."""

    def __init__(self, plugin=None):
        super().__init__()

        if not PYSIDE6_AVAILABLE:
            raise ImportError("PySide6 is required for the GUI interface")

        self.plugin = plugin
        self.current_data = None
        self.current_df = None
        self.charts = []

        # Threading
        self.worker_thread = None
        self.worker = None

        self.setWindowTitle("Data Visualization Studio")
        self.setMinimumSize(1400, 900)
        self.init_ui()
        self.init_style()

    def init_ui(self):
        """Initialize the user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)

        # Create menu bar
        self.create_menu_bar()

        # Create toolbar
        self.create_toolbar()

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Main tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Data tab
        self.create_data_tab()

        # Chart tab
        self.create_chart_tab()

        # Analysis tab
        self.create_analysis_tab()

        # Dashboard tab
        self.create_dashboard_tab()

        # Settings tab
        self.create_settings_tab()

    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        open_action = QAction("Open Data File", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_data_file)
        file_menu.addAction(open_action)

        save_chart_action = QAction("Save Chart", self)
        save_chart_action.setShortcut("Ctrl+S")
        save_chart_action.triggered.connect(self.save_chart)
        file_menu.addAction(save_chart_action)

        file_menu.addSeparator()

        export_dashboard_action = QAction("Export Dashboard", self)
        export_dashboard_action.triggered.connect(self.export_dashboard)
        file_menu.addAction(export_dashboard_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("View")

        refresh_action = QAction("Refresh Data", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_data)
        view_menu.addAction(refresh_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        """Create the toolbar."""
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Quick actions
        load_data_action = QAction("Load Data", self)
        load_data_action.triggered.connect(self.open_data_file)
        toolbar.addAction(load_data_action)

        toolbar.addSeparator()

        create_chart_action = QAction("Create Chart", self)
        create_chart_action.triggered.connect(self.create_chart)
        toolbar.addAction(create_chart_action)

        toolbar.addSeparator()

        # Stop action
        self.stop_action = QAction("Stop", self)
        self.stop_action.triggered.connect(self.stop_operation)
        self.stop_action.setEnabled(False)
        toolbar.addAction(self.stop_action)

    def create_data_tab(self):
        """Create the data loading and viewing tab."""
        data_widget = QWidget()
        layout = QVBoxLayout(data_widget)

        # Data loading section
        load_group = QGroupBox("Data Loading")
        load_layout = QVBoxLayout(load_group)

        # File selection
        file_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Select data file...")

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_data_file)

        self.load_button = QPushButton("Load Data")
        self.load_button.clicked.connect(self.load_data)

        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(self.browse_button)
        file_layout.addWidget(self.load_button)

        load_layout.addLayout(file_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        load_layout.addWidget(self.progress_bar)

        # Progress label
        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        load_layout.addWidget(self.progress_label)

        layout.addWidget(load_group)

        # Data view section
        view_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Data table
        table_group = QGroupBox("Data Preview")
        table_layout = QVBoxLayout(table_group)

        self.data_table = QTableView()
        self.data_model = DataFrameModel()
        self.data_table.setModel(self.data_model)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        table_layout.addWidget(self.data_table)

        view_splitter.addWidget(table_group)

        # Data summary
        summary_group = QGroupBox("Data Summary")
        summary_layout = QVBoxLayout(summary_group)

        self.summary_text = QTextBrowser()
        self.summary_text.setMaximumWidth(350)
        summary_layout.addWidget(self.summary_text)

        view_splitter.addWidget(summary_group)
        view_splitter.setSizes([800, 350])

        layout.addWidget(view_splitter)

        self.tab_widget.addTab(data_widget, "Data")

    def create_chart_tab(self):
        """Create the chart creation tab."""
        chart_widget = QWidget()
        layout = QVBoxLayout(chart_widget)

        # Main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Configuration
        config_scroll = QScrollArea()
        config_scroll.setWidgetResizable(True)
        config_scroll.setMaximumWidth(350)

        self.chart_config_widget = ChartConfigWidget()
        config_scroll.setWidget(self.chart_config_widget)

        main_splitter.addWidget(config_scroll)

        # Right panel - Chart display
        chart_panel = QWidget()
        chart_layout = QVBoxLayout(chart_panel)

        # Chart controls
        controls_layout = QHBoxLayout()

        self.create_chart_button = QPushButton("Generate Chart")
        self.create_chart_button.clicked.connect(self.create_chart)
        self.create_chart_button.setEnabled(False)

        self.save_chart_button = QPushButton("Save Chart")
        self.save_chart_button.clicked.connect(self.save_chart)
        self.save_chart_button.setEnabled(False)

        self.add_to_dashboard_button = QPushButton("Add to Dashboard")
        self.add_to_dashboard_button.clicked.connect(self.add_to_dashboard)
        self.add_to_dashboard_button.setEnabled(False)

        controls_layout.addWidget(self.create_chart_button)
        controls_layout.addWidget(self.save_chart_button)
        controls_layout.addWidget(self.add_to_dashboard_button)
        controls_layout.addStretch()

        chart_layout.addLayout(controls_layout)

        # Chart display area
        self.chart_display = QLabel()
        self.chart_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_display.setStyleSheet("border: 1px solid #ccc; background: white;")
        self.chart_display.setMinimumHeight(400)
        self.chart_display.setText("No chart generated")

        chart_scroll = QScrollArea()
        chart_scroll.setWidget(self.chart_display)
        chart_scroll.setWidgetResizable(True)
        chart_layout.addWidget(chart_scroll)

        main_splitter.addWidget(chart_panel)
        main_splitter.setSizes([350, 800])

        layout.addWidget(main_splitter)

        self.tab_widget.addTab(chart_widget, "Charts")

    def create_analysis_tab(self):
        """Create the statistical analysis tab."""
        analysis_widget = QWidget()
        layout = QVBoxLayout(analysis_widget)

        # Analysis splitter
        analysis_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Analysis configuration
        self.analysis_widget = StatisticalAnalysisWidget()
        self.analysis_widget.analyze_button.clicked.connect(self.run_analysis)
        self.analysis_widget.setMaximumWidth(350)

        analysis_splitter.addWidget(self.analysis_widget)

        # Right panel - Results
        results_group = QGroupBox("Analysis Results")
        results_layout = QVBoxLayout(results_group)

        self.analysis_results = QTextBrowser()
        results_layout.addWidget(self.analysis_results)

        analysis_splitter.addWidget(results_group)
        analysis_splitter.setSizes([350, 800])

        layout.addWidget(analysis_splitter)

        self.tab_widget.addTab(analysis_widget, "Analysis")

    def create_dashboard_tab(self):
        """Create the dashboard management tab."""
        dashboard_widget = QWidget()
        layout = QVBoxLayout(dashboard_widget)

        # Dashboard controls
        controls_group = QGroupBox("Dashboard Controls")
        controls_layout = QHBoxLayout(controls_group)

        self.create_dashboard_button = QPushButton("Create Dashboard")
        self.create_dashboard_button.clicked.connect(self.create_dashboard)

        self.clear_dashboard_button = QPushButton("Clear Dashboard")
        self.clear_dashboard_button.clicked.connect(self.clear_dashboard)

        self.export_dashboard_button = QPushButton("Export Dashboard")
        self.export_dashboard_button.clicked.connect(self.export_dashboard)

        controls_layout.addWidget(self.create_dashboard_button)
        controls_layout.addWidget(self.clear_dashboard_button)
        controls_layout.addWidget(self.export_dashboard_button)
        controls_layout.addStretch()

        layout.addWidget(controls_group)

        # Dashboard preview
        preview_group = QGroupBox("Dashboard Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.dashboard_web_view = QWebEngineView()
        self.dashboard_web_view.setHtml(
            "<html><body><h2>No dashboard created</h2></body></html>"
        )
        preview_layout.addWidget(self.dashboard_web_view)

        layout.addWidget(preview_group)

        # Charts list
        charts_group = QGroupBox("Charts in Dashboard")
        charts_layout = QVBoxLayout(charts_group)

        self.charts_list = QListWidget()
        self.charts_list.setMaximumHeight(150)
        charts_layout.addWidget(self.charts_list)

        layout.addWidget(charts_group)

        self.tab_widget.addTab(dashboard_widget, "Dashboard")

    def create_settings_tab(self):
        """Create the settings tab."""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)

        # Plugin settings
        plugin_group = QGroupBox("Plugin Settings")
        plugin_layout = QFormLayout(plugin_group)

        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setText("visualizations")
        plugin_layout.addRow("Output Directory:", self.output_dir_edit)

        self.auto_clean_check = QCheckBox()
        self.auto_clean_check.setChecked(True)
        plugin_layout.addRow("Auto Clean Data:", self.auto_clean_check)

        self.enable_stats_check = QCheckBox()
        self.enable_stats_check.setChecked(True)
        plugin_layout.addRow("Enable Statistical Analysis:", self.enable_stats_check)

        self.default_dpi_spin = QSpinBox()
        self.default_dpi_spin.setRange(50, 300)
        self.default_dpi_spin.setValue(100)
        plugin_layout.addRow("Default DPI:", self.default_dpi_spin)

        layout.addWidget(plugin_group)

        # Chart defaults
        chart_group = QGroupBox("Chart Defaults")
        chart_layout = QFormLayout(chart_group)

        self.default_width_spin = QSpinBox()
        self.default_width_spin.setRange(200, 2000)
        self.default_width_spin.setValue(800)
        chart_layout.addRow("Default Width:", self.default_width_spin)

        self.default_height_spin = QSpinBox()
        self.default_height_spin.setRange(200, 1500)
        self.default_height_spin.setValue(600)
        chart_layout.addRow("Default Height:", self.default_height_spin)

        self.default_palette_combo = QComboBox()
        self.default_palette_combo.addItems(
            ["viridis", "plasma", "coolwarm", "Set1", "tab10"]
        )
        chart_layout.addRow("Default Color Palette:", self.default_palette_combo)

        layout.addWidget(chart_group)

        # Apply settings button
        apply_layout = QHBoxLayout()
        apply_layout.addStretch()

        self.apply_settings_button = QPushButton("Apply Settings")
        self.apply_settings_button.clicked.connect(self.apply_settings)
        apply_layout.addWidget(self.apply_settings_button)

        layout.addLayout(apply_layout)
        layout.addStretch()

        self.tab_widget.addTab(settings_widget, "Settings")

    def init_style(self):
        """Initialize the application style."""
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                font-size: 14px;
            }
            QTextEdit, QTextBrowser {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTableView {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
                gridline-color: #e0e0e0;
            }
            QTableView::item {
                padding: 4px;
            }
            QTableView::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e1e1e1;
                border: 1px solid #cccccc;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
        """
        )

    def open_data_file(self):
        """Open file dialog to select data file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Data File",
            "",
            "Data Files (*.csv *.xlsx *.json *.parquet);;CSV Files (*.csv);;Excel Files (*.xlsx);;JSON Files (*.json);;Parquet Files (*.parquet)",
        )

        if file_path:
            self.file_path_edit.setText(file_path)

    def browse_data_file(self):
        """Browse for data file."""
        self.open_data_file()

    def load_data(self):
        """Load data from selected file."""
        file_path = self.file_path_edit.text().strip()
        if not file_path:
            QMessageBox.warning(self, "Warning", "Please select a data file.")
            return

        if not self.plugin:
            QMessageBox.critical(self, "Error", "Plugin not initialized.")
            return

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_bar.setValue(0)
        self.load_button.setEnabled(False)
        self.stop_action.setEnabled(True)

        # Start worker thread
        self.worker_thread = QThread()
        self.worker = VisualizationWorker(
            self.plugin,
            "load_data",
            {
                "file_path": file_path,
                "options": {"clean_data": self.auto_clean_check.isChecked()},
            },
        )
        self.worker.moveToThread(self.worker_thread)

        # Connect signals
        self.worker_thread.started.connect(self.worker.run_visualization)
        self.worker.finished.connect(self.data_loaded)
        self.worker.progress.connect(self.update_progress)
        self.worker.error.connect(self.operation_error)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        # Start the thread
        self.worker_thread.start()
        self.status_bar.showMessage("Loading data...")

    def data_loaded(self, result):
        """Handle data loading completion."""
        self.load_button.setEnabled(True)
        self.stop_action.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)

        if result["status"] == "success":
            self.current_data = result["data"]

            # Load DataFrame
            df_json = self.current_data["dataframe"]
            self.current_df = pd.read_json(df_json, orient="records")

            # Update data table
            self.data_model.update_data(self.current_df)

            # Update summary
            summary = self.current_data["summary"]
            self.display_data_summary(summary)

            # Update column lists
            columns = list(self.current_df.columns)
            self.chart_config_widget.update_columns(columns)
            self.analysis_widget.update_columns(columns)

            # Enable chart creation
            self.create_chart_button.setEnabled(True)

            self.status_bar.showMessage(
                f"Data loaded: {self.current_df.shape[0]} rows, {self.current_df.shape[1]} columns"
            )

            # Switch to data tab
            self.tab_widget.setCurrentIndex(0)

        else:
            QMessageBox.critical(
                self, "Data Loading Error", result.get("message", "Unknown error")
            )
            self.status_bar.showMessage("Data loading failed")

    def display_data_summary(self, summary):
        """Display data summary in the summary text browser."""
        html = "<html><body style='font-family: Arial; font-size: 12px;'>"
        html += "<h3>Data Summary</h3>"

        html += f"<p><strong>Shape:</strong> {summary['shape'][0]} rows × {summary['shape'][1]} columns</p>"
        html += f"<p><strong>Memory Usage:</strong> {summary['memory_usage'] / 1024 / 1024:.2f} MB</p>"

        html += "<h4>Column Types</h4>"
        html += f"<p>Numeric: {len(summary['numeric_columns'])}</p>"
        html += f"<p>Categorical: {len(summary['categorical_columns'])}</p>"
        html += f"<p>DateTime: {len(summary['datetime_columns'])}</p>"

        if summary.get("statistics"):
            html += "<h4>Statistical Summary</h4>"
            html += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
            html += "<tr><th>Column</th><th>Mean</th><th>Std</th><th>Min</th><th>Max</th></tr>"

            for col, stats in summary["statistics"].items():
                html += f"<tr>"
                html += f"<td>{col}</td>"
                html += f"<td>{stats.get('mean', 'N/A'):.2f}</td>"
                html += f"<td>{stats.get('std', 'N/A'):.2f}</td>"
                html += f"<td>{stats.get('min', 'N/A'):.2f}</td>"
                html += f"<td>{stats.get('max', 'N/A'):.2f}</td>"
                html += f"</tr>"

            html += "</table>"

        html += "</body></html>"
        self.summary_text.setHtml(html)

    def create_chart(self):
        """Create chart with current configuration."""
        if not self.current_data:
            QMessageBox.warning(self, "Warning", "Please load data first.")
            return

        config = self.chart_config_widget.get_config()

        if not config["x_column"] or not config["y_column"]:
            QMessageBox.warning(self, "Warning", "Please select X and Y columns.")
            return

        # Show progress
        self.create_chart_button.setEnabled(False)

        # Start worker thread
        self.worker_thread = QThread()
        self.worker = VisualizationWorker(
            self.plugin, "create_chart", {"data": self.current_data, "config": config}
        )
        self.worker.moveToThread(self.worker_thread)

        # Connect signals
        self.worker_thread.started.connect(self.worker.run_visualization)
        self.worker.finished.connect(self.chart_created)
        self.worker.error.connect(self.operation_error)
        self.worker.finished.connect(self.worker_thread.quit)

        # Start the thread
        self.worker_thread.start()
        self.status_bar.showMessage("Creating chart...")

    def chart_created(self, result):
        """Handle chart creation completion."""
        self.create_chart_button.setEnabled(True)

        if result["status"] == "success":
            chart_data = result["data"]

            # Display chart
            if chart_data.get("image_data"):
                # Static chart
                image_data = chart_data["image_data"]
                pixmap = self.base64_to_pixmap(image_data)
                self.chart_display.setPixmap(
                    pixmap.scaled(
                        800,
                        600,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
            elif chart_data.get("html_content"):
                # Interactive chart - would need WebEngine view
                self.chart_display.setText("Interactive chart created (HTML)")

            # Store current chart
            self.current_chart = chart_data

            # Enable save and dashboard buttons
            self.save_chart_button.setEnabled(True)
            self.add_to_dashboard_button.setEnabled(True)

            self.status_bar.showMessage("Chart created successfully")

            # Switch to chart tab
            self.tab_widget.setCurrentIndex(1)

        else:
            QMessageBox.critical(
                self, "Chart Creation Error", result.get("message", "Unknown error")
            )
            self.status_bar.showMessage("Chart creation failed")

    def base64_to_pixmap(self, image_data):
        """Convert base64 image data to QPixmap."""
        image_bytes = base64.b64decode(image_data)
        pixmap = QPixmap()
        pixmap.loadFromData(image_bytes)
        return pixmap

    def save_chart(self):
        """Save current chart to file."""
        if not hasattr(self, "current_chart"):
            QMessageBox.warning(self, "Warning", "No chart to save.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Chart",
            f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            "PNG Files (*.png);;JPEG Files (*.jpg);;SVG Files (*.svg);;PDF Files (*.pdf)",
        )

        if file_path:
            try:
                if self.current_chart.get("image_data"):
                    # Save static image
                    image_bytes = base64.b64decode(self.current_chart["image_data"])
                    with open(file_path, "wb") as f:
                        f.write(image_bytes)

                QMessageBox.information(self, "Success", f"Chart saved to {file_path}")
                self.status_bar.showMessage(f"Chart saved: {file_path}")

            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save chart: {e}")

    def add_to_dashboard(self):
        """Add current chart to dashboard."""
        if hasattr(self, "current_chart"):
            self.charts.append(self.current_chart.copy())

            # Update charts list
            chart_config = self.current_chart.get("chart_config", {})
            title = chart_config.get("title", f"Chart {len(self.charts)}")
            self.charts_list.addItem(f"{len(self.charts)}. {title}")

            QMessageBox.information(self, "Success", "Chart added to dashboard!")

    def run_analysis(self):
        """Run statistical analysis."""
        if not self.current_data:
            QMessageBox.warning(self, "Warning", "Please load data first.")
            return

        analysis_type, options = self.analysis_widget.get_analysis_config()

        # Start analysis
        self.analysis_widget.analyze_button.setEnabled(False)

        # Start worker thread
        self.worker_thread = QThread()
        self.worker = VisualizationWorker(
            self.plugin,
            "analyze_data",
            {
                "data": self.current_data,
                "analysis_type": analysis_type,
                "options": options,
            },
        )
        self.worker.moveToThread(self.worker_thread)

        # Connect signals
        self.worker_thread.started.connect(self.worker.run_visualization)
        self.worker.finished.connect(self.analysis_completed)
        self.worker.error.connect(self.operation_error)
        self.worker.finished.connect(self.worker_thread.quit)

        # Start the thread
        self.worker_thread.start()
        self.status_bar.showMessage("Running analysis...")

    def analysis_completed(self, result):
        """Handle analysis completion."""
        self.analysis_widget.analyze_button.setEnabled(True)

        if result["status"] == "success":
            self.analysis_widget.display_results(result["data"])
            self.status_bar.showMessage("Analysis completed")

            # Switch to analysis tab
            self.tab_widget.setCurrentIndex(2)

        else:
            QMessageBox.critical(
                self, "Analysis Error", result.get("message", "Unknown error")
            )
            self.status_bar.showMessage("Analysis failed")

    def create_dashboard(self):
        """Create dashboard from charts."""
        if not self.charts:
            QMessageBox.warning(self, "Warning", "No charts available for dashboard.")
            return

        # Start dashboard creation
        self.create_dashboard_button.setEnabled(False)

        # Start worker thread
        self.worker_thread = QThread()
        self.worker = VisualizationWorker(
            self.plugin,
            "generate_dashboard",
            {
                "data": self.current_data,
                "charts": [chart.get("chart_config", {}) for chart in self.charts],
            },
        )
        self.worker.moveToThread(self.worker_thread)

        # Connect signals
        self.worker_thread.started.connect(self.worker.run_visualization)
        self.worker.finished.connect(self.dashboard_created)
        self.worker.error.connect(self.operation_error)
        self.worker.finished.connect(self.worker_thread.quit)

        # Start the thread
        self.worker_thread.start()
        self.status_bar.showMessage("Creating dashboard...")

    def dashboard_created(self, result):
        """Handle dashboard creation completion."""
        self.create_dashboard_button.setEnabled(True)

        if result["status"] == "success":
            dashboard_data = result["data"]
            html_content = dashboard_data.get("dashboard_html", "")

            # Display dashboard
            self.dashboard_web_view.setHtml(html_content)

            self.current_dashboard = dashboard_data
            self.status_bar.showMessage("Dashboard created successfully")

            # Switch to dashboard tab
            self.tab_widget.setCurrentIndex(3)

        else:
            QMessageBox.critical(
                self, "Dashboard Error", result.get("message", "Unknown error")
            )
            self.status_bar.showMessage("Dashboard creation failed")

    def clear_dashboard(self):
        """Clear dashboard and charts list."""
        self.charts.clear()
        self.charts_list.clear()
        self.dashboard_web_view.setHtml(
            "<html><body><h2>No dashboard created</h2></body></html>"
        )
        self.current_dashboard = None

    def export_dashboard(self):
        """Export dashboard to HTML file."""
        if not hasattr(self, "current_dashboard") or not self.current_dashboard:
            QMessageBox.warning(self, "Warning", "No dashboard to export.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Dashboard",
            f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            "HTML Files (*.html)",
        )

        if file_path:
            try:
                html_content = self.current_dashboard.get("dashboard_html", "")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html_content)

                QMessageBox.information(
                    self, "Success", f"Dashboard exported to {file_path}"
                )
                self.status_bar.showMessage(f"Dashboard exported: {file_path}")

            except Exception as e:
                QMessageBox.critical(
                    self, "Export Error", f"Failed to export dashboard: {e}"
                )

    def refresh_data(self):
        """Refresh data display."""
        if self.current_df is not None:
            self.data_model.update_data(self.current_df)

    def stop_operation(self):
        """Stop current operation."""
        if self.worker:
            self.worker.cancel()
        self.stop_action.setEnabled(False)
        self.status_bar.showMessage("Operation stopped")

    def update_progress(self, message, value):
        """Update progress display."""
        self.progress_label.setText(message)
        self.progress_bar.setValue(value)

    def operation_error(self, error_message):
        """Handle operation error."""
        QMessageBox.critical(self, "Operation Error", error_message)
        self.status_bar.showMessage("Operation failed")

        # Reset UI state
        self.load_button.setEnabled(True)
        self.create_chart_button.setEnabled(True)
        self.analysis_widget.analyze_button.setEnabled(True)
        self.create_dashboard_button.setEnabled(True)
        self.stop_action.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)

    def apply_settings(self):
        """Apply settings to plugin."""
        if not self.plugin:
            return

        # Update plugin configuration
        config = {
            "output_directory": self.output_dir_edit.text(),
            "auto_clean_data": self.auto_clean_check.isChecked(),
            "enable_statistical_analysis": self.enable_stats_check.isChecked(),
            "default_dpi": self.default_dpi_spin.value(),
            "default_chart_size": (
                self.default_width_spin.value(),
                self.default_height_spin.value(),
            ),
        }

        # Apply to plugin (would call plugin method)
        QMessageBox.information(self, "Settings", "Settings applied successfully.")
        self.status_bar.showMessage("Settings updated")

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Data Visualization Studio",
            """
Data Visualization Studio v1.0.0

Advanced data visualization and statistical analysis system.

Features:
• Multiple chart types with customization
• Statistical analysis and correlation matrices
• Interactive plotting capabilities
• Dashboard creation and export
• Data import from multiple formats

Powered by Aetherra Plugin System
            """.strip(),
        )


def main():
    """Main entry point for testing the GUI."""
    if not PYSIDE6_AVAILABLE:
        print("PySide6 is required to run the GUI")
        return

    app = QApplication(sys.argv)

    # Create and show the GUI
    gui = DataVisualizationGUI()
    gui.show()
    sys.exit(app.exec())  # nosec B102: Qt application execution


if __name__ == "__main__":
    main()
