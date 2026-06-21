#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧬 Aetherra Self-Incorporation System
=====================================

Autonomous codebase perception, understanding, and incorporation system.
Enables Aetherra OS to discover, analyze, and safely integrate its entire
codebase at boot and over time, realizing the Synthesis vision of a
Self-Hosting Cognitive Organism.

Core Subsystems:
1. Code Discovery & Indexing
2. Heuristic Classifier
3. Policy & Safety Gate
4. Integration Planner
5. Core Integrator
6. Ethics & Audit Ledger
7. Hot-Swap & Rollback (HMR)
"""

# Standard library imports
import asyncio
import contextlib
import hashlib
import json
import logging
import os
import sqlite3
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

# Aetherra imports (lazy-loaded to avoid circular dependencies)
# Security layer imported at service initialization

logger = logging.getLogger(__name__)


@dataclass
class UserActivity:
    """Track user activity patterns for night cycle scheduling."""

    last_interaction: datetime = field(default_factory=datetime.now)
    interaction_count: int = 0
    active_processes: int = 0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    network_activity: bool = False

    def is_idle(self, idle_threshold_minutes: int = 30) -> bool:
        """Check if user has been idle for the threshold duration."""
        idle_duration = datetime.now() - self.last_interaction
        return idle_duration.total_seconds() > (idle_threshold_minutes * 60)

    def is_low_resource_usage(self) -> bool:
        """Check if system resource usage is low enough for night cycle."""
        return self.cpu_usage < 20.0 and self.memory_usage < 70.0


@dataclass
class NightCycleMetrics:
    """Metrics for night cycle learning and adaptation."""

    cycle_start: datetime
    cycle_end: datetime | None = None
    discoveries_processed: int = 0
    patterns_learned: int = 0
    optimizations_applied: int = 0
    errors_resolved: int = 0
    performance_improvements: float = 0.0
    quality_score: float = 0.0
    insights_generated: list[str] = field(default_factory=list)


@dataclass
class LearningInsight:
    """Represents a learned insight from night cycle analysis."""

    insight_id: str
    category: str  # "performance", "security", "quality", "pattern"
    description: str
    confidence: float  # 0.0 to 1.0
    evidence: list[dict[str, Any]] = field(default_factory=list)
    suggested_actions: list[str] = field(default_factory=list)
    priority: str = "normal"  # high, normal, low
    timestamp: datetime = field(default_factory=datetime.now)


class NightCyclePhase(Enum):
    """Phases of the night cycle processing."""

    INACTIVE = "inactive"
    MONITORING = "monitoring"  # Watching for night cycle opportunity
    DISCOVERY_ANALYSIS = "discovery_analysis"  # Analyzing recent discoveries
    PATTERN_LEARNING = "pattern_learning"  # Learning from historical data
    OPTIMIZATION = "optimization"  # Applying optimizations
    VALIDATION = "validation"  # Validating changes
    REPORTING = "reporting"  # Generating insights report


class TrustTier(Enum):
    """Trust levels for discovered code items."""

    VERIFIED = "verified"
    TRUSTED = "trusted"
    STANDARD = "standard"
    EXPERIMENTAL = "experimental"
    QUARANTINED = "quarantined"


class ItemType(Enum):
    """Types of discoverable code items."""

    UNKNOWN = "unknown"
    PLUGIN = "plugin"
    AGENT = "agent"
    AETHER = "aether"
    WORKFLOW = "workflow"
    UTILITY = "utility"
    DATASET = "dataset"
    DOCS = "docs"


class ServiceStatus(Enum):
    """Service operational status."""

    STARTING = "starting"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    STOPPING = "stopping"


@dataclass
class FileItem:
    """Core data structure for discovered files."""

    id: str  # sha256 hash
    path: str
    hash: str
    size: int
    mtime: float
    type: ItemType = ItemType.UNKNOWN
    language: str = "other"
    entrypoints: list[str] = field(default_factory=list)
    discovered_at: datetime = field(default_factory=datetime.now)


@dataclass
class ClassificationResult:
    """Result of file classification analysis."""

    file_id: str
    type: ItemType
    declared_capabilities: list[str] = field(default_factory=list)
    requires: list[str] = field(default_factory=list)
    risk_hints: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0


@dataclass
class SafetyDecision:
    """Security and safety evaluation result."""

    file_id: str
    verified: bool = False
    signing: dict[str, Any] = field(default_factory=dict)
    scans: dict[str, str] = field(default_factory=dict)
    capability_ok: bool = False
    trust_tier: TrustTier = TrustTier.EXPERIMENTAL
    reasons: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PlanAction:
    """Integration action to be executed."""

    action: str  # register_plugin, register_agent, etc.
    target: dict[str, Any] = field(default_factory=dict)
    deps: list[str] = field(default_factory=list)
    priority: str = "normal"  # high, normal, background
    created_at: datetime = field(default_factory=datetime.now)


class EthicsProfile(Enum):
    """Ethical reasoning frameworks for decision evaluation."""

    UTILITARIAN = "utilitarian"  # Maximize overall benefit/harm ratio
    DEONTOLOGICAL = "deontological"  # Rule-based, duty-oriented ethics
    VIRTUE = "virtue"  # Character and virtue-based ethics
    CARE = "care"  # Relationship and care-oriented ethics


@dataclass
class EthicsScore:
    """Ethical evaluation score for an integration decision."""

    overall_score: float  # 0.0 to 1.0, higher is more ethical
    utilitarian_score: float = 0.0  # Benefit vs harm analysis
    deontological_score: float = 0.0  # Rule compliance score
    virtue_score: float = 0.0  # Character/virtue alignment
    care_score: float = 0.0  # Care/relationship impact
    confidence: float = 0.0  # 0.0 to 1.0, confidence in evaluation
    reasoning: list[str] = field(default_factory=list)  # Human-readable reasoning
    risk_factors: list[str] = field(default_factory=list)  # Identified risks
    ethical_benefits: list[str] = field(default_factory=list)  # Identified benefits


class EthicsEngine:
    """
    Evaluates integration decisions against ethical frameworks.

    Provides multi-dimensional ethical analysis combining utilitarian,
    deontological, virtue ethics, and care ethics perspectives.
    """

    def __init__(self, config: "SelfIncorporationConfig"):
        self.config = config
        self.profile_weights = self._load_ethics_profile()

    def _load_ethics_profile(self) -> dict[str, float]:
        """Load ethical profile weights from configuration."""
        # Default balanced profile
        default_weights = {
            "utilitarian": 0.4,  # Moderate focus on outcomes
            "deontological": 0.3,  # Moderate focus on rules/duties
            "virtue": 0.2,  # Some focus on character
            "care": 0.1,  # Some focus on relationships
        }

        # TODO: Load from policy files or environment
        profile_env = os.getenv("AETHERRA_ETHICS_PROFILE", "balanced")

        profiles = {
            "strict": {
                "utilitarian": 0.2,
                "deontological": 0.6,
                "virtue": 0.1,
                "care": 0.1,
            },
            "consequentialist": {
                "utilitarian": 0.7,
                "deontological": 0.1,
                "virtue": 0.1,
                "care": 0.1,
            },
            "virtue_focused": {
                "utilitarian": 0.2,
                "deontological": 0.2,
                "virtue": 0.4,
                "care": 0.2,
            },
        }

        return profiles.get(profile_env, default_weights)

    def evaluate_integration(
        self,
        action: str,
        target: dict[str, Any],
        safety_decision: "SafetyDecision | None" = None,
    ) -> EthicsScore:
        """
        Evaluate an integration decision from multiple ethical perspectives.
        """
        reasoning: list[str] = []
        risk_factors: list[str] = []
        ethical_benefits: list[str] = []

        # Utilitarian Analysis: Maximize benefit, minimize harm
        utilitarian_score = self._evaluate_utilitarian(
            action, target, safety_decision, reasoning, risk_factors, ethical_benefits
        )

        # Deontological Analysis: Rule-based compliance
        deontological_score = self._evaluate_deontological(
            action, target, safety_decision, reasoning, risk_factors, ethical_benefits
        )

        # Virtue Ethics Analysis: Character and excellence
        virtue_score = self._evaluate_virtue(
            action, target, safety_decision, reasoning, risk_factors, ethical_benefits
        )

        # Care Ethics Analysis: Relationships and care
        care_score = self._evaluate_care(
            action, target, safety_decision, reasoning, risk_factors, ethical_benefits
        )

        # Calculate weighted overall score
        overall_score = (
            utilitarian_score * self.profile_weights["utilitarian"]
            + deontological_score * self.profile_weights["deontological"]
            + virtue_score * self.profile_weights["virtue"]
            + care_score * self.profile_weights["care"]
        )

        # Calculate confidence based on agreement between frameworks
        scores = [utilitarian_score, deontological_score, virtue_score, care_score]
        score_variance = sum((s - overall_score) ** 2 for s in scores) / len(scores)
        confidence = max(
            0.0, 1.0 - (score_variance * 2)
        )  # Higher variance = lower confidence

        return EthicsScore(
            overall_score=overall_score,
            utilitarian_score=utilitarian_score,
            deontological_score=deontological_score,
            virtue_score=virtue_score,
            care_score=care_score,
            confidence=confidence,
            reasoning=reasoning,
            risk_factors=risk_factors,
            ethical_benefits=ethical_benefits,
        )

    def _evaluate_utilitarian(
        self,
        action: str,
        target: dict[str, Any],
        safety_decision: "SafetyDecision | None",
        reasoning: list[str],
        risk_factors: list[str],
        ethical_benefits: list[str],
    ) -> float:
        """Evaluate from utilitarian perspective: maximize overall good."""
        score = 0.5  # Neutral baseline

        # Benefits analysis
        if action in ["register_plugin", "register_agent"]:
            score += 0.2
            ethical_benefits.append("Extends system capabilities")
            reasoning.append("UTIL: Plugin/agent registration increases system utility")

        if action in ["load_aether_script", "expose_tool"]:
            score += 0.15
            ethical_benefits.append("Enables new functionality")
            reasoning.append("UTIL: New functionality provides user benefit")

        # Risk analysis from safety decision
        if safety_decision:
            trust_tier = safety_decision.trust_tier
            if trust_tier == TrustTier.VERIFIED:
                score += 0.2
                reasoning.append("UTIL: Verified code minimizes harm risk")
            elif trust_tier == TrustTier.TRUSTED:
                score += 0.1
                reasoning.append("UTIL: Trusted code has acceptable risk")
            elif trust_tier == TrustTier.QUARANTINED:
                score -= 0.3
                risk_factors.append("High risk of system harm")
                reasoning.append("UTIL: Quarantined code poses significant harm risk")

        # Capability escalation concerns
        capabilities = target.get("declared_capabilities", [])
        caps_str = str(capabilities)
        has_network = "network" in caps_str
        has_exec_like = ("exec" in caps_str) or ("filesystem" in caps_str)
        if has_network:
            score -= 0.1
            risk_factors.append("Network access capability")
            reasoning.append("UTIL: Network access increases potential for harm")

        if has_exec_like:
            score -= 0.15
            risk_factors.append("System access capability")
            reasoning.append("UTIL: System access capabilities increase harm potential")

        # Dangerous combination penalty: network + exec/filesystem
        if has_network and has_exec_like:
            score -= 0.3
            risk_factors.append(
                "Dangerous capability combination: network + exec/filesystem"
            )
            reasoning.append(
                "UTIL: Combined network and system access substantially raises harm risk"
            )

        # Complexity consideration: higher complexity slightly reduces utilitarian score
        complexity_score = float(target.get("complexity_score", 0) or 0)
        if complexity_score >= 0.6:
            score -= 0.15
            risk_factors.append("High complexity increases risk")
            reasoning.append("UTIL: Higher complexity elevates likelihood of harm")

        return max(0.0, min(1.0, score))

    def _evaluate_deontological(
        self,
        action: str,
        target: dict[str, Any],
        safety_decision: "SafetyDecision | None",
        reasoning: list[str],
        risk_factors: list[str],
        ethical_benefits: list[str],
    ) -> float:
        """Evaluate from deontological perspective: rule and duty compliance."""
        score = 0.5  # Neutral baseline

        # Rule compliance (signatures, policies)
        if safety_decision:
            if safety_decision.verified and safety_decision.signing.get("ok"):
                score += 0.3
                ethical_benefits.append("Proper signature verification")
                reasoning.append("DEONT: Follows verification duties")
            elif not safety_decision.verified:
                score -= 0.2
                risk_factors.append("Unsigned code violates verification rules")
                reasoning.append("DEONT: Violates signature verification duty")

            if safety_decision.capability_ok:
                score += 0.2
                reasoning.append("DEONT: Respects capability authorization rules")
            else:
                score -= 0.3
                risk_factors.append("Unauthorized capability escalation")
                reasoning.append("DEONT: Violates capability authorization rules")

        # Duty to user consent and transparency
        if action in ["register_plugin", "register_agent"]:
            score += 0.1
            reasoning.append("DEONT: Transparent system modification")

        # Duty to system integrity
        trust_tier = getattr(safety_decision, "trust_tier", TrustTier.STANDARD)
        if trust_tier == TrustTier.QUARANTINED:
            score -= 0.4  # Strong deontological objection to risky integration
            risk_factors.append("Violates duty to maintain system integrity")
            reasoning.append("DEONT: Integration violates system integrity duty")

        # Duty to prevent dangerous capability combinations
        caps_str = str(target.get("declared_capabilities", []))
        if ("network" in caps_str) and (
            ("exec" in caps_str) or ("filesystem" in caps_str)
        ):
            score -= 0.2
            risk_factors.append("Policy concern: network + exec/filesystem combination")
            reasoning.append(
                "DEONT: Avoids hazardous combinations that violate safety duties"
            )

        return max(0.0, min(1.0, score))

    def _evaluate_virtue(
        self,
        action: str,
        target: dict[str, Any],
        safety_decision: "SafetyDecision | None",
        reasoning: list[str],
        risk_factors: list[str],
        ethical_benefits: list[str],
    ) -> float:
        """Evaluate from virtue ethics perspective: character and excellence."""
        score = 0.5  # Neutral baseline

        # Virtues: Prudence, Justice, Temperance, Courage, Honesty

        # Prudence: Wise decision-making
        if safety_decision and safety_decision.verified:
            score += 0.2
            ethical_benefits.append("Demonstrates prudent verification")
            reasoning.append("VIRTUE: Shows prudence in verification")

        # Justice: Fair treatment and respect for rights
        capabilities = target.get("declared_capabilities", [])
        if not capabilities or len(capabilities) <= 2:
            score += 0.1
            reasoning.append("VIRTUE: Shows justice in minimal capability requests")

        # Temperance: Moderation and self-restraint
        if action in ["sandbox", "quarantine"]:
            score += 0.15
            ethical_benefits.append("Shows restraint with risky code")
            reasoning.append("VIRTUE: Demonstrates temperance in risk management")

        # Courage: Appropriate risk-taking for growth
        if action in ["register_plugin", "load_aether_script"]:
            score += 0.1
            reasoning.append("VIRTUE: Shows courage in system growth")

        # Honesty: Transparency in decisions
        score += 0.05  # Audit system itself demonstrates honesty
        reasoning.append("VIRTUE: Audit trail demonstrates honesty")

        # Vices: Recklessness, dishonesty
        if safety_decision and safety_decision.trust_tier == TrustTier.QUARANTINED:
            score -= 0.2
            risk_factors.append("Reckless integration of dangerous code")
            reasoning.append("VIRTUE: Reckless to integrate quarantined code")

        return max(0.0, min(1.0, score))

    def _evaluate_care(
        self,
        action: str,
        target: dict[str, Any],
        safety_decision: "SafetyDecision | None",
        reasoning: list[str],
        risk_factors: list[str],
        ethical_benefits: list[str],
    ) -> float:
        """Evaluate from care ethics perspective: relationships and care."""
        score = 0.5  # Neutral baseline

        # Care for users and stakeholders
        if action in ["register_plugin", "expose_tool"]:
            score += 0.2
            ethical_benefits.append("Enhances user experience and capabilities")
            reasoning.append("CARE: Shows care for user needs and growth")

        # Care for system health and longevity
        if safety_decision:
            trust_tier = safety_decision.trust_tier
            if trust_tier in [TrustTier.VERIFIED, TrustTier.TRUSTED]:
                score += 0.15
                reasoning.append("CARE: Shows care for system health")
            elif trust_tier == TrustTier.QUARANTINED:
                score -= 0.3
                risk_factors.append("Endangers system and dependent users")
                reasoning.append("CARE: Fails to care for system and user safety")

        # Care for future generations (sustainability)
        if action in ["index_docs", "audit"]:
            score += 0.1
            ethical_benefits.append("Supports knowledge preservation")
            reasoning.append("CARE: Shows care for future knowledge access")

        # Relational responsibility
        capabilities = target.get("declared_capabilities", [])
        if "memory" in str(capabilities):
            score += 0.05
            reasoning.append("CARE: Memory capabilities can enhance relationships")

        return max(0.0, min(1.0, score))


@dataclass
class AuditRecord:
    """Complete audit trail for integration decisions."""

    trace_id: str
    timestamp: datetime
    action: str
    target: dict[str, Any]
    policy: dict[str, Any] = field(default_factory=dict)
    decision: str = "pending"  # applied, denied, quarantined
    reasons: list[str] = field(default_factory=list)
    rollbacks: dict[str, Any] = field(default_factory=dict)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    ethics_score: EthicsScore | None = None  # Added ethics evaluation


class AuditLedger:
    """Persistent audit ledger for integration actions and night cycle events."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()
        # Simple in-memory cache for recent ethics decisions (most recent first)
        self._recent_ethics: list[dict[str, Any]] = []
        self._recent_limit = 500

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        try:
            # Create table if missing (latest schema)
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_id TEXT,
                    timestamp TEXT,
                    action TEXT,
                    status TEXT,
                    target_json TEXT,
                    result_json TEXT,
                    trace_id TEXT,
                    ethics_overall REAL,
                    risk_level TEXT,
                    prev_hash TEXT,
                    entry_hash TEXT
                )
                """
            )
            # Lightweight migration: ensure required columns exist on legacy DBs
            try:
                cur = conn.execute("PRAGMA table_info(audit_records)")
                cols = {row[1] for row in cur.fetchall()}
                required_cols = {
                    "plan_id": "TEXT",
                    "timestamp": "TEXT",
                    "action": "TEXT",
                    "status": "TEXT",
                    "target_json": "TEXT",
                    "result_json": "TEXT",
                    "trace_id": "TEXT",
                    "ethics_overall": "REAL",
                    "risk_level": "TEXT",
                    "prev_hash": "TEXT",
                    "entry_hash": "TEXT",
                }
                for col, typ in required_cols.items():
                    if col not in cols:
                        conn.execute(
                            f"ALTER TABLE audit_records ADD COLUMN {col} {typ}"
                        )
            except Exception as exc:
                # Best-effort; continue even if PRAGMA/ALTER fails
                logger.debug("[AUDIT_LEDGER][INIT] PRAGMA/ALTER failed: %s", exc)
            # Indexes for faster ethics lookups
            try:
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_audit_trace_id ON audit_records(trace_id)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_audit_ethics ON audit_records(ethics_overall)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_audit_entry_hash ON audit_records(entry_hash)"
                )
            except Exception as exc:
                logger.debug("[AUDIT_LEDGER][INIT] index creation failed: %s", exc)
            conn.commit()
        finally:
            conn.close()

    def append(
        self,
        plan_id: str,
        action: str,
        status: str,
        target: dict[str, Any],
        result: dict[str, Any],
        trace_id: str | None = None,
        ethics_overall: float | None = None,
        risk_level: str | None = None,
    ) -> None:
        rec = {
            "plan_id": plan_id,
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "status": status,
            "target_json": json.dumps(target, default=str),
            "result_json": json.dumps(result, default=str),
            "trace_id": trace_id,
            "ethics_overall": ethics_overall,
            "risk_level": risk_level,
        }
        # Compute immutable hash chain fields
        prev_hash = None
        conn = sqlite3.connect(self.db_path)
        try:
            try:
                cur = conn.execute(
                    "SELECT entry_hash FROM audit_records ORDER BY id DESC LIMIT 1"
                )
                row = cur.fetchone()
                prev_hash = row[0] if row and row[0] else None
            except Exception:
                prev_hash = None
        finally:
            conn.close()

        # Deterministic entry string: use stored JSON strings and include prev_hash
        prev_hash_str = prev_hash or "genesis"
        base = "|".join(
            [
                str(rec["plan_id"]),
                str(rec["timestamp"]),
                str(rec["action"]),
                str(rec["status"]),
                rec["target_json"] or "",
                rec["result_json"] or "",
                str(rec["trace_id"]) if rec["trace_id"] is not None else "",
                str(rec["ethics_overall"]) if rec["ethics_overall"] is not None else "",
                str(rec["risk_level"]) if rec["risk_level"] is not None else "",
                prev_hash_str,
            ]
        )
        import hashlib as _hl

        entry_hash = _hl.sha256(base.encode("utf-8")).hexdigest()
        rec["prev_hash"] = prev_hash_str
        rec["entry_hash"] = entry_hash
        print(
            f"[AUDIT LEDGER][APPEND] db_path={self.db_path} trace_id={trace_id}",
            flush=True,
        )
        conn = sqlite3.connect(self.db_path)
        try:
            try:
                conn.execute(
                    """
                    INSERT INTO audit_records (plan_id, timestamp, action, status, target_json, result_json, trace_id, ethics_overall, risk_level, prev_hash, entry_hash)
                    VALUES (:plan_id, :timestamp, :action, :status, :target_json, :result_json, :trace_id, :ethics_overall, :risk_level, :prev_hash, :entry_hash)
                    """,
                    rec,
                )
                conn.commit()
            except Exception as e:
                # If insert fails (likely due to legacy schema), attempt migration then retry once
                with contextlib.suppress(Exception):
                    conn.rollback()
                try:
                    # Run migration in the same connection
                    cur = conn.execute("PRAGMA table_info(audit_records)")
                    cols = {row[1] for row in cur.fetchall()}
                    missing = []
                    if "ethics_overall" not in cols:
                        missing.append(("ethics_overall", "REAL"))
                    if "risk_level" not in cols:
                        missing.append(("risk_level", "TEXT"))
                    if "target_json" not in cols:
                        missing.append(("target_json", "TEXT"))
                    if "result_json" not in cols:
                        missing.append(("result_json", "TEXT"))
                    if "prev_hash" not in cols:
                        missing.append(("prev_hash", "TEXT"))
                    if "entry_hash" not in cols:
                        missing.append(("entry_hash", "TEXT"))
                    for col, typ in missing:
                        conn.execute(
                            f"ALTER TABLE audit_records ADD COLUMN {col} {typ}"
                        )
                    if missing:
                        conn.commit()
                    # Retry insert once after migration
                    conn.execute(
                        """
                        INSERT INTO audit_records (plan_id, timestamp, action, status, target_json, result_json, trace_id, ethics_overall, risk_level, prev_hash, entry_hash)
                        VALUES (:plan_id, :timestamp, :action, :status, :target_json, :result_json, :trace_id, :ethics_overall, :risk_level, :prev_hash, :entry_hash)
                        """,
                        rec,
                    )
                    conn.commit()
                except Exception as e2:
                    # Give up; leave to caller to handle/debug
                    print(
                        f"[AUDIT LEDGER][APPEND][ERROR] insert failed after migration: {e} then {e2}",
                        flush=True,
                    )
                    raise
            # Instrument: count rows for this trace_id immediately after insert
            cur = conn.execute(
                "SELECT COUNT(*) FROM audit_records WHERE trace_id = ?", (trace_id,)
            )
            row_count = cur.fetchone()[0]
            print(
                f"[AUDIT LEDGER][APPEND] trace_id={trace_id} row_count_after_insert={row_count}",
                flush=True,
            )
        finally:
            conn.close()

        # Maintain in-memory ethics cache if record includes ethics data
        if ethics_overall is not None:
            cache_entry = {
                "plan_id": plan_id,
                "trace_id": trace_id,
                "timestamp": rec["timestamp"],
                "action": action,
                "status": status,
                "target": target,
                "ethics_overall": ethics_overall,
                "risk_level": risk_level,
                "result": result,
            }
            self._recent_ethics.insert(0, cache_entry)
            if len(self._recent_ethics) > self._recent_limit:
                self._recent_ethics.pop()

    def recent(self, limit: int = 100) -> list[dict[str, Any]]:
        """Return most recent audit records, newest first with cache fallback."""
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute(
                "SELECT plan_id, timestamp, action, status, target_json, result_json, trace_id, ethics_overall, risk_level FROM audit_records ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            rows = cur.fetchall()
            if rows:
                return [
                    {
                        "plan_id": row[0],
                        "timestamp": row[1],
                        "action": row[2],
                        "status": row[3],
                        "target": json.loads(row[4]) if row[4] else {},
                        "result": json.loads(row[5]) if row[5] else {},
                        "trace_id": row[6],
                        "ethics_overall": row[7],
                        "risk_level": row[8],
                    }
                    for row in rows
                ]
        finally:
            conn.close()
        # Fallback to in-memory cache if DB returned nothing
        if getattr(self, "_recent_ethics", None):
            print(
                f"[AUDIT LEDGER][RECENT][CACHE] returning {min(len(self._recent_ethics), limit)} entries",
                flush=True,
            )
            return [
                {
                    "plan_id": it.get("plan_id"),
                    "timestamp": it.get("timestamp"),
                    "action": it.get("action"),
                    "status": it.get("status"),
                    "target": it.get("target") or {},
                    "result": it.get("result") or {},
                    "trace_id": it.get("trace_id"),
                    "ethics_overall": it.get("ethics_overall"),
                    "risk_level": it.get("risk_level"),
                }
                for it in self._recent_ethics[:limit]
            ]
        return []

    def summary(self) -> dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute(
                "SELECT COUNT(*), status FROM audit_records GROUP BY status"
            )
            return {row[1]: row[0] for row in cur.fetchall()}
        finally:
            conn.close()

    def ethics_stats(self) -> dict[str, Any]:
        """Return aggregated ethics decision statistics."""
        conn = sqlite3.connect(self.db_path)
        try:
            stats = {
                "total_decisions": 0,
                "high_risk": 0,
                "medium_risk": 0,
                "low_risk": 0,
                "avg_score": 0.0,
            }
            cur = conn.execute(
                "SELECT ethics_overall, risk_level FROM audit_records WHERE ethics_overall IS NOT NULL"
            )
            rows = cur.fetchall()
            if not rows:
                # Fallback: compute from in-memory cache if present
                cache = getattr(self, "_recent_ethics", [])
                if cache:
                    total_score = 0.0
                    for it in cache:
                        score = it.get("ethics_overall") or 0.0
                        risk = it.get("risk_level")
                        if score is None:
                            continue
                        stats["total_decisions"] += 1
                        total_score += float(score)
                        if risk == "high":
                            stats["high_risk"] += 1
                        elif risk == "medium":
                            stats["medium_risk"] += 1
                        elif risk == "low":
                            stats["low_risk"] += 1
                    stats["avg_score"] = total_score / max(1, stats["total_decisions"])
                    print(
                        f"[AUDIT LEDGER][ETHICS_STATS][CACHE] td={stats['total_decisions']} avg={stats['avg_score']:.3f}",
                        flush=True,
                    )
                    return stats
                return stats
            total_score = 0.0
            for score, risk in rows:
                stats["total_decisions"] += 1
                total_score += score or 0.0
                if risk == "high":
                    stats["high_risk"] += 1
                elif risk == "medium":
                    stats["medium_risk"] += 1
                elif risk == "low":
                    stats["low_risk"] += 1
            stats["avg_score"] = total_score / max(1, stats["total_decisions"])
            return stats
        finally:
            conn.close()

    def get_by_trace(self, trace_id: str) -> dict[str, Any] | None:
        """Retrieve a specific audit record by trace id."""
        if not trace_id:
            return None
        print(
            f"[AUDIT LEDGER][GET_BY_TRACE] db_path={self.db_path} trace_id={trace_id}",
            flush=True,
        )
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute(
                "SELECT COUNT(*) FROM audit_records WHERE trace_id = ?", (trace_id,)
            )
            row_count = cur.fetchone()[0]
            print(
                f"[AUDIT LEDGER][GET_BY_TRACE] trace_id={trace_id} row_count_before_fetch={row_count}",
                flush=True,
            )
            cur = conn.execute(
                "SELECT plan_id, timestamp, action, status, target_json, result_json, trace_id, ethics_overall, risk_level FROM audit_records WHERE trace_id = ? ORDER BY id DESC LIMIT 1",
                (trace_id,),
            )
            row = cur.fetchone()
            if not row:
                # Fallback: search in-memory cache
                cache = getattr(self, "_recent_ethics", [])
                for it in cache:
                    if it.get("trace_id") == trace_id:
                        print(
                            f"[AUDIT LEDGER][GET_BY_TRACE][CACHE] hit trace_id={trace_id}",
                            flush=True,
                        )
                        return {
                            "plan_id": it.get("plan_id"),
                            "timestamp": it.get("timestamp"),
                            "action": it.get("action"),
                            "status": it.get("status"),
                            "target": it.get("target") or {},
                            "result": it.get("result") or {},
                            "trace_id": it.get("trace_id"),
                            "ethics_overall": it.get("ethics_overall"),
                            "risk_level": it.get("risk_level"),
                        }
                return None
            return {
                "plan_id": row[0],
                "timestamp": row[1],
                "action": row[2],
                "status": row[3],
                "target": json.loads(row[4]),
                "result": json.loads(row[5]),
                "trace_id": row[6],
                "ethics_overall": row[7],
                "risk_level": row[8],
            }
        finally:
            conn.close()

    def verify_integrity(self) -> bool:
        """Verify the immutability chain over all records.

        Returns True if every row's prev_hash matches the previous row's entry_hash
        (or 'genesis' for the first row), and entry hashes recompute correctly.
        """
        conn = sqlite3.connect(self.db_path)
        import hashlib as _hl

        try:
            cur = conn.execute(
                "SELECT plan_id, timestamp, action, status, target_json, result_json, trace_id, ethics_overall, risk_level, prev_hash, entry_hash FROM audit_records ORDER BY id ASC"
            )
            prev = None
            for row in cur.fetchall():
                (
                    plan_id,
                    ts,
                    action,
                    status,
                    tgt,
                    res,
                    tr,
                    ethics,
                    risk,
                    prev_hash,
                    entry_hash,
                ) = row
                expected_prev = prev or "genesis"
                if str(prev_hash or "") != expected_prev:
                    return False
                base = "|".join(
                    [
                        str(plan_id),
                        str(ts),
                        str(action),
                        str(status),
                        tgt or "",
                        res or "",
                        str(tr) if tr is not None else "",
                        str(ethics) if ethics is not None else "",
                        str(risk) if risk is not None else "",
                        expected_prev,
                    ]
                )
                calc = _hl.sha256(base.encode("utf-8")).hexdigest()
                if calc != entry_hash:
                    return False
                prev = entry_hash
            return True
        finally:
            conn.close()


class SelfIncorporationConfig:
    def _parse_roots(self) -> list[Path]:
        """Parse configured root directories to scan."""
        roots_env = os.getenv("AETHERRA_SELFINC_ROOTS", "")
        if not roots_env:
            # Default to current working directory (assumed to be repo root)
            return [Path.cwd()]

        roots = []
        for root_str in roots_env.split(";"):
            root_str = root_str.strip()
            if root_str:
                roots.append(Path(root_str))
        return roots

    """Configuration for the Self-Incorporation system."""

    def __init__(self) -> None:
        # Core settings
        self.enabled = os.getenv("AETHERRA_SELFINC_ENABLED", "1") == "1"
        self.roots = self._parse_roots()
        self.max_file_mb = int(os.getenv("AETHERRA_SELFINC_MAX_MB", "50"))
        self.strict_mode = os.getenv("AETHERRA_SELFINC_STRICT", "0") == "1"
        self.require_capabilities = (
            os.getenv("AETHERRA_REQUIRE_CAPABILITIES", "1") == "1"
        )
        self.net_strict = os.getenv("AETHERRA_NET_STRICT", "0") == "1"
        self.hmr_enabled = os.getenv("AETHERRA_HMR_ENABLED", "1") == "1"

        # Security settings (Phase 2B)
        # trust_mode: "strict" (prod), "standard" (default), or "permissive" (dev)
        profile = os.getenv("AETHERRA_PROFILE", "").lower()
        if profile in ("prod", "production"):
            self.trust_mode = "strict"
        elif profile in ("dev", "development"):
            self.trust_mode = "permissive"
        else:
            self.trust_mode = os.getenv("AETHERRA_SELFINC_TRUST_MODE", "standard")

        # Night cycle settings
        self.night_start_hour = int(os.getenv("AETHERRA_NIGHT_START_HOUR", "2"))
        self.night_end_hour = int(os.getenv("AETHERRA_NIGHT_END_HOUR", "4"))

        # Storage paths
        state_dir = Path(os.getenv("AETHERRA_STATE_DIR", ".aetherra"))
        state_dir.mkdir(exist_ok=True)
        self.index_db_path = state_dir / "selfinc_index.db"
        self.index_jsonl_path = state_dir / "selfinc_index.jsonl"
        self.audit_db_path = state_dir / "selfinc_audit.db"

        # Policy paths
        policy_dir = Path.home() / ".aetherra" / "policy"
        policy_dir.mkdir(parents=True, exist_ok=True)
        self.capabilities_policy_path = policy_dir / "capabilities.json"
        self.net_policy_path = policy_dir / "net_policy.json"
        self.selfinc_policy_path = policy_dir / "selfinc.json"
        # Guard policy path (Phase 2B)
        # Default to repo policy if present, else user policy dir
        default_guard_path = Path("Aetherra/homeostasis/configs/guard_policies.yaml")
        self.guard_policy_path = (
            default_guard_path
            if default_guard_path.exists()
            else policy_dir / "guard_policies.yaml"
        )
        # Policy-derived knobs (populated by service startup)

    unique_capabilities: list[str] = []


class CodeIndex:
    """SQLite-based index with JSONL mirror for discovered files."""

    def __init__(self, db_path: Path, jsonl_path: Path):
        self.db_path = db_path
        self.jsonl_path = jsonl_path
        self._init_database()

    def _init_database(self) -> None:
        """Initialize SQLite database schema."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS files (
                    id TEXT PRIMARY KEY,
                    path TEXT NOT NULL,
                    hash TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    mtime REAL NOT NULL,
                    type TEXT DEFAULT 'unknown',
                    language TEXT DEFAULT 'other',
                    entrypoints TEXT DEFAULT '[]',
                    discovered_at TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_files_path ON files(path)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_files_type ON files(type)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_files_hash ON files(hash)
            """
            )

            conn.commit()
        finally:
            conn.close()

    def store_file(self, file_item: FileItem) -> None:
        """Store a FileItem in the index."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO files
                (id, path, hash, size, mtime, type, language, entrypoints, discovered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    file_item.id,
                    file_item.path,
                    file_item.hash,
                    file_item.size,
                    file_item.mtime,
                    file_item.type.value,
                    file_item.language,
                    json.dumps(file_item.entrypoints),
                    file_item.discovered_at.isoformat(),
                ),
            )
            conn.commit()

            # Also append to JSONL mirror
            with open(self.jsonl_path, "a", encoding="utf-8") as f:
                json.dump(asdict(file_item), f, default=str)
                f.write("\n")

        finally:
            conn.close()

    def get_file(self, file_id: str) -> FileItem | None:
        """Retrieve a FileItem by ID."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("SELECT * FROM files WHERE id = ?", (file_id,))
            row = cursor.fetchone()
            if not row:
                return None

            return FileItem(
                id=row[0],
                path=row[1],
                hash=row[2],
                size=row[3],
                mtime=row[4],
                type=ItemType(row[5]),
                language=row[6],
                entrypoints=json.loads(row[7]),
                discovered_at=datetime.fromisoformat(row[8]),
            )
        finally:
            conn.close()

    def list_files(self, file_type: ItemType | None = None) -> list[FileItem]:
        """List all files, optionally filtered by type."""
        conn = sqlite3.connect(self.db_path)
        try:
            if file_type:
                cursor = conn.execute(
                    "SELECT * FROM files WHERE type = ? ORDER BY path",
                    (file_type.value,),
                )
            else:
                cursor = conn.execute("SELECT * FROM files ORDER BY path")

            files = []
            for row in cursor.fetchall():
                files.append(
                    FileItem(
                        id=row[0],
                        path=row[1],
                        hash=row[2],
                        size=row[3],
                        mtime=row[4],
                        type=ItemType(row[5]),
                        language=row[6],
                        entrypoints=json.loads(row[7]),
                        discovered_at=datetime.fromisoformat(row[8]),
                    )
                )
            return files
        finally:
            conn.close()


class HeuristicClassifier:
    """
    Advanced file classifier that extracts metadata, capabilities,
    dependencies, and risk assessment from discovered files.
    """

    def __init__(self, config: SelfIncorporationConfig):
        self.config = config

    def classify_file(self, file_item: FileItem) -> ClassificationResult:
        """Perform comprehensive classification of a file."""
        path = Path(file_item.path)
        file_type = file_item.type
        capabilities: list[str] = []
        requires: list[str] = []
        risk_hints: list[str] = []
        metadata: dict[str, Any] = {}
        confidence = 0.5

        if file_item.language == "python":
            (
                capabilities,
                requires,
                risk_hints,
                metadata,
                confidence,
            ) = self._analyze_python_file(path)
        elif file_item.language == "aether":
            (
                capabilities,
                requires,
                risk_hints,
                metadata,
                confidence,
            ) = self._analyze_aether_file(path)
        elif file_item.language == "json":
            (
                capabilities,
                requires,
                risk_hints,
                metadata,
                confidence,
            ) = self._analyze_json_file(path)

        return ClassificationResult(
            file_id=file_item.id,
            type=file_type,
            declared_capabilities=capabilities,
            requires=requires,
            risk_hints=risk_hints,
            metadata=metadata,
            confidence=confidence,
        )

    def _analyze_python_file(
        self, path: Path
    ) -> tuple[list[str], list[str], list[str], dict[str, Any], float]:
        """Analyze Python file for capabilities, dependencies, and risks."""
        capabilities: list[str] = []
        requires: list[str] = []
        risk_hints: list[str] = []
        metadata: dict[str, Any] = {}
        confidence = 0.7

        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()

            # Extract imports
            # Standard library imports
            import re

            # Standard imports
            for match in re.finditer(
                r"^import\s+([a-zA-Z_][a-zA-Z0-9_., ]*)", content, re.MULTILINE
            ):
                modules = [m.strip() for m in match.group(1).split(",")]
                requires.extend(modules)

            # From imports
            for match in re.finditer(
                r"^from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import", content, re.MULTILINE
            ):
                requires.append(match.group(1))

            # Look for capability declarations
            if "def plugin_" in content or "class.*Plugin" in content:
                capabilities.append("plugin_interface")
                confidence = 0.9

            if "def agent_" in content or "class.*Agent" in content:
                capabilities.append("agent_interface")
                confidence = 0.9

            if "async def" in content:
                capabilities.append("async_execution")

            if (
                "requests." in content
                or "urllib" in content
                or "http" in content.lower()
            ):
                capabilities.append("network_access")
                if not self.config.net_strict:
                    risk_hints.append("network_access_permissive")

            if "subprocess" in content or "os.system" in content or "exec(" in content:
                capabilities.append("system_execution")
                risk_hints.append("system_execution_risk")

            if "open(" in content and ("w" in content or "a" in content):
                capabilities.append("file_write")
                risk_hints.append("file_modification")

            # Check for specific Aetherra patterns
            if "aetherra" in content.lower():
                capabilities.append("aetherra_integration")

            if "memory_system" in content or "plugin_manager" in content:
                capabilities.append("system_component")
                confidence = 0.95

            # Extract docstring metadata
            docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if docstring_match:
                docstring = docstring_match.group(1).strip()
                metadata["description"] = docstring[:500]  # Limit length

                # Look for capability declarations in docstring
                if "capabilities:" in docstring.lower():
                    cap_match = re.search(
                        r"capabilities:\s*([^\n]*)", docstring.lower()
                    )
                    if cap_match:
                        declared_caps = [
                            c.strip() for c in cap_match.group(1).split(",")
                        ]
                        capabilities.extend(declared_caps)

            # Count complexity indicators
            class_count = len(re.findall(r"^class\s+", content, re.MULTILINE))
            function_count = len(re.findall(r"^def\s+", content, re.MULTILINE))

            metadata.update(
                {
                    "classes": class_count,
                    "functions": function_count,
                    "lines": len(content.splitlines()),
                    "complexity": "high"
                    if (class_count + function_count) > 10
                    else "medium"
                    if (class_count + function_count) > 3
                    else "low",
                }
            )

        except Exception as e:
            risk_hints.append(f"analysis_error: {str(e)[:100]}")
            confidence = 0.1

        return capabilities, requires, risk_hints, metadata, confidence

    def _analyze_aether_file(
        self, path: Path
    ) -> tuple[list[str], list[str], list[str], dict[str, Any], float]:
        """Analyze .aether script file."""
        capabilities: list[str] = ["aether_script"]
        requires: list[str] = []
        risk_hints: list[str] = []
        metadata: dict[str, Any] = {}
        confidence = 0.9

        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()

            # Look for workflow patterns
            if "workflow" in content.lower():
                capabilities.append("workflow_execution")

            if "plugin_invoke" in content:
                capabilities.append("plugin_orchestration")
                requires.append("plugin_manager")

            if "memory_" in content:
                capabilities.append("memory_access")
                requires.append("memory_system")

            # Check for parallel execution
            if "parallel" in content.lower() or "concurrent" in content.lower():
                capabilities.append("parallel_execution")
                risk_hints.append("concurrent_complexity")

            # Check for error handling
            if "on_error" in content.lower() or "catch" in content.lower():
                capabilities.append("error_handling")

            metadata.update(
                {"type": "aether_script", "lines": len(content.splitlines())}
            )

        except Exception as e:
            risk_hints.append(f"analysis_error: {str(e)[:100]}")
            confidence = 0.1

        return capabilities, requires, risk_hints, metadata, confidence

    def _analyze_json_file(
        self, path: Path
    ) -> tuple[list[str], list[str], list[str], dict[str, Any], float]:
        """Analyze JSON configuration/data files."""
        capabilities: list[str] = []
        requires: list[str] = []
        risk_hints: list[str] = []
        metadata: dict[str, Any] = {}
        confidence = 0.8

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict):
                # Check for plugin configuration
                if "plugin" in str(data).lower() or "capabilities" in data:
                    capabilities.append("plugin_config")

                # Check for agent configuration
                if "agent" in str(data).lower():
                    capabilities.append("agent_config")

                # Check for policy/security configuration
                if any(
                    key in data
                    for key in ["policy", "permissions", "allowed", "denied"]
                ):
                    capabilities.append("security_policy")

                # Extract basic metadata
                metadata.update(
                    {
                        "keys": len(data.keys()) if isinstance(data, dict) else 0,
                        "type": "config"
                        if any(key in data for key in ["version", "name", "config"])
                        else "data",
                    }
                )

        except json.JSONDecodeError:
            risk_hints.append("invalid_json")
            confidence = 0.1
        except Exception as e:
            risk_hints.append(f"analysis_error: {str(e)[:100]}")
            confidence = 0.1

        return capabilities, requires, risk_hints, metadata, confidence


class ClassificationIndex:
    """Index for storing and querying classification results."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_database()

    def _init_database(self) -> None:
        """Initialize classification database schema."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS classifications (
                    file_id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    capabilities TEXT DEFAULT '[]',
                    requires TEXT DEFAULT '[]',
                    risk_hints TEXT DEFAULT '[]',
                    metadata TEXT DEFAULT '{}',
                    confidence REAL DEFAULT 0.0,
                    classified_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_classifications_type ON classifications(type)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_classifications_confidence ON classifications(confidence)
            """
            )

            conn.commit()
        finally:
            conn.close()

    def store_classification(self, result: ClassificationResult) -> None:
        """Store a classification result."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO classifications
                (file_id, type, capabilities, requires, risk_hints, metadata, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    result.file_id,
                    result.type.value,
                    json.dumps(result.declared_capabilities),
                    json.dumps(result.requires),
                    json.dumps(result.risk_hints),
                    json.dumps(result.metadata),
                    result.confidence,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def get_classification(self, file_id: str) -> ClassificationResult | None:
        """Retrieve a classification result by file ID."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                "SELECT * FROM classifications WHERE file_id = ?", (file_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None

            return ClassificationResult(
                file_id=row[0],
                type=ItemType(row[1]),
                declared_capabilities=json.loads(row[2]),
                requires=json.loads(row[3]),
                risk_hints=json.loads(row[4]),
                metadata=json.loads(row[5]),
                confidence=row[6],
            )
        finally:
            conn.close()

    def list_by_capability(self, capability: str) -> list[ClassificationResult]:
        """List files that declare a specific capability."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                "SELECT * FROM classifications WHERE capabilities LIKE ?",
                (f"%{capability}%",),
            )

            results = []
            for row in cursor.fetchall():
                results.append(
                    ClassificationResult(
                        file_id=row[0],
                        type=ItemType(row[1]),
                        declared_capabilities=json.loads(row[2]),
                        requires=json.loads(row[3]),
                        risk_hints=json.loads(row[4]),
                        metadata=json.loads(row[5]),
                        confidence=row[6],
                    )
                )
            return results
        finally:
            conn.close()

    def list_classifications(self) -> list[ClassificationResult]:
        """List all stored classifications."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("SELECT * FROM classifications")

            results = []
            for row in cursor.fetchall():
                results.append(
                    ClassificationResult(
                        file_id=row[0],
                        type=ItemType(row[1]),
                        declared_capabilities=json.loads(row[2]),
                        requires=json.loads(row[3]),
                        risk_hints=json.loads(row[4]),
                        metadata=json.loads(row[5]),
                        confidence=row[6],
                    )
                )
            return results
        finally:
            conn.close()


