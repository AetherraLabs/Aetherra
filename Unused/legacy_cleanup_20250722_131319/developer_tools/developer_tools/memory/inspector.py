"""
Memory Inspector & Editor - Advanced Memory Management Tool

This module provides comprehensive memory inspection and editing capabilities
for the Aetherra & Lyrixa project, including GUI and CLI interfaces for
memory search, editing, visualization, and management.

Key Features:
- Visual memory management interface
- Search and filter memories
- Edit individual memory entries
- Memory graph visualization
- Export/import capabilities
- Memory validation and integrity checks
- Integration with existing memory systems
"""

import os
import json
import hashlib
import logging
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, TYPE_CHECKING
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

if TYPE_CHECKING:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    mdates = None
    FigureCanvasTkAgg = None

class MemoryEntry:
    """Represents a single memory entry"""

    def __init__(self, key: str, value: Any, timestamp: Optional[datetime] = None,
                 metadata: Optional[Dict] = None):
        self.key = key
        self.value = value
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}
        self.checksum = self._calculate_checksum()
        self.pinned = False
        self.tags = set()

    def _calculate_checksum(self) -> str:
        """Calculate checksum for integrity verification"""
        content = f"{self.key}:{json.dumps(self.value, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()

    def validate_integrity(self) -> bool:
        """Validate memory entry integrity"""
        return self.checksum == self._calculate_checksum()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'key': self.key,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
            'checksum': self.checksum,
            'pinned': self.pinned,
            'tags': list(self.tags)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        """Create from dictionary"""
        entry = cls(
            key=data['key'],
            value=data['value'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data.get('metadata', {})
        )
        entry.pinned = data.get('pinned', False)
        entry.tags = set(data.get('tags', []))
        return entry

class MemoryDatabase:
    """Database interface for memory operations"""

    def __init__(self, db_path: str = "memory_inspector.db"):
        self.db_path = db_path
        self.logger = logging.getLogger('MemoryInspector.Database')
        self._init_database()

    def _init_database(self):
        """Initialize database schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS memories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        key TEXT UNIQUE NOT NULL,
                        value TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        metadata TEXT,
                        checksum TEXT NOT NULL,
                        pinned INTEGER DEFAULT 0,
                        tags TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_key ON memories(key)
                ''')

                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)
                ''')

                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_pinned ON memories(pinned)
                ''')

        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise

    def store_memory(self, entry: MemoryEntry) -> bool:
        """Store memory entry in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO memories
                    (key, value, timestamp, metadata, checksum, pinned, tags, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry.key,
                    json.dumps(entry.value),
                    entry.timestamp.isoformat(),
                    json.dumps(entry.metadata),
                    entry.checksum,
                    int(entry.pinned),
                    json.dumps(list(entry.tags)),
                    datetime.now().isoformat()
                ))
            return True
        except Exception as e:
            self.logger.error(f"Failed to store memory {entry.key}: {e}")
            return False

    def get_memory(self, key: str) -> Optional[MemoryEntry]:
        """Retrieve memory entry by key"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    'SELECT * FROM memories WHERE key = ?', (key,)
                )
                row = cursor.fetchone()

                if row:
                    return self._row_to_memory_entry(row)
                return None

        except Exception as e:
            self.logger.error(f"Failed to get memory {key}: {e}")
            return None

    def search_memories(self, query: str = "", tags: Optional[List[str]] = None,
                       pinned_only: bool = False) -> List[MemoryEntry]:
        """Search memories with filters"""
        try:
            sql = "SELECT * FROM memories WHERE 1=1"
            params = []

            if query:
                sql += " AND (key LIKE ? OR value LIKE ?)"
                params.extend([f"%{query}%", f"%{query}%"])

            if pinned_only:
                sql += " AND pinned = 1"

            if tags:
                # Simple tag matching - could be improved
                for tag in tags:
                    sql += " AND tags LIKE ?"
                    params.append(f"%{tag}%")

            sql += " ORDER BY timestamp DESC"

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(sql, params)
                rows = cursor.fetchall()

                return [self._row_to_memory_entry(row) for row in rows]

        except Exception as e:
            self.logger.error(f"Failed to search memories: {e}")
            return []

    def delete_memory(self, key: str) -> bool:
        """Delete memory entry"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('DELETE FROM memories WHERE key = ?', (key,))
                return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Failed to delete memory {key}: {e}")
            return False

    def get_all_memories(self) -> List[MemoryEntry]:
        """Get all memory entries"""
        return self.search_memories()

    def _row_to_memory_entry(self, row) -> MemoryEntry:
        """Convert database row to MemoryEntry"""
        _, key, value, timestamp, metadata, checksum, pinned, tags, _, _ = row

        entry = MemoryEntry(
            key=key,
            value=json.loads(value),
            timestamp=datetime.fromisoformat(timestamp),
            metadata=json.loads(metadata) if metadata else {}
        )
        entry.checksum = checksum
        entry.pinned = bool(pinned)
        entry.tags = set(json.loads(tags) if tags else [])

        return entry

