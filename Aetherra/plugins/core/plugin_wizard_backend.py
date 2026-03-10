"""
Plugin Wizard Backend - Headless multi-step wizard for plugin creation.

Provides a code-generation pipeline for creating structured plugins
without any UI dependency. Steps: basic_info → type_selection →
capabilities → dependencies → code → manifest.

Example:
    >>> wizard = PluginWizardBackend()
    >>> wizard.set_basic_info("my_plugin", "Does something useful", "author")
    >>> wizard.set_type("processor")
    >>> wizard.set_capabilities(["data-transform"])
    >>> result = wizard.finalize()
    >>> print(result.plugin_code)
    >>> print(result.manifest_json)
"""

import json
import textwrap
from dataclasses import dataclass, field
from typing import List, Optional


# ──────────────────────────────────────────────────────────────────────────────
# Templates
# ──────────────────────────────────────────────────────────────────────────────

_PLUGIN_TEMPLATE = '''\
"""
{name} - {description}

Author: {author}
Version: {version}
Category: {category}
"""

from Aetherra.plugins.core.plugin_sdk import PluginMetadata, register_plugin


METADATA = PluginMetadata(
    name="{name}",
    description="{description}",
    author="{author}",
    version="{version}",
    category="{category}",
    capabilities={capabilities_repr},
    dependencies={dependencies_repr},
)

register_plugin("{name}", METADATA)


class {class_name}:
    """Main plugin class for {name}."""

{methods}
'''

_PROCESSOR_METHOD = '''\
    def process(self, data):
        """Process input data and return result."""
        # TODO: Implement processing logic
        return data
'''

_ANALYZER_METHOD = '''\
    def analyze(self, data):
        """Analyze input data and return insights."""
        # TODO: Implement analysis logic
        return {"result": None, "data": data}
'''

_CONNECTOR_METHOD = '''\
    def connect(self, config):
        """Establish connection using config."""
        # TODO: Implement connection logic
        pass

    def disconnect(self):
        """Close the connection."""
        pass
'''

_FILTER_METHOD = '''\
    def filter(self, data, criteria=None):
        """Filter input data by criteria."""
        # TODO: Implement filtering logic
        return data
'''

_GENERIC_METHOD = '''\
    def run(self, *args, **kwargs):
        """Main entry point for plugin."""
        # TODO: Implement plugin logic
        pass
'''

_PLUGIN_TYPE_METHODS = {
    "processor": _PROCESSOR_METHOD,
    "analyzer": _ANALYZER_METHOD,
    "connector": _CONNECTOR_METHOD,
    "filter": _FILTER_METHOD,
    "generic": _GENERIC_METHOD,
}

_MANIFEST_TEMPLATE = {
    "name": "{name}",
    "version": "{version}",
    "description": "{description}",
    "author": "{author}",
    "category": "{category}",
    "entry": "{entry}",
    "phase": "post_init",
    "capabilities": [],
    "dependencies": [],
    "tags": [],
    "hooks": [],
}


# ──────────────────────────────────────────────────────────────────────────────
# Data classes
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class WizardResult:
    """Result produced by the wizard after finalization."""

    plugin_code: str
    """Generated Python source code"""
    manifest_json: str
    """Generated manifest JSON string"""
    manifest_dict: dict = field(default_factory=dict)
    """Manifest as dictionary"""
    plugin_name: str = ""
    """Plugin name used"""
    suggested_filename: str = ""
    """Suggested filename for the plugin module"""

    def __post_init__(self):
        if not self.manifest_dict and self.manifest_json:
            try:
                self.manifest_dict = json.loads(self.manifest_json)
            except (json.JSONDecodeError, TypeError):
                pass


@dataclass
class ValidationError:
    """A single validation error with step context."""

    step: str
    message: str


class WizardValidationError(Exception):
    """Raised when wizard state fails validation."""

    def __init__(self, errors: List[ValidationError]):
        self.errors = errors
        messages = "; ".join(f"[{e.step}] {e.message}" for e in errors)
        super().__init__(f"Wizard validation failed: {messages}")


# ──────────────────────────────────────────────────────────────────────────────
# Wizard
# ──────────────────────────────────────────────────────────────────────────────

