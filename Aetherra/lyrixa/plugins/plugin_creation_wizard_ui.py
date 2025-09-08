# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Plugin Creation Wizard UI
Step-by-step plugin creation interface for non-technical users
"""


import sys

from PySide6.QtCore import Qt  # noqa: F401 (optional runtime import)
from PySide6.QtGui import QFont, QPixmap  # noqa: F401 (optional runtime import)
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWizard,
    QWizardPage,
)


class PluginCreationWizardUI(QWizard):
    """Plugin Creation Wizard UI with step-by-step guidance."""

    def __init__(self):
        super().__init__()
        self.plugin_data = {}
        self.setup_wizard()
        self.apply_styling()

    def setup_wizard(self):
        """Set up the wizard with all pages."""
        self.setWindowTitle("🧙‍♂️ Plugin Creation Wizard")
        self.setMinimumSize(800, 600)

        # Welcome page
        self.addPage(self.create_welcome_page())

        # Plugin type selection
        self.addPage(self.create_plugin_type_page())

        # Basic information
        self.addPage(self.create_basic_info_page())

        # Functionality configuration
        self.addPage(self.create_functionality_page())

        # Advanced options
        self.addPage(self.create_advanced_options_page())

        # Code generation
        self.addPage(self.create_code_generation_page())

        # Review and finish
        self.addPage(self.create_finish_page())

    def create_welcome_page(self):
        """Create the welcome page."""
        page = QWizardPage()
        page.setTitle("Welcome to the Plugin Creation Wizard")
        page.setSubTitle(
            "This wizard will guide you through creating a custom plugin for Aetherra"
        )

        layout = QVBoxLayout(page)

        # Welcome content
        welcome_text = QTextBrowser()
        welcome_text.setMaximumHeight(300)
        welcome_text.setHtml(
            """
            <div style='text-align: center; padding: 20px;'>
                <h2 style='color: #FF6D00;'>🎉 Welcome to Plugin Creation!</h2>
                <p style='font-size: 14px; line-height: 1.6;'>
                    This wizard will help you create powerful plugins for the Aetherra ecosystem
                    without requiring extensive programming knowledge.
                </p>

                <h3 style='color: #FF6D00;'>What you can create:</h3>
                <ul style='text-align: left; display: inline-block;'>
                    <li>🔧 Utility plugins for system automation</li>
                    <li>🎨 User interface components</li>
                    <li>🧠 AI-powered tools and assistants</li>
                    <li>📊 Data processing and analysis tools</li>
                    <li>🌐 Web service integrations</li>
                    <li>🎮 Interactive applications</li>
                </ul>

                <h3 style='color: #FF6D00;'>Wizard Features:</h3>
                <ul style='text-align: left; display: inline-block;'>
                    <li>✅ Step-by-step guidance</li>
                    <li>🎯 Template-based generation</li>
                    <li>🛡️ Automatic validation</li>
                    <li>📝 Built-in documentation</li>
                    <li>🧪 Testing framework integration</li>
                </ul>

                <p style='margin-top: 20px;'>
                    <strong>Ready to get started?</strong> Click "Next" to begin creating your plugin!
                </p>
            </div>
        """
        )
        layout.addWidget(welcome_text)

        # Getting started tips
        tips_group = QGroupBox("💡 Tips for Success")
        tips_layout = QVBoxLayout(tips_group)

        tips = [
            "Have a clear idea of what your plugin should do",
            "Think about who will use your plugin and how",
            "Consider what data your plugin will need",
            "Plan any external services or APIs you might use",
        ]

        for tip in tips:
            tip_label = QLabel(f"• {tip}")
            tip_label.setWordWrap(True)
            tips_layout.addWidget(tip_label)

        layout.addWidget(tips_group)

        return page

    def create_plugin_type_page(self):
        """Create the plugin type selection page."""
        page = QWizardPage()
        page.setTitle("Choose Your Plugin Type")
        page.setSubTitle("Select the type of plugin that best matches your needs")

        layout = QVBoxLayout(page)

        # Plugin type selection
        self.plugin_type_group = QButtonGroup()

        # Define plugin types with descriptions
        plugin_types = [
            {
                "id": "utility",
                "name": "🔧 Utility Plugin",
                "description": "Tools for system automation, file processing, and general utilities",
            },
            {
                "id": "interface",
                "name": "🎨 Interface Plugin",
                "description": "User interface components, widgets, and interactive elements",
            },
            {
                "id": "ai_assistant",
                "name": "🧠 AI Assistant Plugin",
                "description": "AI-powered tools, chatbots, and intelligent assistants",
            },
            {
                "id": "data_processor",
                "name": "📊 Data Processor",
                "description": "Data analysis, transformation, and visualization tools",
            },
            {
                "id": "web_service",
                "name": "🌐 Web Service Integration",
                "description": "API integrations, web scrapers, and online service connectors",
            },
            {
                "id": "game_tool",
                "name": "🎮 Interactive Tool",
                "description": "Games, simulations, and interactive applications",
            },
        ]

        for i, plugin_type in enumerate(plugin_types):
            type_group = QGroupBox()
            type_layout = QVBoxLayout(type_group)

            radio = QRadioButton(plugin_type["name"])
            radio.setProperty("plugin_type", plugin_type["id"])
            if i == 0:  # Select first option by default
                radio.setChecked(True)
            self.plugin_type_group.addButton(radio)
            type_layout.addWidget(radio)

            desc_label = QLabel(plugin_type["description"])
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet(
                "color: #CCCCCC; font-style: italic; margin-left: 20px;"
            )
            type_layout.addWidget(desc_label)

            layout.addWidget(type_group)

        # Register field for validation
        page.registerField("plugin_type", self.plugin_type_group.buttons()[0])

        return page

    def create_basic_info_page(self):
        """Create the basic information page."""
        page = QWizardPage()
        page.setTitle("Basic Plugin Information")
        page.setSubTitle("Provide essential details about your plugin")

        layout = QVBoxLayout(page)

        # Basic info form
        form_group = QGroupBox("📝 Plugin Details")
        form_layout = QGridLayout(form_group)

        # Plugin name
        form_layout.addWidget(QLabel("Plugin Name:"), 0, 0)
        self.plugin_name = QLineEdit()
        self.plugin_name.setPlaceholderText("my_awesome_plugin")
        page.registerField("plugin_name*", self.plugin_name)  # Required field
        form_layout.addWidget(self.plugin_name, 0, 1)

        # Display name
        form_layout.addWidget(QLabel("Display Name:"), 1, 0)
        self.display_name = QLineEdit()
        self.display_name.setPlaceholderText("My Awesome Plugin")
        form_layout.addWidget(self.display_name, 1, 1)

        # Version
        form_layout.addWidget(QLabel("Version:"), 2, 0)
        self.version = QLineEdit()
        self.version.setText("1.0.0")
        form_layout.addWidget(self.version, 2, 1)

        # Author
        form_layout.addWidget(QLabel("Author:"), 3, 0)
        self.author = QLineEdit()
        self.author.setPlaceholderText("Your Name")
        form_layout.addWidget(self.author, 3, 1)

        layout.addWidget(form_group)

        # Description
        desc_group = QGroupBox("📄 Description")
        desc_layout = QVBoxLayout(desc_group)

        self.description = QTextEdit()
        self.description.setMaximumHeight(120)
        self.description.setPlaceholderText(
            "Describe what your plugin does, how it works, and who should use it..."
        )
        page.registerField("description*", self.description, "plainText")
        desc_layout.addWidget(self.description)

        layout.addWidget(desc_group)

        # Category and tags
        meta_group = QGroupBox("🏷️ Categorization")
        meta_layout = QGridLayout(meta_group)

        meta_layout.addWidget(QLabel("Category:"), 0, 0)
        self.category = QComboBox()
        self.category.addItems(
            [
                "productivity",
                "utility",
                "development",
                "entertainment",
                "education",
                "business",
                "science",
                "other",
            ]
        )
        meta_layout.addWidget(self.category, 0, 1)

        meta_layout.addWidget(QLabel("Tags:"), 1, 0)
        self.tags = QLineEdit()
        self.tags.setPlaceholderText("tag1, tag2, tag3")
        meta_layout.addWidget(self.tags, 1, 1)

        layout.addWidget(meta_group)

        return page

    def create_functionality_page(self):
        """Create the functionality configuration page."""
        page = QWizardPage()
        page.setTitle("Plugin Functionality")
        page.setSubTitle("Define what your plugin will do")

        layout = QVBoxLayout(page)

        # Core functionality
        core_group = QGroupBox("⚙️ Core Functionality")
        core_layout = QVBoxLayout(core_group)

        core_layout.addWidget(
            QLabel("What should your plugin do? (Select all that apply)")
        )

        # Functionality checkboxes
        self.functionality_checks = {}
        functionalities = [
            ("process_data", "Process and transform data"),
            ("user_interface", "Provide user interface elements"),
            ("file_operations", "Read, write, or manipulate files"),
            ("network_requests", "Make network requests or API calls"),
            ("database_access", "Store or retrieve data from databases"),
            ("ai_integration", "Use AI/ML capabilities"),
            ("system_integration", "Interact with the operating system"),
            ("real_time_processing", "Process data in real-time"),
            ("scheduled_tasks", "Run scheduled or background tasks"),
            ("event_handling", "Respond to system or user events"),
        ]

        for func_id, func_desc in functionalities:
            checkbox = QCheckBox(func_desc)
            self.functionality_checks[func_id] = checkbox
            core_layout.addWidget(checkbox)

        layout.addWidget(core_group)

        # Input/Output specification
        io_group = QGroupBox("🔄 Input/Output")
        io_layout = QGridLayout(io_group)

        io_layout.addWidget(QLabel("Input Type:"), 0, 0)
        self.input_type = QComboBox()
        self.input_type.addItems(
            ["Text", "File", "JSON", "Binary", "User Input", "No Input", "Custom"]
        )
        io_layout.addWidget(self.input_type, 0, 1)

        io_layout.addWidget(QLabel("Output Type:"), 1, 0)
        self.output_type = QComboBox()
        self.output_type.addItems(
            ["Text", "File", "JSON", "Binary", "Visual Display", "No Output", "Custom"]
        )
        io_layout.addWidget(self.output_type, 1, 1)

        layout.addWidget(io_group)

        # Dependencies
        deps_group = QGroupBox("📦 Dependencies")
        deps_layout = QVBoxLayout(deps_group)

        deps_layout.addWidget(QLabel("Does your plugin need external libraries?"))

        # Common dependency checkboxes
        self.dependency_checks = {}
        dependencies = [
            ("requests", "HTTP requests (requests)"),
            ("numpy", "Numerical computing (numpy)"),
            ("pandas", "Data analysis (pandas)"),
            ("pillow", "Image processing (Pillow)"),
            ("beautifulsoup4", "Web scraping (BeautifulSoup)"),
            ("sqlite3", "Database (sqlite3 - built-in)"),
            ("tkinter", "GUI toolkit (tkinter - built-in)"),
        ]

        for dep_id, dep_desc in dependencies:
            checkbox = QCheckBox(dep_desc)
            self.dependency_checks[dep_id] = checkbox
            deps_layout.addWidget(checkbox)

        # Custom dependencies
        custom_deps_layout = QHBoxLayout()
        custom_deps_layout.addWidget(QLabel("Custom dependencies:"))
        self.custom_dependencies = QLineEdit()
        self.custom_dependencies.setPlaceholderText("package1, package2, package3")
        custom_deps_layout.addWidget(self.custom_dependencies)
        deps_layout.addLayout(custom_deps_layout)

        layout.addWidget(deps_group)

        return page

    def create_advanced_options_page(self):
        """Create the advanced options page."""
        page = QWizardPage()
        page.setTitle("Advanced Options")
        page.setSubTitle("Configure advanced plugin features (optional)")

        layout = QVBoxLayout(page)

        # Configuration options
        config_group = QGroupBox("⚙️ Configuration")
        config_layout = QVBoxLayout(config_group)

        self.config_checks = {}
        configs = [
            ("settings_ui", "Include settings/configuration UI"),
            ("error_handling", "Advanced error handling and logging"),
            ("unit_tests", "Generate unit tests"),
            ("documentation", "Auto-generate documentation"),
            ("localization", "Support for multiple languages"),
            ("plugin_api", "Expose API for other plugins"),
            ("background_service", "Run as background service"),
            ("event_system", "Integrate with event system"),
        ]

        for config_id, config_desc in configs:
            checkbox = QCheckBox(config_desc)
            self.config_checks[config_id] = checkbox
            config_layout.addWidget(checkbox)

        layout.addWidget(config_group)

        # Performance options
        perf_group = QGroupBox("🚀 Performance")
        perf_layout = QGridLayout(perf_group)

        perf_layout.addWidget(QLabel("Expected Load:"), 0, 0)
        self.expected_load = QComboBox()
        self.expected_load.addItems(["Light", "Medium", "Heavy", "Variable"])
        perf_layout.addWidget(self.expected_load, 0, 1)

        perf_layout.addWidget(QLabel("Memory Usage:"), 1, 0)
        self.memory_usage = QComboBox()
        self.memory_usage.addItems(["Low", "Medium", "High", "Variable"])
        perf_layout.addWidget(self.memory_usage, 1, 1)

        perf_layout.addWidget(QLabel("Caching:"), 2, 0)
        self.caching_enabled = QCheckBox("Enable result caching")
        perf_layout.addWidget(self.caching_enabled, 2, 1)

        layout.addWidget(perf_group)

        # Security options
        security_group = QGroupBox("🛡️ Security")
        security_layout = QVBoxLayout(security_group)

        self.security_checks = {}
        security_options = [
            ("input_validation", "Strict input validation"),
            ("output_sanitization", "Output sanitization"),
            ("permission_checks", "Permission and access checks"),
            ("secure_storage", "Secure data storage"),
            ("audit_logging", "Security audit logging"),
        ]

        for sec_id, sec_desc in security_options:
            checkbox = QCheckBox(sec_desc)
            self.security_checks[sec_id] = checkbox
            security_layout.addWidget(checkbox)

        layout.addWidget(security_group)

        return page

    def create_code_generation_page(self):
        """Create the code generation page."""
        page = QWizardPage()
        page.setTitle("Code Generation")
        page.setSubTitle("Generating your plugin code...")

        layout = QVBoxLayout(page)

        # Generation progress
        progress_group = QGroupBox("🔨 Generation Progress")
        progress_layout = QVBoxLayout(progress_group)

        self.generation_progress = QProgressBar()
        self.generation_progress.setRange(0, 100)
        progress_layout.addWidget(self.generation_progress)

        self.generation_status = QLabel("Ready to generate...")
        progress_layout.addWidget(self.generation_status)

        layout.addWidget(progress_group)

        # Generation details
        details_group = QGroupBox("📝 Generation Details")
        details_layout = QVBoxLayout(details_group)

        self.generation_details = QTextBrowser()
        self.generation_details.setMaximumHeight(200)
        details_layout.addWidget(self.generation_details)

        layout.addWidget(details_group)

        # Generated files preview
        files_group = QGroupBox("📁 Generated Files")
        files_layout = QVBoxLayout(files_group)

        self.generated_files = QListWidget()
        files_layout.addWidget(self.generated_files)

        layout.addWidget(files_group)

        return page

    def create_finish_page(self):
        """Create the finish page."""
        page = QWizardPage()
        page.setTitle("Plugin Creation Complete!")
        page.setSubTitle("Your plugin has been successfully generated")

        layout = QVBoxLayout(page)

        # Success message
        success_group = QGroupBox("🎉 Success!")
        success_layout = QVBoxLayout(success_group)

        success_text = QTextBrowser()
        success_text.setMaximumHeight(150)
        success_text.setHtml(
            """
            <div style='text-align: center; color: green;'>
                <h2>✅ Plugin Created Successfully!</h2>
                <p>Your plugin has been generated and is ready to use.</p>
            </div>
        """
        )
        success_layout.addWidget(success_text)

        layout.addWidget(success_group)

        # Summary
        summary_group = QGroupBox("📋 Plugin Summary")
        summary_layout = QVBoxLayout(summary_group)

        self.plugin_summary = QTextBrowser()
        summary_layout.addWidget(self.plugin_summary)

        layout.addWidget(summary_group)

        # Next steps
        next_steps_group = QGroupBox("🚀 Next Steps")
        next_steps_layout = QVBoxLayout(next_steps_group)

        # Action buttons
        actions_layout = QHBoxLayout()

        test_plugin_btn = QPushButton("🧪 Test Plugin")
        install_plugin_btn = QPushButton("📦 Install Plugin")
        view_code_btn = QPushButton("👁️ View Code")
        open_folder_btn = QPushButton("📁 Open Folder")

        actions_layout.addWidget(test_plugin_btn)
        actions_layout.addWidget(install_plugin_btn)
        actions_layout.addWidget(view_code_btn)
        actions_layout.addWidget(open_folder_btn)

        next_steps_layout.addLayout(actions_layout)

        # Tips
        tips_text = QLabel(
            """
