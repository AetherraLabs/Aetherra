"""Dependency checks must inspect the interpreter running the gate."""

import sys
import tomllib
from pathlib import Path
from unittest.mock import Mock

import pytest
from packaging.requirements import Requirement

from tools import enforce_lock_sync


def test_freeze_uses_gate_interpreter(monkeypatch):
    freeze = Mock(return_value="example==1.2.3\n")
    monkeypatch.setattr(enforce_lock_sync.subprocess, "check_output", freeze)
    assert enforce_lock_sync.collect_freeze() == {"example==1.2.3"}
    assert freeze.call_args.args[0] == [sys.executable, "-m", "pip", "freeze"]


@pytest.mark.parametrize(
    "profile", ["pyproject.toml", "requirements.txt", "requirements/base.txt"]
)
def test_install_profiles_declare_required_signing_backend(profile):
    root = Path(__file__).resolve().parents[2]
    text = (root / profile).read_text(encoding="utf-8")
    if profile == "pyproject.toml":
        declarations = tomllib.loads(text)["project"]["dependencies"]
    else:
        declarations = [
            line.strip()
            for line in text.splitlines()
            if line.strip() and not line.lstrip().startswith(("#", "-"))
        ]
    requirements = [
        Requirement(line.partition(" #")[0].strip()) for line in declarations
    ]
    signing = [
        requirement
        for requirement in requirements
        if requirement.name.lower() == "pynacl"
    ]
    assert len(signing) == 1, (
        "Strict plugin verification needs a declared signing backend"
    )
    assert "1.6.2" in signing[0].specifier
    assert "1.6.1" not in signing[0].specifier


def test_ci_lock_pins_required_signing_backend():
    root = Path(__file__).resolve().parents[2]
    pins = enforce_lock_sync.parse_lock(root / "requirements-ci.lock")
    assert "PyNaCl==1.6.2" in pins


def test_freeze_excludes_unpinned_and_direct_references(monkeypatch):
    freeze = Mock(
        return_value=(
            "# generated\nexample==1.2.3\n-e local\n"
            "private @ https://synthetic.invalid/package.whl\nother>=2\n"
        )
    )
    monkeypatch.setattr(enforce_lock_sync.subprocess, "check_output", freeze)
    assert enforce_lock_sync.collect_freeze() == {"example==1.2.3"}
