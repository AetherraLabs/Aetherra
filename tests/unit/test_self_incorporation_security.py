"""
Unit tests for Self-Incorporation Security Layer (Phase 2B).

Tests:
- Signature verification (strict vs permissive modes)
- Capability grant validation
- Network policy compliance
- Policy drift detection
- Proposal authentication and authorization
- Rate limiting for proposals
"""

# Standard library imports
import asyncio
import os
import tempfile
import time
from pathlib import Path

# Third party imports
import pytest

# Aetherra imports
from Aetherra.homeostasis.self_incorporation_security import (
    ProposalAuthResult,
    SecurityValidationResult,
    SelfIncorporationSecurity,
)


@pytest.fixture
def security_layer():
    """Create security layer in standard mode."""
    return SelfIncorporationSecurity(trust_mode="standard")


@pytest.fixture
def strict_security_layer():
    """Create security layer in strict mode."""
    # Set environment to force strict mode
    os.environ["AETHERRA_PROFILE"] = "prod"
    layer = SelfIncorporationSecurity(trust_mode="strict")
    yield layer
    # Cleanup
    os.environ.pop("AETHERRA_PROFILE", None)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_signature_verification_no_signature_permissive(security_layer, tmp_path):
    """Test: File without signature passes in permissive mode."""
    test_file = tmp_path / "test.py"
    test_file.write_text("print('hello')", encoding="utf-8")

    result = await security_layer.verify_signature(test_file)

    assert result is True, "File without signature should pass in permissive mode"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_signature_verification_no_signature_strict(
    strict_security_layer, tmp_path
):
    """Test: File without signature fails in strict mode."""
    test_file = tmp_path / "test.py"
    test_file.write_text("print('hello')", encoding="utf-8")

    result = await strict_security_layer.verify_signature(test_file)

    assert result is False, "File without signature should fail in strict mode"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_signature_verification_valid_signature(security_layer, tmp_path):
    """Test: File with valid signature passes."""
    import hashlib

    test_file = tmp_path / "test.py"
    content = "print('hello')"
    test_file.write_text(content, encoding="utf-8")

    # Create valid signature
    file_hash = hashlib.sha256(content.encode()).hexdigest()
    sig_file = test_file.with_suffix(test_file.suffix + ".sig")
    sig_file.write_text(f"sha256:{file_hash}", encoding="utf-8")

    result = await security_layer.verify_signature(test_file)

    assert result is True, "File with valid signature should pass"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_signature_verification_invalid_signature(security_layer, tmp_path):
    """Test: File with invalid signature fails."""
    test_file = tmp_path / "test.py"
    test_file.write_text("print('hello')", encoding="utf-8")

    # Create invalid signature
    sig_file = test_file.with_suffix(test_file.suffix + ".sig")
    sig_file.write_text("sha256:invalid_hash_here", encoding="utf-8")

    result = await security_layer.verify_signature(test_file)

    assert result is False, "File with invalid signature should fail"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_capabilities_check_no_requirements(security_layer):
    """Test: Empty capability list always passes."""
    result = await security_layer.check_capabilities("test_component", [])

    assert result is True, "Empty capability list should always pass"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_capabilities_check_missing_capability(security_layer):
    """Test: Missing capability fails check."""
    result = await security_layer.check_capabilities(
        "test_component", ["network:outbound", "filesystem:write"]
    )

    # Without grants, capabilities will fail
    assert result is False, "Missing capabilities should fail"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_network_policy_no_network_imports(security_layer, tmp_path):
    """Test: File without network imports passes policy check."""
    test_file = tmp_path / "test.py"
    test_file.write_text("print('hello')\nimport os\nimport sys", encoding="utf-8")

    result = await security_layer.check_network_policy(test_file)

    assert result is True, "File without network imports should pass"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_network_policy_with_network_imports_permissive(security_layer, tmp_path):
    """Test: Network imports allowed in permissive mode."""
    test_file = tmp_path / "test.py"
    test_file.write_text("import socket\nimport urllib.request", encoding="utf-8")

    result = await security_layer.check_network_policy(test_file)

    assert result is True, "Network imports allowed in permissive mode"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_network_policy_with_network_imports_strict(
    strict_security_layer, tmp_path
):
    """Test: Network imports blocked in strict mode without capability."""
    test_file = tmp_path / "test.py"
    test_file.write_text("import socket\nimport urllib.request", encoding="utf-8")

    result = await strict_security_layer.check_network_policy(test_file)

    assert result is False, "Network imports should be blocked in strict mode"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_policy_drift_detection_no_cache(security_layer, tmp_path):
    """Test: First evaluation creates cache baseline."""
    test_file = tmp_path / "test.py"
    test_file.write_text("print('hello')", encoding="utf-8")

    result = await security_layer.detect_policy_drift(test_file, 0.5)

    assert result.approved is True, "First evaluation should pass (no drift)"
    assert result.reason == "no_drift"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_policy_drift_detection_large_drift(security_layer, tmp_path):
    """Test: Large risk delta triggers drift detection."""
    test_file = tmp_path / "test.py"
    test_file.write_text("print('hello')", encoding="utf-8")

    # First evaluation (low risk)
    await security_layer.detect_policy_drift(test_file, 0.2)

    # Second evaluation (high risk - should trigger drift)
    result = await security_layer.detect_policy_drift(test_file, 0.8)

    assert result.approved is False, "Large risk delta should trigger drift detection"
    assert result.reason == "critical_policy_drift"
    assert result.details["delta"] > 0.3


