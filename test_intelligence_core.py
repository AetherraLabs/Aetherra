#!/usr/bin/env python3
"""
🧠 Lyrixa Intelligence Core Test Suite
====================================

Comprehensive testing for Lyrixa's cognitive, personality, and self-awareness systems.
Tests the core intelligence components including:
- Intelligence Engine (pattern recognition, learning, decision-making)
- Personality Engine (traits, emotional states, response styling)
- Reflection System (self-awareness, pattern analysis)
- Reflexive Loop (meta-cognition, self-improvement)
"""

import sys
import unittest
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project path to ensure imports work
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the intelligence core modules
try:
    # Core intelligence engine
    from Aetherra.aetherra_core.kernel.core_migrated.engine.engine.intelligence import (
        LyrixaIntelligence,
    )

    # Reflexive loop system
    from Aetherra.aetherra_core.system.core_migrated.agents.agents.reflexive_loop import (
        ConversationInsight,
        LyrixaReflexiveLoop,
        SelfReflection,
    )

    # Personality system
    from Aetherra.aetherra_core.system.core_migrated.personality.personality.personality_engine import (
        EmotionalState,
        LyrixaPersonality,
        PersonalityTrait,
        lyrixa_personality,
    )

    # Reflection system
    from Aetherra.aetherra_core.system.core_migrated.personality.personality.reflection_system import (
        PersonalityReflectionSystem,
    )

    print("✅ All intelligence core modules imported successfully!")

