#!/usr/bin/env python3
"""
Test Ollama model availability
"""

import ollama


def test_ollama_models():
    try:
        client = ollama.Client()
        models = client.list()
        print(f"Full response: {models}")
        print("Available Ollama models:")
        for model in models["models"]:
            print(f"  - Model: {model}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_ollama_models()
