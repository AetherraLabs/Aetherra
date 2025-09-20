#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Advanced Project Intelligence System
Provides comprehensive file and directory analysis with deep insights
"""

# Standard library imports
import ast
import hashlib
import json
import mimetypes
import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path


class AdvancedProjectAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.file_intelligence = {}
        self.directory_intelligence = {}
        self.dependency_map = defaultdict(set)
        self.import_graph = defaultdict(set)
        self.file_relationships = defaultdict(list)
        self.code_metrics = {}

    def analyze_file_content(self, filepath):
        """Deep analysis of file content and purpose"""
        file_path = Path(filepath)
        analysis = {
            "path": str(filepath),
            "name": file_path.name,
            "extension": file_path.suffix,
            "size": file_path.stat().st_size if file_path.exists() else 0,
            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            if file_path.exists()
            else None,
            "mime_type": mimetypes.guess_type(str(filepath))[0],
            "hash": self.calculate_file_hash(filepath),
            "purpose": "Unknown",
            "description": "",
            "dependencies": [],
            "exports": [],
            "complexity": 0,
            "usage_patterns": [],
            "quality_metrics": {},
        }

        try:
            # Read file content for analysis
            with open(filepath, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            analysis["line_count"] = len(content.split("\n"))
            analysis["char_count"] = len(content)

            # Analyze by file type
            if filepath.suffix == ".py":
                analysis.update(self.analyze_python_file(filepath, content))
            elif filepath.suffix in [".js", ".jsx", ".ts", ".tsx"]:
                analysis.update(self.analyze_javascript_file(filepath, content))
            elif filepath.suffix == ".md":
                analysis.update(self.analyze_markdown_file(filepath, content))
            elif filepath.suffix in [".json", ".yml", ".yaml"]:
                analysis.update(self.analyze_config_file(filepath, content))
            elif filepath.suffix in [".html", ".htm"]:
                analysis.update(self.analyze_html_file(filepath, content))
            elif filepath.suffix == ".css":
                analysis.update(self.analyze_css_file(filepath, content))
            else:
                analysis.update(self.analyze_generic_file(filepath, content))

            # Infer purpose from filename and content
            analysis["purpose"] = self.infer_file_purpose(filepath, content, analysis)

        except Exception as e:
            analysis["error"] = str(e)
            analysis["purpose"] = "Error reading file"

        return analysis

    def analyze_python_file(self, filepath, content):
        """Detailed Python file analysis"""
        analysis = {
            "language": "Python",
            "imports": [],
            "classes": [],
            "functions": [],
            "decorators": [],
            "docstring": None,
            "complexity_score": 0,
            "test_functions": [],
            "is_package": False,
            "entry_points": [],
        }

        try:
            tree = ast.parse(content)

            # Extract docstring
            analysis["docstring"] = ast.get_docstring(tree)

            # Walk through AST nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"].append(
                            {
                                "module": alias.name,
                                "alias": alias.asname,
                                "type": "import",
                            }
                        )
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        analysis["imports"].append(
                            {
                                "module": node.module,
                                "names": [alias.name for alias in node.names],
                                "type": "from_import",
                            }
                        )
                elif isinstance(node, ast.ClassDef):
                    analysis["classes"].append(
                        {
                            "name": node.name,
                            "line": node.lineno,
                            "methods": [
                                n.name
                                for n in node.body
                                if isinstance(n, ast.FunctionDef)
                            ],
                            "decorators": [
                                self.extract_decorator_name(d)
                                for d in node.decorator_list
                            ],
                            "docstring": ast.get_docstring(node),
                        }
                    )
                elif isinstance(node, ast.FunctionDef):
                    func_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "decorators": [
                            d.id if hasattr(d, "id") else str(d)
                            for d in node.decorator_list
                        ],
                        "docstring": ast.get_docstring(node),
                    }

                    if node.name.startswith("test_"):
                        analysis["test_functions"].append(func_info)
                    else:
                        analysis["functions"].append(func_info)

                    # Check for entry points
                    if node.name in ["main", "__main__", "run", "start"]:
                        analysis["entry_points"].append(node.name)

            # Calculate complexity
            analysis["complexity_score"] = len(analysis["classes"]) * 2 + len(
                analysis["functions"]
            )

            # Check if it's a package file
            analysis["is_package"] = filepath.name == "__init__.py"

        except SyntaxError as e:
            analysis["syntax_error"] = str(e)
        except Exception as e:
            analysis["analysis_error"] = str(e)

        return analysis

    def analyze_javascript_file(self, filepath, content):
        """JavaScript/TypeScript file analysis"""
        analysis = {
            "language": "JavaScript/TypeScript",
            "imports": [],
            "exports": [],
            "functions": [],
            "classes": [],
            "components": [],
            "is_react": False,
            "is_typescript": filepath.suffix in [".ts", ".tsx"],
        }

        # Look for React patterns
        if "import React" in content or 'from "react"' in content:
            analysis["is_react"] = True

        # Find imports (basic regex patterns)
        import_patterns = [
            r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'const\s+.*?\s+=\s+require\([\'"]([^\'"]+)[\'"]\)',
            r'import\s+[\'"]([^\'"]+)[\'"]',
        ]

        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            analysis["imports"].extend(matches)

        # Find exports
        export_patterns = [
            r"export\s+(?:default\s+)?(?:class|function|const|let|var)\s+(\w+)",
            r"export\s+{\s*([^}]+)\s*}",
            r"module\.exports\s*=\s*(\w+)",
        ]

        for pattern in export_patterns:
            matches = re.findall(pattern, content)
            analysis["exports"].extend(matches)

        # Find React components (basic detection)
        component_pattern = r"(?:function|const)\s+([A-Z]\w+)\s*(?:\([^)]*\))?\s*(?:=>)?\s*{[^}]*return\s*\([^;]+JSX|<"
        components = re.findall(component_pattern, content, re.MULTILINE | re.DOTALL)
        analysis["components"] = components

        return analysis

    def analyze_markdown_file(self, filepath, content):
        """Markdown file analysis"""
        analysis = {
            "language": "Markdown",
            "headings": [],
            "links": [],
            "images": [],
            "code_blocks": [],
            "word_count": len(content.split()),
            "is_readme": filepath.name.lower().startswith("readme"),
        }

        # Extract headings
        heading_pattern = r"^(#{1,6})\s+(.+)$"
        headings = re.findall(heading_pattern, content, re.MULTILINE)
        analysis["headings"] = [{"level": len(h[0]), "text": h[1]} for h in headings]

        # Extract links
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        links = re.findall(link_pattern, content)
        analysis["links"] = [{"text": l[0], "url": l[1]} for l in links]

        # Extract images
        image_pattern = r"!\[([^\]]*)\]\(([^)]+)\)"
        images = re.findall(image_pattern, content)
        analysis["images"] = [{"alt": i[0], "url": i[1]} for i in images]

        # Extract code blocks
        code_pattern = r"```(\w+)?\n(.*?)\n```"
        code_blocks = re.findall(code_pattern, content, re.DOTALL)
        analysis["code_blocks"] = [
            {"language": c[0], "code": c[1][:100]} for c in code_blocks
        ]

        return analysis

    def analyze_config_file(self, filepath, content):
        """Configuration file analysis"""
        analysis = {
            "language": "Configuration",
            "format": filepath.suffix[1:],  # Remove the dot
            "keys": [],
            "structure_depth": 0,
            "is_package_config": filepath.name
            in ["package.json", "pyproject.toml", "requirements.txt"],
        }

        try:
            if filepath.suffix == ".json":
                # Standard library imports
                import json

                data = json.loads(content)
                analysis["keys"] = list(data.keys()) if isinstance(data, dict) else []
                analysis["structure_depth"] = self.calculate_dict_depth(data)

                # Special handling for package.json
                if filepath.name == "package.json":
                    analysis["package_info"] = {
                        "name": data.get("name"),
                        "version": data.get("version"),
                        "dependencies": list(data.get("dependencies", {}).keys()),
                        "scripts": list(data.get("scripts", {}).keys()),
                    }

        except Exception as e:
            analysis["parse_error"] = str(e)

        return analysis

    def analyze_html_file(self, filepath, content):
        """HTML file analysis"""
        analysis = {
            "language": "HTML",
            "title": "",
            "external_resources": [],
            "forms": 0,
            "is_template": False,
        }

        # Extract title
        title_match = re.search(r"<title[^>]*>([^<]+)</title>", content, re.IGNORECASE)
        if title_match:
            analysis["title"] = title_match.group(1)

        # Check for template syntax
        template_patterns = [
            r"{%.*?%}",  # Django/Jinja2
            r"{{.*?}}",  # Handlebars/Vue/Angular
            r"<%.*?%>",  # JSP/EJS
        ]

        for pattern in template_patterns:
            if re.search(pattern, content):
                analysis["is_template"] = True
                break

        # Count forms
        analysis["forms"] = len(re.findall(r"<form[^>]*>", content, re.IGNORECASE))

        return analysis

    def analyze_css_file(self, filepath, content):
        """CSS file analysis"""
        analysis = {
            "language": "CSS",
            "selectors": [],
            "media_queries": 0,
            "imports": [],
            "is_sass": filepath.suffix in [".scss", ".sass"],
        }

        # Extract selectors (basic)
        selector_pattern = r"([.#]?[\w-]+(?:\s*[>+~]\s*[\w-]+)*)\s*{"
        selectors = re.findall(selector_pattern, content)
        analysis["selectors"] = selectors[:20]  # Limit to first 20

        # Count media queries
        analysis["media_queries"] = len(re.findall(r"@media", content, re.IGNORECASE))

        # Find imports
        import_pattern = r'@import\s+[\'"]([^\'"]+)[\'"]'
        imports = re.findall(import_pattern, content)
        analysis["imports"] = imports

        return analysis

    def analyze_generic_file(self, filepath, content):
        """Generic file analysis"""
        analysis = {"language": "Other", "is_binary": False, "encoding": "utf-8"}

        # Check if binary
        try:
            content.encode("utf-8")
            # Look for binary indicators
            if b"\x00" in content.encode("utf-8"):
                analysis["is_binary"] = True
        except:
            analysis["is_binary"] = True
            analysis["encoding"] = "unknown"

        return analysis

    def infer_file_purpose(self, filepath, content, analysis):
        """Infer the purpose of a file based on multiple factors"""
        name = filepath.name.lower()
        path_str = str(filepath).lower()

        # Test files
        if "test" in name or "test" in path_str or name.startswith("test_"):
            return "Test file for automated testing"

        # Demo files
        if "demo" in name or "example" in name:
            return "Demonstration or example file"

        # Configuration files
        if name in [
            "config.py",
            "settings.py",
            "config.json",
            ".env",
            "pyproject.toml",
        ]:
            return "Configuration file"

        # Main entry points
        if name in ["main.py", "app.py", "index.js", "server.py"]:
            return "Main application entry point"

        # Package initialization
        if name == "__init__.py":
            return "Python package initialization file"

        # Documentation
        if filepath.suffix == ".md":
            if name.startswith("readme"):
                return "Project documentation (README)"
            else:
                return "Documentation file"

        # Based on Python analysis
        if analysis.get("language") == "Python":
            if analysis.get("classes"):
                return f"Python module with {len(analysis['classes'])} class(es)"
            elif analysis.get("functions"):
                return f"Python module with {len(analysis['functions'])} function(s)"
            elif analysis.get("is_package"):
                return "Python package initialization"

        # Based on directory location
        if "api" in path_str:
            return "API-related functionality"
        elif "gui" in path_str or "ui" in path_str:
            return "User interface component"
        elif "core" in path_str:
            return "Core system functionality"
        elif "util" in path_str or "helper" in path_str:
            return "Utility/helper functions"

        return f'{analysis.get("language", "File")} source file'

    def calculate_file_hash(self, filepath):
        """Calculate SHA256 hash of file content"""
        try:
            with open(filepath, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except:
            return None

    def calculate_dict_depth(self, d):
        """Calculate the depth of a nested dictionary"""
        if isinstance(d, dict) and d:
            return 1 + max(self.calculate_dict_depth(v) for v in d.values())
        elif isinstance(d, list) and d:
            return max(
                self.calculate_dict_depth(item)
                for item in d
                if isinstance(item, (dict, list))
            )
        return 0

    def analyze_directory_intelligence(self, dir_path):
        """Deep directory analysis with intelligence"""
        directory = Path(dir_path)

        analysis = {
            "path": str(directory),
            "name": directory.name,
            "purpose": self.infer_directory_purpose(directory),
            "total_files": 0,
            "total_size": 0,
            "file_types": defaultdict(int),
            "programming_languages": defaultdict(int),
            "complexity_score": 0,
            "main_files": [],
            "entry_points": [],
            "test_coverage": 0,
            "documentation_coverage": 0,
            "subdirectories": [],
            "key_functions": [],
            "dependencies": set(),
            "quality_indicators": {},
        }

        if not directory.exists():
            return analysis

        try:
            # Analyze all files in directory
            for item in directory.iterdir():
                if item.is_file():
                    file_analysis = self.analyze_file_content(item)
                    analysis["total_files"] += 1
                    analysis["total_size"] += file_analysis.get("size", 0)

                    # Track file types
                    ext = item.suffix or "no_extension"
                    analysis["file_types"][ext] += 1

                    # Track programming languages
                    lang = file_analysis.get("language", "Other")
                    analysis["programming_languages"][lang] += 1

                    # Identify main files
                    if item.name.lower() in [
                        "main.py",
                        "index.js",
                        "app.py",
                        "__init__.py",
                    ]:
                        analysis["main_files"].append(item.name)

                    # Collect entry points
                    if file_analysis.get("entry_points"):
                        analysis["entry_points"].extend(file_analysis["entry_points"])

                    # Add to complexity score
                    analysis["complexity_score"] += file_analysis.get(
                        "complexity_score", 0
                    )

                    # Collect dependencies
                    if file_analysis.get("imports"):
                        for imp in file_analysis["imports"]:
                            if isinstance(imp, dict):
                                analysis["dependencies"].add(imp.get("module", ""))
                            else:
                                analysis["dependencies"].add(str(imp))

                elif item.is_dir() and not item.name.startswith("."):
                    analysis["subdirectories"].append(item.name)

            # Calculate coverage metrics
            test_files = sum(1 for f in directory.glob("**/test_*.py")) + sum(
                1 for f in directory.glob("**/*_test.py")
            )
            doc_files = sum(1 for f in directory.glob("**/*.md")) + sum(
                1 for f in directory.glob("**/README*")
            )

            if analysis["total_files"] > 0:
                analysis["test_coverage"] = (test_files / analysis["total_files"]) * 100
                analysis["documentation_coverage"] = (
                    doc_files / analysis["total_files"]
                ) * 100

            # Quality indicators
            analysis["quality_indicators"] = {
                "has_readme": any(
                    f.name.lower().startswith("readme")
                    for f in directory.glob("*")
                    if f.is_file()
                ),
                "has_tests": test_files > 0,
                "has_documentation": doc_files > 0,
                "organized_structure": len(analysis["subdirectories"]) > 0,
                "complexity_per_file": analysis["complexity_score"]
                / max(analysis["total_files"], 1),
            }

        except PermissionError:
            analysis["error"] = "Permission denied"

        return analysis

    def infer_directory_purpose(self, directory):
        """Infer directory purpose with enhanced intelligence"""
        name = directory.name.lower()
        parent = directory.parent.name.lower() if directory.parent != directory else ""

        purpose_map = {
            "test": "Testing infrastructure and automated tests",
            "tests": "Testing infrastructure and automated tests",
            "spec": "Test specifications and testing files",
            "doc": "Documentation and guides",
            "docs": "Documentation and guides",
            "documentation": "Project documentation",
            "config": "Configuration files and settings",
            "configuration": "Configuration files and settings",
            "data": "Data storage, databases, and data files",
            "database": "Database files and data storage",
            "db": "Database files and storage",
            "gui": "Graphical user interface components",
            "ui": "User interface components and assets",
            "frontend": "Frontend application code",
            "backend": "Backend server and API code",
            "api": "API definitions, handlers, and endpoints",
            "core": "Core system functionality and components",
            "engine": "Core processing engines and algorithms",
            "kernel": "System kernel and low-level components",
            "plugin": "Plugin system and extensions",
            "plugins": "Plugin system and extensions",
            "extension": "Extensions and add-ons",
            "extensions": "Extensions and add-ons",
            "util": "Utility functions and helper modules",
            "utils": "Utility functions and helper modules",
            "helper": "Helper functions and utilities",
            "helpers": "Helper functions and utilities",
            "tool": "Development and maintenance tools",
            "tools": "Development and maintenance tools",
            "script": "Automation and utility scripts",
            "scripts": "Automation and utility scripts",
            "bridge": "Integration bridges and adapters",
            "bridges": "Integration bridges and adapters",
            "adapter": "System adapters and interfaces",
            "adapters": "System adapters and interfaces",
            "interface": "Interface definitions and implementations",
            "interfaces": "Interface definitions and implementations",
            "component": "Reusable components and modules",
            "components": "Reusable components and modules",
            "module": "Modular components and functionality",
            "modules": "Modular components and functionality",
            "service": "Service layer and business logic",
            "services": "Service layer and business logic",
            "controller": "Application controllers and handlers",
            "controllers": "Application controllers and handlers",
            "model": "Data models and schemas",
            "models": "Data models and schemas",
            "view": "View layer and presentation logic",
            "views": "View layer and presentation logic",
            "template": "Templates and view templates",
            "templates": "Templates and view templates",
            "static": "Static assets (CSS, JS, images)",
            "assets": "Static assets and resources",
            "resource": "Application resources and assets",
            "resources": "Application resources and assets",
            "lib": "Third-party libraries and dependencies",
            "library": "Library code and reusable modules",
            "vendor": "Third-party vendor code",
            "external": "External dependencies and libraries",
            "runtime": "Runtime components and services",
            "deploy": "Deployment scripts and configurations",
            "deployment": "Deployment configurations and scripts",
            "build": "Build scripts and compilation tools",
            "dist": "Distribution files and built artifacts",
            "output": "Generated output and build artifacts",
            "bin": "Binary files and executables",
            "src": "Source code files",
            "source": "Source code files",
            "example": "Example code and demonstrations",
            "examples": "Example code and demonstrations",
            "demo": "Demonstration code and samples",
            "demos": "Demonstration code and samples",
            "sample": "Sample code and examples",
            "samples": "Sample code and examples",
            "backup": "Backup files and archives",
            "backups": "Backup files and archives",
            "archive": "Archived files and old versions",
            "archives": "Archived files and old versions",
            "log": "Log files and logging output",
            "logs": "Log files and logging output",
            "temp": "Temporary files and cache",
            "tmp": "Temporary files and cache",
            "cache": "Cache files and temporary storage",
            "migration": "Database migrations and schema changes",
            "migrations": "Database migrations and schema changes",
            "schema": "Database schemas and structures",
            "schemas": "Database schemas and structures",
            "fixture": "Test fixtures and sample data",
            "fixtures": "Test fixtures and sample data",
            "mock": "Mock objects and test doubles",
            "mocks": "Mock objects and test doubles",
            "stub": "Stub implementations and placeholders",
            "stubs": "Stub implementations and placeholders",
        }

        # Check exact match first
        if name in purpose_map:
            return purpose_map[name]

        # Check for partial matches
        for key, purpose in purpose_map.items():
            if key in name:
                return purpose

        # Context-based inference
        if "aetherra" in name:
            return "Aetherra OS core component"
        elif "lyrixa" in name:
            return "Lyrixa AI assistant component"
        elif "intelligence" in name or "ai" in name:
            return "Artificial intelligence and ML components"
        elif "memory" in name:
            return "Memory management and storage systems"
        elif "quantum" in name:
            return "Quantum computing and advanced algorithms"
        elif "ethics" in name:
            return "Ethics and safety systems"
        elif "web" in name:
            return "Web interface and server components"
        elif "agent" in name:
            return "Agent-based systems and AI agents"

        return f"Specialized directory for {name} functionality"

    def run_comprehensive_analysis(self):
        """Run the complete advanced analysis"""
        print("🔬 Running Advanced Project Intelligence Analysis...")
        print("=" * 60)

        total_files = 0
        total_dirs = 0

        # Analyze all files and directories
        for root, dirs, files in os.walk(self.project_root):
            # Skip common excludes
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".") and d not in ["__pycache__", "node_modules"]
            ]

            current_dir = Path(root)

            # Analyze directory
            dir_analysis = self.analyze_directory_intelligence(current_dir)
            self.directory_intelligence[str(current_dir)] = dir_analysis
            total_dirs += 1

            # Analyze files in directory
            for filename in files:
                if filename.startswith("."):
                    continue

                filepath = current_dir / filename
                file_analysis = self.analyze_file_content(filepath)
                self.file_intelligence[str(filepath)] = file_analysis
                total_files += 1

                if total_files % 50 == 0:
                    print(
                        f"   📊 Analyzed {total_files} files and {total_dirs} directories..."
                    )

        print("✅ Analysis complete!")
        print(f"   📁 Directories analyzed: {total_dirs}")
        print(f"   📄 Files analyzed: {total_files}")

        return {
            "files": self.file_intelligence,
            "directories": self.directory_intelligence,
            "summary": self.generate_intelligence_summary(),
        }

    def generate_intelligence_summary(self):
        """Generate comprehensive intelligence summary"""
        summary = {
            "total_files": len(self.file_intelligence),
            "total_directories": len(self.directory_intelligence),
            "languages": defaultdict(int),
            "file_types": defaultdict(int),
            "purposes": defaultdict(int),
            "complexity_analysis": {},
            "quality_metrics": {},
            "dependency_analysis": {},
            "project_health": {},
        }

        total_complexity = 0
        total_size = 0

        # Analyze files
        for file_path, file_data in self.file_intelligence.items():
            lang = file_data.get("language", "Other")
            summary["languages"][lang] += 1

            ext = Path(file_path).suffix or "no_extension"
            summary["file_types"][ext] += 1

            purpose = file_data.get("purpose", "Unknown")
            summary["purposes"][purpose] += 1

            total_complexity += file_data.get("complexity_score", 0)
            total_size += file_data.get("size", 0)

        # Calculate averages
        if summary["total_files"] > 0:
            summary["complexity_analysis"] = {
                "average_complexity": total_complexity / summary["total_files"],
                "total_complexity": total_complexity,
                "average_file_size": total_size / summary["total_files"],
                "total_project_size": total_size,
            }

        return summary

    def save_intelligence_report(self, filename="advanced_project_intelligence.json"):
        """Save comprehensive analysis to file"""
        analysis_data = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "analysis_type": "Advanced Project Intelligence",
            "files": self.file_intelligence,
            "directories": self.directory_intelligence,
            "summary": self.generate_intelligence_summary(),
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False, default=str)

        print(f"💾 Advanced intelligence report saved to {filename}")
        return filename


if __name__ == "__main__":
    # Run advanced analysis
    analyzer = AdvancedProjectAnalyzer(".")
    results = analyzer.run_comprehensive_analysis()
    analyzer.save_intelligence_report()
