# Aetherra Threat Model (Alpha)

> Maintained and officially operated by **Aetherra Labs**. **Powered by Aetherra Labs.**

## 1. Scope & Method

Methodology: Lightweight hybrid STRIDE + Asset/Attack Surface review focused on the Alpha release footprint.

In-Scope Components:

- Kernel / Orchestrator (task queue, hot module reload)
- Memory System (vector / persistent stores)
- Plugin & Workflow Subsystems (discovery, execution, signatures)
- Hub / HTTP surfaces (trainer, metrics, registration endpoints)
- Signing & Provenance (release manifest, plugin hashing, SPDX)
- Telemetry / Metrics Export

Out-of-Scope (Alpha):

- Multi-tenant isolation guarantees
- Formal sandboxing of untrusted Python (planned hardening)
- Full supply chain attestation (SLSA provenance)

## 2. Assets & Security Properties

| Asset                              | Security Properties (Desired)                    | Notes                                                           |
| ---------------------------------- | ------------------------------------------------ | --------------------------------------------------------------- |
| Signed Release Artifacts           | Integrity, Authenticity                          | Manifest + optional Ed25519 signature (alpha)                   |
| Workflows (.aether)                | Integrity, Non‑tampering                         | Signature verification (strict mode)                            |
| Plugins (local & aetherplug)       | Integrity, Source Attribution                    | Hashes computed locally (alpha); elevation policy pending       |
| Memory Databases                   | Confidentiality (basic), Integrity, Availability | No encryption at rest yet; access limited by process boundaries |
| Steward Keys                       | Confidentiality, Non-repudiation                 | Single key pair currently; rotation appendix defines cadence    |
| SBOM & Lock File                   | Integrity, Reproducibility                       | Lock drift gate + manifest provenance hash                      |
| Telemetry (metrics)                | Integrity, Availability                          | No sensitive PII expected                                       |
| Configuration / Secrets (env vars) | Confidentiality                                  | Rely on host OS protections                                     |

## 3. Threat Actors

| Actor                     | Capability | Motivation                            | Examples                                        |
| ------------------------- | ---------- | ------------------------------------- | ----------------------------------------------- |
| Opportunistic Attacker    | Low–Med    | Arbitrary compromise                  | Supply chain dependency injection               |
| Malicious Contributor     | Med        | Backdoor / persistence                | Craft PR with hidden payload                    |
| Key Exfiltrator           | Med–High   | Sign rogue artifacts                  | CI secret theft                                 |
| Plugin Author (Untrusted) | Low–Med    | Escalate privileges / data access     | Malformed plugin code exploiting shared process |
| Supply Chain Attacker     | High       | Dependency compromise / typosquatting | Fake transitive package                         |

## 4. Attack Surfaces & Vectors

| Surface                 | Example Vectors              | Current Mitigations                     | Gaps / Planned                                           |
| ----------------------- | ---------------------------- | --------------------------------------- | -------------------------------------------------------- |
| Release Packaging       | Manifest tamper              | Hash + optional signature               | Multi-sig + transparency log (future)                    |
| Dependency Graph        | Typosquatting, vuln packages | Lock file + vuln scan (pip-audit / osv) | Automated allowlist / license deny list (planned)        |
| Plugins                 | Malicious code exec          | Hash capture, optional signing stub     | Process isolation / sandboxing, trust tiers enforcement  |
| Hot Module Reload (HMR) | Load untrusted module        | Allowed source gating, audit            | Strong policy on allowed list + signature check (future) |
| Workflows (.aether)     | Tampering / chain injection  | Signing & strict mode quarantine        | Provenance chain, revocation list (future)               |
| Memory System           | Corrupt / exfiltrate DB      | In-process access only                  | Encryption at rest, RBAC (future)                        |
| Hub HTTP API            | DoS / malformed requests     | Timeouts, limited surfaces              | Auth / rate limiting (future)                            |
| Telemetry Submission    | Poison metrics               | Local only (no remote push)             | Authenticated remote export (future)                     |

## 5. STRIDE Summary

| Category               | Representative Risk                 | Status                                             |
| ---------------------- | ----------------------------------- | -------------------------------------------------- |
| Spoofing               | Fake plugin claims official status  | Mitigation partial (hash + policy doc)             |
| Tampering              | Modified workflow or artifact       | Hash + signature (alpha)                           |
| Repudiation            | Disputed release origin             | Signature (single key) – multi-sig pending         |
| Information Disclosure | Memory DB introspection             | Minimal; no encryption yet (accepted)              |
| Denial of Service      | Plugin infinite loop / slow invoke  | Timeouts + future metrics assertions               |
| Elevation of Privilege | Malicious plugin touching internals | No sandbox; trust tier & future isolation required |

## 6. Current Mitigation Matrix

