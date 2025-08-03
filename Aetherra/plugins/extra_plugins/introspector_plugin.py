#!/usr/bin/env python3
"""
🔍 LYRIXA INTROSPECTOR PLUGIN
============================

Autonomous file analysis and self-insight generation system.
Scans Lyrixa's own codebase to identify improvement opportunities,
issues, and patterns for self-enhancement.
"""

import ast
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.enhanced_memory import LyrixaEnhancedMemorySystem


class IntrospectorPlugin:
    """Plugin for autonomous code analysis and self-insight generation"""

    # Required plugin metadata
    name = "introspector_plugin"
    description = "Autonomous file analysis and self-insight generation for Lyrixa"
    version = "1.0.0"

    input_schema = {
        "type": "object",
        "properties": {
            "target_files": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of file paths to analyze",
            },
            "analysis_depth": {
                "type": "string",
                "enum": ["basic", "medium", "deep"],
                "default": "medium",
                "description": "Depth of analysis to perform",
            },
        },
        "required": ["target_files"],
    }

    output_schema = {
        "type": "object",
        "properties": {
            "insights": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Generated insights and improvement suggestions",
            },
            "metrics": {
                "type": "object",
                "description": "Code quality and complexity metrics",
            },
            "recommendations": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific improvement recommendations",
            },
        },
    }

    created_by = "Lyrixa Autonomous System"

    def __init__(self, memory_system: Optional[LyrixaEnhancedMemorySystem] = None):
        self.memory_system = memory_system
        self.analysis_patterns = {
            "todo_fixme": r"(?i)(?:TODO|FIXME|XXX|HACK)(?:\s*[:]\s*)?(.+)",
            "complexity_indicators": [
                r"if\s+.+and\s+.+and\s+",  # Complex conditionals
                r"try:\s*\n(?:\s+.+\n)*\s+except\s+Exception",  # Bare exception handling
                r"def\s+\w+\([^)]{50,}\)",  # Long parameter lists
            ],
            "code_smells": [
                r"print\s*\(",  # Debug prints
                r"import\s+\*",  # Wildcard imports
                r"class\s+\w+\([^)]*\):\s*\n\s*pass",  # Empty classes
            ],
            "improvement_opportunities": [
                r"async\s+def.*(?!await)",  # Async functions without await
                r"def\s+\w+.*:\s*\n(?:\s*#.*\n)*\s*$",  # Functions without implementation
            ],
        }

    async def main(
        self, target_files: List[str], analysis_depth: str = "medium"
    ) -> Dict[str, Any]:
        """Main introspection analysis function (now supports more file types and directories)"""
        print(
            f"🔍 Starting introspection analysis on {len(target_files)} files/directories..."
        )

        insights = []
        metrics = {"total_files": 0, "total_lines": 0, "issues_found": 0}
        recommendations = []
        exts = {".py", ".aether", ".json", ".md", ".js", ".css"}

        def expand_targets(targets):
            expanded = set()
            for t in targets:
                path = Path(t)
                if path.is_dir():
                    for subpath in path.rglob("*"):
                        if subpath.is_file() and subpath.suffix in exts:
                            expanded.add(str(subpath))
                elif path.exists() and path.suffix in exts:
                    expanded.add(str(path))
            return list(expanded)

        all_files = expand_targets(target_files)
        print(f"🔎 Expanded to {len(all_files)} files for introspection.")

        for file_path in all_files:
            try:
                file_insights = await self._analyze_file(file_path, analysis_depth)
                if file_insights:
                    insights.extend(file_insights["insights"])
                    recommendations.extend(file_insights["recommendations"])
                    metrics["total_files"] += 1
                    metrics["total_lines"] += file_insights.get("line_count", 0)
                    metrics["issues_found"] += len(file_insights["insights"])
            except Exception as e:
                insights.append(
                    {
                        "type": "analysis_error",
                        "file": file_path,
                        "issue": f"Failed to analyze file: {str(e)}",
                        "severity": "medium",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        # Store insights in memory for future reference
        if self.memory_system and insights:
            await self._store_insights_in_memory(insights, metrics, recommendations)

        # Generate high-level recommendations
        high_level_recommendations = await self._generate_high_level_recommendations(
            insights, metrics
        )
        recommendations.extend(high_level_recommendations)

        print(
            f"✅ Introspection complete: {metrics['issues_found']} insights generated"
        )

        return {
            "success": True,
            "insights": insights,
            "metrics": metrics,
            "recommendations": recommendations,
            "analysis_timestamp": datetime.now().isoformat(),
        }

    async def _analyze_file(
        self, file_path: str, depth: str
    ) -> Optional[Dict[str, Any]]:
        """Analyze a single file for insights"""
        path = Path(file_path)

        # Skip non-existent or non-text files
        if not path.exists() or path.suffix not in {".py", ".aether", ".json", ".md"}:
            return None

        try:
            content = path.read_text(encoding="utf-8")
            line_count = len(content.splitlines())

            insights = []
            recommendations = []

            # Basic analysis: TODO/FIXME detection
            todo_matches = re.finditer(self.analysis_patterns["todo_fixme"], content)
            for match in todo_matches:
                insights.append(
                    {
                        "type": "todo_fixme",
                        "file": str(path),
                        "issue": f"TODO/FIXME found: {match.group(1).strip()}",
                        "line": content[: match.start()].count("\n") + 1,
                        "severity": "low",
                        "actionable": True,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            # Medium/Deep analysis for Python files
            if path.suffix == ".py" and depth in ["medium", "deep"]:
                python_insights = await self._analyze_python_file(content, str(path))
                insights.extend(python_insights)

            # Deep analysis: Advanced pattern detection
            if depth == "deep":
                advanced_insights = await self._deep_analysis(content, str(path))
                insights.extend(advanced_insights)

            # Generate file-specific recommendations
            if insights:
                file_recommendations = await self._generate_file_recommendations(
                    insights, str(path)
                )
                recommendations.extend(file_recommendations)

            return {
                "insights": insights,
                "recommendations": recommendations,
                "line_count": line_count,
                "file_type": path.suffix,
            }

        except Exception as e:
            return {
                "insights": [
                    {
                        "type": "file_error",
                        "file": str(path),
                        "issue": f"Error reading file: {str(e)}",
                        "severity": "medium",
                        "timestamp": datetime.now().isoformat(),
                    }
                ],
                "recommendations": [],
                "line_count": 0,
            }

    async def _analyze_python_file(
        self, content: str, file_path: str
    ) -> List[Dict[str, Any]]:
        """Perform Python-specific analysis"""
        insights = []

        try:
            # Parse AST for structural analysis
            tree = ast.parse(content)

            # Analyze functions and classes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for complex functions
                    if len(node.body) > 20:
                        insights.append(
                            {
                                "type": "complexity",
                                "file": file_path,
                                "issue": f"Function '{node.name}' is complex ({len(node.body)} statements)",
                                "line": node.lineno,
                                "severity": "medium",
                                "suggestion": "Consider breaking into smaller functions",
                                "timestamp": datetime.now().isoformat(),
                            }
                        )

                    # Check for missing docstrings
                    if not ast.get_docstring(node):
                        insights.append(
                            {
                                "type": "documentation",
                                "file": file_path,
                                "issue": f"Function '{node.name}' lacks documentation",
                                "line": node.lineno,
                                "severity": "low",
                                "suggestion": "Add docstring to improve code maintainability",
                                "timestamp": datetime.now().isoformat(),
                            }
                        )

                elif isinstance(node, ast.ClassDef):
                    # Check for large classes
                    methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    if len(methods) > 15:
                        insights.append(
                            {
                                "type": "design",
                                "file": file_path,
                                "issue": f"Class '{node.name}' has many methods ({len(methods)})",
                                "line": node.lineno,
                                "severity": "medium",
                                "suggestion": "Consider splitting into multiple classes or using composition",
                                "timestamp": datetime.now().isoformat(),
                            }
                        )

        except SyntaxError as e:
            insights.append(
                {
                    "type": "syntax_error",
                    "file": file_path,
                    "issue": f"Syntax error: {str(e)}",
                    "line": getattr(e, "lineno", 0),
                    "severity": "high",
                    "actionable": True,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        # Pattern-based analysis
        for pattern in self.analysis_patterns["code_smells"]:
            matches = re.finditer(pattern, content)
            for match in matches:
                insights.append(
                    {
                        "type": "code_smell",
                        "file": file_path,
                        "issue": f"Potential code smell detected: {match.group()}",
                        "line": content[: match.start()].count("\n") + 1,
                        "severity": "low",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        return insights

    async def _deep_analysis(
        self, content: str, file_path: str
    ) -> List[Dict[str, Any]]:
        """Perform deep analysis for advanced insights"""
        insights = []

        # Analyze for improvement opportunities
        for pattern in self.analysis_patterns["improvement_opportunities"]:
            matches = re.finditer(pattern, content)
            for match in matches:
                insights.append(
                    {
                        "type": "improvement_opportunity",
                        "file": file_path,
                        "issue": f"Potential improvement: {match.group()}",
                        "line": content[: match.start()].count("\n") + 1,
                        "severity": "low",
                        "suggestion": "Consider optimizing or completing implementation",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        # Check for performance concerns
        performance_patterns = [
            r"for\s+\w+\s+in\s+range\(len\(",  # Use enumerate instead
            r"\.append\([^)]+\)\s*\n\s*for",  # List comprehension opportunity
        ]

        for pattern in performance_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                insights.append(
                    {
                        "type": "performance",
                        "file": file_path,
                        "issue": f"Performance improvement opportunity: {match.group()}",
                        "line": content[: match.start()].count("\n") + 1,
                        "severity": "low",
                        "suggestion": "Consider more efficient Python patterns",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        return insights

    async def _generate_file_recommendations(
        self, insights: List[Dict], file_path: str
    ) -> List[str]:
        """Generate specific recommendations for a file"""
        recommendations = []

        # Group insights by type
        insight_types = {}
        for insight in insights:
            insight_type = insight.get("type", "unknown")
            if insight_type not in insight_types:
                insight_types[insight_type] = 0
            insight_types[insight_type] += 1

        # Generate recommendations based on patterns
        if insight_types.get("todo_fixme", 0) > 3:
            recommendations.append(
                f"File {file_path} has many TODOs - consider prioritizing completion"
            )

        if insight_types.get("complexity", 0) > 2:
            recommendations.append(
                f"File {file_path} has complex functions - consider refactoring"
            )

        if insight_types.get("documentation", 0) > 5:
            recommendations.append(
                f"File {file_path} needs better documentation coverage"
            )

        return recommendations

    async def _generate_high_level_recommendations(
        self, insights: List[Dict], metrics: Dict
    ) -> List[str]:
        """Generate system-wide recommendations"""
        recommendations = []

        total_issues = metrics.get("issues_found", 0)
        total_files = metrics.get("total_files", 1)

        if total_issues > total_files * 5:  # More than 5 issues per file on average
            recommendations.append(
                "High number of issues detected - consider code quality review"
            )

        # Count severity levels
        high_severity = sum(
            1 for insight in insights if insight.get("severity") == "high"
        )
        if high_severity > 0:
            recommendations.append(
                f"Found {high_severity} high-severity issues requiring immediate attention"
            )

        # Check for patterns across files
        todo_count = sum(
            1 for insight in insights if insight.get("type") == "todo_fixme"
        )
        if todo_count > 10:
            recommendations.append("Consider creating a TODO cleanup sprint")

        return recommendations

    async def _store_insights_in_memory(
        self, insights: List[Dict], metrics: Dict, recommendations: List[str]
    ):
        """Store analysis results in enhanced memory system"""
        if not self.memory_system:
            return

        try:
            await self.memory_system.store_enhanced_memory(
                content={
                    "insights": insights,
                    "metrics": metrics,
                    "recommendations": recommendations,
                    "analysis_timestamp": datetime.now().isoformat(),
                },
                context={
                    "type": "self_insight",
                    "source": "introspector_plugin",
                    "analysis_scope": "codebase_analysis",
                },
                tags=["self_insight", "introspection", "code_analysis", "autonomous"],
                importance=0.8,
            )
            print("📝 Stored introspection insights in memory")

        except Exception as e:
            print(f"[WARN] Failed to store insights in memory: {e}")

    async def get_historical_insights(
        self, days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """Retrieve historical insights for trend analysis"""
        if not self.memory_system:
            return []

        try:
            memories = await self.memory_system.get_memories_by_tags(
                ["self_insight", "introspection"], limit=50
            )

            # Filter by date and return insights
            cutoff_date = datetime.now().timestamp() - (days_back * 24 * 60 * 60)
            recent_insights = []

            for memory in memories:
                created_at = memory.get("created_at", "")
                if (
                    created_at
                    and datetime.fromisoformat(
                        created_at.replace("Z", "+00:00")
                    ).timestamp()
                    > cutoff_date
                ):
                    content = memory.get("content", {})
                    if "insights" in content:
                        recent_insights.extend(content["insights"])

            return recent_insights

        except Exception as e:
            print(f"[WARN] Failed to retrieve historical insights: {e}")
            return []


# Plugin interface functions
async def main(input_data: Any, **kwargs) -> Dict[str, Any]:
    """Main plugin entry point"""
    plugin = IntrospectorPlugin(kwargs.get("memory_system"))

    if isinstance(input_data, dict):
        target_files = input_data.get("target_files", [])
        analysis_depth = input_data.get("analysis_depth", "medium")
    else:
        # Fallback for simple string input
        target_files = [str(input_data)] if input_data else []
        analysis_depth = "medium"

    return await plugin.main(target_files, analysis_depth)
