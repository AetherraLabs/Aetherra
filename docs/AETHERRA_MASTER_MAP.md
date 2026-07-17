# Aetherra Master Map

Updated: 2026-07-16

This is the operational map for the Aetherra repository. It is generated
from tracked files and is paired with `docs/AETHERRA_FILE_MANIFEST.json`,
which contains the per-file and per-directory inventory.

## Rule

A file is treated as required only when it has evidence that it participates
in boot, runtime, governance, security, UI, plugin operation, configuration,
documentation, tooling, or verification. Files without that evidence are
marked for review before removal.

## Current Inventory

- Tracked files: 1929
- Tracked directories: 231
- Files confirmed keep: 248
- Files requiring suite/doc/tool/provisional review: 1681
- Runtime/candidate/unknown files needing evidence: 694

### By Category

- configuration: 95
- documentation: 314
- legacy-or-archive: 4
- operational-runtime: 793
- rename-debt: 1
- test: 514
- tooling: 208

### By Lifecycle

- boot: 4
- build-or-ci: 95
- documentation: 314
- governed-runtime: 30
- historical: 4
- maintenance: 208
- operator: 9
- plugin-runtime: 91
- runtime: 543
- runtime-api: 73
- runtime-support: 34
- runtime-ui: 9
- unknown-or-compatibility: 1
- verification: 514

## Top-Level Folder Map

| Folder | Files | Category | Status |
| --- | ---: | --- | --- |
| `Aetherra/` | 713 | operational-runtime | provisional-runtime |
| `tests/` | 512 | test | review-by-suite |
| `docs/` | 266 | documentation | review-doc |
| `tools/` | 188 | tooling | review-tool |
| `aetherra_hub/` | 56 | operational-runtime | keep |
| `.github/` | 45 | configuration | keep |
| `docs-organized/` | 21 | documentation | review-doc |
| `plugins/` | 11 | operational-runtime | provisional-runtime |
| `aetherra_coding/` | 7 | operational-runtime | provisional-runtime |
| `scripts/` | 7 | tooling | review-tool |
| `requirements/` | 6 | configuration | keep |
| `archive/` | 4 | legacy-or-archive | candidate-review |
| `config/` | 3 | configuration | keep |
| `configs/` | 3 | configuration | keep |
| `demos/` | 3 | tooling | review-tool |
| `examples/` | 2 | tooling | review-tool |
| `lyrixa/` | 2 | operational-runtime | provisional-runtime |
| `schema_validators/` | 2 | configuration | keep |
| `toolshed/` | 2 | tooling | review-tool |
| `.devcontainer/` | 1 | configuration | keep |
| `.githooks/` | 1 | configuration | keep |
| `.vscode/` | 1 | configuration | keep |
| `badge/` | 1 | tooling | review-tool |
| `cli/` | 1 | operational-runtime | provisional-runtime |
| `documentation/` | 1 | documentation | review-doc |
| `metadata/` | 1 | documentation | review-doc |

## Operational Runtime Files

These are files currently classified as directly involved in boot,
runtime, governed runtime, API operation, plugin operation, or Runtime UI.

