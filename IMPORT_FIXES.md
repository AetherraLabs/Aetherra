# [TOOL] Fixing Import Errors in Aetherra

When you fork the Aetherra repository, you might encounter import errors. This guide will help you resolve them quickly.

## Common Import Issues

### 1. **Missing `__init__.py` files**
```
ModuleNotFoundError: No module named 'aetherra_core'
ImportError: cannot import name 'memory_system' from 'aetherra_core.memory'
```

### 2. **Python path issues**
```
ImportError: attempted relative import with no known parent package
ModuleNotFoundError: No module named 'Aetherra.aetherra_core'
```

### 3. **Missing dependencies**
```
ModuleNotFoundError: No module named 'flask'
ImportError: No module named 'aiohttp'
```

## Quick Fix (Automated)

**Option 1: Quick Fix (Recommended for most users)**

```bash
# Fast fix without heavy dependencies (recommended first)
python quick_fix_imports.py
```

**Option 2: Full Fix (if you need dependency management)**

```bash
# Complete fix with dependency installation (may take longer)
python fix_imports.py
```

The quick fix script will:
- [OK] Create missing `__init__.py` files
- [OK] Check your Python version
- [OK] Test basic import patterns
- [OK] Complete in under 30 seconds

The full fix script additionally:
- [OK] Install missing dependencies (may timeout on slow connections)
- [OK] Generate detailed diagnostic report
- [OK] Test advanced import patterns

## Manual Fix Steps

If you prefer to fix issues manually:

### Step 1: Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### Step 2: Verify Python Version

Aetherra requires Python 3.8 or higher:

```bash
python --version
```

If you have an older version, please upgrade Python.

### Step 3: Check Project Structure

Ensure these key directories have `__init__.py` files:

```
Aetherra/
├── __init__.py [OK]
├── aetherra_core/
│   ├── __init__.py ❗ (often missing)
│   ├── engine/
│   │   └── __init__.py ❗ (often missing)
│   ├── memory/
│   │   └── __init__.py [OK]
│   ├── plugins/
│   │   └── __init__.py ❗ (often missing)
│   └── orchestration/
│       └── __init__.py ❗ (often missing)
```

### Step 4: Test Imports

Try these test imports to verify everything works:

```python
# Test 1: Basic module import
from Aetherra.aetherra_core import get_system_status

# Test 2: Kernel loop import
from aetherra_kernel_loop import get_kernel

# Test 3: Service registry import
from aetherra_service_registry import get_service_registry

# Test 4: Startup script
import aetherra_startup
```

## Development Setup

For the best development experience:

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate
```

### 2. Install in Development Mode

```bash
# Install package in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### 3. VS Code Setup

Install recommended extensions (see [CONTRIBUTING.md](CONTRIBUTING.md)):

```bash
# Install GitLens for code change tracking
code --install-extension eamodio.gitlens

# Install Python extension
code --install-extension ms-python.python

# Install Pylance for better IntelliSense
code --install-extension ms-python.vscode-pylance
```

## Troubleshooting Specific Errors

### Error: `No module named 'aetherra_core'`

**Solution:** The `aetherra_core` directory is missing its `__init__.py` file.

```bash
# Create the missing file
echo '# Aetherra Core Package' > Aetherra/aetherra_core/__init__.py
```

### Error: `No module named 'engine'`

**Solution:** Create missing `__init__.py` in engine directory:

```bash
# Create the missing file
echo '# Aetherra Engine Package' > Aetherra/aetherra_core/engine/__init__.py
```

### Error: `Import could not be resolved`

**Solution:** This is often a VS Code Python interpreter issue:

1. Open VS Code
2. Press `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (macOS)
3. Type "Python: Select Interpreter"
4. Choose the interpreter from your virtual environment

### Error: Dependency conflicts

**Solution:** Use clean environment:

```bash
# Deactivate current environment
deactivate

# Remove old environment
rm -rf .venv

# Create fresh environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install fresh dependencies
pip install -r requirements.txt
```

## Getting Help

If you're still having issues:

1. **Check the automated fix report**: Look for `import_fix_report.md` in your project root
2. **Search existing issues**: Check [GitHub Issues](https://github.com/AetherraLabs/Aetherra/issues)
3. **Join our Discord**: Get real-time help from the community
4. **Create a new issue**: Include your error message and `import_fix_report.md`

## Contributing Guidelines

Once your imports are working:

1. Read our [CONTRIBUTING.md](CONTRIBUTING.md) guide
2. Install recommended VS Code extensions
3. Set up pre-commit hooks
4. Follow our coding standards

---

**Quick Commands Summary:**

```bash
# Fast fix for most issues (recommended first)
python quick_fix_imports.py

# Full fix with dependency management
python fix_imports.py

# Manual installation if needed
pip install -r requirements.txt

# Development setup
pip install -e ".[dev]"

# Test basic imports
python test_imports.py
```