class PolicyEngine:
    """
    Policy evaluation engine that enforces security and capability policies.
    """

    def __init__(self, config: SelfIncorporationConfig):
        self.config = config
        self.capability_policies = self._load_capability_policies()
        self.network_policies = self._load_network_policies()
        self.selfinc_policies = self._load_selfinc_policies()

    def _load_capability_policies(self) -> dict[str, Any]:
        """Load capability allowlist/denylist policies."""
        try:
            # Standard library imports
            from typing import cast

            if self.config.capabilities_policy_path.exists():
                with open(self.config.capabilities_policy_path, encoding="utf-8") as f:
                    return cast(dict[str, Any], json.load(f))
        except Exception as e:
            logger.debug(f"[POLICY] Failed to load capability policies: {e}")

        # Default policy - be permissive but flag risky capabilities
        return {
            "version": "1.0",
            "allowed_capabilities": [
                "plugin_interface",
                "agent_interface",
                "aether_script",
                "workflow_execution",
                "memory_access",
                "file_read",
                "async_execution",
                "aetherra_integration",
                "system_component",
            ],
            "restricted_capabilities": [
                "network_access",
                "file_write",
                "system_execution",
            ],
            "denied_capabilities": ["arbitrary_code_execution", "privilege_escalation"],
            "require_verification": ["system_execution", "network_access"],
        }

    def _load_network_policies(self) -> dict[str, Any]:
        """Load network access policies."""
        try:
            # Standard library imports
            from typing import cast

            if self.config.net_policy_path.exists():
                with open(self.config.net_policy_path, encoding="utf-8") as f:
                    return cast(dict[str, Any], json.load(f))
        except Exception as e:
            logger.debug(f"[POLICY] Failed to load network policies: {e}")

        # Default network policy based on config
        if self.config.net_strict:
            return {
                "mode": "strict",
                "allowed_domains": ["localhost", "127.0.0.1", ".aetherra.dev"],
                "denied_domains": ["*"],
                "require_approval": True,
            }
        return {
            "mode": "permissive",
            "allowed_domains": ["*"],
            "denied_domains": [],
            "require_approval": False,
        }

    def _load_selfinc_policies(self) -> dict[str, Any]:
        """Load self-incorporation specific policies."""
        # Try project root first
        project_policy_path = Path.cwd() / "selfinc_policy.json"
        try:
            # Standard library imports
            from typing import cast

            if project_policy_path.exists():
                with open(project_policy_path, encoding="utf-8") as f:
                    return cast(dict[str, Any], json.load(f))
        except Exception as e:
            logger.debug(
                f"[POLICY] Failed to load selfinc_policy.json from project root: {e}"
            )

        # Fallback to default config path
        try:
            # Standard library imports
            from typing import cast

            if self.config.selfinc_policy_path.exists():
                with open(self.config.selfinc_policy_path, encoding="utf-8") as f:
                    return cast(dict[str, Any], json.load(f))
        except Exception as e:
            logger.debug(
                f"[POLICY] Failed to load selfinc policies from config path: {e}"
            )

        # Default selfinc policy
        return {
            "version": "1.0",
            "auto_integrate": ["utility", "docs", "dataset"],
            "require_review": ["plugin", "agent", "workflow"],
            "quarantine": ["unknown"],
            # By default, treat capabilities as multi-provider. Only capabilities
            # listed here are considered exclusive and will trigger conflicts when
            # more than one provider is detected.
            "unique_capabilities": [],
            # Reserved knob to change global behavior if needed in the future.
            "conflict_policy": "multi_provider_by_default",
            "trust_tiers": {
                "verified": {"auto_integrate": True, "elevated_permissions": True},
                "trusted": {"auto_integrate": True, "elevated_permissions": False},
                "standard": {"auto_integrate": False, "elevated_permissions": False},
                "experimental": {
                    "auto_integrate": False,
                    "elevated_permissions": False,
                },
                "quarantined": {"auto_integrate": False, "elevated_permissions": False},
            },
        }

    def evaluate_capabilities(self, capabilities: list[str]) -> tuple[bool, list[str]]:
        """Evaluate if capabilities are allowed by policy."""
        policy = self.capability_policies
        reasons = []
        allowed = True

        for capability in capabilities:
            if capability in policy.get("denied_capabilities", []):
                allowed = False
                reasons.append(f"denied_capability: {capability}")
            elif capability in policy.get("restricted_capabilities", []):
                if self.config.strict_mode:
                    allowed = False
                    reasons.append(
                        f"restricted_capability_in_strict_mode: {capability}"
                    )
                else:
                    reasons.append(f"restricted_capability_flagged: {capability}")
            elif capability not in policy.get("allowed_capabilities", []):
                if self.config.strict_mode:
                    allowed = False
                    reasons.append(f"unknown_capability_in_strict_mode: {capability}")
                else:
                    reasons.append(f"unknown_capability_flagged: {capability}")

        return allowed, reasons


