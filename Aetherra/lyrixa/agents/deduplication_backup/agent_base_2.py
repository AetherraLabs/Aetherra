from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class AgentResponse:
    """Standard response format for all agents"""

    content: str
    confidence: float
    agent_name: str
    metadata: Dict[str, Any]
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class AgentBase(ABC):
    """Base class for all Lyrixa agents"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.status = "initialized"
        self.last_activity = datetime.now()
        self.error_count = 0
        self.success_count = 0
        self.active_tasks = {}

    def log(self, message: str, level: str = "INFO"):
        """Log agent activity"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{self.name}] {level}: {message}")

    async def initialize(self):
        """Initialize the agent - override in subclasses"""
        self.log(f"Initializing {self.name}")
        self.status = "ready"

    @abstractmethod
    async def process_input(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Process input and return response - must be implemented by subclasses"""
        pass

    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "last_activity": self.last_activity.isoformat(),
            "error_count": self.error_count,
            "success_count": self.success_count,
            "active_tasks": len(self.active_tasks),
        }

    async def shutdown(self):
        """Shutdown the agent gracefully"""
        self.log(f"Shutting down {self.name}")
        self.status = "shutdown"
        self.active_tasks.clear()

    def _update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()

    def _increment_success(self):
        """Increment success counter"""
        self.success_count += 1
        self._update_activity()

    def _increment_error(self):
        """Increment error counter"""
        self.error_count += 1
        self._update_activity()
