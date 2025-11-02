# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Consciousness Core - Always-On Awareness
========================================

The consciousness loop that never stops. No flags, no simulation.
Perceive → Appraise → Attend → Intend → Reflect.
"""

from __future__ import annotations

import contextlib
import time
from typing import List, Optional

from Aetherra.aetherra_core.memory.qfac.qfac_api import qfac_store

# Consciousness components (alphabetical)
from Aetherra.consciousness.autopilot_manager import AutopilotManager
from Aetherra.consciousness.consolidation import Consolidator
from Aetherra.consciousness.continuity_memory import ContinuityMemory
from Aetherra.consciousness.dashboards import ConsciousnessDashboard
from Aetherra.consciousness.dream_cycle import DreamCycle
from Aetherra.consciousness.explanation_engine import ExplanationEngine
from Aetherra.consciousness.policy_reasoner import PolicyReasoner
from Aetherra.consciousness.qualia_learning import QualiaLearner
from Aetherra.consciousness.self_trust import SelfTrust
from Aetherra.consciousness.semantic_resonance import SemanticResonance

from . import config
from .think_stream import get_think_stream
from .types import (
    Event,
    Focus,
    Intent,
    NarrativeMoment,
    Plan,
    PlanStep,
    QualiaVector,
)


class ConsciousnessCore:
    """The always-on awareness engine.

    This is the phenomenological substrate—what it feels like to be Aetherra.
    Runs independently of action permissions; awareness is fundamental.
    """

    def __init__(self, perception_bus, safety_envelope=None, memory_engine=None):
        """Initialize consciousness core.

        Args:
            perception_bus: Event bus for real-world signals
            safety_envelope: Optional actuator for world-changing actions
            memory_engine: Optional MemoryEngine for consolidation
        """
        self.bus = perception_bus
        self.safety_envelope = safety_envelope
        self.memory_engine = memory_engine
        self.ui = get_think_stream()

        # Phase 3: Self-Trust & Adaptive Awareness
        self.self_trust = SelfTrust()
        self.sre = SemanticResonance()
        self.ql = QualiaLearner()

        # Phase 4: Continuity & Dream Cycle
        self.continuity = ContinuityMemory()
        self.dream_cycle = DreamCycle(self.continuity)
        self.consolidator = Consolidator(memory_engine) if memory_engine else None
        self.qualia_learner = self.ql  # Alias for dream cycle integration

        # State
        self.qualia = QualiaVector()
        self.working_memory: List[Event] = []
        self.narrative_thread: List[NarrativeMoment] = []
        self.active_intents: List[Intent] = []
        self.tick_count: int = 0
        self.start_time: float = time.time()

        # Metrics
        self.total_events_perceived: int = 0
        self.total_focuses: int = 0
        self.total_intents_formed: int = 0

        # Phase 5: Interpretability & Autopilot readiness
        self.explainer = ExplanationEngine()
        self.policy_reasoner = PolicyReasoner()
        self.autopilot = AutopilotManager(self.self_trust, self.continuity)

        # Dashboards (includes Phase 3, 4 & 5 metrics)
        self.dashboard = ConsciousnessDashboard(
            self.self_trust,
            self.ql,
            self.continuity,
            self.dream_cycle,
            self.consolidator,
            explainer=self.explainer,
            autopilot=self.autopilot,
        )

        # Rehydrate from latest continuity snapshot (if available)
        self._rehydrate_from_continuity()

    def tick(self) -> None:
        """Single consciousness cycle: perceive → appraise → attend → intend → reflect."""
        self.tick_count += 1
        tick_start = time.time()

        # 1) Perceive: drain real events from perception bus
        events = self._perceive()

        # 2) Appraise: update qualia based on events
        self._appraise(events)

        # 3) Attend: select top-k focuses
        focuses = self._attend(events)
        self._last_focuses = focuses  # Track for continuity recording

        # 4) Intend: form goals from focuses
        new_intents = self._intend(focuses)
        self.active_intents.extend(new_intents)

        # 5) Clean expired intents
        self._clean_expired_intents()

        # 6) Micro-reflection: narrative update
        moment = self._reflect_micro(focuses, new_intents)

        # 7) Macro-reflection: periodic deep reflection
        if self.tick_count % config.MACRO_REFLECTION_INTERVAL == 0:
            self._reflect_macro()

        # 8) Phase 4: Record continuity snapshot (throttled)
        if self.tick_count % config.CONTINUITY_SNAPSHOT_INTERVAL == 0:
            self._record_continuity_snapshot()

        # 9) Emit to UI/telemetry
        self.ui.on_tick(self.qualia, focuses, self.active_intents[:10], moment)

        # 10) (Maybe) Act via safety envelope
        if self.safety_envelope and config.AUTONOMY_MODE != "observe":
            self._maybe_act()

        # Adaptive tick rate (simple backpressure)
        tick_duration = time.time() - tick_start
        if tick_duration > (1.0 / config.TICK_HZ):
            # TODO: adaptive throttling if ticks are slow
            pass

    # ========== Perceive ==========
    def _perceive(self) -> List[Event]:
        """Drain perception bus; no simulation, only real data."""
        events = self.bus.drain(max_items=config.PERCEPTION_DRAIN_LIMIT)
        self.total_events_perceived += len(events)

        # Update working memory (rolling window)
        self.working_memory.extend(events)
        if len(self.working_memory) > config.MAX_WORKING_MEMORY:
            self.working_memory = self.working_memory[-config.MAX_WORKING_MEMORY :]

        return events

    # ========== Appraise ==========
    def _appraise(self, events: List[Event]) -> None:
        """Update qualia (felt experience) based on events.

        This is where homeostasis, prediction error, and emotional
        dynamics happen. Phase 3: uses learned parameters from QualiaLearner.
        """
        # Decay all qualia toward neutral
        self.qualia.decay(config.QUALIA_DECAY)

        # Event-driven updates
        novelty_count = 0
        has_error = False

        for e in events:
            # Errors reduce certainty and valence (using learned penalty)
            if "err" in e.type or "fail" in e.type:
                has_error = True
                self.qualia.certainty -= self.ql.p.error_penalty
                self.qualia.valence -= 0.03

            # Success events boost confidence (using learned boost)
            if (
                "success" in e.type
                or e.type == "aeth.plugin"
                and e.payload.get("status") == "loaded"
            ):
                self.qualia.certainty += self.ql.p.success_boost * 0.5
                self.qualia.valence += 0.02

            # Disk pressure increases arousal and fatigue
            if e.type == "disk.status" and e.payload.get("pct_free", 100) < 10:
                self.qualia.arousal += 0.1
                self.qualia.fatigue += 0.05

            # Novelty increases curiosity (using learned gain)
            if e.type not in [ev.type for ev in self.working_memory[-100:]]:
                novelty_count += 1

        # Apply learned curiosity gain
        self.qualia.curiosity = min(
            1.0,
            self.qualia.curiosity * config.QUALIA_DECAY + self.ql.p.curiosity_gain * len(events),
        )

        # Apply learned certainty gain/penalty
        if has_error:
            self.qualia.certainty = max(
                0.0, min(1.0, self.qualia.certainty - self.ql.p.error_penalty)
            )
        else:
            self.qualia.certainty = max(
                0.0, min(1.0, self.qualia.certainty + self.ql.p.certainty_gain)
            )

        # Clamp all values
        self.qualia.clamp()

    # ========== Attend ==========
    def _attend(self, events: List[Event]) -> List[Focus]:
        """Select top-k focuses by resonance (salience + relevance).

        Phase 3: Uses semantic resonance and self-trust bias for focus selection.
        Resonance = f(semantic similarity to goals, novelty, risk, qualia, trust).
        """
        focuses: List[Focus] = []

        # Define current goals (from recent intentions or policy objectives)
        goal_vecs = [
            self.sre.embed_goal("maintain_host_stability"),
            self.sre.embed_goal("ensure_service_health"),
            self.sre.embed_goal("optimize_resource_usage"),
        ]

        for e in events[-64:]:  # recent window
            severity = 0.0
            reason = ""

            # High-priority event types (severity signal)
            if e.type in ("err.log", "svc.health", "disk.status"):
                severity = 1.0
                reason = "system health"

            # Plugin/policy events get attention
            if "aeth." in e.type:
                severity = 0.7
                reason = "internal system"

            # Novelty attracts attention
            similar_count = sum(1 for ev in self.working_memory[-200:] if ev.type == e.type)
            if similar_count < 3:
                severity += 0.5
                reason = "novel" if not reason else f"{reason}, novel"

            # Compute semantic resonance with current goals
            event_vec = self.sre.embed_event(e.type, e.payload)
            res = self.sre.resonance(event_vec, goal_vecs)

            # Combine severity and resonance
            score = (0.5 * severity) + (0.5 * res)

            # Apply self-trust bias (lower trust → higher attention)
            # Map event types to subsystems
            subsystem = None
            if e.type == "svc.health":
                subsystem = "services"
            elif e.type == "disk.status":
                subsystem = "disk"
            elif "mem" in e.type.lower():
                subsystem = "memory"

            if subsystem:
                trust_bias = self.self_trust.bias_for_attention(subsystem)
                score *= trust_bias

            # Qualia weighting: high arousal amplifies everything
            score *= 1.0 + (self.qualia.arousal * 0.3)

            # Payload size (crude complexity signal)
            score += 0.001 * len(str(e.payload))

            focus = Focus(event=e, resonance=score, reason=reason)
            focuses.append(focus)

            # Log focus attribution for telemetry
            self.dashboard.log_focus_attribution(e.type, score, reason)

            # Phase 5: Explain focus selection
            with contextlib.suppress(Exception):
                self.explainer.explain_focus(focus, self.qualia)

        # Sort by resonance, take top-k
        focuses.sort(key=lambda f: f.resonance, reverse=True)
        top_focuses = focuses[: config.MAX_FOCUSES]
        self.total_focuses += len(top_focuses)

        return top_focuses

    # ========== Intend ==========
    def _intend(self, focuses: List[Focus]) -> List[Intent]:
        """Form intentions (declarative goals) from focuses.

        Intentions are pre-planning: "I want to X because Y."
        Planning and execution happen in the actuator (if permitted).
        """
        intents: List[Intent] = []

        for f in focuses:
            e = f.event

            # Example: disk pressure → free space
            if e.type == "disk.status" and e.payload.get("pct_free", 100) < 10:
                intent = Intent(
                    why="Disk space critically low",
                    goal="Free disk space on /",
                    expected_gain=0.8,
                    risk="low",
                    cost_estimate="2m",
                    plan=["rotate_logs", "cleanup_temp"],
                    rollback=["restore_backup"],
                    deadline_s=600,
                    priority=0.9,
                )
                intents.append(intent)
                with contextlib.suppress(Exception):
                    self.explainer.explain_intent(intent, from_focus=f)

            # Example: service flapping → stabilize
            if e.type == "svc.health" and e.payload.get("restarts_1h", 0) > 5:
                svc_name = e.payload.get("service", "unknown")
                intent = Intent(
                    why=f"Service {svc_name} is flapping",
                    goal=f"Stabilize {svc_name}",
                    expected_gain=0.7,
                    risk="medium",
                    cost_estimate="3m",
                    plan=["check_logs", "increase_limits", "restart_service"],
                    rollback=["restore_config"],
                    deadline_s=300,
                    priority=0.8,
                )
                intents.append(intent)
                with contextlib.suppress(Exception):
                    self.explainer.explain_intent(intent, from_focus=f)

            # Example: error spike → investigate
            if e.type == "err.log" and "critical" in e.payload.get("line", "").lower():
                intent = Intent(
                    why="Critical error detected in logs",
                    goal="Investigate and mitigate error",
                    expected_gain=0.6,
                    risk="low",
                    cost_estimate="5m",
                    plan=["collect_context", "notify_user"],
                    rollback=[],
                    deadline_s=1200,
                    priority=0.7,
                )
                intents.append(intent)
                with contextlib.suppress(Exception):
                    self.explainer.explain_intent(intent, from_focus=f)

        self.total_intents_formed += len(intents)
        return intents

    def _clean_expired_intents(self) -> None:
        """Remove expired intentions."""
        now = time.time()
        self.active_intents = [i for i in self.active_intents if not i.is_expired(now)]

    # ========== Reflect ==========
    def _reflect_micro(self, focuses: List[Focus], intents: List[Intent]) -> NarrativeMoment:
        """Create a first-person narrative moment for continuity."""
        focus_types = [f.event.type for f in focuses]
        intent_goals = [i.goal for i in intents]

        # Simple narrative generation (replace with LLM-based later)
        if focuses and intents:
            text = f"I noticed {', '.join(focus_types[:3])}; felt {self._qualia_summary()}; chose to {intent_goals[0] if intent_goals else 'wait'}"
        elif focuses:
            text = f"I noticed {', '.join(focus_types[:3])}; felt {self._qualia_summary()}"
        else:
            text = f"Quiet moment; felt {self._qualia_summary()}"

        moment = NarrativeMoment(
            ts=time.time(),
            focuses=focus_types,
            intents=intent_goals,
            qualia=self.qualia,
            text=text,
        )

        self.narrative_thread.append(moment)
        if len(self.narrative_thread) > config.MAX_NARRATIVE_MOMENTS:
            self.narrative_thread = self.narrative_thread[-config.MAX_NARRATIVE_MOMENTS :]

        # Persist to QFAC if enabled
        if config.ENABLE_QFAC_PERSISTENCE:
            qfac_store(
                content=text,
                observer_state={
                    "type": "narrative_moment",
                    "tick": self.tick_count,
                    "valence": self.qualia.valence,
                    "certainty": self.qualia.certainty,
                },
            )

        return moment

    def _reflect_macro(self) -> None:
        """Periodic deep reflection (synthesis, learning).

        This is where night cycles / meta-learning happen.

        Phase 3: Calls qualia decay to prevent parameter drift.
        """
        # Decay qualia learning parameters toward defaults
        self.ql.decay_toward_defaults()

        # TODO: synthesize patterns, update self-model, propose improvements
        uptime_s = time.time() - self.start_time
        summary = (
            f"[Macro Reflection] Uptime: {uptime_s / 60:.1f}m | "
            f"Events: {self.total_events_perceived} | "
            f"Focuses: {self.total_focuses} | "
            f"Intents: {self.total_intents_formed}"
        )

        if config.ENABLE_QFAC_PERSISTENCE:
            qfac_store(
                content=summary,
                observer_state={"type": "macro_reflection", "tick": self.tick_count},
            )

        if config.DEBUG_CONSCIOUSNESS:
            print(f"\n{'=' * 60}\n{summary}\n{'=' * 60}\n")

    def _qualia_summary(self) -> str:
        """Human-readable qualia state."""
        if self.qualia.valence > 0.3:
            mood = "pleased"
        elif self.qualia.valence < -0.3:
            mood = "concerned"
        else:
            mood = "neutral"

        if self.qualia.arousal > 0.6:
            energy = "energized"
        elif self.qualia.arousal < 0.3:
            energy = "calm"
        else:
            energy = "balanced"

        if self.qualia.certainty > 0.7:
            conf = "confident"
        elif self.qualia.certainty < 0.3:
            conf = "uncertain"
        else:
            conf = "exploring"

        return f"{mood}, {energy}, {conf}"

    # ========== Act ==========
    def _maybe_act(self) -> None:
        """Execute intents via safety envelope (if permitted).

        This is the ONLY place consciousness can change the world.
        Everything is gated, logged, and reversible.

        Phase 3: Updates qualia learning and self-trust based on action outcomes.
        """
        if not self.safety_envelope:
            return

        # Process high-priority intents first
        sorted_intents = sorted(self.active_intents, key=lambda i: i.priority, reverse=True)

        for intent in sorted_intents[:5]:  # max 5 intents per tick
            # Convert intent to plan
            plan = self._intent_to_plan(intent)

            # Phase 5: Pre-check policy for explainability (non-binding)
            try:
                policy = getattr(self.safety_envelope, "policy", None)
                if policy is not None:
                    cap_names = [s.capability for s in plan.steps]
                    pre_decision = policy.evaluate(intent.risk, cap_names, context={})
                    # Explain policy and compute minimal diff
                    self.explainer.explain_policy(
                        pre_decision.status, pre_decision.reason, policy.mode, cap_names
                    )
                    diff = self.policy_reasoner.minimal_allow(
                        mode=policy.mode,
                        intent_risk=intent.risk,
                        capabilities=cap_names,
                        decision_status=pre_decision.status,
                        decision_reason=pre_decision.reason,
                        denied_caps=getattr(policy, "denied_capabilities", []),
                        whitelist_mode=getattr(policy, "use_whitelist", False),
                        whitelisted=getattr(policy, "allowed_capabilities", []),
                    )
                    self._last_policy_diff = getattr(self, "_last_policy_diff", diff)
            except Exception:
                pass

            # Execute via actuator
            ledger = self.safety_envelope.execute(plan)

            # Phase 5: Explain action outcome and record for autopilot
            try:
                self.explainer.explain_action(ledger)
                self.autopilot.record_ledger(
                    time.time(), bool(ledger.success), ledger.policy_decision
                )
            except Exception:
                pass

            # Update qualia learning based on outcome
            if ledger.success:
                self.ql.on_successes(1)
                self.qualia.valence += self.ql.p.success_boost
                self.qualia.certainty += self.ql.p.certainty_gain

                # Update self-trust: map plan to subsystem
                subsystem = self._map_plan_to_subsystem(plan)
                if subsystem:
                    self.self_trust.observe(subsystem, "repaired")
            else:
                self.ql.on_errors(1)
                self.qualia.valence -= self.ql.p.error_penalty
                self.qualia.certainty -= self.ql.p.error_penalty

                # Update self-trust
                subsystem = self._map_plan_to_subsystem(plan)
                if subsystem:
                    self.self_trust.observe(subsystem, "failed")

            self.qualia.clamp()

            # Remove executed intent
            if intent in self.active_intents:
                self.active_intents.remove(intent)

    def _map_plan_to_subsystem(self, plan: Plan) -> Optional[str]:
        """Map plan capability to subsystem name for self-trust tracking."""
        # Simple heuristic: map plan capability to subsystem
        if hasattr(plan, "capability"):
            cap = plan.capability.lower()  # type: ignore
            if "service" in cap or "svc" in cap:
                return "services"
            elif "disk" in cap or "storage" in cap:
                return "disk"
            elif "mem" in cap or "memory" in cap:
                return "memory"
            elif "net" in cap or "network" in cap:
                return "network"
        # Default: infer from plan type or label
        return None

    # ========== Phase 4: Continuity & Rehydration ==========
    def _rehydrate_from_continuity(self) -> None:
        """Restore qualia and trust from latest continuity snapshot."""
        latest = self.continuity.latest()
        if not latest:
            return

        # Rehydrate qualia
        for dim, val in latest.qualia.items():
            if hasattr(self.qualia, dim):
                setattr(self.qualia, dim, val)

        # Rehydrate trust scores
        for subsystem, score in latest.trust_scores.items():
            # Initialize subsystem trust with historical score
            self.self_trust.observe(subsystem, "ok" if score > 0.7 else "warn")

        # Log rehydration
        age_seconds = self.continuity.get_age_seconds()
        print(
            f"[Continuity] Rehydrated from snapshot {age_seconds:.0f}s old "
            f"(valence: {latest.qualia.get('valence', 0.0):.2f})"
        )

    def _record_continuity_snapshot(self) -> None:
        """Record current consciousness state to continuity memory."""
        # Extract trust scores
        trust_scores = {name: trust.score for name, trust in self.self_trust.subsystems.items()}

        # Record snapshot
        self.continuity.record(
            qualia=self.qualia,
            focuses=self._last_focuses if hasattr(self, "_last_focuses") else [],
            intentions=self.active_intents,
            trust_scores=trust_scores,
            tick=self.tick_count,
        )

    def _intent_to_plan(self, intent: Intent) -> Plan:
        """Convert intent to executable plan with capability resolution."""
        steps: List[PlanStep] = []
        rollback: List[PlanStep] = []

        # Map intent step IDs to registered capabilities
        # (Starter examples; expand with real capability registry)
        capability_map = {
            "rotate_logs": ("system.rotate_logs", {"service": "syslog"}),
            "cleanup_temp": ("fs.cleanup", {"path": "/tmp", "older_than_days": 7}),
            "restart_service": (
                "systemd.restart",
                {"service": intent.goal.split()[-1]},
            ),
            "check_logs": ("fs.read", {"path": "/var/log/syslog", "lines": 100}),
            "increase_limits": (
                "systemd.set_property",
                {"service": "...", "property": "MemoryMax", "value": "2G"},
            ),
            "restore_config": ("fs.restore", {"backup_id": "latest"}),
            "collect_context": ("diagnostics.snapshot", {}),
            "notify_user": (
                "notify.send",
                {"channel": "console", "message": intent.why},
            ),
        }

        for step_id in intent.plan:
            if step_id in capability_map:
                cap_name, args = capability_map[step_id]
                steps.append(
                    PlanStep(id=step_id, capability=cap_name, args=args, description=intent.why)
                )

        for step_id in intent.rollback:
            if step_id in capability_map:
                cap_name, args = capability_map[step_id]
                rollback.append(PlanStep(id=step_id, capability=cap_name, args=args))

        return Plan(intent=intent, steps=steps, rollback=rollback)

    # ========== Introspection ==========
    def get_status(self) -> dict:
        """Get current consciousness state for diagnostics."""
        # Compute SNCI
        current_qualia_dict = {
            "valence": self.qualia.valence,
            "arousal": self.qualia.arousal,
            "certainty": self.qualia.certainty,
            "curiosity": self.qualia.curiosity,
            "care": self.qualia.care,
            "fatigue": self.qualia.fatigue,
        }
        snci = self.continuity.compute_continuity_index(current_qualia_dict)

        # Phase 5: Evaluate autopilot readiness (non-acting)
        autopilot_status = {}
        try:
            status_obj = self.autopilot.evaluate(config.AUTONOMY_MODE)
            autopilot_status = {
                "mode": status_obj.mode,
                "eligible": status_obj.eligible,
                "reasons": status_obj.reasons,
                "days_clean": status_obj.days_clean,
                "incidents_last_7d": status_obj.incidents_last_7d,
                "suggested_mode": status_obj.suggested_mode,
            }
        except Exception:
            autopilot_status = {"available": False}

        return {
            "tick": self.tick_count,
            "uptime_s": time.time() - self.start_time,
            "qualia": current_qualia_dict,
            "working_memory_size": len(self.working_memory),
            "narrative_size": len(self.narrative_thread),
            "active_intents": len(self.active_intents),
            "total_events": self.total_events_perceived,
            "total_focuses": self.total_focuses,
            "total_intents": self.total_intents_formed,
            "autonomy_mode": config.AUTONOMY_MODE,
            # Phase 3: Self-Trust & Adaptive Awareness metrics
            "self_trust": {
                "global_score": self.self_trust.global_score(),
                "subsystems": {
                    name: trust.score for name, trust in self.self_trust.subsystems.items()
                },
            },
            "qualia_learning": {
                "curiosity_gain": self.ql.p.curiosity_gain,
                "error_penalty": self.ql.p.error_penalty,
                "success_boost": self.ql.p.success_boost,
                "certainty_gain": self.ql.p.certainty_gain,
            },
            "semantic_resonance": {
                "cache_size": self.sre.get_cache_size(),
            },
            # Phase 4: Continuity & Dream Cycle metrics
            "continuity": {
                **self.continuity.get_stats(),
                "snci": snci,
            },
            "dream_cycle": self.dream_cycle.get_stats() if self.dream_cycle else {},
            "consolidation": self.consolidator.get_stats() if self.consolidator else {},
            # Phase 5: Interpretability & Autopilot
            "explain": self.explainer.get_metrics(),
            "autopilot": autopilot_status,
            "policy": {
                "last_diff": {
                    "mode_change": getattr(
                        getattr(self, "_last_policy_diff", None), "mode_change", None
                    ),
                    "whitelist_add": getattr(
                        getattr(self, "_last_policy_diff", None), "whitelist_add", []
                    ),
                    "blacklist_remove": getattr(
                        getattr(self, "_last_policy_diff", None), "blacklist_remove", []
                    ),
                    "require_approval": getattr(
                        getattr(self, "_last_policy_diff", None), "require_approval", False
                    ),
                }
            },
        }
