from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Configurar el engine con el esquema especificado en DB_SCHEME
connect_args = {"server_settings": {"search_path": settings.DB_SCHEME}}
engine = create_async_engine(
    settings.DATABASE_URL, echo=False, connect_args=connect_args
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
