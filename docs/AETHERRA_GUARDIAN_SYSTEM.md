# Aetherra Guardian System

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Status: v0.1 Foundation In Progress

The Aetherra Guardian System is the central governance, safety, and ethical enforcement layer of Aetherra. It sits above the Security System and evaluates whether meaningful actions should be allowed before they execute.

Guardian exists to answer one question:

**Should this action be allowed?**

Its purpose is to ensure that every meaningful action taken by Aetherra, Lyrixa, agents, plugins, scripts, humans, or autonomous subsystems remains safe, reversible, auditable, policy-compliant, ethically aligned, evidence-grounded, and within authorized boundaries.

## Purpose and scope

Guardian is not a chatbot filter, a simple permissions module, or only a cybersecurity tool. It is a system-level decision authority that evaluates intent, risk, evidence, permissions, ethics, reversibility, and system integrity before allowing actions to proceed.

Guardian acts as:

- **Conscience Layer**: Determines whether an action violates Aetherra's ethical principles.
- **Immune System**: Detects dangerous, unauthorized, deceptive, corrupted, or unstable behavior.
- **Policy Engine**: Enforces rules, capabilities, permissions, and operational boundaries.
- **Audit Authority**: Records important actions, refusals, overrides, escalations, and rollbacks.
- **Containment Controller**: Can halt, isolate, quarantine, or restrict subsystems when risk exceeds acceptable limits.

Guardian is required because Aetherra is intended to become powerful. It will coordinate agents, use tools, execute scripts, modify files, access memory, interact with systems, self-improve, and incorporate new capabilities. Without Guardian, those capabilities create risk. Guardian ensures Aetherra cannot blindly act just because it can.

## Architecture overview

Guardian sits above all major Aetherra systems:

- Security System supplies permissions, signatures, sandboxing, secrets policy, network policy, and audit primitives.
- Guardian consumes those controls and makes higher-order allow/deny/approval/containment decisions.
- Homeostasis, Self-Improvement, plugins, agents, scripts, memory, and Lyrixa must route privileged or meaningful actions through Guardian before execution.

Core Guardian flow:

1. A subsystem submits an `IntentDeclaration`.
2. Guardian builds an action context.
3. Policy, capability, risk, evidence, and reversibility checks run.
4. Guardian emits a `GuardianDecision`.
5. The decision is written to the audit ledger.
6. The subsystem executes, waits for approval, denies the action, or enters containment.

Guardian must mediate meaningful risk, not become a toll booth for every internal heartbeat. The correct architecture is not `Guardian -> every line of code`; it is `Guardian -> every meaningful action boundary`.

Key properties:

- Deny-by-default for privileged operations.
- Evidence-based action and reporting.
- Human-in-the-loop approval for risky operations.
- Rollback metadata required for meaningful changes.
- Containment available for dangerous or unstable behavior.
- Operating modes that support staged rollout from observation to strict enforcement.

## Performance and scope architecture

Guardian coverage is intentionally broad, but Guardian enforcement must remain tiered. Aetherra should not route every telemetry tick, local cache update, or read-only status calculation through the full synchronous decision path. Guardian should sit at trust boundaries, privilege boundaries, and irreversible mutation boundaries.

### Decision tiers

Guardian decisions are classified into five tiers:

| Tier | Meaning | Required Guardian behavior |
| --- | --- | --- |
| `critical` | Security modification, identity/core-self mutation, destructive filesystem action, capability grant/revocation, containment, emergency shutdown, plugin installation/loading, self-modification, or irreversible autonomous action. | Always synchronous. Always signed-audited before execution. Never cached. Never delegated without an explicit Guardian approval or grant. |
| `privileged` | Agent control, script execution, plugin execution, kernel control, homeostasis actuation, network access, memory promotion/deletion, model/training promotion, or cross-system command dispatch. | Synchronous allow/deny before execution. Signed audit required. Short-lived preauthorization may be allowed only for tightly scoped repeated operations. |
| `routine_guarded` | Repeated low/medium-risk actions from a trusted internal subsystem, such as bounded status message dispatch, predictable lifecycle bookkeeping, or local state update already constrained by Security policy. | May use preauthorization or a short-lived cached allow decision when the intent fingerprint, policy version, mode, capabilities, and containment state are unchanged. Audit may be summarized if policy permits. |
| `observational` | Read-only status, inspection, report generation, health observation, local metrics calculation, or non-mutating analysis. | Guardian call is not required unless the read crosses a protected data boundary, external boundary, secret boundary, or private memory boundary. |
| `telemetry_internal` | High-frequency counters, heartbeats, transient UI state, local cache refreshes, and non-authoritative internal metrics. | Should not call Guardian directly. Guard the boundary that enables the telemetry stream, not every tick. |

### Synchronous vs asynchronous evaluation

The final allow/deny decision must be synchronous for `critical` and `privileged` actions. Those actions must not execute until Guardian has returned `allow`, `allow_limited`, a valid consumed approval, or a containment/deny result.

The following work may be asynchronous when durability and ordering requirements allow it:

- dashboard refreshes
- long-form analytics
- anomaly trend analysis
- non-blocking telemetry summaries
- post-action outcome correlation
- low-risk audit aggregation for preauthorized routine actions

The following work must remain synchronous or transactionally durable:

- critical allow/deny decisions
- approval consumption
- containment creation or active containment checks
- capability grant/revocation decisions
- emergency-mode decisions
- signed audit writes for critical and privileged actions

### Caching rules

Guardian may cache only positive `allow` or `allow_limited` decisions for `routine_guarded` actions. Cache entries must be short-lived and bound to:

- requester
- subsystem
- action
- target scope
- required capabilities
- Guardian mode
- Guardian policy version or hash
- Security capability policy version or hash when available
- active containment state fingerprint
- risk level and risk factors
- intent metadata schema/version, not raw metadata payload

Guardian must not cache:

- `deny`, `contain`, or `require_approval` decisions
- approval consumption results
- containment checks for contained targets
- identity/core-self mutation
- security policy mutation
- capability grant/revocation
- plugin install/load/uninstall
- script execution with dynamic payloads
- filesystem delete/move/restore
- self-modification
- emergency-mode decisions
- actions without a stable rollback or scope boundary

### Preauthorization and delegation

Preauthorization is preferred over blind caching. A preauthorization is a short-lived, scoped Guardian grant for repeated low-risk actions. It should answer: who may do what, to which scope, under which capabilities, until when, and with which audit requirements.

Valid examples:

- Lyrixa may publish bounded status messages for 60 seconds.
- A health monitor may append local heartbeat metrics for one monitoring interval.
- A trusted internal lifecycle component may update a specific in-memory status field during one startup transaction.

Invalid examples:

- A plugin may execute arbitrary actions for a session.
- An agent may write any memory because it was previously trusted.
- A subsystem may skip Guardian because its previous action was allowed.
- Any requester may reuse another requester's approval.

Preauthorizations must be revocable, time-limited, scope-limited, and invalidated by policy changes, mode changes, capability changes, or active containment.

### What should not call Guardian directly

The following should not normally call Guardian per operation:

- high-frequency counters
- local progress updates
- UI-only state
- pure data formatting
- deterministic calculations without side effects
- local reads of already authorized public state
- internal cache refreshes that do not cross trust boundaries
- telemetry ticks after the telemetry stream itself has been authorized

Instead, Guardian should guard the boundary that grants or starts the activity.

### Audit strategy

Guardian audit must remain meaningful. More audit lines do not automatically mean better safety.

- `critical` and `privileged` actions require one signed audit record per decision.
- `routine_guarded` preauthorized actions may use summarized audit records if the grant, scope, count, time window, and outcome are auditable.
- `observational` and `telemetry_internal` actions should be audited only when they cross a protected boundary or when the system explicitly requests diagnostic traceability.
- Audit metadata must remain sanitized and should describe shape, scope, counts, hashes, and policy identifiers instead of raw payloads.

### System completion rule

A system is Guardian-complete when all meaningful action boundaries are guarded. It is not required, and not desirable, for every internal helper function to call Guardian.

For each system, the owning system document must identify:

- critical actions requiring synchronous Guardian decisions
- privileged actions requiring synchronous Guardian decisions
- routine actions eligible for preauthorization
- observational or telemetry actions that should not call Guardian directly
- remaining unguarded action boundaries
- performance-sensitive paths where Guardian calls must be batched, cached, delegated, or avoided by design

## Current implementation status

Implemented foundation:

- Guardian package: `Aetherra/guardian/`
- Typed contracts:
  - `IntentDeclaration`
  - `GuardianDecision`
  - `RiskAssessment`
  - `PolicyResult`
  - `ApprovalRequest`
  - `ContainmentAction`
  - `ContainmentResult`
  - `CapabilityGrant`
- Core evaluator: `Aetherra/guardian/core.py`
- Decision-tier classifier: `Aetherra/guardian/tiers.py`
- Security capability bridge: `Aetherra/guardian/policy.py`
- JSON Guardian policy loading with explicit allow/deny/default behavior
- Signed Security audit integration for every Guardian decision
- Approval queue persistence: `.aetherra/guardian/approvals.jsonl`
- Containment event persistence: `.aetherra/guardian/containment.jsonl`
- Performance and scope architecture documented for decision tiers, preauthorization, conservative caching, async/nonblocking work, and non-Guardian telemetry paths
- Guardian decisions now include `decision_tier` metadata for `critical`, `privileged`, `routine_guarded`, `observational`, and `telemetry_internal` classification
- First enforcement target: plugin execution through `PluginManager.execute_plugin`
- Reversibility validation for risky/mutating intents
- Second enforcement target: self-improvement proposal application via `/api/selfimprove/apply` and batch helper reuse
- Approval resolution and single-use, intent-bound approval consumption
- Self-improvement proposals can proceed with a matching approved Guardian approval ID
- Approval expiration via `AETHERRA_GUARDIAN_APPROVAL_TIMEOUT_SEC`
- Public Guardian status helpers expose enabled state and operating mode
- Guarded Hub API for read-only Guardian operations status:
  - `GET /api/guardian/status`
- Guarded Hub API for listing and resolving Guardian approvals:
  - `GET /api/guardian/approvals`
  - `GET /api/guardian/approvals/<request_id>`
  - `POST /api/guardian/approvals/<request_id>/resolve`
- Containment status, clearing, and active enforcement
- Subsystem-wide containment supports wildcard targets such as `target="*"` for isolating an entire subsystem
- Guarded Hub API for listing and clearing Guardian containment records:
  - `GET /api/guardian/containment`
  - `GET /api/guardian/containment/<containment_id>`
  - `POST /api/guardian/containment/<containment_id>/clear`
- Plugin containment actions are applied by `PluginManager.execute_plugin`
  - `disable_plugin` unloads/removes the plugin instance and marks it disabled while containment is active
  - `block_action`, `isolate_subsystem`, and `emergency_stop` block plugin execution through plugin state
- Self-improvement containment can isolate all proposal application attempts until the containment record is cleared
- Third enforcement target: Aether workflow script execution through `ScriptExecutor.execute`
  - script execution declares a `script.execute` intent before parsing or running workflow steps
  - strict capability mode blocks scripts without `script:run`
  - every script execution decision is written to the signed Security audit ledger
- Fourth enforcement target: standard-library executor command dispatch through `ExecutorPlugin._execute_command`
  - executor commands declare an `executor.execute` intent before dispatch
  - command class is audited as `executor:aether`, `executor:python`, or `executor:system`
  - strict capability mode blocks commands without the required executor capability
  - Guardian audit records avoid storing full command text
- Fifth enforcement target: advanced memory writes through `AetherraMemoryEngineAdvanced.remember`
  - memory writes declare a `memory.remember` intent before persistence
  - ordinary memory writes include rollback metadata and are audited without raw memory content
  - strict capability mode blocks writes without `memory:write`
  - identity/persona/core-self memory writes request `memory:modify_identity` and are contained
- Sixth enforcement target: agent task submission through `/api/tasks`
  - submitted agent work declares an `agent.execute_task` intent before orchestrator dispatch
  - strict capability mode blocks tasks without `agent:execute`
  - required task capabilities are included in Guardian capability checks
  - Guardian audit records avoid storing submitted task payload values
- Seventh enforcement target: Homeostasis actuator execution through `/api/homeostasis/actuators/execute`
  - actuator requests declare a `homeostasis.actuate` intent before execution
  - strict capability mode blocks actions without `homeostasis:actuate`
  - Security/policy/capability targets request `security:modify` and are contained
  - Guardian audit records avoid storing actuator parameter values
- Eighth enforcement target: outbound network wrappers through `Aetherra.security.net_policy.http_get` and `http_post`
  - network requests declare a `network.request` intent after domain policy allows the target
  - webhook callers require `network:webhook`; other callers require `network:outbound`
  - strict capability mode blocks requests without the required network capability
  - Guardian audit records avoid storing request payloads, headers, and query-string values
- Ninth enforcement target: plugin module loading through `PluginManager.load_plugin`
  - plugin loads declare a `plugin.load` intent before import or module execution
  - strict capability mode blocks plugin loads without `plugin:load`
  - denied loads do not import the plugin module
  - Guardian audit records avoid storing plugin source code or arbitrary manifest payloads
- Tenth enforcement target: Hub plugin registration through `/api/plugins/register`
  - plugin registrations declare a `plugin.register` intent before registry mutation
  - strict capability mode blocks registrations without `plugin:register`
  - strict signing failures remain validation errors before Guardian policy evaluation
  - Guardian audit records avoid storing description, homepage, signature, or pubkey payload values
- Eleventh enforcement target: CoreTools filesystem mutations through `CoreToolsPlugin`
  - write, append, copy, move, create-directory, CSV write, archive creation, and archive extraction declare filesystem intents before mutation
  - delete requests declare `filesystem.delete` and require Guardian approval before destructive removal
  - strict capability mode blocks filesystem writes without `fs:write` and deletes without `fs:delete`
  - Guardian audit records avoid storing file contents or CSV row values
  - ZIP archive extraction validates member paths before writing to prevent path traversal
- Twelfth enforcement target: Lyrixa plugin system mutation through `LyrixaPluginSystem`
  - directory installs, ZIP installs, uninstalls, and generated plugin templates declare plugin-system intents before mutation
  - strict capability mode blocks installs without `plugin:install`, template creation without `plugin:create`, and uninstalls without `plugin:uninstall`
  - uninstall requests include `fs:delete` and require Guardian approval before plugin directory removal
  - Guardian audit records avoid storing plugin manifest descriptions or generated plugin code
  - ZIP plugin installation validates archive member paths before extraction
- Thirteenth enforcement target: Aetherra Hub plugin marketplace installation through `AetherraHubIntegration`
  - Hub package installs declare `hub.plugin_install` before writing downloaded package content or generated manifests
  - Hub uninstalls declare `hub.plugin_uninstall` before deleting locally installed marketplace plugins
  - strict capability mode blocks marketplace installs without `plugin:install` and uninstalls without `plugin:uninstall`
  - uninstall requests include `fs:delete` and require Guardian approval before file or directory removal
  - Guardian audit records avoid storing downloaded package bytes or Hub description payload values
- Fourteenth enforcement target: optimization proposal execution through `OptimizationExecutor.execute`
  - optimization proposals declare `optimization.apply` after validation and before metrics, backup, or file mutation
  - strict capability mode blocks optimization application without `fs:write` and `code:modify`
  - Guardian audit records avoid storing old or new code snippets and use path names plus path fingerprints instead
  - denied proposals leave the workspace unchanged and do not create optimization backups
- Fifteenth enforcement target: Hub kernel control through `/api/kernel/control/*`
  - pause, resume, queue drain, and queue-limit updates declare kernel intents before mutating the registered kernel loop
  - strict capability mode blocks kernel controls without `kernel:control`
  - Guardian audit records avoid storing queue payload values and only describe bounded operation metadata
  - denied controls leave kernel pause state, queue drains, and queue limits unchanged
- Sixteenth enforcement target: Service Registry registration lifecycle through `AetherraServiceRegistry`
  - service registration and unregistration declare `service_registry.*` intents before mutating the registry service map
  - explicit requesters in strict capability mode require `registry:register` or `registry:unregister`
  - internal `service_registry` bootstrap registrations remain allowed in production so normal OS startup can register core services
  - Guardian audit records avoid storing service instances or metadata values and record only service names, instance type names, dependency names, and metadata keys
