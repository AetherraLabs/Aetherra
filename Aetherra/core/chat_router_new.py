#!/usr/bin/env python3
"""
🎯 Chat Router System for Lyrixa
===============================

This module implements intelligent routing for natural language interaction
with Aetherra's autonomous capabilities. It processes user messages and routes
them to appropriate handlers based on intent, context, and capabilities.
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# Try to import Aetherra components with fallback
try:
    from Aetherra.core.engine.reasoning_engine import ReasoningEngine, ReasoningContext
    from Aetherra.core.engine.introspection_controller import IntrospectionController
    from Aetherra.core.self_improvement_engine import SelfImprovementEngine
    HAS_AETHERRA_ENGINES = True
except ImportError:
    HAS_AETHERRA_ENGINES = False
    logger.warning("Aetherra engines not available, using mock implementations")

    # Create mock classes
    class MockResult:
        def __init__(self):
            self.conclusion = 'Basic routing analysis completed'
            self.alternatives = ['General response available']
            self.confidence = 0.5

    class ReasoningEngine:
        async def reason(self, context):
            return MockResult()

    class ReasoningContext:
        def __init__(self, query, domain, context_data, constraints, objectives):
            self.query = query
            self.domain = domain
            self.context_data = context_data
            self.constraints = constraints
            self.objectives = objectives

    class IntrospectionController:
        def get_current_health(self):
            return {"status": "unknown", "timestamp": datetime.now().isoformat()}

    class SelfImprovementEngine:
        async def improve(self, context):
            return {"status": "improvement_not_available"}


class IntentType(Enum):
    """Types of user intents"""
    QUESTION = "question"
    COMMAND = "command"
    CONVERSATION = "conversation"
    REFLECTION = "reflection"
    ANALYSIS = "analysis"
    CREATIVITY = "creativity"
    PROBLEM_SOLVING = "problem_solving"
    SYSTEM_QUERY = "system_query"
    AUTONOMOUS_REQUEST = "autonomous_request"
    UNKNOWN = "unknown"


class RoutingPriority(Enum):
    """Routing priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"


@dataclass
class RouteDefinition:
    """Defines a routing rule"""
    pattern: str
    handler: str
    intent_type: IntentType
    priority: RoutingPriority
    requires_context: bool = False
    requires_memory: bool = False
    requires_reasoning: bool = False
    description: str = ""


@dataclass
class ChatMessage:
    """Represents a chat message"""
    content: str
    timestamp: datetime
    user_id: str = "default"
    session_id: str = "default"
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class RoutingResult:
    """Result of routing analysis"""
    handler: str
    intent_type: IntentType
    priority: RoutingPriority
    confidence: float
    context_data: Dict[str, Any]
    routing_metadata: Dict[str, Any]
    reasoning_chain: List[str]


