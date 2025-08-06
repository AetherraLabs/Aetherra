"""
Workflowbuilder Plugin Stub
=====================================

This is a stub file to prevent import errors during plugin discovery.
The actual implementation may be located elsewhere or needs to be created.
"""

def get_plugin_info():
    """Return basic plugin information"""
    return {
        "name": "WorkflowBuilder",
        "version": "1.0.0",
        "description": "Stub plugin for WorkflowBuilder",
        "status": "stub",
        "capabilities": []
    }

def activate():
    """Activate the plugin"""
    print(f"📌 Stub plugin WorkflowBuilder activated")

def deactivate():
    """Deactivate the plugin"""
    print(f"📌 Stub plugin WorkflowBuilder deactivated")

# Plugin class (optional)
class WorkflowbuilderPlugin:
    """Stub plugin class"""
    
    def __init__(self):
        self.name = "WorkflowBuilder"
        self.version = "1.0.0"
        self.active = False
    
    def activate(self):
        self.active = True
        return True
    
    def deactivate(self):
        self.active = False
        return True
