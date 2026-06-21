# Lyrixa UI Standards (React/TypeScript)

This document summarizes the lightweight checks enforced by
`tools/verify_ui_standards.py` and a few practical guidelines for the Lyrixa GUI.

## Automated checks

The verifier scans both Python UI files and the React/TypeScript frontend (TS/TSX/JS/JSX):

- React/TS heuristics
  - ERROR: `dangerouslySetInnerHTML` — avoid or ensure proper sanitization.
  - WARN: `alert()`/`window.alert()` — prefer non-blocking toasts (Sonner) or inline banners.
  - WARN: Hard-coded endpoints like `http://localhost` or `127.0.0.1` —
    use a configurable base URL (localStorage or current origin) and allow overrides.
  - INFO: `console.log` — keep out of production code; use structured logs or toasts when user-facing.
  - WARN: Very large modules (>1000 LOC) — consider splitting components.

- Python UI heuristics
  - ERROR: PySide2 / QtWebKit imports — migrate to PySide6; replace deprecated modules.
  - WARN: `time.sleep()` in UI thread — use timers/async.
  - WARN: Synchronous/blocking network calls in UI thread.
  - WARN: Very large modules (>1500 LOC) — consider refactor.

The report is written to `ui_standards_report.md` at the repo root.

## How to run

From VS Code, use the task "Verify UI Standards" or run:

```powershell
python tools/verify_ui_standards.py --dir Aetherra/lyrixa/gui/src --output ui_standards_report.md
```

If `--dir` is missing or invalid, the tool will fall back to `Aetherra/lyrixa/gui/src` when present.

## Current conventions

- Backend URL
  - Default to `window.localStorage.getItem('lyrixa_backend') || window.location.origin`.
  - Allow users to set/override in Settings. Avoid hard-coded dev endpoints in the codebase.

- Notifications & errors
  - Use `toast.success/info/warning/error` (Sonner) for transient messages.
  - Avoid modal `alert()`; use inline banners or toasts.

- Streaming UX
  - Auto-scroll to the latest message while streaming.
  - If streaming fails, reuse the placeholder assistant bubble with the error message (avoid duplicates).
  - SSE-first with REST fallback on any SSE error frame.

- Accessibility & semantics
  - Prefer semantic HTML and ARIA roles for interactive components.
  - Ensure focus management for dialogs and command palettes.

- Structure
  - Split very large screens into subcomponents when exceeding ~1000 LOC.
  - Keep API utils centralized (`lib/api.ts`) and avoid direct `fetch` scattered across the UI.

## Roadmap (nice-to-haves)

- Add checks for missing ARIA labels on interactive elements.
- Detect fetch calls inside render without `useEffect`.
- Enforce use of AbortController for cancellable requests.
- Hook into ESLint config for stricter, type-aware checks.