class ChatRouter:
    """🎯 Intelligent Chat Router for Lyrixa with Aetherra Integration"""

    def __init__(self, workspace_path: str = "."):
        self.workspace_path = workspace_path
        self.routes: List[RouteDefinition] = []
        self.handlers: Dict[str, Callable] = {}
        self.context_cache: Dict[str, Any] = {}
        self.session_history: Dict[str, List[ChatMessage]] = {}

        # Initialize engines if available
        if HAS_AETHERRA_ENGINES:
            self.reasoning_engine = ReasoningEngine()
            self.introspection_controller = IntrospectionController()
            self.self_improvement_engine = SelfImprovementEngine()
            logger.info("✅ Chat Router initialized with Aetherra engines")
        else:
            self.reasoning_engine = ReasoningEngine()
            self.introspection_controller = IntrospectionController()
            self.self_improvement_engine = SelfImprovementEngine()
            logger.info("⚠️ Chat Router initialized with mock engines")

        # Router statistics
        self.stats = {
            "messages_processed": 0,
            "routes_matched": 0,
            "fallback_used": 0,
            "avg_routing_time": 0.0,
            "intent_distribution": {intent.value: 0 for intent in IntentType}
        }

        # Initialize default routes
        self._setup_default_routes()

        logger.info("🎯 Chat Router System initialized")

    def _setup_default_routes(self):
        """Setup default routing rules"""
        default_routes = [
            RouteDefinition(
                pattern=r"^(?:what|how|why|when|where|who|which).*\?$",
                handler="question_handler",
                intent_type=IntentType.QUESTION,
                priority=RoutingPriority.HIGH,
                requires_reasoning=True,
                description="Direct questions requiring reasoning"
            ),
            RouteDefinition(
                pattern=r"^(?:please|can you|could you|would you).*",
                handler="command_handler",
                intent_type=IntentType.COMMAND,
                priority=RoutingPriority.HIGH,
                requires_context=True,
                description="Polite requests and commands"
            ),
            RouteDefinition(
                pattern=r".*(?:think|reflect|analyze|consider|ponder).*",
                handler="reflection_handler",
                intent_type=IntentType.REFLECTION,
                priority=RoutingPriority.MEDIUM,
                requires_reasoning=True,
                requires_memory=True,
                description="Reflection and analysis requests"
            ),
            RouteDefinition(
                pattern=r".*(?:autonomous|self-improve|optimize|enhance).*",
                handler="autonomous_handler",
                intent_type=IntentType.AUTONOMOUS_REQUEST,
                priority=RoutingPriority.CRITICAL,
                requires_context=True,
                requires_memory=True,
                requires_reasoning=True,
                description="Autonomous system operations"
            ),
            RouteDefinition(
                pattern=r".*(?:status|health|system|performance).*",
                handler="system_handler",
                intent_type=IntentType.SYSTEM_QUERY,
                priority=RoutingPriority.MEDIUM,
                description="System status and health queries"
            ),
            RouteDefinition(
                pattern=r".*(?:create|generate|write|compose|design).*",
                handler="creativity_handler",
                intent_type=IntentType.CREATIVITY,
                priority=RoutingPriority.MEDIUM,
                requires_reasoning=True,
                description="Creative tasks and generation"
            ),
            RouteDefinition(
                pattern=r".*(?:solve|fix|debug|troubleshoot|resolve).*",
                handler="problem_solving_handler",
                intent_type=IntentType.PROBLEM_SOLVING,
                priority=RoutingPriority.HIGH,
                requires_reasoning=True,
                requires_context=True,
                description="Problem solving and debugging"
            ),
            RouteDefinition(
                pattern=r".*",
                handler="conversation_handler",
                intent_type=IntentType.CONVERSATION,
                priority=RoutingPriority.LOW,
                description="General conversation fallback"
            )
        ]

        for route in default_routes:
            self.add_route(route)

    def add_route(self, route: RouteDefinition):
        """Add a new route definition"""
        self.routes.append(route)
        logger.info(f"📍 Route added: {route.pattern} -> {route.handler}")

    def register_handler(self, name: str, handler: Callable):
        """Register a message handler"""
        self.handlers[name] = handler
        logger.info(f"🔌 Handler registered: {name}")

    async def route_message(self, message: ChatMessage) -> RoutingResult:
        """Route a message to the appropriate handler"""
        start_time = datetime.now()

        try:
            # Update session history
            self._update_session_history(message)

            # Analyze message intent
            intent_analysis = await self._analyze_intent(message)

            # Find matching route
            route = await self._find_matching_route(message, intent_analysis)

            # Build context data
            context_data = await self._build_context_data(message, route)

            # Create routing result
            result = RoutingResult(
                handler=route.handler,
                intent_type=route.intent_type,
                priority=route.priority,
                confidence=intent_analysis.get("confidence", 0.5),
                context_data=context_data,
                routing_metadata={
                    "route_pattern": route.pattern,
                    "route_description": route.description,
                    "requires_reasoning": route.requires_reasoning,
                    "requires_context": route.requires_context,
                    "requires_memory": route.requires_memory
                },
                reasoning_chain=intent_analysis.get("reasoning_chain", [])
            )

            # Update statistics
            self._update_stats(result, start_time)

            logger.info(f"📤 Message routed: {route.handler} (confidence: {result.confidence:.2f})")

            return result

        except Exception as e:
            logger.error(f"Error routing message: {e}")
            return await self._create_fallback_result(message)

    async def _analyze_intent(self, message: ChatMessage) -> Dict[str, Any]:
        """Analyze message intent using reasoning engine"""
        try:
            if self.reasoning_engine:
                reasoning_context = ReasoningContext(
                    query=f"What is the intent and purpose of this message? Message: '{message.content}'",
                    domain="intent_analysis",
                    context_data={
                        "message": message.content,
                        "timestamp": message.timestamp.isoformat(),
                        "user_id": message.user_id,
                        "session_id": message.session_id
                    },
                    constraints=["classify_intent", "determine_priority", "assess_complexity"],
                    objectives=["accurate_intent_classification", "routing_optimization"]
                )

                reasoning_result = await self.reasoning_engine.reason(reasoning_context)

                return {
                    "intent_analysis": reasoning_result.conclusion,
                    "alternatives": reasoning_result.alternatives,
                    "confidence": reasoning_result.confidence,
                    "reasoning_chain": [reasoning_result.conclusion]
                }
            else:
                return await self._basic_intent_analysis(message)

        except Exception as e:
            logger.error(f"Error analyzing intent: {e}")
            return await self._basic_intent_analysis(message)

    async def _basic_intent_analysis(self, message: ChatMessage) -> Dict[str, Any]:
        """Basic intent analysis without reasoning engine"""
        content = message.content.lower()

        # Simple keyword-based analysis
        if any(word in content for word in ["what", "how", "why", "when", "where", "who", "which"]):
            intent = "question"
            confidence = 0.7
        elif any(word in content for word in ["please", "can you", "could you", "would you"]):
            intent = "command"
            confidence = 0.6
        elif any(word in content for word in ["think", "reflect", "analyze", "consider"]):
            intent = "reflection"
            confidence = 0.5
        elif any(word in content for word in ["autonomous", "self-improve", "optimize"]):
            intent = "autonomous_request"
            confidence = 0.8
        else:
            intent = "conversation"
            confidence = 0.4

        return {
            "intent_analysis": f"Detected intent: {intent}",
            "alternatives": [intent],
            "confidence": confidence,
            "reasoning_chain": [f"Basic keyword analysis: {intent}"]
        }

    async def _find_matching_route(self, message: ChatMessage, intent_analysis: Dict[str, Any]) -> RouteDefinition:
        """Find the best matching route for the message"""
        best_match = None
        best_score = 0.0

        for route in self.routes:
            # Check pattern match
            pattern_match = re.search(route.pattern, message.content, re.IGNORECASE)
            if pattern_match:
                # Calculate match score
                score = self._calculate_route_score(route, intent_analysis, pattern_match)

                if score > best_score:
                    best_score = score
                    best_match = route

        # Use fallback if no good match found
        if best_match is None or best_score < 0.3:
            best_match = self._get_fallback_route()

        return best_match

    def _calculate_route_score(self, route: RouteDefinition, intent_analysis: Dict[str, Any], pattern_match) -> float:
        """Calculate route matching score"""
        score = 0.0

        # Base score from pattern match
        score += 0.3

        # Intent confidence bonus
        score += intent_analysis.get("confidence", 0.0) * 0.4

        # Priority bonus
        priority_scores = {
            RoutingPriority.CRITICAL: 0.3,
            RoutingPriority.HIGH: 0.2,
            RoutingPriority.MEDIUM: 0.1,
            RoutingPriority.LOW: 0.0,
            RoutingPriority.BACKGROUND: -0.1
        }
        score += priority_scores.get(route.priority, 0.0)

        # Pattern specificity bonus (more specific patterns get higher scores)
        if route.pattern != ".*":  # Not the fallback pattern
            score += 0.1

        return min(score, 1.0)

    def _get_fallback_route(self) -> RouteDefinition:
        """Get the fallback route"""
        return RouteDefinition(
            pattern=".*",
            handler="conversation_handler",
            intent_type=IntentType.CONVERSATION,
            priority=RoutingPriority.LOW,
            description="Fallback conversation handler"
        )

    async def _build_context_data(self, message: ChatMessage, route: RouteDefinition) -> Dict[str, Any]:
        """Build context data for the route"""
        context_data = {
            "message": message.content,
            "timestamp": message.timestamp.isoformat(),
            "user_id": message.user_id,
            "session_id": message.session_id,
            "metadata": message.metadata
        }

        # Add session history if required
        if route.requires_context:
            context_data["session_history"] = self._get_session_history(message.session_id)

        # Add system health if required
        if route.requires_context:
            try:
                health_data = self.introspection_controller.get_current_health()
                context_data["system_health"] = health_data
            except Exception as e:
                logger.warning(f"Could not get system health: {e}")

        # Add cached context
        if message.session_id in self.context_cache:
            context_data["cached_context"] = self.context_cache[message.session_id]

        return context_data

    def _update_session_history(self, message: ChatMessage):
        """Update session history with new message"""
        if message.session_id not in self.session_history:
            self.session_history[message.session_id] = []

        self.session_history[message.session_id].append(message)

        # Keep only last 50 messages per session
        if len(self.session_history[message.session_id]) > 50:
            self.session_history[message.session_id] = self.session_history[message.session_id][-50:]

    def _get_session_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get session history for context"""
        history = self.session_history.get(session_id, [])
        return [
            {
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "user_id": msg.user_id
            }
            for msg in history[-limit:]
        ]

    def _update_stats(self, result: RoutingResult, start_time: datetime):
        """Update routing statistics"""
        self.stats["messages_processed"] += 1
        self.stats["routes_matched"] += 1
        self.stats["intent_distribution"][result.intent_type.value] += 1

        # Update average routing time
        routing_time = (datetime.now() - start_time).total_seconds()
        current_avg = self.stats["avg_routing_time"]
        message_count = self.stats["messages_processed"]
        self.stats["avg_routing_time"] = (current_avg * (message_count - 1) + routing_time) / message_count

    async def _create_fallback_result(self, message: ChatMessage) -> RoutingResult:
        """Create fallback routing result"""
        self.stats["fallback_used"] += 1

        return RoutingResult(
            handler="conversation_handler",
            intent_type=IntentType.UNKNOWN,
            priority=RoutingPriority.LOW,
            confidence=0.1,
            context_data={
                "message": message.content,
                "timestamp": message.timestamp.isoformat(),
                "fallback_reason": "No suitable route found"
            },
            routing_metadata={
                "route_pattern": "fallback",
                "route_description": "Fallback handler",
                "requires_reasoning": False,
                "requires_context": False,
                "requires_memory": False
            },
            reasoning_chain=["Fallback routing used"]
        )

    async def process_message(self, content: str, user_id: str = "default", session_id: str = "default") -> Dict[str, Any]:
        """Process a message through the complete routing system"""
        try:
            # Create message object
            message = ChatMessage(
                content=content,
                timestamp=datetime.now(),
                user_id=user_id,
                session_id=session_id
            )

            # Route the message
            routing_result = await self.route_message(message)

            # Execute handler if available
            if routing_result.handler in self.handlers:
                handler = self.handlers[routing_result.handler]
                response = await handler(message, routing_result)
            else:
                response = await self._default_handler(message, routing_result)

            return {
                "response": response,
                "routing_result": routing_result,
                "success": True
            }

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": "I encountered an error processing your message. Please try again.",
                "error": str(e),
                "success": False
            }

    async def _default_handler(self, message: ChatMessage, routing_result: RoutingResult) -> str:
        """Default handler for unregistered routes"""
        return f"I understand you're asking about '{message.content}', but I don't have a specific handler for that type of request yet. I'm routing this as a {routing_result.intent_type.value} with {routing_result.confidence:.2f} confidence."

    def get_router_status(self) -> Dict[str, Any]:
        """Get current router status"""
        return {
            "has_aetherra_engines": HAS_AETHERRA_ENGINES,
            "routes_count": len(self.routes),
            "handlers_count": len(self.handlers),
            "active_sessions": len(self.session_history),
            "stats": self.stats.copy(),
            "routes": [
                {
                    "pattern": route.pattern,
                    "handler": route.handler,
                    "intent_type": route.intent_type.value,
                    "priority": route.priority.value,
                    "description": route.description
                }
                for route in self.routes
            ]
        }

    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get context for a specific session"""
        return {
            "session_id": session_id,
            "history_length": len(self.session_history.get(session_id, [])),
            "cached_context": self.context_cache.get(session_id, {}),
            "last_activity": self.session_history.get(session_id, [])[-1].timestamp.isoformat() if self.session_history.get(session_id) else None
        }

    def clear_session(self, session_id: str):
        """Clear session history and context"""
        if session_id in self.session_history:
            del self.session_history[session_id]
        if session_id in self.context_cache:
            del self.context_cache[session_id]
        logger.info(f"🧹 Session cleared: {session_id}")