class SecurityGate:
    """
    Security verification and risk assessment gate.
    """

    def __init__(self, config: SelfIncorporationConfig, policy_engine: PolicyEngine):
        self.config = config
        self.policy_engine = policy_engine

    def evaluate_security(
        self, file_item: FileItem, classification: ClassificationResult
    ) -> SafetyDecision:
        """Perform comprehensive security evaluation."""
        decision = SafetyDecision(file_id=file_item.id)

        # Step 1: Signature verification (placeholder for now)
        decision.verified, signing_info = self._verify_signatures(file_item)
        decision.signing = signing_info

        # Step 2: Static security scans
        scan_results = self._run_static_scans(file_item, classification)
        decision.scans = scan_results

        # Step 3: Capability evaluation
        capability_ok, cap_reasons = self.policy_engine.evaluate_capabilities(
            classification.declared_capabilities
        )
        decision.capability_ok = capability_ok
        decision.reasons.extend(cap_reasons)

        # Step 4: Risk assessment
        risk_level = self._assess_risk_level(classification)

        # Step 5: Trust tier assignment
        decision.trust_tier = self._assign_trust_tier(
            file_item, classification, decision.verified, capability_ok, risk_level
        )

        # Step 6: Final decision reasoning
        decision.reasons.extend(
            self._generate_decision_reasons(file_item, classification, decision)
        )

        return decision

    def _verify_signatures(self, file_item: FileItem) -> tuple[bool, dict[str, Any]]:
        """Verify file signatures (placeholder implementation)."""
        # TODO: Implement actual signature verification
        # For now, check if file is in trusted locations or has known patterns

        path = Path(file_item.path)
        trusted_paths = ["Aetherra/core", "Aetherra/aetherra_core", "src/lyrixa"]

        is_trusted_location = any(
            trusted_path in str(path) for trusted_path in trusted_paths
        )

        signing_info = {
            "method": "path_based_trust",
            "trusted_location": is_trusted_location,
            "signature_present": False,  # Would check for actual signatures
            "signature_valid": False,
        }

        return is_trusted_location, signing_info

    def _run_static_scans(
        self, file_item: FileItem, classification: ClassificationResult
    ) -> dict[str, str]:
        """Run static security scans on the file."""
        results = {}

        try:
            path = Path(file_item.path)

            # Basic file safety checks
            if file_item.size > self.config.max_file_mb * 1024 * 1024:
                results["size_check"] = (
                    f"WARN: File size {file_item.size} exceeds limit"
                )
            else:
                results["size_check"] = "PASS"

            # Language-specific checks
            if file_item.language == "python":
                results.update(self._scan_python_file(path, classification))
            elif file_item.language == "aether":
                results.update(self._scan_aether_file(path, classification))

            # General risk pattern checks
            risk_patterns = ["eval(", "exec(", "__import__", "subprocess", "os.system"]
            if file_item.language == "python":
                try:
                    with open(path, encoding="utf-8") as f:
                        content = f.read(10000)  # First 10KB

                    found_patterns = [
                        pattern for pattern in risk_patterns if pattern in content
                    ]
                    if found_patterns:
                        results["risk_patterns"] = f"WARN: Found {found_patterns}"
                    else:
                        results["risk_patterns"] = "PASS"
                except Exception:
                    results["risk_patterns"] = "ERROR: Could not scan"

        except Exception as e:
            results["scan_error"] = f"ERROR: {str(e)[:100]}"

        return results

    def _scan_python_file(
        self, path: Path, classification: ClassificationResult
    ) -> dict[str, str]:
        """Python-specific security scans."""
        results = {}

        try:
            # Import hygiene check
            dangerous_imports = [
                "subprocess",
                "os",
                "sys",
                "eval",
                "exec",
                "pickle",
                "marshal",
                "requests",
                "urllib",
                "socket",
                "http",
            ]

            safe_count = 0
            risky_count = 0

            for req in classification.requires:
                if any(danger in req for danger in dangerous_imports):
                    risky_count += 1
                else:
                    safe_count += 1

            if risky_count > 0:
                results["import_hygiene"] = (
                    f"WARN: {risky_count} risky imports, {safe_count} safe"
                )
            else:
                results["import_hygiene"] = "PASS"

            # Function complexity check
            complexity = classification.metadata.get("complexity", "low")
            if complexity == "high":
                results["complexity"] = "WARN: High complexity detected"
            else:
                results["complexity"] = "PASS"

        except Exception as e:
            results["python_scan_error"] = f"ERROR: {str(e)[:50]}"

        return results

    def _scan_aether_file(
        self, path: Path, classification: ClassificationResult
    ) -> dict[str, str]:
        """Aether script specific security scans."""
        results = {}

        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()

            # Check for potentially dangerous aether operations
            dangerous_patterns = ["system_execute", "file_write", "network_call"]
            found_dangerous = [
                pat for pat in dangerous_patterns if pat in content.lower()
            ]

            if found_dangerous:
                results["aether_safety"] = f"WARN: Found {found_dangerous}"
            else:
                results["aether_safety"] = "PASS"

        except Exception as e:
            results["aether_scan_error"] = f"ERROR: {str(e)[:50]}"

        return results

    def _assess_risk_level(self, classification: ClassificationResult) -> str:
        """Assess overall risk level based on classification."""
        risk_score = 0

        # Risk from capabilities
        high_risk_caps = ["system_execution", "network_access", "file_write"]
        medium_risk_caps = ["plugin_interface", "agent_interface"]

        for cap in classification.declared_capabilities:
            if cap in high_risk_caps:
                risk_score += 3
            elif cap in medium_risk_caps:
                risk_score += 1

        # Risk from hints
        risk_score += len(classification.risk_hints)

        # Risk from low confidence
        if classification.confidence < 0.5:
            risk_score += 2

        if risk_score >= 5:
            return "high"
        if risk_score >= 2:
            return "medium"
        return "low"

    def _assign_trust_tier(
        self,
        file_item: FileItem,
        classification: ClassificationResult,
        verified: bool,
        capability_ok: bool,
        risk_level: str,
    ) -> TrustTier:
        """Assign trust tier based on all security factors."""

        # Verified files get higher trust
        if verified and capability_ok and risk_level == "low":
            return TrustTier.VERIFIED

        # Files in core system paths with good capabilities
        if "aetherra_core" in file_item.path.lower() and capability_ok:
            return TrustTier.TRUSTED

        # Standard files that pass basic checks
        if capability_ok and risk_level in ["low", "medium"]:
            return TrustTier.STANDARD

        # Experimental for unknown or medium-risk items
        if risk_level == "medium" or classification.confidence < 0.7:
            return TrustTier.EXPERIMENTAL

        # Quarantine high-risk or policy-violating items
        return TrustTier.QUARANTINED

    def _generate_decision_reasons(
        self,
        file_item: FileItem,
        classification: ClassificationResult,
        decision: SafetyDecision,
    ) -> list[str]:
        """Generate human-readable reasons for the security decision."""
        reasons = []

        reasons.append(f"trust_tier: {decision.trust_tier.value}")
        reasons.append(f"verified: {decision.verified}")
        reasons.append(
            f"capability_policy: {'pass' if decision.capability_ok else 'fail'}"
        )

        if classification.confidence < 0.7:
            reasons.append(f"low_confidence: {classification.confidence:.2f}")

        if classification.risk_hints:
            reasons.append(f"risk_hints: {len(classification.risk_hints)}")

        # Scan result summary
        scan_warnings = [k for k, v in decision.scans.items() if v.startswith("WARN")]
        if scan_warnings:
            reasons.append(f"scan_warnings: {len(scan_warnings)}")

        return reasons


class SafetyIndex:
    """Index for storing and querying safety decisions."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_database()

    def _init_database(self) -> None:
        """Initialize safety decisions database schema."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS safety_decisions (
                    file_id TEXT PRIMARY KEY,
                    verified INTEGER NOT NULL,
                    signing TEXT DEFAULT '{}',
                    scans TEXT DEFAULT '{}',
                    capability_ok INTEGER NOT NULL,
                    trust_tier TEXT NOT NULL,
                    reasons TEXT DEFAULT '[]',
                    timestamp TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_safety_trust_tier ON safety_decisions(trust_tier)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_safety_verified ON safety_decisions(verified)
            """
            )

            conn.commit()
        finally:
            conn.close()

    def store_decision(self, decision: SafetyDecision) -> None:
        """Store a safety decision."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO safety_decisions
                (file_id, verified, signing, scans, capability_ok, trust_tier, reasons, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    decision.file_id,
                    1 if decision.verified else 0,
                    json.dumps(decision.signing),
                    json.dumps(decision.scans),
                    1 if decision.capability_ok else 0,
                    decision.trust_tier.value,
                    json.dumps(decision.reasons),
                    decision.timestamp.isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def get_decision(self, file_id: str) -> SafetyDecision | None:
        """Retrieve a safety decision by file ID."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                "SELECT * FROM safety_decisions WHERE file_id = ?", (file_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None

            return SafetyDecision(
                file_id=row[0],
                verified=bool(row[1]),
                signing=json.loads(row[2]),
                scans=json.loads(row[3]),
                capability_ok=bool(row[4]),
                trust_tier=TrustTier(row[5]),
                reasons=json.loads(row[6]),
                timestamp=datetime.fromisoformat(row[7]),
            )
        finally:
            conn.close()

    def list_by_trust_tier(self, trust_tier: TrustTier) -> list[SafetyDecision]:
        """List decisions by trust tier."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                "SELECT * FROM safety_decisions WHERE trust_tier = ?",
                (trust_tier.value,),
            )

            results = []
            for row in cursor.fetchall():
                results.append(
                    SafetyDecision(
                        file_id=row[0],
                        verified=bool(row[1]),
                        signing=json.loads(row[2]),
                        scans=json.loads(row[3]),
                        capability_ok=bool(row[4]),
                        trust_tier=TrustTier(row[5]),
                        reasons=json.loads(row[6]),
                        timestamp=datetime.fromisoformat(row[7]),
                    )
                )
            return results
        finally:
            conn.close()


class DependencyAnalyzer:
    """
    Analyzes dependencies between discovered components to build integration order.
    """

    def __init__(self, config: SelfIncorporationConfig):
        self.config = config
        self.dependency_graph: dict[
            str, list[str]
        ] = {}  # file_id -> list of dependency file_ids
        self.reverse_deps: dict[
            str, list[str]
        ] = {}  # file_id -> list of files that depend on it

    def analyze_dependencies(
        self,
        classifications: list[ClassificationResult],
        safety_decisions: list[SafetyDecision],
    ) -> dict[str, list[str]]:
        """Analyze dependencies between classified components."""

        # Clear existing graph
        self.dependency_graph.clear()
        self.reverse_deps.clear()

        # Build dependency mappings
        safe_files = {
            d.file_id: d
            for d in safety_decisions
            if d.trust_tier not in [TrustTier.QUARANTINED]
        }

        for classification in classifications:
            if classification.file_id not in safe_files:
                continue  # Skip quarantined files

            file_deps = []

            # Analyze declared requirements
            for requirement in classification.requires:
                dep_file_id = self._resolve_requirement_to_file(
                    requirement, classifications
                )
                if dep_file_id and dep_file_id in safe_files:
                    file_deps.append(dep_file_id)

            # Store dependencies
            self.dependency_graph[classification.file_id] = file_deps

            # Build reverse dependencies
            for dep_id in file_deps:
                if dep_id not in self.reverse_deps:
                    self.reverse_deps[dep_id] = []
                self.reverse_deps[dep_id].append(classification.file_id)

        return self.dependency_graph

    def _resolve_requirement_to_file(
        self, requirement: str, classifications: list[ClassificationResult]
    ) -> str | None:
        """Resolve a requirement string to a file ID if possible."""

        # Simple heuristic resolution - in a real system this would be more sophisticated
        requirement_lower = requirement.lower()

        for classification in classifications:
            # Check if requirement matches any known capabilities
            for capability in classification.declared_capabilities:
                if requirement_lower in capability.lower():
                    return classification.file_id

            # Check metadata for matches
            if "module_name" in classification.metadata:
                module_name = classification.metadata["module_name"].lower()
                if requirement_lower in module_name or module_name in requirement_lower:
                    return classification.file_id

        return None

    def detect_cycles(self) -> list[list[str]]:
        """Detect dependency cycles that would prevent integration."""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: list[str]) -> bool:
            """DFS to detect cycles."""
            if node in rec_stack:
                # Found cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return True

            if node in visited:
                return False

            visited.add(node)
            rec_stack.add(node)

            for neighbor in self.dependency_graph.get(node, []):
                if dfs(neighbor, path + [node]):
                    return True

            rec_stack.remove(node)
            return False

        for node in self.dependency_graph:
            if node not in visited:
                dfs(node, [])

        return cycles

    def topological_sort(self) -> list[str]:
        """Return topologically sorted integration order."""
        in_degree = {}

        # Initialize in-degrees
        for node in self.dependency_graph:
            in_degree[node] = 0

        # Calculate in-degrees
        for node in self.dependency_graph:
            for neighbor in self.dependency_graph[node]:
                in_degree[neighbor] = in_degree.get(neighbor, 0) + 1

        # Kahn's algorithm
        queue = [node for node in in_degree if in_degree[node] == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)

            for neighbor in self.dependency_graph.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return result


class ConflictResolver:
    """
    Resolves conflicts between components that want to provide the same capabilities.
    """

    def __init__(self, config: SelfIncorporationConfig):
        self.config = config

    def detect_conflicts(
        self,
        classifications: list[ClassificationResult],
        safety_decisions: list[SafetyDecision],
    ) -> list[dict[str, Any]]:
        """Detect capability conflicts between components."""
        conflicts = []
        capability_providers: dict[str, list[dict[str, Any]]] = {}
        # Determine which capabilities are exclusive (conflict if >1 provider)
        unique_caps = set(getattr(self.config, "unique_capabilities", []) or [])

        # Group files by capabilities they provide
        for classification in classifications:
            safety = next(
                (s for s in safety_decisions if s.file_id == classification.file_id),
                None,
            )
            if not safety or safety.trust_tier == TrustTier.QUARANTINED:
                continue

            for capability in classification.declared_capabilities:
                if capability not in capability_providers:
                    capability_providers[capability] = []
                capability_providers[capability].append(
                    {
                        "file_id": classification.file_id,
                        "classification": classification,
                        "safety": safety,
                    }
                )

        # Find conflicts (multiple providers for same capability)
        for capability, providers in capability_providers.items():
            # Only treat as conflict if capability is explicitly unique
            if capability in unique_caps and len(providers) > 1:
                conflicts.append(
                    {
                        "capability": capability,
                        "providers": providers,
                        "resolution_strategy": self._determine_resolution_strategy(
                            capability, providers
                        ),
                    }
                )

        return conflicts

    def _determine_resolution_strategy(
        self, capability: str, providers: list[dict[str, Any]]
    ) -> str:
        """Determine how to resolve a capability conflict."""

        # Sort by trust tier priority
        trust_priority = {
            TrustTier.VERIFIED: 5,
            TrustTier.TRUSTED: 4,
            TrustTier.STANDARD: 3,
            TrustTier.EXPERIMENTAL: 2,
            TrustTier.QUARANTINED: 1,
        }

        sorted_providers = sorted(
            providers,
            key=lambda p: trust_priority[p["safety"].trust_tier],
            reverse=True,
        )

        # If there's a clear trust leader, prefer it
        if (
            sorted_providers[0]["safety"].trust_tier
            != sorted_providers[1]["safety"].trust_tier
        ):
            return "prefer_highest_trust"

        # If trust is equal, prefer by confidence
        if (
            sorted_providers[0]["classification"].confidence
            > sorted_providers[1]["classification"].confidence + 0.1
        ):
            return "prefer_highest_confidence"

        # If still tied, require manual resolution
        return "manual_review_required"

    def resolve_conflict(self, conflict: dict[str, Any]) -> dict[str, Any]:
        """Apply resolution strategy to a conflict."""
        strategy = conflict["resolution_strategy"]
        providers = conflict["providers"]

        if strategy == "prefer_highest_trust":
            chosen = max(
                providers, key=lambda p: self._trust_score(p["safety"].trust_tier)
            )
            rejected = [p for p in providers if p != chosen]

        elif strategy == "prefer_highest_confidence":
            chosen = max(providers, key=lambda p: p["classification"].confidence)
            rejected = [p for p in providers if p != chosen]

        else:  # manual_review_required
            return {
                "status": "requires_manual_review",
                "conflict": conflict,
                "chosen": None,
                "rejected": [],
            }

        return {
            "status": "resolved",
            "conflict": conflict,
            "chosen": chosen,
            "rejected": rejected,
        }

    def _trust_score(self, trust_tier: TrustTier) -> int:
        """Convert trust tier to numeric score."""
        scores = {
            TrustTier.VERIFIED: 5,
            TrustTier.TRUSTED: 4,
            TrustTier.STANDARD: 3,
            TrustTier.EXPERIMENTAL: 2,
            TrustTier.QUARANTINED: 1,
        }
        return scores.get(trust_tier, 0)


