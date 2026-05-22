# API de Autenticación

Endpoints para autenticación y gestión de sesiones de usuario.

**Base URL**: `/api/v1`

---

## POST `/auth/login`

Autentica un usuario y retorna tokens de acceso.

### Request

**Content-Type**: `application/x-www-form-urlencoded`

| Campo      | Tipo   | Requerido | Descripción                    |
|------------|--------|-----------|--------------------------------|
| `username` | string | ✅        | Email del usuario              |
| `password` | string | ✅        | Contraseña del usuario         |

### Response

**Status**: `200 OK`

```json
{
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

### Errores

| Status | Descripción                      |
|--------|----------------------------------|
| `401`  | Credenciales incorrectas         |

### Ejemplo cURL

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=secretpassword"
```

---

## POST `/auth/refresh`

Genera un nuevo access token usando un refresh token válido.

### Request

**Query Parameters**:

| Parámetro       | Tipo   | Requerido | Descripción                    |
|-----------------|--------|-----------|--------------------------------|
| `refresh_token` | string | ✅        | Token de refresco válido       |

### Response

**Status**: `200 OK`

```json
{
  "message": "Token refreshed successfully",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

### Errores

| Status | Descripción                      |
|--------|----------------------------------|
| `401`  | Refresh token inválido o expirado|

### Ejemplo cURL

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh?refresh_token=eyJhbGciOi..."
```

---

## GET `/auth/me`

Obtiene el perfil del usuario autenticado actualmente.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |

### Response

**Status**: `200 OK`

```json
{
  "message": "User profile retrieved",
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "is_active": true,
    "roles": ["admin", "user"]
  }
}
```

### Errores

| Status | Descripción                      |
|--------|----------------------------------|
| `403`  | Token inválido o expirado        |
| `404`  | Usuario no encontrado            |
| `400`  | Usuario inactivo                 |

### Ejemplo cURL

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## PATCH `/auth/password`

Cambia la contraseña del usuario autenticado.

### Descripción

Permite al usuario autenticado cambiar su propia contraseña. No requiere la contraseña actual, solo un token de acceso válido.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |
| `Content-Type`  | `application/json`       | ✅        |

**Body**:

| Campo          | Tipo   | Requerido | Descripción              |
|----------------|--------|-----------|--------------------------|
| `new_password` | string | ✅        | Nueva contraseña         |

```json
{
  "new_password": "NuevaContraseña123!"
}
```

### Response

**Status**: `200 OK`

```json
{
  "message": "Password changed successfully",
  "data": true
}
```

### Errores

| Status | Descripción                      |
|--------|----------------------------------|
| `400`  | Error al cambiar contraseña      |
| `403`  | Token inválido o expirado        |

### Ejemplo cURL

```bash
curl -X PATCH "http://localhost:8000/api/v1/auth/password" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"new_password": "NuevaContraseña123!"}'
```

---

## Notas de Seguridad

- Los tokens de acceso tienen una expiración corta (configurada en `ACCESS_TOKEN_EXPIRES_MINUTES`)
- Los tokens de refresco tienen una expiración más larga (configurada en `REFRESH_TOKEN_EXPIRES_DAYS`)
- Siempre usar HTTPS en producción
- No almacenar tokens en localStorage; preferir httpOnly cookies cuando sea posible
- El cambio de contraseña no invalida los tokens existentes (considerar implementar revocación si es necesario)
