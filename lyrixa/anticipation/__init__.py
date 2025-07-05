"""
🔮 LYRIXA ANTICIPATION ENGINE - PHASE 2
=====================================

Proactive AI assistant that anticipates user needs and provides
intelligent suggestions before they're explicitly requested.
"""

__version__ = "2.0.0"
__author__ = "Aetherra AI Systems"

from .context_analyzer import ContextAnalyzer
from .suggestion_generator import SuggestionGenerator  
from .proactive_assistant import ProactiveAssistant

__all__ = [
    "ContextAnalyzer",
    "SuggestionGenerator", 
    "ProactiveAssistant"
]
