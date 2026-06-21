# Deprecated UI Legacy Archive

This folder contains UI surfaces that no longer define Aetherra's active
product direction.

The canonical UI direction is the Runtime Observatory:

- `Aetherra/runtime_ui/`
- `Aetherra/lyrixa/gui/src/App.tsx`
- `docs/AETHERRA_RUNTIME_UI_SYSTEM.md`

Files archived here are retained only as historical reference while the
repository transitions away from legacy Lyrixa apps, old root frontends,
dashboard experiments, and demo UI entrypoints.

Do not import from this folder in runtime code. Useful behavior should be
reimplemented through the Runtime UI contract instead.