class IntegrationPlanner:
    """
    Creates integration plans by analyzing dependencies, resolving conflicts,
    and determining the optimal order and method for integrating components.
    """

    def __init__(self, config: SelfIncorporationConfig):
        self.config = config
        self.dependency_analyzer = DependencyAnalyzer(config)
        self.conflict_resolver = ConflictResolver(config)

    def create_integration_plan(
        self,
        classifications: list[ClassificationResult],
        safety_decisions: list[SafetyDecision],
    ) -> dict[str, Any]:
        """Create a comprehensive integration plan."""

        logger.info(
            f"[PLANNER] Creating integration plan for {len(classifications)} components"
        )

        # Step 1: Analyze dependencies
        dependencies = self.dependency_analyzer.analyze_dependencies(
            classifications, safety_decisions
        )

        # Step 2: Detect dependency cycles
        cycles = self.dependency_analyzer.detect_cycles()
        if cycles:
            logger.warning(f"[PLANNER] Found {len(cycles)} dependency cycles")

        # Step 3: Detect capability conflicts
        conflicts = self.conflict_resolver.detect_conflicts(
            classifications, safety_decisions
        )

        # Step 4: Resolve conflicts
        resolved_conflicts = []
        unresolved_conflicts = []

        for conflict in conflicts:
            resolution = self.conflict_resolver.resolve_conflict(conflict)
            if resolution["status"] == "resolved":
                resolved_conflicts.append(resolution)
            else:
                unresolved_conflicts.append(resolution)

        # Step 5: Filter out rejected components
        active_files = {c.file_id for c in classifications}
        for resolution in resolved_conflicts:
            for rejected in resolution["rejected"]:
                active_files.discard(rejected["file_id"])

        # Step 6: Create integration order
        integration_order = []
        if not cycles and not unresolved_conflicts:
            # Filter dependency graph to only active files
            filtered_graph = {
                file_id: [dep for dep in deps if dep in active_files]
                for file_id, deps in dependencies.items()
                if file_id in active_files
            }

            self.dependency_analyzer.dependency_graph = filtered_graph
            integration_order = self.dependency_analyzer.topological_sort()

        # Step 7: Generate integration actions
        actions = self._generate_integration_actions(
            classifications, safety_decisions, integration_order, active_files
        )

        plan = {
            "plan_id": hashlib.sha256(
                f"{len(classifications)}{time.time()}".encode()
            ).hexdigest()[:8],
            "created_at": datetime.now(),
            "total_components": len(classifications),
            "active_components": len(active_files),
            "dependencies": dependencies,
            "dependency_cycles": cycles,
            "conflicts": conflicts,
            "resolved_conflicts": resolved_conflicts,
            "unresolved_conflicts": unresolved_conflicts,
            "integration_order": integration_order,
            "actions": actions,
            "status": "ready" if not cycles and not unresolved_conflicts else "blocked",
        }

        logger.info(
            f"[PLANNER] Plan {plan['plan_id']}: {plan['status']} with {len(actions)} actions"
        )
        return plan

    def _generate_integration_actions(
        self,
        classifications: list[ClassificationResult],
        safety_decisions: list[SafetyDecision],
        integration_order: list[str],
        active_files: set[str],
    ) -> list[PlanAction]:
        """Generate concrete integration actions."""
        actions = []

        for file_id in integration_order:
            if file_id not in active_files:
                continue

            classification = next(
                (c for c in classifications if c.file_id == file_id), None
            )
            safety = next((s for s in safety_decisions if s.file_id == file_id), None)

            if not classification or not safety:
                continue

            # Determine action type based on component type
            action_type = self._determine_action_type(classification)
            priority = self._determine_priority(classification, safety)

            action = PlanAction(
                action=action_type,
                target={
                    "file_id": file_id,
                    "type": classification.type.value,
                    "capabilities": classification.declared_capabilities,
                    "trust_tier": safety.trust_tier.value,
                },
                deps=self.dependency_analyzer.dependency_graph.get(file_id, []),
                priority=priority,
            )

            actions.append(action)

        return actions

    def _determine_action_type(self, classification: ClassificationResult) -> str:
        """Determine integration action type based on component classification."""
        type_actions = {
            ItemType.PLUGIN: "register_plugin",
            ItemType.AGENT: "register_agent",
            ItemType.AETHER: "load_aether_script",
            ItemType.WORKFLOW: "register_workflow",
            ItemType.UTILITY: "import_utility",
            ItemType.DATASET: "load_dataset",
            ItemType.DOCS: "index_documentation",
        }
        return type_actions.get(classification.type, "generic_import")

    def _determine_priority(
        self, classification: ClassificationResult, safety: SafetyDecision
    ) -> str:
        """Determine integration priority."""

        # High priority for trusted core components
        if safety.trust_tier in [TrustTier.VERIFIED, TrustTier.TRUSTED]:
            return "high"

        # High priority for essential capabilities
        essential_caps = [
            "system_component",
            "aetherra_integration",
            "plugin_interface",
        ]
        if any(cap in classification.declared_capabilities for cap in essential_caps):
            return "high"

        # Background for documentation and datasets
        if classification.type in [ItemType.DOCS, ItemType.DATASET]:
            return "background"

        return "normal"


class CoreIntegrator:
    """
    Executes integration plans by dispatching actions into core system managers.

    Minimal, safe-by-default implementation:
    - Honors dry-run mode (simulate only)
    - Skips actions when required systems are not injected
    - Best-effort name derivation from file path; idempotent where possible
    - HMR integration for safe live updates with automatic rollback
    """

    def __init__(self, service: "SelfIncorporationService"):
        self.service = service

    def _get_hmr_controller(self) -> Any:
        """Get HMR controller from service registry."""
        try:
            # Access registry through the service's service_registry
            registry = getattr(self.service, "service_registry", None)
            if registry:
                info = registry.get_service_info("hmr_controller")
                return info.instance if info else None
        except Exception as e:
            logger.debug(f"[SELFINC][HMR] Failed to get HMR controller: {e}")
        return None

    def _generate_rollback_token(self, action: str, target: dict[str, Any]) -> str:
        """Generate a unique rollback token for this integration."""
        # Standard library imports
        import uuid

        file_id = target.get("file_id", "unknown")
        timestamp = int(time.time())
        token_id = str(uuid.uuid4())[:8]
        return f"rb_{action}_{file_id[:12]}_{timestamp}_{token_id}"

    async def _record_hmr_action(
        self, action: str, target: dict[str, Any], rollback_token: str, success: bool
    ) -> None:
        """Record HMR action in audit ledger with rollback token."""
        try:
            if hasattr(self.service, "audit_ledger") and self.service.audit_ledger:
                self.service.audit_ledger.append(
                    plan_id="hmr_integration",
                    action=f"hmr_{action}",
                    status="applied" if success else "failed",
                    target=target,
                    result={
                        "rollback_token": rollback_token,
                        "hmr_enabled": self.service.config.hmr_enabled,
                        "success": success,
                    },
                )
        except Exception as e:
            logger.debug(f"[SELFINC][HMR] Failed to record HMR action: {e}")

    def _should_use_hmr(self, action: str, target: dict[str, Any]) -> bool:
        """Determine if HMR should be used for this integration."""
        if not self.service.config.hmr_enabled:
            return False

        # Use HMR for live module updates that could affect running services
        hmr_actions = {"register_plugin", "register_agent"}
        return action in hmr_actions

    def _is_locally_reversible_action(self, action: str | None) -> bool:
        """Return whether an action has a local rollback implementation."""

        return action in {"register_workflow", "load_aether_script"}

    def _hmr_supports_token_rollback(self, hmr_controller: Any) -> bool:
        """Return whether an HMR controller can roll back by token."""

        return any(
            callable(getattr(hmr_controller, attr, None))
            for attr in (
                "rollback_token",
                "rollback_by_token",
                "rollback_integration",
            )
        )

    def _hmr_supports_action_rollback(
        self, hmr_controller: Any, action: str | None
    ) -> bool:
        """Return whether HMR can roll back a specific action."""

        if not self._hmr_supports_token_rollback(hmr_controller):
            return False
        supports_action = getattr(hmr_controller, "supports_rollback_action", None)
        if callable(supports_action):
            try:
                if bool(supports_action(str(action or ""))):
                    return True
            except Exception:
                pass
        has_explicit_registration = callable(
            getattr(hmr_controller, "register_rollback_token", None)
        )
        if has_explicit_registration:
            if action == "register_plugin":
                plugin_manager = getattr(self.service, "plugin_manager", None)
                return bool(plugin_manager and hasattr(plugin_manager, "unload_plugin"))
            if action == "register_agent":
                agent_orchestrator = getattr(self.service, "agent_orchestrator", None)
                return bool(
                    agent_orchestrator
                    and any(
                        callable(getattr(agent_orchestrator, attr, None))
                        for attr in (
                            "unregister_agent",
                            "remove_agent",
                            "deregister_agent",
                        )
                    )
                )
        if callable(supports_action):
            return False
        return True

    async def _call_hmr_token_rollback(
        self,
        hmr_controller: Any,
        rollback_token: str,
    ) -> dict[str, Any]:
        """Call the HMR controller's public token rollback API."""

        for attr in ("rollback_token", "rollback_by_token", "rollback_integration"):
            rollback_fn = getattr(hmr_controller, attr, None)
            if not callable(rollback_fn):
                continue
            result = rollback_fn(rollback_token)
            if asyncio.iscoroutine(result):
                result = await result
            if isinstance(result, dict):
                return result
            return {"ok": bool(result), "method": attr}
        return {
            "ok": False,
            "error": "hmr_token_rollback_unsupported",
        }

    async def _register_hmr_rollback_token(
        self,
        hmr_controller: Any,
        *,
        rollback_token: str,
        action: str,
        result: dict[str, Any],
        target: dict[str, Any],
    ) -> dict[str, Any]:
        """Register rollback details with a token-aware HMR controller."""

        register = getattr(hmr_controller, "register_rollback_token", None)
        if not callable(register):
            return {"ok": True, "registered": False, "reason": "implicit_contract"}
        rollback_context: dict[str, Any] = {}
        if action == "register_plugin":
            rollback_context["plugin_manager"] = getattr(
                self.service, "plugin_manager", None
            )
        elif action == "register_agent":
            rollback_context["agent_orchestrator"] = getattr(
                self.service, "agent_orchestrator", None
            )
        try:
            registration = register(
                rollback_token,
                action,
                result,
                target,
                rollback_context=rollback_context,
            )
        except TypeError:
            registration = register(rollback_token, action, result, target)
        if asyncio.iscoroutine(registration):
            registration = await registration
        if isinstance(registration, dict):
            return registration
        return {"ok": bool(registration)}

    async def _execute_with_hmr(
        self, action: str, target: dict[str, Any], deps: list[str], dry_run: bool
    ) -> dict[str, Any]:
        """Execute an action with HMR support for safe live updates."""
        if dry_run:
            return await self._dispatch_action(action, target, deps, dry_run)

        hmr_controller = self._get_hmr_controller()
        if not hmr_controller:
            logger.warning(
                "[SELFINC][HMR] HMR controller not available; refusing non-dry-run HMR action"
            )
            return {
                "status": "error",
                "action": action,
                "error": "rollback_unavailable:hmr_controller_unavailable",
            }
        if not self._hmr_supports_token_rollback(hmr_controller):
            logger.warning(
                "[SELFINC][HMR] HMR controller lacks token rollback support; refusing non-dry-run HMR action"
            )
            return {
                "status": "error",
                "action": action,
                "error": "rollback_unavailable:hmr_token_rollback_unsupported",
            }
        if not self._hmr_supports_action_rollback(hmr_controller, action):
            logger.warning(
                "[SELFINC][HMR] HMR controller cannot roll back action %s; refusing non-dry-run action",
                action,
            )
            return {
                "status": "error",
                "action": action,
                "error": f"rollback_unavailable:{action}:hmr_action_rollback_unsupported",
            }

        # Generate rollback token
        rollback_token = self._generate_rollback_token(action, target)

        # Store rollback token in target for audit trail
        target_with_rollback = {**target, "rollback_token": rollback_token}

        try:
            # Execute the integration action
            result = await self._dispatch_action(
                action, target_with_rollback, deps, dry_run
            )

            # Record HMR action in audit
            success = result.get("status") == "applied"
            if success:
                registration = await self._register_hmr_rollback_token(
                    hmr_controller,
                    rollback_token=rollback_token,
                    action=action,
                    result=result,
                    target=target,
                )
                if not registration.get("ok"):
                    result = {
                        **result,
                        "status": "error",
                        "error": registration.get(
                            "error", "rollback_registration_failed"
                        ),
                    }
                    success = False
            await self._record_hmr_action(action, target, rollback_token, success)

            # Add rollback token to result
            result["rollback_token"] = rollback_token
            # Record last rollback token in service metrics for status surfaces
            try:
                # Standard library imports
                import contextlib

                with contextlib.suppress(Exception):
                    self.service.metrics["last_rollback_token"] = rollback_token
            except Exception as exc:
                logger.debug("[SELFINC] failed recording last_rollback_token: %s", exc)

            return result

        except Exception as e:
            # Record failed HMR action
            await self._record_hmr_action(action, target, rollback_token, False)
            return {
                "status": "error",
                "action": action,
                "error": f"HMR integration failed: {str(e)[:200]}",
                "rollback_token": rollback_token,
            }

    async def execute_plan(
        self, plan: dict[str, Any], dry_run: bool = False
    ) -> dict[str, Any]:
        results: list[dict[str, Any]] = []
        applied = 0
        skipped = 0
        errors = 0
        plan_id = plan.get("plan_id")

        actions = plan.get("actions", [])
        for act in actions:
            try:
                # Accept both PlanAction dataclass and dict
                if hasattr(act, "action"):
                    action_type = act.action
                    target = getattr(act, "target", {})
                    deps = getattr(act, "deps", [])
                else:
                    action_type = act.get("action")
                    target = act.get("target", {})
                    deps = act.get("deps", [])

                # Route through HMR if appropriate
                if self._should_use_hmr(action_type, target):
                    res = await self._execute_with_hmr(
                        action_type, target, deps, dry_run
                    )
                elif (
                    not dry_run
                    and self._is_locally_reversible_action(action_type)
                    and isinstance(target, dict)
                ):
                    rollback_token = self._generate_rollback_token(
                        str(action_type), target
                    )
                    target = {**target, "rollback_token": rollback_token}
                    res = await self._dispatch_action(
                        action_type, target, deps, dry_run
                    )
                    if res.get("status") == "applied":
                        res["rollback_token"] = rollback_token
                        with contextlib.suppress(Exception):
                            self.service.metrics["last_rollback_token"] = (
                                rollback_token
                            )
                else:
                    res = await self._dispatch_action(
                        action_type, target, deps, dry_run
                    )
                results.append(res)
                # Append to audit if available
                try:
                    if (
                        hasattr(self.service, "audit_ledger")
                        and self.service.audit_ledger
                    ):
                        self.service.audit_ledger.append(
                            plan_id=plan_id or "",
                            action=action_type or "",
                            status=res.get("status", "unknown"),
                            target=target or {},
                            result=res,
                        )
                except Exception as exc:
                    # Never fail plan execution due to audit logging, but record it
                    logger.debug(f"[SELFINC][AUDIT] append failed: {exc}")
                if res.get("status") == "applied":
                    applied += 1
                elif res.get("status") == "skipped":
                    skipped += 1
                else:
                    errors += 1
            except Exception as e:  # defensive - never crash whole run
                errors += 1
                results.append(
                    {
                        "status": "error",
                        "error": str(e)[:200],
                        "action": getattr(act, "action", None)
                        if hasattr(act, "action")
                        else act.get("action"),
                    }
                )

        return {
            "ok": errors == 0,
            "applied": applied,
            "skipped": skipped,
            "errors": errors,
            "results": results,
        }

    async def _dispatch_action(
        self, action: str, target: dict[str, Any], deps: list[str], dry_run: bool
    ) -> dict[str, Any]:
        file_id = target.get("file_id")
        trust = target.get("trust_tier")

        # Resolve file path and name hints
        file_item = self.service.code_index.get_file(file_id) if file_id else None
        path = file_item.path if file_item else None
        name_hint = None
        if path:
            try:
                p = Path(path)
                name_hint = p.stem
            except Exception:
                name_hint = None

        # --- register_plugin (unchanged) ---
        if action == "register_plugin":
            if dry_run:
                return {
                    "status": "skipped",
                    "reason": "dry_run",
                    "action": action,
                    "name": name_hint,
                }
            pm: Any = self.service.plugin_manager
            if not pm:
                return {
                    "status": "skipped",
                    "reason": "plugin_manager_missing",
                    "action": action,
                }
            try:
                if hasattr(pm, "load_plugin") and name_hint:
                    ok = pm.load_plugin(name_hint)
                    return {
                        "status": "applied" if ok else "error",
                        "action": action,
                        "name": name_hint,
                    }
                if hasattr(pm, "register_plugin"):
                    ok = pm.register_plugin({"name": name_hint or file_id})
                    return {
                        "status": "applied" if ok else "error",
                        "action": action,
                        "name": name_hint,
                    }
            except Exception as e:
                return {
                    "status": "error",
                    "action": action,
                    "error": str(e)[:200],
                    "name": name_hint,
                }
            return {"status": "skipped", "reason": "no_supported_api", "action": action}

        # --- register_agent (unchanged) ---
        if action == "register_agent":
            if dry_run:
                return {
                    "status": "skipped",
                    "reason": "dry_run",
                    "action": action,
                    "id": name_hint,
                }
            orch: Any = self.service.agent_orchestrator
            if not orch:
                return {
                    "status": "skipped",
                    "reason": "agent_orchestrator_missing",
                    "action": action,
                }
            try:
                agent_id = name_hint or (file_id or "agent_unknown")[-12:]
                caps = target.get("capabilities") or []
                if asyncio.iscoroutinefunction(getattr(orch, "register_agent", None)):
                    ok = await orch.register_agent(
                        agent_id=agent_id, name=agent_id, capabilities=caps
                    )
                else:
                    ok = orch.register_agent(
                        agent_id=agent_id, name=agent_id, capabilities=caps
                    )
                return {
                    "status": "applied" if ok else "error",
                    "action": action,
                    "id": agent_id,
                }
            except Exception as e:
                return {"status": "error", "action": action, "error": str(e)[:200]}

        # --- load_aether_script ---
        if action == "load_aether_script":
            # Idempotency: avoid re-execution by file hash
            if not hasattr(self, "_applied_scripts"):
                self._applied_scripts: set[str] = set()
            script_key = (
                str(file_item.hash)
                if file_item
                and hasattr(file_item, "hash")
                and file_item.hash is not None
                else str(file_id)
            )
            if script_key in self._applied_scripts:
                return {
                    "status": "skipped",
                    "reason": "already_applied",
                    "action": action,
                    "path": path,
                }
            if not path:
                return {
                    "status": "skipped",
                    "reason": "no_path",
                    "action": action,
                }
            if dry_run:
                return {
                    "status": "skipped",
                    "reason": "dry_run",
                    "action": action,
                    "path": path,
                }
            # Resolve AetherScriptService from registry or service
            svc: Any = None
            if self.service.service_registry:
                svc = self.service.service_registry.get_service("aether_script_service")
            if not svc and hasattr(self.service, "aether_script_service"):
                svc = self.service.aether_script_service
            if not svc:
                try:
                    # Aetherra imports
                    from aetherra_script_service import get_aether_script_service

                    svc = await get_aether_script_service(self.service.service_registry)
                except Exception:
                    svc = None
            if not svc:
                return {
                    "status": "skipped",
                    "reason": "aether_script_service_missing",
                    "action": action,
                    "path": path,
                }
            try:
                result = await svc.execute_script_file(path)
                self._applied_scripts.add(script_key)
                return {
                    "status": "applied" if result.get("success") else "error",
                    "action": action,
                    "path": path,
                    "script_key": script_key,
                    "rollback_scope": "selfinc_applied_script_marker",
                    "result": result,
                }
            except Exception as e:
                return {
                    "status": "error",
                    "action": action,
                    "path": path,
                    "error": str(e)[:200],
                }

        # --- register_workflow ---
        if action == "register_workflow":
            # Minimal in-memory registry for now
            if not hasattr(self.service, "_workflows"):
                self.service._workflows = {}
            workflow_name = name_hint or (file_id or "workflow")[-12:]
            if workflow_name in self.service._workflows:
                return {
                    "status": "skipped",
                    "reason": "already_registered",
                    "action": action,
                    "name": workflow_name,
                    "path": path,
                }
            if dry_run:
                return {
                    "status": "skipped",
                    "reason": "dry_run",
                    "action": action,
                    "name": workflow_name,
                    "path": path,
                }
            # Register workflow (just record for now)
            self.service._workflows[workflow_name] = {
                "path": path,
                "registered_at": datetime.now().isoformat(),
                "file_id": file_id,
                "trust": trust,
                "rollback_token": target.get("rollback_token"),
            }
            return {
                "status": "applied",
                "action": action,
                "name": workflow_name,
                "path": path,
                "rollback_token": target.get("rollback_token"),
            }

        # --- other actions ---
        if action in (
            "import_utility",
            "load_dataset",
            "index_documentation",
            "generic_import",
        ):
            return {
                "status": "skipped",
                "reason": "no_op_minimal",
                "action": action,
                "path": path,
            }

        return {"status": "skipped", "reason": "unknown_action", "action": action}


class ActivityMonitor:
    """Monitors user activity and system load to determine night cycle timing."""

    def __init__(self, config: "SelfIncorporationConfig"):
        self.config = config
        self.activity = UserActivity()
        self.monitoring = False

    def update_activity(self, interaction_type: str = "generic") -> None:
        """Update user activity timestamp."""
        self.activity.last_interaction = datetime.now()
        self.activity.interaction_count += 1

    def get_system_load(self) -> tuple[float, float]:
        """Get current CPU and memory usage.

        Note: To keep dependencies light and avoid type-stub warnings, we use a
        conservative fallback that treats the system as lightly loaded. If more
        accurate telemetry is needed, plug in a psutil-based collector behind a
        runtime-only feature flag.
        """
        return 5.0, 30.0  # Assume low usage

    def update_system_metrics(self) -> None:
        """Update current system resource usage."""
        self.activity.cpu_usage, self.activity.memory_usage = self.get_system_load()

    def is_night_cycle_time(self) -> bool:
        """Check if current time is within night cycle window."""
        now = datetime.now()
        current_hour = now.hour

        start_hour = self.config.night_start_hour
        end_hour = self.config.night_end_hour

        # Handle wrap-around (e.g., 23:00 to 03:00)
        if start_hour <= end_hour:
            return start_hour <= current_hour < end_hour
        return current_hour >= start_hour or current_hour < end_hour

    def should_start_night_cycle(self) -> bool:
        """Determine if conditions are right to start a night cycle."""
        if not self.is_night_cycle_time():
            return False

        self.update_system_metrics()

        return (
            self.activity.is_idle(idle_threshold_minutes=30)
            and self.activity.is_low_resource_usage()
        )


