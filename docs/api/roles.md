# API de Roles

Endpoints para gestión de roles y permisos. **Todos los endpoints requieren rol `admin`**.

**Base URL**: `/api/v1`

---

## POST `/roles`

Crea un nuevo rol en el sistema.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |
| `Content-Type`  | `application/json`       | ✅        |

**Body** (RoleCreate):

| Campo  | Tipo   | Requerido | Descripción              |
|--------|--------|-----------|--------------------------|
| `name` | string | ✅        | Nombre único del rol     |

```json
{
  "name": "supervisor"
}
```

### Response

**Status**: `200 OK`

```json
{
  "message": "Role created successfully",
  "data": {
    "role_id": "550e8400-e29b-41d4-a716-446655440020",
    "name": "supervisor"
  }
}
```

### Errores

| Status | Descripción                      |
|--------|----------------------------------|
| `400`  | El rol ya existe                 |
| `403`  | Sin permisos (no es admin)       |

### Ejemplo cURL

```bash
curl -X POST "http://localhost:8000/api/v1/roles" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "supervisor"}'
```

---

## GET `/roles`

Lista todos los roles disponibles en el sistema.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |

### Response

**Status**: `200 OK`

```json
{
  "message": "Roles retrieved successfully",
  "data": [
    {
      "role_id": "550e8400-e29b-41d4-a716-446655440020",
      "name": "admin"
    },
    {
      "role_id": "550e8400-e29b-41d4-a716-446655440021",
      "name": "user"
    },
    {
      "role_id": "550e8400-e29b-41d4-a716-446655440022",
      "name": "supervisor"
    }
  ]
}
```

### Ejemplo cURL

```bash
curl -X GET "http://localhost:8000/api/v1/roles" \
  -H "Authorization: Bearer <admin_token>"
```

---

## POST `/users/{user_id}/roles/{role_id}`

Asigna un rol a un usuario específico.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |

**Path Parameters**:

| Parámetro | Tipo | Descripción          |
|-----------|------|----------------------|
| `user_id` | UUID | ID del usuario       |
| `role_id` | UUID | ID del rol a asignar |

### Response

**Status**: `200 OK`

```json
{
  "message": "Role assigned successfully",
  "data": true
}
```

### Errores

| Status | Descripción                         |
|--------|-------------------------------------|
| `400`  | Error al asignar rol                |
| `403`  | Sin permisos (no es admin)          |
| `404`  | Usuario o rol no encontrado         |

### Ejemplo cURL

```bash
curl -X POST "http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440001/roles/550e8400-e29b-41d4-a716-446655440020" \
  -H "Authorization: Bearer <admin_token>"
```

---

## DELETE `/users/{user_id}/roles/{role_id}`

Revoca un rol de un usuario específico.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |

**Path Parameters**:

| Parámetro | Tipo | Descripción          |
|-----------|------|----------------------|
| `user_id` | UUID | ID del usuario       |
| `role_id` | UUID | ID del rol a revocar |

### Response

**Status**: `200 OK`

```json
{
  "message": "Role revoked successfully",
  "data": true
}
```

### Errores

| Status | Descripción                         |
|--------|-------------------------------------|
| `403`  | Sin permisos (no es admin)          |
| `404`  | Asignación de rol no encontrada     |

### Ejemplo cURL

```bash
curl -X DELETE "http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440001/roles/550e8400-e29b-41d4-a716-446655440020" \
  -H "Authorization: Bearer <admin_token>"
```

---

## Modelo de Rol

| Campo     | Tipo   | Descripción                |
|-----------|--------|----------------------------|
| `role_id` | UUID   | Identificador único        |
| `name`    | string | Nombre del rol             |

---

## Roles Predefinidos

El sistema típicamente incluye los siguientes roles:

| Nombre    | Descripción                                     |
|-----------|-------------------------------------------------|
| `admin`   | Acceso completo al sistema                      |
| `user`    | Acceso básico a recursos propios                |

---

## Notas

- Todos los endpoints requieren autenticación con rol `admin`
- Los nombres de rol deben ser únicos
- Un usuario puede tener múltiples roles
- Los IDs de rol son UUIDs v4
- Revocar un rol no elimina el rol del sistema, solo lo desvincula del usuario
