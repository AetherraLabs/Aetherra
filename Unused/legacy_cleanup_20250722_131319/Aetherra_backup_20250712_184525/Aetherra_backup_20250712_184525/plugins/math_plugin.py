# plugins/math_plugin.py - Mathematical Operations Plugin
import math
import re

from core.plugin_manager import register_plugin


@register_plugin(
    name="calculate",
    description="Safely evaluate mathematical expressions with basic operations",
    capabilities=["arithmetic", "expression_evaluation", "safe_math"],
    version="1.1.0",
    author="AetherraCode Team",
    category="mathematics",
    dependencies=["math", "re"],
    # Enhanced intent-based discovery
    intent_purpose="mathematical calculation and expression evaluation",
    intent_triggers=["calculate", "math", "compute", "evaluate", "solve", "arithmetic"],
    intent_scenarios=[
        "evaluating mathematical expressions",
        "performing basic arithmetic operations",
        "calculating formulas and equations",
        "solving numerical problems",
    ],
    ai_description="Safely evaluates mathematical expressions using standard arithmetic operations (+, -, *, /, parentheses). Provides secure calculation without executing dangerous code.",
    example_usage="plugin: calculate '2 + 3 * 4 - (5 / 2)'",
    confidence_boost=1.3,
)
def calculate(expression):
    """Safely evaluate mathematical expressions"""
    try:
        # Remove any potentially dangerous operations
        safe_expression = re.sub(r"[^0-9+\-*/().\s]", "", expression)

        # Use eval safely with restricted globals
        result = eval(safe_expression, {"__builtins__": {}}, {})
        return f"Result: {expression} = {result}"
    except Exception as e:
        return f"Error calculating '{expression}': {e}"


@register_plugin(
    name="math_func",
    description="Apply mathematical functions like sqrt, sin, cos, etc.",
    capabilities=["trigonometry", "square_root", "mathematical_functions"],
    version="1.1.0",
    author="AetherraCode Team",
    category="mathematics",
    dependencies=["math"],
    # Enhanced intent-based discovery
    intent_purpose="advanced mathematical functions and trigonometry",
    intent_triggers=[
        "sqrt",
        "sin",
        "cos",
        "tan",
        "log",
        "exp",
        "trigonometry",
        "function",
    ],
    intent_scenarios=[
        "calculating square roots and powers",
        "trigonometric calculations (sin, cos, tan)",
        "logarithmic and exponential operations",
        "scientific and engineering computations",
    ],
    ai_description="Provides advanced mathematical functions including trigonometry (sin, cos, tan), square root, logarithms, and exponentials. Essential for scientific calculations and engineering tasks.",
    example_usage="plugin: math_func 'sqrt' 25",
    confidence_boost=1.2,
)
def math_function(func_name, value):
    """Apply mathematical functions"""
    try:
        value = float(value)

        if func_name == "sqrt":
            result = math.sqrt(value)
        elif func_name == "sin":
            result = math.sin(value)
        elif func_name == "cos":
            result = math.cos(value)
        elif func_name == "tan":
            result = math.tan(value)
        elif func_name == "log":
            result = math.log(value)
        elif func_name == "exp":
            result = math.exp(value)
        else:
            return f"Unknown function: {func_name}"

        return f"{func_name}({value}) = {result}"
    except Exception as e:
        return f"Error in {func_name}({value}): {e}"


@register_plugin(
    name="statistics",
    description="Calculate basic statistics for a list of numbers",
    capabilities=[
        "statistics",
        "mean",
        "median",
        "standard_deviation",
        "data_analysis",
    ],
    version="1.0.0",
    author="AetherraCode Team",
    category="mathematics",
    dependencies=["math"],
    # Enhanced intent-based discovery
    intent_purpose="statistical analysis and data summarization",
    intent_triggers=[
        "statistics",
        "stats",
        "mean",
        "median",
        "average",
        "standard deviation",
        "analyze data",
    ],
    intent_scenarios=[
        "analyzing numerical datasets",
        "calculating descriptive statistics",
        "summarizing data distributions",
        "getting statistical insights from numbers",
    ],
    ai_description="Computes essential statistical measures including mean, median, and standard deviation for numerical data. Perfect for quick data analysis and understanding data distributions.",
    example_usage="plugin: statistics 1 2 3 4 5 6 7 8 9 10",
    confidence_boost=1.1,
)
def calculate_stats(*numbers):
    """Calculate basic statistics for a list of numbers"""
    try:
        nums = [float(n) for n in numbers]
        if not nums:
            return "No numbers provided"

        mean = sum(nums) / len(nums)
        sorted_nums = sorted(nums)
        n = len(sorted_nums)

        # Median
        if n % 2 == 0:
            median = (sorted_nums[n // 2 - 1] + sorted_nums[n // 2]) / 2
        else:
            median = sorted_nums[n // 2]

        # Standard deviation
        variance = sum((x - mean) ** 2 for x in nums) / len(nums)
        std_dev = math.sqrt(variance)

        return f"Stats for {nums}: Mean={mean:.2f}, Median={median:.2f}, StdDev={std_dev:.2f}"
    except Exception as e:
        return f"Error calculating statistics: {e}"
