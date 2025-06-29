#!/usr/bin/env python3
"""
NeuroCode Enhancement Integration
Integrates new AI capabilities with existing interpreter
"""

import os
import sys
import time
from typing import Any, Dict

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))


# Enhanced model selection strategy
class AIModelRouter:
    """Intelligent AI model selection and routing"""

    def __init__(self):
        self.model_capabilities = {
            "gpt-4": {
                "strengths": ["complex_reasoning", "code_generation", "architecture_design"],
                "speed": "medium",
                "cost": "high",
                "privacy": "cloud",
            },
            "claude-3": {
                "strengths": ["detailed_analysis", "documentation", "refactoring"],
                "speed": "medium",
                "cost": "medium",
                "privacy": "cloud",
            },
            "ollama_llama": {
                "strengths": ["fast_completion", "code_analysis", "local_processing"],
                "speed": "fast",
                "cost": "free",
                "privacy": "local",
            },
            "ollama_codellama": {
                "strengths": ["code_generation", "debugging", "local_processing"],
                "speed": "fast",
                "cost": "free",
                "privacy": "local",
            },
        }

    def select_best_model(
        self, task_type: str, privacy_required: bool = False, speed_priority: bool = False
    ) -> str:
        """Select the optimal AI model for a specific task"""

        # Privacy-first selection
        if privacy_required:
            local_models = {
                k: v for k, v in self.model_capabilities.items() if v["privacy"] == "local"
            }
            if not local_models:
                return "ollama_llama"  # Default local fallback

            # Choose best local model for task
            for model, caps in local_models.items():
                if task_type in caps["strengths"]:
                    return model
            return "ollama_llama"

        # Speed-first selection
        if speed_priority:
            fast_models = {k: v for k, v in self.model_capabilities.items() if v["speed"] == "fast"}
            for model, caps in fast_models.items():
                if task_type in caps["strengths"]:
                    return model
            return "ollama_llama"

        # Quality-first selection (default)
        task_models = []
        for model, caps in self.model_capabilities.items():
            if task_type in caps["strengths"]:
                task_models.append((model, caps))

        if not task_models:
            return "gpt-4"  # Default high-quality fallback

        # Prefer cloud models for complex tasks, local for simple ones
        complex_tasks = ["complex_reasoning", "architecture_design"]
        if task_type in complex_tasks:
            cloud_models = [m for m, c in task_models if c["privacy"] == "cloud"]
            return cloud_models[0] if cloud_models else task_models[0][0]
        else:
            return task_models[0][0]


try:
    # Try relative imports first (when run as module)
    try:
        from .ai_collaboration import AICollaborationFramework
        from .ai_runtime import ask_ai
        from .intent_parser import IntentToCodeParser, parse_natural_intent
        from .interpreter import NeuroCodeInterpreter
        from .local_ai import LocalAIEngine, local_analyze_code, local_ask_ai
        from .performance_optimizer import PerformanceOptimizer
        from .vector_memory import EnhancedSemanticMemory
    except ImportError:
        # Fallback to direct imports (when run from parent directory)
        from ai_collaboration import AICollaborationFramework
        from ai_runtime import ask_ai
        from intent_parser import IntentToCodeParser, parse_natural_intent
        from interpreter import NeuroCodeInterpreter
        from local_ai import LocalAIEngine, local_analyze_code, local_ask_ai
        from performance_optimizer import PerformanceOptimizer
        from vector_memory import EnhancedSemanticMemory

    ENHANCEMENTS_AVAILABLE = True
    print("✅ All enhancement modules loaded successfully")

except ImportError as e:
    print(f"⚠️  Some enhancement modules not available: {e}")
    ENHANCEMENTS_AVAILABLE = False


