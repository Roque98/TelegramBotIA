# Herramienta de Encriptación/Desencriptación

Script de línea de comandos para encriptar y desencriptar strings usando el sistema compatible con C#.

**Ubicación:** `scripts/desencriptar_string.py`

---

## Uso Básico

### Desencriptar un String

```bash
python scripts/desencriptar_string.py "ICqKPRWYKVg5pZLA7ZQCKA=="
# Salida: usrmon
```

### Encriptar un String

```bash
python scripts/desencriptar_string.py --encrypt "usrmon"
# Salida: ICqKPRWYKVg5pZLA7ZQCKA==
```

---

## Modos de Operación

### 1. Modo Simple (Un solo valor)

**Desencriptar:**
```bash
python scripts/desencriptar_string.py "c+GoNihnM/3L7BeKobPKgA=="
# Salida: MonAplic01@
```

**Encriptar:**
```bash
python scripts/desencriptar_string.py -e "MonAplic01@"
# Salida: c+GoNihnM/3L7BeKobPKgA==
```

### 2. Modo Interactivo

```bash
python scripts/desencriptar_string.py --interactive
```

Sesión de ejemplo:
```
======================================================================
 ENCRIPTACION/DESENCRIPTACION INTERACTIVA
======================================================================

Comandos:
  e <texto>    - Encriptar texto
  d <texto>    - Desencriptar texto
  exit         - Salir

>>> e usrmon
Encriptado: ICqKPRWYKVg5pZLA7ZQCKA==

>>> d ICqKPRWYKVg5pZLA7ZQCKA==
Desencriptado: usrmon

>>> exit
Adios!
```

### 3. Modo Batch (Procesamiento por lotes)

```bash
python scripts/desencriptar_string.py --batch
```

Formato de entrada:
```
E usrmon
D ICqKPRWYKVg5pZLA7ZQCKA==
E MonAplic01@
D c+GoNihnM/3L7BeKobPKgA==
```

Salida:
```
Encriptado: ICqKPRWYKVg5pZLA7ZQCKA==
Desencriptado: usrmon
Encriptado: c+GoNihnM/3L7BeKobPKgA==
Desencriptado: MonAplic01@
```

**Desde archivo:**
```bash
cat valores.txt | python scripts/desencriptar_string.py --batch
```

---

## Opciones de Línea de Comandos

```
usage: desencriptar_string.py [-h] [-e] [-i] [-b] [texto]

positional arguments:
  texto              Texto a desencriptar (Base64)

options:
  -h, --help         Mostrar ayuda
  -e, --encrypt      Encriptar en lugar de desencriptar
  -i, --interactive  Modo interactivo
  -b, --batch        Modo batch: leer múltiples líneas desde stdin
```

---

## Casos de Uso

### 1. Verificar Passwords en Base de Datos

Si tienes passwords encriptados en la base de datos:

```bash
# Desencriptar para ver el password original
python scripts/desencriptar_string.py "c+GoNihnM/3L7BeKobPKgA=="
# Salida: MonAplic01@
```

### 2. Generar Passwords Encriptados para Insertar en BD

```bash
# Encriptar nuevo password
python scripts/desencriptar_string.py -e "NuevoPassword123!"
# Salida: [valor encriptado para insertar en BD]
```

### 3. Procesar Múltiples Valores

Crear archivo `passwords.txt`:
```
E admin123
E password1
E userPass
```

Ejecutar:
```bash
cat passwords.txt | python scripts/desencriptar_string.py --batch > encrypted_passwords.txt
```

### 4. Verificar Compatibilidad Python ↔ C#

Encriptar en Python:
```bash
python scripts/desencriptar_string.py -e "test123"
# Copiar resultado a C#
```

Desencriptar valor de C# en Python:
```bash
python scripts/desencriptar_string.py "[valor de C#]"
# Verificar que devuelve el texto original
```

---

## Integración con Scripts

### PowerShell

```powershell
# Desencriptar
$encrypted = "ICqKPRWYKVg5pZLA7ZQCKA=="
$decrypted = python scripts/desencriptar_string.py $encrypted
Write-Host "Desencriptado: $decrypted"

# Encriptar
$plain = "usrmon"
$encrypted = python scripts/desencriptar_string.py --encrypt $plain
Write-Host "Encriptado: $encrypted"
```

