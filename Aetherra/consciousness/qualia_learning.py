# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Qualia Learning (QL) — Phase 3
===============================

Adaptive qualia parameter adjustment from lived experience.
Online learning adjusts baselines and sensitivities based on outcomes
(success/failure/novelty/strain).

Parameters are clamped and decay toward defaults to prevent runaway drift.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class QualiaParams:
    """Learned parameters for qualia update dynamics.

    These values control how strongly qualia responds to different stimuli.
    All values are clamped to safe ranges.
    """

    curiosity_gain: float = 0.05  # How much novelty increases curiosity [0.01, 0.1]
    error_penalty: float = 0.05  # How much errors reduce certainty [0.01, 0.1]
    success_boost: float = 0.1  # How much success increases confidence [0.05, 0.2]
    certainty_gain: float = 0.02  # Baseline certainty increase [0.01, 0.05]

    def clamp(self) -> None:
        """Ensure all parameters are within safe bounds."""
        self.curiosity_gain = max(0.01, min(0.1, self.curiosity_gain))
        self.error_penalty = max(0.01, min(0.1, self.error_penalty))
        self.success_boost = max(0.05, min(0.2, self.success_boost))
        self.certainty_gain = max(0.01, min(0.05, self.certainty_gain))


class QualiaLearner:
    """Adaptive qualia learning from experience.

    Adjusts qualia parameters based on success/failure patterns:
    - Many errors → reduce curiosity, increase error penalty (more cautious)
    - Many successes → increase success boost and certainty gain (more confident)

    All adjustments are multiplicative and clamped to prevent drift.
    """

    def __init__(self):
        """Initialize qualia learner with default parameters."""
        self.p = QualiaParams()
        self._seen_errors = 0
        self._seen_success = 0
        self._decay_rate = 0.995  # Slow decay toward defaults

    def on_errors(self, n: int) -> None:
        """Record error occurrences and adapt parameters.

        Makes the system less curious and more cautious.

        Args:
            n: Number of errors observed
        """
        self._seen_errors += n

        # Make the system less curious and more cautious if many errors
        self.p.curiosity_gain = max(0.01, self.p.curiosity_gain * 0.98)
        self.p.error_penalty = min(0.1, self.p.error_penalty * 1.02)

        self.p.clamp()

    def on_successes(self, n: int) -> None:
        """Record successful outcomes and adapt parameters.

        Increases satisfaction impact and certainty gain.

        Args:
            n: Number of successes observed
        """
        self._seen_success += n

        # Increase satisfaction impact, modestly raise certainty gain
        self.p.success_boost = min(0.2, self.p.success_boost * 1.01)
        self.p.certainty_gain = min(0.05, self.p.certainty_gain * 1.01)

        self.p.clamp()

    def decay_toward_defaults(self) -> None:
        """Slowly decay parameters toward defaults to prevent runaway drift.

        Call this periodically (e.g., every macro-reflection).
        """
        defaults = QualiaParams()

        # Exponential decay toward defaults
        self.p.curiosity_gain = (self._decay_rate * self.p.curiosity_gain) + (
            (1 - self._decay_rate) * defaults.curiosity_gain
        )
        self.p.error_penalty = (self._decay_rate * self.p.error_penalty) + (
            (1 - self._decay_rate) * defaults.error_penalty
        )
        self.p.success_boost = (self._decay_rate * self.p.success_boost) + (
            (1 - self._decay_rate) * defaults.success_boost
        )
        self.p.certainty_gain = (self._decay_rate * self.p.certainty_gain) + (
            (1 - self._decay_rate) * defaults.certainty_gain
        )

        self.p.clamp()

    def get_stats(self) -> dict:
        """Get diagnostic statistics for telemetry.

        Returns:
            Dict with error/success counts and current parameters
        """
        return {
            "errors_seen": self._seen_errors,
            "successes_seen": self._seen_success,
            "params": {
                "curiosity_gain": self.p.curiosity_gain,
                "error_penalty": self.p.error_penalty,
                "success_boost": self.p.success_boost,
                "certainty_gain": self.p.certainty_gain,
            },
        }
