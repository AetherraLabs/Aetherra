"""Use real Git history and semantic-release; never contact a release server."""

# Standard library imports
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Third party imports
import pytest

pytest.importorskip("semantic_release")

# Aetherra imports
from tools.run_release import build_signed, package_baseline, run_release


def git(repo, *args):
    return subprocess.check_output(
        [
            shutil.which("git"),
            "-c",
            f"safe.directory={repo.as_posix()}",
            "-C",
            str(repo),
            *args,
        ],
        text=True,
        stderr=subprocess.PIPE,
    ).strip()


def semantic(repo, *args):
    env = os.environ.copy()
    for name in (
        "GH_TOKEN",
        "GITHUB_TOKEN",
        "GITHUB_ACTIONS",
        "GITHUB_OUTPUT",
        "GITHUB_ENV",
    ):
        env.pop(name, None)
    return (
        subprocess.run(
            [sys.executable, "-m", "semantic_release", *args],
            cwd=repo,
            env=env,
            text=True,
            capture_output=True,
            check=True,
            timeout=60,
        )
        .stdout.splitlines()[0]
        .strip()
    )


@pytest.fixture
def repo(tmp_path, monkeypatch):
    for name in (
        "GH_TOKEN",
        "GITHUB_TOKEN",
        "GITHUB_ACTIONS",
        "GITHUB_OUTPUT",
        "GITHUB_ENV",
    ):
        monkeypatch.delenv(name, raising=False)
    git(tmp_path, "init", "-b", "historical")
    git(tmp_path, "config", "user.name", "Release Test")
    git(tmp_path, "config", "user.email", "release-test@example.invalid")
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname="release-fixture"\nversion="0.5.0-beta.0"\n'
        '[tool.semantic_release]\nversion_toml=["pyproject.toml:project.version"]\n'
        'build_command=""\nallow_zero_version=true\nmajor_on_zero=false\n'
        'tag_format="v{version}"\n'
        '[tool.semantic_release.branches.main]\nmatch="main"\n'
        'prerelease=true\nprerelease_token="beta"\n',
        encoding="utf-8",
    )
    git(tmp_path, "add", "pyproject.toml")
    git(tmp_path, "commit", "-m", "feat: historical package")
    git(tmp_path, "tag", "v1.0.0")
    git(tmp_path, "tag", "-a", "v0.5.0-beta.0", "-m", "Historical beta")
    original_tag = git(tmp_path, "rev-parse", "refs/tags/v0.5.0-beta.0")
    git(tmp_path, "checkout", "--orphan", "main")
    git(tmp_path, "commit", "-m", "feat: reconstructed package")
    baseline_commit = git(tmp_path, "rev-parse", "HEAD")
    (tmp_path / ".ci").mkdir()
    (tmp_path / ".ci/release-bootstrap.json").write_text(
        json.dumps(
            {
                "version": "0.5.0-beta.0",
                "commit": baseline_commit,
                "original_tag_object": original_tag,
            }
        ),
        encoding="utf-8",
    )
    git(tmp_path, "add", ".ci/release-bootstrap.json")
    git(tmp_path, "commit", "-m", "fix: repair release setup")
    git(
        tmp_path,
        "remote",
        "add",
        "origin",
        "https://github.com/example/release-fixture.git",
    )
    return tmp_path


def refs(repo):
    return git(
        repo,
        "for-each-ref",
        "--format=%(refname) %(objectname)",
        "refs/tags",
        "refs/heads/v0.5.0",
    )


def test_baseline_repairs_real_cli_without_changing_historical_tags(repo):
    original = refs(repo)
    assert semantic(repo, "--noop", "version", "--print") == "0.1.0-beta.1"
    with package_baseline(repo):
        assert semantic(repo, "--noop", "version", "--print") == "0.5.0-beta.1"
    assert refs(repo) == original


def test_first_release_then_normal_increment_uses_new_reachable_tag(repo):
    original_beta = git(repo, "rev-parse", "refs/tags/v0.5.0-beta.0")
    with package_baseline(repo):
        version = semantic(
            repo, "version", "--no-push", "--no-vcs-release", "--skip-build"
        )
        assert version == "0.5.0-beta.1"
    assert git(repo, "rev-parse", "refs/tags/v0.5.0-beta.0") == original_beta
    git(repo, "commit", "--allow-empty", "-m", "fix: another change")
    with package_baseline(repo):
        assert semantic(repo, "--noop", "version", "--print") == "0.5.0-beta.2"


