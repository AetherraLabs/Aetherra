#!/usr/bin/env python3
"""
🎨 NeuroCode Enhanced UI - Modern Tabbed Interface
==================================================

A responsive, modern, and extendable user interface for NeuroCode featuring:
- Clean tabbed interface (Chat, Code, Memory, Plugins)
- Visual memory reflection browsing
- Responsive design with modern aesthetics
- Integrated memory viewer with timeline visualization
- Plugin transparency and management
- Real-time code execution and output

This UI focuses on user experience and visual clarity while maintaining
the powerful AI-native capabilities of NeuroCode.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add core modules to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "core"))

# Qt imports with fallback support
try:
    # Try PySide6 first
    from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, Signal
    from PySide6.QtGui import QBrush, QColor, QFont, QIcon, QPainter, QPalette, QPixmap
    from PySide6.QtWidgets import (
        QApplication,
        QComboBox,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QMainWindow,
        QProgressBar,
        QPushButton,
        QScrollArea,
        QSlider,
        QSplitter,
        QStackedWidget,
        QStatusBar,
        QTabWidget,
        QTextEdit,
        QToolBar,
        QTreeWidget,
        QTreeWidgetItem,
        QVBoxLayout,
        QWidget,
    )

    QT_AVAILABLE = True
except ImportError:
    try:
        # Fallback to PyQt6
        from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
        from PyQt6.QtCore import pyqtSignal as Signal
        from PyQt6.QtGui import QBrush, QColor, QFont, QIcon, QPainter, QPalette, QPixmap
        from PyQt6.QtWidgets import (
            QApplication,
            QComboBox,
            QFrame,
            QGridLayout,
            QGroupBox,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QListWidget,
            QListWidgetItem,
            QMainWindow,
            QProgressBar,
            QPushButton,
            QScrollArea,
            QSlider,
            QSplitter,
            QStackedWidget,
            QStatusBar,
            QTabWidget,
            QTextEdit,
            QToolBar,
            QTreeWidget,
            QTreeWidgetItem,
            QVBoxLayout,
            QWidget,
        )

        QT_AVAILABLE = True
    except ImportError:
        QT_AVAILABLE = False
        print("❌ Qt not available. Please install PySide6 or PyQt6.")

# Import NeuroCode components
if QT_AVAILABLE:
    try:
        from memory import NeuroMemory
        from plugin_manager import get_plugin_ui_data, get_plugins_info, list_plugins_by_category
    except ImportError as e:
        print(f"⚠️ Some NeuroCode components not available: {e}")


class NeuroTheme:
    """Modern dark theme optimized for NeuroCode"""

    # Color palette
    BACKGROUND = "#1a1a1a"
    SURFACE = "#2d2d2d"
    PRIMARY = "#00d4ff"
    SECONDARY = "#ff6b9d"
    ACCENT = "#c3ff00"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#b0b0b0"
    TEXT_MUTED = "#808080"
    BORDER = "#404040"
    SUCCESS = "#00ff88"
    WARNING = "#ffaa00"
    ERROR = "#ff4757"

    @classmethod
    def get_stylesheet(cls) -> str:
        """Get complete application stylesheet"""
        return f"""
        QMainWindow {{
            background-color: {cls.BACKGROUND};
            color: {cls.TEXT_PRIMARY};
        }}
        
        QTabWidget::pane {{
            border: 1px solid {cls.BORDER};
            background-color: {cls.SURFACE};
            border-radius: 8px;
        }}
        
        QTabBar::tab {{
            background-color: {cls.BACKGROUND};
            color: {cls.TEXT_SECONDARY};
            padding: 12px 20px;
            margin-right: 2px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            min-width: 100px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {cls.PRIMARY};
            color: {cls.BACKGROUND};
            font-weight: bold;
        }}
        
        QTabBar::tab:hover {{
            background-color: {cls.BORDER};
            color: {cls.TEXT_PRIMARY};
        }}
        
        QTextEdit {{
            background-color: {cls.SURFACE};
            color: {cls.TEXT_PRIMARY};
            border: 1px solid {cls.BORDER};
            border-radius: 6px;
            padding: 8px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 12px;
        }}
        
        QLineEdit {{
            background-color: {cls.SURFACE};
            color: {cls.TEXT_PRIMARY};
            border: 2px solid {cls.BORDER};
            border-radius: 6px;
            padding: 8px;
            font-size: 14px;
        }}
        
        QLineEdit:focus {{
            border-color: {cls.PRIMARY};
        }}
        
        QPushButton {{
            background-color: {cls.PRIMARY};
            color: {cls.BACKGROUND};
            border: none;
            border-radius: 6px;
            padding: 10px 16px;
            font-weight: bold;
            font-size: 13px;
        }}
        
        QPushButton:hover {{
            background-color: {cls.SECONDARY};
        }}
        
        QPushButton:pressed {{
            background-color: {cls.ACCENT};
            color: {cls.BACKGROUND};
        }}
        
        QLabel {{
            color: {cls.TEXT_PRIMARY};
        }}
        
        QGroupBox {{
            color: {cls.TEXT_PRIMARY};
            border: 2px solid {cls.BORDER};
            border-radius: 8px;
            margin: 10px 0;
            padding-top: 10px;
            font-weight: bold;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px 0 10px;
            color: {cls.PRIMARY};
        }}
        
        QScrollArea {{
            border: none;
            background-color: {cls.SURFACE};
        }}
        
        QTreeWidget {{
            background-color: {cls.SURFACE};
            color: {cls.TEXT_PRIMARY};
            border: 1px solid {cls.BORDER};
            border-radius: 6px;
            alternate-background-color: {cls.BACKGROUND};
        }}
        
        QTreeWidget::item {{
            padding: 4px;
            border-bottom: 1px solid {cls.BORDER};
        }}
        
        QTreeWidget::item:selected {{
            background-color: {cls.PRIMARY};
            color: {cls.BACKGROUND};
        }}
        
        QListWidget {{
            background-color: {cls.SURFACE};
            color: {cls.TEXT_PRIMARY};
            border: 1px solid {cls.BORDER};
            border-radius: 6px;
        }}
        
        QListWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {cls.BORDER};
        }}
        
        QListWidget::item:selected {{
            background-color: {cls.PRIMARY};
            color: {cls.BACKGROUND};
        }}
        
        QComboBox {{
            background-color: {cls.SURFACE};
            color: {cls.TEXT_PRIMARY};
            border: 1px solid {cls.BORDER};
            border-radius: 6px;
            padding: 6px;
        }}
        
        QProgressBar {{
            background-color: {cls.BACKGROUND};
            border: 1px solid {cls.BORDER};
            border-radius: 6px;
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {cls.PRIMARY};
            border-radius: 6px;
        }}
        
        QStatusBar {{
            background-color: {cls.SURFACE};
            color: {cls.TEXT_SECONDARY};
            border-top: 1px solid {cls.BORDER};
        }}
        """


class MemoryReflectionViewer(QWidget):
    """Visual memory reflection browser with timeline and filtering"""

    def __init__(self):
        super().__init__()
        self.memory = None
        try:
            self.memory = NeuroMemory()
        except Exception as e:
            print(f"Memory system not available: {e}")

        self.setup_ui()
        self.refresh_reflections()

    def setup_ui(self):
        """Setup the memory reflection interface"""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("🧠 Memory Reflection Timeline")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {NeuroTheme.PRIMARY}; margin: 10px 0;")
        layout.addWidget(header)

        # Controls
        controls = QHBoxLayout()

        # Time period selector
        self.period_combo = QComboBox()
        self.period_combo.addItems(
            ["Today", "This Week", "This Month", "All Time", "Last 7 Days", "Last 30 Days"]
        )
        self.period_combo.currentTextChanged.connect(self.filter_by_period)

        # Tag filter
        self.tag_filter = QLineEdit()
        self.tag_filter.setPlaceholderText("🏷️ Filter by tags...")
        self.tag_filter.textChanged.connect(self.filter_by_tags)

        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_reflections)

        controls.addWidget(QLabel("Period:"))
        controls.addWidget(self.period_combo)
        controls.addWidget(QLabel("Tags:"))
        controls.addWidget(self.tag_filter)
        controls.addWidget(self.refresh_btn)
        controls.addStretch()

        layout.addLayout(controls)

        # Reflection display area
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Memory list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        left_layout.addWidget(QLabel("📋 Memory Entries"))
        self.memory_list = QTreeWidget()
        self.memory_list.setHeaderLabels(["Time", "Memory", "Tags", "Category"])
        self.memory_list.itemClicked.connect(self.on_memory_selected)
        left_layout.addWidget(self.memory_list)

        # Right panel - Reflection details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        right_layout.addWidget(QLabel("🔍 Reflection Analysis"))
        self.reflection_display = QTextEdit()
        self.reflection_display.setReadOnly(True)
        right_layout.addWidget(self.reflection_display)

        # Memory statistics
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        self.stats_display.setMaximumHeight(150)
        right_layout.addWidget(QLabel("📊 Memory Statistics"))
        right_layout.addWidget(self.stats_display)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 600])

        layout.addWidget(splitter)

    def refresh_reflections(self):
        """Refresh memory reflections and update display"""
        if not self.memory:
            self.reflection_display.setText("❌ Memory system not available")
            return

        try:
            # Clear existing items
            self.memory_list.clear()

            # Get all memories
            all_memories = self.memory.memory

            # Populate memory list
            for i, memory_entry in enumerate(all_memories):
                item = QTreeWidgetItem()

                timestamp = memory_entry.get("timestamp", "Unknown")
                text = memory_entry.get("text", "No content")
                tags = ", ".join(memory_entry.get("tags", []))
                category = memory_entry.get("category", "general")

                # Format timestamp for display
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00").split("+")[0])
                    formatted_time = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    formatted_time = timestamp[:16] if len(timestamp) > 16 else timestamp

                item.setText(0, formatted_time)
                item.setText(1, text[:50] + "..." if len(text) > 50 else text)
                item.setText(2, tags)
                item.setText(3, category)

                # Store full data
                item.setData(0, Qt.ItemDataRole.UserRole, memory_entry)

                self.memory_list.addTopLevelItem(item)

            # Update statistics
            self.update_memory_statistics()

            # Generate initial reflection
            self.generate_reflection_summary()

        except Exception as e:
            self.reflection_display.setText(f"Error loading reflections: {e}")

    def filter_by_period(self, period_text):
        """Filter memories by time period"""
        if not self.memory:
            return

        try:
            # Map period to time filter
            period_map = {
                "Today": "today",
                "This Week": "this_week",
                "This Month": "this_month",
                "Last 7 Days": "7_days",
                "Last 30 Days": "30_days",
                "All Time": None,
            }

            time_filter = period_map.get(period_text)

            # Clear and repopulate list
            self.memory_list.clear()

            if time_filter:
                filtered_memories = self.memory.recall(time_filter=time_filter)
                # Get full memory entries for filtered memories
                all_memories = self.memory.memory
                filtered_entries = [m for m in all_memories if m.get("text") in filtered_memories]
            else:
                filtered_entries = self.memory.memory

            # Populate with filtered entries
            for memory_entry in filtered_entries:
                item = QTreeWidgetItem()

                timestamp = memory_entry.get("timestamp", "Unknown")
                text = memory_entry.get("text", "No content")
                tags = ", ".join(memory_entry.get("tags", []))
                category = memory_entry.get("category", "general")

                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00").split("+")[0])
                    formatted_time = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    formatted_time = timestamp[:16] if len(timestamp) > 16 else timestamp

                item.setText(0, formatted_time)
                item.setText(1, text[:50] + "..." if len(text) > 50 else text)
                item.setText(2, tags)
                item.setText(3, category)
                item.setData(0, Qt.ItemDataRole.UserRole, memory_entry)

                self.memory_list.addTopLevelItem(item)

            # Update reflection for filtered period
            if time_filter:
                reflection = self.memory.reflection_summary(time_filter)
                self.reflection_display.setText(reflection)

        except Exception as e:
            self.reflection_display.setText(f"Filter error: {e}")

    def filter_by_tags(self, tag_text):
        """Filter memories by tags"""
        if not self.memory or not tag_text:
            self.refresh_reflections()
            return

        try:
            # Search memories by tag
            tag_list = [tag.strip() for tag in tag_text.split(",")]
            filtered_memories = self.memory.recall(tags=tag_list)

            # Clear and show filtered results
            self.memory_list.clear()

            if filtered_memories:
                all_memories = self.memory.memory
                filtered_entries = [m for m in all_memories if m.get("text") in filtered_memories]

                for memory_entry in filtered_entries:
                    item = QTreeWidgetItem()

                    timestamp = memory_entry.get("timestamp", "Unknown")
                    text = memory_entry.get("text", "No content")
                    tags = ", ".join(memory_entry.get("tags", []))
                    category = memory_entry.get("category", "general")

                    try:
                        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00").split("+")[0])
                        formatted_time = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        formatted_time = timestamp[:16] if len(timestamp) > 16 else timestamp

                    item.setText(0, formatted_time)
                    item.setText(1, text[:50] + "..." if len(text) > 50 else text)
                    item.setText(2, tags)
                    item.setText(3, category)
                    item.setData(0, Qt.ItemDataRole.UserRole, memory_entry)

                    self.memory_list.addTopLevelItem(item)

        except Exception as e:
            self.reflection_display.setText(f"Tag filter error: {e}")

    def on_memory_selected(self, item):
        """Handle memory selection and show detailed analysis"""
        try:
            memory_entry = item.data(0, Qt.ItemDataRole.UserRole)
            if not memory_entry:
                return

            # Display detailed memory information
            text = memory_entry.get("text", "No content")
            tags = memory_entry.get("tags", [])
            category = memory_entry.get("category", "general")
            timestamp = memory_entry.get("timestamp", "Unknown")

            # Format detailed view
            details = f"""
