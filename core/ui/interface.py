"""
🎯 Neuroplex Main Interface
==========================

Main UI interface that coordinates all UI components including themes,
visual feedback, command suggestions, and rich display.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from .commands import CommandSuggestions, Suggestion
from .display import CodeLanguage, RichDisplay, TextStyle
from .feedback import FeedbackContext, VisualFeedback
from .themes import ThemeConfig, ThemeManager, UITheme


@dataclass
class InterfaceConfig:
    """Configuration for the Neuroplex interface"""

    theme: UITheme = UITheme.DARK
    auto_suggestions: bool = True
    rich_formatting: bool = True
    animations_enabled: bool = True
    keyboard_shortcuts: bool = True
    status_bar: bool = True
    command_history: bool = True
    max_history_size: int = 1000


class KeyboardHandler:
    """Handles keyboard shortcuts and input"""

    def __init__(self):
        self.shortcuts: Dict[str, Callable] = {}
        self.enabled = True

    def register_shortcut(self, key_combination: str, callback: Callable):
        """Register a keyboard shortcut"""
        self.shortcuts[key_combination.lower()] = callback

    def handle_key(self, key_combination: str) -> bool:
        """Handle keyboard input, return True if handled"""
        if not self.enabled:
            return False

        key_combo = key_combination.lower()
        if key_combo in self.shortcuts:
            try:
                self.shortcuts[key_combo]()
                return True
            except Exception as e:
                print(f"Error handling shortcut {key_combination}: {e}")

        return False

    def list_shortcuts(self) -> Dict[str, str]:
        """List all registered shortcuts"""
        # Return mapping of shortcut to description (would need callback metadata)
        return dict.fromkeys(self.shortcuts.keys(), "Custom shortcut")


class StatusBar:
    """Status bar component"""

    def __init__(self):
        self.left_items: List[str] = []
        self.center_items: List[str] = []
        self.right_items: List[str] = []
        self.visible = True

    def set_left(self, items: List[str]):
        """Set left side items"""
        self.left_items = items

    def set_center(self, items: List[str]):
        """Set center items"""
        self.center_items = items

    def set_right(self, items: List[str]):
        """Set right side items"""
        self.right_items = items

    def render(self, width: int = 80) -> str:
        """Render the status bar"""
        if not self.visible:
            return ""

        left_text = " | ".join(self.left_items)
        center_text = " | ".join(self.center_items)
        right_text = " | ".join(self.right_items)

        # Calculate spacing
        used_space = len(left_text) + len(right_text)
        available_center = width - used_space - 4  # 4 for spacing

        if len(center_text) > available_center:
            center_text = center_text[: available_center - 3] + "..."

        # Create formatted line
        center_padding = available_center - len(center_text)
        left_padding = center_padding // 2
        right_padding = center_padding - left_padding

        status_line = f"{left_text}{' ' * left_padding}{center_text}{' ' * right_padding}{right_text}"

        return f"─{status_line}─"


class DashboardView:
    """Real-time dashboard view"""

    def __init__(self):
        self.widgets: Dict[str, Any] = {}
        self.layout = "grid"  # grid, list, columns
        self.refresh_interval = 1.0
        self.enabled = False

    def add_widget(self, name: str, widget: Any):
        """Add a dashboard widget"""
        self.widgets[name] = widget

    def remove_widget(self, name: str):
        """Remove a dashboard widget"""
        if name in self.widgets:
            del self.widgets[name]

    def render(self) -> str:
        """Render the dashboard"""
        if not self.enabled or not self.widgets:
            return ""

        lines = ["🧬 Neuroplex Dashboard", "─" * 30]

        for name, widget in self.widgets.items():
            lines.append(f"📊 {name}:")
            if hasattr(widget, "render"):
                lines.append(f"   {widget.render()}")
            else:
                lines.append(f"   {str(widget)}")
            lines.append("")

        return "\n".join(lines)


class NeuroplexUI:
    """Main Neuroplex UI interface"""

    def __init__(self, config: Optional[InterfaceConfig] = None):
        self.config = config or InterfaceConfig()

        # Initialize components
        self.theme_manager = ThemeManager()
        self.visual_feedback = VisualFeedback()
        self.command_suggestions = CommandSuggestions()
        self.rich_display = RichDisplay()
        self.keyboard_handler = KeyboardHandler()
        self.status_bar = StatusBar()
        self.dashboard = DashboardView()

        # State
        self.is_initialized = False
        self.current_theme: Optional[ThemeConfig] = None
        self.command_history: List[str] = []
        self.callbacks: Dict[str, List[Callable]] = {
            "command_executed": [],
            "theme_changed": [],
            "status_updated": [],
        }

        # Initialize the interface
        self.initialize()

    def initialize(self):
        """Initialize the UI interface"""
        if self.is_initialized:
            return

        # Set initial theme
        self.set_theme(self.config.theme)

        # Setup status bar
        self._setup_status_bar()

        # Register default keyboard shortcuts
        self._register_default_shortcuts()

        # Setup feedback callbacks
        self._setup_feedback_callbacks()

        self.is_initialized = True
        self.show_welcome_message()

    def _setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar.set_left(["Neuroplex", "Ready"])
        self.status_bar.set_center([f"Theme: {self.config.theme.value}"])
        self.status_bar.set_right([datetime.now().strftime("%H:%M:%S")])

    def _register_default_shortcuts(self):
        """Register default keyboard shortcuts"""
        if not self.config.keyboard_shortcuts:
            return

        self.keyboard_handler.register_shortcut("ctrl+r", self._shortcut_run)
        self.keyboard_handler.register_shortcut("ctrl+t", self._shortcut_chat)
        self.keyboard_handler.register_shortcut("ctrl+l", self._shortcut_clear)
        self.keyboard_handler.register_shortcut("ctrl+h", self._shortcut_help)
        self.keyboard_handler.register_shortcut("f1", self._shortcut_help)
        self.keyboard_handler.register_shortcut("ctrl+q", self._shortcut_quit)

    def _setup_feedback_callbacks(self):
        """Setup visual feedback callbacks"""

        def status_callback(update):
            self.status_bar.set_left(["Neuroplex", update.message])
            self._notify_callbacks("status_updated", update)

        self.visual_feedback.status_indicator.add_callback(status_callback)

    def set_theme(self, theme: UITheme | str):
        """Set the current theme"""
        try:
            self.theme_manager.set_theme(theme)
            self.current_theme = self.theme_manager.get_current_theme()

            # Update config
            if isinstance(theme, UITheme):
                self.config.theme = theme

            # Update status bar
            theme_name = theme.value if isinstance(theme, UITheme) else theme
            self.status_bar.set_center([f"Theme: {theme_name}"])

            self.show_success(f"Theme changed to: {self.current_theme.name}")
            self._notify_callbacks("theme_changed", self.current_theme)

        except ValueError as e:
            self.show_error(f"Failed to set theme: {e}")

    def show_welcome_message(self):
        """Show welcome message"""
        if not self.current_theme:
            return

        self.rich_display.print_separator("═", 60)
        self.rich_display.print_text(
            "🧬 Welcome to Neuroplex AI OS",
            TextStyle(bold=True, color=self.current_theme.colors.primary),
        )
        self.rich_display.print_text(
            f"Theme: {self.current_theme.name} | NeuroCode Engine Ready",
            TextStyle(color=self.current_theme.colors.text_secondary),
        )
        self.rich_display.print_separator("═", 60)
        self.rich_display.print_text("")

        if self.config.auto_suggestions:
            self.rich_display.print_info(
                "Type 'help' for commands or start typing for suggestions"
            )

    def show_dashboard(self):
        """Show the system dashboard"""
        if not self.dashboard.enabled:
            self.dashboard.enabled = True

        dashboard_content = self.dashboard.render()
        if dashboard_content:
            self.rich_display.print_text(dashboard_content)

    def hide_dashboard(self):
        """Hide the system dashboard"""
        self.dashboard.enabled = False

    def get_command_suggestions(self, partial_input: str) -> List[Suggestion]:
        """Get command suggestions for partial input"""
        if not self.config.auto_suggestions:
            return []

        return self.command_suggestions.get_suggestions(partial_input)

    def execute_command(self, command_line: str) -> bool:
        """Execute a command and return success status"""
        if not command_line.strip():
            return False

        # Add to history
        if self.config.command_history:
            self.command_history.append(command_line)
            if len(self.command_history) > self.config.max_history_size:
                self.command_history.pop(0)

        # Update command suggestions history
        self.command_suggestions.add_to_history(command_line)

        # Show processing
        with FeedbackContext(self.visual_feedback, "command execution"):
            try:
                # Parse command
                parts = command_line.strip().split()
                if not parts:
                    return False

                command_name = parts[0]
                args = parts[1:]

                # Execute built-in commands
                result = self._execute_builtin_command(command_name, args)

                self._notify_callbacks(
                    "command_executed", {"command": command_line, "success": result}
                )

                return result

            except Exception as e:
                self.show_error(f"Command execution failed: {e}")
                return False

    def _execute_builtin_command(self, command: str, args: List[str]) -> bool:
        """Execute built-in UI commands"""
        command = command.lower()

        if command in ["help", "h", "?"]:
            self._cmd_help(args)
        elif command == "clear":
            self._cmd_clear()
        elif command == "theme":
            self._cmd_theme(args)
        elif command == "status":
            self._cmd_status()
        elif command == "dashboard":
            self._cmd_dashboard(args)
        elif command == "shortcuts":
            self._cmd_shortcuts()
        elif command in ["exit", "quit", "q"]:
            self._cmd_exit()
        else:
            # Command not handled by UI - would delegate to NeuroCode engine
            self.show_warning(f"Command '{command}' not recognized by UI layer")
            return False

        return True

    def _cmd_help(self, args: List[str]):
        """Show help information"""
        if args:
            # Help for specific command
            command = self.command_suggestions.registry.get_command(args[0])
            if command:
                self.rich_display.print_text(f"Command: {command.name}")
                self.rich_display.print_text(f"Description: {command.description}")
                self.rich_display.print_text(f"Usage: {command.usage}")
                if command.examples:
                    self.rich_display.print_text("Examples:")
                    for example in command.examples:
                        self.rich_display.print_text(f"  {example}")
                if command.shortcuts:
                    self.rich_display.print_text(
                        f"Shortcuts: {', '.join(command.shortcuts)}"
                    )
            else:
                self.show_error(f"Command '{args[0]}' not found")
        else:
            # General help
            self.rich_display.print_markdown("""
