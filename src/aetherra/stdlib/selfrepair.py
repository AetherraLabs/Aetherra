#!/usr/bin/env python3
"""
🧬 NeuroCode Standard Library - Self Repair Plugin
Built-in plugin for NeuroCode to automatically debug and repair issues
"""

import re
import ast
from datetime import datetime

class SelfRepairPlugin:
    """Self-repair and debugging capabilities for NeuroCode"""

    def __init__(self):
        self.name = "selfrepair"
        self.description = "Automatic debugging and repair system"
        self.available_actions = ["detect_errors", "suggest_fixes", "auto_repair", "status"]

    def detect_syntax_errors(self, code_content):
        """Detect syntax errors in code"""
        errors = []
        try:
            ast.parse(code_content)
        except SyntaxError as e:
            errors.append({
                'type': 'SyntaxError',
                'line': e.lineno,
                'message': str(e),
                'text': e.text.strip() if e.text else '',
                'suggestion': self._suggest_syntax_fix(e)
            })
        except Exception as e:
            errors.append({
                'type': type(e).__name__,
                'line': 0,
                'message': str(e),
                'text': '',
                'suggestion': "Review code structure and syntax"
            })

        return errors

    def _suggest_syntax_fix(self, syntax_error):
        """Suggest fixes for common syntax errors"""
        message = str(syntax_error).lower()

        if "unexpected eof" in message or "was never closed" in message:
            return "Check for missing closing parentheses, brackets, or quotes"
        elif "invalid syntax" in message:
            return "Review syntax around the indicated line for typos or missing operators"
        elif "indentation" in message:
            return "Fix indentation - ensure consistent use of spaces or tabs"
        elif "unexpected indent" in message:
            return "Remove extra indentation or add missing code block"
        else:
            return "Review Python syntax rules for the error type"

    def analyze_runtime_errors(self, error_traceback):
        """Analyze runtime errors and suggest fixes"""
        analysis = {
            'error_type': 'unknown',
            'likely_cause': 'unknown',
            'suggested_fix': 'Review error details',
            'confidence': 0
        }

        if 'NameError' in error_traceback:
            analysis.update({
                'error_type': 'NameError',
                'likely_cause': 'Variable or function used before definition',
                'suggested_fix': 'Check variable names and import statements',
                'confidence': 85
            })
        elif 'AttributeError' in error_traceback:
            analysis.update({
                'error_type': 'AttributeError',
                'likely_cause': 'Method or attribute does not exist',
                'suggested_fix': 'Verify object type and available methods',
                'confidence': 80
            })
        elif 'IndexError' in error_traceback:
            analysis.update({
                'error_type': 'IndexError',
                'likely_cause': 'Accessing list/array index that does not exist',
                'suggested_fix': 'Add bounds checking or handle empty collections',
                'confidence': 90
            })
        elif 'KeyError' in error_traceback:
            analysis.update({
                'error_type': 'KeyError',
                'likely_cause': 'Accessing dictionary key that does not exist',
                'suggested_fix': 'Use dict.get() or check if key exists first',
                'confidence': 90
            })

        return analysis

    def suggest_code_improvements(self, code_content):
        """Suggest general code improvements"""
        suggestions = []

        # Check for potential issues
        if 'print(' in code_content:
            suggestions.append("Consider using logging instead of print statements for production code")

        if 'except:' in code_content and 'except Exception:' not in code_content:
            suggestions.append("Use specific exception types instead of bare except clauses")

        if re.search(r'def \w+\([^)]*\):\s*$', code_content, re.MULTILINE):
            suggestions.append("Add docstrings to functions for better documentation")

        # Count function complexity
        function_lines = [line for line in code_content.split('\n') if line.strip().startswith('def ')]
        if len(function_lines) > 10:
            suggestions.append("Consider breaking large files into smaller modules")

        return suggestions

    def auto_fix_common_issues(self, code_content):
        """Attempt to automatically fix common issues"""
        fixed_code = code_content
        fixes_applied = []

        # Fix common spacing issues
        if '=' in fixed_code:
            # Add spaces around operators
            fixed_code = re.sub(r'(\w)=(\w)', r'\1 = \2', fixed_code)
            if fixed_code != code_content:
                fixes_applied.append("Added spacing around assignment operators")

        # Fix simple import issues
        if 'import*' in fixed_code.replace(' ', ''):
            fixed_code = fixed_code.replace('import*', 'import *')
            fixes_applied.append("Fixed wildcard import spacing")

        return {
            'fixed_code': fixed_code,
            'fixes_applied': fixes_applied,
            'manual_review_needed': len(fixes_applied) == 0
        }

    def generate_repair_report(self, target_file, issues=None):
        """Generate comprehensive repair report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'target_file': target_file,
            'issues_found': len(issues) if issues else 0,
            'repair_suggestions': [],
            'auto_fix_available': False,
            'confidence_score': 0
        }

        if issues:
            for issue in issues:
                suggestion = {
                    'issue_type': issue.get('type', 'unknown'),
                    'severity': self._assess_severity(issue),
                    'fix_suggestion': issue.get('suggestion', 'Manual review required'),
                    'auto_fixable': self._can_auto_fix(issue)
                }
                report['repair_suggestions'].append(suggestion)

            report['auto_fix_available'] = any(s['auto_fixable'] for s in report['repair_suggestions'])
            report['confidence_score'] = self._calculate_confidence(issues)

        return report

    def _assess_severity(self, issue):
        """Assess the severity of an issue"""
        if issue.get('type') == 'SyntaxError':
            return 'critical'
        elif issue.get('type') in ['NameError', 'AttributeError']:
            return 'high'
        else:
            return 'medium'

    def _can_auto_fix(self, issue):
        """Determine if an issue can be automatically fixed"""
        auto_fixable_types = ['spacing', 'import', 'simple_syntax']
        return any(fix_type in issue.get('suggestion', '').lower() for fix_type in auto_fixable_types)

    def _calculate_confidence(self, issues):
        """Calculate confidence score for repair suggestions"""
        if not issues:
            return 0

        total_confidence = sum(issue.get('confidence', 50) for issue in issues)
        return total_confidence / len(issues)

    def execute_action(self, action, memory_system=None, target="unknown", code_content=""):
        """Execute self-repair actions for NeuroCode"""
        if action == "detect_errors":
            errors = self.detect_syntax_errors(code_content)

            if memory_system:
                memory_system.remember(
                    f"Error detection completed for {target}: {len(errors)} issues found",
                    tags=['selfrepair', 'error_detection', 'debugging'],
                    category='maintenance'
                )

            return errors

        elif action == "suggest_fixes":
            suggestions = self.suggest_code_improvements(code_content)

            if memory_system:
                memory_system.remember(
                    f"Generated {len(suggestions)} improvement suggestions for {target}",
                    tags=['selfrepair', 'suggestions', 'code_quality'],
                    category='maintenance'
                )

            return suggestions

        elif action == "auto_repair":
            repair_result = self.auto_fix_common_issues(code_content)

            if memory_system:
                memory_system.remember(
                    f"Auto-repair attempted for {target}: "
                    f"{len(repair_result['fixes_applied'])} fixes applied",
                    tags=['selfrepair', 'auto_fix', 'maintenance'],
                    category='maintenance'
                )

            return repair_result

        elif action == "status":
            return {
                'plugin_name': self.name,
                'status': 'active',
                'features': [
                    'Syntax error detection',
                    'Code improvement suggestions',
                    'Automatic repair for common issues',
                    'Pattern-based debugging'
                ],
                'available_actions': ['detect_errors', 'suggest_fixes', 'auto_repair', 'status'],
                'usage': [
                    'selfrepair detect_errors [code_content]',
                    'selfrepair suggest_fixes [code_content]',
                    'selfrepair auto_repair [code_content]',
                    'selfrepair status'
                ]
            }

        else:
            return {
                'error': f"Unknown selfrepair action: {action}",
                'available_actions': ['detect_errors', 'suggest_fixes', 'auto_repair', 'status'],
                'usage': [
                    'selfrepair detect_errors [code_content]',
                    'selfrepair suggest_fixes [code_content]',
                    'selfrepair auto_repair [code_content]',
                    'selfrepair status'
                ]
            }


# Register plugin
PLUGIN_CLASS = SelfRepairPlugin
