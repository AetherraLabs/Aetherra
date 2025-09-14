"""
Document Generator Plugin GUI - PySide6 Interface for Professional Document Creation
Author: Aetherra Plugin System
Version: 1.0.0

This GUI provides a comprehensive interface for:
- Template selection and management
- Document data input with form validation
- Real-time preview capabilities
- Multi-format export options
- Custom template creation
"""

import json
import os
import sys
from datetime import datetime
from typing import Any

try:
    from PySide6.QtCore import QDate, Qt, QThread, QTime, QTimer, pyqtSignal
    from PySide6.QtGui import QFont, QPixmap, QTextOption
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QDateEdit,
        QFileDialog,
        QFormLayout,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QMainWindow,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QScrollArea,
        QSpinBox,
        QSplitter,
        QTabWidget,
        QTextEdit,
        QTimeEdit,
        QTreeWidget,
        QTreeWidgetItem,
        QVBoxLayout,
        QWidget,
    )

    PYSIDE6_AVAILABLE = True
except ImportError:
    try:
        from PySide6.QtCore import QDate, Qt, QThread, QTime, QTimer, pyqtSignal
        from PySide6.QtGui import QFont, QPixmap, QTextOption
        from PySide6.QtWidgets import (
            QApplication,
            QCheckBox,
            QComboBox,
            QDateEdit,
            QFileDialog,
            QFormLayout,
            QFrame,
            QGridLayout,
            QGroupBox,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QListWidget,
            QMainWindow,
            QMessageBox,
            QProgressBar,
            QPushButton,
            QScrollArea,
            QSpinBox,
            QSplitter,
            QTabWidget,
            QTextEdit,
            QTimeEdit,
            QTreeWidget,
            QTreeWidgetItem,
            QVBoxLayout,
            QWidget,
        )

        PYSIDE6_AVAILABLE = True
        WEBENGINE_AVAILABLE = False
    except ImportError:
        PYSIDE6_AVAILABLE = False
        WEBENGINE_AVAILABLE = False


class DocumentWorker(QThread):
    """Worker thread for document generation tasks."""

    document_generated = pyqtSignal(dict)
    progress_updated = pyqtSignal(int)
    error_occurred = pyqtSignal(str)

    def __init__(
        self, plugin, template_id: str, data: dict, output_format: str, output_path: str
    ):
        super().__init__()
        self.plugin = plugin
        self.template_id = template_id
        self.data = data
        self.output_format = output_format
        self.output_path = output_path

    def run(self):
        """Generate document in background thread."""
        try:
            self.progress_updated.emit(25)

            # Simulate processing steps
            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            self.progress_updated.emit(50)

            result = loop.run_until_complete(
                self.plugin.generate_document(
                    self.template_id, self.data, self.output_format, self.output_path
                )
            )

            self.progress_updated.emit(100)
            self.document_generated.emit(result)

        except Exception as e:
            self.error_occurred.emit(str(e))