# Neuroplex Help

## Available Commands
Type any command name followed by arguments. Use Tab for auto-completion.

### Core Commands
- `help [command]` - Show help information
- `run <file.aether>` - Execute NeuroCode program
- `chat [message]` - Start AI chat session
- `memory <action>` - Manage AI memory

### UI Commands
- `theme <name>` - Change UI theme
- `clear` - Clear screen
- `status` - Show system status
- `dashboard` - Toggle dashboard view

### Tips
- Use Ctrl+R to run files quickly
- Use Ctrl+T for AI chat
- Use F1 for help anytime
""")

    def _cmd_clear(self):
        """Clear the display"""
        self.rich_display.clear()
        self.show_welcome_message()

    def _cmd_theme(self, args: List[str]):
        """Change theme"""
        if not args:
            themes = self.theme_manager.list_themes()
            self.rich_display.print_text("Available themes:")
            for theme_id, theme_name in themes.items():
                current = " (current)" if theme_id == self.config.theme.value else ""
                self.rich_display.print_text(f"  {theme_id}: {theme_name}{current}")
        else:
            theme_name = args[0]
            try:
                if hasattr(UITheme, theme_name.upper()):
                    self.set_theme(UITheme[theme_name.upper()])
                else:
                    self.set_theme(theme_name)
            except (ValueError, KeyError):
                self.show_error(f"Unknown theme: {theme_name}")

    def _cmd_status(self):
        """Show system status"""
        theme_name = self.current_theme.name if self.current_theme else "Unknown"
        self.rich_display.print_table(
            headers=["Component", "Status", "Details"],
            rows=[
                ["Theme System", "✅ Active", theme_name],
                ["Visual Feedback", "✅ Active", "Real-time indicators"],
                [
                    "Command Suggestions",
                    "✅ Active",
                    f"{len(self.command_suggestions.registry.commands)} commands",
                ],
                [
                    "Rich Display",
                    "✅ Active",
                    f"{len(self.rich_display.output_buffer)} elements",
                ],
                [
                    "Keyboard Shortcuts",
                    "✅ Active" if self.config.keyboard_shortcuts else "❌ Disabled",
                    f"{len(self.keyboard_handler.shortcuts)} shortcuts",
                ],
                [
                    "Dashboard",
                    "✅ Active" if self.dashboard.enabled else "❌ Disabled",
                    f"{len(self.dashboard.widgets)} widgets",
                ],
            ],
        )

    def _cmd_dashboard(self, args: List[str]):
        """Toggle dashboard"""
        if args and args[0] == "off":
            self.hide_dashboard()
            self.show_info("Dashboard hidden")
        else:
            self.show_dashboard()
            self.show_info("Dashboard displayed")

    def _cmd_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts = self.keyboard_handler.list_shortcuts()
        if shortcuts:
            rows = [[key, desc] for key, desc in shortcuts.items()]
            self.rich_display.print_table(
                headers=["Shortcut", "Description"], rows=rows
            )
        else:
            self.show_info("No keyboard shortcuts registered")

    def _cmd_exit(self):
        """Exit the interface"""
        self.show_info("Goodbye! 👋")
        # Would trigger application exit

    def _shortcut_run(self):
        """Keyboard shortcut for run command"""
        self.show_info("Quick run - enter filename:")

    def _shortcut_chat(self):
        """Keyboard shortcut for chat"""
        self.show_info("AI Chat activated - type your message:")

    def _shortcut_clear(self):
        """Keyboard shortcut for clear"""
        self._cmd_clear()

    def _shortcut_help(self):
        """Keyboard shortcut for help"""
        self._cmd_help([])

    def _shortcut_quit(self):
        """Keyboard shortcut for quit"""
        self._cmd_exit()

    def add_callback(self, event: str, callback: Callable):
        """Add event callback"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def remove_callback(self, event: str, callback: Callable):
        """Remove event callback"""
        if event in self.callbacks and callback in self.callbacks[event]:
            self.callbacks[event].remove(callback)

    def _notify_callbacks(self, event: str, data: Any):
        """Notify event callbacks"""
        for callback in self.callbacks.get(event, []):
            try:
                callback(data)
            except Exception as e:
                print(f"Error in callback for {event}: {e}")

    # Convenience methods for display
    def show_text(self, text: str, style: Optional[TextStyle] = None):
        """Show plain text"""
        self.rich_display.print_text(text, style)

    def show_markdown(self, markdown: str):
        """Show markdown content"""
        self.rich_display.print_markdown(markdown)

    def show_code(self, code: str, language: CodeLanguage = CodeLanguage.aetherCODE):
        """Show code with syntax highlighting"""
        self.rich_display.print_code(code, language)

    def show_success(self, message: str, details: Optional[str] = None):
        """Show success message"""
        self.rich_display.print_success(message, details)

    def show_error(self, message: str, details: Optional[str] = None):
        """Show error message"""
        self.rich_display.print_error(message, details)

    def show_warning(self, message: str, details: Optional[str] = None):
        """Show warning message"""
        self.rich_display.print_warning(message, details)

    def show_info(self, message: str, details: Optional[str] = None):
        """Show info message"""
        self.rich_display.print_info(message, details)

    def show_thinking(self, message: str = "AI is thinking..."):
        """Show AI thinking indicator"""
        self.visual_feedback.show_thinking(message)

    def hide_thinking(self):
        """Hide AI thinking indicator"""
        self.visual_feedback.hide_thinking()

    def cleanup(self):
        """Clean up resources"""
        self.visual_feedback.cleanup()
        self.rich_display.clear()
        self.is_initialized = False
