"""Real full-runtime/HTTP/SQLite restart regression; only generation is doubled."""

from __future__ import annotations

import hashlib
import json
import os
import socket
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CHILD = Path(__file__).with_name("continuity_runtime.py")
FACT = "Remember that I call the little observatory in my garden the Lantern Room."
QUESTION = "What nickname did I give the place where I watch the stars?"
DISTRACTORS = [
    "My favorite tea is jasmine.",
    "My sister is called Mira.",
    "I take the number 18 bus to work.",
    "My bicycle has a silver bell.",
    "I call the shed where I keep my garden tools the Copper Finch.",
]


def session(profile, messages, label, *, live=False):
    profile.mkdir(parents=True, exist_ok=True)
    policy = profile / "policy"
    policy.mkdir(exist_ok=True)
    # Enforce the real Guardian and capability interfaces with scoped grants.
    rules = [
        {
            "requester": "service_registry",
            "subsystem": "service_registry",
            "action": "service_registry.*",
            "target": "service_registry:service",
        },
        {
            "requester": "hub:chat",
            "subsystem": "chat",
            "action": "chat.ingress",
            "target": "chat_route:/api/ai/ask",
        },
        {
            "requester": "kernel_loop",
            "subsystem": "kernel",
            "action": "kernel.shutdown",
            "target": "kernel:loop",
        },
    ]
    if live:
        rules.append(
            {
                "requester": "core:llm",
                "subsystem": "network",
                "action": "network.request",
                "target": "network:api.openai.com",
                "capabilities": ["network:outbound"],
            }
        )
    (policy / "guardian.json").write_text(
        json.dumps({"version": 1, "default": "deny", "allow": rules}), encoding="utf-8"
    )
    (policy / "capabilities.json").write_text(
        json.dumps(
            {
                "allow": {
                    "service_registry": [
                        "registry:register",
                        "registry:unregister",
                        "registry:status",
                        "registry:heartbeat",
                        "registry:message",
                        "registry:broadcast",
                        "registry:subscribe",
                    ],
                    "kernel_loop": ["kernel:control"],
                    **({"core:llm": ["network:outbound"]} if live else {}),
                }
            }
        ),
        encoding="utf-8",
    )
    (policy / "net_policy.json").write_text(
        json.dumps(
            {
                "allow_domains": [
                    "127.0.0.1",
                    "localhost",
                    *(["api.openai.com"] if live else []),
                ],
                "deny_domains": [],
            }
        ),
        encoding="utf-8",
    )
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.upper().startswith(
            (
                "AETH",
                "OPENAI",
                "ANTHROPIC",
                "GOOGLE",
                "AZURE",
                "AWS",
                "CLOUDSDK",
                "TEST",
            )
        )
        and not any(
            s in k.upper()
            for s in ("KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL", "PROXY")
        )
    }
    env.update(
        {
            "PYTHONPATH": str(ROOT),
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONIOENCODING": "utf-8",
            "HOME": str(profile),
            "USERPROFILE": str(profile),
            # Keep the pre-provisioned public embedding cache separate from private data.
            "HF_HOME": os.environ.get(
                "HF_HOME", str(Path.home() / ".cache/huggingface")
            ),
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "TOKENIZERS_PARALLELISM": "false",
            "AETHERRA_SKIP_DOTENV": "1",
            "AETHERRA_STATE_DIR": str(profile / "state"),
            "AETHERRA_WORKSPACE_ROOT": str(profile),
            "AETHERRA_POLICY_HOME": str(policy),
            "AETHERRA_GUARDIAN_POLICY": str(policy / "guardian.json"),
            "AETHERRA_GUARDIAN_STATE_DIR": str(profile / "guardian"),
            "AETHERRA_GUARDIAN_ENABLED": "1",
            "AETHERRA_GUARDIAN_MODE": "enforcing",
            "AETHERRA_GUARDIAN_REQUIRE_POLICY": "1",
            "AETHERRA_REQUIRE_CAPABILITIES": "1",
            "AETHERRA_NET_STRICT": "1",
            "AETHERRA_HOMEOSTASIS_OBSERVE_ONLY": "1",
            "AETHERRA_HOMEOSTASIS_MODE": "observe_only",
            "AETHERRA_SELFINC_ENABLED": "0",
            "AETHERRA_HMR_ENABLED": "0",
            "AETHERRA_SELF_IMPROVEMENT_AUTO_IMPLEMENT": "0",
            "AETHERRA_LYRIXA_FORCE_OFFLINE": "1",
            "AETHERRA_NO_FAKE_DATA": "1",
            "AETHERRA_REGISTRY_URL": "",
            "AETHERRA_HUB_ENABLED": "1",
            "AETHERRA_HUB_URL": f"http://127.0.0.1:{port}",
            "AETHERRA_HUB_PORT": str(port),
            "AETHERRA_HUB_PORT_AUTOFIX": "0",
            "AETHERRA_AI_API_ENABLED": "1",
            "AETHERRA_AI_API_REQUIRE_TOKEN": "1",
            "AETHERRA_AI_API_TOKEN": "synthetic-continuity-token",
            "AETHERRA_SKIP_LAUNCHER_AI_DEFAULTS": "1",
            "NO_PROXY": "*",
        }
    )
    if live:
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError(
                "Live smoke unverified: OPENAI_API_KEY is not configured"
            )
        env["OPENAI_API_KEY"] = os.environ["OPENAI_API_KEY"]
        env["AETHERRA_LLM_MODEL"] = os.environ.get("AETHERRA_LLM_MODEL", "gpt-4o")
        # The normal model manager's current primary provider is OpenAI-only.
        # Do not implicitly enable other providers or forward ambient endpoints.
    request = profile / f"{label}-input.json"
    output = profile / f"{label}-result.json"
    request.write_text(json.dumps(messages), encoding="utf-8")
    with (profile / f"{label}-runtime.log").open("w", encoding="utf-8") as log:
        proc = subprocess.run(
            [
                sys.executable,
                str(CHILD),
                str(request),
                str(output),
                *(["--live"] if live else []),
            ],
            cwd=profile,
            env=env,
            stdout=log,
            stderr=log,
            timeout=200,
        )
    assert proc.returncode == 0, (
        f"Child failed; inspect {profile / (label + '-runtime.log')}"
    )
    result = json.loads(output.read_text(encoding="utf-8"))
    assert result["initial_message_count"] == 0
    assert result["stopped"]
    for turn in result["turns"]:
        assert turn["status"] == 200
        assert turn["body"]["ok"] is True
        assert "error" not in turn["body"]["result"]
    return result