class EnhancedNeuroCodeInterpreter:
    """
    Enhanced NeuroCode Interpreter with next-generation AI capabilities
    """

    def __init__(self):
        # Initialize model router
        self.model_router = AIModelRouter()

        # Initialize core interpreter
        self.core_interpreter = NeuroCodeInterpreter()

        # Initialize enhancement modules if available
        if ENHANCEMENTS_AVAILABLE:
            self.local_ai = LocalAIEngine()
            self.vector_memory = EnhancedSemanticMemory("enhanced_memory.json")
            self.intent_parser = IntentToCodeParser()
            self.performance_optimizer = PerformanceOptimizer()
            self.ai_collaboration = AICollaborationFramework()
            print("🚀 Enhanced NeuroCode Interpreter initialized with AI capabilities")
        else:
            self.local_ai = None
            self.vector_memory = None
            self.intent_parser = None
            self.performance_optimizer = None
            self.ai_collaboration = None
            print("⚠️  Running with basic interpreter only")

        # Performance metrics
        self.performance_metrics = {
            "commands_processed": 0,
            "ai_queries": 0,
            "intent_translations": 0,
            "semantic_recalls": 0,
            "optimizations_applied": 0,
            "collaborative_tasks": 0,
        }

    def execute_neurocode(self, code: str) -> str:
        """Execute NeuroCode with enhanced AI capabilities"""
        self.performance_metrics["commands_processed"] += 1

        # Check if this looks like natural language intent
        if self._is_natural_language(code):
            return self._handle_natural_language_intent(code)

        # Check for enhanced commands
        if code.strip().startswith("intent:"):
            return self._handle_intent_command(code)
        elif code.strip().startswith("ai:"):
            return self._handle_ai_command(code)
        elif code.strip().startswith("semantic_recall"):
            return self._handle_semantic_recall(code)
        elif code.strip().startswith("analyze_patterns"):
            return self._handle_pattern_analysis(code)
        elif code.strip().startswith("local_ai"):
            return self._handle_local_ai_command(code)
        elif code.strip().startswith("optimize"):
            return self._handle_optimization_command(code)
        elif code.strip().startswith("collaborate"):
            return self._handle_collaboration_command(code)
        elif code.strip().startswith("performance"):
            return self._handle_performance_command(code)

        # Fall back to core interpreter
        return self.core_interpreter.execute(code)

    def _is_natural_language(self, code: str) -> bool:
        """Detect if input is natural language rather than NeuroCode syntax"""
        if not self.intent_parser:
            return False

        # Simple heuristics for natural language detection
        natural_indicators = [
            len(code.split()) > 5,  # More than 5 words
            any(
                word in code.lower()
                for word in [
                    "create",
                    "build",
                    "make",
                    "develop",
                    "implement",
                    "process",
                    "analyze",
                    "optimize",
                    "monitor",
                    "i want",
                    "i need",
                    "can you",
                    "please",
                ]
            ),
            not any(char in code for char in [":", "=", "def", "class", "import"]),
        ]

        return sum(natural_indicators) >= 2

    def _handle_natural_language_intent(self, natural_description: str) -> str:
        """Handle natural language input by converting to NeuroCode"""
        if not self.intent_parser:
            return "[Enhancement] Intent parser not available. Please use NeuroCode syntax."

        try:
            self.performance_metrics["intent_translations"] += 1

            # Parse natural language to NeuroCode
            parsed_intent = parse_natural_intent(natural_description)

            # Store the translation in memory
            if self.vector_memory:
                self.vector_memory.remember(
                    f"Translated intent: {natural_description} -> {parsed_intent.intent_type.value}",
                    tags=["translation", "intent", "natural_language"],
                    category="ai_assistance",
                )

            # Execute the generated NeuroCode
            result = self.core_interpreter.execute(parsed_intent.generated_code)

            return f"""🧠 Intent Translation Complete!

Original Request: {natural_description}

Intent Type: {parsed_intent.intent_type.value}
Confidence: {parsed_intent.confidence:.2f}

Generated NeuroCode:
{parsed_intent.generated_code[:300]}...

Execution Result:
{result}

💡 Explanation:
{parsed_intent.explanation[:200]}..."""

        except Exception as e:
            return f"[Enhancement Error] Intent translation failed: {e}"

    def _handle_intent_command(self, code: str) -> str:
        """Handle explicit intent: commands"""
        if not self.intent_parser:
            return "[Enhancement] Intent parser not available"

        # Extract intent description
        intent_description = code[7:].strip()  # Remove "intent:"

        try:
            parsed_intent = parse_natural_intent(intent_description)
            return f"""Intent Parsed Successfully!

Type: {parsed_intent.intent_type.value}
Goal: {parsed_intent.primary_goal}
Constraints: {parsed_intent.constraints}
Technologies: {parsed_intent.technologies}
Confidence: {parsed_intent.confidence:.2f}

Generated NeuroCode:
{parsed_intent.generated_code}"""

        except Exception as e:
            return f"[Intent Error] {e}"

    def _handle_ai_command(self, code: str) -> str:
        """Handle AI commands with local AI support"""
        query = code[3:].strip()  # Remove "ai:"
        self.performance_metrics["ai_queries"] += 1

        if self.local_ai:
            # Try local AI first
            local_response = local_ask_ai(query)
            if "[LocalAI]" not in local_response:
                # Store successful AI interaction
                if self.vector_memory:
                    self.vector_memory.remember(
                        f"AI Query: {query} -> {local_response[:100]}...",
                        tags=["ai_interaction", "local_ai"],
                        category="ai_assistance",
                    )
                return f"🤖 [Local AI] {local_response}"

        # Fall back to OpenAI
        try:
            openai_response = ask_ai(query)
            return f"🌐 [OpenAI] {openai_response}"
        except Exception as e:
            return f"[AI Error] {e}"

    def _handle_semantic_recall(self, code: str) -> str:
        """Handle semantic memory recall"""
        if not self.vector_memory:
            return "[Enhancement] Vector memory not available"

        # Extract query
        query = code.replace("semantic_recall", "").strip()
        if not query:
            return "[Error] No query provided for semantic recall"

        try:
            self.performance_metrics["semantic_recalls"] += 1
            results = self.vector_memory.semantic_recall(query, limit=5)

            if not results:
                return f"No memories found for query: {query}"

            response = f"🧠 Semantic Recall Results for: {query}\n\n"
            for i, result in enumerate(results, 1):
                response += f"{i}. Similarity: {result['similarity']:.3f}\n"
                response += f"   Content: {result['content'][:100]}...\n"
                response += f"   Tags: {result['tags']}\n\n"

            return response

        except Exception as e:
            return f"[Semantic Recall Error] {e}"

    def _handle_pattern_analysis(self, code: str) -> str:
        """Handle pattern analysis of memories"""
        if not self.vector_memory:
            return "[Enhancement] Vector memory not available"

        try:
            patterns = self.vector_memory.find_patterns()
            insights = self.vector_memory.get_memory_insights()

            response = "🔍 Memory Pattern Analysis\n\n"
            response += f"Total Memories: {insights['total_memories']}\n"
            response += f"Unique Tags: {insights['unique_tags']}\n"
            response += f"Unique Categories: {insights['unique_categories']}\n\n"

            response += "🎯 Discovered Patterns:\n"
            for i, pattern in enumerate(patterns["patterns"][:3], 1):
                response += f"{i}. {pattern['theme']} (size: {pattern['size']})\n"

            response += f"\n📊 Most Common Tags: {insights['most_common_tags'][:3]}\n"
            response += f"📊 Most Common Categories: {insights['most_common_categories'][:3]}\n"

            return response

        except Exception as e:
            return f"[Pattern Analysis Error] {e}"

    def _handle_local_ai_command(self, code: str) -> str:
        """Handle local AI specific commands"""
        if not self.local_ai:
            return "[Enhancement] Local AI not available"

        command = code.replace("local_ai", "").strip()

        if command == "status":
            status = self.local_ai.get_model_status()
            response = "🤖 Local AI Status\n\n"
            response += f"Available Models: {status['available_models']}\n"
            response += f"Best Model: {status['best_model']}\n"
            response += f"Embeddings Available: {status['embedding_available']}\n"
            return response

        elif command.startswith("analyze"):
            # Extract code to analyze
            code_to_analyze = command.replace("analyze", "").strip()
            if not code_to_analyze:
                return "[Error] No code provided for analysis"

            analysis = local_analyze_code(code_to_analyze)
            return f"🔍 Local AI Code Analysis:\n{analysis}"

        else:
            return "[Error] Unknown local AI command. Available: status, analyze <code>"

    def _handle_optimization_command(self, code: str) -> str:
        """Handle performance optimization commands"""
        if not self.performance_optimizer:
            return "[Enhancement] Performance optimizer not available"

        command = code.replace("optimize", "").strip()
        self.performance_metrics["optimizations_applied"] += 1

        if command == "status":
            metrics = self.performance_optimizer.get_performance_report()
            response = "⚡ Performance Optimization Status\n\n"
            response += f"Commands monitored: {len(metrics.get('commands', {}))}\n"
            response += f"Optimization suggestions: {len(metrics.get('suggestions', {}))}\n"
            response += f"Average execution time: {metrics.get('avg_execution_time', 0):.3f}s\n"
            return response

        elif command.startswith("analyze"):
            # Get recent performance data
            report = self.performance_optimizer.get_performance_report()

            response = "📊 Performance Analysis\n\n"
            if 'suggestions' in report and report['suggestions']:
                response += "🔧 Recent Optimization Suggestions:\n"
                for suggestion in list(report['suggestions'].values())[:3]:  # Top 3 suggestions
                    response += f"• Command: {suggestion['command']}\n"
                    response += f"  Suggestion: {suggestion['suggested_optimization']}\n"
            else:
                response += "✅ No performance issues detected\n"

            return response

        elif command.startswith("profile"):
            # Start performance profiling
            code_to_profile = command.replace("profile", "").strip()
            if not code_to_profile:
                return "[Error] No code provided for profiling"

            # Profile the code execution
            start_time = time.time()
            try:
                result = self.core_interpreter.execute(code_to_profile)
                execution_time = time.time() - start_time

                # Record metrics using the correct method
                self.performance_optimizer.profile_execution(
                    command=code_to_profile,
                    execution_time=execution_time,
                    memory_usage=None,  # Will be auto-detected
                    context={"result_length": len(str(result))}
                )

                return f"⏱️ Profiled execution in {execution_time:.3f}s\nResult: {result}"
            except Exception as e:
                return f"[Profile Error] {e}"

        else:
            return "[Error] Unknown optimization command. Available: status, analyze, profile <code>"

    def _handle_collaboration_command(self, code: str) -> str:
        """Handle AI collaboration commands"""
        if not self.ai_collaboration:
            return "[Enhancement] AI collaboration not available"

        command = code.replace("collaborate", "").strip()
        self.performance_metrics["collaborative_tasks"] += 1

        if command == "status":
            stats = self.ai_collaboration.get_collaboration_stats()
            response = "🤝 AI Collaboration Status\n\n"
            response += f"Active tasks: {stats.get('active_tasks', 0)}\n"
            response += f"Total collaborations: {stats.get('total_collaborations', 0)}\n"
            response += f"Available agents: {stats.get('available_agents', 0)}\n"
            response += f"Success rate: {stats.get('success_rate', 0)}%\n"
            return response

        elif command.startswith("task"):
            # Create a collaborative task
            task_description = command.replace("task", "").strip()
            if not task_description:
                return "[Error] No task description provided"

            # Use async wrapper for collaborative solving
            import asyncio
            try:
                result = asyncio.run(self.ai_collaboration.quick_solve(task_description))
                return f"🚀 Collaborative solution:\n{result}"
            except Exception as e:
                return f"[Collaboration Error] {e}"

        elif command.startswith("agents"):
            # List available agents
            agents = self.ai_collaboration.get_agent_capabilities()
            response = "🤖 Available AI Agents\n\n"
            for agent_role, capabilities in agents.items():
                response += f"• {agent_role}: {', '.join(capabilities)}\n"
            return response

        else:
            return "[Error] Unknown collaboration command. Available: status, task <description>, agents"

    def _handle_performance_command(self, code: str) -> str:
        """Handle performance monitoring commands"""
        if not self.performance_optimizer:
            return "[Enhancement] Performance monitoring not available"

        command = code.replace("performance", "").strip()

        if command == "report":
            metrics = self.performance_metrics
            response = "📈 Performance Report\n\n"
            response += f"Commands processed: {metrics['commands_processed']}\n"
            response += f"AI queries: {metrics['ai_queries']}\n"
            response += f"Intent translations: {metrics['intent_translations']}\n"
            response += f"Semantic recalls: {metrics['semantic_recalls']}\n"
            response += f"Optimizations applied: {metrics['optimizations_applied']}\n"
            response += f"Collaborative tasks: {metrics['collaborative_tasks']}\n"
            return response

        elif command == "benchmark":
            # Run a quick benchmark
            import time
            start_time = time.time()

            # Test basic operations
            for i in range(100):
                self.core_interpreter.execute(f"set test_var_{i} = {i}")

            benchmark_time = time.time() - start_time
            return f"⚡ Benchmark completed in {benchmark_time:.3f}s (100 operations)"

        else:
            return "[Error] Unknown performance command. Available: report, benchmark"

    def get_enhancement_status(self) -> Dict[str, Any]:
        """Get status of all enhancements"""
        return {
            "enhancements_available": ENHANCEMENTS_AVAILABLE,
            "performance_metrics": self.performance_metrics,
            "modules": {
                "local_ai": self.local_ai is not None,
                "vector_memory": self.vector_memory is not None,
                "intent_parser": self.intent_parser is not None,
                "performance_optimizer": self.performance_optimizer is not None,
                "ai_collaboration": self.ai_collaboration is not None,
            }
        }

    def demonstrate_enhancements(self) -> str:
        """Demonstrate available enhancements"""
        demo = "🚀 NeuroCode Enhanced Features Demo\n\n"

        if not ENHANCEMENTS_AVAILABLE:
            return demo + "⚠️  No enhancements available - basic interpreter only"

        demo += "Available Enhancement Commands:\n\n"
        demo += "🧠 Natural Language:\n"
        demo += "  'Create a simple calculator function'\n"
        demo += "  'Build a data processing pipeline'\n\n"

        demo += "⚡ Performance Optimization:\n"
        demo += "  optimize status - View optimization status\n"
        demo += "  optimize analyze - Get performance analysis\n"
        demo += "  optimize profile <code> - Profile code execution\n\n"

        demo += "🤝 AI Collaboration:\n"
        demo += "  collaborate status - View collaboration status\n"
        demo += "  collaborate task <description> - Create collaborative task\n"
        demo += "  collaborate agents - List available AI agents\n\n"

        demo += "🎯 Intent Commands:\n"
        demo += "  intent: build a web scraper\n"
        demo += "  intent: optimize database queries\n\n"

        demo += "🔍 AI Analysis:\n"
        demo += "  ai: analyze this code for bugs\n"
        demo += "  local_ai status - Check local AI status\n\n"

        demo += "🧠 Semantic Memory:\n"
        demo += "  semantic_recall machine learning\n"
        demo += "  analyze_patterns recent code\n\n"

        demo += "📊 Performance Monitoring:\n"
        demo += "  performance report - Get performance report\n"
        demo += "  performance benchmark - Run benchmark test\n"

        return demo


