# Aetherra Security System

Updated: 2026-06-15

Status: Functional Safe Baseline Complete

This document describes the current Aetherra Security System, the controls now implemented in the codebase, how to configure them, and what remains as continuous hardening work. The Security System is considered complete for the current development milestone: it is functional, tested, and safe enough to serve as Aetherra's active security foundation while the next systems are brought up to the same standard.

Security is not treated as permanently finished. Any new capability, plugin surface, network path, memory behavior, or autonomous action path must continue to pass through security review.

## Principles

- Safe by default in production.
- Least privilege for control routes, plugins, keys, network access, and execution.
- Fail closed when production security configuration is missing or invalid.
- Prefer explicit policy over implicit trust.
- Keep audit records tamper-evident and operationally useful.
- Keep development ergonomics reasonable without weakening production posture.

## Milestone Completion

The current milestone is complete because the core protection surfaces are implemented and verified:

- Hub/control authentication is centralized and enforced on mutation/control routes.
- Production API exposure fails closed when required token policy is not enabled.
- API key storage supports encrypted state, scoped access, migration, validation, and safe-mode deletion protection.
- Security audit records use a signed, hash-chained JSONL ledger.
- Plugin execution is isolated by default in production when possible and fails closed when isolation cannot be established.
- Expression/script execution no longer relies on unrestricted `eval`, `exec`, or shell execution paths.
- Network egress is policy checked through safe HTTP wrappers.
- Federation and telemetry surfaces are guarded by explicit enablement, local-only development behavior, token checks, and bounded payload/state handling.
- Static and repository security scanners are part of the verification workflow.

## Verification Snapshot

Latest verification for this milestone:

- Security regression suite: `186 passed, 1 skipped`.
- Repository security scan: `high=0`.
- Static security scan: `0 findings`.
- Ruff checks on touched security/scanner cleanup files: passed.
- Python byte compilation on touched production/security modules: passed.
- `git diff --check`: passed, with only Git line-ending warnings.

The skipped test is an optional dependency case in hub signing when Flask or PyNaCl is unavailable.

## Core Components

### Control Authentication

Module: `aetherra_hub/services/control_auth.py`

Control authentication centralizes token handling for hub mutation and administrative routes.

Implemented behavior:

- Supports `Authorization: Bearer <token>` and `X-Aetherra-Token`.
- Uses constant-time token comparison.
- Requires explicit token configuration for production control routes.
- Allows limited development fallback behavior only where appropriate.
- Provides structured authorization results for consistent route handling.

Guarded route areas include scripts, plugins, agents, telemetry, peers/federation, trainer, consciousness, homeostasis, self-improvement, self-incorporation, interactive routes, and QFAC administration.

### Production Security Guard

Module: `aetherra_hub/app.py`

Production startup now validates unsafe configuration before enabling sensitive API behavior.

Important behavior:

- If the AI API is enabled in production, `AETHERRA_AI_API_REQUIRE_TOKEN=1` must be set.
- Missing required token enforcement causes startup/configuration failure instead of silently exposing control surfaces.
- Development behavior remains usable without normalizing insecure production defaults.

### API Key Security

Module: `Aetherra/security/api_keys.py`

The API key layer is now a production-grade local secret manager for Aetherra's current stage.

Implemented behavior:

- Dynamic state directory support through environment-controlled state paths.
- Atomic writes and file locking.
- Key name validation.
- Encrypted-at-rest storage with master-key support.
- Plaintext-to-encrypted migration while preserving existing entries.
- Scoped production access with deny-by-default behavior.
- Corruption handling that fails closed.
- Safe-mode protection that blocks destructive key deletion.

Primary functions:

- `get_key(name)`
- `set_key(name, value)`
- `delete_key(name)`
- `get_key_scoped(name, requester)`
- `ensure_master_key()`

See also: `docs/api-keys.md`.

### Audit Ledger

Module: `Aetherra/security/audit_ledger.py`

Security audit records are written to a signed, hash-chained JSONL ledger.

Implemented behavior:

- Sequence-numbered append-only records.
- HMAC signatures.
- Hash chaining between records.
- Per-path locks for concurrent writers.
- Atomic append behavior.
- Sidecar key management.
- Legacy prefix anchoring.
- Integrity verification through `verify_integrity`.

Integrated audit paths include:

- `Aetherra/aetherra_core/system/security_system.py`
- `aetherra_hub/services/security.py`
- Plugin audit logging
- Lockdown recovery authorization records

Lockdown recovery fails closed if the audit ledger is tampered with or cannot be written.