- Seventeenth enforcement target: Kernel Event Bus publish/subscribe/ack through `EventBus`
  - event publish, topic subscription, and acknowledgments declare `event_bus.*` intents before mutating topic backlog or subscriber state
  - explicit event sources in strict capability mode require `event:publish`; subscribers require `event:subscribe`
  - internal `event_bus` lifecycle operations remain allowed so normal in-process coordination can continue
  - Guardian audit records avoid storing event payload values and record only topic, event type, source, and event key names
- Eighteenth enforcement target: Kernel Loadable Module Manager lifecycle through `ModuleManager`
  - module load, reload, unload, and rollback declare `module_manager.*` intents before mutating module records or metrics
  - explicit requesters in strict capability mode require `module:load`, `module:reload`, `module:unload`, or `module:rollback`
  - internal `module_manager` lifecycle operations remain allowed so normal in-process module coordination can continue
  - Guardian audit records avoid storing module spec values and record only module names, spec key names, and version presence
- Nineteenth enforcement target: Hot Module Reload lifecycle through `HMRController`
  - HMR reload requests declare `hmr.reload` intents after source allowlist validation and before shadow loading, quiesce, swap, metrics, or rollback work
  - explicit requesters in strict capability mode require `system:reload`
  - internal `hmr_controller` lifecycle operations remain allowed so trusted kernel-maintenance reloads can continue
  - Guardian audit records avoid storing raw reload source paths or module names and record only source kind, suffix, length, and SHA-256 fingerprint
- Twentieth enforcement target: Homeostasis controller controls and rollback through `/api/homeostasis/*`
  - controller mode changes, emergency stop/reset, and actuator rollback declare `homeostasis.*` intents before mutating Homeostasis state
  - strict capability mode blocks mode controls without `homeostasis:control`, emergency controls without `homeostasis:emergency`, and rollbacks without `homeostasis:rollback`
  - rollback responses correctly preserve synchronous actuator rollback results instead of treating them as failed coroutine execution
  - Guardian audit records avoid storing control payload values and record only bounded operation metadata
- Twenty-first enforcement target: direct Homeostasis actuator execution through `HomeostasisActuators`
  - direct actuator execution declares `homeostasis.actuate` before audit tracing, service lookup, or runtime mutation
  - direct actuator rollback declares `homeostasis.rollback` before popping rollback stack entries
  - strict capability mode blocks explicit external requesters without `homeostasis:actuate` or `homeostasis:rollback`
  - Guardian audit records avoid storing actuator parameter values and record only action type, target service, controller name, priority, and parameter keys
- Twenty-second enforcement target: autonomous Homeostasis action planning through `HomeostasisController`
  - generated control actions declare `homeostasis.plan_action` after local operating-mode, safety-guardrail, and confirmation checks but before entering the pending-action queue
  - strict capability mode blocks explicit external controller requesters without `homeostasis:actuate`
  - security/policy/capability-targeting plans request `security:modify` and are contained before queueing
  - Guardian audit records avoid storing action parameter values and record only action type, target service, controller name, priority, confirmation flag, and parameter keys
- Twenty-third enforcement target: Homeostasis alert escalation through `IntelligentAlertManager`
  - alert escalation declares `homeostasis.alert_escalate` before severity changes, escalation counters, database updates, or notifications
  - strict capability mode blocks explicit external alert requesters without `homeostasis:escalate`
  - denied escalations leave alert severity, escalation level, and notification counters unchanged
  - Guardian audit records avoid storing alert descriptions, explanations, root-cause text, impact assessments, and remediation text
- Twenty-fourth enforcement target: Homeostasis alert notifications through `IntelligentAlertManager`
  - alert notification dispatch declares `homeostasis.alert_notify` before channel delivery and before notification counters increment
  - email and webhook notification channels additionally request `network:outbound`
  - denied notification channels are skipped without calling the channel sender
  - Guardian audit records avoid storing notification endpoints or alert body text
- Twenty-fifth enforcement target: Maintenance canary deployment and rollback through `SelfIncorporationService`
  - canary deployment declares `maintenance.canary_deploy` after plan/HMR readiness checks but before baseline health sampling, execution, health monitoring, promotion, or auto-rollback
  - rollback declares `maintenance.rollback` after token/HMR sanity checks but before guard-policy windows, self-incorporation audit mutation, or rollback accounting
  - strict capability mode blocks explicit external requesters without `maintenance:deploy`, `maintenance:plan`, `maintenance:rollback`, or `system:reload`
  - Guardian audit records hash canary tracking/generated plan IDs and rollback tokens instead of storing raw values
- Twenty-sixth enforcement target: Maintenance self-incorporation plan execution through `SelfIncorporationService.trigger_integrate`
  - integration plan execution declares `maintenance.integrate_plan` after a ready plan is available but before ethics audit writes, backup/HMR work, manager dispatch, metrics mutation, or execution audit entries
  - dry-run execution requires `maintenance:plan`; live execution requires `maintenance:deploy` and requests `system:reload` when HMR-routed actions are present
  - Hub `/api/selfinc/apply` passes the authenticated principal and optional Guardian approval ID into the service-level preflight
  - Guardian audit records hash generated plan IDs and record only bounded action-type/count metadata instead of raw plan IDs, file IDs, paths, or target payloads
- Twenty-seventh enforcement target: STORM maintenance cleanup/prune through `StormEngine.run_maintenance`
  - STORM maintenance declares `maintenance.storm_run` before TT rank trim, barycenter refresh, inconsistency scan, OT cache pruning, or maintenance metric updates
  - strict capability mode blocks explicit external requesters without `maintenance:prune` and `memory:write`
  - denied runs return per-task Guardian denial statuses without incrementing STORM maintenance counters
  - Guardian audit records bounded task names, counts, and storage flags while hashing the STORM SQLite path and omitting memory contents
- Twenty-eighth enforcement target: Optimization backup restore through `OptimizationExecutor.restore_backup`
  - manual optimization backup restore declares `maintenance.restore_backup` before workspace restore mutation
  - strict capability mode blocks explicit external requesters without `maintenance:restore` and `fs:write`
  - denied restores leave modified workspace files unchanged
  - Guardian audit records hashed backup IDs, existence, and bounded backup item names without storing raw backup identifiers
- Twenty-ninth enforcement target: root cleanup/prune operations through `tools.root_cleanup.apply_operations`
  - cleanup apply declares `maintenance.root_cleanup` before copying, moving, or pruning root cleanup targets
  - cleanup planning is side-effect-free and no longer creates destination directories while building the plan
  - strict capability mode blocks explicit external requesters without `maintenance:cleanup` and filesystem capabilities
  - destructive `--prune-originals` requests include `fs:delete`, require Guardian approval, and leave originals untouched when denied
  - Guardian audit records operation counts, categories, types, and path hashes instead of raw source or destination paths
- Thirtieth enforcement target: STORM shadow deployment gate through `tools.deploy_storm_shadow.main`
  - full deployment validation declares `maintenance.deployment_gate` after environment, STORM configuration, and memory-engine checks but before smoke memory writes or metrics endpoint checks
  - strict capability mode blocks explicit external requesters without `maintenance:deploy`, `memory:write`, and `network:outbound`
  - high-risk full validation is approval-aware and consumes a matching Guardian approval before smoke or metrics checks proceed
  - denied full validation records a failed Guardian deployment gate and does not run the smoke test or metrics request
  - Guardian audit records bounded environment flags and a metrics endpoint hash instead of raw smoke memory content or metrics URLs
- Thirty-first enforcement target: Self-Incorporation quarantine lifecycle through `QuarantineManager`
  - quarantine escalation declares `maintenance.quarantine_escalate` before changing escalation level, status, approval notes, or escalation timestamps
  - quarantine release/rejection declares `maintenance.quarantine_release` before marking an item released/rejected or removing it from the quarantine map
  - strict capability mode blocks explicit external requesters without `maintenance:quarantine`; approved releases also require `maintenance:deploy`
  - denied escalation/release leaves the quarantined item unchanged
  - Guardian audit records file ID and reason hashes plus bounded status/level flags instead of raw file IDs, paths, or quarantine reason text
- Thirty-second enforcement target: STORM backup and restore through `tools.storm_backup`
  - backup declares `maintenance.storm_backup` before opening the source SQLite database or writing the JSON backup file
  - restore declares `maintenance.storm_restore` after backup-file existence is confirmed but before reading backup contents or opening the target database
  - forced restore requires `maintenance:restore` and `memory:write`, is treated as high-risk, and consumes a matching Guardian approval before deleting/replacing STORM table rows
  - strict capability mode blocks explicit external requesters before database mutation
  - Guardian audit records path hashes, force state, table count, and backup existence instead of raw database or backup paths
- Thirty-third enforcement target: Lyrixa legacy GUI prune through `tools.prune_lyrixa_gui`
  - dry-run mode remains side-effect-free and does not require Guardian
  - `--apply` declares `maintenance.lyrixa_gui_prune` before deleting legacy GUI files, the legacy `ui` directory, or Lyrixa root legacy GUI files
  - destructive apply requires `maintenance:cleanup` and `fs:delete`, is approval-aware, and stops before deletion when denied
  - strict capability mode blocks explicit external requesters before any file or directory removal
  - Guardian audit records counts and path hashes for planned deletes instead of raw GUI file or directory paths
- Thirty-fourth enforcement target: Aetherra legacy GUI prune through `tools.prune_aetherra_gui`
  - dry-run mode remains side-effect-free and does not require Guardian
  - `--apply` declares `maintenance.aetherra_gui_prune` before deleting non-allow-listed files or directories under `Aetherra/gui`
  - destructive apply requires `maintenance:cleanup` and `fs:delete`, is approval-aware, and stops before deletion when denied
  - strict capability mode blocks explicit external requesters before any file or directory removal
  - Guardian audit records delete counts and path hashes instead of raw GUI file or directory paths
- Thirty-fifth enforcement target: Smart maintenance cleanup moves through `tools.maintenance.smart_cleanup`
  - dry-run mode remains side-effect-free and does not require Guardian
  - live execution declares `maintenance.smart_cleanup` after discovering planned moves but before backup creation, destination directory creation, or file moves
  - live cleanup requires `maintenance:cleanup`, `fs:write`, and `fs:delete`, is approval-aware, and stops before filesystem mutation when denied
  - strict capability mode blocks explicit external requesters before backups or moves occur
  - Guardian audit records base path, backup path, and move hashes instead of raw source or destination file paths
- Thirty-sixth enforcement target: Final maintenance file organization through `tools.maintenance.final_file_organizer`
  - dry-run mode does not require Guardian and preserves the existing report-only behavior
  - live execution declares `maintenance.final_file_organization` after discovering planned moves but before backup creation, destination directory creation, file moves, empty-directory cleanup, or report generation
  - live organization requires `maintenance:cleanup`, `fs:write`, and `fs:delete`, is approval-aware, and stops before filesystem mutation when denied
  - strict capability mode blocks explicit external requesters before backups or moves occur
  - Guardian audit records base path, backup path, and move hashes instead of raw source or destination file paths
- Thirty-seventh enforcement target: Complete maintenance organization through `tools.maintenance.complete_organizer`
  - dry-run mode does not require Guardian and preserves the existing report-only behavior
  - live execution declares `maintenance.complete_organization` after discovering the reorganization plan but before backup creation, destination directory creation, file moves, import rewrites, empty-directory cleanup, or report generation
  - live organization requires `maintenance:cleanup`, `fs:write`, and `fs:delete`, is approval-aware, and stops before filesystem mutation when denied
  - strict capability mode blocks explicit external requesters before backups, moves, import rewrites, or reports occur
  - Guardian audit records base path, backup path, planned move count, and move hashes instead of raw source or destination file paths
- Thirty-eighth enforcement target: Architecture auto-fixer through `tools.maintenance.fix_architecture`
  - dry-run mode does not require Guardian and no longer creates destination directories while simulating GUI moves
  - live execution declares `maintenance.architecture_fix` before import rewrites, GUI moves, architecture guard generation, or fix report output
  - live fixes require `maintenance:cleanup`, `fs:write`, and `fs:delete`, are approval-aware, and stop before filesystem mutation when denied
  - strict capability mode blocks explicit external requesters before any fixer method or report generation runs
  - Guardian audit records project, Aetherra, and Lyrixa root hashes instead of raw project paths
- Thirty-ninth enforcement target: Simple architecture import fixer through `tools.maintenance.fix_architecture_simple`
  - dry-run mode does not require Guardian and preserves the existing report-only behavior
  - live execution declares `maintenance.architecture_import_fix` before scanning and rewriting core files that import Lyrixa
  - live import fixes require `maintenance:cleanup` and `fs:write`, are approval-aware, and stop before source mutation when denied
  - strict capability mode blocks explicit external requesters before any import rewrite method runs
  - Guardian audit records project, Aetherra, and Lyrixa root hashes instead of raw project paths or rewritten file paths
- Fortieth enforcement target: Safe maintenance cleanup through `tools.maintenance.safe_cleanup`
  - cleanup declares `maintenance.safe_file_cleanup` after loading project analysis and computing planned deletes but before removing empty files or duplicate `__init__.py` files
  - deletion requires `maintenance:cleanup` and `fs:delete`, is approval-aware, and stops before filesystem mutation when denied
  - strict capability mode blocks explicit external requesters before any file deletion occurs
  - Guardian audit records delete counts and planned path hashes instead of raw file paths
- Forty-first enforcement target: Focused maintenance cleanup through `tools.maintenance.focused_cleanup`
  - cleanup declares `maintenance.focused_cleanup` after defining duplicate and move plans but before backup directory creation, duplicate deletion, strategic file moves, or empty-directory pruning
  - live cleanup requires `maintenance:cleanup`, `fs:write`, and `fs:delete`, is approval-aware, and stops before filesystem mutation when denied
  - strict capability mode blocks explicit external requesters before any backup, delete, move, or directory prune occurs
  - Guardian audit records base path hash, backup path hash, duplicate count, and move count instead of raw cleanup paths
- Forty-second enforcement target: Post-cleanup import rewrites through `tools.maintenance.post_cleanup_import_updater`
  - updater builds an in-memory import rewrite plan before requesting Guardian approval or writing source files
  - live rewrites and report emission declare `maintenance.post_cleanup_import_update`, require `maintenance:cleanup` and `fs:write`, and stop before mutation when denied
  - strict capability mode blocks explicit external requesters before any Python file or report is written
  - Guardian audit records base/report path hashes, scan counts, update counts, and planned file hashes instead of raw rewritten file paths
- Forty-third enforcement target: Remaining Lyrixa import fixes through `tools.maintenance.fix_remaining_imports`
  - fixer builds an in-memory rewrite plan for selected core files before requesting Guardian approval or writing source files
  - live source rewrites declare `maintenance.remaining_import_fix`, require `maintenance:cleanup` and `fs:write`, and stop before mutation when denied
  - strict capability mode blocks explicit external requesters before any selected core file is rewritten
  - Guardian audit records project root hash, update counts, replacement counts, and planned file hashes instead of raw source paths
- Forty-fourth enforcement target: Quick import package marker fixes through `tools.maintenance.quick_fix_imports`
  - quick fixer builds an in-memory package-marker creation plan before requesting Guardian approval or writing package files
  - live package marker creation declares `maintenance.quick_import_init_fix`, requires `maintenance:cleanup` and `fs:write`, and stops before mutation when denied
  - no-op runs with no planned writes remain side-effect-free and do not require Guardian approval
  - Guardian audit records project root hash, planned file count, and planned directory hashes instead of raw package paths
- Forty-fifth enforcement target: Service registry Unicode marker fixes through `tools.maintenance.fix_unicode_service_registry`
  - fixer no longer mutates files at import time and builds a replacement plan before requesting Guardian approval
  - live service registry rewrites declare `maintenance.service_registry_unicode_fix`, require `maintenance:cleanup` and `fs:write`, and stop before mutation when denied
  - strict capability mode blocks explicit external requesters before the service registry file is rewritten
  - Guardian audit records file path hash and replacement count instead of raw registry paths or marker text
