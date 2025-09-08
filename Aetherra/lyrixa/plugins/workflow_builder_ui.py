# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Workflow Builder Plugin UI
Visual workflow design and automation system
"""

import json
import sys
from pathlib import Path

from PySide6.QtCore import QRectF, Qt, QTimer  # noqa: F401 (optional runtime import)
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class WorkflowNode(QGraphicsRectItem):
    """A visual node in the workflow builder."""

    def __init__(self, node_type, title, x=0, y=0):
        super().__init__(0, 0, 120, 80)
        self.node_type = node_type
        self.title = title
        self.setPos(x, y)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        # Style based on node type
        colors = {
            "start": QColor(0, 255, 136),
            "action": QColor(107, 136, 255),
            "condition": QColor(255, 193, 7),
            "end": QColor(255, 107, 107),
        }

        self.setBrush(QBrush(colors.get(node_type, QColor(128, 128, 128))))
        self.setPen(QPen(QColor(255, 255, 255), 2))

        # Add text
        self.text_item = QGraphicsTextItem(title, self)
        self.text_item.setPos(10, 25)
        self.text_item.setDefaultTextColor(QColor(255, 255, 255))


class WorkflowBuilderUI(QWidget):
    """Workflow Builder Plugin UI for creating and managing automated workflows."""

    def __init__(self):
        super().__init__()
        self.workflows_file = Path(__file__).parent.parent / "workflows.json"
        self.setup_ui()
        self.apply_styling()
        self.load_workflows()

        # Auto-save timer
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave_workflow)
        self.autosave_timer.start(30000)  # Auto-save every 30 seconds

    def setup_ui(self):
        """Set up the workflow builder interface."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("⚡ Workflow Builder")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #4CAF50; margin: 10px;"
        )
        layout.addWidget(title)

        # Create main tab widget
        self.tabs = QTabWidget()

        # Visual Designer Tab
        self.tabs.addTab(self.create_visual_designer(), "🎨 Visual Designer")

        # Workflow Library Tab
        self.tabs.addTab(self.create_workflow_library(), "📚 Workflow Library")

        # Execution Monitor Tab
        self.tabs.addTab(self.create_execution_monitor(), "⚡ Execution Monitor")

        # Templates Tab
        self.tabs.addTab(self.create_templates(), "📋 Templates")

        # Settings Tab
        self.tabs.addTab(self.create_settings(), "⚙️ Settings")

        layout.addWidget(self.tabs)

    def create_visual_designer(self):
        """Create the visual workflow designer interface."""
        widget = QWidget()
        layout = QHBoxLayout(widget)

        # Left panel - Toolbox
        toolbox_panel = QFrame()
        toolbox_panel.setFrameStyle(QFrame.Shape.StyledPanel)
        toolbox_panel.setMaximumWidth(250)
        toolbox_layout = QVBoxLayout(toolbox_panel)

        # Workflow info
        info_group = QGroupBox("📝 Workflow Info")
        info_layout = QGridLayout(info_group)

        info_layout.addWidget(QLabel("Name:"), 0, 0)
        self.workflow_name = QLineEdit()
        self.workflow_name.setPlaceholderText("Untitled Workflow")
        info_layout.addWidget(self.workflow_name, 0, 1)

        info_layout.addWidget(QLabel("Description:"), 1, 0)
        self.workflow_description = QTextEdit()
        self.workflow_description.setMaximumHeight(60)
        self.workflow_description.setPlaceholderText("Workflow description...")
        info_layout.addWidget(self.workflow_description, 1, 1)

        toolbox_layout.addWidget(info_group)

        # Node palette
        palette_group = QGroupBox("🎯 Node Palette")
        palette_layout = QVBoxLayout(palette_group)

        # Node types
        node_types = [
            ("▶️ Start", "start"),
            ("⚙️ Action", "action"),
            ("❓ Condition", "condition"),
            ("⏹️ End", "end"),
        ]

        for name, node_type in node_types:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, nt=node_type: self.add_node(nt))
            palette_layout.addWidget(btn)

        toolbox_layout.addWidget(palette_group)

        # Node properties
        props_group = QGroupBox("🔧 Node Properties")
        props_layout = QVBoxLayout(props_group)

        self.node_props = QTextEdit()
        self.node_props.setPlaceholderText("Select a node to edit properties...")
        self.node_props.setMaximumHeight(150)
        props_layout.addWidget(self.node_props)

        save_props_btn = QPushButton("💾 Save Properties")
        props_layout.addWidget(save_props_btn)

        toolbox_layout.addWidget(props_group)

        # Workflow controls
        controls_group = QGroupBox("🎮 Controls")
        controls_layout = QVBoxLayout(controls_group)

        new_btn = QPushButton("📄 New Workflow")
        save_btn = QPushButton("💾 Save Workflow")
        load_btn = QPushButton("📁 Load Workflow")
        test_btn = QPushButton("🧪 Test Workflow")
        run_btn = QPushButton("▶️ Run Workflow")

        controls_layout.addWidget(new_btn)
        controls_layout.addWidget(save_btn)
        controls_layout.addWidget(load_btn)
        controls_layout.addWidget(test_btn)
        controls_layout.addWidget(run_btn)

        toolbox_layout.addWidget(controls_group)
        toolbox_layout.addStretch()

        # Right panel - Canvas
        canvas_panel = QFrame()
        canvas_panel.setFrameStyle(QFrame.Shape.StyledPanel)
        canvas_layout = QVBoxLayout(canvas_panel)

        # Canvas toolbar
        canvas_toolbar = QHBoxLayout()
        zoom_in_btn = QPushButton("🔍+")
        zoom_out_btn = QPushButton("🔍-")
        reset_zoom_btn = QPushButton("🎯")
        clear_btn = QPushButton("🗑️ Clear")

        canvas_toolbar.addWidget(QLabel("Canvas:"))
        canvas_toolbar.addWidget(zoom_in_btn)
        canvas_toolbar.addWidget(zoom_out_btn)
        canvas_toolbar.addWidget(reset_zoom_btn)
        canvas_toolbar.addStretch()
        canvas_toolbar.addWidget(clear_btn)

        canvas_layout.addLayout(canvas_toolbar)

        # Graphics view for workflow design
        self.workflow_scene = QGraphicsScene()
        self.workflow_scene.setSceneRect(0, 0, 1000, 800)
        self.workflow_scene.setBackgroundBrush(QBrush(QColor(25, 25, 25)))

        self.workflow_view = QGraphicsView(self.workflow_scene)
        self.workflow_view.setRenderHint(self.workflow_view.RenderHint.Antialiasing)
        canvas_layout.addWidget(self.workflow_view)

        # Add panels to splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(toolbox_panel)
        splitter.addWidget(canvas_panel)
        splitter.setSizes([250, 750])

        layout.addWidget(splitter)

        # Connect signals
        new_btn.clicked.connect(self.new_workflow)
        save_btn.clicked.connect(self.save_workflow)
        load_btn.clicked.connect(self.load_workflow_dialog)
        test_btn.clicked.connect(self.test_workflow)
        run_btn.clicked.connect(self.run_workflow)
        clear_btn.clicked.connect(self.clear_canvas)

        return widget

    def create_workflow_library(self):
        """Create the workflow library management interface."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Search and filter
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 Search:"))
        self.workflow_search = QLineEdit()
        self.workflow_search.setPlaceholderText("Search workflows...")
        search_layout.addWidget(self.workflow_search)

        self.workflow_filter = QComboBox()
        self.workflow_filter.addItems(
            ["All Workflows", "Active", "Inactive", "Templates", "Personal"]
        )
        search_layout.addWidget(self.workflow_filter)

        layout.addLayout(search_layout)

        # Workflow list
        list_group = QGroupBox("📚 Available Workflows")
        list_layout = QVBoxLayout(list_group)

        self.workflow_list = QTreeWidget()
        self.workflow_list.setHeaderLabels(
            ["Name", "Status", "Last Run", "Success Rate"]
        )
        list_layout.addWidget(self.workflow_list)

        # Workflow actions
        actions_layout = QHBoxLayout()
        edit_btn = QPushButton("✏️ Edit")
        duplicate_btn = QPushButton("📋 Duplicate")
        delete_btn = QPushButton("🗑️ Delete")
        export_btn = QPushButton("📤 Export")
        import_btn = QPushButton("📥 Import")

        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(duplicate_btn)
        actions_layout.addWidget(delete_btn)
        actions_layout.addStretch()
        actions_layout.addWidget(export_btn)
        actions_layout.addWidget(import_btn)

        list_layout.addLayout(actions_layout)
        layout.addWidget(list_group)

        # Workflow details
        details_group = QGroupBox("📋 Workflow Details")
        details_layout = QVBoxLayout(details_group)

        self.workflow_details = QTextEdit()
        self.workflow_details.setReadOnly(True)
        self.workflow_details.setMaximumHeight(150)
        details_layout.addWidget(self.workflow_details)

        layout.addWidget(details_group)

        return widget

    def create_execution_monitor(self):
        """Create the workflow execution monitoring interface."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Execution status
        status_group = QGroupBox("⚡ Execution Status")
        status_layout = QGridLayout(status_group)

        status_layout.addWidget(QLabel("Active Workflows:"), 0, 0)
        self.active_workflows_label = QLabel("0")
        status_layout.addWidget(self.active_workflows_label, 0, 1)

        status_layout.addWidget(QLabel("Queued Tasks:"), 1, 0)
        self.queued_tasks_label = QLabel("0")
        status_layout.addWidget(self.queued_tasks_label, 1, 1)

        status_layout.addWidget(QLabel("Completed Today:"), 2, 0)
        self.completed_today_label = QLabel("0")
        status_layout.addWidget(self.completed_today_label, 2, 1)

        status_layout.addWidget(QLabel("Success Rate:"), 3, 0)
        self.success_rate_label = QLabel("0%")
        status_layout.addWidget(self.success_rate_label, 3, 1)

        layout.addWidget(status_group)

        # Running workflows
        running_group = QGroupBox("🏃 Currently Running")
        running_layout = QVBoxLayout(running_group)

        self.running_workflows = QTreeWidget()
        self.running_workflows.setHeaderLabels(
            ["Workflow", "Step", "Progress", "Started", "ETA"]
        )
        running_layout.addWidget(self.running_workflows)

        # Execution controls
        exec_controls = QHBoxLayout()
        pause_btn = QPushButton("⏸️ Pause Selected")
        stop_btn = QPushButton("⏹️ Stop Selected")
        restart_btn = QPushButton("🔄 Restart Selected")

        exec_controls.addWidget(pause_btn)
        exec_controls.addWidget(stop_btn)
        exec_controls.addWidget(restart_btn)
        exec_controls.addStretch()

        running_layout.addLayout(exec_controls)
        layout.addWidget(running_group)

        # Execution history
        history_group = QGroupBox("📜 Execution History")
        history_layout = QVBoxLayout(history_group)

        self.execution_history = QTreeWidget()
        self.execution_history.setHeaderLabels(
            ["Workflow", "Status", "Started", "Duration", "Error"]
        )
        history_layout.addWidget(self.execution_history)

        layout.addWidget(history_group)

        return widget

    def create_templates(self):
        """Create the workflow templates interface."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Template categories
        categories_group = QGroupBox("📂 Template Categories")
        categories_layout = QHBoxLayout(categories_group)

        categories = [
            "All",
            "Data Processing",
            "File Management",
            "Communication",
            "System Admin",
            "Development",
        ]
        for category in categories:
            btn = QPushButton(category)
            btn.setCheckable(True)
            if category == "All":
                btn.setChecked(True)
            categories_layout.addWidget(btn)

        layout.addWidget(categories_group)

        # Template gallery
        gallery_group = QGroupBox("🎨 Template Gallery")
        gallery_layout = QVBoxLayout(gallery_group)

        # Create scroll area for templates
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)

        # Sample templates
        templates = [
            ("📁 File Organizer", "Automatically organize files by type and date"),
            ("📧 Email Processor", "Process and categorize incoming emails"),
            ("🔄 Data Sync", "Synchronize data between multiple sources"),
            ("📊 Report Generator", "Generate automated reports from data"),
            ("🔍 System Monitor", "Monitor system resources and alert on issues"),
            ("🛠️ Build Pipeline", "Automated build and deployment workflow"),
        ]

        for i, (name, desc) in enumerate(templates):
            template_frame = QFrame()
            template_frame.setFrameStyle(QFrame.Shape.Box)
            template_layout = QVBoxLayout(template_frame)

            template_layout.addWidget(QLabel(name))
            desc_label = QLabel(desc)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #cccccc; font-size: 10px;")
            template_layout.addWidget(desc_label)

            btn_layout = QHBoxLayout()
            use_btn = QPushButton("✨ Use Template")
            preview_btn = QPushButton("👁️ Preview")
            btn_layout.addWidget(use_btn)
            btn_layout.addWidget(preview_btn)
            template_layout.addLayout(btn_layout)

            row, col = divmod(i, 2)
            scroll_layout.addWidget(template_frame, row, col)

        scroll_area.setWidget(scroll_widget)
        gallery_layout.addWidget(scroll_area)
        layout.addWidget(gallery_group)

        return widget

    def create_settings(self):
        """Create the workflow settings interface."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Execution settings
        exec_group = QGroupBox("⚡ Execution Settings")
        exec_layout = QGridLayout(exec_group)

        exec_layout.addWidget(QLabel("Max Concurrent Workflows:"), 0, 0)
        self.max_concurrent = QSpinBox()
        self.max_concurrent.setRange(1, 10)
        self.max_concurrent.setValue(3)
        exec_layout.addWidget(self.max_concurrent, 0, 1)

        exec_layout.addWidget(QLabel("Default Timeout (minutes):"), 1, 0)
        self.default_timeout = QSpinBox()
        self.default_timeout.setRange(1, 1440)
        self.default_timeout.setValue(30)
        exec_layout.addWidget(self.default_timeout, 1, 1)

        exec_layout.addWidget(QLabel("Auto-retry on Failure:"), 2, 0)
        self.auto_retry = QCheckBox()
        self.auto_retry.setChecked(True)
        exec_layout.addWidget(self.auto_retry, 2, 1)

        exec_layout.addWidget(QLabel("Retry Attempts:"), 3, 0)
        self.retry_attempts = QSpinBox()
        self.retry_attempts.setRange(1, 5)
        self.retry_attempts.setValue(2)
        exec_layout.addWidget(self.retry_attempts, 3, 1)

        layout.addWidget(exec_group)

        # Notification settings
        notif_group = QGroupBox("🔔 Notifications")
        notif_layout = QVBoxLayout(notif_group)

        self.notify_success = QCheckBox("Notify on successful completion")
        self.notify_failure = QCheckBox("Notify on workflow failure")
        self.notify_timeout = QCheckBox("Notify on timeout")

        self.notify_success.setChecked(False)
        self.notify_failure.setChecked(True)
        self.notify_timeout.setChecked(True)

        notif_layout.addWidget(self.notify_success)
        notif_layout.addWidget(self.notify_failure)
        notif_layout.addWidget(self.notify_timeout)

        layout.addWidget(notif_group)

        # Logging settings
        log_group = QGroupBox("📋 Logging")
        log_layout = QGridLayout(log_group)

        log_layout.addWidget(QLabel("Log Level:"), 0, 0)
        self.log_level = QComboBox()
        self.log_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level.setCurrentText("INFO")
        log_layout.addWidget(self.log_level, 0, 1)

        log_layout.addWidget(QLabel("Max Log Files:"), 1, 0)
        self.max_log_files = QSpinBox()
        self.max_log_files.setRange(1, 100)
        self.max_log_files.setValue(10)
        log_layout.addWidget(self.max_log_files, 1, 1)

        layout.addWidget(log_group)

        # Save settings button
        save_settings_btn = QPushButton("💾 Save Settings")
        layout.addWidget(save_settings_btn)
        layout.addStretch()

        return widget

    def apply_styling(self):
        """Apply dark theme styling to the workflow builder."""
        self.setStyleSheet(
            """
            QWidget {
                background-color: #1e1e1e;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #404040;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #404040;
                color: white;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #505050;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #4CAF50;
            }
            QPushButton {
                background-color: #404040;
                color: white;
                border: 1px solid #666666;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #505050;
                border-color: #4CAF50;
            }
            QPushButton:pressed {
                background-color: #353535;
            }
            QPushButton:checked {
                background-color: #4CAF50;
                color: white;
            }
            QLineEdit, QTextEdit {
                background-color: #353535;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 8px;
                color: white;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #4CAF50;
            }
            QListWidget, QTreeWidget {
                background-color: #353535;
                border: 1px solid #666666;
                border-radius: 4px;
                alternate-background-color: #404040;
            }
            QListWidget::item, QTreeWidget::item {
                padding: 8px;
                border-bottom: 1px solid #404040;
            }
            QListWidget::item:selected, QTreeWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
            QListWidget::item:hover, QTreeWidget::item:hover {
                background-color: #505050;
            }
            QComboBox {
                background-color: #404040;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 8px;
                color: white;
            }
            QSpinBox {
                background-color: #404040;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 8px;
                color: white;
            }
            QCheckBox {
                color: white;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #666666;
                border-radius: 3px;
                background-color: #353535;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
            }
            QGraphicsView {
                border: 1px solid #666666;
                border-radius: 4px;
            }
            QScrollArea {
                border: 1px solid #666666;
                border-radius: 4px;
            }
            QFrame {
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 5px;
            }
        """
        )

    def load_workflows(self):
        """Load existing workflows from file."""
        try:
            if self.workflows_file.exists():
                with open(self.workflows_file) as f:
                    workflows = json.load(f)
                # Populate workflow library
                self.populate_workflow_library(workflows)
        except Exception as e:
            print(f"Error loading workflows: {e}")

    def populate_workflow_library(self, workflows):
        """Populate the workflow library with saved workflows."""
        self.workflow_list.clear()

        for workflow in workflows:
            item = QTreeWidgetItem(
                [
                    workflow.get("name", "Untitled"),
                    workflow.get("status", "Inactive"),
                    workflow.get("last_run", "Never"),
                    f"{workflow.get('success_rate', 0)}%",
                ]
            )
            self.workflow_list.addTopLevelItem(item)

    def add_node(self, node_type):
        """Add a new node to the workflow canvas."""
        node_count = len(
            [
                item
                for item in self.workflow_scene.items()
                if isinstance(item, WorkflowNode)
            ]
        )
        node = WorkflowNode(
            node_type,
            f"{node_type.title()} {node_count + 1}",
            100 + (node_count % 5) * 150,
            100 + (node_count // 5) * 100,
        )
        self.workflow_scene.addItem(node)

    def new_workflow(self):
        """Create a new workflow."""
        self.workflow_scene.clear()
        self.workflow_name.clear()
        self.workflow_description.clear()

    def save_workflow(self):
        """Save the current workflow."""
        # Implementation for saving workflow
        workflow_data = {
            "name": self.workflow_name.text() or "Untitled Workflow",
            "description": self.workflow_description.toPlainText(),
            "nodes": [],  # Would contain node data
            "connections": [],  # Would contain connection data
        }
        print(f"Saving workflow: {workflow_data['name']}")

    def load_workflow_dialog(self):
        """Show dialog to load a workflow."""
        # Implementation for loading workflow
        print("Loading workflow...")

    def test_workflow(self):
        """Test the current workflow."""
        print("Testing workflow...")

    def run_workflow(self):
        """Run the current workflow."""
        print("Running workflow...")

    def clear_canvas(self):
        """Clear the workflow canvas."""
        self.workflow_scene.clear()

    def autosave_workflow(self):
        """Auto-save the current workflow."""
        if self.workflow_name.text():
            print(f"Auto-saving workflow: {self.workflow_name.text()}")


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = WorkflowBuilderUI()
    window.show()
    sys.exit(app.exec())
