"""
Signature Verification Module for Aetherra Self-Incorporation System

Provides cryptographic file signature verification and management.
Supports SHA-256 hashing and digital signature verification with
fallback to path-based trust for development mode.
"""

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def _path_digest(file_path: str) -> str:
    """Return a stable digest for path correlation without storing full paths."""

    return hashlib.sha256(str(file_path).encode("utf-8")).hexdigest()


@dataclass
class SignatureInfo:
    """Information about a file's signature."""

    file_path: str
    file_hash: str
    is_valid: bool
    method: str  # "manifest", "path_based_trust", "unknown"
    trusted_location: bool = False
    signature_present: bool = False
    signature_valid: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)
    reason: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


class SignatureVerifier:
    """
    Verifies file signatures using cryptographic hashing and manifest validation.

    Supports:
    - SHA-256 file hashing for integrity verification
    - Manifest-based signature validation
    - Path-based trust fallback for development mode
    - Audit logging of all verifications
    """

    def __init__(
        self,
        manifest_path: Optional[str] = None,
        development_mode: bool = False,
        audit_log_path: Optional[str] = None,
    ):
        """
        Initialize SignatureVerifier.

        Args:
            manifest_path: Path to signature manifest JSON file
            development_mode: Enable fallback to path-based trust
            audit_log_path: Path to audit log file
        """
        self.manifest_path = manifest_path
        self.development_mode = development_mode
        self.audit_log_path = audit_log_path
        self.manifest: Dict[str, str] = {}
        self.manifest_metadata: Dict[str, Any] = {}
        self.trusted_paths = [
            "Aetherra/core",
            "Aetherra/aetherra_core",
            "src/lyrixa",
        ]
        self.verification_cache: Dict[str, SignatureInfo] = {}
        self.cache_ttl = 3600  # 1 hour cache TTL

        # Load manifest if provided
        if manifest_path:
            self._load_manifest(manifest_path)

    def _load_manifest(self, manifest_path: str) -> bool:
        """
        Load signature manifest from JSON file.

        Args:
            manifest_path: Path to manifest file

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            manifest_file = Path(manifest_path)
            if not manifest_file.exists():
                logger.warning(f"Manifest file not found: {manifest_path}")
                return False

            with open(manifest_file, encoding="utf-8") as f:
                data = json.load(f)

            # Extract metadata and hashes
            self.manifest_metadata = {
                k: v for k, v in data.items() if k in ["version", "last_updated", "created_by"]
            }
            self.manifest = data.get("hashes", {})

            logger.info(
                f"Loaded signature manifest with {len(self.manifest)} entries "
                f"(version: {self.manifest_metadata.get('version', 'unknown')})"
            )
            return True

        except (OSError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load manifest: {e}")
            return False

    def _compute_file_hash(self, file_path: str) -> str:
        """
        Compute SHA-256 hash of a file.

        Args:
            file_path: Path to file

        Returns:
            SHA-256 hexadecimal hash string

        Raises:
            IOError: If file cannot be read
        """
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except OSError:
            logger.exception(
                "Failed to compute hash for path digest %s",
                _path_digest(file_path),
            )
            raise

    def _is_trusted_location(self, file_path: str) -> bool:
        """
        Check if file is in a trusted location.

        Args:
            file_path: Path to file

        Returns:
            True if file is in trusted path, False otherwise
        """
        file_str = str(file_path).replace("\\", "/")
        # Check both relative and absolute paths
        return any(trusted in file_str for trusted in self.trusted_paths)

    def verify(self, file_path: str) -> Tuple[bool, SignatureInfo]:
        """
        Verify file signature using manifest, hash, or path-based trust.

        Verification strategy:
        1. Check manifest (if loaded)
        2. Fall back to path-based trust in development mode
        3. Return failure with details otherwise

        Args:
            file_path: Path to file to verify

        Returns:
            Tuple of (is_valid: bool, signature_info: SignatureInfo)
        """
        # Check cache first
        cache_key = str(Path(file_path).resolve())
        if cache_key in self.verification_cache:
            cached_info = self.verification_cache[cache_key]
            age = (datetime.utcnow() - cached_info.timestamp).total_seconds()
            if age < self.cache_ttl:
                return cached_info.is_valid, cached_info

        file_path = str(Path(file_path).resolve())

        try:
            # Step 1: Try manifest verification
            if self.manifest:
                return self._verify_with_manifest(file_path)

            # Step 2: Try path-based trust (development mode)
            if self.development_mode:
                return self._verify_with_path_trust(file_path)

            # Step 3: Unknown file, fail
            info = SignatureInfo(
                file_path=file_path,
                file_hash="unknown",
                is_valid=False,
                method="unknown",
                reason="No manifest loaded and development mode disabled",
            )
            self._cache_result(cache_key, info)
            self._audit_log(file_path, False, info)
            return False, info

        except Exception:
            logger.exception("Error during signature verification")
            info = SignatureInfo(
                file_path=file_path,
                file_hash="error",
                is_valid=False,
                method="error",
                reason="verification_error",
            )
            self._cache_result(cache_key, info)
            self._audit_log(file_path, False, info)
            return False, info

    def _verify_with_manifest(self, file_path: str) -> Tuple[bool, SignatureInfo]:
        """
        Verify file against manifest hashes.

        Args:
            file_path: Path to file

        Returns:
            Tuple of (is_valid, SignatureInfo)
        """
        try:
            file_hash = self._compute_file_hash(file_path)

            # Check if file is in manifest - try multiple key formats
            manifest_key = self._normalize_manifest_key(file_path)
            expected_hash = self.manifest.get(manifest_key)

            # If not found, try just the filename
            if expected_hash is None:
                filename_only = Path(file_path).name
                expected_hash = self.manifest.get(filename_only)

            if expected_hash is None:
                # File not in manifest (new file?)
                info = SignatureInfo(
                    file_path=file_path,
                    file_hash=file_hash,
                    is_valid=False,
                    method="manifest",
                    signature_present=False,
                    reason="File not found in signature manifest",
                    details={"computed_hash": file_hash},
                )
            elif file_hash == expected_hash:
                # Hash match!
                info = SignatureInfo(
                    file_path=file_path,
                    file_hash=file_hash,
                    is_valid=True,
                    method="manifest",
                    signature_present=True,
                    signature_valid=True,
                    reason="File hash matches manifest",
                    details={"manifest_hash": expected_hash},
                )
            else:
                # Hash mismatch - file was modified
                info = SignatureInfo(
                    file_path=file_path,
                    file_hash=file_hash,
                    is_valid=False,
                    method="manifest",
                    signature_present=True,
                    signature_valid=False,
                    reason="File hash does not match manifest",
                    details={
                        "computed_hash": file_hash,
                        "manifest_hash": expected_hash,
                    },
                )

            cache_key = file_path
            self._cache_result(cache_key, info)
            self._audit_log(file_path, info.is_valid, info)
            return info.is_valid, info

        except Exception:
            logger.exception("Manifest verification error")
            info = SignatureInfo(
                file_path=file_path,
                file_hash="error",
                is_valid=False,
                method="manifest",
                reason="manifest_verification_error",
            )
            self._cache_result(file_path, info)
            self._audit_log(file_path, False, info)
            return False, info

    def _verify_with_path_trust(self, file_path: str) -> Tuple[bool, SignatureInfo]:
        """
        Verify file using path-based trust (development mode).

        Args:
            file_path: Path to file

        Returns:
            Tuple of (is_valid, SignatureInfo)
        """
        trusted = self._is_trusted_location(file_path)

        try:
            file_hash = self._compute_file_hash(file_path)
        except OSError:
            file_hash = "error"

        info = SignatureInfo(
            file_path=file_path,
            file_hash=file_hash,
            is_valid=trusted,
            method="path_based_trust",
            trusted_location=trusted,
            signature_present=False,
            reason="Development mode: file is in trusted path"
            if trusted
            else "File is not in trusted path",
            details={"trusted_paths": self.trusted_paths},
        )

        cache_key = file_path
        self._cache_result(cache_key, info)
        self._audit_log(file_path, trusted, info)
        return trusted, info

    def _normalize_manifest_key(self, file_path: str) -> str:
        """
        Normalize file path for manifest lookup.

        Args:
            file_path: Path to file

        Returns:
            Normalized manifest key
        """
        # Convert to relative path from repo root if possible
        path = Path(file_path)
        # Use name only for simplicity in lookup
        normalized = str(path).replace("\\", "/")
        # If full path, try to extract just the relative part
        # For now, support both full paths and just filenames
        return normalized

    def _cache_result(self, cache_key: str, info: SignatureInfo) -> None:
        """Cache verification result."""
        self.verification_cache[cache_key] = info

    def _audit_log(self, file_path: str, is_valid: bool, info: SignatureInfo) -> None:
        """
        Log verification to audit log.

        Args:
            file_path: Path to file
            is_valid: Whether verification passed
            info: SignatureInfo with details
        """
        if not self.audit_log_path:
            return

        try:
            audit_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "file_path": Path(file_path).name,
                "file_path_hash": _path_digest(file_path),
                "is_valid": is_valid,
                "method": info.method,
                "reason": info.reason,
            }

            with open(self.audit_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(audit_entry) + "\n")

        except OSError as e:
            logger.error(f"Failed to write audit log: {e}")

    def verify_batch(self, file_paths: list[str]) -> Dict[str, Tuple[bool, SignatureInfo]]:
        """
        Verify multiple files efficiently.

        Args:
            file_paths: List of file paths to verify

        Returns:
            Dictionary mapping file_path -> (is_valid, SignatureInfo)
        """
        results = {}
        for file_path in file_paths:
            results[file_path] = self.verify(file_path)
        return results

    def generate_manifest(self, root_dir: str, output_path: str) -> bool:
        """
        Generate signature manifest for all files in a directory.

        Args:
            root_dir: Root directory to scan
            output_path: Path to write manifest

        Returns:
            True if successful, False otherwise
        """
        try:
            hashes = {}
            root_path = Path(root_dir)

            # Scan all Python files
            for py_file in root_path.rglob("*.py"):
                # Skip common dirs
                if any(
                    skip in str(py_file)
                    for skip in [".venv", "__pycache__", ".git", "dist-packages"]
                ):
                    continue

                file_hash = self._compute_file_hash(str(py_file))
                relative_path = py_file.relative_to(root_path)
                hashes[str(relative_path).replace("\\", "/")] = file_hash

            manifest_data = {
                "version": "1.0",
                "created_by": "Aetherra SignatureVerifier",
                "last_updated": datetime.utcnow().isoformat(),
                "hashes": hashes,
            }

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(manifest_data, f, indent=2)

            logger.info(f"Generated manifest with {len(hashes)} files at {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to generate manifest: {e}")
            return False

    def clear_cache(self) -> None:
        """Clear verification cache."""
        self.verification_cache.clear()
