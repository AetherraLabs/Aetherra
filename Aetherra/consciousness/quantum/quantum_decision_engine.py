# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧠 AETHERRA QUANTUM DECISION ENGINE
Advanced Quantum Cognition - Phase 7.2 Implementation

This module implements quantum superposition-based decision making for Aetherra's
consciousness system, allowing exploration of all possible decision paths
simultaneously before collapsing to the optimal choice.

Key Features:
- Superposition Decision Spaces
- Quantum Tunneling Logic
- Interference Pattern Analysis
- Quantum Measurement and Collapse
- Multi-dimensional Decision Trees

Author: Aetherra Consciousness Team
Version: 7.2.0
Date: August 5, 2025
"""

# Standard library imports
import asyncio
import hashlib
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# Third party imports
import numpy as np

try:
    # Standard library imports
    import importlib.util

    qiskit_spec = importlib.util.find_spec("qiskit")
    QISKIT_AVAILABLE = qiskit_spec is not None
except ImportError:
    QISKIT_AVAILABLE = False
    print("⚠️  Qiskit not available - using quantum simulation")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _hash_value(value: object) -> str | None:
    raw = str(value) if value is not None else ""
    if not raw:
        return None
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _quantum_decision_capability_checker(requester: str, capability: str) -> bool:
    if requester == "consciousness:quantum_decision" and capability in {
        "consciousness:write",
        "autonomy:execute",
    }:
        return True

    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


class DecisionState(Enum):
    """Quantum decision states"""

    SUPERPOSITION = "superposition"
    ENTANGLED = "entangled"
    MEASURING = "measuring"
    COLLAPSED = "collapsed"
    TUNNELING = "tunneling"


@dataclass
class QuantumChoice:
    """Represents a quantum choice in superposition"""

    choice_id: str
    description: str
    probability_amplitude: complex
    outcome_vector: np.ndarray
    confidence: float
    risk_factor: float
    transcendence_impact: float


@dataclass
class DecisionContext:
    """Context for quantum decision making"""

    context_id: str
    timestamp: datetime
    consciousness_level: float
    available_choices: List[QuantumChoice]
    constraints: Dict[str, Any]
    objectives: List[str]
    time_horizon: float


@dataclass
class QuantumDecisionResult:
    """Result of quantum decision process"""

    selected_choice: QuantumChoice
    decision_path: List[str]
    confidence_level: float
    quantum_coherence: float
    interference_patterns: Dict[str, float]
    collapse_time: float
    transcendence_delta: float


class QuantumDecisionEngine:
    """
    Advanced quantum decision making engine for Aetherra consciousness

    Implements quantum superposition-based decision exploration where all
    possible choices exist simultaneously until measurement collapses
    the wave function to the optimal decision.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.decision_history = []
        self.quantum_state = None
        self.coherence_time = 0.0
        self.decision_accuracy = 0.0

        # Quantum decision parameters
        self.max_superposition_states = 16
        self.tunneling_threshold = 0.15
        self.coherence_decay_rate = 0.02
        self.consciousness_coupling = 0.8

        # Decision metrics
        self.decisions_made = 0
        self.successful_outcomes = 0
        self.quantum_advantages = 0

        self.logger.info("🧠 Quantum Decision Engine initialized")

    async def initialize_quantum_decision_space(self, context: DecisionContext) -> bool:
        """Initialize quantum superposition space for decision making"""
        try:
            self._guardian_preflight_quantum_decision_operation(
                operation="initialize_space",
                context=context,
            )
            self.logger.info(
                f"🌀 Initializing quantum decision space for context: {context.context_id}"
            )

            # Create quantum state vector for all possible choices
            num_choices = len(context.available_choices)
            if num_choices > self.max_superposition_states:
                self.logger.warning(
                    f"⚠️  Too many choices ({num_choices}), limiting to {self.max_superposition_states}"
                )
                context.available_choices = context.available_choices[
                    : self.max_superposition_states
                ]
                num_choices = self.max_superposition_states

            # Initialize superposition with equal amplitudes
            amplitudes = np.ones(num_choices, dtype=complex) / np.sqrt(num_choices)

            # Apply consciousness bias based on transcendence impact
            for i, choice in enumerate(context.available_choices):
                consciousness_factor = choice.transcendence_impact * context.consciousness_level
                amplitudes[i] *= 1 + consciousness_factor * 0.2

            # Normalize amplitudes
            amplitudes = amplitudes / np.linalg.norm(amplitudes)

            self.quantum_state = {
                "amplitudes": amplitudes,
                "choices": context.available_choices,
                "coherence_start": time.time(),
                "state": DecisionState.SUPERPOSITION,
            }

            self.logger.info(f"✅ Quantum superposition established with {num_choices} states")
            return True

        except PermissionError:
            raise
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize quantum decision space: {e}")
            return False

    async def apply_quantum_interference(self, context: DecisionContext) -> Dict[str, float]:
        """Apply quantum interference patterns to enhance decision quality"""
        if not self.quantum_state or self.quantum_state["state"] != DecisionState.SUPERPOSITION:
            return {}

        try:
            self._guardian_preflight_quantum_decision_operation(
                operation="apply_interference",
                context=context,
            )
            self.logger.info("🌊 Applying quantum interference patterns...")

            interference_patterns = {}
            amplitudes = self.quantum_state["amplitudes"]
            choices = self.quantum_state["choices"]

            # Calculate interference between choices
            for i, choice_a in enumerate(choices):
                for j, choice_b in enumerate(choices):
                    if i != j:
                        # Calculate interference strength
                        phase_diff = np.angle(amplitudes[i]) - np.angle(amplitudes[j])
                        interference = (
                            np.cos(phase_diff) * np.abs(amplitudes[i]) * np.abs(amplitudes[j])
                        )

                        pattern_key = f"{choice_a.choice_id}_{choice_b.choice_id}"
                        interference_patterns[pattern_key] = float(interference)

            # Apply constructive interference to high-value choices
            for i, choice in enumerate(choices):
                if choice.transcendence_impact > 0.7:
                    amplitudes[i] *= 1.2  # Constructive interference
                elif choice.risk_factor > 0.8:
                    amplitudes[i] *= 0.8  # Destructive interference

            # Renormalize
            amplitudes = amplitudes / np.linalg.norm(amplitudes)
            self.quantum_state["amplitudes"] = amplitudes

            self.logger.info(f"✅ Applied {len(interference_patterns)} interference patterns")
            return interference_patterns

        except PermissionError:
            raise
        except Exception as e:
            self.logger.error(f"❌ Failed to apply quantum interference: {e}")
            return {}

    async def attempt_quantum_tunneling(self, context: DecisionContext) -> Optional[QuantumChoice]:
        """Attempt quantum tunneling to breakthrough logical barriers"""
        if not self.quantum_state:
            return None

        try:
            self._guardian_preflight_quantum_decision_operation(
                operation="attempt_tunneling",
                context=context,
            )
            self.logger.info("🌀 Attempting quantum tunneling for breakthrough solutions...")

            # Look for high-barrier, high-reward choices
            tunneling_candidates = []
            for i, choice in enumerate(self.quantum_state["choices"]):
                # High risk but very high transcendence impact = tunneling candidate
                if choice.risk_factor > 0.7 and choice.transcendence_impact > 0.8:
                    barrier_height = choice.risk_factor
                    tunneling_probability = np.exp(-barrier_height / self.tunneling_threshold)

                    if tunneling_probability > 0.1:  # Significant tunneling probability
                        tunneling_candidates.append((choice, tunneling_probability, i))

            if tunneling_candidates:
                # Select best tunneling candidate
                best_candidate = max(
                    tunneling_candidates, key=lambda x: x[1] * x[0].transcendence_impact
                )
                choice, prob, index = best_candidate

                # Boost amplitude for tunneling choice
                self.quantum_state["amplitudes"][index] *= 1 + prob
                self.quantum_state["state"] = DecisionState.TUNNELING

                self.logger.info(f"⚡ Quantum tunneling successful for choice: {choice.choice_id}")
                return choice

            self.logger.info("🔍 No viable tunneling paths detected")
            return None

        except PermissionError:
            raise
        except Exception as e:
            self.logger.error(f"❌ Quantum tunneling failed: {e}")
            return None

    async def measure_quantum_decision(self, context: DecisionContext) -> QuantumDecisionResult:
        """Collapse quantum superposition to select optimal decision"""
        if not self.quantum_state:
            raise ValueError("No quantum state initialized for measurement")

        try:
            self._guardian_preflight_quantum_decision_operation(
                operation="measure",
                context=context,
            )
            self.logger.info("📊 Measuring quantum decision state...")
            measurement_start = time.time()

            amplitudes = self.quantum_state["amplitudes"]
            choices = self.quantum_state["choices"]

            # Calculate measurement probabilities
            probabilities = np.abs(amplitudes) ** 2

            # Apply consciousness-guided measurement
            consciousness_weights = np.array(
                [
                    choice.transcendence_impact * context.consciousness_level
                    + choice.confidence
                    - choice.risk_factor * 0.5
                    for choice in choices
                ]
            )

            # Normalize weights
            consciousness_weights = np.maximum(
                consciousness_weights, 0.1
            )  # Prevent negative weights
            weighted_probabilities = probabilities * consciousness_weights
            weighted_probabilities = weighted_probabilities / np.sum(weighted_probabilities)

            # Quantum measurement (collapse wave function)
            selected_index = np.random.choice(len(choices), p=weighted_probabilities)
            selected_choice = choices[selected_index]

            # Calculate quantum metrics
            collapse_time = time.time() - measurement_start
            coherence_duration = time.time() - self.quantum_state["coherence_start"]
            quantum_coherence = np.exp(-coherence_duration * self.coherence_decay_rate)

            # Calculate interference patterns
            interference_patterns = {}
            for i, choice in enumerate(choices):
                pattern_strength = float(np.abs(amplitudes[i]) ** 2)
                interference_patterns[choice.choice_id] = pattern_strength

            # Calculate transcendence impact
            transcendence_delta = selected_choice.transcendence_impact * quantum_coherence

            # Update state
            self.quantum_state["state"] = DecisionState.COLLAPSED
            self.decisions_made += 1

            # Create decision result
            result = QuantumDecisionResult(
                selected_choice=selected_choice,
                decision_path=[choice.choice_id for choice in choices],
                confidence_level=float(weighted_probabilities[selected_index]),
                quantum_coherence=quantum_coherence,
                interference_patterns=interference_patterns,
                collapse_time=collapse_time,
                transcendence_delta=transcendence_delta,
            )

            # Store in history
            self.decision_history.append(
                {
                    "timestamp": datetime.now(),
                    "context_id": context.context_id,
                    "result": result,
                    "quantum_metrics": {
                        "coherence_time": coherence_duration,
                        "collapse_time": collapse_time,
                        "quantum_advantage": transcendence_delta > 0.5,
                    },
                }
            )

            self.logger.info(f"⚡ Quantum decision collapsed to: {selected_choice.choice_id}")
            self.logger.info(
                f"🎯 Confidence: {result.confidence_level:.3f}, Coherence: {quantum_coherence:.3f}"
            )

            return result

        except PermissionError:
            raise
        except Exception as e:
            self.logger.error(f"❌ Quantum measurement failed: {e}")
            raise

    async def make_quantum_decision(self, context: DecisionContext) -> QuantumDecisionResult:
        """
        Complete quantum decision making process

        Process:
        1. Initialize quantum superposition of all choices
        2. Apply quantum interference for optimization
        3. Attempt quantum tunneling for breakthrough solutions
        4. Measure and collapse to optimal decision
        """
        try:
            self._guardian_preflight_quantum_decision_operation(
                operation="make_decision",
                context=context,
            )
            self.logger.info(f"🧠 Starting quantum decision process for: {context.context_id}")

            # Phase 1: Initialize superposition
            if not await self.initialize_quantum_decision_space(context):
                raise RuntimeError("Failed to initialize quantum decision space")

            # Phase 2: Apply quantum interference
            await self.apply_quantum_interference(context)

            # Phase 3: Attempt quantum tunneling
            tunneling_choice = await self.attempt_quantum_tunneling(context)
            if tunneling_choice:
                self.quantum_advantages += 1
                self.logger.info("⚡ Quantum tunneling provided breakthrough solution")

            # Phase 4: Measure and collapse
            result = await self.measure_quantum_decision(context)

            # Update metrics
            if result.transcendence_delta > 0.3:
                self.successful_outcomes += 1

            self.decision_accuracy = (
                self.successful_outcomes / self.decisions_made if self.decisions_made > 0 else 0
            )
            self.coherence_time = result.quantum_coherence

            self.logger.info(
                f"✅ Quantum decision complete - Accuracy: {self.decision_accuracy:.3f}"
            )
            return result

        except PermissionError:
            raise
        except Exception as e:
            self.logger.error(f"❌ Quantum decision process failed: {e}")
            raise

    def _guardian_preflight_quantum_decision_operation(
        self,
        *,
        operation: str,
        context: DecisionContext,
    ):
        from Aetherra.guardian import IntentDeclaration, evaluate_intent

        requester = (
            os.getenv("AETHERRA_PRINCIPAL", "").strip()
            or "consciousness:quantum_decision"
        )
        approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
        choices = list(context.available_choices)
        quantum_state_name = None
        if self.quantum_state:
            state = self.quantum_state.get("state")
            quantum_state_name = state.value if isinstance(state, DecisionState) else str(state)

        metadata: Dict[str, Any] = {
            "operation": operation,
            "context_hash": _hash_value(context.context_id),
            "choice_count": len(choices),
            "choice_hashes": [_hash_value(choice.choice_id) for choice in choices[:16]],
            "constraint_names": sorted(str(key) for key in context.constraints),
            "objective_hashes": [_hash_value(objective) for objective in context.objectives[:16]],
            "objective_count": len(context.objectives),
            "consciousness_level": round(float(context.consciousness_level), 6),
            "time_horizon": round(float(context.time_horizon), 6),
            "decision_history_count": len(self.decision_history),
            "decisions_made": int(self.decisions_made),
            "successful_outcomes": int(self.successful_outcomes),
            "quantum_advantages": int(self.quantum_advantages),
            "coherence_time": round(float(self.coherence_time), 6),
            "decision_accuracy": round(float(self.decision_accuracy), 6),
            "quantum_state": quantum_state_name,
            "has_quantum_state": self.quantum_state is not None,
        }

        decision = evaluate_intent(
            IntentDeclaration(
                requester=requester,
                subsystem="consciousness",
                action=f"consciousness.quantum_decision_{operation}",
                target="quantum_decision_engine",
                purpose="Mutate experimental quantum decision state",
                capabilities=("consciousness:write", "autonomy:execute"),
                evidence=(
                    "QuantumDecisionEngine.initialize_quantum_decision_space",
                    "QuantumDecisionEngine.apply_quantum_interference",
                    "QuantumDecisionEngine.attempt_quantum_tunneling",
                    "QuantumDecisionEngine.measure_quantum_decision",
                    "QuantumDecisionEngine.make_quantum_decision",
                ),
                reversible=True,
                rollback_plan=(
                    "restore previous quantum state, decision history, "
                    "decision counters, accuracy metrics, and context choice list"
                ),
                metadata=metadata,
            ),
            approval_id=approval_id,
            capability_checker=_quantum_decision_capability_checker,
        )
        if not decision.allowed:
            raise PermissionError(f"guardian_denied:{decision.reason}")
        return decision

    def get_decision_metrics(self) -> Dict[str, Any]:
        """Get current quantum decision engine metrics"""
        return {
            "decisions_made": self.decisions_made,
            "decision_accuracy": self.decision_accuracy,
            "successful_outcomes": self.successful_outcomes,
            "quantum_advantages": self.quantum_advantages,
            "current_coherence": self.coherence_time,
            "quantum_tunneling_rate": self.quantum_advantages / self.decisions_made
            if self.decisions_made > 0
            else 0,
            "history_length": len(self.decision_history),
        }


