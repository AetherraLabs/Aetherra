#!/usr/bin/env python3
"""
Aetherra Automated Warning Fixer
Automatically fixes easy-to-resolve code warnings across the project.
"""

import ast
import json
import re
from datetime import datetime
from pathlib import Path


class WarningFixer:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.fixes_applied = []
        self.backup_dir = self.project_root / "backups" / "auto_fixes"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, file_path):
        """Create a backup of the file before making changes."""
        backup_path = (
            self.backup_dir
            / f"{file_path.name}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        backup_path.write_text(file_path.read_text(encoding="utf-8"), encoding="utf-8")
        return backup_path

    def remove_unused_imports(self, file_path):
        """Remove unused imports from a Python file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse the AST to identify imports and their usage
            tree = ast.parse(content)

            # Find all imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(
                            {
                                "type": "import",
                                "name": alias.name,
                                "asname": alias.asname,
                                "lineno": node.lineno,
                            }
                        )
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        imports.append(
                            {
                                "type": "from_import",
                                "module": node.module,
                                "name": alias.name,
                                "asname": alias.asname,
                                "lineno": node.lineno,
                            }
                        )

            # Find used names
            used_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    used_names.add(node.id)
                elif isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name):
                        used_names.add(node.value.id)

            # Identify unused imports
            lines = content.split("\n")
            lines_to_remove = set()

            for imp in imports:
                import_name = imp["asname"] if imp["asname"] else imp["name"]
                if imp["type"] == "import":
                    # For "import module", check if module is used
                    if import_name not in used_names:
                        lines_to_remove.add(
                            imp["lineno"] - 1
                        )  # Convert to 0-based index
                elif imp["type"] == "from_import":
                    # For "from module import name", check if name is used
                    if import_name not in used_names and imp["name"] != "*":
                        lines_to_remove.add(imp["lineno"] - 1)

            # Remove unused import lines
            if lines_to_remove:
                self.create_backup(file_path)
                new_lines = [
                    line for i, line in enumerate(lines) if i not in lines_to_remove
                ]
                new_content = "\n".join(new_lines)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                self.fixes_applied.append(
                    {
                        "file": str(file_path),
                        "type": "unused_imports",
                        "count": len(lines_to_remove),
                        "lines_removed": sorted(list(lines_to_remove)),
                    }
                )

                return len(lines_to_remove)

        except (SyntaxError, UnicodeDecodeError, PermissionError) as e:
            print(f"⚠️ Could not process {file_path}: {e}")
            return 0

        return 0

    def fix_print_statements(self, file_path):
        """Remove or comment out debug print statements."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            changes_made = 0

            # Pattern to match debug print statements
            debug_patterns = [
                re.compile(r'^\s*print\s*\(\s*["\']debug', re.IGNORECASE),
                re.compile(r'^\s*print\s*\(\s*["\']test', re.IGNORECASE),
                re.compile(r'^\s*print\s*\(\s*f?["\'].*debug.*["\']', re.IGNORECASE),
            ]

            for i, line in enumerate(lines):
                for pattern in debug_patterns:
                    if pattern.match(line):
                        # Comment out the debug print
                        lines[i] = "# " + line
                        changes_made += 1
                        break

            if changes_made > 0:
                self.create_backup(file_path)
                new_content = "\n".join(lines)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                self.fixes_applied.append(
                    {
                        "file": str(file_path),
                        "type": "debug_prints",
                        "count": changes_made,
                    }
                )

            return changes_made

        except (UnicodeDecodeError, PermissionError) as e:
            print(f"⚠️ Could not process {file_path}: {e}")
            return 0

    def fix_line_length(self, file_path, max_length=120):
        """Fix lines that are too long by adding line breaks."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            changes_made = 0

            for i, line in enumerate(lines):
                if len(line) > max_length and not line.strip().startswith("#"):
                    # Try to break long lines at logical points
                    if "," in line:
                        # Break at comma for function calls, lists, etc.
                        indent = len(line) - len(line.lstrip())
                        parts = line.split(",")
                        if len(parts) > 1:
                            new_line = parts[0] + ","
                            for part in parts[1:-1]:
                                new_line += (
                                    "\n" + " " * (indent + 4) + part.strip() + ","
                                )
                            new_line += "\n" + " " * (indent + 4) + parts[-1].strip()
                            lines[i] = new_line
                            changes_made += 1
                    elif " and " in line or " or " in line:
                        # Break at logical operators
                        for op in [" and ", " or "]:
                            if op in line:
                                indent = len(line) - len(line.lstrip())
                                parts = line.split(op)
                                if len(parts) > 1:
                                    new_line = parts[0] + f" \\{op.strip()}"
                                    for part in parts[1:]:
                                        new_line += (
                                            "\n" + " " * (indent + 4) + part.strip()
                                        )
                                    lines[i] = new_line
                                    changes_made += 1
                                break

            if changes_made > 0:
                self.create_backup(file_path)
                new_content = "\n".join(lines)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                self.fixes_applied.append(
                    {
                        "file": str(file_path),
                        "type": "line_length",
                        "count": changes_made,
                    }
                )

            return changes_made

        except (UnicodeDecodeError, PermissionError) as e:
            print(f"⚠️ Could not process {file_path}: {e}")
            return 0

    def fix_trailing_whitespace(self, file_path):
        """Remove trailing whitespace from lines."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            changes_made = 0

            for i, line in enumerate(lines):
                stripped = line.rstrip()
                if stripped != line:
                    lines[i] = stripped
                    changes_made += 1

            if changes_made > 0:
                self.create_backup(file_path)
                new_content = "\n".join(lines)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                self.fixes_applied.append(
                    {
                        "file": str(file_path),
                        "type": "trailing_whitespace",
                        "count": changes_made,
                    }
                )

            return changes_made

        except (UnicodeDecodeError, PermissionError) as e:
            print(f"⚠️ Could not process {file_path}: {e}")
            return 0

    def fix_file(self, file_path):
        """Apply all automated fixes to a single file."""
        if not file_path.suffix == ".py":
            return 0

        total_fixes = 0
        total_fixes += self.remove_unused_imports(file_path)
        total_fixes += self.fix_print_statements(file_path)
        total_fixes += self.fix_line_length(file_path)
        total_fixes += self.fix_trailing_whitespace(file_path)

        return total_fixes

    def run_automated_fixes(self):
        """Run automated fixes across the entire project."""
        print("🔧 Starting automated warning fixes...")

        python_files = list(self.project_root.rglob("*.py"))
        total_files_processed = 0
        total_fixes_applied = 0

        for py_file in python_files:
            if any(
                exclude in str(py_file)
                for exclude in ["__pycache__", ".git", "venv", "env", "backup"]
            ):
                continue

            print(f"Processing: {py_file.relative_to(self.project_root)}")
            fixes = self.fix_file(py_file)

            if fixes > 0:
                total_files_processed += 1
                total_fixes_applied += fixes
                print(f"  ✅ Applied {fixes} fixes")
            else:
                print(f"  ✨ No fixes needed")

        # Generate summary report
        self.generate_fix_report(total_files_processed, total_fixes_applied)

        return total_files_processed, total_fixes_applied

    def generate_fix_report(self, files_processed, total_fixes):
        """Generate a report of all fixes applied."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "files_processed": files_processed,
            "total_fixes_applied": total_fixes,
            "backup_location": str(self.backup_dir),
            "fixes_by_type": {},
            "detailed_fixes": self.fixes_applied,
        }

        # Count fixes by type
        for fix in self.fixes_applied:
            fix_type = fix["type"]
            if fix_type not in report["fixes_by_type"]:
                report["fixes_by_type"][fix_type] = 0
            report["fixes_by_type"][fix_type] += fix["count"]

        # Save report
        with open("automated_fixes_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)

        # Print summary
        print("\n" + "=" * 60)
        print("🔧 AUTOMATED FIX SUMMARY")
        print("=" * 60)
        print(f"📁 Files Processed: {files_processed}")
        print(f"🔧 Total Fixes Applied: {total_fixes}")
        print(f"💾 Backups Saved To: {self.backup_dir}")

        print("\n📊 FIXES BY TYPE:")
        for fix_type, count in report["fixes_by_type"].items():
            fix_name = fix_type.replace("_", " ").title()
            print(f"  ✅ {fix_name:<20}: {count:4d} fixes")

        print(f"\n📄 Detailed report saved to: automated_fixes_report.json")
        print("=" * 60)


def main():
    """Main entry point for automated warning fixes."""
    print("🌟 Aetherra Automated Warning Fixer")
    print("Applying automated fixes to common code quality issues...\n")

    fixer = WarningFixer()
    files_processed, total_fixes = fixer.run_automated_fixes()

    if total_fixes > 0:
        print(
            f"\n✅ Successfully applied {total_fixes} fixes to {files_processed} files!"
        )
        print("🔄 Run 'python analyze_warnings.py' again to see the improvement")
    else:
        print("\n✨ No automated fixes were needed - code is already clean!")

    print("\n💡 Next Steps:")
    print("1. Review automated_fixes_report.json for details")
    print("2. Test your code to ensure fixes didn't break anything")
    print("3. Commit the changes if everything looks good")
    print("4. Address remaining warnings manually")


if __name__ == "__main__":
    main()
