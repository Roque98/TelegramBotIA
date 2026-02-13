# Generación de Tokens en tu Plataforma

Guía para implementar la generación de tokens en tu plataforma C# para integrar el Chat API.

---

## ⚠️ Importante

**Los tokens deben ser generados en TU plataforma**, NO en el Chat API de Python. El API solo **valida** los tokens que tú generas.

---

## Flujo de Generación

```
1. Usuario inicia chat → 2. Tu backend genera token → 3. Frontend recibe token
                                   ↓
                         4. Frontend envía token + mensaje al Chat API
                                   ↓
                         5. Chat API valida token y responde
```

---

## Implementación en C#

### 1. Método para Generar Token

```csharp
using Consola_Monitoreo;
using Newtonsoft.Json;
using System;

public class ChatTokenService
{
    private readonly Encrypt _encrypt;

    public ChatTokenService()
    {
        _encrypt = new Encrypt();
    }

    /// <summary>
    /// Genera un token encriptado para el Chat API.
    /// </summary>
    /// <param name="numeroEmpleado">Número de empleado</param>
    /// <returns>Token encriptado en Base64</returns>
    public string GenerarToken(int numeroEmpleado)
    {
        // 1. Crear objeto con datos del token
        var tokenData = new
        {
            numero_empleado = numeroEmpleado,
            timestamp = DateTime.Now.ToString("o")  // ISO 8601 format
        };

        // 2. Serializar a JSON
        string json = JsonConvert.SerializeObject(tokenData);

        // 3. Encriptar
        string token = _encrypt.Encriptar(json);

        return token;
    }

    /// <summary>
    /// Verifica si un token aún es válido (menos de 3 minutos de antigüedad).
    /// Útil para cachear tokens.
    /// </summary>
    public bool EsTokenValido(DateTime timestampToken)
    {
        var edad = DateTime.Now - timestampToken;
        return edad.TotalMinutes < 3;
    }
}
```

### 2. Endpoint API en tu Backend

**ASP.NET Web API:**

```csharp
using Microsoft.AspNetCore.Mvc;

[ApiController]
[Route("api/[controller]")]
public class ChatController : ControllerBase
{
    private readonly ChatTokenService _tokenService;

    public ChatController()
    {
        _tokenService = new ChatTokenService();
    }

    /// <summary>
    /// Genera token de autenticación para el chat.
    /// </summary>
    [HttpPost("generar-token")]
    public IActionResult GenerarToken([FromBody] TokenRequest request)
    {
        try
        {
            // Validar que el empleado existe y está autenticado
            // (implementar según tu lógica de autenticación)
            if (!ValidarEmpleado(request.NumeroEmpleado))
            {
                return Unauthorized(new { error = "Empleado no autorizado" });
            }

            // Generar token
            string token = _tokenService.GenerarToken(request.NumeroEmpleado);

            return Ok(new
            {
                success = true,
                token = token,
                numero_empleado = request.NumeroEmpleado,
                timestamp = DateTime.Now,
                valido_hasta = DateTime.Now.AddMinutes(3),
                duracion_minutos = 3
            });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new
            {
                success = false,
                error = "Error generando token",
                detalle = ex.Message
            });
        }
    }

    private bool ValidarEmpleado(int numeroEmpleado)
    {
        // TODO: Implementar validación según tu lógica
        // Ejemplo: verificar en BD, verificar sesión, etc.
        return true;
    }
}

public class TokenRequest
{
    public int NumeroEmpleado { get; set; }
}
```

**ASP.NET Framework (Web Forms/MVC):**

```csharp
using System.Web.Http;

public class ChatController : ApiController
{
    private readonly ChatTokenService _tokenService;

    public ChatController()
    {
        _tokenService = new ChatTokenService();
    }

    [HttpPost]
    [Route("api/chat/generar-token")]
    public IHttpActionResult GenerarToken([FromBody] TokenRequest request)
    {
        try
        {
            if (!ValidarEmpleado(request.NumeroEmpleado))
            {
                return Unauthorized();
            }

            string token = _tokenService.GenerarToken(request.NumeroEmpleado);

            return Ok(new
            {
                success = true,
                token = token,
                numero_empleado = request.NumeroEmpleado,
                timestamp = DateTime.Now,
                valido_hasta = DateTime.Now.AddMinutes(3)
            });
        }
        catch (Exception ex)
        {
            return InternalServerError(ex);
        }
    }

    private bool ValidarEmpleado(int numeroEmpleado)
    {
        // Implementar validación
        return true;
    }
}
```

### 3. Uso desde Frontend (JavaScript)

```javascript
// 1. Obtener token desde TU backend
async function obtenerToken(numeroEmpleado) {
    try {
        const response = await fetch('/api/chat/generar-token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                NumeroEmpleado: numeroEmpleado
            })
        });

        if (!response.ok) {
            throw new Error('Error obteniendo token');
        }

        const data = await response.json();
        return data.token;
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// 2. Enviar mensaje al Chat API de IRIS
async function enviarMensajeChat(token, mensaje) {
    try {
        const response = await fetch('http://localhost:5000/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                token: token,
                message: mensaje
            })
        });

        const data = await response.json();

        if (data.success) {
            return data.response;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// 3. Uso completo
async function iniciarChat(numeroEmpleado, mensaje) {
    try {
        // Obtener token de tu backend
        const token = await obtenerToken(numeroEmpleado);

        // Enviar mensaje al Chat API
        const respuesta = await enviarMensajeChat(token, mensaje);

        // Mostrar respuesta al usuario
        console.log('Respuesta del bot:', respuesta);
        return respuesta;
    } catch (error) {
        console.error('Error en el chat:', error);
        throw error;
    }
}

// Ejemplo de uso
iniciarChat(12345, 'Hola, ¿cuál es mi saldo?')
    .then(respuesta => {
        document.getElementById('chat-response').textContent = respuesta;
    })
    .catch(error => {
        document.getElementById('chat-error').textContent = 'Error: ' + error.message;
    });
```

