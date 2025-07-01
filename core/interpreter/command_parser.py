# core/interpreter/command_parser.py
"""
Command Parser for NeuroCode Interpreter
========================================

Handles parsing and routing of NeuroCode commands.
"""

import re
from typing import Optional

from .base import ParseResult


class CommandParser:
    """Parses NeuroCode commands into structured components"""

    def __init__(self):
        self.command_patterns = {
            "remember": r"remember\s*\(\s*[\"']([^\"']*)[\"']\s*\)",
            "recall": r"recall\s*[\"']([^\"']*)[\"']",
            "goal": r"goal:\s*[\"']([^\"']*)[\"']",
            "agent": r"agent:\s*(\w+)",
            "plugin": r"plugin:\s*(\w+)",
            "function": r"define\s+(\w+)\s*\(",
            "think": r"think\s+about\s+[\"']([^\"']*)[\"']",
            "analyze": r"analyze\s+(\w+)",
            "assistant": r"assistant:\s*(.*)",
            "debug": r"debug:\s*(.*)",
            "meta": r"meta:\s*(\w+)",
        }

        self.enhanced_patterns = {
            "enhanced_remember": r'remember\s*\(\s*["\']([^"\']*)["\'\s*\)\s+as\s+["\']([^"\']*)["\']',
            "enhanced_goal": r'goal:\s*["\']([^"\']*)["\'].*?priority:\s*(\w+)',
            "enhanced_agent": r'agent:\s*(\w+).*?specialization:\s*["\']([^"\']*)["\']',
            "enhanced_plugin": r"plugin:\s*(\w+)\s*\(([^)]*)\)",
        }

    def parse(self, line: str) -> ParseResult:
        """Parse a command line into components"""
        line = line.strip()

        # Try enhanced patterns first
        enhanced_result = self._try_enhanced_parsing(line)
        if enhanced_result:
            return enhanced_result

        # Try basic patterns
        basic_result = self._try_basic_parsing(line)
        if basic_result:
            return basic_result

        # Default to unknown command
        return ParseResult(
            command_type="unknown",
            command_name="unknown",
            parameters={"raw": line},
            raw_line=line,
            enhanced=False,
        )

    def _try_enhanced_parsing(self, line: str) -> Optional[ParseResult]:
        """Try enhanced parsing patterns"""

        # Enhanced remember with tags and metadata
        if "remember(" in line and " as " in line:
            return self._parse_enhanced_remember(line)

        # Enhanced goal with priority and metadata
        if line.startswith("goal:") and ("priority:" in line or "deadline:" in line):
            return self._parse_enhanced_goal(line)

        # Enhanced agent with specialization
        if line.startswith("agent:") and "specialization:" in line:
            return self._parse_enhanced_agent(line)

        # Enhanced plugin with parameters
        if line.startswith("plugin:") and "(" in line:
            return self._parse_enhanced_plugin(line)

        return None

    def _try_basic_parsing(self, line: str) -> Optional[ParseResult]:
        """Try basic command patterns"""

        for command_type, pattern in self.command_patterns.items():
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return ParseResult(
                    command_type=command_type,
                    command_name=command_type,
                    parameters={"content": match.group(1) if match.groups() else line},
                    raw_line=line,
                    enhanced=False,
                )

        return None

    def _parse_enhanced_remember(self, line: str) -> ParseResult:
        """Parse enhanced remember commands"""
        pattern = r'remember\s*\(\s*["\']([^"\']*)["\'\s*\)\s+as\s+["\']([^"\']*)["\']'
        match = re.search(pattern, line)

        if match:
            content = match.group(1)
            tags = [tag.strip() for tag in match.group(2).split(",")]

            # Look for additional parameters
            category = None
            confidence = None

            category_match = re.search(r'category:\s*["\']([^"\']*)["\']', line)
            if category_match:
                category = category_match.group(1)

            confidence_match = re.search(r"confidence:\s*([0-9.]+)", line)
            if confidence_match:
                confidence = float(confidence_match.group(1))

            return ParseResult(
                command_type="enhanced_remember",
                command_name="remember",
                parameters={
                    "content": content,
                    "tags": tags,
                    "category": category,
                    "confidence": confidence,
                },
                raw_line=line,
                enhanced=True,
            )

        return None

    def _parse_enhanced_goal(self, line: str) -> ParseResult:
        """Parse enhanced goal commands"""
        # Extract goal text
        goal_match = re.search(r'goal:\s*["\']([^"\']*)["\']', line)
        if not goal_match:
            return None

        goal_text = goal_match.group(1)

        # Extract priority
        priority = "medium"  # default
        priority_match = re.search(r"priority:\s*(\w+)", line)
        if priority_match:
            priority = priority_match.group(1)

        # Extract deadline
        deadline = None
        deadline_match = re.search(r'deadline:\s*["\']([^"\']*)["\']', line)
        if deadline_match:
            deadline = deadline_match.group(1)

        # Extract assigned agent
        agent = None
        agent_match = re.search(r'agent:\s*["\']([^"\']*)["\']', line)
        if agent_match:
            agent = agent_match.group(1)

        return ParseResult(
            command_type="enhanced_goal",
            command_name="goal",
            parameters={
                "goal": goal_text,
                "priority": priority,
                "deadline": deadline,
                "agent": agent,
            },
            raw_line=line,
            enhanced=True,
        )

    def _parse_enhanced_agent(self, line: str) -> ParseResult:
        """Parse enhanced agent commands"""
        # Extract specialization
        spec_match = re.search(r'specialization:\s*["\']([^"\']*)["\']', line)
        if not spec_match:
            return None

        specialization = spec_match.group(1)

        return ParseResult(
            command_type="enhanced_agent",
            command_name="agent",
            parameters={"action": "activate", "specialization": specialization},
            raw_line=line,
            enhanced=True,
        )

    def _parse_enhanced_plugin(self, line: str) -> ParseResult:
        """Parse enhanced plugin commands with parameters"""
        plugin_match = re.search(r"plugin:\s*(\w+)\s*\(([^)]*)\)", line)
        if not plugin_match:
            return None

        plugin_name = plugin_match.group(1)
        params_str = plugin_match.group(2)

        # Parse parameters
        params = {}
        if params_str.strip():
            for param in params_str.split(","):
                if "=" in param:
                    key, value = param.split("=", 1)
                    params[key.strip()] = value.strip().strip("\"'")

        return ParseResult(
            command_type="enhanced_plugin",
            command_name="plugin",
            parameters={"plugin_name": plugin_name, "params": params},
            raw_line=line,
            enhanced=True,
        )

    def is_block_start(self, line: str) -> bool:
        """Check if line starts a multi-line block"""
        block_starts = [
            "define ",
            "if ",
            "while ",
            "for ",
            "when ",
            "with ",
            "identity {",
            "consciousness {",
            "voice {",
        ]

        line_lower = line.lower().strip()
        return any(line_lower.startswith(start) for start in block_starts)

    def get_block_type(self, line: str) -> str:
        """Determine the type of block being started"""
        line_lower = line.lower().strip()

        if line_lower.startswith("define "):
            return "function"
        elif line_lower.startswith(("if ", "while ", "for ", "when ")):
            return "control"
        elif line_lower.startswith("with "):
            return "context"
        elif any(
            line_lower.startswith(config) for config in ["identity {", "consciousness {", "voice {"]
        ):
            return "config"
        else:
            return "unknown"
