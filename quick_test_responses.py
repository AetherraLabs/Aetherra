#!/usr/bin/env python3
"""
Quick test of conversation responses
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lyrixa.conversation_manager import LyrixaConversationManager

# Test single response
print("Testing single response...")
conv = LyrixaConversationManager(".")
response = conv.generate_response_sync("Hello!")
print(f"Response: {response}")
print("-" * 50)

# Test system status response
response2 = conv.generate_response_sync("What's the system status?")
print(f"Status Response: {response2}")
print("-" * 50)

# Test plugin response
response3 = conv.generate_response_sync("Tell me about plugins")
print(f"Plugin Response: {response3}")
