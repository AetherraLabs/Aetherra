# lyrixa/ai/plugin_rewriter.py

import ast
import datetime
import difflib
import logging
import os
import re
from typing import Dict, List, Optional, Tuple

import openai

from lyrixa.core.plugin_state_memory import PluginStateMemory
from lyrixa.utils.safe_save import SafeSavePlugin


class PluginRewriterError(Exception):
    """Custom exception for Plugin Rewriter errors"""

    pass


class PluginRewriter:
    """
    AI-powered plugin rewriter for explaining, refactoring, and enhancing plugins.
    Provides safety mechanisms, version control, and intelligent code analysis.
    """

    def __init__(self, plugin_dir="plugins", history_dir=".plugin_history"):
        self.plugin_dir = plugin_dir
        self.history_dir = history_dir
        self.safe_saver = SafeSavePlugin()
        self.state_memory = PluginStateMemory()

        # Ensure directories exist
        os.makedirs(self.history_dir, exist_ok=True)
        os.makedirs(self.plugin_dir, exist_ok=True)

        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Safety limits
        self.max_code_size = 50000  # Maximum code size in characters
        self.max_backup_files = 100  # Maximum backup files per plugin

    def explain_plugin(self, plugin_name: str) -> str:
        """
        Generate a natural language explanation of what a plugin does.

        Args:
            plugin_name: Name of the plugin to explain

        Returns:
            str: Natural language explanation of the plugin
        """
        try:
            # Validate and read plugin
            plugin_path = self._get_plugin_path(plugin_name)
            code = self._read_plugin_code(plugin_path)

            # Extract metadata and structure
            metadata = self._extract_plugin_metadata(code)

            # Enhanced prompt with metadata
            prompt = f"""
            Analyze and explain this Python plugin code in clear, natural language.

            Plugin Information:
            - Name: {plugin_name}
            - File size: {len(code)} characters
            - Functions detected: {len(metadata.get("functions", []))}
            - Classes detected: {len(metadata.get("classes", []))}

            Please provide:
            1. A brief summary of what this plugin does
            2. Key functionality and features
            3. Input requirements and expected parameters
            4. Output types and what the plugin produces
            5. Any notable patterns or architectural decisions

            Code to analyze:
            ```python
            {code}
            ```

            Please write in clear, beginner-friendly language that would help a developer understand this plugin.
            """

            response = self._call_openai(prompt)

            # Log the explanation request
            self.logger.info(f"Generated explanation for plugin: {plugin_name}")

            return response

        except Exception as e:
            error_msg = f"Failed to explain plugin '{plugin_name}': {str(e)}"
            self.logger.error(error_msg)
            return error_msg

    def refactor_plugin(
        self, plugin_name: str, goal: str = "optimize code clarity"
    ) -> str:
        """
        Refactor a plugin to meet specific goals with safety measures.

        Args:
            plugin_name: Name of the plugin to refactor
            goal: Refactoring goal (e.g., "optimize memory", "improve readability")

        Returns:
            str: Status message indicating success or failure
        """
        try:
            # Validate inputs
            plugin_path = self._get_plugin_path(plugin_name)
            original_code = self._read_plugin_code(plugin_path)

            # Safety check: backup original
            backup_path = self._create_version_backup(plugin_name, original_code)

            # Enhanced refactoring prompt
            prompt = f"""
            Refactor the following Python plugin code to {goal}.

            IMPORTANT REQUIREMENTS:
            1. Maintain all existing functionality
            2. Preserve the plugin's interface and public methods
            3. Keep all imports that are being used
            4. Add proper docstrings if missing
            5. Follow Python best practices and PEP 8
            6. Return ONLY the refactored Python code, no explanations

            Original code:
            ```python
            {original_code}
            ```

            Refactored code:
            """

            refactored_code = self._call_openai(prompt)

            # Clean the response (remove markdown formatting if present)
            refactored_code = self._clean_code_response(refactored_code)

            # Validate refactored code
            if self._validate_python_syntax(refactored_code):
                # Safe write refactored code
                success = self.safe_saver.safe_write_text(plugin_path, refactored_code)

                if success:
                    self.logger.info(
                        f"Successfully refactored plugin: {plugin_name} (goal: {goal})"
                    )
                    return (
                        f"✅ Refactor successful. Original backed up to: {backup_path}"
                    )
                else:
                    return "❌ Failed to save refactored plugin."
            else:
                return "❌ Refactored code contains syntax errors. Original code preserved."

        except Exception as e:
            error_msg = f"Failed to refactor plugin '{plugin_name}': {str(e)}"
            self.logger.error(error_msg)
            return error_msg

    def add_logging_to_plugin(self, plugin_name: str) -> str:
        """
        Add comprehensive logging to a plugin.

        Args:
            plugin_name: Name of the plugin to add logging to

        Returns:
            str: Status message indicating success or failure
        """
        try:
            plugin_path = self._get_plugin_path(plugin_name)
            original_code = self._read_plugin_code(plugin_path)

            # Backup original
            backup_path = self._create_version_backup(plugin_name, original_code)

            # Enhanced logging injection prompt
            prompt = f"""
            Add comprehensive logging to the following Python plugin code.

            REQUIREMENTS:
            1. Add 'import logging' at the top if not present
            2. Add logging.getLogger(__name__) setup
            3. Add INFO level logs for major function entries/exits
            4. Add DEBUG level logs for important operations
            5. Add ERROR level logs for exception handling
            6. Add timing logs for performance monitoring
            7. Preserve all existing functionality
            8. Return ONLY the modified Python code

            Original code:
            ```python
            {original_code}
            ```

            Code with logging added:
            """

            logged_code = self._call_openai(prompt)
            logged_code = self._clean_code_response(logged_code)

            # Validate modified code
            if self._validate_python_syntax(logged_code):
                success = self.safe_saver.safe_write_text(plugin_path, logged_code)

                if success:
                    self.logger.info(
                        f"Successfully added logging to plugin: {plugin_name}"
                    )
                    return f"✅ Logging added successfully. Original backed up to: {backup_path}"
                else:
                    return "❌ Failed to save plugin with logging."
            else:
                return (
                    "❌ Modified code contains syntax errors. Original code preserved."
                )

        except Exception as e:
            error_msg = f"Failed to add logging to plugin '{plugin_name}': {str(e)}"
            self.logger.error(error_msg)
            return error_msg

    def rollback_plugin(self, plugin_name: str, version: str) -> str:
        """
        Rollback a plugin to a specific version.

        Args:
            plugin_name: Name of the plugin to rollback
            version: Version timestamp to rollback to

        Returns:
            str: Status message
        """
        try:
            backup_path = os.path.join(self.history_dir, f"{plugin_name}_{version}.bak")

            if not os.path.exists(backup_path):
                return f"❌ Version {version} not found for plugin {plugin_name}"

            plugin_path = self._get_plugin_path(plugin_name)

            # Create backup of current version before rollback
            current_code = self._read_plugin_code(plugin_path)
            self._create_version_backup(
                plugin_name, current_code, suffix="pre_rollback"
            )

            # Read backup version
            with open(backup_path, "r", encoding="utf-8") as f:
                backup_code = f.read()

            # Restore backup version
            success = self.safe_saver.safe_write_text(plugin_path, backup_code)

            if success:
                self.logger.info(
                    f"Rolled back plugin {plugin_name} to version {version}"
                )
                return f"✅ Successfully rolled back {plugin_name} to version {version}"
            else:
                return "❌ Failed to rollback plugin"

        except Exception as e:
            error_msg = f"Failed to rollback plugin '{plugin_name}': {str(e)}"
            self.logger.error(error_msg)
            return error_msg

    def list_plugin_versions(self, plugin_name: str) -> List[str]:
        """List all available versions for a plugin"""
        pattern = f"{plugin_name}_*.bak"
        versions = []

        for filename in os.listdir(self.history_dir):
            if filename.startswith(f"{plugin_name}_") and filename.endswith(".bak"):
                # Extract timestamp
                version = filename.replace(f"{plugin_name}_", "").replace(".bak", "")
                versions.append(version)

        return sorted(versions, reverse=True)  # Newest first

    def diff_plugin_versions(
        self, plugin_name: str, version_a: str, version_b: str
    ) -> str:
        """
        Compare two versions of a plugin and show differences.

        Args:
            plugin_name: Name of the plugin
            version_a: First version timestamp
            version_b: Second version timestamp

        Returns:
            str: Unified diff showing changes between versions
        """
        try:
            path_a = os.path.join(self.history_dir, f"{plugin_name}_{version_a}.bak")
            path_b = os.path.join(self.history_dir, f"{plugin_name}_{version_b}.bak")

            if not os.path.exists(path_a):
                return f"❌ Version {version_a} not found for plugin {plugin_name}"
            if not os.path.exists(path_b):
                return f"❌ Version {version_b} not found for plugin {plugin_name}"

            with (
                open(path_a, "r", encoding="utf-8") as f1,
                open(path_b, "r", encoding="utf-8") as f2,
            ):
                lines_a = f1.readlines()
                lines_b = f2.readlines()

            import difflib

            diff = difflib.unified_diff(
                lines_a,
                lines_b,
                fromfile=f"{plugin_name} ({version_a})",
                tofile=f"{plugin_name} ({version_b})",
                lineterm="",
            )
            diff_text = "\n".join(diff)

            if not diff_text.strip():
                return (
                    f"No differences found between versions {version_a} and {version_b}"
                )

            return diff_text

        except Exception as e:
            error_msg = f"Failed to diff plugin versions: {str(e)}"
            self.logger.error(error_msg)
            return error_msg

    # Helper methods
    def _get_plugin_path(self, plugin_name: str) -> str:
        """Get the full path to a plugin file"""
        plugin_path = os.path.join(self.plugin_dir, f"{plugin_name}.py")
        if not os.path.exists(plugin_path):
            raise PluginRewriterError(
                f"Plugin '{plugin_name}' not found at {plugin_path}"
            )
        return plugin_path

    def _read_plugin_code(self, plugin_path: str) -> str:
        """Safely read plugin code with size validation"""
        try:
            with open(plugin_path, "r", encoding="utf-8") as f:
                code = f.read()

            if len(code) > self.max_code_size:
                raise PluginRewriterError(
                    f"Plugin code too large ({len(code)} chars, max {self.max_code_size})"
                )

            return code
        except UnicodeDecodeError:
            raise PluginRewriterError("Plugin file contains invalid UTF-8 encoding")

    def _create_version_backup(
        self, plugin_name: str, code: str, suffix: str = ""
    ) -> str:
        """Create a timestamped backup of plugin code"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{plugin_name}_{timestamp}"
        if suffix:
            backup_name += f"_{suffix}"
        backup_name += ".bak"

        backup_path = os.path.join(self.history_dir, backup_name)

        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(code)

        # Cleanup old backups if too many
        self._cleanup_old_backups(plugin_name)

        return backup_path

    def _cleanup_old_backups(self, plugin_name: str):
        """Remove old backup files if limit exceeded"""
        versions = self.list_plugin_versions(plugin_name)

        if len(versions) > self.max_backup_files:
            # Remove oldest backups
            to_remove = versions[self.max_backup_files :]
            for version in to_remove:
                backup_path = os.path.join(
                    self.history_dir, f"{plugin_name}_{version}.bak"
                )
                if os.path.exists(backup_path):
                    os.remove(backup_path)

    def _extract_plugin_metadata(self, code: str) -> Dict:
        """Extract metadata from plugin code using AST"""
        try:
            tree = ast.parse(code)
            metadata = {
                "functions": [],
                "classes": [],
                "imports": [],
                "docstring": ast.get_docstring(tree),
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metadata["functions"].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    metadata["classes"].append(node.name)
                elif isinstance(node, ast.Import):
                    metadata["imports"].extend([alias.name for alias in node.names])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        metadata["imports"].append(node.module)

            return metadata
        except Exception:
            return {"functions": [], "classes": [], "imports": [], "docstring": None}

    def _validate_python_syntax(self, code: str) -> bool:
        """Validate Python syntax using AST"""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    def _clean_code_response(self, response: str) -> str:
        """Clean AI response to extract only Python code"""
        # Remove markdown code blocks
        response = re.sub(r"^```python\n", "", response, flags=re.MULTILINE)
        response = re.sub(r"^```\n?$", "", response, flags=re.MULTILINE)
        response = response.strip()
        return response

    def _call_openai(self, prompt: str) -> str:
        """Make a safe call to OpenAI API with error handling"""
        try:
            # Use the newer OpenAI client format
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # Lower temperature for more consistent code
                max_tokens=4000,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise PluginRewriterError(f"OpenAI API call failed: {str(e)}")
