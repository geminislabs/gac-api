"""
Referencia de validación para registro de dispositivos (siscom-admin-api).

GAC Web envía POST /api/v1/devices/ al Admin API vía token PASETO.
Este módulo documenta las reglas y permite validar payloads en tests.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

CarrierType = Literal["KORE", "other"]


class SimKoreProfileInput(BaseModel):
    kore_sim_id: str = Field(..., min_length=1)
    kore_account_id: Optional[str] = None


class DeviceRegistrationPayload(BaseModel):
    """Espejo de siscom-admin-api DeviceCreate para validación previa."""

    device_id: str = Field(..., min_length=10, max_length=50)
    brand: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    firmware_version: Optional[str] = None
    notes: Optional[str] = None
    iccid: Optional[str] = Field(None, min_length=18, max_length=22)
    carrier: Optional[CarrierType] = "KORE"
    sim_profile: Optional[SimKoreProfileInput] = None

    @model_validator(mode="after")
    def validate_sim_profile(self):
        if self.sim_profile and self.carrier != "KORE":
            raise ValueError("sim_profile solo es válido cuando carrier='KORE'")
        return self

    @classmethod
    def normalize_web_payload(cls, data: dict) -> dict:
        """Elimina campos que provocan 422 si van vacíos (p. ej. sim_profile)."""
        payload = {k: v for k, v in data.items() if v is not None and v != ""}
        carrier = payload.get("carrier", "KORE")
        sim = payload.get("sim_profile")
        if isinstance(sim, dict):
            kore_id = (sim.get("kore_sim_id") or "").strip()
            if not kore_id:
                payload.pop("sim_profile", None)
            else:
                payload["sim_profile"] = {
                    "kore_sim_id": kore_id,
                    **(
                        {"kore_account_id": sim["kore_account_id"].strip()}
                        if sim.get("kore_account_id")
                        else {}
                    ),
                }
        if carrier != "KORE":
            payload.pop("sim_profile", None)
        return payload