💡 Tips:
• Test your plugin thoroughly before sharing
• Read the generated documentation
• Consider adding more features over time
• Share your plugin with the community
        """
        )
        tips_text.setWordWrap(True)
        next_steps_layout.addWidget(tips_text)

        layout.addWidget(next_steps_group)

        # Connect signals
        test_plugin_btn.clicked.connect(self.test_plugin)
        install_plugin_btn.clicked.connect(self.install_plugin)
        view_code_btn.clicked.connect(self.view_code)
        open_folder_btn.clicked.connect(self.open_folder)

        return page

    def apply_styling(self):
        """Apply dark theme styling to the wizard."""
        self.setStyleSheet(
            """
            QWizard {
                background-color: #1e1e1e;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QWizardPage {
                background-color: #1e1e1e;
                color: white;
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
                color: #FF6D00;
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
                border-color: #FF6D00;
            }
            QPushButton:pressed {
                background-color: #353535;
            }
            QLineEdit, QTextEdit, QTextBrowser {
                background-color: #353535;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 8px;
                color: white;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #FF6D00;
            }
            QListWidget {
                background-color: #353535;
                border: 1px solid #666666;
                border-radius: 4px;
                alternate-background-color: #404040;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #404040;
            }
            QListWidget::item:selected {
                background-color: #FF6D00;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #505050;
            }
            QProgressBar {
                border: 1px solid #666666;
                border-radius: 4px;
                text-align: center;
                color: white;
                background-color: #353535;
            }
            QProgressBar::chunk {
                background-color: #FF6D00;
                border-radius: 3px;
            }
            QComboBox {
                background-color: #404040;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 8px;
                color: white;
            }
            QCheckBox, QRadioButton {
                color: white;
                font-size: 12px;
            }
            QCheckBox::indicator, QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #666666;
                border-radius: 3px;
                background-color: #353535;
            }
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {
                background-color: #FF6D00;
            }
            QLabel {
                color: white;
            }
        """
        )

    def validateCurrentPage(self):
        """Validate current page before proceeding."""
        current_id = self.currentId()

        if current_id == 5:  # Code generation page
            self.generate_plugin_code()
            return True

        return super().validateCurrentPage()

    def generate_plugin_code(self):
        """Generate the plugin code."""
        self.generation_progress.setValue(0)
        self.generation_status.setText("Starting code generation...")

        # Simulate generation process

        from PySide6.QtCore import QTimer

        self.gen_timer = QTimer()
        self.gen_step = 0
        self.gen_timer.timeout.connect(self.update_generation)
        self.gen_timer.start(200)

    def update_generation(self):
        """Update generation progress."""
        self.gen_step += 1
        progress = min(self.gen_step * 10, 100)
        self.generation_progress.setValue(progress)

        steps = [
            "Analyzing plugin specification...",
            "Generating plugin structure...",
            "Creating main plugin class...",
            "Adding functionality methods...",
            "Implementing error handling...",
            "Generating configuration files...",
            "Creating documentation...",
            "Adding unit tests...",
            "Finalizing plugin package...",
            "Plugin generation complete!",
        ]

        if self.gen_step <= len(steps):
            self.generation_status.setText(steps[self.gen_step - 1])

            # Add details
            details = f"Step {self.gen_step}: {steps[self.gen_step - 1]}\n"
            self.generation_details.append(details)

            # Add files as they're "generated"
            if self.gen_step == 3:
                self.generated_files.addItem("📄 main_plugin.py")
            elif self.gen_step == 6:
                self.generated_files.addItem("⚙️ config.json")
            elif self.gen_step == 7:
                self.generated_files.addItem("📖 README.md")
            elif self.gen_step == 8:
                self.generated_files.addItem("🧪 test_plugin.py")
            elif self.gen_step == 9:
                self.generated_files.addItem("📦 setup.py")

        if progress >= 100:
            self.gen_timer.stop()
            self.update_plugin_summary()

    def update_plugin_summary(self):
        """Update the plugin summary on the finish page."""
        plugin_name = self.plugin_name.text() or "Unnamed Plugin"
        description = self.description.toPlainText() or "No description"

        # Get selected functionality
        selected_funcs = []
        for func_id, checkbox in self.functionality_checks.items():
            if checkbox.isChecked():
                selected_funcs.append(checkbox.text())

        # Get selected dependencies
        selected_deps = []
        for dep_id, checkbox in self.dependency_checks.items():
            if checkbox.isChecked():
                selected_deps.append(dep_id)

        summary_html = f"""
        <h3 style='color: #FF6D00;'>{plugin_name}</h3>
        <p><strong>Description:</strong> {description}</p>
        <p><strong>Version:</strong> {self.version.text()}</p>
        <p><strong>Author:</strong> {self.author.text()}</p>
        <p><strong>Category:</strong> {self.category.currentText()}</p>

        <h4 style='color: #FF6D00;'>Functionality:</h4>
        <ul>
        """

        for func in selected_funcs[:5]:  # Show first 5
            summary_html += f"<li>{func}</li>"

        if len(selected_funcs) > 5:
            summary_html += f"<li><i>...and {len(selected_funcs) - 5} more</i></li>"

        summary_html += "</ul>"

        if selected_deps:
            summary_html += "<h4 style='color: #FF6D00;'>Dependencies:</h4><ul>"
            for dep in selected_deps:
                summary_html += f"<li>{dep}</li>"
            summary_html += "</ul>"

        self.plugin_summary.setHtml(summary_html)

    def test_plugin(self):
        """Test the generated plugin."""
        QMessageBox.information(
            self,
            "Test Plugin",
            "Plugin testing functionality would be implemented here.",
        )

    def install_plugin(self):
        """Install the generated plugin."""
        QMessageBox.information(
            self,
            "Install Plugin",
            "Plugin installation functionality would be implemented here.",
        )

    def view_code(self):
        """View the generated code."""
        QMessageBox.information(
            self, "View Code", "Code viewing functionality would be implemented here."
        )

    def open_folder(self):
        """Open the plugin folder."""
        QMessageBox.information(
            self,
            "Open Folder",
            "Plugin folder opening functionality would be implemented here.",
        )


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    wizard = PluginCreationWizardUI()
    wizard.show()
    sys.exit(app.exec())
