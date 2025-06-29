<<<<<<< HEAD
# plugins/math_plugin.py - Mathematical Operations Plugin
from core.plugin_manager import register_plugin
import math
import re

@register_plugin("calculate")
def calculate(expression):
    """Safely evaluate mathematical expressions"""
    try:
        # Remove any potentially dangerous operations
        safe_expression = re.sub(r'[^0-9+\-*/().\s]', '', expression)
        
        # Use eval safely with restricted globals
        result = eval(safe_expression, {"__builtins__": {}}, {})
        return f"Result: {expression} = {result}"
    except Exception as e:
        return f"Error calculating '{expression}': {e}"

@register_plugin("math_func")
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

@register_plugin("statistics")
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
            median = (sorted_nums[n//2 - 1] + sorted_nums[n//2]) / 2
        else:
            median = sorted_nums[n//2]
        
        # Standard deviation
        variance = sum((x - mean) ** 2 for x in nums) / len(nums)
        std_dev = math.sqrt(variance)
        
        return f"Stats for {nums}: Mean={mean:.2f}, Median={median:.2f}, StdDev={std_dev:.2f}"
    except Exception as e:
        return f"Error calculating statistics: {e}"
=======
# plugins/math_plugin.py - Mathematical Operations Plugin
from core.plugin_manager import register_plugin
import math
import re

@register_plugin("calculate")
def calculate(expression):
    """Safely evaluate mathematical expressions"""
    try:
        # Remove any potentially dangerous operations
        safe_expression = re.sub(r'[^0-9+\-*/().\s]', '', expression)
        
        # Use eval safely with restricted globals
        result = eval(safe_expression, {"__builtins__": {}}, {})
        return f"Result: {expression} = {result}"
    except Exception as e:
        return f"Error calculating '{expression}': {e}"

@register_plugin("math_func")
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

@register_plugin("statistics")
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
            median = (sorted_nums[n//2 - 1] + sorted_nums[n//2]) / 2
        else:
            median = sorted_nums[n//2]
        
        # Standard deviation
        variance = sum((x - mean) ** 2 for x in nums) / len(nums)
        std_dev = math.sqrt(variance)
        
        return f"Stats for {nums}: Mean={mean:.2f}, Median={median:.2f}, StdDev={std_dev:.2f}"
    except Exception as e:
        return f"Error calculating statistics: {e}"
>>>>>>> 20a510e90c83aa50461841f557e9447d03056c8d