### Bash

```bash
#!/bin/bash

# Desencriptar
encrypted="ICqKPRWYKVg5pZLA7ZQCKA=="
decrypted=$(python scripts/desencriptar_string.py "$encrypted")
echo "Desencriptado: $decrypted"

# Encriptar
plain="usrmon"
encrypted=$(python scripts/desencriptar_string.py --encrypt "$plain")
echo "Encriptado: $encrypted"
```

### Python

```python
import subprocess

def encriptar_valor(texto_plano):
    """Encriptar usando el script."""
    result = subprocess.run(
        ['python', 'scripts/desencriptar_string.py', '--encrypt', texto_plano],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def desencriptar_valor(texto_cifrado):
    """Desencriptar usando el script."""
    result = subprocess.run(
        ['python', 'scripts/desencriptar_string.py', texto_cifrado],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

# Uso
encrypted = encriptar_valor("usrmon")
print(f"Encriptado: {encrypted}")

decrypted = desencriptar_valor(encrypted)
print(f"Desencriptado: {decrypted}")
```

---

## Manejo de Errores

### Error: Texto no es Base64 válido

```bash
python scripts/desencriptar_string.py "texto_invalido"
# ERROR: No se pudo desencriptar el texto
```

**Solución:** Verificar que el texto esté en formato Base64.

### Error: Padding inválido

```bash
python scripts/desencriptar_string.py "SGVsbG8gV29ybGQ="
# ERROR: No se pudo desencriptar el texto
```

**Solución:** El texto es Base64 válido pero no fue encriptado con este sistema.

---

## Ejemplos Prácticos

### Ejemplo 1: Migrar Passwords

```bash
# 1. Exportar passwords encriptados de C#
# 2. Crear archivo con formato batch
cat << EOF > migrate.txt
D [password_encriptado_1]
D [password_encriptado_2]
D [password_encriptado_3]
EOF

# 3. Desencriptar y procesar
python scripts/desencriptar_string.py --batch < migrate.txt > passwords_planos.txt
```

### Ejemplo 2: Validar Compatibilidad

```bash
# Test de ida y vuelta
ORIGINAL="TestPassword123"
ENCRYPTED=$(python scripts/desencriptar_string.py -e "$ORIGINAL")
DECRYPTED=$(python scripts/desencriptar_string.py "$ENCRYPTED")

if [ "$ORIGINAL" == "$DECRYPTED" ]; then
    echo "OK: Encriptacion/Desencriptacion funciona correctamente"
else
    echo "ERROR: Original '$ORIGINAL' != Desencriptado '$DECRYPTED'"
fi
```

---

## Notas de Seguridad

⚠️ **IMPORTANTE:**

1. **No usar en producción para nuevos sistemas** - Este es un sistema legacy compatible con C#
2. **Passwords visibles** - Los passwords desencriptados se muestran en pantalla
3. **Historial de comandos** - Evitar poner passwords sensibles en línea de comandos
4. **Usar variables de entorno** cuando sea posible:

```bash
# Malo
python scripts/desencriptar_string.py -e "SuperSecretPassword"

# Mejor
read -s PASSWORD
python scripts/desencriptar_string.py -e "$PASSWORD"
```

---

## Troubleshooting

### No encuentra el módulo src.auth.encryption

**Error:**
```
ModuleNotFoundError: No module named 'src'
```

**Solución:**
```bash
# Asegurarse de ejecutar desde el directorio raíz del proyecto
cd D:\proyectos\gs\GPT5
python scripts/desencriptar_string.py "..."
```

### Encoding de caracteres en Windows

Si ves caracteres extraños en la salida:

```bash
# Windows PowerShell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
python scripts/desencriptar_string.py "..."

# Windows CMD
chcp 65001
python scripts/desencriptar_string.py "..."
```

---

## Ver También

- [Documentación de Encriptación](ENCRYPTION_COMPATIBILITY.md)
- [Ejemplos de Uso](../examples/ejemplo_encryption.py)
- [Tests](../tests/auth/test_encryption.py)

---

**Última actualización:** 2025-12-22
**Versión:** 1.0.0
