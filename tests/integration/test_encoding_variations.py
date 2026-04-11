"""
Probar variaciones de encoding para el algoritmo PasswordDeriveBytes.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import hashlib
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Constantes
PASSWORD = "m0n4pl1cBAZ.10"
SALT_VALUE = "c9a5d2f21f00469ff48a60fe5311b2ff"
INITIAL_VECTOR = "bQBhAHIAaQANAAoA"
PASSWORD_ITERATIONS = 2
KEY_SIZE = 256

test_cases = [
    ('ICqKPRWYKVg5pZLA7ZQCKA==', 'usrmon'),
    ('c+GoNihnM/3L7BeKobPKgA==', 'MonAplic01@'),
    ('GlMuTDkzdxRIcm7fkMsuvQ==', 'sa')
]

def pkcs7_unpad(data: bytes) -> bytes:
    padding_length = data[-1]
    return data[:-padding_length]

def test_key(key_bytes: bytes, description: str):
    print(f"\n{description}")
    print(f"Key: {key_bytes.hex()[:32]}...")

    iv_bytes = INITIAL_VECTOR.encode('ascii')
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
                print(f"  [OK] {expected}")
                success_count += 1
            else:
                print(f"  [FAIL] esperado '{expected}', got '{plain_text}'")
        except Exception as e:
            print(f"  [ERROR] {expected}: {str(e)[:40]}")

    if success_count == len(test_cases):
        print(f"\n  *** [SUCCESS] ESTE ES EL ALGORITMO CORRECTO! ***")
        return True
    return False

# Variación con diferentes encodings de ctrl
def test_ctrl_encoding():
    password_bytes = PASSWORD.encode('ascii')
    salt_bytes = SALT_VALUE.encode('ascii')
    key_size_bytes = KEY_SIZE // 8

    lasthash = hashlib.md5(password_bytes + salt_bytes).digest()
    for _ in range(PASSWORD_ITERATIONS - 1):
        lasthash = hashlib.md5(lasthash).digest()

    # Probar diferentes encodings para ctrl
    encodings = [
        ("ASCII '1'", lambda x: str(x).encode('ascii')),
        ("UTF-8 '1'", lambda x: str(x).encode('utf-8')),
        ("Bytes chr()", lambda x: bytes([x])),
        ("Latin-1", lambda x: str(x).encode('latin-1')),
    ]

    for encoding_name, encoding_func in encodings:
        key_material = lasthash
        ctrl = 1
        while len(key_material) < key_size_bytes:
            key_material += hashlib.md5(encoding_func(ctrl) + lasthash).digest()
            ctrl += 1

        if test_key(key_material[:key_size_bytes], f"Ctrl encoding: {encoding_name}"):
            return True

    return False

print("=" * 70)
print(" PROBANDO VARIACIONES DE ENCODING")
print("=" * 70)

test_ctrl_encoding()
