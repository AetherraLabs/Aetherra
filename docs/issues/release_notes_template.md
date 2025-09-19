# Release Notes — Aetherra OS — Self-Incorporation v1

Date: YYYY-MM-DD

## Summary

A kernel-orchestrated system that sees, understands, and safely integrates 100% of its codebase at boot and during operation.
It includes a quarantine workflow, audit/ethics ledger, strict security gates (.aether HMAC + plugin ed25519), and hot-swap/rollback support.
The result is a Self-Hosting Cognitive Organism: no dark code, continuous evolution, safety by default.

## Highlights

- /api/selfinc/status + Prom metrics
- Strict mode gates for signatures and capabilities
- Quarantine → Escalate → Release workflow with UI hooks
- HMR swap with auto-rollback and audit
- Night cycle deep checks and ethics delta report
- New CLI: aether selfinc {scan|plan|apply|rollback|audit}
- Integrator Spec→Tests gate
- Ethics & Audit append-only ledger
- Hub policy alignment with tokens/claims
- Lyrixa Self-Incorporation panel

## Upgrade Notes

- New env flags: `AETHERRA_SELFINC_STRICT`, `AETHERRA_SELFINC_*`, `AETHERRA_PASSIVE_*`
- Ensure policy bootstrap updated; re-run Bootstrap Policy Files task if needed

## Compatibility

- Backward compatible by default; strict mode is opt-in via env

## Deprecations (if any)

- N/A

## Known Issues (if any)

- N/A

## Acknowledgements

- Contributors and reviewers
