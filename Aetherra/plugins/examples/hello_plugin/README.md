# Hello Plugin Example

A minimal, safe example plugin showing how to:

- Subclass `PluginInterface`
- Return a structured `PluginResult`
- Register and execute via `PluginChainExecutor`

## Structure

```text
Aetherra/plugins/examples/hello-plugin/
  hello_plugin.py   # Implementation
  README.md         # This file
```

## Quick Test

```bash
python - <<'PY'
import asyncio
from Aetherra.plugins.core.plugin_chain_executor import PluginChainExecutor, ChainStrategy
from Aetherra.plugins.examples.hello-plugin.hello_plugin import HelloPlugin

async def main():
    ex = PluginChainExecutor(db_path=':memory:')
    ex.register_plugin(HelloPlugin('hello', message='Hi Developer'))
    chain = await ex.execute_chain(['hello'], strategy=ChainStrategy.SEQUENTIAL, context={'sample':'value'})
    print(chain.results[0].output)

asyncio.run(main())
PY
```

Expected JSON (shape):

```json
{
  "greeting": "Hi Developer from hello",
  "input": null,
  "context_keys": ["sample"],
  "timestamp": "...Z"
}
```

SPDX-License-Identifier: GPL-3.0-or-later
