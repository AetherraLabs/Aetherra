"""
Standalone tests for SignatureVerifier (no Aetherra engine dependencies)

Run with: python test_signature_verifier_standalone.py
"""

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
import sys
import hashlib

# Add the project to path so we can import SignatureVerifier
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import directly without triggering engine initialization
import importlib.util
spec = importlib.util.spec_from_file_location(
    "signature_verifier",
    "Aetherra/aetherra_core/system/signature_verifier.py"
)
sig_verifier_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sig_verifier_module)

SignatureVerifier = sig_verifier_module.SignatureVerifier
SignatureInfo = sig_verifier_module.SignatureInfo


class TestSignatureVerifierStandalone(unittest.TestCase):
    """Standalone tests for SignatureVerifier."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_01_compute_file_hash(self):
        """Test SHA-256 hash computation."""
        test_file = self.temp_path / "test.py"
        test_file.write_bytes(b"print('Hello')\n")

        verifier = SignatureVerifier(development_mode=True)
        file_hash = verifier._compute_file_hash(str(test_file))

        # Hash should be 64 characters (SHA-256)
        self.assertEqual(len(file_hash), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in file_hash))
        print("✓ test_01_compute_file_hash PASSED")

    def test_02_empty_file_hash(self):
        """Test empty file hashing."""
        empty_file = self.temp_path / "empty.py"
        empty_file.write_bytes(b"")

        verifier = SignatureVerifier(development_mode=True)
        file_hash = verifier._compute_file_hash(str(empty_file))

        # Known SHA-256 of empty string
        expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        self.assertEqual(file_hash, expected)
        print("✓ test_02_empty_file_hash PASSED")

    def test_03_is_trusted_location(self):
        """Test trusted location detection."""
        verifier = SignatureVerifier(development_mode=True)

        self.assertTrue(verifier._is_trusted_location("Aetherra/core/test.py"))
        self.assertTrue(verifier._is_trusted_location("Aetherra/aetherra_core/test.py"))
        self.assertTrue(verifier._is_trusted_location("src/lyrixa/test.py"))
        self.assertFalse(verifier._is_trusted_location("tests/test.py"))
        self.assertFalse(verifier._is_trusted_location("demos/test.py"))
        print("✓ test_03_is_trusted_location PASSED")

    def test_04_path_based_trust_trusted_file(self):
        """Test path-based trust with trusted file."""
        trusted_dir = self.temp_path / "Aetherra" / "core"
        trusted_dir.mkdir(parents=True)
        trusted_file = trusted_dir / "test.py"
        trusted_file.write_bytes(b"content")

        verifier = SignatureVerifier(development_mode=True)
        is_valid, info = verifier.verify(str(trusted_file))

        self.assertTrue(is_valid)
        self.assertEqual(info.method, "path_based_trust")
        self.assertTrue(info.trusted_location)
        print("✓ test_04_path_based_trust_trusted_file PASSED")

    def test_05_path_based_trust_untrusted_file(self):
        """Test path-based trust with untrusted file."""
        untrusted_file = self.temp_path / "untrusted.py"
        untrusted_file.write_bytes(b"content")

        verifier = SignatureVerifier(development_mode=True)
        is_valid, info = verifier.verify(str(untrusted_file))

        self.assertFalse(is_valid)
        self.assertEqual(info.method, "path_based_trust")
        self.assertFalse(info.trusted_location)
        print("✓ test_05_path_based_trust_untrusted_file PASSED")

    def test_06_manifest_loading(self):
        """Test manifest file loading."""
        manifest_data = {
            "version": "1.0",
            "created_by": "TestSuite",
            "last_updated": datetime.utcnow().isoformat(),
            "hashes": {"test.py": "abc123"},
        }

        manifest_file = self.temp_path / "manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(manifest_data, f)

        verifier = SignatureVerifier(manifest_path=str(manifest_file))

        self.assertEqual(verifier.manifest["test.py"], "abc123")
        self.assertEqual(verifier.manifest_metadata["version"], "1.0")
        print("✓ test_06_manifest_loading PASSED")

    def test_07_manifest_verification_valid(self):
        """Test manifest verification with valid hash."""
        test_file = self.temp_path / "test.py"
        test_content = b"test content"
        test_file.write_bytes(test_content)

        # Compute hash
        file_hash = hashlib.sha256(test_content).hexdigest()

        # Create manifest
        manifest_data = {
            "version": "1.0",
            "created_by": "TestSuite",
            "last_updated": datetime.utcnow().isoformat(),
            "hashes": {"test.py": file_hash},
        }

        manifest_file = self.temp_path / "manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(manifest_data, f)

        verifier = SignatureVerifier(manifest_path=str(manifest_file))
        is_valid, info = verifier.verify(str(test_file))

        self.assertTrue(is_valid)
        self.assertTrue(info.signature_valid)
        print("✓ test_07_manifest_verification_valid PASSED")

    def test_08_manifest_verification_invalid(self):
        """Test manifest verification with invalid hash."""
        test_file = self.temp_path / "test.py"
        test_file.write_bytes(b"test content")

        # Create manifest with wrong hash
        manifest_data = {
            "version": "1.0",
            "created_by": "TestSuite",
            "last_updated": datetime.utcnow().isoformat(),
            "hashes": {"test.py": "wronghash"},
        }

        manifest_file = self.temp_path / "manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(manifest_data, f)

        verifier = SignatureVerifier(manifest_path=str(manifest_file))
        is_valid, info = verifier.verify(str(test_file))

        self.assertFalse(is_valid)
        self.assertFalse(info.signature_valid)
        print("✓ test_08_manifest_verification_invalid PASSED")

    def test_09_batch_verification(self):
        """Test batch verification."""
        files = []
        for i in range(3):
            f = self.temp_path / f"test{i}.py"
            f.write_bytes(f"content {i}".encode())
            files.append(str(f))

        verifier = SignatureVerifier(development_mode=True)
        results = verifier.verify_batch(files)

        self.assertEqual(len(results), 3)
        for file_path, (is_valid, info) in results.items():
            self.assertIsInstance(info, SignatureInfo)
        print("✓ test_09_batch_verification PASSED")

    def test_10_caching(self):
        """Test verification caching."""
        test_file = self.temp_path / "test.py"
        test_file.write_bytes(b"content")

        verifier = SignatureVerifier(development_mode=True)

        # First verification (cache miss)
        is_valid1, info1 = verifier.verify(str(test_file))

        # Second verification (cache hit)
        is_valid2, info2 = verifier.verify(str(test_file))

        # Should get same result
        self.assertEqual(is_valid1, is_valid2)
        # Timestamps should be identical (from cache)
        self.assertEqual(info1.timestamp, info2.timestamp)
        print("✓ test_10_caching PASSED")

    def test_11_clear_cache(self):
        """Test cache clearing."""
        test_file = self.temp_path / "test.py"
        test_file.write_bytes(b"content")

        verifier = SignatureVerifier(development_mode=True)
        verifier.verify(str(test_file))

        self.assertGreater(len(verifier.verification_cache), 0)
        verifier.clear_cache()
        self.assertEqual(len(verifier.verification_cache), 0)
        print("✓ test_11_clear_cache PASSED")

    def test_12_generate_manifest(self):
        """Test manifest generation."""
        python_dir = self.temp_path / "code"
        python_dir.mkdir()

        for i in range(3):
            f = python_dir / f"test{i}.py"
            f.write_bytes(f"content{i}".encode())

        output_manifest = self.temp_path / "manifest.json"

        verifier = SignatureVerifier()
        success = verifier.generate_manifest(str(python_dir), str(output_manifest))

        self.assertTrue(success)
        self.assertTrue(output_manifest.exists())

        with open(output_manifest) as f:
            manifest_data = json.load(f)

        self.assertEqual(len(manifest_data["hashes"]), 3)
        self.assertEqual(manifest_data["version"], "1.0")
        print("✓ test_12_generate_manifest PASSED")

    def test_13_audit_logging(self):
        """Test audit log generation."""
        audit_log = self.temp_path / "audit.log"
        test_file = self.temp_path / "test.py"
        test_file.write_bytes(b"content")

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
        print("✓ test_13_audit_logging PASSED")

    def test_14_normalize_manifest_key(self):
        """Test manifest key normalization."""
        verifier = SignatureVerifier()

        normalized = verifier._normalize_manifest_key("path\\to\\file.py")
        self.assertEqual(normalized, "path/to/file.py")

        normalized = verifier._normalize_manifest_key("path/to/file.py")
        self.assertEqual(normalized, "path/to/file.py")
        print("✓ test_14_normalize_manifest_key PASSED")


def run_tests():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("TASK 1.1: SIGNATURE VERIFICATION - UNIT TESTS")
    print("=" * 70 + "\n")

    suite = unittest.TestLoader().loadTestsFromTestCase(TestSignatureVerifierStandalone)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70 + "\n")

    if result.wasSuccessful():
        print("✓ ALL TESTS PASSED")
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit(run_tests())
