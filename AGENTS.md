# AGENTS.md — Guía para agentes de código

Instrucciones para asistentes de IA (Cursor, Copilot, etc.) que trabajen en este repositorio.

## Proyecto

**gac-api** — API FastAPI del Gemini Admin Console (GAC): usuarios, roles, clientes, órdenes, pagos, envíos, dispositivos y tokens PASETO internos.

## Stack

| Capa        | Tecnología                          |
| ----------- | ----------------------------------- |
| Framework   | FastAPI + Uvicorn                   |
| ORM         | SQLAlchemy 2 (async)                |
| DB          | PostgreSQL (schema `gac`)           |
| Auth        | JWT + PASETO (tokens internos)      |
| Lint/format | Ruff + Black                        |
| Tests       | pytest + pytest-cov                 |
| Runtime     | Python 3.12+ (CI); Docker 3.11      |
| Deploy      | Docker → EC2 (push a `master`)      |

## Estructura

```text
app/api/v1/             # REST endpoints
app/services/           # lógica de negocio
app/models/             # SQLAlchemy models
app/schemas/            # Pydantic DTOs
tests/                  # pytest (SQLite in-memory + Postgres opcional)
docs/                   # guías y gobernanza
```

## Convenciones

- **Python 3.12+** en CI y tooling (ver `.python-version`).
- **Formato:** Black (88 cols), Ruff para lint.
- **Commits:** Conventional Commits (`feat:`, `fix:`, `chore:`, etc.).
- **Alcance:** Cambios mínimos y enfocados. No reformatear código no relacionado.

## Comandos obligatorios antes de terminar

```bash
make validate
```

Equivalente: `make lint`, `make format-check`, `make test`, `docker build`.

Opcional: `make scan-secrets`, `make audit-deps`, `make scan-osv`, `pre-commit run --all-files`.

## Gobernanza

- Branch protection y política de CI: `docs/GOVERNANCE.md`
- CODEOWNERS y Dependabot: `.github/`
- Deploy secrets: `.github/GITHUB_SETUP.md`

## Módulos sensibles

- `app/core/security.py` — JWT y hashing de contraseñas
- `app/core/paseto.py` — tokens PASETO internos
- `app/api/deps.py` — autenticación y autorización por roles

## Deploy

- CI en PR/push a `develop`/`master` (`.github/workflows/quality.yml`)
- Deploy automático al pushear `master` (`.github/workflows/deploy.yml`)
