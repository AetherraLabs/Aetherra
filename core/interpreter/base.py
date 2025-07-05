# core/interpreter/base.py
"""
AetherraCode Interpreter Base Classes
=================================

Core interfaces and base classes for the modular interpreter system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


@dataclass
class ExecutionResult:
    """Result of executing a AetherraCode command"""

    success: bool
    output: str
    command_type: str
    execution_time: float
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class ParseResult:
    """Result of parsing a AetherraCode command"""

    command_type: str
    command_name: str
    parameters: Dict[str, Any]
    raw_line: str
    enhanced: bool = False


class AetherraCodeInterpreterBase(ABC):
    """
    Abstract base class for AetherraCode interpreters

    Defines the core interface that all interpreter implementations must follow.
    """

    def __init__(self):
        self.command_history: List[str] = []
        self.execution_stats: Dict[str, int] = {}
        self.startup_time = datetime.now()

    @abstractmethod
    def execute(self, line: str) -> Union[str, ExecutionResult]:
        """Execute a single line of AetherraCode"""
        pass

    @abstractmethod
    def parse_command(self, line: str) -> ParseResult:
        """Parse a command line into structured components"""
        pass

    @abstractmethod
    def get_command_history(self) -> List[str]:
        """Get the command execution history"""
        pass

    def track_command(self, command: str) -> None:
        """Track command usage for analytics"""
        self.command_history.append(command)
        cmd_type = command.split()[0] if command.split() else "unknown"
        self.execution_stats[cmd_type] = self.execution_stats.get(cmd_type, 0) + 1

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get interpreter execution statistics"""
        return {
            "total_commands": len(self.command_history),
            "command_types": self.execution_stats,
            "uptime": (datetime.now() - self.startup_time).total_seconds(),
            "startup_time": self.startup_time.isoformat(),
        }


class CommandHandler(ABC):
    """Base class for command handlers"""

    @abstractmethod
    def can_handle(self, command_type: str) -> bool:
        """Check if this handler can process the command type"""
        pass

    @abstractmethod
    def handle(self, parse_result: ParseResult, context: Dict[str, Any]) -> ExecutionResult:
        """Handle the parsed command"""
        pass


class InterpreterComponent(ABC):
    """Base class for interpreter components"""

    def __init__(self, name: str):
        self.name = name
        self.enabled = True

    @abstractmethod
    def initialize(self, interpreter_context: Dict[str, Any]) -> bool:
        """Initialize the component with interpreter context"""
        pass

    def enable(self) -> None:
        """Enable this component"""
        self.enabled = True

    def disable(self) -> None:
        """Disable this component"""
        self.enabled = False

    def is_enabled(self) -> bool:
        """Check if component is enabled"""
        return self.enabled