📝 **Memory Content:**
{text}

🏷️ **Tags:** {", ".join(tags)}
📂 **Category:** {category}
⏰ **Timestamp:** {timestamp}

🔍 **Analysis:**
• Content length: {len(text)} characters
• Tag count: {len(tags)}
• Category classification: {category}
"""

            # Add contextual analysis if memory system supports it
            if hasattr(self.memory, "patterns") and tags:
                try:
                    patterns = self.memory.patterns()
                    tag_freq = patterns.get("tag_frequency", {})

                    details += "\n📊 **Tag Analysis:**\n"
                    for tag in tags:
                        freq = tag_freq.get(tag, 0)
                        details += f"• {tag}: appears {freq} times in memory\n"

                except:
                    pass

            self.reflection_display.setText(details)

        except Exception as e:
            self.reflection_display.setText(f"Selection error: {e}")

    def update_memory_statistics(self):
        """Update memory statistics display"""
        if not self.memory:
            return

        try:
            stats = self.memory.get_memory_stats()
            self.stats_display.setText(stats)
        except Exception as e:
            self.stats_display.setText(f"Statistics error: {e}")

    def generate_reflection_summary(self):
        """Generate initial reflection summary"""
        if not self.memory:
            return

        try:
            reflection = self.memory.reflection_summary("7_days")
            self.reflection_display.setText(reflection)
        except Exception as e:
            self.reflection_display.setText(f"Reflection error: {e}")


class CodeEditorTab(QWidget):
    """Enhanced code editor with NeuroCode support"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Setup code editor interface"""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("💻 NeuroCode Editor")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {NeuroTheme.PRIMARY}; margin: 10px 0;")
        layout.addWidget(header)

        # Editor controls
        controls = QHBoxLayout()

        self.run_btn = QPushButton("▶️ Run Code")
        self.clear_btn = QPushButton("🗑️ Clear")
        self.load_btn = QPushButton("📁 Load Example")

        controls.addWidget(self.run_btn)
        controls.addWidget(self.clear_btn)
        controls.addWidget(self.load_btn)
        controls.addStretch()

        layout.addLayout(controls)

        # Editor and output
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Code editor
        editor_group = QGroupBox("NeuroCode Input")
        editor_layout = QVBoxLayout(editor_group)

        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", 12))
        self.code_editor.setPlaceholderText(
            '# Enter your NeuroCode here...\nremember("Hello NeuroCode!") as "greeting"'
        )
        editor_layout.addWidget(self.code_editor)

        # Output display
        output_group = QGroupBox("Execution Output")
        output_layout = QVBoxLayout(output_group)

        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.output_display.setFont(QFont("Consolas", 11))
        output_layout.addWidget(self.output_display)

        splitter.addWidget(editor_group)
        splitter.addWidget(output_group)
        splitter.setSizes([300, 200])

        layout.addWidget(splitter)

        # Connect signals
        self.run_btn.clicked.connect(self.execute_code)
        self.clear_btn.clicked.connect(self.clear_editor)
        self.load_btn.clicked.connect(self.load_example)

    def execute_code(self):
        """Execute the NeuroCode in the editor"""
        code = self.code_editor.toPlainText()
        if not code.strip():
            self.output_display.setText("❌ No code to execute")
            return

        try:
            # Try to import and use the NeuroCode interpreter
            from enhanced_interpreter import EnhancedNeuroCodeInterpreter

            interpreter = EnhancedNeuroCodeInterpreter()

            # Execute code line by line
            results = []
            for line in code.split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    try:
                        result = interpreter.execute(line)
                        results.append(f">>> {line}")
                        results.append(f"✅ {result}")
                    except Exception as e:
                        results.append(f">>> {line}")
                        results.append(f"❌ Error: {e}")

            output = "\n".join(results)
            self.output_display.setText(output)

        except ImportError:
            self.output_display.setText("❌ NeuroCode interpreter not available")
        except Exception as e:
            self.output_display.setText(f"❌ Execution error: {e}")

    def clear_editor(self):
        """Clear the code editor"""
        self.code_editor.clear()
        self.output_display.clear()

    def load_example(self):
        """Load an example NeuroCode program"""
        example = """# NeuroCode Memory Example
remember("Python is procedural") as "programming_paradigm"
remember("JavaScript can be functional") as "programming_paradigm"
remember("NeuroCode is cognitive") as "programming_paradigm"

recall tag: "programming_paradigm"

remember("Always backup before self-editing") as "best_practice,safety"
remember("API calls should be rate-limited") as "performance,api"

reflect on tags="programming_paradigm"
memory summary"""

        self.code_editor.setText(example)


