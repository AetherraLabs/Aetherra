# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Aetherra Plugin Registry
Handles plugin discovery, metadata loading, and dynamic registration into the Aetherra OS.
"""

# Standard library imports
import json
import re
from pathlib import Path
from typing import Dict, List

PLUGIN_DIR = Path(__file__).parent
PLUGINS_ROOT = PLUGIN_DIR.parent.parent.parent / "plugins"  # repo_root/plugins


def _load_registered_index() -> list[str]:
    idx = PLUGIN_DIR / "registered_plugins.json"
    if idx.exists():
        try:
            data = json.loads(idx.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return list(data.get("plugins", []))
        except Exception:
            return []
    return []


SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?$")


def _validate_manifest(manifest: Dict) -> List[str]:
    warnings: List[str] = []
    required = ["name", "version", "description", "entry", "phase"]
    for key in required:
        if key not in manifest:
            warnings.append(f"missing_field:{key}")
    version = manifest.get("version")
    if isinstance(version, str) and not SEMVER_RE.match(version):
        warnings.append("invalid_version_semver")
    entry = manifest.get("entry") or manifest.get("entry_point")
    if entry and (":" not in entry):
        warnings.append("invalid_entry_format")
    if manifest.get("phase") not in (0, 1, 2, 3, 4, 5, 6):
        warnings.append("unknown_phase")
    return warnings


def discover_plugins() -> Dict[str, Dict]:
    """Discover plugins by scanning plugins/ folder and manifests.

    Preference order:
      1. registered_plugins.json (explicit list) if present
      2. all directories under plugins/ containing plugin.json
    Returns mapping plugin_name -> manifest dict (minimal fields if load fails).
    """
    discovered: Dict[str, Dict] = {}
    candidates = []
    explicit = _load_registered_index()
    if explicit:
        candidates = explicit
    else:
        if PLUGINS_ROOT.exists():
            for p in PLUGINS_ROOT.iterdir():
                if p.is_dir() and (p / "plugin.json").exists():
                    candidates.append(p.name)
    for name in candidates:
        try:
            manifest = load_plugin_manifest(name)
        except Exception:
            manifest = {"name": name, "error": "manifest load failed"}
    # store list of warning codes
    manifest["validation_warnings"] = list(_validate_manifest(manifest))
    discovered[name] = manifest  # type: ignore[index]
    return discovered


def load_plugin_manifest(plugin_name: str) -> Dict:
    """Load plugin manifest supporting root plugins/ and core path fallback."""
    # Preferred: root plugins directory
    primary = PLUGINS_ROOT / plugin_name / "plugin.json"
    alt1 = PLUGINS_ROOT / plugin_name / "manifest.json"
    core_path = PLUGIN_DIR / plugin_name / "manifest.json"
    for path in (primary, alt1, core_path):
        if path.exists():
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
                data.setdefault("_path", str(path))
                return data
    raise FileNotFoundError(f"Plugin {plugin_name} missing manifest.json/plugin.json")


def register_plugins() -> Dict[str, Dict]:
    """Discover and register all available plugins (alias to discover)."""
    return discover_plugins()


if __name__ == "__main__":
    print(register_plugins())
