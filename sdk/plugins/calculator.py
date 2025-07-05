"""
Simple Calculator Plugin
======================

A basic calculator plugin demonstrating mathematical operations.
"""

import os
import sys

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

import ast
import math
import operator
from typing import Any, Dict

from core.plugin_api import register_plugin


@register_plugin(
    name="calculator",
    description="Perform mathematical calculations and operations",
    capabilities=["arithmetic", "trigonometry", "algebra"],
    version="1.0.0",
    author="AetherraCode Team",
    category="utilities",
    intent_purpose="mathematical calculations and problem solving",
    intent_triggers=["calculate", "math", "compute", "solve"],
    intent_scenarios=["basic arithmetic", "scientific calculations", "math homework"],
    ai_description="A calculator plugin for performing various mathematical operations",
    example_usage="plugin: calculator.evaluate '2 + 2 * 3'",
    confidence_boost=1.2
)
def evaluate(expression: str) -> Dict[str, Any]:
    """
    Evaluate a mathematical expression safely.

    Args:
        expression: Mathematical expression to evaluate

    Returns:
        Dict containing the calculation result
    """
    try:
        # Safe mathematical operations
        safe_ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }

        # Safe functions
        safe_funcs = {
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'sqrt': math.sqrt,
            'log': math.log,
            'exp': math.exp,
            'abs': abs,
            'pi': math.pi,
            'e': math.e
        }

        def eval_node(node):
            if isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.Name):
                if node.id in safe_funcs:
                    return safe_funcs[node.id]
                else:
                    raise ValueError(f"Unknown variable: {node.id}")
            elif isinstance(node, ast.BinOp):
                left = eval_node(node.left)
                right = eval_node(node.right)
                return safe_ops[type(node.op)](left, right)
            elif isinstance(node, ast.UnaryOp):
                operand = eval_node(node.operand)
                return safe_ops[type(node.op)](operand)
            elif isinstance(node, ast.Call):
                func = eval_node(node.func)
                args = [eval_node(arg) for arg in node.args]
                return func(*args)
            else:
                raise TypeError(f"Unsupported node type: {type(node)}")

        # Parse and evaluate
        tree = ast.parse(expression, mode='eval')
        result = eval_node(tree.body)

        return {
            "expression": expression,
            "result": result,
            "type": type(result).__name__
        }

    except Exception as e:
        return {
            "expression": expression,
            "error": str(e),
            "result": None
        }

@register_plugin("calculator")
def convert_units(value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
    """
    Convert between different units.

    Args:
        value: Value to convert
        from_unit: Source unit
        to_unit: Target unit

    Returns:
        Dict containing conversion result
    """
    # Length conversions (to meters)
    length_units = {
        'mm': 0.001,
        'cm': 0.01,
        'm': 1.0,
        'km': 1000.0,
        'in': 0.0254,
        'ft': 0.3048,
        'yd': 0.9144,
        'mi': 1609.34
    }

    # Weight conversions (to grams)
    weight_units = {
        'mg': 0.001,
        'g': 1.0,
        'kg': 1000.0,
        'oz': 28.3495,
        'lb': 453.592
    }

    # Temperature conversions
    def convert_temp(value, from_unit, to_unit):
        # Convert to Celsius first
        if from_unit == 'F':
            celsius = (value - 32) * 5/9
        elif from_unit == 'K':
            celsius = value - 273.15
        else:  # Celsius
            celsius = value

        # Convert from Celsius to target
        if to_unit == 'F':
            return celsius * 9/5 + 32
        elif to_unit == 'K':
            return celsius + 273.15
        else:  # Celsius
            return celsius

    try:
        if from_unit in length_units and to_unit in length_units:
            meters = value * length_units[from_unit]
            result = meters / length_units[to_unit]
        elif from_unit in weight_units and to_unit in weight_units:
            grams = value * weight_units[from_unit]
            result = grams / weight_units[to_unit]
        elif from_unit in ['C', 'F', 'K'] and to_unit in ['C', 'F', 'K']:
            result = convert_temp(value, from_unit, to_unit)
        else:
            return {
                "error": f"Cannot convert from {from_unit} to {to_unit}",
                "supported_units": {
                    "length": list(length_units.keys()),
                    "weight": list(weight_units.keys()),
                    "temperature": ['C', 'F', 'K']
                }
            }

        return {
            "original_value": value,
            "from_unit": from_unit,
            "converted_value": result,
            "to_unit": to_unit
        }

    except Exception as e:
        return {
            "error": str(e),
            "original_value": value,
            "from_unit": from_unit,
            "to_unit": to_unit
        }
