# API de Órdenes

Endpoints para gestión de órdenes. **Requiere autenticación**.

**Base URL**: `/api/v1`

---

## POST `/orders`

Crea una nueva orden en el sistema.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |
| `Content-Type`  | `application/json`       | ✅        |

**Body** (OrderCreate):

| Campo       | Tipo   | Requerido | Descripción                    |
|-------------|--------|-----------|--------------------------------|
| `client_id` | UUID   | ✅        | ID del cliente                 |
| `items`     | array  | ✅        | Lista de items de la orden     |
| `notes`     | string | ❌        | Notas adicionales              |

```json
{
  "client_id": "550e8400-e29b-41d4-a716-446655440000",
  "items": [
    {
      "product_key": "nexus",
      "quantity": 2
    }
  ],
  "notes": "Entrega urgente"
}
```

### Response

**Status**: `201 Created`

```json
{
  "message": "Order created successfully",
  "data": {
    "order_id": "550e8400-e29b-41d4-a716-446655440001",
    "client_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "pending",
    "created_by": "550e8400-e29b-41d4-a716-446655440002",
    "created_at": "2025-12-16T10:00:00Z"
  }
}
```

### Errores

| Status | Descripción                      |
|--------|----------------------------------|
| `400`  | Datos de orden inválidos         |
| `403`  | Token inválido o expirado        |

### Ejemplo cURL

```bash
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "550e8400-e29b-41d4-a716-446655440000",
    "items": [{"product_key": "nexus", "quantity": 2}]
  }'
```

---

## GET `/orders/{order_id}`

Obtiene los detalles de una orden específica.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |

**Path Parameters**:

| Parámetro  | Tipo | Descripción          |
|------------|------|----------------------|
| `order_id` | UUID | ID único de la orden |

### Response

**Status**: `200 OK`

```json
{
  "message": "Order retrieved successfully",
  "data": {
    "order_id": "550e8400-e29b-41d4-a716-446655440001",
    "client_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "pending",
    "created_by": "550e8400-e29b-41d4-a716-446655440002",
    "created_at": "2025-12-16T10:00:00Z"
  }
}
```

### Errores

| Status | Descripción          |
|--------|----------------------|
| `404`  | Orden no encontrada  |
| `403`  | Token inválido       |

### Ejemplo cURL

```bash
curl -X GET "http://localhost:8000/api/v1/orders/550e8400-e29b-41d4-a716-446655440001" \
  -H "Authorization: Bearer <token>"
```

---

## GET `/clients/{client_id}/orders`

Obtiene todas las órdenes de un cliente específico.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |

**Path Parameters**:

| Parámetro   | Tipo | Descripción           |
|-------------|------|-----------------------|
| `client_id` | UUID | ID único del cliente  |

### Response

**Status**: `200 OK`

```json
{
  "message": "Orders retrieved successfully",
  "data": [
    {
      "order_id": "550e8400-e29b-41d4-a716-446655440001",
      "client_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "pending",
      "created_by": "550e8400-e29b-41d4-a716-446655440002",
      "created_at": "2025-12-16T10:00:00Z"
    },
    {
      "order_id": "550e8400-e29b-41d4-a716-446655440003",
      "client_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "created_by": "550e8400-e29b-41d4-a716-446655440002",
      "created_at": "2025-12-15T14:30:00Z"
    }
  ]
}
```

### Ejemplo cURL

```bash
curl -X GET "http://localhost:8000/api/v1/clients/550e8400-e29b-41d4-a716-446655440000/orders" \
  -H "Authorization: Bearer <token>"
```

---

## Notas

- Todos los endpoints requieren autenticación
- Los IDs de orden son UUIDs v4
- El campo `created_by` se asigna automáticamente con el ID del usuario autenticado
- Los estados posibles de una orden pueden incluir: `pending`, `processing`, `completed`, `cancelled`
