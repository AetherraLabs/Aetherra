#!/usr/bin/env python3
"""Launch NeuroCode UI in test mode"""

import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "ui"))

# Try to launch UI
try:
    from ui.neuro_ui import main

    print("🚀 Launching NeuroCode Enhanced UI...")
    main()
except Exception as e:
    print(f"❌ Error launching UI: {e}")
    import traceback

    traceback.print_exc()
