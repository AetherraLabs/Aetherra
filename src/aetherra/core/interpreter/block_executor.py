# core/block_executor.py
"""
Block execution engine for Aetherra advanced syntax
Handles multi-line blocks, loops, conditionals, and functions
"""

import re
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass

@dataclass
class ExecutionContext:
    """Context for block execution"""
    variables: Dict[str, Any]
    functions: Dict[str, 'AetherraFunction']
    memory_system: Any
    executor_callback: Callable[[str], Any]
    loop_vars: Optional[Dict[str, Any]] = None

@dataclass
class AetherraFunction:
    """Represents a user-defined Aetherra function"""
    name: str
    params: List[str]
    body: List[str]

class BlockExecutor:
    """Executes Aetherra blocks with advanced syntax"""

    def __init__(self, memory_system, functions_system):
        self.memory = memory_system
        self.functions = functions_system
        self.variables = {}
        self.user_functions = {}

    def execute_block(self, lines: List[str], executor_callback: Callable[[str], Any]) -> str:
        """Execute a block of Aetherra lines"""
        context = ExecutionContext(
            variables=self.variables.copy(),
            functions=self.user_functions.copy(),
            memory_system=self.memory,
            executor_callback=executor_callback
        )

        result = []
        i = 0

        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            # Handle multi-line constructs
            if line.startswith('define '):
                i = self._execute_function_definition(lines, i, context, result)
            elif line.startswith('if '):
                i = self._execute_if_block(lines, i, context, result)
            elif line.startswith('for '):
                i = self._execute_for_loop(lines, i, context, result)
            elif line.startswith('while '):
                i = self._execute_while_loop(lines, i, context, result)
            elif line.startswith('simulate '):
                i = self._execute_simulation(lines, i, context, result)
            else:
                # Handle single line commands
                line_result = self._execute_single_line(line, context)
                if line_result:
                    result.append(line_result)
                i += 1

        # Update persistent state
        self.variables.update(context.variables)
        self.user_functions.update(context.functions)

        return '\n'.join(result) if result else "Block executed successfully"

    def _execute_function_definition(self,
        lines: List[str],
        start: int,
        context: ExecutionContext,
        result: List[str]) -> int:
        """Execute function definition block"""
        line = lines[start].strip()
        match = re.match(r'define\s+(\w+)\s*\((.*?)\)', line)
        if not match:
            result.append(f"[Error] Invalid function definition: {line}")
            return start + 1

        func_name = match.group(1)
        params_str = match.group(2).strip()
        params = [p.strip() for p in params_str.split(',') if p.strip()] if params_str else []

        # Find function body
        body = []
        i = start + 1
        while i < len(lines) and lines[i].strip() != 'end':
            body.append(lines[i])
            i += 1

        if i >= len(lines):
            result.append(f"[Error] Function {func_name} missing 'end'")
            return len(lines)

        # Store function
        context.functions[func_name] = AetherraFunction(func_name, params, body)
        result.append(f"[Function] Defined '{func_name}' with parameters: {', '.join(params) if params else 'none'}")

        return i + 1

    def _execute_if_block(self, lines: List[str], start: int, context: ExecutionContext, result: List[str]) -> int:
        """Execute if statement block"""
        line = lines[start].strip()
        condition = line[3:].strip()  # Remove 'if '

        # Parse then/else blocks
        then_block = []
        else_block = []
        current_block = then_block

        i = start + 1
        while i < len(lines):
            line = lines[i].strip()
            if line == 'end':
                break
            elif line == 'else':
                current_block = else_block
            else:
                current_block.append(lines[i])
            i += 1

        if i >= len(lines):
            result.append(f"[Error] If statement missing 'end'")
            return len(lines)

        # Evaluate condition
        condition_result = self._evaluate_condition(condition, context)

        # Execute appropriate block
        if condition_result:
            if then_block:
                block_result = self.execute_block(then_block, context.executor_callback)
                if block_result and block_result != "Block executed successfully":
                    result.append(block_result)
        else:
            if else_block:
                block_result = self.execute_block(else_block, context.executor_callback)
                if block_result and block_result != "Block executed successfully":
                    result.append(block_result)

        return i + 1

    def _execute_for_loop(self, lines: List[str], start: int, context: ExecutionContext, result: List[str]) -> int:
        """Execute for loop block"""
        line = lines[start].strip()
        match = re.match(r'for\s+(\w+)\s+in\s+(.+)', line)
        if not match:
            result.append(f"[Error] Invalid for loop syntax: {line}")
            return start + 1

        var_name = match.group(1)
        iterable_str = match.group(2).strip()

        # Parse loop body
        body = []
        i = start + 1
        while i < len(lines) and lines[i].strip() != 'end':
            body.append(lines[i])
            i += 1

        if i >= len(lines):
            result.append(f"[Error] For loop missing 'end'")
            return len(lines)

        # Expand iterable
        iterable = self._expand_iterable(iterable_str, context)

        # Execute loop
        for item in iterable:
            context.variables[var_name] = item
            block_result = self.execute_block(body, context.executor_callback)
            if block_result and block_result != "Block executed successfully":
                result.append(f"[Loop {var_name}={item}] {block_result}")

        return i + 1

    def _execute_while_loop(self, lines: List[str], start: int, context: ExecutionContext, result: List[str]) -> int:
        """Execute while loop block"""
        line = lines[start].strip()
        condition = line[6:].strip()  # Remove 'while '

        # Parse loop body
        body = []
        i = start + 1
        while i < len(lines) and lines[i].strip() != 'end':
            body.append(lines[i])
            i += 1

        if i >= len(lines):
            result.append(f"[Error] While loop missing 'end'")
            return len(lines)

        # Execute loop with safety limit
        iterations = 0
        max_iterations = 100  # Safety limit

        while self._evaluate_condition(condition, context) and iterations < max_iterations:
            block_result = self.execute_block(body, context.executor_callback)
            if block_result and block_result != "Block executed successfully":
                result.append(f"[While iteration {iterations + 1}] {block_result}")
            iterations += 1

        if iterations >= max_iterations:
            result.append(f"[Warning] While loop stopped after {max_iterations} iterations")

        return i + 1

    def _execute_simulation(self, lines: List[str], start: int, context: ExecutionContext, result: List[str]) -> int:
        """Execute simulation mode"""
        line = lines[start].strip()
        match = re.match(r'simulate\s+(.+)', line)
        if not match:
            result.append(f"[Error] Invalid simulation syntax: {line}")
            return start + 1

        simulation_spec = match.group(1).strip()

        # Parse simulation body
        body = []
        i = start + 1
        while i < len(lines) and lines[i].strip() != 'end':
            body.append(lines[i])
            i += 1

        if i >= len(lines):
            result.append(f"[Error] Simulation missing 'end'")
            return len(lines)

        # Execute simulation
        result.append(f"[Simulation] Starting simulation: {simulation_spec}")
        result.append("[Simulation] This is a dry-run - no actual changes will be made")

        # Create a simulation context (copy of real context)
        sim_context = ExecutionContext(
            variables=context.variables.copy(),
            functions=context.functions.copy(),
            memory_system=context.memory_system,
            executor_callback=lambda cmd: f"[Simulated] {cmd}"  # Simulation wrapper
        )

        block_result = self.execute_block(body, sim_context.executor_callback)
        if block_result and block_result != "Block executed successfully":
            result.append(f"[Simulation Result] {block_result}")

        result.append("[Simulation] Simulation completed")

        return i + 1

    def _execute_single_line(self, line: str, context: ExecutionContext) -> Optional[str]:
        """Execute a single line command"""
        # Variable assignment
        if '=' in line and not line.startswith('remember'):
            parts = line.split('=', 1)
            if len(parts) == 2:
                var_name = parts[0].strip()
                value_expr = parts[1].strip()
                value = self._evaluate_expression(value_expr, context)
                context.variables[var_name] = value
                return f"[Variable] Set {var_name} = {value}"

        # Function call
        if line.startswith('run '):
            return self._execute_function_call(line, context)

        # Regular command - delegate to main executor
        return context.executor_callback(line)

    def _execute_function_call(self, line: str, context: ExecutionContext) -> str:
        """Execute user-defined function call"""
        match = re.match(r'run\s+(\w+)\s*\((.*?)\)', line)
        if not match:
            return f"[Error] Invalid function call syntax: {line}"

        func_name = match.group(1)
        args_str = match.group(2).strip()

        if func_name not in context.functions:
            return f"[Error] Function '{func_name}' not defined"

        func = context.functions[func_name]
        args = [arg.strip().strip('"\'') for arg in args_str.split(',') if arg.strip()] if args_str else []

        if len(args) != len(func.params):
            return f"[Error] Function {func_name} expects {len(func.params)} arguments, got {len(args)}"

        # Create function context
        func_context = ExecutionContext(
            variables=context.variables.copy(),
            functions=context.functions,
            memory_system=context.memory_system,
            executor_callback=context.executor_callback
        )

        # Set parameters
        for param, arg in zip(func.params, args):
            func_context.variables[param] = self._evaluate_expression(arg, context)

        # Execute function body
        result = self.execute_block(func.body, func_context.executor_callback)

        # Update context with function changes (variables only, not functions)
        context.variables.update(func_context.variables)

        return f"[Function] Executed {func_name}({',
            '.join(args)})" + (f"\n{result}" if result != "Block executed successfully" else "")

    def _evaluate_condition(self, condition: str, context: ExecutionContext) -> bool:
        """Evaluate a condition expression"""
        condition = condition.strip()

        # Memory pattern conditions
        if 'memory.pattern' in condition:
            # Handle memory.pattern("pattern") and memory.pattern("pattern", frequency="daily")
            pattern_match = re.search(r'memory\.pattern\(["\'](.*?)["\'](?:,
                \s*frequency=["\'](.*?)["\']\))?\)',
                condition)
            if pattern_match:
                pattern = pattern_match.group(1)
                frequency = pattern_match.group(2) if pattern_match.group(2) else "weekly"
                # Use the pattern method
                try:
                    return context.memory_system.pattern(pattern, frequency)
                except:
                    return False

        # Variable comparisons
        if '==' in condition:
            left, right = condition.split('==', 1)
            left_val = self._evaluate_expression(left.strip(), context)
            right_val = self._evaluate_expression(right.strip(), context)
            return left_val == right_val

        elif '!=' in condition:
            left, right = condition.split('!=', 1)
            left_val = self._evaluate_expression(left.strip(), context)
            right_val = self._evaluate_expression(right.strip(), context)
            return left_val != right_val

        elif '>=' in condition:
            left, right = condition.split('>=', 1)
            left_val = self._evaluate_expression(left.strip(), context)
            right_val = self._evaluate_expression(right.strip(), context)
            try:
                return float(left_val) >= float(right_val)
            except (ValueError, TypeError):
                return False

        elif '<=' in condition:
            left, right = condition.split('<=', 1)
            left_val = self._evaluate_expression(left.strip(), context)
            right_val = self._evaluate_expression(right.strip(), context)
            try:
                return float(left_val) <= float(right_val)
            except (ValueError, TypeError):
                return False

        elif '>' in condition:
            left, right = condition.split('>', 1)
            left_val = self._evaluate_expression(left.strip(), context)
            right_val = self._evaluate_expression(right.strip(), context)
            try:
                return float(left_val) > float(right_val)
            except (ValueError, TypeError):
                return False

        elif '<' in condition:
            left, right = condition.split('<', 1)
            left_val = self._evaluate_expression(left.strip(), context)
            right_val = self._evaluate_expression(right.strip(), context)
            try:
                return float(left_val) < float(right_val)
            except (ValueError, TypeError):
                return False

        # Boolean evaluation
        return bool(self._evaluate_expression(condition, context))

    def _evaluate_expression(self, expr: str, context: ExecutionContext) -> Any:
        """Evaluate an expression"""
        expr = expr.strip().strip('"\'')

        # Check variables
        if expr in context.variables:
            return context.variables[expr]

        # Try numeric conversion
        try:
            if '.' in expr:
                return float(expr)
            else:
                return int(expr)
        except ValueError:
            pass

        # Boolean literals
        if expr.lower() == 'true':
            return True
        elif expr.lower() == 'false':
            return False

        # String literal
        return expr

    def _expand_iterable(self, iterable_str: str, context: ExecutionContext) -> List[Any]:
        """Expand an iterable string into a list"""
        iterable_str = iterable_str.strip()

        # Handle ranges like "1..5"
        if '..' in iterable_str:
            parts = iterable_str.split('..')
            if len(parts) == 2:
                try:
                    start = int(self._evaluate_expression(parts[0], context))
                    end = int(self._evaluate_expression(parts[1], context))
                    return list(range(start, end + 1))
                except (ValueError, TypeError):
                    pass

        # Handle lists like "[1, 2, 3]"
        if iterable_str.startswith('[') and iterable_str.endswith(']'):
            content = iterable_str[1:-1]
            items = [self._evaluate_expression(item.strip(), context) for item in content.split(',') if item.strip()]
            return items

        # Handle variables
        if iterable_str in context.variables:
            value = context.variables[iterable_str]
            if isinstance(value, (list, tuple)):
                return list(value)
            else:
                return [value]

        # Default: treat as single item
        return [self._evaluate_expression(iterable_str, context)]
