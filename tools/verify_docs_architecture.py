"""Verify documentation architecture structure and required files.

This tool validates the presence and classification of required documentation
artifacts described in `docs/DOCS_ARCHITECTURE.md`.

It emits a JSON report summarizing findings and (optionally) exits non-zero
in strict mode if required files are missing.
"""

from __future__ import annotations

# Standard library imports
import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

REQUIRED_DOCS: dict[str, str] = {
    "docs/INDEX.md": "Canonical index",
    "docs/SYSTEM_INDEX.md": "System status dashboard",
    "docs/Aether_Script_Language_System.md": "Language spec",
    "docs/AETHERRA_MEMORY_SYSTEM.md": "Memory system spec",
    "docs/RELEASE_PROCESS.md": "Release process policy",
    "docs/THREAT_MODEL.md": "Threat model",
    "docs/COVERAGE_POLICY.md": "Coverage policy",
    "docs/GO_NO_GO_GATES.md": "Gating model",
}

OPTIONAL_DOCS: dict[str, str] = {
    "docs/DOCS_ARCHITECTURE.md": "Architecture governance",
    "docs/AETHERRA_SECURITY_SYSTEM.md": "Security system spec",
    "docs/AETHERRA_AGENT_SYSTEM.md": "Agent system spec",
    "docs/AETHERRA_CODING_SYSTEM.md": "Coding system spec",
    "docs/AETHERRA_LYRIXA_SYSTEM.md": "Lyrixa system spec",
    "docs/AETHERRA_CHAT_SYSTEM.md": "Chat system spec",
    "docs/AETHERRA_AI_TRAINER_SYSTEM.md": "AI trainer system (planned)",
}

REPORT_PATH = Path("docs/docs_architecture_report.json")


@dataclass
class DocStatus:
    path: str
    required: bool
    exists: bool
    note: str


@dataclass
class ArchitectureReport:
    root: str
    total_docs_found: int
    required_missing: list[str]
    statuses: list[DocStatus]
    docs_organized_present: bool
    documentation_dir_present: bool

    def to_json(self) -> str:
        return json.dumps(
            {
                "root": self.root,
                "total_docs_found": self.total_docs_found,
                "required_missing": self.required_missing,
                "statuses": [asdict(s) for s in self.statuses],
                "docs_organized_present": self.docs_organized_present,
                "documentation_dir_present": self.documentation_dir_present,
            },
            indent=2,
        )


def scan_all_markdown(root: Path) -> set[Path]:
    return {p for p in root.rglob("*.md") if ".venv" not in p.parts}


def build_report(root: Path) -> ArchitectureReport:
    md_files = scan_all_markdown(root)
    md_rel = {str(p.relative_to(root)).replace("\\", "/") for p in md_files}

    statuses: list[DocStatus] = []
    required_missing: list[str] = []

    for path, note in REQUIRED_DOCS.items():
        exists = path in md_rel
        if not exists:
            required_missing.append(path)
        statuses.append(DocStatus(path=path, required=True, exists=exists, note=note))

    for path, note in OPTIONAL_DOCS.items():
        exists = path in md_rel
        statuses.append(DocStatus(path=path, required=False, exists=exists, note=note))

    return ArchitectureReport(
        root=str(root),
        total_docs_found=len(md_rel),
        required_missing=required_missing,
        statuses=statuses,
        docs_organized_present=(root / "docs-organized").exists(),
        documentation_dir_present=(root / "documentation").exists(),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate documentation architecture completeness"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if required docs are missing",
    )
    parser.add_argument(
        "--output",
        default=str(REPORT_PATH),
        help="Path to write JSON report (default: docs/docs_architecture_report.json)",
    )
    args = parser.parse_args(argv)

    root = Path.cwd()
    report = build_report(root)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report.to_json(), encoding="utf-8")

    print(f"Documentation architecture report written to: {out_path}")
    if report.required_missing:
        print("Missing required documents:")
        for m in report.required_missing:
            print(f"  - {m}")
        if args.strict:
            print("Strict mode: failing due to missing required docs.")
            return 1
    else:
        print("All required documents present ✅")

    return 0


if __name__ == "main":  # pragma: no cover (defensive)
    sys.exit(main())

# NOTE: correct Python entrypoint guard below
if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