def test_personal_fact_survives_full_runtime_restart(tmp_path):
    profile = tmp_path / "primary"
    written = session(profile, [FACT, *DISTRACTORS], "write")
    saved_id = written["turns"][0]["body"]["result"]["memory_id"]
    recalled = session(
        profile, [QUESTION, "What color did I paint its door?"], "recall"
    )
    assert written["pid"] != recalled["pid"]
    turn = recalled["turns"][0]
    result = turn["body"]["result"]
    assert saved_id in {ev["id"] for ev in result["evidence"]}
    assert "Lantern Room" in result["response"]
    assert "Copper Finch" not in result["response"]
    assert len(turn["provider_prompts"]) == 1
    assert saved_id in turn["provider_prompts"][0]
    assert FACT in turn["provider_prompts"][0]
    assert saved_id in result["recall"]["record_ids"]
    assert saved_id in result["llm"]["evidence_ids"]
    assert result["llm"]["used"]
    assert not result["llm"]["fallback"]
    assert result["evidence"][0]["id"] == saved_id
    assert len(result["evidence"]) <= 3
    assert all(fact not in turn["provider_prompts"][0] for fact in DISTRACTORS)
    assert "don't know" in recalled["turns"][1]["body"]["result"]["response"]
    for log in profile.glob("*-runtime.log"):
        assert FACT not in log.read_text(encoding="utf-8")
        assert QUESTION not in log.read_text(encoding="utf-8")

    # New process, existing competing records, no observatory fact.
    missing = tmp_path / "missing"
    session(missing, DISTRACTORS, "write")
    absent = session(missing, [QUESTION], "recall")["turns"][0]
    assert "don't have" in absent["body"]["result"]["response"]
    assert absent["body"]["result"]["evidence"] == []
    # A separate completely empty profile must not see the original content/ID.
    separate = session(tmp_path / "separate", [QUESTION], "recall")["turns"][0]
    assert "don't have" in separate["body"]["result"]["response"]
    for negative in (absent, separate):
        assert saved_id not in json.dumps(negative)
        assert "Lantern Room" not in json.dumps(negative)
        assert "Copper Finch" not in negative["body"]["result"]["response"]


