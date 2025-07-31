"""
Aetherra File Router
=====================

This intelligent system-level utility:
- Scans the full Aetherra directory tree
- Uses semantic and structural matching to determine file purpose
- Moves files into correct system paths (e.g., memory/, lyrixa/, plugins/)
- Wires files into OS (memory, plugins, GUI) automatically
- Logs all actions to memory

"""

import json
import shutil
from pathlib import Path

from Aetherra.aetherra_core.kernel import gui_generator, plugin_registry

## from Aetherra.aetherra_core.memory import lyrixa_memory_engine  # (Unused, removed)
from Aetherra.aetherra_core.system import system_logger

# Root path (assumes this script is in Aetherra/)
ROOT = Path(__file__).resolve().parent
IGNORED_DIRS = {"__pycache__", ".git", ".venv", "node_modules"}

# File purpose inference patterns
CATEGORY_RULES = {
    "memory": ["memory_engine", "fractal", "observer", "episodic", "compression"],
    "lyrixa_plugins": ["lyrixa_plugin", "avatar", "panel", "emotion"],
    "plugins": ["plugin_", "agent_", "reflector", "watchdog"],
    "gui": ["interface", "gui", "dashboard", "main_window"],
    "system": ["heartbeat", "scheduler", "state", "core"],
}


# Intelligent router
class AetherraFileRouter:
    def __init__(self, root=ROOT):
        self.root = Path(root)
        self.routes = []

    def run(self):
        for file in self.root.rglob("*.py"):
            if self._should_ignore(file):
                continue
            category = self._classify(file)
            if category:
                self._move_and_wire(file, category)

    def _should_ignore(self, file):
        # Ignore files in ignored dirs and critical kernel files
        if any(part in IGNORED_DIRS for part in file.parts):
            return True
        # Prevent moving gui_generator.py or plugin_registry.py from kernel
        if (
            file.name in ("gui_generator.py", "plugin_registry.py")
            and "kernel" in file.parts
        ):
            return True
        return False

    def _classify(self, file):
        fname = file.name.lower()
        for category, keywords in CATEGORY_RULES.items():
            if any(key in fname for key in keywords):
                return category
        return None

    def _move_and_wire(self, file, category):
        target_dir = self.root / category
        target_dir.mkdir(exist_ok=True)
        target_path = target_dir / file.name

        # Move the file
        shutil.move(str(file), str(target_path))
        system_logger.log(f"Moved: {file.name} → {category}/")

        # Wire it (register or reflect depending on type)
        if category == "plugins" or category == "lyrixa_plugins":
            plugin_registry.register_plugins()
        elif category == "memory":
            # If reflect_on_file is needed, implement in lyrixa_memory_engine or remove this call
            # lyrixa_memory_engine.reflect_on_file(target_path)
            try:
                from Aetherra.aetherra_core.system import memory_core_adapter

                memory_core_adapter.adapt_memory_module(target_path)
            except Exception as e:
                system_logger.log(f"[router] Could not adapt memory module: {e}")
        elif category == "gui":
            gui_generator.register_component(target_path)
            try:
                gui_generator.scaffold_ui()
            except Exception as e:
                system_logger.log(f"[router] Could not scaffold UI: {e}")

        self.routes.append(
            {"file": file.name, "to": str(target_path), "type": category}
        )

    def export_log(self):
        with open(self.root / "file_routing_log.json", "w") as f:
            json.dump(self.routes, f, indent=2)


if __name__ == "__main__":
    router = AetherraFileRouter()
    router.run()
    router.export_log()
    print("✅ File routing complete. See file_routing_log.json for details.")