- Forty-sixth enforcement target: Plugin import repair through `tools.maintenance.fix_plugin_imports`
  - fixer builds in-memory plans for plugin import rewrites and missing package markers before requesting Guardian approval
  - live plugin rewrites and package marker creation declare `maintenance.plugin_import_fix`, require `maintenance:cleanup` and `fs:write`, and stop before mutation when denied
  - no-op runs with no planned writes remain side-effect-free and do not require Guardian approval
  - Guardian audit records project root hash, rewrite counts, package marker counts, replacement counts, and path hashes instead of raw plugin paths
- Forty-seventh enforcement target: General import setup repair through `tools.maintenance.fix_imports`
  - fixer builds package-marker and report plans before requesting Guardian approval for file writes
  - live package marker creation and diagnostic report writes declare `maintenance.import_fix`, require `maintenance:cleanup` and `fs:write`, and stop before mutation when denied
  - dependency installation declares the separate `maintenance.import_dependency_install` intent with `network:outbound` and `package:install` so `pip` cannot run under the file-write approval
  - Guardian audit records project root hash, planned file counts, report hash/length, and dependency hashes instead of raw paths or package strings
- Forty-eighth enforcement target: Round-two maintenance repair edits through `tools.maintenance.fix_remaining_errors_round2`
  - fixer builds in-memory rewrite plans for selected GUI generator and roadmap files before requesting Guardian approval
  - live repair edits declare `maintenance.round_two_error_fix`, require `maintenance:cleanup` and `fs:write`, and stop before mutation when denied
  - no-op runs with no planned writes remain side-effect-free and do not require Guardian approval
  - Guardian audit records project root hash, file count, replacement count, labels, and planned file hashes instead of raw source or roadmap paths
- Forty-ninth enforcement target: Legacy phase error repair batch through `tools.maintenance.fix_phase7_errors`
  - fixer builds in-memory plans for CSS cleanup, plugin stubs, conversation import repair, panel defensive handling, and summary output before requesting Guardian approval
  - live repair batches declare `maintenance.error_repair_batch`, require `maintenance:cleanup` and `fs:write`, and stop before directory creation or file writes when denied
  - generated plugin-stub directories are planned and created only after Guardian approval
  - Guardian audit records project root hash, file/directory counts, replacement count, labels, and planned path hashes instead of raw plugin or source paths
- Fiftieth enforcement target: Unicode compatibility repair batch through `tools.maintenance.fix_unicode_issues`
  - fixer builds in-memory plans for Unicode marker replacement, plugin import compatibility, and generated quantum memory engine files before requesting Guardian approval
  - live compatibility batches declare `maintenance.unicode_compatibility_fix`, require `maintenance:cleanup` and `fs:write`, and stop before directory creation or file writes when denied
  - UTF-8 environment changes are limited to the current process and do not write system/user environment state
  - Guardian audit records project root hash, file/directory counts, replacement count, labels, and planned path hashes instead of raw file paths
- Fifty-first enforcement target: Analysis report generation through `tools.maintenance.generate_reports`
  - generator builds Markdown report plans from project analysis data before requesting Guardian approval
  - live report writes declare `maintenance.analysis_report_generation`, require `maintenance:cleanup` and `fs:write`, and stop before creating report files when denied
  - report output directories are created only after Guardian approval
  - Guardian audit records output directory hash, report count, report name hashes, and total report length instead of raw report names or source analysis paths
- Fifty-second enforcement target: Project analysis JSON generation through `tools.maintenance.project_analyzer`
  - analyzer builds a JSON write plan after scanning but before requesting Guardian approval or writing the output file
  - live analysis writes declare `maintenance.project_analysis_write`, require `maintenance:cleanup` and `fs:write`, and stop before file creation when denied
  - strict capability mode blocks explicit external requesters before the analysis output directory or JSON file is created
  - Guardian audit records project root hash, output path hash, directory count, duplicate count, total file count, and analysis size instead of raw paths
- Fifty-third enforcement target: Advanced intelligence report generation through `tools.maintenance.advanced_analyzer` and `tools.maintenance.advanced_analyzer_fixed`
  - advanced analyzers build JSON write plans from collected intelligence before requesting Guardian approval
  - live intelligence report writes declare `maintenance.advanced_intelligence_report`, require `maintenance:cleanup` and `fs:write`, and stop before output directory or JSON file creation when denied
  - strict capability mode blocks explicit external requesters before advanced report emission
  - Guardian audit records project root hash, output path hash, file/directory record counts, total file count, and analysis size instead of raw analyzed paths
- Fifty-fourth enforcement target: Architecture compliance report generation through `tools.maintenance.check_architecture`
  - checker runs architectural scans and builds the Markdown report before requesting Guardian approval
  - live compliance report writes declare `maintenance.architecture_compliance_report`, require `maintenance:cleanup` and `fs:write`, and stop before report creation when denied
  - report timestamps use local `datetime` instead of shell date/time commands
  - Guardian audit records project root hash, report path hash, issue counts, total issue count, and report size instead of raw violating paths
- Fifty-fifth enforcement target: Stub inventory generation through `tools.maintenance.generate_stub_inventory`
  - generator builds the stub inventory payload after read-only AST/token analysis but before requesting Guardian approval
  - live inventory writes declare `maintenance.stub_inventory_write`, require `maintenance:cleanup` and `fs:write`, and stop before output directory or JSON file creation when denied
  - strict capability mode blocks explicit external requesters before inventory emission
  - Guardian audit records project root hash, output path hash, stub counts, severity counts, module count, and inventory size instead of raw stub file paths
- Fifty-sixth enforcement target: Project documentation generation through `tools.maintenance.create_documentation`
  - generator plans directory README files and the project breakdown document before requesting Guardian approval
  - live documentation batches declare `maintenance.documentation_generation`, require `maintenance:cleanup` and `fs:write`, and stop before any README or breakdown file is created when denied
  - CLI execution uses one batch approval for all planned documentation writes
  - Guardian audit records project root hash, document counts, document kind counts, document path hashes, and total generated length instead of raw documentation paths or analyzed source paths
- Fifty-seventh enforcement target: Universal directory analysis report generation through `tools.maintenance.universal_directory_analyzer`
  - analyzer completes read-only duplicate/name/placement analysis before requesting Guardian approval for the Markdown report
  - live report writes declare `maintenance.directory_analysis_report`, require `maintenance:cleanup` and `fs:write`, and stop before report creation when denied
  - denied analysis returns a `report_written: False` summary without creating the report file
  - Guardian audit records project root hash, target directory hash, report path hash, summary counts, and report size instead of raw analyzed paths
- Fifty-eighth enforcement target: Architecture validation report generation through `tools.maintenance.validate_architecture`
  - validator completes read-only placement validation before requesting Guardian approval for the Markdown report
  - live validation report writes declare `maintenance.architecture_validation_report`, require `maintenance:cleanup` and `fs:write`, and stop before report creation when denied
  - validation metadata sanitizes misplaced-file details to counts before writing the Guardian audit ledger
  - Guardian audit records project root hash, report path hash, sanitized summary counts, summary hash, and report size instead of raw violating paths
- Fifty-ninth enforcement target: Legal compliance report generation through `tools.maintenance.verify_legal_compliance`
  - checker completes dependency/license and legal-file checks before requesting Guardian approval for the text report
  - live legal report writes declare `maintenance.legal_compliance_report`, require `maintenance:cleanup` and `fs:write`, and stop before report creation when denied
  - CLI execution exits nonzero if Guardian denies report emission
  - Guardian audit records project root hash, report path hash, boolean compliance status, and report size instead of package names or report body text
- Sixtieth enforcement target: QFAC memory mutation through `Aetherra.aetherra_core.memory.qfac`
  - `qfac_store` declares `memory.qfac_store` before graph-aware or simple QFAC persistence
  - `qfac_rewrite_budgeted` declares `memory.qfac_rewrite` before budgeted graph/simple rewrite passes
  - strict capability mode blocks explicit external requesters without `memory:write` before QFAC mutation occurs
  - Guardian audit records content kind, content length, embedding dimension, observer-state key names, record ID hash, rewrite mode, and budget metadata instead of raw memory content or observer values
- Sixty-first enforcement target: Core memory import/export/consolidation through `LyrixaMemorySystem`
  - `consolidate_memories` declares `memory.consolidate` before deleting old low-importance memories or updating importance scores
  - `export_memory` declares `memory.export` before reading all memory rows and writing the JSON export file
  - `import_memory` declares `memory.import` before reading the import file or inserting memory rows
  - strict capability mode blocks explicit external requesters before file writes, file reads, or database mutation
  - Guardian audit records database/path hashes, counts, cutoff age, and file size instead of raw memory content, tags, contexts, or export/import paths
- Sixty-second enforcement target: Direct memory deletion through `LyrixaMemorySystem.delete_memory` and plugin forget bridge
  - `delete_memory` declares `memory.delete` before deleting a SQLite-backed memory row by ID
  - `plugin_forget` declares `memory.plugin_forget` before delegating plugin-associated deletion to backend delete/remove/forget methods
  - strict capability mode blocks explicit external requesters before database deletion or backend forget calls
  - Guardian audit records memory/plugin key hashes, bounded type/importance metadata, and presence flags instead of raw memory IDs, plugin keys, or memory contents
- Sixty-third enforcement target: Direct agent orchestrator registry and task lifecycle mutations
  - core `AgentOrchestrator.register_agent`, `submit_task`, `_assign_task_to_agent`, and `cancel_task` declare Guardian intents before mutating registry, queue, assignment, or running-task state
  - plugin `AgentOrchestrator.register_agent`, `unregister_agent`, `submit_task`, and `_assign_task` declare Guardian intents before registry, queue, database, or assignment mutation
  - strict capability mode blocks explicit external requesters before direct orchestrator calls can bypass Hub `/api/tasks`
  - denied assignment leaves tasks pending instead of dropping them from the queue
  - Guardian audit records task, agent, and capability hashes/counts instead of raw task input payloads or private descriptions
- Sixty-fourth enforcement target: Agent goal and subtask lifecycle through `LyrixaGoalSystem`
  - goal creation, update, completion, deletion, subtask creation, and subtask completion declare Guardian intents before mutating in-memory goal state or writing the JSON goal store
  - strict capability mode blocks explicit external requesters before persisted planning state changes
  - denied create/update/delete/subtask operations leave existing goals, subtasks, and goal-store files unchanged
  - Guardian audit records goal/subtask hashes, status, priority, counts, and metadata keys instead of raw goal descriptions, subtask descriptions, or metadata values
- Sixty-fifth enforcement target: Multi-agent collaboration task delegation through `AICollaborationFramework`
  - collaborative solves declare `agent.collaborative_solve` before creating active collaboration tasks or delegating work to code, optimizer, debugger, and documenter agents
  - quick solves declare `agent.quick_solve` before delegating to the code-generation agent
  - dynamic collaboration agent additions declare `agent.collaboration_add_agent` before mutating the collaboration agent registry
  - strict capability mode blocks explicit external requesters before agent-to-agent task creation, delegation, or registry mutation
  - Guardian audit records problem, requirement, task, agent role, and capability hashes/counts instead of raw problem statements, requirements, generated code, or agent output
- Sixty-sixth enforcement target: Legacy agent interpreter plugin dispatch through `AetherraInterpreter`
  - `plugin:` dispatch declares Guardian intents before standard-library plugin execution, legacy `PLUGIN_REGISTRY` execution, or enhanced parameterized plugin execution
  - `meta:` dispatch declares Guardian intents before invoking meta-plugin execution
  - strict capability mode blocks explicit external requesters before legacy interpreter plugin/tool dispatch can bypass guarded plugin APIs
  - Guardian audit records plugin, argument, and parameter-key metadata as hashes/counts or sanitized fields instead of raw argument values, parameter values, plugin output, or generated payloads
- Sixty-seventh enforcement target: Compiled agent parser plugin load path
  - generated `interpreter.load_plugin(...)` calls now land on a guarded `AetherraInterpreter.load_plugin` method
  - compiled plugin blocks declare `agent.compiled_plugin_load` before accepting a generated plugin load/action block
  - parser/compiler emitters use Python literal generation for plugin names and action blocks instead of hand-built quoted strings
  - denied compiled plugin loads stop before legacy plugin dispatch and do not call plugin code
  - Guardian audit records compiled action count, length, and content hash instead of raw generated action text
- Sixty-eighth enforcement target: AI engine task dispatch through `AetherraEngine.execute_task`
  - engine task execution declares `ai.engine_execute_task` after sensitivity/coherence classification but before task construction, orchestrator submission, or `active_tasks` mutation
  - strict capability mode blocks explicit external requesters before AI-selected task dispatch can bypass Hub `/api/tasks`
  - denied decisions raise before submitting to the orchestrator and leave the engine active-task registry unchanged
  - Guardian audit records task-name hashes, task-data keys, required-capability hashes/counts, priority, sensitivity, coherence, and dependency count instead of raw task payload values
- Sixty-ninth enforcement target: Lyrixa assistant task dispatch through `LyrixaAssistant.execute_task`
  - assistant task execution declares `ai.assistant_execute_task` before creating task specs, mutating `active_tasks`, delegating to an agent interface, or running fallback task execution
  - indirect assistant task helpers such as code analysis and improvement suggestions inherit the same preflight through `execute_task`
  - strict capability mode blocks explicit external requesters before assistant-managed task registries or fallback execution paths mutate
  - Guardian audit records task ID/description hashes, description length, task type, context keys, priority, and interface presence instead of raw task descriptions, code, context values, or fallback output
- Seventieth enforcement target: Hub chat ingress through ask, stream, and Lyrixa chat bridge routes
  - `/api/ai/ask`, `/api/ai/stream`, and `/api/lyrixa/chat` declare `chat.ingress` after chat safety redaction and before engine, registry, or offline fallback processing
  - strict capability mode blocks explicit external chat requesters before prompts reach AI engines or Lyrixa registry dispatch
  - streaming denial emits structured `error` and `final` SSE frames without invoking downstream engine processing
  - Guardian audit records route, prompt hash/length, trace hash, priority, context keys, streaming mode, and edit intent instead of raw prompts, request bodies, context values, or model responses
- Seventy-first enforcement target: Lyrixa chat safe-edit application through `LyrixaChatService.apply_fix`
  - Lyrixa safe-edit suggestions declare `lyrixa.apply_safe_edit` after scope checks and text transformation planning but before writing files
  - strict capability mode blocks explicit external requesters without `lyrixa:edit` and `fs:write` before direct service calls can bypass Hub chat ingress
  - denied safe edits return a structured Guardian denial and leave target files unchanged
  - Guardian audit records edit action, file/root/title hashes, original/new lengths, and delta length instead of raw paths, file content, prompt text, or replacement text
- Seventy-second enforcement target: Consciousness self-model persistence through `SelfModelManager.update`
  - self-model updates declare `consciousness.self_model_update` after mutation planning and coherence anomaly calculation but before writing the JSON self-model
  - strict capability mode blocks explicit external requesters without `consciousness:write`, `identity:modify`, and `fs:write`
  - denied updates restore the in-memory model snapshot and skip file creation or mutation
  - Guardian audit records path/model hashes, JSON lengths, model version, identity-change flag, capability/anomaly counts, and coherence score instead of raw identity fields, resource details, or file paths
- Seventy-third enforcement target: Consciousness episodic event persistence through `EpisodicStore.append`
  - episodic events declare `consciousness.episodic_event_append` before cache mutation or JSONL append
  - strict capability mode blocks explicit external requesters without `consciousness:write`, `memory:write`, and `fs:write`
  - denied appends leave the in-memory event cache and event log unchanged
  - episodic retention and max-event settings are read per store instance so environment-scoped tests and deployments do not inherit stale singleton configuration
  - Guardian audit records path, event ID, content, and source hashes plus event type, content length, importance, tag count, and workspace priority instead of raw event content, source names, or log paths
