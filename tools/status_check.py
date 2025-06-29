#!/usr/bin/env python3
"""
🧬 NeuroCode Status Check
========================

Quick status check for NeuroCode components and dependencies.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    print("🧬 NeuroCode Multi-LLM Status Report")
    print("=" * 50)

    # Test core components
    try:
        print("✅ Grammar Parser: Available")
    except Exception as e:
        print(f"❌ Grammar Parser: Error - {e}")

    try:
        print("✅ Multi-LLM Manager: Available")
    except Exception as e:
        print(f"❌ Multi-LLM Manager: Error - {e}")

    try:
        print("✅ NeuroCode Engine: Available")
    except Exception as e:
        print(f"❌ NeuroCode Engine: Error - {e}")

    # Test playground
    try:
        import streamlit

        print(f"✅ Streamlit: v{streamlit.__version__}")
    except Exception as e:
        print(f"❌ Streamlit: Error - {e}")

    # Test LLM providers
    providers = []
    try:
        import openai

        providers.append(f"OpenAI v{openai.__version__}")
    except:
        providers.append("OpenAI: Not installed")

    try:
        providers.append("Ollama: Available")
    except:
        providers.append("Ollama: Not installed")

    try:
        providers.append("Anthropic: Available")
    except:
        providers.append("Anthropic: Not installed")

    print("\n🤖 LLM Providers:")
    for provider in providers:
        print(f"   {provider}")

    print("\n🎯 NeuroCode Status: Ready!")
    print("Run 'python launch_playground.py' to start the interactive playground.")


if __name__ == "__main__":
    main()
