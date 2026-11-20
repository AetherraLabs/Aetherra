#!/usr/bin/env python3
"""Keep release metadata consistent without permitting version downgrades."""

from __future__ import annotations

# Standard library imports
import argparse
import re
import tomllib
from pathlib import Path

# Third party imports
from packaging.version import Version


def check_next(current: str, proposed: str) -> None:
    if Version(proposed) < Version(current):
        raise ValueError(
            f"refusing version downgrade from {current} to {proposed}; review reachable release tags"
        )


def sync_readme(path: Path, version: str) -> None:
    Version(version)
    original = path.read_text(encoding="utf-8")
    text, lines = re.subn(
        r"Version:\s*\*\*[0-9A-Za-z_.-]+\*\*", f"Version: **{version}**", original
    )
    badge = version.replace("-", "--").replace("_", "__")
    text, badges = re.subn(
        r"(https://img\.shields\.io/badge/Version-)[^\s)]+",
        rf"\g<1>{badge}-0f766e",
        text,
    )
    if lines != 1 or badges != 1:
        raise ValueError("expected exactly one README version line and badge markers")
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-next")
    args = parser.parse_args()
    try:
        version = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))[
            "project"
        ]["version"]
        if args.check_next:
            check_next(version, args.check_next)
        else:
            sync_readme(Path("README.md"), version)
        return 0
    except (OSError, KeyError, ValueError) as exc:
        print(f"[RELEASE][BLOCKED] {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
