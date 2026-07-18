# Tests — gac-api

## Fixtures

| Fixture | Uso |
| --- | --- |
| `client` | TestClient sin DB (mocks / overrides manuales) |
| `db_session_sqlite` | Sesión async SQLite en memoria |
| `client_sqlite` | TestClient con `get_db` → SQLite |
| `async_client_sqlite` | httpx AsyncClient con SQLite |

## Escribir tests nuevos

Preferir **SQLite** para tests que necesitan persistencia:

```python
@pytest.mark.asyncio
async def test_example(db_session_sqlite: AsyncSession):
    ...
```

Para endpoints con DB:

```python
def test_endpoint(client_sqlite: TestClient):
    response = client_sqlite.get("/health")
```

Los tests existentes que no usan DB siguen con `client` sin cambios.

## PostgreSQL local (integración)

```bash
docker compose -f docker-compose.test.yml up -d
# Postgres en localhost:5433 — usar en PRs futuros de integración
```

## Variables de entorno

`tests/bootstrap_env.py` define defaults antes de importar `app`. No requiere `.env` para la suite unitaria.
