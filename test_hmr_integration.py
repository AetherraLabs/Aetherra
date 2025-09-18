#!/usr/bin/env python3
"""
HMR Integration Test for Self-Incorporation System
================================================

Test script to verify that HMR integration is properly implemented
in the self-incorporation system.
"""

import asyncio
import json
import logging
import tempfile
from pathlib import Path
from unittest.mock import Mock

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_hmr_integration():
    """Test HMR integration functionality."""
    logger.info("🧪 Starting HMR Integration Test...")

    try:
        # Import the self-incorporation service
        from aetherra_self_incorporation import (
            SelfIncorporationConfig,
            SelfIncorporationService,
        )

        # Create a temporary config
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            config = SelfIncorporationConfig()
            config.hmr_enabled = True
            config.index_db_path = temp_path / "test_index.db"
            config.index_jsonl_path = temp_path / "test_index.jsonl"

            # Create service instance
            service = SelfIncorporationService(config)

            # Test HMR controller access
            integrator = service.core_integrator
            hmr_controller = integrator._get_hmr_controller()

            logger.info(f"✅ HMR Controller availability: {hmr_controller is not None}")

            # Test rollback token generation
            test_target = {
                "file_id": "sha256:test123456789abc",
                "path": "test/module.py",
                "trust_tier": "standard",
            }

            rollback_token = integrator._generate_rollback_token(
                "register_plugin", test_target
            )
            logger.info(f"✅ Rollback token generated: {rollback_token}")

            assert rollback_token.startswith("rb_register_plugin_"), (
                f"Invalid token format: {rollback_token}"
            )

            # Test HMR routing logic
            should_use_hmr_plugin = integrator._should_use_hmr(
                "register_plugin", test_target
            )
            should_use_hmr_docs = integrator._should_use_hmr("index_docs", test_target)

            logger.info(
                f"✅ HMR routing - plugin: {should_use_hmr_plugin}, docs: {should_use_hmr_docs}"
            )

            assert should_use_hmr_plugin == True, "register_plugin should use HMR"
            assert should_use_hmr_docs == False, "index_docs should not use HMR"

            # Test rollback functionality
            test_token = "rb_test_action_123456789_1726467600_abcd1234"
            rollback_result = await service.trigger_rollback(test_token)

            logger.info(f"✅ Rollback test result: {rollback_result}")

            # In test environment, HMR controller may not be available
            expected_errors = ["rollback_token_not_found", "hmr_controller_unavailable"]
            actual_error = rollback_result.get("error")
            assert actual_error in expected_errors, (
                f"Expected one of {expected_errors}, got: {rollback_result}"
            )

            # Test API integration patterns
            logger.info("✅ Testing integration with HMR...")

            # Create a mock plan action
            test_plan = {
                "plan_id": "test_hmr_plan",
                "actions": [
                    {
                        "action": "register_plugin",
                        "target": test_target,
                        "deps": [],
                        "priority": "normal",
                    }
                ],
            }

            # Execute in dry-run mode (should not fail)
            integration_result = await integrator.execute_plan(test_plan, dry_run=True)
            logger.info(f"✅ Dry-run integration result: {integration_result}")

            assert integration_result.get("ok") is not None, (
                "Integration should return ok status"
            )

        logger.info("🎉 All HMR integration tests passed!")
        return True

    except Exception as e:
        logger.error(f"❌ HMR integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run the HMR integration test."""
    success = await test_hmr_integration()
    if success:
        print("\n✅ HMR Integration Test: PASSED")
        exit(0)
    else:
        print("\n❌ HMR Integration Test: FAILED")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