| Control                   | Implemented | Strength | Notes                                 |
| ------------------------- | ----------- | -------- | ------------------------------------- |
| SPDX + License Headers    | Yes         | High     | Enforces provenance & legal clarity   |
| Release Manifest Hashing  | Yes         | High     | Full artifact enumeration             |
| Optional Ed25519 Signing  | Yes         | Medium   | Single key only                       |
| Lock Drift Enforcement    | Yes         | High     | CI gate via `enforce_lock_sync.py`    |
| Vulnerability Scanning    | Yes         | Medium   | Dependent on local tools availability |
| License Inventory         | Yes         | Low      | Non-enforcing baseline                |
| Plugin Content Hashing    | Yes         | Medium   | Integrity only; no policy yet         |
| Workflow Signature Verify | Yes         | Medium   | Strict mode gating                    |
| Failure Injection Tests   | Partial     | Medium   | Assertions expansion pending          |
| HMR Audit & Counters      | Yes         | Medium   | No signature on module sources yet    |

## 6A. Newly Added Supply Chain Controls (0.1.0-alpha.2)

Recent hardening additions integrated into quality gates:

| Control                          | Description                                                                      | Threats Mitigated                                         | Residual Gap                                  |
| -------------------------------- | -------------------------------------------------------------------------------- | --------------------------------------------------------- | --------------------------------------------- |
| License Trend Gating             | Enforces non-regression: UNKNOWN delta > tolerance or ABS_MAX breach fails gates | Silent license drift, supply chain opacity                | Does not yet deny specific SPDX IDs (planned) |
| Overrides Lifecycle + Prune Tool | Temporary SPDX overrides w/ stale detection & pruning script                     | Accumulating stale overrides masking upstream fixes       | Manual review still required                  |
| SBOM Generation (JSON)           | Deterministic dependency inventory artifact each gate run                        | Tampered dependency inclusion, unverifiable builds        | Not yet signed / attested                     |
| Packaging Smoke Test             | Build/install sanity ensures wheel reproducibility and import viability          | Shipping broken artifact, unnoticed packaging regressions | No multi-platform matrix yet                  |
| Vulnerability Scan Hook          | Optional pip-audit/osv scan (best-effort) gating high severity                   | Known CVE inclusion at release time                       | Tool availability variance                    |
| Prometheus License Metrics       | Gauges export current UNKNOWN count & trend delta                                | Lack of observability / delayed detection                 | Alerting pipeline not wired yet               |

These controls close previously identified gaps in Sections 4 & 6 (Dependency Graph, Release Packaging). Supply chain roadmap items (multi-sig, attestations, deny list) remain scheduled for Beta (see Roadmap Controls & Gap Analysis file).

## 7. Residual Risks (Alpha Accepted)

- No runtime sandbox: Plugins execute with kernel process privileges.
- Single signing key: Compromise = total release forgery risk until rotation executed.
- Lack of formal dependency provenance (no attestations / in-toto).
- Memory content unencrypted at rest.
- Limited network policy enforcement.

## 8. Roadmap Controls

| Control                                | Target Phase | Notes                              |
| -------------------------------------- | ------------ | ---------------------------------- |
| Multi-signature Release (threshold)    | Beta         | Steward + Build Attestor           |
| Transparency Log (Merkle)              | Beta         | Append-only manifest index         |
| Plugin Sandboxing (subprocess / WASM)  | Beta         | Policy-driven isolation            |
| License Deny / Policy Gate             | Beta         | Hard fail on disallowed / UNKNOWN  |
| SBOM Provenance Attestation (SLSA L2+) | Beta         | Repro build pipeline integration   |
| Encrypted Memory (select stores)       | Beta         | Configurable secret wrapper        |
| Plugin Signature Enforcement           | GA           | Required for elevation             |
| Revocation List Distribution           | GA           | Fetched at startup; caches locally |

## 9. Key Rotation & Revocation (Summary)

Refer to `OWNERSHIP.md` Appendix A for procedural detail.

Snapshot:

- Rotation Cadence: 12 months or sooner on incident.
- Revocation Propagation: Commit revocation file + release advisory; clients fetch on update.
- Key Metadata: key id (first 8 hex), created_at, expires_at.

## 10. Monitoring & Metrics (Security-Relevant)

| Metric                               | Purpose                              |
| ------------------------------------ | ------------------------------------ |
| aetherra_signing_failures_total      | Detect signature verification issues |
| aetherra_quarantined_artifacts_total | Track rejected workflows/plugins     |
| hmr_audit event counters             | Monitor reload anomalies             |
| plugin_timeout_total (planned)       | Detect misbehaving plugins           |

## 11. Assumptions

- Host environment is not hostile (no ptrace / code injection prevention in scope yet).
- Contributors act in good faith; malicious submissions are caught in review.
- CI secrets protected by platform policies.

## 12. Review & Update

- Reviewed prior to each pre-release (alpha -> beta) milestone.
- Updates require PR + steward approval.

---
For security concerns: [security@aetherra.dev](mailto:security@aetherra.dev)
