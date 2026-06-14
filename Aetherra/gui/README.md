# Aetherra OS Monitor GUI

This directory now contains a single, minimal, supported OS GUI:

- Entry point: `Aetherra/gui/aetherra_os_gui.py` (PySide6)
- Compatibility launchers that delegate here: `launch_enhanced_neural_os.py`, `run_aetherra_os.py`
- Canonical Aetherra user interface is being consolidated under `frontend/` and the top-level `aetherra_os.py` launcher.

Quick run (PowerShell):

```powershell
python "Aetherra/gui/aetherra_os_gui.py"
```

Or use the compatibility launcher:

```powershell
python "Aetherra/gui/launch_enhanced_neural_os.py"
```

Requirements: PySide6 and requests.

Notes:

- This native GUI is transitional support while the unified Aetherra interface moves to the canonical frontend.
- Lyrixa-branded UI surfaces are being internalized and retired from the public launch path.
<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

