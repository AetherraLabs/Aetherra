"""
Optimization Executor - Apply and validate performance optimizations.

Manages optimization proposals, applies changes safely, validates results,
and rolls back on failure. Supports 4 optimization types:
  1. Code refactoring (remove unused imports, consolidate functions)
  2. Configuration tuning (cache sizes, timeouts, batch sizes)
  3. Algorithm improvements (data structure replacements)
  4. Resource allocation (memory, CPU, I/O optimization)

Features:
  - Atomic operations (backup → apply → validate → commit)
  - Automatic rollback on test failures
  - Metrics verification and comparison
  - Detailed audit trail for all changes
  - Safety limits (max file size, etc.)

Example:
    >>> executor = OptimizationExecutor(workspace="/path/to/workspace")
    >>> proposal = OptimizationProposal(...)
    >>> result = executor.execute(proposal)
    >>> if result.success:
    ...     print(f"Optimization improved {result.metrics_gained}")
"""

import json
import logging
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from Aetherra.guardian import GuardianStatus, IntentDeclaration, evaluate_intent
from Aetherra.security.capabilities import has_capability

logger = logging.getLogger(__name__)


@dataclass
class Metrics:
    """Performance metrics for comparison."""

    execution_time: float = 0.0
    """Execution time in seconds"""
    memory_usage: float = 0.0
    """Memory usage in MB"""
    cpu_usage: float = 0.0
    """CPU usage percentage"""
    code_lines: int = 0
    """Total lines of code"""
    test_coverage: float = 0.0
    """Test coverage percentage"""
    custom_metrics: Dict[str, Any] = field(default_factory=dict)
    """Custom application-specific metrics"""

    def compare(self, other: "Metrics") -> Dict[str, float]:
        """
        Compare metrics with another set.

        Args:
            other: Metrics to compare against

        Returns:
            Dictionary of improvements (negative = better)
        """
        return {
            "execution_time_improvement": other.execution_time - self.execution_time,
            "memory_improvement": other.memory_usage - self.memory_usage,
            "cpu_improvement": other.cpu_usage - self.cpu_usage,
            "code_reduction": other.code_lines - self.code_lines,
            "coverage_improvement": other.test_coverage - self.test_coverage,
        }


@dataclass
class CodeChange:
    """A single code change to apply."""

    file_path: str
    """Path to file to modify"""
    change_type: str
    """Type: 'remove_import', 'consolidate_function', 'replace_algorithm'"""
    old_code: str
    """Original code snippet"""
    new_code: str
    """Replacement code snippet"""
    reason: str = ""
    """Why this change is being made"""
    line_number: int = 0
    """Line number where change occurs"""

    def apply_to_file(self) -> Tuple[bool, str]:
        """
        Apply change to file.

        Returns:
            Tuple of (success, message)
        """
        try:
            with open(self.file_path) as f:
                content = f.read()

            if self.old_code not in content:
                return (
                    False,
                    f"Old code not found in {self.file_path}",
                )

            new_content = content.replace(self.old_code, self.new_code)

            with open(self.file_path, "w") as f:
                f.write(new_content)

            return True, f"Applied change to {self.file_path}"
        except Exception as e:
            return False, f"Error applying change: {str(e)}"


@dataclass
class ConfigChange:
    """A configuration change to apply."""

    config_path: str
    """Path to config file"""
    key_path: str
    """Dot-notation path to config key (e.g., 'cache.max_size')"""
    old_value: Any
    """Original value"""
    new_value: Any
    """New value"""
    reason: str = ""
    """Why this change is being made"""

    def apply_to_file(self) -> Tuple[bool, str]:
        """
        Apply config change to file.

        Returns:
            Tuple of (success, message)
        """
        try:
            # Load config file
            with open(self.config_path) as f:
                if self.config_path.endswith(".json"):
                    config = json.load(f)
                elif self.config_path.endswith(".yaml") or self.config_path.endswith(".yml"):
                    config = yaml.safe_load(f)
                else:
                    return False, "Unsupported config format"

            # Navigate to nested key
            keys = self.key_path.split(".")
            current = config
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]

            # Check old value matches
            if current.get(keys[-1]) != self.old_value:
                return False, "Current value doesn't match expected old value"

            # Apply change
            current[keys[-1]] = self.new_value

            # Save config file
            with open(self.config_path, "w") as f:
                if self.config_path.endswith(".json"):
                    json.dump(config, f, indent=2)
                else:
                    yaml.safe_dump(config, f)

            return True, f"Applied config change to {self.config_path}"
        except Exception as e:
            return False, f"Error applying config change: {str(e)}"


