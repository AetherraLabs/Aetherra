# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Aetherra AI OS
Builds a standalone Windows executable
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all Aetherra submodules
aetherra_hiddenimports = collect_submodules('Aetherra')

# Additional hidden imports that PyInstaller might miss
hidden_imports = [
    'aetherra_kernel_loop',
    'aetherra_service_registry',
    'aetherra_agent_fabric',
    'aetherra_persistent_memory',
    'aetherra_hub',
    'aetherra_hub.app',
    'aetherra_hub.blueprints',
    'aetherra_hub.blueprints.ai_stream',
    'aetherra_hub.blueprints.lyrixa_chat',
    'aetherra_event_bus',
    'aetherra_plugin_discovery',
    'flask',
    'flask_socketio',
    'flask_cors',
    'socketio',
    'engineio',
    'werkzeug',
    'jinja2',
    'click',
    'dotenv',
    'openai',
    'anthropic',
    'requests',
    'aiohttp',
    'asyncio',
    'sqlite3',
    'json',
    'yaml',
    'toml',
    'psutil',
    'numpy',
] + aetherra_hiddenimports

# Collect data files
aetherra_datas = collect_data_files('Aetherra')

# Additional data files to include
datas = [
    ('.env.example', '.'),
    ('config.json', '.'),
    ('Aetherra/lyrixa/gui/dist', 'Aetherra/lyrixa/gui/dist'),  # Bundle Lyrixa UI static files
] + aetherra_datas

# Binaries (if any platform-specific libraries are needed)
binaries = []

a = Analysis(
    ['aetherra_os_launcher.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',  # Exclude if not needed
        'tkinter',     # Exclude if not using GUI
        'PySide6',
        'PyQt6',
        'jupyter',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AetherraOS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Set to False for GUI mode
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path if available: 'icon.ico'
    version_file=None,  # Can generate version_file.txt with version info
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AetherraOS',
)