class PluginWizardBackend:
    """
    Headless multi-step plugin creation wizard.

    Call ``set_basic_info()``, ``set_type()``, ``set_capabilities()``,
    ``set_dependencies()``, and optionally ``set_tags()`` / ``set_hooks()``
    before calling ``finalize()`` to produce a ``WizardResult``.
    """

    SUPPORTED_TYPES = set(_PLUGIN_TYPE_METHODS.keys())

    def __init__(self):
        self._name: str = ""
        self._description: str = ""
        self._author: str = "Unknown"
        self._version: str = "1.0.0"
        self._category: str = "general"
        self._plugin_type: str = "generic"
        self._capabilities: List[str] = []
        self._dependencies: List[str] = []
        self._tags: List[str] = []
        self._hooks: List[str] = []
        self._step_order: List[str] = []
        self._current_step: int = 0

    # ── Step setters ──────────────────────────────────────────────────────────

    def set_basic_info(
        self,
        name: str,
        description: str = "",
        author: str = "Unknown",
        version: str = "1.0.0",
        category: str = "general",
    ) -> "PluginWizardBackend":
        """
        Step 1 — Set basic plugin information.

        Args:
            name: Plugin identifier (alphanumeric + underscore)
            description: Short description
            author: Author name
            version: Semantic version string
            category: Category string

        Returns:
            Self for chaining
        """
        self._name = name.strip()
        self._description = description.strip()
        self._author = author.strip() or "Unknown"
        self._version = version.strip() or "1.0.0"
        self._category = category.strip() or "general"
        if "basic_info" not in self._step_order:
            self._step_order.append("basic_info")
        return self

    def set_type(self, plugin_type: str) -> "PluginWizardBackend":
        """
        Step 2 — Set plugin type.

        Args:
            plugin_type: One of ``processor``, ``analyzer``, ``connector``,
                         ``filter``, or ``generic``

        Returns:
            Self for chaining

        Raises:
            ValueError: If type is not supported
        """
        if plugin_type not in self.SUPPORTED_TYPES:
            raise ValueError(
                f"Unsupported type '{plugin_type}'. Choose from: "
                + ", ".join(sorted(self.SUPPORTED_TYPES))
            )
        self._plugin_type = plugin_type
        if "type_selection" not in self._step_order:
            self._step_order.append("type_selection")
        return self

    def set_capabilities(self, capabilities: List[str]) -> "PluginWizardBackend":
        """
        Step 3 — Set plugin capabilities.

        Args:
            capabilities: List of capability strings

        Returns:
            Self for chaining
        """
        self._capabilities = [c.strip() for c in capabilities if c.strip()]
        if "capabilities" not in self._step_order:
            self._step_order.append("capabilities")
        return self

    def set_dependencies(self, dependencies: List[str]) -> "PluginWizardBackend":
        """
        Step 4 — Set plugin dependencies.

        Args:
            dependencies: List of other plugin names this plugin depends on

        Returns:
            Self for chaining
        """
        self._dependencies = [d.strip() for d in dependencies if d.strip()]
        if "dependencies" not in self._step_order:
            self._step_order.append("dependencies")
        return self

    def set_tags(self, tags: List[str]) -> "PluginWizardBackend":
        """Set searchable tags."""
        self._tags = [t.strip() for t in tags if t.strip()]
        return self

    def set_hooks(self, hooks: List[str]) -> "PluginWizardBackend":
        """Set lifecycle hook names the plugin registers."""
        self._hooks = [h.strip() for h in hooks if h.strip()]
        return self

    # ── Validation ────────────────────────────────────────────────────────────

    def validate(self) -> List[ValidationError]:
        """
        Validate current wizard state.

        Returns:
            List of ValidationError (empty if valid)
        """
        errors: List[ValidationError] = []

        if not self._name:
            errors.append(ValidationError("basic_info", "Plugin name is required"))
        elif not self._name.replace("_", "").replace("-", "").isalnum():
            errors.append(
                ValidationError("basic_info", "Name must be alphanumeric (underscores/dashes allowed)")
            )

        if not self._description:
            errors.append(ValidationError("basic_info", "Description is required"))

        if self._plugin_type not in self.SUPPORTED_TYPES:
            errors.append(
                ValidationError("type_selection", f"Unsupported type: {self._plugin_type}")
            )

        # Validate version format (basic semver: x.y.z)
        parts = self._version.split(".")
        if len(parts) < 2 or not all(p.isdigit() for p in parts):
            errors.append(
                ValidationError("basic_info", f"Invalid version format: {self._version}")
            )

        return errors

    # ── Code + manifest generation ────────────────────────────────────────────

    def generate_plugin_code(self) -> str:
        """
        Generate Python source code for the plugin.

        Returns:
            Formatted Python source string
        """
        class_name = _to_class_name(self._name)
        methods = _PLUGIN_TYPE_METHODS.get(self._plugin_type, _GENERIC_METHOD)

        code = _PLUGIN_TEMPLATE.format(
            name=self._name,
            description=self._description,
            author=self._author,
            version=self._version,
            category=self._category,
            class_name=class_name,
            capabilities_repr=repr(self._capabilities),
            dependencies_repr=repr(self._dependencies),
            methods=methods,
        )
        return code

    def generate_manifest(self) -> dict:
        """
        Generate plugin manifest dictionary.

        Returns:
            Dict suitable for writing as ``plugin.json``
        """
        entry_module = f"Aetherra.plugins.{self._category}.{self._name}"
        manifest = {
            "name": self._name,
            "version": self._version,
            "description": self._description,
            "author": self._author,
            "category": self._category,
            "entry": entry_module,
            "phase": "post_init",
            "capabilities": list(self._capabilities),
            "dependencies": list(self._dependencies),
            "tags": list(self._tags),
            "hooks": list(self._hooks),
        }
        return manifest

    def finalize(self) -> WizardResult:
        """
        Validate state and produce the final WizardResult.

        Returns:
            WizardResult with plugin_code and manifest_json

        Raises:
            WizardValidationError: If the wizard state is invalid
        """
        errors = self.validate()
        if errors:
            raise WizardValidationError(errors)

        code = self.generate_plugin_code()
        manifest = self.generate_manifest()
        manifest_json = json.dumps(manifest, indent=2)
        filename = f"{self._name}.py"

        return WizardResult(
            plugin_code=code,
            manifest_json=manifest_json,
            manifest_dict=manifest,
            plugin_name=self._name,
            suggested_filename=filename,
        )

    # ── Introspection ─────────────────────────────────────────────────────────

    def get_state(self) -> dict:
        """Return current wizard state as dictionary."""
        return {
            "name": self._name,
            "description": self._description,
            "author": self._author,
            "version": self._version,
            "category": self._category,
            "plugin_type": self._plugin_type,
            "capabilities": list(self._capabilities),
            "dependencies": list(self._dependencies),
            "tags": list(self._tags),
            "hooks": list(self._hooks),
            "steps_completed": list(self._step_order),
        }

    def reset(self) -> "PluginWizardBackend":
        """Reset wizard to initial state."""
        self.__init__()
        return self


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _to_class_name(plugin_name: str) -> str:
    """Convert plugin_name to CamelCase class name."""
    return "".join(part.capitalize() for part in plugin_name.replace("-", "_").split("_"))
