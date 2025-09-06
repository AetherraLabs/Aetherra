#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Unit test for tools/create_annotated_tag.py (print only).

Covers synthetic manifest fallback path (no manifest present) and ensures
output includes version marker and tool identifier.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

pytestmark = pytest.mark.unit


def test_create_annotated_tag_synthetic(tmp_path, monkeypatch):
    dist = tmp_path / "dist"
    dist.mkdir()
    # create a fake artifact wheel file
    wheel = dist / "aetherra-0.0.0a1-py3-none-any.whl"
    wheel.write_bytes(b"fake-wheel-bytes")

    # run script with synthetic manifest fallback (no manifest file created)
    # Locate script in repository and copy into tmp dir so relative dist lookup works
    repo_root = pathlib.Path(__file__).resolve().parents[2]
    script_src = repo_root / "tools" / "create_annotated_tag.py"
    script_dst = tmp_path / "create_annotated_tag.py"
    script_dst.write_text(script_src.read_text(encoding="utf-8"), encoding="utf-8")
    cp = subprocess.run(
        [sys.executable, str(script_dst), "--version", "0.0.0-test"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    out = cp.stdout
    assert "Aetherra Release 0.0.0-test" in out
    assert "tool: create_annotated_tag.py@" in out
    # Synthetic path should include artifacts count line
    assert "artifacts:" in out
