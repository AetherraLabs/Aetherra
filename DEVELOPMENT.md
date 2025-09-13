# 🏗️ Development Setup Guide

This guide will help you set up a professional development environment for Aetherra.

## Quick Start

1. **Automated Setup** (Recommended):
   ```bash
   python setup_dev_environment.py
   ```

2. **Manual Setup**:
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate     # Windows
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements/dev.txt
   
   # Setup pre-commit hooks
   pre-commit install --install-hooks
   ```

## Project Structure

```
Aetherra/
├── src/                      # Organized source code
│   ├── aetherra_core/        # Core system components
│   └── aetherra_services/    # Service layer modules
├── scripts/                  # Utility and maintenance scripts
├── demos/                    # UI demos and examples
├── tests/                    # All test files
├── reports/                  # Generated reports and analysis
├── docs/                     # Documentation
├── tools/                    # Development tools
└── requirements/             # Dependency specifications
```

## Development Workflow

### 1. Code Quality Checks
```bash
# Run all quality checks
pre-commit run --all-files

# Individual checks
black .                       # Format code
isort .                       # Sort imports
ruff check .                  # Lint code
mypy .                        # Type checking
```

### 2. Testing
```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest tests/capabilities/     # Core capability tests
python -m pytest tests/unit/             # Unit tests
python -m pytest tests/integration/      # Integration tests

# With coverage
python -m pytest --cov=src --cov-report=html
```

### 3. Security Scanning
```bash
# Security checks
bandit -r src/
safety check
pip-audit
```

## Environment Variables

Key environment variables for development:

```bash
# Enable development features
export AETHERRA_PROFILE=development

# Enable verbose logging
export AETHERRA_LOG_LEVEL=DEBUG

# Enable AI API for testing
export AETHERRA_AI_API_ENABLED=1
export AETHERRA_AI_API_STREAM=1

# Enable metrics
export AETHERRA_PROMETHEUS=1
```

## Common Tasks

### Running the Application
```bash
# Start the hub server
python -m aetherra_hub.compat

# Start with specific port
python -m aetherra_hub.compat --port 3001
```

### Building Documentation
```bash
cd docs/
make html
```

### Running Performance Tests
```bash
# Memory profiling
python -m memory_profiler your_script.py

# Performance testing
locust -f tests/performance/
```

## Troubleshooting

### Port Conflicts
If you see "Address already in use" errors in tests:
```bash
# Find processes using common test ports
lsof -i :3015
kill -9 <PID>
```

### Import Errors
After reorganization, some imports may need updating:
```bash
# Update import paths
python scripts/aetherra_import_updater.py
```

### Pre-commit Issues
```bash
# Reset pre-commit if hooks fail
pre-commit uninstall
pre-commit install --install-hooks
pre-commit run --all-files
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes following the code style
4. Ensure tests pass: `python -m pytest`
5. Commit with descriptive messages
6. Push and create a Pull Request

## Code Style Guidelines

- **Line Length**: 120 characters
- **Import Style**: isort with black profile
- **Type Hints**: Required for public APIs
- **Docstrings**: Google style for public functions
- **Testing**: Pytest with descriptive test names

## Getting Help

- **Documentation**: Check `docs/` directory
- **Issues**: Use GitHub Issues for bugs and features
- **Discussion**: Use GitHub Discussions for questions
- **Code Style**: Follow the pre-commit configuration