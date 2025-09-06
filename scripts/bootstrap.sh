#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
set -euo pipefail

echo "[BOOTSTRAP] Starting Aetherra bootstrap (Unix)"

VERSION=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --version) VERSION="$2"; shift 2;;
    *) echo "Unknown arg: $1"; exit 2;;
  esac
done

if [[ ! -d .venv ]]; then
  echo "[BOOTSTRAP] Creating virtual environment .venv"
  python -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel > /dev/null
python -m pip install -e .[dev]

if [[ -n "$VERSION" ]]; then
  export AETHERRA_VERSION="$VERSION"
fi

echo "[BOOTSTRAP] Running smoke test"
python tools/os_smoke.py --profile test

echo "[BOOTSTRAP] Running regression fast set"
python tools/run_regression_suite.py

echo "[BOOTSTRAP] Running quality gates"
python tools/quality_gates.py

echo "[BOOTSTRAP] Success"