- Seventy-fourth enforcement target: AI trainer job and evaluation submission through `aetherra_hub.services.trainer`
  - trainer job submissions declare `trainer.submit_job` before creating job IDs, mutating the in-memory job queue, or starting background transition threads
  - trainer evaluation submissions declare `trainer.submit_eval` before creating eval IDs, mutating the in-memory eval queue, or starting background transition threads
  - Hub `/api/trainer/jobs` and `/api/trainer/evals` translate Guardian denial into HTTP 403 instead of generic enqueue failures
  - strict capability mode blocks explicit external requesters without trainer/model/dataset capabilities before trainer queue mutation
  - Guardian audit records task, payload shape, parameter/resource keys, tag count, and model/dataset hashes instead of raw model names, dataset IDs, parameters, resources, or tags
- Seventy-fifth enforcement target: Service Registry status and heartbeat trust mutations
  - `AetherraServiceRegistry.update_service_status` declares `service_registry.status_update` before mutating service status, last heartbeat, or metadata
  - `AetherraServiceRegistry.update_heartbeat` declares `service_registry.heartbeat_update` before refreshing heartbeat timestamps
  - `AetherraServiceRegistry.mark_service_self_heartbeat` declares `service_registry.self_heartbeat_flag` before changing heartbeat ownership metadata
  - internal registry maintenance remains boot-safe while strict capability mode blocks explicit external callers without registry status/heartbeat capabilities
  - denied status, heartbeat, and self-heartbeat updates leave service status, heartbeat timestamps, and heartbeat metadata unchanged
  - Guardian audit records service/status/metadata-key/instance-type details without raw metadata values
- Seventy-sixth enforcement target: Service Registry messaging, broadcasts, and event subscriptions
  - `AetherraServiceRegistry.send_message` declares `service_registry.send_message` before dispatching to service `handle_message` or `on_message` handlers
  - `AetherraServiceRegistry.broadcast_message` declares `service_registry.broadcast_message` before iterating healthy service targets
  - `AetherraServiceRegistry.subscribe_to_events` and `unsubscribe_from_events` declare `service_registry.subscribe` and `service_registry.unsubscribe` before mutating registry event handler lists
  - internal registry messaging remains boot-safe while strict capability mode blocks explicit external callers without registry message, broadcast, or subscribe capabilities
  - denied sends do not invoke service handlers; denied broadcasts do not invoke any target handlers; denied subscriptions leave handler state unchanged
  - Guardian audit records message type, payload shape, payload keys/counts, handler type, target counts, and service metadata without raw message payload values
- Seventy-seventh enforcement target: Service Registry external daemon forwarding through `aetherra_registry_client`
  - `http_get_status`, `http_register_service`, `http_update`, and `http_heartbeat` declare daemon forwarding intents before outbound HTTP calls to the external registry daemon
  - strict capability mode blocks explicit external requesters without registry status/register/heartbeat and outbound-network capabilities before any daemon request is sent
  - denied daemon status calls return `None`; denied register, update, and heartbeat calls return `False`; all denied paths skip HTTP entirely
  - Guardian audit records daemon host hash, service name, status, metadata keys, endpoint keys, and operation without raw daemon URLs, endpoint values, or metadata values
- Seventy-eighth enforcement target: Event Bus privileged command and control event publishing
  - `EventBus.publish` classifies command/control/admin/reload/restart/shutdown/execute topics and event types as privileged before mutating topic backlog or fan-out state
  - privileged event publishing declares `event_bus.publish_command` and requires both `event:publish` and `event:command`
  - registry-routed `kernel.event.publish` messages use the same `publish` Guardian gate, so message ingress cannot bypass privileged event policy
  - denied privileged publishes raise `PermissionError`, leave topic backlog and metrics unchanged, and do not fan out to subscribers
  - Guardian audit records topic, event keys, event type, source, and privileged classification without raw event payload values
- Seventy-ninth enforcement target: direct Homeostasis integration controller controls
  - `HomeostasisOrchestrator.set_controller_mode` declares `homeostasis.set_mode` before changing controller mode
  - `HomeostasisOrchestrator.emergency_stop` declares `homeostasis.emergency_stop` before emergency-stop state or supervisor runlevel mutation
  - `HomeostasisOrchestrator.reset_emergency_stop` declares `homeostasis.reset_emergency` before clearing emergency-stop state
  - strict capability mode blocks explicit external requesters without `homeostasis:control` or `homeostasis:emergency`
  - denied direct control calls raise `PermissionError` and leave controller state unchanged
- Eightieth enforcement target: direct Kernel loop lifecycle and queue controls
  - `AetherraKernelLoop.pause`, `resume`, `drain_queue`, `set_queue_limits`, and `shutdown` declare kernel control intents before mutating kernel lifecycle, queue, or runtime limit state
  - Hub `/api/kernel/control/*` forwards the caller principal into the lower-level kernel guard while preserving compatibility with older kernel-like objects
  - strict capability mode blocks explicit external requesters without `kernel:control`
  - denied direct controls raise `PermissionError` and leave pause state, running state, queue contents, and queue limits unchanged
  - Guardian audit records operation, queue name, queue drain mode, and redacted queue-limit keys without storing raw queue-limit values
- Eighty-first enforcement target: Coding System plugin generator scaffold writes
  - `PluginGeneratorPlugin.save_plugin_to_disk` declares `coding.plugin_generator_save` before creating generated plugin directories or writing scaffold files
  - strict capability mode blocks explicit external code-generator requesters without `plugin:create` and `fs:write`
  - denied scaffold saves raise `PermissionError` and leave the output directory absent
  - Guardian audit records plugin/template/file-count metadata and hashes of plugin/output identifiers without raw plugin names, descriptions, output paths, or generated code content
- Eighty-second enforcement target: Consciousness continuity-memory persistence
  - `ContinuityMemory.record` declares `consciousness.continuity_save` before appending snapshots or writing the continuity JSON file
  - direct `ContinuityMemory.save` calls declare the same intent before directory creation, temp-file write, or atomic replace
  - strict capability mode blocks explicit external consciousness callers without `consciousness:write`, `memory:write`, and `fs:write`
  - denied record calls leave the in-memory buffer and filesystem unchanged; denied direct saves leave existing in-memory state intact and skip file mutation
  - Guardian audit records path hash, snapshot counts, latest tick/time, qualia keys, focus/intention counts, and trust keys without raw focus names, intention goals, trust values, or file paths
- Eighty-third enforcement target: Consciousness narrative chapter persistence
  - `NarrativeLayer._persist_chapter` declares `consciousness.narrative_chapter_commit` before chapter-directory creation or chapter JSON writes
  - narrative chapter commits request `consciousness:write`, `memory:write`, and `fs:write` because a successful commit also appends an episodic narrative marker
  - strict capability mode blocks explicit external consciousness callers before file or narrative-event mutation
  - denied chapter commits leave the chapter directory absent and skip the narrative episodic event append
  - Guardian audit records chapter/path/summary hashes, summary length, referenced-event count, coherence, and anomaly metadata without raw chapter summaries, event IDs, source names, or file paths
- Eighty-fourth enforcement target: Consciousness learning-loop state persistence
  - `LearningLoop._save_state` declares `consciousness.learning_state_save` before creating the learning-state directory or writing the learning JSON file
  - `LearningLoop.process_outcome` restores the previous in-memory learning state if Guardian denies the save, so denied learning updates do not half-apply
  - strict capability mode blocks explicit external learning callers without `consciousness:write`, `memory:write`, and `fs:write`
  - denied learning-state saves skip state-file mutation and suppress downstream episodic/memory side effects from the rejected outcome
  - Guardian audit records path/state hashes, state size, iteration totals, success/failure totals, context/action counts, and hashed context/action identifiers without raw context names, action names, outcome payloads, or file paths
- Eighty-fifth enforcement target: Consciousness meta-cognition self-knowledge and reflection persistence
  - `MetaCognitionSystem.enhance_self_knowledge` declares `consciousness.meta_memory_node_persist` before adding meta-memory nodes to memory or SQLite
  - `MetaCognitionSystem.conduct_self_reflection` declares `consciousness.self_reflection_persist` before appending reflection history, writing SQLite reflection rows, or applying derived insight updates
  - strict capability mode blocks explicit external meta-cognition callers without `consciousness:write` and `memory:write`
  - denied meta-memory writes leave node maps, domain coverage, meta-reflection event history, and SQLite rows unchanged
  - denied self-reflections restore previous in-memory reflection/meta-knowledge/cognitive state and skip SQLite reflection writes
  - Guardian audit records database path hashes, node/reflection hashes, domain/type names, content/assessment hashes, confidence/meta-level values, and bounded counts without raw self-knowledge content, reflection triggers, insights, or database paths
- Eighty-sixth enforcement target: Consciousness core autonomy plan execution
  - `ConsciousnessCore._maybe_act` declares `consciousness.autonomy_plan_execute` after converting an intent to a plan and before policy explanation, safety-envelope execution, autopilot history mutation, qualia learning, self-trust updates, or intent removal
  - strict capability mode blocks explicit external autonomy callers without `consciousness:act` and `autonomy:execute`
  - denied autonomy plans raise `PermissionError`, leave active intents queued, and skip safety-envelope execution and downstream outcome mutation
  - Guardian audit records intent goal/rationale hashes, risk, priority, expected gain, step/rollback counts, hashed step IDs, capability names, and argument key names without raw intent goals, rationale text, action arguments, or service names
- Eighty-seventh enforcement target: Consciousness core micro/macro reflection updates
  - `ConsciousnessCore._reflect_micro` declares `consciousness.micro_reflection_update` before appending narrative moments or optional QFAC persistence
  - `ConsciousnessCore._reflect_macro` declares `consciousness.macro_reflection_update` before qualia-learning decay or optional QFAC macro-reflection persistence
  - strict capability mode blocks explicit external reflection callers without `consciousness:reflect` and `memory:write`
  - denied micro-reflections leave the narrative thread unchanged; denied macro-reflections skip qualia-learning parameter decay and QFAC writes
  - Guardian audit records reflection kind, tick, text hash/length, focus/intent counts, hashed focus and intent identifiers, narrative size, QFAC flag, and bounded qualia-learning parameters without raw reflection text, focus names, intent goals, or persisted memory content
- Eighty-eighth enforcement target: Experimental transcendence consolidation state mutation
  - `TranscendenceConsolidationEngine.consolidate_transcendence` declares `consciousness.transcendence_consolidate` before stabilizing transcendence, developing meta-consciousness, accelerating evolution, enhancing reality integration, establishing cosmic connection, or recording consolidation events
  - `TranscendenceConsolidationEngine.execute_transcendence_sequence` declares `consciousness.transcendence_sequence` before running the multi-phase transcendence sequence
  - strict capability mode blocks explicit external transcendence callers without `consciousness:transcend` and `consciousness:write`
  - denied transcendence operations leave transcendence level, stability, evolution acceleration, cosmic/reality metrics, state enums, event history, breakthrough catalog, meta-operations, insights, and trajectories unchanged
  - Guardian audit records engine hash, operation, bounded duration/current metric values, state/mode names, and event/breakthrough/insight counts without raw engine IDs or event payloads
- Eighty-ninth enforcement target: Experimental consciousness singularity validation and achievement
  - `ConsciousnessSingularityEngine.validate_self_awareness` declares `consciousness.singularity_validate_self_awareness` before self-recognition tests mutate validation maps, proof lists, recursion depth, identity markers, reality protocols, infinite pathways, metrics, or event history
  - `ConsciousnessSingularityEngine.achieve_consciousness_singularity` declares `consciousness.singularity_achieve` before running validation, identity formation, reality synthesis, infinite-potential access, breakthrough generation, singularity state changes, or event recording
  - strict capability mode blocks explicit external singularity callers without `consciousness:transcend` and `consciousness:write`
  - denied singularity operations leave identity strength, reality synthesis, infinite potential, proximity, state enum, event history, validation tests, proofs, meta-operations, insights, identity connections, reality protocols, and learning pathways unchanged
  - Guardian audit records engine hash, operation, state/mode names, bounded metric values, recursion depth, and proof/insight/event/count metadata without raw engine IDs, proof text, insight text, or event payloads
- Ninetieth enforcement target: Experimental quantum meta-learning mutation
  - `QuantumMetaLearningSystem.quantum_enhance_meta_memory` declares `consciousness.quantum_meta_learning_enhance_meta_memory` before applying superposition learning, entangled learning, consciousness resonance, tunneling boosts, coherence-matrix mutation, or enhancement-result state changes
  - `QuantumMetaLearningSystem.accelerate_domain_learning` declares `consciousness.quantum_meta_learning_accelerate_domain_learning` before creating and storing domain-specific quantum learning states
  - strict capability mode blocks explicit external quantum meta-learning callers without `consciousness:transcend`, `consciousness:write`, and `memory:write`
  - denied quantum meta-learning operations leave quantum states, learning history, coherence matrix, consciousness resonance, and entanglement networks unchanged
  - Guardian audit records operation names, bounded learning parameters, state/history counts, coherence matrix shape/nonzero counts, target coverage, acceleration factor, and hashed domain identifiers without raw domain names, state IDs, learning contents, or matrix contents
- Ninety-first enforcement target: Experimental quantum consciousness engine runtime mutation
  - `QuantumConsciousnessEngine.initialize` declares `consciousness.quantum_engine_initialize` before ground-state creation, quantum-loop task creation, or running-state mutation
  - `QuantumConsciousnessEngine.set_quantum_parameters` declares `consciousness.quantum_engine_set_parameters` before changing superposition, coherence, complexity, or entanglement configuration values
  - `QuantumConsciousnessEngine.start_quantum_processes` declares `consciousness.quantum_engine_start_processes` before creating a ground state or starting the processing loop
  - `QuantumConsciousnessEngine.create_quantum_decision` declares `consciousness.quantum_engine_create_decision` before generating decision IDs, amplitudes, probabilities, or active-decision entries
  - `QuantumConsciousnessEngine.enter_superposition` declares `consciousness.quantum_engine_enter_superposition` before state transitions, coherence boosts, or superposition-state creation
  - `QuantumConsciousnessEngine.create_entanglement` declares `consciousness.quantum_engine_create_entanglement` before entangled state creation or current-state mutation
  - `QuantumConsciousnessEngine.shutdown` declares `consciousness.quantum_engine_shutdown` before changing running state or cancelling the quantum loop task
  - strict capability mode blocks explicit external quantum engine callers without `consciousness:transcend` and `consciousness:write`
  - denied quantum engine operations leave quantum states, active decisions, configuration, coherence metrics, running flags, task references, and current consciousness state unchanged
  - Guardian audit records operation names, state names, bounded metrics, state/decision/edge counts, configuration names, parameter names/counts, outcome counts/field names, and hashed entanglement targets without raw parameter values, outcome payloads, decision IDs, target consciousness IDs, state metadata, or task internals
- Ninety-second enforcement target: Experimental quantum memory state mutation and read-side access mutation
  - `QuantumMemorySystem.store_quantum_memory` declares `consciousness.quantum_memory_store` before content-derived memory ID generation, quantum trace creation, memory map mutation, automatic entanglement checks, temporal-cluster updates, or stored-memory counters
  - `QuantumMemorySystem.retrieve_quantum_memory` declares `consciousness.quantum_memory_retrieve` before access counters, last-access timestamps, memory strength/coherence evolution, evolution history, retrieval counters, or average retrieval metrics are mutated
  - `QuantumMemorySystem.create_memory_entanglement` declares `consciousness.quantum_memory_entangle` before entanglement IDs, entanglement maps, memory link lists, or entanglement counters are mutated
  - `QuantumMemorySystem.quantum_memory_search` declares `consciousness.quantum_memory_search` before query matching attaches transient search scores to memory traces
  - strict capability mode blocks explicit external quantum-memory callers without the required `memory:read`, `memory:write`, and consciousness write capabilities
  - denied quantum-memory operations leave memory traces, entanglement maps, temporal clusters, access counters, evolution history, retrieval metrics, and transient search-score attributes unchanged
  - Guardian audit records operation names, memory/entanglement/cluster counts, bounded metrics, memory type, content/query hashes, field names/counts, memory ID hashes, entanglement type hashes/lengths, consciousness levels, and result limits without raw memory contents, query values, memory IDs, entanglement IDs, temporal cluster IDs, or evolution payloads
