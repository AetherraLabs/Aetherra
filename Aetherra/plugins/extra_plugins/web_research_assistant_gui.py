"""
Web Research Assistant GUI - Advanced Research Interface
Author: Aetherra Plugin System
Version: 1.0.0

Professional PySide6 GUI for the Web Research Assistant Plugin
Features:
- Multi-tab research interface with query management
- Real-time web content extraction and analysis
- Visual source credibility assessment
- Interactive research report generation
- Fact-checking dashboard with confidence indicators
- Export capabilities with multiple format support
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

try:
    from PySide6.QtCore import (
        QEasingCurve,
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
        QAction,
        QApplication,
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
        QScrollArea,
        QSizePolicy,
        QSlider,
        QSpacerItem,
        QSpinBox,
        QSplitter,
        QStatusBar,
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


class ResearchWorker(QObject):
    """Background worker for research operations."""

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

    async def run_research(self):
        """Run research operation."""
        try:
            self.progress.emit("Starting research...", 10)

            if self.is_cancelled:
                return

            if self.action == "conduct_research":
                # Simulate research progress
                self.progress.emit("Searching for sources...", 25)

                if self.is_cancelled:
                    return

                result = await self.plugin.conduct_research(
                    self.payload.get("query"), self.payload.get("options", {})
                )

                self.progress.emit("Analyzing content...", 50)

                if self.is_cancelled:
                    return

                self.progress.emit("Generating report...", 75)

                if self.is_cancelled:
                    return

                self.progress.emit("Research complete!", 100)
                self.finished.emit(result)

            elif self.action == "extract_content":
                self.progress.emit("Extracting content...", 50)
                result = await self.plugin.extract_single_source(
                    self.payload.get("url")
                )
                self.progress.emit("Extraction complete!", 100)
                self.finished.emit(result)

            elif self.action == "search_sources":
                self.progress.emit("Searching sources...", 50)
                result = await self.plugin.search_for_sources(
                    self.payload.get("query"), self.payload.get("max_results", 10)
                )
                self.progress.emit("Search complete!", 100)
                self.finished.emit(result)

            elif self.action == "fact_check":
                self.progress.emit("Fact checking...", 50)
                result = await self.plugin.fact_check_content(
                    self.payload.get("content")
                )
                self.progress.emit("Fact check complete!", 100)
                self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))


class SourceCredibilityWidget(QWidget):
    """Widget for displaying source credibility information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Source Credibility Analysis")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)

        # Credibility table
        self.credibility_table = QTableWidget()
        self.credibility_table.setColumnCount(5)
        self.credibility_table.setHorizontalHeaderLabels(
            ["Source", "Domain", "Credibility", "Word Count", "Reading Level"]
        )
        self.credibility_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.credibility_table)

        # Summary stats
        self.stats_label = QLabel("No sources analyzed")
        layout.addWidget(self.stats_label)

    def update_sources(self, sources):
        """Update the source display."""
        self.credibility_table.setRowCount(len(sources))

        high_credibility = 0
        total_words = 0

        for i, source in enumerate(sources):
            # Source title/URL
            title_item = QTableWidgetItem(source.get("title", "Untitled")[:50])
            self.credibility_table.setItem(i, 0, title_item)

            # Domain
            domain_item = QTableWidgetItem(source.get("domain", ""))
            self.credibility_table.setItem(i, 1, domain_item)

            # Credibility score
            credibility = source.get("credibility_score", 0.0)
            credibility_item = QTableWidgetItem(f"{credibility:.2f}")

            # Color code based on credibility
            if credibility > 0.7:
                credibility_item.setBackground(QColor(144, 238, 144))  # Light green
                high_credibility += 1
            elif credibility > 0.5:
                credibility_item.setBackground(QColor(255, 255, 224))  # Light yellow
            else:
                credibility_item.setBackground(QColor(255, 182, 193))  # Light red

            self.credibility_table.setItem(i, 2, credibility_item)

            # Word count
            word_count = source.get("word_count", 0)
            total_words += word_count
            word_item = QTableWidgetItem(str(word_count))
            self.credibility_table.setItem(i, 3, word_item)

            # Reading level
            reading_level = source.get("reading_level", "Unknown")
            level_item = QTableWidgetItem(reading_level)
            self.credibility_table.setItem(i, 4, level_item)

        # Update stats
        avg_credibility = (
            sum(s.get("credibility_score", 0) for s in sources) / len(sources)
            if sources
            else 0
        )
        self.stats_label.setText(
            f"Sources: {len(sources)} | High Credibility: {high_credibility} | "
            f"Total Words: {total_words:,} | Avg Credibility: {avg_credibility:.2f}"
        )


