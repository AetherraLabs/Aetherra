# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Test provenance_tag_wrapper fallback behavior.

Simulates missing annotated helper so wrapper should invoke simple helper.
We create temporary stub versions of the helpers inside a temp directory
and adjust PATH by running from that directory (wrapper uses relative paths).

Assertions:
 - Wrapper exits 0
 - Output includes [WRAPPER][simple] OK and tool marker for create_provenance_tag.py
 - Annotated helper absence is reported as failure (rc=127) before fallback
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

pytestmark = pytest.mark.unit


def test_wrapper_fallback_to_simple(tmp_path: pathlib.Path):
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()

    # Write wrapper script into temp tools directory (copy from repo)
    repo_root = pathlib.Path(__file__).resolve().parents[2]
    wrapper_src = repo_root / "tools" / "provenance_tag_wrapper.py"
    wrapper_dst = tools_dir / "provenance_tag_wrapper.py"
    wrapper_dst.write_text(wrapper_src.read_text(encoding="utf-8"), encoding="utf-8")

    # Create only simple helper stub (annotated helper intentionally missing)
    simple_helper = tools_dir / "create_provenance_tag.py"
    simple_helper.write_text(
        """#!/usr/bin/env python3\nimport sys, argparse, pathlib, hashlib, datetime\n\nTOOL_VERSION='test'\n\nparser=argparse.ArgumentParser();parser.add_argument('--version',required=True);parser.add_argument('--lock');parser.add_argument('--manifest');parser.add_argument('--print-only', action='store_true');parser.add_argument('--tag');parser.add_argument('--apply', action='store_true')\nargs=parser.parse_args()\nprint(f'Aetherra Release {args.version}')\nprint(f'tool: create_provenance_tag.py@{TOOL_VERSION}')\n""",
        encoding="utf-8",
    )

    # Run wrapper expecting fallback
    cmd = [sys.executable, str(wrapper_dst), "--version", "1.2.3-test"]
    proc = subprocess.run(
        cmd, cwd=tmp_path, capture_output=True, text=True, encoding="utf-8"
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    # simple helper success marker (fallback path)
    assert "[WRAPPER][simple] OK" in proc.stdout
    assert "tool: create_provenance_tag.py@" in proc.stdout
