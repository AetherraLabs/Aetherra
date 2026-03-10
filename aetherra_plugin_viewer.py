#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🔌 Aetherra Plugin Viewer
========================
Simple GUI to view discovered local plugins that are available to the Hub.

This provides a quick way to see what plugins have been discovered and
would be visible in the Aetherra Hub marketplace.
"""

# Standard library imports
import asyncio
import json
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

# Aetherra imports
from aetherra_plugin_discovery import AetherraPluginDiscovery


class PluginViewerGUI:
    """Simple GUI to view discovered plugins."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔌 Aetherra Plugin Viewer - Local Plugin Catalog")
        self.root.geometry("900x700")

        # Plugin discovery service
        self.discovery = AetherraPluginDiscovery()
        self.plugins = {}

        self.setup_ui()
        self.refresh_plugins()

    def setup_ui(self):
        """Setup the user interface."""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=0)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame, text="🔌 Aetherra Plugin Catalog", font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")

        # Left panel - Plugin list
        list_frame = ttk.LabelFrame(
            main_frame, text="[DISC] Discovered Plugins", padding="5"
        )
        list_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))

        # Plugin listbox with scrollbar
        list_scroll_frame = ttk.Frame(list_frame)
        list_scroll_frame.pack(fill=tk.BOTH, expand=True)

        self.plugin_listbox = tk.Listbox(list_scroll_frame, width=30)
        list_scrollbar = ttk.Scrollbar(
            list_scroll_frame, orient=tk.VERTICAL, command=self.plugin_listbox.yview
        )
        self.plugin_listbox.configure(yscrollcommand=list_scrollbar.set)
        self.plugin_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind selection event
        self.plugin_listbox.bind("<<ListboxSelect>>", self.on_plugin_select)

        # Right panel - Plugin details
        details_frame = ttk.LabelFrame(
            main_frame, text="📋 Plugin Details", padding="5"
        )
        details_frame.grid(row=1, column=1, sticky="nsew")
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(0, weight=1)

        # Plugin details text area
        self.details_text = scrolledtext.ScrolledText(
            details_frame, wrap=tk.WORD, width=50, height=25, font=("Consolas", 10)
        )
        self.details_text.grid(row=0, column=0, sticky="nsew")

        # Bottom panel - Summary and actions
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=2, column=0, columnspan=2, sticky="we", pady=(10, 0))
        bottom_frame.columnconfigure(0, weight=1)

        # Summary label
        self.summary_label = ttk.Label(bottom_frame, text="No plugins loaded")
        self.summary_label.grid(row=0, column=0, sticky="w")

        # Action buttons
        button_frame = ttk.Frame(bottom_frame)
        button_frame.grid(row=0, column=1, sticky="e")
        ttk.Button(button_frame, text="🔄 Refresh", command=self.refresh_plugins).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(
            button_frame, text="💾 Export List", command=self.export_plugin_list
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            button_frame, text="🏪 Sync with Hub", command=self.sync_with_hub
        ).pack(side=tk.LEFT)

    def refresh_plugins(self):
        """Refresh the plugin list."""

        def refresh_async():
            asyncio.run(self._refresh_plugins_async())

        # Run async refresh in background thread
        thread = threading.Thread(target=refresh_async, daemon=True)
        thread.start()

    async def _refresh_plugins_async(self):
        """Async plugin refresh."""
        try:
            # Discover plugins
            self.plugins = await self.discovery.discover_all_plugins()

            # Update UI in main thread
            self.root.after(0, self._update_plugin_list)

        except Exception as e:
            self.root.after(
                0,
                lambda err=e: messagebox.showerror(
                    "Error", f"Failed to refresh plugins: {err}"
                ),
            )

    def _update_plugin_list(self):
        """Update the plugin list in the UI."""
        # Clear existing list
        self.plugin_listbox.delete(0, tk.END)

        # Add plugins to list
        for name, metadata in self.plugins.items():
            display_name = (
                f"[{metadata.plugin_type.upper()}] {name} v{metadata.version}"
            )
            self.plugin_listbox.insert(tk.END, display_name)

        # Update summary
        summary = self.discovery.get_plugin_summary()
        summary_text = f"Total: {summary['total_plugins']} plugins ({', '.join([f'{k}: {v}' for k, v in summary['by_type'].items()])})"
        self.summary_label.config(text=summary_text)

        # Clear details if no plugins
        if not self.plugins:
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(1.0, "No plugins found.")

    def on_plugin_select(self, event):
        """Handle plugin selection."""
        selection = self.plugin_listbox.curselection()
        if not selection:
            return

        # Get selected plugin name
        display_name = self.plugin_listbox.get(selection[0])
        # Extract actual plugin name (remove type prefix and version)
        plugin_name = display_name.split("] ")[1].rsplit(" v", 1)[0]

        if plugin_name in self.plugins:
            self.show_plugin_details(self.plugins[plugin_name])

    def show_plugin_details(self, metadata):
        """Show detailed information about a plugin."""
        # Clear existing content
        self.details_text.delete(1.0, tk.END)

        # Format plugin details
        details = f"""🔌 Plugin Information
========================

[DISC] Name: {metadata.name}
📝 Version: {metadata.version}
👤 Author: {metadata.author}
📂 Category: {metadata.category}
🏷️ Type: {metadata.plugin_type}
⚖️ License: {metadata.license}

📄 Description:
{metadata.description}

[TOOL] Technical Details:
• Aetherra Version: {metadata.aetherra_version}
• Local Path: {metadata.local_path or "Not specified"}
• Entry Point: {metadata.entry_point or "Not specified"}

🏷️ Keywords:
{", ".join(metadata.keywords) if metadata.keywords else "None"}

[DISC] Dependencies:
{json.dumps(metadata.dependencies, indent=2) if metadata.dependencies else "None"}

🔗 Exports:
{json.dumps(metadata.exports, indent=2) if metadata.exports else "None"}

🌐 Links:
• Repository: {metadata.repository or "Not specified"}
• Documentation: {metadata.documentation or "Not specified"}
• Homepage: {metadata.homepage or "Not specified"}
"""

        self.details_text.insert(1.0, details)

    def export_plugin_list(self):
        """Export the plugin list to a file."""
        try:
            # Standard library imports
            from tkinter import filedialog

            # Ask for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Export Plugin List",
            )

            if filename:
                # Prepare export data
                export_data = {
                    "export_info": {
                        "timestamp": self.discovery.get_plugin_summary(),
                        "total_plugins": len(self.plugins),
                    },
                    "plugins": {},
                }

                # Convert plugin metadata to JSON-serializable format
                for name, metadata in self.plugins.items():
                    export_data["plugins"][name] = {
                        "name": metadata.name,
                        "version": metadata.version,
                        "description": metadata.description,
                        "author": metadata.author,
                        "category": metadata.category,
                        "license": metadata.license,
                        "plugin_type": metadata.plugin_type,
                        "aetherra_version": metadata.aetherra_version,
                        "keywords": metadata.keywords,
                        "dependencies": metadata.dependencies,
                        "exports": metadata.exports,
                        "local_path": metadata.local_path,
                        "repository": metadata.repository,
                        "documentation": metadata.documentation,
                        "homepage": metadata.homepage,
                    }

                # Write to file
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)

                messagebox.showinfo("Success", f"Plugin list exported to {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export plugin list: {e}")

    def sync_with_hub(self):
        """Sync plugins with the Aetherra Hub."""

        def sync_async():
            asyncio.run(self._sync_with_hub_async())

        # Run sync in background thread
        thread = threading.Thread(target=sync_async, daemon=True)
        thread.start()

    async def _sync_with_hub_async(self):
        """Async Hub sync."""
        try:
            # Try to sync with Hub
            success_count = await self.discovery.sync_all_with_hub()

            # Show result
            if success_count > 0:
                message = f"[OK] Successfully synced {success_count} plugins with Aetherra Hub"
            else:
                message = "[WARN] No plugins were synced. Hub may be offline."

            self.root.after(0, lambda: messagebox.showinfo("Sync Result", message))

        except Exception as e:
            self.root.after(
                0,
                lambda err=e: messagebox.showerror(
                    "Sync Error", f"Failed to sync with Hub: {err}"
                ),
            )

    def run(self):
        """Run the GUI."""
        self.root.mainloop()


def main():
    """Main function."""
    print("🔌 Starting Aetherra Plugin Viewer...")

    try:
        app = PluginViewerGUI()
        app.run()
    except Exception as e:
        print(f"❌ Error starting Plugin Viewer: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
