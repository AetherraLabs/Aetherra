"""Release version changes must preserve the README gate and never downgrade."""

# Standard library imports
from pathlib import Path

# Third party imports
import pytest

# Aetherra imports
from tools.sync_release_version import check_next, sync_readme


def test_readme_version_and_escaped_badge_follow_package_version(tmp_path):
    path = tmp_path / "README.md"
    path.write_text(
        "# Aetherra\nVersion: **0.5.0-beta.0**\n"
        "![Version](https://img.shields.io/badge/Version-0.5.0--beta.0-0f766e)\n",
        encoding="utf-8",
    )
    sync_readme(path, "0.5.1-beta.2")
    assert path.read_text(encoding="utf-8") == (
        "# Aetherra\nVersion: **0.5.1-beta.2**\n"
        "![Version](https://img.shields.io/badge/Version-0.5.1--beta.2-0f766e)\n"
    )


def test_downgrade_from_prerelease_history_is_rejected():
    with pytest.raises(ValueError, match="downgrade"):
        check_next("0.5.0-beta.0", "0.1.0")


def test_forward_release_is_allowed():
    check_next("0.5.0-beta.0", "0.5.0")


def test_missing_readme_marker_does_not_partially_rewrite(tmp_path):
    path = tmp_path / "README.md"
    path.write_text("Version: **0.5.0**\n", encoding="utf-8")
    with pytest.raises(ValueError, match="markers"):
        sync_readme(path, "0.5.1")
    assert path.read_text(encoding="utf-8") == "Version: **0.5.0**\n"
