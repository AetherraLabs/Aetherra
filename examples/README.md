# Aether Script Examples

This folder contains runnable `.aether` scripts for the v1.1 Language System.

- `daily_anomaly_digest.aether` — Demonstrates meta/policy/require, parallel/await, on_error, transaction, and observability hooks.

To verify scripts locally:

```powershell
python tools/verify_aether_scripts.py --root . --profile test
```

In strict mode (signature checks):

```powershell
$env:AETHERRA_SCRIPT_VERIFY_STRICT = "1"
python tools/verify_aether_scripts.py --root . --strict
```

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
