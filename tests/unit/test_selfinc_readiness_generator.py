# Standard library imports
import json
import subprocess
import sys
from pathlib import Path

META = Path("metadata/selfinc_readiness.json")
SCRIPT = Path("tools/generate_selfinc_readiness_doc.py")
OUT = Path("docs/SELFINC_PRODUCTION_READINESS_GENERATED.md")


def test_generator_creates_doc(tmp_path):
    assert META.exists(), "Metadata file missing"
    assert SCRIPT.exists(), "Generator script missing"
    # Run generator
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--meta", str(META), "--out", str(OUT)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    text = OUT.read_text(encoding="utf-8")
    # Required sections
    for marker in [
        "## 2. Validation Dimensions",
        "## 3. Environment Variables",
        "## 4. HTTP API",
        "## 5. Risk Register",
        "## 6. Phase 2 Items",
    ]:
        assert marker in text, f"Missing section: {marker}"
    # Spot check a dimension name from metadata
    meta = json.loads(META.read_text(encoding="utf-8"))
    first_dim = meta["dimensions"][0]["name"]
    assert first_dim.split()[0] in text
