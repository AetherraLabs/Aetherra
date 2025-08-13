"""
API key management helpers.

- Stores keys in user config dir ~/.aetherra/keys.json (Windows friendly).
- Provides get/set/delete and in-memory cache.
- Avoids printing secrets; integrates with env override AETHERRA_<NAME>.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

APP_DIR = Path(os.path.expanduser("~/.aetherra")).resolve()
KEYS_FILE = APP_DIR / "keys.json"

_cache = None


def _ensure():
    APP_DIR.mkdir(parents=True, exist_ok=True)
    if not KEYS_FILE.exists():
        KEYS_FILE.write_text("{}", encoding="utf-8")


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
    if _cache is not None:
        KEYS_FILE.write_text(json.dumps(_cache, indent=2), encoding="utf-8")


def get_key(name: str) -> Optional[str]:
    env_name = f"AETHERRA_{name.upper()}"
    if env_name in os.environ:
        return os.environ[env_name]
    data = _load()
    return data.get(name)


def set_key(name: str, value: str):
    data = _load()
    data[name] = value
    _save()


def delete_key(name: str):
    data = _load()
    if name in data:
        del data[name]
        _save()
