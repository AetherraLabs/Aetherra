# Standard library imports
import importlib
import json
import os
import sys
from pathlib import Path

# Third party imports
import pytest

MODULE = "Aetherra.security.api_keys"


def reload_api_keys():
    if MODULE in sys.modules:
        del sys.modules[MODULE]
    return importlib.import_module(MODULE)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch, tmp_path):
    # Isolate ~/.aetherra
    fake_home = tmp_path / "HOME"
    fake_home.mkdir(parents=True)
    monkeypatch.setenv("USERPROFILE", str(fake_home))
    monkeypatch.setenv("HOME", str(fake_home))
    # Ensure profile set to production for enforcement tests
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    # Reset allow override
    monkeypatch.delenv("AETHERRA_ALLOW_UNBOUNDED", raising=False)
    monkeypatch.delenv("AETHERRA_KEYS_MASTER", raising=False)
    monkeypatch.delenv("AETHERRA_KEYS_ALLOW_PLAINTEXT", raising=False)
    return


def _keys_file(root: Path) -> Path:
    return root / ".aetherra" / "keys.json"


def _master_file(root: Path) -> Path:
    return root / ".aetherra" / "keys_master.key"


def test_auto_provisions_master_key_and_encrypts(tmp_path, monkeypatch):
    # Load module fresh
    api = reload_api_keys()

    # Setting a key should auto-provision master key and encrypt
    api.set_key("openai_api_key", "sk-test")

    kf = _keys_file(Path(os.path.expanduser("~")))
    mf = _master_file(Path(os.path.expanduser("~")))
    assert mf.exists(), "master key should be created in prod"
    raw = json.loads(kf.read_text())
    assert raw.get("__encrypted__") is True
    assert isinstance(raw.get("openai_api_key"), dict)
    assert "cipher" in raw["openai_api_key"]

    # Retrieval should work
    val = api.get_key("openai_api_key")
    assert val == "sk-test"


def test_refuse_plaintext_when_cryptography_missing(tmp_path, monkeypatch):
    # Simulate cryptography not installed by forcing Fernet to None
    api = reload_api_keys()
    monkeypatch.setattr(api, "Fernet", None, raising=False)
    # Now attempt set should raise in prod
    with pytest.raises(RuntimeError):
        api.set_key("provider_key", "value123")


def test_plaintext_allowed_only_with_override(tmp_path, monkeypatch):
    monkeypatch.setenv("AETHERRA_KEYS_ALLOW_PLAINTEXT", "1")
    api = reload_api_keys()
    # No Fernet in this scenario -> plaintext path
    monkeypatch.setattr(api, "Fernet", None, raising=False)
    # Should not raise
    api.set_key("ok_plain", "hello")
    raw = json.loads(_keys_file(Path(os.path.expanduser("~"))).read_text())
    assert raw.get("__encrypted__") is not True
    assert raw.get("ok_plain") == "hello"
