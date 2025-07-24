#!/usr/bin/env python3
"""
Verify that all required dependencies are installed and working.
This script tests the current requirements without launching the full GUI.
"""

import sys


def test_imports():
    """Test all critical imports."""
    results = []

    # Test core requirements
    test_cases = [
        ("requests", "HTTP client"),
        ("psutil", "System monitoring"),
        ("yaml", "YAML processing"),
        ("typing_extensions", "Enhanced typing"),
        ("PySide6.QtWidgets", "Qt GUI framework"),
        ("PySide6.QtWebEngineWidgets", "Qt WebEngine"),
        ("fastapi", "FastAPI web framework"),
        ("uvicorn", "ASGI server"),
        ("pydantic", "Data validation"),
        ("openai", "OpenAI API client"),
        ("anthropic", "Anthropic API client"),
        ("dotenv", "Environment variables"),
    ]

    for module, description in test_cases:
        try:
            __import__(module)
            results.append((module, "✅", description))
        except ImportError as e:
            results.append((module, "❌", f"{description} - {e}"))

    return results


def main():
    """Main verification function."""
    print("🔍 AETHERRA LYRIXA - DEPENDENCY VERIFICATION")
    print("=" * 50)
    print(f"Python Version: {sys.version}")
    print("=" * 50)

    results = test_imports()

    success_count = 0
    total_count = len(results)

    for module, status, description in results:
        print(f"{status} {module:25} | {description}")
        if status == "✅":
            success_count += 1

    print("=" * 50)
    print(f"📊 RESULTS: {success_count}/{total_count} dependencies verified")

    if success_count == total_count:
        print("🎉 ALL DEPENDENCIES VERIFIED! Lyrixa is ready to launch.")
        print("\n🚀 Next steps:")
        print("   1. Set up .env file with API keys")
        print("   2. Run: python Aetherra/lyrixa/launcher.py")
        return 0
    else:
        print("❌ Some dependencies are missing. Please install them:")
        print("   pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
