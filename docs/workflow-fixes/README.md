# Automated Workflow Failure Fixes

This directory contains tools and scripts to automatically fix common workflow failures in the Aetherra repository, particularly Unicode encoding issues that cause failures on Windows systems.

## Problem Statement

The Aetherra repository was experiencing workflow failures due to `UnicodeEncodeError: 'charmap' codec can't encode character` errors. This happens when:

1. Python files contain Unicode emoji characters (🔍, 🧠, ✅, etc.)
2. The system uses cp1252 encoding (common on Windows)
3. Python tries to print or output these characters to stdout/stderr

## Solution

The automated fix system:

1. **Detects** Unicode characters in Python files that cause encoding issues
2. **Replaces** them with ASCII-safe alternatives (e.g., 🔍 → [SCAN], 🧠 → [BRAIN])
3. **Adds** proper encoding declarations to Python files
4. **Configures** environment variables for Unicode support
5. **Verifies** that fixes work correctly

## Quick Fix Usage

### 1. Simple Quick Fix
```bash
python quick_fix_workflows.py
```
This applies critical fixes to the most important files.

### 2. Comprehensive Fix
```bash
python quick_fix_workflows.py all
```
This fixes all Python files with Unicode issues.

### 3. Test Only
```bash
python quick_fix_workflows.py test
```
This only tests if the current fixes are working.

## Advanced Usage

### Using the Main Fix Tool
```bash
# Fix specific files
python tools/auto_fix_workflow_failures.py --files "aether.py,setup.py"

# Dry run to see what would be changed
python tools/auto_fix_workflow_failures.py --dry-run

# Fix all files
python tools/auto_fix_workflow_failures.py --all

# Just verify existing fixes
python tools/auto_fix_workflow_failures.py --verify
```

### Classify Workflow Failures
```bash
python tools/classify_aether_workflow_failures.py
```
This analyzes and categorizes current workflow failures.

## Automated Workflow

The repository includes a GitHub Actions workflow (`.github/workflows/auto-fix-workflow-failures.yml`) that can:

- Run automatically on a schedule
- Be triggered manually with different scopes
- Apply fixes and commit them automatically
- Generate reports on workflow health

## What Gets Fixed

### Unicode Character Replacements
- 🔍 → [SCAN]
- 🧠 → [BRAIN] 
- ✅ → [OK]
- ❌ → [ERROR]
- ⚠️ → [WARN]
- 💡 → [INFO]
- And many more...

### File Modifications
- Adds `# -*- coding: utf-8 -*-` declarations
- Replaces Unicode characters with ASCII alternatives
- Preserves all functionality while ensuring compatibility

### Environment Setup
- Sets `PYTHONIOENCODING=utf-8`
- Sets `PYTHONUTF8=1`
- Ensures proper Unicode handling

## Files Included

- `tools/auto_fix_workflow_failures.py` - Main comprehensive fix tool
- `quick_fix_workflows.py` - Simple quick fix script
- `test_unicode_workflow_fix.py` - Verification test script
- `.github/workflows/auto-fix-workflow-failures.yml` - GitHub Actions workflow
- `tools/classify_aether_workflow_failures.py` - Workflow failure analyzer

## Testing

After applying fixes, you can verify they work:

```bash
python test_unicode_workflow_fix.py
```

This will test critical files and ensure Unicode errors are resolved.

## Manual Environment Setup

If you need to manually set up your environment for Unicode support:

```bash
# On Windows Command Prompt
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

# On PowerShell
$env:PYTHONIOENCODING="utf-8"
$env:PYTHONUTF8="1"

# On Linux/Mac
export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1
```

## Contributing

When adding new Unicode characters to the codebase:

1. Consider if ASCII alternatives would work just as well
2. If Unicode is necessary, add mappings to `UNICODE_REPLACEMENTS` in the fix tool
3. Test on systems with limited encoding support
4. Update this documentation if needed

## Troubleshooting

### Still Getting Unicode Errors?

1. Run the classifier to see current issues:
   ```bash
   python tools/classify_aether_workflow_failures.py
   ```

2. Apply comprehensive fixes:
   ```bash
   python quick_fix_workflows.py all
   ```

3. Check environment variables are set:
   ```bash
   echo $PYTHONIOENCODING
   echo $PYTHONUTF8
   ```

### New Unicode Characters Found?

Add them to the `UNICODE_REPLACEMENTS` mapping in `tools/auto_fix_workflow_failures.py` and run the fix again.

---

This system ensures that Aetherra workflows can run reliably across all platforms and encoding configurations.