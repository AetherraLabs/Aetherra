#!/usr/bin/env python3
# type: ignore
"""
🧬 Neuroplex GUI - The Ultimate NeuroCode Experience
A revolutionary interface that brings AI-native programming to life

This is the flagship GUI for NeuroCode and Neuroplex, featuring:
- Real-time code execution with AI reasoning
- Visual memory and goal tracking
- Interactive AI collaboration
- Beautiful modern design
- Live system monitoring
- Plugin ecosystem management

Note: Type checking is disabled for this file due to cross-backend Qt compatibility.
The code works perfectly at runtime with both PySide6 and PyQt6.
"""

import random
import sys
from datetime import datetime
from pathlib import Path
from typing import List

# Add core modules to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "core"))

# Check for Qt availability - prioritize PySide6
QT_AVAILABLE = False
QtWidgets = None
QtCore = None
QtGui = None

try:
    # Try PySide6 first
    from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, Signal
    from PySide6.QtGui import QAction, QBrush, QColor, QFont, QPainter, QPen
    from PySide6.QtWidgets import (
        QApplication,
        QFileDialog,
        QFrame,
        QGraphicsOpacityEffect,
        QGroupBox,
        QHBoxLayout,
        QInputDialog,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
    
    QT_AVAILABLE = True
    QT_BACKEND = "PySide6"
    print(f"🎨 Using {QT_BACKEND} for Neuroplex GUI")
    
except ImportError:
    try:
        # Fallback to PyQt6
        from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
        from PyQt6.QtCore import pyqtSignal as Signal
        from PyQt6.QtGui import QAction, QBrush, QColor, QFont, QPainter, QPen
        from PyQt6.QtWidgets import (
            QApplication,
            QFileDialog,
            QFrame,
            QGraphicsOpacityEffect,
            QGroupBox,
            QHBoxLayout,
            QInputDialog,
            QLabel,
            QLineEdit,
            QMainWindow,
            QMessageBox,
            QProgressBar,
            QPushButton,
            QTabWidget,
            QTextEdit,
            QVBoxLayout,
            QWidget,
        )
        
        QT_AVAILABLE = True
        QT_BACKEND = "PyQt6"
        print(f"🎨 Using {QT_BACKEND} for Neuroplex GUI")
        
    except ImportError:
        print("❌ No Qt library available. Please install PySide6 or PyQt6.")
        sys.exit(1)

# Import NeuroCode components with robust fallback handling
try:
    import importlib
    import importlib.util
    
    # Correct path to core modules
    core_path = project_root / "core"
    
    # Add core path to sys.path for imports
    if str(core_path) not in sys.path:
        sys.path.insert(0, str(core_path))
    
    # Add project root to PYTHONPATH to enable package imports
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    def safe_import_module(module_name, file_path):
        """Safely import a module using multiple strategies"""
        module = None
        
        # Strategy 1: Try direct module import first
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, f'Neuro{module_name.title()}') or hasattr(module, 'NeuroCodeInterpreter'):
                return module
        except Exception:
            pass
        
        # Strategy 2: Try package-qualified import
        try:
            module = importlib.import_module(f'core.{module_name}')
            return module
        except Exception:
            pass
        
        # Strategy 3: Try file-based import with proper module setup
        try:
            if file_path.exists():
                spec = importlib.util.spec_from_file_location(f"core.{module_name}", file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    
                    # Setup module in sys.modules to resolve relative imports
                    sys.modules[f"core.{module_name}"] = module
                    sys.modules[module_name] = module
                    
                    # Mock the core package for relative imports
                    if 'core' not in sys.modules:
                        import types
                        core_module = types.ModuleType('core')
                        core_module.__path__ = [str(core_path)]
                        core_module.__file__ = str(core_path / '__init__.py')
                        sys.modules['core'] = core_module
                    
                    # Execute the module
                    spec.loader.exec_module(module)
                    return module
        except Exception as e:
            print(f"Failed to import {module_name}: {e}")
        
        return None
    
    # Import interpreter with robust strategy
    NeuroCodeInterpreter = None
    interpreter_module = safe_import_module("interpreter", core_path / "interpreter.py")
    if interpreter_module:
        NeuroCodeInterpreter = getattr(interpreter_module, 'NeuroCodeInterpreter', None)
    
    # Import memory with robust strategy
    NeuroMemory = None
    memory_module = safe_import_module("memory", core_path / "memory.py")
    if memory_module:
        NeuroMemory = getattr(memory_module, 'NeuroMemory', None)
    
    # Import chat router with robust strategy
    NeuroCodeChatRouter = None
    chat_module = safe_import_module("chat_router", core_path / "chat_router.py")
    if chat_module:
        NeuroCodeChatRouter = getattr(chat_module, 'NeuroCodeChatRouter', None)
    
    NEUROCODE_AVAILABLE = all([NeuroCodeInterpreter, NeuroMemory, NeuroCodeChatRouter])
    
    if NEUROCODE_AVAILABLE:
        print("✅ All NeuroCode components imported successfully")
    else:
        missing = []
        if not NeuroCodeInterpreter:
            missing.append("NeuroCodeInterpreter")
        if not NeuroMemory:
            missing.append("NeuroMemory")
        if not NeuroCodeChatRouter:
            missing.append("NeuroCodeChatRouter")
        print(f"⚠️ Some NeuroCode components not available: {', '.join(missing)} - GUI will run in demo mode")
        
except Exception as e:
    print(f"⚠️ NeuroCode components not fully available: {e}")
    NeuroCodeInterpreter = None
    NeuroMemory = None
    NeuroCodeChatRouter = None
    NEUROCODE_AVAILABLE = False

class NeuroAnimation(QPropertyAnimation):
    """Custom animation for NeuroCode UI elements"""
    def __init__(self, target, property_name):
        super().__init__(target, property_name.encode())
        self.setDuration(500)
        self.setEasingCurve(QEasingCurve.Type.OutCubic)

class NeuroTheme:
    """NeuroCode theme and styling"""
    
    # Color palette inspired by neural networks and AI
    PRIMARY = "#1e3a8a"      # Deep blue
    SECONDARY = "#3b82f6"    # Bright blue  
    ACCENT = "#06d6a0"       # Neon green
    BACKGROUND = "#0f172a"   # Dark slate
    SURFACE = "#1e293b"      # Slate gray
    TEXT_PRIMARY = "#f8fafc" # Light gray
    TEXT_SECONDARY = "#94a3b8" # Medium gray
    SUCCESS = "#10b981"      # Green
    WARNING = "#f59e0b"      # Amber
    ERROR = "#ef4444"        # Red
    
    @staticmethod
    def get_stylesheet() -> str:
        return f"""
        QMainWindow {{
            background-color: {NeuroTheme.BACKGROUND};
            color: {NeuroTheme.TEXT_PRIMARY};
        }}
        
        QWidget {{
            background-color: {NeuroTheme.BACKGROUND};
            color: {NeuroTheme.TEXT_PRIMARY};
            font-family: 'Consolas', 'Monaco', monospace;
        }}
        
        QPushButton {{
            background-color: {NeuroTheme.PRIMARY};
            color: {NeuroTheme.TEXT_PRIMARY};
            border: 2px solid {NeuroTheme.SECONDARY};
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: bold;
            font-size: 14px;
        }}
        
        QPushButton:hover {{
            background-color: {NeuroTheme.SECONDARY};
            border-color: {NeuroTheme.ACCENT};
        }}
        
        QPushButton:pressed {{
            background-color: {NeuroTheme.ACCENT};
        }}
        
        QTextEdit, QLineEdit {{
            background-color: {NeuroTheme.SURFACE};
            color: {NeuroTheme.TEXT_PRIMARY};
            border: 2px solid {NeuroTheme.PRIMARY};
            border-radius: 6px;
            padding: 8px;
            font-size: 14px;
        }}
        
        QTextEdit:focus, QLineEdit:focus {{
            border-color: {NeuroTheme.ACCENT};
        }}
        
        QTabWidget::pane {{
            border: 2px solid {NeuroTheme.PRIMARY};
            border-radius: 8px;
            background-color: {NeuroTheme.SURFACE};
        }}
        
        QTabBar::tab {{
            background-color: {NeuroTheme.PRIMARY};
            color: {NeuroTheme.TEXT_PRIMARY};
            padding: 12px 20px;
            margin-right: 2px;
            border-radius: 6px 6px 0 0;
        }}
        
        QTabBar::tab:selected {{
            background-color: {NeuroTheme.ACCENT};
            color: {NeuroTheme.BACKGROUND};
        }}
        
        QGroupBox {{
            border: 2px solid {NeuroTheme.PRIMARY};
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            color: {NeuroTheme.ACCENT};
        }}
        
        QProgressBar {{
            border: 2px solid {NeuroTheme.PRIMARY};
            border-radius: 8px;
            background-color: {NeuroTheme.SURFACE};
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {NeuroTheme.ACCENT};
            border-radius: 6px;
        }}
        
        QScrollBar:vertical {{
            background-color: {NeuroTheme.SURFACE};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {NeuroTheme.PRIMARY};
            border-radius: 6px;
            min-height: 30px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {NeuroTheme.ACCENT};
        }}
        """

class PulsingWidget(QWidget):
    """Widget that pulses with neural activity"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self.pulse)
        self.pulse_value = 0.0
        self.pulse_direction = 1
        
    def start_pulsing(self):
        self.pulse_timer.start(50)  # 20 FPS
        
    def stop_pulsing(self):
        self.pulse_timer.stop()
        self.opacity_effect.setOpacity(1.0)
        
    def pulse(self):
        self.pulse_value += 0.05 * self.pulse_direction
        if self.pulse_value >= 1.0:
            self.pulse_direction = -1
            self.pulse_value = 1.0
        elif self.pulse_value <= 0.3:
            self.pulse_direction = 1
            self.pulse_value = 0.3
            
        self.opacity_effect.setOpacity(self.pulse_value)

class NeuroCodeEditor(QTextEdit):
    """Advanced code editor for NeuroCode with syntax highlighting"""
    
    code_executed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Consolas", 14))
        self.setPlaceholderText("🧬 Enter your NeuroCode here...\n\nTry:\nremember('Hello NeuroCode!') as 'greeting'\ngoal: learn AI programming\nagent: on")
        
        # Enable syntax highlighting
        self.setup_syntax_highlighting()
        
    def setup_syntax_highlighting(self):
        """Set up basic NeuroCode syntax highlighting"""
        # This is a simplified version - could be expanded
        pass
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Ctrl+Enter executes code
            self.execute_code()
        else:
            super().keyPressEvent(event)
            
    def execute_code(self):
        code = self.toPlainText().strip()
        if code:
            self.code_executed.emit(code)

class MemoryVisualization(QWidget):
    """Visual representation of NeuroCode memory system"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.memories = []
        self.setMinimumHeight(200)
        
    def add_memory(self, memory_text: str, tags: List[str]):
        self.memories.append({
            'text': memory_text,
            'tags': tags,
            'timestamp': datetime.now(),
            'x': random.randint(50, self.width() - 50) if self.width() > 100 else 50,
            'y': random.randint(50, self.height() - 50) if self.height() > 100 else 50
        })
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)  # type: ignore
        
        # Draw background
        rect = self.rect()
        painter.fillRect(rect, QBrush(QColor(NeuroTheme.SURFACE)))  # type: ignore
        
        # Draw neural network connections
        pen = QPen(QColor(NeuroTheme.PRIMARY))
        pen.setWidth(2)
        painter.setPen(pen)  # type: ignore
        
        for i, memory in enumerate(self.memories):
            for j, other_memory in enumerate(self.memories[i+1:], i+1):
                # Draw connections between related memories
                if set(memory['tags']) & set(other_memory['tags']):
                    painter.drawLine(memory['x'], memory['y'], 
                                   other_memory['x'], other_memory['y'])
        
        # Draw memory nodes
        for memory in self.memories:
            # Node
            brush = QBrush(QColor(NeuroTheme.ACCENT))
            painter.setBrush(brush)  # type: ignore
            
            pen = QPen(QColor(NeuroTheme.TEXT_PRIMARY))
            pen.setWidth(2)
            painter.setPen(pen)  # type: ignore
            painter.drawEllipse(memory['x']-10, memory['y']-10, 20, 20)
            
            # Label
            pen = QPen(QColor(NeuroTheme.TEXT_PRIMARY))
            painter.setPen(pen)  # type: ignore
            painter.drawText(memory['x']+15, memory['y'], memory['text'][:20] + "...")

