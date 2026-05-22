# API de Productos

Endpoints para gestión de productos. **Requiere autenticación**.

**Base URL**: `/api/v1`

---

## GET `/products`

Obtiene la lista de todos los productos disponibles.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |

### Response

**Status**: `200 OK`

```json
{
  "message": "Products retrieved successfully",
  "data": [
    {
      "key": "nexus",
      "name": "Nexus",
      "description": "GPS Tracking Device"
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
curl -X GET "http://localhost:8000/api/v1/products" \
  -H "Authorization: Bearer <token>"
```

---

## POST `/products`

Crea un nuevo producto en el sistema.

### Request

**Headers**:

| Header          | Valor                    | Requerido |
|-----------------|--------------------------|-----------|
| `Authorization` | `Bearer <access_token>`  | ✅        |
| `Content-Type`  | `application/json`       | ✅        |

**Body** (Product):

| Campo         | Tipo   | Requerido | Descripción                          |
|---------------|--------|-----------|--------------------------------------|
| `key`         | string | ✅        | Clave única del producto             |
| `name`        | string | ✅        | Nombre del producto                  |
| `description` | string | ✅        | Descripción del producto             |

```json
{
  "key": "nexus-pro",
  "name": "Nexus Pro",
  "description": "GPS Tracking Device with advanced features"
}
```

### Response

**Status**: `200 OK`

```json
{
  "message": "Product created successfully",
  "data": {
    "key": "nexus-pro",
    "name": "Nexus Pro",
    "description": "GPS Tracking Device with advanced features"
  }
}
```

### Errores

| Status | Descripción                      |
|--------|----------------------------------|
| `400`  | La clave del producto ya existe  |
| `403`  | Token inválido o expirado        |

### Ejemplo cURL

```bash
curl -X POST "http://localhost:8000/api/v1/products" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "nexus-pro",
    "name": "Nexus Pro",
    "description": "GPS Tracking Device with advanced features"
  }'
```

---

## Modelo de Producto

| Campo         | Tipo   | Descripción                                |
|---------------|--------|--------------------------------------------|
| `key`         | string | Identificador único del producto (slug)    |
| `name`        | string | Nombre para mostrar del producto           |
| `description` | string | Descripción detallada del producto         |

---

## Productos Predefinidos

El sistema incluye los siguientes productos por defecto:

| Key     | Nombre | Descripción          |
|---------|--------|----------------------|
| `nexus` | Nexus  | GPS Tracking Device  |

---

## Notas

- Todos los endpoints requieren autenticación
- La clave (`key`) del producto debe ser única en el sistema
- Los productos se almacenan en memoria (no persistentes en la versión actual)
- Se recomienda usar claves en formato slug (minúsculas, sin espacios, guiones permitidos)
