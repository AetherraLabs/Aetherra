#!/usr/bin/env python3
"""Test script to check model status"""

import os
import sys
from pathlib import Path

# Add the Aetherra directory to the Python path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file"""
    env_file = project_root / ".env"
    if env_file.exists():
        print(f"🔍 Loading .env file from: {env_file}")
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value
        print("✅ Environment variables loaded")
    else:
        print("❌ No .env file found")


# Load .env file immediately
load_env_file()

try:
    from Aetherra.lyrixa.conversation_manager import LyrixaConversationManager

    print("🔍 Testing LyrixaConversationManager...")

    # Initialize conversation manager
    conversation_manager = LyrixaConversationManager(workspace_path=str(project_root))

    # Get available models
    model_info = conversation_manager.get_available_models()

    print("📊 Model Information:")
    print(f"  Current Model: {model_info.get('current_model')}")
    print(f"  LLM Enabled: {model_info.get('llm_enabled')}")
    print(f"  Available Models: {model_info.get('available_models', [])}")
    print(f"  Preferred Models: {model_info.get('preferred_models', [])}")

    if model_info.get("llm_enabled"):
        print("✅ LLM is ENABLED - should not be in fallback mode")
    else:
        print("❌ LLM is DISABLED - will be in fallback mode")

    # Additional debugging
    print(f"🔍 LLM Manager exists: {conversation_manager.llm_manager is not None}")
    print(f"🔍 LLM Enabled flag: {conversation_manager.llm_enabled}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
