import importlib
import json
import os
import sys
from pathlib import Path

import pytest

MODULE = "Aetherra.security.api_keys"


def reload_api():
    if MODULE in sys.modules:
        del sys.modules[MODULE]
    return importlib.import_module(MODULE)


@pytest.fixture(autouse=True)
def iso_home(monkeypatch, tmp_path):
    fake = tmp_path / "H"
    fake.mkdir()
    monkeypatch.setenv("HOME", str(fake))
    monkeypatch.setenv("USERPROFILE", str(fake))
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    monkeypatch.delenv("AETHERRA_KEYS_MASTER", raising=False)
    monkeypatch.delenv("AETHERRA_KEYS_ALLOW_PLAINTEXT", raising=False)
    yield


def _keys_file():
    return Path(os.path.expanduser("~/.aetherra/keys.json"))


def _master_file():
    return Path(os.path.expanduser("~/.aetherra/keys_master.key"))


def test_set_key_auto_encryption(monkeypatch):
    api = reload_api()
    api.set_key("service_token", "abc123")
    assert _master_file().exists()
    data = json.loads(_keys_file().read_text())
    assert data.get("__encrypted__") is True
    assert isinstance(data.get("service_token"), dict)
    # round trip
    assert api.get_key("service_token") == "abc123"


def test_plaintext_forbidden_without_crypto(monkeypatch):
    api = reload_api()
    # simulate cryptography unavailable
    monkeypatch.setattr(api, "Fernet", None, raising=False)
    with pytest.raises(RuntimeError):
        api.set_key("pkey", "val")


def test_plaintext_override_allowed(monkeypatch):
    monkeypatch.setenv("AETHERRA_KEYS_ALLOW_PLAINTEXT", "1")
    api = reload_api()
    monkeypatch.setattr(api, "Fernet", None, raising=False)
    api.set_key("ok_plain", "value")
    data = json.loads(_keys_file().read_text())
    assert data.get("__encrypted__") is not True
    assert data.get("ok_plain") == "value"