def create_enhanced_interpreter():
    """Factory function to create enhanced interpreter"""
    return EnhancedNeuroCodeInterpreter()


def test_enhancements():
    """Test enhancement integrations"""
    interpreter = create_enhanced_interpreter()
    print("🧪 Testing enhancements...")

    # Test status
    status = interpreter.get_enhancement_status()
    print(f"✅ Enhancements available: {status['enhancements_available']}")

    return True


if __name__ == "__main__":
    # Run enhancement tests
    test_enhancements()

    # Interactive mode
    print("\n🚀 Enhanced NeuroCode Interactive Mode")
    print("Type 'demo' to see capabilities, 'quit' to exit")

    interpreter = create_enhanced_interpreter()

    while True:
        try:
            user_input = input("\nNeuroCode> ").strip()

            if user_input.lower() in ["quit", "exit"]:
                break
            elif user_input.lower() == "demo":
                print(interpreter.demonstrate_enhancements())
            elif user_input.lower() == "status":
                status = interpreter.get_enhancement_status()
                print(f"Enhanced features available: {status['enhancements_available']}")
                print(f"Commands processed: {status['performance_metrics']['commands_processed']}")
            elif user_input:
                result = interpreter.execute_neurocode(user_input)
                print(result)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! NeuroCode enhancements ready for the future!")
            break