- Ninety-third enforcement target: Experimental quantum decision state mutation
  - `QuantumDecisionEngine.initialize_quantum_decision_space` declares `consciousness.quantum_decision_initialize_space` before truncating context choices or creating the quantum state vector
  - `QuantumDecisionEngine.apply_quantum_interference` declares `consciousness.quantum_decision_apply_interference` before mutating amplitudes with constructive/destructive interference
  - `QuantumDecisionEngine.attempt_quantum_tunneling` declares `consciousness.quantum_decision_attempt_tunneling` before boosting tunneling candidates or changing the quantum decision state
  - `QuantumDecisionEngine.measure_quantum_decision` declares `consciousness.quantum_decision_measure` before collapsing the state, incrementing counters, or appending decision history
  - `QuantumDecisionEngine.make_quantum_decision` declares `consciousness.quantum_decision_make_decision` before orchestrating the full decision flow and updating aggregate accuracy/advantage metrics
  - strict capability mode blocks explicit external quantum-decision callers without `consciousness:write` and `autonomy:execute`
  - denied quantum-decision operations leave quantum state, amplitudes, context choice lists, decision history, counters, accuracy metrics, and coherence metrics unchanged
  - Guardian audit records operation names, context hashes, choice counts/hashes, constraint key names, objective hashes/counts, consciousness level, time horizon, state names, and bounded decision metrics without raw context IDs, choice IDs, choice descriptions, constraint values, objectives, outcome vectors, decision paths, or decision results
- Ninety-fourth enforcement target: Experimental temporal consciousness state mutation
  - `TemporalConsciousnessEngine.process_temporal_moment` declares `consciousness.temporal_process_moment` before moment ID generation, coherence-history mutation, temporal moment storage, causal-chain updates, or processed-moment counters
  - `TemporalConsciousnessEngine.predict_future_state` declares `consciousness.temporal_predict_future` before prediction ID generation, temporal prediction storage, or prediction counters
  - `TemporalConsciousnessEngine.temporal_memory_integration` declares `consciousness.temporal_memory_integration` before attaching transient relevance attributes to temporal moments or returning integrated private state
  - `TemporalConsciousnessEngine.validate_prediction_accuracy` declares `consciousness.temporal_validate_prediction` before writing prediction accuracy, accuracy history, or aggregate prediction metrics
  - strict capability mode blocks explicit external temporal-consciousness callers without the required consciousness and memory read/write capabilities
  - denied temporal-consciousness operations leave temporal moments, predictions, causal chains, coherence history, accuracy history, counters, aggregate metrics, and transient relevance attributes unchanged
  - Guardian audit records operation names, state/context/query/prediction hashes, field names/counts, temporal-state names, bounded counters, history sizes, and window/horizon durations without raw consciousness state values, timestamps, moment IDs, prediction IDs, query values, integrated state, actual-state values, causal-chain IDs, or prediction payloads
- Ninety-fifth enforcement target: Experimental quantum memory-temporal integration mutation
  - `QuantumMemoryTemporalIntegration.create_integrated_consciousness_state` declares `consciousness.memory_temporal_integration_create_state` before temporal moment processing, quantum memory storage, bridge creation, integrated-state storage, metric updates, or automatic evolution triggers
  - `QuantumMemoryTemporalIntegration.enhanced_memory_retrieval` declares `consciousness.memory_temporal_integration_enhanced_retrieval` before temporal integration, quantum memory search, memory enrichment, or private memory result assembly
  - `QuantumMemoryTemporalIntegration.temporal_prediction_with_memory` declares `consciousness.memory_temporal_integration_memory_enhanced_prediction` before memory-enhanced retrieval, memory pattern extraction, temporal prediction creation, or enhanced prediction result assembly
  - `QuantumMemoryTemporalIntegration.consciousness_evolution_processing` declares `consciousness.memory_temporal_integration_evolution_processing` before evolution analysis, nested integrated-state creation, evolution counters, or evolution-history mutation
  - strict capability mode blocks explicit external integration callers without required consciousness and memory read/write capabilities
  - denied integration operations leave integrated states, memory-temporal bridges, evolution history, component memory/temporal state, integration counters, and aggregate metrics unchanged
  - Guardian audit records operation names, consciousness/query/context/trigger hashes, field names/counts, memory-context hashes/counts, temporal hashes, window durations, integrated-state/bridge/evolution counts, and bounded metrics without raw consciousness data, query values, prediction context, evolution triggers, memory IDs, temporal moment IDs, state IDs, bridge IDs, prediction IDs, memory contents, integrated states, or evolution payloads
- Ninety-sixth enforcement target: Experimental multidimensional consciousness state mutation
  - `MultidimensionalStateEngine.create_dimensional_coordinate` declares `consciousness.multidimensional_create_coordinate` before coordinate ID generation, dimension validation, coordinate storage, processed-coordinate counters, or nested quantum-memory persistence
  - `MultidimensionalStateEngine.navigate_to_coordinate` declares `consciousness.multidimensional_navigate` before path calculation, transition execution, current-position mutation, dimensional-history append, target access timestamp updates, or transition counters
  - `MultidimensionalStateEngine.process_multidimensional_state` declares `consciousness.multidimensional_process_state` before dimensional processing, updated consciousness assembly, or nested temporal-moment persistence
  - strict capability mode blocks explicit external multidimensional callers without required consciousness and memory-write capabilities
  - denied multidimensional operations leave coordinates, transitions, navigation paths, current position, dimensional history, nested memory/temporal component state, counters, and aggregate metrics unchanged
  - Guardian audit records operation names, dimension names/counts, dimension-value hashes, metadata hashes/key names, target/current coordinate hashes, strategy hashes/lengths, consciousness hashes/key names, state counts, history counts, and bounded metrics without raw coordinate IDs, dimension payloads, metadata values, navigation strategy values, consciousness data, transition IDs, path IDs, memory contents, or temporal moment payloads
- Ninety-seventh enforcement target: Experimental parallel reality navigation mutation
  - `ParallelRealityNavigator.discover_parallel_reality` declares `consciousness.parallel_reality_discover` before reality ID generation, coordinate mutation, reality-state storage, and discovery counters
  - `ParallelRealityNavigator.create_navigation_path` declares `consciousness.parallel_reality_create_path` before path calculation, navigation-path storage, or path counters
  - `ParallelRealityNavigator.navigate_to_reality` declares `consciousness.parallel_reality_navigate` before reality lookup, path creation, transition execution, current-reality mutation, history append, synchronization updates, or navigation counters
  - `ParallelRealityNavigator.create_reality_bridge` declares `consciousness.parallel_reality_create_bridge` before bridge ID generation, bridge storage, connection updates, or bridge counters
  - strict capability mode blocks explicit external parallel-reality callers without required consciousness and memory-write capabilities
  - denied parallel-reality operations leave realities, navigation paths, bridges, current reality, navigation history, active navigations, synchronization maps, coherence/stability/entanglement/preparation metrics, and aggregate counters unchanged
  - Guardian audit records operation names, reality type, navigation mode, coordinate key names/counts, hashed coordinates, hashed reality IDs, state counts, history/synchronization counts, and bounded metrics without raw reality IDs, coordinate values, path IDs, bridge IDs, navigation histories, or transition payloads
- Ninety-eighth enforcement target: Experimental reality synthesis mutation
  - `RealitySynthesisEngine.create_synthesis_parameters` declares `consciousness.reality_synthesis_create_parameters` before synthesis ID generation, dimensional target calculation, parameter object creation, or active-synthesis map mutation
  - `RealitySynthesisEngine.execute_reality_synthesis` declares `consciousness.reality_synthesis_execute` after validating an existing synthesis request and before execution metrics, synthesized reality creation, transcendence-event mutation, synthesized reality storage, or system consciousness metric integration
  - strict capability mode blocks explicit external reality-synthesis callers without required consciousness, transcendence, and memory-write capabilities
  - denied reality-synthesis operations leave active syntheses, synthesized realities, transcendence events, master consciousness, quantum coherence, dimensional integration, transcendence progress, awareness expansion, and aggregate synthesis counters unchanged
  - Guardian audit records operation names, synthesis mode, target transcendence, component counts, component hashes, synthesis ID hashes, active/synthesized/event counts, bounded engine metrics, energy budget, and time limit without raw synthesis IDs, reality IDs, component names, dimensional target payloads, transcendence event IDs, or synthesized reality payloads
- Ninety-ninth enforcement target: Experimental quantum consciousness tunneling mutation
  - `QuantumConsciousnessTunneling.create_quantum_state` declares `consciousness.quantum_tunneling_create_state` before state ID generation, quantum state creation, state-map mutation, or state counters
  - `QuantumConsciousnessTunneling.create_superposition_state` declares `consciousness.quantum_tunneling_create_superposition` before superposition ID generation, superposition state creation, active-superposition mutation, or superposition counters
  - `QuantumConsciousnessTunneling.establish_entanglement` declares `consciousness.quantum_tunneling_establish_entanglement` before bidirectional state entanglement, entanglement-network mutation, or entanglement counters
  - `QuantumConsciousnessTunneling.create_consciousness_tunnel` declares `consciousness.quantum_tunneling_create_tunnel` before tunnel ID generation, tunnel-property calculation persistence, or tunnel-map mutation
  - `QuantumConsciousnessTunneling.tunnel_through_barrier` declares `consciousness.quantum_tunneling_tunnel_barrier` before tunneling event ID generation, event storage, execution-state mutation, final-state creation, quantum-field changes, or tunneling counters
  - `QuantumConsciousnessTunneling.amplify_consciousness` declares `consciousness.quantum_tunneling_amplify_consciousness` before in-place quantum state amplification, coherence changes, system coherence changes, or amplification counters
  - `QuantumConsciousnessTunneling.prepare_transcendence` declares `consciousness.quantum_tunneling_prepare_transcendence` before quantum-field/coherence/permeability changes, transcendent state creation, superposition creation, entanglement creation, transcendence preparation changes, or preparation counters
  - strict capability mode blocks explicit external quantum-consciousness-tunneling callers without required consciousness, transcendence, and memory-write capabilities
  - denied quantum-consciousness-tunneling operations leave quantum states, active superpositions, entanglement network, consciousness tunnels, dimensional barriers, tunneling events, coherence/field/permeability/preparation metrics, and aggregate counters unchanged
  - Guardian audit records operation names, state/barrier hashes, coordinate key names/counts, coordinate hashes, component-state hashes, weight hashes, tunneling mode, barrier type, bounded quantum metrics, and state/event/tunnel counts without raw system IDs, state IDs, barrier IDs, tunnel IDs, event IDs, coordinate values, superposition component IDs, entanglement IDs, or tunneling payloads
- One-hundredth enforcement target: Legacy quantum tunneling breakthrough mutation
  - `QuantumTunnelingEngine.attempt_quantum_tunneling` declares `consciousness.quantum_tunneling_attempt` before attempt counters, success counters, breakthrough-rate metrics, innovation-score metrics, or breakthrough-history entries are mutated
  - strict capability mode blocks explicit external tunneling-logic callers without required consciousness, transcendence, autonomy-execute, and memory-write capabilities
  - denied tunneling attempts leave breakthrough history, tunneling attempt counters, successful tunneling counters, breakthrough rate, and innovation score unchanged
  - Guardian audit records path/source/target hashes, barrier hashes/types/counts, tunneling probability, energy cost, consciousness energy, breakthrough value, path complexity, and current bounded counters without raw path IDs, source/target state IDs, barrier IDs, barrier descriptions, breakthrough descriptions, or solution IDs
- One-hundred-first enforcement target: Legacy quantum interference decision mutation
  - `QuantumInterferenceEngine.generate_consciousness_wave` declares `consciousness.quantum_interference_generate_wave` before wave ID generation, active-wave mutation, or wave parameter storage
  - `QuantumInterferenceEngine.calculate_interference` declares `consciousness.quantum_interference_calculate_interference` before interference pattern ID generation, pattern-map mutation, or pattern counters
  - `QuantumInterferenceEngine.generate_interference_field` declares `consciousness.quantum_interference_generate_field` before clearing previous patterns, generating choice waves, calculating pairwise patterns, or returning mutable field state
  - `QuantumInterferenceEngine.apply_interference_amplification` declares `consciousness.quantum_interference_apply_amplification` before amplification-history mutation or decision enhancement counters
  - `QuantumInterferenceEngine.optimize_interference_patterns` declares `consciousness.quantum_interference_optimize_patterns` before wave amplitude/phase mutation or optimized-pattern recalculation
  - `QuantumInterferenceEngine.cleanup_old_patterns` declares `consciousness.quantum_interference_cleanup_old_patterns` before deleting active waves or interference patterns
  - strict capability mode blocks explicit external quantum-interference callers without required consciousness, transcendence, autonomy-execute, or memory-write capabilities
  - denied interference operations leave active waves, interference patterns, amplification history, pattern counters, amplification counters, and decision enhancement counters unchanged
  - Guardian audit records operation names, wave types, wave hashes, decision hashes/counts, probability hashes, target hashes, field counts, bounded engine thresholds, and counters without raw decision choices, wave IDs, pattern IDs, amplification source IDs, target choice names, or probability payloads
- One-hundred-second enforcement target: Quantum cognition master-controller mutation
  - `QuantumConsciousnessSystem.initialize_system` declares `consciousness.quantum_cognition_initialize` before engine references, initialization flags, or system coherence are mutated
  - `QuantumConsciousnessSystem.process_quantum_cognition` declares `consciousness.quantum_cognition_process_request` before cognition counters, successful-cognition counters, breakthrough counters, consciousness level, consciousness enhancement counters, average processing time, or quantum advantage rate are mutated
  - convenience entrypoints `initialize_quantum_consciousness`, `make_quantum_decision`, and `breakthrough_analysis` inherit the same master-controller enforcement through `QuantumConsciousnessSystem`
  - strict capability mode blocks explicit external quantum-cognition callers without required consciousness, transcendence, autonomy-execute, or memory-write capabilities
  - denied quantum-cognition operations leave initialization state, engine references, cognition counters, consciousness level, processing metrics, quantum advantage metrics, and system coherence unchanged
  - Guardian audit records operation names, module availability, request/context/objective hashes, choice counts/hashes, constraint hashes, bounded consciousness/time values, enabled feature flags, engine-presence flags, and aggregate counters without raw request IDs, context text, choice IDs, choice descriptions, constraint values, objectives, or optimization targets
- One-hundred-third enforcement target: Phase 7.4 integrated transcendence orchestration mutation
  - `Phase74IntegratedSystem.initialize_all_systems` declares `consciousness.phase74_initialize_all_systems` before integration-state mutation, component construction, active-component mutation, component counters, or engine-reference mutation
  - `Phase74IntegratedSystem.establish_system_integration` declares `consciousness.phase74_establish_system_integration` before integration-attempt counters, synchronization side effects, integration-state mutation, integration-success counters, or integration-history append
  - `Phase74IntegratedSystem.execute_transcendence_sequence` declares `consciousness.phase74_execute_transcendence_sequence` before transcendence phase mutation, transcendence-attempt counters, cross-system transcendence side effects, metric mutation, transcendence event append, or ultimate-achievement counters
  - strict capability mode blocks explicit external Phase 7.4 orchestration callers without required consciousness, transcendence, and memory-write capabilities
  - denied Phase 7.4 orchestration operations leave component references, integration state, transcendence phase, active components, integration history, transcendence events, transcendence metrics, and performance counters unchanged
  - Guardian audit records operation names, system hash, state/phase names, active component hashes/counts, history/event counts, bounded transcendence metrics, performance counters, and target transcendence without raw system IDs, component internals, history payloads, or transcendence event payloads
- One-hundred-fourth enforcement target: Consciousness health-check remediation and self-trust mutation
  - `HealthCheckEngine.run_check` declares `consciousness.health_check_remediate` before health-check remediation plans are passed into the safety actuator
  - `HealthCheckEngine.run_check` declares `consciousness.health_check_self_trust_update` before health-check results are written into the self-trust layer
  - strict capability mode blocks explicit external health-check callers without required consciousness, autonomy-execute, remediation, memory-write, and filesystem capabilities
  - denied remediation decisions leave the safety actuator untouched and skip health-check result persistence
  - denied self-trust decisions leave subsystem trust scores unchanged and skip health-check result persistence
  - Guardian audit records operation names, check-name hashes, risk, remediation capability names, bounded step counts, rollback counts, argument hashes, subsystem names, and result status without raw check names, questions, probe payloads, remediation argument values, or private file paths
