"""Read-only Homeostasis learning and effectiveness reports."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def build_learning_report(audit_records: list[dict[str, Any]]) -> dict[str, Any]:
    """Correlate Homeostasis Guardian decisions with bounded outcome records."""

    decisions = _homeostasis_decisions(audit_records)
    outcomes = _outcomes_by_decision(audit_records)
    action_stats: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "decisions": 0,
            "outcomes": 0,
            "completed": 0,
            "failed": 0,
            "latest_status": None,
        }
    )

    correlated = []
    for decision in decisions:
        decision_hash = decision.get("hash")
        details = decision.get("details") if isinstance(decision.get("details"), dict) else {}
        intent = details.get("intent") if isinstance(details.get("intent"), dict) else {}
        metadata = intent.get("metadata") if isinstance(intent.get("metadata"), dict) else {}
        action_type = str(metadata.get("action_type") or intent.get("action") or "unknown")
        target_service = str(metadata.get("target_service") or intent.get("target") or "unknown")
        decision_outcomes = outcomes.get(str(decision_hash), [])

        stats = action_stats[action_type]
        stats["decisions"] += 1
        stats["outcomes"] += len(decision_outcomes)

        latest_status = None
        if decision_outcomes:
            latest = decision_outcomes[-1]
            outcome_details = latest.get("details") if isinstance(latest.get("details"), dict) else {}
            outcome = (
                outcome_details.get("outcome")
                if isinstance(outcome_details.get("outcome"), dict)
                else {}
            )
            latest_status = str(outcome.get("status") or "unspecified")
            stats["latest_status"] = latest_status
            if latest_status == "completed":
                stats["completed"] += 1
            elif latest_status == "failed":
                stats["failed"] += 1

        correlated.append(
            {
                "decision_audit_id": decision_hash,
                "timestamp": decision.get("timestamp"),
                "action_type": action_type,
                "target_service": target_service,
                "guardian_status": (details.get("decision") or {}).get("status")
                if isinstance(details.get("decision"), dict)
                else None,
                "outcome_count": len(decision_outcomes),
                "latest_outcome_status": latest_status,
            }
        )

    total_outcomes = sum(item["outcomes"] for item in action_stats.values())
    completed = sum(item["completed"] for item in action_stats.values())
    failed = sum(item["failed"] for item in action_stats.values())
    success_rate = completed / total_outcomes if total_outcomes else None

    return {
        "phase": "learning",
        "actions_enabled": False,
        "summary": {
            "decision_count": len(decisions),
            "outcome_count": total_outcomes,
            "completed": completed,
            "failed": failed,
            "success_rate": success_rate,
        },
        "action_effectiveness": dict(sorted(action_stats.items())),
        "correlations": correlated[-50:],
    }


def _homeostasis_decisions(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    decisions = []
    for record in records:
        if record.get("event_type") != "guardian_decision":
            continue
        details = record.get("details") if isinstance(record.get("details"), dict) else {}
        intent = details.get("intent") if isinstance(details.get("intent"), dict) else {}
        if intent.get("subsystem") == "homeostasis":
            decisions.append(record)
    return decisions


def _outcomes_by_decision(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    outcomes: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        if record.get("event_type") != "guardian_outcome":
            continue
        details = record.get("details") if isinstance(record.get("details"), dict) else {}
        decision_id = details.get("decision_audit_id")
        if isinstance(decision_id, str) and decision_id:
            outcomes[decision_id].append(record)
    return outcomes