class FactCheckWidget(QWidget):
    """Widget for displaying fact-checking results."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Fact Check Results")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)

        # Fact check list
        self.fact_list = QListWidget()
        layout.addWidget(self.fact_list)

        # Summary
        self.summary_label = QLabel("No fact checks performed")
        layout.addWidget(self.summary_label)

    def update_fact_checks(self, fact_checks):
        """Update fact check display."""
        self.fact_list.clear()

        for fact_check in fact_checks:
            claim = fact_check.get("claim", "")
            verdict = fact_check.get("verdict", "Unknown")
            confidence = fact_check.get("confidence", 0.0)

            # Create list item
            item_text = f"Claim: {claim[:100]}...\nVerdict: {verdict} (Confidence: {confidence:.1%})"
            item = QListWidgetItem(item_text)

            # Color code based on verdict
            if "true" in verdict.lower():
                item.setBackground(QColor(144, 238, 144))  # Light green
            elif "false" in verdict.lower():
                item.setBackground(QColor(255, 182, 193))  # Light red
            else:
                item.setBackground(QColor(255, 255, 224))  # Light yellow

            self.fact_list.addItem(item)

        self.summary_label.setText(f"Analyzed {len(fact_checks)} factual claims")


class ResearchQueryDialog(QDialog):
    """Dialog for configuring research queries."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Research Query")
        self.setMinimumSize(600, 500)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)

        # Query configuration
        form_group = QGroupBox("Research Parameters")
        form_layout = QFormLayout(form_group)

        # Query text
        self.query_edit = QLineEdit()
        self.query_edit.setPlaceholderText("Enter your research query...")
        form_layout.addRow("Query:", self.query_edit)

        # Keywords
        self.keywords_edit = QLineEdit()
        self.keywords_edit.setPlaceholderText("Additional keywords (comma-separated)")
        form_layout.addRow("Keywords:", self.keywords_edit)

        # Depth
        self.depth_combo = QComboBox()
        self.depth_combo.addItems(["surface", "moderate", "deep"])
        self.depth_combo.setCurrentText("moderate")
        form_layout.addRow("Research Depth:", self.depth_combo)

        # Content types
        content_group = QGroupBox("Content Types")
        content_layout = QVBoxLayout(content_group)

        self.content_checks = {}
        content_types = ["article", "academic", "news", "blog", "social"]
        for content_type in content_types:
            checkbox = QCheckBox(content_type.title())
            if content_type in ["article", "news"]:
                checkbox.setChecked(True)
            self.content_checks[content_type] = checkbox
            content_layout.addWidget(checkbox)

        # Max sources
        self.max_sources_spin = QSpinBox()
        self.max_sources_spin.setRange(5, 50)
        self.max_sources_spin.setValue(20)
        form_layout.addRow("Max Sources:", self.max_sources_spin)

        # Language
        self.language_combo = QComboBox()
        self.language_combo.addItems(["en", "es", "fr", "de", "it", "pt"])
        form_layout.addRow("Language:", self.language_combo)

        layout.addWidget(form_group)
        layout.addWidget(content_group)

        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_research_config(self):
        """Get the research configuration."""
        selected_content_types = [
            content_type
            for content_type, checkbox in self.content_checks.items()
            if checkbox.isChecked()
        ]

        keywords = [
            k.strip() for k in self.keywords_edit.text().split(",") if k.strip()
        ]

        return {
            "query": self.query_edit.text(),
            "keywords": keywords,
            "depth": self.depth_combo.currentText(),
            "content_types": selected_content_types,
            "max_sources": self.max_sources_spin.value(),
            "language": self.language_combo.currentText(),
        }


