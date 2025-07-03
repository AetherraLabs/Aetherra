"""
NeuroCode Core Module
"""

# Make key classes available at package level
try:
    from .chat_router import AetherraChatRouter
    from .interpreter import AetherraInterpreter
    from .aetherra_memory import AetherraMemory

    __all__ = ["AetherraInterpreter", "AetherraMemory", "AetherraChatRouter"]
except ImportError:
    # If relative imports fail, the modules can still be imported individually
    pass
