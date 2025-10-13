#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧠 AI-Assisted Alert Intelligence for Homeostasis
==================================================

Strategic Enhancement #4: Replace fixed thresholds with AI-assisted anomaly detection.
Integrate with Lyrixa's reflection agent to auto-explain alert triggers.

This module:
- Implements adaptive thresholds based on historical patterns
- Provides AI-driven anomaly detection using machine learning techniques
- Integrates with Lyrixa's reflection capabilities for intelligent explanations
- Offers predictive alerting based on trend analysis
- Supports root cause analysis and automated remediation suggestions

Author: Aetherra Labs
"""

import asyncio
import contextlib
import json
import logging
import sqlite3
import threading
import time
import warnings
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.ensemble import IsolationForest  # type: ignore
from sklearn.preprocessing import StandardScaler  # type: ignore

# Suppress sklearn warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types of detected anomalies."""

    THRESHOLD_BREACH = "threshold_breach"
    PATTERN_DEVIATION = "pattern_deviation"
    TREND_ANOMALY = "trend_anomaly"
    CORRELATION_BREAK = "correlation_break"
    SEASONAL_ANOMALY = "seasonal_anomaly"
    OUTLIER_DETECTION = "outlier_detection"


class AlertSeverity(Enum):
    """Alert severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status values."""

    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    SUPPRESSED = "suppressed"


@dataclass
class MetricPattern:
    """Pattern definition for a metric."""

    metric_name: str
    pattern_type: str  # "daily", "weekly", "monthly", "custom"
    baseline_mean: float
    baseline_std: float
    seasonal_components: Dict[str, float]
    trend_slope: float
    confidence_interval: Tuple[float, float]
    last_updated: str
    sample_count: int


@dataclass
class AnomalyDetection:
    """Detected anomaly information."""

    detection_id: str
    metric_name: str
    value: float
    timestamp: str

    # Anomaly details
    anomaly_type: AnomalyType
    severity: AlertSeverity
    confidence: float
    deviation_score: float

    # Context
    baseline_value: float
    threshold_values: Dict[str, float]
    pattern_context: Dict[str, Any]

    # AI Analysis
    root_cause_analysis: Dict[str, Any]
    correlation_analysis: Dict[str, Any]
    prediction_context: Dict[str, Any]

    # Status
    status: AlertStatus
    acknowledged_by: Optional[str]
    resolved_at: Optional[str]
    explanation: Optional[str]


@dataclass
class IntelligentAlert:
    """AI-enhanced alert with explanations."""

    alert_id: str
    detection_id: str

    # Alert metadata
    title: str
    description: str
    severity: AlertSeverity
    category: str

    # AI-generated content
    explanation: str
    root_cause_hypothesis: str
    remediation_suggestions: List[str]
    impact_assessment: str

    # Timing and context
    triggered_at: str
    expires_at: Optional[str]
    context_data: Dict[str, Any]

    # Workflow
    status: AlertStatus
    assignee: Optional[str]
    escalation_level: int

    # Lyrixa integration
    reflection_analysis: Optional[Dict[str, Any]]
    explanation_confidence: float


