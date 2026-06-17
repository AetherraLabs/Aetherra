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
    state_dir = tmp_path / "state"
    monkeypatch.setenv("AETHERRA_STATE_DIR", str(state_dir))
    # Ensure profile set to production for enforcement tests
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    # Reset allow override
    monkeypatch.delenv("AETHERRA_ALLOW_UNBOUNDED", raising=False)
    monkeypatch.delenv("AETHERRA_SAFE_MODE", raising=False)
    monkeypatch.delenv("AETHERRA_KEYS_MASTER", raising=False)
    monkeypatch.delenv("AETHERRA_KEYS_ALLOW_PLAINTEXT", raising=False)
    return


def _keys_file(root: Path) -> Path:
    return root / "keys.json"


def _master_file(root: Path) -> Path:
    return root / "keys_master.key"


def test_auto_provisions_master_key_and_encrypts(tmp_path, monkeypatch):
    # Load module fresh
    api = reload_api_keys()

    # Setting a key should auto-provision master key and encrypt
    api.set_key("openai_api_key", "sk-test")

    state_dir = Path(os.environ["AETHERRA_STATE_DIR"])
    kf = _keys_file(state_dir)
    mf = _master_file(state_dir)
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
    raw = json.loads(_keys_file(Path(os.environ["AETHERRA_STATE_DIR"])).read_text())
    assert raw.get("__encrypted__") is not True
    assert raw.get("ok_plain") == "hello"


def test_encryption_migration_preserves_existing_keys(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "dev")
    monkeypatch.setenv("AETHERRA_KEYS_ALLOW_PLAINTEXT", "1")
    api = reload_api_keys()
    api.set_key("existing_key", "first-secret")

    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    monkeypatch.delenv("AETHERRA_KEYS_ALLOW_PLAINTEXT")
    api.set_key("new_key", "second-secret")

    assert api.get_key("existing_key") == "first-secret"
    assert api.get_key("new_key") == "second-secret"


def test_state_directory_override_is_resolved_at_runtime(monkeypatch, tmp_path):
    api = reload_api_keys()
    second_state = tmp_path / "second-state"
    monkeypatch.setenv("AETHERRA_STATE_DIR", str(second_state))

    api.set_key("runtime_key", "secret")

    assert api.get_keys_file() == second_state.resolve() / "keys.json"
    assert api.get_key("runtime_key") == "secret"


def test_corrupt_store_fails_closed(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "dev")
    api = reload_api_keys()
    api.get_app_dir().mkdir(parents=True)
    api.get_keys_file().write_text("not-json", encoding="utf-8")

    with pytest.raises(api.KeyStoreError, match="unable to read key store"):
        api.get_key("provider_key")


def test_production_scoped_access_is_deny_by_default(monkeypatch):
    api = reload_api_keys()
    api.set_key("provider_key", "secret")

    assert api.get_key_scoped("provider_key", None) is None
    assert api.get_key_scoped("provider_key", "plugin:unknown") is None

    policy_file = api.get_app_dir() / "policy" / "keys_policy.json"
    policy_file.parent.mkdir(parents=True)
    policy_file.write_text(
        json.dumps({"allow": {"plugin:trusted": ["provider_key"]}}),
        encoding="utf-8",
    )
    assert api.get_key_scoped("provider_key", "plugin:trusted") == "secret"


def test_safe_mode_blocks_deletion(monkeypatch):
    api = reload_api_keys()
    api.set_key("provider_key", "secret")
    monkeypatch.setenv("AETHERRA_SAFE_MODE", "1")

    with pytest.raises(RuntimeError, match="safe mode"):
        api.delete_key("provider_key")


@pytest.mark.parametrize("name", ["", "../escape", "has space", "x" * 129])
def test_invalid_key_names_are_rejected(name, monkeypatch):
    api = reload_api_keys()
    with pytest.raises(ValueError, match="invalid key name"):
        api.set_key(name, "secret")