class ChatTab(QWidget):
    """AI chat interface tab"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Setup chat interface"""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("💬 AI Chat Assistant")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {NeuroTheme.PRIMARY}; margin: 10px 0;")
        layout.addWidget(header)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setText(
            "🤖 NeuroCode AI Assistant ready! Ask me anything about NeuroCode, memory systems, or programming."
        )
        layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your message here...")
        self.chat_input.returnPressed.connect(self.send_message)

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(self.send_btn)

        layout.addLayout(input_layout)

    def send_message(self):
        """Send chat message"""
        message = self.chat_input.text().strip()
        if not message:
            return

        # Add user message
        self.chat_display.append(f"\n🧑 You: {message}")

        # Generate AI response (simplified)
        response = self.generate_response(message)
        self.chat_display.append(f"🤖 Assistant: {response}")

        # Clear input
        self.chat_input.clear()

    def generate_response(self, message: str) -> str:
        """Generate AI response (simplified implementation)"""
        message_lower = message.lower()

        if "memory" in message_lower:
            return "NeuroCode's memory system is revolutionary! It supports tagging, categories, temporal filtering, and AI-powered reflection. You can store memories with 'remember()' and recall them with 'recall tag:'."

        elif "plugin" in message_lower:
            return "NeuroCode has an extensible plugin system with rich metadata support. Plugins can be categorized, searched, and managed through the UI. Check the Plugins tab for transparency!"

        elif "neurocode" in message_lower:
            return "NeuroCode is an AI-native programming language that bridges human cognition and machine intelligence. It features memory systems, goal tracking, and agent collaboration."

        elif "help" in message_lower:
            return "I can help you with NeuroCode syntax, memory operations, plugin development, or general programming questions. Try asking about specific features!"

        else:
            return f"I understand you're asking about: '{message}'. NeuroCode is designed to be intuitive and powerful. Would you like to know more about memory systems, plugins, or language features?"


