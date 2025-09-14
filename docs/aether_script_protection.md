# Aether Script Protection and Signing

Aether Script is an Aetherra Labs creation. To protect its integrity, we support optional source signing and strict verification.

## Goals

- Ensure .aether sources can be verified before execution
- Keep files portable and human-readable
- Avoid heavy dependencies by default; allow stronger crypto later

## How it works

- Scripts may include a first-line signature header:
  `# @signature: <hex>`
- The signature is an HMAC-SHA256 over the body (all lines after the header)
- The secret is read from the API key store under `aether_script_signing_secret`; if missing, a dev fallback secret is used (replace in production)

## Enforcing verification

- Set `AETHERRA_SCRIPT_VERIFY_STRICT=1` to require a valid signature header during execution.
- The interpreter will reject unsigned or tampered scripts with a clear error.

## Developer usage

Python helpers in `Aetherra/security/script_signing.py`:

- `embed_signature(text) -> str` adds/updates the signature header for a given body
- `verify_embedded_signature(text) -> (ok, reason)` checks the header against the body

## Migration path

- Start with HMAC signing for simplicity.
- Optionally add ed25519 signing (PyNaCl) later for asymmetric verification.

## Notes

- Do not commit production secrets. Use the API keys store (`Aetherra.security.api_keys`) to set `aether_script_signing_secret`.
- Keep the signature header as the first line.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

