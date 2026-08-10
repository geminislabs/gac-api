import asyncio
from logging.config import fileConfig

import sqlalchemy as sa
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import app settings and models
import sys
import os

sys.path.append(os.getcwd())

from app.core.config import settings
from app.core.database import Base

# Import all models here to ensure they are registered
from app.models import *

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # La tabla de versiones vive en 'gac', junto a lo que gestiona.
        # Por defecto alembic la crearia en el search_path, que es 'public'
        # porque DB_SCHEME no se escribe en el .env del despliegue. El usuario
        # de la aplicacion no tiene por que poder crear nada en public, y de
        # hecho en produccion no puede.
        version_table_schema="gac",
    )

    with context.begin_transaction():
        context.run_migrations()


def _ensure_schema(connection: Connection) -> None:
    """Crea el esquema 'gac' solo si de verdad falta.

    Orden obligado: la tabla de versiones de alembic vive en 'gac', asi que el
    esquema tiene que existir ANTES de que alembic la cree, es decir antes de la
    primera migracion.

    Se consulta primero en vez de lanzar 'CREATE SCHEMA IF NOT EXISTS': Postgres
    comprueba el privilegio CREATE sobre la base antes de evaluar el IF NOT
    EXISTS, asi que la version a ciegas falla con "permission denied" incluso
    cuando el esquema ya esta. El usuario de la aplicacion en produccion no
    tiene ese privilegio, y no deberia necesitarlo para migrar un esquema que
    ya existe.
    """
    exists = connection.execute(
        sa.text("SELECT 1 FROM information_schema.schemata WHERE schema_name = 'gac'")
    ).scalar()
    if not exists:
        connection.execute(sa.text("CREATE SCHEMA gac"))

    # El commit va SIEMPRE, se haya creado el esquema o no. El SELECT de arriba
    # ya abre una transaccion implicita, y si se deja abierta alembic no es
    # dueno de la suya: ejecuta las migraciones y al cerrar la conexion se hace
    # rollback de todo, sin un solo error por ninguna parte.
    connection.commit()


def do_run_migrations(connection: Connection) -> None:
    _ensure_schema(connection)
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # Ver la nota en run_migrations_offline: la tabla de versiones va en
        # 'gac', no en el search_path.
        version_table_schema="gac",
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
