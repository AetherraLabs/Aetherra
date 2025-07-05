from Aetherra.core.chat_router import AetherraChatRouter

print("Testing Production Mode (no debug)...")

# Test production mode - no debug prints
cr = AetherraChatRouter(demo_mode=True, debug_mode=False)
resp = cr.route_message("test_user", "Hello! What can you do?")
print("Production response:", resp.get("text", "No text")[:200])

print("\nTesting Debug Mode...")

# Test debug mode
cr_debug = AetherraChatRouter(demo_mode=True, debug_mode=True)
resp_debug = cr_debug.route_message("test_user", "Hello!")
print("Debug response:", resp_debug.get("text", "No text")[:100])
