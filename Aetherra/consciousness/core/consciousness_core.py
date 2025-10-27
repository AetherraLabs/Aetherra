# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Consciousness Core - Always-On Awareness
========================================

The consciousness loop that never stops. No flags, no simulation.
Perceive → Appraise → Attend → Intend → Reflect.
"""

from __future__ import annotations

import time
from typing import List

from Aetherra.aetherra_core.memory.qfac.qfac_api import qfac_store

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

    def __init__(self, perception_bus, safety_envelope=None):
        """Initialize consciousness core.

        Args:
            perception_bus: Event bus for real-world signals
            safety_envelope: Optional actuator for world-changing actions
        """
        self.bus = perception_bus
        self.safety_envelope = safety_envelope
        self.ui = get_think_stream()

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

        # 8) Emit to UI/telemetry
        self.ui.on_tick(self.qualia, focuses, self.active_intents[:10], moment)

        # 9) (Maybe) Act via safety envelope
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
        dynamics happen. Starter heuristics below; expand with real models.
        """
        # Decay all qualia toward neutral
        self.qualia.decay(config.QUALIA_DECAY)

        # Event-driven updates
        novelty_count = 0

        for e in events:
            # Errors reduce certainty and valence
            if "err" in e.type or "fail" in e.type:
                self.qualia.certainty -= 0.05
                self.qualia.valence -= 0.03

            # Success events boost confidence
            if (
                "success" in e.type
                or e.type == "aeth.plugin"
                and e.payload.get("status") == "loaded"
            ):
                self.qualia.certainty += 0.02
                self.qualia.valence += 0.02

            # Disk pressure increases arousal and fatigue
            if e.type == "disk.status" and e.payload.get("pct_free", 100) < 10:
                self.qualia.arousal += 0.1
                self.qualia.fatigue += 0.05

            # Novelty increases curiosity
            if e.type not in [ev.type for ev in self.working_memory[-100:]]:
                novelty_count += 1

        self.qualia.curiosity += 0.05 * min(novelty_count, 5) / 5.0

        # Clamp all values
        self.qualia.clamp()

    # ========== Attend ==========
    def _attend(self, events: List[Event]) -> List[Focus]:
        """Select top-k focuses by resonance (salience + relevance).

        Resonance = f(semantic similarity to goals, novelty, risk, qualia).
        Starter implementation uses simple heuristics.
        """
        focuses: List[Focus] = []

        for e in events[-64:]:  # recent window
            score = 0.0
            reason = ""

            # High-priority event types
            if e.type in ("err.log", "svc.health", "disk.status"):
                score += 1.0
                reason = "system health"

            # Plugin/policy events get attention
            if "aeth." in e.type:
                score += 0.7
                reason = "internal system"

            # Novelty attracts attention
            similar_count = sum(1 for ev in self.working_memory[-200:] if ev.type == e.type)
            if similar_count < 3:
                score += 0.5
                reason = "novel"

            # Qualia weighting: high arousal amplifies everything
            score *= 1.0 + (self.qualia.arousal * 0.3)

            # Payload size (crude complexity signal)
            score += 0.001 * len(str(e.payload))

            focuses.append(Focus(event=e, resonance=score, reason=reason))

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
                intents.append(
                    Intent(
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
                )

            # Example: service flapping → stabilize
            if e.type == "svc.health" and e.payload.get("restarts_1h", 0) > 5:
                svc_name = e.payload.get("service", "unknown")
                intents.append(
                    Intent(
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
                )

            # Example: error spike → investigate
            if e.type == "err.log" and "critical" in e.payload.get("line", "").lower():
                intents.append(
                    Intent(
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
                )

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
        For now, just log a marker.
        """
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
        """
        if not self.safety_envelope:
            return

        # Process high-priority intents first
        sorted_intents = sorted(self.active_intents, key=lambda i: i.priority, reverse=True)

        for intent in sorted_intents[:5]:  # max 5 intents per tick
            # Convert intent to plan
            plan = self._intent_to_plan(intent)

            # Execute via actuator
            ledger = self.safety_envelope.execute(plan)

            # Update qualia based on outcome
            if ledger.success:
                self.qualia.valence += 0.1
                self.qualia.certainty += 0.05
            else:
                self.qualia.valence -= 0.1
                self.qualia.certainty -= 0.05

            self.qualia.clamp()

            # Remove executed intent
            if intent in self.active_intents:
                self.active_intents.remove(intent)

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
        return {
            "tick": self.tick_count,
            "uptime_s": time.time() - self.start_time,
            "qualia": {
                "valence": self.qualia.valence,
                "arousal": self.qualia.arousal,
                "certainty": self.qualia.certainty,
                "curiosity": self.qualia.curiosity,
                "care": self.qualia.care,
                "fatigue": self.qualia.fatigue,
            },
            "working_memory_size": len(self.working_memory),
            "narrative_size": len(self.narrative_thread),
            "active_intents": len(self.active_intents),
            "total_events": self.total_events_perceived,
            "total_focuses": self.total_focuses,
            "total_intents": self.total_intents_formed,
            "autonomy_mode": config.AUTONOMY_MODE,
        }
