[Docs](../index.md) › [Uso](README.md) › Guía del API REST

# Guía del API REST

El bot expone un servicio HTTP que permite integrar Iris en aplicaciones web, portales
corporativos o cualquier sistema que pueda hacer requests HTTP. Corre en el mismo proceso
que el bot de Telegram en el puerto **5000**.

---

## Autenticación

Todos los endpoints (excepto `/api/health`) requieren un **token AES+Base64** en el body.
El token es generado por la plataforma externa (C#) y contiene la identidad del usuario.

### Formatos de token soportados

**Formato nuevo** (plataforma C# actual):
```json
{
  "UserId": "1065129",
  "idGerencias": ["1"],
  "idConsola": "1",
  "fechaExpiracion": "2026-05-20T12:10:54"
}
```

**Formato legado**:
```json
{
  "numero_empleado": 12345,
  "timestamp": "2026-04-23T10:30:00"
}
```

### Reglas de validez

| Formato | Validación |
|---------|-----------|
| Nuevo (`fechaExpiracion`) | Válido mientras `fechaExpiracion` sea futura |
| Legado (`timestamp`) | Válido por **3 minutos** desde su creación |

### Generar token para pruebas locales

```bash
python scripts/generar_token.py 1065129
```

---

## Endpoints

### `POST /api/chat`

Envía un mensaje al orquestador de agentes y retorna la respuesta generada por el LLM.
La interacción queda registrada en `BotIAv2_InteractionLogs` con `channel = 'api'`.

**Request**
```json
{
  "token": "base64_del_token_encriptado",
  "message": "¿Qué alertas hay activas?"
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `token` | string | ✓ | Token encriptado AES+Base64 |
| `message` | string | ✓ | Texto del mensaje. No puede estar vacío |

**Response 200**
```json
{
  "success": true,
  "response": "Actualmente hay 3 alertas críticas...",
  "numero_empleado": 1065129,
  "timestamp": "2026-04-23T12:00:52"
}
```

**Response error**
```json
{
  "success": false,
  "error": "Token expirado: la fecha de expiración ya pasó",
  "error_code": "EXPIRED_TOKEN"
}
```

| Código HTTP | Descripción |
|-------------|-------------|
| 200 | Mensaje procesado exitosamente |
| 400 | Campo faltante o `message` vacío |
| 401 | Token inválido o expirado |
| 500 | Error interno |

**Ejemplo con cURL:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "token": "n1VAITKknem...",
    "message": "¿Qué alertas hay activas?"
  }'
```

---

### `POST /api/tickets`

Obtiene los tickets históricos de un equipo/IP de PRTG y genera un análisis de causa raíz
usando el LLM.

**Flujo interno:**
1. Consulta tickets históricos por IP (y sensor si se provee)
2. Si no se provee sensor, lo resuelve automáticamente desde alertas activas
3. Envía los tickets al LLM para análisis de patrones y causa raíz
4. Retorna el análisis generado

**Request**
```json
{
  "token": "base64_del_token_encriptado",
  "ip": "10.118.57.142",
  "sensor": "Memoria cache usada"
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `token` | string | ✓ | Token encriptado AES+Base64 |
| `ip` | string | ✓ | IP del equipo en PRTG |
| `sensor` | string | — | Nombre del sensor (ej: `"Memoria"`, `"CPU"`, `"Ping"`). Si se omite, se resuelve automáticamente |

**Response 200**
```json
{
  "success": true,
  "ip": "10.118.57.142",
  "sensor": "Memoria cache usada",
  "total_tickets": 3,
  "analisis": "**Análisis de tickets históricos**\n\n**Patrón identificado:** ...",
  "timestamp": "2026-04-23T12:47:09"
}
```

| Código HTTP | Descripción |
|-------------|-------------|
| 200 | Consulta y análisis completados |
| 400 | Campo `ip` faltante o vacío |
| 401 | Token inválido o expirado |
| 503 | Servicio no inicializado (bot aún arrancando) |
| 500 | Error interno |

---

### `POST /api/chat/validate-token`

Valida un token sin enviar ningún mensaje. Útil para verificar credenciales al inicio de sesión.

**Request**
```json
{
  "token": "base64_del_token_encriptado"
}
```

**Response 200 — token válido**
```json
{
  "success": true,
  "valid": true,
  "numero_empleado": 1065129,
  "timestamp_token": "2026-04-23T10:30:00",
  "edad_segundos": 45
}
```

**Response 200 — token inválido**
```json
{
  "success": true,
  "valid": false,
  "error": "Token expirado: la fecha de expiración ya pasó"
}
```

> Este endpoint siempre retorna HTTP 200. El resultado está en el campo `valid`.

---

### `GET /api/health`

Health check del servicio. No requiere autenticación.

```bash
curl http://localhost:5000/api/health
```

**Response 200**
```json
{
  "status": "ok",
  "timestamp": "2026-04-23T12:00:00"
}
```

---

## Códigos de error

| `error_code` | Descripción |
|--------------|-------------|
| `INVALID_TOKEN` | El token no pudo desencriptarse o le faltan campos |
| `EXPIRED_TOKEN` | El token venció (`fechaExpiracion` pasada o más de 3 min) |
| `MISSING_FIELD` | Falta un campo requerido en el body |
| `EMPTY_MESSAGE` | El campo `message` está vacío |
| `INVALID_CONTENT_TYPE` | El `Content-Type` no es `application/json` |
| `NOT_READY` | El bot aún está inicializándose |
| `PROCESSING_ERROR` | Error al procesar el mensaje con el agente |
| `INTERNAL_ERROR` | Error interno inesperado del servidor |

---

## Observabilidad

Las llamadas a `/api/chat` y `/api/tickets` quedan registradas en `BotIAv2_InteractionLogs`:

| Columna | Valor para canal API |
|---------|---------------------|
| `channel` | `api` |
| `idUsuario` | `numero_empleado` del token |
| `telegramChatId` | `NULL` |
| `telegramUsername` | `NULL` |

---

## Dashboard interactivo

El panel en `/admin` incluye una sección **API Reference** con documentación y playground
para probar los endpoints directamente desde el navegador.

---

**← Anterior** [Guía de administrador](guia-administrador.md) · [Índice](README.md) · **Siguiente →** [Configuración y despliegue](configuracion.md)
