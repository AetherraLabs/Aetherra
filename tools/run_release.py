"""Run semantic-release with an explicitly reviewed package-version baseline."""

from __future__ import annotations

# Standard library imports
import argparse
import json
import os
import re
import subprocess
import sys
import tomllib
from contextlib import contextmanager
from pathlib import Path


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), *args], text=True, stderr=subprocess.PIPE
    ).strip()


def release_tags(repo: Path) -> set[str]:
    return {
        tag
        for tag in git(repo, "tag", "--merged", "HEAD").splitlines()
        if re.fullmatch(r"v\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?", tag)
    }


@contextmanager
def package_baseline(repo: Path):
    """Bridge disconnected history locally, once; never push or rewrite public tags."""
    if release_tags(repo):
        yield
        return
    if git(repo, "rev-parse", "--is-shallow-repository") != "false":
        raise ValueError("release bootstrap requires complete Git history")
    git_dir = git(repo, "rev-parse", "--path-format=absolute", "--git-dir")
    common_dir = git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if Path(git_dir).resolve() != Path(common_dir).resolve():
        raise ValueError("release bootstrap requires a standalone checkout")
    config = json.loads(
        (repo / ".ci/release-bootstrap.json").read_text(encoding="utf-8")
    )
    current = tomllib.loads((repo / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]["version"]
    version, commit = config["version"], config["commit"]
    if current != version:
        raise ValueError("package version does not match the approved release baseline")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("release baseline requires a full commit ID")
    git(repo, "merge-base", "--is-ancestor", commit, "HEAD")
    baseline = tomllib.loads(git(repo, "show", f"{commit}:pyproject.toml"))
    if baseline["project"]["version"] != version:
        raise ValueError("baseline commit has a different package version")
    ref = f"refs/tags/v{version}"
    original = git(repo, "rev-parse", "--verify", ref)
    if original != config["original_tag_object"]:
        raise ValueError("historical tag identity differs from the approved baseline")
    # PSR 9.21.1 drops a zero prerelease revision when resolving its traversal
    # boundary (beta.0 becomes v0.5.0). A non-tag local alias lets Git resolve
    # that boundary without inventing a stable release in PSR's version list.
    alias = f"refs/heads/v{version.split('-')[0]}"
    if git(
        repo,
        "for-each-ref",
        "--format=%(refname)",
        alias,
        alias.replace("heads", "tags"),
    ):
        raise ValueError("release baseline traversal alias already exists")
    # Compare-and-swap both ways. PSR pushes only its new tag, never this local ref.
    git(repo, "update-ref", ref, commit, original)
    try:
        git(repo, "update-ref", alias, commit, "0" * 40)
        try:
            yield
        finally:
            git(repo, "update-ref", "-d", alias, commit)
    finally:
        git(repo, "update-ref", ref, original, commit)


def run_release(repo: Path, *, plan: bool = False) -> str:
    command = [sys.executable, "-m", "semantic_release"]
    with package_baseline(repo):
        output = subprocess.check_output(
            [*command, "version", "--print"], cwd=repo, text=True
        )
        version = output.splitlines()[0].strip()
        subprocess.run(
            [sys.executable, "tools/sync_release_version.py", "--check-next", version],
            cwd=repo,
            check=True,
        )
        tag = f"v{version}"
        already_released = tag in git(repo, "tag", "--list").splitlines()
        if already_released and tag not in release_tags(repo):
            raise ValueError(f"proposed release tag {tag} belongs to unrelated history")
        if not plan:
            if already_released:
                build_signed(repo)
            subprocess.run([*command, "version"], cwd=repo, check=True)
            # The default publish target is the globally highest tag, possibly v1.0.0
            # on the historical branch. Always publish the version just calculated.
            subprocess.run([*command, "publish", "--tag", tag], cwd=repo, check=True)
        return version


def build_signed(repo: Path) -> None:
    """Fail before release publication unless the actual distributions are signed."""
    if not os.environ.get("AETHERRA_RELEASE_PRIVKEY"):
        raise ValueError(
            "AETHERRA_RELEASE_PRIVKEY is required; unsigned releases are forbidden"
        )
    if any((repo / "dist").glob("*")):
        raise ValueError("release build requires an empty dist directory")
    public_key = (repo / "keys/release_signing_ed25519.pub").read_text().strip()
    version = tomllib.loads((repo / "pyproject.toml").read_text())["project"]["version"]
    commands = [
        ["tools/sync_release_version.py"],
        ["-m", "build"],
        ["tools/sign_release_manifest.py", "--dist", "dist", "--version", version],
        [
            "tools/verify_release_manifest.py",
            "--manifest",
            "dist/release-manifest.json",
            "--pubkey",
            public_key,
        ],
    ]
    for command in commands:
        subprocess.run([sys.executable, *command], cwd=repo, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--plan", action="store_true", help="validate without publishing")
    mode.add_argument(
        "--build", action="store_true", help="build and verify signed distributions"
    )
    args = parser.parse_args()
    try:
        if args.build:
            build_signed(Path.cwd())
        else:
            print(run_release(Path.cwd(), plan=args.plan))
        return 0
    except (OSError, KeyError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"[RELEASE][BLOCKED] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
