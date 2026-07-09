"""Patch SQLAlchemy metadata for in-memory SQLite tests (test-only)."""

from __future__ import annotations

import uuid as _uuid_module
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Text, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql.schema import ColumnDefault

_METADATA_PATCH_STATE: dict = {"applied": False, "saved": None}


class _SQLiteUUID(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return _uuid_module.UUID(str(value))
        except (ValueError, AttributeError):
            return value


_PG_TYPE_REPLACEMENTS = {
    PG_UUID: _SQLiteUUID(),
    JSONB: Text(),
}


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _python_default_for(server_default_text: str):
    text = server_default_text.lower()
    if any(k in text for k in ("gen_random_uuid", "uuid_generate")):
        return uuid4
    if any(k in text for k in ("now()", "current_timestamp", "timezone(")):
        return _utcnow
    return None


def _patch_fk_target(target: str) -> str:
    parts = target.split(".")
    if len(parts) == 3:
        return f"{parts[0]}_{parts[1]}.{parts[2]}"
    if len(parts) == 2 and parts[0] == "gac":
        return f"gac_{parts[1]}"
    return target


def _patch_metadata(metadata) -> dict:
    saved: dict = {}
    for table in metadata.tables.values():
        table_id = id(table)
        if table.schema is not None:
            saved[(table_id, "__table_schema__")] = {
                "schema": table.schema,
                "name": table.name,
            }
            table.name = f"{table.schema}_{table.name}"
            table.schema = None

        for column in table.columns:
            col_save: dict = {}
            fk_patches: list[tuple] = []

            if column.server_default is not None:
                sd_text = str(getattr(column.server_default, "arg", ""))
                col_save["server_default"] = column.server_default
                column.server_default = None
                if column.default is None:
                    callable_default = _python_default_for(sd_text)
                    if callable_default:
                        col_save["default"] = column.default
                        column.default = ColumnDefault(callable_default)

            fk_patches: list[tuple] = []
            for fk in column.foreign_keys:
                original = fk._colspec
                fk_patches.append((fk, original))
                fk._colspec = _patch_fk_target(str(original))

            for pg_type, sqlite_type in _PG_TYPE_REPLACEMENTS.items():
                if isinstance(column.type, pg_type):
                    col_save["type"] = column.type
                    column.type = sqlite_type
                    break

            if col_save:
                saved[(table_id, column.name)] = col_save
            if fk_patches:
                saved[(table_id, column.name, "__fks__")] = fk_patches

    return saved


def _restore_metadata(metadata, saved: dict) -> None:
    for table in metadata.tables.values():
        table_id = id(table)
        schema_key = (table_id, "__table_schema__")
        if schema_key in saved:
            if "name" in saved[schema_key]:
                table.name = saved[schema_key]["name"]
            if "schema" in saved[schema_key]:
                table.schema = saved[schema_key]["schema"]

        for column in table.columns:
            key = (table_id, column.name)
            if key in saved:
                if "server_default" in saved[key]:
                    column.server_default = saved[key]["server_default"]
                if "default" in saved[key]:
                    column.default = saved[key]["default"]
                if "type" in saved[key]:
                    column.type = saved[key]["type"]
            fk_key = (table_id, column.name, "__fks__")
            if fk_key in saved:
                for fk, original in saved[fk_key]:
                    fk._colspec = original


def ensure_sqlite_metadata(metadata) -> None:
    if _METADATA_PATCH_STATE["applied"]:
        return
    import app.models  # noqa: F401 — register all models on Base.metadata

    _METADATA_PATCH_STATE["saved"] = _patch_metadata(metadata)
    _METADATA_PATCH_STATE["applied"] = True


def restore_sqlite_metadata(metadata) -> None:
    saved = _METADATA_PATCH_STATE["saved"]
    if saved is not None:
        _restore_metadata(metadata, saved)
        _METADATA_PATCH_STATE["applied"] = False
        _METADATA_PATCH_STATE["saved"] = None
