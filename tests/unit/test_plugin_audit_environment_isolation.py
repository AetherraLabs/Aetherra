"""Lockdown tests must restore their environment before later signing work."""

# Standard library imports
import os
import subprocess
import sys
from pathlib import Path

# Third party imports
import pytest

ROOT = Path(__file__).resolve().parents[2]
PROBE = """
import os
from pathlib import Path

import pytest

original = os.environ.get("AETHERRA_SAFE_MODE")
state = Path(os.environ["AETHERRA_STATE_DIR"])
result = pytest.main([
    "-q", "-o", "addopts=", "-p", "no:cacheprovider",
    "--basetemp", str(state.parent / "nested-pytest"),
    "tests/unit/test_plugin_manager_audit.py::test_emergency_lockdown_enables_safe_mode",
    "tests/unit/test_plugin_manager_audit.py::test_lockdown_recovery_fails_closed_when_audit_is_tampered",
])
assert result == 0, "lockdown contracts failed"
assert os.environ.get("AETHERRA_SAFE_MODE") == original, "safe-mode environment leaked"

from Aetherra.security.api_keys import get_key, get_keys_file, set_key
from Aetherra.security.plugin_signing import generate_keypair, sign_manifest, verify_plugin_signature

assert get_keys_file().is_relative_to(state)
if original == "1":
    with pytest.raises(RuntimeError, match="safe mode"):
        set_key("plugin_signing_secret", "synthetic-blocked-key")
    assert not get_keys_file().exists()
else:
    public, secret = generate_keypair()
    set_key("plugin_signing_secret", secret)
    assert get_key("plugin_signing_secret") == secret
    signed = sign_manifest({"name": "isolated", "version": "1.0.0"}, secret)
    assert signed["pubkey"] == public
    assert signed["signature"]
    assert verify_plugin_signature(signed)
"""


@pytest.mark.parametrize("safe_mode", [None, "", "0", "1"])
def test_lockdown_suite_restores_safe_mode_before_signing(tmp_path, safe_mode):
    environment = {
        name: value
        for name, value in os.environ.items()
        if name.upper() in {"SYSTEMROOT", "WINDIR", "PATH", "TEMP", "TMP", "COMSPEC"}
    }
    environment.update(
        AETHERRA_SKIP_DOTENV="1",
        AETHERRA_LYRIXA_FORCE_OFFLINE="1",
        AETHERRA_STATE_DIR=str(tmp_path / "state"),
        AETHERRA_WORKSPACE_ROOT=str(tmp_path / "workspace"),
        AETHERRA_PROFILE="test",
        AETHERRA_SIGNING_STRICT="1",
        PYTHONDONTWRITEBYTECODE="1",
        PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
    )
    if safe_mode is not None:
        environment["AETHERRA_SAFE_MODE"] = safe_mode
    result = subprocess.run(
        [sys.executable, "-c", PROBE],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "nested-pytest").is_dir()
