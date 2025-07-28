#!/usr/bin/env python3
"""
Enhanced Aetherra Interpreter
============================

Enhanced interpreter for the new .aether language features including:
- if/else control blocks
- for/while loops
- try/catch error handling
- match/switch statements
- wait/delay timing control
- break/continue flow control
- return values from functions
- import/use module system
"""

import time
from typing import Any, Dict

from ..aetherra_grammar import AetherraCodeAST


class ControlFlowException(Exception):
    """Base class for control flow exceptions"""

    pass


class BreakException(ControlFlowException):
    """Exception for break statements"""

    pass


class ContinueException(ControlFlowException):
    """Exception for continue statements"""

    pass


class ReturnException(ControlFlowException):
    """Exception for return statements"""

    def __init__(self, value=None):
        self.value = value
        super().__init__()


class AetherraEnhancedInterpreter:
    """Enhanced interpreter for new .aether language features"""

    def __init__(self, base_interpreter=None):
        self.base_interpreter = base_interpreter
        self.variables = {}
        self.imported_modules = {}
        self.in_loop = False
        self.in_function = False

    def execute(
        self, ast_node: AetherraCodeAST, context: Dict[str, Any] | None = None
    ) -> Any:
        """Execute an AST node with enhanced language features"""
        if context is None:
            context = {}

        self.variables.update(context)

        try:
            return self._execute_node(ast_node)
        except (BreakException, ContinueException, ReturnException) as e:
            # These should be handled by their containing structures
            raise e
        except Exception as e:
            print(f"Execution error: {e}")
            return None

    def _execute_node(self, node: AetherraCodeAST) -> Any:
        """Execute a single AST node"""
        if not isinstance(node, AetherraCodeAST):
            return node

        # Enhanced control flow handlers
        if node.type == "if":
            return self._execute_if(node)
        elif node.type == "for":
            return self._execute_for(node)
        elif node.type == "while":
            return self._execute_while(node)
        elif node.type == "try":
            return self._execute_try(node)
        elif node.type == "match":
            return self._execute_match(node)
        elif node.type == "wait":
            return self._execute_wait(node)
        elif node.type == "break":
            return self._execute_break(node)
        elif node.type == "continue":
            return self._execute_continue(node)
        elif node.type == "return":
            return self._execute_return(node)
        elif node.type == "import" or node.type == "use":
            return self._execute_import(node)
        elif node.type == "function":
            return self._execute_function_definition(node)
        elif node.type == "program":
            return self._execute_program(node)
        elif node.type == "assignment":
            return self._execute_assignment(node)
        else:
            # Delegate to base interpreter for standard .aether features
            if self.base_interpreter:
                return self.base_interpreter.execute_ast_node(node)
            else:
                # Basic fallback execution
                return self._execute_basic(node)

    def _execute_if(self, node: AetherraCodeAST) -> Any:
        """Execute if/else statement"""
        condition = self._evaluate_condition(node.value)

        if condition:
            # Execute if block
            if node.children:
                return self._execute_block(node.children[0])
        else:
            # Look for else clause
            for child in node.children[1:]:
                if child.type == "else":
                    return self._execute_block(child)
        return None

    def _execute_for(self, node: AetherraCodeAST) -> Any:
        """Execute for loop"""
        # Parse for loop: for var in iterable
        if len(node.children) < 3:
            print("Invalid for loop structure")
            return None

        var_name = node.children[0].value
        iterable = self._evaluate_expression(node.children[1])
        loop_body = node.children[2:]

        old_in_loop = self.in_loop
        self.in_loop = True

        try:
            results = []
            for item in iterable:
                # Set loop variable
                old_value = self.variables.get(var_name)
                self.variables[var_name] = item

                try:
                    for statement in loop_body:
                        result = self._execute_node(statement)
                        results.append(result)
                except BreakException:
                    break
                except ContinueException:
                    continue
                finally:
                    # Restore old value
                    if old_value is not None:
                        self.variables[var_name] = old_value
                    elif var_name in self.variables:
                        del self.variables[var_name]

            return results
        finally:
            self.in_loop = old_in_loop

    def _execute_while(self, node: AetherraCodeAST) -> Any:
        """Execute while loop"""
        condition_expr = node.value
        loop_body = node.children

        old_in_loop = self.in_loop
        self.in_loop = True

        try:
            results = []
            while self._evaluate_condition(condition_expr):
                try:
                    for statement in loop_body:
                        result = self._execute_node(statement)
                        results.append(result)
                except BreakException:
                    break
                except ContinueException:
                    continue

            return results
        finally:
            self.in_loop = old_in_loop

    def _execute_try(self, node: AetherraCodeAST) -> Any:
        """Execute try/catch statement"""
        try_block = node.children[0] if node.children else []
        catch_clauses = node.children[1:]

        try:
            return self._execute_block(try_block)
        except Exception as e:
            # Find matching catch clause
            for catch_clause in catch_clauses:
                if catch_clause.type == "catch":
                    # Set exception variable
                    exception_var = catch_clause.value
                    self.variables[exception_var] = e

                    # Execute catch block
                    return self._execute_block(catch_clause.children)

            # No catch clause matched, re-raise
            raise e

    def _execute_match(self, node: AetherraCodeAST) -> Any:
        """Execute match/switch statement"""
        match_value = self._evaluate_expression(node.value)

        for case in node.children:
            if case.type == "case":
                case_value = self._evaluate_expression(case.value)
                if match_value == case_value:
                    return self._execute_block(case.children)
            elif case.type == "default":
                return self._execute_block(case.children)

        return None

    def _execute_wait(self, node: AetherraCodeAST) -> Any:
        """Execute wait/delay statement"""
        duration = node.value

        if isinstance(duration, dict):
            amount = float(duration.get("amount", 0))
            unit = duration.get("unit", "s")

            # Convert to seconds
            if unit in ["s", "sec", "seconds"]:
                seconds = amount
            elif unit in ["m", "min", "minutes"]:
                seconds = amount * 60
            elif unit in ["h", "hours"]:
                seconds = amount * 3600
            else:
                seconds = amount  # Default to seconds

            print(f"Waiting {amount} {unit}...")
            time.sleep(seconds)

        return None

    def _execute_break(self, node: AetherraCodeAST) -> Any:
        """Execute break statement"""
        if not self.in_loop:
            print("Break statement outside of loop")
            return None
        raise BreakException()

    def _execute_continue(self, node: AetherraCodeAST) -> Any:
        """Execute continue statement"""
        if not self.in_loop:
            print("Continue statement outside of loop")
            return None
        raise ContinueException()

    def _execute_return(self, node: AetherraCodeAST) -> Any:
        """Execute return statement"""
        if not self.in_function:
            print("Return statement outside of function")
            return None

        return_value = None
        if node.value is not None:
            return_value = self._evaluate_expression(node.value)

        raise ReturnException(return_value)

    def _execute_import(self, node: AetherraCodeAST) -> Any:
        """Execute import/use statement"""
        if node.type == "import":
            module_path = node.value
            alias = node.metadata.get("alias", module_path)

            # Import module (simplified implementation)
            try:
                # For .aether modules, this would load and parse them
                print(f"Importing {module_path} as {alias}")
                self.imported_modules[alias] = {"path": module_path}
            except Exception as e:
                print(f"Failed to import {module_path}: {e}")

        elif node.type == "use":
            module_name = node.value
            print(f"Using module {module_name}")

        return None

    def _execute_function_definition(self, node: AetherraCodeAST) -> Any:
        """Execute function definition"""
        func_name = node.value or "anonymous"
        parameters = node.metadata.get("parameters", [])
        body = node.children

        def aether_function(*args):
            old_in_function = self.in_function
            self.in_function = True

            # Set up parameter bindings
            old_vars = {}
            for i, param in enumerate(parameters):
                old_vars[param] = self.variables.get(param)
                if i < len(args):
                    self.variables[param] = args[i]

            try:
                result = None
                for statement in body:
                    result = self._execute_node(statement)
                return result
            except ReturnException as e:
                return e.value
            finally:
                # Restore old variable values
                for param in parameters:
                    if old_vars[param] is not None:
                        self.variables[param] = old_vars[param]
                    elif param in self.variables:
                        del self.variables[param]
                self.in_function = old_in_function

        # Store function
        self.variables[func_name] = aether_function
        return aether_function

    def _execute_program(self, node: AetherraCodeAST) -> Any:
        """Execute program (sequence of statements)"""
        results = []
        for statement in node.children:
            if statement:
                result = self._execute_node(statement)
                results.append(result)
        return results

    def _execute_assignment(self, node: AetherraCodeAST) -> Any:
        """Execute variable assignment"""
        var_name = node.value
        if node.children:
            value = self._evaluate_expression(node.children[0])
            self.variables[var_name] = value
            return value
        return None

    def _execute_block(self, statements) -> Any:
        """Execute a block of statements"""
        if not isinstance(statements, list):
            statements = [statements]

        results = []
        for statement in statements:
            if statement:
                result = self._execute_node(statement)
                results.append(result)
        return results

    def _execute_basic(self, node: AetherraCodeAST) -> Any:
        """Basic execution for simple nodes"""
        if node.type == "value":
            return node.value
        elif node.type == "identifier":
            return self.variables.get(node.value, node.value)
        else:
            print(f"Unhandled node type: {node.type}")
            return None

    def _evaluate_condition(self, condition) -> bool:
        """Evaluate a condition to boolean"""
        if isinstance(condition, bool):
            return condition
        elif isinstance(condition, str):
            if condition.lower() in ["true", "yes", "1"]:
                return True
            elif condition.lower() in ["false", "no", "0"]:
                return False
            else:
                # Check if it's a variable
                return bool(self.variables.get(condition, False))
        elif isinstance(condition, (int, float)):
            return condition != 0
        else:
            return bool(condition)

    def _evaluate_expression(self, expr) -> Any:
        """Evaluate an expression"""
        if isinstance(expr, AetherraCodeAST):
            if expr.type == "identifier":
                return self.variables.get(expr.value, expr.value)
            elif expr.type == "value":
                return expr.value
            elif expr.type == "comparison":
                return self._evaluate_comparison(expr)
            else:
                return self._execute_node(expr)
        else:
            return expr

    def _evaluate_comparison(self, node: AetherraCodeAST) -> bool:
        """Evaluate comparison expression"""
        if len(node.children) < 2:
            return False

        left = self._evaluate_expression(node.children[0])
        right = self._evaluate_expression(node.children[1])
        op = node.value

        if op == "==":
            return left == right
        elif op == "!=":
            return left != right
        elif op == ">":
            return left > right
        elif op == "<":
            return left < right
        elif op == ">=":
            return left >= right
        elif op == "<=":
            return left <= right
        else:
            return False
