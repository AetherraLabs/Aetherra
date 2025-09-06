# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
import pathlib
import subprocess
import sys
from pathlib import Path as _P

REPO_ROOT = _P(__file__).resolve().parents[2]
SCRIPT = str(REPO_ROOT / "tools" / "create_annotated_tag.py")


def write(path: pathlib.Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_malformed_manifest_graceful(tmp_path: pathlib.Path):
    dist = tmp_path / "dist"
    dist.mkdir()
    # create a wheel artifact file to enable synthetic fallback if parse fails
    wheel = dist / "pkg-0.0.1-py3-none-any.whl"
    wheel.write_bytes(b"fake wheel content")

    # malformed manifest (invalid JSON)
    bad_manifest = dist / "release-manifest.json"
    bad_manifest.write_text('{"version": "0.0.1", "incomplete": ', encoding="utf-8")

    # Run script expecting WARN and synthetic path (still exit 0)
    cmd = [
        sys.executable,
        SCRIPT,
        "--version",
        "0.0.1-alpha.test",
        "--manifest",
        str(bad_manifest),
    ]
    # Run from temp path so dist/ context is local
    proc = subprocess.run(
        cmd, cwd=tmp_path, capture_output=True, text=True, encoding="utf-8"
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    # The body should contain manifest_sha256 (hash of malformed file). Because a manifest path was provided,
    # synthetic artifact enumeration is NOT performed, so no artifacts line is expected.
    assert "manifest_sha256:" in proc.stdout
    # We expect a warning on stderr about parsing failure
    assert "[WARN] Failed to parse manifest" in proc.stderr
