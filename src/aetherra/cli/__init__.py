"""
Aetherra CLI Package
Command-line interfaces for all Aetherra functionality.
"""

# Always available basic CLI
try:
    from .basic import main as run_basic_cli

    BASIC_CLI_AVAILABLE = True
except ImportError:
    BASIC_CLI_AVAILABLE = False
    run_basic_cli = None

try:
    from .demo import main as run_demo
    from .main import AetherraPersonaInterface

    CLI_DEMO_AVAILABLE = True
except ImportError:
    CLI_DEMO_AVAILABLE = False
    run_demo = None
    AetherraPersonaInterface = None

try:
    from .persona import PersonaCLI

    PERSONA_CLI_AVAILABLE = True
except ImportError:
    PERSONA_CLI_AVAILABLE = False
    PersonaCLI = None

# Plugin CLI uses functions, not classes

__all__ = [
    "run_basic_cli",
    "run_demo",
    "AetherraPersonaInterface",
    "PersonaCLI",
    "BASIC_CLI_AVAILABLE",
    "CLI_DEMO_AVAILABLE",
    "PERSONA_CLI_AVAILABLE",
]

__version__ = "1.0.0"
