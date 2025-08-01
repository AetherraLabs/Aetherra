"""
Test Import Resolution
Quick test to verify all imports are working
"""

try:
    print("Testing core memory imports...")
    from Aetherra.core.memory import AetherraMemory, BasicMemory, PatternAnalyzer

    print("✅ Core memory imports successful")

    print("Testing interpreter agent import...")
    from Aetherra.core.interpreter.agent import AetherraAgent

    print("✅ Interpreter agent import successful")

    print("Testing basic memory functionality...")
    memory = BasicMemory()
    memory.store({"text": "test", "timestamp": "2025-07-12T22:50:00"})
    print(f"✅ Basic memory working - stored {len(memory.memories)} items")

    print("Testing pattern analyzer...")
    analyzer = PatternAnalyzer(memory)
    patterns = analyzer.analyze_patterns(memory.memories)
    print(f"✅ Pattern analyzer working - found {len(patterns)} pattern types")

    print("\n🎉 ALL IMPORTS AND BASIC FUNCTIONALITY WORKING!")

except Exception as e:
    print(f"❌ Import/functionality test failed: {e}")
    import traceback

    traceback.print_exc()
