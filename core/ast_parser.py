# core/ast_parser.py
"""
Abstract Syntax Tree parser for NeuroCode
Advanced syntax support including blocks, loops, conditionals, functions
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Union

@dataclass
class NeuroCommand:
    """Base class for NeuroCode commands"""
    command_type: str
    raw_text: str
    indent_level: int = 0

@dataclass
class RememberCommand(NeuroCommand):
    content: str = ""
    tags: Optional[List[str]] = None
    category: str = "general"
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class RecallCommand(NeuroCommand):
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    limit: Optional[int] = None

@dataclass
class FunctionDefineCommand(NeuroCommand):
    name: str = ""
    params: Optional[List[str]] = None
    body: Optional[List['NeuroCommand']] = None
    
    def __post_init__(self):
        if self.params is None:
            self.params = []
        if self.body is None:
            self.body = []

@dataclass
class FunctionCallCommand(NeuroCommand):
    name: str = ""
    args: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.args is None:
            self.args = []

@dataclass
class ReflectCommand(NeuroCommand):
    tags: Optional[List[str]] = None
    category: Optional[str] = None

@dataclass
class IfCommand(NeuroCommand):
    condition: str = ""
    then_body: Optional[List['NeuroCommand']] = None
    else_body: Optional[List['NeuroCommand']] = None
    
    def __post_init__(self):
        if self.then_body is None:
            self.then_body = []

@dataclass
class ForCommand(NeuroCommand):
    variable: str = ""
    iterable: str = ""
    body: Optional[List['NeuroCommand']] = None
    
    def __post_init__(self):
        if self.body is None:
            self.body = []

@dataclass
class WhileCommand(NeuroCommand):
    condition: str = ""
    body: Optional[List['NeuroCommand']] = None
    
    def __post_init__(self):
        if self.body is None:
            self.body = []

@dataclass
class BlockCommand(NeuroCommand):
    body: Optional[List['NeuroCommand']] = None
    
    def __post_init__(self):
        if self.body is None:
            self.body = []

@dataclass
class VariableAssignment(NeuroCommand):
    name: str = ""
    value: str = ""

@dataclass
class ExpressionCommand(NeuroCommand):
    expression: str = ""

class NeuroBlock:
    """Represents a code block with indentation"""
    def __init__(self, lines: List[str], start_indent: int = 0):
        self.lines = lines
        self.start_indent = start_indent
        self.commands = []
    
    def parse(self) -> List[NeuroCommand]:
        """Parse block into NeuroCommands"""
        commands = []
        i = 0
        while i < len(self.lines):
            line = self.lines[i]
            if not line.strip():
                i += 1
                continue
            
            cmd, next_i = self._parse_line(line, i)
            if cmd:
                commands.append(cmd)
            i = next_i
        
        return commands
    
    def _parse_line(self, line: str, index: int) -> tuple:
        """Parse a single line, handling multi-line constructs"""
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        
        # Function definition
        if stripped.startswith('define '):
            return self._parse_function_def(index)
        
        # Control flow
        if stripped.startswith('if '):
            return self._parse_if_statement(index)
        elif stripped.startswith('for '):
            return self._parse_for_loop(index)
        elif stripped.startswith('while '):
            return self._parse_while_loop(index)
        
        # Variable assignment
        if '=' in stripped and not stripped.startswith('remember'):
            return self._parse_assignment(stripped, indent), index + 1
        
        # Regular command
        return NeuroCommand(
            command_type="expression", 
            raw_text=stripped, 
            indent_level=indent
        ), index + 1
    
    def _parse_function_def(self, start_index: int) -> tuple:
        """Parse function definition block"""
        line = self.lines[start_index].strip()
        match = re.match(r'define\s+(\w+)\s*\((.*?)\)', line)
        if not match:
            return None, start_index + 1
        
        func_name = match.group(1)
        params_str = match.group(2).strip()
        params = [p.strip() for p in params_str.split(',') if p.strip()] if params_str else []
        
        # Parse function body until 'end'
        body_commands = []
        i = start_index + 1
        base_indent = len(self.lines[start_index]) - len(self.lines[start_index].lstrip())
        
        while i < len(self.lines):
            line = self.lines[i]
            if line.strip() == 'end':
                break
            if line.strip():
                cmd, _ = self._parse_line(line, i)
                if cmd:
                    body_commands.append(cmd)
            i += 1
        
        return FunctionDefineCommand(
            command_type="function_def",
            raw_text=self.lines[start_index],
            indent_level=base_indent,
            name=func_name,
            params=params,
            body=body_commands
        ), i + 1
    
    def _parse_if_statement(self, start_index: int) -> tuple:
        """Parse if statement block"""
        line = self.lines[start_index].strip()
        condition = line[3:].strip()  # Remove 'if '
        indent = len(self.lines[start_index]) - len(self.lines[start_index].lstrip())
        
        then_commands = []
        else_commands = []
        i = start_index + 1
        in_else = False
        
        while i < len(self.lines):
            line = self.lines[i]
            if line.strip() == 'end':
                break
            elif line.strip() == 'else':
                in_else = True
                i += 1
                continue
            
            if line.strip():
                cmd, _ = self._parse_line(line, i)
                if cmd:
                    if in_else:
                        else_commands.append(cmd)
                    else:
                        then_commands.append(cmd)
            i += 1
        
        return IfCommand(
            command_type="if",
            raw_text=self.lines[start_index],
            indent_level=indent,
            condition=condition,
            then_body=then_commands,
            else_body=else_commands if else_commands else None
        ), i + 1
    
    def _parse_for_loop(self, start_index: int) -> tuple:
        """Parse for loop block"""
        line = self.lines[start_index].strip()
        match = re.match(r'for\s+(\w+)\s+in\s+(.+)', line)
        if not match:
            return None, start_index + 1
        
        variable = match.group(1)
        iterable = match.group(2).strip()
        indent = len(self.lines[start_index]) - len(self.lines[start_index].lstrip())
        
        body_commands = []
        i = start_index + 1
        
        while i < len(self.lines):
            line = self.lines[i]
            if line.strip() == 'end':
                break
            if line.strip():
                cmd, _ = self._parse_line(line, i)
                if cmd:
                    body_commands.append(cmd)
            i += 1
        
        return ForCommand(
            command_type="for",
            raw_text=self.lines[start_index],
            indent_level=indent,
            variable=variable,
            iterable=iterable,
            body=body_commands
        ), i + 1
    
    def _parse_while_loop(self, start_index: int) -> tuple:
        """Parse while loop block"""
        line = self.lines[start_index].strip()
        condition = line[6:].strip()  # Remove 'while '
        indent = len(self.lines[start_index]) - len(self.lines[start_index].lstrip())
        
        body_commands = []
        i = start_index + 1
        
        while i < len(self.lines):
            line = self.lines[i]
            if line.strip() == 'end':
                break
            if line.strip():
                cmd, _ = self._parse_line(line, i)
                if cmd:
                    body_commands.append(cmd)
            i += 1
        
        return WhileCommand(
            command_type="while",
            raw_text=self.lines[start_index],
            indent_level=indent,
            condition=condition,
            body=body_commands
        ), i + 1
    
    def _parse_assignment(self, line: str, indent: int) -> NeuroCommand:
        """Parse variable assignment"""
        parts = line.split('=', 1)
        if len(parts) == 2:
            var_name = parts[0].strip()
            value = parts[1].strip()
            return VariableAssignment(
                command_type="assignment",
                raw_text=line,
                indent_level=indent,
                name=var_name,
                value=value
            )
        return NeuroCommand(
            command_type="expression", 
            raw_text=line, 
            indent_level=indent
        )

class NeuroASTParser:
    """
    Advanced parser for NeuroCode syntax
    Handles blocks, loops, conditionals, and functions
    """
    
    def __init__(self):
        self.variables = {}  # Store variables during execution
        self.functions = {}  # Store parsed functions
    
    def parse_line(self, line: str) -> Optional[NeuroCommand]:
        """Parse a single line into a NeuroCommand"""
        stripped = line.strip()
        if not stripped:
            return None
        
        indent = len(line) - len(line.lstrip())
        
        # Remember command
        if stripped.startswith('remember'):
            return self._parse_remember(line)
        
        # Recall command
        elif stripped.startswith('recall'):
            return self._parse_recall(line)
        
        # Function definition (single line - for multi-line use parse_block)
        elif stripped.startswith('define'):
            return self._parse_function_define(line)
        
        # Function call
        elif re.match(r'run\s+\w+', stripped):
            return self._parse_function_call(line)
        
        # Variable assignment
        elif '=' in stripped and not stripped.startswith('remember'):
            return self._parse_assignment(stripped, indent)
        
        # Regular expression/command
        return NeuroCommand(
            command_type="expression", 
            raw_text=stripped, 
            indent_level=indent
        )
    
    def parse_block(self, lines: List[str]) -> List[NeuroCommand]:
        """Parse multiple lines as a block"""
        block = NeuroBlock(lines)
        return block.parse()
    
    def _parse_remember(self, line: str) -> Optional[RememberCommand]:
        """Parse remember command with tags"""
        match = re.match(r'remember\s+(.+?)(?:\s+as\s+"([^"]+)")?(?:\s+in\s+(\w+))?', line)
        if match:
            content = match.group(1)
            tags_str = match.group(2)
            category = match.group(3) or "general"
            
            tags = [tag.strip() for tag in tags_str.split(',')] if tags_str else []
            indent = len(line) - len(line.lstrip())
            
            return RememberCommand(
                command_type="remember",
                raw_text=line,
                indent_level=indent,
                content=content,
                tags=tags,
                category=category
            )
        return None
    
    def _parse_recall(self, line: str) -> Optional[RecallCommand]:
        """Parse recall command"""
        match = re.match(r'recall(?:\s+tag:\s*"([^"]+)")?(?:\s+from\s+(\w+))?(?:\s+limit\s+(\d+))?', line)
        if match:
            tags_str = match.group(1)
            category = match.group(2)
            limit = int(match.group(3)) if match.group(3) else None
            
            tags = [tag.strip() for tag in tags_str.split(',')] if tags_str else None
            indent = len(line) - len(line.lstrip())
            
            return RecallCommand(
                command_type="recall",
                raw_text=line,
                indent_level=indent,
                tags=tags,
                category=category,
                limit=limit
            )
        return None
    
    def _parse_function_define(self, line: str) -> Optional[FunctionDefineCommand]:
        """Parse single-line function definition"""
        match = re.match(r'define\s+(\w+)\s*\((.*?)\)\s*:\s*(.+)', line)
        if match:
            func_name = match.group(1)
            params_str = match.group(2).strip()
            body_str = match.group(3).strip()
            
            params = [p.strip() for p in params_str.split(',') if p.strip()] if params_str else []
            # For single line, create a simple expression command as body
            body_commands = [NeuroCommand(
                command_type="expression", 
                raw_text=body_str,
                indent_level=0
            )]
            indent = len(line) - len(line.lstrip())
            
            return FunctionDefineCommand(
                command_type="function_def",
                raw_text=line,
                indent_level=indent,
                name=func_name,
                params=params,
                body=body_commands
            )
        return None
    
    def _parse_function_call(self, line: str) -> Optional[FunctionCallCommand]:
        """Parse function call"""
        match = re.match(r'run\s+(\w+)\s*\((.*?)\)', line)
        if match:
            func_name = match.group(1)
            args_str = match.group(2).strip()
            
            args = [arg.strip().strip('"\'') for arg in args_str.split(',') if arg.strip()] if args_str else []
            indent = len(line) - len(line.lstrip())
            
            return FunctionCallCommand(
                command_type="function_call",
                raw_text=line,
                indent_level=indent,
                name=func_name,
                args=args
            )
        return None
    
    def _parse_assignment(self, line: str, indent: int) -> NeuroCommand:
        """Parse variable assignment"""
        parts = line.split('=', 1)
        if len(parts) == 2:
            var_name = parts[0].strip()
            value = parts[1].strip()
            return VariableAssignment(
                command_type="assignment",
                raw_text=line,
                indent_level=indent,
                name=var_name,
                value=value
            )
        return NeuroCommand(
            command_type="expression", 
            raw_text=line, 
            indent_level=indent
        )
    
    def evaluate_condition(self, condition: str) -> bool:
        """Evaluate a condition string (basic implementation)"""
        # Basic condition evaluation - can be extended
        condition = condition.strip()
        
        # Handle memory.pattern conditions
        if 'memory.pattern' in condition:
            # Extract pattern from condition
            match = re.search(r'memory\.pattern\("([^"]+)"\)', condition)
            if match:
                pattern = match.group(1)
                # This would need to be connected to actual memory system
                return True  # Placeholder
        
        # Handle variable comparisons
        if '==' in condition:
            left, right = condition.split('==', 1)
            left_val = self._evaluate_expression(left.strip())
            right_val = self._evaluate_expression(right.strip())
            return left_val == right_val
        
        elif '!=' in condition:
            left, right = condition.split('!=', 1)
            left_val = self._evaluate_expression(left.strip())
            right_val = self._evaluate_expression(right.strip())
            return left_val != right_val
        
        elif '>' in condition:
            left, right = condition.split('>', 1)
            left_val = self._evaluate_expression(left.strip())
            right_val = self._evaluate_expression(right.strip())
            try:
                return float(left_val) > float(right_val)
            except (ValueError, TypeError):
                return False
        
        # Default: treat as boolean
        return bool(self._evaluate_expression(condition))
    
    def _evaluate_expression(self, expr: str):
        """Evaluate a simple expression"""
        expr = expr.strip().strip('"\'')
        
        # Check if it's a variable
        if expr in self.variables:
            return self.variables[expr]
        
        # Try to parse as number
        try:
            if '.' in expr:
                return float(expr)
            else:
                return int(expr)
        except ValueError:
            pass
        
        # Return as string
        return expr
    
    def set_variable(self, name: str, value: Any):
        """Set a variable value"""
        self.variables[name] = value
    
    def get_variable(self, name: str) -> Any:
        """Get a variable value"""
        return self.variables.get(name)
    
    def expand_iterable(self, iterable_str: str) -> List[Any]:
        """Expand an iterable string into a list"""
        iterable_str = iterable_str.strip()
        
        # Handle ranges like "1..5"
        if '..' in iterable_str:
            parts = iterable_str.split('..')
            if len(parts) == 2:
                try:
                    start = int(parts[0])
                    end = int(parts[1])
                    return list(range(start, end + 1))
                except ValueError:
                    pass
        
        # Handle lists like "[1, 2, 3]"
        if iterable_str.startswith('[') and iterable_str.endswith(']'):
            content = iterable_str[1:-1]
            items = [item.strip().strip('"\'') for item in content.split(',') if item.strip()]
            return items
        
        # Handle variables
        if iterable_str in self.variables:
            value = self.variables[iterable_str]
            if isinstance(value, (list, tuple)):
                return list(value)
            else:
                return [value]
        
        # Default: treat as single item
        return [iterable_str]
    
    def validate_syntax(self, line: str) -> tuple[bool, str]:
        """
        Validate NeuroCode syntax
        Returns (is_valid, error_message)
        """
        try:
            cmd = self.parse_line(line)
            if cmd is None:
                return False, "Invalid syntax or unsupported command"
            return True, ""
        except Exception as e:
            return False, str(e)
