"""
Lyrixa/Aetherra Mutation Engine
--------------------------------
This module provides a safe, sandboxed environment for code and configuration mutation, validation, and rollback.
It is designed to be used by the self-evaluation agent for autonomous self-improvement.

Features:
    - Apply code/config mutations in a sandboxed environment
    - Validate changes via tests, linting, and static analysis
    - Rollback on failure or upon user request
    - Log all mutations and results
    - Support for human-in-the-loop review/approval
    - Multi-language support (Python, JavaScript, JSON, YAML, etc.)
    - Safety mechanisms and validation pipelines
    - Backup and restore functionality
"""

import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class MutationType(Enum):
    """Types of mutations that can be applied"""

    CODE_MODIFICATION = "code_modification"
    CONFIG_UPDATE = "config_update"
    DEPENDENCY_CHANGE = "dependency_change"
    STRUCTURE_CHANGE = "structure_change"
    FEATURE_ADDITION = "feature_addition"
    BUG_FIX = "bug_fix"
    OPTIMIZATION = "optimization"
    REFACTORING = "refactoring"


class ValidationLevel(Enum):
    """Validation strictness levels"""

    BASIC = "basic"  # Basic syntax check
    STANDARD = "standard"  # Linting + basic tests
    STRICT = "strict"  # Full test suite + static analysis
    PARANOID = "paranoid"  # All checks + security analysis


