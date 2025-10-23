# Installation & Quickstart

## 1. Fast Install (Pip)

```powershell
# From a clean directory (Windows PowerShell)
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install aetherra  # (Placeholder: once published to PyPI)
```

Until PyPI publish, clone repo:

```powershell
git clone https://github.com/AetherraLabs/Aetherra.git
cd "Aetherra"
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt  # or: pip install -e .
```

## 2. One-Liner Quick Hub (Dev Mode)

```powershell
$env:AETHERRA_AI_API_ENABLED='1'; $env:AETHERRA_AI_API_STREAM='1'; python -m aetherra_hub.compat
```

In another shell:

```powershell
Invoke-RestMethod -Method Post -Uri 'http://localhost:3001/api/lyrixa/chat' -ContentType 'application/json' -Body '{"message":"hello"}'
```

## 3. Docker Quickstart

```powershell
docker build -t aetherra-dev .
docker run -p 3001:3001 -e AETHERRA_AI_API_ENABLED=1 -e AETHERRA_AI_API_STREAM=1 aetherra-dev python -m aetherra_hub.compat
```

## 4. Sample Workflows (.aether)

| File                                      | Purpose                                  |
| ----------------------------------------- | ---------------------------------------- |
| `workflows/parallel_workflow_demo.aether` | Demonstrates parallel execution chain.   |
| `workflows/on_error_chain_demo.aether`    | Error handling / fallback demonstration. |
| `workflows/plugin_chain_demo.aether`      | Plugin chain execution showcase.         |
| `ai_os_test.aether`                       | End‑to‑end OS capability script.         |

Run a workflow:

```powershell
python aether.py workflows/parallel_workflow_demo.aether
```

## 5. Environment Flags (Common)

| Flag                         | Effect                                   | Default |
| ---------------------------- | ---------------------------------------- | ------- |
| `AETHERRA_AI_API_ENABLED`    | Enables chat endpoints                   | 0       |
| `AETHERRA_AI_API_STREAM`     | Enables streaming endpoint               | 0       |
| `AETHERRA_TRAINER_ENABLED`   | Enables trainer job/eval routes          | 0       |
| `AETHERRA_QUIET`             | Suppress verbose logs                    | 0       |
| `AETHERRA_MEMORY_STORM`      | Enable STORM memory features             | 0       |
| `AETHERRA_STORM_SHADOW_MODE` | STORM runs in shadow mode (metrics only) | 1       |

## 6. Tests & Health

Capability tests:

```powershell
pytest -q -o addopts= tests/capabilities
```

Diagnostics (non-fatal warnings tolerated in some external modes):

```powershell
python tools/lyrixa_diagnostics.py
```

## 7. Uninstall

```powershell
deactivate  # if venv
Remove-Item -Recurse -Force .venv
```

## 8. Next Steps

- Explore metrics at `http://localhost:3001/metrics`
- Inspect `BETA_READINESS_REPORT.md`
- Sign workflows: `python tools/sign_aether.py workflows/parallel_workflow_demo.aether`

## 9. Run OS with STORM (Shadow Mode)

Recommended safe production validation path: STORM collects metrics while returning baseline results.

```powershell
# 1) Start the Hub (recommended)
python tools/run_hub_ai_api.py --port 3001

# 2) In another shell, enable STORM shadow mode and start the OS
$env:AETHERRA_MEMORY_STORM='1'; $env:AETHERRA_STORM_SHADOW_MODE='1'; python aetherra_os_launcher.py --mode full -v
```

On boot you should see a STORM status line in logs similar to:

```text
[STORM:POST-BOOT] enabled=1 shadow_mode=1 backend=ot:earthmover tt_rank_cap=128
```
