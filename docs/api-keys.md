# API Keys and Secrets

This guide explains how Aetherra manages API keys locally and how to configure them safely.

- Storage: `%USERPROFILE%/.aetherra/keys.json` on Windows (or `~/.aetherra/keys.json` cross-platform).
- Env override: any key named `foo` can be provided via `AETHERRA_FOO` environment variable.
- Programmatic access: `from Aetherra.security.api_keys import get_key, set_key, delete_key`.
- Git hygiene: never commit keys; `.aetherra/` is outside the repo.

## Examples

```python
from Aetherra.security.api_keys import get_key, set_key

# set a key once
set_key("openai", "sk-...redacted...")

# use it
api_key = get_key("openai")
```

## CLI suggestion

Consider setting environment variables in your shell profile:

- PowerShell:

```powershell
[System.Environment]::SetEnvironmentVariable("AETHERRA_OPENAI", "sk-...", "User")
[#] Enable plugin manifest signing in discovery
[System.Environment]::SetEnvironmentVariable("AETHERRA_SIGN_PLUGINS", "1", "User")
[#] Enforce signature verification on the Hub
[System.Environment]::SetEnvironmentVariable("AETHERRA_SIGNING_STRICT", "1", "User")
[#] Seed federation peers (comma-separated URLs)
[System.Environment]::SetEnvironmentVariable("AETHERRA_PEERS", "http://host1:3001,http://host2:3001", "User")
```

- Bash (Linux/macOS):

```bash
echo 'export AETHERRA_OPENAI=sk-...' >> ~/.bashrc
echo 'export AETHERRA_SIGN_PLUGINS=1' >> ~/.bashrc
echo 'export AETHERRA_SIGNING_STRICT=1' >> ~/.bashrc
echo 'export AETHERRA_PEERS=http://host1:3001,http://host2:3001' >> ~/.bashrc
```

## Related features

- Discovery can sign plugin manifests when `AETHERRA_SIGN_PLUGINS=1` and a secret is set via `set_key("plugin_signing_secret", ...)`.
- Hub enforces signature verification when `AETHERRA_SIGNING_STRICT=1`.
- Federation peers can be pre-seeded via `AETHERRA_PEERS` at Hub startup.

## Rotation and environments

- Keep separate secrets per environment (dev/staging/prod). Example keys:
	- `plugin_signing_secret.dev`, `plugin_signing_secret.staging`, `plugin_signing_secret.prod`
- Rotate production signing keys quarterly or on suspicion of leak:
	1) Generate new secret and store as `plugin_signing_secret.next`
	2) Enable dual-signing period (discovery signs with both; hub accepts both)
	3) Flip `plugin_signing_secret` to new value; keep `.next` for one week
	4) Remove old key and `.next`
- Never store production secrets in code or CI logs; use environment or a secrets store.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
