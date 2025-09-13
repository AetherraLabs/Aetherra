#!/usr/bin/env python3
"""
Generate compatibility imports for reorganized modules.
This creates backward compatibility shims for any imports that might be broken.
"""

import os
from pathlib import Path

def create_compatibility_imports():
    """Create compatibility import files for moved modules."""
    
    # Map of old module names to new locations
    moved_modules = {
        # Services
        'aetherra_aar_broker': 'src.aetherra_services.aetherra_aar_broker',
        'aetherra_cognitive_task_manager': 'src.aetherra_services.aetherra_cognitive_task_manager',
        'aetherra_core_analyzer': 'src.aetherra_services.aetherra_core_analyzer',
        'aetherra_event_bus': 'src.aetherra_services.aetherra_event_bus',
        'aetherra_file_watcher': 'src.aetherra_services.aetherra_file_watcher',
        'aetherra_hmr_controller': 'src.aetherra_services.aetherra_hmr_controller',
        'aetherra_hub_server': 'src.aetherra_services.aetherra_hub_server',
        'aetherra_kernel_loop': 'src.aetherra_services.aetherra_kernel_loop',
        'aetherra_live_monitor': 'src.aetherra_services.aetherra_live_monitor',
        'aetherra_meta_memory': 'src.aetherra_services.aetherra_meta_memory',
        'aetherra_module_manager': 'src.aetherra_services.aetherra_module_manager',
        'aetherra_outbox': 'src.aetherra_services.aetherra_outbox',
        'aetherra_persistent_memory': 'src.aetherra_services.aetherra_persistent_memory',
        'aetherra_plugin_discovery': 'src.aetherra_services.aetherra_plugin_discovery',
        'aetherra_plugin_viewer': 'src.aetherra_services.aetherra_plugin_viewer',
        'aetherra_quantum_meta_learning': 'src.aetherra_services.aetherra_quantum_meta_learning',
        'aetherra_self_organizer': 'src.aetherra_services.aetherra_self_organizer',
        'aetherra_shared_service_registry': 'src.aetherra_services.aetherra_shared_service_registry',
        
        # Core modules
        'aetherra_adaptive_behavior': 'src.aetherra_core.aetherra_adaptive_behavior',
        'aetherra_agent_daemon': 'src.aetherra_core.aetherra_agent_daemon',
        'aetherra_agent_fabric': 'src.aetherra_core.aetherra_agent_fabric',
        'aetherra_cognitive_task_manager_simple': 'src.aetherra_core.aetherra_cognitive_task_manager_simple',
        'aetherra_os': 'src.aetherra_core.aetherra_os',
        'aetherra_os_launcher': 'src.aetherra_core.aetherra_os_launcher',
        'aetherra_startup': 'src.aetherra_core.aetherra_startup',
        'beyond_transcendence_engine': 'src.aetherra_core.beyond_transcendence_engine',
        'quantum_memory_bridge': 'src.aetherra_core.quantum_memory_bridge',
    }
    
    created_files = []
    
    for old_name, new_location in moved_modules.items():
        # Skip if compatibility file already exists
        compat_file = f"{old_name}.py"
        if os.path.exists(compat_file):
            continue
            
        # Create compatibility import file
        content = f'''# Compatibility imports for moved modules
# This file provides backward compatibility for imports after reorganization

# Import {old_name} from new location
from {new_location} import *
'''
        
        with open(compat_file, 'w') as f:
            f.write(content)
        
        created_files.append(compat_file)
        print(f"Created compatibility import: {compat_file}")
    
    return created_files

if __name__ == "__main__":
    print("🔗 Creating compatibility imports for reorganized modules...")
    created = create_compatibility_imports()
    
    if created:
        print(f"\n✅ Created {len(created)} compatibility import files")
        print("These files provide backward compatibility for any code that imports")
        print("modules from their old locations.")
    else:
        print("\n✅ All compatibility imports already exist")
    
    print("\n💡 Note: For new code, please use the new import paths:")
    print("   from src.aetherra_core.* import ...")
    print("   from src.aetherra_services.* import ...")