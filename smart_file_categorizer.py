#!/usr/bin/env python3
"""
🧠 SMART FILE CATEGORIZER
========================

Intelligent analysis tool to categorize files into:
- Aetherra Core (foundational OS systems)
- Lyrixa (personality/cognitive systems)

This tool analyzes code content to make smart categorization decisions.
"""

import ast
import logging
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SmartFileCategorizer:
    """
    Intelligent file categorizer using code analysis
    """

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)

        # Keywords that indicate Aetherra Core functionality
        self.aetherra_keywords = {
            "plugin",
            "kernel",
            "runtime",
            "security",
            "scheduler",
            "memory_kernel",
            "qfac",
            "quantum",
            "fractal",
            "compression",
            "goal_scheduler",
            "orchestration",
            "sandbox",
            "permissions",
            "authentication",
            "monitoring",
            "diagnostics",
            "api_gateway",
            "websocket",
            "integration",
            "bridge",
            "system_monitor",
            "performance",
            "health_check",
            "audit_log",
            "access_control",
        }

        # Keywords that indicate Lyrixa functionality
        self.lyrixa_keywords = {
            "personality",
            "identity",
            "emotion",
            "mood",
            "conversation",
            "chat",
            "dialogue",
            "response",
            "prompt",
            "narrative",
            "reflection",
            "introspection",
            "self_awareness",
            "consciousness",
            "empathy",
            "social",
            "learning",
            "curiosity",
            "belief",
            "thought",
            "feeling",
            "experience",
            "memory_introspection",
            "night_cycle",
            "contradiction",
            "coherence",
            "trait",
            "communication_style",
            "behavioral",
            "adaptive",
        }

        # File patterns for categorization
        self.aetherra_patterns = [
            r"plugin.*manager",
            r"kernel",
            r"runtime",
            r"security",
            r"scheduler",
            r"monitoring",
            r"integration",
            r"api.*gateway",
            r"bridge.*(?!lyrixa)",
            r"system.*monitor",
        ]

        self.lyrixa_patterns = [
            r"personality",
            r"identity",
            r"emotion",
            r"conversation",
            r"chat",
            r"reflection",
            r"introspect",
            r"narrative",
            r"prompt.*engine",
            r"lyrixa.*(?:agent|core|engine)",
        ]

    def analyze_file_content(self, file_path: Path) -> Dict:
        """Analyze file content for categorization clues"""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")

            analysis = {
                "aetherra_score": 0,
                "lyrixa_score": 0,
                "keywords_found": {"aetherra": set(), "lyrixa": set()},
                "imports": set(),
                "classes": set(),
                "functions": set(),
            }

            # Analyze Python AST if it's a Python file
            if file_path.suffix == ".py":
                try:
                    tree = ast.parse(content)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                analysis["imports"].add(alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                analysis["imports"].add(node.module)
                        elif isinstance(node, ast.ClassDef):
                            analysis["classes"].add(node.name)
                        elif isinstance(node, ast.FunctionDef):
                            analysis["functions"].add(node.name)

                except SyntaxError:
                    pass  # Skip files with syntax errors

            # Keyword analysis
            content_lower = content.lower()

            for keyword in self.aetherra_keywords:
                if keyword in content_lower:
                    analysis["aetherra_score"] += content_lower.count(keyword)
                    analysis["keywords_found"]["aetherra"].add(keyword)

            for keyword in self.lyrixa_keywords:
                if keyword in content_lower:
                    analysis["lyrixa_score"] += content_lower.count(keyword)
                    analysis["keywords_found"]["lyrixa"].add(keyword)

            # Pattern analysis
            for pattern in self.aetherra_patterns:
                if re.search(pattern, content_lower):
                    analysis["aetherra_score"] += 5

            for pattern in self.lyrixa_patterns:
                if re.search(pattern, content_lower):
                    analysis["lyrixa_score"] += 5

            return analysis

        except Exception as e:
            logger.warning(f"Failed to analyze {file_path}: {e}")
            return {
                "aetherra_score": 0,
                "lyrixa_score": 0,
                "keywords_found": {"aetherra": set(), "lyrixa": set()},
            }

    def analyze_file_path(self, file_path: Path) -> Dict:
        """Analyze file path for categorization clues"""
        path_str = str(file_path).lower()

        analysis = {"aetherra_score": 0, "lyrixa_score": 0, "path_indicators": []}

        # Path-based scoring
        if any(
            part in path_str
            for part in ["kernel", "runtime", "security", "monitoring", "integration"]
        ):
            analysis["aetherra_score"] += 10
            analysis["path_indicators"].append("aetherra_path")

        if any(
            part in path_str
            for part in [
                "personality",
                "emotion",
                "conversation",
                "reflection",
                "lyrixa",
            ]
        ):
            analysis["lyrixa_score"] += 10
            analysis["path_indicators"].append("lyrixa_path")

        # Special cases
        if "bridge" in path_str and "lyrixa" not in path_str:
            analysis["aetherra_score"] += 5  # Integration bridges are Aetherra

        if file_path.name.startswith("prompt_") or "chat" in path_str:
            analysis["lyrixa_score"] += 8  # Prompt/chat is Lyrixa

        return analysis

    def categorize_file(self, file_path: Path) -> Tuple[str, float, Dict]:
        """Categorize a single file"""
        content_analysis = self.analyze_file_content(file_path)
        path_analysis = self.analyze_file_path(file_path)

        # Combine scores
        total_aetherra = (
            content_analysis["aetherra_score"] + path_analysis["aetherra_score"]
        )
        total_lyrixa = content_analysis["lyrixa_score"] + path_analysis["lyrixa_score"]

        # Special case overrides
        file_name = file_path.name.lower()

        # Force Aetherra categorization
        if any(
            term in file_name
            for term in ["plugin_manager", "kernel", "scheduler", "security", "monitor"]
        ):
            total_aetherra += 20

        # Force Lyrixa categorization
        if any(
            term in file_name
            for term in [
                "personality",
                "identity",
                "emotion",
                "conversation",
                "prompt_engine",
            ]
        ):
            total_lyrixa += 20

        # Determine category
        if total_aetherra > total_lyrixa:
            category = "aetherra"
            confidence = (
                total_aetherra / (total_aetherra + total_lyrixa)
                if (total_aetherra + total_lyrixa) > 0
                else 0.5
            )
        elif total_lyrixa > total_aetherra:
            category = "lyrixa"
            confidence = (
                total_lyrixa / (total_aetherra + total_lyrixa)
                if (total_aetherra + total_lyrixa) > 0
                else 0.5
            )
        else:
            category = "unclear"
            confidence = 0.5

        details = {
            "aetherra_score": total_aetherra,
            "lyrixa_score": total_lyrixa,
            "content_analysis": content_analysis,
            "path_analysis": path_analysis,
        }

        return category, confidence, details

    def scan_project(self) -> Dict:
        """Scan entire project and categorize files"""
        logger.info("🔍 Scanning project for file categorization...")

        results = {
            "aetherra": [],
            "lyrixa": [],
            "unclear": [],
            "databases": [],
            "config": [],
        }

        # Scan both Aetherra and Aetherra_v2 directories
        for scan_dir in ["Aetherra", "Aetherra_v2"]:
            scan_path = self.project_root / scan_dir
            if not scan_path.exists():
                continue

            for file_path in scan_path.rglob("*"):
                if not file_path.is_file():
                    continue

                # Skip certain file types
                if file_path.suffix in [".pyc", ".log", ".tmp"]:
                    continue

                # Categorize databases separately
                if file_path.suffix == ".db":
                    results["databases"].append(
                        {
                            "path": str(file_path.relative_to(self.project_root)),
                            "name": file_path.name,
                        }
                    )
                    continue

                # Categorize config files
                if file_path.suffix in [".json", ".yaml", ".yml", ".toml", ".ini"]:
                    results["config"].append(
                        {
                            "path": str(file_path.relative_to(self.project_root)),
                            "name": file_path.name,
                        }
                    )
                    continue

                # Categorize code files
                if file_path.suffix in [".py", ".js", ".md"]:
                    category, confidence, details = self.categorize_file(file_path)

                    file_info = {
                        "path": str(file_path.relative_to(self.project_root)),
                        "name": file_path.name,
                        "confidence": confidence,
                        "details": details,
                    }

                    results[category].append(file_info)

        # Sort by confidence (highest first)
        for category in ["aetherra", "lyrixa", "unclear"]:
            results[category].sort(key=lambda x: x["confidence"], reverse=True)

        return results

    def generate_categorization_report(self, results: Dict) -> None:
        """Generate detailed categorization report"""
        report_content = f"""# 🧠 SMART FILE CATEGORIZATION REPORT

Generated: {Path(__file__).parent}

## 📊 SUMMARY

- **Aetherra Core Files**: {len(results["aetherra"])}
- **Lyrixa Files**: {len(results["lyrixa"])}
- **Unclear Files**: {len(results["unclear"])}
- **Database Files**: {len(results["databases"])}
- **Config Files**: {len(results["config"])}

---

## 🧬 AETHERRA CORE FILES

These files contain foundational OS systems and should go to Aetherra/:

"""

        for file_info in results["aetherra"][:20]:  # Top 20
            report_content += f"- **{file_info['name']}** ({file_info['confidence']:.2f}) - `{file_info['path']}`\n"
            if file_info["details"]["content_analysis"]["keywords_found"]["aetherra"]:
                keywords = ", ".join(
                    list(
                        file_info["details"]["content_analysis"]["keywords_found"][
                            "aetherra"
                        ]
                    )[:5]
                )
                report_content += f"  - Keywords: {keywords}\n"

        report_content += f"""

## 🧠 LYRIXA FILES

These files contain personality/cognitive systems and should go to Lyrixa/:

"""

        for file_info in results["lyrixa"][:20]:  # Top 20
            report_content += f"- **{file_info['name']}** ({file_info['confidence']:.2f}) - `{file_info['path']}`\n"
            if file_info["details"]["content_analysis"]["keywords_found"]["lyrixa"]:
                keywords = ", ".join(
                    list(
                        file_info["details"]["content_analysis"]["keywords_found"][
                            "lyrixa"
                        ]
                    )[:5]
                )
                report_content += f"  - Keywords: {keywords}\n"

        report_content += f"""

## ❓ UNCLEAR FILES

These files need manual review:

"""

        for file_info in results["unclear"][:10]:  # Top 10
            report_content += f"- **{file_info['name']}** - `{file_info['path']}`\n"

        report_content += f"""

## 💾 DATABASE FILES

"""
        for db_info in results["databases"]:
            report_content += f"- `{db_info['path']}`\n"

        # Save report
        report_path = self.project_root / "smart_categorization_report.md"
        report_path.write_text(report_content, encoding="utf-8")

        logger.info(f"📊 Categorization report saved: {report_path}")

        # Print summary
        print(f"""
🧠 SMART CATEGORIZATION COMPLETE!

📊 RESULTS:
🧬 Aetherra Core: {len(results["aetherra"])} files
🧠 Lyrixa: {len(results["lyrixa"])} files
❓ Unclear: {len(results["unclear"])} files
💾 Databases: {len(results["databases"])} files

📋 Report saved: {report_path}

🎯 HIGH CONFIDENCE RECOMMENDATIONS:

🧬 AETHERRA CORE (Top 5):""")

        for file_info in results["aetherra"][:5]:
            print(f"   ✅ {file_info['name']} ({file_info['confidence']:.2f})")

        print(f"""
🧠 LYRIXA (Top 5):""")

        for file_info in results["lyrixa"][:5]:
            print(f"   ✅ {file_info['name']} ({file_info['confidence']:.2f})")


def main():
    """Main execution"""
    project_root = Path(__file__).parent

    categorizer = SmartFileCategorizer(str(project_root))
    results = categorizer.scan_project()
    categorizer.generate_categorization_report(results)


if __name__ == "__main__":
    main()
