"""
Unit tests for OptimizationExecutor - Execute and validate optimizations.

Tests cover:
- Code refactoring changes
- Config tuning changes
- Metric capture and comparison
- Proposal validation
- Backup and restore
- Dry run mode
- Rollback on failure
- Audit logging
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Aetherra.aetherra_core.system.optimization_executor import (
    CodeChange,
    ConfigChange,
    ImplementationResult,
    Metrics,
    OptimizationExecutor,
    OptimizationProposal,
)


class TestMetrics(unittest.TestCase):
    """Test Metrics dataclass."""

    def test_01_create_metrics(self):
        """Test creating metrics object."""
        metrics = Metrics(
            execution_time=1.5,
            memory_usage=256,
            cpu_usage=45.5,
            code_lines=5000,
            test_coverage=85.5,
        )
        self.assertEqual(metrics.execution_time, 1.5)
        self.assertEqual(metrics.memory_usage, 256)
        self.assertEqual(metrics.code_lines, 5000)

    def test_02_compare_metrics(self):
        """Test comparing metrics."""
        before = Metrics(
            execution_time=2.0,
            memory_usage=512,
            cpu_usage=80,
            code_lines=10000,
            test_coverage=75.0,
        )
        after = Metrics(
            execution_time=1.5,
            memory_usage=256,
            cpu_usage=40,
            code_lines=8000,
            test_coverage=85.0,
        )

        comparison = before.compare(after)
        self.assertTrue(comparison["execution_time_improvement"] < 0)  # Better
        self.assertTrue(comparison["memory_improvement"] < 0)  # Better
        self.assertTrue(comparison["code_reduction"] < 0)  # Fewer lines
        self.assertTrue(comparison["coverage_improvement"] > 0)  # Better coverage

    def test_03_custom_metrics(self):
        """Test custom metrics field."""
        metrics = Metrics(
            custom_metrics={
                "cache_hit_rate": 0.95,
                "avg_query_time": 0.15,
            }
        )
        self.assertEqual(metrics.custom_metrics["cache_hit_rate"], 0.95)


class TestCodeChange(unittest.TestCase):
    """Test CodeChange dataclass."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_create_code_change(self):
        """Test creating code change object."""
        change = CodeChange(
            file_path="/path/to/file.py",
            change_type="remove_import",
            old_code="import os, sys",
            new_code="import os",
            reason="Remove unused import",
        )
        self.assertEqual(change.change_type, "remove_import")
        self.assertEqual(change.reason, "Remove unused import")

    def test_02_apply_code_change(self):
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
        self.assertTrue(success)

        # Verify change
        new_content = test_file.read_text()
        self.assertNotIn("import sys", new_content)
        self.assertIn("import os", new_content)

    def test_03_apply_change_file_not_found(self):
        """Test applying change to non-existent file."""
        change = CodeChange(
            file_path="/nonexistent/file.py",
            change_type="remove_import",
            old_code="import os",
            new_code="",
        )
        success, msg = change.apply_to_file()
        self.assertFalse(success)