---

## Optimizaciones

### 1. Cachear Tokens (Opcional)

Puedes cachear tokens para no generarlos en cada request:

```csharp
using System.Collections.Generic;
using System.Runtime.Caching;

public class ChatTokenService
{
    private readonly Encrypt _encrypt;
    private readonly MemoryCache _cache;

    public ChatTokenService()
    {
        _encrypt = new Encrypt();
        _cache = MemoryCache.Default;
    }

    public string ObtenerOGenerarToken(int numeroEmpleado)
    {
        string cacheKey = $"chat_token_{numeroEmpleado}";

        // Intentar obtener del cache
        var cachedToken = _cache.Get(cacheKey) as CachedToken;

        if (cachedToken != null && EsTokenValido(cachedToken.Timestamp))
        {
            return cachedToken.Token;
        }

        // Generar nuevo token
        string token = GenerarToken(numeroEmpleado);

        // Cachear por 2 minutos (menos de 3 para evitar expiración)
        var policy = new CacheItemPolicy
        {
            AbsoluteExpiration = DateTimeOffset.Now.AddMinutes(2)
        };

        _cache.Set(cacheKey, new CachedToken
        {
            Token = token,
            Timestamp = DateTime.Now
        }, policy);

        return token;
    }

    private class CachedToken
    {
        public string Token { get; set; }
        public DateTime Timestamp { get; set; }
    }
}
```

### 2. Validación de Seguridad

```csharp
public string GenerarToken(int numeroEmpleado)
{
    // 1. Validar que el número de empleado es válido
    if (numeroEmpleado <= 0)
    {
        throw new ArgumentException("Número de empleado inválido");
    }

    // 2. Verificar que el empleado existe en la BD
    if (!EmpleadoExiste(numeroEmpleado))
    {
        throw new UnauthorizedAccessException("Empleado no encontrado");
    }

    // 3. Verificar que el empleado tiene permisos para usar el chat
    if (!TienePermisoChat(numeroEmpleado))
    {
        throw new UnauthorizedAccessException("Sin permiso para usar el chat");
    }

    // 4. Generar token
    var tokenData = new
    {
        numero_empleado = numeroEmpleado,
        timestamp = DateTime.Now.ToString("o")
    };

    string json = JsonConvert.SerializeObject(tokenData);
    string token = _encrypt.Encriptar(json);

    // 5. Log (opcional)
    LogGeneracionToken(numeroEmpleado);

    return token;
}
```

---

## Testing

### Probar Generación de Token

```csharp
[TestMethod]
public void TestGenerarToken()
{
    var service = new ChatTokenService();
    int numeroEmpleado = 12345;

    string token = service.GenerarToken(numeroEmpleado);

    // Verificar que el token no está vacío
    Assert.IsNotNull(token);
    Assert.IsTrue(token.Length > 0);

    // Verificar que es Base64 válido
    try
    {
        Convert.FromBase64String(token);
    }
    catch
    {
        Assert.Fail("Token no es Base64 válido");
    }
}
```

### Probar con el Chat API (Integración)

```csharp
using System.Net.Http;
using Newtonsoft.Json;

[TestMethod]
public async Task TestIntegracionChatAPI()
{
    var service = new ChatTokenService();
    string token = service.GenerarToken(12345);

    var client = new HttpClient();
    var request = new
    {
        token = token,
        message = "Hola, esto es un test"
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

    Assert.IsTrue(response.IsSuccessStatusCode);

    string responseBody = await response.Content.ReadAsStringAsync();
    var data = JsonConvert.DeserializeObject<dynamic>(responseBody);

    Assert.AreEqual(true, data.success);
    Assert.IsNotNull(data.response);
}
```

---

## Troubleshooting

### "Token inválido: no se pudo desencriptar"

**Causa:** La clase `Encrypt` de C# no está usando los mismos parámetros.

**Solución:** Verificar que la clase `Encrypt` en C# tiene exactamente estos parámetros:
```csharp
Password = "m0n4pl1cBAZ.10"
SaltValue = "c9a5d2f21f00469ff48a60fe5311b2ff"
hashAlgorithm = "MD5"
PasswordIterations = 2
InitialVector = "bQBhAHIAaQANAAoA"
KeySize = 256
```

### "Token expirado"

**Causa:** El timestamp es demasiado antiguo.

**Solución:** Generar token nuevo antes de cada request o implementar cache con duración menor a 3 minutos.

### "JSON malformado"

**Causa:** El JSON no tiene el formato esperado.

**Solución:** Asegurar que el JSON tiene exactamente estos campos:
```json
{
  "numero_empleado": 12345,
  "timestamp": "2025-12-23T10:30:00"
}
```

---

## Referencias

- [Documentación del Chat API](CHAT_API_GUIDE.md)
- [Documentación de Encriptación](ENCRYPTION_COMPATIBILITY.md)
- [Endpoints API](API_ENDPOINTS.md)

---

**Última actualización:** 2025-12-23
**Versión:** 1.0.0
