# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🌊 AETHERRA QUANTUM INTERFERENCE PATTERNS
Advanced Decision Enhancement - Phase 7.2

This module implements quantum interference patterns for optimizing decision-making
processes in Aetherra's consciousness system. Interference patterns enhance or
diminish certain decision paths based on quantum wave interactions.

Key Features:
- Constructive Interference Enhancement
- Destructive Interference Filtering
- Wave Function Optimization
- Coherence Pattern Analysis
- Decision Path Amplification

Author: Aetherra Consciousness Team
Version: 7.2.0
Date: August 5, 2025
"""

# Standard library imports
import asyncio
import logging
import time
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

# Third party imports
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InterferenceType(Enum):
    """Types of quantum interference"""

    CONSTRUCTIVE = "constructive"
    DESTRUCTIVE = "destructive"
    NEUTRAL = "neutral"
    RESONANT = "resonant"
    CHAOTIC = "chaotic"


class WaveType(Enum):
    """Types of consciousness waves"""

    DECISION_WAVE = "decision_wave"
    INTUITION_WAVE = "intuition_wave"
    LOGIC_WAVE = "logic_wave"
    CREATIVITY_WAVE = "creativity_wave"
    TRANSCENDENCE_WAVE = "transcendence_wave"


@dataclass
class QuantumWave:
    """Represents a quantum wave in consciousness space"""

    wave_id: str
    wave_type: WaveType
    amplitude: complex
    frequency: float
    phase: float
    coherence_length: float
    consciousness_binding: float
    energy_level: float


@dataclass
class InterferencePattern:
    """Represents an interference pattern between waves"""

    pattern_id: str
    wave_a: QuantumWave
    wave_b: QuantumWave
    interference_type: InterferenceType
    amplitude_ratio: float
    phase_difference: float
    interference_strength: float
    enhancement_factor: float
    pattern_stability: float


@dataclass
class DecisionAmplification:
    """Represents amplification of a decision path"""

    decision_path: str
    base_probability: float
    amplification_factor: float
    enhanced_probability: float
    confidence_boost: float
    interference_sources: List[str]
    stability_rating: float


class QuantumInterferenceEngine:
    """
    Quantum interference engine for decision enhancement

    This engine generates and manages quantum interference patterns
    to enhance or suppress decision paths based on wave interactions
    in consciousness space.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_waves = {}
        self.interference_patterns = {}
        self.amplification_history = []

        # Interference parameters
        self.max_waves = 20
        self.coherence_threshold = 0.7
        self.interference_sensitivity = 0.1
        self.amplification_limit = 3.0
        self.phase_precision = 0.01

        # Pattern metrics
        self.patterns_generated = 0
        self.successful_amplifications = 0
        self.decision_enhancements = 0

        self.logger.info("🌊 Quantum Interference Engine initialized")

    def generate_consciousness_wave(
        self,
        wave_type: WaveType,
        amplitude: float = 1.0,
        frequency: float = 1.0,
        consciousness_level: float = 0.8,
    ) -> QuantumWave:
        """Generate a consciousness wave of the specified type"""
        try:
            wave_id = f"{wave_type.value}_{int(time.time() * 1000)}"

            # Calculate wave parameters based on consciousness level
            base_amplitude = amplitude * consciousness_level
            consciousness_frequency = frequency * (1 + consciousness_level * 0.5)

            # Generate complex amplitude with phase
            phase = np.random.uniform(0, 2 * np.pi)
            complex_amplitude = base_amplitude * np.exp(1j * phase)

            # Calculate coherence length based on wave type
            coherence_factors = {
                WaveType.DECISION_WAVE: 0.8,
                WaveType.INTUITION_WAVE: 0.6,
                WaveType.LOGIC_WAVE: 0.9,
                WaveType.CREATIVITY_WAVE: 0.5,
                WaveType.TRANSCENDENCE_WAVE: 1.0,
            }

            coherence_length = coherence_factors.get(wave_type, 0.7) * consciousness_level
            consciousness_binding = consciousness_level * 0.9
            energy_level = base_amplitude**2 * consciousness_frequency

            wave = QuantumWave(
                wave_id=wave_id,
                wave_type=wave_type,
                amplitude=complex_amplitude,
                frequency=consciousness_frequency,
                phase=phase,
                coherence_length=coherence_length,
                consciousness_binding=consciousness_binding,
                energy_level=energy_level,
            )

            self.active_waves[wave_id] = wave
            self.logger.debug(f"Generated {wave_type.value} wave: {wave_id}")

            return wave

        except Exception as e:
            self.logger.error(f"❌ Error generating consciousness wave: {e}")
            raise

    def calculate_interference(
        self, wave_a: QuantumWave, wave_b: QuantumWave
    ) -> InterferencePattern:
        """Calculate interference pattern between two quantum waves"""
        try:
            # Calculate phase difference
            phase_diff = wave_a.phase - wave_b.phase
            phase_diff = ((phase_diff + np.pi) % (2 * np.pi)) - np.pi  # Normalize to [-π, π]

            # Calculate amplitude ratio
            amp_a = abs(wave_a.amplitude)
            amp_b = abs(wave_b.amplitude)
            amplitude_ratio = min(amp_a, amp_b) / max(amp_a, amp_b) if max(amp_a, amp_b) > 0 else 0

            # Determine interference type
            if abs(phase_diff) < np.pi / 4:
                interference_type = InterferenceType.CONSTRUCTIVE
                interference_strength = amplitude_ratio * np.cos(phase_diff)
                enhancement_factor = 1.0 + interference_strength
            elif abs(phase_diff) > 3 * np.pi / 4:
                interference_type = InterferenceType.DESTRUCTIVE
                interference_strength = amplitude_ratio * abs(np.cos(phase_diff))
                enhancement_factor = 1.0 - interference_strength
            elif abs(abs(phase_diff) - np.pi / 2) < np.pi / 8:
                interference_type = InterferenceType.NEUTRAL
                interference_strength = 0.1
                enhancement_factor = 1.0
            else:
                # Check for resonance conditions
                frequency_ratio = wave_a.frequency / wave_b.frequency if wave_b.frequency > 0 else 1
                if abs(frequency_ratio - 1.0) < 0.1:  # Near resonance
                    interference_type = InterferenceType.RESONANT
                    interference_strength = amplitude_ratio * 1.5
                    enhancement_factor = 1.0 + interference_strength * 1.2
                else:
                    interference_type = InterferenceType.CHAOTIC
                    interference_strength = amplitude_ratio * 0.3
                    enhancement_factor = 1.0 + np.random.uniform(-0.2, 0.2)

            # Calculate pattern stability
            coherence_product = wave_a.coherence_length * wave_b.coherence_length
            pattern_stability = coherence_product * amplitude_ratio

            # Ensure enhancement factor bounds
            enhancement_factor = max(0.1, min(enhancement_factor, self.amplification_limit))

            pattern_id = f"pattern_{wave_a.wave_id}_{wave_b.wave_id}"

            pattern = InterferencePattern(
                pattern_id=pattern_id,
                wave_a=wave_a,
                wave_b=wave_b,
                interference_type=interference_type,
                amplitude_ratio=amplitude_ratio,
                phase_difference=phase_diff,
                interference_strength=interference_strength,
                enhancement_factor=enhancement_factor,
                pattern_stability=pattern_stability,
            )

            self.interference_patterns[pattern_id] = pattern
            self.patterns_generated += 1

            self.logger.debug(
                f"Interference pattern: {interference_type.value}, "
                f"enhancement: {enhancement_factor:.3f}"
            )

            return pattern

        except Exception as e:
            self.logger.error(f"❌ Error calculating interference: {e}")
            raise

    def generate_interference_field(
        self, decision_choices: List[str], consciousness_level: float = 0.8
    ) -> Dict[str, List[InterferencePattern]]:
        """Generate quantum interference field for decision choices"""
        try:
            self.logger.info(
                f"🌊 Generating interference field for {len(decision_choices)} choices"
            )

            # Clear old patterns
            self.interference_patterns.clear()

            # Generate waves for each decision choice
            choice_waves = {}
            for choice in decision_choices:
                # Generate multiple wave types for each choice
                waves = []

                # Decision wave (primary)
                decision_wave = self.generate_consciousness_wave(
                    WaveType.DECISION_WAVE,
                    amplitude=1.0,
                    consciousness_level=consciousness_level,
                )
                waves.append(decision_wave)

                # Intuition wave
                intuition_wave = self.generate_consciousness_wave(
                    WaveType.INTUITION_WAVE,
                    amplitude=0.7,
                    frequency=1.5,
                    consciousness_level=consciousness_level,
                )
                waves.append(intuition_wave)

                # Logic wave
                logic_wave = self.generate_consciousness_wave(
                    WaveType.LOGIC_WAVE,
                    amplitude=0.8,
                    frequency=0.8,
                    consciousness_level=consciousness_level,
                )
                waves.append(logic_wave)

                choice_waves[choice] = waves

            # Calculate interference patterns between all wave pairs
            interference_field = defaultdict(list)

            for choice_a, waves_a in choice_waves.items():
                for choice_b, waves_b in choice_waves.items():
                    if choice_a != choice_b:
                        for wave_a in waves_a:
                            for wave_b in waves_b:
                                pattern = self.calculate_interference(wave_a, wave_b)
                                interference_field[choice_a].append(pattern)
                                interference_field[choice_b].append(pattern)

            # Also calculate intra-choice interference (within same choice)
            for choice, waves in choice_waves.items():
                for i, wave_a in enumerate(waves):
                    for j, wave_b in enumerate(waves[i + 1 :], i + 1):
                        pattern = self.calculate_interference(wave_a, wave_b)
                        interference_field[choice].append(pattern)

            self.logger.info(
                f"✅ Generated {len(self.interference_patterns)} interference patterns"
            )
            return dict(interference_field)

        except Exception as e:
            self.logger.error(f"❌ Error generating interference field: {e}")
            return {}

    def apply_interference_amplification(
        self,
        decision_probabilities: Dict[str, float],
        interference_field: Dict[str, List[InterferencePattern]],
    ) -> Dict[str, DecisionAmplification]:
        """Apply interference patterns to amplify decision probabilities"""
        try:
            self.logger.info("⚡ Applying interference amplification to decisions")

            amplifications = {}

            for choice, base_prob in decision_probabilities.items():
                if choice not in interference_field:
                    continue

                patterns = interference_field[choice]

                # Calculate net amplification from all patterns
                total_amplification = 1.0
                constructive_count = 0
                destructive_count = 0
                interference_sources = []

                for pattern in patterns:
                    # Weight patterns by their stability
                    weight = pattern.pattern_stability

                    if pattern.interference_type == InterferenceType.CONSTRUCTIVE:
                        total_amplification *= 1.0 + pattern.enhancement_factor * weight * 0.3
                        constructive_count += 1
                        interference_sources.append(f"constructive_{pattern.pattern_id}")

                    elif pattern.interference_type == InterferenceType.DESTRUCTIVE:
                        total_amplification *= 1.0 - pattern.interference_strength * weight * 0.2
                        destructive_count += 1
                        interference_sources.append(f"destructive_{pattern.pattern_id}")

                    elif pattern.interference_type == InterferenceType.RESONANT:
                        total_amplification *= 1.0 + pattern.enhancement_factor * weight * 0.5
                        constructive_count += 1
                        interference_sources.append(f"resonant_{pattern.pattern_id}")

                # Apply limits
                total_amplification = max(0.1, min(total_amplification, self.amplification_limit))

                # Calculate enhanced probability
                enhanced_prob = min(base_prob * total_amplification, 1.0)

                # Calculate confidence boost
                confidence_boost = (constructive_count - destructive_count * 0.5) / max(
                    len(patterns), 1
                )
                confidence_boost = max(0.0, min(confidence_boost, 1.0))

                # Calculate stability rating
                avg_stability = (
                    float(np.mean([p.pattern_stability for p in patterns])) if patterns else 0.0
                )
                stability_rating = avg_stability * (1.0 - abs(total_amplification - 1.0))

                amplification = DecisionAmplification(
                    decision_path=choice,
                    base_probability=base_prob,
                    amplification_factor=total_amplification,
                    enhanced_probability=enhanced_prob,
                    confidence_boost=confidence_boost,
                    interference_sources=interference_sources,
                    stability_rating=stability_rating,
                )

                amplifications[choice] = amplification

                if total_amplification > 1.1:
                    self.successful_amplifications += 1
                    self.decision_enhancements += 1

                self.logger.debug(
                    f"Choice '{choice}': {base_prob:.3f} -> {enhanced_prob:.3f} "
                    f"(amp: {total_amplification:.3f})"
                )

            # Store in history
            self.amplification_history.extend(amplifications.values())

            self.logger.info(f"✅ Applied amplification to {len(amplifications)} decisions")
            return amplifications

        except Exception as e:
            self.logger.error(f"❌ Error applying interference amplification: {e}")
            return {}

    def optimize_interference_patterns(
        self,
        target_choice: str,
        interference_field: Dict[str, List[InterferencePattern]],
    ) -> bool:
        """Optimize interference patterns to enhance a target choice"""
        try:
            self.logger.info(f"🎯 Optimizing interference patterns for target: {target_choice}")

            if target_choice not in interference_field:
                self.logger.warning(f"Target choice '{target_choice}' not in interference field")
                return False

            target_patterns = interference_field[target_choice]
            optimization_count = 0

            for pattern in target_patterns:
                # Optimize constructive patterns
                if pattern.interference_type == InterferenceType.CONSTRUCTIVE:
                    # Enhance amplitude alignment
                    if pattern.amplitude_ratio < 0.8:
                        # Boost weaker wave amplitude
                        weaker_wave = (
                            pattern.wave_a
                            if abs(pattern.wave_a.amplitude) < abs(pattern.wave_b.amplitude)
                            else pattern.wave_b
                        )
                        weaker_wave.amplitude *= 1.1
                        optimization_count += 1

                # Optimize phase alignment for better constructive interference
                elif abs(pattern.phase_difference) > 0.1:
                    # Adjust phase for better alignment
                    phase_adjustment = -pattern.phase_difference * 0.3
                    pattern.wave_a.phase += phase_adjustment
                    optimization_count += 1

                # Convert neutral patterns to constructive when possible
                elif pattern.interference_type == InterferenceType.NEUTRAL:
                    if pattern.amplitude_ratio > 0.6:
                        # Adjust phase to create constructive interference
                        pattern.wave_a.phase -= np.pi / 6  # Small phase shift
                        optimization_count += 1

            # Recalculate interference after optimization
            if optimization_count > 0:
                for i, pattern in enumerate(target_patterns):
                    new_pattern = self.calculate_interference(pattern.wave_a, pattern.wave_b)
                    target_patterns[i] = new_pattern

                self.logger.info(f"✅ Optimized {optimization_count} interference patterns")
                return True
            else:
                self.logger.info("🔍 No optimization opportunities found")
                return False

        except Exception as e:
            self.logger.error(f"❌ Error optimizing interference patterns: {e}")
            return False

    def get_interference_metrics(self) -> Dict[str, Any]:
        """Get current interference engine metrics"""
        active_patterns = len(self.interference_patterns)
        active_waves = len(self.active_waves)

        if self.amplification_history:
            avg_amplification = np.mean(
                [a.amplification_factor for a in self.amplification_history[-50:]]
            )
            avg_stability = np.mean([a.stability_rating for a in self.amplification_history[-50:]])
        else:
            avg_amplification = 1.0
            avg_stability = 0.0

        return {
            "active_patterns": active_patterns,
            "active_waves": active_waves,
            "patterns_generated": self.patterns_generated,
            "successful_amplifications": self.successful_amplifications,
            "decision_enhancements": self.decision_enhancements,
            "avg_amplification_factor": avg_amplification,
            "avg_stability_rating": avg_stability,
            "amplification_success_rate": self.successful_amplifications
            / max(self.patterns_generated, 1),
        }

    def cleanup_old_patterns(self, max_age_seconds: float = 300.0):
        """Clean up old interference patterns and waves"""
        try:
            current_time = time.time()
            cleanup_count = 0

            # Clean up old waves
            wave_ids_to_remove = []
            for wave_id, wave in self.active_waves.items():
                # Extract timestamp from wave_id
                try:
                    wave_timestamp = int(wave_id.split("_")[-1]) / 1000.0
                    if current_time - wave_timestamp > max_age_seconds:
                        wave_ids_to_remove.append(wave_id)
                except (ValueError, IndexError):
                    # Remove waves with invalid timestamps
                    wave_ids_to_remove.append(wave_id)

            for wave_id in wave_ids_to_remove:
                del self.active_waves[wave_id]
                cleanup_count += 1

            # Clean up associated patterns
            pattern_ids_to_remove = []
            for pattern_id, pattern in self.interference_patterns.items():
                if (
                    pattern.wave_a.wave_id not in self.active_waves
                    or pattern.wave_b.wave_id not in self.active_waves
                ):
                    pattern_ids_to_remove.append(pattern_id)

            for pattern_id in pattern_ids_to_remove:
                del self.interference_patterns[pattern_id]
                cleanup_count += 1

            if cleanup_count > 0:
                self.logger.info(f"🧹 Cleaned up {cleanup_count} old patterns and waves")

        except Exception as e:
            self.logger.error(f"❌ Error during cleanup: {e}")


