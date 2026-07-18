"""SQLite compatibility shims for PostgreSQL types used in tests."""

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles

_REGISTERED = False


@compiles(JSONB, "sqlite")
def _compile_jsonb_for_sqlite(type_, compiler, **kw):
    return "JSON"


def register_sqlite_dialect_compat() -> None:
    global _REGISTERED
    if _REGISTERED:
        return
    _REGISTERED = True
