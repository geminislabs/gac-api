# API de Dispositivos

Endpoints para consulta de dispositivos. **Requiere autenticación**.

**Base URL**: `/api/v1`

---

## GET `/devices`

Obtiene la lista de dispositivos disponibles para el usuario autenticado.

### Descripción

Este endpoint actúa como proxy hacia siscom-admin-api o consulta un caché local para obtener la lista de dispositivos asociados al usuario.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |

### Response

**Status**: `200 OK`

```json
{
  "message": "Devices retrieved successfully",
  "data": [
    {
      "device_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "GPS Tracker 001",
      "type": "nexus",
      "status": "active"
    }
  ]
}
```

### Errores

| Status | Descripción                      |
|--------|----------------------------------|
| `403`  | Token inválido o expirado        |

### Ejemplo cURL

```bash
curl -X GET "http://localhost:8200/api/v1/devices" \
  -H "Authorization: Bearer <token>"
```

---

## Notas

- Este endpoint requiere autenticación con cualquier rol válido
- La respuesta puede variar dependiendo de la integración con siscom-admin-api
- Los datos pueden provenir de un caché local para mejorar el rendimiento
