"""Exercise the real release signer and verifier with a public test-vector seed."""

# Standard library imports
import json
import os
import subprocess
import sys
from pathlib import Path

# Third party imports
import pytest

ROOT = Path(__file__).resolve().parents[2]
# RFC 8032 test vector 1; never a production credential.
SEED = "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"
PUBLIC = "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"


def run_tool(name, *args, seed=None):
    env = os.environ.copy()
    env.pop("AETHERRA_RELEASE_PRIVKEY", None)
    if seed is not None:
        env["AETHERRA_RELEASE_PRIVKEY"] = seed
    return subprocess.run(
        [sys.executable, str(ROOT / "tools" / name), *map(str, args)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


@pytest.fixture
def signed_manifest(tmp_path):
    (tmp_path / "artifact.txt").write_text("synthetic release\n", encoding="utf-8")
    manifest = tmp_path / "release-manifest.json"
    result = run_tool(
        "sign_release_manifest.py",
        "--dist",
        tmp_path,
        "--version",
        "0.0.0-test",
        "--output",
        manifest,
        seed=SEED,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return manifest


def verify(manifest):
    return run_tool(
        "verify_release_manifest.py",
        "--manifest",
        manifest,
        "--dist",
        manifest.parent,
        "--pubkey",
        PUBLIC,
    )


def test_manifest_does_not_disclose_private_seed(signed_manifest):
    assert SEED[:8] not in signed_manifest.read_text(encoding="utf-8")


def test_generated_signature_verifies(signed_manifest):
    result = verify(signed_manifest)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "signature valid" in result.stdout


def test_signed_metadata_tampering_fails(signed_manifest):
    manifest = json.loads(signed_manifest.read_text(encoding="utf-8"))
    manifest["signing"]["tool_version"] = "tampered"
    signed_manifest.write_text(json.dumps(manifest), encoding="utf-8")
    assert verify(signed_manifest).returncode != 0


def test_required_public_key_rejects_missing_signature(signed_manifest):
    signed_manifest.with_suffix(".json.sig").unlink()
    assert verify(signed_manifest).returncode != 0


@pytest.mark.parametrize("public_key", ["", " ", "not-a-key", "00" * 32])
def test_explicit_invalid_public_key_cannot_skip_verification(
    signed_manifest, public_key
):
    result = run_tool(
        "verify_release_manifest.py",
        "--manifest",
        signed_manifest,
        "--dist",
        signed_manifest.parent,
        "--pubkey",
        public_key,
    )
    assert result.returncode != 0


def test_invalid_private_key_fails_without_unsigned_output(tmp_path):
    manifest = tmp_path / "release-manifest.json"
    result = run_tool(
        "sign_release_manifest.py",
        "--dist",
        tmp_path,
        "--version",
        "0.0.0-test",
        "--output",
        manifest,
        seed="invalid-private-seed",
    )
    assert result.returncode != 0
    assert not manifest.exists()
    assert "invalid-private-seed" not in result.stdout + result.stderr
