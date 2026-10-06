# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Security

- **`python-jose` se cambia por `PyJWT`.** `python-jose` traía `ecdsa` (PYSEC-2026-1325 /
  GHSA-wj6h-64fc-37mp, ignorado en `pip-audit`) y tiene CVE-2026-85394 sin versión corregida. Ninguno
  era explotable aquí (HS256 con secreto propio, sin llave pública), pero eran avisos permanentes.
  `scripts/pip-audit-scan.sh` queda sin excepciones
  - `app/core/security.py`, `app/api/deps.py`, `app/services/auth_service.py`: `import jwt` y
    `jwt.PyJWTError` en vez de `JWTError`. `ExpiredSignatureError` hereda de ella: un token vencido
    sigue dando 403 en `get_current_user` y `None` en el refresh
  - **Las sesiones abiertas sobreviven**: un token firmado por `python-jose` 3.5.0 se verifica con
    PyJWT (`tests/test_pyjwt_compat.py`, con un token literal). Al revés también —verificado a
    mano—, así que volver a la imagen anterior tampoco cierra sesiones

### Fixed

- `sqlalchemy[asyncio]` acotado a `<2.1`. SQLAlchemy 2.1 (24/09/2026) hizo `ForeignKey._colspec` de
  sólo lectura y `tests/sqlite_metadata.py` lo modifica: 12 tests daban error en cualquier PR. Además,
  el próximo deploy habría instalado 2.1 en producción, que corre 2.0.x desde el 10/08, sin haberla
  probado. Subir a 2.1 queda para su propio PR, adaptando `tests/sqlite_metadata.py`

### Added

- Engineering foundation: blocking CI (`quality` + `security` jobs)
- Soft foundations: SQLite in-memory test fixtures (`db_session_sqlite`, `client_sqlite`)
- Quality gates: `CODEOWNERS`, `dependabot.yml`, `docs/GOVERNANCE.md`, OSV-Scanner, `osv-scanner.toml`
- Coverage floor (65% on `app/`) via `pyproject.toml` and `pytest.ini`
- `scripts/gitleaks-scan.sh`, `scripts/pip-audit-scan.sh`, `scripts/osv-scan.sh`, `scripts/setup.sh`
- `.pre-commit-config.yaml` (Ruff, Black, hygiene hooks)
- `AGENTS.md`, `CONTRIBUTING.md`, `SECURITY.md`, `docs/RELEASE.md`
- `.editorconfig`, `.python-version`, `.gitleaks.toml`
- GitHub pull request template and issue templates
- `make validate`, `make run-dev`, `make scan-secrets`, `make audit-deps`, `make scan-osv`

### Changed

- CI: Ruff, Black, pytest, and Docker build are blocking
- Test harness: SQLite fixtures, bootstrap env defaults, per-request DB sessions
- Minimum Python version **3.12** for CI and tooling (Dockerfile remains 3.11 until follow-up)

### Fixed

- Async/event-loop test failures with TestClient + SQLAlchemy
- Minimum dependency floors raised for security (fastapi, pydantic, python-jose, python-multipart, pyseto, cryptography)
