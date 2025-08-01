#!/usr/bin/env python3
"""
Test Self Metrics Dashboard SocketIO functionality
"""

import json
import time

import socketio


def test_self_metrics():
    """Test the Self Metrics Dashboard SocketIO integration"""

    print("🔍 Testing Self Metrics Dashboard...")

    # Create SocketIO client
    sio = socketio.SimpleClient()

    try:
        # Connect to server
        print("🔍 Connecting to http://127.0.0.1:8686...")
        sio.connect("http://127.0.0.1:8686")
        print("✅ Connected successfully!")

        # Test get_self_metrics
        print("🔍 Testing get_self_metrics...")
        sio.emit("get_self_metrics", {})

        # Wait for response
        print("⏳ Waiting for self_metrics_data response...")
        event = sio.receive(timeout=5)
        print(f"📨 Received: {event}")

        if event[0] == "self_metrics_data":
            data = event[1]
            print("✅ Self Metrics data received:")
            print(
                f"   📊 Memory Continuity: {data.get('memory_continuity', {}).get('score', 'N/A')}%"
            )
            print(
                f"   📈 Growth Trajectory: {data.get('growth_trajectory', {}).get('score', 'N/A')}%"
            )
            print(
                f"   ⚔️ Conflict Analysis: {data.get('conflict_analysis', {}).get('score', 'N/A')}%"
            )
            print(
                f"   🎯 Ethical Alignment: {data.get('ethical_alignment', {}).get('score', 'N/A')}%"
            )
            print(
                f"   🧠 Cognitive Coherence: {data.get('cognitive_coherence', {}).get('score', 'N/A')}%"
            )
        else:
            print(f"❌ Unexpected response: {event}")

        # Test get_available_models to check AI status
        print("🔍 Testing get_available_models...")
        sio.emit("get_available_models", {})

        # Wait for response
        print("⏳ Waiting for models_list response...")
        event = sio.receive(timeout=5)
        print(f"📨 Received: {event}")

        if event[0] == "models_list":
            data = event[1]
            print("✅ Models data received:")
            print(f"   🤖 Available models: {len(data.get('available_models', []))}")
            print(f"   🎯 Current model: {data.get('current_model', 'N/A')}")
            print(f"   🚦 LLM enabled: {data.get('llm_enabled', False)}")
            if data.get("llm_enabled"):
                print("✅ AI Models are ACTIVE (not in fallback mode)")
            else:
                print("❌ AI Models are in FALLBACK mode")
        else:
            print(f"❌ Unexpected response: {event}")

        print("✅ Self Metrics test completed successfully!")

    except Exception as e:
        print(f"❌ Error during test: {e}")
    finally:
        sio.disconnect()
        print("🔚 Disconnected from server")


if __name__ == "__main__":
    test_self_metrics()
