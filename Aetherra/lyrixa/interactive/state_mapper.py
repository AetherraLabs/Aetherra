#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""
🎯 Lyrixa State Mapper
======================

Maps system health signals to emotional states and expression intensity.
Loads all mapping rules and thresholds from state_map.json.

This replaces the hardcoded emotion_mapper.py with JSON-driven configuration,
making it easy to tune Lyrixa's reactions without editing Python code.

State Mapping Rules:
-------------------
Source              | Signal → Range           | Mapping → Expression
--------------------|--------------------------|---------------------
Memory Pulse        | coherence_score (0..1)   | <0.7="concerned"; 0.7-0.9="focused"; >0.9="calm"
Homeostasis         | quarantined_actuators,   | spikes → "concerned"; decay → baseline
                    | dlq_count, drops_*       |
STORM Shadow        | sheaf_inconsistency,     | high inconsist → "pensive"; perfect coherence → "confident"
                    | coherence_score          |
Kernel Health       | queue sizes/limits,      | CB open or high backlog → "on-edge"
                    | circuit breaker state    |
Chat Stream         | SSE lifecycle +          | low confidence → softer tone; resume → quick "blink"
                    | confidence               |
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from Aetherra.security.sandbox import SandboxViolation, safe_eval

logger = logging.getLogger(__name__)


