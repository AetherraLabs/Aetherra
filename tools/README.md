# aetherra Project Tools

This directory contains utility tools for the aetherra project.

## UI Standards Verification Tool

`verify_ui_standards.py` - A tool to verify that the codebase complies with the established UI standards.

### Features

- Checks for emoji usage in code
- Identifies unsupported Qt CSS styling
- Detects chat bubble styling patterns
- Finds inconsistent spacing in UI styling
- Generates a detailed report of any issues found

### Usage

```bash
# Basic usage (scan current directory)
python tools/verify_ui_standards.py

# Scan a specific directory
python tools/verify_ui_standards.py --dir src/aetherra/ui

# Exclude specific directories
python tools/verify_ui_standards.py --exclude archive backups

# Generate a report file
python tools/verify_ui_standards.py --output ui_standards_report.md
```

### Exit Codes

- `0`: Success - No UI standards violations found
- `1`: Warning - UI standards violations found

## Running the Verification

It's recommended to run this verification tool:

1. After making UI changes
2. Before committing code
3. As part of continuous integration pipelines

This helps maintain the professional, consistent UI standards established for the project.