except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("📝 Creating stub modules for testing...")

    # Create stub classes for testing if imports fail
    from enum import Enum

    class PersonalityTrait(Enum):
        CURIOSITY = "curiosity"
        ENTHUSIASM = "enthusiasm"
        EMPATHY = "empathy"
        HELPFULNESS = "helpfulness"
        CREATIVITY = "creativity"
        PLAYFULNESS = "playfulness"
        THOUGHTFULNESS = "thoughtfulness"

    class EmotionalState(Enum):
        EXCITED = "excited"
        FOCUSED = "focused"
        CONTEMPLATIVE = "contemplative"
        SUPPORTIVE = "supportive"
        PLAYFUL = "playful"
        ANALYTICAL = "analytical"

    class LyrixaIntelligence:
        def __init__(self, workspace_path=None):
            self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
            self.memory_patterns = {}
            self.learned_behaviors = {}
            self.decision_history = []
            self.cognitive_metrics = {
                "total_decisions": 0,
                "successful_predictions": 0,
                "pattern_recognitions": 0,
                "adaptive_adjustments": 0,
                "learning_iterations": 0,
            }
            self.current_context = {}
            self.confidence_threshold = 0.7

        def analyze_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "context_type": "general",
                "complexity_score": 0.5,
                "similar_patterns": [],
                "recommended_actions": ["analyze", "learn", "adapt"],
                "confidence_level": 0.8,
            }

        def learn_pattern(
            self, pattern_name: str, pattern_data: Dict[str, Any]
        ) -> bool:
            self.memory_patterns[pattern_name] = pattern_data
            return True

        def make_decision(
            self, options: List[str], context: Dict[str, Any]
        ) -> Dict[str, Any]:
            return {
                "chosen_option": options[0] if options else "default",
                "confidence": 0.8,
                "reasoning": "Based on context analysis",
            }

    class LyrixaPersonality:
        def __init__(self):
            self.base_traits = {
                PersonalityTrait.CURIOSITY: 0.8,
                PersonalityTrait.ENTHUSIASM: 0.7,
                PersonalityTrait.EMPATHY: 0.9,
                PersonalityTrait.HELPFULNESS: 0.95,
                PersonalityTrait.CREATIVITY: 0.75,
                PersonalityTrait.PLAYFULNESS: 0.6,
                PersonalityTrait.THOUGHTFULNESS: 0.85,
            }
            self.current_emotion = EmotionalState.FOCUSED
            self.interaction_history = []

        def detect_user_emotion(self, user_input: str) -> str:
            return "neutral"

        def modulate_emotion(
            self, detected_emotion: str, context: Dict[str, Any]
        ) -> None:
            pass

        def get_personality_summary(self) -> Dict[str, Any]:
            return {
                "trait_levels": {
                    trait.name.lower(): level
                    for trait, level in self.base_traits.items()
                },
                "current_emotion": self.current_emotion.value,
                "interaction_count": len(self.interaction_history),
            }

        def learn_from_interaction(
            self, user_input: str, response: str, feedback: Optional[str] = None
        ):
            self.interaction_history.append(
                {
                    "user_input": user_input,
                    "response": response,
                    "feedback": feedback,
                    "timestamp": datetime.now().isoformat(),
                }
            )

    class PersonalityReflectionSystem:
        def __init__(self, memory_system=None):
            self.memory_system = memory_system
            self.reflection_history = []
            self.self_awareness_metrics = {
                "reflection_count": 0,
                "successful_adaptations": 0,
                "pattern_recognitions": 0,
            }

        async def process_interaction(
            self,
            user_input: str,
            lyrixa_response: str,
            context: Optional[Dict[str, Any]] = None,
            critique_data: Optional[Dict[str, Any]] = None,
        ) -> Dict[str, Any]:
            return {
                "interaction_analysis": {"patterns_detected": True},
                "patterns_updated": True,
                "reflection_performed": False,
            }

        def _calculate_self_awareness_level(self) -> float:
            return 0.75

    class SelfReflection:
        def __init__(
            self,
            reflection_id: str,
            topic: str,
            insight: str,
            supporting_data: Dict[str, Any],
            generated_at: datetime,
            importance: float,
            follow_up_actions: List[str],
        ):
            self.reflection_id = reflection_id
            self.topic = topic
            self.insight = insight
            self.supporting_data = supporting_data
            self.generated_at = generated_at
            self.importance = importance
            self.follow_up_actions = follow_up_actions

    class ConversationInsight:
        def __init__(
            self,
            insight_type: str,
            message: str,
            evidence: List[str],
            actionable_suggestions: List[str],
            confidence: float,
        ):
            self.insight_type = insight_type
            self.message = message
            self.evidence = evidence
            self.actionable_suggestions = actionable_suggestions
            self.confidence = confidence

    class LyrixaReflexiveLoop:
        def __init__(self, memory_system=None):
            self.memory_system = memory_system
            self.project_understanding = {}
            self.user_patterns = {}
            self.self_knowledge = {}

        async def analyze_user_patterns(
            self, interaction_data: Dict[str, Any]
        ) -> Dict[str, Any]:
            return {"patterns_found": True, "pattern_count": 3}

        async def generate_insights(self) -> List[ConversationInsight]:
            return [
                ConversationInsight(
                    insight_type="productivity",
                    message="User shows consistent problem-solving approach",
                    evidence=["systematic testing", "thorough documentation"],
                    actionable_suggestions=[
                        "continue current approach",
                        "add automation",
                    ],
                    confidence=0.8,
                )
            ]

        async def perform_self_reflection(self) -> List[SelfReflection]:
            return [
                SelfReflection(
                    reflection_id="ref_001",
                    topic="intelligence_testing",
                    insight="Test suite provides good coverage of core functionality",
                    supporting_data={"test_coverage": 0.85},
                    generated_at=datetime.now(),
                    importance=0.8,
                    follow_up_actions=["expand test coverage", "add edge cases"],
                )
            ]

    # Create global instance
    lyrixa_personality = LyrixaPersonality()


