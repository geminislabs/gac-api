# API de Usuarios

Endpoints para gestión de usuarios. **Todos los endpoints requieren rol `admin`**.

**Base URL**: `/api/v1`

---

## POST `/users`

Crea un nuevo usuario en el sistema.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |
| `Content-Type`  | `application/json`       | ✅        |

**Body**:

| Campo       | Tipo     | Requerido | Descripción                          |
|-------------|----------|-----------|--------------------------------------|
| `email`     | string   | ✅        | Email único del usuario              |
| `password`  | string   | ✅        | Contraseña (será hasheada)           |
| `full_name` | string   | ✅        | Nombre completo                      |
| `is_active` | boolean  | ❌        | Estado activo (default: `true`)      |
| `roles`     | string[] | ❌        | Lista de nombres de roles a asignar  |

```json
{
  "email": "newuser@example.com",
  "password": "SecurePassword123!",
  "full_name": "Juan Pérez",
  "is_active": true,
  "roles": ["user"]
}
```

### Response

**Status**: `201 Created`

```json
{
  "message": "User created successfully",
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "email": "newuser@example.com",
    "full_name": "Juan Pérez",
    "is_active": true,
    "roles": ["user"]
  }
}
```

### Errores

| Status | Descripción                      |
|--------|----------------------------------|
| `400`  | Email ya existe o datos inválidos|
| `403`  | Sin permisos (no es admin)       |

### Ejemplo cURL

```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePassword123!",
    "full_name": "Juan Pérez",
    "roles": ["user"]
  }'
```

---

## GET `/users`

Lista todos los usuarios del sistema con paginación.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |

**Query Parameters**:

| Parámetro | Tipo    | Default | Descripción                    |
|-----------|---------|---------|--------------------------------|
| `skip`    | integer | `0`     | Número de registros a omitir   |
| `limit`   | integer | `100`   | Número máximo de registros     |

### Response

**Status**: `200 OK`

```json
{
  "message": "Users retrieved successfully",
  "data": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "admin@example.com",
      "full_name": "Admin User",
      "is_active": true,
      "roles": ["admin"]
    },
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440001",
      "email": "user@example.com",
      "full_name": "Regular User",
      "is_active": true,
      "roles": ["user"]
    }
  ]
}
```

### Ejemplo cURL

```bash
curl -X GET "http://localhost:8000/api/v1/users?skip=0&limit=10" \
  -H "Authorization: Bearer <token>"
```

---

## GET `/users/{user_id}`

Obtiene los detalles de un usuario específico.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |

**Path Parameters**:

| Parámetro | Tipo | Descripción          |
|-----------|------|----------------------|
| `user_id` | UUID | ID único del usuario |

### Response

**Status**: `200 OK`

```json
{
  "message": "User retrieved successfully",
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "email": "user@example.com",
    "full_name": "Regular User",
    "is_active": true,
    "roles": ["user"]
  }
}
```

### Errores

| Status | Descripción           |
|--------|-----------------------|
| `404`  | Usuario no encontrado |
| `403`  | Sin permisos          |

### Ejemplo cURL

```bash
curl -X GET "http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440001" \
  -H "Authorization: Bearer <token>"
```

---

## PATCH `/users/{user_id}`

Actualiza parcialmente un usuario existente.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |
| `Content-Type`  | `application/json`       | ✅        |

**Path Parameters**:

| Parámetro | Tipo | Descripción          |
|-----------|------|----------------------|
| `user_id` | UUID | ID único del usuario |

**Body** (todos los campos son opcionales):

| Campo       | Tipo     | Descripción                     |
|-------------|----------|---------------------------------|
| `email`     | string   | Nuevo email                     |
| `password`  | string   | Nueva contraseña                |
| `full_name` | string   | Nuevo nombre completo           |
| `is_active` | boolean  | Nuevo estado activo             |
| `roles`     | string[] | Nueva lista de roles            |

```json
{
  "full_name": "Juan Carlos Pérez",
  "is_active": false
}
```

### Response

**Status**: `200 OK`

```json
{
  "message": "User updated successfully",
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "email": "user@example.com",
    "full_name": "Juan Carlos Pérez",
    "is_active": false,
    "roles": ["user"]
  }
}
```

### Errores

| Status | Descripción           |
|--------|-----------------------|
| `404`  | Usuario no encontrado |
| `403`  | Sin permisos          |

### Ejemplo cURL

```bash
curl -X PATCH "http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440001" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Juan Carlos Pérez"}'
```

---

## DELETE `/users/{user_id}`

Desactiva un usuario (soft delete). No elimina físicamente el registro.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |

**Path Parameters**:

| Parámetro | Tipo | Descripción          |
|-----------|------|----------------------|
| `user_id` | UUID | ID único del usuario |

### Response

**Status**: `200 OK`

```json
{
  "message": "User deactivated successfully",
  "data": true
}
```

### Errores

| Status | Descripción           |
|--------|-----------------------|
| `404`  | Usuario no encontrado |
| `403`  | Sin permisos          |

### Ejemplo cURL

```bash
curl -X DELETE "http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440001" \
  -H "Authorization: Bearer <token>"
```

---

## PATCH `/users/{user_id}/password`

Resetea la contraseña de un usuario (solo admin).

### Descripción

Permite a un administrador resetear la contraseña de cualquier usuario sin conocer la contraseña actual. Útil para soporte técnico cuando un usuario olvida su contraseña.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |
| `Content-Type`  | `application/json`       | ✅        |

**Path Parameters**:

| Parámetro | Tipo | Descripción          |
|-----------|------|----------------------|
| `user_id` | UUID | ID del usuario       |

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
  "message": "Password reset successfully",
  "data": true
}
```

### Errores

| Status | Descripción                      |
|--------|----------------------------------|
| `403`  | Sin permisos (no es admin)       |
| `404`  | Usuario no encontrado            |

### Ejemplo cURL

```bash
curl -X PATCH "http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440001/password" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"new_password": "NuevaContraseña123!"}'
```

---

## Notas

- Todos los endpoints requieren autenticación con rol `admin`
- Los IDs de usuario son UUIDs v4
- La eliminación es "soft delete" (solo desactiva `is_active`)
- Las contraseñas se almacenan hasheadas con Argon2
- El reset de contraseña no invalida los tokens existentes del usuario
