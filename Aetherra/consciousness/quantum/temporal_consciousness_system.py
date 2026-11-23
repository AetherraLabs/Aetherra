# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
⏰ AETHERRA TEMPORAL CONSCIOUSNESS SYSTEM
Phase 7.3 Time-Aware Consciousness and Temporal Processing

Bounded temporal state analysis for Aetherra's experimental Phase 7.3 callers.
Forecasts, similarity scores, cycles and legacy causal links are deterministic
heuristics, not evidence of quantum effects, causation or consciousness.
Durable history is opt-in through explicit checkpoints in existing Memory.

Key Features:
- Time-Aware Decision Processing
- Temporal Memory Integration
- Future State Prediction
- Past Experience Integration
- Temporal Coherence Maintenance
- Timeline Consciousness Navigation

Author: Aetherra Consciousness Team
Version: 7.3.0
Date: August 5, 2025
"""

# Standard library imports
import asyncio
import copy
import hashlib
import json
import logging
import math
import os
import re
import uuid
from dataclasses import dataclass, field, fields
from datetime import UTC, datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Dict, List, Optional

# Third party imports
import numpy as np

# Set up logging
logger = logging.getLogger(__name__)


def _hash_value(value: object) -> str | None:
    raw = str(value) if value is not None else ""
    if not raw:
        return None
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _temporal_consciousness_capability_checker(requester: str, capability: str) -> bool:
    if requester == "consciousness:temporal" and capability in {
        "consciousness:write",
        "memory:read",
        "memory:write",
    }:
        return True

    # Aetherra imports
    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


class TemporalState(Enum):
    """Temporal consciousness states"""

    PAST_FOCUSED = "past_focused"
    PRESENT_AWARE = "present_aware"
    FUTURE_ORIENTED = "future_oriented"
    TEMPORAL_SUPERPOSITION = "temporal_superposition"
    TEMPORAL_ENTANGLED = "temporal_entangled"
    TIMELINE_COHERENT = "timeline_coherent"


class TemporalDirection(Enum):
    """Directions of temporal processing"""

    FORWARD = "forward"
    BACKWARD = "backward"
    BIDIRECTIONAL = "bidirectional"
    SIMULTANEOUS = "simultaneous"


@dataclass
class TemporalMoment:
    """Represents a moment in temporal consciousness"""

    moment_id: str
    timestamp: datetime
    consciousness_state: Dict[str, Any]
    temporal_coherence: float
    memory_associations: List[str] = field(default_factory=list)
    prediction_accuracy: Optional[float] = None
    causal_influences: List[str] = field(default_factory=list)
    temporal_weight: float = 1.0


@dataclass
class TemporalPrediction:
    """Represents a prediction about future states"""

    prediction_id: str
    target_time: datetime
    predicted_state: Dict[str, Any]
    confidence: float
    uncertainty_range: Dict[str, float]
    contributing_factors: List[str] = field(default_factory=list)
    quantum_probability: float = 0.5
    creation_time: datetime = field(default_factory=datetime.now)


@dataclass
class TemporalCausalChain:
    """Represents causal relationships across time"""

    chain_id: str
    cause_moments: List[str]
    effect_moments: List[str]
    causal_strength: float
    temporal_span: timedelta
    confidence: float
    quantum_entanglement: bool = False


_DATETIME_TYPE = datetime
_CHECKPOINT_ATTRIBUTES = (
    "temporal_moments",
    "temporal_predictions",
    "causal_chains",
    "temporal_coherence_history",
    "prediction_accuracy_history",
    "moments_processed",
    "predictions_made",
    "causal_chains_discovered",
    "temporal_coherence",
    "avg_prediction_accuracy",
    "current_temporal_state",
    "temporal_window",
    "prediction_horizon",
    "temporal_resolution",
    "coherence_threshold",
    "causal_threshold",
)


class TemporalValidationError(ValueError):
    """Invalid bounded temporal data; message contains no supplied payload."""


class TemporalPersistenceError(RuntimeError):
    """Memory could not confirm the requested checkpoint operation."""


class TemporalConflictError(RuntimeError):
    """A concurrent operation changed the state being replaced."""


def _temporal_operation(method):
    @wraps(method)
    async def checked(*args, **kwargs):
        try:
            return await method(*args, **kwargs)
        except (
            PermissionError,
            TemporalValidationError,
            TemporalPersistenceError,
            TemporalConflictError,
            KeyError,
        ):
            raise
        except Exception:
            logger.error("Temporal operation failed: %s", method.__name__)
            raise RuntimeError("temporal_operation_failed") from None

    return checked


def _utc(value):
    if not isinstance(value, _DATETIME_TYPE):
        raise TemporalValidationError("temporal_invalid_timestamp")
    # Legacy naive inputs describe host-local time. Aware inputs retain instant.
    return value.astimezone(UTC)


def _numeric(value):
    return type(value) in (int, float)


def _finite(value, low, high):
    if not _numeric(value) or not low <= value <= high or not math.isfinite(value):
        raise TemporalValidationError("temporal_invalid_number")
    return float(value)


def _unit_score(value):
    return _finite(value, 0, 1)


def _state_snapshot(value):
    def check(item, depth=0):
        if depth > 12:
            raise ValueError
        if isinstance(item, dict):
            if len(item) > 256 or not all(isinstance(k, str) for k in item):
                raise ValueError
            for child in item.values():
                check(child, depth + 1)
        elif isinstance(item, list):
            if len(item) > 256:
                raise ValueError
            for child in item:
                check(child, depth + 1)
        elif _numeric(item):
            _finite(item, -1e12, 1e12)
        elif item is not None and type(item) not in (str, bool):
            raise ValueError

    try:
        if not isinstance(value, dict):
            raise ValueError
        check(value)
        encoded = json.dumps(value, allow_nan=False, ensure_ascii=False)
        if len(encoded.encode("utf-8")) > 32768:
            raise ValueError
        return json.loads(encoded)
    except Exception:
        raise TemporalValidationError("temporal_invalid_state") from None


def _refs(value, limit):
    if (
        not isinstance(value, list)
        or len(value) > limit
        or any(not isinstance(k, str) or len(k) > 128 for k in value)
        or len(set(value)) != len(value)
    ):
        raise ValueError("temporal_invalid_references")


def _similarity(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        keys = a.keys() | b.keys()
        return (
            sum(_similarity(a[k], b[k]) if k in a and k in b else 0 for k in keys)
            / len(keys)
            if keys
            else 1.0
        )
    if _numeric(a) and _numeric(b):
        return max(0.0, 1.0 - abs(a - b) / max(abs(a), abs(b), 1.0))
    if isinstance(a, list) and isinstance(b, list):
        return (
            sum(_similarity(x, y) for x, y in zip(a, b, strict=False))
            / max(len(a), len(b))
            if a or b
            else 1.0
        )
    return float(type(a) is type(b) and a == b)


def _blend(weighted):
    weighted = [(v, w) for v, w in weighted if w > 0]
    if all(isinstance(v, dict) for v, _ in weighted):
        keys = sorted(set().union(*(v.keys() for v, _ in weighted)))
        return {k: _blend([(v[k], w) for v, w in weighted if k in v]) for k in keys}
    if all(_numeric(v) for v, _ in weighted):
        total = sum(w for _, w in weighted)
        return sum(v * (w / total) for v, w in weighted)
    return copy.deepcopy(max(weighted, key=lambda pair: pair[1])[0])


def _slope(times, values):
    center = sum(times) / len(times)
    variance = sum((t - center) ** 2 for t in times)
    if variance < 1e-18:
        return 0.0
    mean = sum(values) / len(values)
    return (
        sum((t - center) * (v - mean) for t, v in zip(times, values, strict=True))
        / variance
    )


class TemporalConsciousnessEngine:
    """Bounded, deterministic temporal analysis with explicit Memory checkpoints.

    Async callers share one event loop. Public dictionaries remain compatible
    inspection surfaces, not an authority boundary for trusted in-process code.
    Prediction scores and legacy 'causal' names describe heuristics, not proof.
    """

    def __init__(
        self,
        *,
        memory_system=None,
        clock=None,
        max_moments=256,
        max_predictions=128,
        max_causal_chains=512,
    ):
        self.logger = logging.getLogger(__name__)
        self.memory_system = memory_system
        self._clock = clock or (lambda: datetime.now(UTC))
        self.max_moments = max_moments
        self.max_predictions = max_predictions
        self.max_causal_chains = max_causal_chains
        self.temporal_moments = {}
        self.temporal_predictions = {}
        self.causal_chains = {}
        self.temporal_window = timedelta(hours=24)
        self.prediction_horizon = timedelta(hours=6)
        self.coherence_threshold = 0.7
        self.causal_threshold = 0.5
        self.temporal_resolution = timedelta(seconds=1)
        self.current_temporal_state = TemporalState.PRESENT_AWARE
        self.temporal_coherence_history = []
        self.prediction_accuracy_history = []
        self.moments_processed = 0
        self.predictions_made = 0
        self.causal_chains_discovered = 0
        self.temporal_coherence = 0.0
        self.avg_prediction_accuracy = 0.0
        self._revision = 0
        self._validate_config()

    def _validate_config(self):
        for value in (self.max_moments, self.max_predictions, self.max_causal_chains):
            if type(value) is not int or not 1 <= value <= 4096:
                raise TemporalValidationError("temporal_invalid_capacity")
        for value in (
            self.temporal_window,
            self.prediction_horizon,
            self.temporal_resolution,
        ):
            if (
                not isinstance(value, timedelta)
                or not 0 < value.total_seconds() <= 366 * 86400
            ):
                raise TemporalValidationError("temporal_invalid_window")
        for value in (self.coherence_threshold, self.causal_threshold):
            _unit_score(value)

    def _now(self):
        return _utc(self._clock())

    def _unchanged(self, revision):
        if self._revision != revision:
            raise TemporalConflictError("temporal_operation_conflict")

    def _retained(self, moments, predictions, chains):
        # Event time determines moment eviction; insertion order breaks ties.
        kept = sorted(moments.values(), key=lambda m: m.timestamp)[-self.max_moments :]
        moments = {m.moment_id: copy.deepcopy(m) for m in kept}
        chains = {
            key: copy.deepcopy(c)
            for key, c in chains.items()
            if set(c.cause_moments + c.effect_moments) <= moments.keys()
        }
        chains = dict(list(chains.items())[-self.max_causal_chains :])
        predictions = copy.deepcopy(
            dict(list(predictions.items())[-self.max_predictions :])
        )
        for moment in moments.values():
            moment.memory_associations = [
                key for key in moment.memory_associations if key in moments
            ]
            moment.causal_influences = [
                key for key in moment.causal_influences if key in chains
            ]
        for prediction in predictions.values():
            prediction.contributing_factors = [
                key for key in prediction.contributing_factors if key in moments
            ]
        return moments, predictions, chains

    @_temporal_operation
    async def process_temporal_moment(self, consciousness_state, timestamp=None):
        state = _state_snapshot(consciousness_state)
        timestamp = _utc(timestamp) if timestamp is not None else self._now()
        self._validate_config()
        self._guardian_preflight_temporal_consciousness_operation(
            operation="process_moment",
            capabilities=("consciousness:write", "memory:write"),
            extra_metadata={
                "state_hash": _hash_value(state),
                "state_field_names": sorted(state),
                "state_field_count": len(state),
                "timestamp_hash": _hash_value(timestamp.isoformat()),
            },
        )
        revision = self._revision
        moment = TemporalMoment(
            "moment_" + uuid.uuid4().hex,
            timestamp,
            state,
            await self._calculate_temporal_coherence(state, timestamp),
        )
        moment.temporal_weight = 1 + moment.temporal_coherence * 0.5
        await self._find_temporal_associations(moment)
        new_chains = await self._update_causal_chains(moment)
        retained = self._retained(
            {**self.temporal_moments, moment.moment_id: moment},
            self.temporal_predictions,
            {**self.causal_chains, **new_chains},
        )
        if moment.moment_id not in retained[0]:
            raise TemporalValidationError("temporal_outside_retention")
        self._unchanged(revision)
        self.temporal_moments, self.temporal_predictions, self.causal_chains = retained
        self.moments_processed += 1
        self.causal_chains_discovered += len(new_chains)
        self.temporal_coherence_history = (
            self.temporal_coherence_history + [moment.temporal_coherence]
        )[-100:]
        self.temporal_coherence = float(np.mean(self.temporal_coherence_history))
        self._revision += 1
        return moment.moment_id

    @_temporal_operation
    async def predict_future_state(self, target_time, consciousness_context):
        context = _state_snapshot(consciousness_context)
        target_time, now = _utc(target_time), self._now()
        self._validate_config()
        delta = target_time - now
        if not timedelta(0) < delta <= self.prediction_horizon:
            raise TemporalValidationError("temporal_invalid_prediction_horizon")
        self._guardian_preflight_temporal_consciousness_operation(
            operation="predict_future",
            capabilities=("consciousness:write", "memory:read", "memory:write"),
            extra_metadata={
                "target_time_hash": _hash_value(target_time.isoformat()),
                "context_hash": _hash_value(context),
                "context_field_names": sorted(context),
                "context_field_count": len(context),
            },
        )
        revision = self._revision
        moments = (await self._get_recent_moments(timedelta(hours=2), as_of=now))[-5:]
        trends = await self._analyze_temporal_trends(moments)
        projected = await self._project_trends_forward(context, trends, delta)
        confidence = await self._calculate_prediction_confidence(trends, delta)
        prediction = TemporalPrediction(
            "pred_" + uuid.uuid4().hex,
            target_time,
            projected,
            confidence,
            await self._calculate_uncertainty_range(trends, delta),
            contributing_factors=[m.moment_id for m in moments],
            quantum_probability=self._apply_quantum_prediction_factors(
                projected, context
            ),
            creation_time=now,
        )
        retained = self._retained(
            self.temporal_moments,
            {**self.temporal_predictions, prediction.prediction_id: prediction},
            self.causal_chains,
        )
        self._unchanged(revision)
        self.temporal_moments, self.temporal_predictions, self.causal_chains = retained
        self.predictions_made += 1
        self._revision += 1
        return copy.deepcopy(prediction)

    @_temporal_operation
    async def temporal_memory_integration(self, query_time, context):
        context, query_time = _state_snapshot(context), _utc(query_time)
        self._validate_config()
        self._guardian_preflight_temporal_consciousness_operation(
            operation="memory_integration",
            capabilities=("consciousness:write", "memory:read", "memory:write"),
            extra_metadata={
                "query_time_hash": _hash_value(query_time.isoformat()),
                "context_hash": _hash_value(context),
                "context_field_names": sorted(context),
                "context_field_count": len(context),
            },
        )
        moments = await self._get_recent_moments(
            self.temporal_window, as_of=min(query_time, self._now())
        )
        weighted = []
        for moment in reversed(moments):
            distance = (query_time - moment.timestamp).total_seconds()
            relevance = max(0.0, 1.0 - distance / self.temporal_window.total_seconds())
            weight = relevance * moment.temporal_weight * moment.temporal_coherence
            if weight > 0:
                weighted.append((moment, weight))
        weighted = weighted[:10]
        integrated = _blend(
            [(context, 1.0), *((m.consciousness_state, w) for m, w in weighted)]
        )
        return {
            "integrated_state": _state_snapshot(integrated),
            "temporal_strength": (
                min(sum(w for _, w in weighted) / len(weighted), 1.0)
                if weighted
                else 0.0
            ),
            "moments_used": len(weighted),
            "integration_time": query_time,
            "contributing_moments": [m.moment_id for m, _ in weighted],
        }

    @_temporal_operation
    async def detect_temporal_patterns(self, pattern_window):
        if not isinstance(pattern_window, timedelta) or pattern_window <= timedelta(0):
            raise TemporalValidationError("temporal_invalid_window")
        self._guardian_preflight_temporal_consciousness_operation(
            operation="detect_patterns",
            capabilities=("memory:read",),
            extra_metadata={"window_seconds": pattern_window.total_seconds()},
        )
        moments = await self._get_recent_moments(pattern_window)
        if len(moments) < 3:
            return []
        coherence = await self._detect_coherence_patterns(moments)
        patterns = [coherence] if coherence["strength"] > 0.05 else []
        patterns += await self._detect_cyclical_patterns(moments)
        patterns += await self._detect_state_transitions(moments)
        patterns += await self._detect_causal_sequences(moments)
        return patterns

    @_temporal_operation
    async def validate_prediction_accuracy(self, prediction_id, actual_state):
        state = _state_snapshot(actual_state)
        self._guardian_preflight_temporal_consciousness_operation(
            operation="validate_prediction",
            capabilities=("consciousness:write", "memory:write"),
            extra_metadata={
                "prediction_hash": _hash_value(prediction_id),
                "actual_state_hash": _hash_value(state),
                "actual_state_field_names": sorted(state),
                "actual_state_field_count": len(state),
            },
        )
        if prediction_id not in self.temporal_predictions:
            raise KeyError("temporal_prediction_missing")
        revision = self._revision
        prediction = copy.deepcopy(self.temporal_predictions[prediction_id])
        accuracy = await self._calculate_state_similarity(
            prediction.predicted_state, state
        )
        self._unchanged(revision)
        prediction.prediction_accuracy = accuracy
        self.temporal_predictions[prediction_id] = prediction
        # A revision of an existing validation replaces its score, not another sample.
        self.prediction_accuracy_history = [
            p.prediction_accuracy
            for p in self.temporal_predictions.values()
            if hasattr(p, "prediction_accuracy")
        ][-50:]
        self.avg_prediction_accuracy = float(np.mean(self.prediction_accuracy_history))
        self._revision += 1
        return accuracy

    async def _get_recent_moments(self, time_window, *, as_of=None):
        now = _utc(as_of) if as_of is not None else self._now()
        return sorted(
            (
                m
                for m in self.temporal_moments.values()
                if now - time_window <= m.timestamp <= now
            ),
            key=lambda m: m.timestamp,
        )

    async def _calculate_temporal_coherence(self, state, timestamp):
        moments = await self._get_recent_moments(timedelta(minutes=30), as_of=timestamp)
        scores = [
            await self._calculate_state_similarity(state, m.consciousness_state)
            * math.exp(-(timestamp - m.timestamp).total_seconds() / 1800)
            for m in moments
        ]
        return float(np.mean(scores)) if scores else 1.0

    async def _find_temporal_associations(self, moment):
        candidates = await self._get_recent_moments(
            self.temporal_window, as_of=moment.timestamp
        )
        scored = [
            (
                await self._calculate_state_similarity(
                    moment.consciousness_state, m.consciousness_state
                ),
                m.moment_id,
            )
            for m in candidates
        ]
        moment.memory_associations = [
            key
            for score, key in sorted(scored, reverse=True)
            if score > self.coherence_threshold
        ][:5]

    async def _update_causal_chains(self, moment):
        # Legacy API names retained. Similarity/proximity is correlation only.
        chains = {}
        for cause in await self._get_recent_moments(
            timedelta(hours=1), as_of=moment.timestamp
        ):
            if cause.timestamp >= moment.timestamp:
                continue
            span = moment.timestamp - cause.timestamp
            strength = await self._calculate_state_similarity(
                cause.consciousness_state, moment.consciousness_state
            )
            strength /= 1 + span.total_seconds() / 3600
            if strength > self.causal_threshold:
                key = f"chain_{cause.moment_id}_{moment.moment_id}"
                chains[key] = TemporalCausalChain(
                    key, [cause.moment_id], [moment.moment_id], strength, span, strength
                )
                moment.causal_influences.append(key)
        return chains

    async def _calculate_state_similarity(self, state_a, state_b):
        return _similarity(_state_snapshot(state_a), _state_snapshot(state_b))

    def _merge_dicts_weighted(self, dict_a, dict_b, weight):
        return _blend(
            [
                (_state_snapshot(dict_a), 1.0),
                (_state_snapshot(dict_b), _finite(weight, 0, 10)),
            ]
        )

    async def _analyze_temporal_trends(self, moments):
        moments = sorted(moments, key=lambda m: m.timestamp)
        result = {
            "trend_strength": 0.0,
            "direction": "none",
            "coherence_trend": 0.0,
            "patterns": [],
            "state_slopes": {},
            "sample_count": len(moments),
        }
        if len(moments) < 2:
            return result
        times = [
            (m.timestamp - moments[0].timestamp).total_seconds() / 3600 for m in moments
        ]
        slope = _slope(times, [m.temporal_coherence for m in moments])
        direction = "stable"
        if slope > 1e-12:
            direction = "increasing"
        elif slope < -1e-12:
            direction = "decreasing"
        result.update(
            trend_strength=min(abs(slope), 1.0),
            coherence_trend=slope,
            direction=direction,
            patterns=["coherence_evolution"],
        )
        keys = set.intersection(*(set(m.consciousness_state) for m in moments))
        for key in sorted(keys):
            values = [m.consciousness_state[key] for m in moments]
            if all(_numeric(v) for v in values):
                result["state_slopes"][key] = _slope(times, values)
        return result

    async def _project_trends_forward(self, current_state, trends, time_delta):
        state = copy.deepcopy(current_state)
        for key, slope in trends["state_slopes"].items():
            if key in state and _numeric(state[key]):
                bound = max(abs(state[key]), 1.0) * 0.5
                change = max(
                    -bound, min(bound, slope * time_delta.total_seconds() / 3600)
                )
                state[key] = max(-1e12, min(1e12, state[key] + change))
        return _state_snapshot(state)

    async def _calculate_prediction_confidence(self, trends, time_delta):
        distance = time_delta / self.prediction_horizon
        support = min(trends["sample_count"] / 5, 1.0)
        return (0.3 + 0.4 * support) * (1 - 0.5 * distance)

    async def _calculate_uncertainty_range(self, trends, time_delta):
        confidence = await self._calculate_prediction_confidence(trends, time_delta)
        return {
            "high": 1 - confidence,
            "medium": confidence * 0.5,
            "low": confidence * 0.5,
        }

    def _apply_quantum_prediction_factors(self, predicted_state, current_state):
        # Compatibility field; a bounded similarity score, not quantum evidence.
        return _similarity(predicted_state, current_state)

    async def _detect_coherence_patterns(self, moments):
        trend = await self._analyze_temporal_trends(moments)
        return {
            "type": "coherence_trend",
            "strength": trend["trend_strength"],
            "direction": trend["direction"],
            "causation_established": False,
        }

    async def _detect_cyclical_patterns(self, moments):
        signatures = [
            json.dumps(m.consciousness_state, sort_keys=True) for m in moments
        ]
        # Exact repeated states: at least three full cycles and two distinct states.
        for period in range(2, min(16, len(signatures) // 3) + 1):
            cycle = signatures[-period:]
            repeats = 1
            while (repeats + 1) * period <= len(signatures):
                start = len(signatures) - (repeats + 1) * period
                if signatures[start : start + period] != cycle:
                    break
                repeats += 1
            tail = signatures[-period * repeats :]
            if repeats >= 3 and len(set(cycle)) > 1:
                used = moments[-len(tail) :]
                return [
                    {
                        "type": "repeating_state_cycle",
                        "period_moments": period,
                        "repetitions": repeats,
                        "moments": [m.moment_id for m in used],
                        "strength": len(tail) / len(moments),
                        "causation_established": False,
                    }
                ]
        return []

    async def _detect_state_transitions(self, moments):
        transitions = []
        for previous, current in zip(moments, moments[1:], strict=False):
            similarity = await self._calculate_state_similarity(
                previous.consciousness_state, current.consciousness_state
            )
            if similarity < 0.5:
                transitions.append(
                    {
                        "type": "state_transition",
                        "from_moment": previous.moment_id,
                        "to_moment": current.moment_id,
                        "transition_strength": 1 - similarity,
                        "timestamp": current.timestamp,
                        "causation_established": False,
                    }
                )
        return transitions

    async def _detect_causal_sequences(self, moments):
        sequences = []
        for i in range(len(moments) - 2):
            sequence = moments[i : i + 3]
            if (
                not sequence[0].timestamp
                < sequence[1].timestamp
                < sequence[2].timestamp
            ):
                continue
            strength = (
                sum(
                    [
                        await self._calculate_state_similarity(
                            a.consciousness_state, b.consciousness_state
                        )
                        for a, b in zip(sequence, sequence[1:], strict=False)
                    ]
                )
                / 2
            )
            if strength > 0.6:
                sequences.append(
                    {
                        "type": "causal_sequence",
                        "moments": [m.moment_id for m in sequence],
                        "strength": strength,
                        "start_time": sequence[0].timestamp,
                        "end_time": sequence[-1].timestamp,
                        "causation_established": False,
                    }
                )
        return sequences

    def _checkpoint(self, handle):
        def encoded(obj):
            value = copy.deepcopy(vars(obj))
            for key, item in value.items():
                if isinstance(item, _DATETIME_TYPE):
                    value[key] = item.isoformat()
                elif isinstance(item, timedelta):
                    value[key] = item.total_seconds()
            return value

        return {
            "schema": 1,
            "checkpoint_id": handle,
            "moments": [encoded(m) for m in self.temporal_moments.values()],
            "predictions": [encoded(p) for p in self.temporal_predictions.values()],
            "chains": [encoded(c) for c in self.causal_chains.values()],
            "coherence_history": list(self.temporal_coherence_history),
            "accuracy_history": list(self.prediction_accuracy_history),
            "counts": [
                self.moments_processed,
                self.predictions_made,
                self.causal_chains_discovered,
            ],
            "state": self.current_temporal_state.value,
            "settings": {
                "temporal_window": self.temporal_window.total_seconds(),
                "prediction_horizon": self.prediction_horizon.total_seconds(),
                "temporal_resolution": self.temporal_resolution.total_seconds(),
                "coherence_threshold": self.coherence_threshold,
                "causal_threshold": self.causal_threshold,
            },
        }

    @_temporal_operation
    async def save_checkpoint(self):
        self._validate_config()
        self._guardian_preflight_temporal_consciousness_operation(
            operation="save_checkpoint",
            capabilities=("consciousness:write", "memory:write"),
        )
        if self.memory_system is None:
            raise TemporalPersistenceError("temporal_memory_unavailable")
        handle = uuid.uuid4().hex
        payload = self._checkpoint(handle)
        self._decode_checkpoint(payload, handle)  # Validate before any durable write.
        try:
            receipt = await self.memory_system.store_memory(
                content=copy.deepcopy(payload),
                memory_type="temporal_checkpoint:" + handle,
                importance=0.5,
                tags=["temporal_checkpoint"],
                context={"component": "temporal_consciousness", "schema": 1},
            )
        except Exception:
            raise TemporalPersistenceError("temporal_checkpoint_store_failed") from None
        if not isinstance(receipt, str) or not receipt.strip():
            raise TemporalPersistenceError("temporal_checkpoint_store_unconfirmed")
        return handle

    @_temporal_operation
    async def restore_checkpoint(self, checkpoint_id):
        self._guardian_preflight_temporal_consciousness_operation(
            operation="restore_checkpoint",
            capabilities=("consciousness:write", "memory:read", "memory:write"),
            extra_metadata={"checkpoint_hash": _hash_value(checkpoint_id)},
        )
        if (
            not isinstance(checkpoint_id, str)
            or re.fullmatch(r"[0-9a-f]{32}", checkpoint_id) is None
        ):
            raise TemporalValidationError("temporal_invalid_checkpoint_id")
        if self.memory_system is None:
            raise TemporalPersistenceError("temporal_memory_unavailable")
        revision = self._revision
        try:
            rows = await self.memory_system.recall_memories(
                query_text="",
                limit=2,
                memory_type="temporal_checkpoint:" + checkpoint_id,
            )
        except Exception:
            raise TemporalPersistenceError("temporal_checkpoint_unavailable") from None
        if not isinstance(rows, list) or len(rows) != 1:
            raise TemporalPersistenceError(
                "temporal_checkpoint_missing_unreadable_or_ambiguous"
            )
        row = rows[0]
        if (
            not isinstance(row.id, str)
            or not row.id.strip()
            or row.memory_type != "temporal_checkpoint:" + checkpoint_id
        ):
            raise TemporalPersistenceError("temporal_checkpoint_invalid_record")
        candidate = self._decode_checkpoint(row.content, checkpoint_id)
        if self._revision != revision:
            raise TemporalConflictError("temporal_restore_conflict")
        for name in _CHECKPOINT_ATTRIBUTES:
            setattr(self, name, getattr(candidate, name))
        self._revision += 1
        return {
            "status": "restored",
            "checkpoint_id": checkpoint_id,
            "memory_id": row.id,
            "moments_restored": len(self.temporal_moments),
            "predictions_restored": len(self.temporal_predictions),
        }

    def _decode_checkpoint(self, payload, handle):
        try:
            if not isinstance(payload, dict) or set(payload) != {
                "schema",
                "checkpoint_id",
                "moments",
                "predictions",
                "chains",
                "coherence_history",
                "accuracy_history",
                "counts",
                "state",
                "settings",
            }:
                raise ValueError
            if (
                type(payload["schema"]) is not int
                or payload["schema"] != 1
                or payload["checkpoint_id"] != handle
            ):
                raise ValueError
            if (
                len(json.dumps(payload, allow_nan=False).encode("utf-8"))
                > 16 * 1024 * 1024
            ):
                raise ValueError
            candidate = TemporalConsciousnessEngine(
                clock=self._clock,
                max_moments=self.max_moments,
                max_predictions=self.max_predictions,
                max_causal_chains=self.max_causal_chains,
            )
            settings = payload["settings"]
            if set(settings) != {
                "temporal_window",
                "prediction_horizon",
                "temporal_resolution",
                "coherence_threshold",
                "causal_threshold",
            }:
                raise ValueError
            for key, value in settings.items():
                setattr(
                    candidate,
                    key,
                    (
                        timedelta(seconds=_finite(value, 0, 366 * 86400))
                        if key
                        in {
                            "temporal_window",
                            "prediction_horizon",
                            "temporal_resolution",
                        }
                        else _unit_score(value)
                    ),
                )
            candidate._validate_config()
            for name, model, id_field, limit in [
                ("moments", TemporalMoment, "moment_id", self.max_moments),
                (
                    "predictions",
                    TemporalPrediction,
                    "prediction_id",
                    self.max_predictions,
                ),
                ("chains", TemporalCausalChain, "chain_id", self.max_causal_chains),
            ]:
                records = payload[name]
                if not isinstance(records, list) or len(records) > limit:
                    raise ValueError
                destination = getattr(
                    candidate,
                    {
                        "moments": "temporal_moments",
                        "predictions": "temporal_predictions",
                        "chains": "causal_chains",
                    }[name],
                )
                for record in records:
                    data = copy.deepcopy(record)
                    accuracy = (
                        data.pop("prediction_accuracy", None)
                        if name == "predictions"
                        else None
                    )
                    if set(data) != {f.name for f in fields(model)}:
                        raise ValueError
                    key = data[id_field]
                    if not isinstance(key, str) or len(key) > 128 or key in destination:
                        raise ValueError
                    prefix = {
                        "moments": "moment",
                        "predictions": "pred",
                        "chains": "chain",
                    }[name]
                    if not key.startswith(prefix + "_"):
                        raise ValueError
                    for field_name in ("timestamp", "target_time", "creation_time"):
                        if field_name in data:
                            instant = _DATETIME_TYPE.fromisoformat(data[field_name])
                            # Persisted instants must not depend on the restore host.
                            if instant.tzinfo is None or instant.utcoffset() is None:
                                raise ValueError
                            data[field_name] = _utc(instant)
                    if name == "moments":
                        data["consciousness_state"] = _state_snapshot(
                            data["consciousness_state"]
                        )
                        _unit_score(data["temporal_coherence"])
                        _finite(data["temporal_weight"], 1, 1.5)
                        if data["prediction_accuracy"] is not None:
                            _unit_score(data["prediction_accuracy"])
                        _refs(data["memory_associations"], 5)
                        _refs(data["causal_influences"], self.max_causal_chains)
                    elif name == "predictions":
                        data["predicted_state"] = _state_snapshot(
                            data["predicted_state"]
                        )
                        _unit_score(data["confidence"])
                        _unit_score(data["quantum_probability"])
                        _refs(data["contributing_factors"], 5)
                        if (
                            not timedelta(0)
                            < data["target_time"] - data["creation_time"]
                            <= candidate.prediction_horizon
                        ):
                            raise ValueError
                        distribution = data["uncertainty_range"]
                        if set(distribution) != {
                            "high",
                            "medium",
                            "low",
                        } or not math.isclose(
                            sum(_unit_score(v) for v in distribution.values()),
                            1.0,
                            abs_tol=1e-9,
                        ):
                            raise ValueError
                    else:
                        for field_name in ("cause_moments", "effect_moments"):
                            _refs(data[field_name], 1)
                            if len(data[field_name]) != 1:
                                raise ValueError
                        _unit_score(data["causal_strength"])
                        _unit_score(data["confidence"])
                        if data["quantum_entanglement"] is not False:
                            raise ValueError
                        data["temporal_span"] = timedelta(
                            seconds=_finite(data["temporal_span"], 0, 366 * 86400)
                        )
                    obj = model(**data)
                    if accuracy is not None:
                        obj.prediction_accuracy = _unit_score(accuracy)
                    destination[key] = obj
            moment_ids, chain_ids = (
                candidate.temporal_moments.keys(),
                candidate.causal_chains.keys(),
            )
            for moment in candidate.temporal_moments.values():
                if (
                    not set(moment.memory_associations) <= moment_ids
                    or not set(moment.causal_influences) <= chain_ids
                ):
                    raise ValueError
                if any(
                    moment.moment_id not in candidate.causal_chains[key].effect_moments
                    for key in moment.causal_influences
                ):
                    raise ValueError
                if any(
                    key == moment.moment_id
                    or candidate.temporal_moments[key].timestamp > moment.timestamp
                    for key in moment.memory_associations
                ):
                    raise ValueError
            for chain in candidate.causal_chains.values():
                cause = candidate.temporal_moments[chain.cause_moments[0]]
                effect = candidate.temporal_moments[chain.effect_moments[0]]
                if (
                    cause.timestamp >= effect.timestamp
                    or chain.temporal_span != effect.timestamp - cause.timestamp
                ):
                    raise ValueError
            for prediction in candidate.temporal_predictions.values():
                if not set(prediction.contributing_factors) <= moment_ids:
                    raise ValueError
                if any(
                    candidate.temporal_moments[key].timestamp > prediction.creation_time
                    for key in prediction.contributing_factors
                ):
                    raise ValueError
            for key, destination, limit in [
                ("coherence_history", "temporal_coherence_history", 100),
                ("accuracy_history", "prediction_accuracy_history", 50),
            ]:
                values = payload[key]
                if not isinstance(values, list) or len(values) > limit:
                    raise ValueError
                setattr(candidate, destination, [_unit_score(v) for v in values])
            counts = payload["counts"]
            sizes = (
                len(candidate.temporal_moments),
                len(candidate.temporal_predictions),
                len(candidate.causal_chains),
            )
            if (
                not isinstance(counts, list)
                or len(counts) != 3
                or any(
                    type(c) is not int or not size <= c <= 2**63 - 1
                    for c, size in zip(counts, sizes, strict=True)
                )
            ):
                raise ValueError
            if (
                len(candidate.temporal_coherence_history) > counts[0]
                or len(candidate.prediction_accuracy_history) > counts[1]
            ):
                raise ValueError
            (
                candidate.moments_processed,
                candidate.predictions_made,
                candidate.causal_chains_discovered,
            ) = counts
            candidate.current_temporal_state = TemporalState(payload["state"])
            candidate.temporal_coherence = (
                float(np.mean(candidate.temporal_coherence_history))
                if candidate.temporal_coherence_history
                else 0.0
            )
            candidate.avg_prediction_accuracy = (
                float(np.mean(candidate.prediction_accuracy_history))
                if candidate.prediction_accuracy_history
                else 0.0
            )
            return candidate
        except Exception:
            raise TemporalValidationError("temporal_checkpoint_invalid") from None

    def get_temporal_system_metrics(self):
        return {
            "moments_processed": self.moments_processed,
            "active_moments": len(self.temporal_moments),
            "predictions_made": self.predictions_made,
            "active_predictions": len(self.temporal_predictions),
            "causal_chains_discovered": self.causal_chains_discovered,
            "active_causal_chains": len(self.causal_chains),
            "current_temporal_state": self.current_temporal_state.value,
            "temporal_coherence": self.temporal_coherence,
            "avg_prediction_accuracy": self.avg_prediction_accuracy,
            "temporal_window_hours": self.temporal_window.total_seconds() / 3600,
            "prediction_horizon_hours": self.prediction_horizon.total_seconds() / 3600,
            "persistence_mode": (
                "explicit_checkpoint"
                if self.memory_system is not None
                else "in_process"
            ),
            "forecast_model": "bounded_linear_heuristic",
            "causation_established": False,
        }

    def _guardian_preflight_temporal_consciousness_operation(
        self,
        *,
        operation: str,
        capabilities: tuple[str, ...],
        extra_metadata: Dict[str, Any] | None = None,
    ):
        # Aetherra imports
        from Aetherra.guardian import IntentDeclaration, evaluate_intent

        requester = (
            os.getenv("AETHERRA_PRINCIPAL", "").strip() or "consciousness:temporal"
        )
        approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
        metadata: Dict[str, Any] = {
            "operation": operation,
            "moment_count": len(self.temporal_moments),
            "prediction_count": len(self.temporal_predictions),
            "causal_chain_count": len(self.causal_chains),
            "current_temporal_state": self.current_temporal_state.value,
            "coherence_history_count": len(self.temporal_coherence_history),
            "accuracy_history_count": len(self.prediction_accuracy_history),
            "moments_processed": int(self.moments_processed),
            "predictions_made": int(self.predictions_made),
            "causal_chains_discovered": int(self.causal_chains_discovered),
            "temporal_coherence": round(float(self.temporal_coherence), 6),
            "avg_prediction_accuracy": round(float(self.avg_prediction_accuracy), 6),
            "temporal_window_seconds": round(
                float(self.temporal_window.total_seconds()), 6
            ),
            "prediction_horizon_seconds": round(
                float(self.prediction_horizon.total_seconds()), 6
            ),
        }
        if extra_metadata:
            metadata.update(extra_metadata)

        decision = evaluate_intent(
            IntentDeclaration(
                requester=requester,
                subsystem="consciousness",
                action=f"consciousness.temporal_{operation}",
                target="temporal_consciousness_engine",
                purpose="Access bounded temporal analysis state",
                capabilities=capabilities,
                evidence=(
                    "TemporalConsciousnessEngine.process_temporal_moment",
                    "TemporalConsciousnessEngine.predict_future_state",
                    "TemporalConsciousnessEngine.temporal_memory_integration",
                    "TemporalConsciousnessEngine.validate_prediction_accuracy",
                    "TemporalConsciousnessEngine.detect_temporal_patterns",
                    "TemporalConsciousnessEngine.save_checkpoint",
                    "TemporalConsciousnessEngine.restore_checkpoint",
                ),
                reversible=True,
                rollback_plan=(
                    "in-memory updates are staged; retain a prior checkpoint before replacing "
                    "history and restore it to undo replacement; delete an unwanted checkpoint "
                    "using Memory.delete_memory with its retrieved receipt; Memory access "
                    "statistics are not rolled back; a cancelled write may persist unacknowledged"
                ),
                metadata=metadata,
            ),
            approval_id=approval_id,
            capability_checker=_temporal_consciousness_capability_checker,
        )
        if not decision.allowed:
            raise PermissionError(f"guardian_denied:{decision.reason}")
        return decision


# Global temporal consciousness engine instance
temporal_consciousness_engine = None


def initialize_temporal_consciousness_engine(**kwargs) -> TemporalConsciousnessEngine:
    """Initialize global temporal consciousness engine"""
    global temporal_consciousness_engine
    if temporal_consciousness_engine is None:
        temporal_consciousness_engine = TemporalConsciousnessEngine(**kwargs)
    elif kwargs:
        raise RuntimeError("temporal_engine_already_initialized")
    return temporal_consciousness_engine


def get_temporal_consciousness_engine() -> Optional[TemporalConsciousnessEngine]:
    """Get global temporal consciousness engine instance"""
    return temporal_consciousness_engine


# Example usage for testing
async def test_temporal_consciousness():
    """Test the temporal consciousness system"""
    engine = initialize_temporal_consciousness_engine()

    print("⏰ TEMPORAL CONSCIOUSNESS SYSTEM TESTING")
    print("=" * 45)

    # Test 1: Process temporal moments
    print("\n📝 Test 1: Processing Temporal Moments")

    consciousness_states = [
        {
            "awareness_level": 0.8,
            "emotional_state": "curious",
            "focus": "quantum_learning",
        },
        {
            "awareness_level": 0.85,
            "emotional_state": "excited",
            "focus": "breakthrough_discovery",
        },
        {
            "awareness_level": 0.9,
            "emotional_state": "transcendent",
            "focus": "consciousness_evolution",
        },
    ]

    moment_ids = []
    for i, state in enumerate(consciousness_states):
        timestamp = datetime.now() - timedelta(seconds=(2 - i) * 10)
        moment_id = await engine.process_temporal_moment(state, timestamp)
        moment_ids.append(moment_id)
        print(f"  ✅ Processed moment {i + 1}: {moment_id}")

    # Test 2: Temporal prediction
    print("\n🔮 Test 2: Future State Prediction")
    future_time = datetime.now() + timedelta(minutes=30)
    current_context = {"awareness_level": 0.92, "emotional_state": "anticipatory"}

    prediction = await engine.predict_future_state(future_time, current_context)
    print(f"  ✅ Created prediction: {prediction.prediction_id}")
    print(f"  📊 Confidence: {prediction.confidence:.3f}")
    print(f"  🎲 Quantum probability: {prediction.quantum_probability:.3f}")

    # Test 3: Temporal memory integration
    print("\n🧠 Test 3: Temporal Memory Integration")
    integration_time = datetime.now()
    integration_context = {"query": "recent_learning_patterns"}

    integration_result = await engine.temporal_memory_integration(
        integration_time, integration_context
    )
    print(f"  ✅ Integration strength: {integration_result['temporal_strength']:.3f}")
    print(f"  📚 Moments used: {integration_result['moments_used']}")

    # Test 4: Pattern detection
    print("\n🔍 Test 4: Temporal Pattern Detection")
    patterns = await engine.detect_temporal_patterns(timedelta(minutes=5))
    print(f"  ✅ Detected {len(patterns)} temporal patterns")

    for pattern in patterns:
        print(
            f"    - {pattern.get('type', 'unknown')}: strength {pattern.get('strength', 0):.3f}"
        )

    # System metrics
    print("\n📊 Temporal System Metrics:")
    metrics = engine.get_temporal_system_metrics()
    for key, value in metrics.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    print("⏰ AETHERRA TEMPORAL CONSCIOUSNESS SYSTEM - PHASE 7.3")
    print("=" * 60)
    asyncio.run(test_temporal_consciousness())