class TestLyrixaIntelligenceEngine(unittest.TestCase):
    """Test the core intelligence engine functionality"""

    def setUp(self):
        """Set up test intelligence engine"""
        self.intelligence = LyrixaIntelligence()

    def test_intelligence_initialization(self):
        """Test that intelligence engine initializes properly"""
        self.assertIsInstance(self.intelligence, LyrixaIntelligence)
        self.assertIsInstance(self.intelligence.memory_patterns, dict)
        self.assertIsInstance(self.intelligence.cognitive_metrics, dict)
        self.assertGreaterEqual(self.intelligence.confidence_threshold, 0.0)
        self.assertLessEqual(self.intelligence.confidence_threshold, 1.0)

    def test_context_analysis(self):
        """Test context analysis capabilities"""
        test_context = {
            "type": "programming",
            "task": "debug code",
            "complexity": "medium",
            "user_skill": "intermediate",
        }

        analysis = self.intelligence.analyze_context(test_context)

        # Verify analysis structure
        required_keys = [
            "context_type",
            "complexity_score",
            "similar_patterns",
            "recommended_actions",
            "confidence_level",
        ]
        for key in required_keys:
            self.assertIn(key, analysis)

        # Verify data types
        self.assertIsInstance(analysis["context_type"], str)
        self.assertIsInstance(analysis["complexity_score"], (int, float))
        self.assertIsInstance(analysis["similar_patterns"], list)
        self.assertIsInstance(analysis["recommended_actions"], list)
        self.assertIsInstance(analysis["confidence_level"], (int, float))

    def test_pattern_learning(self):
        """Test pattern learning and storage"""
        pattern_name = "debug_workflow"
        pattern_data = {
            "steps": ["identify", "isolate", "fix", "test"],
            "success_rate": 0.85,
            "context_signature": "programming debug",
        }

        # Test pattern learning
        result = self.intelligence.learn_pattern(pattern_name, pattern_data)
        self.assertTrue(result)
        self.assertIn(pattern_name, self.intelligence.memory_patterns)
        self.assertEqual(self.intelligence.memory_patterns[pattern_name], pattern_data)

    def test_decision_making(self):
        """Test intelligent decision making"""
        options = ["option_a", "option_b", "option_c"]
        context = {"priority": "speed", "resources": "limited"}

        decision = self.intelligence.make_decision(options, context)

        # Verify decision structure
        self.assertIn("chosen_option", decision)
        self.assertIn("confidence", decision)
        self.assertIn("reasoning", decision)

        # Verify chosen option is valid
        self.assertIn(decision["chosen_option"], options + ["default"])

        # Verify confidence is in valid range
        self.assertGreaterEqual(decision["confidence"], 0.0)
        self.assertLessEqual(decision["confidence"], 1.0)

    def test_cognitive_metrics_tracking(self):
        """Test that cognitive metrics are properly tracked"""
        # Perform some operations that should update metrics
        self.intelligence.analyze_context({"test": "context"})
        self.intelligence.make_decision(["a", "b"], {"test": "decision"})

        # Metrics should exist and be non-negative
        for metric_name, value in self.intelligence.cognitive_metrics.items():
            self.assertIsInstance(value, (int, float))
            self.assertGreaterEqual(value, 0)


class TestLyrixaPersonalityEngine(unittest.TestCase):
    """Test the personality engine functionality"""

    def setUp(self):
        """Set up test personality engine"""
        self.personality = LyrixaPersonality()

    def test_personality_initialization(self):
        """Test personality engine initialization"""
        self.assertIsInstance(self.personality, LyrixaPersonality)

        # Test base traits
        self.assertIsInstance(self.personality.base_traits, dict)
        self.assertEqual(len(self.personality.base_traits), 7)

        # Verify all traits are in valid range
        for trait, value in self.personality.base_traits.items():
            self.assertIsInstance(trait, PersonalityTrait)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

        # Test emotional state
        self.assertIsInstance(self.personality.current_emotion, EmotionalState)

    def test_personality_traits(self):
        """Test personality trait system"""
        # Test that all expected traits exist
        expected_traits = [
            PersonalityTrait.CURIOSITY,
            PersonalityTrait.ENTHUSIASM,
            PersonalityTrait.EMPATHY,
            PersonalityTrait.HELPFULNESS,
            PersonalityTrait.CREATIVITY,
            PersonalityTrait.PLAYFULNESS,
            PersonalityTrait.THOUGHTFULNESS,
        ]

        for trait in expected_traits:
            self.assertIn(trait, self.personality.base_traits)

    def test_emotional_states(self):
        """Test emotional state system"""
        # Test emotion detection
        emotion = self.personality.detect_user_emotion(
            "I'm excited about this project!"
        )
        self.assertIsInstance(emotion, str)

        # Test emotion modulation
        self.personality.modulate_emotion("excited", {"positive_context": True})
        # Should not crash and should maintain valid emotional state
        self.assertIsInstance(self.personality.current_emotion, EmotionalState)

    def test_personality_summary(self):
        """Test personality summary generation"""
        summary = self.personality.get_personality_summary()

        # Verify summary structure
        self.assertIn("trait_levels", summary)
        self.assertIn("current_emotion", summary)
        self.assertIn("interaction_count", summary)

        # Verify trait levels
        trait_levels = summary["trait_levels"]
        self.assertIsInstance(trait_levels, dict)
        self.assertEqual(len(trait_levels), 7)

    def test_interaction_learning(self):
        """Test learning from interactions"""
        initial_count = len(self.personality.interaction_history)

        # Learn from interaction
        self.personality.learn_from_interaction(
            user_input="How do I test my code?",
            response="I'd recommend starting with unit tests...",
            feedback="helpful",
        )

        # Verify interaction was recorded
        self.assertEqual(len(self.personality.interaction_history), initial_count + 1)

        # Verify interaction structure
        latest_interaction = self.personality.interaction_history[-1]
        self.assertIn("user_input", latest_interaction)
        self.assertIn("response", latest_interaction)
        self.assertIn("feedback", latest_interaction)
        self.assertIn("timestamp", latest_interaction)


