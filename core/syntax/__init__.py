# core/syntax/__init__.py
"""
AetherraCode Syntax Module
=======================

This module provides the complete syntax infrastructure for AetherraCode, including:
- Node types and data structures
- Parser implementation
- Visitor pattern for tree traversal
- Analysis utilities

This is the modularized version of the legacy syntax_tree.py for better maintainability.
"""

from .parser import AetherraParser


# Main API functions
def parse_aetherra(code: str) -> SyntaxNode:
    """Parse AetherraCode into a syntax tree"""
    parser = AetherraParser()
    return parser.parse(code)


__all__ = [
    "NodeType",
    "SyntaxNode",
    "AetherraParser",
    "SyntaxTreeVisitor",
    "analyze_syntax_tree",
    "parse_aetherra",
]
