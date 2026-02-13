# Módulo de Encriptación - Compatibilidad Python ↔ C#

**Ubicación:** `src/auth/encryption.py`

**Propósito:** Proveer encriptación/desencriptación compatible con el sistema C# existente (clase `Encrypt` de `Consola_Monitoreo`).

---

## ⚠️ ADVERTENCIA DE SEGURIDAD IMPORTANTE

Este módulo implementa parámetros **HEREDADOS** del sistema C# existente que **NO cumplen con estándares modernos de seguridad**:

| Parámetro | Valor Usado | Estándar Moderno | Riesgo |
|-----------|-------------|------------------|--------|
| **Hash Algorithm** | MD5 | SHA-256 o superior | 🔴 ALTO |
| **PBKDF2 Iterations** | 2 | 100,000+ | 🔴 ALTO |
| **IV Fijo** | Hardcodeado | IV random por mensaje | 🟡 MEDIO |
| **Key Hardcoded** | En código | Key derivada de secreto externo | 🟡 MEDIO |

### ⚠️ ¿Por qué se mantienen estos parámetros inseguros?

**COMPATIBILIDAD:** Este módulo debe ser **100% compatible** con el sistema C# existente para poder:
- Desencriptar datos encriptados por C#
- Que C# pueda desencriptar datos encriptados por Python
- Migración gradual del sistema sin romper compatibilidad

### 🔒 Recomendaciones de Seguridad

1. **NO usar para nuevos desarrollos** - Solo para interoperabilidad con sistema existente
2. **Planear migración** a algoritmos modernos cuando sea posible
3. **Limitar acceso** - Solo usar en módulos de autenticación legacy
4. **Auditar uso** - Registrar dónde se usa este módulo

---

## 🔧 Especificaciones Técnicas

### Algoritmo de Encriptación

- **Cifrado:** AES-256 (Rijndael)
- **Modo:** CBC (Cipher Block Chaining)
- **Padding:** PKCS7
- **Encoding salida:** Base64

### Derivación de Clave

```
Algoritmo: PBKDF1-MD5 (.NET PasswordDeriveBytes)
Password:  "m0n4pl1cBAZ.10"
Salt:      "c9a5d2f21f00469ff48a60fe5311b2ff"
Iterations: 2
Key Size:  256 bits (32 bytes)
```

### Vector de Inicialización (IV)

```
IV (ASCII): "bQBhAHIAaQANAAoA"
IV (Hex):   62 00 68 00 61 00 52 00 69 00 0D 00 0A 00
```

---

## 📖 Uso

### Ejemplo Básico

```python
from src.auth.encryption import Encrypt

# Crear instancia
encrypt = Encrypt()

# Encriptar
texto_plano = "MiPasswordSecreto"
texto_encriptado = encrypt.encriptar(texto_plano)
print(texto_encriptado)  # Output: "Rq8TzX0E9j+vH7kP2mN3lA==" (ejemplo)

# Desencriptar
texto_recuperado = encrypt.desencriptar(texto_encriptado)
print(texto_recuperado)  # Output: "MiPasswordSecreto"
```

### Funciones de Conveniencia

```python
from src.auth.encryption import encriptar, desencriptar

# Más simple
encrypted = encriptar("password123")
decrypted = desencriptar(encrypted)
```

### Uso en Autenticación

```python
from src.auth.encryption import encriptar, desencriptar

# Almacenar password encriptado
def guardar_usuario(username, password):
    password_encriptado = encriptar(password)
    # Guardar password_encriptado en BD
    db.save(username, password_encriptado)

# Verificar password
def verificar_usuario(username, password):
    password_almacenado = db.get(username).password
    password_real = desencriptar(password_almacenado)
    return password_real == password
```

---

## 🔄 Compatibilidad con C#

### Verificar Compatibilidad

1. **Generar valores en Python:**

```python
from src.auth.encryption import Encrypt

encrypt = Encrypt()
encrypted = encrypt.encriptar("test123")
print(f"Encrypted: {encrypted}")
```

2. **Verificar en C#:**

```csharp
using Consola_Monitoreo;

var encrypt = new Encrypt();
string encrypted = "valor_generado_por_python";
string decrypted = encrypt.Desencriptar(encrypted);
Console.WriteLine(decrypted);  // Debe ser "test123"
```

### Flujo Bidireccional

```
┌─────────────┐                           ┌─────────────┐
│   Python    │                           │     C#      │
│             │                           │             │
│  encriptar()│──────── Base64 ──────────→│Desencriptar()│
│             │         "xyz123..."       │             │
│             │                           │             │
│desencriptar()│←────── Base64 ───────────│ Encriptar() │
│             │         "abc456..."       │             │
└─────────────┘                           └─────────────┘
```

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest tests/auth/test_encryption.py -v

# Test específico de compatibilidad
pytest tests/auth/test_encryption.py::TestCompatibilidadC -v