- `Aetherra/__init__.py` - Aetherra package API (runtime-support; keep)
- `Aetherra/aetherra_core/README.md` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/__init__.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/aetherra_grammar.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/aetherra_interpreter.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/aetherra_parser.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/agent.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/agent_executor.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/agent_orchestrator.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/base.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/cleanup_project.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/cognitive_adapters.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/collaboration.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/contradiction_detection_agent.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/conversation.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/conversation_manager.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/core_agent.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/critique_agent.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/curiosity_agent.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/enhanced.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/enhanced_conversation_manager.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/enhanced_interpreter.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/enhanced_language.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/enhanced_lyrixa.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/enhanced_parser.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/enhanced_self_evaluation_agent.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/escalation_agent.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/goal_agent.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/goal_forecaster.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/goals.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/grammar.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/learning_loop_integration_agent.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/lyrixa.yaml` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/lyrixa_assistant.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/lyrixa_memory.json` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/lyrixa_script_integration.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/natural_compiler.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/optimized_integration.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/parser.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/reflexive_loop.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/self_evaluation_agent.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/agents/self_question_generator_agent.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/ai/README.md` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/ai/llm_integration.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/cognitive/README.md` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/cognitive/meta_reasoning.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/cognitive/reasoning_engine.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/cognitive/reasoning_providers.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/config/README.md` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/config/__init__.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/config/config_loader.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/config/system.json` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/conversation/human_style.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/engine/README.md` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/engine/__init__.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/engine/aetherra_engine.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/engine/assistant.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/engine/intelligence/README.md` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/engine/intelligence/__init__.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/engine/intelligence/intent_recognition.js` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/engine/lyrixa_memory.json` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/engine/prompt_engine.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/engine/readiness.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/engine/reasoning_engine.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/engine/self_improvement_engine.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/events/README.md` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/file_system/README.md` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/file_system/__init__.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/file_system/compression_analyzer.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/intelligence/README.md` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/intelligence/core_intelligence.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/intelligence/intelligence_integration.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/kernel/README.md` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/kernel/__init__.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/kernel/gui_generator.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/kernel/memory_kernel.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/kernel/narrator.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/kernel/pulse.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/kernel/quantum_bridge.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/kernel/reflector.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/kernel/web_bridge.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/QuantumEnhancedMemoryEngine/README.md` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/QuantumEnhancedMemoryEngine/__init__.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/QuantumEnhancedMemoryEngine/causal_brancher.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/QuantumEnhancedMemoryEngine/compression.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/QuantumEnhancedMemoryEngine/fractal_encoder.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/QuantumEnhancedMemoryEngine/observer_effects.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/QuantumEnhancedMemoryEngine/quantum_config.json` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/QuantumEnhancedMemoryEngine/quantum_memory_engine.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/README.md` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/__init__.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/aetherra_memory_engine.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/causal_branch_simulator.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/compression_metrics.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/concept_clustering.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/enhanced_memory.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/fractal_encoder.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/fractal_hierarchies.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/fractal_mesh/README.md` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/fractal_mesh/__init__.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/fractal_mesh/analogs/README.md` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/fractal_mesh/analogs/__init__.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/fractal_mesh/analogs/pattern_matcher.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/fractal_mesh/base.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/fractal_mesh/concepts/README.md` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/fractal_mesh/concepts/__init__.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/fractal_mesh/concepts/concept_clusters.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/fractal_mesh/timelines/README.md` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/fractal_mesh/timelines/__init__.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/fractal_mesh/timelines/episodic_timeline.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/fractal_mesh/timelines/reflective_timeline_engine.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/fractal_replay_engine.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/lightweight_memory_core.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/lyrixa_memory_engine.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/memory_core.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/memory_core_adapter.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/memory_kernel.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/memory_learning.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/models.py` - Core runtime package (runtime; provisional-runtime)
- `Aetherra/aetherra_core/memory/narrator/README.md` - Core runtime package (runtime; provisional-runtime)
- ... 673 more in `docs/AETHERRA_FILE_MANIFEST.json`

## Configuration And Build Files

