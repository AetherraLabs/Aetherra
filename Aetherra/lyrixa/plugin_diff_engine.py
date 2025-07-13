#!/usr/bin/env python3
"""
🔧 PLUGIN DIFF ENGINE
====================

Analyzes plugins and generates improvement suggestions automatically.
Part of Lyrixa's self-improvement system.
"""

import asyncio
import hashlib
import json
import logging
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PluginAnalysis:
    """Represents analysis results for a plugin"""

    def __init__(self, plugin_id: str, plugin_path: str):
        self.plugin_id = plugin_id
        self.plugin_path = plugin_path
        self.code_content = ""
        self.metadata = {}
        self.metrics = {}
        self.issues = []
        self.suggestions = []
        self.confidence_score = 0.0
        self.last_modified = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis to dictionary format"""
        return {
            "plugin_id": self.plugin_id,
            "plugin_path": self.plugin_path,
            "metrics": self.metrics,
            "issues": self.issues,
            "suggestions": self.suggestions,
            "confidence_score": self.confidence_score,
            "last_modified": self.last_modified.isoformat()
            if self.last_modified
            else None,
            "analysis_timestamp": datetime.now().isoformat(),
        }


class ImprovementProposal:
    """Represents a specific improvement proposal for a plugin"""

    def __init__(self, plugin_id: str):
        self.plugin_id = plugin_id
        self.proposed_change = ""
        self.diff_summary = ""
        self.impact = ""
        self.risk_level = "medium"  # low, medium, high
        self.auto_apply = False
        self.confidence = 0.0
        self.suggested_code = ""
        self.reasoning = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert proposal to dictionary format"""
        return {
            "plugin_id": self.plugin_id,
            "proposed_change": self.proposed_change,
            "diff_summary": self.diff_summary,
            "impact": self.impact,
            "risk_level": self.risk_level,
            "auto_apply": self.auto_apply,
            "confidence": self.confidence,
            "suggested_code": self.suggested_code,
            "reasoning": self.reasoning,
            "created_at": datetime.now().isoformat(),
        }


