"""
Lyrixa Intelligence Stack
"""

import sys
from pathlib import Path

# Add parent directory to Python path to import intelligence.py
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    # Import the intelligence module from the parent directory and extract the class
    import importlib.util

    intelligence_file = Path(__file__).parent.parent / "intelligence.py"

    if intelligence_file.exists():
        spec = importlib.util.spec_from_file_location(
            "lyrixa_intelligence_module", intelligence_file
        )
        if spec and spec.loader:
            intelligence_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(intelligence_module)
            LyrixaIntelligence = intelligence_module.LyrixaIntelligence
            INTELLIGENCE_AVAILABLE = True
        else:
            LyrixaIntelligence = None
            INTELLIGENCE_AVAILABLE = False
    else:
        LyrixaIntelligence = None
        INTELLIGENCE_AVAILABLE = False

except Exception as e:
    print(f"⚠️ Could not load LyrixaIntelligence: {e}")
    LyrixaIntelligence = None
    INTELLIGENCE_AVAILABLE = False

# Try to import intelligence integration if available
LyrixaIntelligenceStack = None
try:
    from intelligence_integration import LyrixaIntelligenceStack
except ImportError:
    pass  # Optional component

__all__ = ["LyrixaIntelligence", "LyrixaIntelligenceStack", "INTELLIGENCE_AVAILABLE"]