- `.coveragerc` - Repository configuration (build-or-ci; keep)
- `.devcontainer/devcontainer.json` - Developer container configuration (build-or-ci; keep)
- `.editorconfig` - Repository configuration (build-or-ci; keep)
- `.env.autonomy.production.template` - Repository configuration (build-or-ci; keep)
- `.env.autonomy.staging.template` - Repository configuration (build-or-ci; keep)
- `.env.example` - Repository configuration (build-or-ci; keep)
- `.env.template` - Repository configuration (build-or-ci; keep)
- `.githooks/pre-commit` - Git hook support (build-or-ci; keep)
- `.github/CODEOWNERS` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/CONTRIBUTING.md` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/FUNDING.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/ISSUE_TEMPLATE/bug_report.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/ISSUE_TEMPLATE/config.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/ISSUE_TEMPLATE/feature_request.md` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/ISSUE_TEMPLATE/feature_request.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/ISSUE_TEMPLATE/revolutionary_enhancement.md` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/ISSUE_TEMPLATE/task.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/PAGES_STATUS.md` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/PULL_REQUEST_TEMPLATE/remove_legacy_hub.md` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/actions/setup-python-deps/action.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/dependabot.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/labeler.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/labels.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/pull_request_template.md` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/aether-verification.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/ci-fast-quality.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/ci.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/ci_quality_gates.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/codeql.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/commit-message-lint.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/contributor-check.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/dependabot-auto-merge.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/deploy-pages.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/docs.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/import_validation.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/labels-sync.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/markdown-lint.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/override_prune.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/packaging-check.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/pr-size-gate.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/production-readiness.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/provenance_tag.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/publish_release.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/release-artifacts.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/release.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/repo-sanity.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/security-checks.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/security-sanity.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/semantic-dry-run.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/size-label.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/stale.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/workflow-classifier.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.github/workflows/workflow-parse-baseline.yml` - GitHub workflows and repository automation (build-or-ci; keep)
- `.gitignore` - Repository configuration (build-or-ci; keep)
- `.gitignore_security` - Repository configuration (build-or-ci; keep)
- `.gitleaks.toml` - Repository configuration (build-or-ci; keep)
- `.markdownlint.json` - Repository configuration (build-or-ci; keep)
- `.markdownlint.jsonc` - Repository configuration (build-or-ci; keep)
- `.pre-commit-config.yaml` - Repository configuration (build-or-ci; keep)
- `.vscode/tasks.json` - Workspace task configuration (build-or-ci; keep)
- `.yamllint.yaml` - Repository configuration (build-or-ci; keep)
- `Aetherra/config/README.md` - Aetherra package configuration (build-or-ci; keep)
- `Aetherra/config/quantum/README.md` - Aetherra package configuration (build-or-ci; keep)
- `Aetherra/config/quantum/monitoring_config.json` - Aetherra package configuration (build-or-ci; keep)
- `Aetherra/config/quantum/quantum_config.json` - Aetherra package configuration (build-or-ci; keep)
- `Aetherra/config/quantum/scaling_config.json` - Aetherra package configuration (build-or-ci; keep)
- `Aetherra/pyproject.toml` - Aetherra package configuration (build-or-ci; keep)
- `Dockerfile` - Repository configuration (build-or-ci; keep)
- `MANIFEST.in` - Repository configuration (build-or-ci; keep)
- `aetherra_os.spec` - Repository configuration (build-or-ci; keep)
- `commitlint.config.js` - Repository configuration (build-or-ci; keep)
- `config.autonomy.production.json` - Repository configuration (build-or-ci; keep)
- `config.autonomy.staging.json` - Repository configuration (build-or-ci; keep)
- `config.json` - Repository configuration (build-or-ci; keep)
- `config.production.json` - Repository configuration (build-or-ci; keep)
- `config/config.json` - Configuration files (build-or-ci; keep)
- `config/lyrixa_intelligence.json` - Configuration files (build-or-ci; keep)
- `config/self_model.json` - Configuration files (build-or-ci; keep)
- `configs/qfac.yaml` - Configuration files (build-or-ci; keep)
- `configs/sql/storm_schema_v1.sql` - Configuration files (build-or-ci; keep)
- ... 15 more in `docs/AETHERRA_FILE_MANIFEST.json`

## Verification Surface

Tests are not runtime files, but they are required until each suite is
mapped to a current system, replaced, or intentionally retired.

- `Aetherra/alpha_boot_validation.py` - Alpha boot validation contract (verification; review-by-suite)
- `Aetherra/integration_validation.py` - Cross-system integration validation (verification; review-by-suite)
- `tests/README.md` - Automated tests and probes (verification; review-by-suite)
- `tests/__init__.py` - Automated tests and probes (verification; review-by-suite)
- `tests/acceptance/test_autonomous_error_correction_golden_paths.py` - Automated tests and probes (verification; review-by-suite)
- `tests/acceptance/test_canary_e2e.py` - Automated tests and probes (verification; review-by-suite)
- `tests/acceptance/test_load_and_security_phase2f.py` - Automated tests and probes (verification; review-by-suite)
- `tests/acceptance/test_maintenance_e2e_flow.py` - Automated tests and probes (verification; review-by-suite)
- `tests/acceptance/test_maintenance_security.py` - Automated tests and probes (verification; review-by-suite)
- `tests/acceptance/test_security_strict_and_rate.py` - Automated tests and probes (verification; review-by-suite)
- `tests/ai/README.md` - Automated tests and probes (verification; review-by-suite)
- `tests/ai/test_ai_fallback.py` - Automated tests and probes (verification; review-by-suite)
- `tests/ai/test_intelligence_core.py` - Automated tests and probes (verification; review-by-suite)
- `tests/ai/test_intelligence_core_enhanced.py` - Automated tests and probes (verification; review-by-suite)
- `tests/ai/test_intelligence_real_api.py` - Automated tests and probes (verification; review-by-suite)
- `tests/ai/test_multi_agent_coordination.py` - Automated tests and probes (verification; review-by-suite)
- `tests/ai/test_neural_interface.py` - Automated tests and probes (verification; review-by-suite)
- `tests/ai/test_neural_interface_quick.py` - Automated tests and probes (verification; review-by-suite)
- `tests/ai/test_openai_integration.py` - Automated tests and probes (verification; review-by-suite)
- `tests/api/manual/engine_metrics_probe.py` - Automated tests and probes (verification; review-by-suite)
- `tests/api/test_approvals_api.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_aether_e2e.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_agent_collaboration.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_consciousness_phase3.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_crash_recovery_simulation.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_deterministic_profile_harness.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_diagnostics_schema.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_extended_crash_recovery.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_hello_plugin_capability.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_hello_plugin_metadata.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_hub_metrics_observability.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_hub_plugin_and_chat_integration.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_hub_quantum_endpoint.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_hub_telemetry_and_federation.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_hub_trainer_disabled_and_metrics.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_hub_trainer_endpoints.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_lyrixa_chat.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_lyrixa_chat_bridge_schema.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_lyrixa_chat_endpoint.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_lyrixa_chat_schema_strict.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_lyrixa_ownership_answer.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_lyrixa_primary_chat.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_memory_fragmentation_metrics.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_memory_module_integrity.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_memory_recall.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_memory_systems_coverage.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_openapi_agents_path.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_openapi_examples_and_runner_endpoints.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_ownership_memory.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_passive_heartbeat_interval.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_plugin_analytics_coverage.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_plugin_exec_migrator.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_plugin_parallel_and_failure_paths.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_plugin_reload.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_qfac_admin_cli.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_qfac_in_os.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_qfac_metrics_schema.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_qfac_retrieval_parity_metrics_schema.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_qfac_retrieval_parity_per_k_counters_schema.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_qfac_retrieval_parity_per_k_ratio_schema.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_qfac_retrieval_parity_per_k_schema.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_qfac_retrieval_parity_ratio_schema.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_qfac_retrieval_parity_toggle.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_qfac_retrieval_policy_config_metrics_schema.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_qfac_retrieval_threshold_behavior.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_qfac_shadow_collection_smoke.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_qfac_validator_shadow_schema.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_reflection_memory_stability.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_security_capabilities_coverage.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_security_sandbox_placeholders.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_self_improvement_metrics.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_self_maintenance_services.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_selfinc_proposal_consumer.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_snapshot_replay_harness.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_spec_gate_marker.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_static_security_scan.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_storm_acceptance.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_transcendence_deterministic_metrics.py` - Automated tests and probes (verification; review-by-suite)
- `tests/capabilities/test_working_api_coverage.py` - Automated tests and probes (verification; review-by-suite)
- `tests/coding/test_revert_and_diff.py` - Automated tests and probes (verification; review-by-suite)
- ... 434 more in `docs/AETHERRA_FILE_MANIFEST.json`

## Documentation Surface

Documentation is retained when it is active, architectural, legal,
operator-facing, or historical material that still explains project context.

- `Aetherra/README.md` - Aetherra package overview (documentation; review-doc)
- `Aetherra/docs/AETHERRA_MANIFESTO.md` - Legacy package documentation (documentation; review-doc)
- `Aetherra/docs/AI_OS_MANIFESTO.md` - Legacy package documentation (documentation; review-doc)
- `Aetherra/docs/README.md` - Legacy package documentation (documentation; review-doc)
- `Aetherra/docs/SELF_ORGANIZING_INTELLIGENCE.md` - Legacy package documentation (documentation; review-doc)
- `Aetherra/docs/aetherra_labs_vision.md` - Legacy package documentation (documentation; review-doc)
- `Aetherra/docs/architecture_diagram.png.png` - Legacy package documentation (documentation; review-doc)
- `CHANGELOG.md` - Public project documentation (documentation; keep)
- `CODE_OF_CONDUCT.md` - Public project documentation (documentation; keep)
- `CONTRIBUTING.md` - Public project documentation (documentation; keep)
- `COPYRIGHT` - Public project documentation (documentation; keep)
- `GOVERNANCE.md` - Public project documentation (documentation; keep)
- `INSTALL.md` - Public project documentation (documentation; keep)
- `LEGAL_COMPLIANCE.md` - Public project documentation (documentation; keep)
- `LICENSE` - Public project documentation (documentation; keep)
- `LICENSE_POLICY.md` - Public project documentation (documentation; keep)
- `NOTICE` - Public project documentation (documentation; keep)
- `OWNERSHIP.md` - Public project documentation (documentation; keep)
- `PRIVACY.md` - Public project documentation (documentation; keep)
- `QUICK_START.md` - Public project documentation (documentation; keep)
- `README.md` - Public project documentation (documentation; keep)
- `RELEASE_NOTES_0.5.0-beta.0.md` - Public project documentation (documentation; keep)
- `SECURITY.md` - Public project documentation (documentation; keep)
- `STEWARDSHIP.md` - Public project documentation (documentation; keep)
- `SUPPORT.md` - Public project documentation (documentation; keep)
- `docs-organized/README.md` - Historical/thematic documentation (documentation; review-doc)
- `docs-organized/cleanup/CLEANUP_ANALYSIS.md` - Historical/thematic documentation (documentation; review-doc)
- `docs-organized/cleanup/README.md` - Historical/thematic documentation (documentation; review-doc)
- `docs-organized/deployment/DEPLOYMENT_COMPLETE.md` - Historical/thematic documentation (documentation; review-doc)
- `docs-organized/deployment/README.md` - Historical/thematic documentation (documentation; review-doc)
- `docs-organized/deployment/STAGE_12_COMPLETE.md` - Historical/thematic documentation (documentation; review-doc)
- `docs-organized/fixes/IMPORT_FIXES.md` - Historical/thematic documentation (documentation; review-doc)
- `docs-organized/fixes/README.md` - Historical/thematic documentation (documentation; review-doc)
- `docs-organized/fixes/WEBSOCKET_CONNECTION_FIX.md` - Historical/thematic documentation (documentation; review-doc)
- `docs-organized/guides/MULTI_AI_SETUP_GUIDE.md` - Historical/thematic documentation (documentation; review-doc)
- `docs-organized/guides/README.md` - Historical/thematic documentation (documentation; review-doc)
- `docs-organized/legacy/README.md` - Historical/thematic documentation (documentation; review-doc)
- `docs-organized/manifesto/AETHERRA_MANIFESTO.md` - Historical/thematic documentation (documentation; review-doc)
- `docs-organized/manifesto/AI_OS_MANIFESTO.md` - Historical/thematic documentation (documentation; review-doc)
- `docs-organized/manifesto/README.md` - Historical/thematic documentation (documentation; review-doc)
- `docs-organized/manifesto/SELF_ORGANIZING_INTELLIGENCE.md` - Historical/thematic documentation (documentation; review-doc)
- `docs-organized/project/CONTRIBUTING.md` - Historical/thematic documentation (documentation; review-doc)
- `docs-organized/project/README.md` - Historical/thematic documentation (documentation; review-doc)
- `docs-organized/project/quantum fractal adaptive compression.md` - Historical/thematic documentation (documentation; review-doc)
- `docs-organized/tools/AETHER_SCRIPT_DEMONSTRATION_SUMMARY.md` - Historical/thematic documentation (documentation; review-doc)
- `docs-organized/tools/README.md` - Historical/thematic documentation (documentation; review-doc)
- `docs/404.html` - Active documentation (documentation; review-doc)
- `docs/ACTIVE_SYSTEMS.md` - Active documentation (documentation; review-doc)
- `docs/AETHERRA_AGENT_SYSTEM.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_AI_TRAINER_SYSTEM.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_ARTIFICIAL_INTELLIGENCE_SYSTEM.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_BOOT_INTERACTION_CONTRACT_V1.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_CHAT_SYSTEM.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_CLAIMS_VALIDATION.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_CODING_SYSTEM.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_COMPLETE_OVERVIEW_2026-03-12.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_CONSCIOUSNESS_SYSTEM.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_EVENT_BUS_SYSTEM.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_FILE_MANIFEST.json` - Active documentation (documentation; keep)
- `docs/AETHERRA_GUARDIAN_SYSTEM.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_HMR_GUIDE.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_HOMEOSTASIS_SYSTEM.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_HUB_API_REFERENCE.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_IDENTITY_SPEC_V1.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_INTEGRATION_VALIDATION.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_KERNEL_SYSTEM.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_LYRIXA_SYSTEM.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_MAINTENANCE_SYSTEM.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_MASTER_MAP.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_MEMORY_SYSTEM.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_MIND_MAP.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_PLUGIN_SYSTEM.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_RUNTIME_UI_SYSTEM.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_SECURITY_SYSTEM.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_SELF-IMPROVEMENT_SYSTEM.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_SELF-INCORPORATION_SYSTEM.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_SELF_IMPROVEMENT_API.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_SERVICE_REGISTRY.md` - Active documentation (documentation; keep)
- `docs/AETHERRA_WEBSOCKET_API.md` - Active documentation (documentation; keep)
- `docs/AETHER_SCRIPT_TUTORIAL.md` - Active documentation (documentation; review-doc)
- ... 234 more in `docs/AETHERRA_FILE_MANIFEST.json`

## Review Queues

These files are not deleted by the generator. They are the starting point
for manual evidence review and later removal PRs. `provisional-runtime`
means the file lives under an operational package, but this pass has not
yet proven direct active use.

### Root Or Unknown Candidates

- `Aetherra/aetherra_core/README.md` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/__init__.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/aetherra_grammar.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/aetherra_interpreter.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/aetherra_parser.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/agent.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/agent_executor.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/agent_orchestrator.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/base.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/cleanup_project.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/cognitive_adapters.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/collaboration.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/contradiction_detection_agent.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/conversation.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/conversation_manager.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/core_agent.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/critique_agent.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/curiosity_agent.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/enhanced.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/enhanced_conversation_manager.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/enhanced_interpreter.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/enhanced_language.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/enhanced_lyrixa.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/enhanced_parser.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/enhanced_self_evaluation_agent.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/escalation_agent.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/goal_agent.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/goal_forecaster.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/goals.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/grammar.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/learning_loop_integration_agent.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/lyrixa.yaml` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/lyrixa_assistant.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/lyrixa_memory.json` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/lyrixa_script_integration.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/natural_compiler.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/optimized_integration.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/parser.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/reflexive_loop.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/self_evaluation_agent.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/agents/self_question_generator_agent.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/ai/README.md` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/ai/llm_integration.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/cognitive/README.md` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/cognitive/meta_reasoning.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/cognitive/reasoning_engine.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/cognitive/reasoning_providers.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/config/README.md` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/config/__init__.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/config/config_loader.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/config/system.json` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/conversation/human_style.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/engine/README.md` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/engine/__init__.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/engine/aetherra_engine.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/engine/assistant.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/engine/intelligence/README.md` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/engine/intelligence/__init__.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/engine/intelligence/intent_recognition.js` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/engine/lyrixa_memory.json` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/engine/prompt_engine.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/engine/readiness.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/engine/reasoning_engine.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/engine/self_improvement_engine.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/events/README.md` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/file_system/README.md` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/file_system/__init__.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/file_system/compression_analyzer.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/intelligence/README.md` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/intelligence/core_intelligence.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/intelligence/intelligence_integration.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/kernel/README.md` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/kernel/__init__.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/kernel/gui_generator.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/kernel/memory_kernel.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/kernel/narrator.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/kernel/pulse.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/kernel/quantum_bridge.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/kernel/reflector.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/kernel/web_bridge.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/QuantumEnhancedMemoryEngine/README.md` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/QuantumEnhancedMemoryEngine/__init__.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/QuantumEnhancedMemoryEngine/causal_brancher.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/QuantumEnhancedMemoryEngine/compression.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/QuantumEnhancedMemoryEngine/fractal_encoder.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/QuantumEnhancedMemoryEngine/observer_effects.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/QuantumEnhancedMemoryEngine/quantum_config.json` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/QuantumEnhancedMemoryEngine/quantum_memory_engine.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/README.md` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/__init__.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/aetherra_memory_engine.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/causal_branch_simulator.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/compression_metrics.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/concept_clustering.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/enhanced_memory.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/fractal_encoder.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/fractal_hierarchies.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/fractal_mesh/README.md` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/fractal_mesh/__init__.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/fractal_mesh/analogs/README.md` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/fractal_mesh/analogs/__init__.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/fractal_mesh/analogs/pattern_matcher.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/fractal_mesh/base.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/fractal_mesh/concepts/README.md` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/fractal_mesh/concepts/__init__.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/fractal_mesh/concepts/concept_clusters.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/fractal_mesh/timelines/README.md` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/fractal_mesh/timelines/__init__.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/fractal_mesh/timelines/episodic_timeline.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/fractal_mesh/timelines/reflective_timeline_engine.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/fractal_replay_engine.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/lightweight_memory_core.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/lyrixa_memory_engine.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/memory_core.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/memory_core_adapter.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/memory_kernel.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/memory_learning.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/models.py` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/narrator/README.md` - provisional-runtime; Core runtime package
- `Aetherra/aetherra_core/memory/narrator/__init__.py` - provisional-runtime; Core runtime package
- ... 574 more in `docs/AETHERRA_FILE_MANIFEST.json`

## Cleanup Process

1. Pick one review queue from `docs/AETHERRA_FILE_MANIFEST.json`.
2. Prove each file is imported, executed, documented as active, or unused.
3. Keep active files and update their owner/purpose if needed.
4. Remove unused files in small commits with verification.
5. Regenerate this map after every cleanup pass.

## Regeneration

```powershell
python tools\generate_master_map.py
```

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
