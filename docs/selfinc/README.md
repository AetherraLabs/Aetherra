# Self-Incorporation (v1)

Aetherra OS can discover, classify, and safely integrate changes to its own codebase.
This "self-incorporation" loop runs at boot and on-demand.

What it does (short):

- Discovers files across configured roots and indexes them into
  `.aetherra/selfinc_index.db` with a JSONL mirror `.aetherra/selfinc_index.jsonl`.
- Classifies items (plugins, agents, aether scripts, workflows, utilities, docs)
  and extracts declared capabilities + risk hints.
- Enforces policy and safety gates (signing placeholder, capability allowlists,
  network policy) and assigns a trust tier. High‑risk items are quarantined.
- Plans and applies integration actions (register plugin/agent, load workflow),
  with audit records and rollback tokens.
- Exposes status via `/api/selfinc/status` and operational endpoints:
  `/scan`, `/apply`, `/rollback`, `/audit`, plus an ethics view for decision
  transparency.

Env flags (common):

- `AETHERRA_SELFINC_ENABLED=1` (default) — enable the service.
- `AETHERRA_SELFINC_STRICT=1` — stricter capability enforcement
  (restricted/unknown blocked).
- `AETHERRA_REQUIRE_CAPABILITIES=1` — require explicit capability policy
  (default on for OS).
- `AETHERRA_NET_STRICT=1` — enforce strict network policy (allowlist only).
- `AETHERRA_HMR_ENABLED=1` — enable hot-swap/rollback integration path.

Policy files (bootstrap):

- `~/.aetherra/policy/capabilities.json` — allow + limits per capability.
- `~/.aetherra/policy/net_policy.json` — allowlist/denylist for outbound
  network.
- `~/.aetherra/policy/selfinc.json` — incorporation rules (auto-integrate,
  review, quarantine).

Use the CLI to create defaults:

```powershell
python -m Aetherra.cli.policy_bootstrap --all
# or individually
python -m Aetherra.cli.policy_bootstrap --capabilities
python -m Aetherra.cli.policy_bootstrap --network --allow api.example.com .corp.example
python -m Aetherra.cli.policy_bootstrap --selfinc
```

Operator runbook (quick):

- Strict vs non-strict: set `AETHERRA_SELFINC_STRICT=1`,
  `AETHERRA_REQUIRE_CAPABILITIES=1`, `AETHERRA_NET_STRICT=1` for production.
  In non-strict, risky items are flagged but can be staged for review.
- Quarantine triage: high-risk or policy-violating items are set to
  `quarantined`. Review audit via `/api/selfinc/audit`, update policy, then
  re‑apply with `/api/selfinc/apply`.
- Promote from quarantine: adjust `capabilities.json`/`selfinc.json`, re-run
  `/api/selfinc/scan` → `/apply`.
- Rollback steps: keep the `rb_token` from an apply response; POST it to
  `/api/selfinc/rollback` to revert a specific integration. HMR controller will
  swap back and record `HMR_ROLLBACK` in the audit trail.

Security notes:

- Signing schemes (current status): `.aether` HMAC and plugin `ed25519` are
  earmarked for enforcement; current code has a placeholder verifier and
  path‑based trust while the signing pipeline is finalized.
- How to sign: use `tools/sign_aether.py` for workflows; plugin signing will be
  documented alongside the plugin SDK once available.
- Audit: self‑incorporation decisions are persisted in
  `.aetherra/selfinc_audit.db`; HMR audit frames at
  `.aetherra/hmr_audit.jsonl`.

API quick reference:

- `GET /api/selfinc/status` — current status.
- `POST /api/selfinc/scan` — discover and classify (optional body:
  `{ "path": "/subdir" }`).
- `POST /api/selfinc/apply` — apply plan (`{ "dry_run": false }`).
- `POST /api/selfinc/rollback` — rollback by token (`{ "rb_token": "..." }`).
- `GET /api/selfinc/audit` — audit summary with query filters.
- `GET /api/selfinc/ethics/overview` — ethics dashboard summary.
- `POST /api/selfinc/ethics/evaluate` — evaluate a specific action/plan.
- `GET /api/selfinc/ethics/audit/<trace_id>` — retrieve ethics audit record.

Troubleshooting:

- If `/api/selfinc/status` is 503, the service is not registered. Ensure your
  launcher registers `self_incorporation` or run `tools/run_hub_ai_api.py`
  which registers a default service for tests.
- Windows path issues: policy and state paths are resolved via
  `%USERPROFILE%`/.aetherra; set `AETHERRA_POLICY_HOME` to override.
