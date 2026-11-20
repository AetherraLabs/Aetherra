"""Generated indexes must not publish machine-specific checkout paths."""

# Standard library imports
import sys

# Aetherra imports
from tools import generate_file_index


def test_file_index_has_portable_repository_origin(tmp_path, monkeypatch):
    (tmp_path / "source.py").write_text(
        '"""Synthetic source module."""', encoding="utf-8"
    )
    output = tmp_path / "index.md"
    monkeypatch.setattr(
        generate_file_index,
        "git_tracked_files",
        lambda root, extensions: [root / "source.py"],
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["generate_file_index", "--root", str(tmp_path), "--output", str(output)],
    )
    generate_file_index.main()
    index = output.read_text(encoding="utf-8")
    assert "Generated from: repository source files" in index
    assert str(tmp_path) not in index
    assert "source.py" in index
    assert "Synthetic source module." in index
