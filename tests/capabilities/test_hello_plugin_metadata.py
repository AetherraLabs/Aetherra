# Standard library imports
import json
from pathlib import Path

REQUIRED_KEYS = {"name", "version", "capabilities", "license", "entry_point"}


def test_hello_plugin_metadata_basic():
    meta_path = Path("Aetherra/plugins/examples/hello_plugin/aetherra-plugin.json")
    assert meta_path.exists(), "Metadata file missing for hello plugin"
    data = json.loads(meta_path.read_text())
    missing = REQUIRED_KEYS - data.keys()
    assert not missing, f"Missing required metadata keys: {missing}"
    assert data["name"] == "hello_plugin"
    assert isinstance(data["capabilities"], list) and data["capabilities"], (
        "Capabilities list must be non-empty"
    )
    assert data["entry_point"].endswith(":HelloPlugin")
