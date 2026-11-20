# Release signing identity

The project owner approved this dedicated Ed25519 release identity on
2026-11-19 after no existing release key or public-key record could be located.
This does not establish whether a historical key existed elsewhere.

- Public key: `release_signing_ed25519.pub` (raw public bytes, hex encoded).
- SHA-256 of the raw public key:
  `0eba4cc63f130a4c42d9d9f8161c41267da8120f10c389d719b6b8d08f81830f`.
- Private seed: the GitHub Actions secret `AETHERRA_RELEASE_PRIVKEY`.
- Local recovery copy: Windows DPAPI CurrentUser encryption outside the repository,
  under the owner's local application data. It depends on that Windows profile;
  an encrypted copy alone is not a portable backup.

The API-store Master Key (`AETHERRA_KEYS_MASTER`, Fernet) is unrelated and must
not be reused for release signing. Never commit a private seed, even encrypted.
CI verifies the manifest signature against this public key; changing the secret
to another identity cannot pass. Key replacement requires owner approval and a
reviewed public-key change. See [key rotation](../docs/KEY_ROTATION.md).