class LearningEngine:
    """Autonomous learning engine for night cycle improvements."""

    def __init__(
        self, config: "SelfIncorporationConfig", service: "SelfIncorporationService"
    ):
        self.config = config
        self.service = service
        self.insights_db_path = config.index_db_path.with_suffix(".insights.db")
        self._init_insights_db()

    def _init_insights_db(self) -> None:
        """Initialize the insights database."""
        conn = sqlite3.connect(self.insights_db_path)
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS learning_insights (
                    insight_id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    evidence TEXT,
                    suggested_actions TEXT,
                    priority TEXT DEFAULT 'normal',
                    timestamp TEXT NOT NULL,
                    applied INTEGER DEFAULT 0,
                    validated INTEGER DEFAULT 0
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS night_cycle_history (
                    cycle_id TEXT PRIMARY KEY,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    discoveries_processed INTEGER DEFAULT 0,
                    patterns_learned INTEGER DEFAULT 0,
                    optimizations_applied INTEGER DEFAULT 0,
                    errors_resolved INTEGER DEFAULT 0,
                    performance_improvement REAL DEFAULT 0.0,
                    quality_score REAL DEFAULT 0.0,
                    insights_generated TEXT
                )
            """
            )

            conn.commit()
        finally:
            conn.close()

    async def analyze_recent_discoveries(self) -> list[LearningInsight]:
        """Analyze recent code discoveries for learning opportunities."""
        insights: list[LearningInsight] = []

        # Get recent classifications
        recent_classifications = (
            self.service.classification_index.list_classifications()
        )
        if not recent_classifications:
            return insights

        # Pattern: High complexity files that were successfully integrated
        high_complexity_success = []
        for c in recent_classifications:
            complexity = getattr(c, "complexity_score", None)
            if (
                complexity is not None
                and complexity > 0.7
                and self._was_successfully_integrated(c.file_id)
            ):
                high_complexity_success.append(c)

        if high_complexity_success:
            insight = LearningInsight(
                insight_id=f"complexity_success_{int(time.time())}",
                category="pattern",
                description=f"Successfully integrated {len(high_complexity_success)} high-complexity files",
                confidence=0.8,
                evidence=[
                    {
                        "type": "integration_success",
                        "files": [c.file_id for c in high_complexity_success],
                        "avg_complexity": sum(
                            getattr(c, "complexity_score", 0.0)
                            for c in high_complexity_success
                        )
                        / len(high_complexity_success)
                        if high_complexity_success
                        else 0.0,
                    }
                ],
                suggested_actions=[
                    "Review integration patterns for complex files",
                    "Consider adjusting complexity thresholds",
                    "Extract successful integration strategies",
                ],
                priority="normal",
            )
            insights.append(insight)

        # Pattern: Repeated capability requests
        capability_patterns = self._analyze_capability_patterns(recent_classifications)
        if capability_patterns:
            insight = LearningInsight(
                insight_id=f"capability_patterns_{int(time.time())}",
                category="security",
                description=f"Detected {len(capability_patterns)} recurring capability patterns",
                confidence=0.7,
                evidence=[
                    {"type": "capability_frequency", "patterns": capability_patterns}
                ],
                suggested_actions=[
                    "Review capability policy effectiveness",
                    "Consider pre-approving common safe patterns",
                    "Update capability clustering rules",
                ],
                priority="normal",
            )
            insights.append(insight)

        return insights

    def _was_successfully_integrated(self, file_id: str) -> bool:
        """Check if a file was successfully integrated."""
        try:
            # Check safety index for successful integration
            safety_decision = self.service.safety_index.get_decision(file_id)
            return bool(
                safety_decision
                and getattr(safety_decision.trust_tier, "value", None)
                in [
                    "verified",
                    "trusted",
                ]
            )
        except Exception:
            return False

    def _analyze_capability_patterns(self, classifications: list) -> dict[str, int]:
        """Analyze recurring capability request patterns."""
        capability_counts: dict[str, int] = {}

        for classification in classifications:
            for capability in classification.detected_capabilities:
                capability_counts[capability] = capability_counts.get(capability, 0) + 1

        # Return capabilities requested more than once
        return {cap: count for cap, count in capability_counts.items() if count > 1}

    async def learn_from_audit_history(self) -> list[LearningInsight]:
        """Learn from historical audit data to identify improvement opportunities."""
        insights: list[LearningInsight] = []

        # Analyze audit ledger for patterns
        try:
            # Get recent audit records
            audit_records = self._get_recent_audit_records(days=7)

            # Pattern: Frequent ethics blocks
            ethics_blocks = [
                r
                for r in audit_records
                if r.get("status") == "denied" and "ethics" in str(r)
            ]
            if len(ethics_blocks) > 5:
                insight = LearningInsight(
                    insight_id=f"ethics_blocks_{int(time.time())}",
                    category="quality",
                    description=f"High number of ethics-based denials: {len(ethics_blocks)}",
                    confidence=0.9,
                    evidence=[
                        {
                            "type": "ethics_denial_frequency",
                            "count": len(ethics_blocks),
                            "timeframe": "7_days",
                        }
                    ],
                    suggested_actions=[
                        "Review ethics threshold settings",
                        "Analyze common denial patterns",
                        "Consider ethics policy adjustments",
                    ],
                    priority="high",
                )
                insights.append(insight)

            # Pattern: Performance improvements from successful integrations
            successful_integrations = [
                r for r in audit_records if r.get("status") == "applied"
            ]
            if len(successful_integrations) > 10:
                insight = LearningInsight(
                    insight_id=f"integration_success_{int(time.time())}",
                    category="performance",
                    description=f"High integration success rate: {len(successful_integrations)} successful",
                    confidence=0.8,
                    evidence=[
                        {
                            "type": "integration_success_rate",
                            "successful": len(successful_integrations),
                            "total": len(audit_records),
                        }
                    ],
                    suggested_actions=[
                        "Document successful integration patterns",
                        "Consider relaxing conservative policies",
                        "Optimize integration pipeline performance",
                    ],
                    priority="normal",
                )
                insights.append(insight)

        except Exception as e:
            logger.warning(f"[NIGHT_CYCLE] Error analyzing audit history: {e}")

        return insights

    def _get_recent_audit_records(self, days: int = 7) -> list[dict[str, Any]]:
        """Get recent audit records from the audit ledger."""
        # This would query the audit ledger database
        # For now, return empty list as placeholder
        return []

    async def store_insights(self, insights: list[LearningInsight]) -> None:
        """Store learning insights in the database."""
        if not insights:
            return

        conn = sqlite3.connect(self.insights_db_path)
        try:
            for insight in insights:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO learning_insights
                    (insight_id, category, description, confidence, evidence,
                     suggested_actions, priority, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        insight.insight_id,
                        insight.category,
                        insight.description,
                        insight.confidence,
                        json.dumps(insight.evidence),
                        json.dumps(insight.suggested_actions),
                        insight.priority,
                        insight.timestamp.isoformat(),
                    ),
                )
            conn.commit()
            logger.info(f"[NIGHT_CYCLE] Stored {len(insights)} learning insights")
        finally:
            conn.close()


class NightCycleProcessor:
    """Main night cycle processing coordinator."""

    def __init__(self, service: "SelfIncorporationService"):
        self.service = service
        self.config = service.config
        self.activity_monitor = ActivityMonitor(self.config)
        self.learning_engine = LearningEngine(self.config, service)

        self.current_phase = NightCyclePhase.INACTIVE
        self.current_metrics: NightCycleMetrics | None = None
        self.is_running = False

    async def start_monitoring(self) -> None:
        """Start monitoring for night cycle opportunities."""
        if self.is_running:
            return

        self.is_running = True
        self.current_phase = NightCyclePhase.MONITORING

        logger.info("[NIGHT_CYCLE] Started monitoring for night cycle opportunities")

        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())

    async def stop_monitoring(self) -> None:
        """Stop night cycle monitoring."""
        self.is_running = False
        self.current_phase = NightCyclePhase.INACTIVE
        logger.info("[NIGHT_CYCLE] Stopped night cycle monitoring")

    async def _monitoring_loop(self) -> None:
        """Main monitoring loop that checks for night cycle opportunities."""
        while self.is_running:
            try:
                if (
                    self.current_phase == NightCyclePhase.MONITORING
                    and self.activity_monitor.should_start_night_cycle()
                ):
                    logger.info("[NIGHT_CYCLE] Starting night cycle processing")
                    await self._run_night_cycle()

                # Check every 5 minutes
                await asyncio.sleep(300)

            except Exception as e:
                logger.error(f"[NIGHT_CYCLE] Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Brief pause on error

    async def _run_night_cycle(self) -> None:
        """Execute a complete night cycle processing session."""
        cycle_start = datetime.now()
        self.current_metrics = NightCycleMetrics(cycle_start=cycle_start)

        try:
            # Phase 1: Discovery Analysis
            self.current_phase = NightCyclePhase.DISCOVERY_ANALYSIS
            discovery_insights = await self.learning_engine.analyze_recent_discoveries()
            self.current_metrics.discoveries_processed = len(discovery_insights)

            # Phase 2: Pattern Learning
            self.current_phase = NightCyclePhase.PATTERN_LEARNING
            audit_insights = await self.learning_engine.learn_from_audit_history()
            self.current_metrics.patterns_learned = len(audit_insights)

            # Phase 3: Store insights
            all_insights = discovery_insights + audit_insights
            await self.learning_engine.store_insights(all_insights)

            # Phase 4: Optimization (placeholder for future enhancements)
            self.current_phase = NightCyclePhase.OPTIMIZATION
            optimizations_applied = await self._apply_safe_optimizations(all_insights)
            self.current_metrics.optimizations_applied = optimizations_applied

            # Phase 5: Validation
            self.current_phase = NightCyclePhase.VALIDATION
            await self._validate_night_cycle_changes()

            # Phase 6: Reporting
            self.current_phase = NightCyclePhase.REPORTING
            await self._generate_night_cycle_report(all_insights)

            # Complete cycle
            self.current_metrics.cycle_end = datetime.now()
            duration = (
                self.current_metrics.cycle_end - self.current_metrics.cycle_start
            ).total_seconds()

            logger.info(
                f"[NIGHT_CYCLE] Completed night cycle in {duration:.1f}s: "
                f"{self.current_metrics.discoveries_processed} discoveries, "
                f"{self.current_metrics.patterns_learned} patterns learned, "
                f"{self.current_metrics.optimizations_applied} optimizations applied"
            )

        except Exception as e:
            logger.error(f"[NIGHT_CYCLE] Error during night cycle: {e}")
        finally:
            self.current_phase = NightCyclePhase.MONITORING

    async def _apply_safe_optimizations(self, insights: list[LearningInsight]) -> int:
        """Apply safe optimizations based on learning insights."""
        applied_count = 0

        for insight in insights:
            if insight.confidence > 0.8 and insight.priority == "high":
                # Only apply very confident, high-priority insights
                logger.info(f"[NIGHT_CYCLE] Applying insight: {insight.description}")
                # TODO: Implement specific optimization actions
                applied_count += 1

        return applied_count

    async def _validate_night_cycle_changes(self) -> None:
        """Validate that night cycle changes didn't break anything."""
        # Run basic system health checks
        try:
            # Check service status
            if self.service.status != ServiceStatus.HEALTHY:
                logger.warning("[NIGHT_CYCLE] Service not healthy after night cycle")

            # Check database integrity
            self.service.code_index._init_database()

            logger.info("[NIGHT_CYCLE] Validation completed successfully")

        except Exception as e:
            logger.error(f"[NIGHT_CYCLE] Validation failed: {e}")

    async def _generate_night_cycle_report(
        self, insights: list[LearningInsight]
    ) -> None:
        """Generate a summary report of night cycle activities."""
        if not self.current_metrics:
            return

        report = {
            "cycle_id": f"night_{int(self.current_metrics.cycle_start.timestamp())}",
            "timestamp": self.current_metrics.cycle_start.isoformat(),
            "duration_seconds": (
                datetime.now() - self.current_metrics.cycle_start
            ).total_seconds(),
            "metrics": {
                "discoveries_processed": self.current_metrics.discoveries_processed,
                "patterns_learned": self.current_metrics.patterns_learned,
                "optimizations_applied": self.current_metrics.optimizations_applied,
                "insights_generated": len(insights),
            },
            "insights_summary": [
                {
                    "category": insight.category,
                    "confidence": insight.confidence,
                    "priority": insight.priority,
                    "description": insight.description[:100] + "..."
                    if len(insight.description) > 100
                    else insight.description,
                }
                for insight in insights
            ],
        }

        # Store in audit trail
        if hasattr(self.service, "audit_ledger"):
            self.service.audit_ledger.append(
                plan_id="night_cycle",
                action="night_cycle_complete",
                status="applied",
                target={"cycle_phase": "reporting"},
                result=report,
            )

        logger.info(
            f"[NIGHT_CYCLE] Generated report: {len(insights)} insights, "
            f"{self.current_metrics.optimizations_applied} optimizations applied"
        )


class QuarantineManager:
    """
    Manages the lifecycle of quarantined code: isolation, privilege escalation, release, and audit trail.
    Integrates with SecuritySandbox for initial isolation and supports policy-driven escalation/approval.
    """

    def __init__(
        self, audit_ledger: Any | None = None, policy_engine: Any | None = None
    ) -> None:
        self.audit_ledger = audit_ledger
        self.policy_engine = policy_engine
        self.quarantined_items: dict[str, Any] = {}  # file_id -> metadata

    @staticmethod
    def _guardian_hash_value(value: Any | None) -> str | None:
        if value is None:
            return None
        raw = str(value)
        if not raw:
            return None
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def _guardian_capability_checker(requester: str, capability: str) -> bool:
        if requester == "maintenance" and capability in {
            "maintenance:quarantine",
            "maintenance:deploy",
        }:
            return True

        from Aetherra.security.capabilities import has_capability

        return has_capability(requester, capability)

    def _guardian_preflight_quarantine_change(
        self,
        *,
        file_id: str,
        item: dict[str, Any],
        action: str,
        purpose: str,
        capabilities: tuple[str, ...],
        metadata: dict[str, Any],
        requester: str,
        approval_id: str | None,
    ):
        from Aetherra.guardian import IntentDeclaration, evaluate_intent

        return evaluate_intent(
            IntentDeclaration(
                requester=str(requester or "maintenance"),
                subsystem="maintenance",
                action=action,
                target="maintenance:self_incorporation_quarantine",
                purpose=purpose,
                capabilities=capabilities,
                evidence=(
                    "self_incorporation.QuarantineManager",
                    f"file_id_hash:{self._guardian_hash_value(file_id) or 'none'}",
                ),
                reversible=True,
                rollback_plan="restore the prior quarantine metadata from audit or re-quarantine the item",
                metadata={
                    "file_id_hash": self._guardian_hash_value(file_id),
                    "current_status": str(item.get("status") or "unknown"),
                    "reason_hash": self._guardian_hash_value(item.get("reason")),
                    **metadata,
                },
            ),
            approval_id=approval_id,
            capability_checker=self._guardian_capability_checker,
        )

    def quarantine(
        self, file_id: str, reason: str, context: dict[str, Any] | None = None
    ) -> None:
        """Place a file or code item into quarantine."""
        context = context or {}
        self.quarantined_items[file_id] = {
            "status": "quarantined",
            "reason": reason,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "escalation_level": 0,
        }
        if self.audit_ledger:
            self.audit_ledger.append(
                plan_id=file_id,
                action="quarantine",
                status="quarantined",
                target={"file_id": file_id, **context},
                result={"reason": reason},
            )

    def escalate(
        self,
        file_id: str,
        new_level: int,
        approval: str | None = None,
        *,
        requester: str = "maintenance",
        approval_id: str | None = None,
    ) -> None:
        """Escalate privileges for a quarantined item, with optional approval."""
        item = self.quarantined_items.get(file_id)
        if not item:
            raise ValueError(f"File {file_id} not in quarantine")
        decision = self._guardian_preflight_quarantine_change(
            file_id=file_id,
            item=item,
            action="maintenance.quarantine_escalate",
            purpose="Escalate a self-incorporation quarantine item for remediation or review",
            capabilities=("maintenance:quarantine",),
            metadata={
                "new_level": int(new_level),
                "has_legacy_approval_note": bool(approval),
            },
            requester=requester,
            approval_id=approval_id,
        )
        if not decision.allowed:
            raise PermissionError(f"guardian_denied:{decision.reason}")
        item["escalation_level"] = new_level
        item["status"] = "escalated"
        item["approval"] = approval
        item["escalated_at"] = datetime.now().isoformat()
        if self.audit_ledger:
            self.audit_ledger.append(
                plan_id=file_id,
                action="escalate_privilege",
                status="escalated",
                target={"file_id": file_id},
                result={"level": new_level, "approval": approval},
            )

    def release(
        self,
        file_id: str,
        approved: bool = False,
        *,
        requester: str = "maintenance",
        approval_id: str | None = None,
    ) -> None:
        """Release a quarantined item (after approval or remediation)."""
        item = self.quarantined_items.get(file_id)
        if not item:
            raise ValueError(f"File {file_id} not in quarantine")
        decision = self._guardian_preflight_quarantine_change(
            file_id=file_id,
            item=item,
            action="maintenance.quarantine_release",
            purpose="Release or reject a self-incorporation quarantine item",
            capabilities=(
                "maintenance:quarantine",
                "maintenance:deploy",
            )
            if approved
            else ("maintenance:quarantine",),
            metadata={
                "approved": bool(approved),
                "escalation_level": int(item.get("escalation_level") or 0),
            },
            requester=requester,
            approval_id=approval_id,
        )
        if not decision.allowed:
            raise PermissionError(f"guardian_denied:{decision.reason}")
        item["status"] = "released" if approved else "rejected"
        item["released_at"] = datetime.now().isoformat()
        if self.audit_ledger:
            self.audit_ledger.append(
                plan_id=file_id,
                action="release_quarantine",
                status=item["status"],
                target={"file_id": file_id},
                result={"approved": approved},
            )
        # Optionally remove from quarantine
        del self.quarantined_items[file_id]

    def get_status(self, file_id: str) -> dict[str, Any]:
        """Get quarantine status and metadata for a file."""
        result = self.quarantined_items.get(file_id, {})
        return result if isinstance(result, dict) else {}

    def list_quarantined(self) -> list[dict[str, Any]]:
        """List all currently quarantined items."""
        return [
            v for v in self.quarantined_items.values() if v["status"] == "quarantined"
        ]


class SelfIncorporationService:
    """
    Main Self-Incorporation service implementing the autonomous codebase
    perception and integration pipeline.
    """

    # Class-level attribute type declarations for type checkers
    _workflows: dict[str, Any]
    metrics: dict[str, Any]
    service_registry: Any | None
    aether_script_service: Any | None
    kernel_loop: Any | None
    plugin_manager: Any | None
    agent_orchestrator: Any | None

    def __init__(self, config: SelfIncorporationConfig | None = None):
        self.config = config or SelfIncorporationConfig()
        self.status = ServiceStatus.STARTING
        self._running = False
        # Runtime knobs (can be tuned by proposals)
        self._processing_velocity: float = 1.0  # 0.1 - 3.0
        self._optimization_hints: dict[str, Any] = {}

        # Security Layer (Phase 2B) - lazy import to avoid circular dependencies
        from Aetherra.homeostasis.self_incorporation_security import (  # noqa: E402
            SelfIncorporationSecurity,
        )

        self.security_layer = SelfIncorporationSecurity(
            trust_mode=self.config.trust_mode
        )

        # Guard Policies (Phase 2B)
        try:
            from Aetherra.homeostasis.guard_policy_enforcer import (  # noqa: E402
                GuardPolicyEnforcer,
            )

            self.guard_enforcer = GuardPolicyEnforcer(self.config.guard_policy_path)
        except Exception as _gpe:
            logger.debug("[SELFINC] Guard policy enforcer not available: %s", _gpe)
            self.guard_enforcer = None

        # Core subsystems
        self.code_index = CodeIndex(
            self.config.index_db_path, self.config.index_jsonl_path
        )
        self.classifier = HeuristicClassifier(self.config)
        self.classification_index = ClassificationIndex(
            self.config.index_db_path.with_suffix(".classification.db")
        )

        # Policy & Safety Gate
        self.policy_engine = PolicyEngine(self.config)
        # Expose unique capabilities on config for conflict resolution
        try:
            self.config.unique_capabilities = self.policy_engine.selfinc_policies.get(
                "unique_capabilities", []
            )
        except Exception:
            self.config.unique_capabilities = []
        self.security_gate = SecurityGate(self.config, self.policy_engine)
        self.safety_index = SafetyIndex(
            self.config.index_db_path.with_suffix(".safety.db")
        )

        # Integration Planner
        self.integration_planner = IntegrationPlanner(self.config)

        # Core Integrator (Phase 4)
        self.core_integrator = CoreIntegrator(self)

        # Ethics & Audit Ledger (Phase 5)
        self.audit_ledger = AuditLedger(self.config.audit_db_path)
        self.ethics_engine = EthicsEngine(self.config)  # Added ethics evaluation

        # Quarantine Manager (Phase 6)
        self.quarantine_manager = QuarantineManager(
            audit_ledger=self.audit_ledger, policy_engine=self.policy_engine
        )

        # Night Cycle Processing (Phase 5)
        self.night_cycle_processor = NightCycleProcessor(self)

        # Minimal workflow registry (in-memory)
        self._workflows = {}

        # Metrics and state
        self.metrics = {
            "files_discovered": 0,
            "files_classified": 0,
            "files_integrated": 0,
            "files_quarantined": 0,
            "proposals_executed": 0,
            "proposals_accepted": 0,
            "last_scan_duration": 0.0,
            "last_scan_timestamp": 0.0,
            "boot_completed": False,
            "night_cycles_completed": 0,
            "last_night_cycle_timestamp": 0.0,
            "night_cycle_insights": 0,
            # Guard policy observability (Phase 2B)
            "guard_rejections_total": 0,
            "guard_rejections_by_policy": {},
            "guard_last_violation": None,
        }

        # System integrations (injected by kernel)
        self.service_registry = None
        self.aether_script_service = None
        self.kernel_loop = None
        self.plugin_manager = None
        self.agent_orchestrator = None

        logger.info(f"[SELFINC] Initialized with roots: {self.config.roots}")

    def quarantine_file(
        self, file_id: str, reason: str, context: dict[str, Any] | None = None
    ) -> None:
        """Quarantine a file or code item due to suspicious or untrusted status."""
        self.quarantine_manager.quarantine(file_id, reason, context)
        self.metrics["files_quarantined"] = self.metrics.get("files_quarantined", 0) + 1
        logger.info(f"[SELFINC] Quarantined {file_id}: {reason}")

    async def start(self) -> None:
        """Start the Self-Incorporation service."""
        if not self.config.enabled:
            logger.info("[SELFINC] Service disabled via configuration")
            return

        logger.info("[SELFINC] Starting Self-Incorporation service...")
        self.status = ServiceStatus.STARTING
        self._running = True

        # Register with service registry if available
        if self.service_registry:
            await self.service_registry.register_service(
                "self_incorporation",
                self,
                metadata={
                    "version": "1.0.0",
                    "description": "Autonomous codebase incorporation system",
                    "capabilities": ["discovery", "classification", "integration"],
                    "self_heartbeat": True,
                },
            )

        self.status = ServiceStatus.HEALTHY
        logger.info("[SELFINC] Service started successfully")

    async def stop(self) -> None:
        """Stop the Self-Incorporation service."""
        logger.info("[SELFINC] Stopping Self-Incorporation service...")
        self._running = False
        self.status = ServiceStatus.STOPPING

        # Unregister from service registry
        if self.service_registry:
            await self.service_registry.unregister_service("self_incorporation")

        logger.info("[SELFINC] Service stopped")

    async def handle_message(self, message_type: str, data: dict[str, Any] | None):
        """Handle messages sent via the service registry.

        Supported messages:
        - "selfimprovement.proposal": Handle an improvement proposal payload
        - "selfinc.status": Return current status and runtime knobs
        """
        mt = (message_type or "").lower()
        payload = data or {}

        if mt.endswith("selfinc.status"):
            st = await self.get_status()
            st["runtime"] = {
                "processing_velocity": self._processing_velocity,
                "optimization_hints": self._optimization_hints,
            }
            return st

        if mt.endswith("selfimprovement.proposal"):
            try:
                return await self.handle_improvement_proposal(payload)
            except Exception as exc:
                logger.error("[SELFINC] Proposal handling failed: %s", exc)
                return {"status": "error", "error": str(exc)}

        return {"error": "unknown_message", "message_type": message_type}

    async def handle_improvement_proposal(
        self, proposal: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle improvement proposals from the Self-Improvement Engine.

        Expected proposal schema (best-effort, tolerant to missing fields):
        {
          "proposal_id": str,
          "type": "scale_up" | "optimize" | "degrade" | "change_strategy",
          "description": str,
          "params": { ... },
          "trace_id": str,
          "sender": str (optional, for authentication)
        }

        Returns a result dict with fields:
        { "status": "accepted"|"rejected"|"error", "plan_id": str, "details": { ... } }
        """
        import uuid
        from datetime import datetime as _dt

        if not isinstance(proposal, dict):
            return {"status": "error", "error": "invalid_proposal_format"}

        ptype = (
            str(proposal.get("type") or proposal.get("action") or "").strip().lower()
        )
        pid = str(proposal.get("proposal_id") or uuid.uuid4())
        trace_id = str(proposal.get("trace_id") or pid)
        params: dict[str, Any] = proposal.get("params") or {}
        sender = proposal.get("sender")

        # Safety: require service enabled and running
        if not self._running or not self.config.enabled:
            return {
                "status": "rejected",
                "reason": "service_not_available",
                "proposal_id": pid,
            }

        # Phase 2B: Guard policies pre-check (integration velocity, actuator frequency, rollback cascade)
        enforcer = getattr(self, "guard_enforcer", None)
        if enforcer is not None:
            ok, violations = enforcer.check_proposal(proposal)
            if not ok:
                logger.warning(
                    "[SELFINC] Proposal rejected by guard policies: %s",
                    ",".join(violations),
                )
                # Metrics: record guard rejection
                try:
                    self.metrics["guard_rejections_total"] = (
                        int(self.metrics.get("guard_rejections_total", 0)) + 1
                    )
                    by_pol = dict(self.metrics.get("guard_rejections_by_policy", {}))
                    key = str(violations[0] if violations else "unknown")
                    by_pol[key] = int(by_pol.get(key, 0)) + 1
                    self.metrics["guard_rejections_by_policy"] = by_pol
                    self.metrics["guard_last_violation"] = key
                except Exception as _gmx:
                    logger.debug(
                        "[SELFINC] guard rejection metrics update failed: %s", _gmx
                    )
                return {
                    "status": "rejected",
                    "reason": f"guard_violation:{violations[0]}",
                    "proposal_id": pid,
                }

        # Phase 2B: Authenticate and authorize proposal
        auth_result = await self.security_layer.authenticate_proposal(proposal, sender)
        if not auth_result.authenticated or not auth_result.authorized:
            logger.warning(
                f"[SELFINC] Proposal rejected: {auth_result.reason} (sender: {auth_result.sender})"
            )
            return {
                "status": "rejected",
                "reason": auth_result.reason,
                "proposal_id": pid,
                "sender": auth_result.sender,
            }

        # Log authenticated sender
        logger.info(f"[SELFINC] Proposal accepted from {auth_result.sender}: {ptype}")

        # Validate proposal type
        allowed_types = {"scale_up", "optimize", "degrade", "change_strategy"}
        if ptype not in allowed_types:
            return {
                "status": "rejected",
                "reason": f"unsupported_type:{ptype}",
                "proposal_id": pid,
            }

        # Increment executed proposals counter (attempt)
        from contextlib import suppress

        with suppress(Exception):
            self.metrics["proposals_executed"] = (
                int(self.metrics.get("proposals_executed", 0)) + 1
            )

        # Build a minimal action plan (in-memory) and execute safe adjustments
        plan_id = f"plan-{pid}"
        action_status = "accepted"
        details: dict[str, Any] = {
            "proposal_id": pid,
            "type": ptype,
            "executed_at": _dt.now().isoformat(),
        }

        try:
            if ptype == "scale_up":
                delta = float(params.get("delta", 0.2))
                old = self._processing_velocity
                self._processing_velocity = max(0.1, min(3.0, old + delta))
                details.update(
                    {
                        "processing_velocity": {
                            "old": old,
                            "new": self._processing_velocity,
                        }
                    }
                )

            elif ptype == "degrade":
                delta = float(params.get("delta", 0.2))
                old = self._processing_velocity
                self._processing_velocity = max(0.1, min(3.0, old - delta))
                details.update(
                    {
                        "processing_velocity": {
                            "old": old,
                            "new": self._processing_velocity,
                        }
                    }
                )

            elif ptype == "optimize":
                # Record optimization hints; optionally tune soft knobs
                hint_key = str(params.get("hint", "general"))
                hint_val = params.get("value", True)
                self._optimization_hints[hint_key] = hint_val
                # Example: adjust permissive auto-integrate list in memory (non-persistent)
                try:
                    auto_list = (
                        self.policy_engine.selfinc_policies.get("auto_integrate") or []
                    )
                    val = params.get("auto_integrate")
                    if isinstance(auto_list, list) and isinstance(val, list):
                        self.policy_engine.selfinc_policies["auto_integrate"] = list(
                            {*auto_list, *val}
                        )
                except Exception as _opt_exc:
                    logger.debug(
                        "[SELFINC][OPT] policy adjustment failed: %s", _opt_exc
                    )
                details.update({"optimization_hint": {hint_key: hint_val}})

            elif ptype == "change_strategy":
                # Strategy changes are recorded as hints; actual adoption occurs in scheduled cycles
                strategy = params.get("strategy", "conservative")
                self._optimization_hints["strategy"] = strategy
                details.update({"strategy": strategy})

            # Optional: Execute integration actions if provided by proposal
            try:
                actions = None
                # Proposal may provide actions directly or an integration_plan structure
                if isinstance(params.get("actions"), list):
                    actions = params.get("actions")
                elif isinstance(params.get("integration_plan"), dict):
                    actions = params["integration_plan"].get("actions")

                if actions:
                    async def _proposal_plan(include_experimental=False):
                        return {
                            "plan_id": plan_id,
                            "status": "ready",
                            "actions": actions,
                        }

                    original_plan_runner = self._run_integration_planning
                    self._run_integration_planning = _proposal_plan
                    try:
                        exec_res = await self.trigger_integrate(
                            dry_run=bool(params.get("dry_run", False)),
                            requester=str(auth_result.sender or "self_improvement"),
                            approval_id=params.get("guardian_approval_id"),
                            return_results=True,
                        )
                    finally:
                        self._run_integration_planning = original_plan_runner

                    if not exec_res.get("ok"):
                        action_status = "rejected"
                        details["reason"] = exec_res.get("reason") or exec_res.get(
                            "status"
                        ) or "integration_rejected"
                    details["integration"] = {
                        "applied": exec_res.get("applied"),
                        "skipped": exec_res.get("skipped"),
                        "errors": exec_res.get("errors"),
                        "status": exec_res.get("status"),
                    }
                    # If plan executed with errors, treat as rejected best-effort
                    if int(exec_res.get("errors", 0)) > 0:
                        action_status = "rejected"
                        details["reason"] = "integration_errors"
            except Exception as _iex:
                logger.debug(
                    "[SELFINC][PROPOSAL] integration execution failed: %s", _iex
                )
                action_status = "rejected"
                details["reason"] = "integration_exception"

            # Append to audit ledger for traceability
            if hasattr(self, "audit_ledger") and self.audit_ledger:
                try:
                    self.audit_ledger.append(
                        plan_id=plan_id,
                        action=f"proposal:{ptype}",
                        status=action_status,
                        target={"proposal_id": pid, "params": params},
                        result={"details": details},
                        trace_id=trace_id,
                        ethics_overall=None,
                        risk_level="low",
                    )
                except Exception as _e:
                    logger.debug("[SELFINC][AUDIT] append failed: %s", _e)

            # Increment accepted counter if applicable
            with suppress(Exception):
                if action_status == "accepted":
                    self.metrics["proposals_accepted"] = (
                        int(self.metrics.get("proposals_accepted", 0)) + 1
                    )

            # Record guard acceptance for velocity/frequency windows
            try:
                enforcer2 = getattr(self, "guard_enforcer", None)
                if enforcer2 is not None and action_status == "accepted":
                    enforcer2.record_accept(proposal)
            except Exception as _ge:
                logger.debug("[SELFINC] guard acceptance record failed: %s", _ge)

            # Notify Self-Improvement Engine best-effort
            try:
                if self.service_registry:
                    await self.service_registry.send_message(
                        "self_improvement_engine",
                        "selfimprovement.proposal_result",
                        {
                            "proposal_id": pid,
                            "plan_id": plan_id,
                            "status": action_status,
                            "details": details,
                        },
                    )
            except Exception as _e:
                logger.debug("[SELFINC] notify SIE failed: %s", _e)

            return {"status": action_status, "plan_id": plan_id, "details": details}

        except Exception as exc:
            logger.error("[SELFINC] Proposal execution error: %s", exc)
            return {"status": "error", "error": str(exc), "proposal_id": pid}

    def inject_systems(
        self,
        service_registry: Any,
        kernel_loop: Any,
        plugin_manager: Any,
        agent_orchestrator: Any,
    ) -> None:
        """Inject core system references for integration."""
        self.service_registry = service_registry
        self.kernel_loop = kernel_loop
        self.plugin_manager = plugin_manager
        self.agent_orchestrator = agent_orchestrator
        logger.info("[SELFINC] Core systems injected")

    async def health_check(self) -> dict[str, Any]:
        """Return service health status."""
        return {
            "status": self.status.value,
            "running": self._running,
            "config_enabled": self.config.enabled,
            "roots_count": len(self.config.roots),
            "metrics": self.metrics.copy(),
        }

    async def get_status(self) -> dict[str, Any]:
        """Get comprehensive status for API endpoints."""
        health = await self.health_check()

        # Count files by type and trust tier
        files_by_type = {}
        for item_type in ItemType:
            count = len(self.code_index.list_files(item_type))
            if count > 0:
                files_by_type[item_type.value] = count

        # Guard policy snapshot (if available)
        guards: dict[str, Any] = {}
        enforcer = getattr(self, "guard_enforcer", None)
        if enforcer is not None:
            try:
                # Current window counts
                iv = enforcer.policies.get("integration_velocity")
                af = enforcer.policies.get("actuator_frequency")
                rc = enforcer.policies.get("rollback_cascade")
                # Cleanup windows to get accurate counts relative to now
                now_ts = time.time()
                if iv:
                    # access private deques (read-only metrics)
                    enforcer._cleanup_window(enforcer._accepted, iv.window_sec, now_ts)  # type: ignore[attr-defined]
                if rc:
                    enforcer._cleanup_window(enforcer._rollbacks, rc.window_sec, now_ts)  # type: ignore[attr-defined]
                if af:
                    enforcer._cleanup_components(af.window_sec, now_ts)  # type: ignore[attr-defined]
                guards = {
                    "policies": {
                        "integration_velocity": {
                            "threshold": getattr(iv, "threshold", None),
                            "window_sec": getattr(iv, "window_sec", None),
                        },
                        "actuator_frequency": {
                            "threshold": getattr(af, "threshold", None),
                            "window_sec": getattr(af, "window_sec", None),
                        },
                        "rollback_cascade": {
                            "threshold": getattr(rc, "threshold", None),
                            "window_sec": getattr(rc, "window_sec", None),
                        },
                    },
                    "windows": {
                        "accepted_in_window": len(getattr(enforcer, "_accepted", [])),
                        "rollbacks_in_window": len(getattr(enforcer, "_rollbacks", [])),
                        "components_active": len(
                            getattr(enforcer, "_component_actions", {})
                        ),
                    },
                    "rejections": {
                        "total": int(self.metrics.get("guard_rejections_total", 0)),
                        "by_policy": dict(
                            self.metrics.get("guard_rejections_by_policy", {})
                        ),
                        "last_violation": self.metrics.get("guard_last_violation"),
                    },
                }
            except Exception:
                guards = {"error": "guard_metrics_unavailable"}

        return {
            **health,
            "files_by_type": files_by_type,
            "last_scan": {
                "timestamp": self.metrics["last_scan_timestamp"],
                "duration": self.metrics["last_scan_duration"],
            },
            "boot_status": {"completed": self.metrics["boot_completed"]},
            "proposals_executed": self.metrics.get("proposals_executed", 0),
            "proposals_accepted": self.metrics.get("proposals_accepted", 0),
            "last_rollback_token": self.metrics.get("last_rollback_token"),
            "guards": guards,
        }

    async def trigger_classify(self, type_filter: str | None = None) -> dict[str, Any]:
        """Trigger classification of discovered files."""
        start_time = time.time()
        logger.info(f"[SELFINC] Starting classification with filter: {type_filter}")

        classified_count = await self._run_classification(type_filter)

        duration = time.time() - start_time
        self.metrics["files_classified"] = classified_count

        return {
            "ok": True,
            "classified": classified_count,
            "duration": duration,
            "timestamp": start_time,
        }

    async def _run_classification(self, type_filter: str | None = None) -> int:
        """Execute the classification phase."""
        classified = 0

        # Get files to classify
        files_to_classify = []
        if type_filter:
            try:
                item_type = ItemType(type_filter)
                files_to_classify = self.code_index.list_files(item_type)
            except ValueError:
                logger.warning(f"[SELFINC] Invalid type filter: {type_filter}")
                return 0
        else:
            files_to_classify = self.code_index.list_files()

        for file_item in files_to_classify:
            try:
                # Check if already classified (skip if up to date)
                existing = self.classification_index.get_classification(file_item.id)
                if existing and existing.confidence > 0.5:
                    continue

                # Classify the file
                result = self.classifier.classify_file(file_item)
                self.classification_index.store_classification(result)
                classified += 1

                # Yield control periodically
                if classified % 50 == 0:
                    await asyncio.sleep(0.001)

            except Exception as e:
                logger.debug(f"[SELFINC] Failed to classify {file_item.path}: {e}")

        return classified

    async def trigger_security_eval(
        self, trust_filter: str | None = None
    ) -> dict[str, Any]:
        """Trigger security evaluation of classified files."""
        start_time = time.time()
        logger.info(
            f"[SELFINC] Starting security evaluation with filter: {trust_filter}"
        )

        evaluated_count = await self._run_security_evaluation(trust_filter)

        duration = time.time() - start_time
        self.metrics["files_evaluated"] = evaluated_count

        return {
            "ok": True,
            "evaluated": evaluated_count,
            "duration": duration,
            "timestamp": start_time,
        }

    async def _run_security_evaluation(self, trust_filter: str | None = None) -> int:
        """Execute the security evaluation phase."""
        evaluated = 0

        # Get classified files to evaluate
        classified_files = self.classification_index.list_classifications()

        for classification in classified_files:
            try:
                # Check if already evaluated (skip if up to date)
                existing = self.safety_index.get_decision(classification.file_id)
                if (
                    existing
                    and existing.trust_tier != TrustTier.QUARANTINED
                    and (not trust_filter or trust_filter == existing.trust_tier.value)
                ):
                    # Skip unless trust filter specifically requested
                    continue

                # Get file info for evaluation
                file_item = self.code_index.get_file(classification.file_id)
                if not file_item:
                    continue

                # Run security evaluation
                decision = self.security_gate.evaluate_security(
                    file_item, classification
                )
                self.safety_index.store_decision(decision)
                evaluated += 1

                # Log significant decisions and quarantine if needed
                if decision.trust_tier == TrustTier.QUARANTINED:
                    logger.info(
                        f"[SELFINC] {file_item.path} -> QUARANTINED. Triggering quarantine workflow."
                    )
                    self.quarantine_file(
                        classification.file_id,
                        reason="Security evaluation: high risk/quarantined",
                        context={"path": file_item.path},
                    )
                elif decision.trust_tier == TrustTier.VERIFIED:
                    logger.info(f"[SELFINC] {file_item.path} -> VERIFIED")

                # Yield control periodically
                if evaluated % 25 == 0:
                    await asyncio.sleep(0.001)

            except Exception as e:
                logger.debug(
                    f"[SELFINC] Failed to evaluate {classification.file_id}: {e}"
                )

        return evaluated

    async def get_trust_summary(self) -> dict[str, Any]:
        """Get summary of trust tier distributions."""
        summary = {}

        # Count by trust tier
        for tier in TrustTier:
            decisions = self.safety_index.list_by_trust_tier(tier)
            summary[tier.value] = len(decisions)

        # Recent evaluations
        conn = sqlite3.connect(self.safety_index.db_path)
        try:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM safety_decisions WHERE timestamp > datetime('now', '-1 hour')"
            )
            recent_count = cursor.fetchone()[0]
            summary["recent_evaluations"] = recent_count
        except Exception:
            summary["recent_evaluations"] = 0
        finally:
            conn.close()

        return summary

    async def trigger_planning(
        self, include_experimental: bool = False
    ) -> dict[str, Any]:
        """Trigger integration planning for evaluated components."""
        start_time = time.time()
        logger.info("[SELFINC] Starting integration planning")

        plan = await self._run_integration_planning(include_experimental)

        duration = time.time() - start_time
        self.metrics["last_plan_duration"] = duration
        self.metrics["last_plan_timestamp"] = start_time

        return {
            "ok": True,
            "plan_id": plan.get("plan_id"),
            "status": plan.get("status"),
            "total_components": plan.get("total_components", 0),
            "active_components": plan.get("active_components", 0),
            "actions": len(plan.get("actions", [])),
            "conflicts": len(plan.get("conflicts", [])),
            "duration": duration,
            "timestamp": start_time,
        }

    async def _run_integration_planning(
        self, include_experimental: bool = False
    ) -> dict[str, Any]:
        """Execute the integration planning phase."""

        # Get all classifications
        classifications = self.classification_index.list_classifications()

        # Get safety decisions, optionally including experimental
        all_decisions = []
        trust_tiers = [TrustTier.VERIFIED, TrustTier.TRUSTED, TrustTier.STANDARD]
        if include_experimental:
            trust_tiers.append(TrustTier.EXPERIMENTAL)

        for tier in trust_tiers:
            decisions = self.safety_index.list_by_trust_tier(tier)
            all_decisions.extend(decisions)

        logger.info(
            f"[SELFINC] Planning for {len(classifications)} classifications, "
            f"{len(all_decisions)} safety decisions"
        )

        # Create integration plan
        return self.integration_planner.create_integration_plan(
            classifications, all_decisions
        )

    async def _evaluate_plan_ethics(self, plan: dict[str, Any]) -> dict[str, Any]:
        """Evaluate the ethical implications of an integration plan."""
        actions = plan.get("actions", [])
        if not actions:
            # Empty plan is ethically neutral
            return {
                "overall_score": 0.7,
                "utilitarian_score": 0.7,
                "deontological_score": 0.7,
                "virtue_score": 0.7,
                "care_score": 0.7,
                "confidence": 0.9,
                "reasoning": ["Empty plan has no ethical impact"],
                "risk_factors": [],
                "ethical_benefits": [],
            }

        # Evaluate each action and aggregate scores
        action_scores = []
        all_reasoning = []
        all_risk_factors = []
        all_ethical_benefits = []

        for action in actions:
            # Extract action details
            action_type = action.get("action", "unknown")
            target = action.get("target", {})

            # Get corresponding safety decision if available
            safety_decision = None
            file_id = target.get("file_id")
            if file_id:
                safety_decision = self.safety_index.get_decision(file_id)

            # Evaluate this action
            ethics_score = self.ethics_engine.evaluate_integration(
                action_type, target, safety_decision
            )

            action_scores.append(ethics_score)
            all_reasoning.extend(ethics_score.reasoning)
            all_risk_factors.extend(ethics_score.risk_factors)
            all_ethical_benefits.extend(ethics_score.ethical_benefits)
        # Aggregate scores across all actions
        if action_scores:
            avg_overall = sum(score.overall_score for score in action_scores) / len(
                action_scores
            )
            avg_utilitarian = sum(
                score.utilitarian_score for score in action_scores
            ) / len(action_scores)
            avg_deontological = sum(
                score.deontological_score for score in action_scores
            ) / len(action_scores)
            avg_virtue = sum(score.virtue_score for score in action_scores) / len(
                action_scores
            )
            avg_care = sum(score.care_score for score in action_scores) / len(
                action_scores
            )
            avg_confidence = sum(score.confidence for score in action_scores) / len(
                action_scores
            )
        else:
            avg_overall = avg_utilitarian = avg_deontological = avg_virtue = (
                avg_care
            ) = avg_confidence = 0.5

        # Plan-level risk assessment
        plan_reasoning = [f"Evaluated {len(actions)} integration actions"]
        plan_risk_factors = []
        plan_benefits = []

        # Check for high-risk combinations
        high_risk_count = sum(1 for score in action_scores if score.overall_score < 0.4)
        if high_risk_count > 0:
            plan_risk_factors.append(f"{high_risk_count} high-risk actions in plan")
            plan_reasoning.append(
                f"PLAN: {high_risk_count} actions flagged as high risk"
            )

        # Check for capability escalation across actions
        all_capabilities = []
        for action in actions:
            target = action.get("target", {})
            capabilities = target.get("declared_capabilities", [])
            all_capabilities.extend(capabilities)

        unique_capabilities = set(all_capabilities)
        if len(unique_capabilities) > 5:
            plan_risk_factors.append("Plan introduces many new capabilities")
            plan_reasoning.append(
                f"PLAN: Introduces {len(unique_capabilities)} capabilities"
            )

        if "network" in unique_capabilities and "exec" in unique_capabilities:
            plan_risk_factors.append("Dangerous capability combination: network + exec")
            plan_reasoning.append(
                "PLAN: Risk from network + exec capability combination"
            )

        # Benefits from integration diversity
        action_types = {action.get("action", "unknown") for action in actions}
        if len(action_types) > 1:
            plan_benefits.append("Diverse integration improves system capabilities")
            plan_reasoning.append(
                f"PLAN: Benefit from {len(action_types)} different action type"
            )

        return {
            "overall_score": avg_overall,
            "utilitarian_score": avg_utilitarian,
            "deontological_score": avg_deontological,
            "virtue_score": avg_virtue,
            "care_score": avg_care,
            "confidence": avg_confidence,
            "reasoning": plan_reasoning + all_reasoning[:10],  # Limit for readability
            "risk_factors": plan_risk_factors + all_risk_factors[:10],
            "ethical_benefits": plan_benefits + all_ethical_benefits[:10],
        }

    async def trigger_integrate(
        self,
        dry_run: bool = False,
        include_experimental: bool = False,
        force: bool = False,
        return_results: bool = False,
        requester: str = "maintenance",
        approval_id: str | None = None,
    ) -> dict[str, Any]:
        """Compute a plan (or reuse logic) and execute it via CoreIntegrator.

        By default, executes only when plan status is 'ready'. Use force=True to
        proceed despite 'blocked' status (not recommended).
        """
        start_time = time.time()
        logger.info(
            "[SELFINC] Starting integration execution%s",
            " (dry-run)" if dry_run else "",
        )

        plan = await self._run_integration_planning(include_experimental)
        status = plan.get("status")
        if status != "ready" and not force:
            return {
                "ok": False,
                "plan_id": plan.get("plan_id"),
                "status": status,
                "reason": "plan_blocked",
                "actions": len(plan.get("actions", [])),
                "duration": time.time() - start_time,
            }

        from Aetherra.guardian import GuardianStatus

        guardian_decision = self._guardian_preflight_integrate(
            plan=plan,
            dry_run=dry_run,
            include_experimental=include_experimental,
            force=force,
            requester=requester,
            approval_id=approval_id,
        )
        if guardian_decision.status not in {
            GuardianStatus.ALLOW,
            GuardianStatus.ALLOW_LIMITED,
        }:
            logger.warning(
                "[SELFINC] Integration plan denied by Guardian: %s",
                guardian_decision.reason,
            )
            return {
                "ok": False,
                "plan_id": plan.get("plan_id"),
                "status": "guardian_denied",
                "reason": guardian_decision.reason,
                "guardian": guardian_decision.to_audit_dict(),
                "actions": len(plan.get("actions", [])),
                "duration": time.time() - start_time,
            }

        rollback_error = self._plan_rollback_support_error(
            plan=plan,
            dry_run=dry_run,
        )
        if rollback_error is not None:
            logger.warning(
                "[SELFINC] Integration plan blocked before execution: %s",
                rollback_error,
            )
            return {
                "ok": False,
                "plan_id": plan.get("plan_id"),
                "status": "rollback_unavailable",
                "reason": rollback_error,
                "actions": len(plan.get("actions", [])),
                "duration": time.time() - start_time,
            }

        # Ethics evaluation before execution
        ethics_evaluation = await self._evaluate_plan_ethics(plan)
        ethics_threshold = float(os.getenv("AETHERRA_ETHICS_THRESHOLD", "0.6"))

        # Derive risk level and trace id for audit
        try:
            # Standard library imports
            import hashlib
            import time as _time

            raw = f"plan:{plan.get('plan_id')}:{ethics_evaluation['overall_score']}:{_time.time()}".encode()
            plan_trace_id = hashlib.sha256(raw).hexdigest()[:16]
        except Exception:
            plan_trace_id = None
        if ethics_evaluation["overall_score"] < 0.4:
            plan_risk_level = "high"
        elif ethics_evaluation["overall_score"] < 0.6:
            plan_risk_level = "medium"
        else:
            plan_risk_level = "low"

        if ethics_evaluation["overall_score"] < ethics_threshold and not force:
            # Record ethics denial in audit
            audit_target = {
                "plan_id": plan.get("plan_id", "unknown"),
                "actions_count": len(plan.get("actions", [])),
            }
            audit_result = {
                "ethics_score": ethics_evaluation["overall_score"],
                "risk_factors": ethics_evaluation["risk_factors"],
                "threshold": ethics_threshold,
            }
            self.audit_ledger.append(
                plan_id=plan.get("plan_id", "unknown"),
                action="integration_plan",
                status="denied",
                target=audit_target,
                result=audit_result,
                trace_id=plan_trace_id,
                ethics_overall=ethics_evaluation["overall_score"],
                risk_level=plan_risk_level,
            )

            return {
                "ok": False,
                "plan_id": plan.get("plan_id"),
                "status": "ethics_blocked",
                "reason": "ethics_evaluation_failed",
                "ethics_score": ethics_evaluation["overall_score"],
                "risk_factors": ethics_evaluation["risk_factors"],
                "actions": len(plan.get("actions", [])),
                "duration": time.time() - start_time,
            }

        exec_result = await self.core_integrator.execute_plan(plan, dry_run=dry_run)
        execution_results = exec_result.get("results", [])
        rollback_tokens = [
            str(item.get("rollback_token"))
            for item in execution_results
            if isinstance(item, dict) and item.get("rollback_token")
        ]
        if exec_result.get("ok"):
            self.metrics["files_integrated"] = self.metrics.get(
                "files_integrated", 0
            ) + exec_result.get("applied", 0)

        # Record applied plan ethics audit
        # Standard library imports
        import contextlib

        with contextlib.suppress(Exception):
            self.audit_ledger.append(
                plan_id=plan.get("plan_id", "unknown"),
                action="integration_plan",
                status="applied" if exec_result.get("ok") else "failed",
                target={
                    "plan_id": plan.get("plan_id"),
                    "actions_count": len(plan.get("actions", [])),
                },
                result={
                    "ethics_score": ethics_evaluation.get("overall_score"),
                    "risk_factors": ethics_evaluation.get("risk_factors", []),
                    "applied": exec_result.get("applied"),
                    "errors": exec_result.get("errors"),
                    "rollback_token_count": len(rollback_tokens),
                },
                trace_id=plan_trace_id,
                ethics_overall=ethics_evaluation.get("overall_score"),
                risk_level=plan_risk_level,
            )

        result: dict[str, Any] = {
            "ok": exec_result.get("ok", False),
            "plan_id": plan.get("plan_id"),
            "status": status,
            "applied": exec_result.get("applied", 0),
            "skipped": exec_result.get("skipped", 0),
            "errors": exec_result.get("errors", 0),
            "duration": time.time() - start_time,
        }
        if rollback_tokens:
            result["rollback_tokens"] = rollback_tokens
            result["last_rollback_token"] = rollback_tokens[-1]
        if return_results:
            result["results"] = execution_results
        return result

    async def get_integration_status(self) -> dict[str, Any]:
        """Get current integration planning status and metrics."""

        # Count components by status
        classifications = self.classification_index.list_classifications()

        trust_counts: dict[str, int] = {}
        for tier in TrustTier:
            decisions = self.safety_index.list_by_trust_tier(tier)
            trust_counts[tier.value] = len(decisions)

        type_counts: dict[str, int] = {}
        for classification in classifications:
            item_type = classification.type.value
            type_counts[item_type] = type_counts.get(item_type, 0) + 1

        return {
            "total_discovered": sum(type_counts.values()),
            "trust_distribution": trust_counts,
            "type_distribution": type_counts,
            "ready_for_planning": trust_counts.get("verified", 0)
            + trust_counts.get("trusted", 0)
            + trust_counts.get("standard", 0),
            "planning_metrics": {
                "last_plan_duration": self.metrics.get("last_plan_duration", 0.0),
                "last_plan_timestamp": self.metrics.get("last_plan_timestamp", 0.0),
            },
        }

    @staticmethod
    def _guardian_hash_value(value: Any | None) -> str | None:
        if value is None:
            return None
        raw = str(value)
        if not raw:
            return None
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _guardian_capability_checker(self, requester: str, capability: str) -> bool:
        if requester == "maintenance" and capability in {
            "maintenance:deploy",
            "maintenance:plan",
            "maintenance:rollback",
            "system:reload",
        }:
            return True
        from Aetherra.security.capabilities import has_capability

        return has_capability(requester, capability)

    def _guardian_canary_capabilities(self, dry_run: bool) -> tuple[str, ...]:
        capabilities = ["maintenance:plan", "maintenance:deploy"]
        if not dry_run:
            capabilities.append("system:reload")
        return tuple(capabilities)

    def _guardian_integrate_capabilities(
        self, *, plan: dict[str, Any], dry_run: bool
    ) -> tuple[str, ...]:
        capabilities = ["maintenance:plan"]
        if not dry_run:
            capabilities.append("maintenance:deploy")
            actions = plan.get("actions", [])
            if not isinstance(actions, list):
                actions = []
            hmr_actions = {"register_plugin", "register_agent", "load_aether_script"}
            uses_hmr = any(
                isinstance(action, dict)
                and str(action.get("action") or "").strip() in hmr_actions
                for action in actions
            )
            if self.config.hmr_enabled and uses_hmr:
                capabilities.append("system:reload")
        return tuple(capabilities)

    def _guardian_plan_metadata(
        self,
        *,
        plan: dict[str, Any],
        tracking_plan_id: str | None,
        canary_percent: float,
        canary_duration: int,
        health_check_interval: int,
        rollback_threshold: float,
        dry_run: bool,
    ) -> dict[str, Any]:
        actions = plan.get("actions", [])
        if not isinstance(actions, list):
            actions = []
        action_types = sorted(
            {
                str(action.get("action") or action.get("op") or "unknown")[:80]
                for action in actions
                if isinstance(action, dict)
            }
        )
        return {
            "tracking_plan_id_hash": self._guardian_hash_value(tracking_plan_id),
            "generated_plan_id_hash": self._guardian_hash_value(plan.get("plan_id")),
            "plan_status": str(plan.get("status") or "unknown"),
            "actions_count": len(actions),
            "action_types": tuple(action_types[:10]),
            "canary_percent": float(canary_percent),
            "canary_duration": int(canary_duration),
            "health_check_interval": int(health_check_interval),
            "rollback_threshold": float(rollback_threshold),
            "dry_run": bool(dry_run),
        }

    def _guardian_preflight_canary(
        self,
        *,
        plan: dict[str, Any],
        tracking_plan_id: str | None,
        canary_percent: float,
        canary_duration: int,
        health_check_interval: int,
        rollback_threshold: float,
        dry_run: bool,
        requester: str,
        approval_id: str | None,
    ):
        from Aetherra.guardian import IntentDeclaration, evaluate_intent

        generated_plan_id_hash = self._guardian_hash_value(plan.get("plan_id"))
        return evaluate_intent(
            IntentDeclaration(
                requester=str(requester or "maintenance"),
                subsystem="maintenance",
                action="maintenance.canary_deploy",
                target="maintenance:canary_deployment",
                purpose="Evaluate and execute a canary deployment for a self-incorporation plan",
                capabilities=self._guardian_canary_capabilities(dry_run),
                evidence=(
                    "self_incorporation.integrate_with_canary",
                    f"plan_id_hash:{generated_plan_id_hash or 'none'}",
                ),
                reversible=True,
                rollback_plan="use the generated HMR rollback token through self-incorporation rollback",
                metadata=self._guardian_plan_metadata(
                    plan=plan,
                    tracking_plan_id=tracking_plan_id,
                    canary_percent=canary_percent,
                    canary_duration=canary_duration,
                    health_check_interval=health_check_interval,
                    rollback_threshold=rollback_threshold,
                    dry_run=dry_run,
                ),
            ),
            approval_id=approval_id,
            capability_checker=self._guardian_capability_checker,
        )

    def _guardian_preflight_integrate(
        self,
        *,
        plan: dict[str, Any],
        dry_run: bool,
        include_experimental: bool,
        force: bool,
        requester: str,
        approval_id: str | None,
    ):
        from Aetherra.guardian import IntentDeclaration, evaluate_intent

        generated_plan_id_hash = self._guardian_hash_value(plan.get("plan_id"))
        return evaluate_intent(
            IntentDeclaration(
                requester=str(requester or "maintenance"),
                subsystem="maintenance",
                action="maintenance.integrate_plan",
                target="maintenance:self_incorporation_plan",
                purpose="Execute a self-incorporation integration plan",
                capabilities=self._guardian_integrate_capabilities(
                    plan=plan,
                    dry_run=dry_run,
                ),
                expected_outcome="Self-incorporation plan is executed or simulated under existing safety gates",
                evidence=(
                    "self_incorporation.trigger_integrate",
                    f"plan_id_hash:{generated_plan_id_hash or 'none'}",
                ),
                reversible=True,
                rollback_plan="restore from generated integration audit/HMR rollback records or skip dry-run changes",
                metadata={
                    **self._guardian_plan_metadata(
                        plan=plan,
                        tracking_plan_id=None,
                        canary_percent=0.0,
                        canary_duration=0,
                        health_check_interval=0,
                        rollback_threshold=0.0,
                        dry_run=dry_run,
                    ),
                    "include_experimental": bool(include_experimental),
                    "force": bool(force),
                },
            ),
            approval_id=approval_id,
            capability_checker=self._guardian_capability_checker,
        )

    def _plan_rollback_support_error(
        self,
        *,
        plan: dict[str, Any],
        dry_run: bool,
    ) -> str | None:
        """Return a failure reason when a non-dry-run plan cannot be rolled back."""

        if dry_run:
            return None

        actions = plan.get("actions", [])
        if not isinstance(actions, list):
            return "invalid_actions"

        hmr_actions = {"register_plugin", "register_agent"}
        local_actions = {"register_workflow", "load_aether_script"}
        for item in actions:
            if hasattr(item, "action"):
                action = str(getattr(item, "action") or "")
            elif isinstance(item, dict):
                action = str(item.get("action") or "")
            else:
                return "invalid_action_entry"

            if not action:
                return "missing_action"
            if action in local_actions:
                continue
            if action in hmr_actions:
                if not self.config.hmr_enabled:
                    return f"rollback_unavailable:{action}:hmr_disabled"
                hmr_controller = self.core_integrator._get_hmr_controller()
                if not hmr_controller:
                    return f"rollback_unavailable:{action}:hmr_controller_unavailable"
                if not self.core_integrator._hmr_supports_token_rollback(
                    hmr_controller
                ):
                    return f"rollback_unavailable:{action}:hmr_token_rollback_unsupported"
                if not self.core_integrator._hmr_supports_action_rollback(
                    hmr_controller,
                    action,
                ):
                    return f"rollback_unavailable:{action}:hmr_action_rollback_unsupported"
                continue

        return None

    def _guardian_preflight_rollback(
        self,
        *,
        rollback_token: str,
        requester: str,
        approval_id: str | None,
    ):
        from Aetherra.guardian import IntentDeclaration, evaluate_intent

        token_hash = self._guardian_hash_value(rollback_token)
        return evaluate_intent(
            IntentDeclaration(
                requester=str(requester or "maintenance"),
                subsystem="maintenance",
                action="maintenance.rollback",
                target="maintenance:rollback_token",
                purpose="Rollback a self-incorporation integration using an HMR rollback token",
                capabilities=("maintenance:rollback",),
                evidence=(
                    "self_incorporation.trigger_rollback",
                    f"rollback_token_hash:{token_hash or 'none'}",
                ),
                reversible=True,
                rollback_plan="re-run the canary deployment only after health and policy checks pass",
                metadata={
                    "rollback_token_hash": token_hash,
                    "rollback_token_length": len(rollback_token or ""),
                    "hmr_enabled": bool(self.config.hmr_enabled),
                },
            ),
            approval_id=approval_id,
            capability_checker=self._guardian_capability_checker,
        )

    def _find_rollback_audit_records(
        self, rollback_token: str
    ) -> list[dict[str, Any]]:
        """Find audit records that reference a rollback token."""

        if not hasattr(self, "audit_ledger") or not self.audit_ledger:
            return []
        all_records = self.audit_ledger.recent(limit=1000)
        return [
            record
            for record in all_records
            if record.get("result", {}).get("rollback_token") == rollback_token
        ]

    async def _execute_local_rollback(
        self,
        audit_record: dict[str, Any],
        rollback_token: str,
    ) -> dict[str, Any]:
        """Execute a local rollback for supported bounded actions."""

        action = str(audit_record.get("action") or "")
        result = audit_record.get("result") or {}
        if action == "register_workflow":
            workflow_name = str(result.get("name") or "").strip()
            workflows = getattr(self, "_workflows", None)
            if not workflow_name:
                return {
                    "ok": False,
                    "error": "rollback_target_missing",
                    "action": action,
                }
            if not isinstance(workflows, dict):
                return {
                    "ok": False,
                    "error": "workflow_registry_missing",
                    "action": action,
                    "workflow": workflow_name,
                }
            existing = workflows.get(workflow_name)
            if existing is None:
                return {
                    "ok": False,
                    "error": "rollback_target_not_found",
                    "action": action,
                    "workflow": workflow_name,
                }
            if existing.get("rollback_token") != rollback_token:
                return {
                    "ok": False,
                    "error": "rollback_token_mismatch",
                    "action": action,
                    "workflow": workflow_name,
                }
            del workflows[workflow_name]
            return {
                "ok": True,
                "action": action,
                "workflow": workflow_name,
                "status": "rolled_back",
            }

        if action == "load_aether_script":
            script_key = str(result.get("script_key") or "").strip()
            applied_scripts = getattr(self.core_integrator, "_applied_scripts", None)
            if not script_key:
                return {
                    "ok": False,
                    "error": "rollback_target_missing",
                    "action": action,
                }
            if not isinstance(applied_scripts, set):
                return {
                    "ok": False,
                    "error": "script_marker_registry_missing",
                    "action": action,
                }
            if script_key not in applied_scripts:
                return {
                    "ok": False,
                    "error": "rollback_target_not_found",
                    "action": action,
                }
            applied_scripts.remove(script_key)
            return {
                "ok": True,
                "action": action,
                "status": "rolled_back",
                "rollback_scope": "selfinc_applied_script_marker",
            }

        if action in {
            "register_plugin",
            "register_agent",
            "hmr_register_plugin",
            "hmr_register_agent",
            "hmr_load_aether_script",
        }:
            hmr_controller = self.core_integrator._get_hmr_controller()
            if not hmr_controller:
                return {
                    "ok": False,
                    "error": "hmr_controller_unavailable",
                    "action": action,
                }
            if not self.core_integrator._hmr_supports_token_rollback(hmr_controller):
                return {
                    "ok": False,
                    "error": "hmr_token_rollback_unsupported",
                    "action": action,
                }
            rollback_result = await self.core_integrator._call_hmr_token_rollback(
                hmr_controller,
                rollback_token,
            )
            return {
                "ok": bool(rollback_result.get("ok")),
                "action": action,
                "status": "rolled_back"
                if rollback_result.get("ok")
                else "rollback_failed",
                "hmr": rollback_result,
                **(
                    {}
                    if rollback_result.get("ok")
                    else {"error": rollback_result.get("error", "hmr_rollback_failed")}
                ),
            }

        return {
            "ok": False,
            "error": "rollback_operation_unsupported",
            "action": action or "unknown",
        }

    async def trigger_rollback(
        self,
        rollback_token: str,
        requester: str = "maintenance",
        approval_id: str | None = None,
    ) -> dict[str, Any]:
        """Rollback an integration using HMR rollback token."""
        start_time = time.time()
        token_hash = self._guardian_hash_value(rollback_token)
        logger.info("[SELFINC] Starting rollback for token hash: %s", token_hash)

        if not rollback_token or not rollback_token.startswith("rb_"):
            return {
                "ok": False,
                "error": "invalid_rollback_token",
                "token": rollback_token,
                "duration": time.time() - start_time,
            }

        try:
            from Aetherra.guardian import GuardianStatus

            guardian_decision = self._guardian_preflight_rollback(
                rollback_token=rollback_token,
                requester=requester,
                approval_id=approval_id,
            )
            if guardian_decision.status not in {
                GuardianStatus.ALLOW,
                GuardianStatus.ALLOW_LIMITED,
            }:
                logger.warning(
                    "[SELFINC][HMR] Rollback denied by Guardian: %s",
                    guardian_decision.reason,
                )
                return {
                    "ok": False,
                    "error": f"guardian_denied:{guardian_decision.reason}",
                    "guardian": guardian_decision.to_audit_dict(),
                    "duration": time.time() - start_time,
                }

            # Guard policy: check rollback cascade before proceeding
            enforcer = getattr(self, "guard_enforcer", None)
            if enforcer is not None:
                ok, violations = enforcer.check_proposal(
                    {"type": "rollback", "params": {}}
                )
                if not ok:
                    logger.warning(
                        "[SELFINC] Rollback rejected by guard policies: %s",
                        ",".join(violations),
                    )
                    # Metrics: record guard rejection
                    try:
                        self.metrics["guard_rejections_total"] = (
                            int(self.metrics.get("guard_rejections_total", 0)) + 1
                        )
                        by_pol = dict(
                            self.metrics.get("guard_rejections_by_policy", {})
                        )
                        key = str(violations[0] if violations else "unknown")
                        by_pol[key] = int(by_pol.get(key, 0)) + 1
                        self.metrics["guard_rejections_by_policy"] = by_pol
                        self.metrics["guard_last_violation"] = key
                    except Exception as _gmx2:
                        logger.debug(
                            "[SELFINC] guard rejection metrics update failed: %s", _gmx2
                        )
                    return {
                        "ok": False,
                        "error": f"guard_violation:{violations[0]}",
                        "token": rollback_token,
                        "duration": time.time() - start_time,
                    }
            audit_records = self._find_rollback_audit_records(rollback_token)

            if not audit_records:
                return {
                    "ok": False,
                    "error": "rollback_token_not_found",
                    "token": rollback_token,
                    "duration": time.time() - start_time,
                }

            rollback_result = await self._execute_local_rollback(
                audit_records[0],
                rollback_token,
            )
            if not rollback_result.get("ok"):
                return {
                    "ok": False,
                    "error": rollback_result.get("error", "rollback_failed"),
                    "token": rollback_token,
                    "affected_integrations": len(audit_records),
                    "duration": time.time() - start_time,
                    "details": {
                        key: value
                        for key, value in rollback_result.items()
                        if key not in {"ok", "error"}
                    },
                }

            # Record the rollback attempt in audit
            if hasattr(self, "audit_ledger") and self.audit_ledger:
                self.audit_ledger.append(
                    plan_id="rollback",
                    action="selfinc_rollback",
                    status="applied",
                    target={
                        "rollback_token_hash": token_hash,
                        "rolled_back_action": rollback_result.get("action"),
                    },
                    result={
                        "rollback_token_hash": token_hash,
                        "affected_integrations": len(audit_records),
                        "rollback": rollback_result,
                        "timestamp": time.time(),
                    },
                )
                # Update guard windows for rollback cascade tracking
                if enforcer is not None:
                    enforcer.record_rollback()

            return {
                "ok": True,
                "token": rollback_token,
                "affected_integrations": len(audit_records),
                "rollback": rollback_result,
                "duration": time.time() - start_time,
            }

        except Exception as e:
            logger.error(f"[SELFINC][HMR] Rollback failed: {e}")
            return {
                "ok": False,
                "error": f"rollback_failed: {str(e)[:200]}",
                "token": rollback_token,
                "duration": time.time() - start_time,
            }

    async def integrate_with_canary(
        self,
        plan_id: str | None = None,
        canary_percent: float = 0.1,
        canary_duration: int = 300,
        health_check_interval: int = 10,
        rollback_threshold: float = 0.9,
        dry_run: bool = False,
        requester: str = "maintenance",
        approval_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Integrate new capability using canary deployment strategy.

        Flow:
        1. Generate integration plan (or use provided plan_id)
        2. Record baseline health metrics
        3. Execute integration with HMR
        4. Monitor health for canary_duration seconds at health_check_interval
        5. Auto-rollback if health drops below rollback_threshold
        6. Return canary status: canary_stable or auto_rollback

        Args:
            plan_id: Optional existing plan ID to use (otherwise generates new plan)
            canary_percent: Percentage of traffic for canary (0.0-1.0) [default: 0.1 = 10%]
            canary_duration: Duration in seconds to monitor canary health [default: 300 = 5 min]
            health_check_interval: Seconds between health checks [default: 10]
            rollback_threshold: Minimum health score to keep canary (0.0-1.0) [default: 0.9]
            dry_run: If True, simulate without actual integration
            requester: Security principal requesting the maintenance operation
            approval_id: Optional Guardian approval request ID for high-risk environments

        Returns:
            {
                "ok": bool,
                "status": "canary_stable" | "auto_rollback" | "error",
                "deployment": "canary_promoted" | "canary_failed",
                "plan_id": str,
                "rollback_token": str | None,
                "baseline_health": float,
                "canary_health_samples": list[float],
                "min_health": float,
                "max_health": float,
                "avg_health": float,
                "health_delta": float,
                "rollback_reason": str | None,
                "duration": float,
            }
        """
        start_time = time.time()
        logger.info(
            f"[SELFINC][CANARY] Starting canary deployment (canary_percent={canary_percent:.1%}, duration={canary_duration}s)"
        )

        # Step 1: Generate integration plan
        # Note: plan_id parameter is for logging/tracking only; plans are not cached
        logger.info(
            f"[SELFINC][CANARY] Generating integration plan{f' (tracking: {plan_id})' if plan_id else ''}"
        )
        plan = await self._run_integration_planning(include_experimental=False)
        generated_plan_id = plan.get("plan_id")

        if plan.get("status") != "ready":
            return {
                "ok": False,
                "status": "error",
                "error": "plan_not_ready",
                "plan_id": generated_plan_id,
                "plan_status": plan.get("status"),
                "duration": time.time() - start_time,
            }

        # Check HMR availability
        if not self.config.hmr_enabled:
            logger.warning(
                "[SELFINC][CANARY] HMR disabled, cannot use canary deployment"
            )
            return {
                "ok": False,
                "status": "error",
                "error": "hmr_disabled",
                "plan_id": generated_plan_id,
                "duration": time.time() - start_time,
            }

        hmr_controller = None
        if self.service_registry:
            info = self.service_registry.get_service_info("hmr_controller")
            hmr_controller = info.instance if info else None

        if not hmr_controller:
            logger.warning("[SELFINC][CANARY] HMR controller unavailable")
            return {
                "ok": False,
                "status": "error",
                "error": "hmr_controller_unavailable",
                "plan_id": generated_plan_id,
                "duration": time.time() - start_time,
            }

        rollback_support_error = self._plan_rollback_support_error(
            plan=plan,
            dry_run=dry_run,
        )
        if rollback_support_error is not None:
            logger.warning(
                "[SELFINC][CANARY] Rollback support unavailable: %s",
                rollback_support_error,
            )
            return {
                "ok": False,
                "status": "error",
                "error": rollback_support_error,
                "plan_id": generated_plan_id,
                "duration": time.time() - start_time,
            }

        from Aetherra.guardian import GuardianStatus

        guardian_decision = self._guardian_preflight_canary(
            plan=plan,
            tracking_plan_id=plan_id,
            canary_percent=canary_percent,
            canary_duration=canary_duration,
            health_check_interval=health_check_interval,
            rollback_threshold=rollback_threshold,
            dry_run=dry_run,
            requester=requester,
            approval_id=approval_id,
        )
        if guardian_decision.status not in {
            GuardianStatus.ALLOW,
            GuardianStatus.ALLOW_LIMITED,
        }:
            logger.warning(
                "[SELFINC][CANARY] Canary deployment denied by Guardian: %s",
                guardian_decision.reason,
            )
            return {
                "ok": False,
                "status": "error",
                "error": f"guardian_denied:{guardian_decision.reason}",
                "plan_id": generated_plan_id,
                "guardian": guardian_decision.to_audit_dict(),
                "duration": time.time() - start_time,
            }

        # Step 2: Record baseline health
        baseline_health = await self._get_system_health_score()
        logger.info(f"[SELFINC][CANARY] Baseline health: {baseline_health:.2f}")

        if baseline_health < rollback_threshold:
            logger.warning(
                f"[SELFINC][CANARY] Baseline health ({baseline_health:.2f}) below rollback threshold ({rollback_threshold:.2f})"
            )
            return {
                "ok": False,
                "status": "error",
                "error": "baseline_health_too_low",
                "plan_id": generated_plan_id,
                "baseline_health": baseline_health,
                "rollback_threshold": rollback_threshold,
                "duration": time.time() - start_time,
            }

        # Step 3: Execute integration with HMR
        rollback_token = None
        if not dry_run:
            logger.info("[SELFINC][CANARY] Executing integration with HMR")
            exec_result = await self.core_integrator.execute_plan(plan, dry_run=False)

            if not exec_result.get("ok"):
                return {
                    "ok": False,
                    "status": "error",
                    "error": "integration_failed",
                    "plan_id": generated_plan_id,
                    "exec_result": exec_result,
                    "duration": time.time() - start_time,
                }

            # Extract rollback token from last applied action
            rollback_token = self.metrics.get("last_rollback_token")
            logger.info(
                f"[SELFINC][CANARY] Integration complete, rollback token: {rollback_token}"
            )

            if exec_result.get("applied", 0) > 0:
                self.metrics["files_integrated"] = self.metrics.get(
                    "files_integrated", 0
                ) + exec_result.get("applied", 0)

        # Step 4: Monitor health during canary period
        health_samples: list[float] = []
        num_checks = max(1, canary_duration // health_check_interval)

        logger.info(
            f"[SELFINC][CANARY] Monitoring health for {canary_duration}s ({num_checks} checks)"
        )

        for check_num in range(num_checks):
            if dry_run:
                # Simulate stable health in dry-run
                current_health = baseline_health
            else:
                await asyncio.sleep(health_check_interval)
                current_health = await self._get_system_health_score()

            health_samples.append(current_health)
            logger.debug(
                f"[SELFINC][CANARY] Health check {check_num + 1}/{num_checks}: {current_health:.2f}"
            )

            # Check for health degradation
            if current_health < rollback_threshold:
                logger.warning(
                    f"[SELFINC][CANARY] Health degraded to {current_health:.2f} (threshold: {rollback_threshold:.2f})"
                )

                # Step 5: Auto-rollback on health degradation
                if not dry_run and rollback_token:
                    logger.error("[SELFINC][CANARY] Triggering automatic rollback")
                    rollback_result = await self.trigger_rollback(rollback_token)

                    if rollback_result.get("ok"):
                        logger.info("[SELFINC][CANARY] Rollback successful")
                    else:
                        logger.error(
                            f"[SELFINC][CANARY] Rollback failed: {rollback_result.get('error')}"
                        )

                # Record canary failure metrics
                self.metrics["canary_deployments_failed"] = (
                    self.metrics.get("canary_deployments_failed", 0) + 1
                )

                return {
                    "ok": False,
                    "status": "auto_rollback",
                    "deployment": "canary_failed",
                    "plan_id": generated_plan_id,
                    "rollback_token": rollback_token,
                    "baseline_health": baseline_health,
                    "canary_health_samples": health_samples,
                    "min_health": min(health_samples) if health_samples else 0.0,
                    "max_health": max(health_samples) if health_samples else 0.0,
                    "avg_health": (
                        sum(health_samples) / len(health_samples)
                        if health_samples
                        else 0.0
                    ),
                    "health_delta": current_health - baseline_health,
                    "rollback_reason": f"health_below_threshold ({current_health:.2f} < {rollback_threshold:.2f})",
                    "checks_completed": len(health_samples),
                    "duration": time.time() - start_time,
                }

        # All health checks passed - canary stable
        min_health = min(health_samples) if health_samples else baseline_health
        max_health = max(health_samples) if health_samples else baseline_health
        avg_health = (
            sum(health_samples) / len(health_samples)
            if health_samples
            else baseline_health
        )

        logger.info(
            f"[SELFINC][CANARY] Canary stable! Health: min={min_health:.2f}, max={max_health:.2f}, avg={avg_health:.2f}"
        )

        # Record successful canary metrics
        if not dry_run:
            self.metrics["canary_deployments_successful"] = (
                self.metrics.get("canary_deployments_successful", 0) + 1
            )

        return {
            "ok": True,
            "status": "canary_stable",
            "deployment": "canary_promoted",
            "plan_id": generated_plan_id,
            "rollback_token": rollback_token,
            "baseline_health": baseline_health,
            "canary_health_samples": health_samples,
            "min_health": min_health,
            "max_health": max_health,
            "avg_health": avg_health,
            "health_delta": avg_health - baseline_health,
            "rollback_reason": None,
            "checks_completed": len(health_samples),
            "duration": time.time() - start_time,
        }

    async def _get_system_health_score(self) -> float:
        """
        Get current system health score from Homeostasis.

        Returns:
            float: Health score 0.0-1.0, or 0.95 if homeostasis unavailable
        """
        try:
            if self.service_registry:
                info = self.service_registry.get_service_info("homeostasis_system")
                if info and hasattr(info.instance, "get_system_health_status"):
                    status = await info.instance.get_system_health_status()
                    system_health = status.get("system_health", {})
                    health_score = system_health.get("health_score", 0.95)
                    # Convert from 0-100 to 0.0-1.0 if needed
                    if health_score > 1.0:
                        health_score = health_score / 100.0
                    return float(health_score)
        except Exception as e:
            logger.debug(f"[SELFINC][CANARY] Failed to get health score: {e}")

        # Default to healthy if homeostasis unavailable
        return 0.95

    async def get_planning_details(
        self, include_experimental: bool = False, limit: int = 50
    ) -> dict[str, Any]:
        """Return detailed planning diagnostics: cycles and conflicts.

        Note: This runs a planning pass to collect data but does not persist any state.
        """
        plan = await self._run_integration_planning(include_experimental)

        # Truncate large lists for readability
        def _truncate(seq: Any) -> list[Any]:
            try:
                return list(seq)[: max(0, int(limit))]
            except Exception:
                return []

        return {
            "plan_id": plan.get("plan_id"),
            "status": plan.get("status"),
            "dependency_cycles": _truncate(plan.get("dependency_cycles", [])),
            "conflicts": _truncate(plan.get("conflicts", [])),
            "resolved_conflicts": _truncate(plan.get("resolved_conflicts", [])),
            "unresolved_conflicts": _truncate(plan.get("unresolved_conflicts", [])),
            "actions": _truncate(plan.get("actions", [])),
            "totals": {
                "cycles": len(plan.get("dependency_cycles", [])),
                "conflicts": len(plan.get("conflicts", [])),
                "resolved_conflicts": len(plan.get("resolved_conflicts", [])),
                "unresolved_conflicts": len(plan.get("unresolved_conflicts", [])),
                "actions": len(plan.get("actions", [])),
            },
        }

    async def trigger_scan(self, root_filter: str | None = None) -> dict[str, Any]:
        """Trigger a discovery scan with optional path filter."""
        start_time = time.time()
        logger.info(f"[SELFINC] Starting scan with filter: {root_filter}")

        discovered_count = await self._run_discovery(root_filter)

        duration = time.time() - start_time
        self.metrics["last_scan_duration"] = duration
        self.metrics["last_scan_timestamp"] = start_time

        return {
            "ok": True,
            "discovered": discovered_count,
            "duration": duration,
            "timestamp": start_time,
        }

    async def _run_discovery(self, root_filter: str | None = None) -> int:
        """Execute the code discovery phase."""
        discovered = 0

        roots_to_scan = self.config.roots
        if root_filter:
            # Filter roots by the provided pattern
            filter_path = Path(root_filter).resolve()
            filtered_roots = []

            for root in self.config.roots:
                root_resolved = root.resolve()
                # Check if filter_path is under this root or vice versa
                try:
                    if filter_path == root_resolved:
                        filtered_roots.append(root)
                    elif filter_path.is_relative_to(root_resolved):
                        # Filter path is under this root, scan just the filter path
                        filtered_roots.append(filter_path)
                    elif root_resolved.is_relative_to(filter_path):
                        # Root is under filter path, scan the root
                        filtered_roots.append(root)
                except (ValueError, OSError):
                    # Path resolution issues, skip
                    continue

            if filtered_roots:
                roots_to_scan = filtered_roots
            else:
                # If no roots match, try to use the filter path directly if it exists
                if filter_path.exists():
                    roots_to_scan = [filter_path]

        for root in roots_to_scan:
            if not root.exists():
                logger.warning(f"[SELFINC] Root path does not exist: {root}")
                continue

            logger.info(f"[SELFINC] Scanning root: {root}")
            discovered += await self._scan_directory(root)

        self.metrics["files_discovered"] = discovered
        return discovered

    async def _scan_directory(self, directory: Path) -> int:
        """Recursively scan a directory for files."""
        discovered = 0

        try:
            for item in directory.rglob("*"):
                if item.is_file():
                    # Skip files that are too large
                    if item.stat().st_size > self.config.max_file_mb * 1024 * 1024:
                        continue

                    # Skip common ignore patterns
                    if self._should_ignore_file(item):
                        continue

                    file_item = await self._create_file_item(item)
                    if file_item:
                        self.code_index.store_file(file_item)
                        discovered += 1

                        # Yield control periodically
                        if discovered % 100 == 0:
                            await asyncio.sleep(0.001)

        except Exception as e:
            logger.error(f"[SELFINC] Error scanning {directory}: {e}")

        return discovered

    def _should_ignore_file(self, path: Path) -> bool:
        """Check if a file should be ignored during discovery."""
        # Common ignore patterns (dirs and files)
        ignore_patterns = [
            ".*",  # Hidden files
            "__pycache__",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            "node_modules",
            ".git",
            ".svn",
            ".hg",
            ".idea",
            ".vscode",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            ".coverage",
            "coverage.xml",
            "dist",
            "build",
            ".venv",
            "venv",
            "env",
            "site-packages",
            "*.log",
            "*.tmp",
            "*.temp",
            # Large/binary artifacts
            "*.png",
            "*.jpg",
            "*.jpeg",
            "*.gif",
            "*.svg",
            "*.webp",
            "*.zip",
            "*.tar",
            "*.gz",
            "*.whl",
            "*.dll",
            "*.so",
            "*.dylib",
            "*.exe",
            "*.bin",
        ]

        path_str = str(path)
        for pattern in ignore_patterns:
            if pattern.startswith("*."):
                if path.suffix == pattern[1:]:
                    return True
            elif pattern in path_str:
                return True

        # Check for .aetherraignore files (basic implementation)
        # TODO: Implement full .aetherraignore parsing

        # Allow user-provided extra ignore patterns via env (semicolon separated)
        try:
            extra = os.getenv("AETHERRA_SELFINC_IGNORE", "").strip()
            if extra:
                for pat in [p.strip() for p in extra.split(";") if p.strip()]:
                    if pat.startswith("*."):
                        if path.suffix == pat[1:]:
                            return True
                    elif pat in path_str:
                        return True
        except Exception as exc:
            logger.debug("Self-Inc ignore pattern parse error: %s", exc, exc_info=True)

        return False

    async def _create_file_item(self, path: Path) -> FileItem | None:
        """Create a FileItem from a filesystem path."""
        try:
            stat = path.stat()

            # Calculate file hash
            hash_obj = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            content_hash = hash_obj.hexdigest()

            file_id = f"sha256:{content_hash}"

            # Determine language from extension
            language = self._detect_language(path)

            # Basic file type classification
            file_type = self._classify_file_type(path, language)

            # Extract basic entrypoints for Python files
            entrypoints = self._extract_entrypoints(path, language)

            # Prefer a path relative to project root; fall back to absolute/str
            try:
                rel = path.resolve().relative_to(Path.cwd().resolve())
                rel_path = str(rel)
            except Exception:
                rel_path = str(path)

            return FileItem(
                id=file_id,
                path=rel_path,
                hash=content_hash,
                size=stat.st_size,
                mtime=stat.st_mtime,
                type=file_type,
                language=language,
                entrypoints=entrypoints,
            )

        except Exception as e:
            logger.debug(f"[SELFINC] Failed to create FileItem for {path}: {e}")
            return None

    def _detect_language(self, path: Path) -> str:
        """Detect programming language from file extension."""
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".md": "markdown",
            ".txt": "text",
            ".aether": "aether",
            ".html": "html",
            ".css": "css",
            ".sql": "sql",
            ".sh": "shell",
            ".bat": "batch",
        }

        return extension_map.get(path.suffix.lower(), "other")

    def _classify_file_type(self, path: Path, language: str) -> ItemType:
        """Classify file type based on path patterns and content."""
        path_str = str(path).lower()

        # Check for .aether files first
        if path.suffix.lower() == ".aether":
            return ItemType.AETHER

        # Check path patterns for specific types
        if "/plugin" in path_str or "plugin_" in path.name.lower():
            return ItemType.PLUGIN

        if "/agent" in path_str or "agent_" in path.name.lower():
            return ItemType.AGENT

        if "/workflow" in path_str or "workflow_" in path.name.lower():
            return ItemType.WORKFLOW

        if (
            language in ["markdown", "text"]
            or "/doc" in path_str
            or path.suffix.lower() in [".md", ".txt", ".rst"]
        ):
            return ItemType.DOCS

        if "/data" in path_str or path.suffix.lower() in [
            ".json",
            ".csv",
            ".xml",
            ".yaml",
            ".yml",
        ]:
            return ItemType.DATASET

        if language == "python":
            # Try to detect Python file types by content
            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read(8192)  # Read first 8KB

                if "class.*Plugin" in content or "def plugin_" in content:
                    return ItemType.PLUGIN
                if "class.*Agent" in content or "def agent_" in content:
                    return ItemType.AGENT
                if "workflow" in content.lower() and (
                    "def " in content or "class " in content
                ):
                    return ItemType.WORKFLOW

            except Exception as exc:
                logger.debug(f"[SELFINC] Failed to infer python type for {path}: {exc}")

        return ItemType.UTILITY

    def _extract_entrypoints(self, path: Path, language: str) -> list[str]:
        """Extract entrypoints (functions, classes, etc.) from file."""
        entrypoints = []

        if language == "python":
            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read()

                # Simple regex-based extraction (could be improved with AST)
                # Standard library imports
                import re

                # Find class definitions
                for match in re.finditer(r"^class\s+(\w+)", content, re.MULTILINE):
                    entrypoints.append(f"class:{match.group(1)}")

                # Find function definitions (not methods)
                for match in re.finditer(r"^def\s+(\w+)", content, re.MULTILINE):
                    entrypoints.append(f"function:{match.group(1)}")

            except Exception as exc:
                logger.debug(
                    f"[SELFINC] Entrypoint extraction failed for {path}: {exc}"
                )

        elif language == "javascript":
            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read()

                # Standard library imports
                import re

                # Find function definitions
                for match in re.finditer(r"function\s+(\w+)", content):
                    entrypoints.append(f"function:{match.group(1)}")

                # Find class definitions
                for match in re.finditer(r"class\s+(\w+)", content):
                    entrypoints.append(f"class:{match.group(1)}")

            except Exception as exc:
                logger.debug(
                    f"[SELFINC] JS entrypoint extraction failed for {path}: {exc}"
                )

        return entrypoints[:20]  # Limit to prevent excessive data

    async def get_audit_summary(self) -> dict[str, int]:
        """Return a summary of audit records grouped by status."""
        try:
            return self.audit_ledger.summary() if self.audit_ledger else {}
        except Exception as e:
            logger.debug(f"[SELFINC] Failed to get audit summary: {e}")
            return {}

    async def export_audit_recent(self, path: str, limit: int = 100) -> dict[str, Any]:
        """Export recent audit records to a JSON file."""
        try:
            records = self.audit_ledger.recent(limit=limit) if self.audit_ledger else []
            out_path = Path(path)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2, default=str)
            return {"ok": True, "written": len(records), "path": str(out_path)}
        except Exception as e:
            return {"ok": False, "error": str(e)[:200]}
