# Aetherra Core OS Kernel (shim)

This package exposes the Aetherra OS kernel loop and HMR controller under the
`Aetherra.aetherra_core.os_kernel` namespace while the implementation lives in
root-level modules (`aetherra_kernel_loop.py`, `aetherra_hmr_controller.py`).

Purpose:

- Provide a stable, modular import path immediately.
- Allow incremental migration of implementations into this folder without
  breaking existing code.

Public imports:

- `from Aetherra.aetherra_core.os_kernel import AetherraKernelLoop, get_kernel`
- `from Aetherra.aetherra_core.os_kernel import HMRController, get_hmr_controller`

Later, the implementations can be moved here and the forwarders removed.
