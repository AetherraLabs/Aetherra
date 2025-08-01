#!/usr/bin/env python3
"""
🧪 Simple Ollama Test
====================

Test Ollama directly without heavy imports.
"""

import json

import requests


def test_ollama_api():
    """Test Ollama API directly"""
    print("🔧 Testing Ollama API")
    print("=" * 25)

    try:
        # Check service
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("❌ Ollama service not responding")
            return False

        models = response.json().get("models", [])
        print(f"✅ Found {len(models)} models:")
        for model in models:
            print(f"   • {model['name']}")

        # Test a model
        if models:
            test_model = "llama3.2:3b"
            print(f"\n🧠 Testing {test_model}...")

            payload = {
                "model": test_model,
                "prompt": "Hello! Respond with exactly: 'Ollama working!'",
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 10},
            }

            response = requests.post(
                "http://localhost:11434/api/generate", json=payload, timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "").strip()
                print(f"✅ Response: {response_text}")
                return True
            else:
                print(f"❌ Failed: {response.status_code}")
                return False

        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_python_ollama():
    """Test Python ollama package"""
    print("\n🐍 Testing Python Ollama Package")
    print("=" * 35)

    try:
        import ollama

        client = ollama.Client()
        print("✅ Ollama client created")

        # List models
        models = client.list()
        model_names = [m.model for m in models.models]
        print(f"✅ Available models: {model_names}")

        # Test generation
        if model_names:
            test_model = "llama3.2:3b"
            print(f"\n🧠 Testing {test_model}...")

            response = client.generate(
                model=test_model,
                prompt="Say 'Python Ollama working!'",
                options={"temperature": 0.1, "num_predict": 10},
            )

            print(f"✅ Response: {response['response']}")
            return True

        return False

    except ImportError:
        print("⚠️  Ollama Python package not installed")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 OLLAMA SIMPLE TEST")
    print("=" * 30)

    api_test = test_ollama_api()
    python_test = test_python_ollama()

    print("\n" + "=" * 30)
    print("📊 RESULTS")
    print("=" * 30)
    print(f"🔗 API Test: {'✅ PASS' if api_test else '❌ FAIL'}")
    print(f"🐍 Python Test: {'✅ PASS' if python_test else '❌ FAIL'}")

    if api_test or python_test:
        print("\n🎉 OLLAMA IS WORKING!")
        print("🚀 Local AI models are ready!")
    else:
        print("\n❌ Ollama tests failed")
        print("💡 Check Ollama installation")
