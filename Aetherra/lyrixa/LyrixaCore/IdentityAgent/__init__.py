"""
IdentityAgent - Core Identity Management System
Manages beliefs, personal history, and dynamic self-model for unified cognitive stack.
"""

from .core_beliefs import CoreBeliefs
from .personal_history import EventType, PersonalHistory
from .self_model import SelfModel

__all__ = ["CoreBeliefs", "PersonalHistory", "EventType", "SelfModel"]
