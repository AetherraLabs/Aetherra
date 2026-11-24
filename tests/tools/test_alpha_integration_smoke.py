"""The disposable alpha verifier must preserve isolation and reject false evidence."""

# Standard library imports
import json
import sqlite3
import sys
import threading
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer

# Third party imports
import pytest

# Aetherra imports
from tools import alpha_integration_smoke as smoke


def test_child_environment_scrubs_ambient_authority_and_keeps_git_tuples(
    monkeypatch, tmp_path
):
    ambient = {
        "PATH": "synthetic-tools",
        "SystemRoot": "synthetic-windows",
        "HOME": str(tmp_path / "other-user-home"),
        "USERPROFILE": str(tmp_path / "other-user-home"),
        "OPENAI_API_KEY": "test-key",
        "ANTHROPIC_API_KEY": "test-key",
        "AZURE_CLIENT_SECRET": "test-secret",
        "AWS_ACCESS_KEY_ID": "test-key",
        "GH_TOKEN": "test-token",
        "DATABASE_PASSWORD": "placeholder",
        "HTTP_PROXY": "http://invalid.example",
        "OPENAI_BASE_URL": "https://invalid.example",
        "AETHERRA_ALLOW_UNSIGNED_DEV": "1",
        "AETHERRA_GUARDIAN_MODE": "permissive",
        "AETHERRA_SELFINC_ENABLED": "1",
        "AETHERRA_SELF_IMPROVEMENT_AUTO_IMPLEMENT": "1",
        "PYTHONSTARTUP": "untrusted.py",
        "TEST_MODE": "ambient-test-mode",
        "GIT_CONFIG_COUNT": "2",
        "GIT_CONFIG_KEY_0": "safe.directory",
        "GIT_CONFIG_VALUE_0": str(tmp_path),
        "GIT_CONFIG_KEY_1": "protocol.file.allow",
        "GIT_CONFIG_VALUE_1": "never",
    }
    monkeypatch.setattr(smoke.os, "environ", ambient)

    env = smoke.child_environment(tmp_path, 12345)

    for key in ambient:
        if key.startswith("GIT_CONFIG_") or key in {"PATH", "SystemRoot"}:
            assert env[key] == ambient[key]
        elif key not in {
            "HOME",
            "USERPROFILE",
            "AETHERRA_GUARDIAN_MODE",
            "AETHERRA_SELFINC_ENABLED",
            "AETHERRA_SELF_IMPROVEMENT_AUTO_IMPLEMENT",
        }:
            assert key not in env
    assert env["HOME"] == env["USERPROFILE"] == str(tmp_path)
    assert env["AETHERRA_HUB_URL"] == "http://127.0.0.1:12345"
    assert env["NO_PROXY"] == "*"


@pytest.mark.parametrize("credential", [None, ""])
def test_live_environment_requires_explicit_credential(
    monkeypatch, tmp_path, credential
):
    ambient = {"HOME": str(tmp_path), "USERPROFILE": str(tmp_path)}
    if credential is not None:
        ambient["OPENAI_API_KEY"] = credential
    monkeypatch.setattr(smoke.os, "environ", ambient)

    with pytest.raises(RuntimeError, match="explicitly configure OPENAI_API_KEY"):
        smoke.child_environment(tmp_path, 12345, live=True)


