# sdk/plugins/example.py
"""
Example NeuroCode Plugin
========================

Demonstrates basic plugin functionality including greetings, calculations,
and proper plugin registration following NeuroCode SDK best practices.
"""

import os
import sys

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

# Import after path setup  # noqa: E402
try:
    from core.plugin_api import register_plugin
except ImportError:
    # Fallback for testing environments
    def register_plugin(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

@register_plugin(
    name="example",
    description="Simple example plugin demonstrating basic functionality",
    capabilities=["greetings", "calculations", "examples"],
    version="1.0.0",
    author="NeuroCode Team",
    category="examples",
    example_usage="plugin: example.hello_world 'NeuroCode'",
    ai_description="Example plugin for demonstrations and testing"
)
def hello_world(args: str = ""):
    """
    A simple example plugin that demonstrates basic functionality.

    Args:
        args: Arguments passed from the plugin call

    Returns:
        str: A greeting message with the provided arguments
    """
    if not args:
        return "Hello from example plugin!"
    return f"Hello from example plugin! Args: {args}"

@register_plugin(
    name="example",
    description="Greet someone by name with a personalized message",
    example_usage="plugin: example.greet 'Alice'",
    ai_description="Generates personalized greetings"
)
def greet(name: str = "World"):
    """
    Greet someone by name.

    Args:
        name: The name to greet (default: "World")

    Returns:
        str: A personalized greeting
    """
    # Input validation
    if not isinstance(name, str):
        return "Error: Name must be a string"

    name = name.strip()
    if not name:
        name = "World"

    return f"Hello, {name}! Welcome to NeuroCode plugins!"

@register_plugin(
    name="example",
    description="Safely evaluate mathematical expressions",
    capabilities=["math", "calculations"],
    example_usage="plugin: example.calculate '2 + 3 * 4'",
    ai_description="Safe mathematical expression evaluator"
)
def calculate(expression: str):
    """
    Safely evaluate a mathematical expression.

    Args:
        expression: A mathematical expression to evaluate

    Returns:
        str: The result of the calculation or an error message
    """
    # Input validation
    if not isinstance(expression, str):
        return "Error: Expression must be a string"

    expression = expression.strip()
    if not expression:
        return "Error: Expression cannot be empty"

    try:
        # Safe evaluation of basic math expressions
        import ast
        import operator

        # Supported operations
        ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
        }

        def eval_expr(node):
            if isinstance(node, ast.Num):  # For older Python versions
                return node.n
            elif isinstance(node, ast.Constant):  # For Python 3.8+
                return node.value
            elif isinstance(node, ast.BinOp):
                return ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
            elif isinstance(node, ast.UnaryOp):
                return ops[type(node.op)](eval_expr(node.operand))
            else:
                raise TypeError(f"Unsupported operation: {type(node)}")

        result = eval_expr(ast.parse(expression, mode='eval').body)
        return f"Result: {result}"

    except ZeroDivisionError:
        return f"Error: Division by zero in '{expression}'"
    except KeyError:
        return f"Error: Unsupported operation in '{expression}'"
    except (SyntaxError, ValueError) as e:
        return f"Error: Invalid expression '{expression}': {str(e)}"
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"

@register_plugin(
    name="example",
    description="Display plugin status and available functions",
    example_usage="plugin: example.status",
    ai_description="Shows plugin health and available commands"
)
def status():
    """
    Show plugin status and available functions.

    Returns:
        str: Plugin status information
    """
    functions = ["hello_world", "greet", "calculate", "status"]
    return f"Example plugin active. Available functions: {', '.join(functions)}"
