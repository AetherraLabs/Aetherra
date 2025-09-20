#!/usr/bin/env bash
set -euo pipefail

# --- Config ---
PY_DIRS="Aetherra"
FRONTEND_DIR="frontend"

# Modes: default to "fix" for backward-compat; also support --check and --guarded-fix
MODE="fix"
SECURITY_DEEP=0
for arg in "$@"; do
  case "$arg" in
    --check) MODE="check" ;;
    --fix) MODE="fix" ;;
    --guarded-fix) MODE="guarded-fix" ;;
    --security-deep) SECURITY_DEEP=1 ;;
  esac
done

echo "[doctor] Mode: $MODE"

run_ruff_check() {
  if command -v ruff >/dev/null 2>&1; then
    echo "[doctor] Ruff format --check"
    ruff format --check . || true
    echo "[doctor] Ruff check (no fix)"
    ruff check . || true
  else
    echo "[doctor][warn] ruff not found; skipping format/lint"
  fi
}

run_ruff_fix() {
  if command -v ruff >/dev/null 2>&1; then
    echo "[doctor] Ruff format & fix"
    ruff format .
    ruff check . --fix
  else
    echo "[doctor][warn] ruff not found; skipping format/lint"
  fi
}

run_types_tests() {
  echo "[doctor] MyPy (strict-ish)"
  if command -v mypy >/dev/null 2>&1; then
    mypy $PY_DIRS || true
  else
    echo "[doctor][warn] mypy not found; skipping type check"
  fi

  echo "[doctor] Pyright (optional)"
  if command -v pyright >/dev/null 2>&1; then
    pyright || true
  else
    echo "[doctor][info] pyright not installed; editor extension can provide feedback"
  fi

  echo "[doctor] PyTest (quick)"
  if command -v pytest >/dev/null 2>&1; then
    pytest -q --maxfail=1 --disable-warnings
  else
    echo "[doctor][warn] pytest not found; skipping tests"
  fi
}

run_secret_scan() {
  echo "[doctor] Gitleaks scan"
  if command -v gitleaks >/dev/null 2>&1; then
    gitleaks detect --no-banner --redact --report-path tools/gitleaks_report.json || true
  else
    echo "[doctor][warn] gitleaks not found; install 'gitleaks' or 'gitleaks-bin' (pip)"
  fi
}

run_security_deep() {
  if [ "$SECURITY_DEEP" -eq 1 ]; then
    echo "[doctor] Security deep: bandit & pip-audit"
    if command -v bandit >/dev/null 2>&1; then
      bandit -q -r $PY_DIRS -f json -o tools/bandit_report.json || true
    else
      echo "[doctor][info] bandit not installed; skipping"
    fi
    if command -v pip-audit >/dev/null 2>&1; then
      pip-audit -f json -o tools/pip_audit_report.json || true
    else
      echo "[doctor][info] pip-audit not installed; skipping"
    fi
  fi
}

run_frontend() {
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
}

case "$MODE" in
  check)
    run_ruff_check
    run_types_tests
    run_secret_scan
    run_security_deep
    run_frontend
    ;;
  fix)
    run_ruff_fix
    run_types_tests
    run_secret_scan
    run_security_deep
    run_frontend
    ;;
  guarded-fix)
    if command -v git >/dev/null 2>&1; then
      if [ -n "$(git status --porcelain)" ]; then
        echo "[doctor][error] Guarded fix requires a clean git working tree. Commit or stash changes first." >&2
        exit 2
      fi
    else
      echo "[doctor][warn] git not found; guarded-fix cannot guarantee safety"
    fi
    run_ruff_fix
    set +e
    pytest -q --maxfail=1 --disable-warnings
    TEST_RC=$?
    set -e
    if [ $TEST_RC -ne 0 ]; then
      if command -v git >/dev/null 2>&1; then
        echo "[doctor] Tests failed; reverting changes via git reset --hard"
        git reset --hard
      fi
      exit $TEST_RC
    fi
    run_types_tests
    run_secret_scan
    run_security_deep
    run_frontend
    ;;
  *)
    echo "[doctor][error] Unknown mode: $MODE" >&2
    exit 2
    ;;
esac

echo "[doctor] Done ✓"
