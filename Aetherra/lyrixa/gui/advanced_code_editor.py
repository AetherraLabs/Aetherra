# advanced_code_editor.py
# 🧠 Enhanced AST-aware Code Editor for Lyrixa
# Implements context-aware parsing, self-verification, and intelligent editing

import ast
import re
import json
import hashlib
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class EditHistory:
    """Track code editing history for learning"""
    timestamp: float
    operation: str
    before_hash: str
    after_hash: str
    reasoning: str
    success: bool
    syntax_valid: bool
    test_passed: bool = False

@dataclass
class PluginMetadata:
    """Structured plugin metadata"""
    name: str
    functions: List[str]
    classes: List[str]
    version: str
    description: str
    dependencies: List[str]

class ASTAwareCodeEditor:
    """
    🧠 Advanced code editor with AST parsing, self-verification, and learning capabilities
    """

    def __init__(self):
        self.edit_history: List[EditHistory] = []
        self.metadata_cache: Dict[str, PluginMetadata] = {}

    def parse_plugin_metadata(self, code: str) -> Optional[PluginMetadata]:
        """
        🔍 Extract structured metadata from plugin code
        """
        try:
            metadata = {
                'name': '',
                'functions': [],
                'classes': [],
                'version': '1.0',
                'description': '',
                'dependencies': []
            }

            # Parse metadata comments at the top
            lines = code.split('\n')
            for line in lines[:20]:  # Check first 20 lines
                line = line.strip()
                if line.startswith('# @plugin:'):
                    metadata['name'] = line.split(':', 1)[1].strip()
                elif line.startswith('# @functions:'):
                    metadata['functions'] = [f.strip() for f in line.split(':', 1)[1].split(',')]
                elif line.startswith('# @classes:'):
                    metadata['classes'] = [c.strip() for c in line.split(':', 1)[1].split(',')]
                elif line.startswith('# @version:'):
                    metadata['version'] = line.split(':', 1)[1].strip()
                elif line.startswith('# @description:'):
                    metadata['description'] = line.split(':', 1)[1].strip()
                elif line.startswith('# @dependencies:'):
                    metadata['dependencies'] = [d.strip() for d in line.split(':', 1)[1].split(',')]

            # Parse AST to find actual functions and classes
            tree = ast.parse(code)
            ast_functions = []
            ast_classes = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    ast_functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    ast_classes.append(node.name)

            # Merge with detected functions/classes
            if not metadata['functions']:
                metadata['functions'] = ast_functions
            if not metadata['classes']:
                metadata['classes'] = ast_classes

            return PluginMetadata(**metadata)

        except Exception as e:
            print(f"⚠️ Failed to parse plugin metadata: {e}")
            return None

    def analyze_code_structure(self, code: str) -> Dict[str, Any]:
        """
        🧠 Parse code into AST and analyze structure
        """
        try:
            tree = ast.parse(code)
            analysis = {
                'valid_syntax': True,
                'functions': [],
                'classes': [],
                'imports': [],
                'globals': [],
                'complexity_score': 0
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis['functions'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'docstring': ast.get_docstring(node),
                        'decorators': [ast.unparse(d) for d in node.decorator_list] if hasattr(ast, 'unparse') else []
                    })
                    analysis['complexity_score'] += 1

                elif isinstance(node, ast.ClassDef):
                    analysis['classes'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        'docstring': ast.get_docstring(node),
                        'bases': [ast.unparse(base) for base in node.bases] if hasattr(ast, 'unparse') else []
                    })
                    analysis['complexity_score'] += 2

                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis['imports'].append(alias.name)

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        analysis['imports'].append(f"{module}.{alias.name}")

                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            analysis['globals'].append(target.id)

            return analysis

        except SyntaxError as e:
            return {
                'valid_syntax': False,
                'error': str(e),
                'line': e.lineno,
                'offset': e.offset
            }

    def intelligent_code_merge(self, existing_code: str, new_code: str, reasoning: str = "") -> Tuple[str, bool, str]:
        """
        🤖 AST-aware intelligent code merging with self-verification
        """
        start_time = time.time()

        # Analyze existing code structure
        existing_analysis = self.analyze_code_structure(existing_code)
        if not existing_analysis.get('valid_syntax', False):
            return existing_code, False, f"Invalid existing code syntax: {existing_analysis.get('error', 'Unknown error')}"

        # Analyze new code structure
        new_analysis = self.analyze_code_structure(new_code)
        if not new_analysis.get('valid_syntax', False):
            return existing_code, False, f"Invalid new code syntax: {new_analysis.get('error', 'Unknown error')}"

        # Determine merge strategy based on AST analysis
        strategy = self._determine_merge_strategy(existing_analysis, new_analysis)

        # Perform the merge
        try:
            if strategy == "function_replace":
                merged_code = self._replace_functions(existing_code, new_code, existing_analysis, new_analysis)
            elif strategy == "class_replace":
                merged_code = self._replace_classes(existing_code, new_code, existing_analysis, new_analysis)
            elif strategy == "intelligent_append":
                merged_code = self._intelligent_append(existing_code, new_code)
            elif strategy == "full_replace":
                merged_code = new_code
            else:
                merged_code = existing_code + "\n\n# Added functionality:\n" + new_code

            # Self-verification
            verification_result = self._verify_merged_code(merged_code)

            # Record edit history
            self._record_edit_history(
                operation=strategy,
                before_code=existing_code,
                after_code=merged_code,
                reasoning=reasoning,
                success=verification_result['syntax_valid'],
                syntax_valid=verification_result['syntax_valid']
            )

            return merged_code, verification_result['syntax_valid'], verification_result.get('message', 'Success')

        except Exception as e:
            error_msg = f"Merge failed: {str(e)}"
            self._record_edit_history(
                operation="failed_merge",
                before_code=existing_code,
                after_code=existing_code,
                reasoning=reasoning,
                success=False,
                syntax_valid=False
            )
            return existing_code, False, error_msg

    def _determine_merge_strategy(self, existing_analysis: Dict, new_analysis: Dict) -> str:
        """Determine the best merge strategy based on AST analysis"""
        existing_functions = {f['name'] for f in existing_analysis.get('functions', [])}
        new_functions = {f['name'] for f in new_analysis.get('functions', [])}

        existing_classes = {c['name'] for c in existing_analysis.get('classes', [])}
        new_classes = {c['name'] for c in new_analysis.get('classes', [])}

        # Check for function overlaps
        function_overlap = existing_functions.intersection(new_functions)
        class_overlap = existing_classes.intersection(new_classes)

        if function_overlap and not class_overlap:
            return "function_replace"
        elif class_overlap and not function_overlap:
            return "class_replace"
        elif function_overlap and class_overlap:
            return "full_replace"
        else:
            return "intelligent_append"

    def _replace_functions(self, existing_code: str, new_code: str, existing_analysis: Dict, new_analysis: Dict) -> str:
        """Replace specific functions using AST-guided replacement"""
        lines = existing_code.split('\n')
        new_functions = {f['name']: f for f in new_analysis.get('functions', [])}

        for func_info in existing_analysis.get('functions', []):
            func_name = func_info['name']
            if func_name in new_functions:
                # Find function in new code and extract it
                new_func_code = self._extract_function_from_code(new_code, func_name)
                if new_func_code:
                    # Replace in existing code
                    existing_code = self._replace_function_in_code(existing_code, func_name, new_func_code)

        return existing_code

    def _replace_classes(self, existing_code: str, new_code: str, existing_analysis: Dict, new_analysis: Dict) -> str:
        """Replace specific classes using AST-guided replacement"""
        new_classes = {c['name']: c for c in new_analysis.get('classes', [])}

        for class_info in existing_analysis.get('classes', []):
            class_name = class_info['name']
            if class_name in new_classes:
                # Find class in new code and extract it
                new_class_code = self._extract_class_from_code(new_code, class_name)
                if new_class_code:
                    # Replace in existing code
                    existing_code = self._replace_class_in_code(existing_code, class_name, new_class_code)

        return existing_code

    def _intelligent_append(self, existing_code: str, new_code: str) -> str:
        """Intelligently append new code while avoiding conflicts"""
        if not existing_code.endswith('\n'):
            existing_code += '\n'

        return existing_code + '\n# ✨ Enhanced functionality:\n' + new_code

    def _extract_function_from_code(self, code: str, function_name: str) -> Optional[str]:
        """Extract a specific function from code using AST"""
        try:
            tree = ast.parse(code)
            lines = code.split('\n')

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                    start_line = node.lineno - 1  # Convert to 0-based indexing
                    end_line = node.end_lineno if hasattr(node, 'end_lineno') else len(lines)
                    return '\n'.join(lines[start_line:end_line])

            return None
        except:
            return None

    def _extract_class_from_code(self, code: str, class_name: str) -> Optional[str]:
        """Extract a specific class from code using AST"""
        try:
            tree = ast.parse(code)
            lines = code.split('\n')

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    start_line = node.lineno - 1
                    end_line = node.end_lineno if hasattr(node, 'end_lineno') else len(lines)
                    return '\n'.join(lines[start_line:end_line])

            return None
        except:
            return None

    def _replace_function_in_code(self, existing_code: str, function_name: str, new_function_code: str) -> str:
        """Replace a function in existing code"""
        pattern = rf'(def\s+{function_name}\s*\([^)]*\)\s*:[^\n]*(?:\n(?:[ \t]+[^\n]*|\n))*)'
        match = re.search(pattern, existing_code, re.MULTILINE)

        if match:
            return existing_code[:match.start()] + new_function_code + existing_code[match.end():]

        # If not found, append
        return existing_code + '\n\n' + new_function_code

    def _replace_class_in_code(self, existing_code: str, class_name: str, new_class_code: str) -> str:
        """Replace a class in existing code"""
        pattern = rf'(class\s+{class_name}\s*(?:\([^)]*\))?\s*:[^\n]*(?:\n(?:[ \t]+[^\n]*|\n))*)'
        match = re.search(pattern, existing_code, re.MULTILINE)

        if match:
            return existing_code[:match.start()] + new_class_code + existing_code[match.end():]

        # If not found, append
        return existing_code + '\n\n' + new_class_code

    def _verify_merged_code(self, code: str) -> Dict[str, Any]:
        """
        🤖 Self-verification of merged code
        """
        try:
            # Basic syntax check
            ast.parse(code)

            # Additional checks could include:
            # - Import validation
            # - Style checking (if black/ruff available)
            # - Basic lint checks

            return {
                'syntax_valid': True,
                'message': 'Code verification passed',
                'suggestions': []
            }

        except SyntaxError as e:
            return {
                'syntax_valid': False,
                'message': f'Syntax error: {str(e)} at line {e.lineno}',
                'line': e.lineno,
                'offset': e.offset
            }
        except Exception as e:
            return {
                'syntax_valid': False,
                'message': f'Verification error: {str(e)}'
            }

    def generate_test_case(self, function_info: Dict) -> str:
        """
        🧪 Generate basic test case for a function
        """
        func_name = function_info['name']
        args = function_info.get('args', [])
        docstring = function_info.get('docstring', '')

        # Simple test case template
        test_code = f'''
def test_{func_name}():
    """Test case for {func_name}"""
    # TODO: Add proper test assertions
    try:
        result = {func_name}({', '.join(['None'] * len(args))})
        assert result is not None, "Function should return a value"
        print(f"✅ {func_name} test passed")
        return True
    except Exception as e:
        print(f"❌ {func_name} test failed: {{e}}")
        return False
'''
        return test_code

    def _record_edit_history(self, operation: str, before_code: str, after_code: str,
                           reasoning: str, success: bool, syntax_valid: bool):
        """Record edit history for learning"""
        before_hash = hashlib.md5(before_code.encode()).hexdigest()
        after_hash = hashlib.md5(after_code.encode()).hexdigest()

        history_entry = EditHistory(
            timestamp=time.time(),
            operation=operation,
            before_hash=before_hash,
            after_hash=after_hash,
            reasoning=reasoning,
            success=success,
            syntax_valid=syntax_valid
        )

        self.edit_history.append(history_entry)

        # Keep only last 100 entries
        if len(self.edit_history) > 100:
            self.edit_history = self.edit_history[-100:]

    def get_learning_insights(self) -> Dict[str, Any]:
        """Analyze edit history to provide learning insights"""
        if not self.edit_history:
            return {'message': 'No edit history available'}

        total_edits = len(self.edit_history)
        successful_edits = sum(1 for e in self.edit_history if e.success)
        syntax_valid_edits = sum(1 for e in self.edit_history if e.syntax_valid)

        operation_stats = {}
        for entry in self.edit_history:
            op = entry.operation
            if op not in operation_stats:
                operation_stats[op] = {'total': 0, 'successful': 0}
            operation_stats[op]['total'] += 1
            if entry.success:
                operation_stats[op]['successful'] += 1

        return {
            'total_edits': total_edits,
            'success_rate': successful_edits / total_edits if total_edits > 0 else 0,
            'syntax_accuracy': syntax_valid_edits / total_edits if total_edits > 0 else 0,
            'operation_stats': operation_stats,
            'most_successful_operation': max(operation_stats.items(),
                                           key=lambda x: x[1]['successful'] / x[1]['total'] if x[1]['total'] > 0 else 0)[0] if operation_stats else None
        }

    def save_metadata_template(self, file_path: str, metadata: PluginMetadata) -> str:
        """Generate metadata template for a plugin file"""
        template = f'''# @plugin: {metadata.name}
# @functions: {', '.join(metadata.functions)}
# @classes: {', '.join(metadata.classes)}
# @version: {metadata.version}
# @description: {metadata.description}
# @dependencies: {', '.join(metadata.dependencies)}

"""
{metadata.description}
Version: {metadata.version}
"""

'''
        return template


