# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🤖 Lyrixa AI Agent
==================

Primary AI agent for handling intelligent conversations and responses
using OpenAI or other AI models.
"""

# Standard library imports
import os
from typing import Any, Dict, List, Optional

# Persistent memory
try:
    # Aetherra imports
    from aetherra_persistent_memory import get_persistent_memory_system
except Exception:
    get_persistent_memory_system = None

# Local imports
from .agent_base import AgentBase


class LyrixaAI(AgentBase):
    """
    Main AI conversation agent for Lyrixa.

    Handles intelligent responses, conversation context, and
    integration with AI models like OpenAI GPT.
    """

    def __init__(self, model: str = "gpt-3.5-turbo", name: Optional[str] = None):
        """
        Initialize the Lyrixa AI agent.

        Args:
            model: AI model to use (e.g., "gpt-3.5-turbo", "gpt-4")
            name: Optional agent name
        """
        super().__init__("lyrixa_ai", name)
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.conversation_history = []
        self.max_history = 50  # Maximum conversation turns to remember

        # Check if API key is available
        if self.api_key:
            self.update_status("ready", {"model": model, "api_available": True})
        else:
            self.update_status(
                "warning",
                {"model": model, "api_available": False, "message": "No API key found"},
            )

    def can_handle(self, request_type: str) -> bool:
        """Check if this agent can handle the request type."""
        return request_type in [
            "chat",
            "conversation",
            "ai_response",
            "intelligent_query",
        ]

    def get_capabilities(self) -> List[str]:
        """Get list of AI capabilities."""
        capabilities = super().get_capabilities()
        capabilities.extend(
            [
                "natural_language_processing",
                "conversation_management",
                "intelligent_responses",
                "context_awareness",
                "multi_turn_dialogue",
            ]
        )
        return capabilities

    async def _handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle AI conversation requests.

        Args:
            request: Request containing message and context

        Returns:
            AI response dictionary
        """
        message = request.get("message", "")
        context = request.get("context", {})

        if not message:
            return {
                "success": False,
                "error": "No message provided",
                "agent_id": self.agent_id,
            }

        # Ownership guard: never speculate; consult persistent memory first
        if self._is_ownership_query(message):
            reply = await self._ownership_reply(message)
            self._add_to_history("assistant", reply)
            return {
                "success": True,
                "response": reply,
                "agent_id": self.agent_id,
                "model": self.model,
                "conversation_id": context.get("conversation_id"),
                "metadata": {"guard": "ownership", "provider": "memory"},
            }

        # Add to conversation history
        self._add_to_history("user", message, context)

        # Generate AI response
        if self.api_key:
            response_text = await self._generate_ai_response(message, context)
        else:
            response_text = await self._generate_fallback_response(message, context)

        # Add response to history
        self._add_to_history("assistant", response_text)

        return {
            "success": True,
            "response": response_text,
            "agent_id": self.agent_id,
            "model": self.model,
            "conversation_id": context.get("conversation_id"),
            "metadata": {
                "response_length": len(response_text),
                "history_length": len(self.conversation_history),
            },
        }

    async def _generate_ai_response(self, message: str, context: Dict[str, Any]) -> str:
        """
        Generate response using AI model.

        Args:
            message: User message
            context: Conversation context

        Returns:
            AI-generated response
        """
        try:
            # Third party imports
            import openai

            # Initialize OpenAI client
            client = openai.OpenAI(api_key=self.api_key)

            # Prepare conversation history for context
            messages = []

            # Add system message for Lyrixa personality
            messages.append(
                {
                    "role": "system",
                    "content": (
                        "You are Lyrixa, an advanced AI assistant within the Aetherra AI OS."
                        " Be helpful and concise. If asked who owns Aetherra or Aetherra Labs,"
                        " do not speculate; if no verified record is available, respond exactly:"
                        " 'I don't have a record of ownership.'"
                    ),
                }
            )

            # Add recent conversation history for context
            recent_history = (
                self.conversation_history[-5:] if self.conversation_history else []
            )
            for entry in recent_history:
                if entry["role"] in ["user", "assistant"]:
                    messages.append(
                        {"role": entry["role"], "content": entry["content"]}
                    )

            # Add current user message
            messages.append({"role": "user", "content": message})

            # Make API call
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1,
            )

            ai_response = response.choices[0].message.content
            if ai_response:
                ai_response = ai_response.strip()
            else:
                ai_response = (
                    "I apologize, but I couldn't generate a response at this time."
                )
            return ai_response

        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return await self._generate_fallback_response(message, context)

    async def _generate_fallback_response(
        self, message: str, context: Dict[str, Any]
    ) -> str:
        """
        Generate fallback response when AI is unavailable.

        Args:
            message: User message
            context: Conversation context

        Returns:
            Fallback response
        """
        # Simple rule-based responses for when AI is unavailable
        message_lower = message.lower()

        if self._is_ownership_query(message):
            return "I don't have a record of ownership."
        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            return "Hello! I'm Lyrixa AI. How can I assist you today?"
        elif any(word in message_lower for word in ["help", "what can you do"]):
            return "I'm here to help with conversations and questions. I can discuss various topics and assist with tasks."
        elif "?" in message:
            return f"That's an interesting question about '{message[:30]}...' Let me think about that."
        else:
            return f"I understand you mentioned '{message[:30]}...' Could you tell me more about what you'd like to know?"

    def _add_to_history(
        self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ):
        """Add message to conversation history."""
        entry = {
            "role": role,
            "content": content,
            "timestamp": self.last_activity.isoformat(),
        }
        if metadata:
            # Store as string to avoid strict type complaints
            entry["metadata"] = str(metadata)

        self.conversation_history.append(entry)

        # Trim history if too long
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history :]

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation."""
        return {
            "total_messages": len(self.conversation_history),
            "model": self.model,
            "api_available": bool(self.api_key),
            "last_messages": self.conversation_history[-5:]
            if self.conversation_history
            else [],
        }

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        self.update_status("ready", {"history_cleared": True})

    # --- Ownership guard helpers ---
    def _is_ownership_query(self, message: str) -> bool:
        m = (message or "").lower()
        keys = [
            "who owns aetherra",
            "who owns aetherra labs",
            "owner of aetherra",
            "owner of aetherra labs",
            "ownership of aetherra",
            "ownership of aetherra labs",
            "who founded aetherra",
            "who founded aetherra labs",
        ]
        return any(k in m for k in keys)

    async def _ownership_reply(self, message: str) -> str:
        try:
            if not get_persistent_memory_system:
                return "I don't have a record of ownership."
            pmem = await get_persistent_memory_system()
            # Try verified facts by tag
            facts = await pmem.recall_by_tag("ownership", limit=5)
            verified = [f for f in facts if f.get("verified")]
            if not verified:
                cands = await pmem.retrieve(
                    "Aetherra Labs ownership", limit=5, memory_type="fact"
                )
                verified = [c for c in cands if c.get("verified")]
            if verified:
                verified.sort(key=lambda x: x.get("created_at", ""), reverse=True)
                content = str(verified[0].get("content") or "")
                return content or "I don't have a record of ownership."
            return "I don't have a record of ownership."
        except Exception:
            return "I don't have a record of ownership."
