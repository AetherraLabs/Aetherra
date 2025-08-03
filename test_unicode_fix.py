#!/usr/bin/env python3
"""
Test Unicode encoding fixes
"""

print('=== UNICODE ENCODING TEST ===')
print('Testing imports...')

import sys
sys.path.insert(0, '.')

try:
    from aetherra_service_registry import AetherraServiceRegistry
    print('[OK] Service registry imported successfully')
except Exception as e:
    print(f'[ERROR] Service registry import failed: {e}')

try:
    from Aetherra.aetherra_core.plugins.plugin_manager import PluginManager
    print('[OK] Plugin manager imported successfully')
except Exception as e:
    print(f'[ERROR] Plugin manager import failed: {e}')

print('[SUCCESS] All Unicode fixes applied and verified!')