class PluginDiffEngine:
    """
    🔧 Plugin Diff Engine

    Analyzes plugins for improvement opportunities and generates
    specific suggestions with diff patches.
    """

    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.plugin_directories = [
            self.workspace_path / "Aetherra" / "plugins",
            self.workspace_path / "plugins",
            self.workspace_path / "src" / "plugins",
        ]
        self.analysis_cache = {}
        self.improvement_history = []

    def discover_plugins(self) -> List[Tuple[str, Path]]:
        """Discover all plugin files in the workspace"""
        plugins = []

        for plugin_dir in self.plugin_directories:
            if not plugin_dir.exists():
                continue

            # Find .py and .aether files
            for ext in ["*.py", "*.aether"]:
                for plugin_file in plugin_dir.glob(ext):
                    if plugin_file.name.startswith("__"):
                        continue  # Skip __init__.py and similar

                    plugin_id = plugin_file.stem
                    plugins.append((plugin_id, plugin_file))

        return plugins

    def analyze_plugin(self, plugin_id: str, plugin_path: Path) -> PluginAnalysis:
        """Perform comprehensive analysis of a plugin"""
        analysis = PluginAnalysis(plugin_id, str(plugin_path))

        try:
            # Read plugin content
            analysis.code_content = plugin_path.read_text(encoding="utf-8")
            analysis.last_modified = datetime.fromtimestamp(plugin_path.stat().st_mtime)

            # Extract metadata if available
            analysis.metadata = self._extract_metadata(analysis.code_content)

            # Calculate metrics
            analysis.metrics = self._calculate_metrics(analysis.code_content)

            # Identify issues
            analysis.issues = self._identify_issues(analysis.code_content)

            # Generate suggestions
            analysis.suggestions = self._generate_suggestions(
                analysis.code_content, analysis.issues
            )

            # Calculate overall confidence score
            analysis.confidence_score = self._calculate_confidence_score(analysis)

            logger.info(
                f"✅ Analyzed plugin: {plugin_id} (score: {analysis.confidence_score:.2f})"
            )

        except Exception as e:
            logger.error(f"❌ Failed to analyze plugin {plugin_id}: {e}")
            analysis.issues.append(f"Analysis error: {e}")

        return analysis

    def _extract_metadata(self, code: str) -> Dict[str, Any]:
        """Extract metadata from plugin code"""
        metadata = {}

        # Look for docstring metadata
        docstring_match = re.search(r'"""(.*?)"""', code, re.DOTALL)
        if docstring_match:
            metadata["description"] = docstring_match.group(1).strip()

        # Look for JSON metadata in comments
        json_match = re.search(r"#\s*METADATA:\s*({.*?})", code, re.DOTALL)
        if json_match:
            try:
                metadata.update(json.loads(json_match.group(1)))
            except json.JSONDecodeError:
                pass

        # Extract function and class names
        metadata["functions"] = re.findall(r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)", code)
        metadata["classes"] = re.findall(r"class\s+([a-zA-Z_][a-zA-Z0-9_]*)", code)

        return metadata

    def _calculate_metrics(self, code: str) -> Dict[str, Any]:
        """Calculate various code metrics"""
        lines = code.split("\n")

        return {
            "total_lines": len(lines),
            "code_lines": len(
                [l for l in lines if l.strip() and not l.strip().startswith("#")]
            ),
            "comment_lines": len([l for l in lines if l.strip().startswith("#")]),
            "function_count": len(re.findall(r"def\s+[a-zA-Z_]", code)),
            "class_count": len(re.findall(r"class\s+[a-zA-Z_]", code)),
            "complexity_score": self._estimate_complexity(code),
            "has_error_handling": "try:" in code or "except" in code,
            "has_async": "async" in code or "await" in code,
            "has_logging": "logger" in code or "logging" in code,
            "has_docstrings": '"""' in code or "'''" in code,
        }

    def _estimate_complexity(self, code: str) -> float:
        """Estimate code complexity based on various factors"""
        complexity = 0

        # Count control structures
        complexity += len(re.findall(r"\b(if|for|while|try|except|with)\b", code))

        # Count nested structures (rough estimate)
        indentation_levels = []
        for line in code.split("\n"):
            if line.strip():
                indent = len(line) - len(line.lstrip())
                indentation_levels.append(indent)

        if indentation_levels:
            complexity += max(indentation_levels) / 4  # Assume 4-space indents

        return complexity

    def _identify_issues(self, code: str) -> List[Dict[str, Any]]:
        """Identify potential issues in the plugin code"""
        issues = []

        # Check for common issues
        if "TODO" in code or "FIXME" in code:
            issues.append(
                {
                    "type": "todo",
                    "severity": "low",
                    "description": "Contains TODO or FIXME comments",
                    "suggestion": "Complete pending tasks",
                }
            )

        if not ("try:" in code or "except" in code):
            issues.append(
                {
                    "type": "error_handling",
                    "severity": "medium",
                    "description": "No error handling detected",
                    "suggestion": "Add try/except blocks for robustness",
                }
            )

        if not ("logger" in code or "logging" in code or "print" in code):
            issues.append(
                {
                    "type": "logging",
                    "severity": "low",
                    "description": "No logging or output detected",
                    "suggestion": "Add logging for better debugging",
                }
            )

        # Check for inefficient patterns
        if "time.sleep(" in code and "async" not in code:
            issues.append(
                {
                    "type": "blocking_sleep",
                    "severity": "medium",
                    "description": "Uses blocking sleep() calls",
                    "suggestion": "Consider using async/await with asyncio.sleep()",
                }
            )

        # Check for hardcoded values
        hardcoded_paths = re.findall(r'["\'][C-Z]:\\[^"\']*["\']', code)
        if hardcoded_paths:
            issues.append(
                {
                    "type": "hardcoded_paths",
                    "severity": "medium",
                    "description": f"Contains hardcoded paths: {hardcoded_paths[:3]}",
                    "suggestion": "Use relative paths or configuration",
                }
            )

        return issues

    def _generate_suggestions(
        self, code: str, issues: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Generate specific improvement suggestions"""
        suggestions = []

        for issue in issues:
            if issue["type"] == "error_handling":
                suggestions.append(
                    {
                        "type": "add_error_handling",
                        "priority": "high",
                        "description": "Add comprehensive error handling",
                        "implementation": "Wrap main logic in try/except blocks",
                    }
                )

            elif issue["type"] == "logging":
                suggestions.append(
                    {
                        "type": "add_logging",
                        "priority": "medium",
                        "description": "Add logging for better observability",
                        "implementation": "Import logging and add logger.info/error calls",
                    }
                )

            elif issue["type"] == "blocking_sleep":
                suggestions.append(
                    {
                        "type": "async_conversion",
                        "priority": "high",
                        "description": "Convert to async for better performance",
                        "implementation": "Add async/await and use asyncio.sleep()",
                    }
                )

        # Performance suggestions
        if "for" in code and "append" in code:
            suggestions.append(
                {
                    "type": "list_comprehension",
                    "priority": "low",
                    "description": "Consider list comprehensions for better performance",
                    "implementation": "Replace for loops with list comprehensions where appropriate",
                }
            )

        return suggestions

    def _calculate_confidence_score(self, analysis: PluginAnalysis) -> float:
        """Calculate overall confidence score for the plugin"""
        score = 0.5  # Base score

        # Positive factors
        if analysis.metrics.get("has_error_handling"):
            score += 0.2
        if analysis.metrics.get("has_logging"):
            score += 0.1
        if analysis.metrics.get("has_docstrings"):
            score += 0.1
        if analysis.metrics.get("has_async"):
            score += 0.1

        # Negative factors
        score -= len(analysis.issues) * 0.05

        # Complexity penalty
        complexity = analysis.metrics.get("complexity_score", 0)
        if complexity > 10:
            score -= 0.1

        return max(0.0, min(1.0, score))

    def generate_improvement_proposal(
        self, analysis: PluginAnalysis
    ) -> Optional[ImprovementProposal]:
        """Generate a specific improvement proposal based on analysis"""
        if analysis.confidence_score > 0.8:
            return None  # Plugin is already good

        # Find the highest priority issue
        high_priority_issues = [
            s for s in analysis.suggestions if s.get("priority") == "high"
        ]
        if not high_priority_issues:
            medium_priority_issues = [
                s for s in analysis.suggestions if s.get("priority") == "medium"
            ]
            if not medium_priority_issues:
                return None
            suggestion = medium_priority_issues[0]
        else:
            suggestion = high_priority_issues[0]

        proposal = ImprovementProposal(analysis.plugin_id)
        proposal.proposed_change = suggestion["description"]
        proposal.impact = "Improves " + suggestion["type"].replace("_", " ")
        proposal.reasoning = suggestion["implementation"]

        # Determine risk level and auto-apply
        if suggestion["type"] in ["add_logging", "add_error_handling"]:
            proposal.risk_level = "low"
            proposal.auto_apply = False  # Always require review for code changes
        elif suggestion["type"] == "async_conversion":
            proposal.risk_level = "medium"
            proposal.auto_apply = False
        else:
            proposal.risk_level = "low"
            proposal.auto_apply = False

        proposal.confidence = analysis.confidence_score

        # Generate improved code suggestion
        proposal.suggested_code = self._generate_improved_code(
            analysis.code_content, suggestion
        )
        proposal.diff_summary = self._generate_diff_summary(
            analysis.code_content, proposal.suggested_code
        )

        return proposal

    def _generate_improved_code(self, original_code: str, suggestion: Dict) -> str:
        """Generate improved version of the code"""
        # This is a simplified implementation
        # In a real system, this would use more sophisticated code transformation

        improved_code = original_code

        if suggestion["type"] == "add_error_handling":
            # Add basic error handling wrapper
            if "def main(" in improved_code:
                improved_code = improved_code.replace("def main(", "def main(")
                # Find main function and wrap its content
                # This is a simplified approach
                if 'if __name__ == "__main__":' in improved_code:
                    improved_code = improved_code.replace(
                        'if __name__ == "__main__":\n    main()',
                        """if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error running plugin: {e}")""",
                    )

        elif suggestion["type"] == "add_logging":
            # Add logging import and basic logging
            if "import logging" not in improved_code:
                improved_code = "import logging\n\n" + improved_code
                improved_code = improved_code.replace(
                    "def main(", "logger = logging.getLogger(__name__)\n\ndef main("
                )

        return improved_code

    def _generate_diff_summary(self, original: str, improved: str) -> str:
        """Generate a human-readable diff summary"""
        original_lines = original.split("\n")
        improved_lines = improved.split("\n")

        if len(improved_lines) > len(original_lines):
            added_lines = len(improved_lines) - len(original_lines)
            return f"+ Added {added_lines} lines (imports, error handling, logging)"
        elif len(improved_lines) < len(original_lines):
            removed_lines = len(original_lines) - len(improved_lines)
            return f"- Removed {removed_lines} lines (cleanup, optimization)"
        else:
            return "~ Modified existing lines (refactoring, improvements)"

    async def analyze_all_plugins(self) -> List[PluginAnalysis]:
        """Analyze all discovered plugins"""
        plugins = self.discover_plugins()
        analyses = []

        logger.info(f"🔍 Starting analysis of {len(plugins)} plugins...")

        for plugin_id, plugin_path in plugins:
            analysis = self.analyze_plugin(plugin_id, plugin_path)
            analyses.append(analysis)

            # Brief pause to prevent overwhelming the system
            await asyncio.sleep(0.1)

        return analyses

    async def generate_improvement_proposals(self) -> List[ImprovementProposal]:
        """Generate improvement proposals for all plugins"""
        analyses = await self.analyze_all_plugins()
        proposals = []

        for analysis in analyses:
            proposal = self.generate_improvement_proposal(analysis)
            if proposal:
                proposals.append(proposal)
                logger.info(
                    f"💡 Generated improvement proposal for {analysis.plugin_id}"
                )

        return proposals

    def save_analysis_report(
        self, analyses: List[PluginAnalysis], output_path: str = None
    ):
        """Save analysis report to file"""
        if output_path is None:
            output_path = self.workspace_path / "plugin_analysis_report.json"

        report = {
            "timestamp": datetime.now().isoformat(),
            "total_plugins": len(analyses),
            "analyses": [analysis.to_dict() for analysis in analyses],
            "summary": self._generate_summary(analyses),
        }

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"📊 Analysis report saved to {output_path}")

    def _generate_summary(self, analyses: List[PluginAnalysis]) -> Dict[str, Any]:
        """Generate summary statistics"""
        if not analyses:
            return {}

        confidence_scores = [a.confidence_score for a in analyses]
        issue_counts = [len(a.issues) for a in analyses]

        return {
            "average_confidence": sum(confidence_scores) / len(confidence_scores),
            "plugins_with_issues": len([a for a in analyses if a.issues]),
            "total_issues": sum(issue_counts),
            "plugins_needing_improvement": len(
                [a for a in analyses if a.confidence_score < 0.7]
            ),
            "high_quality_plugins": len(
                [a for a in analyses if a.confidence_score > 0.8]
            ),
        }


