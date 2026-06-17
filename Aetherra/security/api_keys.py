# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""Local API-key storage with encryption-at-rest and scoped retrieval."""

from __future__ import annotations

import contextlib
import json
import os
import re
import tempfile
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    from cryptography.fernet import Fernet  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    Fernet = None  # type: ignore


class KeyStoreError(RuntimeError):
    """Raised when the local key store cannot be read or written safely."""


_KEY_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
_LOCK = threading.RLock()
_cache: dict[str, Any] | None = None
_cache_path: Path | None = None
_fernet: Any | None = None
_fernet_source: tuple[str | None, Path] | None = None


def get_app_dir() -> Path:
    """Return the current state directory, honoring runtime overrides."""
    override = os.getenv("AETHERRA_STATE_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return Path(os.path.expanduser("~/.aetherra")).resolve()


def get_keys_file() -> Path:
    return get_app_dir() / "keys.json"


def get_master_key_file() -> Path:
    return get_app_dir() / "keys_master.key"


# Compatibility snapshots. New code should use the accessors above because
# AETHERRA_STATE_DIR may be changed after this module is imported.
APP_DIR = get_app_dir()
KEYS_FILE = get_keys_file()
MASTER_KEY_FILE = get_master_key_file()


def _validate_name(name: str) -> str:
    if not isinstance(name, str) or not _KEY_NAME_RE.fullmatch(name):
        raise ValueError("invalid key name")
    return name


def _safe_mode_enabled() -> bool:
    try:
        from Aetherra.aetherra_core.system.security_system import is_safe_mode_enabled

        return is_safe_mode_enabled()
    except (ImportError, AttributeError):
        return (os.getenv("AETHERRA_SAFE_MODE", "") or "").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }


def _ensure() -> None:
    app_dir = get_app_dir()
    keys_file = get_keys_file()
    try:
        app_dir.mkdir(parents=True, exist_ok=True)
        if not keys_file.exists():
            _atomic_write(keys_file, "{}")
        with contextlib.suppress(OSError):
            os.chmod(app_dir, 0o700)
            os.chmod(keys_file, 0o600)
    except OSError as exc:
        raise KeyStoreError(f"unable to initialize key store: {exc}") from exc

    profile = (os.getenv("AETHERRA_PROFILE", "") or "").strip().lower()
    allow_plain = os.getenv("AETHERRA_KEYS_ALLOW_PLAINTEXT", "0") == "1"
    if (
        profile in {"prod", "production", "staging"}
        and not allow_plain
        and Fernet is not None
        and not os.getenv("AETHERRA_KEYS_MASTER")
        and not get_master_key_file().exists()
    ):
        ensure_master_key()


