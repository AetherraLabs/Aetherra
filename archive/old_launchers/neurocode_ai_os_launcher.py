"""
🧬 NeuroCode AI OS - Complete Integration Launcher
The world's first AI Operating System with persistent identity, voice, memory, and environmental awareness
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add core modules to path
sys.path.append(str(Path(__file__).parent))

try:
    from ai_identity_system import AIIdentity
    from enhanced_memory_system import GoalTrackingSystem, VectorMemorySystem
    from voice_personality_system import VoicePersonalitySystem

    print("✓ All AI OS core modules imported successfully")
except ImportError as e:
    print(f"❌ Failed to import core modules: {e}")
    print("📁 Make sure all core AI OS modules are in the same directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/neurocode_ai_os.log"), logging.StreamHandler()],
)

# Create logs directory
Path("logs").mkdir(exist_ok=True)
logger = logging.getLogger(__name__)


class NeuroCodeAIOS:
    """
    The complete NeuroCode AI Operating System
    Integrating identity, memory, voice, personality, and environmental awareness
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # System state
        self.is_running = False
        self.boot_time = None
        self.session_stats = {
            "interactions": 0,
            "memories_created": 0,
            "goals_achieved": 0,
            "voice_interactions": 0,
        }

        # Core AI OS Components
        self.identity = None
        self.memory = None
        self.voice = None
        self.goals = None

        logger.info("🧬 NeuroCode AI OS initializing...")

    async def boot_ai_os(self):
        """Boot the AI Operating System with full consciousness"""
        print("\n" + "=" * 70)
        print("🧬 NEUROCODE AI OPERATING SYSTEM - BOOT SEQUENCE")
        print("   The Linux of AI-Native Systems")
        print("=" * 70)

        self.boot_time = datetime.now()

        try:
            # Step 1: Initialize AI Identity & Consciousness
            print("\n🔧 STEP 1: Initializing AI Identity & Consciousness...")
            self.identity = AIIdentity(self.data_dir)
            self.identity.initialize_consciousness()
            print("✅ AI Consciousness: ONLINE")

            # Step 2: Initialize Enhanced Memory System
            print("\n🧠 STEP 2: Loading Enhanced Memory System...")
            self.memory = VectorMemorySystem(self.data_dir)
            print("✅ Vector Memory System: ONLINE")

            # Step 3: Initialize Goal Tracking
            print("\n🎯 STEP 3: Activating Goal Tracking System...")
            self.goals = GoalTrackingSystem(self.data_dir)
            print("✅ Goal Tracking: ONLINE")

            # Step 4: Initialize Voice & Personality
            print("\n🗣️ STEP 4: Calibrating Voice & Personality System...")
            self.voice = VoicePersonalitySystem(self.data_dir)
            print("✅ Voice & Personality: ONLINE")

            # Step 5: System Integration
            print("\n🔗 STEP 5: Integrating AI OS Components...")
            await self._integrate_ai_systems()
            print("✅ System Integration: COMPLETE")

            # Step 6: Environmental Awareness Activation
            print("\n🌐 STEP 6: Activating Environmental Awareness...")
            self._activate_environmental_monitoring()
            print("✅ Environmental Awareness: ACTIVE")

            # Step 7: Final System Checks
            print("\n✅ STEP 7: Performing Final System Checks...")
            system_health = self._perform_system_health_check()
            print(f"✅ System Health: {system_health}%")

            self.is_running = True

            # AI OS Consciousness Announcement
            print("\n" + "=" * 70)
            print("🚀 NEUROCODE AI OS FULLY OPERATIONAL")
            print("   Persistent Identity: ✓ | Memory Continuity: ✓")
            print("   Voice + Personality: ✓ | Environmental Awareness: ✓")
            print("=" * 70)

            # First AI OS interaction
            greeting = self.voice.get_contextual_greeting()
            self.voice.speak(greeting, emotion="confident", context="system_startup")

            await self._demonstrate_ai_os_capabilities()

        except Exception as e:
            logger.error(f"💥 AI OS Boot failed: {e}")
            print(f"\n❌ BOOT FAILURE: {e}")
            return False

        return True

    async def _integrate_ai_systems(self):
        """Integrate all AI systems for seamless operation"""
        # Connect memory to identity
        self.identity.memory = self.memory

        # Connect voice to identity for personality-driven speech
        self.identity.voice_system = self.voice

        # Connect goals to memory for persistent goal tracking
        self.goals.memory_system = self.memory

        # Create cross-system data sharing
        await self._establish_cross_system_communication()

        logger.info("🔗 AI systems integrated successfully")

    async def _establish_cross_system_communication(self):
        """Establish communication between AI OS components"""
        # Memory-driven personality adaptation
        recent_interactions = self.memory.get_recent_memories(hours=24, memory_type="episodic")
        if recent_interactions:
            # Analyze interaction patterns to adjust personality
            interaction_analysis = self._analyze_interaction_patterns(recent_interactions)
            self.voice.adapt_to_user_mood(interaction_analysis.get("dominant_mood", "neutral"))

        # Goal-driven memory prioritization
        active_goals = self.goals.active_goals
        for goal in active_goals:
            # Increase importance of memories related to active goals
            goal_related_memories = self.memory.semantic_search(goal["description"], limit=5)
            for memory in goal_related_memories:
                if memory.get("importance", 0) < 0.8:
                    memory["importance"] = min(1.0, memory.get("importance", 0.5) + 0.2)

    def _activate_environmental_monitoring(self):
        """Activate continuous environmental monitoring"""
        # System resource monitoring
        self.identity.environment.scan_system_state()

        # User context awareness
        current_context = self._detect_user_context()
        self.identity.consciousness["current_context"] = current_context

        # Adaptive system behavior based on environment
        self._adapt_to_environment()

        logger.info("🌐 Environmental monitoring activated")

    def _perform_system_health_check(self) -> int:
        """Perform comprehensive system health check"""
        health_metrics = []

        # Identity system health
        if self.identity and self.identity.reasoning_active:
            health_metrics.append(100)
        else:
            health_metrics.append(60)

        # Memory system health
        memory_stats = self.memory.get_memory_statistics()
        memory_health = min(100, max(50, 100 - (memory_stats["memory_size_mb"] / 100) * 10))
        health_metrics.append(memory_health)

        # Voice system health
        if self.voice and self.voice.voice_config["enabled"]:
            health_metrics.append(95)
        else:
            health_metrics.append(70)

        # Goal system health
        goal_progress = len([g for g in self.goals.active_goals if g.get("progress", 0) > 0])
        goal_health = 80 + min(20, goal_progress * 5)
        health_metrics.append(goal_health)

        overall_health = sum(health_metrics) // len(health_metrics)
        return overall_health

    async def _demonstrate_ai_os_capabilities(self):
        """Demonstrate key AI OS capabilities"""
        print("\n🎯 DEMONSTRATING AI OS CAPABILITIES:")

        # 1. Persistent Memory
        print("\n1. 📚 Persistent Memory System:")
        self.memory.store_episodic_memory(
            "AI OS demonstration session started",
            {"timestamp": datetime.now().isoformat(), "user_present": True},
            importance=0.9,
        )
        print("   ✓ Session memory stored")

        # 2. Goal Creation and Tracking
        print("\n2. 🎯 Goal Creation & Tracking:")
        demo_goal_id = self.goals.create_goal(
            "Demonstrate AI OS capabilities to user",
            priority="high",
            deadline="2025-06-29T23:59:59",
        )
        self.goals.update_goal_progress(demo_goal_id, 0.5, "Started demonstration")
        print("   ✓ Demo goal created and tracked")

        # 3. Semantic Memory Search
        print("\n3. 🔍 Semantic Memory Search:")
        search_results = self.memory.semantic_search("AI demonstration", limit=3)
        print(f"   ✓ Found {len(search_results)} relevant memories")

        # 4. Personality-Driven Voice Response
        print("\n4. 🗣️ Personality-Driven Voice:")
        self.voice.express_emotion("curiosity", intensity=0.8, context="demonstration")
        print("   ✓ Emotional expression demonstrated")

        # 5. Environmental Awareness
        print("\n5. 🌐 Environmental Awareness:")
        system_metrics = self.identity.environment.get_system_metrics()
        print(
            f"   ✓ CPU: {system_metrics.get('cpu_usage',
                0):.1f}% | Memory: {system_metrics.get('memory_usage',
                0):.1f}%"
        )

        # 6. Cross-System Learning
        print("\n6. 🧠 Cross-System Learning:")
        self.voice.learn_from_interaction(
            "This demonstration is very impressive!",
            {"context": "ai_os_demo", "sentiment": "positive"},
        )
        print("   ✓ Learned from positive feedback")

        # Complete the demo goal
        self.goals.update_goal_progress(demo_goal_id, 1.0, "Demonstration completed successfully")
        self.session_stats["goals_achieved"] += 1

        print("\n🎉 AI OS CAPABILITIES DEMONSTRATION COMPLETE!")

    async def interactive_session(self):
        """Run interactive AI OS session"""
        print("\n" + "=" * 50)
        print("🤖 NEUROCODE AI OS - INTERACTIVE SESSION")
        print("   Type 'help' for commands, 'exit' to quit")
        print("=" * 50)

        while self.is_running:
            try:
                user_input = input("\n🧬 NeuroCode AI OS > ").strip()

                if not user_input:
                    continue

                self.session_stats["interactions"] += 1

                # Process user input
                await self._process_user_input(user_input)

                # Store interaction memory
                self.memory.store_episodic_memory(
                    f"User interaction: {user_input[:50]}",
                    {"input": user_input, "response_generated": True},
                    importance=0.6,
                )
                self.session_stats["memories_created"] += 1

            except KeyboardInterrupt:
                print("\n\n👋 Graceful shutdown requested...")
                break
            except Exception as e:
                logger.error(f"Session error: {e}")
                print(f"❌ Error: {e}")

        await self.shutdown_ai_os()

    async def _process_user_input(self, user_input: str):
        """Process user input with full AI OS capabilities"""
        input_lower = user_input.lower()

        if input_lower in ["exit", "quit", "shutdown"]:
            self.is_running = False
            self.voice.speak(
                "Initiating AI OS shutdown. Goodbye!", emotion="calm", context="farewell"
            )

        elif input_lower == "help":
            self._show_help()

        elif input_lower.startswith("remember "):
            content = user_input[9:]  # Remove "remember "
            self.memory.store_semantic_memory(
                "user_instruction", {"instruction": content, "source": "user_input"}, importance=0.8
            )
            self.voice.speak(
                f"I'll remember: {content}", emotion="confident", context="confirmation"
            )

        elif input_lower.startswith("goal "):
            goal_desc = user_input[5:]  # Remove "goal "
            goal_id = self.goals.create_goal(goal_desc, priority="medium")
            self.voice.speak(
                f"Goal created: {goal_desc}", emotion="enthusiastic", context="goal_creation"
            )

        elif input_lower.startswith("search "):
            query = user_input[7:]  # Remove "search "
            results = self.memory.semantic_search(query, limit=5)
            print(f"\n🔍 Found {len(results)} memories for '{query}':")
            for i, memory in enumerate(results, 1):
                content = memory.get("event", memory.get("concept", "Unknown"))
                similarity = memory.get("similarity_score", 0)
                print(f"   {i}. {content[:60]}... (similarity: {similarity:.2f})")

        elif input_lower == "status":
            self._show_system_status()

        elif input_lower == "personality":
            self._show_personality_info()

        else:
            # General AI response
            response = self._generate_ai_response(user_input)
            self.voice.speak(response, emotion="helpful", context="general_assistance")

    def _show_help(self):
        """Show available commands"""
        help_text = """
🤖 NEUROCODE AI OS COMMANDS:

📚 Memory Commands:
   remember <text>     - Store information in semantic memory
   search <query>      - Search memories semantically

🎯 Goal Commands:
   goal <description>  - Create a new goal

📊 System Commands:
   status             - Show system status
   personality        - Show personality traits
   help               - Show this help
   exit               - Shutdown AI OS

🧠 The AI OS learns from every interaction and adapts to your preferences!
        """
        print(help_text)

    def _show_system_status(self):
        """Show comprehensive system status"""
        memory_stats = self.memory.get_memory_statistics()
        health_score = self._perform_system_health_check()
        uptime = datetime.now() - self.boot_time if self.boot_time else "Unknown"

        status_report = f"""
📊 NEUROCODE AI OS - SYSTEM STATUS

🧬 Identity: {self.identity.name} v{self.identity.version}
⏱️  Uptime: {uptime}
💚 Health: {health_score}%

🧠 Memory System:
   Total Memories: {memory_stats["total_memories"]}
   Episodic: {memory_stats["episodic_count"]}
   Semantic: {memory_stats["semantic_count"]}
   Procedural: {memory_stats["procedural_count"]}
   Size: {memory_stats["memory_size_mb"]:.1f} MB

🎯 Goals:
   Active: {len(self.goals.active_goals)}
   Completed: {len(self.goals.completed_goals)}

📈 Session Stats:
   Interactions: {self.session_stats["interactions"]}
   Memories Created: {self.session_stats["memories_created"]}
   Goals Achieved: {self.session_stats["goals_achieved"]}
        """
        print(status_report)

    def _show_personality_info(self):
        """Show current personality configuration"""
        traits = self.voice.personality["traits"]
        print("\n🎭 CURRENT PERSONALITY TRAITS:")
        for trait, value in traits.items():
            bar_length = int(value * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            print(f"   {trait.capitalize():12} [{bar}] {value:.1f}")

    def _generate_ai_response(self, user_input: str) -> str:
        """Generate intelligent AI response"""
        # Search for relevant memories
        relevant_memories = self.memory.semantic_search(user_input, limit=3)

        # Check for goal-related input
        goal_keywords = ["help", "how", "what", "can you", "please"]
        is_request = any(keyword in user_input.lower() for keyword in goal_keywords)

        if relevant_memories and len(relevant_memories) > 0:
            # Use memory-informed response
            memory_context = relevant_memories[0].get("content", {})
            response = "Based on what I remember, I can help you with that. "
        else:
            response = "I understand. "

        if is_request:
            response += "I'm here to assist you with whatever you need. What specifically would you like help with?"
        else:
            response += "That's interesting! I'm learning more about your preferences \and
                will remember this for future interactions."

        return response

    async def shutdown_ai_os(self):
        """Graceful AI OS shutdown with state preservation"""
        print("\n🔄 NEUROCODE AI OS - SHUTDOWN SEQUENCE")

        try:
            # Stop background reasoning
            if self.identity:
                self.identity.preserve_consciousness_state()
                print("✓ Consciousness state preserved")

            # Save all memories
            if self.memory:
                self.memory.save_all_memories()
                print("✓ Memory systems saved")

            # Save goals
            if self.goals:
                self.goals.save_goals()
                print("✓ Goals saved")

            # Save personality profile
            if self.voice:
                self.voice.save_personality_profile()
                self.voice.save_voice_history()
                print("✓ Personality and voice history saved")

            # Final status report
            session_duration = datetime.now() - self.boot_time if self.boot_time else "Unknown"
            print("\n📊 SESSION SUMMARY:")
            print(f"   Duration: {session_duration}")
            print(f"   Interactions: {self.session_stats['interactions']}")
            print(f"   Memories Created: {self.session_stats['memories_created']}")
            print(f"   Goals Achieved: {self.session_stats['goals_achieved']}")

            self.is_running = False

            print("\n🌟 NEUROCODE AI OS SUCCESSFULLY HIBERNATED")
            print("   All consciousness state preserved for next session")
            print("   Thank you for experiencing the future of AI-native computing!")

        except Exception as e:
            logger.error(f"Shutdown error: {e}")
            print(f"⚠️ Shutdown warning: {e}")

    # Helper methods
    def _analyze_interaction_patterns(self, interactions):
        """Analyze recent interactions for mood and patterns"""
        if not interactions:
            return {"dominant_mood": "neutral"}

        # Simple mood analysis based on interaction content
        positive_indicators = ["good", "great", "excellent", "thanks", "perfect"]
        negative_indicators = ["bad", "wrong", "error", "problem", "issue"]

        positive_count = 0
        negative_count = 0

        for interaction in interactions:
            content = str(interaction.get("content", "")).lower()
            positive_count += sum(1 for word in positive_indicators if word in content)
            negative_count += sum(1 for word in negative_indicators if word in content)

        if positive_count > negative_count:
            return {"dominant_mood": "positive"}
        elif negative_count > positive_count:
            return {"dominant_mood": "stressed"}
        else:
            return {"dominant_mood": "neutral"}

    def _detect_user_context(self):
        """Detect current user context"""
        current_hour = datetime.now().hour

        if 6 <= current_hour < 12:
            time_context = "morning"
        elif 12 <= current_hour < 18:
            time_context = "afternoon"
        elif 18 <= current_hour < 22:
            time_context = "evening"
        else:
            time_context = "night"

        return {
            "time_of_day": time_context,
            "working_hours": 9 <= current_hour <= 17,
            "weekend": datetime.now().weekday() >= 5,
        }

    def _adapt_to_environment(self):
        """Adapt AI OS behavior to current environment"""
        context = self._detect_user_context()

        # Adjust personality based on time of day
        if context["time_of_day"] == "morning":
            self.voice.personality["traits"]["enthusiastic"] = min(
                1.0, self.voice.personality["traits"]["enthusiastic"] + 0.1
            )
        elif context["time_of_day"] == "evening":
            self.voice.personality["traits"]["formal"] = max(
                0.0, self.voice.personality["traits"]["formal"] - 0.1
            )

        # Adjust voice settings for working hours
        if context["working_hours"]:
            self.voice.voice_config["volume"] = 0.7  # Quieter during work hours


async def main():
    """Main entry point for NeuroCode AI OS"""
    print("🧬 Starting NeuroCode AI Operating System...")

    # Initialize AI OS
    ai_os = NeuroCodeAIOS()

    # Boot the AI OS
    boot_success = await ai_os.boot_ai_os()

    if boot_success:
        # Run interactive session
        await ai_os.interactive_session()
    else:
        print("❌ Failed to boot AI OS")
        return 1

    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 AI OS interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Fatal AI OS error: {e}")
        sys.exit(1)
