"""
Lyrixa Models Package
====================

LLM abstraction layer with support for OpenAI, local models, and dynamic routing.
"""

from .local_model import LocalModel
from .model_router import ModelRouter
from .openai_model import OpenAIModel

__all__ = ["OpenAIModel", "LocalModel", "ModelRouter"]


# Lazy loading of instances to avoid initialization issues during import
def get_router():
    """Get the global router instance (lazy loading)"""
    from .model_router import router

    return router


def get_default_openai_model():
    """Get the default OpenAI model instance (lazy loading)"""
    from .openai_model import default_openai_model

    return default_openai_model
