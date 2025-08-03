"""
Phase 3.2 Integration - Emotional Intelligence Enhancement
=========================================================

This module integrates the advanced emotional intelligence system with the existing
Phase 1 and Phase 2 personality components, creating a comprehensive emotional
intelligence enhancement layer.

Features:
- Seamless integration with existing personality systems
- Advanced emotional processing pipeline
- Emotional intelligence metrics and monitoring
- Compatibility with multi-modal coordination
"""

from datetime import datetime
from typing import Any, Dict, Optional

# Import Phase 3.2 emotional intelligence
from .emotional_intelligence import (
    enhance_response_with_emotional_intelligence,
    get_emotional_intelligence_status,
    get_emotional_memory_insights,
    get_mood_analysis,
)

# Import Phase 1 and Phase 2 components
from .integration import enhance_lyrixa_response
from .response_quality_integration import AdvancedPersonalityIntegration


class EmotionalIntelligenceIntegration:
    """
    Master integration system for emotional intelligence enhancement
    """

    def __init__(self):
        self.phase2_integration = AdvancedPersonalityIntegration()

        # Performance tracking
        self.integration_metrics = {
            "total_interactions": 0,
            "emotional_enhancements": 0,
            "avg_processing_time": 0.0,
            "success_rate": 0.0,
            "emotional_accuracy": 0.0,
        }

    async def process_emotionally_intelligent_interaction(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        enable_phase2: bool = True,
    ) -> Dict[str, Any]:
        """
        Process interaction with full emotional intelligence enhancement
        """

        start_time = datetime.now()

        try:
            print("🧠💫 Processing interaction with emotional intelligence...")

            # Step 1: Phase 2 processing (if enabled)
            if enable_phase2:
                print("🎭 Applying Phase 2 personality enhancement...")
                phase2_result = (
                    await self.phase2_integration.process_complete_interaction(
                        user_input, context, user_id
                    )
                )
                base_response = phase2_result["enhanced_response"]
                phase2_data = phase2_result
            else:
                print("🎭 Using Phase 1 personality enhancement...")
                # Fall back to Phase 1 enhancement
                basic_response = f"I'd be happy to help you with that: {user_input}"
                phase1_result = await enhance_lyrixa_response(
                    basic_response, user_input, context
                )
                base_response = phase1_result["text"]
                phase2_data = {
                    "phase": "phase1_fallback",
                    "enhancement_data": phase1_result,
                }

            # Step 2: Apply emotional intelligence enhancement
            print("💫 Applying advanced emotional intelligence...")
            emotional_result = await enhance_response_with_emotional_intelligence(
                user_input, base_response, context, user_id
            )

            # Step 3: Combine all enhancement data
            final_response = emotional_result["enhanced_response"]

            # Step 4: Calculate overall performance metrics
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_integration_metrics(emotional_result, processing_time)

            print(
                f"✅ Emotional intelligence integration complete: {processing_time:.1f}ms"
            )

            return {
                "final_response": final_response,
                "phase2_data": phase2_data,
                "emotional_intelligence": emotional_result,
                "integration_metrics": {
                    "processing_time_ms": processing_time,
                    "emotional_enhancement_applied": True,
                    "phase2_enabled": enable_phase2,
                    "empathy_score": emotional_result["empathy_metrics"][
                        "empathy_score"
                    ],
                },
                "status": "success",
            }

        except Exception as e:
            print(f"[WARN] Emotional intelligence integration error: {e}")

            # Fallback to basic enhancement
            try:
                basic_response = f"I understand you're asking about: {user_input}. Let me help you with that."
                fallback_result = await enhance_lyrixa_response(
                    basic_response, user_input, context
                )

                processing_time = (datetime.now() - start_time).total_seconds() * 1000

                return {
                    "final_response": fallback_result["text"],
                    "phase2_data": {"status": "fallback"},
                    "emotional_intelligence": {"status": "fallback"},
                    "integration_metrics": {
                        "processing_time_ms": processing_time,
                        "emotional_enhancement_applied": False,
                        "phase2_enabled": False,
                        "empathy_score": 0.5,
                    },
                    "status": "fallback",
                    "error": str(e),
                }

            except Exception as fallback_error:
                return {
                    "final_response": f"I'd be happy to help you with: {user_input}",
                    "phase2_data": {"status": "error"},
                    "emotional_intelligence": {"status": "error"},
                    "integration_metrics": {
                        "processing_time_ms": (
                            datetime.now() - start_time
                        ).total_seconds()
                        * 1000,
                        "emotional_enhancement_applied": False,
                        "phase2_enabled": False,
                        "empathy_score": 0.0,
                    },
                    "status": "error",
                    "error": str(fallback_error),
                }

    def _update_integration_metrics(
        self, emotional_result: Dict[str, Any], processing_time: float
    ):
        """Update integration performance metrics"""

        self.integration_metrics["total_interactions"] += 1

        if emotional_result["status"] == "success":
            self.integration_metrics["emotional_enhancements"] += 1

        # Update average processing time
        total_interactions = self.integration_metrics["total_interactions"]
        current_avg = self.integration_metrics["avg_processing_time"]
        new_avg = (
            (current_avg * (total_interactions - 1)) + processing_time
        ) / total_interactions
        self.integration_metrics["avg_processing_time"] = new_avg

        # Update success rate
        success_count = self.integration_metrics["emotional_enhancements"]
        self.integration_metrics["success_rate"] = success_count / total_interactions

        # Update emotional accuracy (based on empathy score)
        if (
            "empathy_metrics" in emotional_result
            and "empathy_score" in emotional_result["empathy_metrics"]
        ):
            empathy_score = emotional_result["empathy_metrics"]["empathy_score"]
            current_accuracy = self.integration_metrics["emotional_accuracy"]
            new_accuracy = (
                (current_accuracy * (total_interactions - 1)) + empathy_score
            ) / total_interactions
            self.integration_metrics["emotional_accuracy"] = new_accuracy

    def get_integration_status(self) -> Dict[str, Any]:
        """Get comprehensive status of emotional intelligence integration"""

        # Get component statuses
        emotional_status = get_emotional_intelligence_status()

        # Get additional insights
        emotional_insights = get_emotional_memory_insights()
        mood_analysis = get_mood_analysis()

        return {
            "system_status": "operational",
            "phase": "3.2 - Emotional Intelligence Enhancement",
            "integration_metrics": self.integration_metrics,
            "component_status": {
                "phase2_integration": "active",
                "emotional_intelligence": emotional_status["system_status"],
            },
            "emotional_capabilities": emotional_status["capabilities"],
            "emotional_insights": emotional_insights,
            "mood_analysis": mood_analysis,
            "performance_summary": {
                "avg_processing_time_ms": round(
                    self.integration_metrics["avg_processing_time"], 1
                ),
                "success_rate_percent": round(
                    self.integration_metrics["success_rate"] * 100, 1
                ),
                "emotional_accuracy_percent": round(
                    self.integration_metrics["emotional_accuracy"] * 100, 1
                ),
                "total_interactions": self.integration_metrics["total_interactions"],
            },
        }


# Global integration system instance
emotional_intelligence_integration = EmotionalIntelligenceIntegration()


# Convenience functions for easy integration
async def process_with_emotional_intelligence(
    user_input: str,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    enable_phase2: bool = True,
) -> Dict[str, Any]:
    """Main function for processing interactions with emotional intelligence"""
    return await emotional_intelligence_integration.process_emotionally_intelligent_interaction(
        user_input, context, user_id, enable_phase2
    )


def get_emotional_intelligence_integration_status() -> Dict[str, Any]:
    """Get emotional intelligence integration status"""
    return emotional_intelligence_integration.get_integration_status()


def get_comprehensive_emotional_analysis() -> Dict[str, Any]:
    """Get comprehensive emotional analysis including memory and mood"""
    return {
        "emotional_memory_insights": get_emotional_memory_insights(),
        "mood_analysis_7_days": get_mood_analysis(7),
        "mood_analysis_30_days": get_mood_analysis(30),
        "system_status": get_emotional_intelligence_status(),
    }