# Example usage and testing
if __name__ == "__main__":

    async def main():
        print("🔧 Plugin Diff Engine Test")
        print("=" * 30)

        # Initialize the engine
        workspace_path = Path(__file__).parent.parent
        engine = PluginDiffEngine(str(workspace_path))

        # Discover and analyze plugins
        plugins = engine.discover_plugins()
        print(f"📦 Discovered {len(plugins)} plugins")

        # Analyze a few plugins
        if plugins:
            sample_plugin = plugins[0]
            print(f"🔍 Analyzing sample plugin: {sample_plugin[0]}")

            analysis = engine.analyze_plugin(sample_plugin[0], sample_plugin[1])
            print(f"✅ Analysis complete - Confidence: {analysis.confidence_score:.2f}")
            print(f"🐛 Issues found: {len(analysis.issues)}")
            print(f"💡 Suggestions: {len(analysis.suggestions)}")

            # Generate improvement proposal
            proposal = engine.generate_improvement_proposal(analysis)
            if proposal:
                print(f"🚀 Improvement proposal generated:")
                print(f"   Change: {proposal.proposed_change}")
                print(f"   Impact: {proposal.impact}")
                print(f"   Risk: {proposal.risk_level}")

        print("🎉 Plugin Diff Engine test complete!")

    asyncio.run(main())