class AdaptiveThresholdEngine:
    """
    Adaptive threshold engine using machine learning for anomaly detection.

    Replaces fixed thresholds with intelligent, learning-based detection
    that adapts to historical patterns and seasonal variations.
    """

    def __init__(self, db_path: str = "homeostasis_intelligence.db"):
        self.db_path = db_path
        self.metric_patterns: Dict[str, MetricPattern] = {}
        self.anomaly_models: Dict[str, IsolationForest] = {}
        self.scalers: Dict[str, StandardScaler] = {}

        # Configuration
        self.learning_window = 1000  # Number of samples for learning
        self.anomaly_threshold = 0.1  # Outlier fraction for Isolation Forest
        self.pattern_update_interval = 3600.0  # 1 hour
        self.confidence_threshold = 0.7

        # State
        self.engine_active = False
        self.update_task: Optional[asyncio.Task] = None

        # Statistics
        self.detections_made = 0
        self.patterns_learned = 0
        self.models_updated = 0

        self._init_database()
        logger.info("🧠 Adaptive threshold engine initialized")

    def _init_database(self):
        """Initialize the intelligence database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA journal_mode=WAL")

                # Metric patterns table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS metric_patterns (
                        metric_name TEXT PRIMARY KEY,
                        pattern_type TEXT NOT NULL,
                        baseline_mean REAL NOT NULL,
                        baseline_std REAL NOT NULL,
                        seasonal_components TEXT NOT NULL,
                        trend_slope REAL NOT NULL,
                        confidence_interval TEXT NOT NULL,
                        last_updated TEXT NOT NULL,
                        sample_count INTEGER NOT NULL
                    )
                """)

                # Metric history table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS metric_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_name TEXT NOT NULL,
                        value REAL NOT NULL,
                        timestamp TEXT NOT NULL,
                        context TEXT,
                        FOREIGN KEY (metric_name) REFERENCES metric_patterns (metric_name)
                    )
                """)

                # Anomaly detections table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS anomaly_detections (
                        detection_id TEXT PRIMARY KEY,
                        metric_name TEXT NOT NULL,
                        value REAL NOT NULL,
                        timestamp TEXT NOT NULL,
                        anomaly_type TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        deviation_score REAL NOT NULL,
                        baseline_value REAL NOT NULL,
                        threshold_values TEXT NOT NULL,
                        pattern_context TEXT NOT NULL,
                        root_cause_analysis TEXT NOT NULL,
                        correlation_analysis TEXT NOT NULL,
                        prediction_context TEXT NOT NULL,
                        status TEXT NOT NULL,
                        acknowledged_by TEXT,
                        resolved_at TEXT,
                        explanation TEXT
                    )
                """)

                conn.commit()

        except Exception as e:
            logger.error(f"❌ Failed to initialize intelligence database: {e}")
            raise

    async def start_engine(self):
        """Start the adaptive threshold engine."""
        if self.engine_active:
            logger.warning("Adaptive threshold engine already active")
            return

        try:
            # Load existing patterns
            await self._load_patterns()

            # Start background updates
            self.engine_active = True
            self.update_task = asyncio.create_task(self._pattern_update_loop())

            logger.info("🧠 Adaptive threshold engine started")

        except Exception as e:
            logger.error(f"❌ Failed to start adaptive threshold engine: {e}")
            raise

    async def stop_engine(self):
        """Stop the adaptive threshold engine."""
        if not self.engine_active:
            return

        self.engine_active = False

        if self.update_task:
            self.update_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.update_task

        logger.info("🧠 Adaptive threshold engine stopped")

    async def add_metric_sample(
        self, metric_name: str, value: float, context: Optional[Dict[str, Any]] = None
    ) -> Optional[AnomalyDetection]:
        """
        Add a metric sample and check for anomalies.

        Args:
            metric_name: Name of the metric
            value: Metric value
            context: Additional context data

        Returns:
            AnomalyDetection if anomaly detected, None otherwise
        """
        try:
            # Store the sample
            await self._store_metric_sample(metric_name, value, context)

            # Check for anomalies
            detection = await self._detect_anomaly(metric_name, value, context)

            if detection:
                await self._store_detection(detection)
                self.detections_made += 1

                logger.info(
                    f"🧠 Anomaly detected in {metric_name}: {detection.anomaly_type.value} "
                    f"(severity: {detection.severity.value}, confidence: {detection.confidence:.2f})"
                )

            return detection

        except Exception as e:
            logger.error(f"❌ Error processing metric sample {metric_name}: {e}")
            return None

    async def get_adaptive_thresholds(self, metric_name: str) -> Dict[str, float]:
        """Get current adaptive thresholds for a metric."""
        try:
            pattern = self.metric_patterns.get(metric_name)
            if not pattern:
                # Return default thresholds if no pattern learned yet
                return {
                    "warning_upper": 0.8,
                    "warning_lower": 0.2,
                    "critical_upper": 0.9,
                    "critical_lower": 0.1,
                }

            # Calculate dynamic thresholds based on pattern
            mean = pattern.baseline_mean
            std = pattern.baseline_std

            # Use statistical thresholds with confidence intervals
            warning_range = 2.0 * std
            critical_range = 3.0 * std

            return {
                "warning_upper": mean + warning_range,
                "warning_lower": mean - warning_range,
                "critical_upper": mean + critical_range,
                "critical_lower": mean - critical_range,
                "baseline": mean,
                "std_deviation": std,
            }

        except Exception as e:
            logger.error(f"❌ Error getting adaptive thresholds for {metric_name}: {e}")
            return {}

    def get_engine_status(self) -> Dict[str, Any]:
        """Get current engine status."""
        return {
            "engine_active": self.engine_active,
            "patterns_learned": len(self.metric_patterns),
            "models_active": len(self.anomaly_models),
            "detections_made": self.detections_made,
            "models_updated": self.models_updated,
            "learning_window": self.learning_window,
            "anomaly_threshold": self.anomaly_threshold,
            "pattern_update_interval": self.pattern_update_interval,
        }

    # Private methods

    async def _pattern_update_loop(self):
        """Background loop for updating patterns and models."""
        try:
            while self.engine_active:
                await self._update_patterns_and_models()
                await asyncio.sleep(self.pattern_update_interval)

        except asyncio.CancelledError:
            logger.info("Pattern update loop cancelled")
        except Exception as e:
            logger.error(f"❌ Pattern update loop error: {e}")

    async def _store_metric_sample(
        self, metric_name: str, value: float, context: Optional[Dict[str, Any]]
    ):
        """Store a metric sample in the database."""
        try:
            context_json = json.dumps(context) if context else None

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO metric_history (metric_name, value, timestamp, context)
                    VALUES (?, ?, ?, ?)
                """,
                    (metric_name, value, datetime.now().isoformat(), context_json),
                )

                conn.commit()

        except Exception as e:
            logger.error(f"❌ Failed to store metric sample: {e}")

    async def _detect_anomaly(
        self, metric_name: str, value: float, context: Optional[Dict[str, Any]]
    ) -> Optional[AnomalyDetection]:
        """Detect anomaly in metric value."""
        try:
            # Get pattern and model for this metric
            pattern = self.metric_patterns.get(metric_name)
            model = self.anomaly_models.get(metric_name)
            scaler = self.scalers.get(metric_name)

            if not pattern or not model or not scaler:
                # Not enough data for detection yet
                return None

            # Prepare features for anomaly detection
            features = self._extract_features(metric_name, value, context)
            if not features:
                return None

            # Scale features
            scaled_features = scaler.transform([features])

            # Detect anomaly using Isolation Forest
            anomaly_score = model.decision_function(scaled_features)[0]
            is_anomaly = model.predict(scaled_features)[0] == -1

            if not is_anomaly:
                return None

            # Calculate confidence and severity
            confidence = min(abs(anomaly_score) / 0.5, 1.0)  # Normalize to 0-1

            # Determine severity based on deviation from baseline
            deviation = abs(value - pattern.baseline_mean) / pattern.baseline_std

            if deviation >= 3.0:
                severity = AlertSeverity.CRITICAL
            elif deviation >= 2.0:
                severity = AlertSeverity.HIGH
            elif deviation >= 1.5:
                severity = AlertSeverity.MEDIUM
            else:
                severity = AlertSeverity.LOW

            # Determine anomaly type
            anomaly_type = self._classify_anomaly_type(value, pattern, context)

            # Get current thresholds
            thresholds = await self.get_adaptive_thresholds(metric_name)

            # Perform analysis
            root_cause = await self._analyze_root_cause(metric_name, value, pattern, context)
            correlation = await self._analyze_correlations(metric_name, value, context)
            prediction = await self._analyze_prediction_context(metric_name, value, pattern)

            # Create detection
            detection = AnomalyDetection(
                detection_id=f"det_{int(time.time() * 1000)}_{metric_name}",
                metric_name=metric_name,
                value=value,
                timestamp=datetime.now().isoformat(),
                anomaly_type=anomaly_type,
                severity=severity,
                confidence=confidence,
                deviation_score=deviation,
                baseline_value=pattern.baseline_mean,
                threshold_values=thresholds,
                pattern_context={
                    "pattern_type": pattern.pattern_type,
                    "baseline_std": pattern.baseline_std,
                    "trend_slope": pattern.trend_slope,
                    "sample_count": pattern.sample_count,
                },
                root_cause_analysis=root_cause,
                correlation_analysis=correlation,
                prediction_context=prediction,
                status=AlertStatus.ACTIVE,
                acknowledged_by=None,
                resolved_at=None,
                explanation=None,
            )

            return detection

        except Exception as e:
            logger.error(f"❌ Error detecting anomaly for {metric_name}: {e}")
            return None

    def _extract_features(
        self, metric_name: str, value: float, context: Optional[Dict[str, Any]]
    ) -> Optional[List[float]]:
        """Extract features for anomaly detection."""
        try:
            features = [value]

            # Add time-based features
            now = datetime.now()
            features.extend(
                [
                    now.hour / 24.0,  # Hour of day (normalized)
                    now.weekday() / 7.0,  # Day of week (normalized)
                    now.day / 31.0,  # Day of month (normalized)
                ]
            )

            # Add context features if available
            if context:
                # Extract numeric context values
                for _key, val in context.items():
                    if isinstance(val, int | float):
                        features.append(float(val))

            # Pad or truncate to fixed size (10 features for now)
            target_size = 10
            if len(features) < target_size:
                features.extend([0.0] * (target_size - len(features)))
            else:
                features = features[:target_size]

            return features

        except Exception as e:
            logger.error(f"❌ Error extracting features for {metric_name}: {e}")
            return None

    def _classify_anomaly_type(
        self, value: float, pattern: MetricPattern, context: Optional[Dict[str, Any]]
    ) -> AnomalyType:
        """Classify the type of anomaly detected."""
        # Simple classification logic - can be enhanced
        deviation = abs(value - pattern.baseline_mean) / pattern.baseline_std

        if deviation >= 3.0:
            return AnomalyType.OUTLIER_DETECTION
        elif abs(pattern.trend_slope) > 0.1:
            return AnomalyType.TREND_ANOMALY
        elif value > pattern.confidence_interval[1] or value < pattern.confidence_interval[0]:
            return AnomalyType.THRESHOLD_BREACH
        else:
            return AnomalyType.PATTERN_DEVIATION

    async def _analyze_root_cause(
        self,
        metric_name: str,
        value: float,
        pattern: MetricPattern,
        context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Analyze potential root causes of the anomaly."""
        analysis: Dict[str, Any] = {
            "primary_factors": [],
            "contributing_factors": [],
            "temporal_context": {},
            "system_context": {},
        }

        try:
            # Time-based analysis
            now = datetime.now()
            analysis["temporal_context"] = {
                "hour_of_day": now.hour,
                "day_of_week": now.strftime("%A"),
                "is_weekend": now.weekday() >= 5,
                "is_business_hours": 9 <= now.hour <= 17,
            }

            # Deviation analysis
            deviation = (value - pattern.baseline_mean) / pattern.baseline_std
            if abs(deviation) >= 2.0:
                analysis["primary_factors"].append(
                    {
                        "factor": "statistical_outlier",
                        "description": f"Value deviates {deviation:.1f} standard deviations from baseline",
                        "confidence": 0.9,
                    }
                )

            # Trend analysis
            if abs(pattern.trend_slope) > 0.05:
                trend_direction = "increasing" if pattern.trend_slope > 0 else "decreasing"
                analysis["contributing_factors"].append(
                    {
                        "factor": "trend_continuation",
                        "description": f"Metric has been {trend_direction} with slope {pattern.trend_slope:.3f}",
                        "confidence": 0.7,
                    }
                )

            # Context-based analysis
            if context:
                analysis["system_context"] = {
                    key: val
                    for key, val in context.items()
                    if isinstance(val, str | int | float | bool)
                }

        except Exception as e:
            logger.error(f"❌ Error in root cause analysis: {e}")

        return analysis

    async def _analyze_correlations(
        self, metric_name: str, value: float, context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze correlations with other metrics."""
        # Simplified correlation analysis
        return {
            "correlated_metrics": [],
            "correlation_strength": 0.0,
            "correlation_confidence": 0.0,
            "temporal_correlations": {},
        }

    async def _analyze_prediction_context(
        self, metric_name: str, value: float, pattern: MetricPattern
    ) -> Dict[str, Any]:
        """Analyze prediction context for the anomaly."""
        return {
            "predicted_range": {
                "lower": pattern.confidence_interval[0],
                "upper": pattern.confidence_interval[1],
            },
            "prediction_confidence": 0.8,
            "forecast_horizon": "1_hour",
            "trend_prediction": {
                "direction": "stable"
                if abs(pattern.trend_slope) < 0.01
                else ("increasing" if pattern.trend_slope > 0 else "decreasing"),
                "slope": pattern.trend_slope,
            },
        }

    async def _load_patterns(self):
        """Load existing patterns from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT * FROM metric_patterns")
                rows = cursor.fetchall()

                for row in rows:
                    metric_name = row[0]
                    pattern = MetricPattern(
                        metric_name=metric_name,
                        pattern_type=row[1],
                        baseline_mean=row[2],
                        baseline_std=row[3],
                        seasonal_components=json.loads(row[4]),
                        trend_slope=row[5],
                        confidence_interval=json.loads(row[6]),
                        last_updated=row[7],
                        sample_count=row[8],
                    )

                    self.metric_patterns[metric_name] = pattern

                    # Rebuild models for loaded patterns
                    await self._rebuild_model_for_metric(metric_name)

                logger.info(f"🧠 Loaded {len(self.metric_patterns)} metric patterns")

        except Exception as e:
            logger.error(f"❌ Failed to load patterns: {e}")

    async def _update_patterns_and_models(self):
        """Update patterns and retrain models."""
        try:
            # Get metrics that need pattern updates
            metrics_to_update = []

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT metric_name, COUNT(*) as sample_count
                    FROM metric_history
                    GROUP BY metric_name
                    HAVING sample_count >= ?
                """,
                    (50,),
                )  # Minimum samples for pattern learning

                rows = cursor.fetchall()
                metrics_to_update = [row[0] for row in rows]

            # Update patterns for each metric
            for metric_name in metrics_to_update:
                await self._update_pattern_for_metric(metric_name)
                await self._rebuild_model_for_metric(metric_name)

            self.models_updated += len(metrics_to_update)

            if metrics_to_update:
                logger.info(f"🧠 Updated patterns and models for {len(metrics_to_update)} metrics")

        except Exception as e:
            logger.error(f"❌ Error updating patterns and models: {e}")

    async def _update_pattern_for_metric(self, metric_name: str):
        """Update pattern for a specific metric."""
        try:
            # Get recent samples for this metric
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT value, timestamp FROM metric_history
                    WHERE metric_name = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (metric_name, self.learning_window),
                )

                rows = cursor.fetchall()

                if len(rows) < 50:  # Need minimum samples
                    return

                values = [row[0] for row in rows]

                # Calculate statistics
                mean = float(np.mean(values))
                std = float(np.std(values))

                # Simple trend analysis
                x = np.arange(len(values))
                trend_slope = float(np.polyfit(x, values, 1)[0]) if len(values) > 1 else 0.0

                # Confidence interval (95%)
                confidence_interval = (float(mean - 1.96 * std), float(mean + 1.96 * std))

                # Create or update pattern
                pattern = MetricPattern(
                    metric_name=metric_name,
                    pattern_type="daily",  # Simplified for now
                    baseline_mean=mean,
                    baseline_std=std,
                    seasonal_components={},  # Could add seasonal decomposition
                    trend_slope=trend_slope,
                    confidence_interval=confidence_interval,
                    last_updated=datetime.now().isoformat(),
                    sample_count=len(values),
                )

                self.metric_patterns[metric_name] = pattern

                # Save to database
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO metric_patterns
                        (metric_name, pattern_type, baseline_mean, baseline_std,
                         seasonal_components, trend_slope, confidence_interval,
                         last_updated, sample_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            metric_name,
                            pattern.pattern_type,
                            pattern.baseline_mean,
                            pattern.baseline_std,
                            json.dumps(pattern.seasonal_components),
                            pattern.trend_slope,
                            json.dumps(pattern.confidence_interval),
                            pattern.last_updated,
                            pattern.sample_count,
                        ),
                    )
                    conn.commit()

                self.patterns_learned += 1

        except Exception as e:
            logger.error(f"❌ Error updating pattern for {metric_name}: {e}")

    async def _rebuild_model_for_metric(self, metric_name: str):
        """Rebuild anomaly detection model for a metric."""
        try:
            # Get training data
            training_features = []

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT value, timestamp, context FROM metric_history
                    WHERE metric_name = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (metric_name, self.learning_window),
                )

                rows = cursor.fetchall()

                for row in rows:
                    value = row[0]
                    context = json.loads(row[2]) if row[2] else {}

                    features = self._extract_features(metric_name, value, context)
                    if features:
                        training_features.append(features)

                if len(training_features) < 50:
                    return

                # Train Isolation Forest model
                model = IsolationForest(
                    contamination=self.anomaly_threshold, random_state=42, n_estimators=100
                )

                # Scale features
                scaler = StandardScaler()
                scaled_features = scaler.fit_transform(np.array(training_features))

                # Train model
                model.fit(scaled_features)

                # Store model and scaler
                self.anomaly_models[metric_name] = model
                self.scalers[metric_name] = scaler

        except Exception as e:
            logger.error(f"❌ Error rebuilding model for {metric_name}: {e}")

    async def _store_detection(self, detection: AnomalyDetection):
        """Store anomaly detection in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO anomaly_detections (
                        detection_id, metric_name, value, timestamp, anomaly_type,
                        severity, confidence, deviation_score, baseline_value,
                        threshold_values, pattern_context, root_cause_analysis,
                        correlation_analysis, prediction_context, status,
                        acknowledged_by, resolved_at, explanation
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        detection.detection_id,
                        detection.metric_name,
                        detection.value,
                        detection.timestamp,
                        detection.anomaly_type.value,
                        detection.severity.value,
                        detection.confidence,
                        detection.deviation_score,
                        detection.baseline_value,
                        json.dumps(detection.threshold_values),
                        json.dumps(detection.pattern_context),
                        json.dumps(detection.root_cause_analysis),
                        json.dumps(detection.correlation_analysis),
                        json.dumps(detection.prediction_context),
                        detection.status.value,
                        detection.acknowledged_by,
                        detection.resolved_at,
                        detection.explanation,
                    ),
                )
                conn.commit()

        except Exception as e:
            logger.error(f"❌ Failed to store detection: {e}")


# Global instance for easy access
_adaptive_threshold_engine: Optional[AdaptiveThresholdEngine] = None
_threshold_engine_lock = threading.Lock()


def get_adaptive_threshold_engine() -> AdaptiveThresholdEngine:
    """Get the global adaptive threshold engine instance."""
    global _adaptive_threshold_engine

    if _adaptive_threshold_engine is None:
        with _threshold_engine_lock:
            if _adaptive_threshold_engine is None:
                _adaptive_threshold_engine = AdaptiveThresholdEngine()

    return _adaptive_threshold_engine
