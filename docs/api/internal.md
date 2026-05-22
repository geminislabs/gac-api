# API Interna

Endpoints para comunicación interna entre servicios. **Requieren rol `admin`**.

**Base URL**: `/api/v1`

---

## POST `/internal/tokens/app`

Genera un token PASETO v4.local para comunicación segura interna de aplicaciones.

### Descripción

Este endpoint genera un token PASETO firmado con clave simétrica que permite a GAC comunicarse de forma segura con otras aplicaciones. El token tiene una expiración corta (5 minutos) por seguridad.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |

> ⚠️ El usuario autenticado debe tener el rol `admin`

### Response

**Status**: `200 OK`

```json
{
  "message": "Token generated successfully",
  "data": "v4.local.eyJpbnRlcm5hbF9pZCI6IjU1MGU4NDAwLWUyOWItNDFkNC1hNzE2LTQ0NjY1NTQ0MDAwMCIsInNlcnZpY2UiOiJnYWMiLCJyb2xlIjoiTkVYVVNfQURNSU4iLCJzY29wZSI6ImludGVybmFsLW5leHVzLWFkbWluIiwiaWF0IjoiMjAyNS0xMi0wOFQxMDowMDowMCswMDowMCIsImV4cCI6IjIwMjUtMTItMDhUMTA6MDU6MDArMDA6MDAifQ..."
}
```

### Payload del Token Generado

El token PASETO generado contiene los siguientes claims:

| Claim         | Tipo   | Descripción                              |
|---------------|--------|------------------------------------------|
| `internal_id` | string | UUID del usuario que generó el token     |
| `service`     | string | Servicio origen (`"gac"`)                |
| `role`        | string | Rol del token (`"GAC_ADMIN"`)            |
| `scope`       | string | Alcance (`"internal-gac-admin"`)         |
| `iat`         | string | Fecha de emisión (ISO 8601)              |
| `exp`         | string | Fecha de expiración (iat + 5 minutos)    |

### Ejemplo de Payload Decodificado

```json
{
  "internal_id": "550e8400-e29b-41d4-a716-446655440000",
  "service": "gac",
  "role": "GAC_ADMIN",
  "scope": "internal-gac-admin",
  "iat": "2025-12-08T10:00:00+00:00",
  "exp": "2025-12-08T10:05:00+00:00"
}
```

### Compatibilidad con Otros Servicios

Los tokens PASETO generados son **100% compatibles** con la función de validación de otros servicios:

```python
def decode_service_token(
    token: str,
    required_service: Optional[str] = None,
    required_role: Optional[str] = None,
) -> dict | None:
    # Valida expiración, scope, service y role
    # Retorna payload o None si inválido
```

**Scopes válidos aceptados**: `service-auth`, `internal-nexus-admin`, `internal-gac-admin`, `internal-app-admin`

### Errores

| Status | Descripción                                    |
|--------|------------------------------------------------|
| `403`  | Usuario no autenticado o sin rol `admin`       |

### Ejemplo cURL

```bash
curl -X POST "http://localhost:8000/api/v1/internal/tokens/app" \
  -H "Authorization: Bearer <admin_access_token>"
```

### Ejemplo de Uso en Python

```python
import httpx

# 1. Obtener token PASETO
response = httpx.post(
    "http://localhost:8000/api/v1/internal/tokens/app",
    headers={"Authorization": f"Bearer {admin_token}"}
)
paseto_token = response.json()["data"]

# 2. Usar el token para comunicarse con otras aplicaciones
app_response = httpx.get(
    "http://other-app-service/api/v1/some-endpoint",
    headers={"Authorization": f"Bearer {paseto_token}"}
)
```

### Validación del Token en Nexus (Python)

```python
import pyseto
from pyseto import Key

# En el servicio Nexus
secret_key = "tu-clave-secreta-compartida"
key = Key.new(version=4, purpose="local", key=secret_key)

# Decodificar y validar el token
token = pyseto.decode(key, paseto_token)
payload = token.payload  # dict con los claims
```

---

## POST `/internal/tokens/refresh`

Refresca un token PASETO existente generando uno nuevo con expiración renovada.

### Descripción

Este endpoint permite refrescar tokens PASETO que están próximos a expirar o que ya expiraron, generando un nuevo token con la misma información pero con una nueva fecha de expiración.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |
| `Content-Type`  | `application/json`       | ✅        |

**Body**:

```json
{
  "token": "v4.local.eyJpbnRlcm5hbF9pZCI6IjU1MGU4NDAwLWUyOWItNDFkNC1hNzE2LTQ0NjY1NTQ0MDAwMCIsInNlcnZpY2UiOiJnYWMiLCJyb2xlIjoiR0FDX0FETUlOIiwic2NvcGUiOiJpbnRlcm5hbC1nYWMtYWRtaW4iLCJpYXQiOiIyMDI1LTEyLTA4VDEwOjAwOjAwKzAwOjAwIiwiZXhwIjoiMjAyNS0xMi0wOFQxMDowNTowMCswMDowMCJ9..."
}
```

