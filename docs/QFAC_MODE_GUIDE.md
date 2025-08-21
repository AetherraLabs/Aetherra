# AETHERRA QFAC Mode Guide

This guide explains how to use the Quantum Fractal Adaptive Compression (QFAC) system in Aetherra, including modes, environment variables, OS wiring, and quick tests.

## Modes

- classical (default): classical compression analytics; no quantum bridge
- hybrid: classical compression + optional quantum bridge encoding/retrieval (auto-fallback if no quantum libs)
- quantum: same code path as hybrid but expects a real quantum backend

Select via environment variable:

- PowerShell: `$env:AETHERRA_QFAC_MODE='hybrid'`
- Bash: `export AETHERRA_QFAC_MODE=hybrid`

## OS Wiring

QFAC can be registered alongside the core memory engine when launching the OS.

- Enable via env: `AETHERRA_QFAC_IN_OS=1`
- Optional alias: `AETHERRA_ENABLE_QFAC=1`

Example (PowerShell):

```powershell
$env:AETHERRA_QFAC_IN_OS='1'
python aetherra_os_launcher.py
```

Services registered:

- memory_system: AetherraMemoryEngine (primary)
- qfac_memory_system: QFACMemorySystem (optional extension)

## CLI Launcher

Use `Aetherra/aetherra_core/memory/qfac_launcher.py`:

- `demo`: run end-to-end demo
- `status`: print system status
- `analyze <file>`: analyze compression potential
- `benchmark`: run synthetic benchmarks

Example (PowerShell):

```powershell
python Aetherra/aetherra_core/memory/qfac_launcher.py demo
python Aetherra/aetherra_core/memory/qfac_launcher.py status
```

## Headless Dashboard

The dashboard is implemented as a Flask blueprint. When unavailable, a stub is used so headless environments still run.

## Tests

Run the unit tests covering mode selection and fallback:

```powershell
pytest -q tests/unit/test_qfac_modes.py
```

Expected:

- Classical mode: roundtrip works; no quantum metadata required
- Hybrid mode: roundtrip works; may include `quantum_encoding` metadata when bridge is initialized; otherwise falls back silently

## Troubleshooting

- If `pytest` is not found, ensure the Python environment is activated and dependencies are installed
- If quantum frameworks (Qiskit/Cirq) are missing, hybrid mode still works using simulation; logs will indicate simulation mode
- Set `AETHERRA_QUIET=1` for reduced logging during CI smoke tests
