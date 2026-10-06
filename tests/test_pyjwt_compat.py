"""Las sesiones abiertas sobreviven al cambio de `python-jose` a PyJWT
(06/10/2026).

Los refresh tokens duran 7 días: al desplegar, producción tiene tokens que
firmó `python-jose`. Si PyJWT no los aceptara, se cerraría la sesión de todo
el mundo. El token de abajo lo firmó `python-jose` 3.5.0 con `SECRETO` y
caduca en 2100: es un literal a propósito, para que esta comprobación no
necesite tener `python-jose` instalado. El secreto va fijo aquí y no sale de
`settings`: en el CI `JWT_SECRET` lo pone `quality.yml` y no
`tests/bootstrap_env.py`, así que leerlo de `settings` hacía depender el test
del entorno.

El sentido inverso —tokens emitidos con PyJWT que `python-jose` acepte, por
si hubiera que volver a la imagen anterior— se verificó a mano al hacer el
cambio: mismos claims (`exp`, `sub`, `type`) y misma firma HS256.
"""

import jwt

from app.schemas.auth import TokenPayload

SECRETO = "test-jwt-secret-key-for-unit-tests"
FIRMADO_POR_PYTHON_JOSE_3_5_0 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjQxMDI0NDQ4MDAsInN1YiI6IjNmMmM5YTFlLTAwMDAtNDAwMC04MDAwLTAwMDAwMDAwMDAwMSIsInR5cGUiOiJyZWZyZXNoIn0.5rVhUREHD8Uqcw56iPFeVgw6r7AI8supBulBWPwwU6U"


def test_un_refresh_token_de_python_jose_se_sigue_aceptando():
    """Misma llamada a `jwt.decode` y mismo `TokenPayload` que
    `AuthService.refresh_token` y `get_current_user` (HS256)."""
    payload = jwt.decode(
        FIRMADO_POR_PYTHON_JOSE_3_5_0,
        SECRETO,
        algorithms=["HS256"],
    )
    datos = TokenPayload(**payload)

    assert datos.type == "refresh"
    assert str(datos.sub) == "3f2c9a1e-0000-4000-8000-000000000001"


def test_ese_token_con_otro_secreto_no_se_acepta():
    """Control: el test de arriba pasa por la firma, no por no mirarla."""
    try:
        jwt.decode(FIRMADO_POR_PYTHON_JOSE_3_5_0, "otro-secreto", algorithms=["HS256"])
    except jwt.InvalidSignatureError:
        return
    raise AssertionError("aceptó un token con la firma de otro secreto")
