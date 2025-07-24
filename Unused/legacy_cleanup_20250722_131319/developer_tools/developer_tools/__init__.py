"""
Aetherra & Lyrixa Developer Tools Package

A comprehensive suite of developer tools to enhance project reliability,
prevent data loss, and improve debugging capabilities.
"""

__version__ = "1.0.0"
__author__ = "Aetherra Development Team"

# Import only implemented modules to avoid import errors
try:
    from .safety.write_guard import WriteGuard, WriteGuardConfig
    WRITE_GUARD_AVAILABLE = True
except ImportError:
    WRITE_GUARD_AVAILABLE = False

try:
    from .safety.safe_save import SafeSavePlugin, SafeSaveConfig
    SAFE_SAVE_AVAILABLE = True
except ImportError:
    SAFE_SAVE_AVAILABLE = False

try:
    from .memory.inspector import MemoryInspector, MemoryEditor
    MEMORY_INSPECTOR_AVAILABLE = True
except ImportError:
    MEMORY_INSPECTOR_AVAILABLE = False

try:
    from .plugins.sandbox import PluginSandbox, SandboxConfig
    PLUGIN_SANDBOX_AVAILABLE = True
except ImportError:
    PLUGIN_SANDBOX_AVAILABLE = False

try:
    from .monitoring.health_dashboard import ProjectHealthDashboard
    from .monitoring.error_tracker import ErrorTracker
    from .monitoring.performance_profiler import PerformanceProfiler
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

try:
    from .memory.backup import MemoryWorkflowBackup
    MEMORY_BACKUP_AVAILABLE = True
except ImportError:
    MEMORY_BACKUP_AVAILABLE = False

try:
    from .knowledge.sync import KnowledgeBaseSync
    KNOWLEDGE_SYNC_AVAILABLE = True
except ImportError:
    KNOWLEDGE_SYNC_AVAILABLE = False

# Only export what's available
__all__ = []

if WRITE_GUARD_AVAILABLE:
    __all__.extend(['WriteGuard', 'WriteGuardConfig'])

if SAFE_SAVE_AVAILABLE:
    __all__.extend(['SafeSavePlugin', 'SafeSaveConfig'])

if MEMORY_INSPECTOR_AVAILABLE:
    __all__.extend(['MemoryInspector', 'MemoryEditor'])

if PLUGIN_SANDBOX_AVAILABLE:
    __all__.extend(['PluginSandbox', 'SandboxConfig'])

if MONITORING_AVAILABLE:
    __all__.extend(['ProjectHealthDashboard', 'ErrorTracker', 'PerformanceProfiler'])

if MEMORY_BACKUP_AVAILABLE:
    __all__.extend(['MemoryWorkflowBackup'])

if KNOWLEDGE_SYNC_AVAILABLE:
    __all__.extend(['KnowledgeBaseSync'])

def get_available_tools():
    """Get list of available developer tools"""
    tools = {}

    if WRITE_GUARD_AVAILABLE:
        tools['WriteGuard'] = 'File write monitoring and protection'

    if SAFE_SAVE_AVAILABLE:
        tools['SafeSave'] = 'Enforced atomic write operations'

    if MEMORY_INSPECTOR_AVAILABLE:
        tools['MemoryInspector'] = 'Memory inspection and editing'

    if PLUGIN_SANDBOX_AVAILABLE:
        tools['PluginSandbox'] = 'Isolated plugin testing environment'

    if MONITORING_AVAILABLE:
        tools['ProjectHealthDashboard'] = 'Real-time system monitoring'
        tools['ErrorTracker'] = 'Centralized error logging and analysis'
        tools['PerformanceProfiler'] = 'Resource usage analysis'

    if MEMORY_BACKUP_AVAILABLE:
        tools['MemoryWorkflowBackup'] = 'Versioned memory and workflow snapshots'

    if KNOWLEDGE_SYNC_AVAILABLE:
        tools['KnowledgeBaseSync'] = 'Auto-sync docs to memory system'

    return tools

def print_available_tools():
    """Print available developer tools"""
    tools = get_available_tools()
    print("🛠️ Available Developer Tools:")
    for tool, description in tools.items():
        print(f"  ✅ {tool:30}: {description}")

    if not tools:
        print("  ❌ No developer tools available")

# Version and status information
def get_status():
    """Get developer tools status"""
    return {
        'version': __version__,
        'available_tools': list(get_available_tools().keys()),
        'total_tools': len(get_available_tools()),
        'write_guard_available': WRITE_GUARD_AVAILABLE,
        'safe_save_available': SAFE_SAVE_AVAILABLE,
        'memory_inspector_available': MEMORY_INSPECTOR_AVAILABLE,
        'plugin_sandbox_available': PLUGIN_SANDBOX_AVAILABLE,
        'monitoring_available': MONITORING_AVAILABLE,
        'memory_backup_available': MEMORY_BACKUP_AVAILABLE,
        'knowledge_sync_available': KNOWLEDGE_SYNC_AVAILABLE
    }
