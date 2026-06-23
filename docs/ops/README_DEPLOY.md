# Aetherra Pages Deployment

This guide documents the current GitHub Pages deployment path for Aetherra.

## Current Shape

The repository publishes the tracked `docs/` static site directly through
GitHub Pages. There is no tracked `aetherra-website/` or root frontend source
tree in mainline.

```text
.
├── docs/                              # GitHub Pages source
├── docs/index.html                    # Pages entrypoint
├── docs/assets/                       # Static assets
└── .github/workflows/deploy-pages.yml # Pages deployment workflow
```

## Deployment Workflow

The workflow at `.github/workflows/deploy-pages.yml`:

1. Runs on pushes to `main` that change `docs/**`.
2. Uploads the tracked `docs/` directory.
3. Deploys it to GitHub Pages.

No Node install or Vite build is performed by this workflow.

## Local Inspection

Serve `docs/` with any static file server to inspect the Pages site locally.
For example:

```bash
python -m http.server 8080 -d docs
```

Then open `http://localhost:8080`.

## Troubleshooting

- If Pages deploys a blank site, confirm `docs/index.html` exists.
- If assets fail to load, confirm referenced files exist under `docs/assets/`.
- If the workflow does not run, confirm the change touched `docs/**` or trigger
  the workflow manually from GitHub Actions.

## Active Runtime UI

The active Aetherra Runtime Observatory source lives at
`Aetherra/lyrixa/gui/`. It is separate from the tracked GitHub Pages static
site.
