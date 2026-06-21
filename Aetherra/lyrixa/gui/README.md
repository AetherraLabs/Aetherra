# Aetherra Runtime Observatory

This package is the active Runtime UI alpha shell for Aetherra.

It is intentionally read-only:

- It renders the Cognitive Observatory experience.
- It consumes `/api/runtime-ui/bootstrap` when the Hub is available.
- It falls back to a bounded local snapshot for static build inspection.
- It does not own mutation, approval, execution, or privileged controls.

The folder name still includes `lyrixa/gui` for compatibility with the existing
Hub frontend serving path. The product direction is Aetherra Runtime
Observatory, not the legacy Lyrixa GUI.

Active files:

- `src/App.tsx`
- `src/index.css`
- `src/main.tsx`
- `index.html`
- `package.json`
- Vite, TypeScript, PostCSS, and Tailwind configuration

Legacy Lyrixa GUI files from this package have been moved to
`deprecated/ui_legacy/Aetherra/lyrixa/gui/`.
