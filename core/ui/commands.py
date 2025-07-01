"""
💡 Command Suggestions System
============================

Provides intelligent command suggestions, auto-completion, and keyboard shortcuts
for the Neuroplex interface.
"""

import difflib
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set


class CommandCategory(Enum):
    """Categories of commands"""

    CORE = "core"
    NEUROCODE = "neurocode"
    MEMORY = "memory"
    PLUGIN = "plugin"
    SYSTEM = "system"
    AI = "ai"
    DEBUG = "debug"
    HELP = "help"


@dataclass
class Command:
    """Command definition"""

    name: str
    category: CommandCategory
    description: str
    usage: str
    examples: List[str]
    aliases: Optional[List[str]] = None
    parameters: Optional[List[str]] = None
    shortcuts: Optional[List[str]] = None

    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []
        if self.parameters is None:
            self.parameters = []
        if self.shortcuts is None:
            self.shortcuts = []


@dataclass
class Suggestion:
    """Command suggestion with metadata"""

    command: Command
    score: float
    reason: str
    context_match: bool = False


class CommandRegistry:
    """Registry of all available commands"""

    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self.aliases: Dict[str, str] = {}
        self.shortcuts: Dict[str, str] = {}
        self.categories: Dict[CommandCategory, List[str]] = defaultdict(list)
        self._initialize_core_commands()

    def _initialize_core_commands(self):
        """Initialize core system commands"""
        core_commands = [
            Command(
                name="help",
                category=CommandCategory.HELP,
                description="Show help information",
                usage="help [command]",
                examples=["help", "help run", "help memory"],
                aliases=["h", "?"],
                shortcuts=["F1"],
            ),
            Command(
                name="run",
                category=CommandCategory.NEUROCODE,
                description="Execute NeuroCode program",
                usage="run <file.neuro> [args...]",
                examples=["run hello.neuro", "run demo.neuro --verbose"],
                aliases=["execute", "exec"],
                shortcuts=["Ctrl+R"],
            ),
            Command(
                name="parse",
                category=CommandCategory.NEUROCODE,
                description="Parse NeuroCode file and show AST",
                usage="parse <file.neuro>",
                examples=["parse hello.neuro"],
                aliases=["ast"],
                shortcuts=["Ctrl+P"],
            ),
            Command(
                name="memory",
                category=CommandCategory.MEMORY,
                description="Manage AI memory system",
                usage="memory <action> [args...]",
                examples=["memory list", "memory search query", "memory clear"],
                aliases=["mem"],
                parameters=["list", "search", "clear", "save", "load"],
            ),
            Command(
                name="chat",
                category=CommandCategory.AI,
                description="Start AI chat session",
                usage="chat [message]",
                examples=["chat", "chat How do I write a loop?"],
                aliases=["ai", "ask"],
                shortcuts=["Ctrl+T"],
            ),
            Command(
                name="plugin",
                category=CommandCategory.PLUGIN,
                description="Manage plugins",
                usage="plugin <action> [name]",
                examples=["plugin list", "plugin install math", "plugin remove old"],
                aliases=["plugins", "ext"],
                parameters=["list", "install", "remove", "enable", "disable", "info"],
            ),
            Command(
                name="theme",
                category=CommandCategory.SYSTEM,
                description="Change UI theme",
                usage="theme <theme_name>",
                examples=["theme dark", "theme neon", "theme matrix"],
                parameters=["dark", "light", "neon", "matrix", "cyberpunk"],
            ),
            Command(
                name="debug",
                category=CommandCategory.DEBUG,
                description="Debug NeuroCode programs",
                usage="debug <file.neuro> [breakpoints...]",
                examples=["debug test.neuro", "debug app.neuro 10 25"],
                aliases=["dbg"],
                shortcuts=["F5"],
            ),
            Command(
                name="clear",
                category=CommandCategory.SYSTEM,
                description="Clear terminal screen",
                usage="clear",
                examples=["clear"],
                aliases=["cls"],
                shortcuts=["Ctrl+L"],
            ),
            Command(
                name="status",
                category=CommandCategory.SYSTEM,
                description="Show system status",
                usage="status",
                examples=["status"],
                aliases=["info", "stat"],
            ),
            Command(
                name="exit",
                category=CommandCategory.SYSTEM,
                description="Exit Neuroplex",
                usage="exit",
                examples=["exit"],
                aliases=["quit", "q"],
                shortcuts=["Ctrl+Q", "Alt+F4"],
            ),
        ]

        for cmd in core_commands:
            self.register_command(cmd)

    def register_command(self, command: Command):
        """Register a new command"""
        self.commands[command.name] = command
        self.categories[command.category].append(command.name)

        # Register aliases
        if command.aliases:
            for alias in command.aliases:
                self.aliases[alias] = command.name

        # Register shortcuts
        if command.shortcuts:
            for shortcut in command.shortcuts:
                self.shortcuts[shortcut] = command.name

    def get_command(self, name: str) -> Optional[Command]:
        """Get command by name or alias"""
        # Check direct name
        if name in self.commands:
            return self.commands[name]

        # Check aliases
        if name in self.aliases:
            return self.commands[self.aliases[name]]

        return None

    def get_all_commands(self) -> List[Command]:
        """Get all registered commands"""
        return list(self.commands.values())

    def get_commands_by_category(self, category: CommandCategory) -> List[Command]:
        """Get commands by category"""
        return [self.commands[name] for name in self.categories[category]]

    def get_command_names(self, include_aliases: bool = True) -> List[str]:
        """Get all command names"""
        names = list(self.commands.keys())
        if include_aliases:
            names.extend(self.aliases.keys())
        return sorted(names)


