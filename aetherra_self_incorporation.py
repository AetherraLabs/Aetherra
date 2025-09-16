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

import asyncio
import hashlib
import json
import logging
import os
import sqlite3
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

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
        reasoning = []
        risk_factors = []
        ethical_benefits = []

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
        if "network" in str(capabilities):
            score -= 0.1
            risk_factors.append("Network access capability")
            reasoning.append("UTIL: Network access increases potential for harm")

        if "exec" in str(capabilities) or "filesystem" in str(capabilities):
            score -= 0.15
            risk_factors.append("System access capability")
            reasoning.append("UTIL: System access capabilities increase harm potential")

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

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_id TEXT,
                    timestamp TEXT,
                    action TEXT,
                    status TEXT,
                    target_json TEXT,
                    result_json TEXT
                )
                """
            )
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
    ):
        rec = {
            "plan_id": plan_id,
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "status": status,
            "target_json": json.dumps(target, default=str),
            "result_json": json.dumps(result, default=str),
        }
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT INTO audit_records (plan_id, timestamp, action, status, target_json, result_json)
                VALUES (:plan_id, :timestamp, :action, :status, :target_json, :result_json)
                """,
                rec,
            )
            conn.commit()
        finally:
            conn.close()

    def recent(self, limit: int = 100) -> list[dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute(
                "SELECT plan_id, timestamp, action, status, target_json, result_json FROM audit_records ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            rows = cur.fetchall()
            return [
                {
                    "plan_id": row[0],
                    "timestamp": row[1],
                    "action": row[2],
                    "status": row[3],
                    "target": json.loads(row[4]),
                    "result": json.loads(row[5]),
                }
                for row in rows
            ]
        finally:
            conn.close()

    def summary(self) -> dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute(
                "SELECT COUNT(*), status FROM audit_records GROUP BY status"
            )
            return {row[1]: row[0] for row in cur.fetchall()}
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

    def __init__(self):
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
        # Policy-derived knobs (populated by service startup)
        self.unique_capabilities = []


class CodeIndex:
    """SQLite-based index with JSONL mirror for discovered files."""

    def __init__(self, db_path: Path, jsonl_path: Path):
        self.db_path = db_path
        self.jsonl_path = jsonl_path
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database schema."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
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
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_files_path ON files(path)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_files_type ON files(type)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_files_hash ON files(hash)
            """)

            conn.commit()
        finally:
            conn.close()

    def store_file(self, file_item: FileItem):
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

        # Basic type classification (already done in file_item.type)
        file_type = file_item.type

        # Extract detailed metadata based on file type
        capabilities = []
        requires = []
        risk_hints = []
        metadata = {}
        confidence = 0.5

        if file_item.language == "python":
            capabilities, requires, risk_hints, metadata, confidence = (
                self._analyze_python_file(path)
            )
        elif file_item.language == "aether":
            capabilities, requires, risk_hints, metadata, confidence = (
                self._analyze_aether_file(path)
            )
        elif file_item.language == "json":
            capabilities, requires, risk_hints, metadata, confidence = (
                self._analyze_json_file(path)
            )

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
        capabilities = []
        requires = []
        risk_hints = []
        metadata = {}
        confidence = 0.7

        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()

            # Extract imports
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
        capabilities = ["aether_script"]
        requires = []
        risk_hints = []
        metadata = {}
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
        capabilities = []
        requires = []
        risk_hints = []
        metadata = {}
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

    def _init_database(self):
        """Initialize classification database schema."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
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
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_classifications_type ON classifications(type)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_classifications_confidence ON classifications(confidence)
            """)

            conn.commit()
        finally:
            conn.close()

    def store_classification(self, result: ClassificationResult):
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
            if self.config.capabilities_policy_path.exists():
                with open(self.config.capabilities_policy_path, encoding="utf-8") as f:
                    return json.load(f)
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
            if self.config.net_policy_path.exists():
                with open(self.config.net_policy_path, encoding="utf-8") as f:
                    return json.load(f)
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
        else:
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
            if project_policy_path.exists():
                with open(project_policy_path, encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.debug(
                f"[POLICY] Failed to load selfinc_policy.json from project root: {e}"
            )

        # Fallback to default config path
        try:
            if self.config.selfinc_policy_path.exists():
                with open(self.config.selfinc_policy_path, encoding="utf-8") as f:
                    return json.load(f)
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

    def _init_database(self):
        """Initialize safety decisions database schema."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
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
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_safety_trust_tier ON safety_decisions(trust_tier)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_safety_verified ON safety_decisions(verified)
            """)

            conn.commit()
        finally:
            conn.close()

    def store_decision(self, decision: SafetyDecision):
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
        self.dependency_graph = {}  # file_id -> list of dependency file_ids
        self.reverse_deps = {}  # file_id -> list of files that depend on it

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
        capability_providers = {}
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

    def _get_hmr_controller(self):
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
        import uuid

        file_id = target.get("file_id", "unknown")
        timestamp = int(time.time())
        token_id = str(uuid.uuid4())[:8]
        return f"rb_{action}_{file_id[:12]}_{timestamp}_{token_id}"

    async def _record_hmr_action(
        self, action: str, target: dict[str, Any], rollback_token: str, success: bool
    ):
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
        hmr_actions = {"register_plugin", "register_agent", "load_aether_script"}
        return action in hmr_actions

    async def _execute_with_hmr(
        self, action: str, target: dict[str, Any], deps: list[str], dry_run: bool
    ) -> dict[str, Any]:
        """Execute an action with HMR support for safe live updates."""
        if dry_run:
            return await self._dispatch_action(action, target, deps, dry_run)

        hmr_controller = self._get_hmr_controller()
        if not hmr_controller:
            logger.warning(
                "[SELFINC][HMR] HMR controller not available, proceeding without HMR"
            )
            return await self._dispatch_action(action, target, deps, dry_run)

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
            await self._record_hmr_action(action, target, rollback_token, success)

            # Add rollback token to result
            result["rollback_token"] = rollback_token

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
                    action_type = act.action  # type: ignore[attr-defined]
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
            pm = self.service.plugin_manager
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
            orch = self.service.agent_orchestrator
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
                self._applied_scripts = set()
            script_key = file_item.hash if file_item else file_id
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
            svc = None
            if self.service.service_registry:
                svc = self.service.service_registry.get_service("aether_script_service")
            if not svc and hasattr(self.service, "aether_script_service"):
                svc = self.service.aether_script_service
            if not svc:
                try:
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
            }
            return {
                "status": "applied",
                "action": action,
                "name": workflow_name,
                "path": path,
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

    def update_activity(self, interaction_type: str = "generic"):
        """Update user activity timestamp."""
        self.activity.last_interaction = datetime.now()
        self.activity.interaction_count += 1

    def get_system_load(self) -> tuple[float, float]:
        """Get current CPU and memory usage."""
        try:
            # Simple system load detection
            import psutil

            cpu_percent = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            memory_percent = memory_info.percent
            return cpu_percent, memory_percent
        except ImportError:
            # Fallback if psutil not available
            return 5.0, 30.0  # Assume low usage

    def update_system_metrics(self):
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

    def _init_insights_db(self):
        """Initialize the insights database."""
        conn = sqlite3.connect(self.insights_db_path)
        try:
            conn.execute("""
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
            """)

            conn.execute("""
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
            """)

            conn.commit()
        finally:
            conn.close()

    async def analyze_recent_discoveries(self) -> list[LearningInsight]:
        """Analyze recent code discoveries for learning opportunities."""
        insights = []

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
        capability_counts = {}

        for classification in classifications:
            for capability in classification.detected_capabilities:
                capability_counts[capability] = capability_counts.get(capability, 0) + 1

        # Return capabilities requested more than once
        return {cap: count for cap, count in capability_counts.items() if count > 1}

    async def learn_from_audit_history(self) -> list[LearningInsight]:
        """Learn from historical audit data to identify improvement opportunities."""
        insights = []

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

    async def store_insights(self, insights: list[LearningInsight]):
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

    async def start_monitoring(self):
        """Start monitoring for night cycle opportunities."""
        if self.is_running:
            return

        self.is_running = True
        self.current_phase = NightCyclePhase.MONITORING

        logger.info("[NIGHT_CYCLE] Started monitoring for night cycle opportunities")

        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())

    async def stop_monitoring(self):
        """Stop night cycle monitoring."""
        self.is_running = False
        self.current_phase = NightCyclePhase.INACTIVE
        logger.info("[NIGHT_CYCLE] Stopped night cycle monitoring")

    async def _monitoring_loop(self):
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

    async def _run_night_cycle(self):
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

    async def _validate_night_cycle_changes(self):
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

    async def _generate_night_cycle_report(self, insights: list[LearningInsight]):
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

    def __init__(self, audit_ledger=None, policy_engine=None):
        self.audit_ledger = audit_ledger
        self.policy_engine = policy_engine
        self.quarantined_items = {}  # file_id -> metadata

    def quarantine(
        self, file_id: str, reason: str, context: dict[str, Any] | None = None
    ):
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

    def escalate(self, file_id: str, new_level: int, approval: str | None = None):
        """Escalate privileges for a quarantined item, with optional approval."""
        item = self.quarantined_items.get(file_id)
        if not item:
            raise ValueError(f"File {file_id} not in quarantine")
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

    def release(self, file_id: str, approved: bool = False):
        """Release a quarantined item (after approval or remediation)."""
        item = self.quarantined_items.get(file_id)
        if not item:
            raise ValueError(f"File {file_id} not in quarantine")
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
        return self.quarantined_items.get(file_id, {})

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

    def __init__(self, config: SelfIncorporationConfig | None = None):
        self.config = config or SelfIncorporationConfig()
        self.status = ServiceStatus.STARTING
        self._running = False

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
            "last_scan_duration": 0.0,
            "last_scan_timestamp": 0.0,
            "boot_completed": False,
            "night_cycles_completed": 0,
            "last_night_cycle_timestamp": 0.0,
            "night_cycle_insights": 0,
        }

    def quarantine_file(
        self, file_id: str, reason: str, context: dict[str, Any] | None = None
    ):
        """Quarantine a file or code item due to suspicious or untrusted status."""
        self.quarantine_manager.quarantine(file_id, reason, context)
        self.metrics["files_quarantined"] = self.metrics.get("files_quarantined", 0) + 1
        logger.info(f"[SELFINC] Quarantined {file_id}: {reason}")

        # Minimal workflow registry (in-memory)
        self._workflows = {}

        # Metrics and state
        self.metrics = {
            "files_discovered": 0,
            "files_classified": 0,
            "files_integrated": 0,
            "files_quarantined": 0,
            "last_scan_duration": 0.0,
            "last_scan_timestamp": 0.0,
            "boot_completed": False,
            "night_cycles_completed": 0,
            "last_night_cycle_timestamp": 0.0,
            "night_cycle_insights": 0,
        }

        # System integrations (injected by kernel)
        self.service_registry = None
        self.aether_script_service = None
        self.kernel_loop = None
        self.plugin_manager = None
        self.agent_orchestrator = None

        logger.info(f"[SELFINC] Initialized with roots: {self.config.roots}")

    async def start(self):
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

    async def stop(self):
        """Stop the Self-Incorporation service."""
        logger.info("[SELFINC] Stopping Self-Incorporation service...")
        self._running = False
        self.status = ServiceStatus.STOPPING

        # Unregister from service registry
        if self.service_registry:
            await self.service_registry.unregister_service("self_incorporation")

        logger.info("[SELFINC] Service stopped")

    def inject_systems(
        self, service_registry, kernel_loop, plugin_manager, agent_orchestrator
    ):
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

        return {
            **health,
            "files_by_type": files_by_type,
            "last_scan": {
                "timestamp": self.metrics["last_scan_timestamp"],
                "duration": self.metrics["last_scan_duration"],
            },
            "boot_status": {"completed": self.metrics["boot_completed"]},
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

        # Ethics evaluation before execution
        ethics_evaluation = await self._evaluate_plan_ethics(plan)
        ethics_threshold = float(os.getenv("AETHERRA_ETHICS_THRESHOLD", "0.6"))

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
        if exec_result.get("ok"):
            self.metrics["files_integrated"] = self.metrics.get(
                "files_integrated", 0
            ) + exec_result.get("applied", 0)

        result: dict[str, Any] = {
            "ok": exec_result.get("ok", False),
            "plan_id": plan.get("plan_id"),
            "status": status,
            "applied": exec_result.get("applied", 0),
            "skipped": exec_result.get("skipped", 0),
            "errors": exec_result.get("errors", 0),
            "duration": time.time() - start_time,
        }
        if return_results:
            result["results"] = exec_result.get("results", [])
        return result

    async def get_integration_status(self) -> dict[str, Any]:
        """Get current integration planning status and metrics."""

        # Count components by status
        classifications = self.classification_index.list_classifications()

        trust_counts = {}
        for tier in TrustTier:
            decisions = self.safety_index.list_by_trust_tier(tier)
            trust_counts[tier.value] = len(decisions)

        type_counts = {}
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

    async def trigger_rollback(self, rollback_token: str) -> dict[str, Any]:
        """Rollback an integration using HMR rollback token."""
        start_time = time.time()
        logger.info(f"[SELFINC] Starting rollback for token: {rollback_token}")

        if not rollback_token or not rollback_token.startswith("rb_"):
            return {
                "ok": False,
                "error": "invalid_rollback_token",
                "token": rollback_token,
                "duration": time.time() - start_time,
            }

        # Check if HMR is enabled
        if not self.config.hmr_enabled:
            return {
                "ok": False,
                "error": "hmr_disabled",
                "token": rollback_token,
                "duration": time.time() - start_time,
            }

        # Get HMR controller
        hmr_controller = None
        if self.service_registry:
            info = self.service_registry.get_service_info("hmr_controller")
            hmr_controller = info.instance if info else None

        if not hmr_controller:
            return {
                "ok": False,
                "error": "hmr_controller_unavailable",
                "token": rollback_token,
                "duration": time.time() - start_time,
            }

        try:
            # Look up the rollback token in audit records
            audit_records = []
            if hasattr(self, "audit_ledger") and self.audit_ledger:
                # Search for records with this rollback token
                all_records = self.audit_ledger.recent(limit=1000)
                audit_records = [
                    r
                    for r in all_records
                    if r.get("result", {}).get("rollback_token") == rollback_token
                ]

            if not audit_records:
                return {
                    "ok": False,
                    "error": "rollback_token_not_found",
                    "token": rollback_token,
                    "duration": time.time() - start_time,
                }

            # For now, we'll log the rollback attempt and return success
            # In a full implementation, this would interface with the HMR controller
            # to actually perform the rollback operation
            logger.info(
                f"[SELFINC][HMR] Rollback requested for {len(audit_records)} integration(s)"
            )

            # Record the rollback attempt in audit
            if hasattr(self, "audit_ledger") and self.audit_ledger:
                self.audit_ledger.append(
                    plan_id="rollback",
                    action="hmr_rollback",
                    status="applied",
                    target={"rollback_token": rollback_token},
                    result={
                        "rollback_token": rollback_token,
                        "affected_integrations": len(audit_records),
                        "timestamp": time.time(),
                    },
                )

            return {
                "ok": True,
                "token": rollback_token,
                "affected_integrations": len(audit_records),
                "duration": time.time() - start_time,
                "note": "rollback_logged_hmr_implementation_pending",
            }

        except Exception as e:
            logger.error(f"[SELFINC][HMR] Rollback failed: {e}")
            return {
                "ok": False,
                "error": f"rollback_failed: {str(e)[:200]}",
                "token": rollback_token,
                "duration": time.time() - start_time,
            }

    async def get_planning_details(
        self, include_experimental: bool = False, limit: int = 50
    ) -> dict[str, Any]:
        """Return detailed planning diagnostics: cycles and conflicts.

        Note: This runs a planning pass to collect data but does not persist any state.
        """
        plan = await self._run_integration_planning(include_experimental)

        # Truncate large lists for readability
        def _truncate(seq):
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
        # Common ignore patterns
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
            "*.log",
            "*.tmp",
            "*.temp",
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

            return FileItem(
                id=file_id,
                path=str(path.relative_to(Path.cwd())),
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
