"""Resolve real offline wheels without freezing unrelated installed packages."""

from __future__ import annotations

# Standard library imports
import os
import subprocess
import venv
import zipfile
from pathlib import Path

# Third party imports
import pytest

TOOL = Path(__file__).resolve().parents[2] / "tools" / "dependency_lock.py"


def wheel(directory, name, version, requires=()):
    stem = f"{name}-{version}"
    metadata = (
        f"Metadata-Version: 2.1\nName: {name.replace('_', '-')}\nVersion: {version}\n"
    )
    metadata += "".join(f"Requires-Dist: {item}\n" for item in requires)
    with zipfile.ZipFile(directory / f"{stem}-py3-none-any.whl", "w") as archive:
        archive.writestr(f"{name}.py", "")
        archive.writestr(f"{stem}.dist-info/METADATA", metadata)
        archive.writestr(
            f"{stem}.dist-info/WHEEL",
            "Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
        )
        archive.writestr(f"{stem}.dist-info/RECORD", "")


@pytest.fixture
def local_environment(tmp_path):
    wheels = tmp_path / "wheels"
    wheels.mkdir()
    wheel(wheels, "alpha_fixture", "1.0", ["beta-fixture>=1.0"])
    wheel(wheels, "beta_fixture", "1.0")
    wheel(wheels, "beta_fixture", "2.0")
    wheel(wheels, "unrelated_fixture", "1.0")
    virtualenv = tmp_path / "venv"
    venv.EnvBuilder(with_pip=True).create(virtualenv)
    python = virtualenv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    env = os.environ.copy()
    for key in list(env):
        if key.upper().startswith(("PIP_", "PYTHON")):
            env.pop(key)
    env.update(PIP_CONFIG_FILE=os.devnull, PIP_NO_INDEX="1", PYTHONNOUSERSITE="1")
    installed = subprocess.run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--no-index",
            "--find-links",
            str(wheels),
            "alpha-fixture==1.0",
            "beta-fixture==1.0",
            "unrelated-fixture==1.0",
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert installed.returncode == 0, installed.stderr
    requirements = tmp_path / "runtime.txt"
    requirements.write_text(
        f"--no-index\n--find-links {wheels.as_uri()}\nalpha-fixture==1.0\n",
        encoding="utf-8",
    )
    constraints = tmp_path / "constraints.txt"
    constraints.write_text("beta-fixture==1.0\n", encoding="utf-8")
    return python, env, requirements, constraints


def resolve(local_environment, output):
    python, env, requirements, constraints = local_environment
    return subprocess.run(
        [
            str(python),
            str(TOOL),
            "--requirements",
            str(requirements),
            "--constraint",
            str(constraints),
            "--output",
            str(output),
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_resolved_lock_includes_installed_transitives_but_excludes_unrelated(
    local_environment, tmp_path
):
    output = tmp_path / "resolved.lock"
    result = resolve(local_environment, output)
    assert result.returncode == 0, result.stderr
    pins = {
        line
        for line in output.read_text().splitlines()
        if not line.startswith("#") and line
    }
    assert pins == {"alpha-fixture==1.0", "beta-fixture==1.0"}


def test_failed_resolution_preserves_existing_lock(local_environment, tmp_path):
    local_environment[3].write_text("beta-fixture==0.0\n", encoding="utf-8")
    output = tmp_path / "existing.lock"
    output.write_text("known-good==1.0\n", encoding="utf-8")
    result = resolve(local_environment, output)
    assert result.returncode != 0
    assert output.read_text() == "known-good==1.0\n"
