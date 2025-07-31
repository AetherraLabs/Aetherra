# Minimal gui_generator for Aetherra

from pathlib import Path


def register_component(path):
    print(f"[gui_generator] Registered GUI component: {path}")


def scaffold_ui(gui_dir=None):
    gui_dir = gui_dir or Path(__file__).parent.parent / "gui"
    components = []
    for file in gui_dir.glob("*.py"):
        components.append(file.name)
    print(f"[gui_generator] Scaffolded UI components: {components}")
    return components
