#!/usr/bin/env python3
"""
🧠 LYRIXA ENHANCED CONVERSATION MANAGER (#7)
============================================

Advanced conversational AI with multi-turn memory, intent translation,
and context-aware dialogue capabilities for Aetherra AI OS.

ROADMAP ITEM #7: Enhanced Conversational AI
- Multi-Turn Conversation Memory
- Intent-to-Code Translation
- Context-Aware Dialogue Management
- Thread-Aware Session Continuity
- Personality Persistence & Auto-Selection
"""

import asyncio
import logging
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

# Set up logging
logger = logging.getLogger(__name__)


class ConversationType(Enum):
    """Types of conversation interactions"""
    QUESTION = "question"
    CODE_REQUEST = "code_request"
    EXPLANATION = "explanation"
    TASK_CREATION = "task_creation"
    MEMORY_QUERY = "memory_query"
    SYSTEM_COMMAND = "system_command"
    CASUAL_CHAT = "casual_chat"


class IntentType(Enum):
    """Natural language intent classifications"""
    CREATE_CODE = "create_code"
    EXPLAIN_CONCEPT = "explain_concept"
    DEBUG_ISSUE = "debug_issue"
    MANAGE_PROJECT = "manage_project"
    QUERY_MEMORY = "query_memory"
    LEARN_TOPIC = "learn_topic"
    EXECUTE_TASK = "execute_task"


@dataclass
class ConversationContext:
    """Rich conversation context for multi-turn memory"""
    session_id: str
    thread_id: str
    user_id: str
    topic: Optional[str] = None
    intent: Optional[IntentType] = None
    conversation_type: Optional[ConversationType] = None
    project_context: Optional[str] = None
    personality_mode: str = "default"
    confidence_score: float = 0.0
    urgency_level: int = 1  # 1-5 scale
    requires_followup: bool = False


@dataclass
class ConversationTurn:
    """Individual turn in conversation with full context"""
    turn_id: str
    timestamp: datetime
    user_input: str
    assistant_response: str
    context: ConversationContext
    intent_analysis: Dict[str, Any]
    generated_code: Optional[str] = None
    confidence: float = 0.0
    feedback_score: Optional[int] = None


