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
multi_agent_module = _safe_import_core_module("multi_agent_manager")

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
        def generate_neuro_workflow(self, description, complexity="standard"):
            return f"# Basic workflow for: {description}\nremember \"{description}\"\nset_goal \"Complete task\""

if ai_runtime_module:
    ask_ai = ai_runtime_module.ask_ai
else:
    def ask_ai(prompt, temperature=0.2):
        return "[AI Disabled] OPENAI_API_KEY not configured"

if multi_agent_module:
    MultiAgentManager = multi_agent_module.MultiAgentManager
else:
    class MultiAgentManager:
        def assign_task(self, description, priority=5): return "demo_task_id"
        def execute_task(self, task_id): return {"success": True, "result": "Demo execution"}
        def coordinate_multi_agent_task(self, description): return {"success": True, "agents_involved": ["Demo"]}
        def get_agent_status(self): return {"agents": {}, "pending_tasks": 0}

class NeuroCodeChatRouter:
    """
    Intelligent router for chat-based NeuroCode interaction
    """

    def __init__(self, demo_mode=False, debug_mode=False):
        self.interpreter = NeuroCodeInterpreter()
        self.memory = NeuroMemory()
        self.compiler = NaturalLanguageCompiler()
        self.multi_agent_manager = MultiAgentManager()
        self.chat_history = []
        self.active_goals = []
        self.system_personality = self._load_personality()
        self.demo_mode = demo_mode  # For testing without AI calls
        self.debug_mode = debug_mode  # For debug logging
        
        # Initialize personality system
        self.current_personality = None
        self.personality_persistence_enabled = False
        self.auto_personality_selection = False
        self.set_personality("default")

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

        # Multi-agent coordination requests
        if any(keyword in message_lower for keyword in ["coordinate", "collaborate", "team", "agents", "multi-agent"]):
            return {"type": "multi_agent_request", "confidence": 0.9}

        # Workflow generation requests
        if any(keyword in message_lower for keyword in ["workflow", "generate", "create workflow", ".neuro"]):
            return {"type": "workflow_generation", "confidence": 0.9}

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
        
        # Workflow generation
        if any(keyword in message_lower for keyword in ["workflow", "process", "steps", "generate .neuro", "create workflow"]):
            return {"type": "workflow_generation", "confidence": 0.8}

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

        elif intent_type == "multi_agent_request":
            response.update(self._handle_multi_agent_request(message))

        elif intent_type == "workflow_generation":
            response.update(self._handle_workflow_generation(message))

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
        
        elif intent_type == "workflow_generation":
            response.update(self._handle_workflow_generation(message))

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
        """Execute NeuroCode with self-correction logic"""
        try:
            results = []
            errors = []
            corrections = []
            
            for line in neurocode.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        result = self.interpreter.execute(line)
                        if result:
                            results.append(result)
                    except Exception as exec_error:
                        # Self-correction logic for plugin errors
                        correction_result = self._attempt_self_correction(line, str(exec_error))
                        
                        if correction_result["success"]:
                            corrections.append(correction_result)
                            results.append(correction_result["result"])
                        else:
                            errors.append({
                                "command": line,
                                "error": str(exec_error),
                                "correction_attempted": correction_result.get("correction_attempted", False)
                            })

            # Build response with correction information
            response = {
                "success": len(errors) == 0,
                "results": results,
                "errors": errors,
                "corrections": corrections,
                "message": self._build_execution_message(results, errors, corrections)
            }
            
            # Store execution results for learning
            if hasattr(self, 'execution_history'):
                self.execution_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "neurocode": neurocode,
                    "response": response
                })
            else:
                self.execution_history = [{
                    "timestamp": datetime.now().isoformat(),
                    "neurocode": neurocode,
                    "response": response
                }]
            
            return response

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Critical error executing NeuroCode: {e}",
                "corrections": [],
                "errors": [{"command": neurocode, "error": str(e)}]
            }
    
    def _attempt_self_correction(self, command: str, error: str) -> Dict:
        """Attempt to self-correct plugin errors"""
        correction_attempts = []
        
        # Common error patterns and corrections
        error_corrections = {
            "module not found": self._fix_import_error,
            "attribute error": self._fix_attribute_error,
            "plugin not loaded": self._fix_plugin_loading,
            "syntax error": self._fix_syntax_error,
            "permission denied": self._fix_permission_error
        }
        
        error_lower = error.lower()
        
        for error_pattern, correction_func in error_corrections.items():
            if error_pattern in error_lower:
                try:
                    correction_result = correction_func(command, error)
                    if correction_result["success"]:
                        return {
                            "success": True,
                            "correction_attempted": True,
                            "correction_type": error_pattern,
                            "original_command": command,
                            "corrected_command": correction_result.get("corrected_command"),
                            "result": correction_result["result"]
                        }
                    else:
                        correction_attempts.append(correction_result)
                except Exception as correction_error:
                    correction_attempts.append({
                        "type": error_pattern,
                        "error": str(correction_error)
                    })
        
        return {
            "success": False,
            "correction_attempted": True,
            "attempts": correction_attempts,
            "original_error": error
        }
    
    def _fix_import_error(self, command: str, error: str) -> Dict:
        """Fix module import errors"""
        # Try to suggest alternative imports or installations
        missing_module = None
        
        # Extract module name from error
        import re
        match = re.search(r"no module named '([^']+)'", error.lower())
        if match:
            missing_module = match.group(1)
        
        if missing_module:
            # Common module aliases
            module_alternatives = {
                "cv2": "opencv-python",
                "sklearn": "scikit-learn",
                "PIL": "Pillow",
                "np": "numpy",
                "pd": "pandas"
            }
            
            if missing_module in module_alternatives:
                suggestion = f"install {module_alternatives[missing_module]}"
                return {
                    "success": False,
                    "suggestion": suggestion,
                    "message": f"Module {missing_module} not found. Try: {suggestion}"
                }
        
        return {"success": False, "message": "Could not auto-fix import error"}
    
    def _fix_attribute_error(self, command: str, error: str) -> Dict:
        """Fix attribute access errors"""
        # Simple correction for common attribute mistakes
        if "has no attribute" in error.lower():
            return {
                "success": False,
                "message": "Attribute not found. Check object type and available methods.",
                "suggestion": "Use dir(object) to see available attributes"
            }
        return {"success": False}
    
    def _fix_plugin_loading(self, command: str, error: str) -> Dict:
        """Fix plugin loading issues"""
        # Try to reload or suggest plugin installation
        plugin_pattern = r"use\s+(\w+)"
        match = re.search(plugin_pattern, command)
        
        if match:
            plugin_name = match.group(1)
            try:
                # Attempt to reload plugin if method exists
                if hasattr(self.interpreter, 'reload_plugin'):
                    result = self.interpreter.reload_plugin(plugin_name)
                    if result:
                        # Retry original command
                        retry_result = self.interpreter.execute(command)
                        return {
                            "success": True,
                            "corrected_command": command,
                            "result": retry_result,
                            "correction": f"Reloaded plugin {plugin_name}"
                        }
            except Exception:
                pass
        
        return {
            "success": False,
            "message": "Plugin loading failed. Check if plugin is installed and compatible.",
            "suggestion": "Try: reload plugins or check plugin status"
        }
    
    def _fix_syntax_error(self, command: str, error: str) -> Dict:
        """Fix basic syntax errors"""
        # Simple syntax corrections
        corrected = command
        
        # Common fixes
        if "unexpected indent" in error.lower():
            corrected = corrected.lstrip()
        elif "invalid syntax" in error.lower() and "=" in command:
            # Try to fix assignment issues
            if " = " not in command and "=" in command:
                corrected = command.replace("=", " = ", 1)
        
        if corrected != command:
            try:
                result = self.interpreter.execute(corrected)
                return {
                    "success": True,
                    "corrected_command": corrected,
                    "result": result,
                    "correction": "Fixed syntax"
                }
            except Exception:
                pass
        
        return {"success": False, "message": "Could not auto-fix syntax error"}
    
    def _fix_permission_error(self, command: str, error: str) -> Dict:
        """Handle permission errors"""
        return {
            "success": False,
            "message": "Permission denied. Check file/directory permissions or run with appropriate privileges.",
            "suggestion": "Ensure you have necessary permissions for this operation"
        }
    
    def _build_execution_message(self, results: List, errors: List, corrections: List) -> str:
        """Build informative execution message"""
        if not errors and not corrections:
            return "NeuroCode executed successfully"
        
        messages = []
        
        if results:
            messages.append(f"✅ {len(results)} command(s) executed successfully")
        
        if corrections:
            messages.append(f"🔧 {len(corrections)} error(s) auto-corrected")
            for correction in corrections:
                messages.append(f"   • Fixed {correction.get('correction_type', 'error')}")
        
        if errors:
            messages.append(f"❌ {len(errors)} error(s) encountered")
            for error in errors[:3]:  # Show first 3 errors
                messages.append(f"   • {error['command']}: {error['error']}")
        
        return "\n".join(messages)

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
        intent = chat_entry.get("intent", {})
        confidence = intent.get("confidence", 0)
        
        # Only store meaningful interactions
        if confidence > 0.7:
            # Extract key information from the conversation
            user_message = chat_entry.get("user", "")
            assistant_response = chat_entry.get("assistant", "")
            
            # Create memory entry for important conversations
            memory_entry = {
                "type": "conversation",
                "timestamp": chat_entry.get("timestamp"),
                "user_intent": intent.get("type"),
                "user_message": user_message,
                "assistant_response": assistant_response,
                "confidence": confidence,
                "context": chat_entry.get("context", {})
            }
            
            # Store in memory system if available
            if hasattr(self.memory, 'remember'):
                self.memory.remember(f"conversation_{intent.get('type')}", memory_entry)
            
            # Update conversation context for better continuity
            self._update_conversation_context(memory_entry)
    
    def _update_conversation_context(self, memory_entry: Dict):
        """Update conversation context for better multi-turn handling"""
        # Track conversation themes and topics
        if not hasattr(self, 'conversation_topics'):
            self.conversation_topics = []
        
        # Extract topics from user message
        user_message = memory_entry.get("user_message", "").lower()
        
        # Simple topic extraction based on keywords
        topic_keywords = {
            "development": ["code", "program", "develop", "build", "create"],
            "memory": ["remember", "recall", "memory", "forget"],
            "goals": ["goal", "objective", "target", "mission", "aim"],
            "debugging": ["error", "bug", "problem", "fix", "debug"],
            "learning": ["learn", "teach", "explain", "understand", "how"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in user_message for keyword in keywords):
                if topic not in self.conversation_topics:
                    self.conversation_topics.append(topic)
                # Keep only recent topics (last 10)
                if len(self.conversation_topics) > 10:
                    self.conversation_topics = self.conversation_topics[-10:]

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

    def save_personality_settings(self, filename: str = "personality_settings.json"):
        """Save current personality settings to file"""
        try:
            import json
            import os
            
            settings_dir = "data"
            if not os.path.exists(settings_dir):
                os.makedirs(settings_dir)
            
            filepath = os.path.join(settings_dir, filename)
            
            personality_data = {
                "current_personality": getattr(self, 'current_personality', {}),
                "personality_history": getattr(self, 'personality_history', []),
                "auto_selection_enabled": getattr(self, 'auto_personality_selection', False),
                "selection_criteria": getattr(self, 'personality_criteria', {}),
                "last_updated": datetime.now().isoformat()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(personality_data, f, indent=2)
            
            return {"success": True, "file": filepath}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def load_personality_settings(self, filename: str = "personality_settings.json"):
        """Load personality settings from file"""
        try:
            import json
            import os
            
            filepath = os.path.join("data", filename)
            
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    personality_data = json.load(f)
                
                # Restore settings
                if "current_personality" in personality_data:
                    self.current_personality = personality_data["current_personality"]
                
                self.personality_history = personality_data.get("personality_history", [])
                self.auto_personality_selection = personality_data.get("auto_selection_enabled", False)
                self.personality_criteria = personality_data.get("selection_criteria", {})
                
                return {"success": True, "loaded": personality_data}
            else:
                # Initialize with defaults
                self.set_personality("default")
                self.personality_history = []
                self.auto_personality_selection = False
                self.personality_criteria = {}
                
                return {"success": True, "message": "No existing settings, initialized defaults"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def enable_auto_personality_selection(self, criteria: Optional[Dict] = None):
        """Enable automatic personality selection based on context"""
        self.auto_personality_selection = True
        
        # Default criteria for automatic selection
        default_criteria = {
            "learning_keywords": ["learn", "teach", "explain", "understand", "how"],
            "development_keywords": ["code", "program", "debug", "optimize", "build"],
            "casual_keywords": ["chat", "talk", "hello", "hi", "casual"],
            "technical_keywords": ["analyze", "performance", "system", "technical"]
        }
        
        self.personality_criteria = criteria if criteria else default_criteria
        
        # Save settings
        self.save_personality_settings()
    
    def auto_select_personality(self, message: str) -> str:
        """Automatically select personality based on message content"""
        if not getattr(self, 'auto_personality_selection', False):
            return getattr(self, 'current_personality', {}).get('name', 'default')
        
        message_lower = message.lower()
        criteria = getattr(self, 'personality_criteria', {})
        
        # Count matches for each personality type
        personality_scores = {
            "mentor": 0,
            "dev_focused": 0,
            "sassy": 0,
            "default": 0
        }
        
        # Score based on keywords
        for keyword in criteria.get("learning_keywords", []):
            if keyword in message_lower:
                personality_scores["mentor"] += 1
        
        for keyword in criteria.get("development_keywords", []):
            if keyword in message_lower:
                personality_scores["dev_focused"] += 1
        
        for keyword in criteria.get("technical_keywords", []):
            if keyword in message_lower:
                personality_scores["dev_focused"] += 1
        
        for keyword in criteria.get("casual_keywords", []):
            if keyword in message_lower:
                personality_scores["sassy"] += 1
        
        # Select personality with highest score
        selected_personality = max(personality_scores.keys(), key=lambda k: personality_scores[k])
        
        # Only switch if there's a clear preference (score > 0)
        if personality_scores[selected_personality] > 0:
            current_name = getattr(self, 'current_personality', {}).get('name', 'default')
            if selected_personality != current_name:
                self.set_personality(selected_personality)
                
                # Track personality changes
                if not hasattr(self, 'personality_history'):
                    self.personality_history = []
                
                self.personality_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "from": current_name,
                    "to": selected_personality,
                    "trigger": message[:50],
                    "scores": personality_scores
                })
                
                # Keep only recent history (last 20 changes)
                if len(self.personality_history) > 20:
                    self.personality_history = self.personality_history[-20:]
        
        return selected_personality

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

    def _handle_multi_agent_request(self, message: str) -> Dict:
        """Handle multi-agent coordination requests"""
        try:
            # Coordinate multiple agents for complex task
            result = self.multi_agent_manager.coordinate_multi_agent_task(message)
            
            if result["success"]:
                agents_involved = result.get("agents_involved", [])
                plan = result.get("plan", {})
                
                response_text = "🤖 **Multi-Agent Coordination Initiated**\n\n"
                response_text += f"**Task**: {message}\n\n"
                response_text += f"**Agents Involved**: {', '.join(agents_involved)}\n\n"
                
                if "task_breakdown" in plan:
                    response_text += "**Execution Plan**:\n"
                    for i, step in enumerate(plan["task_breakdown"][:5], 1):
                        response_text += f"{i}. {step}\n"
                
                response_text += "\n**Coordination Status**: Active\n"
                response_text += f"**Subtasks Completed**: {len(result.get('subtask_results', []))}"
                
                return {
                    "text": response_text,
                    "neurocode": f'remember "Multi-agent coordination: {message}"',
                    "suggestions": ["Check agent status", "View detailed results", "Coordinate next phase"]
                }
            else:
                return {
                    "text": "🤖 Unable to coordinate multi-agent task. Agents may be busy or task complexity too high.",
                    "suggestions": ["Try simpler task", "Check agent availability", "Retry later"]
                }
        
        except Exception as e:
            return {
                "text": f"🤖 Multi-agent coordination error: {str(e)}",
                "suggestions": ["Check agent status", "Simplify request", "Try single agent"]
            }
    
    def _handle_workflow_generation(self, message: str) -> Dict:
        """Handle workflow generation requests"""
        try:
            # Determine complexity based on message content
            complexity = "standard"
            if any(word in message.lower() for word in ["simple", "basic", "quick"]):
                complexity = "simple"
            elif any(word in message.lower() for word in ["advanced", "complex", "detailed"]):
                complexity = "advanced"
            
            # Generate the workflow
            workflow = self.compiler.generate_neuro_workflow(message, complexity)
            
            # Save workflow to file if requested
            workflow_filename = None
            if ".neuro" in message.lower() or "save" in message.lower():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                workflow_filename = f"generated_workflow_{timestamp}.neuro"
                
                try:
                    with open(workflow_filename, 'w') as f:
                        f.write(workflow)
                except Exception:
                    workflow_filename = None
            
            response_text = "🧬 **NeuroCode Workflow Generated**\n\n"
            response_text += f"**Description**: {message}\n"
            response_text += f"**Complexity**: {complexity}\n"
            
            if workflow_filename:
                response_text += f"**Saved to**: {workflow_filename}\n"
            
            response_text += f"\n**Preview**:\n```neurocode\n{workflow[:300]}{'...' if len(workflow) > 300 else ''}\n```"
            
            return {
                "text": response_text,
                "neurocode": workflow if len(workflow) < 500 else workflow[:500] + "\n# ... (truncated)",
                "suggestions": ["Execute workflow", "Modify workflow", "Save to file"]
            }
        
        except Exception as e:
            return {
                "text": f"🧬 Workflow generation error: {str(e)}",
                "suggestions": ["Simplify description", "Try basic workflow", "Check compiler status"]
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
        if not hasattr(self, 'current_personality') or self.current_personality is None:
            self.set_personality("default")

        # Auto-select personality if enabled
        if getattr(self, 'auto_personality_selection', False):
            selected = self.auto_select_personality(user_input)
            if self.debug_mode:
                print(f"[CHAT DEBUG] Auto-selected personality: {selected}")

        # Ensure we have a valid personality
        personality_prompt = "You are Neuroplex, a helpful AI assistant."
        if self.current_personality and isinstance(self.current_personality, dict):
            personality_prompt = self.current_personality.get('prompt', personality_prompt)

        # Build rich context prompt
        context_prompt = f"""{personality_prompt}

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
            return f"Hello! I'm {personality['name']}, your NeuroCode assistant. How can I help you today?"

        elif any(word in message_lower for word in ["help", "what", "how"]):
            return """I can help you with:
🧠 **Memory**: `remember "anything"`
🎯 **Goals**: `set_goal "your objective"`
🤖 **Plugins**: `use [plugin] to [action]`
💭 **Analysis**: `think about "topic"`

What would you like to explore?"""

        elif any(word in message_lower for word in ["status", "how are you"]):
            return "I'm functioning well! My systems are active and I'm ready to help with NeuroCode development."

        elif any(word in message_lower for word in ["memory", "remember"]):
            return "I can help you store and recall information. Try: `remember \"important information\"`"

        elif any(word in message_lower for word in ["goal", "objective"]):
            return "Let's set some goals! Try: `set_goal \"achieve something meaningful\"`"

        else:
            return f"I'm {personality['name']}, ready to help with NeuroCode! Tell me what you'd like to do."

    def _build_conversation_context(self, current_message: str) -> Dict:
        """Build rich context for AI conversation with multi-turn awareness"""
        # Get recent chat history with better context
        recent_chat = []
        conversation_summary = ""
        
        # Build conversation thread with more context
        for entry in self.chat_history[-10:]:  # Last 10 exchanges for better context
            user_msg = entry.get('user', '')
            assistant_msg = entry.get('assistant', '')
            intent_type = entry.get('intent', {}).get('type', 'unknown')
            
            recent_chat.append(f"[{intent_type}] User: {user_msg}")
            recent_chat.append(f"Assistant: {assistant_msg}")
        
        # Create conversation summary for AI context
        if len(self.chat_history) > 0:
            topics = getattr(self, 'conversation_topics', [])
            if topics:
                conversation_summary = f"Recent conversation topics: {', '.join(topics[-5:])}"
        
        # Get system state
        memories = getattr(self.memory, 'memories', [])
        goals = getattr(self.interpreter, 'goals', [])
        
        # Get relevant memories based on current message
        relevant_memories = self._get_relevant_memories(current_message)
        
        return {
            "recent_chat": "\n".join(recent_chat) if recent_chat else "No previous conversation",
            "conversation_summary": conversation_summary,
            "relevant_memories": relevant_memories,
            "memory_count": len(memories),
            "goals_count": len(goals),
            "plugins": len(getattr(self.interpreter, 'loaded_plugins', {})),
            "current_message": current_message,
            "conversation_topics": getattr(self, 'conversation_topics', []),
            "session_length": len(self.chat_history)
        }
    
    def _get_relevant_memories(self, message: str) -> List[Dict]:
        """Get memories relevant to the current message"""
        relevant_memories = []
        message_lower = message.lower()
        
        # Search through stored conversation memories using safe attribute access
        try:
            if hasattr(self.memory, 'memories'):
                memories = getattr(self.memory, 'memories', [])
                if memories:
                    for memory in memories:
                        if isinstance(memory, dict):
                            # Check if memory is conversation-related
                            if memory.get('type') == 'conversation':
                                user_msg = memory.get('user_message', '').lower()
                                assistant_msg = memory.get('assistant_response', '').lower()
                                
                                # Simple relevance check based on common words
                                message_words = set(message_lower.split())
                                memory_words = set(user_msg.split() + assistant_msg.split())
                                common_words = message_words.intersection(memory_words)
                                
                                if len(common_words) > 1:  # At least 2 common words
                                    relevant_memories.append({
                                        "timestamp": memory.get('timestamp'),
                                        "user_intent": memory.get('user_intent'),
                                        "summary": f"Previous discussion about {memory.get('user_intent')}"
                                    })
            elif hasattr(self.memory, 'recall'):
                # Use recall method if available
                recalled_memories = self.memory.recall(message_lower)
                if recalled_memories:
                    relevant_memories = recalled_memories[-5:]
        except Exception as e:
            # Gracefully handle any memory access errors
            if self.debug_mode:
                print(f"[CHAT DEBUG] Memory access error: {e}")
        
        return relevant_memories[-5:]  # Return most recent 5 relevant memories
    
    def generate_proactive_suggestions(self, user_input: str, context: Dict) -> List[str]:
        """Generate proactive suggestions based on conversation context"""
        suggestions = []
        input_lower = user_input.lower()
        
        # Memory-based suggestions
        if any(word in input_lower for word in ["remember", "memory", "recall"]):
            suggestions.extend([
                "Explore memory timeline",
                "Search related memories",
                "Save important information"
            ])
        
        # Goal-based suggestions
        if any(word in input_lower for word in ["goal", "objective", "target"]):
            suggestions.extend([
                "Set new goals",
                "Track progress",
                "Break down objectives"
            ])
        
        # Multi-agent suggestions
        if any(word in input_lower for word in ["complex", "difficult", "help"]):
            suggestions.extend([
                "Coordinate multiple agents",
                "Break into subtasks",
                "Use specialized agents"
            ])
        
        # Learning suggestions
        if any(word in input_lower for word in ["learn", "understand", "explain"]):
            suggestions.extend([
                "Create learning workflow",
                "Find resources",
                "Practice with examples"
            ])
        
        # Workflow suggestions
        if any(word in input_lower for word in ["create", "build", "develop"]):
            suggestions.extend([
                "Generate NeuroCode workflow",
                "Use project templates",
                "Plan development phases"
            ])
        
        # Limit to top 3 most relevant suggestions
        return suggestions[:3]
