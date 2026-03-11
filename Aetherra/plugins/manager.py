#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""Plugins Manager (Phase 3 roadmap module).

Provides lightweight discovery, manifest validation, loading, and capability
execution for plugins in `Aetherra/plugins/`.
"""

from __future__ import annotations

# Standard library imports
import importlib
import importlib.util
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# Local imports
from .manifest_schema import validate_manifest


@dataclass
class PluginRecord:
    name: str
    path: Path
    manifest: Dict[str, Any] = field(default_factory=dict)
    loaded: bool = False
    instance: Any = None
    errors: List[str] = field(default_factory=list)


class PluginManager:
    """Production-facing plugin manager for the roadmap Phase 3 target."""

    def __init__(self, plugins_dir: str | Path | None = None) -> None:
        base = Path(plugins_dir) if plugins_dir else Path(__file__).resolve().parent
        self.plugins_dir = base
        self.registry: Dict[str, PluginRecord] = {}

    def discover_plugins(self) -> List[str]:
        """Discover plugin modules and manifest-backed plugin directories."""
        discovered: List[str] = []

        # Single-file plugin modules in plugins root
        for py in self.plugins_dir.glob("*.py"):
            if py.name.startswith("__") or py.stem in {"manager", "manifest_schema", "ai_plugin_generator_v2"}:
                continue
            name = py.stem
            self.registry.setdefault(name, PluginRecord(name=name, path=py))
            discovered.append(name)

        # Directory plugins with plugin.json
        for d in self.plugins_dir.iterdir():
            if not d.is_dir():
                continue
            manifest = d / "plugin.json"
            if not manifest.exists():
                continue
            name = d.name
            rec = self.registry.setdefault(name, PluginRecord(name=name, path=d))
            rec.manifest = self._load_manifest(manifest)
            discovered.append(name)

        return sorted(set(discovered))

    def validate_plugin(self, plugin_name: str) -> tuple[bool, List[str]]:
        """Validate plugin manifest if present."""
        rec = self.registry.get(plugin_name)
        if rec is None:
            return False, ["plugin_not_discovered"]

        if not rec.manifest:
            # File-based legacy plugin: no strict manifest required.
            return True, []

        ok, errors, normalized = validate_manifest(rec.manifest)
        if ok:
            rec.manifest = normalized
            rec.errors = []
        else:
            rec.errors = list(errors)
        return ok, rec.errors

    def load_plugin(self, plugin_name: str) -> bool:
        """Load plugin module and instantiate Plugin class if present."""
        rec = self.registry.get(plugin_name)
        if rec is None:
            return False

        # Validate first if manifest exists
        ok, errors = self.validate_plugin(plugin_name)
        if not ok:
            rec.loaded = False
            rec.errors = errors
            return False

        try:
            mod = self._import_plugin_module(rec)
            instance = None

            if hasattr(mod, "PLUGIN_CLASS") and isinstance(getattr(mod, "PLUGIN_CLASS"), type):
                instance = mod.PLUGIN_CLASS()
            elif hasattr(mod, "Plugin") and isinstance(getattr(mod, "Plugin"), type):
                instance = mod.Plugin()
            else:
                # Module-level fallback
                instance = mod

            rec.instance = instance
            rec.loaded = True
            rec.errors = []
            return True
        except Exception as exc:
            rec.loaded = False
            rec.errors = [f"load_error: {exc}"]
            return False

    def execute_capability(self, plugin_name: str, capability: str, **kwargs) -> Any:
        """Execute a capability on a loaded plugin.

        Resolution order:
        1) method named exactly capability
        2) execute_action(capability, **kwargs)
        3) execute(capability=..., **kwargs)
        """
        rec = self.registry.get(plugin_name)
        if rec is None or not rec.loaded or rec.instance is None:
            raise RuntimeError(f"Plugin '{plugin_name}' is not loaded")

        target = rec.instance
        if hasattr(target, capability) and callable(getattr(target, capability)):
            return getattr(target, capability)(**kwargs)

        if hasattr(target, "execute_action") and callable(getattr(target, "execute_action")):
            return target.execute_action(capability, **kwargs)

        if hasattr(target, "execute") and callable(getattr(target, "execute")):
            return target.execute(capability=capability, **kwargs)

        raise AttributeError(
            f"Capability '{capability}' not found for plugin '{plugin_name}'"
        )

    def unload_plugin(self, plugin_name: str) -> bool:
        rec = self.registry.get(plugin_name)
        if rec is None:
            return False
        rec.instance = None
        rec.loaded = False
        return True

    def list_plugins(self, include_unloaded: bool = True) -> List[Dict[str, Any]]:
        out = []
        for rec in self.registry.values():
            if not include_unloaded and not rec.loaded:
                continue
            out.append(
                {
                    "name": rec.name,
                    "path": str(rec.path),
                    "loaded": rec.loaded,
                    "errors": list(rec.errors),
                    "capabilities": list(rec.manifest.get("capabilities", [])) if rec.manifest else [],
                }
            )
        return sorted(out, key=lambda x: x["name"])

    def _load_manifest(self, path: Path) -> Dict[str, Any]:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _import_plugin_module(self, rec: PluginRecord):
        # Directory plugin entry via manifest
        if rec.path.is_dir() and rec.manifest:
            entry_point = rec.manifest.get("entry_point", "")
            if entry_point:
                module_name = entry_point.split(":", 1)[0]
                return importlib.import_module(module_name)

            # Fallback to <dir>/<dir>.py
            candidate = rec.path / f"{rec.name}.py"
            if candidate.exists():
                return self._import_by_path(candidate, f"aetherra_plugin_{rec.name}")

        # File plugin
        if rec.path.is_file() and rec.path.suffix == ".py":
            try:
                # Try package import first
                return importlib.import_module(f"Aetherra.plugins.{rec.name}")
            except Exception:
                return self._import_by_path(rec.path, f"aetherra_plugin_{rec.name}")

        raise ImportError(f"Unable to import plugin from path: {rec.path}")

    @staticmethod
    def _import_by_path(path: Path, module_name: str):
        spec = importlib.util.spec_from_file_location(module_name, str(path))
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot create import spec for {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


PLUGIN_MANAGER_SINGLETON: Optional[PluginManager] = None


def get_plugin_manager(plugins_dir: str | Path | None = None) -> PluginManager:
    global PLUGIN_MANAGER_SINGLETON
    if PLUGIN_MANAGER_SINGLETON is None:
        PLUGIN_MANAGER_SINGLETON = PluginManager(plugins_dir=plugins_dir)
    return PLUGIN_MANAGER_SINGLETON
