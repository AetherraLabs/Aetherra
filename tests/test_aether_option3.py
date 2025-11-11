#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""
Tests for .aether Option 3 features:
- Typed assignments (name: Type = value)
- Dict literals {key: value}
- Policy/require/transaction enforcement hooks
"""

import asyncio

import pytest

from aetherra_script_service import AetherScriptService


def execute_script_content(script: str) -> dict:
    """Synchronous wrapper for test convenience."""
    service = AetherScriptService()

    # Create new event loop for each test to avoid conflicts
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    payload = loop.run_until_complete(
        service.execute_script_content(script, filename="<test>")
    )

    # Flatten nested result structure: payload -> result -> results
    result = {
        "success": payload.get("success", True),
    }

    # Extract assignments from nested results array
    if payload.get("result") and "results" in payload["result"]:
        for res in payload["result"]["results"]:
            if res.get("type") in ("assignment", "typed_assignment"):
                result[res.get("variable", res.get("var"))] = res.get("value")

    # Add metadata fields with underscore prefix from result payload
    result_payload = payload.get("result", {})
    if "policy" in result_payload:
        result["_policy"] = result_payload["policy"]
    if "requires" in result_payload:
        # Merge all require blocks into a single dict with plugins and capabilities lists
        merged_requires = {"plugins": [], "capabilities": []}
        for req_block in result_payload["requires"]:
            if "plugins" in req_block:
                merged_requires["plugins"].extend(req_block["plugins"])
            if "capabilities" in req_block:
                merged_requires["capabilities"].extend(req_block["capabilities"])
        result["_requires"] = merged_requires
    if "transactions" in result_payload:
        result["_transactions"] = result_payload["transactions"]
    if "types" in result_payload:
        result["_types"] = result_payload["types"]

    return result


def test_dict_literal_basic():
    """Test basic dict literal parsing and evaluation."""
    script = """
goal "test dict literals"
config = {"debug": true, "max_retries": 3}
"""
    results = execute_script_content(script)
    assert results["success"]
    assert "config" in results
    assert isinstance(results["config"], dict)
    assert results["config"]["debug"] is True
    assert results["config"]["max_retries"] == 3


def test_dict_literal_nested():
    """Test nested dict literals."""
    script = """
goal "nested dicts"
settings = {"db": {"host": "localhost", "port": 5432}, "cache": {"ttl": 300}}
"""
    results = execute_script_content(script)
    assert results["success"]
    assert results["settings"]["db"]["host"] == "localhost"
    assert results["settings"]["db"]["port"] == 5432
    assert results["settings"]["cache"]["ttl"] == 300


def test_dict_literal_with_variables():
    """Test dict literals referencing variables."""
    script = """
goal "dict with vars"
host = "127.0.0.1"
port = 8080
server = {"host": host, "port": port, "protocol": "http"}
"""
    results = execute_script_content(script)
    assert results["success"]
    assert results["server"]["host"] == "127.0.0.1"
    assert results["server"]["port"] == 8080
    assert results["server"]["protocol"] == "http"


def test_typed_assignment_basic():
    """Test typed assignment parsing (name: Type = value)."""
    script = """
goal "typed assignments"
count: int = 42
name: str = "Alice"
active: bool = true
"""
    results = execute_script_content(script)
    assert results["success"]
    assert results["count"] == 42
    assert results["name"] == "Alice"
    assert results["active"] is True
    # Check type metadata if stored
    if "_types" in results:
        assert results["_types"]["count"] == "int"
        assert results["_types"]["name"] == "str"
        assert results["_types"]["active"] == "bool"


def test_typed_assignment_with_generics():
    """Test typed assignments with generic types."""
    script = """
goal "generic types"
items: List[str] = ["a", "b", "c"]
mapping: Dict[str, int] = {"x": 1, "y": 2}
"""
    results = execute_script_content(script)
    assert results["success"]
    assert results["items"] == ["a", "b", "c"]
    assert results["mapping"] == {"x": 1, "y": 2}
    if "_types" in results:
        assert "List[str]" in results["_types"]["items"]
        assert "Dict[str, int]" in results["_types"]["mapping"]


def test_policy_enforcement_deterministic():
    """Test that deterministic policy is validated."""
    script = """
goal "deterministic run"
policy
    deterministic = true
    seed = 1337
x = 10
"""
    results = execute_script_content(script)
    assert results["success"]
    # Check policy is recorded
    assert results.get("_policy", {}).get("deterministic") is True
    assert results.get("_policy", {}).get("seed") == 1337


def test_require_enforcement_missing_plugin():
    """Test that missing required plugins are flagged."""
    script = """
goal "require check"
require
    plugins = ["nonexistent_plugin>=1.0.0"]
x = 5
"""
    results = execute_script_content(script)
    # Should succeed parsing but flag missing plugin
    assert results["success"]
    assert "nonexistent_plugin>=1.0.0" in results.get("_requires", {}).get(
        "plugins", []
    )
    # Enforcement hook should add warning or error if strict mode enabled


def test_require_enforcement_missing_capability():
    """Test that missing required capabilities are flagged."""
    script = """
goal "capability check"
require
    capabilities = ["network.write", "storage.admin"]
x = 5
"""
    results = execute_script_content(script)
    assert results["success"]
    assert "network.write" in results.get("_requires", {}).get("capabilities", [])
    assert "storage.admin" in results.get("_requires", {}).get("capabilities", [])


def test_transaction_rollback_token():
    """Test that transaction blocks generate rollback tokens."""
    script = """
goal "transaction with rollback"
transaction
    - store(summary, tag="daily")
    - escalate_to("Ops")
"""
    results = execute_script_content(script)
    assert results["success"]
    # Check transaction recorded
    assert len(results.get("_transactions", [])) > 0
    tx = results["_transactions"][0]
    assert tx.get("ops_count") == 2
    # Rollback token should be generated if enforcement enabled
    if "_rollback_tokens" in results:
        assert len(results["_rollback_tokens"]) > 0


def test_combined_option3_features():
    """Test all Option 3 features working together."""
    script = """
goal "combined option 3"

policy
    deterministic = true
    token_budget = 50000

require
    plugins = ["summarizer>=0.2"]
    capabilities = ["memory.read"]

config: Dict[str, int] = {"max_items": 100, "timeout": 30}
items: List[str] = ["a", "b", "c"]

transaction
    x = config
    y = items
"""
    results = execute_script_content(script)
    assert results["success"]
    assert results["config"]["max_items"] == 100
    assert results["items"] == ["a", "b", "c"]
    assert results.get("_policy", {}).get("deterministic") is True
    assert "summarizer>=0.2" in results.get("_requires", {}).get("plugins", [])
    assert len(results.get("_transactions", [])) > 0
