# core/syntax_tree.py
"""
AetherraCode Syntax Tree Parser (Modular Interface)
================================================

This module provides a compatibility interface to the new modular syntax system.
For new development, use the modular system directly from core.syntax.

The modular syntax system is organized as follows:
- core/syntax/nodes.py - Node types and data structures
- core/syntax/parser.py - Parser implementation
- core/syntax/visitor.py - Visitor pattern implementation
- core/syntax/analysis.py - Analysis utilities
- core/syntax/__init__.py - Main API

This file maintains backward compatibility with existing code.
"""

from typing import Any, Dict

# Import everything from the new modular system
try:
    from core.syntax import parse_aetherra
    from core.syntax.analysis import analyze_syntax_tree as _analyze_syntax_tree
    from core.syntax.nodes import NodeType, SyntaxNode  # type: ignore
    from core.syntax.parser import AetherraParser  # type: ignore
    from core.syntax.visitor import SyntaxTreeVisitor  # type: ignore

    # Flag to indicate successful import
    _SYNTAX_AVAILABLE = True

except ImportError:
    # Fallback: create stub classes for compatibility
    class NodeType:  # type: ignore
        """Stub NodeType class for when core.syntax is not available."""

        pass

    class SyntaxNode:  # type: ignore
        """Stub SyntaxNode class for when core.syntax is not available."""

        pass

    class AetherraParser:  # type: ignore
        """Stub AetherraParser class for when core.syntax is not available."""

        pass

    class SyntaxTreeVisitor:  # type: ignore
        """Stub SyntaxTreeVisitor class for when core.syntax is not available."""

        pass

    def parse_aetherra(code: str) -> Any:
        """Stub parse_aetherra function for when core.syntax is not available."""
        return SyntaxNode()

    # Flag to indicate failed import
    _SYNTAX_AVAILABLE = False


def analyze_syntax_tree(node: Any) -> Dict[str, Any]:
    """
    Analyze syntax tree with backward compatibility.

    This function maintains backward compatibility while using the new modular system.
    """
    if _SYNTAX_AVAILABLE:
        # _analyze_syntax_tree is guaranteed to be available when _SYNTAX_AVAILABLE is True
        return _analyze_syntax_tree(node)  # type: ignore
    else:
        # Fallback implementation
        return {}


# Legacy function for backward compatibility
def _calculate_depth(node: Any, current_depth: int = 0) -> int:
    """Calculate the maximum depth of a syntax tree (legacy function)"""
    try:
        from .syntax.analysis import _calculate_depth as new_calculate_depth

        return new_calculate_depth(node, current_depth)
    except ImportError:
        # Fallback implementation
        if not hasattr(node, "children") or not node.children:
            return current_depth

        max_depth = current_depth
        for child in node.children:
            child_depth = _calculate_depth(child, current_depth + 1)
            max_depth = max(max_depth, child_depth)

        return max_depth


# Export the same API as the original monolithic module
__all__ = [
    "NodeType",
    "SyntaxNode",
    "AetherraParser",
    "SyntaxTreeVisitor",
    "parse_aetherra",
    "analyze_syntax_tree",
]
