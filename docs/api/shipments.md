# API de Envíos

Endpoints para gestión de envíos. **Requiere autenticación**.

**Base URL**: `/api/v1`

---

## POST `/shipments`

Crea un nuevo envío en el sistema.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |
| `Content-Type`  | `application/json`       | ✅        |

**Body** (ShipmentCreate):

| Campo            | Tipo   | Requerido | Descripción                      |
|------------------|--------|-----------|----------------------------------|
| `client_id`      | UUID   | ✅        | ID del cliente                   |
| `order_id`       | UUID   | ❌        | ID de la orden asociada          |
| `address`        | string | ✅        | Dirección de entrega             |
| `city`           | string | ✅        | Ciudad de entrega                |
| `postal_code`    | string | ❌        | Código postal                    |
| `contact_name`   | string | ❌        | Nombre del contacto              |
| `contact_phone`  | string | ❌        | Teléfono del contacto            |

```json
{
  "client_id": "550e8400-e29b-41d4-a716-446655440000",
  "order_id": "550e8400-e29b-41d4-a716-446655440001",
  "address": "Av. Principal 123",
  "city": "Ciudad de México",
  "postal_code": "06600",
  "contact_name": "Juan Pérez",
  "contact_phone": "+52 55 1234 5678"
}
```

### Response

**Status**: `201 Created`

```json
{
  "message": "Shipment created successfully",
  "data": {
    "shipment_id": "550e8400-e29b-41d4-a716-446655440030",
    "client_id": "550e8400-e29b-41d4-a716-446655440000",
    "order_id": "550e8400-e29b-41d4-a716-446655440001",
    "status": "pending",
    "address": "Av. Principal 123",
    "city": "Ciudad de México",
    "created_at": "2025-12-16T10:00:00Z"
  }
}
```

### Errores

| Status | Descripción                      |
|--------|----------------------------------|
| `400`  | Datos de envío inválidos         |
| `403`  | Token inválido o expirado        |

### Ejemplo cURL

```bash
curl -X POST "http://localhost:8200/api/v1/shipments" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "550e8400-e29b-41d4-a716-446655440000",
    "address": "Av. Principal 123",
    "city": "Ciudad de México"
  }'
```

---

## PATCH `/shipments/{shipment_id}/status`

Actualiza el estado de un envío específico.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |
| `Content-Type`  | `application/json`       | ✅        |

**Path Parameters**:

| Parámetro     | Tipo | Descripción           |
|---------------|------|-----------------------|
| `shipment_id` | UUID | ID único del envío    |

**Body** (ShipmentUpdateStatus):

| Campo    | Tipo   | Requerido | Descripción       |
|----------|--------|-----------|-------------------|
| `status` | string | ✅        | Nuevo estado      |

```json
{
  "status": "in_transit"
}
```

### Response

**Status**: `200 OK`

```json
{
  "message": "Shipment status updated successfully",
  "data": {
    "shipment_id": "550e8400-e29b-41d4-a716-446655440030",
    "client_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "in_transit",
    "address": "Av. Principal 123",
    "city": "Ciudad de México",
    "updated_at": "2025-12-16T12:30:00Z"
  }
}
```

### Errores

| Status | Descripción            |
|--------|------------------------|
| `404`  | Envío no encontrado    |
| `403`  | Token inválido         |

### Ejemplo cURL

```bash
curl -X PATCH "http://localhost:8200/api/v1/shipments/550e8400-e29b-41d4-a716-446655440030/status" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_transit"}'
```

---

## GET `/clients/{client_id}/shipments`

Obtiene todos los envíos de un cliente específico.

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
  "message": "Shipments retrieved successfully",
  "data": [
    {
      "shipment_id": "550e8400-e29b-41d4-a716-446655440030",
      "client_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "in_transit",
      "address": "Av. Principal 123",
      "city": "Ciudad de México",
      "created_at": "2025-12-16T10:00:00Z"
    },
    {
      "shipment_id": "550e8400-e29b-41d4-a716-446655440031",
      "client_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "delivered",
      "address": "Calle Secundaria 456",
      "city": "Guadalajara",
      "created_at": "2025-12-14T08:00:00Z"
    }
  ]
}
```

### Ejemplo cURL

```bash
curl -X GET "http://localhost:8200/api/v1/clients/550e8400-e29b-41d4-a716-446655440000/shipments" \
  -H "Authorization: Bearer <token>"
```

---

## Estados de Envío

| Estado       | Descripción                              |
|--------------|------------------------------------------|
| `pending`    | Envío creado, pendiente de procesamiento |
| `processing` | Preparando el envío                      |
| `in_transit` | En camino hacia el destino               |
| `delivered`  | Entregado exitosamente                   |
| `returned`   | Devuelto al remitente                    |
| `cancelled`  | Envío cancelado                          |

---

## Flujo de Estados

```
pending → processing → in_transit → delivered
                                  ↘ returned
           ↓
        cancelled
```

---

## Notas

- Todos los endpoints requieren autenticación
- Los IDs de envío son UUIDs v4
- Se recomienda actualizar el estado del envío conforme avanza en la cadena de entrega
- Los envíos pueden asociarse opcionalmente a una orden existente
