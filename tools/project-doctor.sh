#!/usr/bin/env bash
set -euo pipefail

# --- Config ---
# Limit mypy to the main package to keep noise manageable; adjust as needed.
PY_DIRS="Aetherra"
FRONTEND_DIR="frontend"

echo "[doctor] Python: Ruff format & fix"
if command -v ruff >/dev/null 2>&1; then
  ruff format .
  ruff check . --fix
else
  echo "[doctor][warn] ruff not found; skipping format/lint"
fi

echo "[doctor] Python: MyPy (strict-ish)"
if command -v mypy >/dev/null 2>&1; then
  mypy $PY_DIRS
else
  echo "[doctor][warn] mypy not found; skipping type check"
fi

echo "[doctor] Python: Pyright (optional)"
if command -v pyright >/dev/null 2>&1; then
  # Do not fail the run on pyright; it's primarily for editor feedback
  pyright || true
else
  echo "[doctor][info] pyright not installed; editor extension can provide realtime feedback"
fi

echo "[doctor] Python: PyTest (quick)"
if command -v pytest >/dev/null 2>&1; then
  pytest -q --maxfail=1 --disable-warnings
else
  echo "[doctor][warn] pytest not found; skipping tests"
fi

echo "[doctor] Security: Gitleaks scan"
if command -v gitleaks >/dev/null 2>&1; then
  gitleaks detect --no-banner --redact --report-path tools/gitleaks_report.json || true
else
  echo "[doctor][warn] gitleaks not found; install 'gitleaks' or 'gitleaks-bin' (pip)"
fi

# --- Optional: frontend autofix ---
if [ -d "$FRONTEND_DIR" ] && [ -f "$FRONTEND_DIR/package.json" ]; then
  echo "[doctor] Frontend: lint & format"
  (
    cd "$FRONTEND_DIR"
    if command -v npm >/dev/null 2>&1; then
      npm run lint --silent || true
      npm run format --silent || true
      npm run typecheck --silent || true
    else
      echo "[doctor][warn] npm not found; skipping frontend checks"
    fi
  )
fi

echo "[doctor] Done ✓"