# Factory function for easy integration
def create_chat_router(workspace_path: str = ".") -> ChatRouter:
    """Create and return a chat router instance"""
    return ChatRouter(workspace_path=workspace_path)


# Example handler functions
async def example_question_handler(message: ChatMessage, routing_result: RoutingResult) -> str:
    """Example handler for questions"""
    return f"You asked: '{message.content}'. This is a question with {routing_result.confidence:.2f} confidence."


async def example_command_handler(message: ChatMessage, routing_result: RoutingResult) -> str:
    """Example handler for commands"""
    return f"I understand you want me to: '{message.content}'. This is a command with {routing_result.confidence:.2f} confidence."


if __name__ == "__main__":
    # Example usage
    async def main():
        router = create_chat_router()

        # Register example handlers
        router.register_handler("question_handler", example_question_handler)
        router.register_handler("command_handler", example_command_handler)

        # Test messages
        test_messages = [
            "What is the meaning of life?",
            "Please help me with this problem",
            "Can you analyze this situation?",
            "How does autonomous improvement work?",
            "Hello there!"
        ]

        for msg in test_messages:
            result = await router.process_message(msg)
            print(f"Message: {msg}")
            print(f"Response: {result['response']}")
            print(f"Intent: {result['routing_result'].intent_type.value}")
            print(f"Confidence: {result['routing_result'].confidence:.2f}")
            print("-" * 50)

    asyncio.run(main())