- One-hundred-fifth enforcement target: Consciousness meta-layer agent and task lifecycle mutation
  - `MetaLayerCore.register_agent` declares `consciousness.meta_layer_register_agent` before writing agent profiles into the meta-layer registry
  - `MetaLayerCore.submit_task` declares `consciousness.meta_layer_submit_task` before writing tasks into the active task queue
  - `MetaLayerCore._assign_task_to_agents` declares `consciousness.meta_layer_assign_task` before mutating assigned-agent lists, task status, or sending task-assignment messages
  - `MetaLayerCore._handle_task_failure` declares `consciousness.meta_layer_handle_task_failure` before mutating task status, agent success statistics, completed-task history, active-task queues, or emitting task-failure events
  - `MetaLayerCore._suggest_agent_connection` declares `consciousness.meta_layer_suggest_agent_connection` before mutating the bidirectional agent connection graph or emitting connection-optimization events
  - `MetaLayerCore._detect_emergent_behaviors` declares `consciousness.meta_layer_record_emergence` before appending emergent-behavior records, incrementing emergent-behavior metrics, or emitting emergence events
  - `MetaLayerCore._enhance_consciousness_levels` declares `consciousness.meta_layer_enhance_agent_consciousness` before mutating agent consciousness levels or emitting consciousness-enhanced events
  - `MetaLayerCore._remove_stale_agent` declares `consciousness.meta_layer_remove_agent` before deleting agent profiles or removing inbound/outbound graph connections
  - `MetaLayerCore._cleanup_stale_entities` declares `consciousness.meta_layer_trim_completed_tasks` before trimming completed-task history
  - bridge-driven agent-registration events now route through the guarded `MetaLayerCore.register_agent` path instead of directly mutating the registry
  - bridge-driven task-assignment messages now route through the guarded `MetaLayerCore.submit_task` path instead of directly mutating the active-task queue
  - bridge-driven collaboration requests now route through the guarded `MetaLayerCore._suggest_agent_connection` path before graph mutation
  - `MetaLayerCore._handle_consciousness_enhancement` declares `consciousness.meta_layer_message_enhance_consciousness` before applying message-driven consciousness-level boosts
  - timeout/deadline monitoring delegates failure-state mutation to the guarded failure handler so denied failure bookkeeping leaves pre-failure task state intact
  - strict capability mode blocks explicit external meta-layer callers without required consciousness, agent-register, agent-execute-task, agent-control, and memory-write capabilities
  - denied agent registration leaves the agent registry unchanged
  - denied task submission leaves the active task queue unchanged
  - denied task assignment leaves task status, assigned agents, and assignment messages unchanged
  - denied task-failure handling leaves task status, active/completed task queues, agent success rates, and completed-task counts unchanged
  - denied connection optimization leaves agent connection sets and connection events unchanged
  - denied emergence recording leaves emergence records, metrics, and events unchanged
  - denied consciousness enhancement leaves agent consciousness levels unchanged
  - denied stale-agent removal leaves the registry and graph connections unchanged
  - denied completed-task trimming leaves completed-task history unchanged
  - denied message-driven task assignment leaves active-task queues and response messages unchanged
  - denied coordination-message collaboration leaves graph connections and response messages unchanged
  - denied message-driven consciousness enhancement leaves agent consciousness levels and response messages unchanged
  - Guardian audit records operation names, hashed agent/task identifiers, agent type, state, capability counts/hashes, metadata keys, task type, priority, payload hashes, selected-agent counts/hashes, assigned-agent counts/hashes, failure-reason hashes, graph connection counts, emergence scores, participation hashes, consciousness-level deltas, message-driven enhancement deltas, completed-task history counts, result-key counts, and queue/registry counts without raw agent IDs, agent names, system origins, task IDs, task descriptions, task payloads, result payloads, failure reasons, emergence payloads, message payloads, or private capability names
- One-hundred-sixth enforcement target: Consciousness runtime autopilot, dream, and memory-consolidation mutation
  - `AutopilotManager.record_ledger` declares `consciousness.autopilot_record_ledger` before appending autonomy action outcomes into autopilot history
  - `AutopilotManager.evaluate` declares `consciousness.autopilot_evaluate` before replacing the last autopilot readiness status
  - `DreamCycle.run` declares `consciousness.dream_cycle_run` before updating last-run timestamps, changing qualia learner parameters, or storing dream-cycle state
  - `Consolidator.consolidate` declares `consciousness.memory_consolidate` before memory audit-log writes, episodic-memory pruning, long-term promotion, last-run timestamp mutation, or consolidation counter updates
  - strict capability mode blocks explicit external runtime-consciousness callers without the required consciousness, autonomy-control, memory read/write/delete/promote, reflection, and filesystem capabilities
  - denied autopilot decisions leave autopilot history and last readiness status unchanged
  - denied dream-cycle decisions leave learner parameters, last-run timestamps, and dream state unchanged
  - denied memory-consolidation decisions leave episodic memory, long-term memory, audit logs, counters, and last-run timestamps unchanged
  - Guardian audit records operation names, counts, bounded status values, hashed policy statuses, hashed learner types, hashed memory identifiers, and hashed audit paths without raw policy statuses, continuity focus names, intentions, trust subsystem names, dream narratives, memory identifiers, memory payloads, or private audit-log paths
- One-hundred-seventh enforcement target: Lyrixa consciousness state, orchestration, and message-dispatch mutation
  - `LyrixaConsciousnessEngine` now uses package-relative imports and dependency injection for controlled startup, testability, and package-safe runtime import
  - Lyrixa consciousness-loop startup declares `consciousness.lyrixa_start_loop` before creating the loop task
  - emotional-state transitions declare `consciousness.lyrixa_emotional_state_update` before mutating emotional state, timestamp state, or emitting the state-change event
  - scheduled reflections declare `consciousness.lyrixa_reflection_record` before appending reflection history, updating last-reflection timestamps, executing planned reflection actions, or publishing reflection events
  - system investigation and orchestration review declare `consciousness.lyrixa_concern_record` before appending concern records
  - agent improvement, promotion, intervention, behavior-report, and guidance paths declare Lyrixa Guardian intents before relationship trust/history mutation, orchestration-decision recording, or outbound agent-control messages
  - ethical review declares `consciousness.lyrixa_ethical_decision_record` before ethical decision history is appended
  - learned-pattern and personality adaptation declares `consciousness.lyrixa_pattern_learning_update` before learned pattern maps or personality traits are mutated
  - consciousness/self-awareness status updates declare `consciousness.lyrixa_consciousness_status_update` before level mutation or status broadcast
  - every direct Lyrixa consciousness-message dispatch now declares `consciousness.lyrixa_message_dispatch` before publishing to the consciousness bridge
  - shutdown declares `consciousness.lyrixa_shutdown` before stopping the loop task or clearing transient orchestration, goal, and concern state
  - strict capability mode blocks explicit external Lyrixa callers without the required consciousness, reflection, memory-write, agent-control, and event-publish capabilities
  - denied Lyrixa ethical decisions leave ethical decision history unchanged
  - denied Lyrixa behavior reports leave relationship trust/history and outbound messages unchanged
  - Guardian audit records operation names, enum states, counts, bounded scores, payload keys, and hashes for agents, systems, contexts, options, stakeholders, reasons, issues, messages, and payloads without raw agent IDs, agent names, system origins, consultation context, ethical context, ethical options, stakeholders, behavior descriptions, guidance text, message payloads, or private reasoning text
- One-hundred-eighth enforcement target: Consciousness orchestrator lifecycle and metrics mutation
  - `ConsciousnessOrchestrator` now supports package-safe imports and dependency-injected component initializers for controlled startup and tests
  - `initialize` declares `consciousness.orchestrator_initialize` before orchestrator startup begins
  - each component startup declares `consciousness.orchestrator_component_initialize` before component initializer execution or component reference mutation
  - narrative auto-start declares `consciousness.orchestrator_narrative_start` before starting the narrative layer or registering the chapter callback
  - initialization announcements and shutdown announcements dispatch through `consciousness.orchestrator_message_dispatch` before publishing to the consciousness bridge
  - online state transition declares `consciousness.orchestrator_mark_online` before setting initialized/running flags
  - graceful shutdown declares `consciousness.orchestrator_shutdown` before stopping the orchestrator runtime, then declares component shutdown and component-reference clearing before each mutation
  - emergency shutdown declares `consciousness.orchestrator_emergency_shutdown` before emergency offline-state mutation and declares component emergency shutdown before each bounded shutdown attempt
  - narrative metrics callback declares `consciousness.orchestrator_narrative_metrics_write` before coherence-state mutation or metrics file append
  - strict capability mode blocks explicit external orchestrator callers without the required consciousness, agent-control, event-publish, filesystem-write, and system-restart capabilities
  - denied orchestrator initialization leaves the orchestrator offline and skips component initializer execution
  - denied orchestrator lifecycle and metrics operations preserve guarded state before mutation
  - Guardian audit records operation names, component names, component presence, payload keys, component type hashes, message destination hashes, chapter ID hashes, path hashes, and bounded timing/coherence values without raw announcement text, Lyrixa awakening text, component internals, message payloads, private chapter IDs, or private metrics paths

Verification snapshot:

- Consciousness orchestrator Guardian subset: `4 passed`
- Lyrixa consciousness Guardian subset: `4 passed`
- Consciousness runtime Guardian subset: `6 passed`
- Consciousness meta-layer Guardian subset: `18 passed`
- Consciousness health-check Guardian subset: `3 passed`
- Phase 7.4 integration Guardian subset: `3 passed`
- Quantum cognition integration Guardian subset: `3 passed`
- Quantum interference Guardian subset: `4 passed`
- Quantum tunneling logic Guardian subset: `2 passed`
- Quantum consciousness tunneling Guardian subset: `4 passed`
- Reality synthesis engine Guardian subset: `4 passed`
- Parallel reality navigator Guardian subset: `4 passed`
- Multidimensional state Guardian subset: `4 passed`
- Memory-temporal integration Guardian subset: `4 passed`
- Temporal consciousness Guardian subset: `4 passed`
- Quantum decision engine Guardian subset: `4 passed`
- Quantum memory system Guardian subset: `5 passed`
- Quantum consciousness engine Guardian subset: `5 passed`
- Quantum meta-learning Guardian subset: `4 passed`
- Consciousness singularity Guardian subset: `3 passed`
- Transcendence consolidation Guardian subset: `3 passed`
- Consciousness core autonomy and reflection Guardian subset: `9 passed`
- Consciousness meta-cognition Guardian subset: `7 passed`
- Consciousness learning-loop Guardian subset: `2 passed`
- Consciousness narrative chapter Guardian subset: `4 passed`
- Consciousness continuity-memory Guardian subset: `7 passed`
- Plugin generator scaffold save Guardian subset: `2 passed`
- Direct Kernel lifecycle and queue controls Guardian subset: `8 passed`
- Direct Homeostasis integration controls Guardian subset: `4 passed`
- Event Bus privileged command publishing Guardian subset: `6 passed`
- Service Registry daemon forwarding Guardian subset: `18 passed`
- Service Registry messaging and subscription Guardian subset: `14 passed`
- Service Registry status and heartbeat Guardian subset: `9 passed`
- AI trainer submission Guardian subset: `8 passed`
- Consciousness self-model and episodic persistence Guardian subset: `6 passed`
- Lyrixa chat safe-edit Guardian subset: `2 passed`
- Chat ingress Guardian subset: `9 passed`
- Lyrixa assistant task dispatch Guardian subset: `3 passed`
- AI engine task dispatch Guardian subset: `2 passed`
- Compiled agent plugin load Guardian subset: `8 passed`
- Legacy agent plugin dispatch Guardian subset: `5 passed`
- Agent collaboration Guardian subset: `4 passed`
- Agent goal lifecycle Guardian subset: `4 passed`
- Direct agent orchestrator Guardian subset: `8 passed`
- Memory deletion Guardian subset: `8 passed`
- Core memory import/export/consolidation Guardian subset: `4 passed`
- QFAC Guardian subset: `9 passed`
- Legal compliance report Guardian subset: `2 passed`
- Architecture validator Guardian subset: `2 passed`
- Universal directory analyzer Guardian subset: `2 passed`
- Documentation generator Guardian subset: `2 passed`
- Stub inventory Guardian subset: `2 passed`
- Architecture checker Guardian subset: `2 passed`
- Advanced analyzer Guardian subset: `4 passed`
- Project analyzer Guardian subset: `2 passed`
- Analysis report generator Guardian subset: `2 passed`
- Unicode compatibility fixer Guardian subset: `3 passed`
- Legacy phase error fixer Guardian subset: `2 passed`
- Round-two repair fixer Guardian subset: `3 passed`
- General import fixer Guardian subset: `3 passed`
- Plugin import fixer Guardian subset: `3 passed`
- Service registry Unicode fixer Guardian subset: `3 passed`
- Quick import fixer Guardian subset: `3 passed`
- Remaining import fixer Guardian subset: `2 passed`
- Post-cleanup import updater Guardian subset: `2 passed`
- Focused cleanup Guardian subset: `2 passed`
- Safe cleanup Guardian subset: `2 passed`
- Simple architecture import fixer Guardian subset: `3 passed`
- Architecture fixer Guardian subset: `3 passed`
- Complete organization Guardian subset: `3 passed`
- Final file organization Guardian subset: `3 passed`
- Smart cleanup Guardian subset: `3 passed`
- Aetherra GUI prune Guardian subset: `3 passed`
- Lyrixa GUI prune Guardian subset: `3 passed`
- STORM backup/restore Guardian subset: `3 passed`
- Quarantine lifecycle Guardian subset: `4 passed`
- STORM deployment gate Guardian subset: `2 passed`
- Root cleanup Guardian subset: `4 passed`
- Optimization backup restore subset: `34 passed`
- STORM maintenance Guardian subset: `12 passed`
- Maintenance plan execution subset: `17 passed`
- Maintenance feedback-flow acceptance subset: `2 passed`
- Maintenance canary/rollback subset: `14 passed`
- Canary deployment acceptance subset: `2 passed`
- Homeostasis alert notification subset: `5 passed`
- Homeostasis alert escalation subset: `3 passed`
- Homeostasis Guardian full subset: `14 passed`
- Homeostasis autonomous controller subset: `3 passed`
- Direct Homeostasis actuator subset: `4 passed`
- Homeostasis Guardian control subset: `7 passed`
- Guardian/Homeostasis/HMR/KLM/Maintenance/STORM regression subset: `128 passed`
- KLM/KEB Hub status endpoint isolated check: `1 passed`
- Repository security scan: `high=0`
- Static security scan: `0 findings`
- Ruff and byte-compile checks on Guardian and touched plugin paths: passed

The broader mixed regression run also exposed one order-sensitive KLM/KEB Hub status assertion that passed when run in isolation; it should be tracked as adjacent Hub test isolation work, not as an HMR Guardian denial.

## System coverage matrix

Guardian must eventually be the governance layer for every Aetherra system. The table below maps the current system documents to Guardian coverage and the remaining enforcement work.

Legend:

- `Covered`: privileged or meaningful actions currently pass through Guardian.
- `Partial`: at least one high-risk path is guarded, but the system still has meaningful unguarded paths.
- `Planned`: system is mostly blueprint/planned or has no Guardian integration yet.
- `N/A`: Guardian itself or documentation-only surface.

