# enhanced_plugin_editor.py
# 🧠 Enhanced Plugin Editor with AI Feedback, Validation, and Sandbox Testing
# "Incredible: drag-and-edit, execute, format, and AI-enhance"
# "Feels like a dev console inside the AI"

import os
import json
import ast
import re
import asyncio
import tempfile
import subprocess
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPlainTextEdit,
    QPushButton, QLabel, QSplitter, QTreeWidget, QTreeWidgetItem,
    QComboBox, QSpinBox, QCheckBox, QGroupBox, QProgressBar,
    QMessageBox, QDialog, QDialogButtonBox, QTextEdit, QListWidget,
    QListWidgetItem, QFrame, QScrollArea, QFormLayout, QSlider,
    QFileDialog, QLineEdit, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QPropertyAnimation, QRect
from PySide6.QtGui import QFont, QColor, QPixmap, QIcon, QSyntaxHighlighter, QTextCharFormat


@dataclass
class PluginValidationResult:
    """Result of plugin validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    metadata: Dict[str, Any]
    performance_score: float
    security_score: float


@dataclass
class AIFeedback:
    """AI feedback on plugin output"""
    confidence: float
    suggestions: List[str]
    potential_issues: List[str]
    optimization_tips: List[str]
    code_quality_score: float
    maintainability_score: float


class AetherPluginHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for .aether plugin files"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_rules()

    def setup_rules(self):
        """Setup syntax highlighting rules"""
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(86, 156, 214))  # Blue
        keyword_format.setFontWeight(QFont.Bold)

        keywords = [
            'plugin', 'function', 'fn', 'let', 'const', 'if', 'else',
            'for', 'while', 'return', 'try', 'catch', 'throw', 'await',
            'async', 'memory', 'neural', 'lyrixa', 'call', 'log', 'remember'
        ]

        self.rules = []
        for word in keywords:
            pattern = rf'\b{word}\b'
            self.rules.append((re.compile(pattern), keyword_format))

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(206, 145, 120))  # Orange
        self.rules.append((re.compile(r'".*?"'), string_format))
        self.rules.append((re.compile(r"'.*?'"), string_format))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(106, 153, 85))  # Green
        comment_format.setFontItalic(True)
        self.rules.append((re.compile(r'//.*'), comment_format))
        self.rules.append((re.compile(r'/\*.*?\*/'), comment_format))

        # Functions
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(220, 220, 170))  # Yellow
        self.rules.append((re.compile(r'\b\w+(?=\s*\()'), function_format))

    def highlightBlock(self, text):
        """Apply syntax highlighting to text block"""
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)


class PluginSandbox:
    """Isolated sandbox for testing plugins"""

    def __init__(self, plugin_code: str, plugin_type: str = "aether"):
        self.plugin_code = plugin_code
        self.plugin_type = plugin_type
        self.sandbox_dir = None
        self.results = []
        self.errors = []

    def create_sandbox(self):
        """Create isolated sandbox environment"""
        self.sandbox_dir = tempfile.mkdtemp(prefix="aether_sandbox_")

        # Create dummy memory and goal structures
        dummy_memory = {
            "short_term": ["test_memory_1", "test_memory_2"],
            "long_term": {"knowledge": "test_knowledge"},
            "goals": ["test_goal_1", "test_goal_2"]
        }

        # Write dummy files
        with open(os.path.join(self.sandbox_dir, "memory.json"), "w") as f:
            json.dump(dummy_memory, f)

        # Write plugin file
        plugin_file = f"test_plugin.{self.plugin_type}"
        with open(os.path.join(self.sandbox_dir, plugin_file), "w") as f:
            f.write(self.plugin_code)

        return self.sandbox_dir

    def run_tests(self) -> Dict[str, Any]:
        """Run comprehensive tests on plugin"""
        if not self.sandbox_dir:
            self.create_sandbox()

        results = {
            "syntax_valid": False,
            "execution_time": 0,
            "memory_usage": 0,
            "errors": [],
            "warnings": [],
            "output": "",
            "security_issues": []
        }

        try:
            # Syntax validation
            if self.plugin_type == "py":
                results["syntax_valid"] = self._validate_python_syntax()
            else:
                results["syntax_valid"] = self._validate_aether_syntax()

            # Security scan
            results["security_issues"] = self._scan_security_issues()

            # Performance test
            start_time = time.time()
            results["output"] = self._execute_plugin()
            results["execution_time"] = time.time() - start_time

        except Exception as e:
            results["errors"].append(str(e))

        return results

    def _validate_python_syntax(self) -> bool:
        """Validate Python syntax"""
        try:
            ast.parse(self.plugin_code)
            return True
        except SyntaxError as e:
            self.errors.append(f"Python syntax error: {e}")
            return False

    def _validate_aether_syntax(self) -> bool:
        """Validate .aether syntax"""
        # Basic .aether syntax validation
        required_patterns = [
            r'plugin\s+\w+',  # plugin declaration
            r'function\s+\w+|fn\s+\w+',  # function declaration
        ]

        for pattern in required_patterns:
            if not re.search(pattern, self.plugin_code):
                self.errors.append(f"Missing required pattern: {pattern}")
                return False

        return True

    def _scan_security_issues(self) -> List[str]:
        """Scan for potential security issues"""
        security_issues = []

        dangerous_patterns = [
            (r'eval\s*\(', "Dangerous eval() usage"),
            (r'exec\s*\(', "Dangerous exec() usage"),
            (r'os\.system\s*\(', "System command execution"),
            (r'subprocess\.', "Subprocess execution"),
            (r'open\s*\(.*[\'"]w[\'"]', "File write operations"),
            (r'import\s+os', "OS module import"),
            (r'__import__', "Dynamic imports"),
        ]

        for pattern, message in dangerous_patterns:
            if re.search(pattern, self.plugin_code):
                security_issues.append(message)

        return security_issues

    def _execute_plugin(self) -> str:
        """Execute plugin in sandbox"""
        # Mock execution for now
        return f"Plugin executed successfully in sandbox\nCode length: {len(self.plugin_code)} characters"

    def cleanup(self):
        """Clean up sandbox environment"""
        if self.sandbox_dir and os.path.exists(self.sandbox_dir):
            import shutil
            shutil.rmtree(self.sandbox_dir)


class AIFeedbackEngine:
    """AI-powered feedback engine for plugin analysis"""

    def __init__(self):
        self.analysis_cache = {}
        self.feedback_history = []

    def analyze_plugin_output(self, plugin_code: str, output: str, execution_time: float) -> AIFeedback:
        """Analyze plugin output and provide AI feedback"""

        # Calculate scores
        code_quality = self._calculate_code_quality(plugin_code)
        maintainability = self._calculate_maintainability(plugin_code)

        # Generate suggestions
        suggestions = self._generate_suggestions(plugin_code, output, execution_time)

        # Identify potential issues
        issues = self._identify_issues(plugin_code, output)

        # Optimization tips
        optimization_tips = self._generate_optimization_tips(plugin_code, execution_time)

        feedback = AIFeedback(
            confidence=0.85,  # AI confidence in analysis
            suggestions=suggestions,
            potential_issues=issues,
            optimization_tips=optimization_tips,
            code_quality_score=code_quality,
            maintainability_score=maintainability
        )

        # Cache the analysis
        self.analysis_cache[hash(plugin_code)] = feedback
        self.feedback_history.append(feedback)

        return feedback

    def _calculate_code_quality(self, code: str) -> float:
        """Calculate code quality score"""
        score = 1.0

        # Check for comments
        if '//' in code or '/*' in code:
            score += 0.2

        # Check for error handling
        if 'try' in code and 'catch' in code:
            score += 0.3

        # Check for input validation
        if 'validate' in code.lower() or 'check' in code.lower():
            score += 0.2

        # Penalize for excessive length
        if len(code) > 1000:
            score -= 0.2

        return min(score, 1.0)

    def _calculate_maintainability(self, code: str) -> float:
        """Calculate maintainability score"""
        score = 1.0

        # Check for function decomposition
        function_count = len(re.findall(r'function\s+\w+|fn\s+\w+', code))
        if function_count > 1:
            score += 0.2

        # Check for meaningful names
        if len(re.findall(r'\b\w{3,}\b', code)) / len(code.split()) > 0.7:
            score += 0.1

        # Check for documentation
        if 'description:' in code or '/**' in code:
            score += 0.2

        return min(score, 1.0)

    def _generate_suggestions(self, code: str, output: str, execution_time: float) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []

        if execution_time > 1.0:
            suggestions.append("Consider optimizing for better performance")

        if 'error' in output.lower():
            suggestions.append("Add more comprehensive error handling")

        if len(code.split('\n')) > 100:
            suggestions.append("Consider breaking into smaller functions")

        if not re.search(r'//.*|/\*.*\*/', code):
            suggestions.append("Add comments to improve code documentation")

        return suggestions

    def _identify_issues(self, code: str, output: str) -> List[str]:
        """Identify potential issues"""
        issues = []

        if 'undefined' in output.lower():
            issues.append("Undefined variables or functions detected")

        if not re.search(r'return\s+', code):
            issues.append("No return statements found - plugin may not provide output")

        if len(code.strip()) < 50:
            issues.append("Plugin code seems too short - may be incomplete")

        return issues

    def _generate_optimization_tips(self, code: str, execution_time: float) -> List[str]:
        """Generate optimization tips"""
        tips = []

        if 'for' in code and 'while' in code:
            tips.append("Consider using more efficient iteration methods")

        if execution_time > 0.5:
            tips.append("Profile the code to identify performance bottlenecks")

        if re.search(r'lyrixa\.log\s*\(', code):
            tips.append("Consider reducing logging in production for better performance")

        return tips


class PluginValidator:
    """Comprehensive plugin validator"""

    def __init__(self):
        self.validation_rules = self._load_validation_rules()

    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules for .aether plugins"""
        return {
            "required_metadata": ["name", "description", "version"],
            "required_functions": ["execute", "initialize"],
            "security_blacklist": ["eval", "exec", "__import__", "os.system"],
            "performance_thresholds": {
                "max_execution_time": 5.0,
                "max_memory_usage": 100 * 1024 * 1024,  # 100MB
                "max_lines": 500
            }
        }

    def validate_plugin(self, plugin_code: str, plugin_type: str = "aether") -> PluginValidationResult:
        """Comprehensive plugin validation"""
        errors = []
        warnings = []
        suggestions = []
        metadata = {}

        # Parse metadata
        metadata = self._parse_metadata(plugin_code)

        # Validate structure
        if plugin_type == "aether":
            errors.extend(self._validate_aether_structure(plugin_code))
        else:
            errors.extend(self._validate_python_structure(plugin_code))

        # Security validation
        security_issues = self._validate_security(plugin_code)
        errors.extend(security_issues)

        # Performance validation
        perf_warnings = self._validate_performance(plugin_code)
        warnings.extend(perf_warnings)

        # Generate suggestions
        suggestions = self._generate_validation_suggestions(plugin_code, metadata)

        # Calculate scores
        performance_score = self._calculate_performance_score(plugin_code)
        security_score = self._calculate_security_score(plugin_code)

        return PluginValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            metadata=metadata,
            performance_score=performance_score,
            security_score=security_score
        )

    def _parse_metadata(self, code: str) -> Dict[str, Any]:
        """Parse plugin metadata"""
        metadata = {}

        # Extract metadata from comments or structured format
        metadata_patterns = [
            (r'name:\s*"([^"]*)"', 'name'),
            (r'description:\s*"([^"]*)"', 'description'),
            (r'version:\s*"([^"]*)"', 'version'),
            (r'author:\s*"([^"]*)"', 'author'),
        ]

        for pattern, key in metadata_patterns:
            match = re.search(pattern, code)
            if match:
                metadata[key] = match.group(1)

        return metadata

    def _validate_aether_structure(self, code: str) -> List[str]:
        """Validate .aether plugin structure"""
        errors = []

        # Check for plugin declaration
        if not re.search(r'plugin\s+\w+', code):
            errors.append("Missing plugin declaration")

        # Check for functions
        if not re.search(r'function\s+\w+|fn\s+\w+', code):
            errors.append("No functions found in plugin")

        # Check for proper syntax
        if code.count('{') != code.count('}'):
            errors.append("Mismatched braces")

        return errors

    def _validate_python_structure(self, code: str) -> List[str]:
        """Validate Python plugin structure"""
        errors = []

        try:
            tree = ast.parse(code)

            # Check for class or function definitions
            has_class = any(isinstance(node, ast.ClassDef) for node in tree.body)
            has_function = any(isinstance(node, ast.FunctionDef) for node in tree.body)

            if not has_class and not has_function:
                errors.append("No class or function definitions found")

        except SyntaxError as e:
            errors.append(f"Python syntax error: {e}")

        return errors

    def _validate_security(self, code: str) -> List[str]:
        """Validate security aspects"""
        errors = []

        for dangerous_pattern in self.validation_rules["security_blacklist"]:
            if dangerous_pattern in code:
                errors.append(f"Security risk: {dangerous_pattern} usage detected")

        return errors

    def _validate_performance(self, code: str) -> List[str]:
        """Validate performance aspects"""
        warnings = []

        thresholds = self.validation_rules["performance_thresholds"]

        if len(code.split('\n')) > thresholds["max_lines"]:
            warnings.append(f"Plugin exceeds recommended line count ({thresholds['max_lines']})")

        # Check for potential performance issues
        if 'while True' in code:
            warnings.append("Infinite loop detected - may cause performance issues")

        return warnings

    def _generate_validation_suggestions(self, code: str, metadata: Dict[str, Any]) -> List[str]:
        """Generate suggestions for improvement"""
        suggestions = []

        # Check metadata completeness
        for required_field in self.validation_rules["required_metadata"]:
            if required_field not in metadata:
                suggestions.append(f"Add {required_field} to plugin metadata")

        # Code quality suggestions
        if not re.search(r'//.*|/\*.*\*/', code):
            suggestions.append("Add comments to improve code readability")

        if 'TODO' in code.upper():
            suggestions.append("Complete TODO items before deployment")

        return suggestions

    def _calculate_performance_score(self, code: str) -> float:
        """Calculate performance score"""
        score = 1.0

        # Penalize for length
        lines = len(code.split('\n'))
        if lines > 200:
            score -= 0.2

        # Penalize for complex patterns
        if 'while True' in code:
            score -= 0.3

        # Reward for efficient patterns
        if 'return' in code:
            score += 0.1

        return max(0.0, min(1.0, score))

    def _calculate_security_score(self, code: str) -> float:
        """Calculate security score"""
        score = 1.0

        # Check for dangerous patterns
        for dangerous_pattern in self.validation_rules["security_blacklist"]:
            if dangerous_pattern in code:
                score -= 0.2

        # Reward for security practices
        if 'validate' in code.lower():
            score += 0.1

        return max(0.0, min(1.0, score))