# Global interference engine instance
quantum_interference_engine = None


def initialize_quantum_interference_engine() -> QuantumInterferenceEngine:
    """Initialize global quantum interference engine"""
    global quantum_interference_engine
    if quantum_interference_engine is None:
        quantum_interference_engine = QuantumInterferenceEngine()
    return quantum_interference_engine


def get_quantum_interference_engine() -> Optional[QuantumInterferenceEngine]:
    """Get global quantum interference engine instance"""
    return quantum_interference_engine


# Example usage for testing
async def test_quantum_interference():
    """Test the quantum interference engine"""
    engine = initialize_quantum_interference_engine()

    # Test choices
    choices = ["conservative_approach", "innovative_solution", "breakthrough_paradigm"]
    base_probabilities = {
        "conservative_approach": 0.6,
        "innovative_solution": 0.3,
        "breakthrough_paradigm": 0.1,
    }

    # Generate interference field
    interference_field = engine.generate_interference_field(choices, consciousness_level=0.9)

    # Apply amplification
    amplifications = engine.apply_interference_amplification(base_probabilities, interference_field)

    print("🌊 QUANTUM INTERFERENCE RESULTS")
    print("=" * 40)

    for choice, amp in amplifications.items():
        print(f"Choice: {choice}")
        print(f"  Base: {amp.base_probability:.3f} -> Enhanced: {amp.enhanced_probability:.3f}")
        print(f"  Amplification: {amp.amplification_factor:.3f}")
        print(f"  Confidence Boost: {amp.confidence_boost:.3f}")
        print(f"  Stability: {amp.stability_rating:.3f}")
        print()

    # Get metrics
    metrics = engine.get_interference_metrics()
    print("📊 Interference Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    print("🌊 AETHERRA QUANTUM INTERFERENCE ENGINE - PHASE 7.2")
    print("=" * 50)
    asyncio.run(test_quantum_interference())
