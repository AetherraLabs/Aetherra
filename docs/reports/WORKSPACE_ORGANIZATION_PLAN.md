# aetherra Project - Workspace Organization Plan

## Current Status
- Modular UI architecture successfully implemented
- Many files are currently scattered in the root directory
- Some folders already exist: core/, ui/, docs/, tests/, plugins/, stdlib/, etc.
- Core folder needs further modularization

## Target Structure

```
aetherra Project/
├── .env
├── .gitignore
├── LICENSE
├── README.md
├── pyproject.toml
├── requirements.txt
├── setup.py (new)
│
├── docs/                           # All documentation
│   ├── ARCHITECTURE.md
│   ├── INSTALLATION.md
│   ├── TUTORIAL.md
│   ├── CONTRIBUTING.md
│   ├── api/                        # API documentation
│   ├── guides/                     # User guides
│   └── reports/                    # Status reports and completion reports
│
├── src/                            # Main source code
│   ├── aetherra/                  # Core aetherra package
│   │   ├── __init__.py
│   │   ├── core/                   # Core engine components
│   │   │   ├── __init__.py
│   │   │   ├── parser/             # Parser subsystem
│   │   │   ├── interpreter/        # Interpreter subsystem
│   │   │   ├── ast/                # AST components
│   │   │   ├── memory/             # Memory systems
│   │   │   ├── ai/                 # AI integration
│   │   │   └── utils/              # Core utilities
│   │   ├── ui/                     # User interface (already modular)
│   │   ├── plugins/                # Plugin system
│   │   ├── stdlib/                 # Standard library
│   │   └── cli/                    # Command-line interface
│   └── Lyrixa/                  # Lyrixa application
│       ├── __init__.py
│       └── main.py
│
├── launchers/                      # Application launchers
│   ├── launch_aetherra.py
│   ├── launch_Lyrixa.py
│   ├── launch_playground.py
│   └── legacy/                     # Legacy launchers
│
├── scripts/                        # Utility scripts
│   ├── setup/                      # Setup scripts
│   ├── build/                      # Build scripts
│   └── tools/                      # Development tools
│
├── tests/                          # Test suite
│   ├── unit/                       # Unit tests
│   ├── integration/                # Integration tests
│   ├── performance/                # Performance tests
│   └── fixtures/                   # Test fixtures
│
├── examples/                       # Example programs
│   ├── basic/                      # Basic examples
│   ├── advanced/                   # Advanced examples
│   └── demos/                      # Demo applications
│
├── data/                           # Data files and stores
│   ├── memory_store.json.example
│   ├── goals_store.json.example
│   └── aetherra_functions.json.example
│
├── temp/                           # Temporary files
├── logs/                           # Log files
├── archive/                        # Archived files
└── .vscode/                        # VS Code configuration
```

## Core Modularization Plan

Break down the large core files into specialized subsystems:

### 1. Parser Subsystem (`src/aetherra/core/parser/`)
- `__init__.py`
- `grammar.py` (from aetherra_grammar.py)
- `lexer.py`
- `parser.py` (from aetherra_parser.py)
- `enhanced_parser.py`
- `intent_parser.py`
- `natural_compiler.py`

### 2. AST Subsystem (`src/aetherra/core/ast/`)
- `__init__.py`
- `nodes.py`
- `builder.py`
- `parser.py` (from ast_parser.py)
- `optimizer.py`

### 3. Interpreter Subsystem (`src/aetherra/core/interpreter/`)
- `__init__.py`
- `base.py`
- `enhanced.py` (from enhanced_interpreter.py)
- `runtime.py`
- `block_executor.py`
- `debug_system.py`

### 4. Memory Subsystem (`src/aetherra/core/memory/`)
- `__init__.py`
- `base.py` (from memory.py)
- `vector.py` (from vector_memory.py)
- `temporal.py`
- `enhanced.py`

### 5. AI Integration (`src/aetherra/core/ai/`)
- `__init__.py`
- `runtime.py` (from ai_runtime.py)
- `collaboration.py` (from ai_collaboration.py)
- `llm_integration.py`
- `multi_llm_manager.py`
- `local_ai.py`
- `universal_ai.py`
- `chat_router.py`

### 6. Core Utils (`src/aetherra/core/utils/`)
- `__init__.py`
- `functions.py`
- `input_utils.py`
- `performance_optimizer.py`

## File Migration Plan

### Phase 1: Create new directory structure
### Phase 2: Move and reorganize core files
### Phase 3: Move launchers, scripts, and utilities
### Phase 4: Organize documentation and reports
### Phase 5: Clean up obsolete files
### Phase 6: Update all imports and references
### Phase 7: Rename workspace to "aetherra Project"

## Benefits

1. **Improved VS Code Performance**: Smaller, focused files reduce parsing overhead
2. **Better Maintainability**: Clear separation of concerns
3. **Enhanced Discoverability**: Logical file organization
4. **Easier Testing**: Isolated components are easier to test
5. **Professional Structure**: Industry-standard project layout
6. **Reduced Complexity**: Breaking monolithic files into focused modules

## Implementation Notes

- All imports will be updated to reflect new structure
- Legacy files will be moved to archive/ or deleted if obsolete
- Package __init__.py files will provide clean public APIs
- Documentation will be updated to reflect new structure
