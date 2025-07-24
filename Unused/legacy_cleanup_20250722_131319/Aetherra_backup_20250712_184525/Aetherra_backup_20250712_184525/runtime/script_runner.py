# aetherra/runtime/script_runner.py

import json
import os

from Aetherra.runtime.aether_runtime import AetherRuntime


class ScriptRunner:
    def __init__(self, registry_path="Aetherra/scripts/script_registry.json"):
        self.registry_path = registry_path
        self.registry = self._load_registry()

    def _load_registry(self):
        if not os.path.exists(self.registry_path):
            raise FileNotFoundError(
                f"Standard library registry not found: {self.registry_path}"
            )
        with open(self.registry_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_scripts(self):
        scripts = []
        for script_name, script_data in self.registry.get("scripts", {}).items():
            scripts.append(
                {
                    "name": script_name,
                    "description": script_data["description"],
                    "category": script_data["category"],
                    "tags": script_data["tags"],
                }
            )
        return scripts

    def get_script_path(self, name):
        scripts = self.registry.get("scripts", {})
        if name in scripts:
            return scripts[name]["path"]
        raise ValueError(f"Script '{name}' not found in registry.")

    def run_script(self, name, context):
        path = self.get_script_path(name)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Script not found at path: {path}")

        runtime = AetherRuntime()
        runtime.register_context(
            memory=context.get("memory"),
            plugins=context.get("plugins"),
            agents=context.get("agents"),
        )
        runtime.load_script(path)
        runtime.execute()

        return f"✅ Script '{name}' executed successfully."


# Example usage (in CLI or Lyrixa shell)
if __name__ == "__main__":
    runner = ScriptRunner()
    print("Available Scripts:")
    for script in runner.list_scripts():
        print(f"- {script['name']}: {script['description']}")
