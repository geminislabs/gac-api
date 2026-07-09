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
   bash scripts/setup.sh
   # o: make install-dev
   ```

3. Configure environment:
   Copy `.env.example` to `.env` and adjust if necessary.

4. Run migrations:
   ```bash
   alembic upgrade head
   # o: make migrations-up
   ```

5. Run the server:
   ```bash
   make run-dev
   ```
   Servidor en http://localhost:8000 con hot-reload.

## Development (lint, tests, CI)

```bash
make help           # Ver comandos disponibles
make validate       # format-check + lint + test + docker build (como CI)
make all-checks     # format-check + lint + test
make run-dev        # uvicorn --reload en puerto 8000
```

Register git hooks (once per clone):

```bash
pre-commit install
```

Run hooks manually:

```bash
pre-commit run --all-files
```

On each `git commit`, pre-commit runs Ruff and Black. Los tests se ejecutan en CI (`quality.yml`) y con `make test` / `make validate`.

PostgreSQL de test local (integración futura):

```bash
make test-db-up    # puerto 5433
make test-db-down
```

Ver `tests/README.md` para fixtures SQLite (`db_session_sqlite`, `client_sqlite`).

## Documentation

- Swagger UI: `/docs`
- ReDoc: `/redoc`