def _atomic_write(path: Path, content: str | bytes) -> None:
    """Atomically replace a sensitive file in its destination directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    binary = isinstance(content, bytes)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        mode = "wb" if binary else "w"
        kwargs = {} if binary else {"encoding": "utf-8", "newline": "\n"}
        with os.fdopen(fd, mode, **kwargs) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        with contextlib.suppress(OSError):
            os.chmod(temporary_path, 0o600)
        os.replace(temporary_path, path)
    except Exception:
        with contextlib.suppress(OSError):
            temporary_path.unlink()
        raise


def _load_master_key() -> bytes | None:
    env_key = os.getenv("AETHERRA_KEYS_MASTER")
    if env_key:
        return env_key.encode("utf-8")
    master_file = get_master_key_file()
    if not master_file.exists():
        return None
    try:
        return master_file.read_bytes().strip()
    except OSError as exc:
        raise KeyStoreError(f"unable to read master key: {exc}") from exc


def _get_fernet() -> Any | None:
    global _fernet, _fernet_source
    if Fernet is None:
        return None
    source = (os.getenv("AETHERRA_KEYS_MASTER"), get_master_key_file())
    if _fernet_source == source:
        return _fernet
    key = _load_master_key()
    if not key:
        _fernet = None
        _fernet_source = source
        return None
    try:
        _fernet = Fernet(key)
        _fernet_source = source
        return _fernet
    except (TypeError, ValueError) as exc:
        raise KeyStoreError("invalid Fernet master key") from exc


def _load() -> dict[str, Any]:
    global _cache, _cache_path
    _ensure()
    keys_file = get_keys_file()
    if _cache is not None and _cache_path == keys_file:
        return _cache
    try:
        loaded = json.loads(keys_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise KeyStoreError(f"unable to read key store: {exc}") from exc
    if not isinstance(loaded, dict):
        raise KeyStoreError("key store root must be a JSON object")
    _cache = loaded
    _cache_path = keys_file
    return _cache


def _save() -> None:
    if _cache is None:
        return
    try:
        _atomic_write(get_keys_file(), json.dumps(_cache, indent=2, sort_keys=True) + "\n")
    except OSError as exc:
        raise KeyStoreError(f"unable to write key store: {exc}") from exc


def _encrypted_copy(data: dict[str, Any], fernet: Any) -> dict[str, Any]:
    converted: dict[str, Any] = {
        "__encrypted__": True,
        "__updated_at": datetime.now(UTC).isoformat(),
    }
    for name, value in data.items():
        if name.startswith("__"):
            continue
        if isinstance(value, dict) and isinstance(value.get("cipher"), str):
            converted[name] = value
            continue
        plaintext = value if isinstance(value, str) else str(value)
        converted[name] = {"cipher": fernet.encrypt(plaintext.encode()).decode()}
    return converted


def _maybe_encrypt_on_write() -> None:
    global _cache
    fernet = _get_fernet()
    if fernet is None:
        return
    data = _load()
    if not data or data.get("__encrypted__") is True:
        return
    _cache = _encrypted_copy(data, fernet)
    _save()


def get_key(name: str) -> str | None:
    """Retrieve a key for trusted core code."""
    _validate_name(name)
    if _safe_mode_enabled():
        return None
    env_name = f"AETHERRA_{name.upper()}"
    if env_name in os.environ:
        return os.environ[env_name]
    with _LOCK:
        data = _load()
        if data.get("__encrypted__") is True:
            entry = data.get(name)
            if not isinstance(entry, dict) or not isinstance(entry.get("cipher"), str):
                return None
            fernet = _get_fernet()
            if fernet is None:
                return None
            try:
                return fernet.decrypt(entry["cipher"].encode()).decode("utf-8")
            except Exception as exc:
                raise KeyStoreError(f"unable to decrypt key {name!r}") from exc
        value = data.get(name)
        return value if isinstance(value, str) else None


def set_key(name: str, value: str) -> None:
    _validate_name(name)
    if not isinstance(value, str) or not value:
        raise ValueError("key value must be a non-empty string")
    if _safe_mode_enabled():
        raise RuntimeError("safe mode: secret storage is disabled")
    with _LOCK:
        data = _load()
        fernet = _get_fernet()
        profile = (os.getenv("AETHERRA_PROFILE", "") or "").strip().lower()
        allow_plain = os.getenv("AETHERRA_KEYS_ALLOW_PLAINTEXT", "0") == "1"
        if fernet is None and profile in {"prod", "production", "staging"} and not allow_plain:
            ensure_master_key()
            fernet = _get_fernet()
            if fernet is None:
                raise KeyStoreError("encryption_required_in_production")

        global _cache
        if fernet is not None:
            encrypted = (
                data
                if data.get("__encrypted__") is True
                else _encrypted_copy(data, fernet)
            )
            encrypted[name] = {"cipher": fernet.encrypt(value.encode()).decode()}
            encrypted["__updated_at"] = datetime.now(UTC).isoformat()
            _cache = encrypted
        else:
            data[name] = value
            data["__updated_at"] = datetime.now(UTC).isoformat()
        _save()


def delete_key(name: str) -> None:
    _validate_name(name)
    if _safe_mode_enabled():
        raise RuntimeError("safe mode: secret storage is disabled")
    with _LOCK:
        data = _load()
        if name in data:
            del data[name]
            data["__updated_at"] = datetime.now(UTC).isoformat()
            _save()


def get_key_scoped(name: str, requester: str | None) -> str | None:
    """Retrieve a key only when the requester is authorized by policy."""
    _validate_name(name)
    profile = (os.getenv("AETHERRA_PROFILE", "") or "").strip().lower()
    allow_unscoped = os.getenv("AETHERRA_KEYS_ALLOW_UNSCOPED", "0") == "1"
    if requester is None:
        if profile in {"prod", "production", "staging"} and not allow_unscoped:
            return None
        return get_key(name)
    if not isinstance(requester, str) or not requester.strip():
        return None

    policy_path = get_app_dir() / "policy" / "keys_policy.json"
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    if not isinstance(policy, dict):
        return None
    allow = policy.get("allow")
    if not isinstance(allow, dict):
        return None
    allowed = allow.get(requester)
    if not isinstance(allowed, list) or name not in allowed:
        return None
    return get_key(name)


def ensure_master_key() -> str | None:
    """Generate and persist a Fernet master key when one is not configured."""
    global _fernet, _fernet_source
    if Fernet is None:
        return None
    env_key = os.getenv("AETHERRA_KEYS_MASTER")
    if env_key:
        return env_key
    master_file = get_master_key_file()
    with _LOCK:
        if master_file.exists():
            try:
                return master_file.read_text(encoding="utf-8").strip()
            except OSError as exc:
                raise KeyStoreError(f"unable to read master key: {exc}") from exc
        key = Fernet.generate_key()
        try:
            _atomic_write(master_file, key + b"\n")
        except OSError as exc:
            raise KeyStoreError(f"unable to persist master key: {exc}") from exc
        _fernet = None
        _fernet_source = None
        _maybe_encrypt_on_write()
        return key.decode("utf-8")
