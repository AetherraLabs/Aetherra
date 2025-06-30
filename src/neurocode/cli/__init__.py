"""
NeuroCode CLI Package
Command-line interfaces for all NeuroCode functionality.
"""

from .demo import main as run_demo
from .main import NeuroCodePersonaInterface
from .persona import PersonaCLI

# Plugin CLI uses functions, not classes

__all__ = [
    "run_demo",
    "NeuroCodePersonaInterface",
    "PersonaCLI",
]

__version__ = "1.0.0"
