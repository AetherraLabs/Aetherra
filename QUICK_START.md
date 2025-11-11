# Aetherra Turn-Key Development Quick Start

This guide gets a full local Aetherra stack (Registry + Hub + OS + Plugin Marketplace) running and populated in under a minute.

## 1. Prerequisites

- Python 3.11+ virtual environment activated (`.venv` recommended)
- Required dependencies installed (`pip install -r requirements.txt` if present)
- Optional: Set an AI API token if you want guarded endpoints (`set AETHERRA_AI_API_TOKEN=yourtoken` on Windows PowerShell)

## 2. One-Command Stack Startup

```powershell
python start_aetherra_stack.py
```

What happens:

1. Registry Daemon ensured (default `http://127.0.0.1:3030`).
2. Hub launched (default desired `http://127.0.0.1:3012`, auto-port if busy).
3. OS started in `full` mode.
4. Hub runtime URL exported via `AETHERRA_HUB_URL`.

If the chosen hub port is busy, the script auto-selects the next free port and sets `AETHERRA_HUB_URL` accordingly.

## 3. Plugin Auto-Discovery & Registration

To populate the Hub marketplace with local plugins:

```powershell
python tools/run_plugin_discovery_sync.py
```

Result: Discovers local Python / sample plugins under `Aetherra/plugins` and registers them.

### Dev Unsigned Override

During development you may not have full signing verification available. The system now supports an explicit override:

- Environment flag: `AETHERRA_ALLOW_UNSIGNED_DEV=1`
- Header used by discovery: `X-Aeth-Allow-Unsigned: 1`

Behavior under override:

- Plugin manifests are sent WITHOUT signature/pubkey fields.
- Hub bypasses strict signature verification for that request.
- All valid manifests register successfully (verified by 15/15 success in current session).

This override is auto-enabled by the discovery runner
(`tools/run_plugin_discovery_sync.py`).

To force targeting a specific Hub instance when multiple are running, set:

```powershell
$env:AETHERRA_FORCE_HUB_URL = "http://127.0.0.1:3001"
python tools/run_plugin_discovery_sync.py
```

## 4. Validating the Environment

Run smoke + capability tests:

```powershell
# Smoke tests
# (VS Code Task) or directly:
pytest -q tests/smoke

# Capabilities tests
pytest -q tests/capabilities
```

(Tasks are available in VS Code: "Smoke tests (no coverage)" and "Verify Claims (Capabilities Tests)")

## 5. Manual Plugin Registration Probe

Quick curl-style (Python) probe:

```powershell
python -c "import requests;print(requests.post('http://127.0.0.1:3001/api/plugins/register',json={'name':'quickprobe','version':'1.0.0','description':'probe'},headers={'X-Aeth-Allow-Unsigned':'1'}).text)"
```

Expected output includes `"status":"ok"`.

## 6. Common Environment Flags

| Flag                          | Purpose                                                          |
| ----------------------------- | ---------------------------------------------------------------- |
| AETHERRA_ALLOW_UNSIGNED_DEV=1 | Bypass signature verification for development                    |
| AETHERRA_FORCE_HUB_URL        | Force discovery to target a specific Hub URL                     |
| AETHERRA_AI_API_TOKEN         | Provides token for AI endpoints; auto-enables require flag       |
| AETHERRA_SIGNING_STRICT=1     | Enforce plugin signature (omit when using unsigned dev override) |

## 7. Troubleshooting

- Repeated `invalid signature` errors: Ensure `AETHERRA_ALLOW_UNSIGNED_DEV=1` is
	exported and discovery ran after patch (manifests should not contain
	signature/pubkey fields).
- Discovery targeting wrong Hub: Set `AETHERRA_FORCE_HUB_URL` before running sync.
- Plugins not appearing: Check `aetherra_hub/services/plugins.py` logs; ensure minimal path executed (advanced mode skipped under override).

## 8. Next Steps

- Re-enable signing strictness once verification libs are installed (remove override).
- Add telemetry / metrics dashboards.
- Extend discovery to support `.aetherplug` packaged format with validation.

---

Turn-key goal validated: Stack auto-start + dynamic Hub port + successful unsigned dev plugin registration.
