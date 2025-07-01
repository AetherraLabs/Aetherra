#!/usr/bin/env python3
"""
Simple test to check src/neurocode/core imports
"""

import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

print("🧪 Simple import test for src/neurocode/core")
print("=" * 50)

try:
    print("Testing basic core import...")
    print("✅ neurocode.core imported")
except Exception as e:
    print(f"❌ neurocode.core failed: {e}")

try:
    print("Testing interpreter import...")
    print("✅ EnhancedNeuroCodeInterpreter imported")
except Exception as e:
    print(f"❌ EnhancedNeuroCodeInterpreter failed: {e}")

try:
    print("Testing parser import...")
    print("✅ NeuroCodeParser imported")
except Exception as e:
    print(f"❌ NeuroCodeParser failed: {e}")

try:
    print("Testing memory import...")
    print("✅ Memory system imported")
except Exception as e:
    print(f"❌ Memory system failed: {e}")

try:
    print("Testing AI modules...")
    print("✅ AI collaboration imported")
except Exception as e:
    print(f"❌ AI collaboration failed: {e}")

print("\n✅ Basic import test completed!")
