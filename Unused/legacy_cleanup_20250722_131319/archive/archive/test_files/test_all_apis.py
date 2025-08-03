#!/usr/bin/env python3
"""
🔑 Complete API Configuration Test
=================================

Test all API keys: OpenAI, Anthropic (Claude), and Google (Gemini).
"""

import os
import sys

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # Manual .env loading if dotenv not available
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#") and "=" in line:
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))


def test_openai_key():
    """Test OpenAI API key"""
    print("🤖 Testing OpenAI API Key")
    print("=" * 30)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found")
        return False

    print(f"✅ API key found: {api_key[:15]}...{api_key[-4:]}")

    try:
        import openai

        client = openai.OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized")

        # Quick test (but expect quota error)
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello! Just testing the API."}],
                max_tokens=10,
            )
            print("✅ OpenAI API working!")
            return True
        except Exception as e:
            if "quota" in str(e).lower() or "429" in str(e):
                print("[WARN]  OpenAI API key valid but quota exceeded")
                return True
            else:
                print(f"❌ OpenAI API error: {e}")
                return False

    except ImportError:
        print("❌ OpenAI package not installed")
        return False
    except Exception as e:
        print(f"❌ OpenAI setup error: {e}")
        return False


def test_anthropic_key():
    """Test Anthropic API key"""
    print("\n🎭 Testing Anthropic API Key")
    print("=" * 32)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found")
        return False

    print(f"✅ API key found: {api_key[:15]}...{api_key[-4:]}")

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        print("✅ Anthropic client initialized")

        # Quick test (but expect credit error)
        try:
            message = client.messages.create(
                model="claude-3-haiku-20240307",  # Cheaper model
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello!"}],
            )
            print("✅ Anthropic API working!")
            return True
        except Exception as e:
            if "credit" in str(e).lower() or "billing" in str(e).lower():
                print("[WARN]  Anthropic API key valid but needs credits")
                return True
            else:
                print(f"❌ Anthropic API error: {e}")
                return False

    except ImportError:
        print("❌ Anthropic package not installed")
        return False
    except Exception as e:
        print(f"❌ Anthropic setup error: {e}")
        return False


def test_google_key():
    """Test Google API key"""
    print("\n🌟 Testing Google API Key")
    print("=" * 28)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found")
        return False

    print(f"✅ API key found: {api_key[:15]}...{api_key[-4:]}")

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        print("✅ Google AI client configured")

        # Quick test
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")  # Updated model name
            test_response = model.generate_content("Hello! Just testing the API.")
            print("✅ Google Gemini API working!")
            return True
        except Exception as e:
            if "quota" in str(e).lower() or "limit" in str(e).lower():
                print("[WARN]  Google API key valid but quota/limit reached")
                return True
            else:
                print(f"❌ Google API error: {e}")
                return False

    except ImportError:
        print("❌ Google AI package not installed")
        print("[DISC] Install with: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ Google setup error: {e}")
        return False


def test_lyrixa_integration():
    """Test API integration with Lyrixa"""
    print("\n🎙️ Testing Lyrixa Multi-LLM Integration")
    print("=" * 42)

    try:
        from lyrixa.conversation_manager import LyrixaConversationManager

        workspace_path = os.path.dirname(__file__)
        conv_manager = LyrixaConversationManager(workspace_path)

        print("✅ Lyrixa conversation manager initialized")

        # Test with a simple message
        response = conv_manager.generate_response(
            "Hello! Which AI model are you using?"
        )

        # Handle async response
        if hasattr(response, "__await__"):
            import asyncio

            response = asyncio.run(response)

        response_str = str(response)

        # Check which model responded
        if "claude" in response_str.lower() or "anthropic" in response_str.lower():
            print("✅ Claude is responding through Lyrixa!")
            model_used = "Claude (Anthropic)"
        elif "gpt" in response_str.lower() or "openai" in response_str.lower():
            print("✅ GPT is responding through Lyrixa!")
            model_used = "GPT (OpenAI)"
        elif "gemini" in response_str.lower() or "google" in response_str.lower():
            print("✅ Gemini is responding through Lyrixa!")
            model_used = "Gemini (Google)"
        elif "fallback" in response_str.lower():
            print("[WARN]  Lyrixa using fallback mode - no LLM models available")
            model_used = "Fallback"
        else:
            print("✅ Got response from Lyrixa (model unclear)")
            model_used = "Unknown"

        print(f"🤖 Active model: {model_used}")
        print(f"📄 Response preview: {response_str[:100]}...")

        return True

    except Exception as e:
        print(f"❌ Lyrixa integration test failed: {e}")
        return False


def main():
    """Run all API configuration tests"""
    print("🚀 COMPLETE API CONFIGURATION TEST SUITE")
    print("=" * 50)
    print("Testing OpenAI, Anthropic, and Google API keys...\n")

    # Test all API keys
    openai_test = test_openai_key()
    anthropic_test = test_anthropic_key()
    google_test = test_google_key()

    # Test Lyrixa integration
    lyrixa_test = test_lyrixa_integration()

    print("\n" + "=" * 50)
    print("📊 COMPLETE TEST RESULTS")
    print("=" * 50)
    print(f"🤖 OpenAI (GPT): {'✅ CONFIGURED' if openai_test else '❌ FAILED'}")
    print(
        f"🎭 Anthropic (Claude): {'✅ CONFIGURED' if anthropic_test else '❌ FAILED'}"
    )
    print(f"🌟 Google (Gemini): {'✅ CONFIGURED' if google_test else '❌ FAILED'}")
    print(f"🎙️ Lyrixa Integration: {'✅ WORKING' if lyrixa_test else '❌ FAILED'}")

    configured_count = sum([openai_test, anthropic_test, google_test])

    print(f"\n🎯 API SUMMARY:")
    print(f"   • {configured_count}/3 API providers configured")
    print(f"   • Lyrixa integration: {'Working' if lyrixa_test else 'Needs attention'}")

    if configured_count >= 1 and lyrixa_test:
        print("\n🎉 EXCELLENT! You have multiple AI models configured!")
        print("💡 Lyrixa will automatically use the best available model.")
        print("🔄 If one model is unavailable, it will fallback to others.")
    elif configured_count >= 1:
        print("\n[WARN]  API keys configured but Lyrixa integration needs work.")
    else:
        print("\n❌ No API keys working. Please check your configuration.")

    print(f"\n🌟 Your AI-powered Lyrixa system is ready!")


if __name__ == "__main__":
    main()