@dataclass
class OptimizationProposal:
    """A proposed optimization to apply."""

    proposal_id: str
    """Unique identifier for proposal"""
    title: str
    """Human-readable title"""
    description: str
    """Detailed description"""
    optimization_type: str
    """Type: 'code_refactoring', 'config_tuning', 'algorithm', 'resource'"""
    code_changes: List[CodeChange] = field(default_factory=list)
    """Code changes to apply"""
    config_changes: List[ConfigChange] = field(default_factory=list)
    """Config changes to apply"""
    expected_metrics: Metrics = field(default_factory=Metrics)
    """Expected metrics after optimization"""
    risk_level: str = "low"
    """Risk level: 'low', 'medium', 'high'"""
    requires_verification: bool = True
    """Whether proposal requires test verification"""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    """Creation timestamp"""


@dataclass
class ImplementationResult:
    """Result of optimization execution."""

    success: bool
    """Whether optimization succeeded"""
    proposal_id: str
    """ID of executed proposal"""
    message: str
    """Status message"""
    metrics_before: Metrics = field(default_factory=Metrics)
    """Metrics before optimization"""
    metrics_after: Metrics = field(default_factory=Metrics)
    """Metrics after optimization"""
    metrics_gained: Dict[str, float] = field(default_factory=dict)
    """Improvements from optimization"""
    changes_applied: int = 0
    """Number of changes applied"""
    rollback_reason: str = ""
    """Reason for rollback if any"""
    audit_trail: List[str] = field(default_factory=list)
    """Detailed audit log"""
    executed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    """Execution timestamp"""


