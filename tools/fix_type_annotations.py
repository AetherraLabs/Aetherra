#!/usr/bin/env python3
"""
Type Annotation Auto-Fixer for Aetherra Project
==============================================

Automatically adds basic type annotations to Python files to improve
code quality and type safety.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union


class TypeAnnotationFixer:
    """Automatically fix missing type annotations in Python files."""

    def __init__(self):
        self.common_return_types = {
            # Common method patterns
            "__init__": "None",
            "__str__": "str",
            "__repr__": "str",
            "__len__": "int",
            "__bool__": "bool",
            "__enter__": "Self",
            "__exit__": "None",
            # Common method name patterns
            "get_": "Optional[Any]",
            "set_": "None",
            "update_": "None",
            "create_": "Any",
            "delete_": "None",
            "remove_": "None",
            "add_": "None",
            "clear_": "None",
            "reset_": "None",
            "initialize_": "None",
            "setup_": "None",
            "cleanup_": "None",
            "close_": "None",
            "open_": "Any",
            "load_": "Any",
            "save_": "None",
            "start_": "None",
            "stop_": "None",
            "pause_": "None",
            "resume_": "None",
            "enable_": "None",
            "disable_": "None",
            "validate_": "bool",
            "check_": "bool",
            "is_": "bool",
            "has_": "bool",
            "can_": "bool",
            "should_": "bool",
            "process_": "Any",
            "handle_": "Any",
            "execute_": "Any",
            "run_": "Any",
        }

        self.common_param_types = {
            "self": None,  # Skip self
            "cls": None,  # Skip cls
            "data": "Any",
            "value": "Any",
            "key": "str",
            "name": "str",
            "path": "Union[str, Path]",
            "file": "Union[str, Path]",
            "filename": "str",
            "text": "str",
            "content": "str",
            "message": "str",
            "error": "Exception",
            "exception": "Exception",
            "config": "Dict[str, Any]",
            "options": "Dict[str, Any]",
            "args": "*args",
            "kwargs": "**kwargs",
            "enabled": "bool",
            "force": "bool",
            "strict": "bool",
            "verbose": "bool",
            "debug": "bool",
            "timeout": "float",
            "delay": "float",
            "count": "int",
            "size": "int",
            "length": "int",
            "width": "int",
            "height": "int",
            "x": "float",
            "y": "float",
            "z": "float",
        }

    def get_suggested_return_type(self, func_name: str, is_method: bool = False) -> str:
        """Get suggested return type based on function name patterns."""
        # Check exact matches first
        if func_name in self.common_return_types:
            return self.common_return_types[func_name]

        # Check prefix patterns
        for prefix, return_type in self.common_return_types.items():
            if func_name.startswith(prefix):
                return return_type

        # Default based on context
        if is_method and func_name.startswith("_"):
            return "None"  # Private methods often return None

        return "Any"

    def get_suggested_param_type(self, param_name: str) -> Optional[str]:
        """Get suggested parameter type based on parameter name."""
        if param_name in self.common_param_types:
            return self.common_param_types[param_name]

        # Pattern matching
        if param_name.endswith("_id"):
            return "str"
        elif param_name.endswith("_list"):
            return "List[Any]"
        elif param_name.endswith("_dict"):
            return "Dict[str, Any]"
        elif param_name.endswith("_set"):
            return "Set[Any]"
        elif param_name.endswith("_path"):
            return "Union[str, Path]"
        elif param_name.endswith("_file"):
            return "Union[str, Path]"
        elif param_name.endswith("_url"):
            return "str"
        elif param_name.endswith("_callback"):
            return "Callable"

        return "Any"

    def fix_file(self, file_path: Path) -> bool:
        """Fix type annotations in a single file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse the AST to find functions without annotations
            try:
                tree = ast.parse(content)
            except SyntaxError:
                print(f"Syntax error in {file_path}, skipping...")
                return False

            lines = content.split("\n")
            modified = False

            # Find functions without return annotations
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith("__") and node.name.endswith("__"):
                        continue  # Skip most dunder methods except __init__

                    line_idx = node.lineno - 1
                    if line_idx >= len(lines):
                        continue

                    line = lines[line_idx]

                    # Check if function lacks return annotation
                    if not node.returns and ") -> " not in line:
                        # Determine if it's a method
                        is_method = any(
                            arg.arg in ["self", "cls"] for arg in node.args.args
                        )

                        # Get suggested return type
                        return_type = self.get_suggested_return_type(
                            node.name, is_method
                        )

                        # Add return annotation
                        if line.rstrip().endswith(":"):
                            lines[line_idx] = line.rstrip()[:-1] + f" -> {return_type}:"
                            modified = True
                        elif "):" in line:
                            lines[line_idx] = line.replace("):", f") -> {return_type}:")
                            modified = True

                    # Check parameters without annotations
                    for arg in node.args.args:
                        if arg.arg in ["self", "cls"]:
                            continue

                        if not arg.annotation:
                            param_type = self.get_suggested_param_type(arg.arg)
                            if param_type and param_type not in ["*args", "**kwargs"]:
                                # Find the parameter in the line and add annotation
                                param_pattern = rf"\\b{re.escape(arg.arg)}\\b"
                                if re.search(param_pattern, line):
                                    # Add type annotation
                                    new_line = re.sub(
                                        rf"\\b{re.escape(arg.arg)}\\b(?=\\s*[,)])",
                                        f"{arg.arg}: {param_type}",
                                        line,
                                    )
                                    if new_line != line:
                                        lines[line_idx] = new_line
                                        modified = True

            if modified:
                # Add necessary imports at the top
                imports_to_add = set()
                new_content = "\n".join(lines)

                if "Any" in new_content and "from typing import" not in new_content:
                    imports_to_add.add("Any")
                if "Optional" in new_content and "Optional" not in new_content:
                    imports_to_add.add("Optional")
                if "Dict" in new_content and "Dict" not in new_content:
                    imports_to_add.add("Dict")
                if "List" in new_content and "List" not in new_content:
                    imports_to_add.add("List")
                if "Union" in new_content and "Union" not in new_content:
                    imports_to_add.add("Union")
                if "Callable" in new_content and "Callable" not in new_content:
                    imports_to_add.add("Callable")
                if "Set" in new_content and "Set" not in new_content:
                    imports_to_add.add("Set")

                if imports_to_add:
                    # Find existing typing import or add new one
                    lines = new_content.split("\n")
                    import_line_idx = None

                    for i, line in enumerate(lines):
                        if line.startswith("from typing import"):
                            import_line_idx = i
                            break

                    if import_line_idx is not None:
                        # Extend existing import
                        existing_imports = (
                            lines[import_line_idx]
                            .replace("from typing import ", "")
                            .split(", ")
                        )
                        all_imports = set(existing_imports) | imports_to_add
                        lines[import_line_idx] = (
                            f"from typing import {', '.join(sorted(all_imports))}"
                        )
                    else:
                        # Add new import after other imports
                        insert_idx = 0
                        for i, line in enumerate(lines):
                            if (
                                line.startswith(("import ", "from "))
                                or line.strip() == ""
                            ):
                                insert_idx = i + 1
                            else:
                                break

                        lines.insert(
                            insert_idx,
                            f"from typing import {', '.join(sorted(imports_to_add))}",
                        )

                    new_content = "\n".join(lines)

                # Write back to file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                return True

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        return False

    def fix_project(
        self, root_path: Path, file_patterns: List[str] = None
    ) -> Dict[str, int]:
        """Fix type annotations across the project."""
        if file_patterns is None:
            file_patterns = ["**/*.py"]

        results = {"fixed": 0, "errors": 0, "skipped": 0}

        for pattern in file_patterns:
            for py_file in root_path.glob(pattern):
                # Skip certain directories
                if any(part.startswith(".") for part in py_file.parts):
                    results["skipped"] += 1
                    continue
                if "venv" in py_file.parts or "node_modules" in py_file.parts:
                    results["skipped"] += 1
                    continue

                try:
                    if self.fix_file(py_file):
                        print(f"Fixed: {py_file}")
                        results["fixed"] += 1
                    else:
                        results["skipped"] += 1
                except Exception as e:
                    print(f"Error: {py_file}: {e}")
                    results["errors"] += 1

        return results


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Fix missing type annotations")
    parser.add_argument("--root", default=".", help="Root directory to scan")
    parser.add_argument("--files", nargs="*", help="Specific files to fix")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be fixed"
    )

    args = parser.parse_args()

    fixer = TypeAnnotationFixer()
    root_path = Path(args.root)

    if args.files:
        # Fix specific files
        for file_path in args.files:
            path = Path(file_path)
            if path.exists():
                if fixer.fix_file(path):
                    print(f"Fixed: {path}")
                else:
                    print(f"No changes: {path}")
    else:
        # Fix entire project
        results = fixer.fix_project(root_path)
        print(f"\n📊 Results:")
        print(f"  Fixed: {results['fixed']} files")
        print(f"  Errors: {results['errors']} files")
        print(f"  Skipped: {results['skipped']} files")


if __name__ == "__main__":
    main()
