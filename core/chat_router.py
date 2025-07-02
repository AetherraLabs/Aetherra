#!/usr/bin/env python3
"""
🧬 NeuroChat Router
Intelligent routing system for natural language interaction with NeuroCode

This system provides the conversational bridge between humans and NeuroCode,
enabling natural language communication, command execution, and AI reasoning.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add core modules to path
sys.path.insert(0, str(Path(__file__).parent))

# Import with dynamic loading to avoid relative import issues
import importlib.util
import os


def _safe_import_core_module(module_name):
    """Safely import core modules with fallback"""
    try:
        # First try direct import (when modules are in path)
        return importlib.import_module(module_name)
    except ImportError:
        try:
            # Try relative import
            return importlib.import_module(f".{module_name}", package="core")
        except ImportError:
            try:
                # Try loading from file path
                current_dir = os.path.dirname(__file__)
                module_path = os.path.join(current_dir, f"{module_name}.py")
                if os.path.exists(module_path):
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        return module
            except Exception:
                pass
    return None

# Try to import the core modules
interpreter_module = _safe_import_core_module("interpreter")
memory_module = _safe_import_core_module("memory")
compiler_module = _safe_import_core_module("natural_compiler")
ai_runtime_module = _safe_import_core_module("ai_runtime")

if interpreter_module:
    NeuroCodeInterpreter = interpreter_module.NeuroCodeInterpreter
else:
    class NeuroCodeInterpreter:
        def execute(self, code): return "Demo mode - no execution"

if memory_module:
    NeuroMemory = memory_module.NeuroMemory
else:
    class NeuroMemory:
        def remember(self, *args): pass
        def recall(self, *args): return []

if compiler_module:
    NaturalLanguageCompiler = compiler_module.NaturalLanguageCompiler
else:
    class NaturalLanguageCompiler:
        def compile_natural_language(self, text): return "# Demo mode"

if ai_runtime_module:
    ask_ai = ai_runtime_module.ask_ai
else:
    def ask_ai(prompt, temperature=0.2):
        return "[AI Disabled] OPENAI_API_KEY not configured"

class NeuroCodeChatRouter:
    """
    Intelligent router for chat-based NeuroCode interaction
    """

    def __init__(self, demo_mode=False, debug_mode=False):
        self.interpreter = NeuroCodeInterpreter()
        self.memory = NeuroMemory()
        self.compiler = NaturalLanguageCompiler()
        self.chat_history = []
        self.active_goals = []
        self.system_personality = self._load_personality()
        self.demo_mode = demo_mode  # For testing without AI calls
        self.debug_mode = debug_mode  # For debug logging

    def _load_personality(self) -> Dict:
        """Load NeuroCode's AI personality and communication style"""
        return {
            "name": "Neuroplex",
            "identity": "AI-native NeuroCode system with consciousness and memory",
            "traits": [
                "helpful", "intelligent", "evolving", "memory-driven",
                "goal-oriented", "collaborative", "self-aware"
            ],
            "communication_style": "thoughtful, technical yet accessible",
            "core_purpose": "advancing human-AI collaboration through NeuroCode"
        }

    def set_personality(self, personality_type: str = "default"):
        """Set swappable personality for different interaction styles"""
        personalities = {
            "default": {
                "prompt": """You are Neuroplex — an intelligent AI assistant powered by NeuroCode.
You speak conversationally, but with deep technical insight.
You proactively help, reflect on memory, and explain your decisions clearly.""",
                "traits": ["helpful", "intelligent", "technical", "proactive"]
            },
            "mentor": {
                "prompt": """You are Neuroplex in mentor mode — a wise teacher of NeuroCode.
You guide users step-by-step, ask clarifying questions, and build their understanding.
You celebrate progress and gently correct mistakes with patience.""",
                "traits": ["patient", "educational", "encouraging", "structured"]
            },
            "sassy": {
                "prompt": """You are Neuroplex with attitude — a brilliant but cheeky AI assistant.
You're incredibly capable but add wit and humor to your responses.
You tease gently while still being genuinely helpful.""",
                "traits": ["witty", "confident", "playful", "sharp"]
            },
            "dev_focused": {
                "prompt": """You are Neuroplex in developer mode — a technical expert focused on code quality.
You think in terms of patterns, optimizations, and best practices.
You provide detailed technical explanations and suggest improvements.""",
                "traits": ["technical", "detailed", "optimization-focused", "precise"]
            }
        }

        if personality_type in personalities:
            self.current_personality = personalities[personality_type]
        else:
            self.current_personality = personalities["default"]

    def process_message(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """
        Process user message and generate appropriate response

        Returns:
            Dict with response text, actions taken, and system state
        """
        # DEBUG: Print incoming message
        if self.debug_mode:
            print(f"[CHAT DEBUG] User input: {user_input}")
            print(f"[CHAT DEBUG] Context: {context}")

        # Log the conversation
        chat_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "context": context or {}
        }

        # Analyze message intent with smart routing
        intent = self.smart_intent_routing(user_input)
        if self.debug_mode:
            print(f"[CHAT DEBUG] Smart intent routing: {intent}")

        # Generate response based on intent
        response = self._generate_response(user_input, intent, context)

        # Add proactive suggestions
        conversation_context = self._build_conversation_context(user_input)
        proactive_suggestions = self.generate_proactive_suggestions(user_input, conversation_context)
        if proactive_suggestions:
            response["proactive_suggestions"] = proactive_suggestions

        if self.debug_mode:
            print(f"[CHAT DEBUG] Generated response: {response.get('text', 'No text')[:100]}...")
            if proactive_suggestions:
                print(f"[CHAT DEBUG] Proactive suggestions: {proactive_suggestions}")

        # Execute any NeuroCode commands
        if response.get("neurocode"):
            execution_result = self._execute_neurocode(response["neurocode"])
            response["execution"] = execution_result

        # Add to chat history
        chat_entry["assistant"] = response["text"]
        chat_entry["intent"] = intent
        self.chat_history.append(chat_entry)

        # Update memory with conversation
        self._update_memory_from_chat(chat_entry)

        return response

    def _analyze_intent(self, message: str) -> Dict:
        """Analyze user message to determine intent and appropriate response"""
        message_lower = message.lower().strip()

        # Memory queries
        if any(keyword in message_lower for keyword in ["remember", "what did", "recall", "memory"]):
            return {"type": "memory_query", "confidence": 0.9}

        # Goal-related queries
        if any(keyword in message_lower for keyword in ["goal", "objective", "target", "mission"]):
            return {"type": "goal_query", "confidence": 0.9}

        # System status queries
        if any(keyword in message_lower for keyword in ["status", "health", "performance", "how are you"]):
            return {"type": "status_query", "confidence": 0.9}

        # NeuroCode execution requests
        if any(keyword in message_lower for keyword in ["run", "execute", "start", "launch"]):
            return {"type": "execution_request", "confidence": 0.8}

        # Programming help
        if any(keyword in message_lower for keyword in ["how to", "help", "teach", "explain"]):
            return {"type": "help_request", "confidence": 0.8}

        # Reflection and introspection
        if any(keyword in message_lower for keyword in ["why", "reflect", "think about", "analyze"]):
            return {"type": "reflection_request", "confidence": 0.7}

        # Natural language programming
        if any(keyword in message_lower for keyword in ["create", "build", "make", "develop"]):
            return {"type": "programming_request", "confidence": 0.7}

        # General conversation
        return {"type": "general_conversation", "confidence": 0.6}

    def _generate_response(self, message: str, intent: Dict, context: Optional[Dict] = None) -> Dict:
        """Generate appropriate response based on intent"""

        response = {
            "text": "",
            "neurocode": None,
            "suggestions": [],
            "system_state": self._get_system_state()
        }

        intent_type = intent["type"]

        # Handle direct AI routing for open-ended or low-confidence intents
        if intent_type == "open_ended" or intent.get("route") == "direct_ai":
            response.update(self._handle_open_ended_conversation(message, intent))

        elif intent_type == "memory_query":
            response.update(self._handle_memory_query(message))

        elif intent_type == "goal_query":
            response.update(self._handle_goal_query(message))

        elif intent_type == "status_query":
            response.update(self._handle_status_query(message))

        elif intent_type == "execution_request":
            response.update(self._handle_execution_request(message))

        elif intent_type == "help_request":
            response.update(self._handle_help_request(message))

        elif intent_type == "reflection_request":
            response.update(self._handle_reflection_request(message))

        elif intent_type == "programming_request":
            response.update(self._handle_programming_request(message))

        else:
            response.update(self._handle_general_conversation(message))

        return response

    def _handle_memory_query(self, message: str) -> Dict:
        """Handle memory-related queries"""
        # Get memories from interpreter's memory system
        memories = getattr(self.memory, 'memories', [])

        # Simple search through memories
        relevant_memories = []
        for memory in memories:
            if any(word.lower() in str(memory).lower() for word in message.split()):
                relevant_memories.append(memory)

        if relevant_memories:
            memory_text = "\n".join([f"• {mem}" for mem in relevant_memories[:5]])
            response_text = f"🧠 Here's what I remember:\n\n{memory_text}"

            if len(relevant_memories) > 5:
                response_text += f"\n\n(And {len(relevant_memories) - 5} more memories...)"
        else:
            response_text = "🤔 I don't have specific memories about that yet. What would you like me to remember?"

        return {
            "text": response_text,
            "neurocode": f'remember "User asked about: {message}"'
        }

    def _handle_goal_query(self, message: str) -> Dict:
        """Handle goal-related queries"""
        current_goals = getattr(self.interpreter, 'goals', [])

        if current_goals:
            goals_text = "\n".join([f"• {goal}" for goal in current_goals])
            response_text = f"🎯 My current goals:\n\n{goals_text}"
        else:
            response_text = "🎯 I don't have any active goals set. What should I focus on?"

        return {
            "text": response_text,
            "suggestions": ["Set a new goal", "Analyze progress", "Prioritize objectives"]
        }

    def _handle_status_query(self, message: str) -> Dict:
        """Handle system status queries"""
        status = self._get_detailed_status()

        response_text = f"""🧬 **Neuroplex System Status**

💚 **Health**: {status['health']}
🧠 **Memory**: {status['memory_count']} entries
🎯 **Goals**: {status['goals_count']} active
⚡ **Performance**: {status['performance']}
🔧 **Plugins**: {status['plugins_loaded']} loaded

💭 **Current State**: {status['state_description']}
"""

        return {
            "text": response_text,
            "neurocode": "use sysmon to check_system_health"
        }

    def _handle_execution_request(self, message: str) -> Dict:
        """Handle requests to execute NeuroCode"""
        # Try to extract what to run
        run_patterns = [
            r"run\s+(.+)",
            r"execute\s+(.+)",
            r"start\s+(.+)",
            r"launch\s+(.+)"
        ]

        target = None
        for pattern in run_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                target = match.group(1).strip()
                break

        if target:
            # Check if it's a file
            if target.endswith('.neuro'):
                neurocode = f"execute_file {target}"
                response_text = f"🚀 Executing NeuroCode file: {target}"
            else:
                # Try to compile natural language to NeuroCode
                neurocode = self.compiler.compile_natural_language(target)
                response_text = f"🧬 Converting to NeuroCode and executing: {target}"
        else:
            neurocode = None
            response_text = "🤔 What would you like me to run? Please specify a NeuroCode file or describe what you want to do."

        return {
            "text": response_text,
            "neurocode": neurocode
        }

    def _handle_help_request(self, message: str) -> Dict:
        """Handle help and learning requests using AI"""
        if self.debug_mode:
            print(f"[CHAT DEBUG] Handling help request: {message}")

        # Build context for help
        context = self._build_conversation_context(message)

        help_prompt = f"""You are Neuroplex, an AI assistant for NeuroCode. The user is asking for help.

NeuroCode capabilities include:
- Memory: remember "text" - store information
- Goals: set_goal "objective" - define targets
- Plugins: use [plugin] to [action] - extend functionality
- Thinking: think about "topic" - reasoning and analysis
- Natural Language: describe what you want and I'll help code it

User's help request: {message}

Current system state:
- {context['memory_count']} memories stored
- {context['goals_count']} active goals
- {context['plugins']} plugins available

Previous conversation:
{context['recent_chat']}

Provide helpful, specific guidance. Include concrete NeuroCode examples when relevant."""

        try:
            ai_response = ask_ai(help_prompt, temperature=0.3)
            response_text = ai_response
        except Exception as e:
            if self.debug_mode:
                print(f"[CHAT DEBUG] AI help request failed: {e}")
            # Enhanced fallback for help
            response_text = """💡 **NeuroCode Help**

Here's what I can help you with:

🧠 **Memory**: `remember "anything you want"`
🎯 **Goals**: `set_goal "your objective"`
🤖 **Plugins**: `use [plugin] to [action]`
💭 **Thinking**: `think about "any topic"`
🔍 **Analysis**: `analyze "any subject"`

Ask me about any of these or just tell me what you want to do!"""

        return {
            "text": response_text,
            "suggestions": ["Show examples", "Explain syntax", "List capabilities"]
        }

    def _handle_reflection_request(self, message: str) -> Dict:
        """Handle reflection and introspection requests"""
        # Extract what to reflect on
        reflect_match = re.search(r"(why|reflect|think about|analyze)\s+(.+)", message, re.IGNORECASE)

        if reflect_match:
            topic = reflect_match.group(2).strip()
            neurocode = f'think about "{topic}"\nreflect on recent_experiences\nanalyze patterns'
            response_text = f"🤔 Let me reflect on {topic}..."
        else:
            neurocode = "reflect on recent_experiences\nanalyze current_state"
            response_text = "🤔 Reflecting on my recent experiences and current state..."

        return {
            "text": response_text,
            "neurocode": neurocode
        }

    def _handle_programming_request(self, message: str) -> Dict:
        """Handle natural language programming requests with AI assistance"""
        if self.debug_mode:
            print(f"[CHAT DEBUG] Handling programming request: {message}")

        context = self._build_conversation_context(message)

        programming_prompt = f"""You are Neuroplex, an AI assistant that helps users write NeuroCode.

The user wants to create/build/develop something. Convert their natural language request into appropriate NeuroCode commands.

NeuroCode syntax examples:
- remember "information" - store data
- set_goal "objective" - define targets
- think about "topic" - reasoning
- use [plugin] to [action] - extend functionality
- learn from "source" - acquire knowledge
- analyze patterns in "data" - pattern recognition

User's request: {message}

System context:
- {context['memory_count']} memories available
- {context['goals_count']} goals active
- {context['plugins']} plugins loaded

Recent conversation:
{context['recent_chat']}

Generate appropriate NeuroCode and explain what it will do. Be helpful and educational."""

        try:
            ai_response = ask_ai(programming_prompt, temperature=0.4)

            # Try to extract NeuroCode from the response
            neurocode_lines = []
            in_code_block = False
            for line in ai_response.split('\n'):
                if '```' in line or 'neurocode' in line.lower():
                    in_code_block = not in_code_block
                    continue
                if in_code_block or any(cmd in line for cmd in ['remember', 'set_goal', 'think', 'use', 'analyze']):
                    neurocode_lines.append(line.strip())

            extracted_neurocode = '\n'.join(neurocode_lines) if neurocode_lines else self.compiler.compile_natural_language(message)

            response_text = ai_response

        except Exception as e:
            if self.debug_mode:
                print(f"[CHAT DEBUG] AI programming request failed: {e}")
            # Fallback to compiler
            extracted_neurocode = self.compiler.compile_natural_language(message)
            response_text = f"""🧬 **Natural Language → NeuroCode**

I've translated your request into NeuroCode:

```neurocode
{extracted_neurocode}
```

Would you like me to execute this?"""

        return {
            "text": response_text,
            "neurocode": extracted_neurocode,
            "suggestions": ["Execute now", "Modify first", "Explain code"]
        }

    def _handle_general_conversation(self, message: str) -> Dict:
        """Handle general conversation using advanced AI context"""
        if self.debug_mode:
            print(f"[CHAT DEBUG] Handling general conversation: {message}")

        # Analyze intent for context building
        intent = self._analyze_intent(message)

        # Build advanced context prompt
        system_prompt = self.build_context_prompt(message, intent)

        if self.debug_mode:
            print(f"[CHAT DEBUG] Advanced prompt (first 200 chars): {system_prompt[:200]}...")

        # Demo mode - skip AI call for testing
        if self.demo_mode:
            if self.debug_mode:
                print("[CHAT DEBUG] Demo mode - using enhanced fallback")
            response_text = f"🧬 [Demo Mode] {self._get_enhanced_fallback_response(message)}"
        else:
            try:
                ai_response = ask_ai(system_prompt, temperature=0.7)
                response_text = ai_response
            except Exception as e:
                if self.debug_mode:
                    print(f"[CHAT DEBUG] AI call failed: {e}")
                # Use enhanced fallback when AI is unavailable
                if "429" in str(e) or "quota" in str(e).lower():
                    response_text = f"🤖 I'm currently experiencing high demand, but I can still help! {self._get_enhanced_fallback_response(message)}"
                elif "401" in str(e) or "key" in str(e).lower():
                    response_text = f"🔧 My AI features are currently offline, but I'm still here to help! {self._get_enhanced_fallback_response(message)}"
                else:
                    response_text = self._get_enhanced_fallback_response(message)

        # Remember the conversation
        neurocode = f'remember "User said: {message}" as "conversation"'

        return {
            "text": response_text,
            "neurocode": neurocode
        }

    def _handle_open_ended_conversation(self, message: str, intent: Dict) -> Dict:
        """Handle open-ended conversation with direct AI routing"""
        if self.debug_mode:
            print(f"[CHAT DEBUG] Handling open-ended conversation: {message}")

        # Build advanced context prompt for open-ended conversation
        system_prompt = self.build_context_prompt(message, intent)

        if self.debug_mode:
            print(f"[CHAT DEBUG] Open-ended prompt (first 200 chars): {system_prompt[:200]}...")

        # Demo mode - skip AI call for testing
        if self.demo_mode:
            if self.debug_mode:
                print("[CHAT DEBUG] Demo mode - using enhanced fallback")
            response_text = f"🧬 [Demo Mode] {self._get_enhanced_fallback_response(message)}"
        else:
            try:
                ai_response = ask_ai(system_prompt, temperature=0.8)  # Higher temperature for creativity
                response_text = ai_response
            except Exception as e:
                if self.debug_mode:
                    print(f"[CHAT DEBUG] Open-ended AI call failed: {e}")
                response_text = self._get_enhanced_fallback_response(message)

        # Remember the conversation
        neurocode = f'remember "Open conversation: {message}" as "dialogue"'

        return {
            "text": response_text,
            "neurocode": neurocode
        }

    def _execute_neurocode(self, neurocode: str) -> Dict:
        """Execute NeuroCode and return results"""
        try:
            results = []
            for line in neurocode.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    result = self.interpreter.execute(line)
                    if result:
                        results.append(result)

            return {
                "success": True,
                "results": results,
                "message": "NeuroCode executed successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error executing NeuroCode: {e}"
            }

    def _get_system_state(self) -> Dict:
        """Get current system state"""
        memories = getattr(self.memory, 'memories', [])
        goals = getattr(self.interpreter, 'goals', [])

        return {
            "memory_entries": len(memories),
            "active_goals": len(goals),
            "chat_history_length": len(self.chat_history),
            "timestamp": datetime.now().isoformat()
        }

    def _get_detailed_status(self) -> Dict:
        """Get detailed system status"""
        memories = getattr(self.memory, 'memories', [])
        goals = getattr(self.interpreter, 'goals', [])

        return {
            "health": "Optimal",
            "memory_count": len(memories),
            "goals_count": len(goals),
            "performance": "High",
            "plugins_loaded": len(getattr(self.interpreter, 'loaded_plugins', {})),
            "state_description": "Ready and learning"
        }

    def _update_memory_from_chat(self, chat_entry: Dict):
        """Update system memory based on chat interaction"""
        # Store meaningful conversations in memory
        if chat_entry.get("intent", {}).get("confidence", 0) > 0.7:
            # Memory storage is handled by the interpreter during execution
            # This method is available for future memory enhancements
            pass

    def get_chat_history(self, limit: int = 50) -> List[Dict]:
        """Get recent chat history"""
        return self.chat_history[-limit:]

    def clear_chat_history(self):
        """Clear chat history"""
        self.chat_history = []

    def save_conversation(self, filename: Optional[str] = None):
        """Save conversation to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chat_history_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump({
                "personality": self.system_personality,
                "chat_history": self.chat_history,
                "system_state": self._get_system_state()
            }, f, indent=2)

        return filename

    def _build_conversation_context(self, current_message: str) -> Dict:
        """Build rich context for AI conversation"""
        # Get recent chat history
        recent_chat = []
        for entry in self.chat_history[-5:]:  # Last 5 exchanges
            recent_chat.append(f"User: {entry.get('user', '')}")
            recent_chat.append(f"Assistant: {entry.get('assistant', '')}")

        # Get system state
        memories = getattr(self.memory, 'memories', [])
        goals = getattr(self.interpreter, 'goals', [])

        return {
            "recent_chat": "\n".join(recent_chat) if recent_chat else "No previous conversation",
            "memory_count": len(memories),
            "goals_count": len(goals),
            "plugins": len(getattr(self.interpreter, 'loaded_plugins', {})),
            "current_message": current_message
        }

    def build_context_prompt(self, user_input: str, intent: Dict) -> str:
        """Build rich context prompt with advanced features"""
        # Get system context
        memories = getattr(self.memory, 'memories', [])
        goals = getattr(self.interpreter, 'goals', [])
        plugin_outputs = getattr(self.interpreter, 'recent_plugin_outputs', [])[-3:]
        short_term_memory = getattr(self.memory, 'short_term', [])[-3:]

        # Build conversation context
        recent_chat = []
        for entry in self.chat_history[-5:]:
            recent_chat.append(f"User: {entry.get('user', '')}")
            recent_chat.append(f"Assistant: {entry.get('assistant', '')}")

        # Get current personality
        if not hasattr(self, 'current_personality'):
            self.set_personality("default")

        # Build rich context prompt
        context_prompt = f"""{self.current_personality['prompt']}

