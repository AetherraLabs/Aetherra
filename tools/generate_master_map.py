#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""Generate Aetherra's operational Master Map and file manifest."""

from __future__ import annotations

import json
import subprocess
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER_MAP_PATH = ROOT / "docs" / "AETHERRA_MASTER_MAP.md"
MANIFEST_PATH = ROOT / "docs" / "AETHERRA_FILE_MANIFEST.json"


@dataclass(frozen=True)
class FileRecord:
    path: str
    category: str
    lifecycle: str
    owner: str
    purpose: str
    keep_status: str


OPERATIONAL_ROOT_FILES = {
    "aether.py": ("Aether Script CLI/runtime entry", "runtime"),
    "aetherra_os_launcher.py": ("Primary OS launcher", "boot"),
    "aetherra_os.py": ("OS compatibility entrypoint", "boot"),
    "aetherra_startup.py": ("Startup helper", "boot"),
    "main.py": ("Repository entrypoint", "boot"),
    "aetherra_service_registry.py": ("Service registry", "runtime"),
    "aetherra_shared_service_registry.py": ("Shared service registry", "runtime"),
    "aetherra_kernel_loop.py": ("Kernel loop", "runtime"),
    "aetherra_event_bus.py": ("Kernel event bus", "runtime"),
    "aetherra_module_manager.py": ("Kernel module manager", "runtime"),
    "aetherra_hmr_controller.py": ("Hot module reload controller", "governed-runtime"),
    "aetherra_persistent_memory.py": ("Persistent memory facade", "runtime"),
    "aetherra_script_service.py": ("Aether Script service", "runtime"),
    "aetherra_self_incorporation.py": ("Self-Incorporation service entry", "governed-runtime"),
    "aetherra_registry_client.py": ("Registry client", "runtime"),
    "aetherra_registry_daemon.py": ("Registry daemon", "runtime"),
    "aetherra_plugin_discovery.py": ("Plugin discovery and Hub sync support", "plugin-runtime"),
    "aetherra_agent_fabric.py": ("Agent Fabric runtime support", "runtime"),
    "aetherra_agent_daemon.py": ("Agent Fabric daemon entry", "runtime"),
    "aetherra_aar_broker.py": ("Agent runtime HTTP broker", "runtime-api"),
    "aetherra_outbox.py": ("Agent runtime write-ahead outbox", "runtime-support"),
    "quantum_memory_bridge.py": ("Quantum memory bridge compatibility entry", "runtime"),
    "unicode_logger.py": ("Unicode-safe logging support", "runtime-support"),
}

CONFIG_ROOT_FILES = {
    ".coveragerc",
    ".editorconfig",
    ".env.autonomy.production.template",
    ".env.autonomy.staging.template",
    ".env.example",
    ".env.template",
    ".gitleaks.toml",
    ".gitignore",
    ".gitignore_security",
    ".markdownlint.json",
    ".markdownlint.jsonc",
    ".pre-commit-config.yaml",
    ".yamllint.yaml",
    "commitlint.config.js",
    "config.autonomy.production.json",
    "config.autonomy.staging.json",
    "config.json",
    "config.production.json",
    "Dockerfile",
    "license_overrides.yml",
    "MANIFEST.in",
    "pyproject.toml",
    "requirements-ci.lock",
    "requirements.lock",
    "requirements.txt",
    "setup.py",
}

PUBLIC_DOC_ROOT_FILES = {
    "CHANGELOG.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "COPYRIGHT",
    "GOVERNANCE.md",
    "INSTALL.md",
    "LEGAL_COMPLIANCE.md",
    "LICENSE",
    "LICENSE_POLICY.md",
    "NOTICE",
    "OWNERSHIP.md",
    "PRIVACY.md",
    "QUICK_START.md",
    "README.md",
    "RELEASE_NOTES_0.5.0-beta.0.md",
    "SECURITY.md",
    "STEWARDSHIP.md",
    "SUPPORT.md",
}

