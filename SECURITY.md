# Security Policy

We take security and privacy seriously. Please follow these guidelines to report vulnerabilities and keep users safe.

## Supported Versions

We aim to support the latest stable main branch. Security fixes are backported on a best-effort basis.

## Reporting a Vulnerability

- Do not open public issues for security vulnerabilities.
- Email security reports to <mailto:security@aetherralabs.org> with details and a proof of concept when possible.
- Please allow up to 72 hours for initial response.

## Scope

All code in this repository, published Docker images, and hosted demo infrastructure are in scope unless explicitly marked otherwise.

## Coordinated Disclosure

- We follow responsible disclosure. We will work with you on a timeline.
- We will credit reporters in release notes unless you prefer to remain anonymous.

## Hardening Checklist (Internal)

- Secret scanning and push protection enabled
- CodeQL security analysis enabled
- Dependabot security updates enabled
- CI uses least-privilege tokens and avoids printing secrets
- Dependencies pinned and lockfiles committed