class PluginTab(QWidget):
    """Enhanced plugin management tab"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.refresh_plugins()

    def setup_ui(self):
        """Setup plugin management interface"""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("🔌 Plugin Ecosystem")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {NeuroTheme.PRIMARY}; margin: 10px 0;")
        layout.addWidget(header)

        # Controls
        controls = QHBoxLayout()

        self.refresh_btn = QPushButton("🔄 Refresh")
        self.category_filter = QComboBox()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search plugins...")

        controls.addWidget(QLabel("Category:"))
        controls.addWidget(self.category_filter)
        controls.addWidget(QLabel("Search:"))
        controls.addWidget(self.search_box)
        controls.addWidget(self.refresh_btn)
        controls.addStretch()

        layout.addLayout(controls)

        # Plugin display
        self.plugin_display = QTextEdit()
        self.plugin_display.setReadOnly(True)
        layout.addWidget(self.plugin_display)

        # Connect signals
        self.refresh_btn.clicked.connect(self.refresh_plugins)
        self.category_filter.currentTextChanged.connect(self.filter_by_category)
        self.search_box.textChanged.connect(self.search_plugins)

    def refresh_plugins(self):
        """Refresh plugin information"""
        try:
            ui_data = get_plugin_ui_data()

            # Update category filter
            categories = list(ui_data.get("categories", {}).keys())
            self.category_filter.clear()
            self.category_filter.addItem("All Categories")
            self.category_filter.addItems(categories)

            # Display plugins
            self.display_plugins(ui_data)

        except Exception as e:
            self.plugin_display.setText(f"❌ Error loading plugins: {e}")

    def display_plugins(self, ui_data):
        """Display plugin information"""
        html = f"""
        <div style='font-family: Consolas, monospace; color: #e0e0e0;'>
        <h2 style='color: {NeuroTheme.PRIMARY};'>🔌 Plugin Ecosystem</h2>
        
        <div style='background: #2a2a2a; padding: 15px; border-radius: 8px; margin: 10px 0;'>
            <b>📊 Overview:</b><br>
            • Total Plugins: <span style='color: {NeuroTheme.SUCCESS};'>{ui_data.get("total_plugins", 0)}</span><br>
            • Enabled: <span style='color: {NeuroTheme.SUCCESS};'>{ui_data.get("enabled_plugins", 0)}</span><br>
            • Available: <span style='color: {NeuroTheme.SUCCESS};'>{ui_data.get("available_plugins", 0)}</span>
        </div>
        """

        categories = ui_data.get("categories", {})
        for category, plugins in categories.items():
            html += f"<h3 style='color: {NeuroTheme.SECONDARY}; margin-top: 20px;'>📂 {category.title()}</h3>"

            for plugin in plugins:
                status_color = NeuroTheme.SUCCESS if plugin["enabled"] else NeuroTheme.ERROR
                icon = "🟢" if plugin["available"] else "🔴"

                html += f"""
                <div style='background: #2d2d2d; margin: 10px 0; padding: 15px; border-radius: 8px; border-left: 4px solid {status_color};'>
                    <div style='color: #ffffff; font-weight: bold; margin-bottom: 8px;'>
                        {icon} {plugin["name"]} <span style='color: {NeuroTheme.PRIMARY};'>v{plugin["version"]}</span>
                    </div>
                    <div style='color: #cccccc; margin-bottom: 8px;'>{plugin["description"]}</div>
                    <div style='color: #aaaaaa; font-size: 12px;'>
                        👤 {plugin["author"]} | 🎯 {", ".join(plugin["capabilities"])}
                    </div>
                </div>
                """

        html += "</div>"
        self.plugin_display.setHtml(html)

    def filter_by_category(self, category):
        """Filter plugins by category"""
        # Implementation would filter the display based on selected category
        pass

    def search_plugins(self, query):
        """Search plugins by query"""
        # Implementation would filter plugins based on search query
        pass


class AgentTab(QWidget):
    """Agent Reflection Loop interface tab"""

    def __init__(self):
        super().__init__()
        self.agent = None
        self.setup_ui()
        self.initialize_agent()

    def setup_ui(self):
        """Setup agent interface"""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("🤖 Agent Reflection Loop")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {NeuroTheme.PRIMARY}; margin: 10px 0;")
        layout.addWidget(header)

        # Agent controls
        controls = QHBoxLayout()

        self.start_btn = QPushButton("🚀 Start Agent")
        self.stop_btn = QPushButton("🛑 Stop Agent")
        self.stop_btn.setEnabled(False)

        self.status_label = QLabel("⚪ Agent Stopped")
        self.status_label.setStyleSheet(f"color: {NeuroTheme.TEXT_SECONDARY}; font-weight: bold;")

        controls.addWidget(self.start_btn)
        controls.addWidget(self.stop_btn)
        controls.addWidget(self.status_label)
        controls.addStretch()

        layout.addLayout(controls)

        # Agent configuration
        config_group = QGroupBox("🔧 Agent Configuration")
        config_layout = QVBoxLayout(config_group)

        config_row1 = QHBoxLayout()
        config_row1.addWidget(QLabel("Reflection Interval (seconds):"))
        self.interval_input = QLineEdit("30")
        self.interval_input.setMaximumWidth(100)
        config_row1.addWidget(self.interval_input)

        config_row1.addWidget(QLabel("Confidence Threshold:"))
        self.confidence_input = QLineEdit("0.7")
        self.confidence_input.setMaximumWidth(100)
        config_row1.addWidget(self.confidence_input)
        config_row1.addStretch()

        config_layout.addLayout(config_row1)
        layout.addWidget(config_group)

        # Agent activity display
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Agent status and insights
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        left_layout.addWidget(QLabel("📊 Agent Status"))
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        self.status_display.setMaximumHeight(150)
        left_layout.addWidget(self.status_display)

        left_layout.addWidget(QLabel("🔍 Recent Insights"))
        self.insights_list = QListWidget()
        left_layout.addWidget(self.insights_list)

        # Right panel - Suggestions and actions
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        right_layout.addWidget(QLabel("💡 Agent Suggestions"))
        self.suggestions_display = QTextEdit()
        self.suggestions_display.setReadOnly(True)
        right_layout.addWidget(self.suggestions_display)

        # Manual action buttons
        action_controls = QHBoxLayout()
        self.execute_btn = QPushButton("▶️ Execute Suggestion")
        self.approve_btn = QPushButton("✅ Approve")
        self.reject_btn = QPushButton("❌ Reject")

        self.execute_btn.setEnabled(False)
        self.approve_btn.setEnabled(False)
        self.reject_btn.setEnabled(False)

        action_controls.addWidget(self.execute_btn)
        action_controls.addWidget(self.approve_btn)
        action_controls.addWidget(self.reject_btn)
        action_controls.addStretch()

        right_layout.addLayout(action_controls)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 600])

        layout.addWidget(splitter)

        # Connect signals
        self.start_btn.clicked.connect(self.start_agent)
        self.stop_btn.clicked.connect(self.stop_agent)
        self.execute_btn.clicked.connect(self.execute_current_suggestion)
        self.approve_btn.clicked.connect(self.approve_suggestion)
        self.reject_btn.clicked.connect(self.reject_suggestion)

        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_display)
        self.status_timer.start(2000)  # Update every 2 seconds

        # Current suggestion tracking
        self.current_suggestion = None
        self.current_neurocode = ""

    def initialize_agent(self):
        """Initialize the agent reflection loop"""
        try:
            # Import here to avoid circular imports
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from agent_reflection_loop import AgentReflectionLoop

            self.agent = AgentReflectionLoop()

            # Set up UI callbacks
            self.agent.set_ui_callbacks(
                on_insight=self.on_agent_insight,
                on_suggestion=self.on_agent_suggestion,
                on_action=self.on_agent_action,
            )

            self.status_display.setText("🤖 Agent initialized and ready")

        except Exception as e:
            self.status_display.setText(f"❌ Failed to initialize agent: {e}")

    def start_agent(self):
        """Start the agent reflection loop"""
        if not self.agent:
            self.status_display.setText("❌ Agent not available")
            return

        # Update configuration
        try:
            interval = float(self.interval_input.text())
            confidence = float(self.confidence_input.text())

            self.agent.update_config(
                {"reflection_interval": interval, "confidence_threshold": confidence}
            )
        except ValueError:
            self.status_display.setText("❌ Invalid configuration values")
            return

        # Start the agent
        self.agent.start()

        # Update UI
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("🟢 Agent Running")
        self.status_label.setStyleSheet(f"color: {NeuroTheme.SUCCESS}; font-weight: bold;")

        self.suggestions_display.setText("🤖 Agent started! Waiting for first reflection cycle...")

    def stop_agent(self):
        """Stop the agent reflection loop"""
        if self.agent:
            self.agent.stop()

        # Update UI
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("🔴 Agent Stopped")
        self.status_label.setStyleSheet(f"color: {NeuroTheme.ERROR}; font-weight: bold;")

        self.suggestions_display.append("\n🛑 Agent stopped by user")

    def update_status_display(self):
        """Update the agent status display"""
        if not self.agent:
            return

        try:
            status = self.agent.get_status()

            status_text = f"""🤖 Agent Status Report
