# Standard library imports
import json
import subprocess
import sys
from pathlib import Path


def test_memory_fragmentation_metrics_heuristic(tmp_path):
    # Keep imported suite services and background threads outside the measurement.
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "-c",
            "import json, sys; sys.path.insert(0, sys.argv[1]); "
            "from tools.memory_fragmentation_metrics import measure_fragmentation; "
            "print(json.dumps(measure_fragmentation(workload_iterations=1500).to_dict()))",
            str(Path(__file__).resolve().parents[2]),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    stats = json.loads(result.stdout)
    # Structural sanity
    assert stats["before_traces"] > 0
    assert stats["after_traces"] > 0
    # Ratio bounds (distinct files / total traces) should always be <= 1.0
    assert 0 < stats["fragmentation_ratio_before"] <= 1.0
    assert 0 < stats["fragmentation_ratio_after"] <= 1.0
    # Heuristic: fragmentation ratio should not increase by more than 0.25
    delta = stats["fragmentation_ratio_after"] - stats["fragmentation_ratio_before"]
    assert delta <= 0.25, f"Fragmentation ratio increased too much: {delta:.3f}"
    # Size non-negative
    assert stats["after_size"] >= 0
