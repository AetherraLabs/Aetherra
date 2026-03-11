"""Standalone tests for tools/verify_phase5_manifest_policy.py.

Run with:
    python test_phase5_manifest_policy_standalone.py
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.verify_phase5_manifest_policy import verify_policy


class TestPhase5ManifestPolicy(unittest.TestCase):
    def test_verify_policy_passes_without_signature_requirement(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = root / "release_manifest.json"
            manifest.write_text("{}", encoding="utf-8")

            summary = root / "summary.json"
            summary.write_text(
                json.dumps(
                    {
                        "release_manifest": {
                            "enabled": True,
                            "path": str(manifest),
                            "step": {"ok": True},
                            "signature_exists": False,
                            "signature_sha256": None,
                        }
                    }
                ),
                encoding="utf-8",
            )

            ok, reason = verify_policy(summary, require_signature=False)
            self.assertTrue(ok)
            self.assertEqual(reason, "ok")

    def test_verify_policy_fails_when_signature_required_but_missing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = root / "release_manifest.json"
            manifest.write_text("{}", encoding="utf-8")

            summary = root / "summary.json"
            summary.write_text(
                json.dumps(
                    {
                        "release_manifest": {
                            "enabled": True,
                            "path": str(manifest),
                            "step": {"ok": True},
                            "signature_exists": False,
                            "signature_sha256": None,
                        }
                    }
                ),
                encoding="utf-8",
            )

            ok, reason = verify_policy(summary, require_signature=True)
            self.assertFalse(ok)
            self.assertEqual(reason, "release_manifest_signature_missing")

    def test_verify_policy_passes_with_signature_requirement(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = root / "release_manifest.json"
            manifest.write_text("{}", encoding="utf-8")

            signature = root / "release_manifest.json.sig"
            signature.write_text("deadbeef", encoding="utf-8")

            summary = root / "summary.json"
            summary.write_text(
                json.dumps(
                    {
                        "release_manifest": {
                            "enabled": True,
                            "path": str(manifest),
                            "step": {"ok": True},
                            "signature_exists": True,
                            "signature_sha256": "abc123",
                            "signature_path": str(signature),
                        }
                    }
                ),
                encoding="utf-8",
            )

            ok, reason = verify_policy(summary, require_signature=True)
            self.assertTrue(ok)
            self.assertEqual(reason, "ok")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestPhase5ManifestPolicy)
    total = suite.countTestCases()
    print(f"Running {total} phase-5 manifest-policy tests...")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"Result: {total - len(result.failures) - len(result.errors)}/{total} passed")
    sys.exit(0 if result.wasSuccessful() else 1)
