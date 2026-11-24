"""Declared installers and committed locks must select compatible providers."""

# Standard library imports
from pathlib import Path

# Third party imports
import pytest
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

ROOT = Path(__file__).resolve().parents[2]


def requirements(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line and not line.startswith("-"):
            yield Requirement(line)


@pytest.mark.parametrize("lock", ["requirements.lock", "requirements-ci.lock"])
@pytest.mark.parametrize(
    "source", ["requirements.txt", "requirements/base.txt", "requirements/ci.txt"]
)
def test_declared_versions_accept_the_committed_lock(source, lock):
    pins = {
        canonicalize_name(req.name): next(iter(req.specifier)).version
        for req in requirements(ROOT / lock)
    }
    shared = [
        req
        for req in requirements(ROOT / source)
        if canonicalize_name(req.name) in pins
        and (req.marker is None or req.marker.evaluate())
    ]
    assert shared, "The installer must share dependencies with its lock"
    incompatible = [
        f"{req} excludes {pins[canonicalize_name(req.name)]}"
        for req in shared
        if not req.specifier.contains(pins[canonicalize_name(req.name)])
    ]
    assert not incompatible, "\n".join(incompatible)


@pytest.mark.parametrize("source", ["requirements.txt", "requirements/base.txt"])
@pytest.mark.parametrize(
    ("provider", "unsupported"),
    [("openai", "3.57.0"), ("anthropic", "2.11.0")],
)
def test_installers_exclude_sdks_with_incompatible_guarded_transports(
    source, provider, unsupported
):
    declared = {req.name: req for req in requirements(ROOT / source)}
    # These SDKs require HTTPX2 clients; our security transports implement HTTPX.
    assert not declared[provider].specifier.contains(unsupported)