class StateMapper:
    """
    Maps system health signals to emotional states and intensities.
    Loads all configuration from state_map.json.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the state mapper.

        Args:
            config_path: Path to state_map.json (defaults to this directory)
        """
        if config_path is None:
            config_path = Path(__file__).parent / "state_map.json"

        self.config_path = config_path
        self.config = self._load_config()

        # Extract commonly used configs
        self.signal_weights = self.config["signal_weights"]
        self.thresholds = self.config["thresholds"]
        self.state_mapping = self.config["state_mapping"]
        self.expression_configs = self.config["expression_configs"]
        self.safety = self.config["safety"]

        logger.info(f"🎯 State Mapper loaded from {config_path}")

    def _load_config(self) -> Dict:
        """Load and validate state_map.json."""
        if not self.config_path.exists():
            logger.error(f"❌ state_map.json not found at {self.config_path}")
            raise FileNotFoundError(f"state_map.json not found at {self.config_path}")

        try:
            with open(self.config_path, encoding="utf-8") as f:
                config = json.load(f)

            # Validate required sections
            required_keys = [
                "signal_weights",
                "thresholds",
                "state_mapping",
                "expression_configs",
                "safety",
            ]
            missing = [k for k in required_keys if k not in config]
            if missing:
                raise ValueError(f"Missing required config sections: {missing}")

            logger.debug("✅ state_map.json loaded and validated")
            return config

        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in state_map.json: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to load state_map.json: {e}")
            raise

    def map_memory_pulse(self, coherence_score: float) -> Tuple[str, float]:
        """
        Map memory coherence to mood and intensity.

        Args:
            coherence_score: Memory coherence score (0.0-1.0)

        Returns:
            Tuple of (mood, intensity)
        """
        rules = self.state_mapping["memory_pulse"]["rules"]
        thresholds = self.thresholds["memory"]

        # Evaluate rules in order
        for rule in rules:
            condition = rule["condition"]
            mood = rule["mood"]

            # Parse condition
            if "<" in condition:
                threshold_key = condition.split("<")[1].strip()
                # Support dotted paths like thresholds.memory.coherence_low
                if "." in threshold_key:
                    threshold_key = threshold_key.split(".")[-1]
                if coherence_score < thresholds[threshold_key]:
                    intensity = self._evaluate_intensity_formula(
                        rule.get("intensity_formula", rule.get("intensity_base", "0.5")),
                        {"coherence_score": coherence_score, "coherence": coherence_score},
                    )
                    return (mood, intensity)

            elif ">" in condition:
                threshold_key = condition.split(">")[1].strip()
                if "." in threshold_key:
                    threshold_key = threshold_key.split(".")[-1]
                if coherence_score > thresholds[threshold_key]:
                    intensity = self._evaluate_intensity_formula(
                        rule.get("intensity_formula", rule.get("intensity_base", "0.5")),
                        {"coherence_score": coherence_score, "coherence": coherence_score},
                    )
                    return (mood, intensity)

            elif "between" in condition:
                # Parse "coherence_score between coherence_low and coherence_high"
                parts = condition.split()
                low_key = parts[2]
                high_key = parts[4]
                if "." in low_key:
                    low_key = low_key.split(".")[-1]
                if "." in high_key:
                    high_key = high_key.split(".")[-1]
                if thresholds[low_key] <= coherence_score < thresholds[high_key]:
                    intensity = self._evaluate_intensity_formula(
                        rule.get("intensity_formula", rule.get("intensity_base", "0.5")),
                        {"coherence_score": coherence_score, "coherence": coherence_score},
                    )
                    return (mood, intensity)

        # Default fallback
        return ("calm", 0.3)

    def map_homeostasis_signal(
        self, dlq_count: int, quarantined_count: int, drops_total: int = 0
    ) -> Tuple[str, float]:
        """
        Map homeostasis health to mood and intensity.

        Args:
            dlq_count: Dead letter queue count
            quarantined_count: Number of quarantined actuators
            drops_total: Total dropped tasks/events

        Returns:
            Tuple of (mood, intensity)
        """
        thresholds = self.thresholds["homeostasis"]

        concern_score = 0.0

        # DLQ contribution
        if dlq_count >= thresholds["dlq_critical"]:
            concern_score += 0.4
        elif dlq_count >= thresholds["dlq_warning"]:
            concern_score += 0.2

        # Quarantine contribution
        if quarantined_count >= thresholds["quarantine_critical"]:
            concern_score += 0.3
        elif quarantined_count >= thresholds["quarantine_warning"]:
            concern_score += 0.15

        # Drops contribution
        if drops_total > 50:
            concern_score += 0.2
        elif drops_total > 10:
            concern_score += 0.1

        # Simple mapping by concern score
        if concern_score >= 0.7:
            return ("concerned", min(1.0, 0.6 + concern_score))
        if concern_score >= 0.3:
            return ("focused", min(1.0, 0.4 + concern_score))
        return ("calm", 0.3)

    def map_kernel_health(
        self, queue_size: int, queue_limit: int, circuit_breaker_state: str, drops_burst: int = 0
    ) -> Tuple[str, float]:
        """
        Map kernel health to mood and intensity.

        Args:
            queue_size: Current queue size
            queue_limit: Queue capacity limit
            circuit_breaker_state: CB state ("closed", "half_open", "open")
            drops_burst: Burst drop count

        Returns:
            Tuple of (mood, intensity)
        """
        backpressure_ratio = queue_size / queue_limit if queue_limit > 0 else 0.0
        rules = self.state_mapping["kernel_health"]["rules"]
        thresholds = self.thresholds["kernel"]

        # Evaluate rules in priority order adapting JSON condition format
        for rule in rules:
            condition = rule["condition"]
            mood = rule["mood"]

            normalized = condition.replace('"', "'")

            # Circuit breaker open OR expression
            if (
                "circuit_breaker" in normalized
                and "open" in normalized
                and circuit_breaker_state == "open"
            ):
                return (mood, rule.get("intensity_base", 0.9))

            # Backpressure conditions (JSON uses 'backpressure >= thresholds.kernel.backpressure_high')
            if "backpressure" in normalized and ">=" in normalized:
                threshold_key = normalized.split(">=")[1].strip()
                # remove possible OR tail
                if " OR" in threshold_key:
                    threshold_key = threshold_key.split(" OR")[0].strip()
                if "." in threshold_key:
                    threshold_key = threshold_key.split(".")[-1]
                if backpressure_ratio >= thresholds.get(threshold_key, 1.0):
                    intensity_formula = rule.get("intensity_formula")
                    if intensity_formula:
                        intensity = self._evaluate_intensity_formula(
                            intensity_formula,
                            {
                                "backpressure_ratio": backpressure_ratio,
                                "backpressure": backpressure_ratio,
                            },
                        )
                    else:
                        intensity = float(rule.get("intensity_base", 0.7))
                    return (mood, intensity)

            # Combined circuit breaker OR backpressure critical condition
            if (
                "backpressure" in normalized
                and "critical" in normalized
                and backpressure_ratio >= thresholds.get("backpressure_critical", 0.95)
            ):
                return (mood, float(rule.get("intensity_base", 0.9)))

            # Default rule
            if normalized.strip() == "default":
                return (mood, float(rule.get("intensity_base", 0.3)))

        # Default fallback
        return ("calm", 0.3)

    def map_storm_shadow(
        self, sheaf_inconsistency: float, coherence_score: float
    ) -> Tuple[str, float]:
        """
        Map STORM shadow metrics to mood and intensity.

        Args:
            sheaf_inconsistency: Sheaf inconsistency score (0.0-1.0)
            coherence_score: STORM coherence score (0.0-1.0)

        Returns:
            Tuple of (mood, intensity)
        """
        rules = self.state_mapping["storm_shadow"]["rules"]
        thresholds = self.thresholds["storm"]

        # Evaluate rules in order
        for rule in rules:
            condition = rule["condition"]
            mood = rule["mood"]

            if "sheaf_inconsistency" in condition and ">=" in condition:
                threshold_key = condition.split(">=")[1].strip()
                if "." in threshold_key:
                    threshold_key = threshold_key.split(".")[-1]
                if sheaf_inconsistency >= thresholds[threshold_key]:
                    intensity = self._evaluate_intensity_formula(
                        rule["intensity_formula"],
                        {"sheaf_inconsistency": sheaf_inconsistency},
                    )
                    return (mood, intensity)

            if "coherence" in condition and ">=" in condition:
                threshold_key = condition.split(">=")[1].strip()
                if "." in threshold_key:
                    threshold_key = threshold_key.split(".")[-1]
                if coherence_score >= thresholds[threshold_key]:
                    intensity = self._evaluate_intensity_formula(
                        rule["intensity_formula"],
                        {"coherence_score": coherence_score, "coherence": coherence_score},
                    )
                    return (mood, intensity)

        # Default fallback
        return ("calm", 0.4)

    def map_chat_stream_event(self, event_type: str, confidence: float) -> Tuple[str, float]:
        """
        Map chat stream events to mood and intensity.

        Args:
            event_type: Stream event type (start, complete, resume, error)
            confidence: Reply confidence score (0.0-1.0)

        Returns:
            Tuple of (mood, intensity)
        """
        rules = self.state_mapping["chat_stream"]["rules"]
        thresholds = self.thresholds["chat"]

        # Evaluate rules matching event_type
        for rule in rules:
            condition = rule["condition"]
            mood = rule["mood"]

            if event_type in condition:
                # Handle confidence-based rules for stream_complete
                if event_type == "stream_complete" and "confidence" in condition:
                    if "<" in condition:
                        threshold_key = condition.split("<")[1].strip().split()[0]
                        if "." in threshold_key:
                            threshold_key = threshold_key.split(".")[-1]
                        if confidence < thresholds[threshold_key]:
                            return (mood, 0.5)
                    elif "between" in condition:
                        # Parse "between X and Y"
                        parts = condition.split()
                        low_key = parts[parts.index("between") + 1]
                        high_key = parts[parts.index("and") + 1]
                        if "." in low_key:
                            low_key = low_key.split(".")[-1]
                        if "." in high_key:
                            high_key = high_key.split(".")[-1]
                        if thresholds[low_key] <= confidence < thresholds[high_key]:
                            return (mood, 0.5)
                    elif ">=" in condition:
                        threshold_key = condition.split(">=")[1].strip()
                        if "." in threshold_key:
                            threshold_key = threshold_key.split(".")[-1]
                        if confidence >= thresholds[threshold_key]:
                            return (mood, 0.7)
                else:
                    # Simple event match (no confidence check)
                    normalized = condition.strip().replace('"', "'")
                    if normalized == f"event_type == '{event_type}'":
                        intensity_val = rule.get(
                            "intensity_formula", rule.get("intensity_base", 0.7)
                        )
                        if isinstance(intensity_val, str):
                            try:
                                intensity = float(intensity_val)
                            except Exception:
                                intensity = 0.7
                        else:
                            intensity = float(intensity_val)
                        return (mood, intensity)

        # Default fallback
        return ("calm", 0.3)

    def combine_signals(
        self, signals: Dict[str, Tuple[str, float]]
    ) -> Tuple[str, float, List[str]]:
        """
        Combine multiple signals into a single emotion state.

        Args:
            signals: Dict mapping signal source to (mood, intensity) tuples

        Returns:
            Tuple of (final_mood, final_intensity, reasons)
        """
        if not signals:
            return ("calm", 0.3, ["no_signals"])

        # Collect all moods with their weighted intensities
        mood_scores: Dict[str, float] = {}
        reasons = []

        for source, (mood, intensity) in signals.items():
            weight = self._get_source_weight(source)
            weighted_intensity = intensity * weight

            mood_scores[mood] = mood_scores.get(mood, 0.0) + weighted_intensity
            reasons.append(f"{source}={mood}@{intensity:.2f}")

        # Priority ordering for mood selection
        mood_priority = {
            "on_edge": 5,
            "concerned": 4,
            "pensive": 3,
            "focused": 2,
            "thoughtful": 2,
            "confident": 2,
            "delighted": 1,
            "calm": 1,
            "resting": 0,
        }

        # Select mood with highest combined score, breaking ties by priority
        best_mood = max(mood_scores.items(), key=lambda x: (x[1], mood_priority.get(x[0], 0)))[0]

        # Compute final intensity as weighted average
        total_weight = sum(self._get_source_weight(s) for s in signals)
        final_intensity = (
            sum(
                intensity * self._get_source_weight(source)
                for source, (_, intensity) in signals.items()
            )
            / total_weight
            if total_weight > 0
            else 0.5
        )

        return (best_mood, final_intensity, reasons)

    def _get_source_weight(self, source: str) -> float:
        """Get weight for a signal source."""
        weight_map = {
            "memory": self.signal_weights["memory_coherence"],
            "homeostasis": self.signal_weights["homeostasis_health"],
            "kernel": self.signal_weights["kernel_backpressure"],
            "storm": self.signal_weights["storm_consistency"],
            "chat": 0.1,  # Chat events are transient
        }
        return weight_map.get(source, 0.1)

    def adjust_for_context(
        self, mood: str, intensity: float, is_user_idle: bool = False, error_burst: bool = False
    ) -> Tuple[str, float]:
        """
        Adjust mood/intensity based on contextual factors.

        Args:
            mood: Base mood
            intensity: Base intensity
            is_user_idle: Whether user is currently idle
            error_burst: Whether an error burst is detected

        Returns:
            Adjusted (mood, intensity)
        """
        # User idle → transition to resting
        if is_user_idle and mood in ["calm", "focused"]:
            return ("resting", 0.2)

        # Error burst → elevate to concerned if not already critical
        if error_burst and mood not in ["on_edge", "concerned"]:
            return ("concerned", max(0.7, intensity))

        return (mood, intensity)

    def _evaluate_intensity_formula(self, formula: str, variables: Dict[str, float]) -> float:
        """
        Safely evaluate intensity formula with given variables.

        Args:
            formula: Python expression string
            variables: Dict of variable names to values

        Returns:
            Evaluated intensity (clamped to 0.0-1.0)
        """
        try:
            result = safe_eval(formula, variables)
            if isinstance(result, bool) or not isinstance(result, int | float):
                raise SandboxViolation("Intensity formula must return a number")
            return max(0.0, min(1.0, float(result)))
        except (ArithmeticError, SandboxViolation, TypeError, ValueError) as e:
            logger.warning(f"⚠️ Failed to evaluate intensity formula '{formula}': {e}")
            return 0.5  # Safe default

    def get_expression_config(self, state: str) -> Dict:
        """Get expression configuration for a given state."""
        return self.expression_configs.get(state, self.expression_configs.get("calm", {}))

    def reload_config(self):
        """Reload state_map.json (useful for live tuning)."""
        logger.info("🔄 Reloading state_map.json")
        self.config = self._load_config()
        self.signal_weights = self.config["signal_weights"]
        self.thresholds = self.config["thresholds"]
        self.state_mapping = self.config["state_mapping"]
        self.expression_configs = self.config["expression_configs"]
        self.safety = self.config["safety"]


# Module-level singleton
_state_mapper: Optional[StateMapper] = None


def get_state_mapper() -> StateMapper:
    """Get the global state mapper instance."""
    global _state_mapper
    if _state_mapper is None:
        _state_mapper = StateMapper()
    return _state_mapper


def set_state_mapper(mapper: StateMapper):
    """Set a custom state mapper (useful for testing/tuning)."""
    global _state_mapper
    _state_mapper = mapper
