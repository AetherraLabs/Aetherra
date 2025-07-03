"""
Aetherra Core Package
Core engine and runtime components.
"""

from .parser.parser import AetherraParser


# Create create_parser function
def create_parser():
    """Create an Aetherra parser function.
    Returns a function that takes code and returns AST.
    """

    def parse_function(code: str):
        from .parser.parser import AetherraLexer

        lexer = AetherraLexer(code)
        tokens = lexer.tokenize()
        parser = AetherraParser(tokens)
        return parser.parse()

    return parse_function


__all__ = [
    "AetherraInterpreter",
    "AetherraMemory",
    "AetherraParser",
    "create_interpreter",
    "create_memory_system",
    "create_parser",
]

__version__ = "1.0.0"