### Sandbox and Restricted Execution

Module: `Aetherra/security/sandbox.py`

The sandbox now separates three concerns: safe expression evaluation, restricted statement execution, and isolated process execution.

Implemented behavior:

- `safe_eval` supports only tightly validated expressions.
- Dangerous AST nodes and calls are rejected.
- Builtin shadowing, custom callables, oversized containers, unsafe sequence multiplication, and unsafe exponent behavior are rejected.
- `execute_restricted_python` supports a narrow statement language for simple assignments, expressions, and captured `print`.
- Imports, loops, functions, file access, process access, and other broad Python execution features are blocked in restricted mode.
- `run_isolated` provides spawn-based process isolation with JSON-only args/results and hard timeout termination.
- `run_command_no_shell` executes commands with `shell=False`, bounded output, token validation, and timeout handling.

Important note:

`run_with_timeout` remains a trusted/cooperative helper. It is not a security boundary for untrusted code.

### Script and Command Executors

Modules:

- `Aetherra/stdlib/executor.py`
- `Aetherra/aetherra_core/script_service/script_executor.py`

Executor behavior has been hardened:

- Raw unrestricted `exec` was removed from these paths.
- Python snippets are routed through `execute_restricted_python`.
- Shell commands are routed through `run_command_no_shell`.
- Shell metacharacter/operator injection is rejected by the command parser.
- Execution results preserve useful output without exposing broad host execution.

### Plugin Security

Primary modules:

- `Aetherra/aetherra_core/plugins/plugin_manager.py`
- `Aetherra/security/plugin_signing.py`
- `aetherra_hub/blueprints/plugins.py`

Implemented behavior:

- Production plugin execution uses process isolation by default when reconstructable.
- If a production plugin cannot be safely isolated, execution fails closed.
- Plugin execution audit events are written through the signed ledger.
- Plugin registration and mutation routes require control authorization.
- Unsigned development-mode behavior is not allowed to downgrade production registration checks.
- Plugin signing state honors dynamic policy/state directories.

### Capability Policy

Module: `Aetherra/security/capabilities.py`

Capability checks support explicit policy-driven access.

Implemented behavior:

- Dynamic policy path support.
- Strict production behavior.
- Deny-by-default capability enforcement where strict mode applies.
- Test coverage for allow/deny policy behavior and limits.

### Network Policy and Federation

Modules:

- `Aetherra/security/net_policy.py`
- `Aetherra/hub/federation.py`
- `aetherra_hub/blueprints/peers.py`

Implemented behavior:

- Dynamic network policy path support.
- Domain allow/deny policy enforcement.
- Safe HTTP wrappers for outbound requests.
- Federation peer management requires control authorization.
- Peer URLs are validated.
- Sync/announce behavior is disabled unless `AETHERRA_FEDERATION_ENABLED=1`.
- Federation outbound calls use policy-checked HTTP wrappers and outbound auth headers.

### Telemetry Privacy and Ingress Hardening

Modules:

- `Aetherra/telemetry/optin.py`
- `aetherra_hub/blueprints/telemetry.py`

Implemented behavior:

- Telemetry remains opt-in.
- Telemetry mutation/ingress routes use control authorization or local-only development behavior.
- Payload size is bounded.
- In-memory telemetry state is bounded.
- Sender behavior includes token support.

### Prompt and AI Route Safety

Modules:

- `Aetherra/security/prompt_defense.py`
- `aetherra_hub/blueprints/ai_ask.py`
- `aetherra_hub/blueprints/ai_stream.py`

Implemented behavior:

- AI ask routes run safety precheck before engine dispatch.
- Policy violations return structured responses.
- AI ask and stream auth use centralized token logic.
- Missing-token bypass behavior was removed.

## Configuration

Common environment flags:

```powershell
$env:AETHERRA_PROFILE='production'
$env:AETHERRA_AI_API_ENABLED='1'
$env:AETHERRA_AI_API_REQUIRE_TOKEN='1'
$env:AETHERRA_AI_API_TOKEN='<strong-token>'
$env:AETHERRA_REQUIRE_CAPABILITIES='1'
$env:AETHERRA_NET_STRICT='1'
$env:AETHERRA_SIGNING_STRICT='1'
$env:AETHERRA_SCRIPT_VERIFY_STRICT='1'
$env:AETHERRA_FEDERATION_ENABLED='0'
```

Policy/state path controls:

- `AETHERRA_POLICY_HOME`
- `AETHERRA_STATE_DIR`
- `AETHERRA_KEYS_MASTER`

