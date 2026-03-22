# Guía del Chat API Middleware

Documentación completa para integrar el chat de IRIS en plataformas externas mediante autenticación con tokens encriptados.

---

## Tabla de Contenidos

- [Introducción](#introducción)
- [Arquitectura](#arquitectura)
- [Autenticación con Tokens](#autenticación-con-tokens)
- [Endpoints Disponibles](#endpoints-disponibles)
- [Integración](#integración)
- [Herramientas de Desarrollo](#herramientas-de-desarrollo)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Seguridad](#seguridad)

---

## Introducción

El **Chat API Middleware** permite integrar el bot IRIS en cualquier plataforma externa (web, móvil, aplicaciones de terceros) mediante una API REST simple con autenticación basada en tokens encriptados.

### Características

✅ Autenticación sin necesidad de gestionar sesiones JWT
✅ Tokens encriptados con expiración automática (3 minutos)
✅ Fácil integración desde JavaScript, Python, C#, etc.
✅ Validación de tokens antes de enviar mensajes
✅ Compatible con el sistema de encriptación C# existente

---

## Arquitectura

```
┌───────────────────────────────────────────────────────────────┐
│                    TU PLATAFORMA (C#)                         │
│                                                               │
│  1. Usuario solicita chat                                    │
│  2. Tu backend genera token:                                 │
│     - Crear JSON: {numero_empleado, timestamp}              │
│     - Encriptar con clase Encrypt                           │
│     - Enviar token al frontend                              │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        │ 3. Frontend envía request con token
                        ▼
           ┌────────────────────────┐
           │   Chat API Middleware  │
           │   (Python/Flask)       │
           │                        │
           │  POST /api/chat        │
           │  {                     │
           │    token: "...",       │
           │    message: "..."      │
           │  }                     │
           └────────┬───────────────┘
                    │
                    │ 4. Validar token
                    │    - Desencriptar
                    │    - Verificar timestamp < 3 min
                    │    - Extraer numero_empleado
                    ▼
           ┌─────────────────────────┐
           │  Token válido?          │
           └────┬──────────────┬─────┘
                │ Sí           │ No
                ▼              ▼
       ┌────────────────┐  ┌──────────────┐
       │ IRIS Bot Agent │  │ Error 401    │
       │ - Procesar     │  │ Token        │
       │ - Generar      │  │ inválido     │
       │   respuesta    │  └──────────────┘
       └────────┬───────┘
                │
                │ 6. Retornar respuesta
                ▼
    ┌──────────────────────────┐
    │  JSON Response           │
    │  {                       │
    │    success: true,        │
    │    response: "...",      │
    │    numero_empleado: ...  │
    │  }                       │
    └──────────────────────────┘
                │
                │ 7. Frontend muestra respuesta
                ▼
┌───────────────────────────────────────────────────────────────┐
│                    TU PLATAFORMA                              │
│  - Mostrar respuesta del bot al usuario                      │
└───────────────────────────────────────────────────────────────┘
```

**⚠️ IMPORTANTE:** El token SIEMPRE se genera en TU plataforma (C#), NO en el Chat API.

---

## Autenticación con Tokens

### Estructura del Token

El token contiene un JSON encriptado:

```json
{
  "numero_empleado": 12345,
  "timestamp": "2025-12-23T10:30:00"
}
```

### Proceso de Generación

⚠️ **IMPORTANTE:** Los tokens deben ser generados por **tu plataforma externa**, NO por el API de Python.

**C# (Plataforma que integra el chat):**
```csharp
using Consola_Monitoreo;
using Newtonsoft.Json;

public string GenerarTokenChat(int numeroEmpleado)
{
    var encrypt = new Encrypt();

    var tokenData = new {
        numero_empleado = numeroEmpleado,
        timestamp = DateTime.Now.ToString("o")  // ISO 8601
    };

    string json = JsonConvert.SerializeObject(tokenData);
    string token = encrypt.Encriptar(json);

    return token;
}

// Uso:
string token = GenerarTokenChat(12345);
// Token: "X9pycVZHvG1UcTtwRKSjRukBr7gfJgbP..."
```

**Solo para testing/desarrollo local (Python):**
```bash
# ⚠️ Solo usar para testing local, NO en producción
python scripts/generar_token.py 12345
```

**Desde código Python (solo testing):**
```python
# ⚠️ Solo usar para testing local, NO en producción
from src.auth.token_middleware import generar_token

token = generar_token(numero_empleado=12345)
```

### Validación del Token

El token es válido si:
1. ✅ Se puede desencriptar correctamente
2. ✅ Contiene `numero_empleado` y `timestamp` válidos
3. ✅ El timestamp no tiene más de 3 minutos de antigüedad
4. ✅ El timestamp no es del futuro

---

## Endpoints Disponibles

### 1. POST /api/chat

Enviar mensaje al chat.

**Request:**
```http
POST /api/chat HTTP/1.1
Content-Type: application/json

{
  "token": "X9pycVZHvG1UcTtwRKSjRukBr7gfJgbP...",
  "message": "¿Cuál es el estado de mi orden?"
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "response": "Tu orden #12345 está en proceso de envío.",
  "numero_empleado": 12345,
  "timestamp": "2025-12-23T10:33:15"
}
```

**Response (Error - 401):**
```json
{
  "success": false,
  "error": "Token expirado: han pasado 5 minutos (máximo 3)",
  "error_code": "EXPIRED_TOKEN"
}
```

### 2. POST /api/chat/validate-token

Validar token sin enviar mensaje.

**Request:**
```json
{
  "token": "X9pycVZHvG1UcTtwRKSjRukBr7gfJgbP..."
}
```

**Response:**
```json
{
  "success": true,
  "valid": true,
  "numero_empleado": 12345,
  "timestamp_token": "2025-12-23T10:30:00",
  "edad_segundos": 45
}
```

### 3. POST /api/chat/generate-token

⚠️ **ENDPOINT DESHABILITADO** - Los tokens se generan en la plataforma externa.

**Response (501):**
```json
{
  "success": false,
  "error": "Este endpoint está deshabilitado. Los tokens deben ser generados por la plataforma externa.",
  "error_code": "NOT_IMPLEMENTED"
}
```

**Generar tokens en tu plataforma (C#):**
Ver sección [Autenticación con Tokens](#autenticación-con-tokens) para código completo.

### 4. GET /api/health

Health check.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-12-23T10:30:00"
}
```

---

## Integración

### JavaScript / React

```javascript
// 1. Obtener token desde TU backend/plataforma
// El token debe ser generado por tu servidor C# usando la clase Encrypt
async function obtenerTokenDesdeMiBackend(numeroEmpleado) {
  // Llamar a TU API que genera el token (no al Chat API)
  const response = await fetch('/tu-api/generar-token-chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({numero_empleado: numeroEmpleado})
  });
  const data = await response.json();
  return data.token;  // Token generado por tu backend C#
}

// 2. Enviar mensaje al Chat API de IRIS
async function enviarMensaje(token, mensaje) {
  const response = await fetch('http://localhost:5000/api/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({token, message: mensaje})
  });

  const data = await response.json();

  if (data.success) {
    return data.response;
  } else {
    throw new Error(data.error);
  }
}

// 3. Uso
const token = await obtenerTokenDesdeMiBackend(12345);
const respuesta = await enviarMensaje(token, '¿Cuál es mi saldo?');
console.log(respuesta);
```

**Implementación del endpoint en tu backend C#:**
```csharp
// En tu servidor C# (tu-api/generar-token-chat)
[HttpPost("generar-token-chat")]
public IActionResult GenerarTokenChat([FromBody] TokenRequest request)
{
    var encrypt = new Encrypt();

    var tokenData = new {
        numero_empleado = request.NumeroEmpleado,
        timestamp = DateTime.Now.ToString("o")
    };

    string json = JsonConvert.SerializeObject(tokenData);
    string token = encrypt.Encriptar(json);

    return Ok(new { token });
}
```

### Python / Requests

```python
import requests
from src.auth.token_middleware import generar_token

# 1. Generar token
token = generar_token(12345)

# 2. Enviar mensaje
response = requests.post(
    'http://localhost:5000/api/chat',
    json={
        'token': token,
        'message': '¿Cuál es mi saldo?'
    }
)

# 3. Procesar respuesta
if response.status_code == 200:
    data = response.json()
    print(f"Respuesta: {data['response']}")
else:
    print(f"Error: {response.json()['error']}")
```

### C# / HttpClient

```csharp
using System.Net.Http;
using System.Text;
using Newtonsoft.Json;
using Consola_Monitoreo;

// 1. Generar token
var encrypt = new Encrypt();
var tokenData = new {
    numero_empleado = 12345,
    timestamp = DateTime.Now.ToString("o")
};
string json = JsonConvert.SerializeObject(tokenData);
string token = encrypt.Encriptar(json);

// 2. Enviar mensaje
var client = new HttpClient();
var request = new {
    token = token,
    message = "¿Cuál es mi saldo?"
};

var content = new StringContent(
    JsonConvert.SerializeObject(request),
    Encoding.UTF8,
    "application/json"
);

var response = await client.PostAsync(
    "http://localhost:5000/api/chat",
    content
);

// 3. Procesar respuesta
string responseBody = await response.Content.ReadAsStringAsync();
var data = JsonConvert.DeserializeObject<dynamic>(responseBody);

if (data.success == true) {
    Console.WriteLine($"Respuesta: {data.response}");
} else {
    Console.WriteLine($"Error: {data.error}");
}
```

---

## Herramientas de Desarrollo

### 1. Generar Tokens

**Comando:**
```bash
# Simple
python scripts/generar_token.py 12345

# Verbose (con detalles)
python scripts/generar_token.py --verbose 12345

# JSON (para integración)
python scripts/generar_token.py --json 12345

# Múltiples empleados
python scripts/generar_token.py 12345 54321 99999
```

### 2. Validar Tokens

**Comando:**
```bash
# Validar token
python scripts/generar_token.py --validate "X9pycVZHvG1UcTtwRKSjRukBr7gfJgbP..."

# Validar con detalles
python scripts/generar_token.py --validate --verbose "X9pycVZHvG1UcTtwRKSjRukBr7gfJgbP..."
```

### 3. Ejecutar el Servidor

**Comando:**
```bash
python src/api/chat_endpoint.py
```

**Salida:**
```
* Running on http://0.0.0.0:5000
* Debug mode: on
```

### 4. Ejemplos Interactivos

**Comando:**
```bash
python examples/ejemplo_chat_api.py
```

Ejecuta 7 ejemplos diferentes de uso del API.

---

## Testing

### Tests Unitarios

```bash
# Todos los tests de token middleware
pytest tests/auth/test_token_middleware.py -v

# Test específico
pytest tests/auth/test_token_middleware.py::TestTokenMiddleware::test_generar_token_valido -v

# Con cobertura
pytest tests/auth/test_token_middleware.py --cov=src.auth.token_middleware
```

### Tests de Integración (Manual)

```bash
# 1. Iniciar servidor
python src/api/chat_endpoint.py

# 2. En otra terminal, ejecutar ejemplos
python examples/ejemplo_chat_api.py

# 3. O usar cURL
TOKEN=$(python scripts/generar_token.py 12345)
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"token\": \"$TOKEN\", \"message\": \"Hola\"}"
```

---

## Troubleshooting

### Error: "Token inválido: no se pudo desencriptar"

**Causa:** El token no es Base64 válido o no fue encriptado correctamente.

**Solución:**
```python
# Verificar que el token se generó correctamente
from src.auth.token_middleware import generar_token
token = generar_token(12345)
print(f"Token válido: {token}")
```

### Error: "Token expirado"

**Causa:** Han pasado más de 3 minutos desde que se generó el token.

**Solución:**
```python
# Generar token nuevo
token = generar_token(12345)
# Usarlo inmediatamente
```

### Error: "Falta campo 'message'"

**Causa:** El request body no incluye el campo `message`.

**Solución:**
```javascript
// Asegurar que ambos campos están presentes
fetch('/api/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    token: token,      // ✓
    message: mensaje   // ✓
  })
});
```

### Error: ConnectionRefusedError

**Causa:** El servidor no está corriendo.

**Solución:**
```bash
# Iniciar el servidor
python src/api/chat_endpoint.py
```

---

## Seguridad

### Buenas Prácticas

1. **Tokens de corta duración**: Los tokens expiran en 3 minutos
2. **HTTPS en producción**: Siempre usar HTTPS
3. **No exponer generate-token en producción**: Deshabilitar o proteger endpoint
4. **Validar inputs**: El API valida todos los inputs
5. **Logging**: Todos los errores se registran para auditoría

### Configuración de Producción

```python
# src/api/chat_endpoint.py

# Deshabilitar endpoint de generación de tokens
@app.route('/api/chat/generate-token', methods=['POST'])
def generate_token():
    if not app.debug:
        return jsonify({
            "success": False,
            "error": "Endpoint no disponible en producción"
        }), 403
    # ... resto del código
```

### Rate Limiting (Recomendado)

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.json.get('token', 'anonymous')
)

@app.route('/api/chat', methods=['POST'])
@limiter.limit("10 per minute")
def chat():
    # ... código existente
```

---

## Referencias

- [Documentación de Endpoints](API_ENDPOINTS.md)
- [Documentación de Encriptación](ENCRYPTION_COMPATIBILITY.md)
- [Ejemplos de Uso](../examples/ejemplo_chat_api.py)
- [Tests](../tests/auth/test_token_middleware.py)

---

**Última actualización:** 2025-12-23
**Versión:** 1.0.0
**Estado:** ✅ Producción Ready
