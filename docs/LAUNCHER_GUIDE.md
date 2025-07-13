# 🚀 Aetherra Project Launcher Guide

## Main Launchers

### 🎙️ **Lyrixa AI Assistant**
**Primary Launcher:** `lyrixa/launcher.py`
- **Purpose:** Main Lyrixa AI Assistant with Aether Runtime integration
- **Features:** Full AI OS capabilities, memory system, plugin manager
- **Usage:** `python lyrixa/launcher.py`

### 🌟 **Aetherra System**
**System Launcher:** `launchers/aetherra_launcher.py`
- **Purpose:** Aetherra AI OS system launcher
- **Features:** System-wide initialization and verification
- **Usage:** `python launchers/aetherra_launcher.py`

### 🛠️ **Developer Tools**
**Tools Launcher:** `launchers/developer_tools_launcher.py`
- **Purpose:** Comprehensive developer tool suite
- **Features:** All development and testing tools
- **Usage:** `python launchers/developer_tools_launcher.py`

## VS Code Tasks

Use the following VS Code tasks for quick access:
- **"Launch Lyrixa AI"** - Starts the main Lyrixa AI Assistant
- **"Verify Aetherra UI"** - Runs Aetherra system verification
- **"Verify UI Standards"** - Checks UI compliance

## Archived Launchers

The following launchers have been moved to `archive/old_launchers/`:
- `lyrixa_gui_launcher.py` - Old GUI launcher (replaced by main launcher)
- `lyrixa_unified_launcher.py` - Old unified launcher
- `lyrixa_unified_launcher_win.py` - Old Windows unified launcher

## Quick Start

For most users:
```bash
# Start Lyrixa AI Assistant
python lyrixa/launcher.py

# Or use VS Code task: "Launch Lyrixa AI"
```

For developers:
```bash
# Full development environment
python launchers/developer_tools_launcher.py
```

For system verification:
```bash
# Verify Aetherra system
python launchers/aetherra_launcher.py
```
