"""
AetherraCode Core Module
"""

# Make key classes available at package level
try:
    from .aetherra_parser import compile_aetherra, parse_aetherra
    from .agent import AetherraAgent
    from .ast_parser import AetherraASTParser
    from .intelligence import (
        justify_self_editing_decision,
        memory_driven_code_suggestion,
        provide_adaptive_suggestions,
        suggest_system_evolution,
    )

    __all__ = [
        "AetherraAgent",
        "AetherraASTParser",
        "parse_aetherra",
        "compile_aetherra",
        "justify_self_editing_decision",
        "memory_driven_code_suggestion",
        "provide_adaptive_suggestions",
        "suggest_system_evolution",
    ]
except ImportError:
    # If relative imports fail, the modules can still be imported individually
    __all__ = []