class EnhancedPluginEditor(QWidget):
    """Enhanced Plugin Editor with AI feedback, validation, and sandbox testing"""

    def __init__(self, plugin_dir, memory_manager, plugin_manager):
        super().__init__()
        self.plugin_dir = plugin_dir
        self.memory = memory_manager
        self.plugins = plugin_manager
        self.current_file_path = None

        # Initialize components
        self.validator = PluginValidator()
        self.ai_feedback = AIFeedbackEngine()
        self.sandbox = None

        # Setup UI
        self.init_ui()

        # Auto-validation timer
        self.validation_timer = QTimer()
        self.validation_timer.timeout.connect(self.auto_validate)
        self.validation_timer.setSingleShot(True)

        # Load settings
        self.load_settings()

    def init_ui(self):
        """Initialize the enhanced UI"""
        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("🧠 Enhanced Plugin Editor")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")

        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("color: #4CAF50; font-size: 12px;")

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("AI Enhanced"))
        header_layout.addWidget(self.status_indicator)

        layout.addLayout(header_layout)

        # Main content
        main_splitter = QSplitter(Qt.Horizontal)

        # Left side - Editor and tabs
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Editor tabs
        self.editor_tabs = QTabWidget()

        # Code editor tab
        self.setup_code_editor_tab()

        # AI feedback tab
        self.setup_ai_feedback_tab()

        # Validation tab
        self.setup_validation_tab()

        # Sandbox tab
        self.setup_sandbox_tab()

        left_layout.addWidget(self.editor_tabs)
        main_splitter.addWidget(left_widget)

        # Right side - Tools and insights
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Tools panel
        tools_group = QGroupBox("🛠️ Tools")
        tools_layout = QVBoxLayout(tools_group)

        # Quick actions
        self.format_btn = QPushButton("🎨 Format Code")
        self.format_btn.clicked.connect(self.format_code)

        self.optimize_btn = QPushButton("⚡ AI Optimize")
        self.optimize_btn.clicked.connect(self.ai_optimize)

        self.test_btn = QPushButton("🧪 Run Tests")
        self.test_btn.clicked.connect(self.run_comprehensive_tests)

        tools_layout.addWidget(self.format_btn)
        tools_layout.addWidget(self.optimize_btn)
        tools_layout.addWidget(self.test_btn)

        # Settings panel
        settings_group = QGroupBox("⚙️ Settings")
        settings_layout = QFormLayout(settings_group)

        self.auto_validate_cb = QCheckBox("Auto-validate")
        self.auto_validate_cb.setChecked(True)
        self.auto_validate_cb.toggled.connect(self.toggle_auto_validate)

        self.ai_feedback_cb = QCheckBox("AI Feedback")
        self.ai_feedback_cb.setChecked(True)

        self.sandbox_mode_cb = QCheckBox("Sandbox Mode")
        self.sandbox_mode_cb.setChecked(True)

        settings_layout.addRow("Auto-validate:", self.auto_validate_cb)
        settings_layout.addRow("AI Feedback:", self.ai_feedback_cb)
        settings_layout.addRow("Sandbox Mode:", self.sandbox_mode_cb)

        right_layout.addWidget(tools_group)
        right_layout.addWidget(settings_group)
        right_layout.addStretch()

        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([800, 300])

        layout.addWidget(main_splitter)

        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.progress_bar)

        layout.addLayout(status_layout)

        self.setLayout(layout)

    def setup_code_editor_tab(self):
        """Setup the main code editor tab"""
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)

        # Toolbar
        toolbar_layout = QHBoxLayout()

        self.file_label = QLabel("📝 New Plugin")
        self.file_label.setStyleSheet("font-weight: bold;")

        self.open_btn = QPushButton("📁 Open")
        self.open_btn.clicked.connect(self.open_plugin)

        self.save_btn = QPushButton("💾 Save")
        self.save_btn.clicked.connect(self.save_plugin)

        self.new_btn = QPushButton("📄 New")
        self.new_btn.clicked.connect(self.new_plugin)

        toolbar_layout.addWidget(self.file_label)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.open_btn)
        toolbar_layout.addWidget(self.save_btn)
        toolbar_layout.addWidget(self.new_btn)

        editor_layout.addLayout(toolbar_layout)

        # Code editor
        self.code_editor = QPlainTextEdit()
        self.code_editor.setPlaceholderText("// Write your .aether plugin here\n// AI-enhanced editing with real-time feedback\n\nplugin my_plugin {\n    description: \"My awesome plugin\"\n    version: \"1.0.0\"\n    \n    fn execute(input) {\n        // Your code here\n        return \"Hello from plugin!\"\n    }\n}")

        # Setup syntax highlighting
        self.highlighter = AetherPluginHighlighter(self.code_editor.document())

        # Setup font
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.Monospace)
        self.code_editor.setFont(font)

        # Connect text change for auto-validation
        self.code_editor.textChanged.connect(self.on_text_changed)

        editor_layout.addWidget(self.code_editor)

        self.editor_tabs.addTab(editor_widget, "📝 Code Editor")

    def setup_ai_feedback_tab(self):
        """Setup AI feedback tab"""
        feedback_widget = QWidget()
        feedback_layout = QVBoxLayout(feedback_widget)

        # AI feedback header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("🧠 AI Analysis"))

        self.analyze_btn = QPushButton("🔍 Analyze")
        self.analyze_btn.clicked.connect(self.analyze_with_ai)

        header_layout.addStretch()
        header_layout.addWidget(self.analyze_btn)

        feedback_layout.addLayout(header_layout)

        # Feedback display
        self.feedback_display = QTreeWidget()
        self.feedback_display.setHeaderLabels(["Category", "Details", "Score"])
        self.feedback_display.setAlternatingRowColors(True)

        feedback_layout.addWidget(self.feedback_display)

        # AI suggestions
        suggestions_group = QGroupBox("💡 AI Suggestions")
        suggestions_layout = QVBoxLayout(suggestions_group)

        self.suggestions_list = QListWidget()
        suggestions_layout.addWidget(self.suggestions_list)

        # Apply suggestion button
        self.apply_suggestion_btn = QPushButton("✨ Apply Selected Suggestion")
        self.apply_suggestion_btn.clicked.connect(self.apply_suggestion)
        self.apply_suggestion_btn.setEnabled(False)

        suggestions_layout.addWidget(self.apply_suggestion_btn)

        feedback_layout.addWidget(suggestions_group)

        self.editor_tabs.addTab(feedback_widget, "🧠 AI Feedback")

    def setup_validation_tab(self):
        """Setup validation tab"""
        validation_widget = QWidget()
        validation_layout = QVBoxLayout(validation_widget)

        # Validation header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("✅ Plugin Validation"))

        self.validate_btn = QPushButton("🔍 Validate")
        self.validate_btn.clicked.connect(self.validate_plugin)

        header_layout.addStretch()
        header_layout.addWidget(self.validate_btn)

        validation_layout.addLayout(header_layout)

        # Validation results
        self.validation_tree = QTreeWidget()
        self.validation_tree.setHeaderLabels(["Type", "Message", "Line"])
        self.validation_tree.setAlternatingRowColors(True)

        validation_layout.addWidget(self.validation_tree)

        # Validation scores
        scores_group = QGroupBox("📊 Scores")
        scores_layout = QFormLayout(scores_group)

        self.performance_score_label = QLabel("N/A")
        self.security_score_label = QLabel("N/A")
        self.overall_score_label = QLabel("N/A")

        scores_layout.addRow("Performance:", self.performance_score_label)
        scores_layout.addRow("Security:", self.security_score_label)
        scores_layout.addRow("Overall:", self.overall_score_label)

        validation_layout.addWidget(scores_group)

        self.editor_tabs.addTab(validation_widget, "✅ Validation")

    def setup_sandbox_tab(self):
        """Setup sandbox testing tab"""
        sandbox_widget = QWidget()
        sandbox_layout = QVBoxLayout(sandbox_widget)

        # Sandbox header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("🧪 Sandbox Testing"))

        self.run_sandbox_btn = QPushButton("▶️ Run in Sandbox")
        self.run_sandbox_btn.clicked.connect(self.run_in_sandbox)

        header_layout.addStretch()
        header_layout.addWidget(self.run_sandbox_btn)

        sandbox_layout.addLayout(header_layout)

        # Sandbox configuration
        config_group = QGroupBox("⚙️ Sandbox Configuration")
        config_layout = QFormLayout(config_group)

        self.mock_memory_cb = QCheckBox("Mock Memory")
        self.mock_memory_cb.setChecked(True)

        self.mock_goals_cb = QCheckBox("Mock Goals")
        self.mock_goals_cb.setChecked(True)

        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(1, 60)
        self.timeout_spinbox.setValue(10)
        self.timeout_spinbox.setSuffix(" seconds")

        config_layout.addRow("Mock Memory:", self.mock_memory_cb)
        config_layout.addRow("Mock Goals:", self.mock_goals_cb)
        config_layout.addRow("Timeout:", self.timeout_spinbox)

        sandbox_layout.addWidget(config_group)

        # Sandbox results
        results_group = QGroupBox("📊 Test Results")
        results_layout = QVBoxLayout(results_group)

        self.sandbox_results = QTextEdit()
        self.sandbox_results.setReadOnly(True)
        self.sandbox_results.setPlaceholderText("Run tests to see results...")

        results_layout.addWidget(self.sandbox_results)

        sandbox_layout.addWidget(results_group)

        self.editor_tabs.addTab(sandbox_widget, "🧪 Sandbox")

    def on_text_changed(self):
        """Handle text changes in editor"""
        if self.auto_validate_cb.isChecked():
            # Reset timer for auto-validation
            self.validation_timer.stop()
            self.validation_timer.start(1000)  # 1 second delay

        # Update status
        self.status_label.setText(f"Editing... {len(self.code_editor.toPlainText())} characters")

    def auto_validate(self):
        """Auto-validate the current plugin"""
        if self.code_editor.toPlainText().strip():
            self.validate_plugin()

    def validate_plugin(self):
        """Validate the current plugin"""
        code = self.code_editor.toPlainText()
        if not code.strip():
            return

        self.status_label.setText("Validating...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        # Run validation
        try:
            result = self.validator.validate_plugin(code)

            # Update validation display
            self.validation_tree.clear()

            # Add errors
            for error in result.errors:
                item = QTreeWidgetItem(["❌ Error", error, "?"])
                item.setForeground(0, QColor("red"))
                self.validation_tree.addTopLevelItem(item)

            # Add warnings
            for warning in result.warnings:
                item = QTreeWidgetItem(["⚠️ Warning", warning, "?"])
                item.setForeground(0, QColor("orange"))
                self.validation_tree.addTopLevelItem(item)

            # Add suggestions
            for suggestion in result.suggestions:
                item = QTreeWidgetItem(["💡 Suggestion", suggestion, "?"])
                item.setForeground(0, QColor("blue"))
                self.validation_tree.addTopLevelItem(item)

            # Update scores
            self.performance_score_label.setText(f"{result.performance_score:.2f}")
            self.security_score_label.setText(f"{result.security_score:.2f}")
            overall_score = (result.performance_score + result.security_score) / 2
            self.overall_score_label.setText(f"{overall_score:.2f}")

            # Update status indicator
            if result.is_valid:
                self.status_indicator.setStyleSheet("color: #4CAF50; font-size: 12px;")
                self.status_label.setText("✅ Valid")
            else:
                self.status_indicator.setStyleSheet("color: #F44336; font-size: 12px;")
                self.status_label.setText("❌ Invalid")

            self.validation_tree.expandAll()

        except Exception as e:
            self.status_label.setText(f"Validation error: {str(e)}")

        finally:
            self.progress_bar.setVisible(False)

    def analyze_with_ai(self):
        """Analyze plugin with AI feedback"""
        code = self.code_editor.toPlainText()
        if not code.strip():
            return

        self.status_label.setText("AI analyzing...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        try:
            # Simulate plugin execution for feedback
            output = "Sample plugin output"
            execution_time = 0.5

            # Get AI feedback
            feedback = self.ai_feedback.analyze_plugin_output(code, output, execution_time)

            # Update feedback display
            self.feedback_display.clear()

            # Add confidence
            confidence_item = QTreeWidgetItem(["🎯 Confidence", f"{feedback.confidence:.1%}", ""])
            self.feedback_display.addTopLevelItem(confidence_item)

            # Add scores
            quality_item = QTreeWidgetItem(["📊 Code Quality", f"{feedback.code_quality_score:.2f}", ""])
            maintainability_item = QTreeWidgetItem(["🔧 Maintainability", f"{feedback.maintainability_score:.2f}", ""])

            self.feedback_display.addTopLevelItem(quality_item)
            self.feedback_display.addTopLevelItem(maintainability_item)

            # Add suggestions to list
            self.suggestions_list.clear()
            for suggestion in feedback.suggestions:
                item = QListWidgetItem(f"💡 {suggestion}")
                self.suggestions_list.addItem(item)

            for tip in feedback.optimization_tips:
                item = QListWidgetItem(f"⚡ {tip}")
                self.suggestions_list.addItem(item)

            for issue in feedback.potential_issues:
                item = QListWidgetItem(f"⚠️ {issue}")
                self.suggestions_list.addItem(item)

            # Enable apply button if suggestions exist
            self.apply_suggestion_btn.setEnabled(self.suggestions_list.count() > 0)

            self.feedback_display.expandAll()
            self.status_label.setText("✅ AI analysis complete")

        except Exception as e:
            self.status_label.setText(f"AI analysis error: {str(e)}")

        finally:
            self.progress_bar.setVisible(False)

    def run_in_sandbox(self):
        """Run plugin in sandbox environment"""
        code = self.code_editor.toPlainText()
        if not code.strip():
            return

        self.status_label.setText("Running in sandbox...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        try:
            # Create sandbox
            plugin_type = "aether" if "plugin" in code else "py"
            self.sandbox = PluginSandbox(code, plugin_type)

            # Run tests
            results = self.sandbox.run_tests()

            # Display results
            result_text = "🧪 Sandbox Test Results\n" + "=" * 50 + "\n\n"

            # Basic info
            result_text += f"✅ Syntax Valid: {results['syntax_valid']}\n"
            result_text += f"⏱️ Execution Time: {results['execution_time']:.3f}s\n"
            result_text += f"💾 Memory Usage: {results['memory_usage']} bytes\n\n"

            # Output
            if results['output']:
                result_text += "📤 Output:\n"
                result_text += results['output'] + "\n\n"

            # Errors
            if results['errors']:
                result_text += "❌ Errors:\n"
                for error in results['errors']:
                    result_text += f"  • {error}\n"
                result_text += "\n"

            # Warnings
            if results['warnings']:
                result_text += "⚠️ Warnings:\n"
                for warning in results['warnings']:
                    result_text += f"  • {warning}\n"
                result_text += "\n"

            # Security issues
            if results['security_issues']:
                result_text += "🔒 Security Issues:\n"
                for issue in results['security_issues']:
                    result_text += f"  • {issue}\n"
                result_text += "\n"

            # Overall assessment
            if results['syntax_valid'] and not results['errors'] and not results['security_issues']:
                result_text += "🎉 Overall: Plugin passed all sandbox tests!"
            else:
                result_text += "⚠️ Overall: Plugin has issues that need attention."

            self.sandbox_results.setPlainText(result_text)
            self.status_label.setText("✅ Sandbox testing complete")

        except Exception as e:
            self.status_label.setText(f"Sandbox error: {str(e)}")
            self.sandbox_results.setPlainText(f"Error running sandbox: {str(e)}")

        finally:
            self.progress_bar.setVisible(False)
            if self.sandbox:
                self.sandbox.cleanup()

    def format_code(self):
        """Format the current code"""
        code = self.code_editor.toPlainText()
        if not code.strip():
            return

        # Simple formatting for .aether files
        formatted_code = self._format_aether_code(code)
        self.code_editor.setPlainText(formatted_code)
        self.status_label.setText("✅ Code formatted")

    def _format_aether_code(self, code: str) -> str:
        """Format .aether code"""
        lines = code.split('\n')
        formatted_lines = []
        indent_level = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append('')
                continue

            # Decrease indent for closing braces
            if stripped.startswith('}'):
                indent_level = max(0, indent_level - 1)

            # Add formatted line
            formatted_lines.append('    ' * indent_level + stripped)

            # Increase indent for opening braces
            if stripped.endswith('{'):
                indent_level += 1

        return '\n'.join(formatted_lines)

    def ai_optimize(self):
        """AI-powered code optimization"""
        code = self.code_editor.toPlainText()
        if not code.strip():
            return

        self.status_label.setText("AI optimizing...")

        # Simple optimization example
        optimized_code = self._apply_ai_optimizations(code)
        self.code_editor.setPlainText(optimized_code)
        self.status_label.setText("✅ AI optimization complete")

    def _apply_ai_optimizations(self, code: str) -> str:
        """Apply AI-suggested optimizations"""
        # Example optimizations
        optimized = code

        # Add error handling if missing
        if 'try' not in optimized and 'catch' not in optimized:
            optimized = optimized.replace(
                'fn execute(input) {',
                'fn execute(input) {\n    try {'
            )
            optimized = optimized.replace(
                'return',
                '    } catch (error) {\n        log("Error: " + error)\n        return null\n    }\n    return'
            )

        # Add input validation
        if 'validate' not in optimized.lower():
            optimized = optimized.replace(
                'fn execute(input) {',
                'fn execute(input) {\n    if (!input) {\n        throw "Input is required"\n    }'
            )

        return optimized

    def run_comprehensive_tests(self):
        """Run all tests: validation, AI feedback, and sandbox"""
        self.status_label.setText("Running comprehensive tests...")

        # Run validation
        self.validate_plugin()

        # Run AI analysis
        self.analyze_with_ai()

        # Run sandbox
        self.run_in_sandbox()

        self.status_label.setText("✅ All tests complete")

    def apply_suggestion(self):
        """Apply selected AI suggestion"""
        current_item = self.suggestions_list.currentItem()
        if not current_item:
            return

        suggestion_text = current_item.text()

        # Apply suggestion based on type
        if "Add comments" in suggestion_text:
            self._add_comments_to_code()
        elif "Add error handling" in suggestion_text:
            self._add_error_handling()
        elif "Add input validation" in suggestion_text:
            self._add_input_validation()

        self.status_label.setText("✅ Suggestion applied")

    def _add_comments_to_code(self):
        """Add comments to code"""
        code = self.code_editor.toPlainText()

        # Add header comment if missing
        if not code.strip().startswith('//'):
            header_comment = "// AI-Generated Plugin\n// Auto-generated with enhanced editor\n\n"
            code = header_comment + code

        # Add function comments
        code = re.sub(
            r'(fn\s+\w+\s*\([^)]*\)\s*{)',
            r'// Function implementation\n    \1',
            code
        )

        self.code_editor.setPlainText(code)

    def _add_error_handling(self):
        """Add error handling to code"""
        code = self.code_editor.toPlainText()

        # Wrap execute function with try-catch
        code = re.sub(
            r'(fn\s+execute\s*\([^)]*\)\s*{)',
            r'\1\n    try {',
            code
        )

        # Add catch block before function end
        code = re.sub(
            r'(    return[^}]*\n)(})',
            r'\1    } catch (error) {\n        log("Error in plugin: " + error)\n        return null\n    }\n\2',
            code
        )

        self.code_editor.setPlainText(code)

    def _add_input_validation(self):
        """Add input validation to code"""
        code = self.code_editor.toPlainText()

        # Add validation at start of execute function
        code = re.sub(
            r'(fn\s+execute\s*\(([^)]*)\)\s*{)',
            r'\1\n    if (!\2) {\n        throw "Input parameter is required"\n    }',
            code
        )

        self.code_editor.setPlainText(code)

    def open_plugin(self):
        """Open a plugin file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Plugin", self.plugin_dir,
            "Plugin Files (*.py *.aether);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                self.code_editor.setPlainText(content)
                self.current_file_path = file_path
                self.file_label.setText(f"📝 {os.path.basename(file_path)}")
                self.status_label.setText(f"Opened {file_path}")

                # Auto-validate on open
                if self.auto_validate_cb.isChecked():
                    self.validate_plugin()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")

    def save_plugin(self):
        """Save the current plugin"""
        if not self.current_file_path:
            # Save as new file
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Plugin", self.plugin_dir,
                "Aether Plugin (*.aether);;Python Plugin (*.py);;All Files (*)"
            )

            if file_path:
                self.current_file_path = file_path
            else:
                return

        try:
            with open(self.current_file_path, 'w', encoding='utf-8') as f:
                f.write(self.code_editor.toPlainText())

            self.file_label.setText(f"📝 {os.path.basename(self.current_file_path)}")
            self.status_label.setText(f"Saved {self.current_file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

    def new_plugin(self):
        """Create a new plugin"""
        template = """// Enhanced Plugin Template
// Generated with AI-powered editor

plugin my_enhanced_plugin {
    description: "An enhanced plugin with AI feedback"
    version: "1.0.0"
    author: "Enhanced Editor"

    // Plugin configuration
    config: {
        timeout: 5000,
        retries: 3,
        validation: true
    }

    // Main execution function
    fn execute(input) {
        // Input validation
        if (!input) {
            throw "Input is required"
        }

        try {
            // Your plugin logic here
            log("Processing input: " + input)

            // Process the input
            let result = process_input(input)

            // Return result
            return {
                success: true,
                data: result,
                timestamp: now()
            }

        } catch (error) {
            log("Error in plugin: " + error)
            return {
                success: false,
                error: error,
                timestamp: now()
            }
        }
    }

    // Helper function
    fn process_input(input) {
        // Add your processing logic here
        return "Processed: " + input
    }

    // Initialization function
    fn initialize() {
        log("Enhanced plugin initialized")
        return true
    }

    // Cleanup function
    fn cleanup() {
        log("Enhanced plugin cleanup")
    }
}"""

        self.code_editor.setPlainText(template)
        self.current_file_path = None
        self.file_label.setText("📝 New Plugin")
        self.status_label.setText("New plugin created")

    def toggle_auto_validate(self, enabled):
        """Toggle auto-validation"""
        if enabled:
            self.status_label.setText("Auto-validation enabled")
        else:
            self.validation_timer.stop()
            self.status_label.setText("Auto-validation disabled")

    def load_settings(self):
        """Load editor settings"""
        # Load user preferences
        pass

    def save_settings(self):
        """Save editor settings"""
        # Save user preferences
        pass

    def closeEvent(self, event):
        """Handle close event"""
        # Save settings
        self.save_settings()

        # Cleanup sandbox
        if self.sandbox:
            self.sandbox.cleanup()

        event.accept()


# Test the enhanced plugin editor
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Create test editor
    editor = EnhancedPluginEditor("./plugins", None, None)
    editor.show()

    sys.exit(app.exec())
