# GAC API Reference

Documentación completa de la API de GAC.

**Base URL**: `http://localhost:8200/api/v1`

---

## Índice de Documentación

| Módulo | Descripción | Autenticación |
|--------|-------------|---------------|
| [Autenticación](api/auth.md) | Login, refresh token, perfil de usuario | Público / Bearer |
| [Usuarios](api/users.md) | CRUD de usuarios | Admin |
| [Roles](api/roles.md) | Gestión de roles y permisos | Admin |
| [Órdenes](api/orders.md) | Gestión de órdenes de compra | Bearer |
| [Pagos](api/payments.md) | Registro y consulta de pagos | Bearer |
| [Envíos](api/shipments.md) | Gestión de envíos y tracking | Bearer |
| [Productos](api/products.md) | Catálogo de productos | Bearer |
| [Dispositivos](api/devices.md) | Consulta de dispositivos | Bearer |
| [API Interna](api/internal.md) | Tokens para comunicación entre servicios | Admin |

---

## Resumen de Endpoints

### Autenticación (`/auth`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/auth/login` | Autenticar usuario |
| `POST` | `/auth/refresh` | Refrescar access token |
| `GET` | `/auth/me` | Obtener perfil del usuario actual |
| `PATCH` | `/auth/password` | Cambiar contraseña propia |

### Usuarios (`/users`) - Admin Only

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/users` | Crear usuario |
| `GET` | `/users` | Listar usuarios |
| `GET` | `/users/{user_id}` | Obtener usuario |
| `PATCH` | `/users/{user_id}` | Actualizar usuario |
| `PATCH` | `/users/{user_id}/password` | Resetear contraseña |
| `DELETE` | `/users/{user_id}` | Desactivar usuario |

### Roles (`/roles`) - Admin Only

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/roles` | Crear rol |
| `GET` | `/roles` | Listar roles |
| `POST` | `/users/{user_id}/roles/{role_id}` | Asignar rol a usuario |
| `DELETE` | `/users/{user_id}/roles/{role_id}` | Revocar rol de usuario |

### Órdenes (`/orders`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/orders` | Crear orden |
| `GET` | `/orders/{order_id}` | Obtener orden |
| `GET` | `/clients/{client_id}/orders` | Órdenes de un cliente |

### Pagos (`/payments`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/payments` | Registrar pago |
| `GET` | `/payments/{payment_id}` | Obtener pago |
| `GET` | `/clients/{client_id}/payments` | Pagos de un cliente |

### Envíos (`/shipments`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/shipments` | Crear envío |
| `PATCH` | `/shipments/{shipment_id}/status` | Actualizar estado |
| `GET` | `/clients/{client_id}/shipments` | Envíos de un cliente |

### Productos (`/products`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/products` | Listar productos |
| `POST` | `/products` | Crear producto |

### Dispositivos (`/devices`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/devices` | Listar dispositivos |

### API Interna (`/internal`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/internal/tokens/nexus` | Generar token PASETO para Nexus |

---

## Autenticación

La API utiliza autenticación basada en tokens JWT (Bearer tokens).

### Obtener Token

```bash
curl -X POST "http://localhost:8200/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=secretpassword"
```

### Usar Token

```bash
curl -X GET "http://localhost:8200/api/v1/auth/me" \
  -H "Authorization: Bearer <access_token>"
```

---

## Formato de Respuesta

Todas las respuestas siguen el formato estándar `ResponseModel`:

```json
{
  "message": "Descripción del resultado",
  "data": { ... }
}
```

### Códigos de Estado Comunes

| Código | Descripción |
|--------|-------------|
| `200` | Operación exitosa |
| `201` | Recurso creado |
| `400` | Error en la solicitud |
| `401` | No autenticado |
| `403` | Sin permisos |
| `404` | Recurso no encontrado |
| `500` | Error interno del servidor |

---

## Tipos de Datos Comunes

### UUID
Todos los IDs son UUIDs v4 en formato string:
```
"550e8400-e29b-41d4-a716-446655440000"
```

### Fechas
Las fechas se devuelven en formato ISO 8601:
```
"2025-12-16T10:00:00Z"
```

---

## Paginación

Algunos endpoints soportan paginación con los parámetros:

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `skip` | integer | `0` | Registros a omitir |
| `limit` | integer | `100` | Máximo de registros |

Ejemplo:
```bash
curl "http://localhost:8200/api/v1/users?skip=0&limit=10"
```

---

## Notas de Seguridad

- Siempre usar HTTPS en producción
- Los tokens de acceso tienen expiración corta
- Los refresh tokens tienen expiración más larga
- Las contraseñas se almacenan hasheadas con Argon2
- Los tokens internos (PASETO) expiran en 5 minutos
