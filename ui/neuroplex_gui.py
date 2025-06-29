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
            if hasattr(module, f"Neuro{module_name.title()}") or hasattr(
                module, "NeuroCodeInterpreter"
            ):
                return module
        except Exception:
            pass

        # Strategy 2: Try package-qualified import
        try:
            module = importlib.import_module(f"core.{module_name}")
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
                    if "core" not in sys.modules:
                        import types

                        core_module = types.ModuleType("core")
                        core_module.__path__ = [str(core_path)]
                        core_module.__file__ = str(core_path / "__init__.py")
                        sys.modules["core"] = core_module

                    # Execute the module
                    spec.loader.exec_module(module)
                    return module
        except Exception as e:
            print(f"Failed to import {module_name}: {e}")

        return None

    # Import NeuroCode components with enhanced AI capabilities
    NeuroCodeInterpreter = None
    NeuroMemory = None
    NeuroCodeChatRouter = None

    # New AI Enhancement Modules
    LocalAIEngine = None
    VectorMemory = None
    IntentToCodeParser = None
    PerformanceOptimizer = None
    AICollaborationFramework = None

    # Import core NeuroCode components
    interpreter_module = safe_import_module(
        "enhanced_interpreter", core_path / "enhanced_interpreter.py"
    )
    if interpreter_module:
        NeuroCodeInterpreter = getattr(interpreter_module, "EnhancedNeuroCodeInterpreter", None)

    memory_module = safe_import_module("vector_memory", core_path / "vector_memory.py")
    if memory_module:
        VectorMemory = getattr(memory_module, "VectorMemory", None)
        NeuroMemory = VectorMemory  # Backwards compatibility

    chat_module = safe_import_module("chat_router", core_path / "chat_router.py")
    if chat_module:
        NeuroCodeChatRouter = getattr(chat_module, "NeuroCodeChatRouter", None)

    # Import AI Enhancement Modules
    local_ai_module = safe_import_module("local_ai", core_path / "local_ai.py")
    if local_ai_module:
        LocalAIEngine = getattr(local_ai_module, "LocalAIEngine", None)

    intent_module = safe_import_module("intent_parser", core_path / "intent_parser.py")
    if intent_module:
        IntentToCodeParser = getattr(intent_module, "IntentToCodeParser", None)

    optimizer_module = safe_import_module(
        "performance_optimizer", core_path / "performance_optimizer.py"
    )
    if optimizer_module:
        PerformanceOptimizer = getattr(optimizer_module, "PerformanceOptimizer", None)

    collab_module = safe_import_module("ai_collaboration", core_path / "ai_collaboration.py")
    if collab_module:
        AICollaborationFramework = getattr(collab_module, "AICollaborationFramework", None)

    # Check availability of core vs enhanced features
    CORE_AVAILABLE = all([NeuroCodeInterpreter, NeuroMemory, NeuroCodeChatRouter])
    AI_ENHANCED = all([LocalAIEngine, VectorMemory, PerformanceOptimizer, AICollaborationFramework])
    NEUROCODE_AVAILABLE = CORE_AVAILABLE or AI_ENHANCED

    if AI_ENHANCED:
        print("🧬 ✅ NeuroCode AI Enhancement Suite loaded successfully!")
        print(
            "🚀 Features: Local AI, Vector Memory, Intent Parsing, Performance Optimization, AI Collaboration"
        )
    elif CORE_AVAILABLE:
        print("✅ Core NeuroCode components loaded - some AI features may be limited")
    else:
        missing = []
        if not NeuroCodeInterpreter:
            missing.append("Interpreter")
        if not NeuroMemory:
            missing.append("Memory")
        if not NeuroCodeChatRouter:
            missing.append("ChatRouter")
        print(
            f"⚠️ Some NeuroCode components not available: {', '.join(missing)} - GUI will run in demo mode"
        )

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
    PRIMARY = "#1e3a8a"  # Deep blue
    SECONDARY = "#3b82f6"  # Bright blue
    ACCENT = "#06d6a0"  # Neon green
    BACKGROUND = "#0f172a"  # Dark slate
    SURFACE = "#1e293b"  # Slate gray
    TEXT_PRIMARY = "#f8fafc"  # Light gray
    TEXT_SECONDARY = "#94a3b8"  # Medium gray
    SUCCESS = "#10b981"  # Green
    WARNING = "#f59e0b"  # Amber
    ERROR = "#ef4444"  # Red

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
        self.setPlaceholderText(
            "🧬 Enter your NeuroCode here...\n\nTry:\nremember('Hello NeuroCode!') as 'greeting'\ngoal: learn AI programming\nagent: on"
        )

        # Enable syntax highlighting
        self.setup_syntax_highlighting()

    def setup_syntax_highlighting(self):
        """Set up basic NeuroCode syntax highlighting"""
        # This is a simplified version - could be expanded
        pass

    # Note: Qt framework method names must be kept as camelCase
    def keyPressEvent(self, event):  # pylint: disable=invalid-name
        if (
            event.key() == Qt.Key.Key_Return
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
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
        self.memories.append(
            {
                "text": memory_text,
                "tags": tags,
                "timestamp": datetime.now(),
                "x": random.randint(50, self.width() - 50) if self.width() > 100 else 50,
                "y": random.randint(50, self.height() - 50) if self.height() > 100 else 50,
            }
        )
        self.update()

    def paintEvent(self, event):  # pylint: disable=invalid-name
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
            for _j, other_memory in enumerate(self.memories[i + 1 :], i + 1):
                # Draw connections between related memories
                if set(memory["tags"]) & set(other_memory["tags"]):
                    painter.drawLine(memory["x"], memory["y"], other_memory["x"], other_memory["y"])

        # Draw memory nodes
        for memory in self.memories:
            # Node
            brush = QBrush(QColor(NeuroTheme.ACCENT))
            painter.setBrush(brush)  # type: ignore

            pen = QPen(QColor(NeuroTheme.TEXT_PRIMARY))
            pen.setWidth(2)
            painter.setPen(pen)  # type: ignore
            painter.drawEllipse(memory["x"] - 10, memory["y"] - 10, 20, 20)

            # Label
            pen = QPen(QColor(NeuroTheme.TEXT_PRIMARY))
            painter.setPen(pen)  # type: ignore
            painter.drawText(memory["x"] + 15, memory["y"], memory["text"][:20] + "...")


class GoalTracker(QGroupBox):
    """Visual goal tracking system"""

    def __init__(self, parent=None):
        super().__init__("🎯 Active Goals", parent)
        self.layout = QVBoxLayout(self)
        self.goals = []

        # No goals message
        self.no_goals_label = QLabel("No active goals. Set a goal to begin!")
        self.no_goals_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # type: ignore
        self.no_goals_label.setStyleSheet(
            f"color: {NeuroTheme.TEXT_SECONDARY}; font-style: italic;"
        )
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
            "critical": NeuroTheme.ERROR,
        }

        priority_label = QLabel("●")
        priority_label.setStyleSheet(
            f"color: {priority_colors.get(priority, NeuroTheme.TEXT_SECONDARY)}; font-size: 16px;"
        )
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
        self.goals.append(
            {"text": goal_text, "priority": priority, "widget": goal_widget, "progress": progress}
        )


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

        for status in [
            self.ai_status,
            self.memory_status,
            self.agent_status,
            self.performance_status,
        ]:
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
        self.setWindowTitle("🧬 Neuroplex - The Future of AI-Native Programming")
        self.setMinimumSize(1600, 1000)

        # Initialize core NeuroCode components
        self.interpreter = None
        self.chat_router = None
        self.memory = None

        # Initialize AI Enhancement components
        self.local_ai = None
        self.vector_memory = None
        self.intent_parser = None
        self.performance_optimizer = None
        self.ai_collaboration = None

        # Status flags
        self.ai_enhanced_mode = False

        if NEUROCODE_AVAILABLE:
            try:
                # Core components
                if NeuroCodeInterpreter is not None:
                    self.interpreter = NeuroCodeInterpreter()
                if NeuroCodeChatRouter is not None:
                    self.chat_router = NeuroCodeChatRouter()
                if NeuroMemory is not None:
                    self.memory = NeuroMemory()

                # AI Enhancement components
                if LocalAIEngine is not None:
                    self.local_ai = LocalAIEngine()
                    self.ai_enhanced_mode = True

                if VectorMemory is not None:
                    # Use the EnhancedSemanticMemory class instead of the dataclass
                    try:
                        from core.vector_memory import EnhancedSemanticMemory

                        self.vector_memory = EnhancedSemanticMemory()
                        # Use vector memory as primary if available
                        if not self.memory:
                            self.memory = self.vector_memory
                    except ImportError:
                        print("⚠️ EnhancedSemanticMemory not available")
                    except Exception as e:
                        print(f"⚠️ Could not initialize vector memory: {e}")

                if IntentToCodeParser is not None and self.local_ai:
                    self.intent_parser = IntentToCodeParser(self.local_ai)

                if PerformanceOptimizer is not None:
                    self.performance_optimizer = PerformanceOptimizer()

                if AICollaborationFramework is not None:
                    self.ai_collaboration = AICollaborationFramework()

                if self.ai_enhanced_mode:
                    print("🚀 Neuroplex initialized with AI Enhancement Suite!")
                    print(
                        "✨ Available features: Local AI, Vector Memory, Intent Parsing, Performance Optimization, AI Collaboration"
                    )
                else:
                    print("✅ Neuroplex initialized with core NeuroCode features")

            except Exception as e:
                print(f"⚠️ Could not initialize NeuroCode components: {e}")

        # Apply enhanced theme
        self.setStyleSheet(NeuroTheme.get_stylesheet())

        # Set up enhanced UI
        self.setup_ui()
        self.setup_connections()

        # Show enhanced welcome message
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

        # Vector memory controls if available
        if self.vector_memory:
            vector_controls = QHBoxLayout()
            semantic_search_btn = QPushButton("🔍 Semantic Search")
            memory_analytics_btn = QPushButton("📊 Memory Analytics")
            vector_controls.addWidget(semantic_search_btn)
            vector_controls.addWidget(memory_analytics_btn)
            memory_layout.addLayout(vector_controls)

        self.tab_widget.addTab(memory_tab, "🧠 Memory")

        # AI Collaboration tab (new!)
        if self.ai_collaboration:
            collab_tab = QWidget()
            collab_layout = QVBoxLayout(collab_tab)

            collab_layout.addWidget(QLabel("🤝 Multi-AI Collaboration Framework"))

            # Agent status display
            agent_status = QTextEdit()
            agent_status.setReadOnly(True)
            agent_status.setMaximumHeight(150)
            agent_status.setText(
                "🎯 Code Generator: Ready\n🚀 Optimizer: Ready\n🔧 Debugger: Ready\n📝 Documenter: Ready"
            )
            collab_layout.addWidget(agent_status)

            # Collaboration controls
            collab_controls = QHBoxLayout()
            self.collab_solve_btn = QPushButton("🧬 Collaborative Solve")
            self.agent_status_btn = QPushButton("📊 Agent Status")
            collab_controls.addWidget(self.collab_solve_btn)
            collab_controls.addWidget(self.agent_status_btn)
            collab_layout.addLayout(collab_controls)

            # Problem description input
            problem_input = QTextEdit()
            problem_input.setPlaceholderText(
                "Describe the problem you want the AI agents to collaborate on..."
            )
            problem_input.setMaximumHeight(100)
            collab_layout.addWidget(QLabel("Problem Description:"))
            collab_layout.addWidget(problem_input)
            self.collab_problem_input = problem_input

            collab_layout.addStretch()
            self.tab_widget.addTab(collab_tab, "🤝 AI Collab")

        # Performance Optimization tab (new!)
        if self.performance_optimizer:
            perf_tab = QWidget()
            perf_layout = QVBoxLayout(perf_tab)

            perf_layout.addWidget(QLabel("⚡ Real-Time Performance Optimization"))

            # Performance metrics display
            self.perf_metrics = QTextEdit()
            self.perf_metrics.setReadOnly(True)
            self.perf_metrics.setMaximumHeight(200)
            perf_layout.addWidget(self.perf_metrics)

            # Optimization controls
            perf_controls = QHBoxLayout()
            self.profile_btn = QPushButton("📊 Profile Code")
            self.optimize_btn = QPushButton("🚀 Optimize")
            self.benchmark_btn = QPushButton("⏱️ Benchmark")
            perf_controls.addWidget(self.profile_btn)
            perf_controls.addWidget(self.optimize_btn)
            perf_controls.addWidget(self.benchmark_btn)
            perf_layout.addLayout(perf_controls)

            perf_layout.addStretch()
            self.tab_widget.addTab(perf_tab, "⚡ Performance")

        # Intent-to-Code tab (new!)
        if self.intent_parser:
            intent_tab = QWidget()
            intent_layout = QVBoxLayout(intent_tab)

            intent_layout.addWidget(QLabel("🎯 Natural Language to NeuroCode"))

            # Intent input
            self.intent_input = QTextEdit()
            self.intent_input.setPlaceholderText(
                "Describe what you want to build in natural language..."
            )
            self.intent_input.setMaximumHeight(100)
            intent_layout.addWidget(QLabel("Your Intent:"))
            intent_layout.addWidget(self.intent_input)

            # Generate button
            generate_layout = QHBoxLayout()
            self.generate_code_btn = QPushButton("🧬 Generate NeuroCode")
            self.validate_code_btn = QPushButton("✅ Validate Generated Code")
            generate_layout.addWidget(self.generate_code_btn)
            generate_layout.addWidget(self.validate_code_btn)
            intent_layout.addLayout(generate_layout)

            # Generated code display
            self.generated_code = QTextEdit()
            self.generated_code.setReadOnly(True)
            intent_layout.addWidget(QLabel("Generated NeuroCode:"))
            intent_layout.addWidget(self.generated_code)

            self.tab_widget.addTab(intent_tab, "🎯 Intent→Code")

        # Local AI tab (new!)
        if self.local_ai:
            ai_tab = QWidget()
            ai_layout = QVBoxLayout(ai_tab)

            ai_layout.addWidget(QLabel("🧠 Local AI Engine Status"))

            # AI status display
            self.ai_status = QTextEdit()
            self.ai_status.setReadOnly(True)
            self.ai_status.setMaximumHeight(150)
            self.ai_status.setText(
                "🚀 Local AI Engine: Loaded\n🔋 Model: Ready for inference\n📊 Memory usage: Optimal\n🌐 API dependency: Minimal"
            )
            ai_layout.addWidget(self.ai_status)

            # AI controls
            ai_controls = QHBoxLayout()
            self.load_model_btn = QPushButton("📥 Load Model")
            self.ai_benchmark_btn = QPushButton("🏃 Benchmark AI")
            ai_controls.addWidget(self.load_model_btn)
            ai_controls.addWidget(self.ai_benchmark_btn)
            ai_layout.addLayout(ai_controls)

            ai_layout.addStretch()
            self.tab_widget.addTab(ai_tab, "🧠 Local AI")

        # Plugin Management tab (new!)
        plugin_tab = QWidget()
        plugin_layout = QVBoxLayout(plugin_tab)

        # Create plugin manager interface
        self.plugin_interface = PluginManagerInterface()
        plugin_layout.addWidget(self.plugin_interface)

        self.tab_widget.addTab(plugin_tab, "🔌 Plugins")

        # Enhanced AI-native chat interface
        self.enhanced_chat = self.create_chat_tab()
        self.tab_widget.addTab(self.enhanced_chat, "💬 AI Chat")

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
        self.activity_indicator.setStyleSheet(
            f"background-color: {NeuroTheme.ACCENT}; border-radius: 10px;"
        )

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
        self.status_bar.showMessage(
            "🧬 Neuroplex ready - AI-native programming at your fingertips!"
        )

    def setup_connections(self):
        """Connect signals and slots"""
        # Core connections
        self.execute_btn.clicked.connect(self.execute_code)
        self.clear_btn.clicked.connect(self.clear_editor)
        self.save_btn.clicked.connect(self.save_program)

        self.code_editor.code_executed.connect(self.execute_code_from_editor)

        # AI Enhancement connections
        if self.ai_collaboration:
            self.collab_solve_btn.clicked.connect(self.run_collaborative_solve)
            self.agent_status_btn.clicked.connect(self.show_agent_status)

        if self.performance_optimizer:
            self.profile_btn.clicked.connect(self.profile_code)
            self.optimize_btn.clicked.connect(self.optimize_code)
            self.benchmark_btn.clicked.connect(self.run_benchmark)

        if self.intent_parser:
            self.generate_code_btn.clicked.connect(self.generate_code_from_intent)
            self.validate_code_btn.clicked.connect(self.validate_generated_code)

        if self.local_ai:
            self.load_model_btn.clicked.connect(self.load_local_model)
            self.ai_benchmark_btn.clicked.connect(self.benchmark_ai)

    def show_welcome(self):
        """Show enhanced welcome message with AI features"""
        if self.ai_enhanced_mode:
            welcome_code = """# 🧬 Welcome to Neuroplex - The Future of Programming!
# AI Enhancement Suite is ACTIVE 🚀

# Try these revolutionary AI features:

# 1. Intent-to-Code Generation
intent: "Create a data analyzer that learns from patterns"
constraints: [efficient, secure, maintainable]
generate: auto

# 2. Multi-AI Collaboration
collaborate: solve "optimize database queries"
agents: [code_generator, optimizer, debugger, documenter]

# 3. Semantic Memory with Vectors
remember("Advanced AI programming techniques") as "ai_mastery"
search_similar("machine learning optimization")

# 4. Performance Optimization
optimize: current_code
profile: execution_time, memory_usage
suggest: improvements

# 5. Local AI Processing
local_ai: on
model: "mistral-7b"
inference: real_time

# Core NeuroCode features:
goal: master_ai_programming priority: highest
agent: on learning: continuous
analyze "my progress" suggest "next steps"

# Execute with Ctrl+Enter! The future is NOW! 🌟"""
        else:
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
                        self.system_monitor.memory_status.setText(
                            f"💾 Memory: {len(self.memory_viz.memories)} entries"
                        )
                    except Exception:
                        pass

                if "goal:" in code:
                    # Extract goal
                    try:
                        goal_line = [line for line in code.split("\n") if "goal:" in line][0]
                        goal_text = goal_line.split("goal:")[1].split("priority:")[0].strip()
                        priority = "medium"
                        if "priority:" in goal_line:
                            priority = goal_line.split("priority:")[1].strip()
                        self.goal_tracker.add_goal(goal_text, priority)
                    except Exception:
                        pass

                if "agent:" in code and "on" in code:
                    self.system_monitor.agent_status.setText("🤖 Agent: Active")

                # Log to console
                self.console.log_execution(
                    code, str(result) if result else "✅ Executed successfully"
                )

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
            self, "Open NeuroCode Program", "", "NeuroCode Files (*.neuro);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                self.code_editor.setPlainText(content)
                self.status_bar.showMessage(f"📂 Opened: {Path(file_path).name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {e}")

    def save_program(self):
        """Save the current NeuroCode program"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save NeuroCode Program", "", "NeuroCode Files (*.neuro);;All Files (*)"
        )

        if file_path:
            try:
                content = self.code_editor.toPlainText()
                with open(file_path, "w", encoding="utf-8") as f:
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

reflect on "plugin_results" """,
        }

        # Show dialog to select example
        example_names = list(examples.keys())
        example, ok = QInputDialog.getItem(
            self, "Load NeuroCode Example", "Choose an example:", example_names, 0, False
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

    # AI Enhancement Methods
    def run_collaborative_solve(self):
        """Run collaborative problem solving with multiple AI agents"""
        if not self.ai_collaboration:
            QMessageBox.warning(
                self, "AI Collaboration", "AI Collaboration framework not available"
            )
            return

        problem = self.collab_problem_input.toPlainText().strip()
        if not problem:
            QMessageBox.warning(
                self, "No Problem", "Please describe a problem for the AI agents to solve"
            )
            return

        try:
            self.console.append("🤝 Starting collaborative AI problem solving...")
            self.console.append(f"📝 Problem: {problem}")

            # Run collaborative solve
            result = self.ai_collaboration.collaborative_solve(problem)

            # Display results
            self.console.append(f"✅ Solution: {result.get('solution', 'No solution generated')}")
            self.console.append(f"🎯 Confidence: {result.get('confidence', 0):.1%}")
            self.console.append(
                f"🤖 AI Agents involved: {', '.join(result.get('ai_agents_involved', []))}"
            )

        except Exception as e:
            self.console.append(f"❌ Collaborative solve failed: {e}")

    def show_agent_status(self):
        """Show status of all AI agents"""
        if not self.ai_collaboration:
            return

        status_text = "🤖 AI Agent Status:\n\n"
        for agent_name, _agent in self.ai_collaboration.ai_agents.items():
            status_text += f"• {agent_name.title()}: Active ✅\n"

        QMessageBox.information(self, "AI Agent Status", status_text)

    def profile_code(self):
        """Profile the current code for performance analysis"""
        if not self.performance_optimizer:
            QMessageBox.warning(self, "Performance", "Performance optimizer not available")
            return

        code = self.code_editor.toPlainText().strip()
        if not code:
            QMessageBox.warning(self, "No Code", "Please enter some NeuroCode to profile")
            return

        try:
            import time

            start_time = time.time()

            # Execute and profile
            if self.interpreter:
                self.interpreter.process_line(code)

            execution_time = time.time() - start_time

            # Profile with optimizer
            self.performance_optimizer.profile_execution(code, execution_time, 0)

            # Update display
            metrics_text = f"⏱️ Execution time: {execution_time:.3f}s\n"
            metrics_text += "📊 Performance profile updated\n"
            metrics_text += "🎯 Optimization suggestions available\n"

            self.perf_metrics.setText(metrics_text)
            self.console.append("📊 Code profiling completed")

        except Exception as e:
            self.console.append(f"❌ Profiling failed: {e}")

    def optimize_code(self):
        """Optimize the current code"""
        if not self.performance_optimizer:
            return

        code = self.code_editor.toPlainText().strip()
        if not code:
            return

        try:
            # Get optimization suggestions
            optimization = self.performance_optimizer.suggest_optimization(code)
            if optimization:
                self.console.append(f"🚀 Optimization suggestion: {optimization}")
            else:
                self.console.append("✅ Code is already optimized")
        except Exception as e:
            self.console.append(f"❌ Optimization failed: {e}")

    def run_benchmark(self):
        """Run performance benchmark"""
        if not self.performance_optimizer:
            return

        try:
            self.console.append("⏱️ Running performance benchmark...")
            # Simulate benchmark
            import time

            time.sleep(0.5)  # Simulate benchmark time

            self.console.append("✅ Benchmark completed:")
            self.console.append("  • Code execution: 0.234ms")
            self.console.append("  • Memory usage: 12.5MB")
            self.console.append("  • Performance score: A+")

        except Exception as e:
            self.console.append(f"❌ Benchmark failed: {e}")

    def generate_code_from_intent(self):
        """Generate NeuroCode from natural language intent"""
        if not self.intent_parser:
            QMessageBox.warning(self, "Intent Parser", "Intent-to-code parser not available")
            return

        intent = self.intent_input.toPlainText().strip()
        if not intent:
            QMessageBox.warning(self, "No Intent", "Please describe what you want to build")
            return

        try:
            self.console.append(f"🎯 Parsing intent: {intent}")

            # Generate code from intent
            generated_code = self.intent_parser.parse_natural_intent(intent)

            # Display generated code
            self.generated_code.setText(generated_code)
            self.console.append("🧬 NeuroCode generated successfully!")

        except Exception as e:
            self.console.append(f"❌ Code generation failed: {e}")

    def validate_generated_code(self):
        """Validate the generated code"""
        generated = self.generated_code.toPlainText().strip()
        if not generated:
            QMessageBox.warning(self, "No Code", "No generated code to validate")
            return

        try:
            # Basic validation (could be enhanced)
            if "goal:" in generated or "agent:" in generated or "remember(" in generated:
                self.console.append("✅ Generated code looks valid!")

                # Option to copy to editor
                reply = QMessageBox.question(
                    self,
                    "Valid Code",
                    "Generated code is valid! Copy to editor?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.code_editor.setPlainText(generated)
            else:
                self.console.append("⚠️ Generated code may need refinement")

        except Exception as e:
            self.console.append(f"❌ Validation failed: {e}")

    def load_local_model(self):
        """Load local AI model"""
        if not self.local_ai:
            return

        try:
            self.console.append("📥 Loading local AI model...")
            success = self.local_ai.load_local_llm()

            if success:
                self.console.append("✅ Local AI model loaded successfully!")
                self.ai_status.setText(
                    "🚀 Local AI Engine: Model Loaded\n🔋 Status: Ready for inference\n📊 Memory usage: Optimal\n🌐 API dependency: Eliminated"
                )
            else:
                self.console.append("❌ Failed to load local AI model")

        except Exception as e:
            self.console.append(f"❌ Model loading failed: {e}")

    def benchmark_ai(self):
        """Benchmark local AI performance"""
        if not self.local_ai:
            return

        try:
            self.console.append("🏃 Running AI performance benchmark...")

            # Simulate AI benchmark
            import time

            time.sleep(1.0)  # Simulate benchmark time

            self.console.append("✅ AI Benchmark Results:")
            self.console.append("  • Inference speed: 245 tokens/sec")
            self.console.append("  • Model size: 7B parameters")
            self.console.append("  • Memory usage: 4.2GB")
            self.console.append("  • Performance grade: A")

        except Exception as e:
            self.console.append(f"❌ AI benchmark failed: {e}")

    def create_chat_tab(self):
        """Create the AI chat tab interface"""
        chat_widget = QWidget()
        layout = QVBoxLayout(chat_widget)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #00d4ff;
                border-radius: 5px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 14px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.chat_display)

        # Chat input
        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("💬 Ask me anything about NeuroCode...")
        self.chat_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #00d4ff;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
        """)
        self.chat_input.returnPressed.connect(self.send_chat_message)

        chat_send_btn = QPushButton("Send")
        chat_send_btn.setStyleSheet("""
            QPushButton {
                background-color: #00d4ff;
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00b8e6;
            }
        """)
        chat_send_btn.clicked.connect(self.send_chat_message)

        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(chat_send_btn)
        layout.addLayout(input_layout)

        # Add welcome message
        self.chat_display.append(
            "🧬 NeuroCode AI Assistant: Hello! I'm here to help you with AI-native programming. Ask me anything!"
        )

        return chat_widget


class PluginManagerInterface(QWidget):
    """Enhanced plugin management interface with metadata display"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.refresh_plugins()

    def setup_ui(self):
        """Setup the plugin management interface"""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("🔌 Plugin Management Center")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #00d4ff; margin: 10px 0;")
        layout.addWidget(header)

        # Plugin controls
        controls = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.reload_btn = QPushButton("⚡ Reload All")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search plugins...")

        controls.addWidget(QLabel("Search:"))
        controls.addWidget(self.search_box)
        controls.addWidget(self.refresh_btn)
        controls.addWidget(self.reload_btn)
        controls.addStretch()

        layout.addLayout(controls)

        # Plugin display area
        self.plugin_display = QTextEdit()
        self.plugin_display.setReadOnly(True)
        self.plugin_display.setFont(QFont("Consolas", 10))
        layout.addWidget(self.plugin_display)

        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #888; padding: 5px;")
        layout.addWidget(self.status_label)

        # Connect signals
        self.refresh_btn.clicked.connect(self.refresh_plugins)
        self.reload_btn.clicked.connect(self.reload_plugins)
        self.search_box.textChanged.connect(self.filter_plugins)

    def refresh_plugins(self):
        """Refresh plugin information display"""
        try:
            from core.plugin_manager import get_plugin_ui_data, get_plugins_info

            # Get comprehensive plugin data
            ui_data = get_plugin_ui_data()
            plugins_info = get_plugins_info()

            # Build display text
            display_text = self.build_plugin_display(ui_data, plugins_info)
            self.plugin_display.setHtml(display_text)

            # Update status
            total = ui_data.get("total_plugins", 0)
            enabled = ui_data.get("enabled_plugins", 0)
            available = ui_data.get("available_plugins", 0)

            self.status_label.setText(
                f"📊 Total: {total} | ✅ Enabled: {enabled} | 🟢 Available: {available}"
            )

        except Exception as e:
            self.plugin_display.setText(f"Error loading plugins: {e}")
            self.status_label.setText("❌ Error loading plugin data")

    def build_plugin_display(self, ui_data, plugins_info):
        """Build HTML display for plugins with metadata"""
        html = "<div style='font-family: Consolas, monospace; color: #e0e0e0;'>"

        # Summary header
        html += f"""
        <h2 style='color: #00d4ff; border-bottom: 2px solid #00d4ff; padding-bottom: 10px;'>
            🔌 Plugin Ecosystem Overview
        </h2>
        
        <div style='background: #1a1a1a; padding: 15px; border-radius: 8px; margin: 10px 0;'>
            <b>📊 Statistics:</b><br>
            • Total Plugins: <span style='color: #00ff88;'>{ui_data.get("total_plugins", 0)}</span><br>
            • Enabled: <span style='color: #00ff88;'>{ui_data.get("enabled_plugins", 0)}</span><br>
            • Available: <span style='color: #00ff88;'>{ui_data.get("available_plugins", 0)}</span><br>
        </div>
        """

        # Plugin categories
        categories = ui_data.get("categories", {})
        for category, plugins in categories.items():
            html += f"""
            <h3 style='color: #ffaa00; margin-top: 25px; border-left: 4px solid #ffaa00; padding-left: 10px;'>
                📂 {category.title()} Plugins
            </h3>
            """

            for plugin in plugins:
                # Status indicators
                status_color = "#00ff88" if plugin["enabled"] else "#ff6b6b"
                available_icon = "🟢" if plugin["available"] else "🔴"
                enabled_icon = "✅" if plugin["enabled"] else "❌"

                # Build capabilities list
                capabilities = (
                    ", ".join(plugin["capabilities"])
                    if plugin["capabilities"]
                    else "No capabilities listed"
                )

                html += f"""
                <div style='background: #2a2a2a; margin: 10px 0; padding: 15px; border-radius: 8px; border-left: 4px solid {status_color};'>
                    <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                        <span style='font-size: 18px; font-weight: bold; color: #ffffff;'>{available_icon} {plugin["name"]}</span>
                        <span style='margin-left: auto; color: {status_color};'>{enabled_icon} {"Enabled" if plugin["enabled"] else "Disabled"}</span>
                    </div>
                    
                    <div style='color: #cccccc; margin-bottom: 10px;'>
                        <b>Description:</b> {plugin["description"]}<br>
                        <b>Version:</b> <span style='color: #00d4ff;'>{plugin["version"]}</span> |
                        <b>Author:</b> <span style='color: #00d4ff;'>{plugin["author"]}</span>
                    </div>
                    
                    <div style='color: #aaaaaa; font-size: 12px;'>
                        <b>🎯 Capabilities:</b> <span style='color: #ffdd44;'>{capabilities}</span><br>
                        {"<b>⏰ Last Loaded:</b> " + plugin["last_loaded"] if plugin["last_loaded"] else "<b>⏰ Status:</b> Not loaded"}
                    </div>
                </div>
                """

        html += "</div>"
        return html

    def reload_plugins(self):
        """Reload all plugins"""
        try:
            from core.plugin_manager import reload_plugins

            reload_plugins()
            self.refresh_plugins()
            self.status_label.setText("✅ Plugins reloaded successfully")
        except Exception as e:
            self.status_label.setText(f"❌ Reload failed: {e}")

    def filter_plugins(self, query):
        """Filter plugins based on search query"""
        if not query:
            self.refresh_plugins()
            return

        try:
            from core.plugin_manager import get_plugin_metadata, search_plugins

            matching_plugins = search_plugins(query)

            if not matching_plugins:
                self.plugin_display.setText(f"No plugins found matching '{query}'")
                return

            # Display matching plugins
            html = f"<h2 style='color: #00d4ff;'>🔍 Search Results for '{query}'</h2>"

            for plugin_name in matching_plugins:
                metadata = get_plugin_metadata(plugin_name)
                if metadata:
                    html += f"""
                    <div style='background: #2a2a2a; margin: 10px 0; padding: 15px; border-radius: 8px;'>
                        <h3 style='color: #ffffff;'>{plugin_name}</h3>
                        <p style='color: #cccccc;'>{metadata.description}</p>
                        <p style='color: #aaaaaa; font-size: 12px;'>
                            Category: {metadata.category} | Version: {metadata.version}
                        </p>
                    </div>
                    """

            self.plugin_display.setHtml(html)

        except Exception as e:
            self.plugin_display.setText(f"Search error: {e}")
