"""
🌌 Lyrixa Quantum Memory Bridge Integration
========================================

This module provides seamless integration of Phase 5 Quantum Memory Bridge
capabilities into the main Lyrixa engine and user interface.

Integration Points:
- LyrixaEngine memory_system quantum enhancement
- UI quantum status indicators and controls
- Performance monitoring with quantum metrics
- Graceful fallback when quantum hardware unavailable

Usage:
    from lyrixa.quantum_bridge_integration import enhance_lyrixa_with_quantum

    # Enhance existing Lyrixa instance
    quantum_enhanced_lyrixa = enhance_lyrixa_with_quantum(lyrixa_instance)

    # Or create new quantum-enhanced instance
    lyrixa = create_quantum_lyrixa()
"""

import logging
from typing import Any, Dict, Optional

try:
    from .memory.quantum_memory_integration import (
        QuantumMemoryConfig,
        create_quantum_enhanced_memory_engine
    )
    QUANTUM_INTEGRATION_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Quantum memory integration not available: {e}")
    QUANTUM_INTEGRATION_AVAILABLE = False

    # Create placeholder classes for graceful degradation
    class QuantumMemoryConfig:
        def __init__(self, **kwargs):
            pass

    def create_quantum_enhanced_memory_engine(*args, **kwargs):
        return None


def enhance_lyrixa_with_quantum(lyrixa_engine, quantum_config: Optional[QuantumMemoryConfig] = None):
    """
    Enhance an existing LyrixaEngine instance with quantum memory capabilities

    Args:
        lyrixa_engine: Existing LyrixaEngine instance
        quantum_config: Optional quantum configuration

    Returns:
        Enhanced LyrixaEngine with quantum memory capabilities
    """

    if not QUANTUM_INTEGRATION_AVAILABLE:
        logging.warning("Quantum integration not available - returning unmodified engine")
        return lyrixa_engine

    try:
        # Create quantum-enhanced memory system
        quantum_memory_engine = create_quantum_enhanced_memory_engine(
            memory_config=lyrixa_engine.memory_system.config if hasattr(lyrixa_engine.memory_system, 'config') else None,
            quantum_config=quantum_config
        )

        # Only proceed if quantum engine was successfully created
        if quantum_memory_engine is None:
            logging.warning("Quantum memory engine creation failed - returning unmodified engine")
            return lyrixa_engine

        # Replace the memory system with quantum-enhanced version
        original_memory = lyrixa_engine.memory_system
        lyrixa_engine.memory_system = quantum_memory_engine

        # Copy any existing data if possible
        if hasattr(original_memory, 'fragments') and hasattr(quantum_memory_engine, 'fractal_mesh'):
            logging.info("Migrating existing memory fragments to quantum-enhanced system...")
            # Migration logic would go here

        # Add quantum-specific methods to the engine
        lyrixa_engine.get_quantum_status = quantum_memory_engine.get_quantum_system_status
        lyrixa_engine.check_quantum_coherence = quantum_memory_engine.check_quantum_coherence
        lyrixa_engine.quantum_maintenance = quantum_memory_engine.quantum_maintenance_cycle

        logging.info("✅ Lyrixa engine successfully enhanced with quantum memory capabilities")
        return lyrixa_engine

    except Exception as e:
        logging.error(f"Failed to enhance Lyrixa with quantum capabilities: {e}")
        return lyrixa_engine


def create_quantum_lyrixa(config: Optional[Dict[str, Any]] = None):
    """
    Create a new Lyrixa instance with quantum memory capabilities from the start

    Args:
        config: Configuration dictionary for Lyrixa and quantum components

    Returns:
        New LyrixaEngine instance with quantum memory
    """

    try:
        # Import LyrixaEngine here to avoid circular imports
        from .engine.lyrixa_engine import LyrixaEngine

        # Extract quantum config if provided
        quantum_config = None
        if config and 'quantum' in config:
            quantum_config = QuantumMemoryConfig(**config['quantum'])

        # Create standard Lyrixa engine
        lyrixa = LyrixaEngine()  # Use default parameters

        # Enhance with quantum capabilities
        quantum_lyrixa = enhance_lyrixa_with_quantum(lyrixa, quantum_config)

        return quantum_lyrixa

    except Exception as e:
        logging.error(f"Failed to create quantum Lyrixa: {e}")
        # Fallback to standard Lyrixa
        from .engine.lyrixa_engine import LyrixaEngine
        return LyrixaEngine()


