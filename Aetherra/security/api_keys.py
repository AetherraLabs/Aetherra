# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
API key management helpers.

- Stores keys in user config dir ~/.aetherra/keys.json (Windows friendly).
- Provides get/set/delete and in-memory cache.
- Avoids printing secrets; integrates with env override AETHERRA_<NAME>.
- Optional encrypt-at-rest with Fernet when a master key is available.

Encryption design:
- If the environment variable `AETHERRA_KEYS_MASTER` is set to a base64 urlsafe
    32-byte key (Fernet format), or if a master key file exists at
    `~/.aetherra/keys_master.key`, values will be stored encrypted at rest.
- Backward compatible: plaintext files are still readable and will be upgraded on write.
"""

from __future__ import annotations

# Standard library imports
import contextlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

try:  # Optional dependency
    # Third party imports
    from cryptography.fernet import Fernet  # type: ignore
except Exception:  # pragma: no cover - optional
    Fernet = None  # type: ignore
APP_DIR = Path(os.path.expanduser("~/.aetherra")).resolve()
KEYS_FILE = APP_DIR / "keys.json"
MASTER_KEY_FILE = APP_DIR / "keys_master.key"

_cache = None
_fernet = None


def _ensure():
    APP_DIR.mkdir(parents=True, exist_ok=True)
    if not KEYS_FILE.exists():
        KEYS_FILE.write_text("{}", encoding="utf-8")
    # best-effort restrictive perms (no-op on some platforms)
    with contextlib.suppress(Exception):
        os.chmod(APP_DIR, 0o700)
        if KEYS_FILE.exists():
            os.chmod(KEYS_FILE, 0o600)
    # In production/staging, auto-provision a master key if not present and plaintext is not allowed
    try:
        profile = (os.getenv("AETHERRA_PROFILE", "") or "").strip().lower()
        allow_plain = os.getenv("AETHERRA_KEYS_ALLOW_PLAINTEXT", "0") == "1"
        if (
            profile in ("prod", "production", "staging")
            and not allow_plain
            and Fernet is not None
            and not os.getenv("AETHERRA_KEYS_MASTER")
            and not MASTER_KEY_FILE.exists()
        ):
            ensure_master_key()
    except Exception:
        # non-fatal
        pass


def _load_master_key() -> bytes | None:
    """Return Fernet key bytes if available, else None.

    Priority: env AETHERRA_KEYS_MASTER -> file ~/.aetherra/keys_master.key
    """
    env_key = os.getenv("AETHERRA_KEYS_MASTER")
    if env_key:
        try:
            return env_key.encode("utf-8")
        except Exception:
            return None
    if MASTER_KEY_FILE.exists():
        try:
            data = MASTER_KEY_FILE.read_bytes()
            return data.strip()
        except Exception:
            return None
    return None


def _get_fernet() -> Any | None:
    global _fernet
    if _fernet is not None:
        return _fernet
    if Fernet is None:
        return None
    key = _load_master_key()
    if not key:
        return None
    try:
        _fernet = Fernet(key)
        return _fernet
    except Exception:
        return None


def _load():
    global _cache
    _ensure()
    if _cache is None:
        try:
            _cache = json.loads(KEYS_FILE.read_text(encoding="utf-8"))
        except Exception:
            _cache = {}
    return _cache


def _save():
    if _cache is None:
        return
    KEYS_FILE.write_text(json.dumps(_cache, indent=2), encoding="utf-8")
    with contextlib.suppress(Exception):
        os.chmod(KEYS_FILE, 0o600)


def _maybe_encrypt_on_write():
    """If Fernet is available and master key configured, rewrite values encrypted.

    Backward compatible: when a plaintext map exists, convert values to
    {"cipher": "..."} structure and set top-level flag "__encrypted__": true.
    """
    f = _get_fernet()
    if f is None:
        return
    data = _load()
    if not data:
        return
    if data.get("__encrypted__") is True:
        return
    converted: dict[str, object] = {
        "__encrypted__": True,
        "__updated_at": datetime.utcnow().isoformat(),
    }
    for k, v in list(data.items()):
        if k.startswith("__"):
            continue
        try:
            if isinstance(v, str):
                token = f.encrypt(v.encode("utf-8")).decode("utf-8")
                converted[k] = {"cipher": token}
            elif isinstance(v, dict) and "cipher" in v:
                converted[k] = v
            else:
                # coerce to str then encrypt
                token = f.encrypt(str(v).encode("utf-8")).decode("utf-8")
                converted[k] = {"cipher": token}
        except Exception:
            # leave as-is on failure (do not corrupt)
            converted[k] = v
    _cache.clear()  # type: ignore
    _cache.update(converted)  # type: ignore
    _save()


def get_key(name: str) -> str | None:
    env_name = f"AETHERRA_{name.upper()}"
    if env_name in os.environ:
        return os.environ[env_name]
    data = _load()
    # Encrypted layout
    if data.get("__encrypted__") is True:
        try:
            entry = data.get(name)
            if not entry:
                return None
            if isinstance(entry, dict) and "cipher" in entry:
                f = _get_fernet()
                if not f:
                    # Can't decrypt without Fernet key; treat as unavailable
                    return None
                token = entry.get("cipher")
                if not isinstance(token, str):
                    return None
                pt = f.decrypt(token.encode("utf-8"))
                out = pt.decode("utf-8")
                # drop references quickly (Python doesn't guarantee zeroization)
                del pt
                return out
            # unexpected structure
            return None
        except Exception:
            return None
    # Plaintext layout
    val = data.get(name)
    if isinstance(val, str):
        return val
    return None


def set_key(name: str, value: str):
    data = _load()
    f = _get_fernet()
    # Enforce encryption in production/staging unless explicitly allowed
    if not f:
        profile = (os.getenv("AETHERRA_PROFILE", "") or "").strip().lower()
        allow_plain = os.getenv("AETHERRA_KEYS_ALLOW_PLAINTEXT", "0") == "1"
        if profile in ("prod", "production", "staging") and not allow_plain:
            # Attempt to provision a master key automatically
            try:
                ensure_master_key()
                f = _get_fernet()
            except Exception:
                f = None
            if not f:
                raise RuntimeError("encryption_required_in_production")
    if f:
        enc_map: dict[str, object]
        enc_map = data if data.get("__encrypted__") else {"__encrypted__": True}
        token = f.encrypt(value.encode("utf-8")).decode("utf-8")
        enc_map[name] = {"cipher": token}
        enc_map["__updated_at"] = datetime.utcnow().isoformat()
        _cache.clear()  # type: ignore
        _cache.update(enc_map)  # type: ignore
        _save()
        return
    # plaintext fallback
    data[name] = value
    _save()


def delete_key(name: str):
    data = _load()
    if name in data:
        del data[name]
        _save()


def get_key_scoped(name: str, requester: str | None) -> str | None:
    """Return a key only if the requester is allowed by policy.

    Deny-by-default when a requester is provided. Allow global callers when
    requester is None (backward-compatible), or when env override
    AETHERRA_KEYS_ALLOW_UNSCOPED=1 is set.
    Policy file (optional): ~/.aetherra/policy/keys_policy.json
    {
      "allow": { "plugin:example": ["openai_api_key"] }
    }
    """
    # Unscoped allowed for backward compatibility unless explicitly disabled
    if requester is None or os.getenv("AETHERRA_KEYS_ALLOW_UNSCOPED", "0") == "1":
        return get_key(name)

    policy_path = APP_DIR / "policy" / "keys_policy.json"
    try:
        if policy_path.exists():
            policy = json.loads(policy_path.read_text(encoding="utf-8"))
            allow = policy.get("allow", {})
            allowed = allow.get(requester, [])
            if name in allowed:
                return get_key(name)
            return None
    except Exception:
        return None
    return None


def ensure_master_key() -> str | None:
    """Generate and persist a Fernet master key if none exists; return base64 key.

    No-op if cryptography isn't available. Returns the key as a string for convenience.
    """
    if Fernet is None:
        return None
    if os.getenv("AETHERRA_KEYS_MASTER"):
        return os.getenv("AETHERRA_KEYS_MASTER")
    if MASTER_KEY_FILE.exists():
        try:
            return MASTER_KEY_FILE.read_text(encoding="utf-8").strip()
        except Exception:
            return None
    try:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        key = Fernet.generate_key()
        MASTER_KEY_FILE.write_bytes(key + b"\n")
        with contextlib.suppress(Exception):
            os.chmod(MASTER_KEY_FILE, 0o600)
        # attempt to encrypt existing plaintext entries
        _maybe_encrypt_on_write()
        return key.decode("utf-8")
    except Exception:
        return None
