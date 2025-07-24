#!/usr/bin/env python3
"""
🧩 Enhanced Plugin Capability Extraction System
==============================================

Advanced system for extracting detailed plugin capabilities, metadata,
and creating semantic plugin profiles for better AI integration.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class PluginCapabilityExtractor:
    """
    Enhanced plugin capability extraction with semantic analysis
    and AI-native metadata generation.
    """

    def __init__(self):
        self.capability_patterns = {
            "file_operations": [
                r"open\s*\(", r"read\s*\(", r"write\s*\(", r"save\s*\(",
                r"create\s*\(", r"delete\s*\(", r"copy\s*\(", r"move\s*\("
            ],
            "data_processing": [
                r"process\s*\(", r"transform\s*\(", r"analyze\s*\(",
                r"filter\s*\(", r"sort\s*\(", r"group\s*\(", r"aggregate\s*\("
            ],
            "communication": [
                r"send\s*\(", r"receive\s*\(", r"request\s*\(", r"response\s*\(",
                r"api\s*\(", r"http\s*\(", r"socket\s*\("
            ],
            "automation": [
                r"schedule\s*\(", r"execute\s*\(", r"run\s*\(", r"trigger\s*\(",
                r"workflow\s*\(", r"batch\s*\(", r"pipeline\s*\("
            ],
            "analysis": [
                r"scan\s*\(", r"detect\s*\(", r"classify\s*\(", r"predict\s*\(",
                r"evaluate\s*\(", r"measure\s*\(", r"monitor\s*\("
            ],
            "generation": [
                r"generate\s*\(", r"create\s*\(", r"build\s*\(", r"make\s*\(",
                r"produce\s*\(", r"synthesize\s*\(", r"render\s*\("
            ]
        }

        self.confidence_factors = {
            "has_docstring": 0.1,
            "has_type_hints": 0.15,
            "has_error_handling": 0.1,
            "has_tests": 0.2,
            "function_count": 0.05,  # per function
            "line_count": 0.01,  # per 100 lines
            "has_main_function": 0.1,
            "imports_quality": 0.15
        }

    def extract_enhanced_metadata(self, plugin_path: str) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from a plugin file.

        Returns:
            Enhanced metadata dict with capabilities, confidence, tags, etc.
        """
        try:
            with open(plugin_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return self._create_error_metadata(plugin_path, "Failed to read file")

        plugin_name = Path(plugin_path).stem

        # Basic extraction
        metadata = {
            "name": plugin_name,
            "file_path": plugin_path,
            "size_bytes": len(content.encode('utf-8')),
            "line_count": len(content.splitlines()),
            "extraction_time": datetime.utcnow().isoformat(),
        }

        # Extract detailed capabilities
        metadata["capabilities"] = self._extract_capabilities(content)
        metadata["functions"] = self._extract_functions(content)
        metadata["imports"] = self._extract_imports(content)
        metadata["tags"] = self._generate_tags(content, metadata["capabilities"])
        metadata["description"] = self._extract_description(content)
        metadata["category"] = self._determine_category(metadata["capabilities"], metadata["tags"])

        # Calculate confidence score
        metadata["confidence_score"] = self._calculate_confidence(content, metadata)

        # Add usage and performance placeholders
        metadata["usage_count"] = 0
        metadata["last_used"] = None
        metadata["average_execution_time"] = 0.0
        metadata["success_rate"] = 1.0
        metadata["memory_usage"] = 0

        # AI recommendations
        metadata["lyrixa_recommended"] = metadata["confidence_score"] > 0.8
        metadata["complexity_level"] = self._assess_complexity(content, metadata)
        metadata["collaboration_potential"] = self._assess_collaboration_potential(metadata["capabilities"])

        return metadata

    def _extract_capabilities(self, content: str) -> List[str]:
        """Extract capabilities by analyzing code patterns"""
        capabilities = []

        for capability, patterns in self.capability_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    capabilities.append(capability)
                    break

        # Additional semantic analysis
        if "class " in content:
            capabilities.append("object_oriented")
        if "async def " in content:
            capabilities.append("asynchronous")
        if "import requests" in content or "import urllib" in content:
            capabilities.append("web_integration")
        if "import json" in content:
            capabilities.append("json_processing")
        if "import sqlite3" in content or "import mysql" in content:
            capabilities.append("database_integration")

        return list(set(capabilities))  # Remove duplicates

    def _extract_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract function information"""
        functions = []

        # Find all function definitions
        function_pattern = r'def\s+(\w+)\s*\([^)]*\)(?:\s*->\s*[^:]+)?:'
        matches = re.finditer(function_pattern, content)

        for match in matches:
            func_name = match.group(1)
            func_start = match.start()

            # Try to extract docstring
            func_content = content[func_start:]
            docstring_match = re.search(r'"""([^"]+)"""', func_content[:500])
            docstring = docstring_match.group(1).strip() if docstring_match else ""

            functions.append({
                "name": func_name,
                "has_docstring": bool(docstring),
                "docstring": docstring[:200] + "..." if len(docstring) > 200 else docstring,
                "is_private": func_name.startswith("_"),
                "is_main": func_name == "main"
            })

        return functions

    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements"""
        imports = []

        # Standard imports
        import_pattern = r'import\s+([^\s\n]+)'
        from_pattern = r'from\s+([^\s\n]+)\s+import'

        for match in re.finditer(import_pattern, content):
            imports.append(match.group(1))

        for match in re.finditer(from_pattern, content):
            imports.append(match.group(1))

        return list(set(imports))

    def _extract_description(self, content: str) -> str:
        """Extract plugin description from docstring or comments"""
        # Try module docstring first
        module_docstring = re.search(r'^"""([^"]+)"""', content, re.MULTILINE)
        if module_docstring:
            return module_docstring.group(1).strip()

        # Try single-line module docstring
        module_docstring = re.search(r"^'''([^']+)'''", content, re.MULTILINE)
        if module_docstring:
            return module_docstring.group(1).strip()

        # Try comments at the top
        lines = content.splitlines()
        description_lines = []
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line.startswith("#") and not line.startswith("#!/"):
                description_lines.append(line[1:].strip())
            elif line and not line.startswith("#"):
                break

        if description_lines:
            return " ".join(description_lines)

        return "No description available"

    def _generate_tags(self, content: str, capabilities: List[str]) -> List[str]:
        """Generate semantic tags based on content analysis"""
        tags = []

        # Tag based on capabilities
        capability_to_tags = {
            "file_operations": ["file", "io", "storage"],
            "data_processing": ["data", "processing", "transformation"],
            "communication": ["network", "api", "communication"],
            "automation": ["automation", "workflow", "scheduling"],
            "analysis": ["analysis", "monitoring", "detection"],
            "generation": ["generation", "creation", "synthesis"]
        }

        for capability in capabilities:
            if capability in capability_to_tags:
                tags.extend(capability_to_tags[capability])

        # Content-based tags
        content_lower = content.lower()
        if "ai" in content_lower or "ml" in content_lower or "machine learning" in content_lower:
            tags.append("ai")
        if "gui" in content_lower or "tkinter" in content_lower or "pyside" in content_lower:
            tags.append("gui")
        if "web" in content_lower or "flask" in content_lower or "django" in content_lower:
            tags.append("web")
        if "database" in content_lower or "sql" in content_lower:
            tags.append("database")

        return list(set(tags))

    def _determine_category(self, capabilities: List[str], tags: List[str]) -> str:
        """Determine the primary category for the plugin"""
        category_scores = {
            "utility": 0,
            "analysis": 0,
            "automation": 0,
            "integration": 0,
            "enhancement": 0,
            "generation": 0
        }

        # Score based on capabilities
        capability_scoring = {
            "file_operations": {"utility": 2},
            "data_processing": {"analysis": 2, "utility": 1},
            "communication": {"integration": 2},
            "automation": {"automation": 3},
            "analysis": {"analysis": 3},
            "generation": {"generation": 3}
        }

        for capability in capabilities:
            if capability in capability_scoring:
                for category, score in capability_scoring[capability].items():
                    category_scores[category] += score

        # Score based on tags
        tag_scoring = {
            "ai": {"enhancement": 2, "analysis": 1},
            "gui": {"utility": 2},
            "web": {"integration": 2},
            "database": {"integration": 1, "utility": 1}
        }

        for tag in tags:
            if tag in tag_scoring:
                for category, score in tag_scoring[tag].items():
                    category_scores[category] += score

        # Return category with highest score
        if not any(category_scores.values()):
            return "utility"
        return max(category_scores.keys(), key=lambda k: category_scores[k])

    def _calculate_confidence(self, content: str, metadata: Dict[str, Any]) -> float:
        """Calculate confidence score based on code quality indicators"""
        confidence = 0.5  # Base confidence

        # Quality indicators
        if '"""' in content or "'''" in content:
            confidence += self.confidence_factors["has_docstring"]

        if "->" in content or ": str" in content or ": int" in content:
            confidence += self.confidence_factors["has_type_hints"]

        if "try:" in content and "except" in content:
            confidence += self.confidence_factors["has_error_handling"]

        if "test_" in content or "unittest" in content or "pytest" in content:
            confidence += self.confidence_factors["has_tests"]

        # Function count bonus
        function_count = len(metadata.get("functions", []))
        confidence += min(function_count * self.confidence_factors["function_count"], 0.3)

        # Line count bonus (quality assumption for longer, well-structured code)
        line_count = metadata.get("line_count", 0)
        confidence += min((line_count // 100) * self.confidence_factors["line_count"], 0.2)

        # Main function presence
        functions = metadata.get("functions", [])
        if any(f.get("is_main", False) for f in functions):
            confidence += self.confidence_factors["has_main_function"]

        # Import quality (standard library vs external dependencies)
        imports = metadata.get("imports", [])
        standard_libs = ["os", "sys", "json", "re", "datetime", "pathlib", "typing"]
        quality_ratio = sum(1 for imp in imports if any(std in imp for std in standard_libs)) / max(len(imports), 1)
        confidence += quality_ratio * self.confidence_factors["imports_quality"]

        return min(confidence, 1.0)  # Cap at 1.0

    def _assess_complexity(self, content: str, metadata: Dict[str, Any]) -> str:
        """Assess the complexity level of the plugin"""
        function_count = len(metadata.get("functions", []))
        line_count = metadata.get("line_count", 0)
        capabilities_count = len(metadata.get("capabilities", []))

        complexity_score = 0
        complexity_score += min(function_count / 5, 1.0)  # Normalize to 0-1
        complexity_score += min(line_count / 500, 1.0)    # Normalize to 0-1
        complexity_score += min(capabilities_count / 8, 1.0)  # Normalize to 0-1

        # Check for advanced patterns
        if "class " in content:
            complexity_score += 0.2
        if "async " in content:
            complexity_score += 0.3
        if "decorator" in content or "@" in content:
            complexity_score += 0.2

        complexity_score /= 3  # Average the scores

        if complexity_score < 0.3:
            return "simple"
        elif complexity_score < 0.7:
            return "moderate"
        else:
            return "complex"

    def _assess_collaboration_potential(self, capabilities: List[str]) -> float:
        """Assess how well this plugin can collaborate with others"""
        collaboration_indicators = {
            "communication": 0.3,
            "data_processing": 0.2,
            "file_operations": 0.1,
            "automation": 0.2,
            "analysis": 0.15,
            "generation": 0.15
        }

        potential = 0.0
        for capability in capabilities:
            if capability in collaboration_indicators:
                potential += collaboration_indicators[capability]

        return min(potential, 1.0)

    def _create_error_metadata(self, plugin_path: str, error_msg: str) -> Dict[str, Any]:
        """Create minimal metadata for plugins that couldn't be analyzed"""
        return {
            "name": Path(plugin_path).stem,
            "file_path": plugin_path,
            "error": error_msg,
            "confidence_score": 0.0,
            "capabilities": [],
            "category": "unknown",
            "tags": ["error"],
            "description": f"Plugin analysis failed: {error_msg}",
            "extraction_time": datetime.utcnow().isoformat()
        }

    def bulk_extract_plugins(self, plugins_directory: str) -> List[Dict[str, Any]]:
        """Extract metadata for all plugins in a directory"""
        plugins_dir = Path(plugins_directory)
        if not plugins_dir.exists():
            return []

        all_metadata = []

        for plugin_file in plugins_dir.glob("*.py"):
            if plugin_file.name.startswith("__"):
                continue  # Skip __init__.py and __pycache__

            metadata = self.extract_enhanced_metadata(str(plugin_file))
            all_metadata.append(metadata)

        # Sort by confidence score descending
        all_metadata.sort(key=lambda x: x.get("confidence_score", 0), reverse=True)

        return all_metadata


def demo_capability_extraction():
    """Demonstrate the enhanced capability extraction system"""
    extractor = PluginCapabilityExtractor()

    # Find plugins directory
    plugins_dirs = [
        "Aetherra/plugins",
        "src/aetherra/plugins",
        "lyrixa_plugins",
        "plugins",
        "sdk/plugins"
    ]

    plugins_dir = None
    for directory in plugins_dirs:
        if os.path.exists(directory):
            plugins_dir = directory
            break

    if not plugins_dir:
        print("❌ No plugins directory found")
        return

    print(f"🧩 Extracting capabilities from: {plugins_dir}")

    # Extract all plugin metadata
    all_plugins = extractor.bulk_extract_plugins(plugins_dir)

    print(f"\n✅ Analyzed {len(all_plugins)} plugins")
    print("\n🏆 Top Plugins by Confidence:")

    for i, plugin in enumerate(all_plugins[:5], 1):
        print(f"\n{i}. {plugin['name']}")
        print(f"   Category: {plugin['category']}")
        print(f"   Confidence: {plugin['confidence_score']:.2f}")
        print(f"   Capabilities: {', '.join(plugin['capabilities'][:3])}...")
        print(f"   Tags: {', '.join(plugin['tags'][:3])}...")
        print(f"   Description: {plugin['description'][:60]}...")

    # Save detailed results
    output_file = "enhanced_plugin_metadata.json"
    with open(output_file, 'w') as f:
        json.dump(all_plugins, f, indent=2)

    print(f"\n💾 Detailed metadata saved to: {output_file}")

    return all_plugins


if __name__ == "__main__":
    demo_capability_extraction()
