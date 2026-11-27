"""Normal CLI, separate processes and strict disposable Memory profiles."""

# Standard library imports
import os
import socket
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

# Third party imports
import pytest


def test_temporal_runtime_launch(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2] / "tools"))
    # Third party imports
    from alpha_temporal_smoke import run

    report = run(tmp_path / "temporal")
    assert [phase["name"] for phase in report["phases"]] == [
        "temporal-create",
        "temporal-resume",
        "temporal-isolated",
    ]
    assert report["restored_observation_ids"]
    assert report["pruned_through"] > 0
    assert len({phase["pid"] for phase in report["phases"]}) == 3


@pytest.mark.parametrize("case", ["foreign_listener", "fallback", "owned"])
def test_browser_listener_ownership(tmp_path, monkeypatch, case):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2] / "tools"))
    # Third party imports
    from alpha_integration_smoke import write_json
    from alpha_temporal_smoke import hold

    with (
        socket.socket() as listener,
        subprocess.Popen(
            [sys.executable, "-c", "import sys; sys.stdin.read()"],
            stdin=subprocess.PIPE,
        ) as other,
    ):
        try:
            listener.bind(("127.0.0.1", 0))
            listener.listen()
            host, port = listener.getsockname()
            pid = other.pid if case == "foreign_listener" else os.getpid()
            child = SimpleNamespace(
                artifacts=tmp_path,
                port=port,
                base=f"http://{host}:{port}",
                process=SimpleNamespace(pid=pid, poll=lambda: None),
            )
            write_json(
                tmp_path / "boot.json",
                {
                    "pid": pid,
                    "owned_hub_listener": [host, 0 if case == "fallback" else port],
                },
            )
            (tmp_path / "browser-release").touch()
            ready = tmp_path / "browser-ready.json"
            if case == "owned":
                hold(child, 1)
                assert ready.is_file()
            else:
                with pytest.raises(RuntimeError, match="listener"):
                    hold(child, 1)
                assert not ready.exists()
        finally:
            other.communicate(timeout=5)


@pytest.mark.parametrize(
    ("module", "arguments"),
    [("alpha_temporal_smoke", ""), ("alpha_consciousness_automatic_smoke", ", 0")],
)
def test_optimized_smoke_refuses_before_artifacts_or_children(
    tmp_path, module, arguments
):
    output = tmp_path / "output"
    child_attempt = tmp_path / "child-attempt"
    code = f"""
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from {module} import run

def observe(event, args):
    if event == "subprocess.Popen":
        Path(sys.argv[3]).touch()
        raise RuntimeError("unexpected subprocess")

sys.addaudithook(observe)
run(Path(sys.argv[2]){arguments})
"""
    result = subprocess.run(
        [
            sys.executable,
            "-O",
            "-c",
            code,
            str(Path(__file__).resolve().parents[2] / "tools"),
            str(output),
            str(child_attempt),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode != 0
    assert "requires Python assertions" in result.stderr
    assert not output.exists()
    assert not child_attempt.exists()


def test_finish_reports_nonzero_graceful_exit(tmp_path, monkeypatch):
    # Standard library imports
    from unittest.mock import Mock

    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2] / "tools"))
    # Third party imports
    from alpha_consciousness_automatic_smoke import Launch

    child = Launch.__new__(Launch)
    child.process = Mock(pid=1, returncode=7)
    child.process.poll.side_effect = [None, 7]
    child.process.wait.return_value = 7
    child.stop_method = None
    child.forced = False
    child.artifacts = tmp_path
    child.port = 0
    with pytest.raises(RuntimeError, match="launcher exited with code 7"):
        child.finish()
    child.process.wait.assert_called_once_with(timeout=65)
    child.process.kill.assert_not_called()
    assert (tmp_path / "exit.json").is_file()


def test_supervised_prune_preserves_native_parent_environment(tmp_path):
    # Explicit child environments can carry an empty native Windows value that
    # os.environ clear/update silently deletes from subsequently inherited envs.
    code = r"""
import os
from pathlib import Path
import shutil
import subprocess
import sys

sys.path.insert(0, sys.argv[1])
from alpha_temporal_smoke import supervised_prune

profile = Path(sys.argv[2])
profile.mkdir()
(profile / "temp").mkdir()
artifacts = profile / "evidence"
artifacts.mkdir()
original = dict(os.environ)
original_cwd = Path.cwd()
git = shutil.which("git")
assert git
observed = []

def inspect_child(event, args):
    if event != "subprocess.Popen":
        return
    environment = args[3]
    if environment is None or environment.get("AETHERRA_GUARDIAN_MODE") != "enforcing":
        return
    observed.append(True)
    assert "OPENAI_API_KEY" not in environment
    assert "GH_TOKEN" not in environment
    assert "AETHERRA_ALLOW_UNSIGNED_DEV" not in environment
    assert environment["AETHERRA_SIGNING_STRICT"] == "1"
    assert environment["GIT_CONFIG_VALUE_0"] == ""
    assert args[2] == str(profile)

sys.addaudithook(inspect_child)
subprocess.run([git, "config", "--get", "test.aetherraEmpty"], check=True)
error = None
try:
    supervised_prune(profile, artifacts, "a" * 32, {"generation": 3})
except (AssertionError, subprocess.CalledProcessError) as exc:
    error = exc
finally:
    # Use the inherited native environment: passing env would hide the bug.
    subprocess.run([git, "config", "--get", "test.aetherraEmpty"], check=True)
assert dict(os.environ) == original
assert Path.cwd() == original_cwd
subprocess.run([
    sys.executable, "-c",
    "import os; assert os.environ['OPENAI_API_KEY'] == 'test-key'"
], check=True)
assert isinstance(error, subprocess.CalledProcessError), "prune failure was swallowed"
assert error.returncode != 0
assert observed == [True], "prune did not use an isolated strict child"
assert (artifacts / "supervised-prune.log").is_file()
"""
    environment = {
        name: value
        for name, value in os.environ.items()
        if name.upper() in {"SYSTEMROOT", "WINDIR", "PATH", "TEMP", "TMP", "COMSPEC"}
    }
    environment.update(
        HOME=str(tmp_path),
        USERPROFILE=str(tmp_path),
        GIT_CONFIG_COUNT="1",
        GIT_CONFIG_KEY_0="test.aetherraEmpty",
        GIT_CONFIG_VALUE_0="",
        OPENAI_API_KEY="test-key",
        GH_TOKEN="synthetic-token",
        AETHERRA_ALLOW_UNSIGNED_DEV="1",
        AETHERRA_SKIP_DOTENV="1",
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONUTF8="1",
    )
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "-c",
            code,
            str(Path(__file__).resolve().parents[2] / "tools"),
            str(tmp_path / "profile"),
        ],
        env=environment,
        capture_output=True,
        text=True,
        timeout=45,
    )
    assert result.returncode == 0, result.stdout + result.stderr
