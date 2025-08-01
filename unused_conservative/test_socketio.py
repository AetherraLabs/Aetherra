#!/usr/bin/env python3
"""Simple SocketIO test client"""

import time

import socketio

# Create a Socket.IO client
sio = socketio.SimpleClient()

try:
    print("🔍 Attempting to connect to http://127.0.0.1:8686...")
    sio.connect("http://127.0.0.1:8686")
    print("✅ Connected successfully!")

    # Test getting available models
    print("🔍 Testing get_available_models...")
    sio.emit("get_available_models")

    # Wait for response
    event = sio.receive()
    print(f"📨 Received: {event}")

    sio.disconnect()
    print("✅ Test completed")

except Exception as e:
    print(f"❌ Connection failed: {e}")
    import traceback

    traceback.print_exc()
