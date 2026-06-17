"""Filesystem path helpers for Guardian state and policy."""

from __future__ import annotations

import os
from pathlib import Path


def workspace_root() -> Path:
    for env_name in ("AETHERRA_WORKSPACE_ROOT", "AETHERRA_WORKSPACE"):
        value = os.getenv(env_name, "").strip()
        if value:
            return Path(value).expanduser().resolve()
    return Path(".").resolve()


def guardian_state_dir() -> Path:
    configured = os.getenv("AETHERRA_GUARDIAN_STATE_DIR", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return workspace_root() / ".aetherra" / "guardian"


def guardian_policy_file() -> Path:
    configured = os.getenv("AETHERRA_GUARDIAN_POLICY", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    policy_home = os.getenv("AETHERRA_GUARDIAN_POLICY_HOME", "").strip()
    if policy_home:
        return Path(policy_home).expanduser().resolve() / "policy.json"
    return guardian_state_dir() / "policy.json"
