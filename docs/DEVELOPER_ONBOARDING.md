# Developer Onboarding

This guide helps you: (1) create a plugin, (2) write & sign a `.aether` workflow, (3) run verification.

## 1. Environment

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Create a Plugin

```powershell
python tools/create_plugin.py my_transform --category examples
```
Outputs (under `Aetherra/plugins/examples/my_transform/`):

- `my_transform.py` (scaffold)
- `README.md`
- `aetherra-plugin.json`

Edit the class, implement logic inside `execute`, document safety.

## 3. Quick Plugin Test

```powershell
python - <<'PY'
import asyncio
from Aetherra.plugins.core.plugin_chain_executor import PluginChainExecutor, ChainStrategy
from Aetherra.plugins.examples.my_transform.my_transform import MyTransformPlugin
async def main():
    ex = PluginChainExecutor(db_path=':memory:')
    ex.register_plugin(MyTransformPlugin('my_transform'))
    chain = await ex.execute_chain(['my_transform'], strategy=ChainStrategy.SEQUENTIAL, context={'demo':True})
    print(chain.results[0].output)
asyncio.run(main())
PY
```

## 4. Write a .aether Workflow

Create `workflows/my_transform_demo.aether`:

```aether
meta:
  name: my_transform_demo
policy:
  on_error: continue
step1: run_plugin("my_transform", input="sample text")
store(step1, tag="my_transform_result")
```

Sign it:

```powershell
python tools/sign_aether.py workflows/my_transform_demo.aether
```

Run it:

```powershell
python aether.py workflows/my_transform_demo.aether
```

## 5. Verify All Workflows

```powershell
python tools/verify_aether_scripts.py --root . --strict --fail-on-any-risk --profile test
```

## 6. Commit Hygiene

Pre-commit hook auto-signs staged `.aether` files. Dry-run check:

```powershell
python tools/precommit_sign_aether.py --dry-run workflows/my_transform_demo.aether
```

## 7. Troubleshooting

| Issue             | Cause            | Fix                                      |
| ----------------- | ---------------- | ---------------------------------------- |
| Missing signature | Forgot sign step | Run sign script / re-stage               |
| Plugin not found  | Not registered   | Register plugin before execute_chain     |
| Risk score > 0    | Static flags     | Inspect report `aether_static_report.md` |

Happy hacking.