def test_live_environment_forwards_only_intended_synthetic_credential(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(
        smoke.os,
        "environ",
        {
            "HOME": str(tmp_path),
            "USERPROFILE": str(tmp_path),
            "OPENAI_API_KEY": "test-key",
            "GH_TOKEN": "test-token",
        },
    )

    env = smoke.child_environment(tmp_path, 12345, live=True)

    assert env["OPENAI_API_KEY"] == "test-key"
    assert env["AETHERRA_LLM_MODEL"] == "gpt-4o"
    assert "GH_TOKEN" not in env


def test_disposable_profile_enforces_strict_signing_policy_and_observation(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(
        smoke.os, "environ", {"HOME": str(tmp_path), "USERPROFILE": str(tmp_path)}
    )
    profile = tmp_path / "profile"
    smoke.prepare_profile(profile)
    env = smoke.child_environment(profile, 12345)

    for key in (
        "AETHERRA_SKIP_DOTENV",
        "AETHERRA_GUARDIAN_ENABLED",
        "AETHERRA_GUARDIAN_REQUIRE_POLICY",
        "AETHERRA_REQUIRE_CAPABILITIES",
        "AETHERRA_NET_STRICT",
        "AETHERRA_SCRIPT_VERIFY_STRICT",
        "AETHERRA_SIGNING_STRICT",
        "AETHERRA_AUDIT",
        "AETHERRA_HOMEOSTASIS_OBSERVE_ONLY",
        "AETHERRA_AI_API_REQUIRE_TOKEN",
    ):
        assert env[key] == "1"
    assert env["AETHERRA_GUARDIAN_MODE"] == "enforcing"
    assert env["AETHERRA_HOMEOSTASIS_MODE"] == "observe_only"
    for key in (
        "AETHERRA_SELFINC_ENABLED",
        "AETHERRA_HMR_ENABLED",
        "AETHERRA_SELF_IMPROVEMENT_AUTO_IMPLEMENT",
    ):
        assert env[key] == "0"
    policy = profile / "policy"
    guardian = json.loads((policy / "guardian.json").read_text(encoding="utf-8"))
    capabilities = json.loads(
        (policy / "capabilities.json").read_text(encoding="utf-8")
    )
    network = json.loads((policy / "net_policy.json").read_text(encoding="utf-8"))
    assert guardian["default"] == "deny"
    assert {rule["requester"] for rule in guardian["allow"]} == {
        "service_registry",
        "hub:chat",
        "kernel_loop",
    }
    assert set(capabilities["allow"]) == {"service_registry", "kernel_loop"}
    assert all("*" not in grants for grants in capabilities["allow"].values())
    assert network["allow_domains"] == ["127.0.0.1", "localhost"]


@pytest.mark.parametrize("existing_kind", ["directory", "file"])
def test_existing_output_is_rejected_without_writes(
    monkeypatch, tmp_path, existing_kind
):
    output = tmp_path / "existing"
    if existing_kind == "directory":
        output.mkdir()
        sentinel = output / "keep.txt"
    else:
        sentinel = output
    sentinel.write_bytes(b"preserve-this-existing-data")
    before = {
        p.relative_to(tmp_path): p.read_bytes()
        for p in tmp_path.rglob("*")
        if p.is_file()
    }
    monkeypatch.setattr(
        sys, "argv", ["alpha_integration_smoke", "--output", str(output)]
    )

    def no_runtime(*args, **kwargs):
        pytest.fail("A unit test must not launch the full runtime")

    monkeypatch.setattr(smoke, "run_session", no_runtime)

    with pytest.raises(FileExistsError):
        smoke.main()

    after = {
        p.relative_to(tmp_path): p.read_bytes()
        for p in tmp_path.rglob("*")
        if p.is_file()
    }
    assert after == before
    assert not (output / "primary").exists()
    assert not (output / "separate").exists()


@pytest.fixture
def trace_fixture(tmp_path):
    saved_id = "d40f5dd1-039a-450b-a082-ad78558d2ee7"
    stored = {"role": "user", "content": smoke.FACT}
    with sqlite3.connect(tmp_path / "lyrixa_memory.db") as db:
        db.execute("CREATE TABLE memories (id TEXT PRIMARY KEY, content TEXT NOT NULL)")
        db.execute("INSERT INTO memories VALUES (?, ?)", (saved_id, json.dumps(stored)))
    evidence = {"id": saved_id, "content": json.dumps(stored)}
    written = {"pid": 101, "turns": [{"body": {"result": {"memory_id": saved_id}}}]}
    recalled = {
        "pid": 202,
        "provider": {
            "prompts": [
                f"Evidence:\n- {json.dumps(evidence)}\nUser: {smoke.QUESTION}\n"
            ]
        },
        "turns": [
            {
                "body": {
                    "result": {
                        "recall": {"record_ids": [saved_id]},
                        "llm": {"evidence_ids": [saved_id], "fallback": False},
                        "evidence": [evidence],
                        "response": "Your aunt Leona taught you.",
                    }
                }
            }
        ],
    }
    return tmp_path, written, recalled


def test_trace_matches_saved_sqlite_record_to_provider_context(trace_fixture):
    profile, written, recalled = trace_fixture
    trace = smoke.evidence_trace(profile, written, recalled)
    assert trace["retrieved_ids"] == [
        written["turns"][0]["body"]["result"]["memory_id"]
    ]
    assert trace["provider_evidence_ids"] == trace["retrieved_ids"]
    assert trace["write_pid"] == 101
    assert trace["recall_pid"] == 202


@pytest.mark.parametrize(
    "boundary", ["recall", "generation", "evidence", "prompt", "storage"]
)
def test_trace_rejects_unrelated_record_or_context(trace_fixture, boundary):
    profile, written, recalled = trace_fixture
    result = recalled["turns"][0]["body"]["result"]
    unrelated_id = "b11edbc5-69bc-4917-bc07-bc319d71aa3b"
    if boundary == "recall":
        result["recall"]["record_ids"] = [unrelated_id]
    elif boundary == "generation":
        result["llm"]["evidence_ids"] = [unrelated_id]
    elif boundary == "evidence":
        result["evidence"] = [
            {
                "id": unrelated_id,
                "content": json.dumps({"role": "user", "content": "Unrelated"}),
            }
        ]
    elif boundary == "prompt":
        saved_id = written["turns"][0]["body"]["result"]["memory_id"]
        recalled["provider"]["prompts"][0] = recalled["provider"]["prompts"][0].replace(
            saved_id, unrelated_id
        )
    else:
        with sqlite3.connect(profile / "lyrixa_memory.db") as db:
            db.execute(
                "UPDATE memories SET content=?",
                (json.dumps({"role": "user", "content": "Unrelated"}),),
            )

    with pytest.raises(AssertionError):
        smoke.evidence_trace(profile, written, recalled)


def test_trace_binds_expected_fact_to_the_stored_record_not_other_prompt_text(
    trace_fixture,
):
    profile, written, recalled = trace_fixture
    unrelated = {"role": "user", "content": "My favorite tea is oolong."}
    result = recalled["turns"][0]["body"]["result"]
    result["evidence"][0]["content"] = json.dumps(unrelated)
    with sqlite3.connect(profile / "lyrixa_memory.db") as db:
        db.execute("UPDATE memories SET content=?", (json.dumps(unrelated),))
    # IDs match at every boundary, and the unrelated evidence really is stored.
    # A fact elsewhere in the prompt must not satisfy the saved-record check.
    recalled["provider"]["prompts"] = [
        f"Other prompt text: {smoke.FACT}\nEvidence:\n"
        f"- {json.dumps(result['evidence'][0])}\nUser: {smoke.QUESTION}\n"
    ]

    with pytest.raises(AssertionError):
        smoke.evidence_trace(profile, written, recalled)


@pytest.fixture
def generated_turn():
    return {
        "llm": {
            "used": True,
            "fallback": False,
            "diag": {"event": "ok"},
            "model": {"provider": "openai", "model_name": "gpt-4o"},
        },
        "recall": {"event": "ok"},
    }


@pytest.mark.parametrize("live", [False, True])
def test_turn_accepts_successful_generation(generated_turn, live):
    if not live:
        generated_turn["llm"]["model"] = {
            "provider": "deterministic",
            "model_name": "context-responder",
        }
    smoke.validate_turn(generated_turn, live=live)


@pytest.mark.parametrize("live", [False, True])
@pytest.mark.parametrize(
    "failure", ["unused", "fallback", "generation_error", "recall_error"]
)
def test_turn_rejects_fallback_and_degraded_evidence(generated_turn, live, failure):
    if failure == "unused":
        generated_turn["llm"]["used"] = False
    elif failure == "fallback":
        generated_turn["llm"]["fallback"] = True
    elif failure == "generation_error":
        generated_turn["llm"]["diag"]["event"] = "provider_unavailable"
    else:
        generated_turn["recall"]["event"] = "retrieval_unavailable"

    with pytest.raises(AssertionError):
        smoke.validate_turn(generated_turn, live=live)


@pytest.mark.parametrize(
    ("field", "value"),
    [("provider", "deterministic"), ("model_name", "context-responder")],
)
def test_live_turn_rejects_wrong_provider_or_model(generated_turn, field, value):
    generated_turn["llm"]["model"][field] = value

    with pytest.raises(AssertionError):
        smoke.validate_turn(generated_turn, live=True)


@pytest.fixture
def busy_http_server():
    calls = []

    class Handler(BaseHTTPRequestHandler):
        def respond(self):
            body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            calls.append((self.command, self.path, body))
            status, payload = (
                (503, {"error": {"code": "hub_busy"}})
                if len(calls) == 1
                else (200, {"ok": True})
            )
            encoded = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        do_GET = do_POST = respond  # noqa: N815 - BaseHTTPRequestHandler contract

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", calls
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        assert not thread.is_alive()


def test_busy_chat_post_is_never_replayed(busy_http_server):
    base, calls = busy_http_server
    with pytest.raises(urllib.error.HTTPError) as failure:
        smoke.request_json(
            base, "/api/ai/ask", message="Synthetic disclosure", timeout=1
        )
    assert failure.value.code == 503
    assert len(calls) == 1
    assert calls[0][:2] == ("POST", "/api/ai/ask")
    assert json.loads(calls[0][2])["message"] == "Synthetic disclosure"


def test_busy_safe_get_can_retry(busy_http_server):
    base, calls = busy_http_server
    result = smoke.request_json(base, "/api/selfinc/status", timeout=1)
    assert result["status"] == 200
    assert result["body"] == {"ok": True}
    assert [(method, path) for method, path, _ in calls] == [
        ("GET", "/api/selfinc/status"),
        ("GET", "/api/selfinc/status"),
    ]
