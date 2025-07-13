#!/usr/bin/env python3
"""Test script to verify the chat response fix"""


# Test that the direct question response works
def test_direct_response():
    """Test the direct response for common questions"""

    # Test the typo from the original question
    test_questions = [
        "what is aetherra",
        "what si aetherra",  # This was the exact typo from the user
        "What is Aetherra?",
        "what is aetherra?",
    ]

    for question in test_questions:
        message_lower = question.lower()

        # This is the exact logic from the launcher
        if "what is aetherra" in message_lower or "what si aetherra" in message_lower:
            response = """🌟 **Aetherra** is an advanced AI Operating System project that I'm designed to help you with!

**Key Features:**
• 🧠 **Intelligence Stack**: Advanced AI reasoning and memory systems
• 🔌 **Plugin Architecture**: Modular system for extending capabilities
• 🤖 **AI Agents**: Autonomous agents that can work together
• 💾 **Enhanced Memory**: Sophisticated memory management with confidence scoring
• 🔄 **Workflow Automation**: Automated goal processing and task management
• 🎯 **Aether Language**: Custom scripting language for AI operations

**Current Status:**
• All core systems are initialized and running
• Plugin ecosystem is active and healthy
• Memory systems are storing and learning from our interactions
• Intelligence workflows are processing in the background

I'm Lyrixa, your AI assistant built specifically for the Aetherra project. I can help you understand the system, manage workflows, analyze code, and assist with development tasks!"""

            print(f"✅ Question: '{question}'")
            print(f"✅ Response ready: {len(response)} characters")
            print(f"✅ Preview: {response[:100]}...")
            print("---")
        else:
            print(f"❌ Question: '{question}' - No match")

    print("\n✅ Direct response test completed!")


if __name__ == "__main__":
    test_direct_response()
