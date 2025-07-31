# core/syntax/nodes.py
"""
AetherraCode Syntax Tree Node Definitions
=====================================

This module defines the node types and data structures used in AetherraCode's
abstract syntax tree representation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class NodeType(Enum):
    """Types of syntax tree nodes"""

    PROGRAM = "program"
    GOAL = "goal"
    MEMORY = "memory"
    ASSISTANT = "assistant"
    PLUGIN = "plugin"
    FUNCTION_DEF = "function_def"
    FUNCTION_CALL = "function_call"
    VARIABLE_ASSIGN = "variable_assign"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    BLOCK = "block"
    EXPRESSION = "expression"
    LITERAL = "literal"
    COMMENT = "comment"
    AGENT = "agent"
    AGENT_MODE = "agent_mode"
    AGENT_GOAL = "agent_goal"


@dataclass
class SyntaxNode:
    """A node in the AetherraCode syntax tree"""

    type: NodeType
    value: Any = None
    children: Optional[List["SyntaxNode"]] = None
    metadata: Optional[Dict[str, Any]] = None
    line_number: int = 0

    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.metadata is None:
            self.metadata = {}

    def add_child(self, child: "SyntaxNode") -> None:
        """Add a child node to this node"""
        if self.children is None:
            self.children = []
        self.children.append(child)

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value safely"""
        if self.metadata is None:
            return default
        return self.metadata.get(key, default)

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value safely"""
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value

    def has_children(self) -> bool:
        """Check if this node has children"""
        return self.children is not None and len(self.children) > 0

    def child_count(self) -> int:
        """Get the number of children"""
        return len(self.children) if self.children is not None else 0

    def __repr__(self) -> str:
        """String representation for debugging"""
        return (
            f"SyntaxNode(type={self.type.value}, value={self.value}, children={self.child_count()})"
        )
