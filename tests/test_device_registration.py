"""Validación de payloads de registro de dispositivos (reglas siscom-admin-api)."""

import pytest
from pydantic import ValidationError

from app.schemas.device_registration import DeviceRegistrationPayload


def test_normalize_removes_empty_sim_profile():
    raw = {
        "device_id": "123456789012345",
        "brand": "Suntech",
        "model": "ST4330",
        "carrier": "KORE",
        "sim_profile": {"kore_sim_id": "", "kore_account_id": ""},
    }
    normalized = DeviceRegistrationPayload.normalize_web_payload(raw)
    assert "sim_profile" not in normalized
    payload = DeviceRegistrationPayload(**normalized)
    assert payload.carrier == "KORE"


def test_valid_payload_with_kore_profile():
    payload = DeviceRegistrationPayload(
        device_id="123456789012345",
        brand="Suntech",
        model="ST4330",
        carrier="KORE",
        sim_profile={
            "kore_sim_id": "HS0ad6bc269850dfe13bc8bddfcf8399f4",
            "kore_account_id": "CO1757099",
        },
    )
    assert payload.sim_profile is not None
    assert payload.sim_profile.kore_sim_id.startswith("HS")


def test_empty_kore_sim_id_in_profile_raises():
    with pytest.raises(ValidationError):
        DeviceRegistrationPayload(
            device_id="123456789012345",
            brand="Suntech",
            model="ST4330",
            carrier="KORE",
            sim_profile={"kore_sim_id": ""},
        )


def test_device_id_too_short_raises():
    with pytest.raises(ValidationError):
        DeviceRegistrationPayload(
            device_id="123",
            brand="Suntech",
            model="ST4330",
        )


def test_iccid_invalid_length_raises():
    with pytest.raises(ValidationError):
        DeviceRegistrationPayload(
            device_id="123456789012345",
            brand="Suntech",
            model="ST4330",
            iccid="123",
        )


def test_carrier_other_cannot_have_sim_profile():
    with pytest.raises(ValidationError):
        DeviceRegistrationPayload(
            device_id="123456789012345",
            brand="Suntech",
            model="ST4330",
            carrier="other",
            sim_profile={"kore_sim_id": "HS0ad6bc269850dfe13bc8bddfcf8399f4"},
        )
