"""Exercise the workflow's policy decision without contacting GitHub."""

# Standard library imports
import os
import shutil
import subprocess
from pathlib import Path

# Third party imports
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    ("allowed", "api_exit", "expected_exit", "merge_requested"),
    [
        ("false", "0", 0, False),
        ("true", "0", 0, True),
        ("null", "0", 1, False),
        ("", "1", 1, False),
    ],
)
def test_automerge_obeys_repository_policy(
    allowed, api_exit, expected_exit, merge_requested
):
    bash = shutil.which("bash")
    if os.name == "nt" and (git := shutil.which("git")):
        git_bash = Path(git).parent.parent / "bin" / "bash.exe"
        if git_bash.exists():
            bash = str(git_bash)
    if not bash:
        pytest.skip("workflow shell is unavailable")
    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/dependabot-auto-merge.yml").read_text()
    )
    script = next(
        step["run"]
        for step in workflow["jobs"]["auto-merge"]["steps"]
        if step.get("name") == "Enable auto-merge for Dependabot PRs"
    )
    # Replace only the external CLI boundary; execute the actual workflow script.
    fake_cli = """
gh() {
    if [ "$1" = "api" ]; then
        printf '%s\\n' "$TEST_ALLOWED"
        return "$TEST_API_EXIT"
    fi
    if [ "$1" = "pr" ] && [ "$2" = "merge" ]; then
        printf 'MERGE_REQUEST %s\\n' "$*"
        return 0
    fi
    return 99
}
"""
    env = dict(
        os.environ,
        TEST_ALLOWED=allowed,
        TEST_API_EXIT=api_exit,
        GITHUB_REPOSITORY="synthetic/repo",
        PR_URL="https://example.invalid/pr/1",
    )
    result = subprocess.run(
        [bash, "--noprofile", "--norc", "-e", "-o", "pipefail"],
        input=fake_cli + script,
        text=True,
        capture_output=True,
        env=env,
        timeout=10,
    )
    assert result.returncode == expected_exit, result.stdout + result.stderr
    assert (
        "MERGE_REQUEST pr merge --auto --merge https://example.invalid/pr/1"
        in result.stdout
    ) is merge_requested
