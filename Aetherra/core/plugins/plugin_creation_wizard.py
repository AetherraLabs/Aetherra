"""
Plugin Creation Wizard (GUI)
============================

User-friendly GUI wizard for creating plugins without requiring deep technical knowledge.
Provides step-by-step guidance and auto-validation.
"""

import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import Any, Dict, List, Optional


class PluginTemplate:
    """Plugin template for the wizard."""
    # Required plugin metadata
    name = "plugin_creation_wizard"
    description = "PluginTemplate - Auto-generated description"
    input_schema = {
        "type": "object",
        "properties": {
            "input": {"type": "string", "description": "Input data"}
        },
        "required": ["input"]
    }
    output_schema = {
        "type": "object",
        "properties": {
            "result": {"type": "string", "description": "Processing result"},
            "status": {"type": "string", "description": "Operation status"}
        }
    }
    created_by = "Plugin System Auto-Fixer"


    def __init__(
        self, name: str, description: str, template_code: str, category: str = "general"
    ):
        self.name = name
        self.description = description
        self.template_code = template_code
        self.category = category
        self.required_fields = []
        self.optional_fields = []


class PluginCreationWizard:
    """GUI wizard for plugin creation."""

    def __init__(self, parent=None):
        self.parent = parent
        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        self.root.title("Lyrixa Plugin Creation Wizard")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Plugin data
        self.plugin_data = {
            "name": "",
            "description": "",
            "author": "",
            "version": "1.0.0",
            "category": "general",
            "tags": [],
            "capabilities": [],
            "dependencies": [],
            "template": "basic",
            "custom_code": "",
            "hooks": [],
            "ui_elements": [],
        }

        # Templates
        self.templates = self._load_templates()

        # Current step
        self.current_step = 0
        self.steps = [
            "Basic Information",
            "Plugin Type & Template",
            "Capabilities & Features",
            "Dependencies & Requirements",
            "Code & Implementation",
            "UI Elements (Optional)",
            "Review & Generate",
        ]

        self._setup_ui()
        self._show_step(0)

    def _load_templates(self) -> Dict[str, PluginTemplate]:
        """Load plugin templates."""
        templates = {}

        # Basic template
        basic_template = '''"""
{description}

Author: {author}
Version: {version}
Category: {category}
"""

class {class_name}Plugin:
    """Main plugin class."""

    def __init__(self):
        self.name = "{name}"
        self.version = "{version}"
        self.description = "{description}"
        self.capabilities = {capabilities}

    def execute(self, *args, **kwargs):
        """Main plugin execution method."""
        try:
            # TODO: Implement plugin functionality
            result = self._process_data(*args, **kwargs)
            return result
        except Exception as e:
            return {{"error": str(e)}}

    def _process_data(self, *args, **kwargs):
        """Process input data."""
        # TODO: Add your implementation here
        return {{"message": "Plugin executed successfully", "data": args, "params": kwargs}}

    def get_info(self):
        """Get plugin information."""
        return {{
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "capabilities": self.capabilities,
            "author": "{author}",
            "category": "{category}",
            "tags": {tags}
        }}

    def cleanup(self):
        """Cleanup resources."""
        pass

# Plugin instance
plugin = {class_name}Plugin()

# Main function for direct execution
def main(*args, **kwargs):
    """Main function for plugin execution."""
    return plugin.execute(*args, **kwargs)

if __name__ == "__main__":
    # Test the plugin
    result = main()
    print(f"Plugin result: {{result}}")
'''

        templates["basic"] = PluginTemplate(
            "Basic Plugin",
            "Simple plugin template with execute method",
            basic_template,
            "general",
        )

        # Data processing template
        data_template = '''"""
{description}

Author: {author}
Version: {version}
Category: {category}
"""

import json
import csv
from typing import Any, Dict, List, Union

class {class_name}Plugin:
    """Data processing plugin."""

    def __init__(self):
        self.name = "{name}"
        self.version = "{version}"
        self.description = "{description}"
        self.capabilities = {capabilities}
        self.supported_formats = ["json", "csv", "txt"]

    def execute(self, data: Union[str, Dict, List], format_type: str = "auto", **kwargs):
        """Process data based on format."""
        try:
            # Auto-detect format if not specified
            if format_type == "auto":
                format_type = self._detect_format(data)

            # Process based on format
            if format_type == "json":
                return self._process_json(data, **kwargs)
            elif format_type == "csv":
                return self._process_csv(data, **kwargs)
            elif format_type == "text":
                return self._process_text(data, **kwargs)
            else:
                return {{"error": f"Unsupported format: {{format_type}}"}}

        except Exception as e:
            return {{"error": str(e)}}

    def _detect_format(self, data: Any) -> str:
        """Auto-detect data format."""
        if isinstance(data, dict) or isinstance(data, list):
            return "json"
        elif isinstance(data, str):
            if data.strip().startswith(('{', '[')):
                return "json"
            elif ',' in data and '\\n' in data:
                return "csv"
            else:
                return "text"
        return "unknown"

    def _process_json(self, data: Union[str, Dict, List], **kwargs) -> Dict:
        """Process JSON data."""
        if isinstance(data, str):
            data = json.loads(data)

        # TODO: Implement JSON processing logic
        return {{
            "status": "success",
            "format": "json",
            "processed_data": data,
            "metadata": {{"item_count": len(data) if isinstance(data, list) else 1}}
        }}

    def _process_csv(self, data: str, **kwargs) -> Dict:
        """Process CSV data."""
        import io

        reader = csv.DictReader(io.StringIO(data))
        rows = list(reader)

        # TODO: Implement CSV processing logic
        return {{
            "status": "success",
            "format": "csv",
            "processed_data": rows,
            "metadata": {{"row_count": len(rows), "columns": list(rows[0].keys()) if rows else []}}
        }}

    def _process_text(self, data: str, **kwargs) -> Dict:
        """Process text data."""
        lines = data.split('\\n')
        words = data.split()

        # TODO: Implement text processing logic
        return {{
            "status": "success",
            "format": "text",
            "processed_data": data,
            "metadata": {{
                "line_count": len(lines),
                "word_count": len(words),
                "char_count": len(data)
            }}
        }}

    def get_info(self):
        """Get plugin information."""
        return {{
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "capabilities": self.capabilities,
            "supported_formats": self.supported_formats,
            "author": "{author}",
            "category": "{category}",
            "tags": {tags}
        }}

# Plugin instance
plugin = {class_name}Plugin()

def main(data, **kwargs):
    """Main function for data processing."""
    return plugin.execute(data, **kwargs)
'''

        templates["data_processing"] = PluginTemplate(
            "Data Processing Plugin",
            "Template for data processing and transformation",
            data_template,
            "data",
        )

        # API integration template
        api_template = '''"""
{description}

Author: {author}
Version: {version}
Category: {category}
"""

import requests
import json
from typing import Dict, Any, Optional

class {class_name}Plugin:
    """API integration plugin."""

    def __init__(self):
        self.name = "{name}"
        self.version = "{version}"
        self.description = "{description}"
        self.capabilities = {capabilities}
        self.base_url = ""  # TODO: Set your API base URL
        self.headers = {{"Content-Type": "application/json"}}
        self.timeout = 30

    def execute(self, endpoint: str, method: str = "GET", data: Dict = None, **kwargs):
        """Execute API request."""
        try:
            url = f"{{self.base_url}}/{{endpoint.lstrip('/')}}"

            # Prepare request parameters
            request_params = {{
                "url": url,
                "headers": self.headers,
                "timeout": self.timeout
            }}

            # Add data for POST/PUT requests
            if method.upper() in ["POST", "PUT", "PATCH"] and data:
                request_params["json"] = data

            # Make the request
            response = requests.request(method.upper(), **request_params)
            response.raise_for_status()

            # Process response
            return self._process_response(response)

        except requests.exceptions.RequestException as e:
            return {{"error": f"API request failed: {{str(e)}}"}}
        except Exception as e:
            return {{"error": f"Plugin execution failed: {{str(e)}}"}}

    def _process_response(self, response: requests.Response) -> Dict:
        """Process API response."""
        try:
            data = response.json()
        except ValueError:
            data = response.text

        return {{
            "status": "success",
            "status_code": response.status_code,
            "data": data,
            "headers": dict(response.headers),
            "url": response.url
        }}

    def get(self, endpoint: str, params: Dict = None) -> Dict:
        """Convenience method for GET requests."""
        url = f"{{self.base_url}}/{{endpoint.lstrip('/')}}"
        response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
        return self._process_response(response)

    def post(self, endpoint: str, data: Dict) -> Dict:
        """Convenience method for POST requests."""
        return self.execute(endpoint, "POST", data)

    def put(self, endpoint: str, data: Dict) -> Dict:
        """Convenience method for PUT requests."""
        return self.execute(endpoint, "PUT", data)

    def delete(self, endpoint: str) -> Dict:
        """Convenience method for DELETE requests."""
        return self.execute(endpoint, "DELETE")

    def get_info(self):
        """Get plugin information."""
        return {{
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "capabilities": self.capabilities,
            "base_url": self.base_url,
            "author": "{author}",
            "category": "{category}",
            "tags": {tags}
        }}

# Plugin instance
plugin = {class_name}Plugin()

def main(endpoint, method="GET", data=None, **kwargs):
    """Main function for API calls."""
    return plugin.execute(endpoint, method, data, **kwargs)
'''

        templates["api_integration"] = PluginTemplate(
            "API Integration Plugin",
            "Template for API integration and HTTP requests",
            api_template,
            "integration",
        )

        return templates

    def _setup_ui(self):
        """Setup the wizard UI."""
        # Main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 20))

        self.title_label = ttk.Label(
            self.header_frame, text="Plugin Creation Wizard", font=("Arial", 16, "bold")
        )
        self.title_label.pack()

        self.subtitle_label = ttk.Label(
            self.header_frame, text="Step 1 of 7: Basic Information"
        )
        self.subtitle_label.pack()

        # Progress bar
        self.progress = ttk.Progressbar(
            self.header_frame, length=400, mode="determinate"
        )
        self.progress.pack(pady=10)
        self.progress["value"] = (1 / len(self.steps)) * 100

        # Content frame
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Navigation frame
        self.nav_frame = ttk.Frame(self.main_frame)
        self.nav_frame.pack(fill=tk.X, pady=(20, 0))

        self.prev_button = ttk.Button(
            self.nav_frame,
            text="Previous",
            command=self._previous_step,
            state=tk.DISABLED,
        )
        self.prev_button.pack(side=tk.LEFT)

        self.next_button = ttk.Button(
            self.nav_frame, text="Next", command=self._next_step
        )
        self.next_button.pack(side=tk.RIGHT)

        self.cancel_button = ttk.Button(
            self.nav_frame, text="Cancel", command=self._cancel
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=(0, 10))

    def _show_step(self, step_num: int):
        """Show a specific step of the wizard."""
        self.current_step = step_num

        # Update header
        self.subtitle_label.config(
            text=f"Step {step_num + 1} of {len(self.steps)}: {self.steps[step_num]}"
        )
        self.progress["value"] = ((step_num + 1) / len(self.steps)) * 100

        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Show appropriate step content
        if step_num == 0:
            self._show_basic_info_step()
        elif step_num == 1:
            self._show_template_step()
        elif step_num == 2:
            self._show_capabilities_step()
        elif step_num == 3:
            self._show_dependencies_step()
        elif step_num == 4:
            self._show_code_step()
        elif step_num == 5:
            self._show_ui_step()
        elif step_num == 6:
            self._show_review_step()

        # Update navigation buttons
        self.prev_button.config(state=tk.NORMAL if step_num > 0 else tk.DISABLED)
        self.next_button.config(
            text="Generate Plugin" if step_num == len(self.steps) - 1 else "Next"
        )

    def _show_basic_info_step(self):
        """Show basic information step."""
        # Plugin name
        ttk.Label(self.content_frame, text="Plugin Name:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.name_entry = ttk.Entry(self.content_frame, width=50)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)
        self.name_entry.insert(0, self.plugin_data["name"])

        # Description
        ttk.Label(self.content_frame, text="Description:").grid(
            row=1, column=0, sticky=tk.W + tk.N, pady=5
        )
        self.description_text = scrolledtext.ScrolledText(
            self.content_frame, width=50, height=4
        )
        self.description_text.grid(row=1, column=1, padx=10, pady=5)
        self.description_text.insert("1.0", self.plugin_data["description"])

        # Author
        ttk.Label(self.content_frame, text="Author:").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        self.author_entry = ttk.Entry(self.content_frame, width=50)
        self.author_entry.grid(row=2, column=1, padx=10, pady=5)
        self.author_entry.insert(0, self.plugin_data["author"])

        # Version
        ttk.Label(self.content_frame, text="Version:").grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        self.version_entry = ttk.Entry(self.content_frame, width=20)
        self.version_entry.grid(row=3, column=1, sticky=tk.W, padx=10, pady=5)
        self.version_entry.insert(0, self.plugin_data["version"])

        # Category
        ttk.Label(self.content_frame, text="Category:").grid(
            row=4, column=0, sticky=tk.W, pady=5
        )
        self.category_combo = ttk.Combobox(
            self.content_frame,
            width=47,
            values=[
                "general",
                "data",
                "text",
                "file",
                "integration",
                "utility",
                "automation",
                "analysis",
            ],
        )
        self.category_combo.grid(row=4, column=1, padx=10, pady=5)
        self.category_combo.set(self.plugin_data["category"])

    def _show_template_step(self):
        """Show template selection step."""
        ttk.Label(
            self.content_frame,
            text="Choose a plugin template:",
            font=("Arial", 12, "bold"),
        ).pack(pady=10)

        self.template_var = tk.StringVar(value=self.plugin_data["template"])

        for template_key, template in self.templates.items():
            frame = ttk.Frame(self.content_frame)
            frame.pack(fill=tk.X, pady=5, padx=20)

            ttk.Radiobutton(
                frame,
                text=template.name,
                variable=self.template_var,
                value=template_key,
            ).pack(side=tk.LEFT)

            ttk.Label(frame, text=template.description, foreground="gray").pack(
                side=tk.LEFT, padx=20
            )

    def _show_capabilities_step(self):
        """Show capabilities and features step."""
        ttk.Label(
            self.content_frame, text="Plugin Capabilities:", font=("Arial", 12, "bold")
        ).pack(pady=10)

        # Tags
        ttk.Label(self.content_frame, text="Tags (comma-separated):").pack(
            anchor=tk.W, padx=20
        )
        self.tags_entry = ttk.Entry(self.content_frame, width=60)
        self.tags_entry.pack(fill=tk.X, padx=20, pady=5)
        self.tags_entry.insert(0, ", ".join(self.plugin_data["tags"]))

        # Capabilities checkboxes
        ttk.Label(self.content_frame, text="Capabilities:").pack(
            anchor=tk.W, padx=20, pady=(10, 5)
        )

        self.capabilities_frame = ttk.Frame(self.content_frame)
        self.capabilities_frame.pack(fill=tk.X, padx=20)

        capabilities_options = [
            ("execute", "Execute/Process Data"),
            ("info", "Provide Information"),
            ("file_operations", "File Operations"),
            ("data_processing", "Data Processing"),
            ("api_integration", "API Integration"),
            ("ui_interaction", "UI Interaction"),
            ("background_task", "Background Tasks"),
            ("event_handling", "Event Handling"),
        ]

        self.capability_vars = {}
        for i, (cap_key, cap_label) in enumerate(capabilities_options):
            var = tk.BooleanVar(value=cap_key in self.plugin_data["capabilities"])
            self.capability_vars[cap_key] = var

            cb = ttk.Checkbutton(self.capabilities_frame, text=cap_label, variable=var)
            cb.grid(row=i // 2, column=i % 2, sticky=tk.W, padx=10, pady=2)

    def _show_dependencies_step(self):
        """Show dependencies step."""
        ttk.Label(
            self.content_frame,
            text="Dependencies & Requirements:",
            font=("Arial", 12, "bold"),
        ).pack(pady=10)

        # Dependencies
        ttk.Label(self.content_frame, text="Python Dependencies (one per line):").pack(
            anchor=tk.W, padx=20
        )
        self.dependencies_text = scrolledtext.ScrolledText(
            self.content_frame, width=60, height=8
        )
        self.dependencies_text.pack(fill=tk.X, padx=20, pady=5)
        self.dependencies_text.insert(
            "1.0", "\n".join(self.plugin_data["dependencies"])
        )

        # Common dependencies checkboxes
        ttk.Label(self.content_frame, text="Common Dependencies:").pack(
            anchor=tk.W, padx=20, pady=(10, 5)
        )

        common_deps_frame = ttk.Frame(self.content_frame)
        common_deps_frame.pack(fill=tk.X, padx=20)

        common_deps = [
            "requests",
            "numpy",
            "pandas",
            "beautifulsoup4",
            "pillow",
            "matplotlib",
            "flask",
            "django",
        ]

        self.common_dep_vars = {}
        for i, dep in enumerate(common_deps):
            var = tk.BooleanVar(value=dep in self.plugin_data["dependencies"])
            self.common_dep_vars[dep] = var

            cb = ttk.Checkbutton(common_deps_frame, text=dep, variable=var)
            cb.grid(row=i // 4, column=i % 4, sticky=tk.W, padx=10, pady=2)

    def _show_code_step(self):
        """Show code implementation step."""
        ttk.Label(
            self.content_frame, text="Code Implementation:", font=("Arial", 12, "bold")
        ).pack(pady=10)

        # Template preview
        template_frame = ttk.LabelFrame(self.content_frame, text="Template Preview")
        template_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        self.template_preview = scrolledtext.ScrolledText(template_frame, height=15)
        self.template_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Custom code section
        custom_frame = ttk.LabelFrame(self.content_frame, text="Custom Code (Optional)")
        custom_frame.pack(fill=tk.X, padx=20, pady=5)

        self.custom_code_text = scrolledtext.ScrolledText(custom_frame, height=5)
        self.custom_code_text.pack(fill=tk.X, padx=5, pady=5)
        self.custom_code_text.insert("1.0", self.plugin_data["custom_code"])

        # Update template preview
        self._update_template_preview()

    def _show_ui_step(self):
        """Show UI elements step."""
        ttk.Label(
            self.content_frame,
            text="UI Elements (Optional):",
            font=("Arial", 12, "bold"),
        ).pack(pady=10)

        ttk.Label(
            self.content_frame,
            text="This plugin will integrate with Lyrixa's UI automatically.",
        ).pack(padx=20)
        ttk.Label(
            self.content_frame,
            text="Advanced UI customization can be added after generation.",
        ).pack(padx=20, pady=5)

        # UI options
        ui_frame = ttk.LabelFrame(self.content_frame, text="UI Integration Options")
        ui_frame.pack(fill=tk.X, padx=20, pady=10)

        self.ui_vars = {}
        ui_options = [
            ("menu_item", "Add menu item"),
            ("toolbar_button", "Add toolbar button"),
            ("status_display", "Show status in UI"),
            ("progress_indicator", "Show progress indicator"),
            ("notification", "Send notifications"),
        ]

        for option_key, option_label in ui_options:
            var = tk.BooleanVar(value=option_key in self.plugin_data["ui_elements"])
            self.ui_vars[option_key] = var
            ttk.Checkbutton(ui_frame, text=option_label, variable=var).pack(
                anchor=tk.W, padx=10, pady=2
            )

    def _show_review_step(self):
        """Show review and generation step."""
        ttk.Label(
            self.content_frame,
            text="Review & Generate Plugin:",
            font=("Arial", 12, "bold"),
        ).pack(pady=10)

        # Summary
        summary_frame = ttk.LabelFrame(self.content_frame, text="Plugin Summary")
        summary_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        self.summary_text = scrolledtext.ScrolledText(summary_frame, height=15)
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Generate summary
        self._update_summary()

        # Output options
        output_frame = ttk.LabelFrame(self.content_frame, text="Output Options")
        output_frame.pack(fill=tk.X, padx=20, pady=5)

        ttk.Button(
            output_frame,
            text="Choose Output Directory",
            command=self._choose_output_dir,
        ).pack(side=tk.LEFT, padx=5, pady=5)

        self.output_dir_label = ttk.Label(
            output_frame, text="Output: Current directory"
        )
        self.output_dir_label.pack(side=tk.LEFT, padx=10)

        self.output_dir = os.getcwd()

    def _update_template_preview(self):
        """Update the template preview."""
        try:
            # Collect current data
            self._collect_step_data()

            # Get selected template
            template_key = self.plugin_data["template"]
            if template_key in self.templates:
                template = self.templates[template_key]

                # Format template with current data
                formatted_code = self._format_template(template.template_code)

                # Update preview
                self.template_preview.delete("1.0", tk.END)
                self.template_preview.insert("1.0", formatted_code)
        except Exception as e:
            print(f"Error updating template preview: {e}")

    def _format_template(self, template_code: str) -> str:
        """Format template with plugin data."""
        class_name = self._generate_class_name(self.plugin_data["name"])

        return template_code.format(
            name=self.plugin_data["name"],
            description=self.plugin_data["description"],
            author=self.plugin_data["author"],
            version=self.plugin_data["version"],
            category=self.plugin_data["category"],
            class_name=class_name,
            capabilities=json.dumps(self.plugin_data["capabilities"]),
            tags=json.dumps(self.plugin_data["tags"]),
        )

    def _generate_class_name(self, plugin_name: str) -> str:
        """Generate a valid Python class name from plugin name."""
        # Remove special characters and spaces, capitalize words
        import re

        clean_name = re.sub(r"[^a-zA-Z0-9\s]", "", plugin_name)
        words = clean_name.split()
        class_name = "".join(word.capitalize() for word in words)

        # Ensure it starts with a letter
        if class_name and not class_name[0].isalpha():
            class_name = "Plugin" + class_name

        return class_name or "CustomPlugin"

    def _update_summary(self):
        """Update the plugin summary."""
        self._collect_step_data()

        summary = f"""Plugin Name: {self.plugin_data["name"]}
Description: {self.plugin_data["description"]}
Author: {self.plugin_data["author"]}
Version: {self.plugin_data["version"]}
Category: {self.plugin_data["category"]}
Template: {self.plugin_data["template"]}

Tags: {", ".join(self.plugin_data["tags"])}
Capabilities: {", ".join(self.plugin_data["capabilities"])}
Dependencies: {", ".join(self.plugin_data["dependencies"])}
UI Elements: {", ".join(self.plugin_data["ui_elements"])}

Generated Code Preview:
{"-" * 40}
"""

        # Add code preview
        if self.plugin_data["template"] in self.templates:
            template = self.templates[self.plugin_data["template"]]
            formatted_code = self._format_template(template.template_code)
            summary += (
                formatted_code[:500] + "..."
                if len(formatted_code) > 500
                else formatted_code
            )

        self.summary_text.delete("1.0", tk.END)
        self.summary_text.insert("1.0", summary)

    def _collect_step_data(self):
        """Collect data from current step."""
        if self.current_step == 0:  # Basic info
            if hasattr(self, "name_entry"):
                self.plugin_data["name"] = self.name_entry.get()
                self.plugin_data["description"] = self.description_text.get(
                    "1.0", tk.END
                ).strip()
                self.plugin_data["author"] = self.author_entry.get()
                self.plugin_data["version"] = self.version_entry.get()
                self.plugin_data["category"] = self.category_combo.get()

        elif self.current_step == 1:  # Template
            if hasattr(self, "template_var"):
                self.plugin_data["template"] = self.template_var.get()

        elif self.current_step == 2:  # Capabilities
            if hasattr(self, "tags_entry"):
                tags_text = self.tags_entry.get().strip()
                self.plugin_data["tags"] = [
                    tag.strip() for tag in tags_text.split(",") if tag.strip()
                ]

                self.plugin_data["capabilities"] = [
                    cap for cap, var in self.capability_vars.items() if var.get()
                ]

        elif self.current_step == 3:  # Dependencies
            if hasattr(self, "dependencies_text"):
                deps_text = self.dependencies_text.get("1.0", tk.END).strip()
                manual_deps = [
                    dep.strip() for dep in deps_text.split("\n") if dep.strip()
                ]

                common_deps = [
                    dep for dep, var in self.common_dep_vars.items() if var.get()
                ]

                self.plugin_data["dependencies"] = list(set(manual_deps + common_deps))

        elif self.current_step == 4:  # Code
            if hasattr(self, "custom_code_text"):
                self.plugin_data["custom_code"] = self.custom_code_text.get(
                    "1.0", tk.END
                ).strip()

        elif self.current_step == 5:  # UI
            if hasattr(self, "ui_vars"):
                self.plugin_data["ui_elements"] = [
                    ui for ui, var in self.ui_vars.items() if var.get()
                ]

    def _choose_output_dir(self):
        """Choose output directory."""
        directory = filedialog.askdirectory(
            title="Choose Plugin Output Directory", initialdir=self.output_dir
        )
        if directory:
            self.output_dir = directory
            self.output_dir_label.config(text=f"Output: {directory}")

    def _previous_step(self):
        """Go to previous step."""
        if self.current_step > 0:
            self._collect_step_data()
            self._show_step(self.current_step - 1)

    def _next_step(self):
        """Go to next step or generate plugin."""
        self._collect_step_data()

        if self.current_step < len(self.steps) - 1:
            # Validate current step
            if self._validate_current_step():
                self._show_step(self.current_step + 1)
        else:
            # Generate plugin
            self._generate_plugin()

    def _validate_current_step(self) -> bool:
        """Validate current step data."""
        if self.current_step == 0:  # Basic info
            if not self.plugin_data["name"].strip():
                messagebox.showerror("Validation Error", "Plugin name is required.")
                return False
            if not self.plugin_data["description"].strip():
                messagebox.showerror(
                    "Validation Error", "Plugin description is required."
                )
                return False

        return True

    def _generate_plugin(self):
        """Generate the plugin files."""
        try:
            # Final data collection
            self._collect_step_data()

            # Validate plugin name
            if not self.plugin_data["name"].strip():
                messagebox.showerror("Error", "Plugin name is required.")
                return

            # Generate filename
            plugin_filename = (
                self.plugin_data["name"].lower().replace(" ", "_").replace("-", "_")
            )
            plugin_filename = "".join(
                c for c in plugin_filename if c.isalnum() or c == "_"
            )
            plugin_file = os.path.join(self.output_dir, f"{plugin_filename}.py")

            # Generate plugin code
            template = self.templates[self.plugin_data["template"]]
            plugin_code = self._format_template(template.template_code)

            # Add custom code if provided
            if self.plugin_data["custom_code"]:
                plugin_code += f"\n\n# Custom Code\n{self.plugin_data['custom_code']}"

            # Write plugin file
            with open(plugin_file, "w", encoding="utf-8") as f:
                f.write(plugin_code)

            # Generate metadata file
            metadata_file = os.path.join(
                self.output_dir, f"{plugin_filename}_metadata.json"
            )
            metadata = {
                "name": self.plugin_data["name"],
                "description": self.plugin_data["description"],
                "author": self.plugin_data["author"],
                "version": self.plugin_data["version"],
                "category": self.plugin_data["category"],
                "tags": self.plugin_data["tags"],
                "capabilities": self.plugin_data["capabilities"],
                "dependencies": self.plugin_data["dependencies"],
                "ui_elements": self.plugin_data["ui_elements"],
                "created_date": datetime.now().isoformat(),
                "generator": "Lyrixa Plugin Creation Wizard",
            }

            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)

            # Show success message
            messagebox.showinfo(
                "Plugin Generated Successfully!",
                f"Plugin generated successfully!\n\n"
                f"Plugin file: {plugin_file}\n"
                f"Metadata file: {metadata_file}\n\n"
                f"You can now test and use your plugin.",
            )

            # Close wizard
            self.root.destroy()

        except Exception as e:
            messagebox.showerror(
                "Generation Error", f"Failed to generate plugin: {str(e)}"
            )

    def _cancel(self):
        """Cancel wizard."""
        if messagebox.askyesno(
            "Cancel", "Are you sure you want to cancel plugin creation?"
        ):
            self.root.destroy()

    def run(self):
        """Run the wizard."""
        self.root.mainloop()


def create_plugin_wizard(parent=None):
    """Create and run the plugin creation wizard."""
    wizard = PluginCreationWizard(parent)
    wizard.run()


# Example usage
if __name__ == "__main__":
    create_plugin_wizard()