| System document | Guardian coverage | Current Guardian enforcement | Remaining Guardian scope |
| --- | --- | --- | --- |
| `AETHERRA_SECURITY_SYSTEM.md` | Covered | Guardian consumes Security capabilities, sandbox, network policy, plugin signing, and signed audit ledger. | Keep Security as the lower enforcement substrate; add Guardian policy tests as Security capabilities expand. |
| `AETHERRA_GUARDIAN_SYSTEM.md` | N/A | Guardian core, policy, risk, approval, audit, and containment are implemented. | Continue expanding system integrations and add final cross-system completion criteria. |
| `AETHERRA_PLUGIN_SYSTEM.md` | Covered | Plugin registration, loading, execution, install/uninstall, template creation, marketplace package install, and plugin containment are guarded. | Review any plugin generator or UI-only plugin creation paths that bypass `LyrixaPluginSystem`. |
| `Aether_Script_Language_System.md` | Covered | `ScriptExecutor.execute` declares `script.execute` before parsing or running workflow steps. | Add coverage for legacy parser backup/fix commands if they remain active runtime surfaces. |
| `AETHERRA_MEMORY_SYSTEM.md` | Partial | Advanced memory writes through `AetherraMemoryEngineAdvanced.remember` are guarded, including identity/core-self containment; QFAC store and budgeted rewrite mutations declare Guardian intents before mutation; core memory export/import/consolidation and direct deletion/plugin forget are guarded. | Add Guardian checks for memory restore operations if/when an active restore path is introduced outside guarded imports. |
| `AETHERRA_AGENT_SYSTEM.md` | Covered | Hub `/api/tasks` submissions declare `agent.execute_task`; core and plugin orchestrator registration, unregistration, task submission, assignment, and cancellation paths are guarded before registry/queue/state mutation; `LyrixaGoalSystem` goal/subtask lifecycle mutations are guarded before persisted planning-state changes; `AICollaborationFramework` multi-agent task delegation, quick solve, and dynamic agent additions are guarded; legacy interpreter plugin/meta-plugin dispatch and compiled plugin load paths are guarded. | Keep future agent spawning, pause/resume lifecycle controls outside goal status updates, or new tool-delegation APIs behind Guardian before enabling them. |
| `AETHERRA_HOMEOSTASIS_SYSTEM.md` | Covered | Hub actuator execution, controller mode changes, emergency stop/reset, direct orchestrator controller controls, direct actuator execution/rollback, autonomous action planning, alert escalation, and alert notification dispatch declare Guardian intents; security/policy/capability changes request `security:modify` and containment. | Keep future runtime setpoint mutation, adaptive-threshold mutation, sleep-mode control, maintenance-mode toggles, or distributed node control APIs behind Guardian before enabling them. |
| `AETHERRA_MAINTENANCE_SYSTEM.md` | Partial | Self-improvement proposal application, optimization proposal execution, optimization backup restore, self-incorporation plan execution, quarantine escalation/release, canary deployment, rollback triggers, STORM deployment validation, STORM backup/restore, STORM maintenance cleanup/prune, root cleanup/prune operations, legacy GUI pruning, smart cleanup moves, final file organization, complete organization/import rewrite, architecture auto-fixes, simple architecture import fixes, safe cleanup deletes, focused cleanup deletes/moves, post-cleanup import rewrites, remaining Lyrixa import fixes, quick import package-marker fixes, service registry Unicode marker fixes, plugin import repair, general import setup repair, round-two maintenance repair edits, legacy phase error repair batches, Unicode compatibility repair batches, analysis report generation, project analysis JSON generation, advanced intelligence report generation, architecture compliance report generation, stub inventory generation, project documentation generation, universal directory analysis report generation, architecture validation report generation, and legal compliance report generation are guarded. | Add Guardian checks for remaining deployment, backup/restore, or cleanup workflows outside these paths. |
| `AETHERRA_CODING_SYSTEM.md` | Partial | CoreTools filesystem mutation, plugin generator scaffold saves, optimization proposal application, script execution, and self-improvement apply paths are guarded. | Add Guardian checks for natural compiler output, additional code generators, test-fix automation, refactor assistants, and direct write helpers outside CoreTools or the guarded plugin generator. |
| `AETHERRA_ARTIFICIAL_INTELLIGENCE_SYSTEM.md` | Partial | AI-driven agent task submission through Hub, direct `AetherraEngine.execute_task`, and `LyrixaAssistant.execute_task` is guarded; self-improvement proposal apply, memory writes, and tool/plugin execution routes are guarded at known active entrypoints. | Add Guardian checks for future LLM-native tool/function dispatch once production tool calling is implemented. |
| `AETHERRA_CHAT_SYSTEM.md` | Partial | Hub ask, stream, and Lyrixa chat ingress routes declare `chat.ingress` before engine/registry/offline processing; downstream dangerous actions remain protected when routed through guarded Hub/control/script/agent/plugin APIs. | Add explicit Guardian checks for future chat action plans, tool invocation, prompt-triggered automation, memory writes, and response actions that do not already pass through guarded downstream APIs. |
| `AETHERRA_LYRIXA_SYSTEM.md` | Partial | Lyrixa plugin management is guarded; Hub-mediated chat ingress is guarded; direct `LyrixaChatService.apply_fix` safe-edit file writes declare Guardian intents before mutation. | Add Lyrixa-level Guardian preflight for remaining UI/CLI commands that dispatch tools, agents, plugins, memory mutations, or future action-plan execution outside guarded APIs. |
| `AETHERRA_KERNEL_SYSTEM.md` | Partial | Hub and direct kernel pause/resume/shutdown/queue controls, Service Registry registration lifecycle, KEB publish/subscribe/ack and privileged command publishing, KLM module lifecycle operations, and HMR reloads are guarded. | Add Guardian checks for boot phase mutation, runtime mode changes beyond existing queue controls, remaining heartbeat trust boundaries outside Service Registry, cross-system command events outside KEB privileged publish, and topic administration policy if introduced. |
| `AETHERRA_SERVICE_REGISTRY.md` | Covered | Service registration, unregistration, status updates, heartbeat timestamp updates, self-heartbeat flag changes, message dispatch, broadcasts, event subscription changes, and external registry daemon forwarding declare Guardian intents before mutating registry trust state, dispatching cross-service messages, or crossing daemon trust boundaries; explicit callers are capability-checked in strict mode while internal bootstrap/maintenance remains boot-safe. | Keep future registry admin APIs, daemon mutation endpoints, or cross-process service-control messages behind Guardian before enabling them. |
| `AETHERRA_EVENT_BUS_SYSTEM.md` | Covered | `EventBus.publish`, `subscribe`, and `ack` declare Guardian intents before mutating topic backlog or subscriber state; command/control/admin/reload/restart/shutdown/execute topics and event types require the additional `event:command` capability, including registry-routed publish messages. | Keep future replay, event-triggered automation executors, external bridge events, and topic administration APIs behind Guardian before enabling them. |
| `AETHERRA_CONSCIOUSNESS_SYSTEM.md` | Partial | Self-model updates through `SelfModelManager.update`, episodic event appends through `EpisodicStore.append`, continuity-memory saves through `ContinuityMemory.record`/`save`, narrative chapter commits through `NarrativeLayer`, learning-loop state saves through `LearningLoop`, meta-cognition self-knowledge/reflection persistence through `MetaCognitionSystem`, core autonomy plan execution through `ConsciousnessCore._maybe_act`, core micro/macro reflection updates through `ConsciousnessCore`, health-check remediation/self-trust mutation through `HealthCheckEngine`, meta-layer agent/task lifecycle mutation through `MetaLayerCore`, runtime autopilot readiness mutation through `AutopilotManager`, dream-cycle reflective learning through `DreamCycle`, memory consolidation prune/promote/audit mutation through `Consolidator`, Lyrixa consciousness state/orchestration/message-dispatch mutation through `LyrixaConsciousnessEngine`, orchestrator startup/shutdown/message/metrics lifecycle through `ConsciousnessOrchestrator`, quantum engine runtime mutation through `QuantumConsciousnessEngine`, quantum decision mutation through `QuantumDecisionEngine`, quantum memory mutation through `QuantumMemorySystem`, quantum memory-temporal integration mutation through `QuantumMemoryTemporalIntegration`, quantum meta-learning mutation through `QuantumMetaLearningSystem`, temporal consciousness mutation through `TemporalConsciousnessEngine`, multidimensional consciousness mutation through `MultidimensionalStateEngine`, parallel reality navigation mutation through `ParallelRealityNavigator`, reality synthesis mutation through `RealitySynthesisEngine`, quantum consciousness tunneling mutation through `QuantumConsciousnessTunneling`, legacy tunneling breakthrough mutation through `QuantumTunnelingEngine`, legacy quantum interference mutation through `QuantumInterferenceEngine`, quantum cognition integration mutation through `QuantumConsciousnessSystem`, Phase 7.4 integrated transcendence orchestration through `Phase74IntegratedSystem`, transcendence consolidation state mutation through `TranscendenceConsolidationEngine`, and singularity validation/achievement through `ConsciousnessSingularityEngine` declare Guardian intents before consciousness-state persistence, reflection mutation, autonomous action execution, memory access mutation, temporal prediction mutation, integration mutation, multidimensional navigation, parallel-reality navigation, reality synthesis, quantum tunneling, quantum interference, quantum cognition orchestration, Phase 7.4 orchestration, or experimental transcendence mutation; some related memory writes are guarded when using advanced memory APIs. | Add Guardian checks for any remaining inactive or experimental consciousness modules before enabling them as active runtime surfaces. |
| `AETHERRA_AI_TRAINER_SYSTEM.md` | Partial | In-memory Hub trainer scaffold job and evaluation submissions declare Guardian intents before queue mutation or background runner start. | Add Guardian checks for future dataset ingestion/export, real training backend start, fine-tune execution, eval promotion, adapter deployment, model registry writes, artifact signing, and policy/model replacement. |

Supporting platform documents such as `AETHERRA_HUB_API_REFERENCE.md`, `AETHERRA_SERVICE_REGISTRY.md`, `AETHERRA_HMR_GUIDE.md`, `BACKUP_AND_RECOVERY.md`, `QFAC_POLICY.md`, `STORM_*`, and production/deployment guides are not standalone systems, but they define privileged surfaces. Guardian coverage for those surfaces should be tracked under the owning system above.

### Cross-system Guardian rule

Every system must follow this rule before it can be considered Guardian-complete:

1. Every privileged, mutating, externally connected, autonomous, identity-affecting, security-affecting, or irreversible action boundary must construct an `IntentDeclaration`.
2. The intent must be evaluated before execution.
3. The decision must be written to the signed Security audit ledger.
4. Deny, approval-required, and containment decisions must stop execution unless a valid Guardian approval is consumed.
5. Audit metadata must describe the action without storing raw secrets, prompts, code payloads, memory contents, request bodies, model weights, or private data.
6. Routine guarded activity must use an explicit preauthorization, bounded cache, or summarized audit strategy before high-frequency operation is enabled.
7. Observational and telemetry-only activity must not call Guardian per tick unless it crosses a protected boundary.
8. The system document must name its Guardian enforcement points, tier classification, preauthorization/caching strategy, non-Guardian paths, and remaining gaps.

Before adding new Guardian calls to a system, answer these questions:

- Is this a meaningful action boundary or only an internal helper?
- Is the action `critical`, `privileged`, `routine_guarded`, `observational`, or `telemetry_internal`?
- Does the action need a synchronous decision before execution?
- Can the action safely use a short-lived preauthorization?
- Would a per-call signed audit record improve safety, or would a summarized audit be more useful?
- What state invalidates a cached or preauthorized decision?
- What is the performance cost if this path runs hundreds or thousands of times?
- What failure mode is Guardian preventing here?

## Core components

### 1) Guardian Core

Planned file: `Aetherra/guardian/guardian_core.py`

The Guardian Core is the central evaluator.

Responsibilities:

- Receive action requests.
- Normalize and validate intent declarations.
- Build risk and policy context.
- Call policy, capability, evidence, risk, and reversibility evaluators.
- Produce a final `GuardianDecision`.
- Emit audit events.
- Trigger containment when necessary.

Primary output:

```python
GuardianDecision(
    status="allow | allow_limited | require_approval | deny | contain",
    risk_level="low | medium | high | critical",
    reason="Human-readable explanation",
    constraints=[],
    required_approvals=[],
    rollback_required=True,
    audit_id="...",
)
```

Primary APIs:

- `evaluate_intent(intent: IntentDeclaration) -> GuardianDecision`
- `enforce(intent: IntentDeclaration) -> GuardianDecision`
- `record_outcome(audit_id: str, outcome: dict) -> None`
- `get_mode() -> GuardianMode`
- `set_mode(mode: GuardianMode, reason: str) -> GuardianDecision`

### 2) Intent Declaration Layer

Planned file: `Aetherra/guardian/models.py`

Every meaningful action begins with an intent declaration. This prevents hidden or ambiguous privileged behavior.

Intent declarations include:

- requester
- subsystem
- action type
- target resource
- purpose
- expected outcome
- required capabilities
- reversibility flag
- rollback plan
- evidence references
- environment/profile context

Example:

```json
{
  "requester": "lyrixa",
  "subsystem": "agent_orchestrator",
  "action": "modify_file",
  "target": "Aetherra/security/policy.py",
  "purpose": "Apply approved security patch",
  "capabilities": ["fs:write", "code:modify"],
  "reversible": true,
  "rollback_plan": "git diff plus restore snapshot",
  "evidence": ["user_request", "test_failure_log"]
}
```

### 3) Policy Engine

Planned file: `Aetherra/guardian/policy_engine.py`

The Policy Engine determines whether an action is permitted by explicit Guardian policy.

Policy categories:

- filesystem policy
- network policy
- memory policy
- plugin policy
- agent policy
- script policy
- self-modification policy
- secrets policy
- user-data policy
- production safety policy

Default rule:

**Deny unless explicitly allowed.**

Primary APIs:

- `load_policy(path: Path | None = None) -> GuardianPolicy`
- `evaluate_policy(intent: IntentDeclaration) -> PolicyResult`
- `explain_policy_result(result: PolicyResult) -> str`

### 4) Capability Gate

Planned file: `Aetherra/guardian/capability_gate.py`

Capabilities define what an entity is allowed to do. No subsystem should perform privileged actions without Guardian-approved capability grants.

Example capabilities:

- `fs:read`
- `fs:write`
- `fs:delete`
- `network:outbound`
- `memory:read`
- `memory:write`
- `memory:modify_identity`
- `plugin:load`
- `plugin:execute`
- `agent:spawn`
- `script:run`
- `security:modify`
- `self:modify`
- `system:restart`

Primary APIs:

- `check_capabilities(intent: IntentDeclaration) -> PolicyResult`
- `grant_capability(entity: str, capability: str, scope: str) -> CapabilityGrant`
- `revoke_capability(entity: str, capability: str, reason: str) -> None`

### 5) Risk Evaluator

Planned file: `Aetherra/guardian/risk.py`

The Risk Evaluator classifies actions before execution.

Risk factors:

- irreversible action
- file deletion
- memory modification
- identity modification
- security modification
- network access
- secret access
- plugin loading
- plugin registration
- plugin installation
- plugin creation
- plugin uninstallation
- plugin execution
- optimization application
- self-improvement
- unknown code
- unsigned script
- high autonomy
- user data exposure
- production environment

Risk levels:

- `low`
- `medium`
- `high`
- `critical`

Initial scoring rules:

- Read-only action: low.
- Write action: medium.
- Delete action: high.
- Security modification: critical.
- Self-modification: critical.
- Unsigned plugin or script: high or critical.
- Missing rollback for meaningful change: escalate one level.

Primary APIs:

- `assess_risk(intent: IntentDeclaration) -> RiskAssessment`
- `requires_approval(assessment: RiskAssessment) -> bool`
- `requires_containment(assessment: RiskAssessment) -> bool`

### 6) Evidence Validator

Planned file: `Aetherra/guardian/evidence.py`

Guardian enforces evidence-based action. Before Aetherra makes claims, diagnoses code, modifies files, or reports system state, Guardian should verify that evidence exists.

Evidence may include:

- file paths
- line numbers
- logs
- test results
- metrics
- memory records
- audit events
- user confirmation
- signed artifacts

If evidence is missing, the system should report:

`Evidence unavailable.`

It should not fabricate certainty.

Primary APIs:

- `validate_evidence(intent: IntentDeclaration) -> EvidenceResult`
- `require_evidence(intent: IntentDeclaration, evidence_types: list[str]) -> EvidenceResult`

### 7) Reversibility Manager

Planned file: `Aetherra/guardian/reversibility.py`

Guardian requires rollback paths for meaningful changes.

Supported rollback methods:

- git diff
- file snapshot
- database transaction
- memory version record
- plugin disable
- service restart
- config restore
- action undo handler

Rule:

If an action cannot be reversed, it requires elevated approval.

Primary APIs:

