"""
NeuroCode Parser Subsystem
========================

Centralized parser functionality for the NeuroCode language.
This module provides a clean API for all parsing operations.
"""

from .enhanced_parser import EnhancedParser
from .grammar import NEUROCODE_GRAMMAR, NeuroCodeTransformer
from .intent_parser import IntentParser
from .natural_compiler import NaturalCompiler
from .parser import NeuroCodeParser

__all__ = [
    "NEUROCODE_GRAMMAR",
    "NeuroCodeTransformer",
    "NeuroCodeParser",
    "EnhancedParser",
    "IntentParser",
    "NaturalCompiler",
]


def create_parser(enhanced=True):
    """Create a NeuroCode parser instance."""
    if enhanced:
        return EnhancedParser()
    return NeuroCodeParser()


def parse_code(code: str, enhanced=True):
    """Parse NeuroCode source code."""
    parser = create_parser(enhanced)
    return parser.parse(code)


def parse_intent(text: str):
    """Parse natural language intent."""
    intent_parser = IntentParser()
    return intent_parser.parse(text)
