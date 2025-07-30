"""
🌉 Plugin API Bridge  
Interface for safe plugin invocation from Lyrixa
"""

from typing import Dict, Any, Optional
from ..kernel.plugin_manager import PluginManager

class PluginAPI:
    """Clean plugin interface for Lyrixa"""
    
    def __init__(self):
        self.manager = PluginManager()
    
    def invoke_plugin(self, plugin_id: str, action: str, **kwargs) -> Any:
        """Safely invoke plugin action"""
        return self.manager.execute_plugin(plugin_id, action, **kwargs)
    
    def list_plugins(self) -> List[Dict]:
        """Get available plugins"""
        return self.manager.list_available_plugins()
