"""
🛡️ PLUGIN CONFIDENCE & SAFETY SYSTEM
===================================

Advanced confidence scoring and safety assessment for Lyrixa plugins.
Integrates with existing analytics and quality control systems to provide
comprehensive trust metrics and safety recommendations.

Features:
- Runtime performance analysis
- Static code safety analysis  
- Confidence scoring algorithm
- Safety warnings and recommendations
- Integration with Lyrixa core for decision making
"""

import ast
import logging
import sqlite3
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SafetyAnalysis:
    """Comprehensive safety analysis for plugin code."""
    
    UNSAFE_IMPORTS = {
        'os.system', 'os.popen', 'os.spawn', 'os.exec',
        'subprocess.call', 'subprocess.run', 'subprocess.Popen',
        'eval', 'exec', 'compile',
        '__import__', 'importlib.import_module',
        'open', 'file',  # File operations need scrutiny
        'urllib.request', 'requests',  # Network operations
        'socket', 'http', 'ftplib',
        'pickle.loads', 'pickle.load',  # Unsafe deserialization
        'ctypes', 'cffi',  # Low-level system access
        'threading.Thread', 'multiprocessing',  # Threading concerns
    }
    
    UNSAFE_PATTERNS = [
        r'rm\s+-rf',  # Dangerous shell commands
        r'del\s+/[sqf]',  # Windows delete commands
        r'format\s+c:',  # Format commands
        r'\.\./',  # Directory traversal
        r'__.*__',  # Dunder methods (potential security risk)
        r'globals\(\)',  # Global access
        r'locals\(\)',  # Local scope access
        r'setattr\(',  # Dynamic attribute setting
        r'getattr\(',  # Dynamic attribute getting
        r'hasattr\(',  # Attribute checking
    ]
    
    def __init__(self):
        self.analysis_cache = {}
        
    def analyze_code_safety(self, code: str, plugin_name: str) -> Dict[str, Any]:
        """Perform comprehensive safety analysis on plugin code."""
        
        # Check cache first
        code_hash = hash(code)
        if code_hash in self.analysis_cache:
            return self.analysis_cache[code_hash]
        
        safety_report = {
            'plugin_name': plugin_name,
            'timestamp': datetime.now().isoformat(),
            'safety_score': 100.0,  # Start with perfect score, deduct for issues
            'issues': [],
            'warnings': [],
            'recommendations': [],
            'risk_level': 'LOW',  # LOW, MEDIUM, HIGH, CRITICAL
            'safe_to_execute': True
        }
        
        try:
            # Parse AST for static analysis
            tree = ast.parse(code)
            
            # Check for unsafe imports
            self._check_unsafe_imports(tree, safety_report)
            
            # Check for unsafe patterns
            self._check_unsafe_patterns(code, safety_report)
            
            # Check code complexity
            self._check_complexity(tree, safety_report)
            
            # Check for suspicious behaviors
            self._check_suspicious_behaviors(tree, safety_report)
            
            # Calculate final risk assessment
            self._calculate_risk_level(safety_report)
            
        except SyntaxError as e:
            safety_report['issues'].append({
                'type': 'SYNTAX_ERROR',
                'severity': 'CRITICAL',
                'message': f"Syntax error in plugin code: {str(e)}",
                'line': getattr(e, 'lineno', 'unknown')
            })
            safety_report['safety_score'] = 0.0
            safety_report['risk_level'] = 'CRITICAL'
            safety_report['safe_to_execute'] = False
            
        except Exception as e:
            safety_report['issues'].append({
                'type': 'ANALYSIS_ERROR',
                'severity': 'HIGH',
                'message': f"Failed to analyze code: {str(e)}"
            })
            safety_report['safety_score'] = 20.0
            safety_report['risk_level'] = 'HIGH'
            
        # Cache the result
        self.analysis_cache[code_hash] = safety_report
        return safety_report
    
    def _check_unsafe_imports(self, tree: ast.AST, safety_report: Dict):
        """Check for potentially unsafe imports."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in self.UNSAFE_IMPORTS:
                        safety_report['issues'].append({
                            'type': 'UNSAFE_IMPORT',
                            'severity': 'HIGH',
                            'message': f"Potentially unsafe import: {alias.name}",
                            'line': node.lineno
                        })
                        safety_report['safety_score'] -= 15.0
                        
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        import_path = f"{node.module}.{alias.name}"
                        if import_path in self.UNSAFE_IMPORTS:
                            safety_report['issues'].append({
                                'type': 'UNSAFE_IMPORT',
                                'severity': 'HIGH',
                                'message': f"Potentially unsafe import: {import_path}",
                                'line': node.lineno
                            })
                            safety_report['safety_score'] -= 15.0
    
    def _check_unsafe_patterns(self, code: str, safety_report: Dict):
        """Check for unsafe code patterns using regex."""
        for pattern in self.UNSAFE_PATTERNS:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                safety_report['warnings'].append({
                    'type': 'UNSAFE_PATTERN',
                    'severity': 'MEDIUM',
                    'message': f"Potentially unsafe pattern detected: {match.group()}",
                    'line': line_num
                })
                safety_report['safety_score'] -= 10.0
    
    def _check_complexity(self, tree: ast.AST, safety_report: Dict):
        """Check code complexity metrics."""
        complexity = self._calculate_cyclomatic_complexity(tree)
        
        if complexity > 20:
            safety_report['warnings'].append({
                'type': 'HIGH_COMPLEXITY',
                'severity': 'MEDIUM',
                'message': f"High cyclomatic complexity: {complexity}",
                'recommendation': 'Consider breaking down complex functions'
            })
            safety_report['safety_score'] -= 5.0
        elif complexity > 10:
            safety_report['warnings'].append({
                'type': 'MODERATE_COMPLEXITY',
                'severity': 'LOW',
                'message': f"Moderate cyclomatic complexity: {complexity}"
            })
            safety_report['safety_score'] -= 2.0
    
    def _check_suspicious_behaviors(self, tree: ast.AST, safety_report: Dict):
        """Check for suspicious behaviors in the code."""
        for node in ast.walk(tree):
            # Check for dynamic execution
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec', 'compile']:
                        safety_report['issues'].append({
                            'type': 'DYNAMIC_EXECUTION',
                            'severity': 'CRITICAL',
                            'message': f"Dynamic code execution detected: {node.func.id}",
                            'line': node.lineno
                        })
                        safety_report['safety_score'] -= 25.0
    
    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity of the code."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.With):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
                
        return complexity
    
    def _calculate_risk_level(self, safety_report: Dict):
        """Calculate overall risk level based on issues and score."""
        score = safety_report['safety_score']
        has_critical = any(issue['severity'] == 'CRITICAL' for issue in safety_report['issues'])
        has_high = any(issue['severity'] == 'HIGH' for issue in safety_report['issues'])
        
        if has_critical or score < 20:
            safety_report['risk_level'] = 'CRITICAL'
            safety_report['safe_to_execute'] = False
        elif has_high or score < 50:
            safety_report['risk_level'] = 'HIGH'
            safety_report['safe_to_execute'] = False
        elif score < 70:
            safety_report['risk_level'] = 'MEDIUM'
        else:
            safety_report['risk_level'] = 'LOW'


class RuntimeMetrics:
    """Tracks runtime performance and reliability metrics."""
    
    def __init__(self, db_path: str = "plugin_confidence.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the confidence metrics database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS plugin_runtime_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_name TEXT NOT NULL,
                    execution_time REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    error_type TEXT,
                    error_message TEXT,
                    memory_peak REAL,
                    timestamp TEXT NOT NULL,
                    context_info TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS plugin_confidence_scores (
                    plugin_name TEXT PRIMARY KEY,
                    confidence_score REAL NOT NULL,
                    success_rate REAL NOT NULL,
                    avg_execution_time REAL NOT NULL,
                    error_frequency REAL NOT NULL,
                    last_updated TEXT NOT NULL,
                    total_executions INTEGER NOT NULL,
                    safety_score REAL,
                    risk_level TEXT
                )
            """)
    
    def record_execution(self, plugin_name: str, execution_time: float, 
                        success: bool, error_info: Optional[Dict] = None,
                        context_info: Optional[str] = None):
        """Record a plugin execution for metrics tracking."""
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO plugin_runtime_metrics 
                (plugin_name, execution_time, success, error_type, error_message, timestamp, context_info)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                plugin_name,
                execution_time,
                success,
                error_info.get('type') if error_info else None,
                error_info.get('message') if error_info else None,
                datetime.now().isoformat(),
                context_info
            ))
    
    def get_plugin_metrics(self, plugin_name: str, days_back: int = 30) -> Dict[str, Any]:
        """Get comprehensive metrics for a specific plugin."""
        
        cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Get recent executions
            cursor = conn.execute("""
                SELECT execution_time, success, error_type, error_message
                FROM plugin_runtime_metrics 
                WHERE plugin_name = ? AND timestamp > ?
                ORDER BY timestamp DESC
            """, (plugin_name, cutoff_date))
            
            executions = cursor.fetchall()
        
        if not executions:
            return {
                'plugin_name': plugin_name,
                'total_executions': 0,
                'success_rate': 0.0,
                'avg_execution_time': 0.0,
                'error_frequency': 0.0,
                'common_errors': [],
                'performance_trend': 'NO_DATA'
            }
        
        # Calculate metrics
        total_executions = len(executions)
        successful_executions = sum(1 for ex in executions if ex[1])
        success_rate = successful_executions / total_executions
        
        execution_times = [ex[0] for ex in executions]
        avg_execution_time = statistics.mean(execution_times)
        
        error_count = total_executions - successful_executions
        error_frequency = error_count / total_executions
        
        # Analyze common errors
        error_types = [ex[2] for ex in executions if ex[2]]
        from collections import Counter
        common_errors = Counter(error_types).most_common(3)
        
        return {
            'plugin_name': plugin_name,
            'total_executions': total_executions,
            'success_rate': success_rate,
            'avg_execution_time': avg_execution_time,
            'error_frequency': error_frequency,
            'common_errors': common_errors,
            'recent_performance': execution_times[:10],  # Last 10 executions
            'performance_trend': self._calculate_performance_trend(execution_times)
        }
    
    def _calculate_performance_trend(self, execution_times: List[float]) -> str:
        """Calculate if performance is improving, degrading, or stable."""
        if len(execution_times) < 5:
            return 'INSUFFICIENT_DATA'
        
        # Compare first half with second half
        mid = len(execution_times) // 2
        first_half_avg = statistics.mean(execution_times[:mid])
        second_half_avg = statistics.mean(execution_times[mid:])
        
        improvement_threshold = 0.1  # 10% improvement
        degradation_threshold = 0.2  # 20% degradation
        
        change_ratio = (second_half_avg - first_half_avg) / first_half_avg
        
        if change_ratio < -improvement_threshold:
            return 'IMPROVING'
        elif change_ratio > degradation_threshold:
            return 'DEGRADING'
        else:
            return 'STABLE'