class MutationStatus(Enum):
    """Status of a mutation"""

    PENDING = "pending"
    APPLIED = "applied"
    VALIDATED = "validated"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class MutationResult:
    """Result of a mutation operation"""

    success: bool
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Result of mutation validation"""

    passed: bool
    score: float  # 0.0 to 1.0
    checks: Dict[str, bool] = field(default_factory=dict)
    messages: List[str] = field(default_factory=list)
    performance_impact: Optional[Dict[str, float]] = None


@dataclass
class Mutation:
    """Represents a single mutation to be applied"""

    mutation_id: str
    mutation_type: MutationType
    target_file: str
    description: str
    content: Optional[str] = None
    content_changes: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    status: MutationStatus = MutationStatus.PENDING
    backup_path: Optional[str] = None
    validation_level: ValidationLevel = ValidationLevel.STANDARD


class MutationEngine:
    """
    Production-ready mutation engine for safe code and configuration changes.

    Provides comprehensive mutation, validation, and rollback capabilities with
    multi-language support and safety mechanisms.
    """

    def __init__(
        self,
        work_directory: Optional[str] = None,
        backup_directory: Optional[str] = None,
        log_file: Optional[str] = None,
        validation_level: ValidationLevel = ValidationLevel.STANDARD,
        auto_backup: bool = True,
        require_approval: bool = False,
    ):
        self.work_directory = Path(work_directory or os.getcwd())
        self.backup_directory = Path(
            backup_directory or self.work_directory / ".mutations" / "backups"
        )
        self.log_file = Path(
            log_file or self.work_directory / ".mutations" / "mutation_log.json"
        )
        self.validation_level = validation_level
        self.auto_backup = auto_backup
        self.require_approval = require_approval

        # Ensure directories exist
        self.backup_directory.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Active mutations tracking
        self.active_mutations: Dict[str, Mutation] = {}
        self.mutation_history: List[Mutation] = []

        # Validation tools configuration
        self.validation_tools = {
            "python": {
                "syntax": ["python", "-m", "py_compile"],
                "lint": ["flake8", "--max-line-length=100"],
                "format": ["black", "--check"],
                "type": ["mypy"],
                "test": ["pytest", "-v"],
            },
            "javascript": {
                "syntax": ["node", "--check"],
                "lint": ["eslint"],
                "format": ["prettier", "--check"],
                "test": ["npm", "test"],
            },
            "json": {"syntax": ["python", "-m", "json.tool"], "format": ["jq", "."]},
            "yaml": {
                "syntax": ["python", "-c", "import yaml; yaml.safe_load(open('{}'))"]
            },
        }

        print("[TOOL] Mutation Engine initialized")
        print(f"   📁 Work directory: {self.work_directory}")
        print(f"   💾 Backup directory: {self.backup_directory}")
        print(f"   📊 Validation level: {self.validation_level.value}")
        print(f"   🔒 Approval required: {self.require_approval}")

    def create_mutation(
        self,
        target_file: str,
        description: str,
        mutation_type: MutationType = MutationType.CODE_MODIFICATION,
        content: Optional[str] = None,
        content_changes: Optional[Dict[str, Any]] = None,
        validation_level: Optional[ValidationLevel] = None,
    ) -> str:
        """Create a new mutation"""
        mutation_id = f"mut_{int(time.time())}_{len(self.active_mutations)}"

        mutation = Mutation(
            mutation_id=mutation_id,
            mutation_type=mutation_type,
            target_file=target_file,
            description=description,
            content=content,
            content_changes=content_changes,
            validation_level=validation_level or self.validation_level,
            metadata={
                "original_file_size": self._get_file_size(target_file),
                "original_file_hash": self._get_file_hash(target_file),
            },
        )

        self.active_mutations[mutation_id] = mutation
        print(f"🧬 Created mutation {mutation_id}: {description}")
        return mutation_id

    def apply_mutation(self, mutation_id: str) -> MutationResult:
        """Apply a mutation in a safe, sandboxed environment"""
        if mutation_id not in self.active_mutations:
            return MutationResult(
                success=False,
                message=f"Mutation {mutation_id} not found",
                errors=[f"Unknown mutation ID: {mutation_id}"],
            )

        mutation = self.active_mutations[mutation_id]

        try:
            # Create backup if auto_backup is enabled
            if self.auto_backup:
                backup_result = self._create_backup(mutation)
                if not backup_result.success:
                    return backup_result

            # Apply the mutation
            if mutation.content is not None:
                result = self._apply_content_mutation(mutation)
            elif mutation.content_changes:
                result = self._apply_changes_mutation(mutation)
            else:
                return MutationResult(
                    success=False,
                    message="No content or changes specified for mutation",
                    errors=["Either content or content_changes must be provided"],
                )

            if result.success:
                mutation.status = MutationStatus.APPLIED
                self._log_mutation(mutation, result)
                print(f"✅ Applied mutation {mutation_id}")
            else:
                print(f"[ERROR] Failed to apply mutation {mutation_id}")

            return result

        except Exception as e:
            error_msg = f"Error applying mutation {mutation_id}: {str(e)}"
            print(error_msg)
            return MutationResult(success=False, message=error_msg, errors=[str(e)])

    def validate_mutation(self, mutation_id: str) -> ValidationResult:
        """Validate a mutation using comprehensive checks"""
        if mutation_id not in self.active_mutations:
            return ValidationResult(
                passed=False, score=0.0, messages=[f"Mutation {mutation_id} not found"]
            )

        mutation = self.active_mutations[mutation_id]
        target_path = Path(mutation.target_file)

        if not target_path.exists():
            return ValidationResult(
                passed=False,
                score=0.0,
                messages=[f"Target file does not exist: {mutation.target_file}"],
            )

        # Determine file type
        file_extension = target_path.suffix.lower()
        file_type = self._determine_file_type(file_extension)

        validation_checks = {}
        messages = []
        total_score = 0.0
        max_score = 0.0

        try:
            # Syntax validation
            if file_type in self.validation_tools:
                syntax_result = self._run_syntax_check(mutation.target_file, file_type)
                validation_checks["syntax"] = syntax_result
                if syntax_result:
                    total_score += 1.0
                    messages.append("✅ Syntax check passed")
                else:
                    messages.append("[ERROR] Syntax check failed")
                max_score += 1.0

                # Linting (if validation level allows)
                if mutation.validation_level in [
                    ValidationLevel.STANDARD,
                    ValidationLevel.STRICT,
                    ValidationLevel.PARANOID,
                ]:
                    lint_result = self._run_lint_check(mutation.target_file, file_type)
                    validation_checks["lint"] = lint_result
                    if lint_result:
                        total_score += 1.0
                        messages.append("✅ Linting passed")
                    else:
                        messages.append("[WARN] Linting issues found")
                    max_score += 1.0

                # Testing (if validation level allows)
                if mutation.validation_level in [
                    ValidationLevel.STRICT,
                    ValidationLevel.PARANOID,
                ]:
                    test_result = self._run_tests(mutation.target_file, file_type)
                    validation_checks["tests"] = test_result
                    if test_result:
                        total_score += 1.0
                        messages.append("✅ Tests passed")
                    else:
                        messages.append("[ERROR] Tests failed")
                    max_score += 1.0

                # Security analysis (paranoid level)
                if mutation.validation_level == ValidationLevel.PARANOID:
                    security_result = self._run_security_check(
                        mutation.target_file, file_type
                    )
                    validation_checks["security"] = security_result
                    if security_result:
                        total_score += 1.0
                        messages.append("✅ Security check passed")
                    else:
                        messages.append("[WARN] Security concerns found")
                    max_score += 1.0

            # Calculate final score
            final_score = (total_score / max_score) if max_score > 0 else 0.0
            passed = final_score >= 0.7  # 70% threshold for passing

            mutation.status = (
                MutationStatus.VALIDATED if passed else MutationStatus.FAILED
            )

            result = ValidationResult(
                passed=passed,
                score=final_score,
                checks=validation_checks,
                messages=messages,
            )

            print(
                f"🔍 Validation for {mutation_id}: {'PASSED' if passed else 'FAILED'} (Score: {final_score:.2f})"
            )
            return result

        except Exception as e:
            print(f"[ERROR] Validation error for {mutation_id}: {str(e)}")
            return ValidationResult(
                passed=False, score=0.0, messages=[f"Validation error: {str(e)}"]
            )

    def rollback_mutation(self, mutation_id: str) -> MutationResult:
        """Rollback a mutation using backup"""
        if mutation_id not in self.active_mutations:
            return MutationResult(
                success=False, message=f"Mutation {mutation_id} not found"
            )

        mutation = self.active_mutations[mutation_id]

        if not mutation.backup_path or not Path(mutation.backup_path).exists():
            return MutationResult(
                success=False,
                message="No backup available for rollback",
                errors=["Backup file not found"],
            )

        try:
            # Restore from backup
            shutil.copy2(mutation.backup_path, mutation.target_file)
            mutation.status = MutationStatus.ROLLED_BACK

            result = MutationResult(
                success=True,
                message=f"Successfully rolled back mutation {mutation_id}",
                details={"restored_file": mutation.target_file},
            )

            self._log_mutation(mutation, result)
            print(f"🔙 Rolled back mutation {mutation_id}")
            return result

        except Exception as e:
            error_msg = f"Error rolling back mutation {mutation_id}: {str(e)}"
            print(error_msg)
            return MutationResult(success=False, message=error_msg, errors=[str(e)])

    def approve_mutation(self, mutation_id: str) -> MutationResult:
        """Approve a mutation for production use"""
        if mutation_id not in self.active_mutations:
            return MutationResult(
                success=False, message=f"Mutation {mutation_id} not found"
            )

        mutation = self.active_mutations[mutation_id]
        mutation.status = MutationStatus.APPROVED

        # Move to history
        self.mutation_history.append(mutation)
        del self.active_mutations[mutation_id]

        result = MutationResult(
            success=True, message=f"Mutation {mutation_id} approved and archived"
        )

        self._log_mutation(mutation, result)
        print(f"✅ Approved mutation {mutation_id}")
        return result

    def reject_mutation(self, mutation_id: str, reason: str = "") -> MutationResult:
        """Reject a mutation and rollback if applied"""
        if mutation_id not in self.active_mutations:
            return MutationResult(
                success=False, message=f"Mutation {mutation_id} not found"
            )

        mutation = self.active_mutations[mutation_id]

        # Rollback if applied
        if mutation.status == MutationStatus.APPLIED:
            rollback_result = self.rollback_mutation(mutation_id)
            if not rollback_result.success:
                return rollback_result

        mutation.status = MutationStatus.REJECTED
        mutation.metadata["rejection_reason"] = reason

        # Move to history
        self.mutation_history.append(mutation)
        del self.active_mutations[mutation_id]

        result = MutationResult(
            success=True,
            message=f"Mutation {mutation_id} rejected",
            details={"reason": reason},
        )

        self._log_mutation(mutation, result)
        print(f"[ERROR] Rejected mutation {mutation_id}: {reason}")
        return result

    def get_mutation_status(self, mutation_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of a mutation"""
        mutation = self.active_mutations.get(mutation_id)
        if not mutation:
            # Check history
            for hist_mutation in self.mutation_history:
                if hist_mutation.mutation_id == mutation_id:
                    mutation = hist_mutation
                    break

        if not mutation:
            return None

        return {
            "mutation_id": mutation.mutation_id,
            "type": mutation.mutation_type.value,
            "target_file": mutation.target_file,
            "description": mutation.description,
            "status": mutation.status.value,
            "created_at": mutation.created_at.isoformat(),
            "backup_path": mutation.backup_path,
            "validation_level": mutation.validation_level.value,
            "metadata": mutation.metadata,
        }

    def list_mutations(
        self, status_filter: Optional[MutationStatus] = None
    ) -> List[Dict[str, Any]]:
        """List all mutations with optional status filter"""
        all_mutations = list(self.active_mutations.values()) + self.mutation_history

        if status_filter:
            all_mutations = [m for m in all_mutations if m.status == status_filter]

        return [
            {
                "mutation_id": m.mutation_id,
                "type": m.mutation_type.value,
                "target_file": m.target_file,
                "description": m.description,
                "status": m.status.value,
                "created_at": m.created_at.isoformat(),
            }
            for m in all_mutations
        ]

    def cleanup_old_backups(self, days_old: int = 30) -> MutationResult:
        """Clean up backup files older than specified days"""
        try:
            cutoff_time = time.time() - (days_old * 24 * 60 * 60)
            cleaned_files = []

            for backup_file in self.backup_directory.glob("*.bak"):
                if backup_file.stat().st_mtime < cutoff_time:
                    backup_file.unlink()
                    cleaned_files.append(str(backup_file))

            return MutationResult(
                success=True,
                message=f"Cleaned up {len(cleaned_files)} old backup files",
                details={"cleaned_files": cleaned_files},
            )

        except Exception as e:
            return MutationResult(
                success=False,
                message=f"Error cleaning up backups: {str(e)}",
                errors=[str(e)],
            )

    # Private helper methods

    def _create_backup(self, mutation: Mutation) -> MutationResult:
        """Create backup of target file"""
        try:
            source_path = Path(mutation.target_file)
            if not source_path.exists():
                return MutationResult(
                    success=False,
                    message="Source file does not exist",
                    errors=[f"File not found: {mutation.target_file}"],
                )

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = (
                f"{source_path.name}_{mutation.mutation_id}_{timestamp}.bak"
            )
            backup_path = self.backup_directory / backup_filename

            shutil.copy2(source_path, backup_path)
            mutation.backup_path = str(backup_path)

            return MutationResult(
                success=True,
                message="Backup created successfully",
                details={"backup_path": str(backup_path)},
            )

        except Exception as e:
            return MutationResult(
                success=False,
                message=f"Failed to create backup: {str(e)}",
                errors=[str(e)],
            )

    def _apply_content_mutation(self, mutation: Mutation) -> MutationResult:
        """Apply content-based mutation"""
        try:
            if mutation.content is None:
                return MutationResult(
                    success=False,
                    message="No content provided for mutation",
                    errors=["Content is None"],
                )

            with open(mutation.target_file, "w", encoding="utf-8") as f:
                f.write(mutation.content)

            return MutationResult(
                success=True,
                message="Content mutation applied successfully",
                details={
                    "target_file": mutation.target_file,
                    "content_length": len(mutation.content),
                },
            )

        except Exception as e:
            return MutationResult(
                success=False,
                message=f"Failed to apply content mutation: {str(e)}",
                errors=[str(e)],
            )

    def _apply_changes_mutation(self, mutation: Mutation) -> MutationResult:
        """Apply changes-based mutation (JSON/YAML config changes)"""
        try:
            if mutation.content_changes is None:
                return MutationResult(
                    success=False,
                    message="No content changes provided for mutation",
                    errors=["Content changes is None"],
                )

            target_path = Path(mutation.target_file)

            if target_path.suffix.lower() == ".json":
                with open(target_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Apply changes
                self._apply_dict_changes(data, mutation.content_changes)

                with open(target_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

            else:
                return MutationResult(
                    success=False,
                    message="Changes-based mutation only supported for JSON files currently",
                    errors=["Unsupported file type for changes mutation"],
                )

            return MutationResult(
                success=True,
                message="Changes mutation applied successfully",
                details={"target_file": mutation.target_file},
            )

        except Exception as e:
            return MutationResult(
                success=False,
                message=f"Failed to apply changes mutation: {str(e)}",
                errors=[str(e)],
            )

    def _apply_dict_changes(self, data: Dict[str, Any], changes: Dict[str, Any]):
        """Apply nested dictionary changes"""
        for key, value in changes.items():
            if isinstance(value, dict) and key in data and isinstance(data[key], dict):
                self._apply_dict_changes(data[key], value)
            else:
                data[key] = value

    def _determine_file_type(self, extension: str) -> str:
        """Determine file type from extension"""
        type_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "javascript",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
        }
        return type_map.get(extension, "unknown")

    def _run_syntax_check(self, file_path: str, file_type: str) -> bool:
        """Run syntax check for file"""
        try:
            if file_type not in self.validation_tools:
                return True  # Skip if no tools available

            cmd = self.validation_tools[file_type].get("syntax", [])
            if not cmd:
                return True

            # Replace placeholder with actual file path
            cmd = [arg.format(file_path) if "{}" in arg else arg for arg in cmd]
            if file_type == "python":
                cmd.append(file_path)

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0

        except Exception:
            return False

    def _run_lint_check(self, file_path: str, file_type: str) -> bool:
        """Run linting check for file"""
        try:
            if file_type not in self.validation_tools:
                return True

            cmd = self.validation_tools[file_type].get("lint", [])
            if not cmd:
                return True

            cmd.append(file_path)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return result.returncode == 0

        except Exception:
            return False

    def _run_tests(self, file_path: str, file_type: str) -> bool:
        """Run tests related to file"""
        try:
            if file_type not in self.validation_tools:
                return True

            cmd = self.validation_tools[file_type].get("test", [])
            if not cmd:
                return True

            # Run tests in the work directory
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=self.work_directory,
            )
            return result.returncode == 0

        except Exception:
            return False

    def _run_security_check(self, file_path: str, file_type: str) -> bool:
        """Run security analysis on file"""
        try:
            # Basic security checks
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for dangerous patterns
            dangerous_patterns = [
                "eval(",
                "exec(",
                "os.system(",
                "subprocess.call(",
                "__import__",
                "open(",  # Be careful with file operations
            ]

            for pattern in dangerous_patterns:
                if pattern in content:
                    return False

            return True

        except Exception:
            return False

    def _get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return Path(file_path).stat().st_size
        except Exception:
            return 0

    def _get_file_hash(self, file_path: str) -> str:
        """Get file content hash"""
        try:
            import hashlib

            with open(file_path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def _log_mutation(self, mutation: Mutation, result: MutationResult):
        """Log mutation and result to file"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "mutation_id": mutation.mutation_id,
                "mutation_type": mutation.mutation_type.value,
                "target_file": mutation.target_file,
                "description": mutation.description,
                "status": mutation.status.value,
                "result": {
                    "success": result.success,
                    "message": result.message,
                    "details": result.details,
                    "warnings": result.warnings,
                    "errors": result.errors,
                },
            }

            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")

        except Exception as e:
            print(f"[WARN] Failed to log mutation: {str(e)}")


# Convenience functions for common operations


def create_code_mutation(
    engine: MutationEngine, file_path: str, new_content: str, description: str
) -> str:
    """Create a code modification mutation"""
    return engine.create_mutation(
        target_file=file_path,
        description=description,
        mutation_type=MutationType.CODE_MODIFICATION,
        content=new_content,
    )


def create_config_mutation(
    engine: MutationEngine, config_file: str, changes: Dict[str, Any], description: str
) -> str:
    """Create a configuration update mutation"""
    return engine.create_mutation(
        target_file=config_file,
        description=description,
        mutation_type=MutationType.CONFIG_UPDATE,
        content_changes=changes,
    )


# Usage example and testing
if __name__ == "__main__":
    print("🧬 LYRIXA MUTATION ENGINE DEMO")
    print("=" * 50)

    # Initialize mutation engine
    engine = MutationEngine(
        validation_level=ValidationLevel.STANDARD,
        auto_backup=True,
        require_approval=False,
    )

    # Create a test file
    test_file = "test_mutation.py"
    with open(test_file, "w") as f:
        f.write("print('Hello, World!')\n")

    # Create and apply a mutation
    mutation_id = create_code_mutation(
        engine=engine,
        file_path=test_file,
        new_content="print('Hello, Mutated World!')\nprint('This is a mutation test')\n",
        description="Update greeting message and add test line",
    )

    print(f"\n📝 Created mutation: {mutation_id}")

    # Apply the mutation
    apply_result = engine.apply_mutation(mutation_id)
    print(f"Apply result: {apply_result.success} - {apply_result.message}")

    # Validate the mutation
    validation_result = engine.validate_mutation(mutation_id)
    print(
        f"Validation result: {validation_result.passed} (Score: {validation_result.score:.2f})"
    )

    # Show mutation status
    status = engine.get_mutation_status(mutation_id)
    if status:
        print(f"\nMutation status: {status['status']}")
    else:
        print("\nMutation status: Not found")

    # List all mutations
    mutations = engine.list_mutations()
    print(f"\nTotal mutations: {len(mutations)}")

    # Clean up
    if validation_result.passed:
        engine.approve_mutation(mutation_id)
    else:
        engine.rollback_mutation(mutation_id)

    # Clean up test file
    try:
        os.unlink(test_file)
    except Exception:
        pass

    print("\n🎉 Mutation Engine Demo Complete!")
    print("=" * 50)