class MemoryInspector:
    """Core memory inspection and management class"""

    def __init__(self, memory_file: str = "memory_store.json",
                 db_path: str = "memory_inspector.db"):
        self.memory_file = Path(memory_file)
        self.db = MemoryDatabase(db_path)
        self.logger = logging.getLogger('MemoryInspector')

        # Load existing memories
        self._sync_from_file()

    def _sync_from_file(self):
        """Sync memories from existing memory file"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for key, value in data.items():
                    if key != '_metadata':  # Skip metadata
                        entry = MemoryEntry(key, value)
                        self.db.store_memory(entry)

                self.logger.info(f"Synced {len(data)} memories from {self.memory_file}")

        except Exception as e:
            self.logger.error(f"Failed to sync from memory file: {e}")

    def search_memories(self, query: str = "", tags: Optional[List[str]] = None,
                       pinned_only: bool = False) -> List[MemoryEntry]:
        """Search memories with various filters"""
        return self.db.search_memories(query, tags, pinned_only)

    def get_memory(self, key: str) -> Optional[MemoryEntry]:
        """Get specific memory entry"""
        return self.db.get_memory(key)

    def update_memory(self, key: str, new_value: Any, metadata: Optional[Dict] = None) -> bool:
        """Update memory entry"""
        try:
            entry = MemoryEntry(key, new_value, metadata=metadata)
            return self.db.store_memory(entry)
        except Exception as e:
            self.logger.error(f"Failed to update memory {key}: {e}")
            return False

    def pin_memory(self, key: str, pinned: bool = True) -> bool:
        """Pin or unpin memory entry"""
        try:
            entry = self.db.get_memory(key)
            if entry:
                entry.pinned = pinned
                return self.db.store_memory(entry)
            return False
        except Exception as e:
            self.logger.error(f"Failed to pin memory {key}: {e}")
            return False

    def add_tag(self, key: str, tag: str) -> bool:
        """Add tag to memory entry"""
        try:
            entry = self.db.get_memory(key)
            if entry:
                entry.tags.add(tag)
                return self.db.store_memory(entry)
            return False
        except Exception as e:
            self.logger.error(f"Failed to add tag to memory {key}: {e}")
            return False

    def remove_tag(self, key: str, tag: str) -> bool:
        """Remove tag from memory entry"""
        try:
            entry = self.db.get_memory(key)
            if entry:
                entry.tags.discard(tag)
                return self.db.store_memory(entry)
            return False
        except Exception as e:
            self.logger.error(f"Failed to remove tag from memory {key}: {e}")
            return False

    def delete_memory(self, key: str) -> bool:
        """Delete memory entry"""
        return self.db.delete_memory(key)

    def validate_integrity(self) -> Dict[str, bool]:
        """Validate integrity of all memories"""
        results = {}
        for entry in self.db.get_all_memories():
            results[entry.key] = entry.validate_integrity()
        return results

    def export_memories(self, filepath: str, format: str = 'json') -> bool:
        """Export memories to file"""
        try:
            memories = self.db.get_all_memories()

            if format.lower() == 'json':
                data = {entry.key: entry.to_dict() for entry in memories}
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Unsupported export format: {format}")

            self.logger.info(f"Exported {len(memories)} memories to {filepath}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export memories: {e}")
            return False

    def import_memories(self, filepath: str, format: str = 'json') -> bool:
        """Import memories from file"""
        try:
            if format.lower() == 'json':
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                count = 0
                for key, entry_data in data.items():
                    if isinstance(entry_data, dict) and 'timestamp' in entry_data:
                        # Full entry data
                        entry = MemoryEntry.from_dict(entry_data)
                    else:
                        # Simple key-value data
                        entry = MemoryEntry(key, entry_data)

                    if self.db.store_memory(entry):
                        count += 1

                self.logger.info(f"Imported {count} memories from {filepath}")
                return True
            else:
                raise ValueError(f"Unsupported import format: {format}")

        except Exception as e:
            self.logger.error(f"Failed to import memories: {e}")
            return False

class MemoryEditor:
    """Advanced memory editing interface"""

    def __init__(self, inspector: MemoryInspector):
        self.inspector = inspector
        self.logger = logging.getLogger('MemoryEditor')

    def edit_memory_interactive(self, key: str) -> bool:
        """Interactive memory editing (CLI)"""
        try:
            entry = self.inspector.get_memory(key)
            if not entry:
                print(f"Memory '{key}' not found.")
                return False

            print(f"\nEditing memory: {key}")
            print(f"Current value: {json.dumps(entry.value, indent=2)}")
            print(f"Type: {type(entry.value).__name__}")
            print(f"Pinned: {entry.pinned}")
            print(f"Tags: {', '.join(entry.tags)}")

            print("\nOptions:")
            print("1. Edit value")
            print("2. Toggle pin status")
            print("3. Manage tags")
            print("4. Edit metadata")
            print("5. Cancel")

            choice = input("Enter choice (1-5): ").strip()

            if choice == '1':
                return self._edit_value(entry)
            elif choice == '2':
                return self._toggle_pin(entry)
            elif choice == '3':
                return self._manage_tags(entry)
            elif choice == '4':
                return self._edit_metadata(entry)
            else:
                print("Cancelled.")
                return False

        except Exception as e:
            self.logger.error(f"Error in interactive editing: {e}")
            return False

    def _edit_value(self, entry: MemoryEntry) -> bool:
        """Edit memory value"""
        try:
            print(f"\nCurrent value ({type(entry.value).__name__}):")
            print(json.dumps(entry.value, indent=2))

            if isinstance(entry.value, (dict, list)):
                print("\nEnter new JSON value:")
                new_value_str = input()
                try:
                    new_value = json.loads(new_value_str)
                except json.JSONDecodeError:
                    print("Invalid JSON format.")
                    return False
            else:
                print(f"\nEnter new value (current: {entry.value}):")
                new_value_str = input()

                # Try to preserve type
                if isinstance(entry.value, bool):
                    new_value = new_value_str.lower() in ('true', '1', 'yes', 'on')
                elif isinstance(entry.value, int):
                    try:
                        new_value = int(new_value_str)
                    except ValueError:
                        new_value = new_value_str
                elif isinstance(entry.value, float):
                    try:
                        new_value = float(new_value_str)
                    except ValueError:
                        new_value = new_value_str
                else:
                    new_value = new_value_str

            return self.inspector.update_memory(entry.key, new_value, entry.metadata)

        except Exception as e:
            self.logger.error(f"Error editing value: {e}")
            return False

    def _toggle_pin(self, entry: MemoryEntry) -> bool:
        """Toggle pin status"""
        new_status = not entry.pinned
        result = self.inspector.pin_memory(entry.key, new_status)
        if result:
            print(f"Memory {'pinned' if new_status else 'unpinned'}.")
        return result

    def _manage_tags(self, entry: MemoryEntry) -> bool:
        """Manage memory tags"""
        try:
            print(f"\nCurrent tags: {', '.join(entry.tags) if entry.tags else 'None'}")
            print("1. Add tag")
            print("2. Remove tag")
            print("3. Clear all tags")

            choice = input("Enter choice (1-3): ").strip()

            if choice == '1':
                tag = input("Enter tag to add: ").strip()
                if tag:
                    return self.inspector.add_tag(entry.key, tag)
            elif choice == '2':
                tag = input("Enter tag to remove: ").strip()
                if tag:
                    return self.inspector.remove_tag(entry.key, tag)
            elif choice == '3':
                # Clear all tags
                for tag in list(entry.tags):
                    self.inspector.remove_tag(entry.key, tag)
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error managing tags: {e}")
            return False

    def _edit_metadata(self, entry: MemoryEntry) -> bool:
        """Edit memory metadata"""
        try:
            print(f"\nCurrent metadata:")
            print(json.dumps(entry.metadata, indent=2))

            print("\nEnter new metadata (JSON format):")
            metadata_str = input()

            try:
                new_metadata = json.loads(metadata_str) if metadata_str else {}
                return self.inspector.update_memory(entry.key, entry.value, new_metadata)
            except json.JSONDecodeError:
                print("Invalid JSON format for metadata.")
                return False

        except Exception as e:
            self.logger.error(f"Error editing metadata: {e}")
            return False

class MemoryVisualizerGUI:
    """GUI for memory visualization and editing"""

    def __init__(self, inspector: MemoryInspector):
        self.inspector = inspector
        self.editor = MemoryEditor(inspector)
        self.root = tk.Tk()
        self.root.title("Memory Inspector & Editor")
        self.root.geometry("1200x800")

        self._setup_gui()
        self._refresh_memories()

    def _setup_gui(self):
        """Setup GUI components"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Search frame
        search_frame = ttk.LabelFrame(main_frame, text="Search & Filter")
        search_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=5, pady=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, padx=5, pady=5)
        search_entry.bind('<Return>', lambda e: self._search_memories())

        ttk.Button(search_frame, text="Search", command=self._search_memories).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(search_frame, text="Clear", command=self._clear_search).grid(row=0, column=3, padx=5, pady=5)

        self.pinned_only_var = tk.BooleanVar()
        ttk.Checkbutton(search_frame, text="Pinned only", variable=self.pinned_only_var).grid(row=0, column=4, padx=5, pady=5)

        # Memory list frame
        list_frame = ttk.LabelFrame(main_frame, text="Memories")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Treeview for memories
        columns = ('Key', 'Type', 'Pinned', 'Tags', 'Timestamp')
        self.memory_tree = ttk.Treeview(list_frame, columns=columns, show='headings')

        for col in columns:
            self.memory_tree.heading(col, text=col)
            self.memory_tree.column(col, width=150)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.memory_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.memory_tree.xview)
        self.memory_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.memory_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        # Bind selection event
        self.memory_tree.bind('<<TreeviewSelect>>', self._on_memory_select)

        # Details frame
        details_frame = ttk.LabelFrame(main_frame, text="Memory Details")
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.details_text = tk.Text(details_frame, height=10, wrap=tk.WORD)
        details_scrollbar = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scrollbar.set)

        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)

        ttk.Button(buttons_frame, text="Refresh", command=self._refresh_memories).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Edit", command=self._edit_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Pin/Unpin", command=self._toggle_pin_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Delete", command=self._delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Export", command=self._export_memories).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Import", command=self._import_memories).pack(side=tk.LEFT, padx=5)

        if MATPLOTLIB_AVAILABLE:
            ttk.Button(buttons_frame, text="Visualize", command=self._show_visualization).pack(side=tk.LEFT, padx=5)

    def _refresh_memories(self):
        """Refresh memory list"""
        # Clear existing items
        for item in self.memory_tree.get_children():
            self.memory_tree.delete(item)

        # Load memories
        memories = self.inspector.search_memories(
            query=self.search_var.get(),
            pinned_only=self.pinned_only_var.get()
        )

        for memory in memories:
            self.memory_tree.insert('', tk.END, values=(
                memory.key,
                type(memory.value).__name__,
                '✓' if memory.pinned else '',
                ', '.join(memory.tags),
                memory.timestamp.strftime('%Y-%m-%d %H:%M')
            ))

    def _search_memories(self):
        """Search memories"""
        self._refresh_memories()

    def _clear_search(self):
        """Clear search"""
        self.search_var.set('')
        self.pinned_only_var.set(False)
        self._refresh_memories()

    def _on_memory_select(self, event):
        """Handle memory selection"""
        selection = self.memory_tree.selection()
        if selection:
            item = self.memory_tree.item(selection[0])
            key = item['values'][0]

            memory = self.inspector.get_memory(key)
            if memory:
                details = json.dumps(memory.to_dict(), indent=2, ensure_ascii=False)
                self.details_text.delete(1.0, tk.END)
                self.details_text.insert(1.0, details)

    def _edit_selected(self):
        """Edit selected memory"""
        selection = self.memory_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a memory to edit.")
            return

        item = self.memory_tree.item(selection[0])
        key = item['values'][0]

        # Open edit dialog
        EditMemoryDialog(self.root, self.inspector, key, self._refresh_memories)

    def _toggle_pin_selected(self):
        """Toggle pin status of selected memory"""
        selection = self.memory_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a memory to pin/unpin.")
            return

        item = self.memory_tree.item(selection[0])
        key = item['values'][0]

        memory = self.inspector.get_memory(key)
        if memory:
            success = self.inspector.pin_memory(key, not memory.pinned)
            if success:
                self._refresh_memories()
            else:
                messagebox.showerror("Error", "Failed to toggle pin status.")

    def _delete_selected(self):
        """Delete selected memory"""
        selection = self.memory_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a memory to delete.")
            return

        item = self.memory_tree.item(selection[0])
        key = item['values'][0]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete memory '{key}'?"):
            success = self.inspector.delete_memory(key)
            if success:
                self._refresh_memories()
                self.details_text.delete(1.0, tk.END)
            else:
                messagebox.showerror("Error", "Failed to delete memory.")

    def _export_memories(self):
        """Export memories to file"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filepath:
            success = self.inspector.export_memories(filepath)
            if success:
                messagebox.showinfo("Success", f"Memories exported to {filepath}")
            else:
                messagebox.showerror("Error", "Failed to export memories.")

    def _import_memories(self):
        """Import memories from file"""
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filepath:
            success = self.inspector.import_memories(filepath)
            if success:
                self._refresh_memories()
                messagebox.showinfo("Success", f"Memories imported from {filepath}")
            else:
                messagebox.showerror("Error", "Failed to import memories.")

    def _show_visualization(self):
        """Show memory visualization"""
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showerror("Error", "Matplotlib not available for visualization.")
            return

        MemoryVisualizationWindow(self.root, self.inspector)

    def run(self):
        """Run the GUI"""
        self.root.mainloop()

class EditMemoryDialog:
    """Dialog for editing memory entries"""

    def __init__(self, parent, inspector: MemoryInspector, key: str, refresh_callback):
        self.inspector = inspector
        self.key = key
        self.refresh_callback = refresh_callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Edit Memory: {key}")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.memory: Optional[MemoryEntry] = inspector.get_memory(key)
        if not self.memory:
            messagebox.showerror("Error", f"Memory '{key}' not found.")
            self.dialog.destroy()
            return

        self._setup_dialog()

        # Center dialog
        self.dialog.geometry("+{}+{}".format(
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))

    def _setup_dialog(self):
        """Setup dialog components"""
        assert self.memory is not None, "Memory must be loaded before setting up dialog"

        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Key (read-only)
        ttk.Label(main_frame, text="Key:").grid(row=0, column=0, sticky='w', pady=5)
        key_entry = ttk.Entry(main_frame, width=50)
        key_entry.insert(0, self.memory.key)
        key_entry.config(state='readonly')
        key_entry.grid(row=0, column=1, sticky='ew', pady=5)

        # Value
        ttk.Label(main_frame, text="Value:").grid(row=1, column=0, sticky='nw', pady=5)
        self.value_text = tk.Text(main_frame, height=15, width=50)
        self.value_text.insert(1.0, json.dumps(self.memory.value, indent=2, ensure_ascii=False))
        value_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.value_text.yview)
        self.value_text.configure(yscrollcommand=value_scrollbar.set)
        self.value_text.grid(row=1, column=1, sticky='ew', pady=5)
        value_scrollbar.grid(row=1, column=2, sticky='ns', pady=5)

        # Pin status
        self.pinned_var = tk.BooleanVar(value=self.memory.pinned)
        ttk.Checkbutton(main_frame, text="Pinned", variable=self.pinned_var).grid(row=2, column=1, sticky='w', pady=5)

        # Tags
        ttk.Label(main_frame, text="Tags:").grid(row=3, column=0, sticky='w', pady=5)
        self.tags_var = tk.StringVar(value=', '.join(self.memory.tags))
        tags_entry = ttk.Entry(main_frame, textvariable=self.tags_var, width=50)
        tags_entry.grid(row=3, column=1, sticky='ew', pady=5)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)

        ttk.Button(button_frame, text="Save", command=self._save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

        main_frame.grid_columnconfigure(1, weight=1)

    def _save_changes(self):
        """Save changes to memory"""
        assert self.memory is not None, "Memory must be loaded before saving changes"

        try:
            # Parse new value
            value_str = self.value_text.get(1.0, tk.END).strip()
            try:
                new_value = json.loads(value_str)
            except json.JSONDecodeError as e:
                messagebox.showerror("Invalid JSON", f"Invalid JSON format: {e}")
                return

            # Update memory
            success = self.inspector.update_memory(self.key, new_value, self.memory.metadata)
            if not success:
                messagebox.showerror("Error", "Failed to update memory value.")
                return

            # Update pin status
            success = self.inspector.pin_memory(self.key, self.pinned_var.get())
            if not success:
                messagebox.showerror("Error", "Failed to update pin status.")
                return

            # Update tags
            tags_str = self.tags_var.get().strip()
            new_tags = set(tag.strip() for tag in tags_str.split(',') if tag.strip())

            # Remove old tags
            for old_tag in self.memory.tags:
                if old_tag not in new_tags:
                    self.inspector.remove_tag(self.key, old_tag)

            # Add new tags
            for new_tag in new_tags:
                if new_tag not in self.memory.tags:
                    self.inspector.add_tag(self.key, new_tag)

            # Refresh parent and close dialog
            self.refresh_callback()
            self.dialog.destroy()
            messagebox.showinfo("Success", "Memory updated successfully.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {e}")

class MemoryVisualizationWindow:
    """Window for memory visualization"""

    def __init__(self, parent, inspector: MemoryInspector):
        self.inspector = inspector

        self.window = tk.Toplevel(parent)
        self.window.title("Memory Visualization")
        self.window.geometry("800x600")

        self._create_visualization()

    def _create_visualization(self):
        """Create memory visualization"""
        if not MATPLOTLIB_AVAILABLE:
            ttk.Label(self.window, text="Matplotlib not available - install matplotlib for visualization").pack(pady=50)
            return

        try:
            memories = self.inspector.db.get_all_memories()

            if not memories:
                ttk.Label(self.window, text="No memories to visualize").pack(pady=50)
                return

            # Create figure
            assert plt is not None, "matplotlib.pyplot should be available"
            assert FigureCanvasTkAgg is not None, "FigureCanvasTkAgg should be available"

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

            # Timeline of memory creation
            timestamps = [memory.timestamp for memory in memories]
            timestamps.sort()

            ax1.hist([ts.date() for ts in timestamps], bins=min(30, len(set(ts.date() for ts in timestamps))), alpha=0.7)
            ax1.set_title('Memory Creation Timeline')
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Number of Memories')

            # Memory types distribution
            type_counts = {}
            for memory in memories:
                type_name = type(memory.value).__name__
                type_counts[type_name] = type_counts.get(type_name, 0) + 1

            if type_counts:
                ax2.pie(type_counts.values(), labels=type_counts.keys(), autopct='%1.1f%%')
                ax2.set_title('Memory Types Distribution')

            plt.tight_layout()

            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, self.window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            ttk.Label(self.window, text=f"Visualization error: {e}").pack(pady=50)

def main():
    """Main function for testing"""
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Create inspector
    inspector = MemoryInspector()

    # Test CLI interface
    print("Memory Inspector & Editor - CLI Mode")
    print("Available commands: search, edit, pin, export, import, gui, quit")

    while True:
        command = input("\n> ").strip().lower()

        if command == 'quit':
            break
        elif command == 'search':
            query = input("Search query: ")
            results = inspector.search_memories(query)
            print(f"Found {len(results)} memories:")
            for memory in results[:10]:  # Show first 10
                print(f"  {memory.key}: {type(memory.value).__name__}")
        elif command == 'gui':
            gui = MemoryVisualizerGUI(inspector)
            gui.run()
            break
        elif command.startswith('edit '):
            key = command[5:]
            editor = MemoryEditor(inspector)
            editor.edit_memory_interactive(key)
        else:
            print("Available commands: search, edit <key>, pin, export, import, gui, quit")

if __name__ == "__main__":
    main()