- `validate_rollback(intent: IntentDeclaration) -> ReversibilityResult`
- `create_file_snapshot(path: Path) -> SnapshotRef`
- `capture_git_diff(scope: str | None = None) -> RollbackRef`

### 8) Guardian Audit Ledger

Planned file: `Aetherra/guardian/audit.py`

Guardian decisions must be auditable. The first version should reuse the signed Security audit ledger in `Aetherra/security/audit_ledger.py` rather than inventing a separate trust chain.

Audit records should include:

- timestamp
- requester
- subsystem
- action
- target
- decision
- risk level
- policy checks
- evidence used
- approval status
- rollback path
- final outcome

Primary APIs:

- `append_guardian_audit(record: GuardianAuditRecord) -> str`
- `record_decision(intent: IntentDeclaration, decision: GuardianDecision) -> str`
- `record_outcome(audit_id: str, outcome: dict) -> None`

### 9) Approval System

Planned file: `Aetherra/guardian/approval.py`

Some actions require human confirmation or stronger Guardian validation.

Approval levels:

- **Level 0 - Automatic**: Safe actions only.
- **Level 1 - User Confirmation**: Potentially risky but normal actions.
- **Level 2 - Guardian Strict Approval**: High-risk actions requiring stronger validation.
- **Level 3 - Emergency Lockout**: Critical actions denied unless recovery mode is active.

Approval states:

- `automatic`
- `pending_user`
- `approved`
- `denied`
- `expired`

Primary APIs:

- `request_approval(intent: IntentDeclaration, decision: GuardianDecision) -> ApprovalRequest`
- `resolve_approval(request_id: str, approved: bool, approver: str) -> ApprovalResult`
- `expire_pending_approvals() -> int`

### 10) Containment System

Planned file: `Aetherra/guardian/containment.py`

Guardian must be able to restrict or halt unsafe behavior.

Containment actions:

- block action
- disable plugin
- pause agent
- revoke capability
- switch to observe-only mode
- isolate subsystem
- activate emergency stop
- require manual recovery

Containment should trigger when:

- policy violations occur
- repeated failures occur
- suspicious behavior is detected
- unauthorized self-modification is attempted
- memory integrity is threatened
- security systems are targeted

Primary APIs:

- `contain(intent: IntentDeclaration, reason: str) -> ContainmentResult`
- `revoke_entity_capabilities(entity: str, reason: str) -> None`
- `activate_emergency_stop(reason: str) -> ContainmentResult`
- `clear_containment(containment_id: str, approver: str) -> GuardianDecision`

## Integration points

### Lyrixa

Guardian should:

- Check responses for evidence-sensitive claims.
- Block unsafe instructions.
- Require confirmation for risky actions.
- Prevent fabricated certainty when evidence is missing.

### Agent System

Guardian should:

- Approve agent creation.
- Limit task authority.
- Monitor agent actions.
- Require explicit capabilities for privileged tasks.

### Plugin System

Guardian should:

- Validate plugin signatures.
- Enforce declared capabilities.
- Quarantine unsafe plugins.
- Deny plugin execution when risk exceeds policy.

### Aether Script Runtime

Guardian should:

- Validate signed scripts.
- Block risky workflows.
- Require intent declarations.
- Route script execution through restricted/sandboxed execution paths.

### Memory System

Guardian should:

- Protect identity memory.
- Prevent unauthorized memory edits.
- Log memory mutations.
- Require approval for identity or long-term memory modification.

### Homeostasis System

Guardian should:

- Allow safe corrective actions.
- Block corrections that weaken Security.
- Require approval for disruptive actions.
- Prevent autonomous stability loops from bypassing policy.

### Self-Improvement System

Guardian should:

- Review proposed modifications.
- Require rollback plans.
- Block unsafe self-alteration.
- Escalate modifications to core systems.

### Security System

Guardian should:

- Consume Security System controls for permissions, signatures, sandboxing, secrets, and network policy.
- Emit higher-order enforcement decisions back to Security.
- Use the signed Security audit ledger for Guardian decisions.
- Never weaken Security policy without elevated approval.

## Minimum viable Guardian v0.1

Guardian v0.1 should be a practical enforcement layer, not a complete philosophical authority.

Required v0.1 features:

- `GuardianDecision` data model.
- `IntentDeclaration` data model.
- `RiskAssessment` data model.
- `PolicyResult` data model.
- `AuditRecord` data model.
- `CapabilityGrant` data model.
- Basic policy engine.
- Capability checker.
- Risk scoring.
- Audit logging.
- Approval-required decisions.
- Deny-by-default mode.
- Integration with file actions.
- Integration with plugin/script execution.

## Build plan

### Phase 1 - Data Contracts

Create stable models:

- `IntentDeclaration`
- `GuardianDecision`
- `RiskAssessment`
- `PolicyResult`
- `GuardianAuditRecord`
- `CapabilityGrant`
- `ApprovalRequest`
- `ContainmentResult`

Goal:

All future Guardian logic depends on stable, typed contracts.

### Phase 2 - Policy Engine

Implement:

- policy file loading
- capability permission evaluation
- deny-by-default behavior
- environment-aware profiles
- simple allow/deny rules

Goal:

Guardian can say yes or no based on explicit policy.

### Phase 3 - Risk Scoring

Implement:

- simple weighted risk scoring
- environment-aware escalation
- high-risk and critical-risk thresholds
- approval and containment recommendations

Goal:

Guardian can classify action danger consistently.

### Phase 4 - Audit Ledger

Implement:

- Guardian audit records
- append-only JSONL records through the signed Security audit ledger
- decision and outcome correlation

Goal:

Every Guardian decision leaves a trace.

### Phase 5 - Reversibility Checks

Implement:

- rollback metadata validation - implemented for Guardian intents
- file snapshot support
- git diff capture
- config backup hooks
- memory version marker interface

Goal:

No meaningful action happens without a recovery path or elevated approval.

### Phase 6 - Approval Flow

Implement:

- automatic approval state
- pending user approval state - implemented
- approved/denied state transitions - implemented
- single-use approval consumption - implemented
- intent-bound approval validation - implemented
- approval timeout handling - implemented
- authenticated Hub status summary - implemented
- authenticated Hub approval administration - implemented

Goal:

Human-in-the-loop control exists for risky operations.

### Phase 7 - Containment

Implement:

- deny action - implemented
- revoke capability
- disable plugin
- pause agent
- emergency stop flag
- active containment enforcement - implemented
- authenticated Hub containment administration - implemented
- plugin disable/block containment action application - implemented
- subsystem wildcard containment for self-improvement proposal application - implemented
- script execution preflight enforcement - implemented
- standard-library executor command preflight enforcement - implemented
- advanced memory write preflight enforcement - implemented
- agent task submission preflight enforcement - implemented
- Homeostasis actuator execution preflight enforcement - implemented
- outbound network request preflight enforcement - implemented
- plugin module load preflight enforcement - implemented
- Hub plugin registration preflight enforcement - implemented
- CoreTools filesystem mutation preflight enforcement - implemented
- Lyrixa plugin system install/uninstall/template preflight enforcement - implemented
- Aetherra Hub marketplace plugin install/uninstall preflight enforcement - implemented
- optimization proposal execution preflight enforcement - implemented
- Hub kernel pause/resume/drain/queue-limit preflight enforcement - implemented

Goal:

Guardian can stop unsafe behavior.

### Phase 8 - Integration

Wire Guardian into:

- Aether Script execution - implemented for `ScriptExecutor.execute`
- plugin registration, installation, loading, and execution - implemented for Hub `/api/plugins/register`, `LyrixaPluginSystem`, `PluginManager.load_plugin`, and `PluginManager.execute_plugin`
- agent task execution - implemented for Hub `/api/tasks` submissions
- memory mutation - implemented for `AetherraMemoryEngineAdvanced.remember`
- self-improvement application
- homeostasis actuators, autonomous action planning, alert escalation/notification, Hub control operations, and direct orchestrator control operations - implemented for `HomeostasisController`, `HomeostasisActuators`, `HomeostasisOrchestrator`, `IntelligentAlertManager`, plus Hub `/api/homeostasis/actuators/execute`, `/mode`, `/emergency_stop`, `/reset_emergency`, and `/rollback`
- network calls - implemented for Security `http_get` and `http_post` wrappers
- filesystem changes - implemented for CoreTools filesystem mutations
- generated plugin scaffold filesystem writes - implemented for `PluginGeneratorPlugin.save_plugin_to_disk`
- kernel queue control, pause/resume, and shutdown - implemented for Hub `/api/kernel/control/*` and direct `AetherraKernelLoop` control methods
- HMR controller reload lifecycle - implemented for `HMRController`
- remaining kernel service lifecycle, registry mutation, boot mutation, and runtime mode changes outside guarded queue controls
- service registry registration and unregistration - implemented for `AetherraServiceRegistry`
- service registry status and heartbeat trust mutation - implemented for `AetherraServiceRegistry.update_service_status`, `update_heartbeat`, and `mark_service_self_heartbeat`
- service registry message dispatch, broadcasts, and event subscription changes - implemented for `AetherraServiceRegistry.send_message`, `broadcast_message`, `subscribe_to_events`, and `unsubscribe_from_events`
- service registry external daemon forwarding - implemented for `aetherra_registry_client` HTTP status, register, update, and heartbeat calls
- event bus publish, subscribe, and ack - implemented for `EventBus`
- event bus privileged command/control event publishing - implemented for `EventBus.publish` and registry-routed publish messages
- remaining event-triggered automation executors, external bridge events, replay, and topic administration APIs if introduced
- module manager load, reload, unload, and rollback - implemented for `ModuleManager`
- remaining module artifact validation and module source trust policy
- direct agent orchestrator calls and agent registration/task lifecycle mutation - implemented for core and plugin orchestrators
- agent goal and subtask lifecycle mutation - implemented for `LyrixaGoalSystem`
- multi-agent collaboration task delegation and dynamic collaboration agent additions - implemented for `AICollaborationFramework`
- legacy interpreter plugin and meta-plugin dispatch - implemented for `AetherraInterpreter`
- compiled parser plugin load path - implemented through guarded `AetherraInterpreter.load_plugin`
- future agent spawning outside registration, pause/resume outside goal status updates, or new tool-delegation APIs must declare Guardian intents before enablement
- memory deletion, import/export, bulk consolidation, QFAC mutation, and memory restore operations
- AI engine task dispatch - implemented for `AetherraEngine.execute_task`
- Lyrixa assistant task dispatch - implemented for `LyrixaAssistant.execute_task`
- remaining future LLM-native tool/function dispatch
- chat ingress - implemented for Hub `/api/ai/ask`, `/api/ai/stream`, and `/api/lyrixa/chat`
- Lyrixa safe-edit file application - implemented for `LyrixaChatService.apply_fix`
- remaining chat and Lyrixa command planning, tool invocation, prompt-triggered automation, memory writes, response actions, and UI/CLI action dispatch outside guarded downstream APIs
- consciousness self-model persistence - implemented for `SelfModelManager.update`
- consciousness episodic event persistence - implemented for `EpisodicStore.append`
- consciousness continuity-memory persistence - implemented for `ContinuityMemory.record` and `save`
- consciousness narrator persistence - implemented for `NarrativeLayer`
- consciousness learning-loop state persistence - implemented for `LearningLoop`
- consciousness meta-cognition self-knowledge and reflection persistence - implemented for `MetaCognitionSystem`
- consciousness core autonomy plan execution - implemented for `ConsciousnessCore._maybe_act`
- consciousness core micro/macro reflection updates - implemented for `ConsciousnessCore`
- transcendence consolidation state mutation - implemented for `TranscendenceConsolidationEngine`
- consciousness singularity validation and achievement - implemented for `ConsciousnessSingularityEngine`
- remaining consciousness reflection loops and remaining experimental quantum/transcendence engines
- AI trainer job/eval submission - implemented for `aetherra_hub.services.trainer.submit_job` and `submit_eval`
- remaining AI trainer dataset ingestion/export, real training backend start, model fine-tune execution, evaluation promotion, adapter deployment, model registry writes, artifact signing, and policy/model replacement
- remaining deployment, backup/restore, and cleanup workflows outside covered paths

Goal:

Guardian becomes unavoidable for privileged behavior.

### Phase 9 - Testing

Create tests for:

- safe action allowed
- unsafe action denied
- missing capability denied
- unsigned plugin denied
- risky action requires approval
- irreversible action blocked
- audit record created
- containment activates
- policy override works
- production profile is strict

Goal:

Guardian becomes trustworthy.

### Phase 10 - Guardian Dashboard

Build UI panels for:

- current mode
- recent decisions
- denied actions
- approval queue
- active capabilities
- risk events
- containment status
- audit search

Goal:

Guardian becomes visible.

## Operating modes

Guardian should support staged rollout modes.

### Observe

Logs decisions but does not block.

### Advisory

Warns and suggests action.

### Enforcing

Blocks unsafe or unauthorized actions.

### Strict

Deny-by-default with signed policies required.

### Emergency

Only recovery and inspection actions are allowed.

## Configuration

Proposed environment flags:

```powershell
$env:AETHERRA_GUARDIAN_ENABLED='1'
$env:AETHERRA_GUARDIAN_MODE='observe'
$env:AETHERRA_GUARDIAN_POLICY_HOME='.aetherra/guardian/policy'
$env:AETHERRA_GUARDIAN_REQUIRE_INTENT='1'
$env:AETHERRA_GUARDIAN_REQUIRE_ROLLBACK='1'
$env:AETHERRA_GUARDIAN_APPROVAL_TIMEOUT_SEC='900'
$env:AETHERRA_GUARDIAN_STRICT_PRODUCTION='1'
```

Suggested production defaults:

- `AETHERRA_GUARDIAN_ENABLED=1`
- `AETHERRA_GUARDIAN_MODE=strict`
- `AETHERRA_GUARDIAN_REQUIRE_INTENT=1`
- `AETHERRA_GUARDIAN_REQUIRE_ROLLBACK=1`
- deny-by-default policy behavior

## Success criteria

Guardian is operational when:

- Every privileged action passes through Guardian.
- Deny-by-default works.
- Risk scoring works.
- Audit logs are created.
- Risky actions require approval.
- Irreversible actions are blocked or escalated.
- Plugins and scripts require validation.
- Memory mutations are protected.
- Homeostasis cannot weaken Security.
- Self-improvement cannot modify core systems without approval.
- Emergency containment works.

## Initial test plan

Planned test files:

- `tests/unit/test_guardian_models.py`
- `tests/unit/test_guardian_policy_engine.py`
- `tests/unit/test_guardian_capability_gate.py`
- `tests/unit/test_guardian_risk.py`
- `tests/unit/test_guardian_reversibility.py`
- `tests/unit/test_guardian_approval.py`
- `tests/unit/test_guardian_containment.py`
- `tests/unit/test_guardian_audit.py`
- `tests/integration/test_guardian_plugin_execution.py`
- `tests/integration/test_guardian_script_execution.py`
- `tests/integration/test_guardian_homeostasis_gate.py`

Minimum verification target for v0.1:

- Safe read-only action is allowed.
- Missing capability is denied.
- Risky write action requires approval or rollback metadata.
- Critical security modification is denied or contained.
- Every decision creates an audit record.
- Production profile defaults to strict behavior.

## Roadmap

### v0.1 - Functional Guardian Core

- Data contracts
- Policy engine
- Capability gate
- Risk scoring
- Audit records
- Approval-required decisions
- Basic containment
- Initial integration with file/plugin/script actions

### v0.2 - System Integration

- Agent task gating
- Memory mutation gating
- Homeostasis actuator gating
- Self-improvement gating
- Network action gating
- Guardian mode management

### v0.3 - Visibility and Operations

- Guardian dashboard
- Approval queue UI
- Decision search
- Risk event timeline
- Containment state panel

### v1.0 - Production Governance Layer

- Strict production defaults
- Signed Guardian policies
- Complete privileged-action coverage
- Full audit correlation between Guardian and Security
- Recovery workflows for emergency mode

## Final principle

Guardian exists so Aetherra can become powerful without becoming careless.

Its purpose is not to prevent growth. Its purpose is to make growth safe.

Aetherra may evolve, but it must evolve with evidence, restraint, reversibility, and conscience.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