class PluginScorer:
    """
    Main plugin confidence scoring system.
    Combines safety analysis and runtime metrics to generate confidence scores.
    """
    
    def __init__(self, db_path: str = "plugin_confidence.db"):
        self.safety_analyzer = SafetyAnalysis()
        self.runtime_metrics = RuntimeMetrics(db_path)
        self.db_path = db_path
    
    def analyze_plugin(self, plugin_name: str, plugin_code: str, 
                      plugin_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Comprehensive plugin analysis combining safety and runtime metrics.
        """
        
        # Perform safety analysis
        safety_analysis = self.safety_analyzer.analyze_code_safety(plugin_code, plugin_name)
        
        # Get runtime metrics
        runtime_metrics = self.runtime_metrics.get_plugin_metrics(plugin_name)
        
        # Calculate overall confidence score
        confidence_score = self._calculate_confidence_score(safety_analysis, runtime_metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(safety_analysis, runtime_metrics)
        
        # Update database with latest scores
        self._update_confidence_database(plugin_name, confidence_score, safety_analysis, runtime_metrics)
        
        return {
            'plugin_name': plugin_name,
            'confidence_score': confidence_score,
            'safety_analysis': safety_analysis,
            'runtime_metrics': runtime_metrics,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_confidence_score(self, safety_analysis: Dict, runtime_metrics: Dict) -> float:
        """
        Calculate overall confidence score (0.0 to 1.0) based on safety and runtime metrics.
        
        Weighting:
        - Safety Score: 40%
        - Success Rate: 30% 
        - Performance: 20%
        - Error Frequency: 10%
        """
        
        # Safety component (40% weight)
        safety_score = safety_analysis['safety_score'] / 100.0
        safety_component = safety_score * 0.4
        
        # Runtime reliability component (30% weight)
        success_rate = runtime_metrics.get('success_rate', 0.0)
        reliability_component = success_rate * 0.3
        
        # Performance component (20% weight)
        avg_time = runtime_metrics.get('avg_execution_time', float('inf'))
        # Normalize execution time (under 1 second = full score, over 10 seconds = 0 score)
        if avg_time == 0:
            performance_score = 1.0
        else:
            performance_score = max(0.0, min(1.0, (10.0 - avg_time) / 10.0))
        performance_component = performance_score * 0.2
        
        # Error frequency component (10% weight)
        error_frequency = runtime_metrics.get('error_frequency', 1.0)
        error_component = (1.0 - error_frequency) * 0.1
        
        # Calculate final confidence score
        total_confidence = safety_component + reliability_component + performance_component + error_component
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, total_confidence))
    
    def _generate_recommendations(self, safety_analysis: Dict, runtime_metrics: Dict) -> List[Dict]:
        """Generate actionable recommendations based on analysis."""
        
        recommendations = []
        
        # Safety-based recommendations
        if safety_analysis['safety_score'] < 70:
            recommendations.append({
                'type': 'SAFETY',
                'priority': 'HIGH',
                'message': 'Plugin has safety concerns that should be addressed',
                'actions': ['Review unsafe imports', 'Remove dynamic code execution', 'Add input validation']
            })
        
        # Performance-based recommendations
        avg_time = runtime_metrics.get('avg_execution_time', 0)
        if avg_time > 5.0:
            recommendations.append({
                'type': 'PERFORMANCE',
                'priority': 'MEDIUM',
                'message': f'Plugin execution time is high ({avg_time:.2f}s)',
                'actions': ['Profile code for bottlenecks', 'Optimize algorithms', 'Add caching']
            })
        
        # Reliability-based recommendations
        success_rate = runtime_metrics.get('success_rate', 1.0)
        if success_rate < 0.8:
            recommendations.append({
                'type': 'RELIABILITY',
                'priority': 'HIGH',
                'message': f'Plugin has low success rate ({success_rate:.1%})',
                'actions': ['Add error handling', 'Improve input validation', 'Add logging']
            })
        
        # Error pattern recommendations
        common_errors = runtime_metrics.get('common_errors', [])
        if common_errors:
            recommendations.append({
                'type': 'ERROR_HANDLING',
                'priority': 'MEDIUM',
                'message': f'Common errors detected: {", ".join([err[0] for err in common_errors[:2]])}',
                'actions': ['Add specific error handling', 'Improve error messages', 'Add retry logic']
            })
        
        return recommendations
    
    def _update_confidence_database(self, plugin_name: str, confidence_score: float, 
                                  safety_analysis: Dict, runtime_metrics: Dict):
        """Update the confidence database with latest scores."""
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO plugin_confidence_scores 
                (plugin_name, confidence_score, success_rate, avg_execution_time, 
                 error_frequency, last_updated, total_executions, safety_score, risk_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plugin_name,
                confidence_score,
                runtime_metrics.get('success_rate', 0.0),
                runtime_metrics.get('avg_execution_time', 0.0),
                runtime_metrics.get('error_frequency', 0.0),
                datetime.now().isoformat(),
                runtime_metrics.get('total_executions', 0),
                safety_analysis['safety_score'],
                safety_analysis['risk_level']
            ))
    
    def get_plugin_confidence(self, plugin_name: str) -> Optional[Dict]:
        """Get stored confidence score for a plugin."""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT confidence_score, success_rate, avg_execution_time, 
                       error_frequency, last_updated, total_executions, 
                       safety_score, risk_level
                FROM plugin_confidence_scores 
                WHERE plugin_name = ?
            """, (plugin_name,))
            
            result = cursor.fetchone()
            
        if result:
            return {
                'plugin_name': plugin_name,
                'confidence_score': result[0],
                'success_rate': result[1],
                'avg_execution_time': result[2],
                'error_frequency': result[3],
                'last_updated': result[4],
                'total_executions': result[5],
                'safety_score': result[6],
                'risk_level': result[7]
            }
        
        return None
    
    def get_all_plugin_scores(self) -> List[Dict]:
        """Get confidence scores for all plugins."""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT plugin_name, confidence_score, success_rate, avg_execution_time, 
                       error_frequency, last_updated, total_executions, 
                       safety_score, risk_level
                FROM plugin_confidence_scores 
                ORDER BY confidence_score DESC
            """)
            
            results = cursor.fetchall()
        
        return [
            {
                'plugin_name': row[0],
                'confidence_score': row[1],
                'success_rate': row[2],
                'avg_execution_time': row[3],
                'error_frequency': row[4],
                'last_updated': row[5],
                'total_executions': row[6],
                'safety_score': row[7],
                'risk_level': row[8]
            }
            for row in results
        ]
    
    def record_plugin_execution(self, plugin_name: str, execution_time: float, 
                               success: bool, error_info: Optional[Dict] = None):
        """Record a plugin execution for tracking."""
        self.runtime_metrics.record_execution(plugin_name, execution_time, success, error_info)


# Integration helper functions for Lyrixa

def get_plugin_confidence_warning(plugin_name: str, confidence_score: float, 
                                 risk_level: str) -> Optional[str]:
    """Generate user-friendly confidence warnings for Lyrixa."""
    
    if risk_level == 'CRITICAL':
        return f"⚠️ Plugin '{plugin_name}' has critical safety issues. Execution blocked for your protection."
    
    elif risk_level == 'HIGH':
        return f"🚨 Plugin '{plugin_name}' has high risk (confidence: {confidence_score:.1%}). Proceed with caution."
    
    elif confidence_score < 0.5:
        return f"⚠️ Plugin '{plugin_name}' has low confidence ({confidence_score:.1%}). Consider alternatives or improvements."
    
    elif confidence_score < 0.7:
        return f"💡 Plugin '{plugin_name}' has moderate confidence ({confidence_score:.1%}). May need optimization."
    
    return None


def should_block_plugin_execution(risk_level: str, confidence_score: float, 
                                 user_override: bool = False) -> bool:
    """Determine if plugin execution should be blocked."""
    
    if risk_level in ['CRITICAL'] and not user_override:
        return True
    
    if risk_level == 'HIGH' and confidence_score < 0.3 and not user_override:
        return True
    
    return False


# Example usage and testing
if __name__ == "__main__":
    # Initialize the scorer
    scorer = PluginScorer()
    
    # Test with sample plugin code
    sample_code = '''
def execute(command, **kwargs):
    """Safe plugin execution function."""
    try:
        result = f"Executed: {command}"
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_info():
    return {
        "name": "Sample Plugin",
        "version": "1.0.0",
        "description": "A safe sample plugin"
    }
'''
    
    # Analyze the plugin
    analysis = scorer.analyze_plugin("sample_plugin", sample_code)
    
    print("Plugin Confidence Analysis:")
    print(f"Plugin: {analysis['plugin_name']}")
    print(f"Confidence Score: {analysis['confidence_score']:.1%}")
    print(f"Safety Score: {analysis['safety_analysis']['safety_score']:.1f}/100")
    print(f"Risk Level: {analysis['safety_analysis']['risk_level']}")
    
    if analysis['recommendations']:
        print("Recommendations:")
        for rec in analysis['recommendations']:
            print(f"  - {rec['type']}: {rec['message']}")
