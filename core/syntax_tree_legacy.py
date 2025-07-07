# core/syntax_tree_legacy.py
"""
Legacy AetherraCode Syntax Tree Parser (Backup)
============================================

This is the original monolithic syntax_tree.py preserved for reference
and backward compatibility. The new modular system is in core/syntax/.
"""

# This file contains the original content of syntax_tree.py
# It has been preserved for backward compatibility and reference.
# New code should use the modular system in core/syntax/

# The original implementation has been moved to core/syntax/ with the following structure:
# - core/syntax/nodes.py - Node types and data structures
# - core/syntax/parser.py - Parser implementation
# - core/syntax/visitor.py - Visitor pattern implementation
# - core/syntax/analysis.py - Analysis utilities
# - core/syntax/__init__.py - Main API

# For backward compatibility, import from the new modular system:
    AetherraParser,
    NodeType,
    SyntaxNode,
    SyntaxTreeVisitor,
    analyze_syntax_tree,
    parse_aetherra,
)


# Legacy function aliases for backward compatibility
def _calculate_depth(node, current_depth=0):
    """Legacy function - use analyze_syntax_tree instead"""
    from .syntax.analysis import _calculate_depth as new_calculate_depth

    return new_calculate_depth(node, current_depth)


# Preserve the original API
__all__ = [
    "NodeType",
    "SyntaxNode",
    "AetherraParser",
    "SyntaxTreeVisitor",
    "parse_aetherra",
    "analyze_syntax_tree",
]
