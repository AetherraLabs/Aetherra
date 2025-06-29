<<<<<<< HEAD
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
=======
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
>>>>>>> 20a510e90c83aa50461841f557e9447d03056c8d
    pass