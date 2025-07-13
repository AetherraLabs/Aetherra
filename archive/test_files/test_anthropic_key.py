#!/usr/bin/env python3
"""
🔑 Anthropic API Key Test
========================

Test if your Anthropic API key is working correctly.
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


def test_anthropic_key():
    """Test the Anthropic API key configuration"""
    print("🔑 Testing Anthropic API Key Configuration")
    print("=" * 45)

    # Check if API key is set
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        print("📝 Make sure you've added your key to the .env file:")
        print("   ANTHROPIC_API_KEY=your-actual-api-key-here")
        return False

    if api_key == "your-anthropic-api-key-here":
        print(
            "❌ Please replace 'your-anthropic-api-key-here' with your actual API key"
        )
        return False

    print(f"✅ API key found: {api_key[:15]}...{api_key[-4:]}")

    # Test Anthropic connection
    try:
        import anthropic

        print("✅ Anthropic package available")

        client = anthropic.Anthropic(api_key=api_key)
        print("✅ Anthropic client initialized")

        # Test a simple API call
        print("🧪 Testing API connection with simple query...")
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=50,
            messages=[
                {
                    "role": "user",
                    "content": "Hello! Just testing the API. Please respond with 'API test successful'",
                }
            ],
        )

        if message.content and len(message.content) > 0:
            content_block = message.content[0]
            response = getattr(content_block, "text", str(content_block))
            print(f"✅ API Response: {response}")

            if "API test successful" in response or "successful" in response.lower():
                print("🎉 Anthropic API key is working perfectly!")
                return True
            else:
                print("⚠️  API responded but with unexpected content")
                return True
        else:
            print("⚠️  API responded but no content received")
            return False

    except ImportError:
        print("❌ Anthropic package not installed")
        print("📦 Install with: pip install anthropic")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        if "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
            print(
                "🔐 This looks like an authentication issue. Please check your API key."
            )
        elif "quota" in str(e).lower() or "billing" in str(e).lower():
            print(
                "💳 This looks like a quota or billing issue. Check your Anthropic account."
            )
        return False


def test_with_lyrixa():
    """Test Anthropic integration with Lyrixa"""
    print("\n🎙️ Testing Anthropic Integration with Lyrixa")
    print("=" * 45)

    try:
        from lyrixa.conversation_manager import LyrixaConversationManager

        # Initialize conversation manager
        workspace_path = os.path.dirname(__file__)
        conv_manager = LyrixaConversationManager(workspace_path)

        # Test Claude response
        print("🤖 Testing Claude response through Lyrixa...")
        response = conv_manager.generate_response(
            "Hello Claude! Are you working through Lyrixa?"
        )

        # Handle both string and coroutine responses
        if hasattr(response, "__await__"):
            import asyncio

            response = asyncio.run(response)

        response_str = str(response)

        if "claude" in response_str.lower() or "anthropic" in response_str.lower():
            print("✅ Claude responded through Lyrixa!")
        elif "fallback" in response_str.lower():
            print(
                "⚠️  Lyrixa is in fallback mode - Claude might not be the active model"
            )
        else:
            print("✅ Got response through Lyrixa (Claude might be working)")

        print(f"📄 Response preview: {response_str[:100]}...")
        return True

    except Exception as e:
        print(f"❌ Lyrixa integration test failed: {e}")
        return False


def main():
    """Run all Anthropic API tests"""
    print("🚀 Anthropic API Configuration Test Suite")
    print("=" * 50)

    # Test 1: Basic API key configuration
    basic_test = test_anthropic_key()

    # Test 2: Lyrixa integration (only if basic test passes)
    if basic_test:
        integration_test = test_with_lyrixa()
    else:
        integration_test = False

    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    print(f"🔑 API Key Configuration: {'✅ PASS' if basic_test else '❌ FAIL'}")
    print(f"🎙️ Lyrixa Integration: {'✅ PASS' if integration_test else '❌ FAIL'}")

    if basic_test and integration_test:
        print(
            "\n🎉 All tests passed! Your Anthropic API key is ready to use with Lyrixa!"
        )
        print("💡 You can now chat with Claude through the Lyrixa interface!")
    elif basic_test:
        print("\n⚠️  API key works but integration needs attention.")
    else:
        print("\n❌ Please fix the API key configuration first.")
        print("\n📝 Steps to fix:")
        print("1. Edit the .env file in the project root")
        print("2. Replace 'your-anthropic-api-key-here' with your actual API key")
        print("3. Restart any running applications")


if __name__ == "__main__":
    main()
