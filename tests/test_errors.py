"""Utilidades de formato de errores."""

from app.core.errors import format_validation_errors, validation_error_message


def test_format_validation_errors_maps_fields():
    errors = [
        {
            "loc": ("body", "items", 0, "unit_price"),
            "msg": "Field required",
            "type": "missing",
        }
    ]
    formatted = format_validation_errors(errors)
    assert formatted[0]["field"] == "items.0.unit_price"
    assert formatted[0]["message"] == "Field required"


def test_validation_error_message_single_field():
    errors = [
        {
            "loc": ("body", "device_id"),
            "msg": "String should have at least 10 characters",
        }
    ]
    msg = validation_error_message(errors)
    assert "device_id" in msg
