#!/usr/bin/env python3
"""
🎨 LYRIXA PLUGIN VERSION CONTROL GUI
===================================

GUI interface for plugin version control and rollback system.
Provides intuitive access to:
- Version history viewing
- Diff comparison
- Rollback operations
- Snapshot management

Integrates seamlessly with the main Lyrixa GUI.
"""

import os
import tempfile
import tkinter as tk
import webbrowser
from datetime import datetime
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import List

from .plugin_version_control import PluginSnapshot, PluginVersionControl


class PluginVersionHistoryGUI:
    """GUI for managing plugin version history"""

    def __init__(self, parent, version_control: PluginVersionControl):
        self.parent = parent
        self.version_control = version_control
        self.current_plugin = None
        self.snapshots: List[PluginSnapshot] = []

        # Create main window
        self.window = tk.Toplevel(parent)
        self.window.title("Plugin Version History")
        self.window.geometry("900x700")
        self.window.resizable(True, True)

        self._create_widgets()
        self._setup_layout()

    def _create_widgets(self):
        """Create all GUI widgets"""
        # Plugin selection frame
        self.plugin_frame = ttk.Frame(self.window)

        ttk.Label(self.plugin_frame, text="Plugin:").pack(side=tk.LEFT, padx=5)

        self.plugin_var = tk.StringVar()
        self.plugin_combo = ttk.Combobox(
            self.plugin_frame, textvariable=self.plugin_var, width=30, state="readonly"
        )
        self.plugin_combo.pack(side=tk.LEFT, padx=5)
        self.plugin_combo.bind("<<ComboboxSelected>>", self._on_plugin_selected)

        self.refresh_btn = ttk.Button(
            self.plugin_frame, text="Refresh", command=self._refresh_plugins
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        # Notebook for tabs
        self.notebook = ttk.Notebook(self.window)

        # History tab
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="Version History")

        # Diff tab
        self.diff_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.diff_frame, text="Diff Viewer")

        # Stats tab
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")

        self._create_history_tab()
        self._create_diff_tab()
        self._create_stats_tab()

    def _create_history_tab(self):
        """Create version history tab"""
        # Toolbar
        toolbar = ttk.Frame(self.history_frame)

        self.rollback_btn = ttk.Button(
            toolbar, text="🔁 Rollback", command=self._rollback_selected
        )
        self.rollback_btn.pack(side=tk.LEFT, padx=2)

        self.export_btn = ttk.Button(
            toolbar, text="📥 Export", command=self._export_selected
        )
        self.export_btn.pack(side=tk.LEFT, padx=2)

        self.delete_btn = ttk.Button(
            toolbar, text="🗑️ Delete", command=self._delete_selected
        )
        self.delete_btn.pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)

        self.cleanup_btn = ttk.Button(
            toolbar, text="🧹 Cleanup Old", command=self._cleanup_old_snapshots
        )
        self.cleanup_btn.pack(side=tk.LEFT, padx=2)

        toolbar.pack(fill=tk.X, padx=5, pady=5)

        # Treeview for version list
        columns = ("Timestamp", "Confidence", "Size", "Created By", "Description")
        self.tree = ttk.Treeview(
            self.history_frame, columns=columns, show="headings", height=15
        )

        # Configure columns
        self.tree.heading("Timestamp", text="Timestamp")
        self.tree.heading("Confidence", text="Confidence")
        self.tree.heading("Size", text="Size (bytes)")
        self.tree.heading("Created By", text="Created By")
        self.tree.heading("Description", text="Description")

        self.tree.column("Timestamp", width=150)
        self.tree.column("Confidence", width=80)
        self.tree.column("Size", width=100)
        self.tree.column("Created By", width=100)
        self.tree.column("Description", width=300)

        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(
            self.history_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        tree_scroll_x = ttk.Scrollbar(
            self.history_frame, orient=tk.HORIZONTAL, command=self.tree.xview
        )
        self.tree.configure(
            yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set
        )

        # Pack treeview and scrollbars
        tree_frame = ttk.Frame(self.history_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Bind events
        self.tree.bind("<Double-1>", self._on_version_double_click)
        self.tree.bind("<<TreeviewSelect>>", self._on_version_selected)

    def _create_diff_tab(self):
        """Create diff viewer tab"""
        # Toolbar
        diff_toolbar = ttk.Frame(self.diff_frame)

        ttk.Label(diff_toolbar, text="Compare:").pack(side=tk.LEFT, padx=5)

        self.version1_var = tk.StringVar()
        self.version1_combo = ttk.Combobox(
            diff_toolbar, textvariable=self.version1_var, width=20, state="readonly"
        )
        self.version1_combo.pack(side=tk.LEFT, padx=2)

        ttk.Label(diff_toolbar, text="with:").pack(side=tk.LEFT, padx=5)

        self.version2_var = tk.StringVar()
        self.version2_combo = ttk.Combobox(
            diff_toolbar, textvariable=self.version2_var, width=20, state="readonly"
        )
        self.version2_combo.pack(side=tk.LEFT, padx=2)

        self.diff_btn = ttk.Button(
            diff_toolbar, text="Generate Diff", command=self._generate_diff
        )
        self.diff_btn.pack(side=tk.LEFT, padx=5)

        self.save_diff_btn = ttk.Button(
            diff_toolbar, text="Save Diff", command=self._save_diff
        )
        self.save_diff_btn.pack(side=tk.LEFT, padx=2)

        diff_toolbar.pack(fill=tk.X, padx=5, pady=5)

        # Format selection
        format_frame = ttk.Frame(self.diff_frame)
        ttk.Label(format_frame, text="Format:").pack(side=tk.LEFT, padx=5)

        self.diff_format_var = tk.StringVar(value="unified")
        formats = [("Unified", "unified"), ("Context", "context"), ("HTML", "html")]

        for text, value in formats:
            ttk.Radiobutton(
                format_frame, text=text, variable=self.diff_format_var, value=value
            ).pack(side=tk.LEFT, padx=5)

        format_frame.pack(fill=tk.X, padx=5, pady=2)

        # Diff display
        self.diff_text = scrolledtext.ScrolledText(
            self.diff_frame, height=25, wrap=tk.NONE
        )
        self.diff_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _create_stats_tab(self):
        """Create statistics tab"""
        # Stats display
        stats_notebook = ttk.Notebook(self.stats_frame)

        # Overview frame
        overview_frame = ttk.Frame(stats_notebook)
        stats_notebook.add(overview_frame, text="Overview")

        self.stats_text = scrolledtext.ScrolledText(
            overview_frame, height=20, wrap=tk.WORD
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Charts frame (placeholder for future enhancement)
        charts_frame = ttk.Frame(stats_notebook)
        stats_notebook.add(charts_frame, text="Charts")

        ttk.Label(charts_frame, text="📊 Charts coming soon!", font=("Arial", 12)).pack(
            expand=True
        )

        stats_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _setup_layout(self):
        """Setup the main layout"""
        self.plugin_frame.pack(fill=tk.X, padx=5, pady=5)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Load initial data
        self._refresh_plugins()

    def _refresh_plugins(self):
        """Refresh the list of plugins"""
        # Get list of plugins from the plugin directory
        plugin_dir = "lyrixa/plugins"
        if os.path.exists(plugin_dir):
            plugins = []
            for file in os.listdir(plugin_dir):
                if file.endswith(".py") and not file.startswith("__"):
                    plugin_name = file[:-3]  # Remove .py extension
                    plugins.append(plugin_name)

            self.plugin_combo["values"] = plugins
            if plugins and not self.plugin_var.get():
                self.plugin_combo.set(plugins[0])
                self._on_plugin_selected(None)

    def _on_plugin_selected(self, event):
        """Handle plugin selection"""
        plugin_name = self.plugin_var.get()
        if plugin_name:
            self.current_plugin = plugin_name
            self._load_version_history()
            self._update_diff_combos()
            self._update_stats()

    def _load_version_history(self):
        """Load version history for current plugin"""
        if not self.current_plugin:
            return

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Load snapshots
        self.snapshots = self.version_control.list_snapshots(self.current_plugin)

        # Populate treeview
        for snapshot in self.snapshots:
            # Format timestamp
            try:
                dt = datetime.strptime(snapshot.timestamp, "%Y%m%d_%H%M%S")
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                formatted_time = snapshot.timestamp

            self.tree.insert(
                "",
                "end",
                values=(
                    formatted_time,
                    f"{snapshot.confidence_score:.2f}",
                    snapshot.size,
                    snapshot.metadata.get("created_by", "unknown"),
                    snapshot.metadata.get("description", ""),
                ),
            )

    def _update_diff_combos(self):
        """Update diff comparison combos"""
        timestamps = [s.timestamp for s in self.snapshots]

        self.version1_combo["values"] = timestamps
        self.version2_combo["values"] = timestamps

        if len(timestamps) >= 2:
            self.version1_combo.set(timestamps[0])  # Latest
            self.version2_combo.set(timestamps[1])  # Previous

    def _update_stats(self):
        """Update statistics display"""
        if not self.current_plugin:
            return

        stats = self.version_control.get_plugin_history_stats(self.current_plugin)

        stats_text = f"""Plugin Version Statistics: {self.current_plugin}
{"=" * 50}

📊 OVERVIEW
• Total Snapshots: {stats.get("total_snapshots", 0)}
• Recent Snapshots (7 days): {stats.get("recent_snapshots", 0)}

🎯 CONFIDENCE SCORES
• Average: {stats.get("average_confidence", 0):.2f}
• Maximum: {stats.get("max_confidence", 0):.2f}
• Minimum: {stats.get("min_confidence", 0):.2f}

📈 SIZE TRENDS
• Trend: {stats.get("size_trend", "unknown")}
• Recent Sizes: {stats.get("recent_sizes", [])}

💡 RECOMMENDATIONS
"""

        # Add recommendations based on stats
        if stats.get("total_snapshots", 0) > 20:
            stats_text += "• Consider cleaning up old snapshots\n"

        if stats.get("average_confidence", 0) < 0.5:
            stats_text += "• Plugin confidence scores are low - review recent changes\n"

        if stats.get("recent_snapshots", 0) == 0:
            stats_text += "• No recent activity - plugin may be stable\n"

        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)

    def _on_version_selected(self, event):
        """Handle version selection in treeview"""
        selection = self.tree.selection()
        if selection:
            # Enable/disable buttons based on selection
            self.rollback_btn.config(state=tk.NORMAL)
            self.export_btn.config(state=tk.NORMAL)
            self.delete_btn.config(state=tk.NORMAL)
        else:
            self.rollback_btn.config(state=tk.DISABLED)
            self.export_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)

    def _on_version_double_click(self, event):
        """Handle double-click on version"""
        self._view_version_code()

    def _view_version_code(self):
        """View code for selected version"""
        selection = self.tree.selection()
        if not selection:
            return

        # Get selected timestamp
        item = self.tree.item(selection[0])
        timestamp_str = item["values"][0]

        # Find corresponding snapshot
        for snapshot in self.snapshots:
            try:
                dt = datetime.strptime(snapshot.timestamp, "%Y%m%d_%H%M%S")
                if dt.strftime("%Y-%m-%d %H:%M:%S") == timestamp_str:
                    self._show_code_viewer(snapshot)
                    break
            except Exception:
                continue

    def _show_code_viewer(self, snapshot: PluginSnapshot):
        """Show code viewer window for snapshot"""
        viewer = tk.Toplevel(self.window)
        viewer.title(f"Code Viewer: {snapshot.plugin_name} @ {snapshot.timestamp}")
        viewer.geometry("800x600")

        # Read and display code
        try:
            with open(snapshot.file_path, "r", encoding="utf-8") as f:
                code = f.read()

            text_widget = scrolledtext.ScrolledText(viewer, wrap=tk.NONE)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            text_widget.insert(1.0, code)
            text_widget.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read snapshot: {e}")

    def _rollback_selected(self):
        """Rollback to selected version"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a version to rollback to.")
            return

        # Get selected timestamp
        item = self.tree.item(selection[0])
        timestamp_str = item["values"][0]

        # Find corresponding snapshot
        target_snapshot = None
        for snapshot in self.snapshots:
            try:
                dt = datetime.strptime(snapshot.timestamp, "%Y%m%d_%H%M%S")
                if dt.strftime("%Y-%m-%d %H:%M:%S") == timestamp_str:
                    target_snapshot = snapshot
                    break
            except Exception:
                continue

        if not target_snapshot:
            messagebox.showerror("Error", "Could not find selected snapshot.")
            return

        # Confirm rollback
        result = messagebox.askyesno(
            "Confirm Rollback",
            f"Are you sure you want to rollback {self.current_plugin} to version {timestamp_str}?\n\n"
            "This will replace the current plugin file. A backup will be created automatically.",
        )

        if result:
            success = self.version_control.rollback_plugin(
                self.current_plugin, target_snapshot.timestamp
            )

            if success:
                messagebox.showinfo(
                    "Success", f"Plugin {self.current_plugin} rolled back successfully!"
                )
                self._load_version_history()  # Refresh history
            else:
                messagebox.showerror(
                    "Error", "Rollback failed. Check console for details."
                )

    def _export_selected(self):
        """Export selected snapshot"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a version to export.")
            return

        # Get selected timestamp
        item = self.tree.item(selection[0])
        timestamp_str = item["values"][0]

        # Find corresponding snapshot
        for snapshot in self.snapshots:
            try:
                dt = datetime.strptime(snapshot.timestamp, "%Y%m%d_%H%M%S")
                if dt.strftime("%Y-%m-%d %H:%M:%S") == timestamp_str:
                    # Choose export location
                    filename = filedialog.asksaveasfilename(
                        defaultextension=".py",
                        filetypes=[("Python files", "*.py"), ("All files", "*.*")],
                        initialname=f"{self.current_plugin}_{snapshot.timestamp}.py",
                    )

                    if filename:
                        success = self.version_control.export_snapshot(
                            self.current_plugin, snapshot.timestamp, filename
                        )

                        if success:
                            messagebox.showinfo(
                                "Success", f"Snapshot exported to {filename}"
                            )
                        else:
                            messagebox.showerror("Error", "Export failed.")
                    break
            except Exception:
                continue

    def _delete_selected(self):
        """Delete selected snapshot"""
        # Implementation for snapshot deletion
        messagebox.showinfo("Info", "Snapshot deletion not yet implemented.")

    def _cleanup_old_snapshots(self):
        """Cleanup old snapshots"""
        if not self.current_plugin:
            return

        result = messagebox.askyesno(
            "Confirm Cleanup",
            f"Clean up old snapshots for {self.current_plugin}?\n\n"
            "This will keep only the 10 most recent snapshots.",
        )

        if result:
            removed = self.version_control.cleanup_old_snapshots(
                self.current_plugin, 10
            )
            messagebox.showinfo("Cleanup Complete", f"Removed {removed} old snapshots.")
            self._load_version_history()  # Refresh

    def _generate_diff(self):
        """Generate diff between selected versions"""
        v1 = self.version1_var.get()
        v2 = self.version2_var.get()

        if not v1 or not v2:
            messagebox.showwarning("Warning", "Please select two versions to compare.")
            return

        if v1 == v2:
            messagebox.showwarning(
                "Warning", "Please select different versions to compare."
            )
            return

        format_type = self.diff_format_var.get()
        diff = self.version_control.diff_plugin_versions(
            self.current_plugin, v1, v2, format_type
        )

        if format_type == "html":
            # Show HTML diff in browser
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False
            ) as f:
                f.write(diff)
                webbrowser.open(f"file://{f.name}")
        else:
            # Show text diff in widget
            self.diff_text.delete(1.0, tk.END)
            self.diff_text.insert(1.0, diff)

    def _save_diff(self):
        """Save current diff to file"""
        diff_content = self.diff_text.get(1.0, tk.END).strip()

        if not diff_content:
            messagebox.showwarning("Warning", "No diff to save. Generate a diff first.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("Patch files", "*.patch"),
                ("All files", "*.*"),
            ],
            initialname=f"{self.current_plugin}_diff.txt",
        )

        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(diff_content)
                messagebox.showinfo("Success", f"Diff saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save diff: {e}")


def show_version_history_gui(parent, version_control: PluginVersionControl):
    """Show the plugin version history GUI"""
    return PluginVersionHistoryGUI(parent, version_control)


if __name__ == "__main__":
    # Test the GUI
    root = tk.Tk()
    root.withdraw()  # Hide main window

    from plugin_version_control import PluginVersionControl

    version_control = PluginVersionControl()
    gui = show_version_history_gui(root, version_control)

    root.mainloop()