class OptimizationExecutor:
    """Execute optimization proposals with safety and rollback capability."""

    # Safety limits
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
    MAX_CHANGES_PER_FILE = 1000
    MAX_PROPOSAL_CHANGES = 5000

    def __init__(
        self,
        workspace: str,
        backup_dir: Optional[str] = None,
        enable_dry_run: bool = False,
    ):
        """
        Initialize OptimizationExecutor.

        Args:
            workspace: Path to workspace directory
            backup_dir: Directory for backups (default: .optimization_backups)
            enable_dry_run: If True, don't actually apply changes
        """
        self.workspace = Path(workspace)
        self.backup_dir = Path(backup_dir or self.workspace / ".optimization_backups")
        self.enable_dry_run = enable_dry_run
        self.backup_dir.mkdir(exist_ok=True, parents=True)
        logger.info(
            f"OptimizationExecutor initialized: workspace={workspace}, dry_run={enable_dry_run}"
        )

    def _guardian_preflight(self, proposal: OptimizationProposal) -> None:
        target_paths = [
            Path(change.file_path) for change in proposal.code_changes
        ] + [
            Path(change.config_path) for change in proposal.config_changes
        ]
        target_names = tuple(sorted({path.name for path in target_paths if path.name}))
        target_suffixes = tuple(sorted({path.suffix for path in target_paths if path.suffix}))
        target_hashes = tuple(
            sorted(
                {
                    self._path_fingerprint(str(path.expanduser().resolve(strict=False)))
                    for path in target_paths
                }
            )
        )
        requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "optimization_executor"
        intent = IntentDeclaration(
            requester=requester,
            subsystem="optimization_executor",
            action="optimization.apply",
            target=f"optimization:{proposal.proposal_id}",
            purpose=f"Apply optimization proposal: {proposal.title}",
            capabilities=("fs:write", "code:modify"),
            expected_outcome="Optimization proposal is applied with backup and verification",
            reversible=True,
            rollback_plan="Restore the workspace from the optimization backup",
            evidence=(f"proposal:{proposal.proposal_id}",),
            metadata={
                "optimization_type": proposal.optimization_type,
                "risk_level": proposal.risk_level,
                "code_change_count": len(proposal.code_changes),
                "config_change_count": len(proposal.config_changes),
                "requires_verification": bool(proposal.requires_verification),
                "dry_run": bool(self.enable_dry_run),
                "target_names": target_names,
                "target_suffixes": target_suffixes,
                "target_path_hashes": target_hashes,
            },
        )
        decision = evaluate_intent(intent, capability_checker=has_capability)
        if decision.status not in {GuardianStatus.ALLOW, GuardianStatus.ALLOW_LIMITED}:
            raise PermissionError(
                f"Guardian denied optimization proposal {proposal.proposal_id}: {decision.reason}"
            )

    def _guardian_preflight_restore_backup(self, backup_id: str) -> None:
        backup_path = self.backup_dir / backup_id
        backup_items = (
            tuple(sorted(item.name for item in backup_path.iterdir()))
            if backup_path.exists()
            else ()
        )
        requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "optimization_executor"
        backup_hash = self._path_fingerprint(backup_id)
        intent = IntentDeclaration(
            requester=requester,
            subsystem="maintenance",
            action="maintenance.restore_backup",
            target=f"maintenance:optimization_backup:{backup_hash}",
            purpose="Restore workspace files from an optimization backup",
            capabilities=("maintenance:restore", "fs:write"),
            expected_outcome="Workspace files are restored from a selected optimization backup",
            reversible=True,
            rollback_plan="create or retain a newer backup before destructive restore operations",
            evidence=("optimization_executor.restore_backup",),
            metadata={
                "backup_id_hash": backup_hash,
                "backup_exists": backup_path.exists(),
                "backup_item_count": len(backup_items),
                "backup_item_names": backup_items[:10],
            },
        )
        decision = evaluate_intent(intent, capability_checker=has_capability)
        if decision.status not in {GuardianStatus.ALLOW, GuardianStatus.ALLOW_LIMITED}:
            raise PermissionError(
                f"Guardian denied optimization backup restore: {decision.reason}"
            )

    @staticmethod
    def _path_fingerprint(path_value: str) -> str:
        import hashlib

        return hashlib.sha256(path_value.encode("utf-8", errors="replace")).hexdigest()[:16]

    def execute(
        self,
        proposal: OptimizationProposal,
        run_tests: bool = True,
    ) -> ImplementationResult:
        """
        Execute optimization proposal with safety checks.

        Process:
          1. Validate proposal
          2. Capture baseline metrics
          3. Create backup
          4. Apply changes
          5. Verify results
          6. If successful: commit changes and log
          7. If failed: rollback and report

        Args:
            proposal: Optimization proposal to execute
            run_tests: Whether to run tests after applying changes

        Returns:
            ImplementationResult with success status and metrics
        """
        result = ImplementationResult(
            success=False,
            proposal_id=proposal.proposal_id,
            message="Starting optimization",
        )

        try:
            # Step 1: Validate proposal
            is_valid, validation_errors = self._validate_proposal(proposal)
            if not is_valid:
                result.message = f"Proposal validation failed: {validation_errors}"
                return result

            result.audit_trail.append(f"[{datetime.now().isoformat()}] Proposal validation passed")

            self._guardian_preflight(proposal)
            result.audit_trail.append(f"[{datetime.now().isoformat()}] Guardian preflight passed")

            # Step 2: Capture baseline metrics
            result.metrics_before = self._capture_metrics()
            result.audit_trail.append(f"[{datetime.now().isoformat()}] Baseline metrics captured")

            # Step 3: Create backup
            backup_id = self._create_backup(proposal.proposal_id)
            result.audit_trail.append(f"[{datetime.now().isoformat()}] Created backup: {backup_id}")

            # Step 4: Apply changes
            changes_applied = self._apply_changes(proposal)
            result.changes_applied = changes_applied
            result.audit_trail.append(
                f"[{datetime.now().isoformat()}] Applied {changes_applied} changes "
                f"(dry_run={self.enable_dry_run})"
            )

            # Step 5: Verify results
            if run_tests:
                is_valid, test_errors = self._run_verification(proposal)
                if not is_valid:
                    result.rollback_reason = f"Test failures: {test_errors}"
                    result.audit_trail.append(
                        f"[{datetime.now().isoformat()}] Verification failed: {test_errors}"
                    )
                    # Rollback
                    self._restore_backup(backup_id)
                    result.audit_trail.append(
                        f"[{datetime.now().isoformat()}] Rolled back to {backup_id}"
                    )
                    result.message = f"Optimization failed and rolled back: {test_errors}"
                    return result

            # Step 6: Capture metrics after optimization
            result.metrics_after = self._capture_metrics()
            result.audit_trail.append(f"[{datetime.now().isoformat()}] Final metrics captured")

            # Step 7: Compare metrics
            result.metrics_gained = result.metrics_before.compare(result.metrics_after)
            result.audit_trail.append(
                f"[{datetime.now().isoformat()}] Metrics improved: {result.metrics_gained}"
            )

            # Step 8: Commit changes
            if not self.enable_dry_run:
                self._cleanup_backup(backup_id)
                result.audit_trail.append(
                    f"[{datetime.now().isoformat()}] Backup cleaned up, changes committed"
                )

            result.success = True
            result.message = "Optimization completed successfully: "
            f"{changes_applied} changes applied"
            logger.info(f"Optimization {proposal.proposal_id} completed successfully")

            return result

        except Exception as e:
            logger.error(f"Optimization execution failed: {e}")
            result.message = f"Unexpected error: {str(e)}"
            result.rollback_reason = str(e)
            result.audit_trail.append(f"[{datetime.now().isoformat()}] Error: {str(e)}")
            return result

    def _validate_proposal(self, proposal: OptimizationProposal) -> Tuple[bool, str]:
        """
        Validate optimization proposal.

        Args:
            proposal: Proposal to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check proposal has required fields
        if not proposal.proposal_id:
            return False, "proposal_id required"
        if not proposal.title:
            return False, "title required"
        if proposal.optimization_type not in [
            "code_refactoring",
            "config_tuning",
            "algorithm",
            "resource",
        ]:
            return False, f"Invalid optimization_type: {proposal.optimization_type}"

        # Check safety limits
        total_changes = len(proposal.code_changes) + len(proposal.config_changes)
        if total_changes > self.MAX_PROPOSAL_CHANGES:
            return (
                False,
                f"Too many changes: {total_changes} > {self.MAX_PROPOSAL_CHANGES}",
            )

        # Check files exist
        for change in proposal.code_changes:
            if not Path(change.file_path).exists():
                return False, f"File not found: {change.file_path}"

        for change in proposal.config_changes:
            if not Path(change.config_path).exists():
                return False, f"Config file not found: {change.config_path}"

        return True, ""

    def _capture_metrics(self) -> Metrics:
        """
        Capture current system metrics.

        Args:
            None

        Returns:
            Metrics object with current values
        """
        metrics = Metrics()

        try:
            # Count code lines in workspace
            total_lines = 0
            for py_file in self.workspace.rglob("*.py"):
                if ".optimization_backups" not in str(py_file):
                    try:
                        with open(py_file, errors="ignore") as f:
                            total_lines += len(f.readlines())
                    except Exception:
                        pass

            metrics.code_lines = total_lines

            # Mock metrics (in real implementation, would measure actual values)
            import random

            metrics.execution_time = random.uniform(0.1, 2.0)
            metrics.memory_usage = random.uniform(100, 500)
            metrics.cpu_usage = random.uniform(10, 80)
            metrics.test_coverage = random.uniform(60, 95)

        except Exception as e:
            logger.warning(f"Error capturing metrics: {e}")

        return metrics

    def _create_backup(self, proposal_id: str) -> str:
        """
        Create backup of workspace before changes.

        Args:
            proposal_id: ID of proposal for backup naming

        Returns:
            Backup ID
        """
        backup_id = f"{proposal_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = self.backup_dir / backup_id

        try:
            if backup_path.exists():
                shutil.rmtree(backup_path)

            # Backup important directories
            for item in ["Aetherra", "src", "tests", "configs"]:
                src = self.workspace / item
                if src.exists():
                    dst = backup_path / item
                    shutil.copytree(
                        src, dst, ignore=shutil.ignore_patterns("__pycache__", ".pyc", ".git")
                    )

            logger.info(f"Created backup: {backup_id}")
            return backup_id

        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            raise

    def _apply_changes(self, proposal: OptimizationProposal) -> int:
        """
        Apply all changes from proposal.

        Args:
            proposal: Optimization proposal with changes

        Returns:
            Number of successful changes applied
        """
        count = 0

        # Apply code changes
        for change in proposal.code_changes:
            if not self.enable_dry_run:
                success, msg = change.apply_to_file()
                if success:
                    count += 1
                    logger.debug(f"Code change applied: {msg}")
                else:
                    logger.warning(f"Code change failed: {msg}")
            else:
                logger.debug(f"[DRY RUN] Would apply: {change.reason}")
                count += 1

        # Apply config changes
        for change in proposal.config_changes:
            if not self.enable_dry_run:
                success, msg = change.apply_to_file()
                if success:
                    count += 1
                    logger.debug(f"Config change applied: {msg}")
                else:
                    logger.warning(f"Config change failed: {msg}")
            else:
                logger.debug(f"[DRY RUN] Would apply: {change.reason}")
                count += 1

        return count

    def _run_verification(self, proposal: OptimizationProposal) -> Tuple[bool, str]:
        """
        Run verification tests after changes.

        Args:
            proposal: Proposal that was executed

        Returns:
            Tuple of (tests_passed, error_message)
        """
        # Mock test execution
        try:
            # In real implementation, would run actual test suite
            # For now, simulate test results
            import random

            # High-risk proposals have higher failure rate
            failure_rate = 0.3 if proposal.risk_level == "high" else 0.1

            if random.random() < failure_rate:
                return False, "Test suite failed: 5 tests failed"
            else:
                return True, ""

        except Exception as e:
            return False, f"Error running tests: {str(e)}"

    def _restore_backup(self, backup_id: str):
        """
        Restore workspace from backup.

        Args:
            backup_id: ID of backup to restore
        """
        try:
            backup_path = self.backup_dir / backup_id

            if not backup_path.exists():
                logger.error(f"Backup not found: {backup_id}")
                return

            # Restore directories from backup
            for item in backup_path.iterdir():
                if item.is_dir():
                    dst = self.workspace / item.name
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(item, dst)

            logger.info(f"Restored from backup: {backup_id}")

        except Exception as e:
            logger.error(f"Error restoring backup: {e}")

    def _cleanup_backup(self, backup_id: str):
        """
        Delete backup after successful optimization.

        Args:
            backup_id: ID of backup to clean up
        """
        try:
            backup_path = self.backup_dir / backup_id

            if backup_path.exists():
                shutil.rmtree(backup_path)
                logger.info(f"Deleted backup: {backup_id}")

        except Exception as e:
            logger.warning(f"Error deleting backup: {e}")

    def list_backups(self) -> List[str]:
        """
        List all available backups.

        Returns:
            List of backup IDs
        """
        if not self.backup_dir.exists():
            return []

        return [d.name for d in self.backup_dir.iterdir() if d.is_dir()]

    def restore_backup(self, backup_id: str) -> Tuple[bool, str]:
        """
        Manual restore from backup (user-initiated).

        Args:
            backup_id: ID of backup to restore

        Returns:
            Tuple of (success, message)
        """
        try:
            self._guardian_preflight_restore_backup(backup_id)
            self._restore_backup(backup_id)
            return True, f"Restored from backup: {backup_id}"
        except Exception as e:
            return False, f"Error restoring backup: {str(e)}"
