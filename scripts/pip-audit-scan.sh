#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python -m pip install --upgrade pip pip-audit >/dev/null
pip install -r requirements.txt >/dev/null

# Sin excepciones desde el 06/10/2026: la de ecdsa (PYSEC-2026-1325 /
# GHSA-wj6h-64fc-37mp) llegaba por python-jose, que se cambió por PyJWT.
exec python -m pip_audit -r requirements.txt --desc on
