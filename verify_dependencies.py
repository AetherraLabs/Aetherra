#!/usr/bin/env python3
"""
🔧 Dependencies Verification Script
==================================

Quick verification that all required dependencies are properly installed
and functioning in the virtual environment.
"""

import importlib
import sys


def test_import(module_name, display_name=None):
    """Test if a module can be imported"""
    display_name = display_name or module_name
    try:
        module = importlib.import_module(module_name)
        print(f"✅ {display_name}: OK")
        return True
    except ImportError as e:
        print(f"❌ {display_name}: FAILED - {e}")
        return False


def main():
    print("🔧 AETHERRA DEPENDENCIES VERIFICATION")
    print("=" * 50)

    # Check virtual environment
    venv_active = sys.executable.find(".venv") != -1
    print(f"🐍 Virtual Environment: {'✅ ACTIVE' if venv_active else '❌ NOT ACTIVE'}")
    print(f"   Python path: {sys.executable}")
    print()

    # Core requirements
    print("📦 CORE REQUIREMENTS:")
    core_passed = 0
    core_total = 4

    core_passed += test_import("requests", "requests (HTTP client)")
    core_passed += test_import("psutil", "psutil (system monitoring)")
    core_passed += test_import("yaml", "PyYAML (config processing)")
    core_passed += test_import("typing_extensions", "typing-extensions")

    print()

    # GUI Framework
    print("🖥️ GUI FRAMEWORK:")
    gui_passed = 0
    gui_total = 2

    gui_passed += test_import("PySide6", "PySide6 (Qt framework)")
    gui_passed += test_import("PySide6.QtWebEngineWidgets", "PySide6-Addons")

    print()

    # API Server
    print("🌐 API SERVER:")
    api_passed = 0
    api_total = 4

    api_passed += test_import("fastapi", "FastAPI")
    api_passed += test_import("uvicorn", "Uvicorn")
    api_passed += test_import("pydantic", "Pydantic")
    api_passed += test_import("multipart", "python-multipart")

    print()

    # AI Providers
    print("🤖 AI PROVIDERS:")
    ai_passed = 0
    ai_total = 2

    ai_passed += test_import("openai", "OpenAI")
    ai_passed += test_import("anthropic", "Anthropic")

    print()

    # Memory System Dependencies
    print("🧠 MEMORY SYSTEM:")
    memory_passed = 0
    memory_total = 6

    memory_passed += test_import("flask", "Flask (dashboard)")
    memory_passed += test_import("plotly", "Plotly (visualizations)")
    memory_passed += test_import("pandas", "Pandas (data processing)")
    memory_passed += test_import("sentence_transformers", "Sentence Transformers")
    memory_passed += test_import("faiss", "FAISS (vector search)")
    memory_passed += test_import("spacy", "spaCy (NLP)")

    print()

    # Test spaCy model
    print("🔍 NLP MODELS:")
    try:
        import spacy

        nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy English model: OK")
        model_passed = 1
    except Exception as e:
        print(f"❌ spaCy English model: FAILED - {e}")
        model_passed = 0

    print()

    # Optional enhancements
    print("🔧 OPTIONAL ENHANCEMENTS:")
    optional_passed = 0
    optional_total = 1

    optional_passed += test_import("dotenv", "python-dotenv")

    print()

    # Summary
    total_passed = (
        core_passed
        + gui_passed
        + api_passed
        + ai_passed
        + memory_passed
        + model_passed
        + optional_passed
    )
    total_tests = (
        core_total
        + gui_total
        + api_total
        + ai_total
        + memory_total
        + 1
        + optional_total
    )

    print("📊 SUMMARY:")
    print(f"   Core Requirements: {core_passed}/{core_total}")
    print(f"   GUI Framework: {gui_passed}/{gui_total}")
    print(f"   API Server: {api_passed}/{api_total}")
    print(f"   AI Providers: {ai_passed}/{ai_total}")
    print(f"   Memory System: {memory_passed}/{memory_total}")
    print(f"   NLP Models: {model_passed}/1")
    print(f"   Optional: {optional_passed}/{optional_total}")
    print(
        f"   OVERALL: {total_passed}/{total_tests} ({total_passed / total_tests * 100:.1f}%)"
    )

    if total_passed == total_tests:
        print("\n🎉 ALL DEPENDENCIES VERIFIED! System ready for operation.")
        return True
    else:
        print(f"\n⚠️ {total_tests - total_passed} dependencies missing or failed.")
        print("💡 Run: pip install -r requirements.txt")
        return False


if __name__ == "__main__":
    main()