RUNTIME_PREFIXES = {
    "Aetherra/api/": ("Aetherra API package", "runtime-api"),
    "Aetherra/ai_engine/": ("AI coordination package", "runtime"),
    "Aetherra/analysis/": ("Static analysis and risk helpers", "runtime-support"),
    "Aetherra/aetherra_core/": ("Core runtime package", "runtime"),
    "Aetherra/cli/": ("Aetherra command-line package", "operator"),
    "Aetherra/coding/": ("Coding readiness package", "governed-runtime"),
    "Aetherra/guardian/": ("Guardian governance system", "governed-runtime"),
    "Aetherra/security/": ("Security enforcement system", "runtime"),
    "Aetherra/homeostasis/": ("Homeostasis observation and verification", "runtime"),
    "Aetherra/maintenance/": ("Maintenance coordination", "governed-runtime"),
    "Aetherra/self_improvement/": ("Self-Improvement proposal system", "governed-runtime"),
    "Aetherra/self_incorporation/": ("Self-Incorporation execution package", "governed-runtime"),
    "Aetherra/consciousness/": ("Consciousness processing package", "runtime"),
    "Aetherra/core/": ("Legacy core compatibility package", "runtime"),
    "Aetherra/hub/": ("Hub federation package", "runtime-api"),
    "Aetherra/integration/": ("Integration bridge package", "runtime-support"),
    "Aetherra/interface_bridge/": ("Interface bridge compatibility package", "runtime-support"),
    "Aetherra/lyrixa/": ("Lyrixa persona and plugin package", "runtime"),
    "Aetherra/lyrixa_plugins/": ("Lyrixa plugin compatibility package", "plugin-runtime"),
    "Aetherra/observability/": ("Observability and metrics package", "runtime-support"),
    "Aetherra/perception_bus/": ("Perception bus package", "runtime"),
    "Aetherra/quantum/": ("Quantum integration compatibility package", "runtime"),
    "Aetherra/runtime/": ("Aether Script runtime package", "runtime"),
    "Aetherra/runtime_ui/": ("Runtime UI contract and payload package", "runtime-ui"),
    "Aetherra/schedulers/": ("Runtime schedulers", "runtime"),
    "Aetherra/safety_envelope/": ("Safety policy envelope", "runtime"),
    "Aetherra/memory/": ("Memory compatibility package", "runtime"),
    "Aetherra/runners/": ("Runtime runner entrypoints", "runtime"),
    "Aetherra/stdlib/": ("Aether Script standard library", "runtime"),
    "Aetherra/telemetry/": ("Telemetry opt-in package", "runtime-support"),
    "Aetherra/utils/": ("Runtime utility package", "runtime-support"),
    "Aetherra/web/": ("Web adapter compatibility package", "runtime-support"),
    "aetherra_hub/": ("Hub API and service layer", "runtime-api"),
    "aetherra_coding/": ("Coding system operations", "governed-runtime"),
    "lyrixa/": ("Lyrixa import compatibility shim", "runtime-support"),
    "cli/": ("Command-line interfaces", "operator"),
    "plugins/": ("Plugin examples/catalog support", "plugin-runtime"),
    "Aetherra/plugins/": ("Plugin runtime package", "plugin-runtime"),
    "Aetherra/lyrixa/gui/src/": ("Runtime UI source", "runtime-ui"),
}

CONFIRMED_RUNTIME_PREFIXES = {
    "Aetherra/guardian/",
    "Aetherra/security/",
    "aetherra_hub/",
}

REVIEW_OVERRIDES = {
    "beyond_transcendence_engine.py": (
        "rename-debt",
        "Legacy advanced cognition compatibility shim; retain until professionally renamed",
        "keep-rename",
    ),
}