def test_baseline_restored_if_release_fails(repo):
    original = refs(repo)

    def fail_during_release():
        with package_baseline(repo):
            assert refs(repo) != original
            raise RuntimeError("simulated release failure")

    with pytest.raises(RuntimeError, match="simulated release failure"):
        fail_during_release()
    assert refs(repo) == original


def test_unknown_baseline_is_rejected_before_changing_refs(repo):
    original = refs(repo)
    path = repo / ".ci/release-bootstrap.json"
    config = json.loads(path.read_text())
    config["original_tag_object"] = "0" * 40
    path.write_text(json.dumps(config))
    with pytest.raises(ValueError, match="tag identity"), package_baseline(repo):
        pass
    assert refs(repo) == original


def test_shared_worktree_cannot_rewrite_shared_tags(repo, tmp_path):
    original = refs(repo)
    linked = tmp_path / "linked"
    git(repo, "worktree", "add", "--detach", str(linked), "HEAD")
    with (
        pytest.raises(ValueError, match="standalone checkout"),
        package_baseline(linked),
    ):
        pass
    assert refs(repo) == original


def test_runner_publishes_calculated_beta_not_historical_highest_tag(repo, monkeypatch):
    (repo / "tools").mkdir()
    shutil.copy(
        Path(__file__).parents[2] / "tools/sync_release_version.py", repo / "tools"
    )
    original = subprocess.run
    published = []

    def offline_run(command, **kwargs):
        if command[1:4] == ["-m", "semantic_release", "publish"]:
            published.append(command[4:])
            return subprocess.CompletedProcess(command, 0)
        if command[1:] == ["-m", "semantic_release", "version"]:
            command = [*command, "--no-push", "--no-vcs-release", "--skip-build"]
        return original(command, **kwargs)

    monkeypatch.setattr(subprocess, "run", offline_run)
    assert run_release(repo, plan=True) == "0.5.0-beta.1"
    assert published == []
    assert run_release(repo) == "0.5.0-beta.1"
    assert published == [["--tag", "v0.5.0-beta.1"]]


def test_signed_build_rejects_missing_secret_before_build(tmp_path, monkeypatch):
    monkeypatch.delenv("AETHERRA_RELEASE_PRIVKEY", raising=False)
    with pytest.raises(ValueError, match="unsigned releases are forbidden"):
        build_signed(tmp_path)


@pytest.mark.parametrize("wrong_key", [False, True])
def test_signed_build_verifies_actual_manifest(tmp_path, monkeypatch, wrong_key):
    signing = pytest.importorskip("nacl.signing")
    key = signing.SigningKey.generate()
    monkeypatch.setenv("AETHERRA_RELEASE_PRIVKEY", bytes(key).hex())
    (tmp_path / "keys").mkdir()
    trusted = signing.SigningKey.generate().verify_key if wrong_key else key.verify_key
    (tmp_path / "keys/release_signing_ed25519.pub").write_text(bytes(trusted).hex())
    (tmp_path / "pyproject.toml").write_text('[project]\nversion="0.5.0-beta.1"\n')
    (tmp_path / "README.md").write_text(
        "Version: **0.5.0-beta.0**\nhttps://img.shields.io/badge/Version-0.5.0--beta.0-blue\n"
    )
    (tmp_path / "tools").mkdir()
    for name in (
        "sync_release_version.py",
        "sign_release_manifest.py",
        "verify_release_manifest.py",
    ):
        shutil.copy(Path(__file__).parents[2] / "tools" / name, tmp_path / "tools")
    original = subprocess.run

    def fake_package_build(command, **kwargs):
        if command[1:] == ["-m", "build"]:
            (tmp_path / "dist").mkdir()
            (tmp_path / "dist/example.whl").write_bytes(b"synthetic distribution")
            return subprocess.CompletedProcess(command, 0)
        return original(command, **kwargs)

    monkeypatch.setattr(subprocess, "run", fake_package_build)
    if wrong_key:
        with pytest.raises(subprocess.CalledProcessError) as error:
            build_signed(tmp_path)
        assert error.value.returncode == 1
    else:
        build_signed(tmp_path)
        manifest = json.loads((tmp_path / "dist/release-manifest.json").read_text())
        assert manifest["version"] == "0.5.0-beta.1"
        assert [item["path"] for item in manifest["artifacts"]] == ["example.whl"]