@pytest.mark.unit
@pytest.mark.asyncio
async def test_proposal_authentication_with_sender(security_layer):
    """Test: Proposal with valid sender authenticates."""
    proposal = {
        "proposal_id": "test-001",
        "type": "optimize",
        "sender": "self_improvement_engine",
    }

    result = await security_layer.authenticate_proposal(proposal)

    assert result.authenticated is True, "Proposal with sender should authenticate"
    assert result.sender == "self_improvement_engine"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_proposal_authentication_no_sender_permissive(security_layer):
    """Test: Proposal without sender allowed in permissive mode."""
    proposal = {
        "proposal_id": "test-002",
        "type": "optimize",
    }

    result = await security_layer.authenticate_proposal(proposal)

    assert result.authenticated is True, "Anonymous proposal allowed in permissive mode"
    assert result.sender == "anonymous"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_proposal_authentication_no_sender_strict(strict_security_layer):
    """Test: Proposal without sender rejected in strict mode."""
    proposal = {
        "proposal_id": "test-003",
        "type": "optimize",
    }

    result = await strict_security_layer.authenticate_proposal(proposal)

    assert result.authenticated is False, "Anonymous proposal rejected in strict mode"
    assert result.authorized is False
    assert result.reason == "unknown_sender_in_strict_mode"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_proposal_rate_limiting(security_layer):
    """Test: Rate limiting prevents proposal spam."""
    proposal = {
        "proposal_id": "test-004",
        "type": "optimize",
        "sender": "test_sender",
    }

    # Send proposals up to the limit
    results = []
    for i in range(12):  # Limit is 10 per minute
        result = await security_layer.authenticate_proposal(
            {**proposal, "proposal_id": f"test-{i}"}
        )
        results.append(result)

    # First 10 should pass
    assert all(r.authorized for r in results[:10]), "First 10 proposals should pass"

    # 11th and 12th should be rate limited
    assert results[10].authorized is False, "11th proposal should be rate limited"
    assert results[10].reason == "rate_limit_exceeded"
    assert results[11].authorized is False, "12th proposal should be rate limited"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_proposal_rate_limiting_window_reset(security_layer):
    """Test: Rate limit window resets after time period."""
    proposal = {
        "proposal_id": "test-005",
        "type": "optimize",
        "sender": "test_sender_2",
    }

    # Send 10 proposals (up to limit)
    for i in range(10):
        await security_layer.authenticate_proposal(
            {**proposal, "proposal_id": f"test-window-{i}"}
        )

    # 11th should be rate limited
    result_blocked = await security_layer.authenticate_proposal(
        {**proposal, "proposal_id": "test-window-11"}
    )
    assert result_blocked.authorized is False, "11th proposal should be rate limited"

    # Simulate time passing (cheat by clearing timestamps)
    security_layer._proposal_timestamps["test_sender_2"] = []

    # After window reset, proposals should pass again
    result_after_reset = await security_layer.authenticate_proposal(
        {**proposal, "proposal_id": "test-window-12"}
    )
    assert result_after_reset.authorized is True, (
        "Proposal after window reset should pass"
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_comprehensive_validation_all_checks_pass(security_layer, tmp_path):
    """Test: All security checks passing results in approval."""
    test_file = tmp_path / "test.py"
    test_file.write_text("print('hello')", encoding="utf-8")

    plan = {
        "required_capabilities": [],  # No capabilities required
    }

    result = await security_layer.validate_integration_security(test_file, plan)

    assert result.approved is True, "All checks passing should approve integration"
    assert result.reason == "security_approved"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_comprehensive_validation_signature_failure_strict(
    strict_security_layer, tmp_path
):
    """Test: Signature failure in strict mode rejects integration."""
    test_file = tmp_path / "test.py"
    test_file.write_text("print('hello')", encoding="utf-8")
    # No signature file created

    plan = {
        "required_capabilities": [],
    }

    result = await strict_security_layer.validate_integration_security(test_file, plan)

    assert result.approved is False, "Signature failure should reject in strict mode"
    assert result.reason == "signature_verification_failed"


if __name__ == "__main__":
    # Quick local test runner
    import sys

    sys.exit(pytest.main([__file__, "-v"]))
