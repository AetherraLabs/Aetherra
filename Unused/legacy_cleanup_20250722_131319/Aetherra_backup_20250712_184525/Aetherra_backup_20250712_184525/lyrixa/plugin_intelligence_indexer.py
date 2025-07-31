#!/usr/bin/env python3
"""
Plugin Intelligence Indexer
==========================

Scans all plugins, extracts metadata (capabilities, schemas, dependencies), and stores indexed info for fast search and reasoning.
"""

import importlib.util
import os
from typing import Any, Dict, List

PLUGIN_DIRS = [
    os.path.join(os.getcwd(), "plugins"),
    os.path.join(os.getcwd(), "lyrixa", "plugins"),
]


def scan_plugin_file(filepath: str) -> Dict[str, Any]:
    """Extract metadata from a plugin file (best effort)."""
    meta = {
        "file": filepath,
        "name": None,
        "capabilities": [],
        "schemas": {},
        "dependencies": [],
        "errors": [],
    }
    try:
        spec = importlib.util.spec_from_file_location("plugin_module", filepath)
        if spec is not None and spec.loader is not None:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # Try to extract metadata from known attributes/classes
            for attr in dir(module):
                obj = getattr(module, attr)
                if hasattr(obj, "name") and isinstance(obj.name, str):
                    meta["name"] = obj.name
                if hasattr(obj, "capabilities"):
                    meta["capabilities"] = getattr(obj, "capabilities")
                if hasattr(obj, "input_schema"):
                    meta.setdefault("schemas", {})["input"] = getattr(
                        obj, "input_schema"
                    )
                if hasattr(obj, "output_schema"):
                    meta.setdefault("schemas", {})["output"] = getattr(
                        obj, "output_schema"
                    )
                if hasattr(obj, "dependencies"):
                    meta["dependencies"] = getattr(obj, "dependencies")
        else:
            meta["errors"].append("Could not load spec or loader for file: " + filepath)
    except Exception as e:
        meta["errors"].append(str(e))
    return meta


def index_all_plugins() -> List[Dict[str, Any]]:
    """Scan all plugin directories and index plugin metadata."""
    index = []
    for plugin_dir in PLUGIN_DIRS:
        if not os.path.exists(plugin_dir):
            continue
        for fname in os.listdir(plugin_dir):
            if fname.endswith(".py") and not fname.startswith("__"):
                fpath = os.path.join(plugin_dir, fname)
                meta = scan_plugin_file(fpath)
                index.append(meta)
    return index


def get_plugin_capability_index() -> List[Dict[str, Any]]:
    """Get the indexed plugin metadata (capabilities, schemas, etc)."""
    return index_all_plugins()


if __name__ == "__main__":
    import json

    index = get_plugin_capability_index()
    print(json.dumps(index, indent=2))
