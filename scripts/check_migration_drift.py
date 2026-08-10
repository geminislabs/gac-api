"""Compara el estado real de la base con lo que alembic cree que hay.

Por qué existe: parte del esquema de gac se creó con `scripts/create_tables.py`
(`Base.metadata.create_all`), fuera de alembic. Cuando eso pasa, las tablas
existen pero `alembic_version` puede estar vacía o apuntar a una revisión
anterior, y un `alembic upgrade head` a ciegas intenta recrear tablas que ya
están y falla con "already exists".

Este script no toca nada. Solo dice en qué situación estás y qué hacer.

    python -m scripts.check_migration_drift
"""

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sqlalchemy import inspect, text  # noqa: E402

import app.models  # noqa: F401, E402  # registra los modelos en Base.metadata
from app.core.config import settings  # noqa: E402
from app.core.database import Base, engine  # noqa: E402

SCHEMA = "gac"


def _revisions_on_disk() -> list[str]:
    versions = ROOT / "alembic" / "versions"
    found = []
    for path in sorted(versions.glob("*.py")):
        for line in path.read_text().splitlines():
            if line.startswith("revision:") or line.startswith("revision ="):
                found.append(line.split("=")[-1].strip().strip("'\""))
                break
    return found


async def main() -> None:
    async with engine.begin() as conn:
        stamped = None
        has_version_table = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).has_table(
                "alembic_version", schema=SCHEMA
            )
            or inspect(sync_conn).has_table("alembic_version")
        )
        if has_version_table:
            try:
                result = await conn.execute(text("SELECT version_num FROM alembic_version"))
                stamped = [row[0] for row in result]
            except Exception:  # noqa: BLE001 - la tabla puede estar en otro schema
                stamped = None

        real_tables = await conn.run_sync(
            lambda sync_conn: sorted(inspect(sync_conn).get_table_names(schema=SCHEMA))
        )

    expected = sorted(
        name.split(".")[-1]
        for name, table in Base.metadata.tables.items()
        if table.schema == SCHEMA
    )
    on_disk = _revisions_on_disk()

    print(f"Base:    {settings.DB_NAME} @ {settings.DB_HOST}")
    print(f"Schema:  {SCHEMA}")
    print()
    print(f"Revisiones en alembic/versions: {', '.join(on_disk) or '(ninguna)'}")
    print(f"alembic_version en la base:     {stamped if stamped else '(vacia o inexistente)'}")
    print()
    print(f"Tablas en la base ({len(real_tables)}): {', '.join(real_tables) or '(ninguna)'}")
    print(f"Tablas en los modelos ({len(expected)}): {', '.join(expected)}")

    faltan = [t for t in expected if t not in real_tables]
    sobran = [t for t in real_tables if t not in expected and t != "alembic_version"]
    if faltan:
        print(f"\n  En los modelos pero NO en la base: {', '.join(faltan)}")
    if sobran:
        print(f"\n  En la base pero NO en los modelos: {', '.join(sobran)}")

    print("\n" + "=" * 60)
    if not stamped and real_tables:
        print("DESFASE: las tablas existen pero alembic no tiene constancia.")
        print()
        print("Las migraciones de este repo llevan guardas de existencia, asi")
        print("que se pueden ejecutar sobre esta base sin riesgo: crean lo que")
        print("falta y saltan lo que ya esta.")
        print()
        print("    alembic upgrade head")
        print()
        print("NO uses 'alembic stamp': marcaria como aplicadas tablas que no")
        print("existen, y entonces nunca se crearian.")
        if faltan:
            print()
            print(f"Se crearan: {', '.join(faltan)}")
    elif not stamped and not real_tables:
        print("Base vacia. 'alembic upgrade head' es seguro.")
    elif stamped and faltan:
        print(f"alembic esta en {stamped}. Faltan tablas: {', '.join(faltan)}.")
        print("'alembic upgrade head' deberia aplicarlas.")
    else:
        print(f"alembic esta en {stamped} y la base coincide con los modelos.")


if __name__ == "__main__":
    asyncio.run(main())
