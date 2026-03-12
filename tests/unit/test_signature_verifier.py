"""
Unit tests for Signature Verification Module

Tests cover:
- File hashing (SHA-256)
- Manifest loading and validation
- Path-based trust verification
- Batch verification
- Manifest generation
- Caching behavior
- Error handling
- Audit logging
"""

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from Aetherra.aetherra_core.system.signature_verifier import (
    SignatureInfo,
    SignatureVerifier,
)


class TestSignatureVerifier(unittest.TestCase):
    """Test cases for SignatureVerifier class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.test_file = self.temp_path / "test_file.py"
        self.test_content = b"print('Hello, World!')\n"
        self.test_file.write_bytes(self.test_content)

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_compute_file_hash(self):
        """Test SHA-256 hash computation."""
        verifier = SignatureVerifier(development_mode=True)
        file_hash = verifier._compute_file_hash(str(self.test_file))

        # Verify hash is correct length (64 hex chars for SHA-256)
        self.assertEqual(len(file_hash), 64)
        # Verify hash is hexadecimal
        self.assertTrue(all(c in "0123456789abcdef" for c in file_hash))

    def test_compute_file_hash_nonexistent_file(self):
        """Test hash computation with nonexistent file."""
        verifier = SignatureVerifier()
        with self.assertRaises(IOError):
            verifier._compute_file_hash("nonexistent_file.py")

    def test_is_trusted_location(self):
        """Test trusted location detection."""
        verifier = SignatureVerifier(development_mode=True)

        # Test trusted paths
        self.assertTrue(verifier._is_trusted_location("Aetherra/core/test.py"))
        self.assertTrue(verifier._is_trusted_location("Aetherra/aetherra_core/test.py"))
        self.assertTrue(verifier._is_trusted_location("src/lyrixa/test.py"))

        # Test untrusted paths
        self.assertFalse(verifier._is_trusted_location("tests/test.py"))
        self.assertFalse(verifier._is_trusted_location("demos/demo.py"))

    def test_path_based_trust_verification(self):
        """Test path-based trust verification."""
        verifier = SignatureVerifier(development_mode=True)

        # Test trusted location
        trusted_file = "Aetherra/core/trusted.py"
        is_valid, info = verifier.verify(trusted_file)

        # Should fail because file doesn't exist, but within trusted path logic
        # In reality we need to test with actual files
        self.assertIsInstance(info, SignatureInfo)

    def test_path_based_trust_with_existing_file_trusted(self):
        """Test path-based trust with actual trusted file."""
        # Create a file in a trusted-looking path
        trusted_dir = self.temp_path / "Aetherra" / "core"
        trusted_dir.mkdir(parents=True)
        trusted_file = trusted_dir / "test.py"
        trusted_file.write_bytes(self.test_content)

        verifier = SignatureVerifier(development_mode=True)
        is_valid, info = verifier.verify(str(trusted_file))

        self.assertTrue(is_valid)
        self.assertEqual(info.method, "path_based_trust")
        self.assertTrue(info.trusted_location)

    def test_path_based_trust_with_existing_file_untrusted(self):
        """Test path-based trust with untrusted file."""
        untrusted_file = self.temp_path / "untrusted.py"
        untrusted_file.write_bytes(self.test_content)

        verifier = SignatureVerifier(development_mode=True)
        is_valid, info = verifier.verify(str(untrusted_file))

        self.assertFalse(is_valid)
        self.assertEqual(info.method, "path_based_trust")
        self.assertFalse(info.trusted_location)

    def test_manifest_loading(self):
        """Test manifest file loading."""
        manifest_data = {
            "version": "1.0",
            "created_by": "TestSuite",
            "last_updated": datetime.utcnow().isoformat(),
            "hashes": {
                "test.py": "abc123def456789",
            },
        }

        manifest_file = self.temp_path / "manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(manifest_data, f)

        verifier = SignatureVerifier(manifest_path=str(manifest_file))

        self.assertEqual(verifier.manifest["test.py"], "abc123def456789")
        self.assertEqual(verifier.manifest_metadata["version"], "1.0")

    def test_manifest_loading_nonexistent(self):
        """Test manifest loading with nonexistent file."""
        verifier = SignatureVerifier(manifest_path="nonexistent.json")

        self.assertEqual(len(verifier.manifest), 0)

    def test_manifest_verification_valid(self):
        """Test manifest verification with valid hash."""
        # Create a test file and compute its hash
        test_file = self.temp_path / "test.py"
        test_file.write_bytes(b"test content")

        verifier = SignatureVerifier(development_mode=True)
        file_hash = verifier._compute_file_hash(str(test_file))

        # Create manifest with correct hash
        manifest_data = {
            "version": "1.0",
            "created_by": "TestSuite",
            "last_updated": datetime.utcnow().isoformat(),
            "hashes": {
                str(test_file.relative_to(self.temp_path)).replace(
                    "\\", "/"
                ): file_hash,
            },
        }

        manifest_file = self.temp_path / "manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(manifest_data, f)

        # Create new verifier with manifest
        verifier2 = SignatureVerifier(manifest_path=str(manifest_file))
        is_valid, info = verifier2.verify(str(test_file))

        self.assertTrue(is_valid)
        self.assertEqual(info.method, "manifest")
        self.assertTrue(info.signature_valid)

    def test_manifest_verification_invalid_hash(self):
        """Test manifest verification with mismatched hash."""
        test_file = self.temp_path / "test.py"
        test_file.write_bytes(b"test content")

        # Create manifest with wrong hash
        manifest_data = {
            "version": "1.0",
            "created_by": "TestSuite",
            "last_updated": datetime.utcnow().isoformat(),
            "hashes": {
                "test.py": "wronghash1234567890abcdef",
            },
        }

        manifest_file = self.temp_path / "manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(manifest_data, f)

        verifier = SignatureVerifier(manifest_path=str(manifest_file))
        is_valid, info = verifier.verify(str(test_file))

        self.assertFalse(is_valid)
        self.assertFalse(info.signature_valid)

    def test_manifest_verification_file_not_in_manifest(self):
        """Test manifest verification when file not in manifest."""
        test_file = self.temp_path / "test.py"
        test_file.write_bytes(b"test content")

        # Create empty manifest
        manifest_data = {
            "version": "1.0",
            "created_by": "TestSuite",
            "last_updated": datetime.utcnow().isoformat(),
            "hashes": {},
        }

        manifest_file = self.temp_path / "manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(manifest_data, f)

        verifier = SignatureVerifier(manifest_path=str(manifest_file))
        is_valid, info = verifier.verify(str(test_file))

        self.assertFalse(is_valid)
        self.assertFalse(info.signature_present)

    def test_batch_verification(self):
        """Test batch verification of multiple files."""
        # Create multiple test files
        files = []
        for i in range(3):
            test_file = self.temp_path / f"test{i}.py"
            test_file.write_bytes(f"content {i}".encode())
            files.append(str(test_file))

        verifier = SignatureVerifier(development_mode=True)
        results = verifier.verify_batch(files)

        self.assertEqual(len(results), 3)
        for file_path, (is_valid, info) in results.items():
            self.assertIsInstance(info, SignatureInfo)

    def test_caching_behavior(self):
        """Test verification caching."""
        test_file = self.temp_path / "test.py"
        test_file.write_bytes(b"test content")

        verifier = SignatureVerifier(development_mode=True)

        # First verification (cache miss)
        is_valid1, info1 = verifier.verify(str(test_file))

        # Second verification (cache hit)
        is_valid2, info2 = verifier.verify(str(test_file))

        # Results should be identical
        self.assertEqual(is_valid1, is_valid2)
        # Timestamps should be the same (from cache)
        self.assertEqual(info1.timestamp, info2.timestamp)

    def test_clear_cache(self):
        """Test cache clearing."""
        test_file = self.temp_path / "test.py"
        test_file.write_bytes(b"test content")

        verifier = SignatureVerifier(development_mode=True)
        verifier.verify(str(test_file))
        self.assertGreater(len(verifier.verification_cache), 0)

        verifier.clear_cache()
        self.assertEqual(len(verifier.verification_cache), 0)

    def test_generate_manifest(self):
        """Test manifest generation."""
        # Create multiple test files
        python_dir = self.temp_path / "python_code"
        python_dir.mkdir()

        for i in range(3):
            test_file = python_dir / f"test{i}.py"
            test_file.write_bytes(f"content {i}".encode())

        output_manifest = self.temp_path / "generated_manifest.json"

        verifier = SignatureVerifier(development_mode=True)
        success = verifier.generate_manifest(str(python_dir), str(output_manifest))

        self.assertTrue(success)
        self.assertTrue(output_manifest.exists())

        # Verify manifest content
        with open(output_manifest) as f:
            manifest_data = json.load(f)

        self.assertEqual(manifest_data["version"], "1.0")
        self.assertEqual(len(manifest_data["hashes"]), 3)

    def test_generate_manifest_excludes_venv(self):
        """Test that manifest generation excludes virtual env."""
        # Create directories including venv
        venv_dir = self.temp_path / ".venv"
        venv_dir.mkdir()
        venv_file = venv_dir / "lib.py"
        venv_file.write_bytes(b"venv content")

        code_file = self.temp_path / "code.py"
        code_file.write_bytes(b"code content")

        output_manifest = self.temp_path / "manifest.json"

        verifier = SignatureVerifier()
        verifier.generate_manifest(str(self.temp_path), str(output_manifest))

        with open(output_manifest) as f:
            manifest_data = json.load(f)

        # Should include code.py but not venv files
        self.assertEqual(len(manifest_data["hashes"]), 1)
        self.assertIn("code.py", list(manifest_data["hashes"].keys())[0])

    def test_audit_logging(self):
        """Test audit log generation."""
        audit_log = self.temp_path / "audit.log"
        test_file = self.temp_path / "test.py"
        test_file.write_bytes(b"test content")

        verifier = SignatureVerifier(
            development_mode=True, audit_log_path=str(audit_log)
        )
        verifier.verify(str(test_file))

        self.assertTrue(audit_log.exists())

        with open(audit_log) as f:
            log_entry = json.loads(f.read().strip())

        self.assertIn("timestamp", log_entry)
        self.assertIn("file_path", log_entry)
        self.assertIn("is_valid", log_entry)
        self.assertIn("method", log_entry)

    def test_normalize_manifest_key(self):
        """Test manifest key normalization."""
        verifier = SignatureVerifier()

        # Test Windows path conversion
        normalized = verifier._normalize_manifest_key("path\\to\\file.py")
        self.assertEqual(normalized, "path/to/file.py")

        # Test Unix path (should stay same)
        normalized = verifier._normalize_manifest_key("path/to/file.py")
        self.assertEqual(normalized, "path/to/file.py")

    def test_development_mode_disabled(self):
        """Test verification when development mode is disabled."""
        test_file = self.temp_path / "untrusted.py"
        test_file.write_bytes(b"test content")

        # Create verifier without manifest and without dev mode
        verifier = SignatureVerifier(development_mode=False)
        is_valid, info = verifier.verify(str(test_file))

        self.assertFalse(is_valid)
        self.assertEqual(info.method, "unknown")

    def test_signature_info_dataclass(self):
        """Test SignatureInfo dataclass."""
        info = SignatureInfo(
            file_path="/path/to/file.py",
            file_hash="abc123",
            is_valid=True,
            method="manifest",
            reason="Test reason",
        )

        self.assertEqual(info.file_path, "/path/to/file.py")
        self.assertEqual(info.file_hash, "abc123")
        self.assertTrue(info.is_valid)
        self.assertEqual(info.method, "manifest")
        self.assertIsInstance(info.timestamp, datetime)


class TestSignatureVerifierEdgeCases(unittest.TestCase):
    """Edge case tests for SignatureVerifier."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_large_file_hashing(self):
        """Test hashing of large files."""
        large_file = self.temp_path / "large.py"
        # Create a 10MB file
        large_file.write_bytes(b"x" * (10 * 1024 * 1024))

        verifier = SignatureVerifier(development_mode=True)
        file_hash = verifier._compute_file_hash(str(large_file))

        self.assertEqual(len(file_hash), 64)

    def test_empty_file_hashing(self):
        """Test hashing of empty files."""
        empty_file = self.temp_path / "empty.py"
        empty_file.write_bytes(b"")

        verifier = SignatureVerifier(development_mode=True)
        file_hash = verifier._compute_file_hash(str(empty_file))

        # SHA256 of empty file is known
        self.assertEqual(
            file_hash,
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )

    def test_symlink_handling(self):
        """Test handling of symbolic links (if supported)."""
        # This test is OS-dependent, so we'll skip if symlinks not supported
        try:
            target_file = self.temp_path / "target.py"
            target_file.write_bytes(b"target content")

            symlink_file = self.temp_path / "symlink.py"
            symlink_file.symlink_to(target_file)

            verifier = SignatureVerifier(development_mode=True)
            file_hash = verifier._compute_file_hash(str(symlink_file))

            self.assertEqual(len(file_hash), 64)
        except (OSError, NotImplementedError):
            # Symlinks not supported on this system
            self.skipTest("Symlinks not supported on this system")


if __name__ == "__main__":
    unittest.main()
