# Aetherra Tests

This directory contains all test files for the Aetherra project, organized by category.

## Directory Structure

```
tests/
├── conftest.py          # Pytest configuration and fixtures
├── ai/                  # AI and intelligence system tests
├── gui/                 # GUI and interface tests
├── integration/         # Integration and system tests
└── unit/                # Unit tests for core components
```

## Test Categories

### AI Tests (`tests/ai/`)
Tests for AI functionality, intelligence systems, and machine learning components:
- `test_ai_fallback.py` - AI fallback system tests
- `test_chat_intelligence.py` - Chat AI functionality
- `test_intelligence_core.py` - Core intelligence systems
- `test_multi_*.py` - Multi-agent and multi-provider tests
- `test_neural_*.py` - Neural interface tests
- `test_openai_integration.py` - OpenAI API integration

### GUI Tests (`tests/gui/`)
Tests for graphical user interfaces and visual components:
- `test_gui.py` - Main GUI functionality
- `test_hybrid_gui.py` - Hybrid interface tests
- `test_live_gui_generation.py` - Dynamic GUI generation
- `test_lyrixa_gui.py` - Lyrixa interface tests

### Integration Tests (`tests/integration/`)
Tests for system integration, phases, and cross-component functionality:
- `test_phase*.py` - System phase tests
- `test_plugin_*.py` - Plugin system tests
- `test_startup.py` - System startup tests
- `test_launcher_*.py` - Launcher functionality

### Unit Tests (`tests/unit/`)
Tests for individual components and utilities:
- `test_builtin_intelligence.py` - Built-in intelligence tests
- `test_command_handlers.py` - Command handling
- `test_imports.py` - Import system tests
- `test_memory.py` - Memory system tests
- `test_unicode_fix.py` - Unicode handling

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Categories
```bash
pytest tests/ai/          # AI tests only
pytest tests/gui/         # GUI tests only
pytest tests/integration/ # Integration tests only
pytest tests/unit/        # Unit tests only
```

### Run Specific Test Files
```bash
pytest tests/ai/test_intelligence_core.py
pytest tests/gui/test_gui.py
```

### Run with Coverage
```bash
pytest tests/ --cov=Aetherra --cov-report=html
```

## Test Configuration

- `conftest.py` contains shared fixtures and test configuration
- Test environment variables are set automatically
- Database connections use temporary test databases
- Mock fixtures are available for external APIs

## Adding New Tests

1. Place test files in the appropriate category directory
2. Follow the naming convention: `test_*.py`
3. Import required fixtures from `conftest.py`
4. Use descriptive test function names: `test_feature_should_do_something()`

## CI/CD Integration

Tests are automatically run in CI/CD pipelines:
- All tests must pass before merging
- Coverage reports are generated
- Performance benchmarks are tracked
