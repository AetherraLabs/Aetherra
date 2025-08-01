"""
🧠 Lyrixa Memory System - Next Generation
=========================================

Integrated multi-dimensional memory architecture combining:
- Fast vector-based semantic search
- Episodic narrative continuity
- Symbolic concept clustering
- Temporal pattern recognition
- Health monitoring and drift correction
- Reflective meta-cognitive analysis

Components:
- LyrixaMemoryEngine: Main integration layer
- FractalMesh: Multi-dimensional memory organization
- MemoryNarrator: Story generation from fragments
- MemoryPulse: Health monitoring and alerts
- MemoryReflector: Self-analysis and insights
"""

# Core integrated engine
# FractalMesh components
try:
    # Try relative imports first
    from .fractal_mesh import (
        ConceptClusterManager,
        CrossContextAnalogies,
        EpisodicTimeline,
        FractalMeshCore,
    )
    from .lyrixa_memory_engine import (
        LyrixaMemoryEngine,
        MemoryOperationResult,
        MemorySystemConfig,
    )

    # Legacy memory system (maintained for compatibility)
    from .memory_core import LyrixaMemorySystem

    # Memory processing components
    from .narrator import MemoryNarrative, MemoryNarrator
    from .pulse import DriftAlert, MemoryHealth, MemoryPulseMonitor
    from .reflector import MemoryReflector, ReflectionInsight

except ImportError:
    # Fall back to absolute imports or placeholders
    try:
        from Aetherra.lyrixa.memory.lyrixa_memory_engine import (
            LyrixaMemoryEngine,
            MemoryOperationResult,
            MemorySystemConfig,
        )
        from Aetherra.lyrixa.memory.memory_core import LyrixaMemorySystem
    except ImportError:
        print("⚠️ Using placeholder memory classes")

        class LyrixaMemoryEngine:
            def __init__(self, *args, **kwargs):
                pass

        class MemoryOperationResult:
            def __init__(self, success=True, data=None):
                self.success = success
                self.data = data or {}

        class MemorySystemConfig:
            def __init__(self, *args, **kwargs):
                pass

        class LyrixaMemorySystem(LyrixaMemoryEngine):
            pass

    # Placeholder classes for missing components
    class ConceptClusterManager:
        def __init__(self, *args, **kwargs):
            pass

    class CrossContextAnalogies:
        def __init__(self, *args, **kwargs):
            pass

    class EpisodicTimeline:
        def __init__(self, *args, **kwargs):
            pass

    class FractalMeshCore:
        def __init__(self, *args, **kwargs):
            pass

    class MemoryNarrative:
        def __init__(self, *args, **kwargs):
            pass

    class MemoryNarrator:
        def __init__(self, *args, **kwargs):
            pass

    class DriftAlert:
        def __init__(self, *args, **kwargs):
            pass

    class MemoryHealth:
        def __init__(self, *args, **kwargs):
            pass

    class MemoryPulseMonitor:
        def __init__(self, *args, **kwargs):
            pass

    class MemoryReflector:
        def __init__(self, *args, **kwargs):
            pass

    class ReflectionInsight:
        def __init__(self, *args, **kwargs):
            pass

__all__ = [
    # Main engine
    "LyrixaMemoryEngine",
    "MemorySystemConfig",
    "MemoryOperationResult",
    # Legacy system
    "LyrixaMemorySystem",
    # FractalMesh components
    "FractalMeshCore",
    "ConceptClusterManager",
    "EpisodicTimeline",
    "CrossContextAnalogies",
    # Processing components
    "MemoryNarrator",
    "MemoryNarrative",
    "MemoryPulseMonitor",
    "DriftAlert",
    "MemoryHealth",
    "MemoryReflector",
    "ReflectionInsight",
]

# Version info
__version__ = "2.0.0"
__description__ = (
    "Next-generation memory system with episodic continuity and narrative generation"
)