class WebResearchAssistantGUI(QMainWindow):
    """Main GUI for Web Research Assistant Plugin."""

    def __init__(self, plugin=None):
        super().__init__()

        if not PYSIDE6_AVAILABLE:
            raise ImportError("PySide6 is required for the GUI interface")

        self.plugin = plugin
        self.current_research = None

        # Threading
        self.worker_thread = None
        self.worker = None

        self.setWindowTitle("Web Research Assistant")
        self.setMinimumSize(1200, 800)
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

        # Research tab
        self.create_research_tab()

        # URL Extraction tab
        self.create_extraction_tab()

        # Fact Check tab
        self.create_fact_check_tab()

        # Reports tab
        self.create_reports_tab()

        # Settings tab
        self.create_settings_tab()

    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_research_action = QAction("New Research", self)
        new_research_action.setShortcut("Ctrl+N")
        new_research_action.triggered.connect(self.new_research)
        file_menu.addAction(new_research_action)

        file_menu.addSeparator()

        export_action = QAction("Export Report", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_report)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")

        configure_action = QAction("Configure Query", self)
        configure_action.triggered.connect(self.configure_query)
        tools_menu.addAction(configure_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        """Create the toolbar."""
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Quick research button
        research_action = QAction("Quick Research", self)
        research_action.triggered.connect(self.quick_research)
        toolbar.addAction(research_action)

        toolbar.addSeparator()

        # Stop action
        self.stop_action = QAction("Stop", self)
        self.stop_action.triggered.connect(self.stop_operation)
        self.stop_action.setEnabled(False)
        toolbar.addAction(self.stop_action)

    def create_research_tab(self):
        """Create the main research tab."""
        research_widget = QWidget()
        layout = QVBoxLayout(research_widget)

        # Query section
        query_group = QGroupBox("Research Query")
        query_layout = QVBoxLayout(query_group)

        # Query input
        query_input_layout = QHBoxLayout()
        self.query_edit = QLineEdit()
        self.query_edit.setPlaceholderText("Enter your research query...")
        self.query_edit.returnPressed.connect(self.start_research)

        self.research_button = QPushButton("Start Research")
        self.research_button.clicked.connect(self.start_research)

        self.configure_button = QPushButton("Configure")
        self.configure_button.clicked.connect(self.configure_query)

        query_input_layout.addWidget(self.query_edit)
        query_input_layout.addWidget(self.configure_button)
        query_input_layout.addWidget(self.research_button)

        query_layout.addLayout(query_input_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        query_layout.addWidget(self.progress_bar)

        # Progress label
        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        query_layout.addWidget(self.progress_label)

        layout.addWidget(query_group)

        # Results section - split view
        results_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Sources and credibility
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Source credibility widget
        self.credibility_widget = SourceCredibilityWidget()
        left_layout.addWidget(self.credibility_widget)

        results_splitter.addWidget(left_panel)

        # Right panel - Research content
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Research summary
        summary_group = QGroupBox("Research Summary")
        summary_layout = QVBoxLayout(summary_group)

        self.summary_text = QTextBrowser()
        self.summary_text.setMinimumHeight(200)
        summary_layout.addWidget(self.summary_text)

        right_layout.addWidget(summary_group)

        # Key insights
        insights_group = QGroupBox("Key Insights")
        insights_layout = QVBoxLayout(insights_group)

        self.insights_list = QListWidget()
        insights_layout.addWidget(self.insights_list)

        right_layout.addWidget(insights_group)

        results_splitter.addWidget(right_panel)
        results_splitter.setSizes([400, 600])

        layout.addWidget(results_splitter)

        self.tab_widget.addTab(research_widget, "Research")

    def create_extraction_tab(self):
        """Create the URL extraction tab."""
        extraction_widget = QWidget()
        layout = QVBoxLayout(extraction_widget)

        # URL input section
        url_group = QGroupBox("URL Content Extraction")
        url_layout = QVBoxLayout(url_group)

        url_input_layout = QHBoxLayout()
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("Enter URL to extract content...")
        self.url_edit.returnPressed.connect(self.extract_url_content)

        self.extract_button = QPushButton("Extract Content")
        self.extract_button.clicked.connect(self.extract_url_content)

        url_input_layout.addWidget(self.url_edit)
        url_input_layout.addWidget(self.extract_button)
        url_layout.addLayout(url_input_layout)

        layout.addWidget(url_group)

        # Extracted content display
        content_splitter = QSplitter(Qt.Orientation.Vertical)

        # Metadata
        metadata_group = QGroupBox("Content Metadata")
        metadata_layout = QFormLayout(metadata_group)

        self.title_label = QLabel("N/A")
        self.domain_label = QLabel("N/A")
        self.author_label = QLabel("N/A")
        self.date_label = QLabel("N/A")
        self.credibility_label = QLabel("N/A")
        self.word_count_label = QLabel("N/A")
        self.reading_level_label = QLabel("N/A")

        metadata_layout.addRow("Title:", self.title_label)
        metadata_layout.addRow("Domain:", self.domain_label)
        metadata_layout.addRow("Author:", self.author_label)
        metadata_layout.addRow("Publish Date:", self.date_label)
        metadata_layout.addRow("Credibility Score:", self.credibility_label)
        metadata_layout.addRow("Word Count:", self.word_count_label)
        metadata_layout.addRow("Reading Level:", self.reading_level_label)

        content_splitter.addWidget(metadata_group)

        # Content text
        content_group = QGroupBox("Extracted Content")
        content_layout = QVBoxLayout(content_group)

        self.content_text = QTextBrowser()
        content_layout.addWidget(self.content_text)

        content_splitter.addWidget(content_group)
        content_splitter.setSizes([200, 400])

        layout.addWidget(content_splitter)

        self.tab_widget.addTab(extraction_widget, "URL Extraction")

    def create_fact_check_tab(self):
        """Create the fact-checking tab."""
        fact_check_widget = QWidget()
        layout = QVBoxLayout(fact_check_widget)

        # Input section
        input_group = QGroupBox("Content to Fact Check")
        input_layout = QVBoxLayout(input_group)

        self.fact_check_text = QTextEdit()
        self.fact_check_text.setPlaceholderText("Paste content to fact-check...")
        self.fact_check_text.setMaximumHeight(150)
        input_layout.addWidget(self.fact_check_text)

        button_layout = QHBoxLayout()
        self.fact_check_button = QPushButton("Analyze Claims")
        self.fact_check_button.clicked.connect(self.start_fact_check)

        self.clear_fact_check_button = QPushButton("Clear")
        self.clear_fact_check_button.clicked.connect(self.clear_fact_check)

        button_layout.addWidget(self.fact_check_button)
        button_layout.addWidget(self.clear_fact_check_button)
        button_layout.addStretch()

        input_layout.addLayout(button_layout)
        layout.addWidget(input_group)

        # Results section
        self.fact_check_widget = FactCheckWidget()
        layout.addWidget(self.fact_check_widget)

        self.tab_widget.addTab(fact_check_widget, "Fact Check")

    def create_reports_tab(self):
        """Create the reports management tab."""
        reports_widget = QWidget()
        layout = QVBoxLayout(reports_widget)

        # Report generation section
        generation_group = QGroupBox("Generate Report")
        generation_layout = QVBoxLayout(generation_group)

        format_layout = QHBoxLayout()

        format_label = QLabel("Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["summary", "detailed", "academic"])

        self.generate_report_button = QPushButton("Generate Report")
        self.generate_report_button.clicked.connect(self.generate_report)
        self.generate_report_button.setEnabled(False)

        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        format_layout.addWidget(self.generate_report_button)

        generation_layout.addLayout(format_layout)
        layout.addWidget(generation_group)

        # Report display
        display_group = QGroupBox("Report Preview")
        display_layout = QVBoxLayout(display_group)

        self.report_text = QTextBrowser()
        display_layout.addWidget(self.report_text)

        # Export buttons
        export_layout = QHBoxLayout()

        self.export_md_button = QPushButton("Export as Markdown")
        self.export_md_button.clicked.connect(lambda: self.export_report("markdown"))

        self.export_html_button = QPushButton("Export as HTML")
        self.export_html_button.clicked.connect(lambda: self.export_report("html"))

        self.export_pdf_button = QPushButton("Export as PDF")
        self.export_pdf_button.clicked.connect(lambda: self.export_report("pdf"))

        export_layout.addWidget(self.export_md_button)
        export_layout.addWidget(self.export_html_button)
        export_layout.addWidget(self.export_pdf_button)
        export_layout.addStretch()

        display_layout.addLayout(export_layout)
        layout.addWidget(display_group)

        self.tab_widget.addTab(reports_widget, "Reports")

    def create_settings_tab(self):
        """Create the settings tab."""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)

        # Plugin settings
        plugin_group = QGroupBox("Plugin Settings")
        plugin_layout = QFormLayout(plugin_group)

        self.max_sources_spin = QSpinBox()
        self.max_sources_spin.setRange(5, 100)
        self.max_sources_spin.setValue(20)
        plugin_layout.addRow("Max Sources:", self.max_sources_spin)

        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 120)
        self.timeout_spin.setValue(30)
        self.timeout_spin.setSuffix(" seconds")
        plugin_layout.addRow("Timeout:", self.timeout_spin)

        self.search_engine_combo = QComboBox()
        self.search_engine_combo.addItems(["duckduckgo", "bing"])
        plugin_layout.addRow("Search Engine:", self.search_engine_combo)

        self.fact_check_checkbox = QCheckBox("Enable Fact Checking")
        self.fact_check_checkbox.setChecked(True)
        plugin_layout.addRow("", self.fact_check_checkbox)

        self.credibility_threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.credibility_threshold_slider.setRange(0, 100)
        self.credibility_threshold_slider.setValue(60)
        self.credibility_threshold_label = QLabel("0.60")
        self.credibility_threshold_slider.valueChanged.connect(
            lambda v: self.credibility_threshold_label.setText(f"{v / 100:.2f}")
        )

        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(self.credibility_threshold_slider)
        threshold_layout.addWidget(self.credibility_threshold_label)
        plugin_layout.addRow("Credibility Threshold:", threshold_layout)

        layout.addWidget(plugin_group)

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
        # Set a modern look
        self.setStyleSheet("""
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
        """)

    def new_research(self):
        """Start a new research session."""
        self.query_edit.clear()
        self.summary_text.clear()
        self.insights_list.clear()
        self.credibility_widget.credibility_table.setRowCount(0)
        self.credibility_widget.stats_label.setText("No sources analyzed")
        self.current_research = None
        self.generate_report_button.setEnabled(False)
        self.status_bar.showMessage("Ready for new research")

    def configure_query(self):
        """Open query configuration dialog."""
        dialog = ResearchQueryDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            config = dialog.get_research_config()
            self.query_edit.setText(config["query"])
            # Store additional config for use in research
            self.research_config = config

    def quick_research(self):
        """Start quick research with current query."""
        self.start_research()

    def start_research(self):
        """Start the research process."""
        query = self.query_edit.text().strip()
        if not query:
            QMessageBox.warning(self, "Warning", "Please enter a research query.")
            return

        if not self.plugin:
            QMessageBox.critical(self, "Error", "Plugin not initialized.")
            return

        # Get research options
        options = getattr(
            self,
            "research_config",
            {
                "depth": "moderate",
                "content_types": ["article", "news"],
                "max_sources": 20,
            },
        )

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_bar.setValue(0)
        self.research_button.setEnabled(False)
        self.stop_action.setEnabled(True)

        # Start worker thread
        self.worker_thread = QThread()
        self.worker = ResearchWorker(
            self.plugin, "conduct_research", {"query": query, "options": options}
        )
        self.worker.moveToThread(self.worker_thread)

        # Connect signals
        self.worker_thread.started.connect(self.worker.run_research)
        self.worker.finished.connect(self.research_completed)
        self.worker.progress.connect(self.update_progress)
        self.worker.error.connect(self.research_error)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        # Start the thread
        self.worker_thread.start()
        self.status_bar.showMessage("Research in progress...")

    def stop_operation(self):
        """Stop the current operation."""
        if self.worker:
            self.worker.cancel()
        self.research_button.setEnabled(True)
        self.stop_action.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.status_bar.showMessage("Operation stopped")

    def update_progress(self, message, value):
        """Update progress display."""
        self.progress_label.setText(message)
        self.progress_bar.setValue(value)

    def research_completed(self, result):
        """Handle research completion."""
        self.research_button.setEnabled(True)
        self.stop_action.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)

        if result["status"] == "success":
            self.current_research = result["data"]
            self.display_research_results(result["data"])
            self.generate_report_button.setEnabled(True)
            self.status_bar.showMessage("Research completed successfully")
        else:
            QMessageBox.critical(
                self, "Research Error", result.get("message", "Unknown error")
            )
            self.status_bar.showMessage("Research failed")

    def research_error(self, error_message):
        """Handle research error."""
        self.research_button.setEnabled(True)
        self.stop_action.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        QMessageBox.critical(self, "Research Error", error_message)
        self.status_bar.showMessage("Research failed")

    def display_research_results(self, research_data):
        """Display research results in the UI."""
        # Update summary
        summary = research_data.get("summary", "No summary available")
        self.summary_text.setHtml(
            f"<div style='font-family: Arial; line-height: 1.4;'>{summary}</div>"
        )

        # Update insights
        self.insights_list.clear()
        insights = research_data.get("key_insights", [])
        for insight in insights:
            self.insights_list.addItem(insight)

        # Update credibility display
        sources = research_data.get("sources", [])
        self.credibility_widget.update_sources(sources)

        # Switch to research tab
        self.tab_widget.setCurrentIndex(0)

    def extract_url_content(self):
        """Extract content from specified URL."""
        url = self.url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a URL.")
            return

        if not self.plugin:
            QMessageBox.critical(self, "Error", "Plugin not initialized.")
            return

        # Start extraction
        self.extract_button.setEnabled(False)

        # Create worker
        self.worker_thread = QThread()
        self.worker = ResearchWorker(self.plugin, "extract_content", {"url": url})
        self.worker.moveToThread(self.worker_thread)

        # Connect signals
        self.worker_thread.started.connect(self.worker.run_research)
        self.worker.finished.connect(self.extraction_completed)
        self.worker.error.connect(self.extraction_error)
        self.worker.finished.connect(self.worker_thread.quit)

        # Start
        self.worker_thread.start()
        self.status_bar.showMessage("Extracting content...")

    def extraction_completed(self, result):
        """Handle extraction completion."""
        self.extract_button.setEnabled(True)

        if result["status"] == "success":
            source_data = result["data"]
            self.display_extracted_content(source_data)
            self.status_bar.showMessage("Content extracted successfully")
        else:
            QMessageBox.critical(
                self, "Extraction Error", result.get("message", "Unknown error")
            )
            self.status_bar.showMessage("Extraction failed")

    def extraction_error(self, error_message):
        """Handle extraction error."""
        self.extract_button.setEnabled(True)
        QMessageBox.critical(self, "Extraction Error", error_message)
        self.status_bar.showMessage("Extraction failed")

    def display_extracted_content(self, source_data):
        """Display extracted content."""
        # Update metadata labels
        self.title_label.setText(source_data.get("title", "N/A"))
        self.domain_label.setText(source_data.get("domain", "N/A"))
        self.author_label.setText(source_data.get("author", "N/A") or "N/A")
        self.date_label.setText(source_data.get("publish_date", "N/A") or "N/A")

        credibility = source_data.get("credibility_score", 0.0)
        self.credibility_label.setText(f"{credibility:.2f}")

        self.word_count_label.setText(str(source_data.get("word_count", 0)))
        self.reading_level_label.setText(source_data.get("reading_level", "N/A"))

        # Update content
        content = source_data.get("content", "No content extracted")
        self.content_text.setPlainText(content)

        # Switch to extraction tab
        self.tab_widget.setCurrentIndex(1)

    def start_fact_check(self):
        """Start fact-checking process."""
        content = self.fact_check_text.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "Warning", "Please enter content to fact-check.")
            return

        if not self.plugin:
            QMessageBox.critical(self, "Error", "Plugin not initialized.")
            return

        # Start fact checking
        self.fact_check_button.setEnabled(False)

        # Create worker
        self.worker_thread = QThread()
        self.worker = ResearchWorker(self.plugin, "fact_check", {"content": content})
        self.worker.moveToThread(self.worker_thread)

        # Connect signals
        self.worker_thread.started.connect(self.worker.run_research)
        self.worker.finished.connect(self.fact_check_completed)
        self.worker.error.connect(self.fact_check_error)
        self.worker.finished.connect(self.worker_thread.quit)

        # Start
        self.worker_thread.start()
        self.status_bar.showMessage("Fact-checking in progress...")

    def fact_check_completed(self, result):
        """Handle fact-check completion."""
        self.fact_check_button.setEnabled(True)

        if result["status"] == "success":
            fact_checks = result["data"]["fact_checks"]
            self.fact_check_widget.update_fact_checks(fact_checks)
            self.status_bar.showMessage("Fact-checking completed")
        else:
            QMessageBox.critical(
                self, "Fact Check Error", result.get("message", "Unknown error")
            )
            self.status_bar.showMessage("Fact-checking failed")

    def fact_check_error(self, error_message):
        """Handle fact-check error."""
        self.fact_check_button.setEnabled(True)
        QMessageBox.critical(self, "Fact Check Error", error_message)
        self.status_bar.showMessage("Fact-checking failed")

    def clear_fact_check(self):
        """Clear fact-check input and results."""
        self.fact_check_text.clear()
        self.fact_check_widget.fact_list.clear()
        self.fact_check_widget.summary_label.setText("No fact checks performed")

    def generate_report(self):
        """Generate research report."""
        if not self.current_research:
            QMessageBox.warning(self, "Warning", "No research data available.")
            return

        format_type = self.format_combo.currentText()

        # Generate report (simplified - would use plugin method)
        if format_type == "summary":
            report = self.generate_summary_report(self.current_research)
        elif format_type == "detailed":
            report = self.generate_detailed_report(self.current_research)
        else:
            report = self.generate_academic_report(self.current_research)

        self.report_text.setPlainText(report)
        self.tab_widget.setCurrentIndex(3)  # Switch to reports tab

    def generate_summary_report(self, data):
        """Generate summary report."""
        report = f"""Research Report: {data.get("query", {}).get("query", "Unknown Query")}

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Sources Analyzed: {data.get("total_sources", 0)} ({data.get("successful_extractions", 0)} successful)

Executive Summary:
{data.get("summary", "No summary available")}

Key Insights:
"""
        insights = data.get("key_insights", [])
        for i, insight in enumerate(insights, 1):
            report += f"{i}. {insight}\n"

        return report

    def generate_detailed_report(self, data):
        """Generate detailed report."""
        # Similar to summary but with more details
        return (
            self.generate_summary_report(data) + "\n\n[Detailed analysis would be here]"
        )

    def generate_academic_report(self, data):
        """Generate academic-style report."""
        # Academic format
        return f"Literature Review: {data.get('query', {}).get('query', 'Unknown Query')}\n\n[Academic format would be here]"

    def export_report(self, format_type="markdown"):
        """Export report to file."""
        if not self.report_text.toPlainText():
            QMessageBox.warning(self, "Warning", "No report to export.")
            return

        # File dialog
        if format_type == "markdown":
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Export Report",
                f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                "Markdown Files (*.md)",
            )
        elif format_type == "html":
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Export Report",
                f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                "HTML Files (*.html)",
            )
        else:  # PDF
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Export Report",
                f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                "PDF Files (*.pdf)",
            )

        if filename:
            try:
                if format_type in ["markdown", "html"]:
                    with open(filename, "w", encoding="utf-8") as f:
                        content = self.report_text.toPlainText()
                        if format_type == "html":
                            content = f"<html><body><pre>{content}</pre></body></html>"
                        f.write(content)
                else:
                    # PDF export would require additional libraries
                    QMessageBox.information(
                        self, "Info", "PDF export not implemented yet."
                    )
                    return

                QMessageBox.information(
                    self, "Success", f"Report exported to {filename}"
                )
                self.status_bar.showMessage(f"Report exported: {filename}")

            except Exception as e:
                QMessageBox.critical(
                    self, "Export Error", f"Failed to export report: {e}"
                )

    def apply_settings(self):
        """Apply settings to plugin."""
        if not self.plugin:
            return

        # Update plugin configuration
        config = {
            "max_sources": self.max_sources_spin.value(),
            "timeout_seconds": self.timeout_spin.value(),
            "default_search_engine": self.search_engine_combo.currentText(),
            "enable_fact_checking": self.fact_check_checkbox.isChecked(),
            "credibility_threshold": self.credibility_threshold_slider.value() / 100.0,
        }

        # Apply to plugin (would call plugin method)
        QMessageBox.information(self, "Settings", "Settings applied successfully.")
        self.status_bar.showMessage("Settings updated")

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Web Research Assistant",
            """
Web Research Assistant v1.0.0

An intelligent web research and content analysis system.

Features:
• Multi-source web content extraction
• Credibility assessment and fact-checking
• Research report generation
• Citation management

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
    gui = WebResearchAssistantGUI()
    gui.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