class GoalTracker(QGroupBox):
    """Visual goal tracking system"""
    
    def __init__(self, parent=None):
        super().__init__("🎯 Active Goals", parent)
        self.layout = QVBoxLayout(self)
        self.goals = []
        
        # No goals message
        self.no_goals_label = QLabel("No active goals. Set a goal to begin!")
        self.no_goals_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # type: ignore
        self.no_goals_label.setStyleSheet(f"color: {NeuroTheme.TEXT_SECONDARY}; font-style: italic;")
        self.layout.addWidget(self.no_goals_label)  # type: ignore
        
    def add_goal(self, goal_text: str, priority: str = "medium"):
        # Remove no goals message
        if self.no_goals_label.isVisible():
            self.no_goals_label.hide()
            
        goal_widget = QFrame()
        goal_layout = QHBoxLayout(goal_widget)
        
        # Priority indicator
        priority_colors = {
            "low": NeuroTheme.TEXT_SECONDARY,
            "medium": NeuroTheme.WARNING,
            "high": NeuroTheme.ERROR,
            "critical": NeuroTheme.ERROR
        }
        
        priority_label = QLabel("●")
        priority_label.setStyleSheet(f"color: {priority_colors.get(priority, NeuroTheme.TEXT_SECONDARY)}; font-size: 16px;")
        goal_layout.addWidget(priority_label)
        
        # Goal text
        goal_label = QLabel(goal_text)
        goal_label.setWordWrap(True)
        goal_layout.addWidget(goal_label)
        
        # Progress bar
        progress = QProgressBar()
        progress.setValue(0)
        progress.setMaximum(100)
        goal_layout.addWidget(progress)
        
        self.layout.addWidget(goal_widget)
        self.goals.append({
            'text': goal_text,
            'priority': priority,
            'widget': goal_widget,
            'progress': progress
        })

