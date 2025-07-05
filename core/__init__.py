"""
AetherraCode Core Module
"""

# Make key classes available at package level
try:

    __all__ = ["AetherraInterpreter", "AetherraMemory", "AetherraChatRouter"]
except ImportError:
    # If relative imports fail, the modules can still be imported individually
    pass
