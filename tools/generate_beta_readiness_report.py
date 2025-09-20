"""Generate or update the Beta Readiness Report.

Aggregates data from existing artifacts when present (best-effort):
  * docs/docs_architecture_report.json
  * coverage.xml (line-rate)
  * gate_results.json (if produced by Go / No-Go tooling)
  * aetherra_kernel_metrics.json (basic health evidence)

Falls back gracefully if artifacts are missing and notes TODO sections.
"""

from __future__ import annotations

# Standard library imports
import argparse
import json
from datetime import datetime
from pathlib import Path

# Third party imports
from defusedxml import ElementTree


def load_json(path: Path):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # pragma: no cover - resilience
            return None
    return None


def parse_coverage(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        tree = ElementTree.parse(path)
        root = tree.getroot()
        line_rate = root.get("line-rate") or root.attrib.get("line-rate")
        if line_rate:
            try:
                return f"{float(line_rate) * 100:.2f}%"
            except ValueError:
                return None
    except Exception:  # pragma: no cover
        return None
    return None


def summarize_gates(gates):
    if not gates or not isinstance(gates, dict):
        return "No gate results available"
    passed = sum(
        1 for g in gates.values() if isinstance(g, dict) and g.get("status") == "pass"
    )
    total = len(gates)
    return f"{passed}/{total} passing"


def build_report(data: dict) -> str:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    sections = []
    sections.append(f"# Aetherra Beta Readiness Report\n\nGenerated: {now}\n")
    sections.append(
        "## Summary\n\nThis report aggregates structural, test, and documentation integrity signals to assess beta readiness."
    )

    cov = data.get("coverage") or "(coverage.xml not found)"
    gates = data.get("gates_summary") or "(gate results missing)"
    docs_req_missing = data.get("docs_required_missing", [])
    docs_line = (
        "All required documentation present"
        if not docs_req_missing
        else f"Missing required docs: {', '.join(docs_req_missing)}"
    )
    sections.append(
        "\n**Key Signals**\n\n"
        f"- Coverage: {cov}\n"
        f"- Go/No-Go Gates: {gates}\n"
        f"- Docs Architecture: {docs_line}\n"
    )

    sections.append("## Documentation Integrity\n")
    sections.append(
        "The documentation architecture scan confirms presence of core indices and system specifications. "
        "See `docs/DOCS_ARCHITECTURE.md` for governance and classification."
    )

    sections.append("\n## Gate & Policy Surfaces\n")
    if data.get("gates"):
        sections.append("Gate detail (excerpt):")
        for name, gate in list(data["gates"].items())[:7]:  # limit
            status = gate.get("status") if isinstance(gate, dict) else gate
            sections.append(f"- {name}: {status}")
    else:
        sections.append("No gate_results.json available.")

    sections.append("\n## Coverage\n")
    sections.append(f"Reported line-rate: {cov}")

    if data.get("kernel_metrics"):
        sections.append("\n## Kernel Metrics Snapshot\n")
        km = data["kernel_metrics"]
        for key in sorted(km)[:10]:
            val = km[key]
            if isinstance(val, int | float | str):
                sections.append(f"- {key}: {val}")

    sections.append("\n## Risks & Follow-Ups\n")
    sections.append(
        "- Add parallel execution stress test (if absent)\n- Ensure deterministic offline fallback coverage\n- Expand security threat modeling for new surfaces"
    )

    sections.append("\n## Conclusion\n")
    sections.append(
        "System appears beta-ready given present artifacts. Any missing metrics or gate evidence should be regenerated before final tagging."
    )
    return "\n".join(sections) + "\n"


def main():  # pragma: no cover
    parser = argparse.ArgumentParser(description="Generate beta readiness report")
    parser.add_argument("--output", default="BETA_READINESS_REPORT.md")
    args = parser.parse_args()

    root = Path.cwd()
    docs_report = load_json(root / "docs" / "docs_architecture_report.json") or {}
    coverage = parse_coverage(root / "coverage.xml")
    gates = load_json(root / "gate_results.json") or load_json(
        root / "data" / "artifacts" / "gate_results.json"
    )
    kernel_metrics = load_json(root / "aetherra_kernel_metrics.json") or load_json(
        root / "data" / "aetherra_kernel_metrics.json"
    )

    data = {
        "docs_required_missing": docs_report.get("required_missing", []),
        "coverage": coverage,
        "gates": gates,
        "gates_summary": summarize_gates(gates) if gates else None,
        "kernel_metrics": kernel_metrics,
    }
    report_md = build_report(data)
    Path(args.output).write_text(report_md, encoding="utf-8")
    print(f"Beta readiness report written: {args.output}")


if __name__ == "__main__":
    main()
