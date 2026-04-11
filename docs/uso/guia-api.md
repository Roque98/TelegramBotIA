# Guía del API REST

El bot expone un endpoint REST que permite integrar Amber en aplicaciones web, portales
corporativos o cualquier sistema que pueda hacer requests HTTP.

---

## Endpoint

```
POST /api/chat
```

### Headers

| Header | Valor |
|--------|-------|
| `Content-Type` | `application/json` |

### Body

```json
{
  "user_id": "12345",
  "message": "¿Cuántas ventas hubo ayer?",
  "token": "<token_encriptado_AES>",
  "session_id": "optional-session-uuid"
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `user_id` | string | Sí | ID del usuario (número de empleado como string) |
| `message` | string | Sí | Consulta en lenguaje natural |
| `token` | string | Sí | Token AES encriptado (ver sección de autenticación) |
| `session_id` | string | No | ID de sesión para agrupar interacciones |

### Respuesta exitosa

```json
{
  "success": true,
  "response": "Ayer se registraron *45 ventas* por un total de *$127.500*.",
  "numero_empleado": 12345
}
```

### Respuesta de error

```json
{
  "success": false,
  "error": "Token inválido o expirado",
  "code": "AUTH_FAILED"
}
```

---

## Autenticación con tokens AES

El API no usa JWT ni API keys tradicionales. Utiliza tokens encriptados con AES que contienen
el número de empleado y un timestamp. El token tiene un TTL de 3 minutos por defecto.

### Estructura del token (antes de encriptar)

```
<numero_empleado>:<timestamp_unix>
```

Ejemplo:
```
12345:1712500000
```

### Encriptar desde Python

```python
from src.utils.encryption_util import EncryptionUtil

encryptor = EncryptionUtil(key="tu_clave_aes_de_32_chars")
token = encryptor.encrypt("12345:1712500000")
# → "U2FsdGVkX1+abc123..."
```

### Encriptar desde C#

```csharp
using System.Security.Cryptography;
using System.Text;

public static string EncryptAES(string plainText, string key)
{
    byte[] keyBytes = Encoding.UTF8.GetBytes(key.PadRight(32).Substring(0, 32));
    using var aes = Aes.Create();
    aes.Key = keyBytes;
    aes.GenerateIV();
    // ... (ver docs/api/ENCRYPTION_COMPATIBILITY.md para implementación completa)
}
```

La clave AES se configura en la variable de entorno `ENCRYPTION_KEY` (ver [configuracion.md](configuracion.md)).

---

## Ejemplo completo con cURL

```bash
# 1. Generar token (usando el script de utilidad)
python scripts/generate_token.py --employee 12345

# Output: U2FsdGVkX1+xyz...

# 2. Hacer la request
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "12345",
    "message": "¿Cuántas ventas hubo ayer?",
    "token": "U2FsdGVkX1+xyz..."
  }'
```

## Ejemplo completo con Python (requests)

```python
import requests
import time
from src.utils.encryption_util import EncryptionUtil

def chat_with_amber(employee_id: int, message: str, aes_key: str) -> dict:
    token_plain = f"{employee_id}:{int(time.time())}"
    token = EncryptionUtil(key=aes_key).encrypt(token_plain)

    response = requests.post(
        "http://localhost:5000/api/chat",
        json={
            "user_id": str(employee_id),
            "message": message,
            "token": token,
        },
        timeout=30,
    )
    return response.json()

result = chat_with_amber(12345, "¿Cuántas ventas hubo ayer?", "mi_clave_de_32_caracteres_aqui")
print(result["response"])
```

---

## Códigos de error

| Código HTTP | `code` | Descripción |
|-------------|--------|-------------|
| 401 | `AUTH_FAILED` | Token inválido, malformado o expirado |
| 403 | `PERMISSION_DENIED` | Usuario sin permisos para el recurso solicitado |
| 404 | `USER_NOT_FOUND` | El `user_id` no existe en el sistema |
| 422 | `VALIDATION_ERROR` | Body malformado o campos faltantes |
| 500 | `INTERNAL_ERROR` | Error interno del servidor |
| 503 | `SERVICE_UNAVAILABLE` | LLM o base de datos no disponible |

---

## Notas de integración

- El TTL del token es de **3 minutos** desde la generación. Generá el token justo antes de
  hacer el request.
- Las respuestas incluyen formato Markdown de Telegram (`*negrita*`, `_cursiva_`). Si tu
  interfaz no soporta Markdown, podés hacer strip del formato antes de mostrar al usuario.
- El campo `numero_empleado` en la respuesta confirma qué usuario procesó la request.
- No hay paginación: si la respuesta es muy larga, Amber la divide en múltiples párrafos
  dentro del mismo campo `response`.

---

**← Anterior** [Guía de administrador](guia-administrador.md) · [Índice](README.md) · **Siguiente →** [Configuración y despliegue](configuracion.md)