━━━━━━━━━━━━━━━━━━━━━━━━
📊 Running: {status["is_running"]}
🔄 Reflection Cycles: {status["reflection_count"]}
💡 Suggestions Made: {status["suggestions_made"]}
⚡ Actions Taken: {status["actions_taken"]}
⏰ Last Reflection: {status["last_reflection"] or "Never"}

⚙️ Configuration:
   • Interval: {status["config"]["reflection_interval"]}s
   • Confidence Threshold: {status["config"]["confidence_threshold"]}
   • Auto-execute Threshold: {status["config"]["auto_execute_threshold"]}"""

            self.status_display.setText(status_text)

        except Exception as e:
            self.status_display.setText(f"❌ Status update error: {e}")

    def on_agent_insight(self, insight):
        """Handle new insights from the agent"""
        insight_text = (
            f"🔍 {insight.get('type', 'unknown')}: {insight.get('message', 'No message')}"
        )

        # Add to insights list
        item = QListWidgetItem(insight_text)
        confidence = insight.get("confidence", 0)

        if confidence > 0.8:
            item.setBackground(QColor(NeuroTheme.SUCCESS))
        elif confidence > 0.6:
            item.setBackground(QColor(NeuroTheme.WARNING))
        else:
            item.setBackground(QColor(NeuroTheme.TEXT_MUTED))

        self.insights_list.insertItem(0, item)

        # Keep only recent insights
        while self.insights_list.count() > 20:
            self.insights_list.takeItem(self.insights_list.count() - 1)

    def on_agent_suggestion(self, neurocode, confidence):
        """Handle new suggestions from the agent"""
        suggestion_text = f"""
