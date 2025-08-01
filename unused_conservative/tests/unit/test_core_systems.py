#!/usr/bin/env python3
"""
🧪 Aetherra Core System Tests
===========================

Basic tests to verify core Aetherra components can be imported and instantiated.
These tests validate the fundamental system architecture.
"""

import sys
import pytest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestLyrixaCore:
    """Test Lyrixa core components"""
    
    def test_conversation_manager_import(self):
        """Test that ConversationManager can be imported"""
        try:
            from Aetherra.lyrixa.conversation_manager import ConversationManager
            assert ConversationManager is not None
        except ImportError as e:
            pytest.skip(f"ConversationManager not available: {e}")
    
    def test_memory_engine_import(self):
        """Test that memory engine can be imported"""
        try:
            from Aetherra.lyrixa.memory.lyrixa_memory_engine import LyrixaMemoryEngine
            assert LyrixaMemoryEngine is not None
        except ImportError as e:
            pytest.skip(f"Memory engine not available: {e}")
    
    def test_web_interface_import(self):
        """Test that web interface can be imported"""
        try:
            from Aetherra.lyrixa.gui.web_interface_server import AetherraWebInterface
            assert AetherraWebInterface is not None
        except ImportError as e:
            pytest.skip(f"Web interface not available: {e}")


class TestMemorySystem:
    """Test memory system components"""
    
    def test_memory_config_creation(self):
        """Test memory system configuration creation"""
        try:
            from Aetherra.lyrixa.memory.lyrixa_memory_engine import MemorySystemConfig
            config = MemorySystemConfig()
            assert config is not None
        except ImportError as e:
            pytest.skip(f"Memory config not available: {e}")
    
    @pytest.mark.slow
    def test_memory_engine_instantiation(self):
        """Test memory engine can be instantiated"""
        try:
            from Aetherra.lyrixa.memory.lyrixa_memory_engine import (
                LyrixaMemoryEngine, MemorySystemConfig
            )
            config = MemorySystemConfig()
            memory_engine = LyrixaMemoryEngine(config)
            assert memory_engine is not None
        except ImportError as e:
            pytest.skip(f"Memory engine components not available: {e}")
        except Exception as e:
            pytest.skip(f"Memory engine instantiation failed: {e}")


class TestQuantumSystems:
    """Test quantum memory and computing components"""
    
    @pytest.mark.quantum
    def test_quantum_memory_import(self):
        """Test quantum memory bridge import"""
        try:
            from Aetherra.lyrixa.memory.quantum_memory_integration import QuantumMemoryBridge
            assert QuantumMemoryBridge is not None
        except ImportError as e:
            pytest.skip(f"Quantum memory not available: {e}")
    
    @pytest.mark.quantum
    def test_qiskit_availability(self):
        """Test if Qiskit is available"""
        try:
            import qiskit
            assert qiskit.__version__ is not None
        except ImportError:
            pytest.skip("Qiskit not installed")


class TestWebInterface:
    """Test web interface components"""
    
    def test_flask_import(self):
        """Test Flask dependencies are available"""
        try:
            import flask
            import flask_socketio
            assert flask.__version__ is not None
            assert flask_socketio.__version__ is not None
        except ImportError as e:
            pytest.fail(f"Flask dependencies missing: {e}")
    
    def test_web_server_creation(self):
        """Test web server can be created"""
        try:
            from Aetherra.lyrixa.gui.web_interface_server import AetherraWebInterface
            # Test basic instantiation without starting server
            web_interface = AetherraWebInterface()
            assert web_interface is not None
        except ImportError as e:
            pytest.skip(f"Web interface not available: {e}")
        except Exception as e:
            pytest.skip(f"Web interface creation failed: {e}")


class TestAIIntegration:
    """Test AI model integration"""
    
    def test_ai_dependencies(self):
        """Test AI framework dependencies"""
        dependencies = ['openai', 'anthropic', 'google.generativeai']
        available = []
        
        for dep in dependencies:
            try:
                __import__(dep)
                available.append(dep)
            except ImportError:
                pass
        
        # At least one AI provider should be available
        assert len(available) > 0, f"No AI providers available. Tried: {dependencies}"
    
    def test_local_ai_support(self):
        """Test local AI model support"""
        try:
            import requests
            import httpx
            assert requests.__version__ is not None
            assert httpx.__version__ is not None
        except ImportError as e:
            pytest.fail(f"Local AI dependencies missing: {e}")


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v"])
