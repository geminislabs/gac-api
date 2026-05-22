# GAC API

Backend API for Gemini Admin Console (GAC).

## Setup

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   Copy `.env.example` to `.env` and adjust if necessary.

4. Run migrations:
   ```bash
   alembic upgrade head
   ```

5. Run the server:
   ```bash
   # Para desarrollo local
   uvicorn app.main:app --reload --host 0.0.0.0 --port 5160

   # Para acceso desde otras máquinas/red (como EC2)
   uvicorn app.main:app --host 0.0.0.0 --port 5160
   ```

## Development (lint, tests, git hooks)

Install dev dependencies (includes pre-commit; pytest en commits lo instala pre-commit en su propio entorno):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

Register git hooks (once per clone):

```bash
pre-commit install
```

Run all checks manually (same as CI and pre-commit hooks):

```bash
pre-commit run --all-files
```

On each `git commit`, pre-commit runs ruff, black, and pytest automatically (pytest usa un entorno propio de pre-commit; no hace falta activar el venv).

Si añades dependencias en `requirements.txt`, actualiza también `additional_dependencies` del hook `pytest` en `.pre-commit-config.yaml`.

## Documentation

- Swagger UI: `/docs`
- ReDoc: `/redoc`
