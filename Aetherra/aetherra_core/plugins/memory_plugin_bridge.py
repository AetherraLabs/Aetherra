"""
Memory Plugin Bridge
Routes memory read/write/recall commands from plugin ecosystem.
"""

from Aetherra.aetherra_core.memory.aetherra_memory_engine import AetherraMemoryEngine

engine = AetherraMemoryEngine()


def plugin_store(key, content):
    # AetherraMemoryEngine.store expects a dict memory entry
    return engine.store({"plugin": key, "content": content})


def plugin_recall(query):
    # Returns a dict result or empty payload
    return engine.retrieve(query)


def plugin_forget(key):
    # Forget not supported on the core engine; provide a no-op for compatibility
    return {"success": False, "message": "forget not supported"}
