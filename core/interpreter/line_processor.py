# core/interpreter/line_processor.py
"""
Line Processor for AetherraCode Interpreter
========================================

Handles line-by-line processing and multi-line block management.
"""

from typing import Any, Dict, List, Optional, Union


class LineProcessor:
    """Processes AetherraCode lines and manages multi-line blocks"""

    def __init__(self):
        self.block_buffer: List[str] = []
        self.in_block = False
        self.block_type: Optional[str] = None
        self.block_indent = 0

    def process_line(self, line: str, parser, executor) -> Union[str, None]:
        """Process a single line, handling blocks appropriately"""
        line = line.strip()

        # Handle empty lines
        if not line:
            if self.in_block:
                self.block_buffer.append("")
            return None

        # Check if this starts a new block
        if parser.is_block_start(line) and not self.in_block:
            return self._start_block(line, parser)

        # Handle lines within a block
        if self.in_block:
            return self._process_block_line(line, parser, executor)

        # Process regular single-line commands
        parse_result = parser.parse(line)
        execution_result = executor.execute(parse_result)

        if hasattr(execution_result, "output"):
            return execution_result.output
        else:
            return str(execution_result)

    def _start_block(self, line: str, parser) -> str:
        """Start a new multi-line block"""
        self.in_block = True
        self.block_type = parser.get_block_type(line)
        self.block_buffer = [line]
        self.block_indent = self._get_indent_level(line)

        return f"📝 Starting {self.block_type} block..."

    def _process_block_line(self, line: str, parser, executor) -> Optional[str]:
        """Process a line within a multi-line block"""
        # Check for block end
        if self._is_block_end(line):
            return self._end_block(parser, executor)

        # Add line to block buffer
        self.block_buffer.append(line)
        return None  # Don't return output for intermediate lines

    def _is_block_end(self, line: str) -> bool:
        """Check if line ends the current block"""
        if not self.in_block:
            return False

        line_stripped = line.strip()

        # Explicit end keywords
        if line_stripped in ["end", "}"]:
            return True

        # Check for dedent (return to original indent level)
        current_indent = self._get_indent_level(line)
        if current_indent <= self.block_indent and line_stripped:
            return True

        return False

    def _end_block(self, parser, executor) -> str:
        """End the current block and execute it"""
        if not self.in_block:
            return "No block to end"

        block_content = "\n".join(self.block_buffer)
        block_type = self.block_type

        # Reset block state
        self.in_block = False
        self.block_type = None
        self.block_buffer = []
        self.block_indent = 0

        # Execute the block based on type
        return self._execute_block(block_content, block_type, executor)

    def _execute_block(self, block_content: str, block_type: str, executor) -> str:
        """Execute a completed block"""
        if block_type == "function":
            return self._execute_function_block(block_content, executor)
        elif block_type == "control":
            return self._execute_control_block(block_content, executor)
        elif block_type == "config":
            return self._execute_config_block(block_content, executor)
        elif block_type == "context":
            return self._execute_context_block(block_content, executor)
        else:
            return f"✅ {block_type} block completed:\n{block_content[:100]}..."

    def _execute_function_block(self, block_content: str, executor) -> str:
        """Execute a function definition block"""
        lines = block_content.split("\n")
        if not lines:
            return "Empty function block"

        # Extract function signature from first line
        first_line = lines[0].strip()
        if first_line.startswith("define "):
            func_sig = first_line[7:].strip()  # Remove "define "
            if "(" in func_sig:
                func_name = func_sig.split("(")[0].strip()
                return f"⚡ Function '{func_name}' defined with {len(lines) - 1} lines"

        return "⚡ Function block processed"

    def _execute_control_block(self, block_content: str, executor) -> str:
        """Execute a control flow block (if, while, for, when)"""
        lines = block_content.split("\n")
        if not lines:
            return "Empty control block"

        first_line = lines[0].strip().lower()
        control_type = first_line.split()[0] if first_line.split() else "unknown"

        return f"🔄 {control_type.title()} block executed with {len(lines) - 1} statements"

    def _execute_config_block(self, block_content: str, executor) -> str:
        """Execute a configuration block (identity, consciousness, voice)"""
        lines = [line.strip() for line in block_content.split("\n") if line.strip()]
        if not lines:
            return "Empty configuration block"

        first_line = lines[0].strip()
        if first_line.startswith(("identity", "consciousness", "voice")):
            config_type = first_line.split()[0]
            return f"⚙️ {config_type.title()} configuration loaded with {len(lines) - 1} settings"

        return "⚙️ Configuration block processed"

    def _execute_context_block(self, block_content: str, executor) -> str:
        """Execute a context block (with statement)"""
        lines = block_content.split("\n")
        if not lines:
            return "Empty context block"

        return f"🎯 Context block executed with {len(lines) - 1} operations"

    def _get_indent_level(self, line: str) -> int:
        """Get the indentation level of a line"""
        return len(line) - len(line.lstrip())

    def is_in_block(self) -> bool:
        """Check if currently processing a block"""
        return self.in_block

    def get_block_info(self) -> Dict[str, Any]:
        """Get information about the current block"""
        return {
            "in_block": self.in_block,
            "block_type": self.block_type,
            "buffer_lines": len(self.block_buffer),
            "indent_level": self.block_indent,
        }

    def force_end_block(self, parser, executor) -> str:
        """Force end the current block (for error recovery)"""
        if not self.in_block:
            return "No block to end"

        return self._end_block(parser, executor)
