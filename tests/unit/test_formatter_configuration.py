"""CI formatter commands must honor the repository's shared configuration."""

import tomllib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_ci_formatters_use_the_shared_project_configuration():
    configuration = tomllib.loads(
        (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )["tool"]
    assert configuration["black"]["line-length"] == configuration["ruff"]["line-length"]
    assert (
        configuration["isort"]["line_length"] == configuration["black"]["line-length"]
    )
    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/ci-fast-quality.yml").read_text(encoding="utf-8")
    )
    fast = workflow["jobs"]["fast-quality"]["steps"]
    checks = next(
        step["run"] for step in fast if step.get("name") == "Quick lint/format/test"
    )
    quick = (ROOT / "tools/quick_quality_check.ps1").read_text(encoding="utf-8")
    for commands in (checks, quick):
        assert "--line-length" not in commands
        assert "ruff check ." in commands
        assert "ruff format --check ." in commands
        assert "black --check ." in commands
        assert "isort --profile black --check-only ." in commands