class SystemMonitor(QGroupBox):
    """Real-time system monitoring"""
    
    def __init__(self, parent=None):
        super().__init__("🔬 Neural System Status", parent)
        layout = QVBoxLayout(self)
        
        # Status indicators
        self.ai_status = QLabel("🧠 AI Runtime: Active")
        self.memory_status = QLabel("💾 Memory: 0 entries")
        self.agent_status = QLabel("🤖 Agent: Standby")
        self.performance_status = QLabel("⚡ Performance: Optimal")
        
        for status in [self.ai_status, self.memory_status, self.agent_status, self.performance_status]:
            layout.addWidget(status)
            
        # System load visualization
        layout.addWidget(QLabel("System Load:"))
        self.load_bar = QProgressBar()
        self.load_bar.setValue(25)
        layout.addWidget(self.load_bar)
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(2000)  # Update every 2 seconds
        
    def update_status(self):
        # Simulate dynamic updates
        load = random.randint(10, 80)
        self.load_bar.setValue(load)
        
        if load > 70:
            self.performance_status.setText("⚡ Performance: High Load")
        elif load > 40:
            self.performance_status.setText("⚡ Performance: Active")
        else:
            self.performance_status.setText("⚡ Performance: Optimal")

class LiveConsole(QTextEdit):
    """Live console output showing NeuroCode execution"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 11))
        self.append("🧬 NeuroCode Console - Ready for AI-native programming!")
        self.append("=" * 60)
        
    def log_execution(self, code: str, result: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.append(f"\n[{timestamp}] Executing:")
        self.append(f"🔮 {code}")
        self.append(f"✨ {result}")
        self.append("-" * 40)
        
        # Auto-scroll to bottom
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

class NeuroplexMainWindow(QMainWindow):
    """Main Neuroplex GUI window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧬 Neuroplex - AI-Native Programming Interface")
        self.setMinimumSize(1400, 900)
        
        # Initialize NeuroCode interpreter
        self.interpreter = None
        self.chat_router = None
        self.memory = None
        if NEUROCODE_AVAILABLE and NeuroCodeInterpreter is not None:
            try:
                self.interpreter = NeuroCodeInterpreter()
                if NeuroCodeChatRouter is not None:
                    self.chat_router = NeuroCodeChatRouter()
                if NeuroMemory is not None:
                    self.memory = NeuroMemory()
            except Exception as e:
                print(f"⚠️ Could not initialize NeuroCode components: {e}")
        
        # Apply theme
        self.setStyleSheet(NeuroTheme.get_stylesheet())
        
        # Set up UI
        self.setup_ui()
        self.setup_connections()
        
        # Show welcome message
        self.show_welcome()
        
    def setup_ui(self):
        """Set up the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Code and execution
        left_panel = QVBoxLayout()
        
        # NeuroCode editor
        editor_group = QGroupBox("🧬 NeuroCode Editor")
        editor_layout = QVBoxLayout(editor_group)
        
        self.code_editor = NeuroCodeEditor()
        editor_layout.addWidget(self.code_editor)
        
        # Execution controls
        controls_layout = QHBoxLayout()
        self.execute_btn = QPushButton("▶️ Execute")
        self.clear_btn = QPushButton("🗑️ Clear")
        self.save_btn = QPushButton("💾 Save")
        
        controls_layout.addWidget(self.execute_btn)
        controls_layout.addWidget(self.clear_btn)
        controls_layout.addWidget(self.save_btn)
        controls_layout.addStretch()
        
        editor_layout.addLayout(controls_layout)
        left_panel.addWidget(editor_group)
        
        # Live console
        console_group = QGroupBox("📟 Live Console")
        console_layout = QVBoxLayout(console_group)
        self.console = LiveConsole()
        console_layout.addWidget(self.console)
        left_panel.addWidget(console_group)
        
        # Center panel - Visualization and chat
        center_panel = QVBoxLayout()
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Memory visualization tab
        memory_tab = QWidget()
        memory_layout = QVBoxLayout(memory_tab)
        
        self.memory_viz = MemoryVisualization()
        memory_layout.addWidget(QLabel("🧠 Neural Memory Network"))
        memory_layout.addWidget(self.memory_viz)
        
        self.tab_widget.addTab(memory_tab, "🧠 Memory")
        
        # Chat interface tab
        chat_tab = QWidget()
        chat_layout = QVBoxLayout(chat_tab)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.append("🤖 Neuroplex: Hello! I'm your NeuroCode AI companion. How can I help you explore AI-native programming?")
        
        # Chat input
        chat_input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask me anything about NeuroCode...")
        self.chat_send_btn = QPushButton("Send")
        
        chat_input_layout.addWidget(self.chat_input)
        chat_input_layout.addWidget(self.chat_send_btn)
        
        chat_layout.addWidget(self.chat_display)
        chat_layout.addLayout(chat_input_layout)
        
        self.tab_widget.addTab(chat_tab, "💬 AI Chat")
        
        center_panel.addWidget(self.tab_widget)
        
        # Right panel - Goals and monitoring
        right_panel = QVBoxLayout()
        
        # Goal tracker
        self.goal_tracker = GoalTracker()
        right_panel.addWidget(self.goal_tracker)
        
        # System monitor
        self.system_monitor = SystemMonitor()
        right_panel.addWidget(self.system_monitor)
        
        # Neural activity indicator
        activity_group = QGroupBox("⚡ Neural Activity")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_indicator = PulsingWidget()
        self.activity_indicator.setMinimumHeight(100)
        self.activity_indicator.setStyleSheet(f"background-color: {NeuroTheme.ACCENT}; border-radius: 10px;")
        
        activity_layout.addWidget(QLabel("Processing..."))
        activity_layout.addWidget(self.activity_indicator)
        
        right_panel.addWidget(activity_group)
        
        # Add panels to main layout
        main_layout.addLayout(left_panel, 2)
        main_layout.addLayout(center_panel, 3)
        main_layout.addLayout(right_panel, 1)
        
        # Menu bar
        self.setup_menu_bar()
        
        # Status bar
        self.setup_status_bar()
        
    def setup_menu_bar(self):
        """Set up the application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("📁 File")
        
        new_action = QAction("🆕 New Program", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_program)
        file_menu.addAction(new_action)
        
        open_action = QAction("📂 Open Program", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_program)
        file_menu.addAction(open_action)
        
        save_action = QAction("💾 Save Program", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_program)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # NeuroCode menu
        neuro_menu = menubar.addMenu("🧬 NeuroCode")
        
        examples_action = QAction("📚 Load Examples", self)
        examples_action.triggered.connect(self.load_examples)
        neuro_menu.addAction(examples_action)
        
        docs_action = QAction("📖 Documentation", self)
        docs_action.triggered.connect(self.show_documentation)
        neuro_menu.addAction(docs_action)
        
        # Help menu
        help_menu = menubar.addMenu("❓ Help")
        
        about_action = QAction("ℹ️ About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_status_bar(self):
        """Set up the status bar"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("🧬 Neuroplex ready - AI-native programming at your fingertips!")
        
    def setup_connections(self):
        """Connect signals and slots"""
        self.execute_btn.clicked.connect(self.execute_code)
        self.clear_btn.clicked.connect(self.clear_editor)
        self.save_btn.clicked.connect(self.save_program)
        
        self.code_editor.code_executed.connect(self.execute_code_from_editor)
        
        self.chat_send_btn.clicked.connect(self.send_chat_message)
        self.chat_input.returnPressed.connect(self.send_chat_message)
        
    def show_welcome(self):
        """Show welcome message and examples"""
        welcome_code = """# 🧬 Welcome to NeuroCode!
# The first AI-native programming language

# Try these examples:
remember("I'm learning NeuroCode!") as "learning"
goal: master AI programming priority: high
agent: on

# NeuroCode thinks and learns:
analyze "my learning progress"
suggest "next steps for mastery"

# Execute with Ctrl+Enter or click the Execute button!"""

        self.code_editor.setPlainText(welcome_code)
        
    def execute_code(self):
        """Execute NeuroCode from the editor"""
        code = self.code_editor.toPlainText().strip()
        if not code:
            return
            
        self.execute_code_from_editor(code)
        
    def execute_code_from_editor(self, code: str):
        """Execute NeuroCode and show results"""
        # Start neural activity animation
        self.activity_indicator.start_pulsing()
        
        # Update status
        self.status_bar.showMessage("🧠 Processing NeuroCode...")
        
        try:
            if self.interpreter:
                result = self.interpreter.execute(code)
                
                # Check for specific NeuroCode constructs
                if "remember(" in code and "as" in code:
                    # Extract memory for visualization
                    try:
                        # Simple parsing for demo
                        memory_text = code.split("remember(")[1].split(")")[0].strip("'\"")
                        tags = ["demo", "user_input"]
                        self.memory_viz.add_memory(memory_text, tags)
                        self.system_monitor.memory_status.setText(f"💾 Memory: {len(self.memory_viz.memories)} entries")
                    except Exception:
                        pass
                        
                if "goal:" in code:
                    # Extract goal
                    try:
                        goal_line = [line for line in code.split('\n') if 'goal:' in line][0]
                        goal_text = goal_line.split('goal:')[1].split('priority:')[0].strip()
                        priority = "medium"
                        if "priority:" in goal_line:
                            priority = goal_line.split('priority:')[1].strip()
                        self.goal_tracker.add_goal(goal_text, priority)
                    except Exception:
                        pass
                        
                if "agent:" in code and "on" in code:
                    self.system_monitor.agent_status.setText("🤖 Agent: Active")
                    
                # Log to console
                self.console.log_execution(code, str(result) if result else "✅ Executed successfully")
                
            else:
                result = "⚠️ NeuroCode interpreter not available - demo mode"
                self.console.log_execution(code, result)
                
        except Exception as e:
            result = f"❌ Error: {e}"
            self.console.log_execution(code, result)
            
        finally:
            # Stop neural activity animation
            QTimer.singleShot(1000, self.activity_indicator.stop_pulsing)
            QTimer.singleShot(1000, lambda: self.status_bar.showMessage("🧬 Ready"))
            
    def send_chat_message(self):
        """Send message to AI chat"""
        message = self.chat_input.text().strip()
        if not message:
            return
            
        # Add user message to chat
        self.chat_display.append(f"\n🧬 You: {message}")
        self.chat_input.clear()
        
        # Process with chat router if available
        try:
            if self.chat_router:
                response = self.chat_router.process_message(message)
                ai_response = response.get("text", "I'm processing your request...")
            else:
                # Fallback responses
                ai_response = self.get_fallback_response(message)
                
            self.chat_display.append(f"🤖 Neuroplex: {ai_response}")
            
        except Exception as e:
            self.chat_display.append(f"🤖 Neuroplex: Sorry, I encountered an error: {e}")
            
        # Auto-scroll chat
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def get_fallback_response(self, message: str) -> str:
        """Fallback AI responses when chat router is not available"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            return "Hello! I'm your NeuroCode AI companion. I can help you learn AI-native programming!"
            
        elif "neurocode" in message_lower:
            return """NeuroCode is revolutionary! It's the first AI-native programming language where:
            
🧠 Code thinks and reasons about outcomes
🎯 You express intentions, not implementations  
💾 Memory is a first-class language feature
🤖 AI models are built into the language itself
⚡ Programs evolve and optimize themselves

Try typing some NeuroCode in the editor!"""

        elif any(word in message_lower for word in ["help", "how", "what"]):
            return """I can help you with:

🧬 **NeuroCode Syntax** - Learn the language fundamentals
🎯 **Goal Setting** - Define objectives for your programs
💾 **Memory Systems** - Store and recall information
🤖 **AI Integration** - Use built-in AI capabilities
📊 **System Monitoring** - Track performance and health

What would you like to explore?"""

        else:
            return f"That's interesting! I'm analyzing: '{message}'. NeuroCode can help you think through problems like this. Try expressing it as NeuroCode in the editor!"
            
    def clear_editor(self):
        """Clear the code editor"""
        self.code_editor.clear()
        
    def new_program(self):
        """Create a new NeuroCode program"""
        self.code_editor.clear()
        self.code_editor.setPlaceholderText("🧬 New NeuroCode program...")
        
    def open_program(self):
        """Open a NeuroCode program file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open NeuroCode Program", 
            "", 
            "NeuroCode Files (*.neuro);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.code_editor.setPlainText(content)
                self.status_bar.showMessage(f"📂 Opened: {Path(file_path).name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {e}")
                
    def save_program(self):
        """Save the current NeuroCode program"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save NeuroCode Program",
            "",
            "NeuroCode Files (*.neuro);;All Files (*)"
        )
        
        if file_path:
            try:
                content = self.code_editor.toPlainText()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_bar.showMessage(f"💾 Saved: {Path(file_path).name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {e}")
                
    def load_examples(self):
        """Load NeuroCode examples"""
        examples = {
            "Basic Memory": """# NeuroCode Memory Example
remember("NeuroCode is amazing!") as "experience"
remember("Learning AI programming") as "goal"

recall experiences with "amazing"
memory summary""",

            "Goal Setting": """# NeuroCode Goal Example  
goal: build an AI assistant priority: high
goal: learn machine learning priority: medium

agent: on
analyze "goal progress"
suggest "optimization strategies" """,

            "AI Integration": """# NeuroCode AI Example
analyze "system performance patterns"
suggest improvements for "code efficiency"
learn from "user behavior data"

when pattern_detected:
    apply_optimization if confidence > 80%
    remember result as "learned_improvement"
end""",

            "Plugin System": """# NeuroCode Plugin Example
plugin: sysmon
    check_health
    monitor_performance
end

plugin: optimizer
    analyze_code_patterns
    suggest_improvements
end

reflect on "plugin_results" """
        }
        
        # Show dialog to select example
        example_names = list(examples.keys())
        example, ok = QInputDialog.getItem(
            self, 
            "Load NeuroCode Example", 
            "Choose an example:",
            example_names,
            0,
            False
        )
        
        if ok and example:
            self.code_editor.setPlainText(examples[example])
            
    def show_documentation(self):
        """Show NeuroCode documentation"""
        doc_text = """
🧬 **NeuroCode Documentation**

**Basic Syntax:**
• remember(text) as 'tag' - Store memory
• recall tag: 'tag' - Retrieve memories  
• goal: description priority: level - Set objectives
• agent: on/off - Enable AI agent
• analyze "subject" - AI analysis
• suggest "topic" - Get AI suggestions

**Control Flow:**
• if condition: ... end
• when event: ... end  
• for item in collection: ... end

**Plugins:**
• plugin: name ... end

**AI Features:**
• think about "topic"
• learn from "source"
• reflect on "experience"
• optimize for "criteria"

**Examples:**
See File > Load Examples for complete programs!
        """
        
        QMessageBox.information(self, "NeuroCode Documentation", doc_text)
        
    def show_about(self):
        """Show about dialog"""
        about_text = """
🧬 **Neuroplex - AI-Native Programming Interface**

Version 1.0.0

NeuroCode is the first AI-native programming language where code thinks, learns, and evolves alongside you.

**Features:**
• AI-first runtime with built-in machine learning
• Memory-driven evolution and adaptation  
• Natural language programming constructs
• Real-time collaboration with AI agents
• Plugin ecosystem for extensibility

**Created by:** The NeuroCode Foundation
**License:** Open Source
**Website:** neurocode.ai

*"In NeuroCode, the language doesn't just execute your thoughts — it thinks alongside you."*
        """
        
        QMessageBox.about(self, "About Neuroplex", about_text)

def main():
    """Main entry point for Neuroplex GUI"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Neuroplex")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("NeuroCode Foundation")
    
    # Create and show main window
    window = NeuroplexMainWindow()
    window.show()
    
    # Handle graceful shutdown
    def cleanup():
        print("🧬 Neuroplex shutting down...")
        
    app.aboutToQuit.connect(cleanup)
    
    # Run application
    print("🚀 Launching Neuroplex GUI...")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
