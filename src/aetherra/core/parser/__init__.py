"""
Aetherra Parser Subsystem
========================

Centralized parser functionality for the Aetherra language.
This module provides a clean API for all parsing operations.
"""

from .parser import AetherraLexer, AetherraParser

__all__ = [
    "Aetherra_GRAMMAR",
    "AetherraTransformer",
    "AetherraParser",
    "AetherraLexer",
    "create_parser",
    "parse_code",
    "parse_intent",
]


def create_parser(enhanced=True):
    """Create a Aetherra parser instance.

    Returns a function that can parse code, since the actual parser
    needs tokens which come from lexing the code first.
    """

    def parse_function(code: str):
        # Tokenize the code first
        lexer = AetherraLexer(code)
        tokens = lexer.tokenize()

        # Create parser with tokens
        parser = AetherraParser(tokens)
        return parser.parse()

    return parse_function


def parse_code(code: str, enhanced=True):
    """Parse Aetherra source code."""
    parser_func = create_parser(enhanced)
    return parser_func(code)


def parse_intent(text: str):
    """Parse natural language intent.

    This is a simplified intent parser that returns the text as-is
    until a full intent parser is implemented.
    """
    return {"type": "intent", "text": text}