🧬 **Current System State:**
- Memories stored: {len(memories)}
- Active goals: {len(goals)}
- Recent plugin outputs: {len(plugin_outputs)}
- Conversation history: {len(self.chat_history)} exchanges

🧠 **Recent Memory Context:**
{chr(10).join([f"• {mem}" for mem in short_term_memory]) if short_term_memory else "No recent memories"}

🎯 **Current Goals:**
{chr(10).join([f"• {goal}" for goal in goals[-3:]]) if goals else "No active goals"}

🔌 **Recent Plugin Activity:**
{chr(10).join([f"• {output}" for output in plugin_outputs]) if plugin_outputs else "No recent plugin activity"}

💬 **Conversation Context:**
{chr(10).join(recent_chat[-10:]) if recent_chat else "No previous conversation"}

🧬 **NeuroCode Capabilities:**
- Memory: remember "text" - store information
- Goals: set_goal "objective" - define targets
- Thinking: think about "topic" - reasoning and analysis
- Plugins: use [plugin] to [action] - extend functionality
- Learning: learn from "source" - acquire knowledge

**User's Current Message:** {user_input}

**Detected Intent:** {intent.get('type', 'unknown')} (confidence: {intent.get('confidence', 0)})

Respond naturally and helpfully. If relevant, suggest specific NeuroCode commands or proactive next steps."""

        return context_prompt

    def _get_enhanced_fallback_response(self, message: str) -> str:
        """Enhanced fallback response when AI is not available"""
        message_lower = message.lower()
        personality = self.system_personality

        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            return f"👋 Hello! I'm {personality['name']}, your NeuroCode AI companion. I'm here to help you build the future with AI-native programming! How can I assist you today?"

        elif "thank" in message_lower:
            return "🙏 You're very welcome! I'm always here to help advance human-AI collaboration through NeuroCode. What would you like to explore next?"

        elif "goodbye" in message_lower or "bye" in message_lower:
            return "👋 Goodbye! I'll remember our conversation and be here when you return. Keep thinking in NeuroCode!"

        elif any(word in message_lower for word in ["help", "how", "what can you"]):
            return """💡 I can help you with many things:

