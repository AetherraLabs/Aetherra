from core.chat_router import NeuroCodeChatRouter

print("Testing Neuroplex Chat Upgrade...")

# Test demo mode
cr = NeuroCodeChatRouter(demo_mode=True)
resp = cr.process_message("Hello! What can you do?")
print("Demo response:", resp.get('text', 'No text')[:200])
