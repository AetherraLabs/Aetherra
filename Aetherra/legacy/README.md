# Aetherra Legacy Engines and Startup

This folder contains deprecated or OS-unused modules retained temporarily for reference or Lyrixa-only experimentation. They are not part of the Aetherra OS runtime path.

Items here may be removed in a future cleanup once Lyrixa migration (if any) is finalized.

Current contents intent:

- aetherra_startup.py — Old monolithic bootstrap with GUI hooks. Replaced by `aetherra_os_launcher.py` (GUI) or `aetherra_os.py` (headless).
- lyrixa_engine.py — Lyrixa-specific engine variant, not used by Aetherra OS.
- lyrixa_engine_mock.py — Mock/testing variant, not used by Aetherra OS.