# 🧪 Example usage and testing
if __name__ == "__main__":
    editor = ASTAwareCodeEditor()

    # Test plugin metadata parsing
    sample_plugin = '''
# @plugin: advanced_calculator
# @functions: add, multiply, calculate_advanced
# @version: 2.1
# @description: Advanced calculator with scientific functions

class Calculator:
    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b

def calculate_advanced(operation, *args):
    """Perform advanced calculations"""
    pass
'''

    metadata = editor.parse_plugin_metadata(sample_plugin)
    print("=== Plugin Metadata ===")
    if metadata:
        print(f"Name: {metadata.name}")
        print(f"Functions: {metadata.functions}")
        print(f"Classes: {metadata.classes}")
    else:
        print("Failed to parse metadata")

    # Test AST analysis
    analysis = editor.analyze_code_structure(sample_plugin)
    print("\n=== AST Analysis ===")
    print(f"Valid syntax: {analysis['valid_syntax']}")
    print(f"Functions found: {[f['name'] for f in analysis['functions']]}")
    print(f"Classes found: {[c['name'] for c in analysis['classes']]}")

    # Test intelligent merge
    new_function = '''
def add(self, a, b):
    """Enhanced addition with validation"""
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise ValueError("Arguments must be numbers")
    return a + b
'''

    merged_code, success, message = editor.intelligent_code_merge(
        sample_plugin,
        new_function,
        "Enhancing add function with validation"
    )

    print(f"\n=== Intelligent Merge ===")
    print(f"Success: {success}")
    print(f"Message: {message}")

    # Show learning insights
    insights = editor.get_learning_insights()
    print(f"\n=== Learning Insights ===")
    print(f"Total edits: {insights['total_edits']}")
    print(f"Success rate: {insights['success_rate']:.2%}")