class CommandSuggestions:
    """Intelligent command suggestion system"""

    def __init__(self):
        self.registry = CommandRegistry()
        self.usage_history: List[str] = []
        self.max_history = 1000
        self.context_hints: Dict[str, Set[str]] = defaultdict(set)
        self._build_context_hints()

    def _build_context_hints(self):
        """Build context hints for better suggestions"""
        # File-related contexts
        self.context_hints["file"].update(["run", "parse", "debug", "edit"])
        self.context_hints["neuro"].update(["run", "parse", "debug"])

        # Memory contexts
        self.context_hints["memory"].update(["memory", "search", "save", "load"])
        self.context_hints["remember"].update(["memory"])

        # AI contexts
        self.context_hints["ai"].update(["chat", "ask", "help"])
        self.context_hints["question"].update(["chat", "help"])

        # Plugin contexts
        self.context_hints["plugin"].update(["plugin", "install", "remove"])
        self.context_hints["extension"].update(["plugin"])

        # System contexts
        self.context_hints["theme"].update(["theme"])
        self.context_hints["clear"].update(["clear", "cls"])
        self.context_hints["exit"].update(["exit", "quit"])

    def add_to_history(self, command: str):
        """Add command to usage history"""
        self.usage_history.append(command)
        if len(self.usage_history) > self.max_history:
            self.usage_history.pop(0)

    def get_suggestions(self, partial_input: str, max_suggestions: int = 10) -> List[Suggestion]:
        """Get command suggestions for partial input"""
        suggestions = []

        if not partial_input.strip():
            # No input - suggest popular commands
            suggestions.extend(self._get_popular_commands(max_suggestions))
        else:
            # Get suggestions based on partial input
            suggestions.extend(self._get_prefix_matches(partial_input))
            suggestions.extend(self._get_fuzzy_matches(partial_input))
            suggestions.extend(self._get_context_matches(partial_input))

        # Sort by score and remove duplicates
        unique_suggestions = {}
        for suggestion in suggestions:
            key = suggestion.command.name
            if key not in unique_suggestions or suggestion.score > unique_suggestions[key].score:
                unique_suggestions[key] = suggestion

        sorted_suggestions = sorted(
            unique_suggestions.values(),
            key=lambda s: (s.score, s.context_match, self._get_popularity_score(s.command.name)),
            reverse=True,
        )

        return sorted_suggestions[:max_suggestions]

    def _get_prefix_matches(self, partial: str) -> List[Suggestion]:
        """Get commands that start with the partial input"""
        suggestions = []
        partial_lower = partial.lower()

        for name, command in self.registry.commands.items():
            if name.lower().startswith(partial_lower):
                score = len(partial) / len(name)  # Longer matches get higher scores
                suggestions.append(
                    Suggestion(
                        command=command,
                        score=score + 0.5,  # Boost prefix matches
                        reason=f"Starts with '{partial}'",
                    )
                )

            # Check aliases too
            if command.aliases:
                for alias in command.aliases:
                    if alias.lower().startswith(partial_lower):
                        score = len(partial) / len(alias)
                        suggestions.append(
                            Suggestion(
                                command=command,
                                score=score + 0.3,  # Aliases get slightly lower score
                                reason=f"Alias '{alias}' starts with '{partial}'",
                            )
                        )

        return suggestions

    def _get_fuzzy_matches(self, partial: str) -> List[Suggestion]:
        """Get fuzzy string matches"""
        suggestions = []
        partial_lower = partial.lower()

        # Use difflib for fuzzy matching
        command_names = list(self.registry.commands.keys())
        matches = difflib.get_close_matches(
            partial_lower, [name.lower() for name in command_names], n=5, cutoff=0.3
        )

        for match in matches:
            # Find the original command name
            original_name = None
            for name in command_names:
                if name.lower() == match:
                    original_name = name
                    break

            if original_name:
                command = self.registry.commands[original_name]
                score = difflib.SequenceMatcher(None, partial_lower, match).ratio()
                suggestions.append(
                    Suggestion(
                        command=command,
                        score=score * 0.7,  # Reduce score for fuzzy matches
                        reason=f"Similar to '{partial}'",
                    )
                )

        return suggestions

    def _get_context_matches(self, partial: str) -> List[Suggestion]:
        """Get suggestions based on context hints"""
        suggestions = []
        partial_lower = partial.lower()

        for context, command_names in self.context_hints.items():
            if context in partial_lower:
                for command_name in command_names:
                    if command_name in self.registry.commands:
                        command = self.registry.commands[command_name]
                        suggestions.append(
                            Suggestion(
                                command=command,
                                score=0.6,
                                reason=f"Context match for '{context}'",
                                context_match=True,
                            )
                        )

        return suggestions

    def _get_popular_commands(self, count: int = 5) -> List[Suggestion]:
        """Get most popular commands from history"""
        suggestions = []

        # Count command frequency
        command_counts = defaultdict(int)
        for cmd in self.usage_history[-100:]:  # Look at recent history
            base_cmd = cmd.split()[0] if cmd.split() else cmd
            command_counts[base_cmd] += 1

        # Get top commands
        popular_commands = sorted(command_counts.items(), key=lambda x: x[1], reverse=True)

        for cmd_name, freq in popular_commands[:count]:
            command = self.registry.get_command(cmd_name)
            if command:
                suggestions.append(
                    Suggestion(
                        command=command,
                        score=0.8,
                        reason=f"Popular command (used {freq} times recently)",
                    )
                )

        # Add some default popular commands if history is empty
        if not suggestions:
            default_popular = ["help", "run", "chat", "memory", "status"]
            for cmd_name in default_popular:
                command = self.registry.get_command(cmd_name)
                if command:
                    suggestions.append(
                        Suggestion(command=command, score=0.5, reason="Default popular command")
                    )

        return suggestions

    def _get_popularity_score(self, command_name: str) -> float:
        """Get popularity score for a command"""
        recent_history = self.usage_history[-50:]
        count = sum(1 for cmd in recent_history if cmd.startswith(command_name))
        return count / len(recent_history) if recent_history else 0

    def get_parameter_suggestions(self, command_name: str, current_params: List[str]) -> List[str]:
        """Get parameter suggestions for a specific command"""
        command = self.registry.get_command(command_name)
        if not command or not command.parameters:
            return []

        # Filter out already used parameters
        available_params = [p for p in command.parameters if p not in current_params]
        return available_params

    def get_shortcut_info(self, command_name: str) -> List[str]:
        """Get keyboard shortcuts for a command"""
        command = self.registry.get_command(command_name)
        return command.shortcuts if command and command.shortcuts else []

    def search_commands(self, query: str) -> List[Command]:
        """Search commands by description or name"""
        results = []
        query_lower = query.lower()

        for command in self.registry.get_all_commands():
            # Search in name
            if query_lower in command.name.lower():
                results.append(command)
                continue

            # Search in description
            if query_lower in command.description.lower():
                results.append(command)
                continue

            # Search in aliases
            if command.aliases:
                for alias in command.aliases:
                    if query_lower in alias.lower():
                        results.append(command)
                        break

        return results

    def register_custom_command(self, command: Command):
        """Register a custom command"""
        self.registry.register_command(command)
