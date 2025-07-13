#!/usr/bin/env python3
"""Test the Aetherra response directly"""


# Test the question pattern matching
def test_aetherra_question():
    user_input = "what is aetherra"
    message_lower = user_input.lower()

    if "what is aetherra" in message_lower or "what si aetherra" in message_lower:
        print("✅ Question pattern matches!")
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
        print(f"Response ready: {len(response)} characters")
        print("---")
        print(response)
        return True
    else:
        print("❌ Question pattern does not match")
        return False


if __name__ == "__main__":
    test_aetherra_question()
