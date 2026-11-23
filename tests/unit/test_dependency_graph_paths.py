"""Dependency analysis must not discard a checkout because of its parent path."""

# Standard library imports
from pathlib import Path

# Third party imports
import pytest

# Aetherra imports
from aetherra_coding.analysis import DependencyGraphBuilder


@pytest.mark.parametrize("parent", ["visible", ".workspace", ".venv", "dist-packages"])
def test_graph_filters_paths_relative_to_project_root(tmp_path, parent):
    root = tmp_path / parent / "project"
    sources = {
        "pkg/a.py": "import pkg.b\n",
        "pkg/b.py": "import pkg.a\n",
        ".cache/ignored.py": "import pkg.a\n",
        ".venv/ignored.py": "import pkg.a\n",
        "__pycache__/ignored.py": "import pkg.a\n",
        "dist-packages/ignored.py": "import pkg.a\n",
    }
    for name, content in sources.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    builder = DependencyGraphBuilder()
    assert builder.build_graph(root) == {
        Path("pkg/a.py"): {Path("pkg/b.py")},
        Path("pkg/b.py"): {Path("pkg/a.py")},
    }
    assert builder.find_dependents("pkg/b.py") == [Path("pkg/a.py")]
    assert builder.detect_cycles()