Production guidance:

- Require tokens for all AI/control API exposure.
- Enable strict capability and network policy.
- Enable strict plugin/script signing where applicable.
- Keep federation disabled unless actively deployed and policy-reviewed.
- Use encrypted API key storage or environment-provided secrets.

## Verification Commands

Security regression suite:

```powershell
python -m pytest tests\unit\test_security_audit_ledger.py tests\unit\test_api_keys_enforcement.py tests\unit\test_api_keys_prod_encryption_required.py tests\unit\test_plugin_manager_audit.py tests\unit\test_capabilities_policy.py tests\unit\test_capability_limits.py tests\unit\test_net_policy.py tests\unit\test_sandbox_isolation.py tests\capabilities\test_security_sandbox_placeholders.py tests\capabilities\test_security_capabilities_coverage.py tests\unit\test_control_auth.py tests\unit\test_hub_ingress_security.py tests\unit\test_hub_script_control_auth.py tests\unit\test_hub_plugin_control_security.py tests\unit\test_hub_mutation_control_auth.py tests\unit\test_hub_plugin_registration_non_strict.py tests\unit\test_prod_security_guard.py tests\unit\test_prod_security_defaults.py tests\unit\test_qfac_admin_endpoints.py tests\unit\test_invalid_token_metric.py tests\unit\test_security_metrics_phase0.py tests\unit\test_hub_ai_api.py tests\unit\test_hub_agents_api.py tests\unit\test_hub_chat_safety_preflight.py tests\unit\test_security_ledger_disabled.py tests\unit\test_federation_persistence.py tests\unit\test_hub_inthread.py tests\unit\test_state_mapper_formula_security.py tests\unit\test_stdlib_executor_security.py tests\unit\test_script_executor.py tests\integration\test_webhook_manager_security.py tests\test_hub_signing.py tests\test_core_ai_runtime_baseline.py -q --no-cov
```

Repository security scan:

```powershell
$env:AETHERRA_SCAN_VERBOSE='0'
python tools\repo_security_scan.py
```

Static security scan:

```powershell
python tools\static_security_scan.py --root Aetherra --json security_scan.json --md security_scan.md
```

## Known Limitations and Continuous Hardening

The current milestone is complete, but these remain ongoing engineering responsibilities:

- Security review must be repeated whenever new autonomous capabilities are added.
- The Guardian System is not yet built; once implemented, it should sit above the Security layer as a higher-order oversight system.
- Process isolation is the current production-grade plugin boundary; container or VM isolation should be considered for untrusted third-party plugin ecosystems.
- Existing legacy systems outside the security boundary may still need quality cleanup as each system is completed.
- Network/TLS/CORS hardening depends on deployment topology and should be reviewed per environment.
- Threat modeling should be refreshed as Aetherra grows from a Cognitive Operating Layer toward more autonomous operation.

## References

Primary code:

- `Aetherra/security/api_keys.py`
- `Aetherra/security/audit_ledger.py`
- `Aetherra/security/capabilities.py`
- `Aetherra/security/net_policy.py`
- `Aetherra/security/plugin_signing.py`
- `Aetherra/security/prompt_defense.py`
- `Aetherra/security/sandbox.py`
- `Aetherra/aetherra_core/system/security_system.py`
- `Aetherra/aetherra_core/plugins/plugin_manager.py`
- `Aetherra/stdlib/executor.py`
- `Aetherra/aetherra_core/script_service/script_executor.py`
- `aetherra_hub/services/control_auth.py`
- `aetherra_hub/services/security.py`

Primary tests:

- `tests/unit/test_security_audit_ledger.py`
- `tests/unit/test_api_keys_enforcement.py`
- `tests/unit/test_api_keys_prod_encryption_required.py`
- `tests/unit/test_plugin_manager_audit.py`
- `tests/unit/test_sandbox_isolation.py`
- `tests/unit/test_control_auth.py`
- `tests/unit/test_hub_ingress_security.py`
- `tests/unit/test_hub_mutation_control_auth.py`
- `tests/unit/test_state_mapper_formula_security.py`
- `tests/unit/test_stdlib_executor_security.py`
- `tests/unit/test_script_executor.py`
- `tests/integration/test_webhook_manager_security.py`

Related docs:

- `docs/api-keys.md`
- `docs/SECURITY_OPERATIONS_GUIDE.md`
- `docs/AETHERRA_CODING_SYSTEM.md`
- `SECURITY.md`

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