🤖 New Agent Suggestion (Confidence: {confidence:.1f})
{"═" * 50}
{neurocode}
{"═" * 50}

💭 Confidence Level: {confidence:.1f}
🎯 Auto-execute: {"Yes" if confidence >= 0.9 else "No"}
⏰ Generated: {datetime.now().strftime("%H:%M:%S")}
"""

        self.suggestions_display.append(suggestion_text)

        # Store current suggestion for manual execution
        self.current_suggestion = suggestion_text
        self.current_neurocode = neurocode

        # Enable action buttons for manual approval
        if confidence < 0.9:  # Not auto-executed
            self.execute_btn.setEnabled(True)
            self.approve_btn.setEnabled(True)
            self.reject_btn.setEnabled(True)

    def on_agent_action(self, neurocode, success):
        """Handle actions taken by the agent"""
        action_text = f"""
⚡ Agent Action {"✅ EXECUTED" if success else "❌ FAILED"}
{"═" * 50}
{neurocode}
{"═" * 50}
"""

        self.suggestions_display.append(action_text)

    def execute_current_suggestion(self):
        """Execute the current suggestion manually"""
        if not self.current_neurocode:
            return

        try:
            # Import and use the standalone runner
            from neuro_runner_standalone import StandaloneNeuroRunner

            runner = StandaloneNeuroRunner(verbose=False)

            # Create temporary file
            temp_file = Path(__file__).parent.parent / "temp_manual_suggestion.neuro"
            temp_file.write_text(self.current_neurocode, encoding="utf-8")

            # Execute
            results = runner.run_file(str(temp_file))

            # Clean up
            if temp_file.exists():
                temp_file.unlink()

            # Show result
            success = results.get("success", False)
            self.suggestions_display.append(
                f"\n{'✅ Manual execution successful' if success else '❌ Manual execution failed'}"
            )

        except Exception as e:
            self.suggestions_display.append(f"\n❌ Manual execution error: {e}")

        # Disable action buttons
        self.execute_btn.setEnabled(False)
        self.approve_btn.setEnabled(False)
        self.reject_btn.setEnabled(False)

    def approve_suggestion(self):
        """Approve the current suggestion (store for future use)"""
        self.suggestions_display.append("\n✅ Suggestion approved by user")
        self.execute_btn.setEnabled(False)
        self.approve_btn.setEnabled(False)
        self.reject_btn.setEnabled(False)

    def reject_suggestion(self):
        """Reject the current suggestion"""
        self.suggestions_display.append("\n❌ Suggestion rejected by user")
        self.execute_btn.setEnabled(False)
        self.approve_btn.setEnabled(False)
        self.reject_btn.setEnabled(False)


class NeuroUI(QMainWindow):
    """Main NeuroCode UI with tabbed interface"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Setup the main UI with tabbed interface"""
        self.setWindowTitle("🧬 NeuroCode - Enhanced UI")
        self.setMinimumSize(1200, 800)

        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Create tab widget
        self.tab_widget = QTabWidget()

        # Add tabs
        self.chat_tab = ChatTab()
        self.code_tab = CodeEditorTab()
        self.memory_tab = MemoryReflectionViewer()
        self.plugin_tab = PluginTab()
        self.agent_tab = AgentTab()

        self.tab_widget.addTab(self.chat_tab, "💬 Chat")
        self.tab_widget.addTab(self.code_tab, "💻 Code")
        self.tab_widget.addTab(self.memory_tab, "🧠 Memory")
        self.tab_widget.addTab(self.plugin_tab, "🔌 Plugins")
        self.tab_widget.addTab(self.agent_tab, "🤖 Agent")

        layout.addWidget(self.tab_widget)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("NeuroCode Enhanced UI Ready")

    def apply_theme(self):
        """Apply the modern theme"""
        self.setStyleSheet(NeuroTheme.get_stylesheet())


def main():
    """Launch the NeuroCode Enhanced UI"""
    if not QT_AVAILABLE:
        print("❌ Qt not available. Please install PySide6 or PyQt6.")
        return

    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("NeuroCode Enhanced UI")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("NeuroCode Project")

    # Create and show main window
    window = NeuroUI()
    window.show()

    # Start the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
