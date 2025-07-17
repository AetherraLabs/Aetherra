"""
Aetherra Security Module
========================

This module provides comprehensive security features for Aetherra:
- API key management with encryption
- Memory leak detection and monitoring
- Security auditing and logging
- Automatic cleanup and optimization
"""

from .api_key_manager import APIKeyManager, get_api_key_manager
from .memory_manager import MemoryManager, get_memory_manager
from .security_system import (
    AetherraSecuritySystem,
    SecurityConfig,
    secure_api_call,
    get_security_system,
    initialize_aetherra_security
)

__all__ = [
    'APIKeyManager',
    'get_api_key_manager',
    'MemoryManager', 
    'get_memory_manager',
    'AetherraSecuritySystem',
    'SecurityConfig',
    'secure_api_call',
    'get_security_system',
    'initialize_aetherra_security'
]

__version__ = "1.0.0"