CONFIG_PREFIXES = {
    ".devcontainer/": "Developer container configuration",
    ".github/": "GitHub workflows and repository automation",
    ".githooks/": "Git hook support",
    ".vscode/": "Workspace task configuration",
    "config/": "Configuration files",
    "configs/": "Configuration files",
    "requirements/": "Dependency requirements",
    "schema_validators/": "Schema validation support",
    "Aetherra/config/": "Aetherra package configuration",
    "Aetherra/pyproject.toml": "Aetherra package configuration",
    "Aetherra/lyrixa/gui/": "Runtime UI package/build configuration",
}

TEST_PREFIXES = {
    "tests/": "Automated tests and probes",
}

DOC_PREFIXES = {
    "docs/": "Active documentation",
    "docs-organized/": "Historical/thematic documentation",
    "documentation/": "Documentation compatibility folder",
    "metadata/": "Project metadata",
    "Aetherra/docs/": "Legacy package documentation",
}

TOOL_PREFIXES = {
    "tools/": "Developer and maintenance tooling",
    "scripts/": "Automation scripts",
    "toolshed/": "Tool support",
    "demos/": "Demonstrations",
    "examples/": "Examples",
    "development/": "Development support",
    "ISSUE_TEMPLATE/": "Issue template compatibility folder",
    "badge/": "Badge metadata",
    "metrics/": "Metrics support assets",
    "Aetherra/scripts/": "Aetherra package maintenance scripts",
    "Aetherra/tools/": "Aetherra package tools",
}

LEGACY_PREFIXES = {
    "archive/": "Archived historical material",
}

REVIEW_ROOT_FILES = {
    "aetherra_adaptive_behavior.py",
    "aetherra_cognitive_task_manager.py",
    "aetherra_live_monitor.py",
    "aetherra_meta_memory.py",
    "aetherra_plugin_catalog.json",
    "aetherra_plugin_viewer.py",
    "aetherra_quantum_meta_learning.py",
    "beyond_transcendence_engine.py",
    "copyright_header.py",
    "intelligence_report_generator.py",
    "launch_aetherra_unicode.py",
    "licenses_unknown_history.json",
    "licenses_unknown_history.requirements-ci.lock.json",
    "setup_dev.py",
    "test_unicode_workflow_fix.py",
}


def git_ls_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return sorted(line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip())


def first_matching_prefix(path: str, mapping: dict[str, str | tuple[str, str]]):
    for prefix, value in mapping.items():
        if path.startswith(prefix):
            return prefix, value
    return None, None


def classify(path: str) -> FileRecord:
    if path in REVIEW_OVERRIDES:
        category, purpose, keep_status = REVIEW_OVERRIDES[path]
        return FileRecord(path, category, "unknown-or-compatibility", "review", purpose, keep_status)

    if path in OPERATIONAL_ROOT_FILES:
        purpose, lifecycle = OPERATIONAL_ROOT_FILES[path]
        return FileRecord(path, "operational-runtime", lifecycle, "runtime", purpose, "keep")

    prefix, value = first_matching_prefix(path, RUNTIME_PREFIXES)
    if prefix and isinstance(value, tuple):
        purpose, lifecycle = value
        keep_status = "keep" if prefix in CONFIRMED_RUNTIME_PREFIXES else "provisional-runtime"
        return FileRecord(path, "operational-runtime", lifecycle, prefix.rstrip("/"), purpose, keep_status)

    prefix, purpose = first_matching_prefix(path, TEST_PREFIXES)
    if prefix:
        return FileRecord(path, "test", "verification", prefix.rstrip("/"), str(purpose), "review-by-suite")

    prefix, purpose = first_matching_prefix(path, DOC_PREFIXES)
    if prefix:
        status = "keep" if path.startswith("docs/AETHERRA_") or path.startswith("docs/MASTER_") else "review-doc"
        return FileRecord(path, "documentation", "documentation", prefix.rstrip("/"), str(purpose), status)

    prefix, purpose = first_matching_prefix(path, CONFIG_PREFIXES)
    if prefix:
        return FileRecord(path, "configuration", "build-or-ci", prefix.rstrip("/"), str(purpose), "keep")

    if path in CONFIG_ROOT_FILES:
        return FileRecord(path, "configuration", "build-or-ci", "repo-root", "Repository configuration", "keep")

    if path in PUBLIC_DOC_ROOT_FILES:
        return FileRecord(path, "documentation", "documentation", "repo-root", "Public project documentation", "keep")

    prefix, purpose = first_matching_prefix(path, TOOL_PREFIXES)
    if prefix:
        return FileRecord(path, "tooling", "maintenance", prefix.rstrip("/"), str(purpose), "review-tool")

    prefix, purpose = first_matching_prefix(path, LEGACY_PREFIXES)
    if prefix:
        return FileRecord(path, "legacy-or-archive", "historical", prefix.rstrip("/"), str(purpose), "candidate-review")

    if path in REVIEW_ROOT_FILES:
        return FileRecord(
            path,
            "root-review-candidate",
            "unknown-or-compatibility",
            "repo-root",
            "Root-level compatibility, legacy, or unverified operational file",
            "needs-evidence",
        )

    return FileRecord(
        path,
        "unclassified",
        "unknown",
        "unknown",
        "No current classification rule matched this tracked file",
        "needs-review",
    )


