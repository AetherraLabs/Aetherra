"""
Memory Plugin Bridge
Routes memory read/write/recall commands from plugin ecosystem.
"""
from memory.lyrixa_memory_engine import LyrixaMemoryEngine

engine = LyrixaMemoryEngine()

def plugin_store(key, content):
    return engine.store(content, metadata={"plugin": key})

def plugin_recall(query):
    return engine.retrieve(query)

def plugin_forget(key):
    return engine.delete(key)
