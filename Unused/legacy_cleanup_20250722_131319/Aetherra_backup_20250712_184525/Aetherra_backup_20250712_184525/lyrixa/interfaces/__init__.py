#!/usr/bin/env python3
"""
🔗 LYRIXA INTERFACES PACKAGE
============================

Main interfaces package for Lyrixa AI Assistant.
Provides all interface modules for easy import and usage.
"""

# Import main classes from each interface module
try:
    from .lyrixa import LyrixaCore, get_lyrixa_instance, initialize_lyrixa
    from .lyrixa_agent_integration import LyrixaAgentInterface
    from .lyrixa_assistant import LyrixaAssistant, create_assistant, quick_chat
    from .lyrixa_assistant_console import LyrixaConsole

    __all__ = [
        # Core interface
        "LyrixaCore",
        "get_lyrixa_instance",
        "initialize_lyrixa",
        # Agent integration
        "LyrixaAgentInterface",
        # Assistant interface
        "LyrixaAssistant",
        "create_assistant",
        "quick_chat",
        # Console interface
        "LyrixaConsole",
    ]

except ImportError as e:
    # If imports fail, still provide the module but log the error
    print(f"Warning: Some Lyrixa interfaces could not be imported: {e}")
    __all__ = []
