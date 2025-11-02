# Quick Start: Registry Daemon + Hub + OS (Windows)

This guide brings up the Aetherra Registry Daemon, the Hub API, and the OS so the
Hub reads live kernel status from the registry daemon (not file fallback).

## Prerequisites

- Python environment set up (repo's .venv recommended)
- .env includes:
  - `AETHERRA_REGISTRY_URL=http://127.0.0.1:3030`
  - your LLM keys (e.g., `OPENAI_API_KEY=...`)

## Start the stack (via VS Code Tasks)

Run these in order (Terminal → Run Task):

1. Run Registry Daemon (3030)

   - Task: "Run Registry Daemon (3030)"
   - Expected: daemon listens at <http://127.0.0.1:3030>

1. Run Hub (AI API 3001 via Registry)

   - Task: "Run Hub (AI API 3001 via Registry)"
   - Expected: Hub API on <http://127.0.0.1:3001>

1. Run OS (with Registry Daemon)

   - Task: "Run OS (with Registry Daemon)"
   - Expected: OS comes online and registers/heartbeats to the registry daemon

## Verify it's wired correctly

- Registry status

  - Open: <http://127.0.0.1:3030/api/registry/status>
  - You should see `total_services > 0` and keys like `kernel_loop`, `memory_system`.

- Hub kernel status

  - Open: <http://127.0.0.1:3001/api/kernel/status>
  - You should see:
    - `_source: "registry_daemon"`
    - `running: true`

## Optional: Run directly in PowerShell

These are equivalent to the tasks (use your Python exe if needed):

```powershell
# Registry Daemon
python aetherra_registry_daemon.py --host 127.0.0.1 --port 3030

# Hub (listens on 3001)
python tools/run_hub_ai_api.py --port 3001

# OS (verbose)
$env:AETHERRA_REGISTRY_URL = "http://127.0.0.1:3030"; python -u aetherra_os_launcher.py --mode full -v
```

## Troubleshooting

- Hub shows `_source: "file_fallback"`:
  - Ensure the OS is running and your `.env` or task environment includes `AETHERRA_REGISTRY_URL`.
  - Verify Registry Daemon is reachable: <http://127.0.0.1:3030/api/registry/status>

- Windows quoting issues in PS inline commands:
  - Prefer running the VS Code Tasks or use the dedicated `.env` file for config.

- Requests missing when OS tries to register:
  - Install `requests` in your environment.

## Notes

- The OS will continue heartbeating registered services; the daemon marks services
  as degraded if heartbeats go stale.
- Hub prefers daemon status automatically when `AETHERRA_REGISTRY_URL` is set and reachable.
