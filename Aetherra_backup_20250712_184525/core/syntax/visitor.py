# core/syntax/visitor.py
"""
AetherraCode Syntax Tree Visitor
=============================

This module provides the visitor pattern implementation for traversing
and processing AetherraCode syntax trees.
"""

from typing import Any, List

from .nodes import SyntaxNode


class SyntaxTreeVisitor:
    """Visitor pattern for syntax tree traversal"""

    def visit(self, node: SyntaxNode) -> Any:
        """Visit a node in the syntax tree"""
        method_name = f"visit_{node.type.value}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: SyntaxNode) -> Any:
        """Default visitor for unhandled node types"""
        children = node.children if node.children is not None else []
        results = []
        for child in children:
            results.append(self.visit(child))
        return results

    def visit_program(self, node: SyntaxNode) -> List[Any]:
        children = node.children if node.children is not None else []
        return [self.visit(child) for child in children]

    def visit_goal(self, node: SyntaxNode) -> str:
        meta = node.metadata if node.metadata is not None else {}
        return f"Goal: {node.value} (Priority: {meta.get('priority', 'medium')})"

    def visit_memory(self, node: SyntaxNode) -> str:
        """Visit a memory operation node"""
        action = node.value["action"]
        if action == "remember":
            content = node.value["content"]
            tag = node.value.get("tag", "general")
            return f"Remember: '{content}' as '{tag}'"
        elif action == "recall":
            tag = node.value.get("tag")
            since = node.value.get("since")
            category = node.value.get("category")
            details = f"Recall: '{tag}'"
            if since:
                details += f" since '{since}'"
            if category:
                details += f" in category '{category}'"
            return details
        elif action == "search":
            keyword = node.value["keyword"]
            return f"Search memory for: '{keyword}'"
        elif action == "pattern":
            pattern = node.value["pattern"]
            frequency = node.value.get("frequency", "any")
            return f"Pattern: '{pattern}' frequency: {frequency}"
        else:
            return f"Memory: {action}"

    def visit_assistant(self, node: SyntaxNode) -> str:
        """Visit an assistant call node"""
        return f"Assistant: '{node.value}'"

    def visit_plugin(self, node: SyntaxNode) -> str:
        """Visit a plugin call node"""
        name = node.value["name"]
        args = node.value["args"]
        return f"Plugin: {name} {args}"

    def visit_function_def(self, node: SyntaxNode) -> str:
        """Visit a function definition node"""
        name = node.value["name"]
        params = node.value["params"]
        return f"Function: {name}({', '.join(params)})"

    def visit_function_call(self, node: SyntaxNode) -> str:
        """Visit a function call node"""
        name = node.value["name"]
        args = node.value["args"]
        return f"Call: {name}({', '.join(args)})"

    def visit_variable_assign(self, node: SyntaxNode) -> str:
        """Visit a variable assignment node"""
        name = node.value["name"]
        value = node.value["value"]
        return f"Assign: {name} = {value}"

    def visit_conditional(self, node: SyntaxNode) -> str:
        """Visit a conditional node"""
        if node.value["type"] == "if":
            condition = node.value["condition"]
            return f"If: {condition}"
        else:
            return "Else"

    def visit_loop(self, node: SyntaxNode) -> str:
        """Visit a loop node"""
        if node.value["type"] == "for":
            var = node.value["var"]
            iterable = node.value["iterable"]
            return f"For: {var} in {iterable}"
        elif node.value["type"] == "while":
            condition = node.value["condition"]
            return f"While: {condition}"
        else:
            return f"Loop: {node.value['type']}"

    def visit_expression(self, node: SyntaxNode) -> str:
        """Visit an expression node"""
        return f"Expression: {node.value}"

    def visit_comment(self, node: SyntaxNode) -> str:
        """Visit a comment node"""
        return f"Comment: {node.value}"

    def visit_agent(self, node: SyntaxNode) -> str:
        """Visit an agent operation node"""
        action = node.value["action"]
        if action == "start":
            return "Start Agent"
        elif action == "stop":
            return "Stop Agent"
        elif action == "status":
            return "Get Agent Status"
        else:
            return f"Agent: {action}"

    def visit_agent_mode(self, node: SyntaxNode) -> str:
        """Visit an agent mode setting node"""
        mode = node.value["mode"]
        return f"Set Agent Mode: {mode}"

    def visit_agent_goal(self, node: SyntaxNode) -> str:
        """Visit an agent goal operation node"""
        action = node.value["action"]
        if action == "add":
            goal = node.value["goal"]
            priority = node.value.get("priority", "medium")
            return f"Add Agent Goal: '{goal}' (Priority: {priority})"
        elif action == "clear":
            return "Clear Agent Goals"
        else:
            return f"Agent Goal: {action}"


class SyntaxTreeTransformer(SyntaxTreeVisitor):
    """Base class for syntax tree transformations"""

    def transform(self, node: SyntaxNode) -> SyntaxNode:
        """Transform a syntax tree, returning a new tree"""
        return self.visit(node)

    def generic_visit(self, node: SyntaxNode) -> SyntaxNode:
        """Transform children and return a new node"""
        if node.children:
            new_children = [self.visit(child) for child in node.children]
        else:
            new_children = []

        # Create a new node with transformed children
        new_node = SyntaxNode(
            type=node.type,
            value=node.value,
            children=new_children,
            metadata=node.metadata.copy() if node.metadata else {},
            line_number=node.line_number,
        )
        return new_node


class SyntaxTreeAnalyzer(SyntaxTreeVisitor):
    """Specialized visitor for analyzing syntax trees"""

    def __init__(self):
        self.statistics = {
            "node_counts": {},
            "total_depth": 0,
            "max_depth": 0,
            "function_definitions": [],
            "variable_assignments": [],
            "memory_operations": [],
            "agent_operations": [],
        }

    def analyze(self, node: SyntaxNode) -> dict:
        """Analyze a syntax tree and return detailed statistics"""
        self.statistics = {
            "node_counts": {},
            "total_depth": 0,
            "max_depth": 0,
            "function_definitions": [],
            "variable_assignments": [],
            "memory_operations": [],
            "agent_operations": [],
        }

        self._analyze_recursive(node, 0)
        return self.statistics

    def _analyze_recursive(self, node: SyntaxNode, depth: int) -> None:
        """Recursively analyze nodes"""
        # Update statistics
        node_type = node.type.value
        self.statistics["node_counts"][node_type] = (
            self.statistics["node_counts"].get(node_type, 0) + 1
        )
        self.statistics["max_depth"] = max(self.statistics["max_depth"], depth)

        # Collect specific node information
        if node.type.value == "function_def":
            self.statistics["function_definitions"].append(node.value)
        elif node.type.value == "variable_assign":
            self.statistics["variable_assignments"].append(node.value)
        elif node.type.value == "memory":
            self.statistics["memory_operations"].append(node.value)
        elif node.type.value in ["agent", "agent_mode", "agent_goal"]:
            self.statistics["agent_operations"].append(node.value)

        # Recurse into children
        if node.children:
            for child in node.children:
                self._analyze_recursive(child, depth + 1)
