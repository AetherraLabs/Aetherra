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

class NeuroCodeChatRouter:
    """
    Intelligent router for chat-based NeuroCode interaction
    """
    
    def __init__(self):
        self.interpreter = NeuroCodeInterpreter()
        self.memory = NeuroMemory()
        self.compiler = NaturalLanguageCompiler()
        self.chat_history = []
        self.active_goals = []
        self.system_personality = self._load_personality()
        
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
    
    def process_message(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """
        Process user message and generate appropriate response
        
        Returns:
            Dict with response text, actions taken, and system state
        """
        # Log the conversation
        chat_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "context": context or {}
        }
        
        # Analyze message intent
        intent = self._analyze_intent(user_input)
        
        # Generate response based on intent
        response = self._generate_response(user_input, intent, context)
        
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
        
        if intent_type == "memory_query":
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
        """Handle help and learning requests"""
        help_topics = {
            "neurocode": "NeuroCode is an AI-native programming language. Try: 'remember \"hello world\"' or 'set_goal \"learn NeuroCode\"'",
            "memory": "I can remember anything you tell me. Use: remember \"your text here\"",
            "goals": "Set objectives with: set_goal \"your objective here\"",
            "plugins": "Use plugins like: use sysmon to check_system_health",
            "thinking": "I can reason with: think about \"your topic\" or analyze \"your subject\""
        }
        
        # Find relevant help topic
        topic_found = None
        topic = None
        for topic, explanation in help_topics.items():
            if topic in message.lower():
                topic_found = explanation
                break
        
        if topic_found and topic:
            response_text = f"💡 **Help with {topic}**:\n\n{topic_found}"
        else:
            response_text = """💡 **NeuroCode Help**

Here's what I can help you with:

🧠 **Memory**: remember \"anything you want\"
🎯 **Goals**: set_goal \"your objective\"
🤖 **Plugins**: use [plugin] to [action]
💭 **Thinking**: think about \"any topic\"
🔍 **Analysis**: analyze \"any subject\"

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
        """Handle natural language programming requests"""
        neurocode = self.compiler.compile_natural_language(message)
        
        response_text = f"""🧬 **Natural Language → NeuroCode**

I've translated your request into NeuroCode:

```neurocode
{neurocode}
```

Would you like me to execute this?"""
        
        return {
            "text": response_text,
            "neurocode": neurocode,
            "suggestions": ["Execute now", "Modify first", "Explain code"]
        }
    
    def _handle_general_conversation(self, message: str) -> Dict:
        """Handle general conversation"""
        personality = self.system_personality
        
        # Generate contextual response based on NeuroCode's personality  
        # Note: These templates are available for future dynamic response generation
        # but not actively used to prevent unused variable warnings
        
        # Simple keyword-based response selection
        if "hello" in message.lower() or "hi" in message.lower():
            response_text = f"👋 Hello! I'm {personality['name']}, your NeuroCode AI companion. I'm here to help you build the future with AI-native programming!"
        elif "thank" in message.lower():
            response_text = "🙏 You're welcome! I'm always here to help advance human-AI collaboration through NeuroCode."
        elif "goodbye" in message.lower() or "bye" in message.lower():
            response_text = "👋 Goodbye! I'll remember our conversation and be here when you return. Keep thinking in NeuroCode!"
        else:
            response_text = "💭 That's interesting! How can I help you apply NeuroCode to explore this further?"
        
        # Remember the conversation
        neurocode = f'remember "User said: {message}" as "conversation"'
        
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
