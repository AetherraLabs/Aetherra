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

# Import everything from the new modular system
    AetherraParser,
    NodeType,
    SyntaxNode,
    SyntaxTreeVisitor,
    analyze_syntax_tree,
    parse_neurocode,
)


# Legacy function for backward compatibility
def _calculate_depth(node, current_depth=0):
    """Calculate the maximum depth of a syntax tree (legacy function)"""
    from .syntax.analysis import _calculate_depth as new_calculate_depth

    return new_calculate_depth(node, current_depth)


# Export the same API as the original monolithic module
__all__ = [
    "NodeType",
    "SyntaxNode",
    "AetherraParser",
    "SyntaxTreeVisitor",
    "parse_neurocode",
    "analyze_syntax_tree",
]
