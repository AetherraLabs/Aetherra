"""
Lyrixa Intelligence Stack
"""

# Import from the parent directory where the intelligence integration is located
import importlib.util

# Import core intelligence directly to avoid circular imports
from pathlib import Path

from ..intelligence_integration import LyrixaIntelligenceStack

# Add the parent directory to path temporarily
parent_dir = Path(__file__).parent.parent
intelligence_file = parent_dir / "intelligence.py"

LyrixaIntelligence = None

if intelligence_file.exists():
    # Load the intelligence module directly
    spec = importlib.util.spec_from_file_location(
        "lyrixa_intelligence_core", intelligence_file
    )
    if spec and spec.loader:
        intelligence_module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(intelligence_module)
            LyrixaIntelligence = intelligence_module.LyrixaIntelligence
        except Exception as e:
            print(f"⚠️ Could not load LyrixaIntelligence: {e}")
            LyrixaIntelligence = None
    else:
        print("⚠️ Could not create module spec for intelligence.py")
else:
    print("⚠️ intelligence.py file not found")

__all__ = ["LyrixaIntelligence", "LyrixaIntelligenceStack"]
