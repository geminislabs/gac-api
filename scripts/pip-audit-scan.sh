#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python -m pip install --upgrade pip pip-audit >/dev/null
pip install -r requirements.txt >/dev/null

# ecdsa is transitive via python-jose; no upstream fix (Minerva timing — out of scope).
exec python -m pip_audit -r requirements.txt --desc on \
	--ignore-vuln PYSEC-2026-1325 \
	--ignore-vuln GHSA-wj6h-64fc-37mp
