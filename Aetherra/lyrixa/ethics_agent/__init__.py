"""
🤖 Ethics Agent Module
======================

Specialized ethics agents for moral reasoning, bias detection,
and value alignment within the Aetherra AI OS.
"""

# Import ethics components
try:
    from .moral_reasoning import MoralReasoningEngine
except ImportError:
    MoralReasoningEngine = None

try:
    from .bias_detector import BiasDetectionEngine
except ImportError:
    BiasDetectionEngine = None

try:
    from .value_alignment import ValueAlignmentEngine
except ImportError:
    ValueAlignmentEngine = None

__all__ = ["MoralReasoningEngine", "BiasDetectionEngine", "ValueAlignmentEngine"]
