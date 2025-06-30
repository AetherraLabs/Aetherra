# NeuroCode Workspace Reorganization Plan

## Current Issues Identified

### Structural Problems
1. **Duplicate core directories** - We have both `/core/` and `/src/neurocode/core/`
2. **Scattered CLI files** - Multiple CLI files in root instead of organized structure
3. **Mixed concerns** - Demo files, launchers, and core code all in root
4. **Legacy files** - Multiple completion/status markdown files cluttering root
5. **Inconsistent naming** - Mix of `neurocode_*` and `neuroplex_*` patterns

### Modularization Opportunities
1. **Persona System** - Can be its own package
2. **Plugin System** - Should be fully modular
3. **CLI Tools** - Need dedicated CLI package structure
4. **Demos & Examples** - Should be organized by feature
5. **Documentation** - Needs better organization

## Proposed New Structure

```
neurocode/
├── README.md
├── pyproject.toml
├── requirements.txt
├── LICENSE
├── .gitignore
├── .env.example
│
├── src/
│   └── neurocode/
│       ├── __init__.py
│       ├── cli/                    # All CLI tools
│       │   ├── __init__.py
│       │   ├── main.py            # Main CLI entry point
│       │   ├── persona.py         # Persona management CLI
│       │   ├── plugin.py          # Plugin management CLI
│       │   └── demo.py            # Demo runner CLI
│       │
│       ├── core/                   # Core engine components
│       │   ├── __init__.py
│       │   ├── engine/            # Main engine
│       │   ├── parser/            # Language parsing
│       │   ├── interpreter/       # Code execution
│       │   ├── memory/            # Memory systems
│       │   └── ai/               # AI integration
│       │
│       ├── persona/               # Persona system (modular)
│       │   ├── __init__.py
│       │   ├── engine.py          # Persona engine
│       │   ├── archetypes.py      # Archetype definitions
│       │   ├── emotional_memory.py
│       │   ├── contextual_adaptation.py
│       │   └── voice_system.py
│       │
│       ├── plugins/               # Plugin system
│       │   ├── __init__.py
│       │   ├── manager.py         # Plugin manager
│       │   ├── registry.py        # Plugin registry
│       │   ├── loader.py          # Plugin loading
│       │   └── builtin/          # Built-in plugins
│       │
│       ├── stdlib/                # Standard library
│       │   ├── __init__.py
│       │   ├── io/
│       │   ├── data/
│       │   └── utils/
│       │
│       └── ui/                    # User interfaces
│           ├── __init__.py
│           ├── repl/             # REPL interface
│           ├── web/              # Web interface
│           └── desktop/          # Desktop GUI (future)
│
├── examples/                       # Example code and demos
│   ├── basic/                     # Basic examples
│   ├── persona/                   # Persona system demos
│   ├── plugins/                   # Plugin examples
│   └── advanced/                  # Advanced examples
│
├── docs/                          # Documentation
│   ├── user/                     # User guides
│   ├── developer/                # Developer docs
│   ├── api/                      # API documentation
│   └── specs/                    # Technical specifications
│
├── tests/                         # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── fixtures/                 # Test fixtures
│
├── tools/                         # Development tools
│   ├── build/                    # Build scripts
│   ├── deploy/                   # Deployment tools
│   └── dev/                      # Development utilities
│
├── data/                          # Data files
│   ├── examples/                 # Example data
│   ├── templates/                # Code templates
│   └── configs/                  # Configuration files
│
└── scripts/                       # Utility scripts
    ├── install.py
    ├── setup.py
    └── migrate.py
```

## Migration Steps

### Phase 1: Core Restructuring
1. Create new modular structure under `/src/neurocode/`
2. Move and reorganize core components
3. Update import paths throughout codebase
4. Create proper `__init__.py` files with clean APIs

### Phase 2: CLI Consolidation
1. Consolidate all CLI tools into `/src/neurocode/cli/`
2. Create unified CLI entry point
3. Implement plugin-based CLI architecture
4. Update launcher scripts

### Phase 3: Persona System Modularization
1. Extract persona system into dedicated package
2. Clean up dependencies and interfaces
3. Create modular configuration system
4. Implement plugin-style persona loading

### Phase 4: Plugin System Enhancement
1. Formalize plugin API and interfaces
2. Create plugin discovery and loading system
3. Implement plugin dependency management
4. Build plugin development tools

### Phase 5: Documentation & Examples
1. Reorganize documentation by audience
2. Create comprehensive examples hierarchy
3. Build interactive tutorials
4. Generate API documentation

### Phase 6: Cleanup & Polish
1. Remove legacy files and duplicates
2. Standardize naming conventions
3. Create migration guides
4. Update build and deployment scripts

## Benefits

### For Developers
- **Clear separation of concerns** - Each component has dedicated space
- **Easy navigation** - Logical hierarchy and naming
- **Modular development** - Components can be developed independently
- **Clean imports** - No more relative import mess

### For Users
- **Single entry point** - One CLI tool for everything
- **Plugin ecosystem** - Easy to extend and customize
- **Better documentation** - Organized by use case
- **Consistent experience** - Unified interface across all tools

### For Contributors
- **Clear contribution guidelines** - Know where to put what
- **Isolated testing** - Test components independently
- **Easier code review** - Smaller, focused changes
- **Better CI/CD** - Modular testing and deployment

## Implementation Priority

1. **High Priority** - Core restructuring and CLI consolidation
2. **Medium Priority** - Persona and plugin modularization
3. **Low Priority** - Documentation reorganization and examples

This reorganization will set NeuroCode up for massive scale and community contribution!
