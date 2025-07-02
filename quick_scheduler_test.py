#!/usr/bin/env python3
"""
Quick test to verify task scheduler integration
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "core"))

try:
    print("1. Testing task scheduler import...")
    from core.task_scheduler import BackgroundTaskScheduler
    print("✅ Task scheduler imported successfully")

    print("2. Testing task scheduler creation...")
    scheduler = BackgroundTaskScheduler(max_workers=1)
    print("✅ Task scheduler created successfully")

    print("3. Testing GUI import...")
    from src.neurocode.ui.neuroplex import NeuroplexWindow
    print("✅ Neuroplex GUI imported successfully")

    print("4. Testing task scheduler shutdown...")
    scheduler.shutdown(timeout=2.0)
    print("✅ Task scheduler shut down successfully")

    print("\n🎉 All tests passed! Task scheduler integration is working.")

except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