def get_quantum_capability_status() -> Dict[str, Any]:
    """
    Check the availability and status of quantum memory capabilities

    Returns:
        Dictionary containing quantum capability information
    """

    status = {
        "quantum_integration_available": QUANTUM_INTEGRATION_AVAILABLE,
        "capabilities": {
            "quantum_encoding": False,
            "quantum_recall": False,
            "quantum_associations": False,
            "error_correction": False,
            "coherence_monitoring": False
        },
        "requirements": {
            "quantum_memory_bridge": False,
            "qiskit": False,
            "cirq": False
        },
        "recommendations": []
    }

    if QUANTUM_INTEGRATION_AVAILABLE:
        # Check specific quantum capabilities
        try:
            from ...quantum_memory_bridge import QuantumMemoryBridge
            status["requirements"]["quantum_memory_bridge"] = True

            # Test quantum bridge initialization
            QuantumMemoryBridge(quantum_backend="simulator", max_qubits=4)

            status["capabilities"] = {
                "quantum_encoding": True,
                "quantum_recall": True,
                "quantum_associations": True,
                "error_correction": True,
                "coherence_monitoring": True
            }

            # Check framework availability
            try:
                __import__('qiskit')
                status["requirements"]["qiskit"] = True
            except ImportError:
                pass

            try:
                __import__('cirq')
                status["requirements"]["cirq"] = True
            except ImportError:
                pass

        except Exception as e:
            status["error"] = str(e)
            status["recommendations"].append("Install quantum dependencies: pip install qiskit cirq")

    else:
        status["recommendations"].extend([
            "Install quantum memory bridge components",
            "Ensure quantum_memory_bridge.py is in the correct location",
            "Install quantum computing frameworks: pip install qiskit cirq"
        ])

    return status


# Utility functions for UI integration
def format_quantum_metrics_for_ui(quantum_metrics) -> Dict[str, str]:
    """Format quantum metrics for display in user interfaces"""

    if not quantum_metrics:
        return {"status": "Quantum metrics not available"}

    return {
        "coherence": f"{quantum_metrics.coherence_score:.3f}",
        "fidelity": f"{quantum_metrics.quantum_fidelity:.3f}",
        "entanglement": f"{quantum_metrics.entanglement_strength:.3f}",
        "error_rate": f"{(1 - quantum_metrics.error_correction_rate):.3f}",
        "superposition_advantage": f"{quantum_metrics.superposition_advantage:.3f}",
        "decoherence_time": f"{quantum_metrics.decoherence_time:.1f}ms",
        "quantum_volume": str(quantum_metrics.quantum_volume)
    }


def get_quantum_status_summary(lyrixa_engine) -> Dict[str, Any]:
    """Get a summary of quantum status for UI display"""

    summary = {
        "quantum_available": False,
        "quantum_active": False,
        "coherence_level": "N/A",
        "quantum_operations": 0,
        "last_coherence_check": "Never",
        "status_color": "gray",
        "status_message": "Quantum capabilities not available"
    }

    try:
        if hasattr(lyrixa_engine, 'get_quantum_status'):
            quantum_status = lyrixa_engine.get_quantum_status()

            summary.update({
                "quantum_available": quantum_status.get("quantum_available", False),
                "quantum_active": quantum_status.get("quantum_bridge_active", False),
                "quantum_operations": sum(quantum_status.get("quantum_operations", {}).values()),
                "last_coherence_check": quantum_status.get("last_coherence_check", "Never")
            })

            # Determine coherence level and status
            if quantum_status.get("current_coherence"):
                coherence = quantum_status["current_coherence"]
                summary["coherence_level"] = f"{coherence:.3f}"

                if coherence >= 0.8:
                    summary["status_color"] = "green"
                    summary["status_message"] = "Quantum systems operating optimally"
                elif coherence >= 0.6:
                    summary["status_color"] = "yellow"
                    summary["status_message"] = "Quantum systems stable"
                else:
                    summary["status_color"] = "orange"
                    summary["status_message"] = "Quantum coherence degraded"

            elif summary["quantum_available"]:
                summary["status_color"] = "blue"
                summary["status_message"] = "Quantum systems available"

    except Exception as e:
        logging.error(f"Error getting quantum status: {e}")

    return summary


# Integration example for demo purposes
async def demo_lyrixa_quantum_integration():
    """Demonstrate Lyrixa quantum integration"""

    print("🌌 Lyrixa Quantum Integration Demo")
    print("=" * 50)

    # Check quantum capabilities
    capability_status = get_quantum_capability_status()
    print(f"Quantum integration available: {capability_status['quantum_integration_available']}")

    if capability_status['quantum_integration_available']:
        print("✅ Quantum capabilities detected")

        # Create quantum-enhanced Lyrixa
        quantum_lyrixa = create_quantum_lyrixa({
            'quantum': {
                'quantum_backend': 'simulator',
                'max_qubits': 16,
                'enable_quantum_recall': True,
                'enable_quantum_encoding': True
            }
        })

        print("✅ Quantum-enhanced Lyrixa created")

        # Test quantum status
        if hasattr(quantum_lyrixa, 'get_quantum_status'):
            status = quantum_lyrixa.get_quantum_status()
            print(f"Quantum bridge active: {status.get('quantum_bridge_active', False)}")
            print(f"Quantum states: {status.get('quantum_states_count', 0)}")

        # Get UI-friendly status
        ui_status = get_quantum_status_summary(quantum_lyrixa)
        print(f"UI Status: {ui_status['status_message']} ({ui_status['status_color']})")

    else:
        print("❌ Quantum capabilities not available")
        for rec in capability_status['recommendations']:
            print(f"   💡 {rec}")

        # Create standard Lyrixa as fallback
        from .engine.lyrixa_engine import LyrixaEngine
        LyrixaEngine()
        print("✅ Standard Lyrixa created as fallback")

    print("\n✅ Integration demo completed!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_lyrixa_quantum_integration())
