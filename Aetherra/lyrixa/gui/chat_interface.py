#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
[COSMOS] Phase 6: Chat Interface (extracted)
===========================================

Provides full conversational AI integration for the Phase 6 GUI.
Extracted from phase6_personality.py to keep modules focused and smaller.
"""

# Standard library imports
import json
import logging
from dataclasses import asdict
from datetime import datetime
from typing import Any, Protocol, runtime_checkable

# Third party imports
from PySide6.QtCore import QObject, Signal, Slot

logger = logging.getLogger(__name__)


@runtime_checkable
class SupportsChatManager(Protocol):
    ai: Any

    def process_chat_sync(
        self, user_message: str
    ) -> str:  # pragma: no cover - protocol
        ...


class ChatInterface(QObject):
    """
    Full conversational AI integration for Phase 6 chat interface
    """

    # Signals
    messageReceived = Signal(str)  # User message
    responseReady = Signal(str)  # AI response ready
    stateChanged = Signal(str)  # Chat state changes

    def __init__(self, personality_manager: SupportsChatManager, parent=None):
        super().__init__(parent)
        self.personality_manager = personality_manager
        self.ai = personality_manager.ai
        self.conversation_history = []

        logger.info("[PHASE6] ChatInterface initialized")

    @Slot(str, result=str)
    def send_message(self, user_message: str) -> str:
        """Send user message and get AI response"""
        try:
            # Emit that we received the message
            self.messageReceived.emit(user_message)

            # Process through personality manager
            response = self.personality_manager.process_chat_sync(user_message)

            # Store in conversation history
            self.conversation_history.append(
                {
                    "user_message": user_message,
                    "ai_response": response,
                    "timestamp": datetime.now(),
                }
            )

            # Emit the response
            self.responseReady.emit(response)

            return response

        except Exception as e:
            logger.error(f"[PHASE6] Chat interface error: {e}")
            error_response = "I apologize, but I'm having difficulty processing that request right now."
            self.responseReady.emit(error_response)
            return error_response

    @Slot(result=str)
    def get_personality_state(self) -> str:
        """Get current personality state as JSON"""
        try:
            state = asdict(self.ai.personality_state)
            # Ensure timestamp is JSON-serializable
            if isinstance(state.get("timestamp"), datetime):
                state["timestamp"] = state["timestamp"].isoformat()
            return json.dumps(state)
        except Exception as e:
            logger.error(f"[PHASE6] Failed to get personality state: {e}")
            return "{}"

    @Slot(result=str)
    def get_conversation_history(self) -> str:
        """Get recent conversation history"""
        try:
            history = []
            for msg in self.conversation_history[-10:]:  # Last 10 messages
                msg_dict = dict(msg) if isinstance(msg, dict) else msg
                if "timestamp" in msg_dict and hasattr(
                    msg_dict["timestamp"], "isoformat"
                ):
                    msg_dict["timestamp"] = msg_dict["timestamp"].isoformat()
                history.append(msg_dict)
            return json.dumps(history)
        except Exception as e:
            logger.error(f"[PHASE6] Failed to get conversation history: {e}")
            return "[]"


__all__ = [
    "ChatInterface",
]
