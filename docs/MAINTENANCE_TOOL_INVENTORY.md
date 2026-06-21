# Maintenance Tool Inventory

This inventory classifies `tools/maintenance/` by operational behavior. It is a
triage document, not a deletion plan. Do not remove or move tools from this list
without a separate review of imports, tests, and active workflows.

## Category Rules

- Read-only/report: inspects the repository or runtime and should not mutate
  source files. If it writes output, that output should be an explicit report.
- Guardian-gated report writer: writes generated reports or inventories only
  after Guardian approval.
- Guardian-gated action tool: may write, move, delete, install, or rewrite files
  after Guardian approval.
- Legacy/questionable: old, duplicate, oversized, or weakly guarded tooling that
  should not be preferred for new work until reviewed.

## Preferred Read-Only Or Report Tools

These are the safest candidates for routine Maintenance observation and
diagnosis:

- `check_unicode.py`
- `debug_registry_connection.py`
- `final_legal_check.py`
- `launch_monitor.py`
- `verify_imports.py`
- `analyze_stubs.py`
- `aetherra_core_analyzer.py`
- `verify_legal_compliance.py`
- `validate_architecture.py`
- `universal_directory_analyzer.py`
- `project_analyzer.py`
- `advanced_analyzer.py`

Notes:

- Some analyzer/report tools write reports. Those writes should target approved
  output paths and remain Guardian-gated when they create durable files.
- `advanced_analyzer_fixed.py` appears to overlap with `advanced_analyzer.py` and
  should be reviewed before either is treated as canonical.

## Guardian-Gated Report Writers

These tools produce generated reports, inventories, or documentation and already
contain Guardian preflight patterns:

- `advanced_analyzer.py`
- `advanced_analyzer_fixed.py`
- `check_architecture.py`
- `create_documentation.py`
- `generate_reports.py`
- `generate_stub_inventory.py`
- `project_analyzer.py`
- `universal_directory_analyzer.py`
- `validate_architecture.py`
- `verify_legal_compliance.py`

Expected behavior:

- No report write without Guardian approval.
- Generated reports should go to ignored output paths unless intentionally
  promoted into `docs/`.
- Generated root-level report files should be avoided.
- New or updated report writers should use
  `Aetherra.maintenance.classify_report_destination()` before writing durable
  output.

## Guardian-Gated Action Tools

These tools can mutate files, move files, delete files, rewrite imports, or
otherwise alter the repository. They must remain explicit/manual tools and
should not be invoked automatically by Maintenance:

- `complete_organizer.py`
- `final_file_organizer.py`
- `fix_architecture.py`
- `fix_architecture_simple.py`
- `fix_imports.py`
- `fix_phase7_errors.py`
- `fix_plugin_imports.py`
- `fix_remaining_errors_round2.py`
- `fix_remaining_imports.py`
- `fix_unicode_issues.py`
- `fix_unicode_service_registry.py`
- `focused_cleanup.py`
- `post_cleanup_import_updater.py`
- `quick_fix_imports.py`
- `safe_cleanup.py`
- `smart_cleanup.py`

Expected behavior:

- Require Guardian approval.
- Require Security capability checks for file writes, file deletes, network, and
  package install actions.
- Prefer dry-run or plan-first behavior.
- Provide rollback guidance or backups where applicable.
- Never run as part of passive observation.

## Legacy Or Questionable Tools

These need review before being considered part of the functional Maintenance
foundation:

- `aetherra_core_cleaner.py`
- `aetherra_import_updater.py`
- `aetherra_lyrixa_cleaner.py`
- `aetherra_plugins_cleaner.py`
- `clean_hub_tmp.py`
- `clean_hub_tmp_utf8.py`
- `stub_finder.py`

Reasons:

- Some perform direct writes, moves, or deletes without the newer Guardian
  preflight style.
- Some generate root-level reports or backups.
- `clean_hub_tmp.py` is very large and appears to contain broad Hub/runtime
  logic rather than a focused maintenance tool.
- `stub_finder.py` writes `STUB_INVENTORY.json` directly and should be replaced
  by `generate_stub_inventory.py` for guarded inventory generation.

## Current Recommendation

For Maintenance foundation work, prefer:

1. `generate_stub_inventory.py`
2. `project_analyzer.py`
3. `validate_architecture.py`
4. `verify_legal_compliance.py`
5. `verify_imports.py`
6. `universal_directory_analyzer.py`

Treat action tools as manual, Guardian-gated execution paths only. Treat legacy
or questionable tools as cleanup candidates after all systems reach functional
completion.
