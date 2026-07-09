# Guía de contribución

Gracias por contribuir a **gac-api**.

## Requisitos previos

- **Python 3.12+** (ver `.python-version`)
- PostgreSQL para integración (o `make test-db-up` — puerto 5433)

```bash
bash scripts/setup.sh
cp .env.example .env   # ajustar variables
```

## Flujo de trabajo

### 1. Rama base

Trabaja desde `develop`:

```bash
git checkout develop
git pull origin develop
git checkout -b <tipo>/<descripcion-corta>
```

| Prefijo     | Uso                                         |
| ----------- | ------------------------------------------- |
| `feature/`  | Nueva funcionalidad                         |
| `fix/`      | Corrección de bug                           |
| `chore/`    | Tooling, docs, dependencias, CI             |
| `refactor/` | Cambio interno sin cambio de comportamiento |
| `test/`     | Solo tests                                  |

### 2. Commits

[Conventional Commits](https://www.conventionalcommits.org/):

```text
<tipo>(<alcance opcional>): <descripción en imperativo>
```

### 3. Antes de abrir un PR

```bash
make validate
```

Equivalente manual:

```bash
make lint
make format-check
make test
docker build -t gac-api:local .
```

Opcional:

```bash
make scan-secrets
make audit-deps
make scan-osv
make test-cov    # incluye umbral de cobertura (ver docs/GOVERNANCE.md)
pre-commit run --all-files
```

### 4. Pull requests

- Base branch: **`develop`**
- Usa la plantilla de PR (`.github/pull_request_template.md`)
- Actualiza `CHANGELOG.md` en `[Unreleased]` si el cambio es visible

## Hooks locales

```bash
pre-commit install
```

Incluye Ruff y Black. Gitleaks: `make scan-secrets`.

## Gobernanza

Ver `docs/GOVERNANCE.md` para branch protection, CI y política de cobertura.
