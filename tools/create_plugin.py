#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Scaffold a new Aetherra plugin package.

Creates a directory under Aetherra/plugins/<target_dir>/<plugin_name>/ with:
  <plugin_name>.py      - Implementation skeleton
  README.md             - Minimal usage docs
  aetherra-plugin.json  - Metadata stub (future extension)

Usage:
  python tools/create_plugin.py my_feature   # creates under plugins/examples/my_feature by default
  python tools/create_plugin.py my_feature --category agent_adapters
  python tools/create_plugin.py my_feature --dir custom-category

Options:
  --category <name>  Use a known top-level category (examples, agent_adapters, memory_hooks, core)
  --dir <name>       Use a custom directory under Aetherra/plugins/
  --force            Overwrite existing files (idempotent otherwise)

The generated class inherits PluginInterface and includes TODO markers.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS_ROOT = ROOT / "Aetherra" / "plugins"
KNOWN_CATEGORIES = {
    "examples",
    "agent_adapters",
    "memory_hooks",
    "core",
    "extra_plugins",
}

IMPL_TEMPLATE = '''# SPDX-License-Identifier: GPL-3.0-or-later
# Auto-generated plugin scaffold (Created {ts})
"""{plugin_name} plugin

Describe purpose: WHAT it does (1 line) and any assumptions.

Safety Notes:
- Document side effects / external calls.
- Avoid network or filesystem writes unless explicitly intended.
"""
from __future__ import annotations
from typing import Any, Dict
import asyncio
from datetime import datetime
from Aetherra.plugins.core.plugin_chain_executor import PluginInterface, PluginResult


class {class_name}(PluginInterface):
    """TODO: Replace with a concise description.

    Capabilities: list semantic verbs or features (e.g., "summarize", "transform").
    """

    def __init__(self, plugin_id: str, *, example_flag: bool = False):
        super().__init__(plugin_id)
        self.capabilities = ["example"]  # TODO adjust
        self.example_flag = example_flag

    async def execute(self, input_data: Any, context: Dict[str, Any]) -> PluginResult:  # type: ignore[override]
        start = datetime.utcnow()
        await asyncio.sleep(0)  # placeholder for async tasks
        output = {{
            "plugin": self.plugin_id,
            "received": input_data,
            "context_keys": sorted(list(context.keys())),
            "example_flag": self.example_flag,
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }}
        return PluginResult(
            plugin_id=self.plugin_id,
            success=True,
            output=output,
            execution_time=(datetime.utcnow() - start).total_seconds(),
            metadata={{"generated": True}}
    )
'''

README_TEMPLATE = """# {class_name} Plugin

Auto-generated scaffold.

## Quick Run

```python
from Aetherra.plugins.core.plugin_chain_executor import PluginChainExecutor, ChainStrategy
from {import_path}.{plugin_name} import {class_name}
import asyncio
async def demo():
    ex = PluginChainExecutor(db_path=':memory:')
    ex.register_plugin({class_name}('{plugin_name}'))
    chain = await ex.execute_chain(['{plugin_name}'], strategy=ChainStrategy.SEQUENTIAL, context={{'demo':True}})
    print(chain.results[0].output)
asyncio.run(demo())
```
"""

META_TEMPLATE = """{{
  "name": "{plugin_name}",
  "description": "TODO: one-line description",
  "version": "0.1.0",
  "created": "{ts}",
  "capabilities": ["example"],
  "license": "GPL-3.0-or-later"
}}
"""


def snake_to_class(name: str) -> str:
    return (
        "".join(part.capitalize() for part in name.replace("-", "_").split("_"))
        + "Plugin"
    )


def sanitize_dir(name: str) -> str:
    return name.replace("-", "_")


def scaffold(
    name: str, category: str | None, directory: str | None, force: bool = False
) -> Path:
    if category and directory:
        raise SystemExit("Use either --category or --dir, not both")
    target_dir = None
    sanitized = sanitize_dir(name)
    if category:
        if category not in KNOWN_CATEGORIES:
            raise SystemExit(
                f"Unknown category {category}; choose from {KNOWN_CATEGORIES}"
            )
        target_dir = PLUGINS_ROOT / category / sanitized
    elif directory:
        target_dir = PLUGINS_ROOT / directory / sanitized
    else:
        target_dir = PLUGINS_ROOT / "examples" / sanitized
    target_dir.mkdir(parents=True, exist_ok=True)
    class_name = snake_to_class(name)
    ts = datetime.utcnow().isoformat() + "Z"
    impl_path = target_dir / f"{sanitized}.py"
    readme_path = target_dir / "README.md"
    meta_path = target_dir / "aetherra-plugin.json"
    if impl_path.exists() and not force:
        print(f"Exists: {impl_path} (use --force to overwrite)")
    else:
        impl_path.write_text(
            IMPL_TEMPLATE.format(plugin_name=name, class_name=class_name, ts=ts),
            encoding="utf-8",
        )
        print(f"Created {impl_path}")
    if readme_path.exists() and not force:
        print(f"Exists: {readme_path}")
    else:
        readme_path.write_text(
            README_TEMPLATE.format(
                class_name=class_name,
                plugin_name=name,
                import_path=str(target_dir.relative_to(ROOT)).replace("\\", "."),
            ),
            encoding="utf-8",
        )
        print(f"Created {readme_path}")
    if meta_path.exists() and not force:
        print(f"Exists: {meta_path}")
    else:
        meta_path.write_text(
            META_TEMPLATE.format(plugin_name=name, ts=ts), encoding="utf-8"
        )
        print(f"Created {meta_path}")
    return target_dir


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--category")
    ap.add_argument("--dir")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)
    scaffold(args.name, args.category, args.dir, args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