def directory_records(files: Iterable[FileRecord]) -> list[dict[str, object]]:
    direct_files: dict[str, list[FileRecord]] = defaultdict(list)
    descendants: dict[str, list[FileRecord]] = defaultdict(list)
    for record in files:
        parts = record.path.split("/")
        for index in range(1, len(parts)):
            directory = "/".join(parts[:index])
            descendants[directory].append(record)
        if len(parts) > 1:
            direct_files["/".join(parts[:-1])].append(record)

    records = []
    for directory, members in sorted(descendants.items()):
        category = Counter(member.category for member in members).most_common(1)[0][0]
        keep_status = Counter(member.keep_status for member in members).most_common(1)[0][0]
        records.append(
            {
                "path": directory + "/",
                "file_count": len(members),
                "direct_file_count": len(direct_files.get(directory, [])),
                "dominant_category": category,
                "dominant_keep_status": keep_status,
            }
        )
    return records


def path_lines(records: list[FileRecord], category: str, limit: int = 80) -> list[str]:
    selected = [record for record in records if record.category == category]
    lines = []
    for record in selected[:limit]:
        lines.append(f"- `{record.path}` - {record.purpose} ({record.lifecycle}; {record.keep_status})")
    if len(selected) > limit:
        lines.append(f"- ... {len(selected) - limit} more in `docs/AETHERRA_FILE_MANIFEST.json`")
    return lines