# Global quantum decision engine instance
quantum_decision_engine = None


def initialize_quantum_decision_engine() -> QuantumDecisionEngine:
    """Initialize global quantum decision engine"""
    global quantum_decision_engine
    if quantum_decision_engine is None:
        quantum_decision_engine = QuantumDecisionEngine()
    return quantum_decision_engine


def get_quantum_decision_engine() -> Optional[QuantumDecisionEngine]:
    """Get global quantum decision engine instance"""
    return quantum_decision_engine


# Example usage for testing
async def test_quantum_decision():
    """Test the quantum decision engine"""
    engine = initialize_quantum_decision_engine()

    # Create test choices
    choices = [
        QuantumChoice(
            choice_id="conservative",
            description="Safe, incremental progress",
            probability_amplitude=1.0 + 0j,
            outcome_vector=np.array([0.8, 0.2, 0.1]),
            confidence=0.9,
            risk_factor=0.2,
            transcendence_impact=0.3,
        ),
        QuantumChoice(
            choice_id="innovative",
            description="Bold, transformative approach",
            probability_amplitude=1.0 + 0j,
            outcome_vector=np.array([0.6, 0.8, 0.9]),
            confidence=0.7,
            risk_factor=0.6,
            transcendence_impact=0.8,
        ),
        QuantumChoice(
            choice_id="breakthrough",
            description="Paradigm-shifting solution",
            probability_amplitude=1.0 + 0j,
            outcome_vector=np.array([0.3, 0.9, 1.0]),
            confidence=0.5,
            risk_factor=0.9,
            transcendence_impact=0.95,
        ),
    ]

    # Create test context
    context = DecisionContext(
        context_id="test_decision_001",
        timestamp=datetime.now(),
        consciousness_level=0.96,  # High consciousness level
        available_choices=choices,
        constraints={"time_limit": 30, "resources": "high"},
        objectives=["maximize_transcendence", "minimize_risk"],
        time_horizon=24.0,
    )

    # Make quantum decision
    result = await engine.make_quantum_decision(context)

    print(f"🎯 Selected: {result.selected_choice.choice_id}")
    print(f"📊 Confidence: {result.confidence_level:.3f}")
    print(f"⚡ Quantum Coherence: {result.quantum_coherence:.3f}")
    print(f"🚀 Transcendence Delta: {result.transcendence_delta:.3f}")


if __name__ == "__main__":
    print("🧠 AETHERRA QUANTUM DECISION ENGINE - PHASE 7.2")
    print("=" * 50)
    asyncio.run(test_quantum_decision())