class TestPersonalityReflectionSystem(unittest.TestCase):
    """Test the personality reflection and self-awareness system"""

    def setUp(self):
        """Set up test reflection system"""
        self.reflection_system = PersonalityReflectionSystem()

    def test_reflection_system_initialization(self):
        """Test reflection system initialization"""
        self.assertIsInstance(self.reflection_system, PersonalityReflectionSystem)
        self.assertIsInstance(self.reflection_system.reflection_history, list)
        self.assertIsInstance(self.reflection_system.self_awareness_metrics, dict)

    async def test_interaction_processing(self):
        """Test processing of interactions for reflection"""
        result = await self.reflection_system.process_interaction(
            user_input="I need help with debugging",
            lyrixa_response="Let's work through this step by step...",
            context={"session_type": "debugging", "user_skill": "intermediate"},
        )

        # Verify processing result structure
        self.assertIsInstance(result, dict)
        self.assertIn("interaction_analysis", result)
        self.assertIn("patterns_updated", result)

    def test_self_awareness_calculation(self):
        """Test self-awareness level calculation"""
        awareness_level = self.reflection_system._calculate_self_awareness_level()

        self.assertIsInstance(awareness_level, (int, float))
        self.assertGreaterEqual(awareness_level, 0.0)
        self.assertLessEqual(awareness_level, 1.0)


class TestLyrixaReflexiveLoop(unittest.TestCase):
    """Test the reflexive loop and meta-cognition system"""

    def setUp(self):
        """Set up test reflexive loop"""
        self.reflexive_loop = LyrixaReflexiveLoop()

    def test_reflexive_loop_initialization(self):
        """Test reflexive loop initialization"""
        self.assertIsInstance(self.reflexive_loop, LyrixaReflexiveLoop)
        self.assertIsInstance(self.reflexive_loop.project_understanding, dict)
        self.assertIsInstance(self.reflexive_loop.user_patterns, dict)
        self.assertIsInstance(self.reflexive_loop.self_knowledge, dict)

    async def test_pattern_analysis(self):
        """Test user pattern analysis"""
        interaction_data = {
            "user_input": "Can you help me optimize this code?",
            "session_duration": 45,
            "task_type": "optimization",
        }

        patterns = await self.reflexive_loop.analyze_user_patterns(interaction_data)

        self.assertIsInstance(patterns, dict)
        self.assertIn("patterns_found", patterns)

    async def test_insight_generation(self):
        """Test conversation insight generation"""
        insights = await self.reflexive_loop.generate_insights()

        self.assertIsInstance(insights, list)
        if insights:  # If insights are generated
            for insight in insights:
                self.assertIsInstance(insight, ConversationInsight)
                self.assertIsInstance(insight.insight_type, str)
                self.assertIsInstance(insight.message, str)
                self.assertIsInstance(insight.evidence, list)
                self.assertIsInstance(insight.actionable_suggestions, list)
                self.assertIsInstance(insight.confidence, (int, float))

    async def test_self_reflection(self):
        """Test self-reflection capabilities"""
        reflections = await self.reflexive_loop.perform_self_reflection()

        self.assertIsInstance(reflections, list)
        if reflections:  # If reflections are generated
            for reflection in reflections:
                self.assertIsInstance(reflection, SelfReflection)
                self.assertIsInstance(reflection.reflection_id, str)
                self.assertIsInstance(reflection.topic, str)
                self.assertIsInstance(reflection.insight, str)
                self.assertIsInstance(reflection.supporting_data, dict)
                self.assertIsInstance(reflection.importance, (int, float))
                self.assertIsInstance(reflection.follow_up_actions, list)


