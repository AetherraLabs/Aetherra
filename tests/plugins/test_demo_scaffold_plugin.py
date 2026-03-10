# Standard library imports
import importlib
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_plugin_scaffold():
    try:
        mod = importlib.import_module(
            "plugins.demo_scaffold_plugin.demo_scaffold_plugin"
        )
    except ModuleNotFoundError:
        plugin_path = (
            ROOT / "plugins" / "demo_scaffold_plugin" / "demo_scaffold_plugin.py"
        )
        spec = importlib.util.spec_from_file_location(
            "demo_scaffold_plugin_fallback", plugin_path
        )
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore
    cls = mod.DemoScaffoldPlugin
    assert cls().run() == "ok"
