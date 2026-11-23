# Windows Internal Alpha Installation

This profile installs the source-checkout runtime, persistent personal memory,
configured chat providers and React Runtime Observatory on Windows x64 with
Python 3.13 and Node 22.18.0. Use PowerShell 7.5 or newer. The recorded local
verification uses Python 3.13.7. Consult [the alpha decision](ALPHA_READINESS_DECISION.md)
for the accepted operating boundary and verification status.

## Fresh Installation

Start in a new checkout. Keep existing profiles and environments separate.
PR #327 is merged. The command below selects the verified `v0.5.0-beta.6`
released-main revision. For a later release, use the revision and operating
boundary recorded in the alpha decision.

```powershell
git clone https://github.com/AetherraLabs/Aetherra.git Aetherra-alpha
Set-Location Aetherra-alpha
git checkout --detach f55d48a94559364d393fbf10a1e84e397a5109aa
py -3.13 -m venv .venv
$alphaPython = (Resolve-Path .venv/Scripts/python.exe).Path
& $alphaPython -m pip install pip==26.3
& $alphaPython -m pip install -r requirements.lock
& $alphaPython -m pip check
& $alphaPython tools/enforce_lock_sync.py --lock requirements.lock
```

Each command must exit zero. `pip check` must report no broken requirements;
the lock check must report an exact match. The environment must have
`include-system-site-packages = false` in `.venv/pyvenv.cfg`.
Installing into an old shared environment does not establish this result.

Provision the pinned retrieval model while network access is available:

```powershell
$env:HF_HOME = Join-Path (Get-Location) '.aetherra/model-cache'
@'
from sentence_transformers import SentenceTransformer
from Aetherra.aetherra_core.memory.chat_retrieval import MODEL, REVISION
SentenceTransformer(MODEL, revision=REVISION, device="cpu", trust_remote_code=False)
'@ | & $alphaPython -
```

Retain that cache path in the runtime shell. The model is pinned by revision;
remote model code is disabled. This download is separate from text generation.

Install and check the Runtime Observatory:

```powershell
Push-Location Aetherra/lyrixa/gui
npm.cmd ci --ignore-scripts --no-audit
npm.cmd audit --audit-level=low
npm.cmd test
npm.cmd run build
npm.cmd run lint
Pop-Location
```

Use [the operator runbook](ALPHA_OPERATOR_RUNBOOK.md) to start the full launcher
in a new synthetic local profile, apply the scoped Guardian/network policies,
start the Observatory and verify stop/restart. Keep Guardian, capabilities and
signing enforced. The normal entry point remains:

```powershell
& $alphaPython aetherra_os_launcher.py --mode full --no-gui --config "$alphaProfile/launcher.json"
```

An unavailable model is a fallback check. A live-model pass requires the
configured provider, retrieved record IDs and generation evidence IDs, with
`fallback=false`. Local profile directories provide storage isolation.

## Dependency Scope

`requirements.lock` is the Windows/Python 3.13 source-runtime and quality-tool
graph. Its inputs are `requirements.txt` and `requirements/quality.txt`, with
compatible versions constrained by the separately maintained CI lock.
`requirements-ci.lock` continues to describe Ubuntu/Python 3.11 CI.

The old desktop freeze included 261 packages and could not resolve:
`virtualenv==20.31.2` required `filelock<4`, while the lock required
`filelock==4.2.1`. Its audit reported findings in 36 packages. Pyxnat also
introduced the obsolete `pathlib` distribution; Streamlit constrained Pillow
below the current repaired versions. These packages are outside the current
source-runtime requirements. Their previous versions remain inspectable in
Git history at `b827eccea181f672347ecf277bae99a97521c459`.

Some excluded packages serve optional features whose source is preserved:

| Feature path | Scope |
| --- | --- |
| Qt plugin interfaces | PySide6/PyQt integrations are separate from the React Runtime Observatory. |
| Ollama and llama.cpp SDK integrations | Optional SDK paths require their own dependency installation and verification. |
| Quantum/Qiskit components | Optional source-runtime paths; the package metadata still declares a different Qiskit-containing graph. |
| Research, chart and document plugins | BeautifulSoup, Seaborn, Markdown and export libraries are optional feature dependencies. |
| Enhanced formal grammar | The standalone Lark grammar modules require Lark; the normal launcher uses the existing handwritten parser. |

This profile does not establish a wheel-only installation, all optional plugin
features, other operating systems or unattended operation. Installing package
extras or additional plugins changes the dependency graph and requires a fresh
consistency and vulnerability check. No source feature or signing control is
removed to obtain the profile's audit result.

## Regenerate And Verify The Lock

Run this on Windows x64/Python 3.13 from the repository root:

```powershell
& $alphaPython tools/dependency_lock.py -r requirements.txt -r requirements/quality.txt -c requirements-ci.lock --output requirements.lock
```

This explicit-input mode asks pip to resolve the complete graph while ignoring
installed packages. It does not modify the running environment or include
unrelated installed packages. A failed resolution leaves the previous lock
unchanged. The legacy no-input freeze mode remains available for existing
callers; use explicit inputs for this desktop profile.

Install the generated lock into another new environment, then run `pip check`
and `tools/enforce_lock_sync.py`. Keep the audit tool in a separate environment:

```powershell
py -3.13 -m venv .audit-env
& .audit-env/Scripts/python.exe -m pip install pip-audit==2.10.1
& .audit-env/Scripts/python.exe -m pip_audit --path .venv/Lib/site-packages --strict --format json --output desktop-audit.json --progress-spinner off
```

Every installed distribution, including pip, must be audited successfully with
zero reported findings. Audit results are dated advisory evidence. The
`Desktop Installation` workflow repeats fresh installation, dependency checks,
the audit, offline process-restart continuity and signing regressions, boot
contracts and the Observatory build. Production release signing remains in
the existing required signing workflows.
