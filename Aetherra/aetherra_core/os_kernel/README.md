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
- `from Aetherra.aetherra_core.os_kernel import assess_kernel_readiness`

Readiness contract:

- `assess_kernel_readiness(status)` converts a Kernel status dictionary into a
  read-only operator contract: `ready`, `degraded`, `blocked`, or `offline`.
- `build_kernel_readiness_payload(status)` wraps the readiness result for Hub
  API responses without mutating Kernel state.

Later, the implementations can be moved here and the forwarders removed.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