| Campo   | Tipo   | Requerido | Descripción                 |
|---------|--------|-----------|-----------------------------|
| `token` | string | ✅        | Token PASETO existente      |

### Response

**Status**: `200 OK`

```json
{
  "message": "Token refreshed successfully",
  "data": "v4.local.eyJpbnRlcm5hbF9pZCI6IjU1MGU4NDAwLWUyOWItNDFkNC1hNzE2LTQ0NjY1NTQ0MDAwMCIsInNlcnZpY2UiOiJnYWMiLCJyb2xlIjoiR0FDX0FETUlOIiwic2NvcGUiOiJpbnRlcm5hbC1nYWMtYWRtaW4iLCJpYXQiOiIyMDI1LTEyLTA4VDEwOjA1OjAwKzAwOjAwIiwiZXhwIjoiMjAyNS0xMi0wOFQxMDoxMDowMCswMDowMCJ9..."
}
```

### Errores

| Status | Descripción                                    |
|--------|------------------------------------------------|
| `400`  | Token inválido, expirado o malformado         |
| `403`  | Usuario no autenticado o sin rol `admin`       |

### Ejemplo cURL

```bash
curl -X POST "http://localhost:8000/api/v1/internal/tokens/refresh" \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d '{"token": "v4.local..."}'
```

### Ejemplo de Uso en Python

```python
import httpx

# Refrescar un token existente
response = httpx.post(
    "http://localhost:8000/api/v1/internal/tokens/refresh",
    headers={"Authorization": f"Bearer {admin_token}"},
    json={"token": existing_paseto_token}
)
new_paseto_token = response.json()["data"]
```

---

## GET `/internal/debug/user`

Endpoint de debugging para verificar información del usuario autenticado actual.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |

### Response

**Status**: `200 OK`

```json
{
  "message": "User debug info",
  "data": {
    "user_id": "9f5008c0-4c39-4da3-a3a6-c9a63a261296",
    "email": "gac-admin@geminislabs.com",
    "full_name": "System Manager",
    "is_active": true,
    "roles": ["admin"],
    "has_admin_role": true
  }
}
```

### Campos de respuesta

| Campo           | Tipo    | Descripción                              |
|-----------------|---------|------------------------------------------|
| `user_id`       | string  | UUID del usuario                         |
| `email`         | string  | Email del usuario                        |
| `full_name`     | string  | Nombre completo del usuario              |
| `is_active`     | boolean | Estado activo del usuario                |
| `roles`         | array   | Lista de nombres de roles asignados      |
| `has_admin_role`| boolean | Indica si el usuario tiene rol admin     |

### Errores

| Status | Descripción                                    |
|--------|------------------------------------------------|
| `403`  | Usuario no autenticado o sin rol `admin`       |

### Ejemplo cURL

```bash
curl -X GET "http://localhost:8000/api/v1/internal/debug/user" \
  -H "Authorization: Bearer <admin_access_token>"
```

---

## Configuración Requerida

Para que este endpoint funcione correctamente, se debe configurar la siguiente variable de entorno:

| Variable           | Descripción                                      |
|--------------------|--------------------------------------------------|
| `PASETO_SECRET_KEY`| Clave simétrica de 32 bytes (64 caracteres hex)  |

### Generar una clave válida

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Seguridad

- **PASETO v4.local**: Usa cifrado simétrico (XChaCha20-Poly1305) más seguro que JWT
- **Expiración corta**: El token expira en 5 minutos para minimizar el impacto de una filtración
- **Restricción de rol**: Solo usuarios con rol `admin` pueden generar estos tokens
- **Clave compartida**: La misma `PASETO_SECRET_KEY` debe configurarse en GAC y Nexus

---

## Diagrama de Flujo

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Cliente   │      │   GAC API   │      │    Nexus    │
│   (Admin)   │      │             │      │   Service   │
└──────┬──────┘      └──────┬──────┘      └──────┬──────┘
       │                    │                    │
       │ POST /internal/    │                    │
       │ tokens/app         │                    │
       │ ─────────────────► │                    │
       │                    │                    │
       │   paseto_token     │                    │
       │ ◄───────────────── │                    │
       │                    │                    │
       │                    │ Request +          │
       │                    │ paseto_token       │
       │                    │ ─────────────────► │
       │                    │                    │
       │                    │     Response       │
       │                    │ ◄───────────────── │
       │                    │                    │
```

---

## Diferencias entre JWT y PASETO

| Característica      | JWT                    | PASETO                     |
|---------------------|------------------------|----------------------------|
| Algoritmo           | Configurable (riesgoso)| Fijo por versión (seguro)  |
| Cifrado local       | No nativo              | v4.local (XChaCha20)       |
| Vulnerabilidades    | Múltiples conocidas    | Diseño resistente          |
| Tamaño del token    | Más pequeño            | Ligeramente mayor          |