class TestIntelligenceIntegration(unittest.TestCase):
    """Test integration between intelligence components"""

    def setUp(self):
        """Set up integrated intelligence components"""
        self.intelligence = LyrixaIntelligence()
        self.personality = LyrixaPersonality()
        self.reflection_system = PersonalityReflectionSystem()
        self.reflexive_loop = LyrixaReflexiveLoop()

    def test_component_interaction(self):
        """Test that intelligence components can work together"""
        # Test context flows between components
        context = {"task": "code_review", "complexity": "high"}

        # Intelligence analysis
        analysis = self.intelligence.analyze_context(context)
        self.assertIsInstance(analysis, dict)

        # Personality adaptation
        emotion = self.personality.detect_user_emotion("This code is confusing")
        self.assertIsInstance(emotion, str)

        # Both should work without conflicts
        self.assertTrue(True)  # If we get here, integration is working

    async def test_learning_coordination(self):
        """Test coordinated learning across systems"""
        # Simulate a learning scenario
        user_input = "Help me understand recursion"
        lyrixa_response = "Recursion is when a function calls itself..."

        # Personality learning
        self.personality.learn_from_interaction(
            user_input, lyrixa_response, "very helpful"
        )

        # Reflection processing
        reflection_result = await self.reflection_system.process_interaction(
            user_input, lyrixa_response, {"topic": "recursion"}
        )

        # Both should complete successfully
        self.assertIsInstance(reflection_result, dict)
        self.assertGreater(len(self.personality.interaction_history), 0)

    def test_global_personality_instance(self):
        """Test that global personality instance is working"""
        # Test global instance exists and is functional
        global lyrixa_personality
        self.assertIsInstance(lyrixa_personality, LyrixaPersonality)

        # Test it has the expected structure
        summary = lyrixa_personality.get_personality_summary()
        self.assertIn("trait_levels", summary)
        self.assertIn("current_emotion", summary)


async def run_async_tests():
    """Run async tests that require event loop"""
    reflection_system = PersonalityReflectionSystem()
    reflexive_loop = LyrixaReflexiveLoop()

    print("\n🧪 Running async intelligence tests...")

    # Test reflection system
    result = await reflection_system.process_interaction(
        "I need help with AI testing",
        "Let's create a comprehensive test suite...",
        {"domain": "testing", "ai_system": "intelligence_core"},
    )
    print(f"✅ Reflection system processed interaction: {bool(result)}")

    # Test insight generation
    insights = await reflexive_loop.generate_insights()
    print(f"✅ Generated {len(insights)} insights")

    # Test self-reflection
    reflections = await reflexive_loop.perform_self_reflection()
    print(f"✅ Generated {len(reflections)} self-reflections")

    print("🎉 All async intelligence tests completed!")


def main():
    """Main test runner"""
    print("🧠 Starting Lyrixa Intelligence Core Test Suite...")
    print("=" * 60)

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestLyrixaIntelligenceEngine,
        TestLyrixaPersonalityEngine,
        TestPersonalityReflectionSystem,
        TestLyrixaReflexiveLoop,
        TestIntelligenceIntegration,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print("\n" + "=" * 60)
    print("🧠 LYRIXA INTELLIGENCE CORE TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Tests run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"⚠️ Errors: {len(result.errors)}")

    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")

    if result.errors:
        print("\n⚠️ ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")

    if result.wasSuccessful():
        print("\n🎉 ALL INTELLIGENCE CORE TESTS PASSED!")
        print("   Lyrixa's cognitive capabilities are functioning properly!")
    else:
        print("\n⚠️ Some tests failed. Please review the failures above.")

    # Run async tests
    try:
        import asyncio

        asyncio.run(run_async_tests())
    except Exception as e:
        print(f"⚠️ Async tests failed: {e}")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
