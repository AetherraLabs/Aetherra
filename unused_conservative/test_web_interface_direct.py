#!/usr/bin/env python3
"""
Direct Web Interface Message Test
Test sending messages directly to the web interface
"""

import requests
import json
import socketio
import time

# Test the web interface conversation
def test_web_conversation():
    print("🧪 Testing Web Interface Conversation")
    print("=" * 50)

    # Create a Socket.IO client
    sio = socketio.Client()

    @sio.event
    def connect():
        print("✅ Connected to web interface")

    @sio.event
    def message_response(data):
        print(f"🤖 Lyrixa Response: {data.get('response', 'No response')}")
        print(f"   Agent: {data.get('agent', 'unknown')}")
        print(f"   Time: {data.get('timestamp', 'unknown')}")

    @sio.event
    def error(data):
        print(f"❌ Error received: {data.get('message', 'Unknown error')}")

    @sio.event
    def disconnect():
        print("❌ Disconnected from web interface")

    try:
        # Connect to the web interface
        sio.connect('http://127.0.0.1:8686')
        time.sleep(1)

        # Send test messages
        test_messages = [
            "hello",
            "how are you?",
            "tell me about yourself",
            "what are your capabilities?"
        ]

        for message in test_messages:
            print(f"\n🔹 Sending: {message}")
            sio.emit('send_message', {'message': message})
            time.sleep(2)  # Wait for response

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        sio.disconnect()

if __name__ == "__main__":
    test_web_conversation()