class TemplateFieldWidget(QWidget):
    """Dynamic widget for template field input."""

    def __init__(self, field_def: dict, parent=None):
        super().__init__(parent)
        self.field_def = field_def
        self.setup_ui()

    def setup_ui(self):
        """Setup the field input widget."""
        layout = QVBoxLayout(self)

        # Field label
        label = QLabel(self.field_def["name"].replace("_", " ").title())
        if self.field_def.get("required", False):
            label.setText(f"{label.text()} *")
            label.setStyleSheet("font-weight: bold; color: #c0392b;")
        layout.addWidget(label)

        # Field input based on type
        field_type = self.field_def.get("type", "string")

        if field_type == "string":
            self.input_widget = QLineEdit()
            self.input_widget.setPlaceholderText(f"Enter {self.field_def['name']}")
        elif field_type == "email":
            self.input_widget = QLineEdit()
            self.input_widget.setPlaceholderText("email@example.com")
        elif field_type == "url":
            self.input_widget = QLineEdit()
            self.input_widget.setPlaceholderText("https://...")
        elif field_type == "text":
            self.input_widget = QTextEdit()
            self.input_widget.setMaximumHeight(100)
        elif field_type == "date":
            self.input_widget = QDateEdit()
            self.input_widget.setDate(QDate.currentDate())
            self.input_widget.setCalendarPopup(True)
        elif field_type == "time":
            self.input_widget = QTimeEdit()
            self.input_widget.setTime(QTime.currentTime())
        elif field_type == "number":
            self.input_widget = QSpinBox()
            self.input_widget.setRange(-999999, 999999)
        elif field_type == "array":
            self.input_widget = QTextEdit()
            self.input_widget.setPlaceholderText("Enter items, one per line")
            self.input_widget.setMaximumHeight(80)
        else:
            self.input_widget = QLineEdit()

        layout.addWidget(self.input_widget)

    def get_value(self) -> Any:
        """Get the current value from the input widget."""
        if isinstance(self.input_widget, QLineEdit):
            return self.input_widget.text().strip()
        elif isinstance(self.input_widget, QTextEdit):
            text = self.input_widget.toPlainText().strip()
            if self.field_def.get("type") == "array":
                return [line.strip() for line in text.split("\n") if line.strip()]
            return text
        elif isinstance(self.input_widget, QDateEdit):
            return self.input_widget.date().toString("yyyy-MM-dd")
        elif isinstance(self.input_widget, QTimeEdit):
            return self.input_widget.time().toString("HH:mm")
        elif isinstance(self.input_widget, QSpinBox):
            return self.input_widget.value()
        else:
            return ""

    def set_value(self, value: Any):
        """Set the value in the input widget."""
        if isinstance(self.input_widget, QLineEdit):
            self.input_widget.setText(str(value) if value else "")
        elif isinstance(self.input_widget, QTextEdit):
            if isinstance(value, list):
                self.input_widget.setPlainText("\n".join(str(v) for v in value))
            else:
                self.input_widget.setPlainText(str(value) if value else "")
        elif isinstance(self.input_widget, QDateEdit):
            if value:
                self.input_widget.setDate(QDate.fromString(str(value), "yyyy-MM-dd"))
        elif isinstance(self.input_widget, QTimeEdit):
            if value:
                self.input_widget.setTime(QTime.fromString(str(value), "HH:mm"))
        elif isinstance(self.input_widget, QSpinBox):
            self.input_widget.setValue(int(value) if value else 0)


