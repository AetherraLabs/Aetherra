# Technical documentation and company website publishing

The private [AetherraLabs/Aetherra-Website repository](https://github.com/AetherraLabs/Aetherra-Website)
is the intended sole source and publisher for the company website at
`aetherra.dev` and `www.aetherra.dev`. Company homepage builds, assets, hosting,
and compatibility redirects belong there.

This Aetherra software repository remains authoritative for technical
documentation and research evidence. The Website build must import a pinned
snapshot of the retained documentation and preserve its existing public URLs.
That includes `/sections/*.html`, `/help/hub.html`, community and research
pages, Markdown documents, evidence JSON, and schemas. Legacy `/docs/*` routes
must resolve through the Website repository's compatibility handling without
masking actual documentation files.

## Cutover prerequisite

**CLEANUP MUST NOT MERGE until all of the following are verified:**

- The approved company site is served successfully over HTTPS at both
  `https://aetherra.dev/` and `https://www.aetherra.dev/` by the new publisher.
- Existing public documentation URLs and legacy routes work through the new
  publisher, including their stylesheets, icons, and supporting files.
- GitHub Pages is disabled for `AetherraLabs/Aetherra`, so this repository can
  no longer overwrite the company website.

The old repository settings published `main:/docs` independently of the
`deploy-pages.yml` workflow. Deleting that workflow and `docs/CNAME` alone does
not disable the legacy Pages source. This cleanup is prepared before cutover;
its presence on a branch is not evidence that the live migration is complete.
Record the deployed Website revision and verification results before merging.

## Retained documentation

The HTML section guides use `docs/sections/documentation-base.css` and
`docs/sections/documentation-icon.svg`. These preserve the previous shared
stylesheet and icon contents under documentation-specific names.
`section-theme.js` provides documentation navigation, breadcrumbs, and code
copy buttons without loading the company homepage.

The Sphinx entrypoints `docs/conf.py` and `docs/index.rst` and the workflow
`.github/workflows/docs.yml` remain in this repository. That workflow builds
and checks documentation and uploads an artifact; it does not publish the
company website.

To inspect the HTML guides locally:

```bash
python -m http.server 8080 -d docs
```

Open `http://localhost:8080/sections/hub.html`. The documentation tree no longer
contains a company homepage at its root.

## Cleanup verification

Run these commands from a full checkout containing the pre-migration commit:

```bash
python tools/verify_website_migration.py
python tools/ci_verify_no_website_artifacts.py
python -m sphinx -b html docs docs/_build/html
python -m sphinx -b linkcheck docs docs/_build/linkcheck
```

The migration check compares against
`645ab2ed5cccb3c1d26fb4eac414ac7640d6dd96`. It verifies the explicit company file
removals, unchanged technical HTML content apart from repaired asset links,
preserved documentation assets, local HTML dependencies, and unchanged baseline
files outside the cleanup allowlist. It is a one-time cutover check, not a
restriction on subsequent software development. The existing website artifact
guard remains available for normal quality gates.

The old RFC page already links to a missing
`/docs/ARCHITECTURE_VALIDATION_REPORT.md`; the migration check records that
pre-existing exception rather than changing unrelated technical content.

## Active Runtime UI

The Aetherra Runtime Observatory source remains at `Aetherra/lyrixa/gui/`.
It belongs to the software runtime and is unaffected by the company website
migration. Research documents, experiments, evidence, and historical inventories
also remain in this repository.
