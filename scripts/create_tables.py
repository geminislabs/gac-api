"""Bootstrap script para crear todas las tablas declaradas en los modelos.

Idempotente: usa `CREATE TABLE IF NOT EXISTS` vía `Base.metadata.create_all`.
Asume que el schema configurado en `DB_SCHEME` ya existe.
"""

import asyncio
import sys
from pathlib import Path

# Asegura que `app/...` sea importable cuando se corre vía `python -m scripts.create_tables`.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.core.database import Base, engine  # noqa: E402
import app.models  # noqa: F401, E402  # registra los modelos en Base.metadata


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    table_names = sorted(Base.metadata.tables.keys())
    print("OK - tablas creadas/aseguradas:")
    for name in table_names:
        print(f"  - {name}")


if __name__ == "__main__":
    asyncio.run(main())