VARIED_CASES = [
    (
        "My aunt Leona taught me to mend a flat bike tire.",
        "Who showed me how to repair a puncture on my bicycle?",
        "Leona",
        [
            "My uncle Mateo taught me how to swim.",
            "My friend Anika repairs cars for a living.",
            "My bicycle has a silver bell.",
        ],
    ),
    (
        "I unwind after work by playing Debussy's Clair de lune on the piano.",
        "Which composition do I play to relax at the end of a workday?",
        "Clair de lune",
        [
            "On weekends I play Beethoven's Fur Elise on the violin.",
            "My brother plays jazz on his trumpet.",
            "I listen to podcasts during my commute.",
        ],
    ),
]


@pytest.mark.parametrize(
    ("fact", "question", "answer", "competitors"),
    VARIED_CASES,
)
def test_varied_paraphrases_select_evidence_after_restart(
    tmp_path, fact, question, answer, competitors
):
    written = session(tmp_path, [fact, *DISTRACTORS, *competitors], "write")
    saved_id = written["turns"][0]["body"]["result"]["memory_id"]
    restarted = session(tmp_path, [question], "recall")
    turn = restarted["turns"][0]
    result = turn["body"]["result"]
    assert written["pid"] != restarted["pid"]
    assert result["evidence"][0]["id"] == saved_id
    assert saved_id in result["llm"]["evidence_ids"]
    assert answer in result["response"]
    assert saved_id in turn["provider_prompts"][0]
    assert answer in turn["provider_prompts"][0]
    assert len(result["evidence"]) <= 3
    assert not result["llm"]["fallback"]


def live_trace(profile, recorded, *, source=None, question, expected_answer=None):
    """Verify actual SQLite → retrieval → provider-input provenance for a live turn."""
    for turn in recorded["turns"]:
        result = turn["body"]["result"]
        assert result["llm"]["used"] is True
        assert result["llm"]["fallback"] is False
        assert result["llm"]["model"]["provider"] == "openai"
        assert result["llm"]["model"]["model_name"] == "gpt-4o"
        assert result["llm"]["diag"]["event"] == "ok"
        assert result["recall"]["event"] == "ok"
        assert len(turn["provider_prompts"]) == 1
    turn = recorded["turns"][0]
    result = turn["body"]["result"]
    prompt = turn["provider_prompts"][0]
    assert f"User: {question}\n" in prompt
    supplied = [
        json.loads(line[2:]) for line in prompt.splitlines() if line.startswith("- ")
    ]
    ids = [ev["id"] for ev in supplied]
    assert ids == result["recall"]["record_ids"]
    assert ids == result["llm"]["evidence_ids"]
    assert ids == [ev["id"] for ev in result["evidence"]]
    assert len(ids) <= 3
    with sqlite3.connect(profile / "lyrixa_memory.db") as db:
        stored_evidence = []
        for ev in supplied:
            stored = json.loads(
                db.execute(
                    "SELECT content FROM memories WHERE id=?", (ev["id"],)
                ).fetchone()[0]
            )
            assert json.loads(ev["content"]) == stored
            stored_evidence.append({"id": ev["id"], "content": stored})
    if source is not None:
        saved_id = source["turns"][0]["body"]["result"]["memory_id"]
        assert source["pid"] != recorded["pid"]
        assert ids[0] == saved_id
        assert expected_answer in result["response"]
    else:
        saved_id = None
        assert ids == []
    return {
        "question": question,
        "profile": profile.name,
        "write_process": source["pid"] if source else None,
        "recall_process": recorded["pid"],
        "initial_user_message_count": recorded["initial_message_count"],
        "saved_id": saved_id,
        "stored_evidence": stored_evidence,
        "retrieved_evidence": result["evidence"],
        "generation_evidence": supplied,
        "generation_prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "retrieved_ids": ids,
        "responder": result["llm"],
        "reply": result["response"],
        "stopped": recorded["stopped"],
    }


