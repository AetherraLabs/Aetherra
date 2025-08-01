#!/usr/bin/env python3
"""Test Aetherra Playground components"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path.cwd()))

try:
    from Aetherra.core.aethercode_grammar import create_Aetherra_parser

    print("✅ Parser imported successfully")

    from stdlib import stdlib_manager

    print("✅ Standard library imported successfully")

    # Test parser creation
    parser = create_Aetherra_parser()
    print("✅ Parser created successfully")

    # Test stdlib manager
    plugins = stdlib_manager.list_plugins()
    print(f"✅ Standard library loaded {len(plugins)} plugins")

    print("\n🎉 All Aetherra Playground components are ready!")
    print("🚀 The playground should work correctly!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
