"""
NeuroCode Core Package
Core engine and runtime components.
"""

from .interpreter import create_interpreter
from .interpreter.base import NeuroCodeInterpreter
from .memory import create_memory_system
from .memory.base import NeuroMemory as NeuroCodeMemory
from .parser.parser import NeuroCodeParser


# Create create_parser function
def create_parser():
    """Create a NeuroCode parser function.
    Returns a function that takes code and returns AST.
    """

    def parse_function(code: str):
        from .parser.parser import NeuroCodeLexer

        lexer = NeuroCodeLexer(code)
        tokens = lexer.tokenize()
        parser = NeuroCodeParser(tokens)
        return parser.parse()

    return parse_function


__all__ = [
    "NeuroCodeInterpreter",
    "NeuroCodeMemory",
    "NeuroCodeParser",
    "create_interpreter",
    "create_memory_system",
    "create_parser",
]

__version__ = "1.0.0"