def build_markdown(files: list[FileRecord], dirs: list[dict[str, object]]) -> str:
    category_counts = Counter(record.category for record in files)
    status_counts = Counter(record.keep_status for record in files)
    lifecycle_counts = Counter(record.lifecycle for record in files)
    today = date.today().isoformat()

    top_dirs = []
    for entry in dirs:
        if "/" not in str(entry["path"]).rstrip("/"):
            top_dirs.append(entry)

    stale_candidates = [
        record
        for record in files
        if record.keep_status
        in {"candidate-review", "needs-evidence", "needs-review", "provisional-runtime"}
    ]

    lines = [
        "# Aetherra Master Map",
        "",
        f"Updated: {today}",
        "",
        "This is the operational map for the Aetherra repository. It is generated",
        "from tracked files and is paired with `docs/AETHERRA_FILE_MANIFEST.json`,",
        "which contains the per-file and per-directory inventory.",
        "",
        "## Rule",
        "",
        "A file is treated as required only when it has evidence that it participates",
        "in boot, runtime, governance, security, UI, plugin operation, configuration,",
        "documentation, tooling, or verification. Files without that evidence are",
        "marked for review before removal.",
        "",
        "## Current Inventory",
        "",
        f"- Tracked files: {len(files)}",
        f"- Tracked directories: {len(dirs)}",
        f"- Files confirmed keep: {status_counts.get('keep', 0)}",
        f"- Files requiring suite/doc/tool/provisional review: {len(files) - status_counts.get('keep', 0)}",
        f"- Runtime/candidate/unknown files needing evidence: {len(stale_candidates)}",
        "",
        "### By Category",
        "",
    ]

    for category, count in sorted(category_counts.items()):
        lines.append(f"- {category}: {count}")

    lines.extend(["", "### By Lifecycle", ""])
    for lifecycle, count in sorted(lifecycle_counts.items()):
        lines.append(f"- {lifecycle}: {count}")

    lines.extend(["", "## Top-Level Folder Map", ""])
    lines.append("| Folder | Files | Category | Status |")
    lines.append("| --- | ---: | --- | --- |")
    for entry in sorted(top_dirs, key=lambda item: (-int(item["file_count"]), str(item["path"]))):
        lines.append(
            f"| `{entry['path']}` | {entry['file_count']} | "
            f"{entry['dominant_category']} | {entry['dominant_keep_status']} |"
        )

    lines.extend(
        [
            "",
            "## Operational Runtime Files",
            "",
            "These are files currently classified as directly involved in boot,",
            "runtime, governed runtime, API operation, plugin operation, or Runtime UI.",
            "",
        ]
    )
    lines.extend(path_lines(files, "operational-runtime", limit=120))

    lines.extend(
        [
            "",
            "## Configuration And Build Files",
            "",
        ]
    )
    lines.extend(path_lines(files, "configuration", limit=80))

    lines.extend(
        [
            "",
            "## Verification Surface",
            "",
            "Tests are not runtime files, but they are required until each suite is",
            "mapped to a current system, replaced, or intentionally retired.",
            "",
        ]
    )
    lines.extend(path_lines(files, "test", limit=80))

    lines.extend(
        [
            "",
            "## Documentation Surface",
            "",
            "Documentation is retained when it is active, architectural, legal,",
            "operator-facing, or historical material that still explains project context.",
            "",
        ]
    )
    lines.extend(path_lines(files, "documentation", limit=80))

    lines.extend(
        [
            "",
            "## Review Queues",
            "",
            "These files are not deleted by the generator. They are the starting point",
            "for manual evidence review and later removal PRs. `provisional-runtime`",
            "means the file lives under an operational package, but this pass has not",
            "yet proven direct active use.",
            "",
            "### Root Or Unknown Candidates",
            "",
        ]
    )
    for record in stale_candidates[:120]:
        lines.append(f"- `{record.path}` - {record.keep_status}; {record.purpose}")
    if len(stale_candidates) > 120:
        lines.append(f"- ... {len(stale_candidates) - 120} more in `docs/AETHERRA_FILE_MANIFEST.json`")

    lines.extend(
        [
            "",
            "## Cleanup Process",
            "",
            "1. Pick one review queue from `docs/AETHERRA_FILE_MANIFEST.json`.",
            "2. Prove each file is imported, executed, documented as active, or unused.",
            "3. Keep active files and update their owner/purpose if needed.",
            "4. Remove unused files in small commits with verification.",
            "5. Regenerate this map after every cleanup pass.",
            "",
            "## Regeneration",
            "",
            "```powershell",
            "python tools\\generate_master_map.py",
            "```",
            "",
            "<!-- SPDX-License-Identifier: GPL-3.0-or-later -->",
            "<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    paths = git_ls_files()
    records = [classify(path) for path in paths]
    dirs = directory_records(records)

    manifest = {
        "generated_on": date.today().isoformat(),
        "tracked_file_count": len(records),
        "tracked_directory_count": len(dirs),
        "categories": dict(sorted(Counter(record.category for record in records).items())),
        "keep_status": dict(sorted(Counter(record.keep_status for record in records).items())),
        "directories": dirs,
        "files": [record.__dict__ for record in records],
    }

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MASTER_MAP_PATH.write_text(build_markdown(records, dirs), encoding="utf-8")
    print(f"Wrote {MASTER_MAP_PATH.relative_to(ROOT)}")
    print(f"Wrote {MANIFEST_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
