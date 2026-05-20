# API de Pagos

Endpoints para gestión de pagos. **Requiere autenticación**.

**Base URL**: `/api/v1`

---

## POST `/payments`

Registra un nuevo pago en el sistema.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |
| `Content-Type`  | `application/json`       | ✅        |

**Body** (PaymentCreate):

| Campo       | Tipo   | Requerido | Descripción                       |
|-------------|--------|-----------|-----------------------------------|
| `client_id` | UUID   | ✅        | ID del cliente                    |
| `order_id`  | UUID   | ❌        | ID de la orden asociada           |
| `amount`    | number | ✅        | Monto del pago                    |
| `method`    | string | ✅        | Método de pago (card, transfer, cash) |
| `reference` | string | ❌        | Referencia de la transacción      |

```json
{
  "client_id": "550e8400-e29b-41d4-a716-446655440000",
  "order_id": "550e8400-e29b-41d4-a716-446655440001",
  "amount": 150.00,
  "method": "card",
  "reference": "TXN-2025-001234"
}
```

### Response

**Status**: `201 Created`

```json
{
  "message": "Payment created successfully",
  "data": {
    "payment_id": "550e8400-e29b-41d4-a716-446655440010",
    "client_id": "550e8400-e29b-41d4-a716-446655440000",
    "order_id": "550e8400-e29b-41d4-a716-446655440001",
    "amount": 150.00,
    "method": "card",
    "status": "completed",
    "created_at": "2025-12-16T10:00:00Z"
  }
}
```

### Errores

| Status | Descripción                      |
|--------|----------------------------------|
| `400`  | Datos de pago inválidos          |
| `403`  | Token inválido o expirado        |

### Ejemplo cURL

```bash
curl -X POST "http://localhost:8000/api/v1/payments" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "550e8400-e29b-41d4-a716-446655440000",
    "amount": 150.00,
    "method": "card"
  }'
```

---

## GET `/payments/{payment_id}`

Obtiene los detalles de un pago específico.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |

**Path Parameters**:

| Parámetro    | Tipo | Descripción         |
|--------------|------|---------------------|
| `payment_id` | UUID | ID único del pago   |

### Response

**Status**: `200 OK`

```json
{
  "message": "Payment retrieved successfully",
  "data": {
    "payment_id": "550e8400-e29b-41d4-a716-446655440010",
    "client_id": "550e8400-e29b-41d4-a716-446655440000",
    "order_id": "550e8400-e29b-41d4-a716-446655440001",
    "amount": 150.00,
    "method": "card",
    "status": "completed",
    "created_at": "2025-12-16T10:00:00Z"
  }
}
```

### Errores

| Status | Descripción          |
|--------|----------------------|
| `404`  | Pago no encontrado   |
| `403`  | Token inválido       |

### Ejemplo cURL

```bash
curl -X GET "http://localhost:8000/api/v1/payments/550e8400-e29b-41d4-a716-446655440010" \
  -H "Authorization: Bearer <token>"
```

---

## GET `/clients/{client_id}/payments`

Obtiene todos los pagos de un cliente específico.

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
  "message": "Payments retrieved successfully",
  "data": [
    {
      "payment_id": "550e8400-e29b-41d4-a716-446655440010",
      "client_id": "550e8400-e29b-41d4-a716-446655440000",
      "amount": 150.00,
      "method": "card",
      "status": "completed",
      "created_at": "2025-12-16T10:00:00Z"
    },
    {
      "payment_id": "550e8400-e29b-41d4-a716-446655440011",
      "client_id": "550e8400-e29b-41d4-a716-446655440000",
      "amount": 75.50,
      "method": "transfer",
      "status": "pending",
      "created_at": "2025-12-15T14:30:00Z"
    }
  ]
}
```

### Ejemplo cURL

```bash
curl -X GET "http://localhost:8000/api/v1/clients/550e8400-e29b-41d4-a716-446655440000/payments" \
  -H "Authorization: Bearer <token>"
```

---

## Métodos de Pago Soportados

| Método     | Descripción                           |
|------------|---------------------------------------|
| `card`     | Pago con tarjeta de crédito/débito    |
| `transfer` | Transferencia bancaria                |
| `cash`     | Pago en efectivo                      |

## Estados de Pago

| Estado      | Descripción                          |
|-------------|--------------------------------------|
| `pending`   | Pago pendiente de confirmación       |
| `completed` | Pago completado exitosamente         |
| `failed`    | Pago fallido                         |
| `refunded`  | Pago reembolsado                     |

---

## Notas

- Todos los endpoints requieren autenticación
- Los IDs de pago son UUIDs v4
- Los montos se manejan con precisión decimal
- Las referencias de transacción son opcionales pero recomendadas para trazabilidad