class DocumentGeneratorGUI(QMainWindow):
    """Main Document Generator Plugin GUI window."""

    def __init__(self, plugin=None):
        super().__init__()
        if not PYSIDE6_AVAILABLE:
            raise ImportError("PySide6 is required for the Document Generator GUI")

        self.plugin = plugin
        self.current_template = None
        self.field_widgets = {}
        self.document_worker = None

        self.setWindowTitle("Aetherra Document Generator")
        self.setMinimumSize(1000, 700)

        # Initialize UI
        self.init_ui()
        self.load_templates()

    def init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout with splitter
        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Templates and configuration
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)

        # Right panel - Preview and export
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)

        # Set splitter sizes
        splitter.setSizes([400, 600])

        # Status bar
        self.statusBar().showMessage("Ready to generate documents")

    def create_left_panel(self) -> QWidget:
        """Create the left configuration panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Templates section
        templates_group = QGroupBox("Document Templates")
        templates_layout = QVBoxLayout(templates_group)

        # Template category filter
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(
            ["All", "Career", "Business", "Technical", "Custom"]
        )
        self.category_combo.currentTextChanged.connect(self.filter_templates)
        category_layout.addWidget(self.category_combo)
        category_layout.addStretch()
        templates_layout.addLayout(category_layout)

        # Template list
        self.template_list = QListWidget()
        self.template_list.itemClicked.connect(self.select_template)
        templates_layout.addWidget(self.template_list)

        # Template actions
        template_actions = QHBoxLayout()
        self.create_template_btn = QPushButton("Create Template")
        self.create_template_btn.clicked.connect(self.create_custom_template)
        template_actions.addWidget(self.create_template_btn)

        self.edit_template_btn = QPushButton("Edit Template")
        self.edit_template_btn.clicked.connect(self.edit_template)
        self.edit_template_btn.setEnabled(False)
        template_actions.addWidget(self.edit_template_btn)

        templates_layout.addLayout(template_actions)
        layout.addWidget(templates_group)

        # Data input section
        self.data_group = QGroupBox("Document Data")
        self.data_layout = QVBoxLayout(self.data_group)

        # Scrollable area for form fields
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.form_widget = QWidget()
        self.form_layout = QVBoxLayout(self.form_widget)
        scroll_area.setWidget(self.form_widget)

        self.data_layout.addWidget(scroll_area)
        layout.addWidget(self.data_group)

        # Export options
        export_group = QGroupBox("Export Options")
        export_layout = QGridLayout(export_group)

        export_layout.addWidget(QLabel("Format:"), 0, 0)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PDF", "Word (DOCX)", "HTML", "Markdown"])
        export_layout.addWidget(self.format_combo, 0, 1)

        export_layout.addWidget(QLabel("Output:"), 1, 0)
        output_layout = QHBoxLayout()
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setPlaceholderText("Auto-generate filename")
        output_layout.addWidget(self.output_path_edit)

        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_output_path)
        output_layout.addWidget(self.browse_btn)

        export_layout.addLayout(output_layout, 1, 1)

        # Generate button
        self.generate_btn = QPushButton("Generate Document")
        self.generate_btn.clicked.connect(self.generate_document)
        self.generate_btn.setEnabled(False)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        export_layout.addWidget(self.generate_btn, 2, 0, 1, 2)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        export_layout.addWidget(self.progress_bar, 3, 0, 1, 2)

        layout.addWidget(export_group)

        return panel

    def create_right_panel(self) -> QWidget:
        """Create the right preview panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Tab widget for preview and help
        self.preview_tabs = QTabWidget()

        # Preview tab
        preview_tab = QWidget()
        preview_layout = QVBoxLayout(preview_tab)

        # Preview controls
        preview_controls = QHBoxLayout()
        self.refresh_preview_btn = QPushButton("Refresh Preview")
        self.refresh_preview_btn.clicked.connect(self.refresh_preview)
        preview_controls.addWidget(self.refresh_preview_btn)

        self.preview_format_combo = QComboBox()
        self.preview_format_combo.addItems(["Markdown", "HTML"])
        self.preview_format_combo.currentTextChanged.connect(self.refresh_preview)
        preview_controls.addWidget(self.preview_format_combo)

        preview_controls.addStretch()
        preview_layout.addLayout(preview_controls)

        # Preview area
        if WEBENGINE_AVAILABLE:
            self.preview_area = QWebEngineView()
        else:
            self.preview_area = QTextEdit()
            self.preview_area.setReadOnly(True)
            self.preview_area.setFont(QFont("Consolas", 10))

        preview_layout.addWidget(self.preview_area)
        self.preview_tabs.addTab(preview_tab, "Preview")

        # Template info tab
        info_tab = QWidget()
        info_layout = QVBoxLayout(info_tab)

        self.template_info = QTextEdit()
        self.template_info.setReadOnly(True)
        self.template_info.setFont(QFont("Arial", 10))
        info_layout.addWidget(self.template_info)

        self.preview_tabs.addTab(info_tab, "Template Info")

        # Help tab
        help_tab = QWidget()
        help_layout = QVBoxLayout(help_tab)

        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <h3>Document Generator Help</h3>
        <h4>Getting Started:</h4>
        <ol>
        <li>Select a template from the left panel</li>
        <li>Fill in the required fields (marked with *)</li>
        <li>Choose your output format</li>
        <li>Click "Generate Document"</li>
        </ol>

        <h4>Templates:</h4>
        <ul>
        <li><b>Professional Resume:</b> Modern CV with experience, education, and skills</li>
        <li><b>Meeting Notes:</b> Structured notes with agenda and action items</li>
        <li><b>Technical Report:</b> Comprehensive project reports</li>
        </ul>

        <h4>Supported Formats:</h4>
        <ul>
        <li><b>PDF:</b> Professional documents for printing and sharing</li>
        <li><b>Word (DOCX):</b> Editable documents for Microsoft Word</li>
        <li><b>HTML:</b> Web-compatible format with styling</li>
        <li><b>Markdown:</b> Plain text format for developers</li>
        </ul>

        <h4>Tips:</h4>
        <ul>
        <li>Use the preview to see how your document will look</li>
        <li>Required fields are marked with a red asterisk (*)</li>
        <li>For array fields, enter one item per line</li>
        <li>Dates should be in YYYY-MM-DD format</li>
        </ul>
        """)
        help_layout.addWidget(help_text)

        self.preview_tabs.addTab(help_tab, "Help")

        layout.addWidget(self.preview_tabs)
        return panel

    def load_templates(self):
        """Load available templates from the plugin."""
        if not self.plugin:
            return

        try:
            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            result = loop.run_until_complete(self.plugin.list_templates())

            if result["status"] == "success":
                self.templates = {t["id"]: t for t in result["data"]["templates"]}
                self.update_template_list()
            else:
                QMessageBox.warning(
                    self, "Error", f"Failed to load templates: {result['message']}"
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load templates: {e}")

    def update_template_list(self):
        """Update the template list display."""
        self.template_list.clear()

        category_filter = self.category_combo.currentText().lower()

        for template_id, template in self.templates.items():
            if category_filter == "all" or template["category"] == category_filter:
                item_text = f"{template['name']} - {template['description'][:50]}..."
                self.template_list.addItem(item_text)
                self.template_list.item(self.template_list.count() - 1).setData(
                    Qt.UserRole, template_id
                )

    def filter_templates(self):
        """Filter templates by category."""
        self.update_template_list()

    def select_template(self, item):
        """Handle template selection."""
        template_id = item.data(Qt.UserRole)
        if template_id not in self.templates:
            return

        self.current_template = self.templates[template_id]
        self.create_input_form()
        self.update_template_info()
        self.generate_btn.setEnabled(True)
        self.edit_template_btn.setEnabled(True)

    def create_input_form(self):
        """Create input form based on template fields."""
        # Clear existing form
        for widget in self.field_widgets.values():
            widget.setParent(None)
        self.field_widgets.clear()

        if not self.current_template:
            return

        # Create form fields
        for field in self.current_template["fields"]:
            if field["type"] == "object":
                # Create group for object fields
                group = QGroupBox(field["name"].replace("_", " ").title())
                group_layout = QVBoxLayout(group)

                for sub_field in field.get("fields", []):
                    widget = TemplateFieldWidget(sub_field)
                    group_layout.addWidget(widget)
                    self.field_widgets[f"{field['name']}.{sub_field['name']}"] = widget

                self.form_layout.addWidget(group)
            else:
                # Create widget for simple field
                widget = TemplateFieldWidget(field)
                self.form_layout.addWidget(widget)
                self.field_widgets[field["name"]] = widget

        # Add stretch to push fields to top
        self.form_layout.addStretch()

    def update_template_info(self):
        """Update template information display."""
        if not self.current_template:
            return

        info_html = f"""
        <h3>{self.current_template["name"]}</h3>
        <p><b>Category:</b> {self.current_template["category"].title()}</p>
        <p><b>Description:</b> {self.current_template["description"]}</p>
        <p><b>Author:</b> {self.current_template["author"]}</p>
        <p><b>Version:</b> {self.current_template["version"]}</p>
        <p><b>Output Formats:</b> {", ".join(self.current_template["output_formats"])}</p>

        <h4>Required Fields:</h4>
        <ul>
        """

        for field in self.current_template["fields"]:
            if field.get("required", False):
                info_html += f"<li>{field['name'].replace('_', ' ').title()}</li>"

        info_html += "</ul>"

        self.template_info.setHtml(info_html)

    def collect_form_data(self) -> dict[str, Any]:
        """Collect data from form fields."""
        data = {}

        for field_path, widget in self.field_widgets.items():
            value = widget.get_value()

            # Handle nested object fields
            if "." in field_path:
                obj_name, field_name = field_path.split(".", 1)
                if obj_name not in data:
                    data[obj_name] = {}
                data[obj_name][field_name] = value
            else:
                data[field_path] = value

        return data

    def refresh_preview(self):
        """Refresh the document preview."""
        if not self.current_template:
            return

        try:
            data = self.collect_form_data()

            # Generate preview content
            if self.plugin:
                import asyncio

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                content = self.plugin.template_engine.render_template(
                    self.current_template["id"], data
                )

                preview_format = self.preview_format_combo.currentText().lower()

                if WEBENGINE_AVAILABLE and preview_format == "html":
                    # Convert markdown to HTML for web view
                    try:
                        import markdown

                        html_content = markdown.markdown(content)
                        self.preview_area.setHtml(html_content)
                    except ImportError:
                        self.preview_area.setHtml(f"<pre>{content}</pre>")
                else:
                    # Show as plain text
                    if hasattr(self.preview_area, "setPlainText"):
                        self.preview_area.setPlainText(content)
                    else:
                        self.preview_area.setHtml(f"<pre>{content}</pre>")

        except Exception as e:
            if hasattr(self.preview_area, "setPlainText"):
                self.preview_area.setPlainText(f"Preview Error: {e}")
            else:
                self.preview_area.setHtml(f"<p>Preview Error: {e}</p>")

    def browse_output_path(self):
        """Browse for output file path."""
        format_ext = {
            "PDF": "pdf",
            "Word (DOCX)": "docx",
            "HTML": "html",
            "Markdown": "md",
        }

        current_format = self.format_combo.currentText()
        ext = format_ext.get(current_format, "pdf")

        filename, _ = QFileDialog.getSaveFileName(
            self,
            f"Save {current_format} Document",
            f"document.{ext}",
            f"{current_format} Files (*.{ext});;All Files (*)",
        )

        if filename:
            self.output_path_edit.setText(filename)

    def generate_document(self):
        """Generate the document."""
        if not self.current_template or not self.plugin:
            return

        # Validate required fields
        data = self.collect_form_data()
        missing_fields = self._validate_required_fields(data)

        if missing_fields:
            QMessageBox.warning(
                self,
                "Missing Required Fields",
                f"Please fill in the following required fields:\n\n• "
                + "\n• ".join(missing_fields),
            )
            return

        # Prepare generation parameters
        format_map = {
            "PDF": "pdf",
            "Word (DOCX)": "docx",
            "HTML": "html",
            "Markdown": "markdown",
        }

        output_format = format_map[self.format_combo.currentText()]
        output_path = self.output_path_edit.text().strip()

        # Start generation in worker thread
        self.document_worker = DocumentWorker(
            self.plugin, self.current_template["id"], data, output_format, output_path
        )

        self.document_worker.document_generated.connect(self.on_document_generated)
        self.document_worker.progress_updated.connect(self.progress_bar.setValue)
        self.document_worker.error_occurred.connect(self.on_generation_error)

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.generate_btn.setEnabled(False)
        self.statusBar().showMessage("Generating document...")

        self.document_worker.start()

    def on_document_generated(self, result: dict):
        """Handle document generation completion."""
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)

        if result["status"] == "success":
            output_path = result["data"]["output_path"]
            QMessageBox.information(
                self,
                "Document Generated",
                f"Document successfully generated:\n{output_path}",
            )
            self.statusBar().showMessage(
                f"Document saved: {os.path.basename(output_path)}"
            )
        else:
            QMessageBox.critical(
                self,
                "Generation Failed",
                f"Failed to generate document:\n{result['message']}",
            )
            self.statusBar().showMessage("Generation failed")

    def on_generation_error(self, error: str):
        """Handle generation error."""
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)

        QMessageBox.critical(self, "Generation Error", f"An error occurred:\n{error}")
        self.statusBar().showMessage("Generation failed")

    def create_custom_template(self):
        """Open custom template creation dialog."""
        QMessageBox.information(
            self,
            "Custom Templates",
            "Custom template creation will be available in a future update.\n\n"
            "For now, you can modify existing templates or create templates "
            "programmatically using the plugin API.",
        )

    def edit_template(self):
        """Open template editing dialog."""
        QMessageBox.information(
            self,
            "Template Editing",
            "Template editing will be available in a future update.\n\n"
            "Current template structure can be viewed in the Template Info tab.",
        )

    def _validate_required_fields(self, data: dict[str, Any]) -> list[str]:
        """Validate that required fields are filled."""
        missing = []

        def check_field(field_def: dict, field_data: Any, prefix: str = ""):
            field_name = field_def["name"]
            display_name = prefix + field_name.replace("_", " ").title()

            if field_def.get("required", False):
                if field_def["type"] == "object":
                    obj_data = field_data.get(field_name, {}) if field_data else {}
                    for sub_field in field_def.get("fields", []):
                        check_field(sub_field, obj_data, f"{display_name} > ")
                else:
                    value = field_data.get(field_name) if field_data else None
                    if not value or (isinstance(value, str) and not value.strip()):
                        missing.append(display_name)

        if self.current_template:
            for field in self.current_template["fields"]:
                check_field(field, data)

        return missing


def create_document_generator_gui(plugin=None):
    """Factory function to create the Document Generator GUI."""
    if not PYSIDE6_AVAILABLE:
        return None

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    return DocumentGeneratorGUI(plugin)


# Standalone execution for testing
if __name__ == "__main__":
    if PYSIDE6_AVAILABLE:
        app = QApplication(sys.argv)
        window = DocumentGeneratorGUI()
        window.show()
        sys.exit(app.exec())
    else:
        print("PySide6 is not available. GUI cannot be started.")
