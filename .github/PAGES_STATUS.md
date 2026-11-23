# Company website publisher migration

The sole source and publisher for `aetherra.dev` and
`www.aetherra.dev` is the private
[AetherraLabs/Aetherra-Website repository](https://github.com/AetherraLabs/Aetherra-Website).
This software repository retains the authoritative technical documentation,
research evidence, and Runtime Observatory source.

**Cutover verified on 2026-11-23 UTC (November 22 local time).** Both
`https://aetherra.dev/` and `https://www.aetherra.dev/` passed 343 HTTP checks:
285 content checks, 56 compatibility redirects and two genuine 404s. That includes
all 265 retained documentation files and `/docs/PERSONAL_CONTINUITY.md`.

Cloudflare Pages project `aetherra-website` builds the private Website repository's
`main` branch directly. The verified production revision is
`c1c79eb481db24905e3f4a3ccd3426328e4d34c8`, deployment
`a12532cc-1a14-4883-bf0b-de94efc7ec56`. Its approved homepage and 15 associated
release artifacts are byte-identical to the November 22 website release.

The old `main:/docs` GitHub Pages site was deleted after both live checks passed;
the Pages API now returns 404. The separate Pages workflow was disabled before
removal. The obsolete Cloudflare `aetherra` project's production and preview
builds are disabled, as is the redundant Worker build connection created during
setup. The software repository can no longer publish the company website.

The Website repository publishes a pinned, hash-verified snapshot of the retained
technical documents. Its `docs/WEBSITE_MIGRATION.md` records staging/live evidence,
the original DNS settings, retired redirects and rollback instructions.

See [the documentation publishing guide](../docs/ops/README_DEPLOY.md) for local
checks and the cutover evidence. The Sphinx workflow remains a documentation
build and artifact check; it does not deploy the company website.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
