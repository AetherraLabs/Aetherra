# UI Syntax Refactor Plan (Medium-term)

Goal: Safely repair SyntaxErrors in non-critical UI/demo modules and GUI tests while
keeping core runtime stable.

## Scope (initial targets)

- Aetherra/aetherra_core/agents/enhanced_lyrixa.py
- Aetherra/aetherra_core/memory/lightweight_memory_core.py
- Aetherra/gui/lyrixa_gui.py
- Aetherra/lyrixa/gui/*
- Aetherra/lyrixa/lyrixa_basic_gui.py
- Aetherra/lyrixa/plugins/*_ui.py
- Aetherra/plugins/extra_plugins/*_gui.py
- tests/gui/test_hybrid_gui.py
- tests/ai/test_neural_interface.py
- demos/demo_intelligent_error_handler_8.py

## Strategy

- Syntax-only fixes: close blocks, correct try/except, match parentheses/colons, remove
	stray commas, avoid behavior changes.
- Guard optional UI deps with try/except and no-op stubs to prevent import-time errors.
- Keep modules inert during scans/tests with `if __name__ == "__main__":` or
	feature-flag gates.
- Python 3.11 compatibility: adjust f-strings that use 3.12+ features.

## Batching plan

1. Core UI core files: enhanced_lyrixa.py, lightweight_memory_core.py
2. Top-level GUI frames: lyrixa_gui.py, lyrixa_basic_gui.py
3. lyrixa/gui/*
4. lyrixa/plugins/*_ui.py
5. plugins/extra_plugins/*_gui.py
6. tests/gui + tests/ai/test_neural_interface.py
7. demos/demo_intelligent_error_handler_8.py

## Validation

- After each batch: remove corresponding ruff excludes, run `ruff check`, headless
	smoke, and (optionally) a targeted import test for the edited files.

## Risks & mitigations

- Risk: accidental behavior change → Mitigate by restricting to syntax/guarded imports
	only.
- Risk: hidden runtime deps → Use optional imports and clear TODOs for future
	enablement.

## Tracking

- Keep this doc updated as batches are completed; reference PRs/commits accordingly.
