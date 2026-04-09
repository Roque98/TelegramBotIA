"""
Probar diferentes algoritmos de derivación de clave para encontrar el correcto.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import hashlib
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Constantes de C#
PASSWORD = "m0n4pl1cBAZ.10"
SALT_VALUE = "c9a5d2f21f00469ff48a60fe5311b2ff"
INITIAL_VECTOR = "bQBhAHIAaQANAAoA"
PASSWORD_ITERATIONS = 2
KEY_SIZE = 256

# Valores de prueba de C#
test_cases = [
    ('ICqKPRWYKVg5pZLA7ZQCKA==', 'usrmon'),
    ('c+GoNihnM/3L7BeKobPKgA==', 'MonAplic01@'),
    ('GlMuTDkzdxRIcm7fkMsuvQ==', 'sa')
]

def pkcs7_unpad(data: bytes) -> bytes:
    """Remover padding PKCS7."""
    padding_length = data[-1]
    return data[:-padding_length]

def test_key_derivation(key_bytes: bytes, description: str):
    """Probar una derivación de clave específica."""
    print(f"\n{description}")
    print(f"Key: {key_bytes.hex()}")

    iv_bytes = INITIAL_VECTOR.encode('ascii')

    # Probar desencriptar
    success_count = 0
    for encrypted, expected in test_cases:
        try:
            cipher_bytes = base64.b64decode(encrypted)
            cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv_bytes), backend=default_backend())
            decryptor = cipher.decryptor()
            padded_plain = decryptor.update(cipher_bytes) + decryptor.finalize()
            plain_bytes = pkcs7_unpad(padded_plain)
            plain_text = plain_bytes.decode('utf-8')

            if plain_text == expected:
                print(f"  OK: {expected}")
                success_count += 1
            else:
                print(f"  FAIL: esperado '{expected}', obtenido '{plain_text}'")
        except Exception as e:
            print(f"  ERROR: {expected} -> {str(e)[:50]}")

    print(f"  Total: {success_count}/{len(test_cases)} correctos")
    return success_count == len(test_cases)

# Derivación 1: Implementación actual
def derive_key_v1():
    password_bytes = PASSWORD.encode('ascii')
    salt_bytes = SALT_VALUE.encode('ascii')
    key_size_bytes = KEY_SIZE // 8

    lasthash = hashlib.md5(password_bytes + salt_bytes).digest()
    for _ in range(PASSWORD_ITERATIONS - 1):
        lasthash = hashlib.md5(lasthash).digest()

    key_material = lasthash
    ctrl = 1
    while len(key_material) < key_size_bytes:
        key_material += hashlib.md5(str(ctrl).encode('ascii') + lasthash).digest()
        ctrl += 1

    return key_material[:key_size_bytes]

# Derivación 2: Primer bloque con hash adicional
def derive_key_v2():
    password_bytes = PASSWORD.encode('ascii')
    salt_bytes = SALT_VALUE.encode('ascii')
    key_size_bytes = KEY_SIZE // 8

    lasthash = hashlib.md5(password_bytes + salt_bytes).digest()
    for _ in range(PASSWORD_ITERATIONS - 1):
        lasthash = hashlib.md5(lasthash).digest()

    # Primer bloque: hash(lasthash) en lugar de lasthash
    key_material = hashlib.md5(lasthash).digest()
    ctrl = 1
    while len(key_material) < key_size_bytes:
        key_material += hashlib.md5(str(ctrl).encode('ascii') + lasthash).digest()
        ctrl += 1

    return key_material[:key_size_bytes]

# Derivación 3: Sin iteraciones extra
def derive_key_v3():
    password_bytes = PASSWORD.encode('ascii')
    salt_bytes = SALT_VALUE.encode('ascii')
    key_size_bytes = KEY_SIZE // 8

    # Solo una vez
    lasthash = hashlib.md5(password_bytes + salt_bytes).digest()

    key_material = lasthash
    ctrl = 1
    while len(key_material) < key_size_bytes:
        key_material += hashlib.md5(str(ctrl).encode('ascii') + lasthash).digest()
        ctrl += 1

    return key_material[:key_size_bytes]

# Derivación 4: Iterar N veces completas
def derive_key_v4():
    password_bytes = PASSWORD.encode('ascii')
    salt_bytes = SALT_VALUE.encode('ascii')
    key_size_bytes = KEY_SIZE // 8

    lasthash = password_bytes + salt_bytes
    for _ in range(PASSWORD_ITERATIONS):
        lasthash = hashlib.md5(lasthash).digest()

    key_material = lasthash
    ctrl = 1
    while len(key_material) < key_size_bytes:
        key_material += hashlib.md5(str(ctrl).encode('ascii') + lasthash).digest()
        ctrl += 1

    return key_material[:key_size_bytes]

print("=" * 70)
print(" PROBANDO DIFERENTES ALGORITMOS DE DERIVACION DE CLAVE")
print("=" * 70)

if test_key_derivation(derive_key_v1(), "V1: Actual (lasthash directo)"):
    print("\n[SUCCESS] V1 es correcto!")

if test_key_derivation(derive_key_v2(), "V2: hash(lasthash) como primer bloque"):
    print("\n[SUCCESS] V2 es correcto!")

if test_key_derivation(derive_key_v3(), "V3: Sin iteraciones extra (1 sola vez)"):
    print("\n[SUCCESS] V3 es correcto!")

if test_key_derivation(derive_key_v4(), "V4: Iterar N veces completas"):
    print("\n[SUCCESS] V4 es correcto!")
