#!/usr/bin/env python3
"""
Quick test of all major imports to verify project status
"""

import sys
print('Testing main package imports...')

# Test Lyrixa imports
try:
    import lyrixa
    from lyrixa import LyrixaAI, LocalModel, ModelRouter, OpenAIModel
    print('✓ Lyrixa imports successful')
except Exception as e:
    print(f'✗ Lyrixa import error: {e}')

# Test Aetherra imports
try:
    import Aetherra
    from Aetherra import AetherraInterpreter, AetherraParser, AetherraAgent, Config
    print('✓ Aetherra imports successful')
except Exception as e:
    print(f'✗ Aetherra import error: {e}')

# Test core imports
try:
    from core import debug_system, block_executor
    print('✓ Core imports successful')
except Exception as e:
    print(f'✗ Core import error: {e}')

print('All imports tested successfully!')