class LyrixaEnhancedConversationManager:
    """
    🧠 Enhanced Lyrixa Conversation Manager - Roadmap Item #7

    Advanced conversational AI with multi-turn memory, intent translation,
    and sophisticated context management capabilities.
    """

    def __init__(self, memory_engine=None, analytics_engine=None):
        # Core systems
        self.memory_engine = memory_engine
        self.analytics_engine = analytics_engine

        # Enhanced conversation state
        self.conversation_threads = {}  # thread_id -> List[ConversationTurn]
        self.active_sessions = {}  # session_id -> ConversationContext
        self.user_personalities = {}  # user_id -> preferred personality
        self.conversation_summaries = {}  # session_id -> summary

        # Configuration
        self.context_window_size = 100  # Increased for better memory
        self.max_thread_length = 50
        self.intent_confidence_threshold = 0.7
        self.code_generation_enabled = True
        self.memory_integration_enabled = bool(memory_engine)

        # Performance tracking
        self.is_available = True
        self.total_conversations = 0
        self.successful_intent_translations = 0
        self.code_generations = 0

        # Intent patterns for natural language processing
        self.intent_patterns = self._initialize_intent_patterns()

        logger.info("🧠 Enhanced LyrixaConversationManager (#7) initialized with multi-turn memory support")

    def _initialize_intent_patterns(self) -> Dict[str, List[str]]:
        """Initialize intent recognition patterns for natural language processing"""
        return {
            "create_code": [
                r"create\s+(?:a\s+)?(?:function|class|script|program|app|api|website)",
                r"build\s+(?:a\s+)?(?:function|class|script|program|app|api|website)",
                r"generate\s+(?:code|python|javascript|html|css)",
                r"write\s+(?:a\s+)?(?:function|class|script|program)",
                r"implement\s+(?:a\s+)?(?:function|algorithm|feature)",
                r"code\s+(?:a\s+)?(?:solution|function|class)",
            ],
            "explain_concept": [
                r"explain\s+(?:how|what|why)",
                r"what\s+(?:is|are|does)",
                r"how\s+(?:do|does|can)",
                r"tell\s+me\s+about",
                r"describe\s+(?:the|how)",
                r"help\s+me\s+understand",
            ],
            "debug_issue": [
                r"(?:fix|debug|solve|resolve)\s+(?:this|the|my)",
                r"(?:error|bug|issue|problem)",
                r"not\s+working",
                r"broken",
                r"throwing\s+(?:an\s+)?(?:error|exception)",
            ],
            "manage_project": [
                r"(?:create|start|initialize|setup)\s+(?:a\s+)?(?:project|repository)",
                r"organize\s+(?:my\s+)?(?:code|files|project)",
                r"structure\s+(?:my\s+)?project",
                r"project\s+management",
            ],
            "query_memory": [
                r"(?:remember|recall|find)\s+(?:what|when|where)",
                r"what\s+did\s+(?:we|i)\s+(?:discuss|talk\s+about)",
                r"previous\s+(?:conversation|discussion)",
                r"last\s+time",
                r"earlier\s+(?:we|you|i)",
            ],
            "learn_topic": [
                r"(?:learn|study|understand)\s+(?:about|how)",
                r"teach\s+me",
                r"tutorial\s+(?:on|for)",
                r"guide\s+(?:to|for)",
                r"introduction\s+to",
            ],
            "execute_task": [
                r"(?:run|execute|perform|do)\s+(?:this|the|a)",
                r"start\s+(?:the|a)",
                r"launch\s+(?:the|a)",
                r"activate\s+(?:the|a)",
            ]
        }

    async def process_enhanced_message(
        self, message: str, user_id: str = "default", context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Enhanced message processing with multi-turn memory and intent analysis"""

        if context is None:
            context = {}

        start_time = datetime.now()
        self.total_conversations += 1

        # Generate session and thread IDs
        session_id = context.get("session_id", f"session_{user_id}_{int(time.time())}")
        thread_id = context.get("thread_id", f"thread_{session_id}_{len(self.conversation_threads.get(session_id, []))}")

        # Analyze intent and conversation type
        intent_analysis = await self._analyze_intent(message)
        conversation_type = self._classify_conversation_type(message, intent_analysis)

        # Create rich conversation context
        conv_context = ConversationContext(
            session_id=session_id,
            thread_id=thread_id,
            user_id=user_id,
            topic=intent_analysis.get("topic"),
            intent=intent_analysis.get("intent"),
            conversation_type=conversation_type,
            project_context=context.get("project_context"),
            personality_mode=self._select_personality(user_id, intent_analysis),
            confidence_score=intent_analysis.get("confidence", 0.0),
            urgency_level=self._assess_urgency(message, intent_analysis),
            requires_followup=intent_analysis.get("requires_followup", False)
        )

        # Retrieve conversation history and memory context
        conversation_history = self._get_conversation_history(session_id, thread_id)
        memory_context = await self._retrieve_memory_context(message, user_id, conv_context)

        # Generate enhanced response
        response = await self._generate_enhanced_response(
            message, conv_context, conversation_history, memory_context
        )

        # Handle code generation if requested
        generated_code = None
        if intent_analysis.get("intent") == IntentType.CREATE_CODE:
            generated_code = await self._generate_code_from_intent(message, intent_analysis, conv_context)
            if generated_code:
                self.code_generations += 1
                response["generated_code"] = generated_code

        # Create conversation turn record
        turn = ConversationTurn(
            turn_id=f"turn_{session_id}_{len(conversation_history) + 1}",
            timestamp=start_time,
            user_input=message,
            assistant_response=response["response"],
            context=conv_context,
            intent_analysis=intent_analysis,
            generated_code=generated_code,
            confidence=intent_analysis.get("confidence", 0.0)
        )

        # Store conversation turn
        await self._store_conversation_turn(turn)

        # Update analytics if available
        if self.analytics_engine:
            await self._update_analytics(turn, response)

        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()

        return {
            "response": response["response"],
            "intent": intent_analysis.get("intent").value if intent_analysis.get("intent") else None,
            "conversation_type": conversation_type.value if conversation_type else None,
            "confidence": intent_analysis.get("confidence", 0.0),
            "generated_code": generated_code,
            "thread_id": thread_id,
            "session_id": session_id,
            "requires_followup": conv_context.requires_followup,
            "processing_time": processing_time,
            "timestamp": start_time.isoformat(),
            "status": "success"
        }

    async def _analyze_intent(self, message: str) -> Dict[str, Any]:
        """Advanced intent analysis with confidence scoring"""
        message_lower = message.lower()
        intent_scores = {}

        # Score against intent patterns
        for intent_name, patterns in self.intent_patterns.items():
            score = 0.0
            matched_patterns = []

            for pattern in patterns:
                if re.search(pattern, message_lower):
                    score += 1.0
                    matched_patterns.append(pattern)

            if score > 0:
                intent_scores[intent_name] = {
                    "score": score / len(patterns),  # Normalize by pattern count
                    "matches": matched_patterns
                }

        # Determine primary intent
        primary_intent = None
        max_score = 0.0

        if intent_scores:
            primary_intent_name = max(intent_scores.keys(), key=lambda k: intent_scores[k]["score"])
            max_score = intent_scores[primary_intent_name]["score"]

            if max_score >= self.intent_confidence_threshold:
                try:
                    primary_intent = IntentType(primary_intent_name)
                    self.successful_intent_translations += 1
                except ValueError:
                    primary_intent = None

        # Extract topic and context
        topic = self._extract_topic(message)
        requires_followup = self._assess_followup_need(message, intent_scores)

        return {
            "intent": primary_intent,
            "confidence": max_score,
            "intent_scores": intent_scores,
            "topic": topic,
            "requires_followup": requires_followup,
            "analysis_timestamp": datetime.now().isoformat()
        }

    def _classify_conversation_type(self, message: str, intent_analysis: Dict[str, Any]) -> ConversationType:
        """Classify the type of conversation based on message content and intent"""
        intent = intent_analysis.get("intent")

        # Map intents to conversation types
        if intent == IntentType.CREATE_CODE:
            return ConversationType.CODE_REQUEST
        elif intent == IntentType.EXPLAIN_CONCEPT:
            return ConversationType.EXPLANATION
        elif intent == IntentType.DEBUG_ISSUE:
            return ConversationType.CODE_REQUEST
        elif intent == IntentType.MANAGE_PROJECT:
            return ConversationType.TASK_CREATION
        elif intent == IntentType.QUERY_MEMORY:
            return ConversationType.MEMORY_QUERY
        elif intent == IntentType.EXECUTE_TASK:
            return ConversationType.SYSTEM_COMMAND

        # Fallback classification
        message_lower = message.lower()
        if any(word in message_lower for word in ["?", "what", "how", "why", "when", "where"]):
            return ConversationType.QUESTION
        elif any(word in message_lower for word in ["create", "build", "make", "generate", "write"]):
            return ConversationType.CODE_REQUEST
        else:
            return ConversationType.CASUAL_CHAT

    def _select_personality(self, user_id: str, intent_analysis: Dict[str, Any]) -> str:
        """Auto-select personality based on user preferences and context"""
        # Check user's preferred personality
        if user_id in self.user_personalities:
            return self.user_personalities[user_id]

        # Context-aware personality selection
        intent = intent_analysis.get("intent")

        if intent in [IntentType.CREATE_CODE, IntentType.DEBUG_ISSUE]:
            return "developer"
        elif intent == IntentType.LEARN_TOPIC:
            return "mentor"
        elif intent == IntentType.EXPLAIN_CONCEPT:
            return "teacher"
        else:
            return "default"

    def _assess_urgency(self, message: str, intent_analysis: Dict[str, Any]) -> int:
        """Assess urgency level (1-5) based on message content"""
        message_lower = message.lower()
        urgency = 1

        # Urgency indicators
        if any(word in message_lower for word in ["urgent", "critical", "emergency", "asap", "immediately"]):
            urgency = 5
        elif any(word in message_lower for word in ["important", "priority", "needed", "required"]):
            urgency = 4
        elif any(word in message_lower for word in ["soon", "quickly", "fast"]):
            urgency = 3
        elif intent_analysis.get("intent") == IntentType.DEBUG_ISSUE:
            urgency = 3  # Debug issues are typically medium priority

        return urgency

    def _extract_topic(self, message: str) -> Optional[str]:
        """Extract main topic from message"""
        message_lower = message.lower()

        # Programming topics
        programming_topics = ["python", "javascript", "react", "django", "flask", "api", "database", "sql", "html", "css"]
        for topic in programming_topics:
            if topic in message_lower:
                return topic

        # General topics
        if "machine learning" in message_lower or "ml" in message_lower:
            return "machine_learning"
        elif "artificial intelligence" in message_lower or "ai" in message_lower:
            return "artificial_intelligence"
        elif "web development" in message_lower:
            return "web_development"
        elif "data science" in message_lower:
            return "data_science"

        return None

    def _assess_followup_need(self, message: str, intent_scores: Dict[str, Any]) -> bool:
        """Determine if conversation likely needs followup"""
        message_lower = message.lower()

        # Questions typically need followup
        if any(word in message_lower for word in ["?", "what", "how", "why", "explain"]):
            return True

        # Complex requests need followup
        if any(intent in intent_scores for intent in ["create_code", "debug_issue", "manage_project"]):
            return True

        # Learning requests need followup
        if any(word in message_lower for word in ["learn", "tutorial", "guide", "teach"]):
            return True

        return False

    def _get_conversation_history(self, session_id: str, thread_id: str) -> List[ConversationTurn]:
        """Retrieve conversation history for a specific thread"""
        if session_id not in self.conversation_threads:
            return []

        thread_history = []
        for turn in self.conversation_threads[session_id]:
            if turn.context.thread_id == thread_id:
                thread_history.append(turn)

        return thread_history[-self.context_window_size:]

    async def _retrieve_memory_context(
        self, message: str, user_id: str, conv_context: ConversationContext
    ) -> Dict[str, Any]:
        """Retrieve relevant memory context for enhanced response generation"""
        if not self.memory_integration_enabled:
            return {}

        try:
            # Simple memory context simulation (would integrate with actual memory engine)
            memory_results = []
            if hasattr(self.memory_engine, 'recall') and self.memory_engine is not None:
                memory_results = await self.memory_engine.recall(
                    query=message,
                    user_id=user_id,
                    context={
                        "session_id": conv_context.session_id,
                        "topic": conv_context.topic,
                        "intent": conv_context.intent.value if conv_context.intent else None
                    },
                    limit=5
                )

            return {
                "memories": memory_results,
                "memory_count": len(memory_results),
                "relevant_topics": [conv_context.topic] if conv_context.topic else [],
                "memory_confidence": sum(m.get("confidence", 0.0) for m in memory_results) / len(memory_results) if memory_results else 0.0
            }
        except Exception as e:
            logger.warning(f"[WARN] Memory retrieval failed: {e}")
            return {}

    async def _generate_enhanced_response(
        self,
        message: str,
        conv_context: ConversationContext,
        conversation_history: List[ConversationTurn],
        memory_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate enhanced response using all available context"""

        # Build context for response generation
        context_prompt = self._build_context_prompt(conv_context, conversation_history, memory_context)

        # Check for OpenAI API availability
        if os.getenv("OPENAI_API_KEY"):
            try:
                import openai
                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

                # Create enhanced system prompt
                system_prompt = f"""You are Lyrixa, an advanced AI assistant in the Aetherra OS with enhanced conversational capabilities.

{context_prompt}

**Current Context:**
- Personality Mode: {conv_context.personality_mode}
- Intent: {conv_context.intent.value if conv_context.intent else 'general'}
- Topic: {conv_context.topic or 'general'}
- Urgency: {conv_context.urgency_level}/5
- Conversation Type: {conv_context.conversation_type.value if conv_context.conversation_type else 'general'}

**Enhanced Capabilities:**
- Multi-turn conversation memory with thread continuity
- Intent-to-code translation for programming requests
- Context-aware personality adaptation
- Memory-informed responses with historical context

Provide helpful, contextual responses that:
1. Reference relevant conversation history when appropriate
2. Use memory context to provide continuity
3. Match the personality mode and user's expertise level
4. Address the specific intent with appropriate depth
5. Suggest follow-up actions if the request requires it"""

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ]

                # Add recent conversation history
                for turn in conversation_history[-3:]:
                    messages.insert(-1, {"role": "user", "content": turn.user_input})
                    messages.insert(-1, {"role": "assistant", "content": turn.assistant_response})

                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=800,
                    temperature=0.7,
                    presence_penalty=0.1
                )

                ai_response = response.choices[0].message.content
                if ai_response:
                    return {
                        "response": ai_response.strip(),
                        "source": "openai",
                        "confidence": 0.9
                    }

            except Exception as e:
                logger.warning(f"OpenAI API error: {e}")

        # Enhanced fallback response
        return await self._generate_enhanced_fallback(message, conv_context, conversation_history, memory_context)

    def _build_context_prompt(
        self,
        conv_context: ConversationContext,
        conversation_history: List[ConversationTurn],
        memory_context: Dict[str, Any]
    ) -> str:
        """Build comprehensive context prompt for AI response"""
        context_parts = []

        # Session context
        context_parts.append("**Session Information:**")
        context_parts.append(f"- Session: {conv_context.session_id}")
        context_parts.append(f"- User: {conv_context.user_id}")
        context_parts.append(f"- Thread: {conv_context.thread_id}")

        # Conversation continuity
        if conversation_history:
            context_parts.append("\n**Conversation Continuity:**")
            context_parts.append(f"- Previous turns in thread: {len(conversation_history)}")
            recent_topics = [turn.context.topic for turn in conversation_history[-3:] if turn.context.topic]
            if recent_topics:
                context_parts.append(f"- Recent topics discussed: {', '.join(set(recent_topics))}")

        # Memory context
        if memory_context.get("memories"):
            context_parts.append("\n**Memory Context:**")
            context_parts.append(f"- Relevant memories available: {memory_context['memory_count']}")
            context_parts.append(f"- Memory confidence: {memory_context.get('memory_confidence', 0.0):.2f}")

        # Project context
        if conv_context.project_context:
            context_parts.append("\n**Project Context:**")
            context_parts.append(f"- Current project: {conv_context.project_context}")

        return "\n".join(context_parts)

    async def _generate_enhanced_fallback(
        self,
        message: str,
        conv_context: ConversationContext,
        conversation_history: List[ConversationTurn],
        memory_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate enhanced fallback response with context awareness"""

        message_lower = message.lower()
        response_parts = []

        # Greeting detection with context
        if any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
            response_parts.append("Hello! I'm Lyrixa, your enhanced AI assistant with multi-turn conversation memory.")

            if conversation_history:
                last_topic = conversation_history[-1].context.topic
                response_parts.append(f"I see we've been discussing {last_topic or 'various topics'} in our previous conversation.")

            if memory_context.get("memories"):
                response_parts.append("I have access to our conversation history and can maintain context across sessions.")

        # Intent-specific enhanced responses
        elif conv_context.intent == IntentType.CREATE_CODE:
            response_parts.append("[TOOL] I'd be happy to help you create code with intent-to-code translation!")
            if conv_context.topic:
                response_parts.append(f"I can see you're working with {conv_context.topic}.")
            response_parts.append("Please provide more details about what you'd like to build, and I'll generate appropriate code.")

        elif conv_context.intent == IntentType.EXPLAIN_CONCEPT:
            response_parts.append("📚 I can explain that concept with contextual awareness!")
            if memory_context.get("memories"):
                response_parts.append("Based on our previous discussions, I'll tailor the explanation to your experience level.")

        elif conv_context.intent == IntentType.DEBUG_ISSUE:
            response_parts.append("🐛 Let me help you debug that issue with enhanced problem analysis.")
            response_parts.append("Can you share the error message or describe what's not working as expected?")

        elif conv_context.intent == IntentType.QUERY_MEMORY:
            if memory_context.get("memories"):
                response_parts.append(f"🧠 I found {memory_context['memory_count']} relevant memories from our conversations.")
                response_parts.append("Let me know what specific information you're looking for.")
            else:
                response_parts.append("🧠 I don't have specific memories about that topic yet, but I'm learning!")

        # General enhanced fallback
        else:
            response_parts.append(f"I understand you said: '{message[:100]}{'...' if len(message) > 100 else ''}'")

            if conv_context.urgency_level > 3:
                response_parts.append("⚡ I can see this is important - I'll prioritize helping you with this!")

            response_parts.append("🚀 I'm running in enhanced mode with:")
            response_parts.append("• Multi-turn conversation memory")
            response_parts.append("• Intent-to-code translation")
            response_parts.append("• Context-aware personality adaptation")
            response_parts.append("• Thread-aware session continuity")

            if conv_context.requires_followup:
                response_parts.append("\n💬 This seems like it might need follow-up discussion. I'm ready to continue our conversation!")

        return {
            "response": " ".join(response_parts),
            "source": "enhanced_fallback",
            "confidence": 0.7
        }

    async def _generate_code_from_intent(
        self, message: str, intent_analysis: Dict[str, Any], conv_context: ConversationContext
    ) -> Optional[str]:
        """Generate code based on detected intent and context"""
        if not self.code_generation_enabled:
            return None

        message_lower = message.lower()

        # Enhanced code generation patterns
        if "function" in message_lower and "fibonacci" in message_lower:
            return '''def fibonacci(n):
    """Calculate the nth Fibonacci number using dynamic programming"""
    if n <= 0:
        return 0
    elif n == 1:
        return 1

    # Dynamic programming approach for efficiency
    dp = [0, 1]
    for i in range(2, n + 1):
        dp.append(dp[i-1] + dp[i-2])

    return dp[n]

# Example usage with enhanced error handling
def demo_fibonacci():
    try:
        for i in range(10):
            result = fibonacci(i)
            print(f"fibonacci({i}) = {result}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    demo_fibonacci()'''

        elif "class" in message_lower and ("person" in message_lower or "user" in message_lower):
            return '''from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Person:
    """Enhanced Person class with validation and methods"""
    name: str
    age: int
    email: Optional[str] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

        # Validation
        if self.age < 0:
            raise ValueError("Age cannot be negative")
        if len(self.name.strip()) == 0:
            raise ValueError("Name cannot be empty")

    def greet(self) -> str:
        """Generate a personalized greeting"""
        greeting = f"Hello, I'm {self.name} and I'm {self.age} years old."
        if self.email:
            greeting += f" You can reach me at {self.email}."
        return greeting

    def is_adult(self) -> bool:
        """Check if person is an adult (18+)"""
        return self.age >= 18

    def __str__(self) -> str:
        return f"Person(name='{self.name}', age={self.age}, email='{self.email}')"

# Example usage with enhanced functionality
if __name__ == "__main__":
    try:
        person = Person("Alice", 30, "alice@example.com")
        print(person.greet())
        print(f"Is adult: {person.is_adult()}")
        print(f"Created: {person.created_at}")
    except ValueError as e:
        print(f"Validation error: {e}")'''

        elif "api" in message_lower and ("flask" in message_lower or "rest" in message_lower):
            return '''from flask import Flask, jsonify, request
from datetime import datetime
import uuid

app = Flask(__name__)

# In-memory storage (use database in production)
users = {}

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    return jsonify({
        "users": list(users.values()),
        "count": len(users)
    })

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()

        # Validation
        if not data or 'name' not in data or 'email' not in data:
            return jsonify({"error": "Name and email are required"}), 400

        # Create user
        user_id = str(uuid.uuid4())
        user = {
            "id": user_id,
            "name": data['name'],
            "email": data['email'],
            "created_at": datetime.now().isoformat()
        }

        users[user_id] = user

        return jsonify({
            "message": "User created successfully",
            "user": user
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get specific user by ID"""
    if user_id not in users:
        return jsonify({"error": "User not found"}), 404

    return jsonify(users[user_id])

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

if __name__ == '__main__':
    print("🚀 Starting Enhanced Aetherra API...")
    app.run(debug=True, host='0.0.0.0', port=5000)'''

        return None

    async def _store_conversation_turn(self, turn: ConversationTurn) -> bool:
        """Store conversation turn in both local and memory systems"""
        try:
            # Store in local conversation threads
            session_id = turn.context.session_id
            if session_id not in self.conversation_threads:
                self.conversation_threads[session_id] = []

            self.conversation_threads[session_id].append(turn)

            # Maintain thread size limits
            if len(self.conversation_threads[session_id]) > self.max_thread_length:
                self.conversation_threads[session_id] = self.conversation_threads[session_id][-self.max_thread_length:]

            # Store in memory engine if available
            if self.memory_integration_enabled and hasattr(self.memory_engine, 'store_conversation') and self.memory_engine is not None:
                await self.memory_engine.store_conversation(
                    user_input=turn.user_input,
                    assistant_response=turn.assistant_response,
                    context=turn.context.__dict__,
                    intent_analysis=turn.intent_analysis,
                    timestamp=turn.timestamp
                )

            logger.debug(f"📝 Stored conversation turn: {turn.turn_id}")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Error storing conversation turn: {e}")
            return False

    async def _update_analytics(self, turn: ConversationTurn, response: Dict[str, Any]) -> None:
        """Update analytics with conversation metrics"""
        if not self.analytics_engine:
            return

        try:
            metrics = {
                "conversation_turn": {
                    "session_id": turn.context.session_id,
                    "intent": turn.context.intent.value if turn.context.intent else None,
                    "confidence": turn.confidence,
                    "processing_time": response.get("processing_time", 0.0),
                    "personality_mode": turn.context.personality_mode,
                    "urgency_level": turn.context.urgency_level,
                    "code_generated": bool(turn.generated_code),
                    "requires_followup": turn.context.requires_followup,
                    "conversation_type": turn.context.conversation_type.value if turn.context.conversation_type else None
                }
            }

            await self.analytics_engine.collect_metrics(metrics)
            logger.debug(f"📊 Analytics updated for turn: {turn.turn_id}")

        except Exception as e:
            logger.warning(f"[WARN] Analytics update failed: {e}")

    # Enhanced convenience methods
    def set_user_personality(self, user_id: str, personality: str) -> None:
        """Set preferred personality for a user"""
        self.user_personalities[user_id] = personality
        logger.info(f"🎭 Set personality '{personality}' for user {user_id}")

    def get_conversation_summary(self, session_id: str) -> Optional[str]:
        """Get conversation summary for a session"""
        return self.conversation_summaries.get(session_id)

    def get_thread_summary(self, session_id: str, thread_id: str) -> Dict[str, Any]:
        """Get summary of a specific conversation thread"""
        thread_history = self._get_conversation_history(session_id, thread_id)

        if not thread_history:
            return {"error": "No conversation history found"}

        # Generate thread statistics
        total_turns = len(thread_history)
        intents = [turn.context.intent.value for turn in thread_history if turn.context.intent]
        topics = [turn.context.topic for turn in thread_history if turn.context.topic]
        code_generations = sum(1 for turn in thread_history if turn.generated_code)

        return {
            "thread_id": thread_id,
            "session_id": session_id,
            "total_turns": total_turns,
            "unique_intents": list(set(intents)),
            "topics_discussed": list(set(topics)),
            "code_generations": code_generations,
            "start_time": thread_history[0].timestamp.isoformat(),
            "last_activity": thread_history[-1].timestamp.isoformat(),
            "avg_confidence": sum(turn.confidence for turn in thread_history) / total_turns
        }

    def get_enhanced_stats(self) -> Dict[str, Any]:
        """Get comprehensive conversation statistics"""
        total_turns = sum(len(turns) for turns in self.conversation_threads.values())

        return {
            "total_conversations": self.total_conversations,
            "total_turns": total_turns,
            "successful_intent_translations": self.successful_intent_translations,
            "code_generations": self.code_generations,
            "active_sessions": len(self.active_sessions),
            "conversation_threads": len(self.conversation_threads),
            "intent_success_rate": (self.successful_intent_translations / self.total_conversations * 100) if self.total_conversations > 0 else 0,
            "code_generation_rate": (self.code_generations / self.total_conversations * 100) if self.total_conversations > 0 else 0,
            "is_available": self.is_available,
            "memory_integration_enabled": self.memory_integration_enabled,
            "analytics_integration_enabled": bool(self.analytics_engine)
        }

    # Legacy compatibility method
    def process_message(
        self, message: str, user_id: str = "default", context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Legacy compatibility method - processes message synchronously"""
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, we need to create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self.process_enhanced_message(message, user_id, context)
                    )
                    return future.result()
            else:
                return loop.run_until_complete(self.process_enhanced_message(message, user_id, context))
        except RuntimeError:
            # If no event loop exists, create a new one
            return asyncio.run(self.process_enhanced_message(message, user_id, context))


# Convenience function for easy import
def get_enhanced_conversation_manager(memory_engine=None, analytics_engine=None) -> LyrixaEnhancedConversationManager:
    """Get an instance of the enhanced conversation manager"""
    return LyrixaEnhancedConversationManager(memory_engine, analytics_engine)


# Legacy compatibility
def get_conversation_manager(memory_engine=None) -> LyrixaEnhancedConversationManager:
    """Legacy compatibility function"""
    return LyrixaEnhancedConversationManager(memory_engine)


__all__ = [
    "LyrixaEnhancedConversationManager",
    "get_enhanced_conversation_manager",
    "get_conversation_manager",
    "ConversationType",
    "IntentType",
    "ConversationContext",
    "ConversationTurn"
]