class TestConfigChange(unittest.TestCase):
    """Test ConfigChange dataclass."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_create_config_change(self):
        """Test creating config change object."""
        change = ConfigChange(
            config_path="/path/to/config.json",
            key_path="cache.max_size",
            old_value=1000,
            new_value=5000,
        )
        self.assertEqual(change.key_path, "cache.max_size")
        self.assertEqual(change.new_value, 5000)

    def test_02_apply_config_change_json(self):
        """Test applying change to JSON config."""
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
        self.assertTrue(success)

        # Verify change
        new_config = json.loads(config_file.read_text())
        self.assertEqual(new_config["cache"]["max_size"], 5000)

    def test_03_apply_config_change_yaml(self):
        """Test applying change to YAML config."""
        import yaml

        # Create test config
        config_file = Path(self.temp_dir) / "config.yaml"
        config = {
            "database": {
                "host": "localhost",
                "port": 5432,
            }
        }
        config_file.write_text(yaml.dump(config))

        # Apply change
        change = ConfigChange(
            config_path=str(config_file),
            key_path="database.port",
            old_value=5432,
            new_value=3306,
        )
        success, msg = change.apply_to_file()
        self.assertTrue(success)

        # Verify change
        new_config = yaml.safe_load(config_file.read_text())
        self.assertEqual(new_config["database"]["port"], 3306)


class TestOptimizationExecutor(unittest.TestCase):
    """Test OptimizationExecutor main functionality."""

    def setUp(self):
        """Set up test environment."""
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
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_create_executor(self):
        """Test creating executor."""
        self.assertIsNotNone(self.executor)
        self.assertTrue(self.executor.backup_dir.exists())

    def test_02_validate_proposal_valid(self):
        """Test validating valid proposal."""
        proposal = OptimizationProposal(
            proposal_id="opt_001",
            title="Test Optimization",
            description="A test optimization",
            optimization_type="code_refactoring",
        )
        is_valid, msg = self.executor._validate_proposal(proposal)
        self.assertTrue(is_valid)

    def test_03_validate_proposal_missing_id(self):
        """Test validation catches missing proposal ID."""
        proposal = OptimizationProposal(
            proposal_id="",
            title="Test",
            description="Test",
            optimization_type="code_refactoring",
        )
        is_valid, msg = self.executor._validate_proposal(proposal)
        self.assertFalse(is_valid)
        self.assertIn("proposal_id", msg)

    def test_04_validate_proposal_invalid_type(self):
        """Test validation catches invalid optimization type."""
        proposal = OptimizationProposal(
            proposal_id="opt_001",
            title="Test",
            description="Test",
            optimization_type="invalid_type",
        )
        is_valid, msg = self.executor._validate_proposal(proposal)
        self.assertFalse(is_valid)

    def test_05_capture_metrics(self):
        """Test capturing workspace metrics."""
        metrics = self.executor._capture_metrics()
        self.assertIsNotNone(metrics)
        self.assertGreater(metrics.code_lines, 0)
        self.assertGreater(metrics.execution_time, 0)

    def test_06_create_backup(self):
        """Test creating workspace backup."""
        # Create test file
        test_file = self.workspace / "Aetherra" / "test.py"
        test_file.write_text("print('hello')")

        # Create backup
        backup_id = self.executor._create_backup("opt_001")
        self.assertIsNotNone(backup_id)
        self.assertTrue((self.executor.backup_dir / backup_id).exists())

    def test_07_restore_backup(self):
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
        self.assertEqual(content, "original content")

    def test_08_list_backups(self):
        """Test listing available backups."""
        # Create backups
        self.executor._create_backup("opt_001")
        self.executor._create_backup("opt_002")

        # List backups
        backups = self.executor.list_backups()
        self.assertGreaterEqual(len(backups), 2)

    def test_09_cleanup_backup(self):
        """Test cleaning up backup."""
        # Create backup
        backup_id = self.executor._create_backup("opt_001")
        self.assertTrue((self.executor.backup_dir / backup_id).exists())

        # Cleanup
        self.executor._cleanup_backup(backup_id)
        self.assertFalse((self.executor.backup_dir / backup_id).exists())

    def test_10_dry_run_mode(self):
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
        self.assertEqual(changes, 0)  # No actual changes in dry run

    def test_11_execute_simple_proposal(self):
        """Test executing simple optimization proposal."""
        proposal = OptimizationProposal(
            proposal_id="opt_001",
            title="Simple Optimization",
            description="A simple test",
            optimization_type="code_refactoring",
        )

        result = self.executor.execute(proposal, run_tests=False)
        self.assertIsNotNone(result)
        self.assertEqual(result.proposal_id, "opt_001")

    def test_12_execute_with_code_changes(self):
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
        self.assertIsNotNone(result)

    def test_13_audit_trail_logging(self):
        """Test audit trail is populated."""
        proposal = OptimizationProposal(
            proposal_id="opt_audit_001",
            title="Audit Test",
            description="Test audit logging",
            optimization_type="code_refactoring",
        )

        result = self.executor.execute(proposal, run_tests=False)
        self.assertGreater(len(result.audit_trail), 0)
        # Check for timestamped entries
        self.assertTrue(
            any(
                datetime.now().isoformat()[:10] in entry for entry in result.audit_trail
            )
        )

    def test_14_proposal_with_too_many_changes(self):
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
        self.assertFalse(is_valid)

    def test_15_metrics_comparison_shows_improvement(self):
        """Test metrics show optimization improvements."""
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
        self.assertLess(comparison["execution_time_improvement"], 0)
        self.assertLess(comparison["memory_improvement"], 0)

    def test_16_config_change_unsupported_format(self):
        """Test config change with unsupported file format."""
        # Create unsupported config file
        config_file = Path(self.temp_dir) / "config.xml"
        config_file.write_text("<config></config>")

        change = ConfigChange(
            config_path=str(config_file),
            key_path="setting",
            old_value="old",
            new_value="new",
        )

        success, msg = change.apply_to_file()
        self.assertFalse(success)

    def test_17_code_change_object_not_found(self):
        """Test code change when target code doesn't exist."""
        # Create test file
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('hello')")

        change = CodeChange(
            file_path=str(test_file),
            change_type="remove_import",
            old_code="import nonexistent",  # Not in file
            new_code="",
        )

        success, msg = change.apply_to_file()
        self.assertFalse(success)

    def test_18_optimization_result_structure(self):
        """Test ImplementationResult has all required fields."""
        proposal = OptimizationProposal(
            proposal_id="opt_result_001",
            title="Result Test",
            description="Test result structure",
            optimization_type="code_refactoring",
        )

        result = self.executor.execute(proposal, run_tests=False)

        # Check all fields present
        self.assertIsNotNone(result.success)
        self.assertIsNotNone(result.proposal_id)
        self.assertIsNotNone(result.message)
        self.assertIsNotNone(result.metrics_before)
        self.assertIsNotNone(result.metrics_after)
        self.assertIsNotNone(result.executed_at)

    def test_19_restore_backup_invalid_id(self):
        """Test restoring with invalid backup ID."""
        success, msg = self.executor.restore_backup("nonexistent_backup")
        # Should handle gracefully
        self.assertIsNotNone(msg)

    def test_20_multiple_optimizations_independent(self):
        """Test multiple optimizations are independent."""
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
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
        self.assertEqual(result1.proposal_id, "opt_multi_001")
        self.assertEqual(result2.proposal_id, "opt_multi_002")


if __name__ == "__main__":
    unittest.main(verbosity=2)
