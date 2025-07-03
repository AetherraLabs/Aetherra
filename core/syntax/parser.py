# core/syntax/parser.py
"""
NeuroCode Parser Implementation
==============================

This module provides the main parser class for converting NeuroCode text
into a structured syntax tree.
"""

import re
from typing import List, Optional

from .nodes import NodeType, SyntaxNode


class AetherraParser:
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
            "memory_recall_adv": re.compile(
                r'^\s*recall\s+"([^"]+)"(?:\s+since\s+"([^"]+)")?(?:\s+in\s+category\s+"([^"]+)")?\s*$'
            ),
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
            # Agent control patterns
            "agent_mode": re.compile(r'^\s*agent\.mode\s*=\s*"([^"]+)"\s*$'),
            "agent_start": re.compile(r"^\s*agent\.start\(\)\s*$"),
            "agent_stop": re.compile(r"^\s*agent\.stop\(\)\s*$"),
            "agent_goal_add": re.compile(
                r'^\s*agent\.add_goal\("([^"]+)"(?:,\s*priority="([^"]+)")?\)\s*$'
            ),
            "agent_goals_clear": re.compile(r"^\s*agent\.clear_goals\(\)\s*$"),
            "agent_status": re.compile(r"^\s*agent\.status\(\)\s*$"),
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
                parent.add_child(node)
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

        # Agent control operations
        if match := self.patterns["agent_mode"].match(line):
            mode = match.group(1)
            return SyntaxNode(
                NodeType.AGENT_MODE,
                value={"action": "set_mode", "mode": mode},
                line_number=line_number,
            )

        if match := self.patterns["agent_start"].match(line):
            return SyntaxNode(
                NodeType.AGENT,
                value={"action": "start"},
                line_number=line_number,
            )

        if match := self.patterns["agent_stop"].match(line):
            return SyntaxNode(
                NodeType.AGENT,
                value={"action": "stop"},
                line_number=line_number,
            )

        if match := self.patterns["agent_goal_add"].match(line):
            goal_text = match.group(1)
            priority = match.group(2) or "medium"
            return SyntaxNode(
                NodeType.AGENT_GOAL,
                value={"action": "add", "goal": goal_text, "priority": priority},
                line_number=line_number,
            )

        if match := self.patterns["agent_goals_clear"].match(line):
            return SyntaxNode(
                NodeType.AGENT_GOAL,
                value={"action": "clear"},
                line_number=line_number,
            )

        if match := self.patterns["agent_status"].match(line):
            return SyntaxNode(
                NodeType.AGENT,
                value={"action": "status"},
                line_number=line_number,
            )

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
