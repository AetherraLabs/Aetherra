# Standard library imports
import json
import pathlib

# Aetherra imports
from aetherra_coding import CodeOrchestrator, ops_engine


def test_apply_and_revert_new_file(tmp_path: pathlib.Path):
    (tmp_path / "audit").mkdir()
    orch = CodeOrchestrator(repo_root=tmp_path)
    diff = ops_engine.build_new_file_diff(tmp_path / "foo.txt", "hello\n")
    pr = orch.apply_patch(diff)
    assert pr.applied and pr.rollback_token
    assert (tmp_path / "foo.txt").exists()
    rv = orch.revert(pr.rollback_token)
    assert rv.applied
    assert not (tmp_path / "foo.txt").exists()


def test_risk_classification():
    low_diff = "*** Begin Patch\n*** Add File: a.txt\nline1\n*** End Patch"
    lvl, changed = ops_engine.classify_risk(low_diff)
    assert lvl == "low"

    big_lines = "\n".join(f"+L{i}" for i in range(60))
    diff = f"*** Begin Patch\n*** Update File: a.txt\n{big_lines}\n*** End Patch"
    lvl2, changed2 = ops_engine.classify_risk(diff)
    assert lvl2 in {"medium", "high"} and changed2 >= 60


def test_risk_medium_and_high_thresholds(tmp_path: pathlib.Path):
    # medium (between 51 and 200)
    (tmp_path / "audit").mkdir()
    orch = CodeOrchestrator(repo_root=tmp_path)
    medium_lines = "\n".join(f"+L{i}" for i in range(120))
    medium_diff = (
        f"*** Begin Patch\n*** Add File: med.txt\n{medium_lines}\n*** End Patch"
    )
    pr_med = orch.apply_patch(medium_diff, dry_run=True, colorize=False)
    assert pr_med.risk_level == "medium"
    # high (>200)
    high_lines = "\n".join(f"+L{i}" for i in range(250))
    high_diff = f"*** Begin Patch\n*** Add File: big.txt\n{high_lines}\n*** End Patch"
    pr_high = orch.apply_patch(high_diff, dry_run=True, colorize=False)
    assert pr_high.risk_level == "high"


def test_scaffold_updates_registry(tmp_path: pathlib.Path):
    (tmp_path / "audit").mkdir()
    orch = CodeOrchestrator(repo_root=tmp_path)
    pr = orch.scaffold_plugin("sample_auto")
    assert pr.applied
    registry_file = (
        tmp_path / "Aetherra" / "plugins" / "core" / "registered_plugins.json"
    )
    assert registry_file.exists()
    data = json.loads(registry_file.read_text())
    assert "sample_auto" in data.get("plugins", [])
