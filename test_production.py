from core.chat_router import NeuroCodeChatRouter

print("Testing Production Mode (no debug)...")

# Test production mode - no debug prints
cr = NeuroCodeChatRouter(demo_mode=True, debug_mode=False)
resp = cr.process_message("Hello! What can you do?")
print("Production response:", resp.get('text', 'No text')[:200])

print("\nTesting Debug Mode...")

# Test debug mode
cr_debug = NeuroCodeChatRouter(demo_mode=True, debug_mode=True)
resp_debug = cr_debug.process_message("Hello!")
print("Debug response:", resp_debug.get('text', 'No text')[:100])
