# core/syntax/analysis.py
"""
NeuroCode Syntax Tree Analysis Utilities
========================================

This module provides utilities for analyzing NeuroCode syntax trees,
including statistics, validation, and metrics collection.
"""

from typing import Any, Dict

from .nodes import NodeType, SyntaxNode


def analyze_syntax_tree(tree: SyntaxNode) -> Dict[str, Any]:
    """Analyze a syntax tree and return comprehensive statistics"""

    def count_nodes(node: SyntaxNode, counts: Dict[NodeType, int]):
        counts[node.type] = counts.get(node.type, 0) + 1
        if node.children:
            for child in node.children:
                count_nodes(child, counts)

    counts = {}
    count_nodes(tree, counts)

    return {
        "node_counts": {node_type.value: count for node_type, count in counts.items()},
        "total_nodes": sum(counts.values()),
        "max_depth": _calculate_depth(tree),
        "total_lines": tree.get_metadata("total_lines", 0),
        "complexity_score": _calculate_complexity(tree),
        "function_count": counts.get(NodeType.FUNCTION_DEF, 0),
        "memory_operations": counts.get(NodeType.MEMORY, 0),
        "agent_operations": sum([
            counts.get(NodeType.AGENT, 0),
            counts.get(NodeType.AGENT_MODE, 0),
            counts.get(NodeType.AGENT_GOAL, 0)
        ])
    }


def _calculate_depth(node: SyntaxNode, current_depth: int = 0) -> int:
    """Calculate the maximum depth of a syntax tree"""
    if not node.children:
        return current_depth

    max_child_depth = max(_calculate_depth(child, current_depth + 1) for child in node.children)
    return max_child_depth


def _calculate_complexity(node: SyntaxNode) -> int:
    """Calculate a complexity score for the syntax tree"""
    complexity = 0
    
    def traverse(n: SyntaxNode):
        nonlocal complexity
        
        # Add complexity based on node type
        if n.type in [NodeType.CONDITIONAL, NodeType.LOOP]:
            complexity += 2  # Control flow adds complexity
        elif n.type in [NodeType.FUNCTION_DEF, NodeType.FUNCTION_CALL]:
            complexity += 1  # Functions add moderate complexity
        elif n.type in [NodeType.MEMORY, NodeType.AGENT, NodeType.PLUGIN]:
            complexity += 1  # External operations add complexity
        
        # Recurse into children
        if n.children:
            for child in n.children:
                traverse(child)
    
    traverse(node)
    return complexity


def validate_syntax_tree(tree: SyntaxNode) -> Dict[str, Any]:
    """Validate a syntax tree and return validation results"""
    errors = []
    warnings = []
    
    def validate_node(node: SyntaxNode, context: str = ""):
        # Check for required fields
        if node.type is None:
            errors.append(f"Node at {context} has no type")
        
        # Validate specific node types
        if node.type == NodeType.FUNCTION_DEF:
            if not isinstance(node.value, dict) or 'name' not in node.value:
                errors.append(f"Function definition at line {node.line_number} missing name")
        
        elif node.type == NodeType.MEMORY:
            if not isinstance(node.value, dict) or 'action' not in node.value:
                errors.append(f"Memory operation at line {node.line_number} missing action")
        
        elif node.type == NodeType.GOAL:
            if not node.value:
                warnings.append(f"Empty goal at line {node.line_number}")
        
        # Recurse into children
        if node.children:
            for i, child in enumerate(node.children):
                validate_node(child, f"{context}.child[{i}]")
    
    validate_node(tree, "root")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "error_count": len(errors),
        "warning_count": len(warnings)
    }


def extract_functions(tree: SyntaxNode) -> list:
    """Extract all function definitions from a syntax tree"""
    functions = []
    
    def traverse(node: SyntaxNode):
        if node.type == NodeType.FUNCTION_DEF:
            functions.append({
                'name': node.value.get('name'),
                'params': node.value.get('params', []),
                'line': node.line_number,
                'children_count': node.child_count()
            })
        
        if node.children:
            for child in node.children:
                traverse(child)
    
    traverse(tree)
    return functions


def extract_memory_operations(tree: SyntaxNode) -> list:
    """Extract all memory operations from a syntax tree"""
    operations = []
    
    def traverse(node: SyntaxNode):
        if node.type == NodeType.MEMORY:
            operations.append({
                'action': node.value.get('action'),
                'details': node.value,
                'line': node.line_number
            })
        
        if node.children:
            for child in node.children:
                traverse(child)
    
    traverse(tree)
    return operations


def generate_summary_report(tree: SyntaxNode) -> str:
    """Generate a human-readable summary report of the syntax tree"""
    analysis = analyze_syntax_tree(tree)
    validation = validate_syntax_tree(tree)
    functions = extract_functions(tree)
    memory_ops = extract_memory_operations(tree)
    
    report = []
    report.append("NeuroCode Syntax Tree Analysis Report")
    report.append("=" * 40)
    report.append(f"Total nodes: {analysis['total_nodes']}")
    report.append(f"Maximum depth: {analysis['max_depth']}")
    report.append(f"Complexity score: {analysis['complexity_score']}")
    report.append(f"Total lines: {analysis['total_lines']}")
    report.append("")
    
    report.append("Node Distribution:")
    for node_type, count in analysis['node_counts'].items():
        report.append(f"  {node_type}: {count}")
    report.append("")
    
    if functions:
        report.append("Functions:")
        for func in functions:
            params = ', '.join(func['params']) if func['params'] else '()'
            report.append(f"  {func['name']}({params}) at line {func['line']}")
        report.append("")
    
    if memory_ops:
        report.append("Memory Operations:")
        for op in memory_ops:
            report.append(f"  {op['action']} at line {op['line']}")
        report.append("")
    
    if not validation['valid']:
        report.append("Validation Issues:")
        for error in validation['errors']:
            report.append(f"  ERROR: {error}")
        for warning in validation['warnings']:
            report.append(f"  WARNING: {warning}")
    else:
        report.append("✓ Syntax tree validation passed")
    
    return "\n".join(report)