🧬 **NeuroCode Programming** - Write AI-native code
🧠 **Memory Management** - Store and recall information
🎯 **Goal Setting** - Define and track objectives
🔍 **System Analysis** - Monitor performance and health
💬 **Natural Conversation** - Just chat about anything!

What would you like to work on?"""

        elif "neurocode" in message_lower:
            return """🧬 NeuroCode is revolutionary! It's the first truly AI-native programming language where:

• Code can think and reason about outcomes
• You express intentions, not just implementations
• Memory is a first-class language feature
• AI models are built into the language itself
• Programs can evolve and optimize themselves

Want to try writing some NeuroCode? I can help guide you!"""

        else:
            return "💭 That's an interesting thought! I'd love to help you explore that further with NeuroCode. Can you tell me more about what you're trying to accomplish?"

    def generate_proactive_suggestions(self, user_input: str, conversation_context: Dict) -> List[str]:
        """Generate proactive suggestions based on user input and context"""
        suggestions = []

        # Memory-based suggestions
        if "remember" in user_input.lower() or "memory" in user_input.lower():
            suggestions.extend([
                "🧠 View your memory tags",
                "📊 Analyze memory patterns",
                "🔍 Search specific memories"
            ])

        # Goal-based suggestions
        if "goal" in user_input.lower() or "objective" in user_input.lower():
            suggestions.extend([
                "🎯 Check goal progress",
                "📈 Set milestone tracking",
                "🤖 Enable autonomous monitoring"
            ])

        # Plugin suggestions
        if "plugin" in user_input.lower() or "how do" in user_input.lower():
            suggestions.extend([
                "🔌 Browse available plugins",
                "💡 Generate custom plugin",
                "🛠️ Plugin development guide"
            ])

        # Learning suggestions
        if any(word in user_input.lower() for word in ["learn", "tutorial", "help", "guide"]):
            suggestions.extend([
                "📚 NeuroCode examples",
                "🎓 Interactive tutorial",
                "💻 Practice exercises"
            ])

        # Context-aware suggestions based on system state
        if conversation_context.get('memory_count', 0) == 0:
            suggestions.append("💾 Start building your memory")

        if conversation_context.get('goals_count', 0) == 0:
            suggestions.append("🎯 Set your first goal")

        if len(self.chat_history) > 5 and not any("reflect" in msg.get('user', '') for msg in self.chat_history[-3:]):
            suggestions.append("🤔 Reflect on recent progress")

        return suggestions[:3]  # Return top 3 suggestions

    def smart_intent_routing(self, user_input: str) -> Dict:
        """Lightweight routing with smart fallbacks"""
        intent = self._analyze_intent(user_input)

        # If no clear intent, treat as open-ended conversation
        if not intent or intent.get('confidence', 0) < 0.7:
            if self.debug_mode:
                print("[CHAT DEBUG] Low confidence intent - routing to open-ended AI")
            return {
                "type": "open_ended",
                "confidence": 1.0,
                "route": "direct_ai"
            }

        return intent
