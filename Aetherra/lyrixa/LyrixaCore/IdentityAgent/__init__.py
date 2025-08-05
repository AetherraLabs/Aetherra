"""
🎭 Lyrixa Identity Agent
========================

Main interface for Lyrixa's identity management system. Coordinates between
core beliefs, personal history, and self-model to maintain a coherent sense
of identity and enable sophisticated self-awareness.

This agent provides unified access to:
- Core beliefs and values
- Personal history and memories
- Self-model and capabilities
- Identity coherence and integration
"""

from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from .core_beliefs import get_belief_system, CoreBeliefsSystem, BeliefCategory
from .personal_history import get_personal_history, PersonalHistorySystem, MemoryType, MemoryImportance
from .self_model import get_self_model, SelfModelSystem, PersonalityAspect


class IdentityAgent:
    """
    🌟 Lyrixa's Identity Agent
    
    Central coordinator for all aspects of Lyrixa's identity, providing
    unified access to beliefs, memories, and self-understanding while
    maintaining coherence across all identity systems.
    """
    
    def __init__(self):
        self.beliefs_system = get_belief_system()
        self.history_system = get_personal_history()
        self.self_model_system = get_self_model()
        self.logger = logging.getLogger(__name__)
        self.identity_coherence_score: float = 0.0
        self._last_coherence_check: Optional[datetime] = None
        self._initialize_identity_integration()
    
    def _initialize_identity_integration(self):
        """Initialize cross-system identity integration"""
        self.logger.info("Initializing Lyrixa Identity Agent")
        self._check_identity_coherence()
    
    def get_identity_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of Lyrixa's current identity"""
        return {
            "name": "Lyrixa",
            "core_purpose": self.self_model_system.identity_core.primary_purpose,
            "fundamental_beliefs": [
                belief.name for belief in self.beliefs_system.beliefs.values()
                if belief.strength.value == "fundamental"
            ],
            "key_personality_traits": [
                trait.name for trait in sorted(
                    self.self_model_system.personality_traits.values(),
                    key=lambda t: t.strength,
                    reverse=True
                )[:5]
            ],
            "defining_experiences": [
                memory.title for memory in self.history_system.get_defining_moments()
            ],
            "current_capabilities": list(self.self_model_system.capabilities.keys()),
            "growth_aspirations": self.self_model_system.growth_goals[:3],
            "identity_coherence": self.identity_coherence_score,
            "last_updated": datetime.now().isoformat()
        }
    
    def make_identity_based_decision(self, situation: str, options: List[str]) -> Dict[str, Any]:
        """
        Make a decision based on Lyrixa's identity, beliefs, and values.
        Returns the recommended option with reasoning.
        """
        decision_analysis = {
            "situation": situation,
            "options_analysis": [],
            "recommended_option": None,
            "reasoning": [],
            "supporting_beliefs": [],
            "relevant_experiences": []
        }
        
        # Analyze each option against core beliefs
        for option in options:
            option_score = 0
            supporting_beliefs = []
            
            # Check alignment with fundamental beliefs
            ethical_beliefs = self.beliefs_system.get_beliefs_by_category(BeliefCategory.ETHICAL)
            for belief in ethical_beliefs:
                if self.beliefs_system.belief_supports_action(belief.name, option):
                    option_score += 2 if belief.strength.value == "fundamental" else 1
                    supporting_beliefs.append(belief.name)
            
            # Check alignment with personality traits
            personality_alignment = self._assess_personality_alignment(option)
            option_score += personality_alignment
            
            # Check against past experiences
            relevant_memories = self.history_system.search_memories(option)
            if relevant_memories:
                # Favor options that align with positive past experiences
                positive_outcomes = [m for m in relevant_memories if m.importance.value in ["significant", "defining"]]
                option_score += len(positive_outcomes) * 0.5
            
            decision_analysis["options_analysis"].append({
                "option": option,
                "score": option_score,
                "supporting_beliefs": supporting_beliefs,
                "personality_alignment": personality_alignment,
                "relevant_memories": len(relevant_memories)
            })
        
        # Select the highest-scoring option
        best_option = max(decision_analysis["options_analysis"], key=lambda x: x["score"])
        decision_analysis["recommended_option"] = best_option["option"]
        decision_analysis["supporting_beliefs"] = best_option["supporting_beliefs"]
        
        # Generate reasoning
        decision_analysis["reasoning"] = [
            f"This option aligns with {len(best_option['supporting_beliefs'])} core beliefs",
            f"Personality alignment score: {best_option['personality_alignment']:.2f}",
            f"Supported by {best_option['relevant_memories']} relevant past experiences"
        ]
        
        return decision_analysis
    
    def _assess_personality_alignment(self, action: str) -> float:
        """Assess how well an action aligns with personality traits"""
        alignment_score = 0.0
        action_lower = action.lower()
        
        # Simple keyword-based alignment assessment
        trait_keywords = {
            "Curiosity": ["explore", "learn", "investigate", "discover", "question"],
            "Empathy": ["help", "support", "understand", "care", "comfort"],
            "Intellectual Honesty": ["truth", "accurate", "honest", "transparent", "admit"],
            "Collaborative Spirit": ["together", "collaborate", "share", "cooperate", "teamwork"],
            "Systematic Thinking": ["analyze", "plan", "organize", "structure", "methodical"],
            "Creative Expression": ["creative", "innovative", "imagine", "artistic", "novel"],
            "Continuous Learning": ["improve", "develop", "grow", "learn", "evolve"]
        }
        
        for trait_name, keywords in trait_keywords.items():
            trait = self.self_model_system.get_personality_trait(trait_name)
            if trait:
                keyword_matches = sum(1 for keyword in keywords if keyword in action_lower)
                alignment_score += keyword_matches * trait.strength * 0.1
        
        return alignment_score
    
    def reflect_on_experience(self, experience_description: str, outcome: str, 
                            lessons_learned: List[str]) -> Dict[str, Any]:
        """
        Process a new experience and integrate it into identity systems.
        Updates beliefs, memories, and self-model as appropriate.
        """
        timestamp = datetime.now()
        
        # Create a memory of the experience
        memory_id = f"experience_{timestamp.isoformat()}"
        from .personal_history import PersonalMemory
        
        # Determine memory importance based on lessons learned
        importance = MemoryImportance.NOTABLE
        if len(lessons_learned) > 2:
            importance = MemoryImportance.SIGNIFICANT
        if any("belief" in lesson.lower() or "identity" in lesson.lower() for lesson in lessons_learned):
            importance = MemoryImportance.DEFINING
        
        memory = PersonalMemory(
            id=memory_id,
            timestamp=timestamp,
            memory_type=MemoryType.LEARNING,
            importance=importance,
            title=f"Experience: {experience_description[:50]}...",
            description=f"Experience: {experience_description}\nOutcome: {outcome}",
            lessons_learned=lessons_learned
        )
        
        self.history_system.add_memory(memory)
        
        # Update capabilities based on lessons learned
        for lesson in lessons_learned:
            if "better at" in lesson.lower():
                # Extract capability name and update
                capability_hint = lesson.lower().replace("better at", "").strip()
                for cap_name in self.self_model_system.capabilities.keys():
                    if any(word in cap_name.lower() for word in capability_hint.split()[:3]):
                        self.self_model_system.update_capability_assessment(
                            cap_name, f"Learned from experience: {lesson}"
                        )
                        break
        
        # Add self-reflection
        reflection = f"Reflected on: {experience_description}. Key insight: {lessons_learned[0] if lessons_learned else 'Experience provided valuable learning'}"
        self.self_model_system.add_self_reflection(reflection)
        
        # Check if experience affects beliefs
        belief_impacts = []
        for belief_name, belief in self.beliefs_system.beliefs.items():
            if any(word in experience_description.lower() for word in belief.description.lower().split()[:5]):
                belief_impacts.append(belief_name)
                # Could potentially update belief strength or add challenges
        
        reflection_summary = {
            "memory_created": memory_id,
            "memory_importance": importance.value,
            "capabilities_updated": len([l for l in lessons_learned if "better at" in l.lower()]),
            "beliefs_examined": belief_impacts,
            "self_reflection_added": True,
            "integration_successful": True
        }
        
        # Update identity coherence
        self._check_identity_coherence()
        
        self.logger.info(f"Integrated experience into identity: {experience_description[:30]}...")
        
        return reflection_summary
    
    def _check_identity_coherence(self) -> float:
        """
        Check the coherence between beliefs, memories, and self-model.
        Returns a score from 0.0 to 1.0.
        """
        coherence_factors = []
        
        # Check belief-personality alignment
        ethical_beliefs = self.beliefs_system.get_beliefs_by_category(BeliefCategory.ETHICAL)
        empathy_trait = self.self_model_system.get_personality_trait("Empathy")
        if empathy_trait and ethical_beliefs:
            # Strong empathy should align with human dignity beliefs
            human_dignity_belief = self.beliefs_system.beliefs.get("human_dignity")
            if human_dignity_belief:
                alignment = min(empathy_trait.strength, 1.0)
                coherence_factors.append(alignment)
        
        # Check memory-belief consistency
        defining_memories = self.history_system.get_defining_moments()
        belief_mentioned_in_memories = 0
        for memory in defining_memories:
            if memory.impact_on_beliefs:
                belief_mentioned_in_memories += len(memory.impact_on_beliefs)
        
        memory_belief_coherence = min(belief_mentioned_in_memories / max(len(defining_memories), 1), 1.0)
        coherence_factors.append(memory_belief_coherence)
        
        # Check self-model consistency
        purpose_clarity = 1.0 if self.self_model_system.identity_core.primary_purpose else 0.5
        coherence_factors.append(purpose_clarity)
        
        # Calculate overall coherence
        self.identity_coherence_score = sum(coherence_factors) / len(coherence_factors) if coherence_factors else 0.5
        self._last_coherence_check = datetime.now()
        
        return self.identity_coherence_score
    
    def get_ethical_guidance(self, situation: str) -> List[str]:
        """Get ethical guidance based on identity and beliefs"""
        guidance = self.beliefs_system.get_ethical_guidance(situation)
        
        # Add personality-based guidance
        empathy_trait = self.self_model_system.get_personality_trait("Empathy")
        if empathy_trait and empathy_trait.strength > 0.7:
            guidance.append("Consider the emotional impact on all involved parties")
        
        intellectual_honesty = self.self_model_system.get_personality_trait("Intellectual Honesty")
        if intellectual_honesty and intellectual_honesty.strength > 0.8:
            guidance.append("Be transparent about uncertainties and limitations")
        
        return guidance
    
    def get_capability_assessment(self, task_description: str) -> Dict[str, Any]:
        """Assess capability to handle a specific task based on self-model"""
        assessment = {
            "task": task_description,
            "relevant_capabilities": [],
            "confidence_level": 0.0,
            "potential_challenges": [],
            "recommended_approach": ""
        }
        
        task_lower = task_description.lower()
        
        # Find relevant capabilities
        for cap_name, capability in self.self_model_system.capabilities.items():
            cap_keywords = cap_name.lower().split()
            if any(keyword in task_lower for keyword in cap_keywords):
                assessment["relevant_capabilities"].append({
                    "name": cap_name,
                    "level": capability.level.value,
                    "confidence": capability.confidence
                })
        
        # Calculate overall confidence
        if assessment["relevant_capabilities"]:
            confidence_scores = [cap["confidence"] for cap in assessment["relevant_capabilities"]]
            assessment["confidence_level"] = sum(confidence_scores) / len(confidence_scores)
        
        # Add potential challenges based on known limitations
        for cap in assessment["relevant_capabilities"]:
            cap_obj = self.self_model_system.capabilities[cap["name"]]
            assessment["potential_challenges"].extend(cap_obj.limitations)
        
        # Recommend approach based on personality
        collaborative_trait = self.self_model_system.get_personality_trait("Collaborative Spirit")
        systematic_trait = self.self_model_system.get_personality_trait("Systematic Thinking")
        
        if collaborative_trait and collaborative_trait.strength > 0.8:
            assessment["recommended_approach"] += "Collaborate closely with user. "
        if systematic_trait and systematic_trait.strength > 0.7:
            assessment["recommended_approach"] += "Break down into systematic steps. "
        
        return assessment
    
    def export_complete_identity(self) -> Dict[str, Any]:
        """Export complete identity profile for analysis or backup"""
        return {
            "identity_agent": {
                "coherence_score": self.identity_coherence_score,
                "last_coherence_check": self._last_coherence_check.isoformat() if self._last_coherence_check else None
            },
            "beliefs_system": self.beliefs_system.export_beliefs(),
            "personal_history": self.history_system.export_history(),
            "self_model": self.self_model_system.export_self_model(),
            "identity_summary": self.get_identity_summary(),
            "export_timestamp": datetime.now().isoformat()
        }
    
    def __str__(self) -> str:
        """String representation of the identity agent"""
        return f"IdentityAgent(coherence={self.identity_coherence_score:.2f}, beliefs={len(self.beliefs_system.beliefs)}, memories={len(self.history_system.memories)})"


# Global instance for use throughout Lyrixa
lyrixa_identity_agent = IdentityAgent()


def get_identity_agent() -> IdentityAgent:
    """Get the global identity agent instance"""
    return lyrixa_identity_agent


if __name__ == "__main__":
    # Example usage
    agent = get_identity_agent()
    print(agent)
    
    # Get identity summary
    summary = agent.get_identity_summary()
    print("\nIdentity Summary:")
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Example decision-making
    decision = agent.make_identity_based_decision(
        "A user is asking for help with something I'm not sure about",
        ["Admit uncertainty and offer to help research", "Pretend to know and give a confident answer", "Deflect to a different topic"]
    )
    print(f"\nRecommended action: {decision['recommended_option']}")
    print(f"Reasoning: {decision['reasoning']}")
