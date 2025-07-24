"""
Aetherra & Lyrixa Developer Tools - Knowledge Package

This package provides knowledge management and documentation synchronization tools.
"""

# Import knowledge tools with error handling
try:
    from .sync import KnowledgeBaseSync, DocumentInfo, SyncStats
    __all__ = ['KnowledgeBaseSync', 'DocumentInfo', 'SyncStats']
except ImportError as e:
    print(f"Warning: Could not import knowledge sync: {e}")
    __all__ = []

# Package version
__version__ = "1.0.0"
