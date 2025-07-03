# 🧹 NeuroCode Workspace Cleanup Plan

## Files to Remove

### 1. Version Number Files (Likely leftover artifacts)
- 0.17.0, 0.61.0, 0.7.0, 1.24.0, 13.0.0, 2.15.0, 3.1.0, 3.2.0, 3.7.0, 5.9.0

### 2. Debug and Testing Files (Redundant)
- parse_debug.py, parse_debug2.py, parse_debug3.py, parse_debug4.py
- debug_demo.py
- quick_debug_test.py
- tokenize_debug.py
- check_qt.py

### 3. Duplicate/Legacy Core Files
- neurocode.py (superseded by core/interpreter.py)
- neurocode_engine.py (superseded by core modules)
- neuroplex.py (superseded by ui/neuroplex_gui.py)

### 4. Documentation Files (Keep only essential ones)
Remove redundant documentation:
- AST_PARSER_FIXES.md
- COMPLETE_DEBUG_DEMO.py
- DEBUG_SYSTEM_GUIDE.md
- DOCUMENTATION_VERIFICATION_REPORT.md
- FINAL_VERIFICATION_SUMMARY.md
- GUI_FIXES_COMPLETE.md
- IMPLEMENTATION_COMPLETE.md
- IMPLEMENTATION_SUMMARY.md
- LANGUAGE_INDEPENDENCE_ACHIEVED.md
- NEUROCODE_FOUNDATION_ESTABLISHED.md
- NEUROCODE_REVOLUTION.md
- NEUROCODE_VOICE_ACHIEVED.md
- NEUROPLEX_GUI_GUIDE.md
- NEUROPLEX_GUI_STATUS.md
- REVOLUTION_ACHIEVED.md
- SELF_AWARENESS_DEMO.md
- VSCODE_SETUP_COMPLETE.md
- WORKSPACE_ANALYSIS_COMPLETE.md

### 5. Redundant UI Files
- ui/neuro_chat.py (functionality integrated into main GUI)
- ui/neuro_chat_console.py
- ui/neuro_chat_fixed.py
- ui/neuro_ui.py (superseded by neuroplex_gui.py)

### 6. Test Files (Keep only essential ones)
- demo_code.py
- neurocode_language_demo.py
- integration_test.py
- workspace_analysis.py

### 7. Duplicate Requirements Files
- requirements_optimized.txt (keep requirements.txt)

### 8. Legacy Launch Files
- launch_gui.py (superseded by ui/neuroplex_gui.py main())
- startup.py (redundant)

## Files to Keep (Essential)

### Core System
- core/ (entire directory - essential)
- ui/neuroplex_gui.py (main GUI)
- plugins/ (plugin system)
- stdlib/ (standard library)

### Configuration
- .vscode/ (VS Code settings)
- requirements.txt
- .gitignore
- README.md

### Documentation (Essential)
- NEUROCODE_LANGUAGE_SPEC.md
- NEUROCODE_MANIFESTO.md
- NEUROCODE_UNIVERSAL_STANDARD.md
- ARCHITECTURE.md
- OPTIMIZATION_GUIDE.md
- IMMEDIATE_OPTIMIZATION_SUMMARY.md
- COMPLETE_OPTIMIZATION_GUIDE.md
- NEUROPLEX_ANALYSIS_REPORT.md
- MANUAL_EXTENSION_INSTALL.md
- SELF_EDITING_ARCHITECTURE.md
- SELF_EDITING_GUIDE.md

### Test Files (Essential)
- test_core_features.py
- test_advanced_syntax.py
- test_debug_system.py
- test_gui.py
- analysis_test.py

### Demo Files
- *.aether files (NeuroCode examples)

### Setup Scripts
- setup_vscode_extensions.py
- setup_optimization.py

### Data Files
- goals_store.json
- memory_store.json
- neurocode_functions.json
- Neuroplex.ico

### Main Entry Points
- main.py (if it's the main entry point)

## Total Files to Remove: ~45 files
## Files to Keep: ~25 essential files + directories
