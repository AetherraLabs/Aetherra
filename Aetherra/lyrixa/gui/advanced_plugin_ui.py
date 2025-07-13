# advanced_plugin_ui.py
# 🧠 Advanced Plugin Editor UI with AST-aware features
# Demonstrates the enhanced code editing capabilities

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from tkinter import filedialog
import json

class AdvancedPluginEditorUI:
    """
    🧠 Advanced Plugin Editor UI with AST-aware capabilities
    Demonstrates all the enhanced features for code editing accuracy
    """

    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()

        # Try to import advanced functionality
        try:
            from .plugin_editor_refactor import (
                smart_code_merge, parse_plugin_metadata, analyze_code_structure,
                get_learning_insights, generate_test_case_for_function, create_metadata_template
            )
            self.advanced_available = True
            self.status_label.config(text="✅ Advanced AST-aware editing available", foreground="green")
        except ImportError:
            self.advanced_available = False
            self.status_label.config(text="⚠️ Basic editing mode - advanced features not available", foreground="orange")

    def setup_ui(self):
        """Setup the advanced plugin editor UI"""

        # Main frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        title_label = ttk.Label(main_frame, text="🧠 Advanced Plugin Editor", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))

        # Status
        self.status_label = ttk.Label(main_frame, text="Initializing...", font=("Arial", 10))
        self.status_label.pack(pady=(0, 10))

        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Code Editor with AST Analysis
        self.setup_code_editor_tab(notebook)

        # Tab 2: Metadata Editor
        self.setup_metadata_tab(notebook)

        # Tab 3: Test Generator
        self.setup_test_generator_tab(notebook)

        # Tab 4: Learning Insights
        self.setup_insights_tab(notebook)

    def setup_code_editor_tab(self, notebook):
        """Setup the main code editor tab with AST analysis"""

        editor_frame = ttk.Frame(notebook)
        notebook.add(editor_frame, text="🧠 Smart Editor")

        # Controls frame
        controls_frame = ttk.Frame(editor_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        # Merge strategy selection
        ttk.Label(controls_frame, text="Merge Strategy:").pack(side=tk.LEFT, padx=(0, 5))
        self.strategy_var = tk.StringVar(value="intelligent")
        strategy_combo = ttk.Combobox(controls_frame, textvariable=self.strategy_var,
                                    values=["intelligent", "ast_aware", "replace", "append", "block_replace"],
                                    state="readonly", width=15)
        strategy_combo.pack(side=tk.LEFT, padx=(0, 10))

        # Buttons
        ttk.Button(controls_frame, text="📁 Load", command=self.load_code).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="💾 Save", command=self.save_code).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="🧠 Analyze", command=self.analyze_code).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="🔄 Merge", command=self.perform_merge).pack(side=tk.LEFT, padx=(0, 5))

        # Editor panes
        paned_window = ttk.PanedWindow(editor_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # Left pane - Original code
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)

        ttk.Label(left_frame, text="📝 Original Code", font=("Arial", 12, "bold")).pack()
        self.original_text = scrolledtext.ScrolledText(left_frame, height=20, width=50)
        self.original_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # Right pane - New/Modified code
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=1)

        ttk.Label(right_frame, text="✨ New/Modified Code", font=("Arial", 12, "bold")).pack()
        self.new_text = scrolledtext.ScrolledText(right_frame, height=20, width=50)
        self.new_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # Analysis results
        analysis_frame = ttk.LabelFrame(editor_frame, text="🧠 AST Analysis Results", padding=10)
        analysis_frame.pack(fill=tk.X, pady=(10, 0))

        self.analysis_text = tk.Text(analysis_frame, height=6, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(analysis_frame, orient=tk.VERTICAL, command=self.analysis_text.yview)
        self.analysis_text.configure(yscrollcommand=scrollbar.set)

        self.analysis_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_metadata_tab(self, notebook):
        """Setup metadata editing tab"""

        metadata_frame = ttk.Frame(notebook)
        notebook.add(metadata_frame, text="📋 Metadata")

        # Controls
        controls_frame = ttk.Frame(metadata_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(controls_frame, text="🔍 Parse Metadata", command=self.parse_metadata).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="📝 Generate Template", command=self.generate_template).pack(side=tk.LEFT, padx=(0, 5))

        # Metadata form
        form_frame = ttk.LabelFrame(metadata_frame, text="Plugin Metadata", padding=10)
        form_frame.pack(fill=tk.X, pady=(0, 10))

        # Plugin name
        ttk.Label(form_frame, text="Plugin Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.plugin_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.plugin_name_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        # Version
        ttk.Label(form_frame, text="Version:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.version_var = tk.StringVar(value="1.0")
        ttk.Entry(form_frame, textvariable=self.version_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        # Description
        ttk.Label(form_frame, text="Description:").grid(row=2, column=0, sticky=tk.NW, pady=2)
        self.description_text = tk.Text(form_frame, height=3, width=40)
        self.description_text.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        # Functions and classes
        ttk.Label(form_frame, text="Functions:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.functions_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.functions_var, width=40).grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        ttk.Label(form_frame, text="Classes:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.classes_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.classes_var, width=40).grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        # Generated template
        ttk.Label(metadata_frame, text="Generated Metadata Template", font=("Arial", 12, "bold")).pack(pady=(10, 5))
        self.template_text = scrolledtext.ScrolledText(metadata_frame, height=10)
        self.template_text.pack(fill=tk.BOTH, expand=True)

    def setup_test_generator_tab(self, notebook):
        """Setup test case generator tab"""

        test_frame = ttk.Frame(notebook)
        notebook.add(test_frame, text="🧪 Test Generator")

        # Function info input
        info_frame = ttk.LabelFrame(test_frame, text="Function Information", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(info_frame, text="Function Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.func_name_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.func_name_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        ttk.Label(info_frame, text="Arguments (comma-separated):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.func_args_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.func_args_var, width=40).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        ttk.Label(info_frame, text="Docstring:").grid(row=2, column=0, sticky=tk.NW, pady=2)
        self.func_docstring_text = tk.Text(info_frame, height=3, width=40)
        self.func_docstring_text.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        ttk.Button(info_frame, text="🧪 Generate Test", command=self.generate_test).grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=10)

        # Generated test
        ttk.Label(test_frame, text="Generated Test Case", font=("Arial", 12, "bold")).pack(pady=(10, 5))
        self.test_text = scrolledtext.ScrolledText(test_frame, height=15)
        self.test_text.pack(fill=tk.BOTH, expand=True)

    def setup_insights_tab(self, notebook):
        """Setup learning insights tab"""

        insights_frame = ttk.Frame(notebook)
        notebook.add(insights_frame, text="📊 Insights")

        # Controls
        controls_frame = ttk.Frame(insights_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(controls_frame, text="🔄 Refresh Insights", command=self.refresh_insights).pack(side=tk.LEFT)

        # Insights display
        self.insights_text = scrolledtext.ScrolledText(insights_frame, height=20)
        self.insights_text.pack(fill=tk.BOTH, expand=True)

        # Load initial insights
        self.refresh_insights()

    def load_code(self):
        """Load code from file"""
        filename = filedialog.askopenfilename(
            title="Load Python File",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.original_text.delete(1.0, tk.END)
                    self.original_text.insert(1.0, content)
                messagebox.showinfo("Success", f"Loaded {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    def save_code(self):
        """Save merged code to file"""
        filename = filedialog.asksaveasfilename(
            title="Save Python File",
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if filename:
            try:
                content = self.original_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(content)
                messagebox.showinfo("Success", f"Saved {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

    def analyze_code(self):
        """Analyze code structure using AST"""
        if not self.advanced_available:
            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.insert(1.0, "⚠️ Advanced analysis not available - basic mode only")
            return

        try:
            from .plugin_editor_refactor import analyze_code_structure, parse_plugin_metadata

            code = self.original_text.get(1.0, tk.END).strip()
            if not code:
                self.analysis_text.delete(1.0, tk.END)
                self.analysis_text.insert(1.0, "No code to analyze")
                return

            # Analyze structure
            analysis = analyze_code_structure(code)
            metadata = parse_plugin_metadata(code)

            # Display results
            self.analysis_text.delete(1.0, tk.END)
            result = "🧠 AST Analysis Results:\n\n"

            if analysis.get('valid_syntax', False):
                result += "✅ Syntax: Valid\n\n"

                functions = analysis.get('functions', [])
                if functions:
                    result += f"📋 Functions ({len(functions)}):\n"
                    for func in functions:
                        result += f"  • {func['name']}({', '.join(func['args'])})\n"
                        if func.get('docstring'):
                            result += f"    \"{func['docstring'][:50]}...\"\n"
                    result += "\n"

                classes = analysis.get('classes', [])
                if classes:
                    result += f"🏗️ Classes ({len(classes)}):\n"
                    for cls in classes:
                        result += f"  • {cls['name']}\n"
                        if cls.get('methods'):
                            result += f"    Methods: {', '.join(cls['methods'])}\n"
                    result += "\n"

                imports = analysis.get('imports', [])
                if imports:
                    result += f"📦 Imports ({len(imports)}):\n"
                    for imp in imports[:10]:  # Show first 10
                        result += f"  • {imp}\n"
                    if len(imports) > 10:
                        result += f"  ... and {len(imports) - 10} more\n"
                    result += "\n"

                result += f"🔢 Complexity Score: {analysis.get('complexity_score', 0)}\n\n"

            else:
                result += f"❌ Syntax Error: {analysis.get('error', 'Unknown error')}\n"
                if 'line' in analysis:
                    result += f"Line: {analysis['line']}\n"

            if metadata:
                result += "📋 Plugin Metadata:\n"
                result += f"  Name: {metadata.name}\n"
                result += f"  Version: {metadata.version}\n"
                result += f"  Functions: {', '.join(metadata.functions)}\n"
                result += f"  Classes: {', '.join(metadata.classes)}\n"
                if metadata.description:
                    result += f"  Description: {metadata.description}\n"

            self.analysis_text.insert(1.0, result)

        except Exception as e:
            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.insert(1.0, f"❌ Analysis failed: {e}")

    def perform_merge(self):
        """Perform intelligent code merge"""
        if not self.advanced_available:
            messagebox.showwarning("Warning", "Advanced merging not available - using basic append")
            original = self.original_text.get(1.0, tk.END).strip()
            new = self.new_text.get(1.0, tk.END).strip()
            if new:
                merged = original + "\n\n# Added functionality:\n" + new
                self.original_text.delete(1.0, tk.END)
                self.original_text.insert(1.0, merged)
            return

        try:
            from .plugin_editor_refactor import smart_code_merge

            original_code = self.original_text.get(1.0, tk.END).strip()
            new_code = self.new_text.get(1.0, tk.END).strip()
            strategy = self.strategy_var.get()

            if not new_code:
                messagebox.showwarning("Warning", "No new code to merge")
                return

            # Perform merge
            merged_code = smart_code_merge(original_code, new_code, strategy)

            # Update original text with merged result
            self.original_text.delete(1.0, tk.END)
            self.original_text.insert(1.0, merged_code)

            # Clear new text
            self.new_text.delete(1.0, tk.END)

            messagebox.showinfo("Success", f"Code merged successfully using {strategy} strategy")

            # Auto-analyze after merge
            self.analyze_code()

        except Exception as e:
            messagebox.showerror("Error", f"Merge failed: {e}")

    def parse_metadata(self):
        """Parse metadata from current code"""
        if not self.advanced_available:
            messagebox.showwarning("Warning", "Metadata parsing not available")
            return

        try:
            from .plugin_editor_refactor import parse_plugin_metadata

            code = self.original_text.get(1.0, tk.END).strip()
            if not code:
                messagebox.showwarning("Warning", "No code to parse")
                return

            metadata = parse_plugin_metadata(code)
            if metadata:
                self.plugin_name_var.set(metadata.name)
                self.version_var.set(metadata.version)
                self.description_text.delete(1.0, tk.END)
                self.description_text.insert(1.0, metadata.description)
                self.functions_var.set(', '.join(metadata.functions))
                self.classes_var.set(', '.join(metadata.classes))

                messagebox.showinfo("Success", "Metadata parsed successfully")
            else:
                messagebox.showwarning("Warning", "No metadata found in code")

        except Exception as e:
            messagebox.showerror("Error", f"Metadata parsing failed: {e}")

    def generate_template(self):
        """Generate metadata template"""
        try:
            if self.advanced_available:
                from .plugin_editor_refactor import create_metadata_template

                plugin_name = self.plugin_name_var.get() or "my_plugin"
                version = self.version_var.get() or "1.0"
                description = self.description_text.get(1.0, tk.END).strip()
                functions = [f.strip() for f in self.functions_var.get().split(',') if f.strip()]
                classes = [c.strip() for c in self.classes_var.get().split(',') if c.strip()]

                template = create_metadata_template(plugin_name, functions, classes, version, description)
            else:
                # Basic template
                plugin_name = self.plugin_name_var.get() or "my_plugin"
                template = f'''# @plugin: {plugin_name}
# @functions:
# @classes:
# @version: 1.0
# @description:

"""
{plugin_name} Plugin
"""

'''

            self.template_text.delete(1.0, tk.END)
            self.template_text.insert(1.0, template)

        except Exception as e:
            messagebox.showerror("Error", f"Template generation failed: {e}")

    def generate_test(self):
        """Generate test case for function"""
        try:
            func_name = self.func_name_var.get().strip()
            if not func_name:
                messagebox.showwarning("Warning", "Function name is required")
                return

            args = [arg.strip() for arg in self.func_args_var.get().split(',') if arg.strip()]
            docstring = self.func_docstring_text.get(1.0, tk.END).strip()

            function_info = {
                'name': func_name,
                'args': args,
                'docstring': docstring
            }

            if self.advanced_available:
                from .plugin_editor_refactor import generate_test_case_for_function
                test_code = generate_test_case_for_function(function_info)
            else:
                # Basic test generation
                test_code = f'''
def test_{func_name}():
    """Test case for {func_name}"""
    # TODO: Add proper test assertions
    pass
'''

            self.test_text.delete(1.0, tk.END)
            self.test_text.insert(1.0, test_code)

        except Exception as e:
            messagebox.showerror("Error", f"Test generation failed: {e}")

    def refresh_insights(self):
        """Refresh learning insights"""
        try:
            if self.advanced_available:
                from .plugin_editor_refactor import get_learning_insights
                insights = get_learning_insights()

                result = "📊 Learning Insights\n\n"

                total_edits = insights.get('total_edits', 0)
                if isinstance(insights, dict) and isinstance(total_edits, int) and total_edits > 0:
                    result += f"📈 Statistics:\n"
                    result += f"  Total Edits: {insights['total_edits']}\n"
                    result += f"  Success Rate: {insights.get('success_rate', 0):.1%}\n"
                    result += f"  Syntax Accuracy: {insights.get('syntax_accuracy', 0):.1%}\n\n"

                    if insights.get('most_successful_operation'):
                        result += f"🏆 Most Successful Operation: {insights['most_successful_operation']}\n\n"

                    operation_stats = insights.get('operation_stats', {})
                    if isinstance(operation_stats, dict):
                        result += "🔧 Operation Statistics:\n"
                        for op, stats in operation_stats.items():
                            if isinstance(stats, dict):
                                success_rate = stats.get('successful', 0) / stats.get('total', 1) if stats.get('total', 0) > 0 else 0
                                result += f"  {op}: {stats.get('successful', 0)}/{stats.get('total', 0)} ({success_rate:.1%})\n"

                else:
                    result += "No editing history available yet.\n"
                    result += "Start editing code to build learning insights!"

            else:
                result = "📊 Learning Insights\n\n⚠️ Advanced insights not available\nBasic editing mode only"

            self.insights_text.delete(1.0, tk.END)
            self.insights_text.insert(1.0, result)

        except Exception as e:
            self.insights_text.delete(1.0, tk.END)
            self.insights_text.insert(1.0, f"❌ Failed to load insights: {e}")


# Demo function to show the UI
def demo_advanced_plugin_editor():
    """Demo the advanced plugin editor"""
    root = tk.Tk()
    root.title("🧠 Advanced Plugin Editor Demo")
    root.geometry("1200x800")

    app = AdvancedPluginEditorUI(root)

    # Add some sample code
    sample_code = '''# @plugin: calculator_advanced
# @functions: add, multiply, divide
# @version: 2.1
# @description: Advanced calculator with validation

class Calculator:
    """Advanced calculator with input validation"""

    def add(self, a, b):
        """Add two numbers"""
        return a + b

    def multiply(self, a, b):
        """Multiply two numbers"""
        return a * b

def divide(a, b):
    """Divide two numbers with zero check"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
'''

    app.original_text.insert(1.0, sample_code)

    root.mainloop()


if __name__ == "__main__":
    demo_advanced_plugin_editor()
