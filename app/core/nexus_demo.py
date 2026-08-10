"""Cliente del entorno de demo de Nexus.

Es el primer cliente HTTP saliente de gac-api. Habla con dos servicios que viven
en otra EC2 y que se publican bajo el mismo dominio, detrás de una lista de IPs
en Caddy: el invite-gate (invitaciones y estado) y el bridge del worker de
Temporal (ciclo de vida del tenant).

Ambos comparten el mismo bearer, ``GATE_INTERNAL_SECRET``.

Regla que no se debe romper: **el OTP que devuelve create_invite no se persiste
ni se registra en logs.** Viaja de aquí a la respuesta HTTP del vendedor y ahí
muere. El gate solo guarda su hash, así que no hay forma de recuperarlo: si se
pierde, hay que reemitir.
"""

from __future__ import annotations

import secrets
from typing import Any

import httpx

from app.core.config import settings

# El aprovisionamiento del tenant puede tardar; la creación de la invitación es
# un INSERT. Se separan para no esperar 30 s por un endpoint que responde en 50 ms.
_TIMEOUT_FAST = httpx.Timeout(10.0, connect=5.0)
_TIMEOUT_SLOW = httpx.Timeout(30.0, connect=5.0)


class NexusDemoError(RuntimeError):
    """Fallo al hablar con el entorno de demo."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def _base_url() -> str:
    url = (settings.NEXUS_DEMO_OPS_URL or "").rstrip("/")
    if not url:
        raise NexusDemoError("NEXUS_DEMO_OPS_URL no está configurada")
    return url


def _headers() -> dict[str, str]:
    if not settings.GATE_INTERNAL_SECRET:
        raise NexusDemoError("GATE_INTERNAL_SECRET no está configurado")
    return {
        "Authorization": f"Bearer {settings.GATE_INTERNAL_SECRET}",
        "Content-Type": "application/json",
    }


def generate_tenant_id() -> str:
    """Identificador de tenant para una demo nueva.

    El gate lo valida contra ``char_length BETWEEN 1 AND 64`` y el worker exige
    su propio formato, así que se mantiene corto y en minúsculas.
    """
    return f"demo-{secrets.token_hex(4)}"


async def _request(
    method: str,
    path: str,
    *,
    json: dict[str, Any] | None = None,
    timeout: httpx.Timeout = _TIMEOUT_FAST,
) -> Any:
    url = f"{_base_url()}{path}"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(method, url, json=json, headers=_headers())
    except httpx.RequestError as exc:
        # No se incluye la URL completa en el mensaje: lleva el dominio interno
        # y este error acaba en la respuesta al navegador.
        raise NexusDemoError(
            f"no se pudo contactar con el entorno de demo: {exc.__class__.__name__}"
        ) from exc

    if response.status_code == 404:
        raise NexusDemoError("recurso no encontrado en el entorno de demo", 404)
    if response.status_code == 401:
        # Casi siempre es el bearer mal configurado; a veces la IP de egreso
        # cambió y Caddy devuelve 404 en su lugar. Merece un mensaje propio.
        raise NexusDemoError("el entorno de demo rechazó las credenciales", 401)
    if response.status_code >= 400:
        raise NexusDemoError(
            f"el entorno de demo respondió {response.status_code}",
            response.status_code,
        )

    if not response.content:
        return None
    return response.json()


async def create_otp_invite(
    tenant_id: str, scenario: str, email: str, ttl_hours: int
) -> dict[str, Any]:
    """Emite una invitación OTP. Devuelve el código en claro UNA sola vez."""
    return await _request(
        "POST",
        "/internal/invites",
        json={
            "tenant_id": tenant_id,
            "scenario": scenario,
            "kind": "otp",
            "email": email,
            "ttl_hours": ttl_hours,
        },
    )


# No hay start_demo_tenant a proposito: el aprovisionamiento lo arranca el
# invite-gate cuando el cliente canjea el codigo y se registra, porque necesita
# el organization_id y el user_id que nacen de ese registro. Ver
# services/demo-invite-gate/src/register_flow.gleam en nexus-demo-environment.


async def signal_extend(tenant_id: str, ttl_hours: int) -> Any:
    return await _request(
        "POST",
        f"/internal/workflows/demo-tenant/{tenant_id}/signal/extend",
        json={"ttl_hours": ttl_hours},
    )


async def signal_reset(tenant_id: str) -> Any:
    return await _request(
        "POST", f"/internal/workflows/demo-tenant/{tenant_id}/signal/reset"
    )


async def signal_teardown(tenant_id: str) -> Any:
    return await _request(
        "POST", f"/internal/workflows/demo-tenant/{tenant_id}/signal/teardown"
    )


async def get_tenant_state(tenant_id: str) -> dict[str, Any] | None:
    """Estado de un tenant, o None si el gate no lo conoce."""
    try:
        return await _request("GET", f"/internal/tenants/{tenant_id}")
    except NexusDemoError as exc:
        if exc.status_code == 404:
            return None
        raise


async def list_tenant_states(limit: int = 200) -> dict[str, dict[str, Any]]:
    """Estado de todos los tenants, indexado por tenant_id.

    Una sola llamada para pintar el listado entero: pedir el estado fila a fila
    convertiría un listado de 50 demos en 50 peticiones a otra EC2.
    """
    payload = await _request("GET", f"/internal/tenants?limit={int(limit)}")
    tenants = (payload or {}).get("tenants", [])
    return {t["tenant_id"]: t for t in tenants if t.get("tenant_id")}
