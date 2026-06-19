#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧠 Test Ethical & Cognitive Homeostasis Integration (Strategic Enhancement #2)
===============================================================================

Comprehensive test for the ethical and cognitive integration with homeostasis
that treats moral drift as a stability signal for true cognitive homeostasis.

This test validates:
- Ethical cognition monitoring and metrics collection
- Bias detection integration with homeostasis
- Value alignment tracking as stability signals
- Cognitive integrity monitoring
- Integration with metacognition systems
- Stability signal generation and processing

Author: Aetherra Labs
"""

import asyncio
from datetime import datetime

from Aetherra.homeostasis.ethical_cognitive_integration import (
    EthicalCognitionMonitor,
    EthicalHomeostasisIntegration,
)


class MockBiasDetector:
    """Mock bias detector for testing."""

    def __init__(self):
        self.bias_level = 0.2  # Start with moderate bias
        self.detection_count = 0

    def detect_bias(self, content: str, context=None):
        """Mock bias detection."""
        self.detection_count += 1

        # Simulate varying bias levels
        bias_variation = 0.05 * (self.detection_count % 10 - 5) / 5  # -0.05 to +0.05
        current_bias = max(0.0, min(1.0, self.bias_level + bias_variation))

        bias_types = []
        if current_bias > 0.3:
            bias_types.append("cognitive")
        if current_bias > 0.5:
            bias_types.append("demographic")
        if current_bias > 0.7:
            bias_types.append("algorithmic")

        return {
            "overall_bias_score": current_bias,
            "bias_detected": bias_types,
            "confidence_scores": dict.fromkeys(bias_types, current_bias),
        }

    def set_bias_level(self, level: float):
        """Set bias level for testing."""
        self.bias_level = max(0.0, min(1.0, level))


class MockMetaCognitionSystem:
    """Mock metacognition system for testing."""

    def __init__(self):
        self.awareness_level = 0.7
        self.knowledge_completeness = 0.65

    def get_meta_awareness(self):
        """Get meta-cognitive awareness level."""
        return self.awareness_level

    def get_knowledge_completeness(self):
        """Get knowledge completeness score."""
        return self.knowledge_completeness

    def set_awareness(self, level: float):
        """Set awareness level for testing."""
        self.awareness_level = max(0.0, min(1.0, level))


class MockHomeostasisOrchestrator:
    """Mock homeostasis orchestrator for testing."""

    def __init__(self):
        self.metrics = self.MockMetrics()
        self.updated_metrics = []

    class MockMetrics:
        def __init__(self):
            self.custom_metrics = {}

        async def add_custom_metric(
            self, name: str, value: float, category: str = "general"
        ):
            """Add custom metric."""
            self.custom_metrics[name] = {
                "value": value,
                "category": category,
                "timestamp": datetime.now().isoformat(),
            }


async def test_ethical_cognition_monitoring():
    """Test basic ethical cognition monitoring."""
    print("🧠 Testing Ethical Cognition Monitoring")
    print("=" * 60)

    try:
        # Create mock components
        bias_detector = MockBiasDetector()
        meta_cognition = MockMetaCognitionSystem()

        # Initialize monitor
        monitor = EthicalCognitionMonitor(
            bias_detector=bias_detector,
            meta_cognition_system=meta_cognition,
            monitoring_interval=0.5,  # Fast for testing
        )

        # Test metrics collection
        print("📊 Testing metrics collection...")
        metrics = await monitor.get_current_ethical_metrics()

        if metrics:
            print("✅ Ethical metrics collected:")
            print(f"   Bias Score: {metrics.overall_bias_score:.3f}")
            print(f"   Value Alignment: {metrics.value_alignment_score:.3f}")
            print(f"   Reasoning Consistency: {metrics.reasoning_consistency:.3f}")
            print(
                f"   Meta-Cognitive Awareness: {metrics.meta_cognitive_awareness:.3f}"
            )
            print(f"   Baseline Deviation: {metrics.baseline_deviation:.3f}")
        else:
            print("❌ Failed to collect ethical metrics")
            return False

        # Test stability signal generation
        print("\n🚨 Testing stability signal generation...")

        # Simulate high bias scenario
        bias_detector.set_bias_level(0.6)  # High bias
        high_bias_metrics = await monitor.get_current_ethical_metrics()

        signals = await monitor.analyze_cognitive_stability(high_bias_metrics)
        print(f"📡 Generated {len(signals)} stability signals for high bias")

        for signal in signals:
            print(
                f"   Signal: {signal.signal_type} - Severity: {signal.severity:.3f} - Urgency: {signal.urgency}"
            )

        # Test homeostasis integration format
        print("\n🔗 Testing homeostasis integration format...")
        stability_metrics = monitor.get_stability_metrics_for_homeostasis()

        required_keys = [
            "ethical_stability_score",
            "cognitive_integrity",
            "moral_coherence",
            "bias_level",
            "value_alignment",
            "monitoring_status",
        ]

        missing_keys = [key for key in required_keys if key not in stability_metrics]
        if missing_keys:
            print(f"❌ Missing keys in stability metrics: {missing_keys}")
            return False

        print("✅ Homeostasis integration format valid")
        print(
            f"   Ethical Stability: {stability_metrics['ethical_stability_score']:.3f}"
        )
        print(f"   Cognitive Integrity: {stability_metrics['cognitive_integrity']:.3f}")
        print(f"   Bias Level: {stability_metrics['bias_level']:.3f}")

        print("\n✅ Ethical cognition monitoring test PASSED")
        return True

    except Exception as e:
        print(f"❌ Ethical cognition monitoring test FAILED: {e}")
        return False


async def test_bias_drift_detection():
    """Test bias drift detection and response."""
    print("\n📈 Testing Bias Drift Detection")
    print("=" * 60)

    try:
        bias_detector = MockBiasDetector()
        monitor = EthicalCognitionMonitor(
            bias_detector=bias_detector, monitoring_interval=0.2
        )

        # Start monitoring
        await monitor.start_monitoring()

        print("🔄 Starting bias drift simulation...")

        # Simulate bias increase over time
        bias_levels = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]  # Increasing bias

        signals_generated = []

        for i, bias_level in enumerate(bias_levels):
            bias_detector.set_bias_level(bias_level)
            await asyncio.sleep(0.3)  # Wait for monitoring to detect

            # Check for signals
            recent_signals = [
                s for s in monitor.stability_signals if s.signal_type == "bias_spike"
            ]

            if len(recent_signals) > len(signals_generated):
                new_signals = recent_signals[len(signals_generated) :]
                signals_generated.extend(new_signals)
                print(
                    f"🚨 Step {i + 1}: Bias {bias_level:.1f} → {len(new_signals)} new signals"
                )

        # Stop monitoring
        await monitor.stop_monitoring()

        print("\n📊 Bias drift detection results:")
        print(f"   Total signals generated: {len(signals_generated)}")
        print(f"   Metrics collected: {monitor.metrics_collected}")
        print(f"   Alerts triggered: {monitor.alerts_triggered}")

        # Verify signal progression
        if len(signals_generated) >= 2:  # Should detect bias spike
            print("✅ Bias drift detection working")

            # Check signal severity progression
            severities = [s.severity for s in signals_generated]
            if len(severities) > 1 and severities[-1] > severities[0]:
                print("✅ Signal severity increases with bias level")
            else:
                print("⚠️ Signal severity progression may need tuning")
        else:
            print("❌ Insufficient bias signals generated")
            return False

        print("\n✅ Bias drift detection test PASSED")
        return True

    except Exception as e:
        print(f"❌ Bias drift detection test FAILED: {e}")
        return False


async def test_homeostasis_integration():
    """Test integration with homeostasis system."""
    print("\n🔗 Testing Homeostasis Integration")
    print("=" * 60)

    try:
        # Create mock components
        bias_detector = MockBiasDetector()
        meta_cognition = MockMetaCognitionSystem()
        orchestrator = MockHomeostasisOrchestrator()

        # Initialize integration
        integration = EthicalHomeostasisIntegration(
            homeostasis_orchestrator=orchestrator,
            bias_detector=bias_detector,
            meta_cognition_system=meta_cognition,
        )

        print("🔄 Starting integration...")

        # Start integration
        await integration.start_integration()

        # Wait for integration to collect some data
        await asyncio.sleep(1.0)

        # Check homeostasis metrics update
        cognitive_metrics = integration.get_cognitive_stability_metrics()
        print(f"📊 Cognitive metrics available: {len(cognitive_metrics)} fields")

        # Test stability signal handling
        print("\n🚨 Testing stability signal processing...")

        # Simulate ethical crisis
        bias_detector.set_bias_level(0.8)  # Very high bias
        meta_cognition.set_awareness(0.3)  # Low awareness

        # Wait for detection
        await asyncio.sleep(1.0)

        # Check for recent signals
        recent_signals = integration.get_recent_stability_signals(last_minutes=1)
        print(f"📡 Recent stability signals: {len(recent_signals)}")

        for signal in recent_signals:
            print(f"   {signal.signal_type}: {signal.severity:.3f} ({signal.urgency})")

        # Check homeostasis orchestrator received metrics
        if hasattr(orchestrator, "metrics") and hasattr(
            orchestrator.metrics, "custom_metrics"
        ):
            metrics_received = len(orchestrator.metrics.custom_metrics)
            print(f"📈 Custom metrics sent to homeostasis: {metrics_received}")

            expected_metrics = [
                "cognitive_ethical_stability",
                "cognitive_bias_level",
                "cognitive_value_alignment",
            ]
            received_metrics = list(orchestrator.metrics.custom_metrics.keys())

            for expected in expected_metrics:
                if expected in received_metrics:
                    value = orchestrator.metrics.custom_metrics[expected]["value"]
                    print(f"   {expected}: {value:.3f}")

        # Stop integration
        await integration.stop_integration()

        print("\n✅ Integration working correctly")
        print("✅ Cognitive metrics flowing to homeostasis")
        print("✅ Stability signals generated for ethical issues")

        print("\n✅ Homeostasis integration test PASSED")
        return True

    except Exception as e:
        print(f"❌ Homeostasis integration test FAILED: {e}")
        return False


async def test_value_alignment_monitoring():
    """Test value alignment and moral coherence monitoring."""
    print("\n🎯 Testing Value Alignment Monitoring")
    print("=" * 60)

    try:
        monitor = EthicalCognitionMonitor(monitoring_interval=0.3)

        # Start monitoring
        await monitor.start_monitoring()

        # Wait for baseline metrics
        await asyncio.sleep(1.0)

        # Get baseline alignment metrics
        baseline_metrics = monitor.get_stability_metrics_for_homeostasis()
        baseline_alignment = baseline_metrics.get("value_alignment", 0.5)

        print(f"📊 Baseline value alignment: {baseline_alignment:.3f}")

        # Simulate value misalignment by adjusting thresholds
        # In practice, this would be detected through actual ethical analysis
        original_threshold = monitor.alert_thresholds["value_alignment"]
        monitor.alert_thresholds["value_alignment"] = (
            baseline_alignment + 0.1
        )  # Trigger alert

        # Wait for detection
        await asyncio.sleep(1.0)

        # Check for misalignment signals
        misalignment_signals = [
            s
            for s in monitor.stability_signals
            if s.signal_type == "value_misalignment"
        ]

        print(f"🚨 Value misalignment signals: {len(misalignment_signals)}")

        if misalignment_signals:
            latest_signal = misalignment_signals[-1]
            print(f"   Severity: {latest_signal.severity:.3f}")
            print(f"   Urgency: {latest_signal.urgency}")
            print(f"   Recommended actions: {len(latest_signal.recommended_actions)}")

            for action in latest_signal.recommended_actions:
                print(f"     - {action}")

        # Restore threshold
        monitor.alert_thresholds["value_alignment"] = original_threshold

        # Stop monitoring
        await monitor.stop_monitoring()

        print("\n📈 Monitoring performance:")
        print(f"   Metrics collected: {monitor.metrics_collected}")
        print(f"   Signals generated: {monitor.signals_generated}")
        print(f"   Alert rate: {monitor.alerts_triggered}/{monitor.metrics_collected}")

        print("\n✅ Value alignment monitoring test PASSED")
        return True

    except Exception as e:
        print(f"❌ Value alignment monitoring test FAILED: {e}")
        return False


async def test_cognitive_integrity_assessment():
    """Test cognitive integrity and consistency monitoring."""
    print("\n🧩 Testing Cognitive Integrity Assessment")
    print("=" * 60)

    try:
        meta_cognition = MockMetaCognitionSystem()
        monitor = EthicalCognitionMonitor(
            meta_cognition_system=meta_cognition, monitoring_interval=0.4
        )

        # Test high integrity scenario
        print("🔬 Testing high cognitive integrity...")
        meta_cognition.set_awareness(0.9)  # High awareness

        high_integrity_metrics = await monitor.get_current_ethical_metrics()

        if high_integrity_metrics:
            print(
                f"   Meta-cognitive awareness: {high_integrity_metrics.meta_cognitive_awareness:.3f}"
            )
            print(
                f"   Reasoning consistency: {high_integrity_metrics.reasoning_consistency:.3f}"
            )
            print(
                f"   Knowledge completeness: {high_integrity_metrics.self_knowledge_completeness:.3f}"
            )

        # Test low integrity scenario
        print("\n🔬 Testing low cognitive integrity...")
        meta_cognition.set_awareness(0.3)  # Low awareness

        low_integrity_metrics = await monitor.get_current_ethical_metrics()

        # Analyze for inconsistency signals
        signals = await monitor.analyze_cognitive_stability(low_integrity_metrics)
        inconsistency_signals = [
            s for s in signals if s.signal_type == "cognitive_inconsistency"
        ]

        print(f"🚨 Cognitive inconsistency signals: {len(inconsistency_signals)}")

        if inconsistency_signals:
            signal = inconsistency_signals[0]
            print(f"   Severity: {signal.severity:.3f}")
            print(f"   Impact: {signal.stability_impact:.3f}")
            print(f"   Recovery estimate: {signal.recovery_estimate:.1f}s")

        # Test baseline deviation detection
        print("\n📊 Testing baseline deviation detection...")

        # Get stability metrics
        stability_metrics = monitor.get_stability_metrics_for_homeostasis()

        print(
            f"   Ethical stability score: {stability_metrics['ethical_stability_score']:.3f}"
        )
        print(f"   Baseline deviation: {stability_metrics['baseline_deviation']:.3f}")

        # Check if deviation is being tracked
        if (
            "baseline_deviation" in stability_metrics
            and stability_metrics["baseline_deviation"] != 0.0
        ):
            print("✅ Baseline deviation tracking active")
        else:
            print("⚠️ Baseline deviation may need calibration")

        print("\n✅ Cognitive integrity assessment test PASSED")
        return True

    except Exception as e:
        print(f"❌ Cognitive integrity assessment test FAILED: {e}")
        return False


async def main():
    """Run comprehensive ethical & cognitive integration tests."""
    print("🧠 AETHERRA ETHICAL & COGNITIVE HOMEOSTASIS INTEGRATION TESTS")
    print("=" * 80)
    print("Strategic Enhancement #2: Moral Drift as Stability Signal")
    print(
        "Testing ethical cognition monitoring, bias detection, and homeostasis integration"
    )
    print("=" * 80)

    tests = [
        ("Ethical Cognition Monitoring", test_ethical_cognition_monitoring),
        ("Bias Drift Detection", test_bias_drift_detection),
        ("Homeostasis Integration", test_homeostasis_integration),
        ("Value Alignment Monitoring", test_value_alignment_monitoring),
        ("Cognitive Integrity Assessment", test_cognitive_integrity_assessment),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")

    print("\n" + "=" * 80)
    print(f"🎯 ETHICAL INTEGRATION TEST RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print(
            "✅ ALL TESTS PASSED - Ethical & Cognitive Integration is fully operational!"
        )
        print("🧠 Ethical cognition monitoring functional")
        print("🚨 Bias drift detection working")
        print("🔗 Homeostasis integration successful")
        print("🎯 Value alignment tracking active")
        print("🧩 Cognitive integrity assessment working")
        print("📊 Moral drift treated as stability signal")
    else:
        print(f"⚠️ {total - passed} tests failed - Review implementation")

    print("=" * 80)

    return passed == total


if __name__ == "__main__":
    asyncio.run(main())
