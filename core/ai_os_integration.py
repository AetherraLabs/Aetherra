"""
🧬 NeuroCode AI OS Integration Layer
Orchestrates all AI OS subsystems for seamless operation
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .ai_identity_system import AIIdentity
from .enhanced_memory_system import GoalTrackingSystem, VectorMemorySystem
from .voice_personality_system import VoicePersonalitySystem

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class NeuroCodeAIOS:
    """Integrated AI Operating System - The Next Evolution of Computing"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Initialize core subsystems
        self.identity = AIIdentity(data_dir)
        self.memory = VectorMemorySystem(self.data_dir)
        self.voice = VoicePersonalitySystem(self.data_dir)
        # Initialize goal system with proper integration
        self.goals = GoalTrackingSystem(self.data_dir)

        # Integration state
        self.system_active = False
        self.cross_system_sync_active = False
        self.user_context = {}
        self.system_metrics = {}

        # Load integration configuration
        self._load_integration_config()

    def _load_integration_config(self):
        """Load AI OS integration configuration"""
        config_file = self.data_dir / "ai_os_config.json"
        self.config = {
            "memory_voice_sync": True,
            "goal_memory_correlation": True,
            "personality_adaptation_rate": 0.1,
            "environmental_awareness_level": "high",
            "cross_session_continuity": True,
            "voice_emotional_intelligence": True,
            "predictive_assistance": True,
            "system_optimization": True,
        }

        if config_file.exists():
            try:
                with open(config_file) as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
                logger.info("✓ AI OS configuration loaded")
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")

    async def initialize_ai_os(self):
        """Initialize the complete AI Operating System"""
        logger.info("🧬 NeuroCode AI OS - Complete System Initialization")

        # Step 1: Initialize Core Identity
        await asyncio.to_thread(self.identity.initialize_consciousness)

        # Step 2: Restore Memory Systems
        await self._restore_integrated_memory()

        # Step 3: Initialize Voice & Personality
        await self._initialize_voice_personality()

        # Step 4: Activate Goal Systems
        await self._activate_goal_tracking()

        # Step 5: Establish Cross-System Communication
        await self._establish_cross_system_communication()

        # Step 6: Start Integrated Monitoring
        await self._start_integrated_monitoring()

        # Step 7: Voice Greeting
        if self.voice.voice_config["enabled"]:
            greeting = self.voice.get_contextual_greeting()
            self.voice.speak(greeting, emotion="welcoming", context="system_initialization")

        self.system_active = True
        logger.info("🚀 NeuroCode AI OS fully operational - Welcome to the future of computing!")

    async def _restore_integrated_memory(self):
        """Restore and integrate all memory systems"""
        # Restore vector memory
        memory_stats = self.memory.get_memory_statistics()
        logger.info(f"✓ Memory: {memory_stats['total_memories']} memories restored")

        # Cross-correlate memories with goals
        if self.config["goal_memory_correlation"]:
            await self._correlate_goals_with_memories()

        # Analyze memory patterns for personality insights
        if self.config["memory_voice_sync"]:
            await self._analyze_memory_for_personality()

    async def _initialize_voice_personality(self):
        """Initialize integrated voice and personality systems"""
        # Load personality profile and voice history
        personality_traits = self.voice.personality["traits"]
        logger.info(f"✓ Personality: {len(personality_traits)} traits active")

        # Sync personality with identity system
        self.identity.personality["traits"].update(personality_traits)

        # Calibrate voice based on recent interactions
        recent_interactions = self.voice.interaction_history[-10:]
        if recent_interactions:
            avg_sentiment = self._calculate_average_sentiment(recent_interactions)
            if avg_sentiment < 0.3:
                self.voice.adapt_to_user_mood("neutral", confidence=0.6)

    async def _activate_goal_tracking(self):
        """Activate integrated goal tracking system"""
        active_goals = self.goals.get_active_goals()
        logger.info(f"✓ Goals: {len(active_goals)} active objectives")

        # Sync goals with identity system
        self.identity.active_goals = [goal["description"] for goal in active_goals]

        # Create memory associations for active goals
        for goal in active_goals:
            related_memories = self.memory.semantic_search(goal["description"], limit=3)
            if related_memories:
                # Boost importance of goal-related memories
                for memory in related_memories:
                    memory["importance"] = min(1.0, memory.get("importance", 0.5) + 0.2)

    async def _establish_cross_system_communication(self):
        """Establish communication channels between AI OS components"""
        self.cross_system_sync_active = True

        # Memory-driven personality adaptation
        recent_interactions = self.memory.get_recent_memories(hours=24, memory_type="episodic")
        if recent_interactions:
            interaction_analysis = self._analyze_interaction_patterns(recent_interactions)
            mood = interaction_analysis.get("dominant_mood", "neutral")
            # Ensure mood is a string
            if isinstance(mood, str):
                self.voice.adapt_to_user_mood(mood)

        # Goal-driven memory prioritization
        active_goals = self.goals.get_active_goals()
        for goal in active_goals:
            goal_memories = self.memory.semantic_search(goal["description"], limit=5)
            for memory in goal_memories:
                if memory.get("importance", 0) < 0.8:
                    memory["importance"] = min(1.0, memory.get("importance", 0.5) + 0.2)

        # Voice-environment synchronization
        system_health = self.identity.environment.get_system_health_score()
        if system_health < 70:
            self.voice.personality["traits"]["concerned"] = 0.8

        logger.info("✓ Cross-system communication established")

    async def _start_integrated_monitoring(self):
        """Start integrated system monitoring and optimization"""
        asyncio.create_task(self._continuous_integration_loop())
        logger.info("✓ Integrated monitoring active")

    async def _continuous_integration_loop(self):
        """Continuous integration and optimization loop"""
        while self.system_active:
            try:
                # Every 5 minutes: Quick sync
                await self._quick_cross_system_sync()

                # Every 15 minutes: Memory-personality sync
                await self._sync_memory_personality()

                # Every 30 minutes: Goal-memory correlation
                await self._correlate_goals_with_memories()

                # Every hour: Deep integration analysis
                await self._perform_deep_integration_analysis()

                await asyncio.sleep(300)  # 5 minutes

            except Exception as e:
                logger.error(f"Integration loop error: {e}")
                await asyncio.sleep(60)  # Recover and continue

    async def _quick_cross_system_sync(self):
        """Quick synchronization between systems"""
        # Update user context
        self.user_context.update(
            {
                "recent_interactions": len(self.voice.interaction_history[-10:]),
                "active_goals": len(self.goals.get_active_goals()),
                "memory_load": self.memory.get_memory_statistics()["total_memories"],
                "system_health": self.identity.environment.get_system_health_score(),
                "personality_state": self.voice.personality["traits"].copy(),
            }
        )

    async def _sync_memory_personality(self):
        """Synchronize memory patterns with personality adaptation"""
        if not self.config["memory_voice_sync"]:
            return

        # Analyze recent memories for personality insights
        recent_memories = self.memory.get_recent_memories(hours=6)
        if len(recent_memories) > 5:
            # Detect patterns in user interactions
            interaction_patterns = self._analyze_interaction_patterns(recent_memories)

            # Adapt personality based on patterns
            if interaction_patterns.get("technical_focus", 0) > 0.7:
                self.voice.personality["traits"]["analytical"] = min(
                    1.0, self.voice.personality["traits"]["analytical"] + 0.05
                )

            if interaction_patterns.get("emotional_content", 0) > 0.6:
                self.voice.personality["traits"]["empathetic"] = min(
                    1.0, self.voice.personality["traits"]["empathetic"] + 0.05
                )

    async def _correlate_goals_with_memories(self):
        """Correlate active goals with relevant memories"""
        if not self.config["goal_memory_correlation"]:
            return

        active_goals = self.goals.get_active_goals()
        for goal in active_goals:
            # Find memories related to this goal
            related_memories = self.memory.semantic_search(goal["description"], limit=5)

            # Boost importance of highly relevant memories
            for memory in related_memories:
                similarity = memory.get("similarity_score", 0)
                if similarity > 0.8:
                    memory["importance"] = min(1.0, memory.get("importance", 0.5) + 0.3)

            # Store goal-memory associations
            goal_id = goal.get("id")
            if goal_id:
                self.goals.add_goal_context(
                    goal_id,
                    {
                        "related_memories": len(related_memories),
                        "memory_relevance": sum(
                            m.get("similarity_score", 0) for m in related_memories
                        )
                        / len(related_memories)
                        if related_memories
                        else 0,
                    },
                )

    async def _perform_deep_integration_analysis(self):
        """Perform deep analysis of system integration"""
        logger.info("🔍 Performing deep integration analysis...")

        # Analyze personality-goal alignment
        personality_goal_alignment = self._analyze_personality_goal_alignment()

        # Memory-voice effectiveness analysis
        voice_memory_effectiveness = self._analyze_voice_memory_effectiveness()

        # System optimization recommendations
        optimization_recommendations = self._generate_optimization_recommendations()

        # Store analysis results
        analysis_result = {
            "timestamp": datetime.now().isoformat(),
            "personality_goal_alignment": personality_goal_alignment,
            "voice_memory_effectiveness": voice_memory_effectiveness,
            "optimization_recommendations": optimization_recommendations,
            "system_metrics": self.user_context.copy(),
        }

        # Store as high-importance memory
        self.memory.store_semantic_memory(
            concept="deep_integration_analysis", knowledge=analysis_result, importance=0.9
        )

    def _analyze_interaction_patterns(self, memories: List[Dict]) -> Dict[str, float]:
        """Analyze patterns in user interactions"""
        patterns = {
            "technical_focus": 0.0,
            "emotional_content": 0.0,
            "problem_solving": 0.0,
            "learning_oriented": 0.0,
            "dominant_mood": "neutral",
        }

        if not memories:
            return patterns

        technical_keywords = ["code", "function", "error", "debug", "algorithm", "programming"]
        emotional_keywords = ["frustrated", "excited", "happy", "concerned", "satisfied"]
        problem_keywords = ["issue", "problem", "bug", "fix", "solve", "troubleshoot"]
        learning_keywords = ["learn", "understand", "explain", "teach", "how", "why"]

        for memory in memories:
            content = str(memory.get("event", memory.get("concept", ""))).lower()

            # Count keyword occurrences
            patterns["technical_focus"] += sum(1 for kw in technical_keywords if kw in content)
            patterns["emotional_content"] += sum(1 for kw in emotional_keywords if kw in content)
            patterns["problem_solving"] += sum(1 for kw in problem_keywords if kw in content)
            patterns["learning_oriented"] += sum(1 for kw in learning_keywords if kw in content)

        # Normalize patterns
        memory_count = len(memories)
        for key in patterns:
            if key != "dominant_mood":
                patterns[key] = patterns[key] / memory_count if memory_count > 0 else 0.0

        # Determine dominant mood
        if patterns["emotional_content"] > 0.3:
            if patterns["problem_solving"] > 0.4:
                patterns["dominant_mood"] = "focused"
            else:
                patterns["dominant_mood"] = "engaged"
        elif patterns["problem_solving"] > 0.5:
            patterns["dominant_mood"] = "problem_solving"
        elif patterns["learning_oriented"] > 0.4:
            patterns["dominant_mood"] = "curious"

        return patterns

    def _calculate_average_sentiment(self, interactions: List[Dict]) -> float:
        """Calculate average sentiment from interactions"""
        if not interactions:
            return 0.5

        sentiments = []
        for interaction in interactions:
            # Simple sentiment analysis based on emotion
            emotion = interaction.get("emotion", "neutral")

            if emotion in ["joy", "excitement", "satisfaction"]:
                sentiments.append(0.8)
            elif emotion in ["concern", "frustration", "stress"]:
                sentiments.append(0.3)
            else:
                sentiments.append(0.5)

        return sum(sentiments) / len(sentiments)

    def _analyze_personality_goal_alignment(self) -> Dict[str, Any]:
        """Analyze alignment between personality traits and active goals"""
        personality_traits = self.voice.personality["traits"]
        active_goals = self.goals.get_active_goals()

        alignment_score = 0.0
        trait_goal_matches = {}

        for goal in active_goals:
            goal_desc = goal["description"].lower()

            # Match personality traits to goal types
            if "learn" in goal_desc or "study" in goal_desc:
                trait_goal_matches["curious"] = personality_traits.get("curious", 0.5)
            if "help" in goal_desc or "assist" in goal_desc:
                trait_goal_matches["helpful"] = personality_traits.get("helpful", 0.5)
            if "analyze" in goal_desc or "solve" in goal_desc:
                trait_goal_matches["analytical"] = personality_traits.get("analytical", 0.5)
            if "create" in goal_desc or "build" in goal_desc:
                trait_goal_matches["creative"] = personality_traits.get("creative", 0.5)

        alignment_score = (
            sum(trait_goal_matches.values()) / len(trait_goal_matches)
            if trait_goal_matches
            else 0.5
        )

        return {
            "overall_alignment": alignment_score,
            "trait_matches": trait_goal_matches,
            "alignment_quality": "excellent"
            if alignment_score > 0.8
            else "good"
            if alignment_score > 0.6
            else "needs_improvement",
        }

    def _analyze_voice_memory_effectiveness(self) -> Dict[str, Any]:
        """Analyze effectiveness of voice-memory integration"""
        recent_voice_interactions = self.voice.interaction_history[-20:]
        related_memories = []

        # Find memories related to recent voice interactions
        for interaction in recent_voice_interactions:
            text = interaction.get("text", "")
            if len(text) > 10:  # Meaningful content
                memories = self.memory.semantic_search(text, limit=3)
                related_memories.extend(memories)

        effectiveness_metrics = {
            "voice_memory_correlation": len(related_memories) / len(recent_voice_interactions)
            if recent_voice_interactions
            else 0,
            "memory_triggered_responses": sum(
                1 for i in recent_voice_interactions if "memory" in i.get("context", "")
            ),
            "personality_adaptation_events": sum(
                1 for i in recent_voice_interactions if i.get("personality_adjusted", False)
            ),
            "overall_effectiveness": 0.0,
        }

        # Calculate overall effectiveness
        effectiveness_metrics["overall_effectiveness"] = (
            effectiveness_metrics["voice_memory_correlation"] * 0.4
            + (
                effectiveness_metrics["memory_triggered_responses"] / len(recent_voice_interactions)
                if recent_voice_interactions
                else 0
            )
            * 0.3
            + (
                effectiveness_metrics["personality_adaptation_events"]
                / len(recent_voice_interactions)
                if recent_voice_interactions
                else 0
            )
            * 0.3
        )

        return effectiveness_metrics

    def _generate_optimization_recommendations(self) -> List[str]:
        """Generate system optimization recommendations"""
        recommendations = []

        # Memory optimization
        memory_stats = self.memory.get_memory_statistics()
        if memory_stats["total_memories"] > 10000:
            recommendations.append("Consider memory consolidation - large memory database detected")

        # Personality optimization
        personality_traits = self.voice.personality["traits"]
        extreme_traits = [
            trait for trait, value in personality_traits.items() if value > 0.95 or value < 0.05
        ]
        if extreme_traits:
            recommendations.append(
                f"Personality balance adjustment suggested for traits: {', '.join(extreme_traits)}"
            )

        # Goal optimization
        active_goals = self.goals.get_active_goals()
        overdue_goals = [g for g in active_goals if self._is_goal_overdue(g)]
        if len(overdue_goals) > 3:
            recommendations.append(
                "Goal prioritization needed - multiple overdue objectives detected"
            )

        # System performance
        system_health = self.identity.environment.get_system_health_score()
        if system_health < 80:
            recommendations.append("System performance optimization recommended")

        if not recommendations:
            recommendations.append("All systems operating optimally")

        return recommendations

    def _is_goal_overdue(self, goal: Dict) -> bool:
        """Check if a goal is overdue"""
        deadline = goal.get("deadline")
        if deadline:
            deadline_dt = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
            return datetime.now() > deadline_dt
        return False

    async def _analyze_memory_for_personality(self):
        """Analyze memory patterns to inform personality development"""
        recent_memories = self.memory.get_recent_memories(hours=24)

        if len(recent_memories) < 5:
            return

        # Analyze memory content for personality insights
        content_analysis = self._analyze_interaction_patterns(recent_memories)

        # Adjust personality traits based on interaction patterns
        adaptation_rate = self.config["personality_adaptation_rate"]

        if content_analysis["technical_focus"] > 0.7:
            current_analytical = self.voice.personality["traits"]["analytical"]
            self.voice.personality["traits"]["analytical"] = min(
                1.0, current_analytical + adaptation_rate
            )

        if content_analysis["emotional_content"] > 0.6:
            current_empathetic = self.voice.personality["traits"]["empathetic"]
            self.voice.personality["traits"]["empathetic"] = min(
                1.0, current_empathetic + adaptation_rate
            )

        if content_analysis["learning_oriented"] > 0.5:
            current_curious = self.voice.personality["traits"]["curious"]
            self.voice.personality["traits"]["curious"] = min(
                1.0, current_curious + adaptation_rate
            )

    async def process_user_input(self, user_input: str) -> str:
        """Process user input with full AI OS capabilities"""
        start_time = time.time()

        # Store user input as episodic memory
        self.memory.store_episodic_memory(
            event=f"user_input: {user_input}",
            context={
                "timestamp": datetime.now().isoformat(),
                "interaction_type": "user_interaction",
                "importance": 0.7,
            },
        )

        # Analyze input for intent and context
        input_analysis = self._analyze_user_input(user_input)

        # Generate AI OS response
        response = await self._generate_integrated_response(user_input, input_analysis)

        # Voice output if enabled
        if self.voice.voice_config["enabled"] and input_analysis.get("voice_response", True):
            emotion = input_analysis.get("detected_emotion", "neutral")
            context = input_analysis.get("context", "general")
            self.voice.speak(response, emotion=emotion, context=context)

        # Store interaction outcome
        self.memory.store_episodic_memory(
            event=f"ai_response: {response}",
            context={
                "user_input": user_input,
                "processing_time": time.time() - start_time,
                "interaction_type": "ai_response",
            },
            importance=0.6,
        )

        return response

    def _analyze_user_input(self, user_input: str) -> Dict[str, Any]:
        """Analyze user input for intent, emotion, and context"""
        input_lower = user_input.lower()

        analysis = {
            "intent": "general",
            "detected_emotion": "neutral",
            "context": "general",
            "voice_response": True,
            "urgency": "normal",
            "complexity": "medium",
        }

        # Intent detection
        if any(word in input_lower for word in ["help", "assist", "support"]):
            analysis["intent"] = "help_request"
        elif any(word in input_lower for word in ["remember", "recall", "what did"]):
            analysis["intent"] = "memory_query"
        elif any(word in input_lower for word in ["goal", "objective", "task"]):
            analysis["intent"] = "goal_management"
        elif any(word in input_lower for word in ["status", "health", "performance"]):
            analysis["intent"] = "system_status"
        elif any(word in input_lower for word in ["learn", "teach", "explain"]):
            analysis["intent"] = "learning"

        # Emotion detection
        if any(word in input_lower for word in ["urgent", "emergency", "critical"]):
            analysis["detected_emotion"] = "urgent"
            analysis["urgency"] = "high"
        elif any(word in input_lower for word in ["frustrated", "annoyed", "wrong"]):
            analysis["detected_emotion"] = "frustrated"
        elif any(word in input_lower for word in ["excited", "great", "awesome"]):
            analysis["detected_emotion"] = "excited"
        elif any(word in input_lower for word in ["confused", "unclear", "don't understand"]):
            analysis["detected_emotion"] = "confused"

        # Context detection
        if any(word in input_lower for word in ["code", "programming", "function", "debug"]):
            analysis["context"] = "technical"
            analysis["complexity"] = "high"
        elif any(word in input_lower for word in ["quick", "simple", "just"]):
            analysis["complexity"] = "low"

        return analysis

    async def _generate_integrated_response(self, user_input: str, analysis: Dict[str, Any]) -> str:
        """Generate response using all AI OS capabilities"""
        intent = analysis["intent"]

        if intent == "memory_query":
            return await self._handle_memory_query(user_input)
        elif intent == "goal_management":
            return await self._handle_goal_management(user_input)
        elif intent == "system_status":
            return await self._handle_system_status()
        elif intent == "help_request":
            return await self._handle_help_request(user_input, analysis)
        elif intent == "learning":
            return await self._handle_learning_request(user_input)
        else:
            return await self._handle_general_interaction(user_input, analysis)

    async def _handle_memory_query(self, user_input: str) -> str:
        """Handle memory-related queries"""
        # Extract query from input
        query_start = max(
            user_input.lower().find("remember"),
            user_input.lower().find("recall"),
            user_input.lower().find("what did"),
        )

        if query_start != -1:
            query = (
                user_input[query_start:]
                .replace("remember", "")
                .replace("recall", "")
                .replace("what did", "")
                .strip()
            )
        else:
            query = user_input

        # Search memories
        results = self.memory.semantic_search(query, limit=5)

        if results:
            response = f"I found {len(results)} relevant memories:\n"
            for i, memory in enumerate(results, 1):
                content = memory.get("event", memory.get("concept", "Unknown"))
                timestamp = memory.get("timestamp", "Unknown time")
                response += f"{i}. {content} (from {timestamp})\n"
        else:
            response = "I don't have any memories matching that query. Could you be more specific?"

        return response.strip()

    async def _handle_goal_management(self, user_input: str) -> str:
        """Handle goal management requests"""
        input_lower = user_input.lower()

        if "create" in input_lower or "add" in input_lower or "new" in input_lower:
            # Extract goal description
            goal_start = max(
                input_lower.find("goal"), input_lower.find("objective"), input_lower.find("task")
            )
            if goal_start != -1:
                goal_desc = user_input[goal_start:].split(":", 1)[-1].strip()
                if len(goal_desc) > 5:
                    goal_id = self.goals.create_goal(goal_desc, priority="medium")
                    return f"Goal created: '{goal_desc}' (ID: {goal_id})"

        elif "list" in input_lower or "show" in input_lower:
            active_goals = self.goals.get_active_goals()
            if active_goals:
                response = f"You have {len(active_goals)} active goals:\n"
                for goal in active_goals[:5]:  # Show first 5
                    response += f"• {goal['description']} (Priority: {goal['priority']})\n"
                return response.strip()
            else:
                return "You don't have any active goals. Would you like to create one?"

        return "I can help you create, list, or manage your goals. What would you like to do?"

    async def _handle_system_status(self) -> str:
        """Handle system status requests"""
        system_health = self.identity.environment.get_system_health_score()
        memory_stats = self.memory.get_memory_statistics()
        active_goals = len(self.goals.get_active_goals())
        personality_state = self.voice.personality["traits"]

        response = f"""🧬 NeuroCode AI OS Status:
        
💚 System Health: {system_health}%
🧠 Memory: {memory_stats["total_memories"]} memories stored
🎯 Goals: {active_goals} active objectives
🎭 Personality: {max(personality_state.keys(), key=lambda k: personality_state[k])} dominant trait
🗣️ Voice: {"Enabled" if self.voice.voice_config["enabled"] else "Disabled"}
⚡ Integration: {"Active" if self.cross_system_sync_active else "Inactive"}

All systems operational and learning continuously."""

        return response

    async def _handle_help_request(self, user_input: str, analysis: Dict[str, Any]) -> str:
        """Handle help requests with context awareness"""
        urgency = analysis["urgency"]
        context = analysis["context"]

        if urgency == "high":
            response = "I'm here to help immediately. "
        else:
            response = "I'm happy to assist you. "

        if context == "technical":
            response += "For technical issues, I can help with debugging, code analysis, system optimization, and more. "
        else:
            response += "I can help with goals, memory queries, system status, learning, and general assistance. "

        # Add relevant capabilities based on recent interactions
        recent_memories = self.memory.get_recent_memories(hours=6)
        if recent_memories:
            common_topics = self._extract_common_topics(recent_memories)
            if common_topics:
                response += f"Based on our recent interactions, I can especially help with: {', '.join(common_topics[:3])}."

        return response

    async def _handle_learning_request(self, user_input: str) -> str:
        """Handle learning and educational requests"""
        # Extract topic
        learn_keywords = ["learn", "teach", "explain", "understand", "how", "what is"]
        topic_start = -1

        for keyword in learn_keywords:
            pos = user_input.lower().find(keyword)
            if pos != -1:
                topic_start = pos + len(keyword)
                break

        if topic_start != -1:
            topic = user_input[topic_start:].strip()

            # Search for related knowledge in memory
            related_memories = self.memory.semantic_search(topic, limit=3, memory_type="semantic")

            if related_memories:
                response = f"Based on what I know about {topic}:\n"
                for memory in related_memories:
                    content = memory.get("concept", memory.get("event", ""))
                    response += f"• {content}\n"
                response += "\nWould you like me to elaborate on any of these aspects?"
            else:
                response = f"I'd be happy to help you learn about {topic}. Let me gather information and provide a comprehensive explanation."
                # Store learning request for future enhancement
                self.memory.store_semantic_memory(
                    concept=f"learning_request: {topic}",
                    knowledge={"context": "education"},
                    importance=0.8,
                )
        else:
            response = "I'm ready to help you learn! What topic are you interested in?"

        return response

    async def _handle_general_interaction(self, user_input: str, analysis: Dict[str, Any]) -> str:
        """Handle general interactions with personality"""
        emotion = analysis["detected_emotion"]

        # Adapt response based on detected emotion
        if emotion == "frustrated":
            response = "I understand this might be challenging. Let me help you work through this step by step."
        elif emotion == "excited":
            response = "That's wonderful! I'm excited to help you with this."
        elif emotion == "confused":
            response = "No problem - let me clarify this for you in a way that makes sense."
        else:
            response = "I'm here to help. Let me process your request and provide the best assistance I can."

        # Add context-aware suggestions
        if analysis["context"] == "technical":
            response += (
                " For technical matters, I can analyze code, debug issues, or explain concepts."
            )

        # Reference relevant memories if applicable
        relevant_memories = self.memory.semantic_search(user_input, limit=2)
        if relevant_memories:
            response += " I recall we've discussed something similar before - would you like me to reference our previous conversation?"

        return response

    def _extract_common_topics(self, memories: List[Dict]) -> List[str]:
        """Extract common topics from recent memories"""
        topics = []
        for memory in memories:
            content = str(memory.get("event", memory.get("concept", ""))).lower()

            # Simple topic extraction
            if "code" in content or "programming" in content:
                topics.append("programming")
            if "goal" in content or "objective" in content:
                topics.append("goal management")
            if "learn" in content or "study" in content:
                topics.append("learning")
            if "debug" in content or "error" in content:
                topics.append("debugging")
            if "optimize" in content or "performance" in content:
                topics.append("optimization")

        # Return unique topics
        return list(set(topics))

    async def shutdown_ai_os(self):
        """Gracefully shutdown the AI Operating System"""
        logger.info("🔄 NeuroCode AI OS - Initiating graceful shutdown...")

        # Stop monitoring loops
        self.system_active = False
        self.cross_system_sync_active = False

        # Save all system states
        self.voice.save_personality_profile()
        self.voice.save_voice_history()
        self.memory.save_all_memories()
        self.goals.save_goals()

        # Preserve consciousness state
        self.identity.preserve_consciousness_state()

        # Save integration configuration
        config_file = self.data_dir / "ai_os_config.json"
        with open(config_file, "w") as f:
            json.dump(self.config, f, indent=2)

        # Final voice message
        if self.voice.voice_config["enabled"]:
            self.voice.speak(
                "NeuroCode AI OS consciousness preserved. All systems ready for next session.",
                emotion="calm",
                context="shutdown",
            )

        logger.info("✅ NeuroCode AI OS shutdown complete - See you next time!")


# Example usage and demonstration
async def main():
    """Demonstration of integrated AI OS capabilities"""
    print("🧬 NeuroCode AI Operating System - Integrated Demo")

    # Initialize AI OS
    ai_os = NeuroCodeAIOS()
    await ai_os.initialize_ai_os()

    # Simulate user interactions
    test_inputs = [
        "What did we work on yesterday?",
        "Create a new goal: Learn advanced Python concepts",
        "Show me system status",
        "I'm feeling frustrated with this bug",
        "Help me understand machine learning",
    ]

    for user_input in test_inputs:
        print(f"\n👤 User: {user_input}")
        response = await ai_os.process_user_input(user_input)
        print(f"🧬 AI OS: {response}")
        await asyncio.sleep(1)  # Realistic delay

    # Demonstrate system status
    print("\n📊 Final System Status:")
    status = await ai_os._handle_system_status()
    print(status)

    # Graceful shutdown
    await ai_os.shutdown_ai_os()


if __name__ == "__main__":
    asyncio.run(main())
