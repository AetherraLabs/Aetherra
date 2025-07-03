"""
NeuroCode AST Subsystem
======================

Abstract Syntax Tree components for NeuroCode.
Handles AST node creation, parsing, and optimization.
Note: Renamed from 'ast' to 'neuro_ast' to avoid conflicts with Python's built-in ast module.
"""

from .parser import NeuroASTParser

__all__ = ["NeuroASTParser"]
