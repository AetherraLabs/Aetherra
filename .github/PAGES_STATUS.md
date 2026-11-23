# Company website publisher migration

The intended sole source and publisher for `aetherra.dev` and
`www.aetherra.dev` is the private
[AetherraLabs/Aetherra-Website repository](https://github.com/AetherraLabs/Aetherra-Website).
This software repository retains the authoritative technical documentation,
research evidence, and Runtime Observatory source.

**CLEANUP MUST NOT MERGE until the new publisher has been verified at both
`https://aetherra.dev/` and `https://www.aetherra.dev/`, existing public
documentation URLs work, and GitHub Pages is disabled for this repository.**

This is a staged cleanup, not confirmation that the live cutover is complete.
The previous publisher used the `main` branch's `/docs` directory through
legacy GitHub Pages settings. A separate `deploy-pages.yml` workflow also
existed. Removing the workflow and `docs/CNAME` does not disable those repository
settings; both publishing paths must be retired after the new site is verified.

The Website repository must publish a pinned snapshot of the retained technical
documentation and handle legacy website routes. Its migration record should
include the deployed revision, apex and `www` checks, documentation URL checks,
and confirmation that this repository can no longer publish the company site.

See [the documentation publishing guide](../docs/ops/README_DEPLOY.md) for local
checks and the merge prerequisites. The Sphinx workflow remains a documentation
build and artifact check; it does not deploy the company website.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
