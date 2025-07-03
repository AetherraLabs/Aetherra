#!/usr/bin/env python3
"""
🧠 aetherra Multi-LLM Setup Script
==================================

Installs required dependencies for aetherra's multi-LLM support:
- OpenAI for GPT models
- Ollama for local models (Mistral, LLaMA, Mixtral)
- llama-cpp-python for GGUF models
- Anthropic for Claude
- Google AI for Gemini
"""

import subprocess
import sys


def install_package(package, description=""):
    """Install a Python package with pip"""
    print(f"📦 Installing {package}... {description}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing {package}: {e}")
        return False


def main():
    """Main setup function"""
    print("🧬 aetherra Multi-LLM Setup")
    print("=" * 50)
    print("Installing dependencies for multi-LLM support...")
    print()

    # Core LLM packages
    packages = [
        ("openai>=1.0.0", "OpenAI GPT models"),
        ("ollama", "Local Ollama models (Mistral, LLaMA, Mixtral)"),
        ("llama-cpp-python", "GGUF local models"),
        ("anthropic", "Anthropic Claude models"),
        ("google-generativeai", "Google Gemini models"),
        ("streamlit>=1.28.0", "Enhanced playground"),
        ("lark>=1.1.0", "aetherra parser"),
    ]

    successful = 0
    failed = 0

    for package, description in packages:
        if install_package(package, description):
            successful += 1
        else:
            failed += 1
        print()

    print("=" * 50)
    print("✅ Installation Summary:")
    print(f"   Successfully installed: {successful}")
    print(f"   Failed: {failed}")

    if failed == 0:
        print("\n🎉 All dependencies installed successfully!")
        print("\n🚀 Multi-LLM aetherra is ready to use!")
        print("\nNext steps:")
        print("1. Set up API keys (optional for local models):")
        print("   export OPENAI_API_KEY='your-key'")
        print("   export ANTHROPIC_API_KEY='your-key'")
        print("   export GOOGLE_API_KEY='your-key'")
        print("\n2. Install Ollama for local models:")
        print("   Visit: https://ollama.ai/download")
        print("   Run: ollama pull mistral")
        print("   Run: ollama pull llama2")
        print("   Run: ollama pull mixtral")
        print("\n3. Launch aetherra playground:")
        print("   python launch_playground.py")
        print("\n4. Test multi-LLM aetherra:")
        print("   python aetherra_engine.py")
    else:
        print(f"\n⚠️ {failed} packages failed to install.")
        print("Please check the errors above and install manually if needed.")

    print("\n🧬 aetherra Multi-LLM Setup Complete!")


if __name__ == "__main__":
    main()
