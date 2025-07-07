from core.chat_router import aetherraChatRouter

print("Testing Aetherra Chat Upgrade...")

# Test demo mode
cr = aetherraChatRouter(demo_mode=True)
resp = cr.process_message("Hello! What can you do?")
print("Demo response:", resp.get("text", "No text")[:200])
