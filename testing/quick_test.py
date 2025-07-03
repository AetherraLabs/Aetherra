from core.chat_router import AetherraChatRouter

print("Testing Neuroplex Chat Upgrade...")

# Test demo mode
cr = AetherraChatRouter(demo_mode=True)
resp = cr.process_message("Hello! What can you do?")
print("Demo response:", resp.get('text', 'No text')[:200])