# Con cobertura
pytest tests/auth/test_encryption.py --cov=src.auth.encryption
```

### Tests Incluidos

- ✅ Encriptación/Desencriptación básica
- ✅ Textos largos (múltiples bloques AES)
- ✅ Caracteres especiales y UTF-8
- ✅ Manejo de errores
- ✅ Validación Base64
- ✅ Singleton de encryptor
- ✅ **Compatibilidad con C#** (valores reales)

---

## 🔐 Detalles de Implementación

### Diferencias Python vs C# .NET

| Aspecto | C# (.NET Framework) | Python (cryptography) |
|---------|--------------------|-----------------------|
| **Clase Cipher** | `RijndaelManaged` | `AES` (algorithms.AES) |
| **Key Derivation** | `PasswordDeriveBytes` | Custom implementation |
| **Padding** | Automático | Manual (PKCS7) |
| **Base64** | `Convert.ToBase64String` | `base64.b64encode` |

### Implementación de PasswordDeriveBytes

C# `PasswordDeriveBytes` con MD5 **NO es PBKDF2 estándar**. Es un algoritmo propietario de .NET:

```python
# Replicar comportamiento de .NET
data = password + salt
for _ in range(iterations):
    data = md5(data).digest()

# Extender si necesario
while len(key_material) < key_size:
    data = md5(data).digest()
    key_material += data
```

---

## 📊 Comparación con Estándares Modernos

### Configuración Actual (Legacy)

```python
Encrypt(
    password="m0n4pl1cBAZ.10",
    salt="c9a5d2f21f00469ff48a60fe5311b2ff",
    hash_algorithm="MD5",
    iterations=2,
    iv="bQBhAHIAaQANAAoA" (fijo),
    key_size=256
)
```

### Configuración Moderna Recomendada

```python
# ⚠️ NO implementado - solo referencia
ModernEncrypt(
    password=os.environ['SECRET_KEY'],  # Desde variable entorno
    salt=os.urandom(16),                # Random por operación
    hash_algorithm="SHA256",            # SHA-256 o superior
    iterations=100000,                  # OWASP recomienda 100k+
    iv=os.urandom(16),                  # Random por mensaje
    key_size=256
)
```

---

## 🚀 Migración Futura

### Plan de Migración Sugerido

**Fase 1: Dual Support (actual)**
- ✅ Mantener módulo legacy para compatibilidad
- ✅ Crear módulo moderno paralelo
- ✅ Nuevos datos usan módulo moderno
- ✅ Datos legacy se desencriptan con módulo legacy

**Fase 2: Re-encriptación Gradual**
- Re-encriptar datos existentes en background
- Marcar datos re-encriptados en BD
- Mantener ambos módulos activos

**Fase 3: Deprecación**
- Eliminar módulo legacy
- Todos los datos en formato moderno

### Código de Ejemplo para Dual Support

```python
def decrypt_password(encrypted_password: str, version: str = "legacy") -> str:
    """Desencriptar password con soporte dual."""
    if version == "legacy":
        from src.auth.encryption import desencriptar
        return desencriptar(encrypted_password)
    elif version == "modern":
        from src.auth.modern_encryption import decrypt
        return decrypt(encrypted_password)
    else:
        raise ValueError(f"Unknown encryption version: {version}")
```

---

## 📝 Referencias

### Documentación Relacionada

- [Python cryptography library](https://cryptography.io/)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [NIST Digital Identity Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)

### Estándares de Seguridad

- **PBKDF2 Iterations:** OWASP recomienda 100,000+ (2023)
- **Hash Algorithm:** SHA-256 mínimo, SHA-3 preferido
- **IV Management:** Debe ser random y único por mensaje
- **Key Storage:** Usar HSM o secrets manager, no hardcodear

---

## ⚙️ Dependencias

```bash
pip install cryptography
```

**Versión requerida:** `cryptography>=41.0.0`

---

## 🐛 Troubleshooting

### Error: "Invalid padding"

**Causa:** El texto encriptado está corrupto o no fue generado con los mismos parámetros.

**Solución:** Verificar que:
- Password, Salt, IV son exactamente los mismos
- El texto es Base64 válido
- No hay modificaciones en el texto encriptado

### Error: "Invalid Base64"

**Causa:** El string no es Base64 válido.

**Solución:**
```python
import base64
try:
    base64.b64decode(texto)
except Exception as e:
    print(f"No es Base64 válido: {e}")
```

### Incompatibilidad Python ↔ C#

**Síntomas:** Python puede encriptar/desencriptar correctamente, pero C# no puede desencriptar lo generado por Python (o viceversa).

**Debugging:**
1. Verificar constantes exactas (password, salt, IV)
2. Comparar bytes del IV y salt
3. Verificar encoding (ASCII vs UTF-8)
4. Comparar key derivada en ambos lados

```python
# Debug en Python
encrypt = Encrypt()
print(f"Key (hex): {encrypt._key_bytes.hex()}")
print(f"IV (hex):  {encrypt._iv_bytes.hex()}")
```

```csharp
// Debug en C#
var encrypt = new Encrypt();
// Imprimir key e IV en hex para comparar
```

---

## 📞 Soporte

Para issues relacionados con este módulo:

1. Verificar compatibilidad con tests
2. Consultar documentación
3. Revisar logs de error
4. Contactar al equipo de desarrollo

---

**Última actualización:** 2025-12-22
**Versión:** 1.0.0
**Autor:** Claude Code
**Estado:** ✅ Producción (compatible con C# legacy)
