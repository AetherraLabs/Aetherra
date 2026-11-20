"""Publishing must require the same commit's successful production signing."""

# Third party imports
import pytest

# Aetherra imports
from tools.verify_release_ci import verify_run

SHA = "a" * 40


def signed_run():
    return {
        "head_sha": SHA,
        "head_branch": "main",
        "event": "push",
        "status": "completed",
        "conclusion": "success",
    }


def signing_jobs():
    return [
        {
            "steps": [
                {
                    "name": "Production bundle with signed release manifest",
                    "conclusion": "success",
                },
                {"name": "Enforce signed-manifest policy", "conclusion": "success"},
            ]
        }
    ]


def test_successful_signed_build_allows_exact_commit():
    verify_run(signed_run(), signing_jobs(), SHA)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("head_sha", "b" * 40),
        ("head_branch", "feature"),
        ("event", "pull_request"),
        ("status", "in_progress"),
        ("conclusion", "failure"),
    ],
)
def test_other_commit_or_untrusted_or_failed_build_is_rejected(field, value):
    run = signed_run()
    run[field] = value
    with pytest.raises(ValueError, match="exact main commit"):
        verify_run(run, signing_jobs(), SHA)


@pytest.mark.parametrize("conclusion", ["skipped", "failure", None])
def test_green_workflow_without_successful_signing_is_rejected(conclusion):
    jobs = signing_jobs()
    jobs[0]["steps"][0]["conclusion"] = conclusion
    with pytest.raises(ValueError, match="signing"):
        verify_run(signed_run(), jobs, SHA)


def test_absent_signing_policy_is_rejected():
    with pytest.raises(ValueError, match="signing"):
        verify_run(signed_run(), [], SHA)
