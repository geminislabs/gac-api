"""Formato consistente de errores HTTP para respuestas de la API."""

from __future__ import annotations

from typing import Any


def format_validation_errors(errors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convierte errores Pydantic/FastAPI en una lista legible para clientes."""
    formatted: list[dict[str, Any]] = []
    for err in errors:
        loc = err.get("loc", ())
        field = ".".join(str(part) for part in loc if part != "body")
        formatted.append(
            {
                "field": field or "body",
                "message": err.get("msg", "Invalid value"),
                "type": err.get("type"),
            }
        )
    return formatted


def validation_error_message(errors: list[dict[str, Any]]) -> str:
    """Mensaje único resumido para errores 422."""
    parts = format_validation_errors(errors)
    if not parts:
        return "Error de validación en la solicitud"
    if len(parts) == 1:
        p = parts[0]
        return f"{p['field']}: {p['message']}"
    return "; ".join(f"{p['field']}: {p['message']}" for p in parts[:5])
