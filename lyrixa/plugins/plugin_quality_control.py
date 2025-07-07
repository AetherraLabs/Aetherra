"""
Plugin Quality Control System
============================

Comprehensive quality assurance system for Lyrixa plugins.
Validates plugin structure, performance, security, and compliance.
"""

import ast
import os
import time
from datetime import datetime
from typing import Any, Dict, List


class QualityMetrics:
    """Quality metrics for plugin evaluation."""

    def __init__(self):
        self.score = 0.0
        self.max_score = 100.0
        self.categories = {
            "structure": 0.0,
            "documentation": 0.0,
            "performance": 0.0,
            "security": 0.0,
            "compatibility": 0.0,
            "testing": 0.0,
        }
        self.warnings = []
        self.errors = []
        self.suggestions = []


class PluginQualityControl:
    """Plugin quality control and validation system."""

    def __init__(self):
        self.quality_standards = self._load_quality_standards()
        self.performance_benchmarks = {}
        self.security_checks = []
        self.validation_cache = {}

    def _load_quality_standards(self) -> Dict:
        """Load quality standards configuration."""
        return {
            "min_documentation_score": 70,
            "max_execution_time": 10.0,  # seconds
            "min_code_coverage": 80,
            "required_methods": ["execute", "get_info"],
            "forbidden_imports": ["os.system", "subprocess.call", "eval", "exec"],
            "max_complexity": 10,
            "min_structure_score": 60,
        }

    def validate_plugin(
        self, plugin_path: str, plugin_name: str | None = None
    ) -> QualityMetrics:
        """Comprehensive plugin validation."""
        metrics = QualityMetrics()

        if not plugin_name:
            plugin_name = os.path.basename(plugin_path).replace(".py", "")

        try:
            # Check cache first
            cache_key = f"{plugin_path}_{os.path.getmtime(plugin_path)}"
            if cache_key in self.validation_cache:
                return self.validation_cache[cache_key]

            # Read plugin file
            with open(plugin_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                metrics.errors.append(f"Syntax error: {e}")
                return metrics

            # Run validation checks
            self._validate_structure(tree, content, metrics)
            self._validate_documentation(tree, content, metrics)
            self._validate_security(tree, content, metrics)
            self._validate_compatibility(tree, content, metrics)
            self._validate_performance_potential(tree, content, metrics)

            # Calculate final score
            self._calculate_final_score(metrics)

            # Cache results
            self.validation_cache[cache_key] = metrics

            return metrics

        except Exception as e:
            metrics.errors.append(f"Validation error: {e}")
            return metrics

    def _validate_structure(
        self, tree: ast.Module, content: str, metrics: QualityMetrics
    ):
        """Validate plugin structure and organization."""
        score = 0
        max_score = 25

        # Check for required classes/functions
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [
            node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        ]

        # Plugin class check
        plugin_classes = [cls for cls in classes if "plugin" in cls.name.lower()]
        if plugin_classes:
            score += 5

            # Check for required methods
            for plugin_class in plugin_classes:
                methods = [
                    node.name
                    for node in plugin_class.body
                    if isinstance(node, ast.FunctionDef)
                ]

                if "execute" in methods:
                    score += 5
                else:
                    metrics.warnings.append("Plugin class missing 'execute' method")

                if "get_info" in methods or "__init__" in methods:
                    score += 3

                if "__doc__" in [
                    node.targets[0].id
                    for node in plugin_class.body
                    if isinstance(node, ast.Assign)
                    and isinstance(node.targets[0], ast.Name)
                ]:
                    score += 2
        else:
            # Check for main function
            main_functions = [func for func in functions if func.name == "main"]
            if main_functions:
                score += 3
            else:
                metrics.warnings.append("No plugin class or main function found")

        # Check imports organization
        imports = [
            node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))
        ]
        if imports:
            score += 2

        # Check for module docstring
        if (
            tree.body
            and isinstance(tree.body[0], ast.Expr)
            and isinstance(tree.body[0].value, ast.Constant)
            and isinstance(tree.body[0].value.value, str)
        ):
            score += 3
        else:
            metrics.warnings.append("Missing module docstring")

        # Check code organization
        if len(functions) > 0 or len(classes) > 0:
            score += 2

        # Check for version/metadata
        assigns = [node for node in tree.body if isinstance(node, ast.Assign)]
        metadata_vars = ["__version__", "__author__", "__description__"]
        found_metadata = 0
        for assign in assigns:
            for target in assign.targets:
                if isinstance(target, ast.Name) and target.id in metadata_vars:
                    found_metadata += 1

        if found_metadata >= 2:
            score += 3
        elif found_metadata >= 1:
            score += 1

        # Normalize score
        metrics.categories["structure"] = min(100, (score / max_score) * 100)

    def _validate_documentation(
        self, tree: ast.Module, content: str, metrics: QualityMetrics
    ):
        """Validate plugin documentation quality."""
        score = 0
        max_score = 20

        # Count docstrings
        docstrings = 0

        # Module docstring
        if (
            tree.body
            and isinstance(tree.body[0], ast.Expr)
            and isinstance(tree.body[0].value, ast.Constant)
        ):
            docstring = tree.body[0].value.value
            if isinstance(docstring, str) and len(docstring) > 20:
                score += 5
                docstrings += 1

        # Class and function docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                if (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)
                ):
                    docstrings += 1
                    score += 2

        # Comments count
        lines = content.split("\n")
        comment_lines = [line for line in lines if line.strip().startswith("#")]
        if len(comment_lines) > 3:
            score += 3
        elif len(comment_lines) > 0:
            score += 1

        # Check for examples in docstrings
        if "example" in content.lower() or "usage" in content.lower():
            score += 3

        # Check for parameter documentation
        if "@param" in content or "Args:" in content or "Parameters:" in content:
            score += 2

        # Check for return documentation
        if "@return" in content or "Returns:" in content:
            score += 2

        if docstrings == 0:
            metrics.warnings.append("No docstrings found")
        elif docstrings < 3:
            metrics.suggestions.append("Add more docstrings to improve documentation")

        metrics.categories["documentation"] = min(100, (score / max_score) * 100)

    def _validate_security(
        self, tree: ast.Module, content: str, metrics: QualityMetrics
    ):
        """Validate plugin security practices."""
        score = 100  # Start with perfect score, deduct for issues

        # Check for dangerous imports
        dangerous_imports = [
            "os.system",
            "subprocess.call",
            "eval",
            "exec",
            "__import__",
        ]
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in dangerous_imports:
                        score -= 20
                        metrics.warnings.append(f"Dangerous import found: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module in ["os", "subprocess"]:
                    for alias in node.names:
                        if f"{node.module}.{alias.name}" in dangerous_imports:
                            score -= 20
                            metrics.warnings.append(
                                f"Dangerous import found: {node.module}.{alias.name}"
                            )

        # Check for eval/exec usage
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in ["eval", "exec"]:
                    score -= 30
                    metrics.errors.append(f"Dangerous function call: {node.func.id}")

        # Check for file operations
        file_ops = ["open", "read", "write", "delete"]
        file_usage = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in file_ops:
                    file_usage += 1

        if file_usage > 5:
            score -= 10
            metrics.warnings.append("Extensive file operations detected")

        # Check for network operations
        network_modules = ["urllib", "requests", "socket", "http"]
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module_name = node.module if isinstance(node, ast.ImportFrom) else None
                if module_name in network_modules:
                    metrics.suggestions.append(
                        "Network operations detected - ensure proper error handling"
                    )

        metrics.categories["security"] = max(0, score)

    def _validate_compatibility(
        self, tree: ast.Module, content: str, metrics: QualityMetrics
    ):
        """Validate plugin compatibility and dependencies."""
        score = 0
        max_score = 15

        # Check Python version compatibility
        if 'f"' in content or "f'" in content:
            score += 3  # f-strings indicate Python 3.6+

        # Check for type hints
        has_type_hints = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.returns or any(arg.annotation for arg in node.args.args):
                    has_type_hints = True
                    break

        if has_type_hints:
            score += 4
        else:
            metrics.suggestions.append(
                "Consider adding type hints for better compatibility"
            )

        # Check for exception handling
        try_blocks = [node for node in ast.walk(tree) if isinstance(node, ast.Try)]
        if try_blocks:
            score += 3
        else:
            metrics.warnings.append("No exception handling found")

        # Check for standard library usage
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)

        standard_libs = ["os", "sys", "json", "time", "datetime", "pathlib"]
        std_lib_usage = sum(1 for imp in imports if imp in standard_libs)
        if std_lib_usage > 0:
            score += 2

        # Check for third-party dependencies
        third_party = [
            imp
            for imp in imports
            if imp not in standard_libs and not imp.startswith(".")
        ]
        if len(third_party) > 5:
            metrics.suggestions.append(
                "Many third-party dependencies - consider minimizing"
            )

        metrics.categories["compatibility"] = min(100, (score / max_score) * 100)

    def _validate_performance_potential(
        self, tree: ast.Module, content: str, metrics: QualityMetrics
    ):
        """Validate potential performance characteristics."""
        score = 100  # Start high, deduct for potential issues

        # Check for loops
        loops = [
            node for node in ast.walk(tree) if isinstance(node, (ast.For, ast.While))
        ]
        nested_loops = 0

        for loop in loops:
            for nested in ast.walk(loop):
                if isinstance(nested, (ast.For, ast.While)) and nested != loop:
                    nested_loops += 1

        if nested_loops > 2:
            score -= 15
            metrics.warnings.append(
                "Multiple nested loops detected - may impact performance"
            )

        # Check for recursion
        functions = [
            node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        ]
        for func in functions:
            for node in ast.walk(func):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id == func.name:
                        metrics.suggestions.append(
                            f"Recursive function '{func.name}' - ensure proper termination"
                        )

        # Check for large data structures
        lists_comps = [
            node for node in ast.walk(tree) if isinstance(node, ast.ListComp)
        ]
        if len(lists_comps) > 3:
            metrics.suggestions.append(
                "Multiple list comprehensions - consider generator expressions for large data"
            )

        # Check for sleep/blocking operations
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == "sleep":
                    score -= 10
                    metrics.warnings.append("Blocking sleep operation found")
                elif isinstance(node.func, ast.Name) and node.func.id == "input":
                    score -= 5
                    metrics.warnings.append(
                        "User input operation found - may block execution"
                    )

        metrics.categories["performance"] = max(0, score)

    def _calculate_final_score(self, metrics: QualityMetrics):
        """Calculate final quality score."""
        # Weights for each category
        weights = {
            "structure": 0.25,
            "documentation": 0.15,
            "security": 0.25,
            "compatibility": 0.20,
            "performance": 0.15,
        }

        # Calculate weighted score
        total_score = 0
        for category, score in metrics.categories.items():
            total_score += score * weights.get(category, 0)

        # Apply penalties for errors
        error_penalty = len(metrics.errors) * 10
        warning_penalty = len(metrics.warnings) * 2

        metrics.score = max(0, total_score - error_penalty - warning_penalty)

    def test_plugin_performance(
        self, plugin_instance: Any, test_args: List | None = None
    ) -> Dict:
        """Test plugin performance with benchmarks."""
        if not test_args:
            test_args = []

        results = {
            "execution_time": 0,
            "memory_usage": 0,
            "success": False,
            "error": None,
        }

        try:
            import gc

            import psutil

            # Get initial memory
            process = psutil.Process()
            initial_memory = process.memory_info().rss

            # Force garbage collection
            gc.collect()

            # Time execution
            start_time = time.time()

            if hasattr(plugin_instance, "execute"):
                result = plugin_instance.execute(*test_args)
            elif hasattr(plugin_instance, "main"):
                result = plugin_instance.main(*test_args)
            else:
                raise AttributeError("Plugin has no execute or main method")

            end_time = time.time()

            # Get final memory
            final_memory = process.memory_info().rss

            results.update(
                {
                    "execution_time": end_time - start_time,
                    "memory_usage": final_memory - initial_memory,
                    "success": True,
                    "result": result,
                }
            )

        except ImportError:
            results["error"] = "psutil not available for memory testing"
        except Exception as e:
            results["error"] = str(e)

        return results

    def generate_quality_report(
        self, plugin_path: str, plugin_name: str = None
    ) -> Dict:
        """Generate comprehensive quality report."""
        metrics = self.validate_plugin(plugin_path, plugin_name)

        # Determine quality level
        if metrics.score >= 80:
            quality_level = "Excellent"
        elif metrics.score >= 60:
            quality_level = "Good"
        elif metrics.score >= 40:
            quality_level = "Fair"
        else:
            quality_level = "Poor"

        return {
            "plugin_name": plugin_name
            or os.path.basename(plugin_path).replace(".py", ""),
            "plugin_path": plugin_path,
            "overall_score": metrics.score,
            "quality_level": quality_level,
            "category_scores": metrics.categories,
            "errors": metrics.errors,
            "warnings": metrics.warnings,
            "suggestions": metrics.suggestions,
            "timestamp": datetime.now().isoformat(),
            "standards_met": metrics.score
            >= self.quality_standards["min_structure_score"],
        }

    def get_quality_standards(self) -> Dict:
        """Get current quality standards."""
        return self.quality_standards.copy()

    def update_quality_standards(self, standards: Dict):
        """Update quality standards."""
        self.quality_standards.update(standards)

    def clear_cache(self):
        """Clear validation cache."""
        self.validation_cache.clear()


# Global quality control instance
quality_control = PluginQualityControl()


def validate_plugin(plugin_path: str, plugin_name: str = None) -> QualityMetrics:
    """Convenience function for plugin validation."""
    return quality_control.validate_plugin(plugin_path, plugin_name)


def generate_quality_report(plugin_path: str, plugin_name: str = None) -> Dict:
    """Convenience function for quality report generation."""
    return quality_control.generate_quality_report(plugin_path, plugin_name)
