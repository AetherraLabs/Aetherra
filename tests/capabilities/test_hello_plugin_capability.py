# Third party imports
import pytest

# Aetherra imports
from Aetherra.plugins.core.plugin_chain_executor import (
    ChainStrategy,
    ExecutionStatus,
    PluginChainExecutor,
)
from Aetherra.plugins.examples.hello_plugin.hello_plugin import HelloPlugin


@pytest.mark.asyncio
async def test_hello_plugin_basic_execution(tmp_path):
    """Capability: hello plugin executes & returns expected greeting structure.

    Asserts:
    - Chain completes successfully.
    - Result payload contains greeting, timestamp, context keys list.
    - Capabilities list present on plugin instance.
    """
    db_file = tmp_path / "hello_plugin_chain.db"
    ex = PluginChainExecutor(db_path=str(db_file))
    plugin = HelloPlugin("hello", message="Hi Capability Test")
    ex.register_plugin(plugin)

    chain = await ex.execute_chain(
        plugins=["hello"],
        strategy=ChainStrategy.SEQUENTIAL,
        context={"trace_id": "abc123"},
    )
    assert chain.status == ExecutionStatus.COMPLETED
    assert chain.results and len(chain.results) == 1
    result = chain.results[0]
    assert result.success is True
    out = result.output
    assert out["greeting"].startswith("Hi Capability Test")
    assert "timestamp" in out
    assert out["context_keys"] == ["trace_id"]
    assert "greeting" in plugin.capabilities
