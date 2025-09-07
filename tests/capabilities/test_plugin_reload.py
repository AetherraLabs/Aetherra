import uuid

import pytest

from Aetherra.plugins.core.plugin_chain_executor import (
    ChainStrategy,
    ExecutionStatus,
    PluginChainExecutor,
    PluginInterface,
    PluginResult,
)


class TempReloadPlugin(PluginInterface):
    """Temporary plugin used to validate unregister + re-register lifecycle.

    Each instance gets a unique UUID so we can assert a new instance is active
    after re-registration (ensuring old instance state is removed).
    """

    def __init__(self):
        super().__init__(plugin_id="temp_reload_plugin")
        self.instance_id = uuid.uuid4().hex
        self.calls = 0

    async def execute(self, input_data, context):  # type: ignore[override]
        self.calls += 1
        return PluginResult(
            plugin_id=self.plugin_id,
            success=True,
            output={
                "instance_id": self.instance_id,
                "calls": self.calls,
                "input": input_data,
            },
            execution_time=0.0,
            metadata={"lifecycle_test": True},
        )


@pytest.mark.asyncio
async def test_plugin_unregister_and_reregister(tmp_path):
    """Verify plugin can be unregistered and re-registered cleanly.

    Assertions:
    - Initial registration adds plugin to registry.
    - Chain execution succeeds and returns instance UUID.
    - Unregistration removes plugin.
    - Re-registration with same plugin_id uses a new instance (different UUID).
    - Second execution uses new instance (call count isolated to that instance).
    - Registry only contains a single entry for the plugin_id after reload.
    """

    # Use a file-backed temp DB so schema persists across separate connections
    db_file = tmp_path / "plugin_chain_test.db"
    executor = PluginChainExecutor(db_path=str(db_file))

    # Register first instance
    plugin1 = TempReloadPlugin()
    executor.register_plugin(plugin1)
    assert plugin1.plugin_id in executor.registered_plugins

    # Execute chain with single plugin (sequential strategy)
    exec1 = await executor.execute_chain(
        plugins=[plugin1.plugin_id],
        strategy=ChainStrategy.SEQUENTIAL,
        context={"initial_input": "ping"},
    )
    assert exec1.status == ExecutionStatus.COMPLETED
    assert exec1.results and len(exec1.results) == 1
    r1 = exec1.results[0]
    assert r1.success is True
    first_instance_id = r1.output["instance_id"]
    assert plugin1.calls == 1

    # Unregister first instance
    executor.unregister_plugin(plugin1.plugin_id)
    assert plugin1.plugin_id not in executor.registered_plugins

    # Register new instance with same id
    plugin2 = TempReloadPlugin()
    executor.register_plugin(plugin2)
    assert plugin2.plugin_id in executor.registered_plugins
    assert plugin2.instance_id != first_instance_id  # different instance

    # Execute again after reload
    exec2 = await executor.execute_chain(
        plugins=[plugin2.plugin_id],
        strategy=ChainStrategy.SEQUENTIAL,
        context={"initial_input": "pong"},
    )
    assert exec2.status == ExecutionStatus.COMPLETED
    assert exec2.results and len(exec2.results) == 1
    r2 = exec2.results[0]
    assert r2.success is True
    second_instance_id = r2.output["instance_id"]
    assert second_instance_id != first_instance_id
    assert plugin2.calls == 1  # isolated state

    # Ensure registry has exactly one entry for this plugin id
    assert list(executor.registered_plugins.keys()) == [plugin2.plugin_id]
