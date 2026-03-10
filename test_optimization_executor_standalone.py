#!/usr/bin/env python
"""
Standalone test runner for OptimizationExecutor.

Avoids Aetherra engine initialization to prevent Unicode encoding issues.

Run: python test_optimization_executor_standalone.py
"""

import sys
import os
import tempfile
import json
from pathlib import Path
import unittest
import shutil

# Add workspace root to path
sys.path.insert(0, str(Path(__file__).parent))

from Aetherra.aetherra_core.system.optimization_executor import (
    OptimizationExecutor,
    OptimizationProposal,
    CodeChange,
    ConfigChange,
    Metrics,
)


class TestOptimizationExecutorStandalone(unittest.TestCase):
    """Standalone tests for OptimizationExecutor without engine dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)
        self.executor = OptimizationExecutor(
            workspace=str(self.workspace),
            enable_dry_run=False,
        )

        # Create workspace structure
        (self.workspace / "Aetherra").mkdir()
        (self.workspace / "tests").mkdir()

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_create_executor(self):
        """Test creating executor."""
        assert self.executor is not None
        assert self.executor.backup_dir.exists()

    def test_02_validate_proposal_valid(self):
        """Test validating valid proposal."""
        proposal = OptimizationProposal(
            proposal_id="opt_001",
            title="Test Optimization",
            description="A test optimization",
            optimization_type="code_refactoring",
        )
        is_valid, msg = self.executor._validate_proposal(proposal)
        assert is_valid, f"Validation failed: {msg}"

    def test_03_validate_proposal_missing_id(self):
        """Test validation catches missing proposal ID."""
        proposal = OptimizationProposal(
            proposal_id="",
            title="Test",
            description="Test",
            optimization_type="code_refactoring",
        )
        is_valid, msg = self.executor._validate_proposal(proposal)
        assert not is_valid

    def test_04_validate_proposal_invalid_type(self):
        """Test validation catches invalid optimization type."""
        proposal = OptimizationProposal(
            proposal_id="opt_001",
            title="Test",
            description="Test",
            optimization_type="invalid_type",
        )
        is_valid, msg = self.executor._validate_proposal(proposal)
        assert not is_valid

    def test_05_capture_metrics(self):
        """Test capturing workspace metrics."""
        metrics = self.executor._capture_metrics()
        assert metrics is not None
        assert metrics.code_lines >= 0
        assert metrics.execution_time > 0

    def test_06_create_backup(self):
        """Test creating workspace backup."""
        # Create test file
        test_file = self.workspace / "Aetherra" / "test.py"
        test_file.write_text("print('hello')")

        # Create backup
        backup_id = self.executor._create_backup("opt_001")
        assert backup_id is not None
        assert (self.executor.backup_dir / backup_id).exists()

    def test_07_list_backups(self):
        """Test listing available backups."""
        # Create backups
        self.executor._create_backup("opt_001")
        self.executor._create_backup("opt_002")

        # List backups
        backups = self.executor.list_backups()
        assert len(backups) >= 2

    def test_08_cleanup_backup(self):
        """Test cleaning up backup."""
        # Create backup
        backup_id = self.executor._create_backup("opt_001")
        assert (self.executor.backup_dir / backup_id).exists()

        # Cleanup
        self.executor._cleanup_backup(backup_id)
        assert not (self.executor.backup_dir / backup_id).exists()

    def test_09_dry_run_mode(self):
        """Test dry run mode doesn't apply changes."""
        executor = OptimizationExecutor(
            workspace=str(self.workspace),
            enable_dry_run=True,
        )

        proposal = OptimizationProposal(
            proposal_id="opt_001",
            title="Test",
            description="Test",
            optimization_type="code_refactoring",
        )

        changes = executor._apply_changes(proposal)
        assert changes == 0  # No actual changes in dry run

    def test_10_execute_simple_proposal(self):
        """Test executing simple optimization proposal."""
        proposal = OptimizationProposal(
            proposal_id="opt_001",
            title="Simple Optimization",
            description="A simple test",
            optimization_type="code_refactoring",
        )

        result = self.executor.execute(proposal, run_tests=False)
        assert result is not None
        assert result.proposal_id == "opt_001"

    def test_11_execute_with_code_changes(self):
        """Test executing proposal with code changes."""
        # Create test file
        test_file = self.workspace / "Aetherra" / "test.py"
        test_file.write_text("import os\nimport sys\nprint('test')")

        # Create proposal with code change
        change = CodeChange(
            file_path=str(test_file),
            change_type="remove_import",
            old_code="import sys\n",
            new_code="",
            reason="Remove unused import",
        )

        proposal = OptimizationProposal(
            proposal_id="opt_code_001",
            title="Code Cleanup",
            description="Remove unused imports",
            optimization_type="code_refactoring",
            code_changes=[change],
        )

        result = self.executor.execute(proposal, run_tests=False)
        assert result is not None

    def test_12_audit_trail_logging(self):
        """Test audit trail is populated."""
        proposal = OptimizationProposal(
            proposal_id="opt_audit_001",
            title="Audit Test",
            description="Test audit logging",
            optimization_type="code_refactoring",
        )

        result = self.executor.execute(proposal, run_tests=False)
        assert len(result.audit_trail) > 0

    def test_13_proposal_with_too_many_changes(self):
        """Test proposal with too many changes is rejected."""
        changes = [
            CodeChange(
                file_path="/fake/file.py",
                change_type="remove_import",
                old_code="import os",
                new_code="",
            )
            for _ in range(OptimizationExecutor.MAX_PROPOSAL_CHANGES + 1)
        ]

        proposal = OptimizationProposal(
            proposal_id="opt_many_001",
            title="Too many changes",
            description="Exceeds safety limit",
            optimization_type="code_refactoring",
            code_changes=changes,
        )

        is_valid, msg = self.executor._validate_proposal(proposal)
        assert not is_valid

    def test_14_metrics_comparison(self):
        """Test metrics comparison."""
        before = Metrics(
            execution_time=2.0,
            memory_usage=512,
        )
        after = Metrics(
            execution_time=1.0,
            memory_usage=256,
        )

        comparison = before.compare(after)
        # Negative values indicate improvement
        assert comparison["execution_time_improvement"] < 0
        assert comparison["memory_improvement"] < 0

    def test_15_config_change_json(self):
        """Test applying config change to JSON."""
        # Create test config
        config_file = Path(self.temp_dir) / "config.json"
        config = {
            "cache": {
                "max_size": 1000,
                "ttl": 3600,
            }
        }
        config_file.write_text(json.dumps(config))

        # Apply change
        change = ConfigChange(
            config_path=str(config_file),
            key_path="cache.max_size",
            old_value=1000,
            new_value=5000,
        )
        success, msg = change.apply_to_file()
        assert success, f"Config change failed: {msg}"

        # Verify change
        new_config = json.loads(config_file.read_text())
        assert new_config["cache"]["max_size"] == 5000

    def test_16_code_change_apply(self):
        """Test applying code change to file."""
        # Create test file
        test_file = Path(self.temp_dir) / "test.py"
        original_content = "import os\nimport sys\nprint('hello')"
        test_file.write_text(original_content)

        # Apply change
        change = CodeChange(
            file_path=str(test_file),
            change_type="remove_import",
            old_code="import sys\n",
            new_code="",
        )
        success, msg = change.apply_to_file()
        assert success, f"Code change failed: {msg}"

        # Verify change
        new_content = test_file.read_text()
        assert "import sys" not in new_content
        assert "import os" in new_content

    def test_17_restore_backup(self):
        """Test restoring from backup."""
        # Create original file
        test_file = self.workspace / "Aetherra" / "test.py"
        test_file.write_text("original content")

        # Create backup
        backup_id = self.executor._create_backup("opt_001")

        # Modify file
        test_file.write_text("modified content")

        # Restore backup
        self.executor._restore_backup(backup_id)

        # Verify restoration
        content = test_file.read_text()
        assert content == "original content"

    def test_18_optimization_result_fields(self):
        """Test ImplementationResult has all required fields."""
        proposal = OptimizationProposal(
            proposal_id="opt_result_001",
            title="Result Test",
            description="Test result structure",
            optimization_type="code_refactoring",
        )

        result = self.executor.execute(proposal, run_tests=False)

        # Check all fields present
        assert result.success is not None
        assert result.proposal_id is not None
        assert result.message is not None
        assert result.metrics_before is not None
        assert result.metrics_after is not None
        assert result.executed_at is not None

    def test_19_multiple_proposals_independent(self):
        """Test multiple proposals are independent."""
        proposal1 = OptimizationProposal(
            proposal_id="opt_multi_001",
            title="First Optimization",
            description="First",
            optimization_type="code_refactoring",
        )

        proposal2 = OptimizationProposal(
            proposal_id="opt_multi_002",
            title="Second Optimization",
            description="Second",
            optimization_type="config_tuning",
        )

        result1 = self.executor.execute(proposal1, run_tests=False)
        result2 = self.executor.execute(proposal2, run_tests=False)

        # Both should complete
        assert result1 is not None
        assert result2 is not None
        assert result1.proposal_id == "opt_multi_001"
        assert result2.proposal_id == "opt_multi_002"

    def test_20_all_optimization_types(self):
        """Test all 4 optimization types are recognized."""
        types = ["code_refactoring", "config_tuning", "algorithm", "resource"]

        for opt_type in types:
            proposal = OptimizationProposal(
                proposal_id=f"opt_{opt_type}",
                title=f"Test {opt_type}",
                description=f"Testing {opt_type}",
                optimization_type=opt_type,
            )
            is_valid, msg = self.executor._validate_proposal(proposal)
            assert is_valid, f"{opt_type} should be valid: {msg}"


def run_tests():
    """Run all tests with formatted output."""
    print("=" * 70)
    print("TASK 1.3: OPTIMIZATION EXECUTOR - UNIT TESTS")
    print("=" * 70)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestOptimizationExecutorStandalone)

    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print()
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    print()

    if result.wasSuccessful():
        print("✓ ALL TESTS PASSED")
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback[:200]}...")
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback[:200]}...")
        return 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
