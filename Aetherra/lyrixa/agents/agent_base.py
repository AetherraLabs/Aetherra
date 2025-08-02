"""
🤖 Agent Base Class
===================

Base class for all Lyrixa agents providing core functionality
and interface contracts.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional


class AgentBase:
    """
    Base class for all Lyrixa agents.

    Provides core functionality including:
    - Agent identification and metadata
    - Status management
    - Asynchronous operation support
    - Event handling
    """

    def __init__(self, agent_type: str = "base", name: Optional[str] = None):
        """
        Initialize the agent.

        Args:
            agent_type: Type identifier for this agent
            name: Optional human-readable name
        """
        self.agent_id = str(uuid.uuid4())
        self.agent_type = agent_type
        self.name = name or f"{agent_type}_{self.agent_id[:8]}"
        self.status = "initialized"
        self.created_at = datetime.now()
        self.last_activity = self.created_at
        self.metadata = {}

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metadata."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "name": self.name,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "metadata": self.metadata,
        }

    def update_status(self, status: str, metadata: Optional[Dict[str, Any]] = None):
        """Update agent status and optional metadata."""
        self.status = status
        self.last_activity = datetime.now()
        if metadata:
            self.metadata.update(metadata)

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming request.

        This is the main entry point for agent interactions.
        Override in subclasses to implement specific behavior.

        Args:
            request: Request data dictionary

        Returns:
            Response dictionary
        """
        self.update_status("processing")

        try:
            response = await self._handle_request(request)
            self.update_status("ready")
            return response
        except Exception as e:
            self.update_status("error", {"last_error": str(e)})
            return {"success": False, "error": str(e), "agent_id": self.agent_id}

    async def _handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal request handler - override in subclasses.

        Args:
            request: Request data dictionary

        Returns:
            Response dictionary
        """
        return {
            "success": True,
            "message": f"Request handled by {self.name}",
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
        }

    def can_handle(self, request_type: str) -> bool:
        """
        Check if this agent can handle a specific request type.

        Override in subclasses to implement capability checking.

        Args:
            request_type: Type of request to check

        Returns:
            True if agent can handle this request type
        """
        return False

    def get_capabilities(self) -> List[str]:
        """
        Get list of capabilities this agent provides.

        Override in subclasses to list specific capabilities.

        Returns:
            List of capability strings
        """
        return ["status_check", "basic_processing"]

    def cleanup(self):
        """Cleanup agent resources."""
        self.update_status("shutdown")

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.agent_id[:8]}, type={self.agent_type}, status={self.status})>"
