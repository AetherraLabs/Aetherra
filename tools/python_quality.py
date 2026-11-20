#!/usr/bin/env python3
"""Check Python style, allowing only byte-identical legacy files.

The baseline is explicit, versioned debt, not an ignore list. Editing a file
requires fixing its style. Tool/configuration errors and critical Ruff findings
cannot be baselined. Normal checks never update the baseline.
"""

from __future__ import annotations

# Standard library imports
import argparse
import hashlib
import importlib.metadata
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

CHECKS = {
    "ruff": ("ruff", "check", "--force-exclude", "--output-format=json"),
    "ruff-format": (
        "ruff",
        "format",
        "--force-exclude",
        "--check",
        "--output-format=json",
    ),
    "black": ("black", "--check", "--workers=2"),
    "isort": ("isort", "--profile=black", "--check-only", "--filter-files"),
}
PATTERNS = {
    "black": r"^would reformat (.+)$",
    "isort": r"^ERROR: (.+) Imports are incorrectly sorted and/or formatted\.$",
}


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def versions() -> dict[str, str]:
    return {
        name: importlib.metadata.version(name) for name in ("ruff", "black", "isort")
    }


def configuration(root: Path) -> str:
    path = root / "pyproject.toml"
    tool = (
        tomllib.loads(path.read_text(encoding="utf-8")).get("tool", {})
        if path.exists()
        else {}
    )
    return digest(
        json.dumps(
            {name: tool.get(name, {}) for name in ("ruff", "black", "isort")},
            sort_keys=True,
        )
    )


def run(root: Path, args: tuple[str, ...]) -> subprocess.CompletedProcess:
    config = root / "pyproject.toml"
    if config.exists():
        # Explicit root configuration matches pre-commit; nested projects cannot
        # silently weaken the checks or change them with batch composition.
        option = "--settings-path" if args[0] == "isort" else "--config"
        args = (*args, option, str(config))
    return subprocess.run(
        [sys.executable, "-m", *args],
        cwd=root,
        env={**os.environ, "NO_COLOR": "1", "PYTHONUTF8": "1"},
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=300,
        check=False,
    )


def source_files(root: Path) -> list[str]:
    """Use Git's source inventory, not generated pytest fixtures or caches."""
    top = subprocess.run(
        ["git", "--no-optional-locks", "rev-parse", "--show-toplevel"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if top.returncode == 0 and Path(top.stdout.strip()).resolve() == root:
        paths = (
            subprocess.check_output(
                [
                    "git",
                    "--no-optional-locks",
                    "ls-files",
                    "--cached",
                    "--others",
                    "--exclude-standard",
                    "-z",
                ],
                cwd=root,
            )
            .decode("utf-8")
            .split("\0")
        )
    else:
        # Source archives and tiny standalone regression fixtures have no Git index.
        paths = [p.relative_to(root).as_posix() for p in root.rglob("*")]
    return sorted(
        {p for p in paths if Path(p).suffix in (".py", ".pyi") and (root / p).is_file()}
    )


def findings(root: Path) -> dict[str, dict]:
    files = source_files(root)
    batches = [tuple(files[i : i + 60]) for i in range(0, len(files), 60)]
    for batch in batches:
        critical = run(
            root, ("ruff", "check", "--force-exclude", "--select=E9,F63,F7,F82", *batch)
        )
        if critical.returncode:
            raise ValueError(
                "critical Ruff check failed:\n" + critical.stdout + critical.stderr
            )
    result: dict[str, dict] = {}
    for name, args in CHECKS.items():
        print(f"Checking {name} ({len(files)} source files)...", flush=True)
        paths = set()
        for batch in batches:
            proc = run(root, (*args, *batch))
            output = proc.stdout + proc.stderr
            if proc.returncode not in (0, 1):
                raise ValueError(f"{name} tool failed:\n{output}")
            if name in ("ruff", "ruff-format"):
                found = {item["filename"] for item in json.loads(proc.stdout)}
            else:
                found = set(re.findall(PATTERNS[name], output, re.MULTILINE))
            if bool(found) != bool(proc.returncode):
                raise ValueError(f"{name} unrecognized result:\n{output}")
            paths.update(found)
        for value in paths:
            path = (root / value).resolve()
            relative = path.relative_to(root).as_posix()
            entry = result.setdefault(
                relative,
                {"sha256": digest(path.read_text(encoding="utf-8")), "checks": []},
            )
            entry["checks"].append(name)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--baseline", type=Path, default=Path(".ci/python-quality-baseline.json")
    )
    parser.add_argument(
        "--write-baseline",
        type=Path,
        help="Explicit maintainer-only snapshot; review the diff",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        current_versions = versions()
        current_config = configuration(root)
        if args.write_baseline is None:
            baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
            if baseline["versions"] != current_versions:
                raise ValueError(
                    "tool version mismatch; install requirements/quality.txt"
                )
            if baseline["configuration"] != current_config:
                raise ValueError(
                    "formatter configuration changed; review the legacy baseline explicitly"
                )
        current = findings(root)
        if args.write_baseline is not None:
            payload = {
                "schema": 1,
                "versions": current_versions,
                "configuration": current_config,
                "files": dict(sorted(current.items())),
            }
            args.write_baseline.parent.mkdir(parents=True, exist_ok=True)
            args.write_baseline.write_text(
                json.dumps(payload, indent=2) + "\n", encoding="utf-8"
            )
            print(
                f"Recorded {len(current)} legacy files; review this snapshot before committing."
            )
            return 0
        unexpected = []
        for path, entry in current.items():
            old = baseline["files"].get(path)
            if (
                old is None
                or old["sha256"] != entry["sha256"]
                or not set(entry["checks"]).issubset(old["checks"])
            ):
                unexpected.append(f"{path}: {', '.join(entry['checks'])}")
        for line in unexpected:
            print(line)
        resolved = len(set(baseline["files"]) - set(current))
        print(
            f"Python quality: {len(unexpected)} new/edited violations; {len(current) - len(unexpected)} unchanged legacy files; {resolved} resolved."
        )
        return 1 if unexpected else 0
    except (
        ValueError,
        KeyError,
        OSError,
        subprocess.SubprocessError,
        importlib.metadata.PackageNotFoundError,
    ) as exc:
        print(f"Python quality failed: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
