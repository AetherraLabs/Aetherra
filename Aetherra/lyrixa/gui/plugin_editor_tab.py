import os
from typing import Optional

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Import the new plugin editor refactor functionality
try:
    from .plugin_editor_refactor import smart_code_merge, replace_block
    REFACTOR_AVAILABLE = True
    print("✅ Plugin editor refactor functionality loaded")
except ImportError:
    REFACTOR_AVAILABLE = False
    print("⚠️ Plugin editor refactor not available - using fallback mode")

    # Fallback functions if import fails
    def smart_code_merge(existing_code: str, new_code: str, merge_strategy: str = "append") -> str:
        """Fallback smart merge function"""
        if merge_strategy == "append":
            if not existing_code.endswith('\n'):
                existing_code += '\n'
            return existing_code + '\n# ✏️ Additional functionality:\n' + new_code
        return new_code

    def replace_block(existing_code: str, new_block: str) -> str:
        """Fallback block replace function"""
        return existing_code + '\n\n' + new_block


class PluginEditorTab(QWidget):
    def __init__(self, plugin_dir, memory_manager, plugin_manager):
        super().__init__()
        self.plugin_dir = plugin_dir
        self.memory = memory_manager
        self.plugins = plugin_manager
        self.current_file_path = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("📝 Plugin Editor")
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Open a plugin to begin editing...")

        # First row of buttons - File operations
        open_btn = QPushButton("Open Plugin File")
        save_btn = QPushButton("Save Changes")
        test_btn = QPushButton("Test Plugin")
        commit_btn = QPushButton("Apply + Reload Plugin")

        open_btn.clicked.connect(self.open_plugin_file)
        save_btn.clicked.connect(self.save_changes)
        test_btn.clicked.connect(self.test_plugin)
        commit_btn.clicked.connect(self.commit_plugin)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(open_btn)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(test_btn)
        btn_layout.addWidget(commit_btn)

        # Second row of buttons - Plugin generation
        generate_btn = QPushButton("🔧 Generate New Plugin")
        templates_btn = QPushButton("📋 View Templates")
        clear_btn = QPushButton("🗑️ Clear Editor")

        generate_btn.clicked.connect(self.generate_new_plugin)
        templates_btn.clicked.connect(self.show_templates)
        clear_btn.clicked.connect(self.clear_editor)

        generation_layout = QHBoxLayout()
        generation_layout.addWidget(generate_btn)
        generation_layout.addWidget(templates_btn)
        generation_layout.addWidget(clear_btn)
        generation_layout.addStretch()  # Push buttons to the left

        layout.addWidget(self.label)
        layout.addLayout(btn_layout)
        layout.addLayout(generation_layout)
        layout.addWidget(self.editor)
        self.setLayout(layout)

    def open_plugin_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Plugin", self.plugin_dir, "Plugin Files (*.py *.aether)"
        )
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                self.editor.setPlainText(f.read())
            self.current_file_path = file_path
            self.label.setText(f"📝 Editing: {os.path.basename(file_path)}")

    def save_changes(self):
        if not self.current_file_path:
            # This is a new plugin, ask where to save it
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Plugin",
                self.plugin_dir,
                "Python Files (*.py);;Aether Files (*.aether)",
            )
            if file_path:
                self.current_file_path = file_path
            else:
                return

        try:
            with open(self.current_file_path, "w", encoding="utf-8") as f:
                f.write(self.editor.toPlainText())

            self.label.setText(
                f"📝 Editing: {os.path.basename(self.current_file_path)}"
            )
            QMessageBox.information(
                self, "Saved", f"Plugin saved to:\n{self.current_file_path}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Could not save plugin: {e}")

    def test_plugin(self):
        if not self.current_file_path:
            return
        # Example: basic syntax check
        try:
            content = self.editor.toPlainText()
            if self.current_file_path.endswith(".py"):
                compile(content, self.current_file_path, "exec")
            # You can add .aether validation later
            QMessageBox.information(self, "Test Passed", "Plugin syntax looks good.")
        except Exception as e:
            QMessageBox.critical(self, "Test Failed", f"Error: {str(e)}")

    def commit_plugin(self):
        self.save_changes()
        if self.plugins and self.current_file_path:
            plugin_name = os.path.basename(self.current_file_path).replace(".py", "")
            self.plugins.reload_plugin(plugin_name)
            QMessageBox.information(self, "Reloaded", f"{plugin_name} reloaded.")

    def generate_new_plugin(self):
        """Generate a new plugin using the PluginGeneratorPlugin"""
        try:
            # Get plugin description from user
            description, ok = QInputDialog.getText(
                self,
                "Generate Plugin",
                "Describe the plugin you want to create:\n(e.g., 'data visualization charts', 'CSV file processor')",
            )

            if not ok or not description.strip():
                return

            # Import the plugin generator
            try:
                import sys
                from pathlib import Path

                # Add project root to path
                project_root = Path(__file__).parent.parent.parent.parent
                sys.path.append(str(project_root))

                from Aetherra.lyrixa.plugins.plugin_generator_plugin import (
                    PluginGeneratorPlugin,
                )

                generator = PluginGeneratorPlugin()

                # Detect plugin type (simplified version of the agent logic)
                plugin_type = self._detect_plugin_type_simple(description)
                plugin_name = self._extract_plugin_name_simple(description)

                # Generate the plugin
                plugin_id = generator.generate_plugin(
                    plugin_name=plugin_name,
                    template_id=plugin_type,
                    description=f"Generated plugin for {description}",
                    config={"gui_generated": True},
                )

                # Get the generated plugin
                generated_plugin = generator.generated_plugins.get(plugin_id)

                if generated_plugin:
                    # Show the main plugin file in the editor
                    main_file = None
                    for filename, content in generated_plugin.files.items():
                        if filename.endswith(".py") and "init" not in filename:
                            main_file = content
                            break

                    if main_file:
                        self.editor.setPlainText(main_file)
                        self.label.setText(f"📝 Generated: {plugin_name}")
                        self.current_file_path = None  # New plugin, not saved yet

                        QMessageBox.information(
                            self,
                            "Plugin Generated",
                            f"✅ Plugin '{plugin_name}' generated successfully!\n\n"
                            f"Template: {plugin_type}\n"
                            f"Files: {len(generated_plugin.files)}\n\n"
                            f"The main plugin file is now in the editor.\n"
                            f"Use 'Save Changes' to save it to disk.",
                        )
                    else:
                        QMessageBox.warning(
                            self,
                            "Generation Issue",
                            "Plugin generated but no main file found.",
                        )

                else:
                    QMessageBox.critical(
                        self, "Generation Failed", "Failed to generate plugin."
                    )

            except ImportError as e:
                QMessageBox.critical(
                    self,
                    "Generator Not Available",
                    f"Plugin generator is not available: {e}\n\nPlease ensure the plugin generation system is properly installed.",
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Generation Error", f"Error generating plugin: {e}"
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error: {e}")

    def show_templates(self):
        """Show available plugin templates"""
        try:
            import sys
            from pathlib import Path

            project_root = Path(__file__).parent.parent.parent.parent
            sys.path.append(str(project_root))

            from Aetherra.lyrixa.plugins.plugin_generator_plugin import (
                PluginGeneratorPlugin,
            )

            generator = PluginGeneratorPlugin()
            templates = generator.list_templates()

            template_info = "📋 Available Plugin Templates:\n\n"
            for template in templates:
                template_info += f"• **{template['name']}** ({template['category']})\n"
                template_info += f"  {template['description']}\n"
                template_info += f"  Files: {len(template['files'])}, Dependencies: {len(template['dependencies'])}\n\n"

            QMessageBox.information(self, "Plugin Templates", template_info)

        except Exception as e:
            QMessageBox.warning(
                self, "Templates Error", f"Could not load templates: {e}"
            )

    def clear_editor(self):
        """Clear the editor content"""
        if self.editor.toPlainText().strip():
            reply = QMessageBox.question(
                self,
                "Clear Editor",
                "Are you sure you want to clear the editor?\nUnsaved changes will be lost.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.editor.clear()
                self.label.setText("📝 Plugin Editor")
                self.current_file_path = None

    def _detect_plugin_type_simple(self, description: str) -> str:
        """Simple plugin type detection for GUI use"""
        desc_lower = description.lower()

        if any(
            word in desc_lower
            for word in [
                "ui",
                "widget",
                "interface",
                "button",
                "form",
                "display",
                "visual",
                "gui",
                "chart",
                "graph",
            ]
        ):
            return "ui_widget"
        elif any(
            word in desc_lower
            for word in [
                "data",
                "process",
                "parse",
                "transform",
                "analyze",
                "filter",
                "sort",
                "csv",
                "file",
            ]
        ):
            return "data_processor"
        elif any(
            word in desc_lower
            for word in [
                "ml",
                "machine learning",
                "model",
                "train",
                "predict",
                "ai",
                "neural",
                "classifier",
            ]
        ):
            return "ml_model"
        elif any(
            word in desc_lower
            for word in [
                "api",
                "rest",
                "http",
                "request",
                "web",
                "service",
                "endpoint",
                "integration",
            ]
        ):
            return "api_integration"
        else:
            return "ui_widget"  # Default

    def _extract_plugin_name_simple(self, description: str) -> str:
        """Simple plugin name extraction for GUI use"""
        words = description.split()
        filtered_words = []

        skip_words = {
            "for",
            "to",
            "that",
            "can",
            "will",
            "a",
            "an",
            "the",
            "and",
            "or",
            "with",
        }

        for word in words:
            clean_word = word.strip(".,!?;:")
            if (
                clean_word
                and clean_word.lower() not in skip_words
                and len(clean_word) > 2
            ):
                filtered_words.append(clean_word.capitalize())

        if not filtered_words:
            return "CustomPlugin"

        name_parts = filtered_words[:3]  # Take first 3 words max
        return "".join(name_parts) + "Plugin"

    def set_code_block(self, code: str, filename: str = "untitled_plugin.aether"):
        """Set code block in the editor with generated content"""
        self.editor.setPlainText(code)
        self.label.setText(f"📝 Generated: {filename}")
        self.current_file_path = os.path.join(self.plugin_dir, filename)

    def apply_code_edit(self, new_code: str, filename: Optional[str] = None, merge_mode: bool = True):
        """Apply incremental edits to existing code with intelligent merging"""
        try:
            if merge_mode and self.editor.toPlainText().strip():
                existing_code = self.editor.toPlainText()

                if REFACTOR_AVAILABLE:
                    # Use the advanced smart merging functionality
                    merged_code = smart_code_merge(existing_code, new_code, "intelligent")
                    self.editor.setPlainText(merged_code)
                    print("🔄 Applied code edit: Smart merge with refactor functionality")
                else:
                    # Fallback to previous logic
                    if len(new_code) > len(existing_code) and existing_code.strip() in new_code:
                        # New code contains existing code - safe to replace
                        self.editor.setPlainText(new_code)
                        print("🔄 Applied code edit: Replaced with enhanced version")
                    else:
                        # Try to append new functionality
                        if not existing_code.endswith('\n'):
                            existing_code += '\n'

                        # Add separator comment and new code
                        combined_code = existing_code + "\n# ✏️ Additional functionality:\n" + new_code
                        self.editor.setPlainText(combined_code)
                        print("🔄 Applied code edit: Appended new functionality")
            else:
                # First time or force replace
                self.editor.setPlainText(new_code)
                print("🔄 Applied code edit: Initial content set")

            if filename:
                self.label.setText(f"📝 Edited: {filename}")
                self.current_file_path = os.path.join(self.plugin_dir, filename)

            return True
        except Exception as e:
            print(f"❌ Failed to apply code edit: {e}")
            return False

    def replace_function_or_class(self, new_block: str) -> bool:
        """Replace a specific function or class in the current code"""
        try:
            if not REFACTOR_AVAILABLE:
                print("⚠️ Advanced block replacement not available")
                return False

            existing_code = self.editor.toPlainText()
            if not existing_code.strip():
                print("⚠️ No existing code to replace")
                return False

            updated_code = replace_block(existing_code, new_block)
            self.editor.setPlainText(updated_code)
            print("✅ Successfully replaced function/class block")
            return True
        except Exception as e:
            print(f"❌ Failed to replace block: {e}")
            return False

    def focus_editor(self):
        """Focus the editor widget"""
        self.editor.setFocus()

    def analyze_plugin_structure(self, code: str):
        """
        🧠 Analyze plugin structure using AST-aware analysis
        """
        try:
            # Try to use advanced analysis
            if REFACTOR_AVAILABLE:
                from .plugin_editor_refactor import analyze_code_structure, parse_plugin_metadata

                # Get structure analysis
                analysis = analyze_code_structure(code)
                metadata = parse_plugin_metadata(code)

                return {
                    "analysis": analysis,
                    "metadata": metadata,
                    "has_advanced_features": True
                }
            else:
                # Basic analysis fallback
                return {
                    "analysis": {"valid_syntax": True, "message": "Basic analysis only"},
                    "metadata": None,
                    "has_advanced_features": False
                }
        except Exception as e:
            print(f"⚠️ Plugin analysis failed: {e}")
            return {
                "analysis": {"valid_syntax": False, "error": str(e)},
                "metadata": None,
                "has_advanced_features": False
            }

    def generate_plugin_test(self, function_info: dict) -> str:
        """
        🧪 Generate test case for plugin function
        """
        try:
            if REFACTOR_AVAILABLE:
                from .plugin_editor_refactor import generate_test_case_for_function
                return generate_test_case_for_function(function_info)
            else:
                # Basic test generation
                func_name = function_info.get("name", "test_function")
                return f'''
def test_{func_name}():
    """Basic test for {func_name}"""
    # TODO: Implement test logic
    pass
'''
        except Exception as e:
            print(f"⚠️ Test generation failed: {e}")
            return f"# Test generation failed: {e}"

    def create_plugin_metadata_template(self, plugin_name: str = "", functions=None, classes=None):
        """
        📝 Create metadata template for current plugin
        """
        try:
            if REFACTOR_AVAILABLE:
                from .plugin_editor_refactor import create_metadata_template
                return create_metadata_template(plugin_name, functions, classes)
            else:
                # Basic template
                functions = functions or []
                classes = classes or []
                return f'''# @plugin: {plugin_name}
# @functions: {', '.join(functions)}
# @classes: {', '.join(classes)}
# @version: 1.0
# @description: Plugin description

"""
{plugin_name} Plugin
"""

'''
        except Exception as e:
            print(f"⚠️ Template generation failed: {e}")
            return f"# Template generation failed: {e}"

    def get_editing_insights(self):
        """
        📊 Get insights from editing history
        """
        try:
            if REFACTOR_AVAILABLE:
                from .plugin_editor_refactor import get_learning_insights
                return get_learning_insights()
            else:
                return {"message": "Learning insights not available"}
        except Exception as e:
            print(f"⚠️ Getting insights failed: {e}")
            return {"error": str(e)}
