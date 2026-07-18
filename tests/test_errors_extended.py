"""Tests adicionales para app.core.errors (sin DB)."""

from app.core.errors import format_validation_errors, validation_error_message


def test_validation_error_message_empty_errors():
    assert validation_error_message([]) == "Error de validación en la solicitud"


def test_validation_error_message_multiple_fields():
    errors = [
        {"loc": ("body", "email"), "msg": "invalid", "type": "value_error"},
        {"loc": ("body", "name"), "msg": "required", "type": "missing"},
    ]
    msg = validation_error_message(errors)
    assert "email" in msg
    assert "name" in msg


def test_format_validation_errors_skips_body_prefix():
    errors = [{"loc": ("body", "field"), "msg": "bad", "type": "x"}]
    formatted = format_validation_errors(errors)
    assert formatted[0]["field"] == "field"
