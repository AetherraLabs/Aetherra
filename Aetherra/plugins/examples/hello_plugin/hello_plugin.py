# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""A minimal example plugin demonstrating the PluginInterface contract.

Usage (interactive test):

```python
from Aetherra.plugins.core.plugin_chain_executor import PluginChainExecutor, ChainStrategy
from Aetherra.plugins.examples.hello-plugin.hello_plugin import HelloPlugin  # adjust import if necessary
import asyncio

async def demo():
    exec = PluginChainExecutor(db_path=':memory:')
    exec.register_plugin(HelloPlugin('hello', message='Hi'))
    result_chain = await exec.execute_chain(['hello'], strategy=ChainStrategy.SEQUENTIAL, context={'user':'dev'})
    print(result_chain.results[0].output)

asyncio.run(demo())
```
"""

from __future__ import annotations

# Standard library imports
import asyncio
from datetime import datetime
from typing import Any, Dict

# Aetherra imports
from Aetherra.plugins.core.plugin_chain_executor import PluginInterface, PluginResult


class HelloPlugin(PluginInterface):
    """Returns a friendly greeting plus any input data echo.

    Safe: no external side effects, no network/filesystem writes.
    """

    def __init__(self, plugin_id: str, message: str = "Hello"):
        super().__init__(plugin_id)
        self.message = message
        self.capabilities = ["greeting"]

    async def execute(self, input_data: Any, context: Dict[str, Any]) -> PluginResult:  # type: ignore[override]
        await asyncio.sleep(0)  # yield control; baseline async hook
        output = {
            "greeting": f"{self.message} from {self.plugin_id}",
            "input": input_data,
            "context_keys": sorted(list(context.keys())),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        return PluginResult(
            plugin_id=self.plugin_id,
            success=True,
            output=output,
            execution_time=0.0,
            metadata={"kind": "hello_plugin"},
        )
