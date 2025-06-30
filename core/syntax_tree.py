# core/syntax_tree.py
"""
Enhanced NeuroCode Syntax Tree Parser
=====================================

This module provides a comprehensive syntax tree representation for NeuroCode,
supporting multi-line blocks, function definitions, and complex control flow.
"""

import re
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


@dataclass
class SyntaxNode:
    """A node in the NeuroCode syntax tree"""

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


class NeuroCodeParser:
    """Enhanced parser for NeuroCode syntax"""

    def __init__(self):
        self.current_line = 0
        self.indent_stack = [0]

        # Enhanced patterns for multi-line support
        self.patterns = {
            "comment": re.compile(r"^\s*#(.*)$"),
            "goal": re.compile(r"^\s*goal:\s*(.+?)(?:\s+priority:\s*(\w+))?$"),
            "memory_remember": re.compile(r'^\s*remember\("([^"]+)"\)(?:\s+as\s+"([^"]+)")?$'),
            "memory_recall": re.compile(r'^\s*recall\s+"([^"]+)"$'),
            "memory_recall_adv": re.compile(r'^\s*recall\s+"([^"]+)"(?:\s+since\s+"([^"]+)")?(?:\s+in\s+category\s+"([^"]+)")?\s*$'),
            "memory_search": re.compile(r'^\s*memory\.search\("([^"]+)"\)\s*$'),
            "memory_pattern": re.compile(
                r'^\s*memory\.pattern\("([^"]+)"(?:,\s*frequency="([^"]+)")?\)$'
            ),
            "assistant": re.compile(r'^\s*assistant:\s*"([^"]+)"$'),
            "plugin": re.compile(r"^\s*plugin:\s*(\w+)\s+(.+)$"),
            "function_def": re.compile(r"^\s*define\s+(\w+)\s*\((.*?)\)\s*$"),
            "function_call": re.compile(r"^\s*run\s+(\w+)\s*\((.*?)\)\s*$"),
            "variable_assign": re.compile(r"^\s*(\w+)\s*=\s*(.+)$"),
            "if_statement": re.compile(r"^\s*if\s+(.+?):\s*$"),
            "else_statement": re.compile(r"^\s*else:\s*$"),
            "for_loop": re.compile(r"^\s*for\s+(\w+)\s+in\s+(.+?):\s*$"),
            "while_loop": re.compile(r"^\s*while\s+(.+?):\s*$"),
            "end_block": re.compile(r"^\s*end\s*$"),
            "expression": re.compile(r"^\s*(.+)$"),
        }

    def parse(self, code: str) -> SyntaxNode:
        """Parse NeuroCode into a syntax tree"""
        lines = code.strip().split("\n")
        root = SyntaxNode(NodeType.PROGRAM, metadata={"total_lines": len(lines)})

        self.current_line = 0
        self._parse_block(lines, root)

        return root

    def _parse_block(self, lines: List[str], parent: SyntaxNode, target_indent: int = 0) -> int:
        """Parse a block of code with proper indentation handling"""
        i = self.current_line

        while i < len(lines):
            line = lines[i]

            # Skip empty lines
            if not line.strip():
                i += 1
                continue

            # Calculate indentation
            indent = len(line) - len(line.lstrip())

            # If indentation decreased, return to parent block
            if indent < target_indent:
                self.current_line = i
                return i

            # Parse the line
            node = self._parse_line(line, i + 1)
            if node:
                if parent.children is None:
                    parent.children = []
                parent.children.append(node)
                # Handle multi-line blocks
                if self._is_block_start(line):
                    i += 1
                    self.current_line = i
                    # Use the actual indentation of the next line as target
                    next_target = indent + 4
                    i = self._parse_block(lines, node, next_target)
                    continue

            i += 1

        self.current_line = i
        return i

    def _parse_line(self, line: str, line_number: int) -> Optional[SyntaxNode]:
        """Parse a single line of NeuroCode"""
        line = line.strip()

        # Comments
        if match := self.patterns["comment"].match(line):
            return SyntaxNode(
                NodeType.COMMENT, value=match.group(1).strip(), line_number=line_number
            )

        # Goals
        if match := self.patterns["goal"].match(line):
            goal_text = match.group(1)
            priority = match.group(2) or "medium"
            return SyntaxNode(
                NodeType.GOAL,
                value=goal_text,
                metadata={"priority": priority},
                line_number=line_number,
            )

        # Memory operations
        if match := self.patterns["memory_remember"].match(line):
            content = match.group(1)
            tag = match.group(2)
            return SyntaxNode(
                NodeType.MEMORY,
                value={"action": "remember", "content": content, "tag": tag},
                line_number=line_number,
            )

        if match := self.patterns["memory_recall"].match(line):
            tag = match.group(1)
            return SyntaxNode(
                NodeType.MEMORY, value={"action": "recall", "tag": tag}, line_number=line_number
            )

        if match := self.patterns["memory_pattern"].match(line):
            pattern = match.group(1)
            frequency = match.group(2)
            return SyntaxNode(
                NodeType.MEMORY,
                value={"action": "pattern", "pattern": pattern, "frequency": frequency},
                line_number=line_number,
            )

        # Advanced memory recall with time/category
        if match := self.patterns["memory_recall_adv"].match(line):
            tag = match.group(1)
            since = match.group(2)
            category = match.group(3)
            return SyntaxNode(
                NodeType.MEMORY,
                value={"action": "recall", "tag": tag, "since": since, "category": category},
                line_number=line_number,
            )
        # Memory search
        if match := self.patterns["memory_search"].match(line):
            keyword = match.group(1)
            return SyntaxNode(
                NodeType.MEMORY,
                value={"action": "search", "keyword": keyword},
                line_number=line_number,
            )

        # Assistant calls
        if match := self.patterns["assistant"].match(line):
            prompt = match.group(1)
            return SyntaxNode(NodeType.ASSISTANT, value=prompt, line_number=line_number)

        # Plugin calls
        if match := self.patterns["plugin"].match(line):
            plugin_name = match.group(1)
            plugin_args = match.group(2)
            return SyntaxNode(
                NodeType.PLUGIN,
                value={"name": plugin_name, "args": plugin_args},
                line_number=line_number,
            )

        # Function definitions
        if match := self.patterns["function_def"].match(line):
            func_name = match.group(1)
            params = [p.strip() for p in match.group(2).split(",") if p.strip()]
            return SyntaxNode(
                NodeType.FUNCTION_DEF,
                value={"name": func_name, "params": params},
                line_number=line_number,
            )

        # Function calls
        if match := self.patterns["function_call"].match(line):
            func_name = match.group(1)
            args = [a.strip() for a in match.group(2).split(",") if a.strip()]
            return SyntaxNode(
                NodeType.FUNCTION_CALL,
                value={"name": func_name, "args": args},
                line_number=line_number,
            )

        # Variable assignments
        if match := self.patterns["variable_assign"].match(line):
            var_name = match.group(1)
            var_value = match.group(2)
            return SyntaxNode(
                NodeType.VARIABLE_ASSIGN,
                value={"name": var_name, "value": var_value},
                line_number=line_number,
            )

        # Control flow
        if match := self.patterns["if_statement"].match(line):
            condition = match.group(1)
            return SyntaxNode(
                NodeType.CONDITIONAL,
                value={"type": "if", "condition": condition},
                line_number=line_number,
            )

        if match := self.patterns["else_statement"].match(line):
            return SyntaxNode(NodeType.CONDITIONAL, value={"type": "else"}, line_number=line_number)

        if match := self.patterns["for_loop"].match(line):
            var_name = match.group(1)
            iterable = match.group(2)
            return SyntaxNode(
                NodeType.LOOP,
                value={"type": "for", "var": var_name, "iterable": iterable},
                line_number=line_number,
            )

        if match := self.patterns["while_loop"].match(line):
            condition = match.group(1)
            return SyntaxNode(
                NodeType.LOOP,
                value={"type": "while", "condition": condition},
                line_number=line_number,
            )

        # End block marker
        if self.patterns["end_block"].match(line):
            return None  # End blocks are handled by block parsing logic

        # Generic expression
        if match := self.patterns["expression"].match(line):
            return SyntaxNode(NodeType.EXPRESSION, value=match.group(1), line_number=line_number)

        return None

    def _is_block_start(self, line: str) -> bool:
        """Check if a line starts a new block"""
        return bool(
            self.patterns["function_def"].match(line)
            or self.patterns["if_statement"].match(line)
            or self.patterns["else_statement"].match(line)
            or self.patterns["for_loop"].match(line)
            or self.patterns["while_loop"].match(line)
        )


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


def parse_neurocode(code: str) -> SyntaxNode:
    """Parse NeuroCode into a syntax tree"""
    parser = NeuroCodeParser()
    return parser.parse(code)


def analyze_syntax_tree(tree: SyntaxNode) -> Dict[str, Any]:
    """Analyze a syntax tree and return statistics"""

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
        "total_lines": tree.metadata.get("total_lines", 0) if tree.metadata else 0,
    }


def _calculate_depth(node: SyntaxNode, current_depth: int = 0) -> int:
    """Calculate the maximum depth of a syntax tree"""
    if not node.children:
        return current_depth

    max_child_depth = max(_calculate_depth(child, current_depth + 1) for child in node.children)
    return max_child_depth
