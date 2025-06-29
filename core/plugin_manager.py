<<<<<<< HEAD
# core/plugin_manager.py
import os
import importlib.util

PLUGIN_REGISTRY = {}

PLUGIN_DIR = os.path.join(os.path.dirname(__file__), "..", "plugins")

os.makedirs(PLUGIN_DIR, exist_ok=True)

def register_plugin(name):
    def decorator(func):
        PLUGIN_REGISTRY[name] = func
        return func
    return decorator

def load_plugins():
    for filename in os.listdir(PLUGIN_DIR):
        if filename.endswith(".py") and not filename.startswith("_"):
            filepath = os.path.join(PLUGIN_DIR, filename)
            module_name = filename[:-3]
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            
            if spec is None:
                print(f"[Plugin Error] Could not create spec for {module_name}")
                continue
                
            module = importlib.util.module_from_spec(spec)
            
            if spec.loader is None:
                print(f"[Plugin Error] No loader available for {module_name}")
                continue
                
            try:
                spec.loader.exec_module(module)
                print(f"[Plugin] Loaded: {module_name}")
            except Exception as e:
                print(f"[Plugin Error] Failed to load {module_name}: {e}")

def get_plugin(name):
    """Get a specific plugin by name"""
    return PLUGIN_REGISTRY.get(name)

def list_plugins():
    """List all available plugins"""
    return list(PLUGIN_REGISTRY.keys())

def execute_plugin(name, *args, **kwargs):
    """Execute a plugin with given arguments"""
    plugin = get_plugin(name)
    if plugin is None:
        raise ValueError(f"Plugin '{name}' not found")
    
    try:
        return plugin(*args, **kwargs)
    except Exception as e:
        print(f"[Plugin Error] Error executing {name}: {e}")
        raise

def reload_plugins():
    """Reload all plugins"""
    global PLUGIN_REGISTRY
    PLUGIN_REGISTRY.clear()
    load_plugins()

# Call this at startup to populate PLUGIN_REGISTRY
load_plugins()
=======
# core/plugin_manager.py
import os
import importlib.util

PLUGIN_REGISTRY = {}

PLUGIN_DIR = os.path.join(os.path.dirname(__file__), "..", "plugins")

os.makedirs(PLUGIN_DIR, exist_ok=True)

def register_plugin(name):
    def decorator(func):
        PLUGIN_REGISTRY[name] = func
        return func
    return decorator

def load_plugins():
    for filename in os.listdir(PLUGIN_DIR):
        if filename.endswith(".py") and not filename.startswith("_"):
            filepath = os.path.join(PLUGIN_DIR, filename)
            module_name = filename[:-3]
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            
            if spec is None:
                print(f"[Plugin Error] Could not create spec for {module_name}")
                continue
                
            module = importlib.util.module_from_spec(spec)
            
            if spec.loader is None:
                print(f"[Plugin Error] No loader available for {module_name}")
                continue
                
            try:
                spec.loader.exec_module(module)
                print(f"[Plugin] Loaded: {module_name}")
            except Exception as e:
                print(f"[Plugin Error] Failed to load {module_name}: {e}")

def get_plugin(name):
    """Get a specific plugin by name"""
    return PLUGIN_REGISTRY.get(name)

def list_plugins():
    """List all available plugins"""
    return list(PLUGIN_REGISTRY.keys())

def execute_plugin(name, *args, **kwargs):
    """Execute a plugin with given arguments"""
    plugin = get_plugin(name)
    if plugin is None:
        raise ValueError(f"Plugin '{name}' not found")
    
    try:
        return plugin(*args, **kwargs)
    except Exception as e:
        print(f"[Plugin Error] Error executing {name}: {e}")
        raise

def reload_plugins():
    """Reload all plugins"""
    global PLUGIN_REGISTRY
    PLUGIN_REGISTRY.clear()
    load_plugins()

# Call this at startup to populate PLUGIN_REGISTRY
load_plugins()
>>>>>>> 20a510e90c83aa50461841f557e9447d03056c8d
