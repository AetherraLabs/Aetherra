"""
NeuroCode Core Module
"""

# Make key classes available at package level
try:
    from .chat_router import NeuroCodeChatRouter
    from .interpreter import NeuroCodeInterpreter
    from .memory import NeuroMemory
    
    __all__ = ['NeuroCodeInterpreter', 'NeuroMemory', 'NeuroCodeChatRouter']
except ImportError:
    # If relative imports fail, the modules can still be imported individually
    pass