def extended_live_matrix(profile, original_id):
    """Manual-only extension; pytest never invokes live provider calls."""
    report = {
        "model": "gpt-4o",
        "cases": {},
        "model_generated_turns": 0,
        "fallback_turns": 0,
    }

    def run_case(name, facts, question, answer=None):
        directory = profile / name
        written = session(directory, facts, "write", live=True) if facts else None
        recalled = session(directory, [question], "recall", live=True)
        for recorded in [*([written] if written else []), recalled]:
            for turn in recorded["turns"]:
                llm = turn["body"]["result"]["llm"]
                assert llm["used"] is True
                assert llm["fallback"] is False
                assert llm["model"]["provider"] == "openai"
                assert llm["model"]["model_name"] == "gpt-4o"
                report["model_generated_turns"] += 1
        trace = live_trace(
            directory,
            recalled,
            source=written if answer else None,
            question=question,
            expected_answer=answer,
        )
        trace["seed_records"] = [
            {"id": turn["body"]["result"]["memory_id"], "content": fact}
            for fact, turn in zip(
                facts, written["turns"] if written else [], strict=True
            )
        ]
        if answer is None:
            assert original_id not in json.dumps(recalled)
            assert "Lantern Room" not in json.dumps(recalled)
            assert "Copper Finch" not in trace["reply"]
            trace["original_profile_id_absent"] = original_id
            if written:
                assert written["pid"] != recalled["pid"]
                trace["write_process"] = written["pid"]
        report["cases"][name] = trace
        (profile / "extended-live-result.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )
        print(
            json.dumps(
                {
                    "case": name,
                    "retrieved_ids": trace["retrieved_ids"],
                    "reply": trace["reply"],
                    "fallback": False,
                }
            ),
            flush=True,
        )

    for name, (fact, question, answer, competitors) in zip(
        ("bicycle_paraphrase", "music_paraphrase"), VARIED_CASES, strict=True
    ):
        run_case(name, [fact, *DISTRACTORS, *competitors], question, answer)
    run_case("missing_fact", DISTRACTORS, QUESTION)
    run_case("separate_profile", [], QUESTION)
    return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Explicit live smoke through the normal full launcher and /api/ai/ask"
    )
    parser.add_argument("--live", action="store_true", required=True)
    parser.add_argument(
        "--extended",
        action="store_true",
        help="Also verify varied paraphrases and missing/separate-profile cases with gpt-4o",
    )
    parser.add_argument(
        "--profile",
        type=Path,
        required=True,
        help="New disposable directory for synthetic data",
    )
    options = parser.parse_args()
    profile = options.profile.resolve()
    if profile.exists():
        parser.error("Use a new empty profile directory")
    written = session(profile, [FACT, *DISTRACTORS], "write", live=True)
    restarted = session(
        profile, [QUESTION, "What color did I paint its door?"], "recall", live=True
    )
    saved_id = written["turns"][0]["body"]["result"]["memory_id"]
    result = restarted["turns"][0]["body"]["result"]
    print(
        json.dumps(
            {
                "saved_id": saved_id,
                "retrieved_ids": result["recall"]["record_ids"],
                "llm": result["llm"],
                "reply": result["response"],
                "door_reply": restarted["turns"][1]["body"]["result"]["response"],
            },
            indent=2,
        )
    )
    assert saved_id in result["llm"]["evidence_ids"]
    assert not result["llm"]["fallback"], "Fallback is not a live-model pass"
    assert "Lantern Room" in result["response"]
    assert all(
        turn["body"]["result"]["llm"]["used"]
        for turn in [*written["turns"], *restarted["turns"]]
    )
    if options.extended:
        live_trace(
            profile,
            restarted,
            source=written,
            question=QUESTION,
            expected_answer="Lantern Room",
        )
        extended_live_matrix(profile, saved_id)
