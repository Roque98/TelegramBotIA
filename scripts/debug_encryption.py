"""
Script de debugging para comparar valores de encriptación Python vs C#.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domain.auth.encryption import Encrypt
import hashlib

def debug_encryption():
    """Mostrar todos los valores intermedios para debugging."""
    print("=" * 70)
    print(" DEBUG - VALORES INTERNOS DE ENCRIPTACION")
    print("=" * 70)
    print()

    encrypt = Encrypt()

    # Constantes
    print("CONSTANTES:")
    print(f"  PASSWORD: {encrypt.PASSWORD}")
    print(f"  SALT_VALUE: {encrypt.SALT_VALUE}")
    print(f"  HASH_ALGORITHM: {encrypt.HASH_ALGORITHM}")
    print(f"  PASSWORD_ITERATIONS: {encrypt.PASSWORD_ITERATIONS}")
    print(f"  INITIAL_VECTOR: {encrypt.INITIAL_VECTOR}")
    print(f"  KEY_SIZE: {encrypt.KEY_SIZE} bits")
    print()

    # Bytes generados
    print("BYTES GENERADOS:")
    print(f"  IV bytes ({len(encrypt._iv_bytes)} bytes):")
    print(f"    Hex: {encrypt._iv_bytes.hex()}")
    print(f"    ASCII: {repr(encrypt._iv_bytes)}")
    print()

    print(f"  Salt bytes ({len(encrypt._salt_bytes)} bytes):")
    print(f"    Hex: {encrypt._salt_bytes.hex()}")
    print(f"    ASCII: {repr(encrypt._salt_bytes[:16])}... (truncado)")
    print()

    print(f"  Key bytes ({len(encrypt._key_bytes)} bytes):")
    print(f"    Hex: {encrypt._key_bytes.hex()}")
    print()

    # Probar encriptación de "usrmon"
    print("=" * 70)
    print(" TEST: Encriptar 'usrmon'")
    print("=" * 70)
    print()

    plain_text = "usrmon"
    encrypted = encrypt.encriptar(plain_text)

    print(f"  Texto plano: {plain_text}")
    print(f"  Encriptado (Python): {encrypted}")
    print(f"  Esperado (C#):       ICqKPRWYKVg5pZLA7ZQCKA==")
    print(f"  Coincide: {encrypted == 'ICqKPRWYKVg5pZLA7ZQCKA=='}")
    print()

    # Intentar desencriptar el valor de C#
    print("=" * 70)
    print(" TEST: Desencriptar valor de C#")
    print("=" * 70)
    print()

    csharp_encrypted = "ICqKPRWYKVg5pZLA7ZQCKA=="
    try:
        decrypted = encrypt.desencriptar(csharp_encrypted)
        print(f"  Valor C#: {csharp_encrypted}")
        print(f"  Desencriptado: {decrypted}")
        print(f"  Esperado: usrmon")
        print(f"  Coincide: {decrypted == 'usrmon'}")
    except Exception as e:
        print(f"  ERROR: {e}")
    print()

    # Mostrar código C# para comparar
    print("=" * 70)
    print(" CODIGO C# PARA DEBUGGING")
    print("=" * 70)
    print()
    print("Copiar este código a C# para obtener los valores internos:")
    print()
    print("```csharp")
    print("using System;")
    print("using System.Security.Cryptography;")
    print("using System.Text;")
    print()
    print("class DebugEncryption {")
    print("    static void Main() {")
    print("        string password = \"m0n4pl1cBAZ.10\";")
    print("        string saltValue = \"c9a5d2f21f00469ff48a60fe5311b2ff\";")
    print("        string initialVector = \"bQBhAHIAaQANAAoA\";")
    print()
    print("        byte[] ivBytes = Encoding.ASCII.GetBytes(initialVector);")
    print("        byte[] saltBytes = Encoding.ASCII.GetBytes(saltValue);")
    print()
    print("        PasswordDeriveBytes pdb = new PasswordDeriveBytes(")
    print("            password, saltBytes, \"MD5\", 2);")
    print("        byte[] keyBytes = pdb.GetBytes(32);")
    print()
    print("        Console.WriteLine(\"IV Bytes (\" + ivBytes.Length + \"):\");")
    print("        Console.WriteLine(BitConverter.ToString(ivBytes));")
    print()
    print("        Console.WriteLine(\"\\nSalt Bytes (\" + saltBytes.Length + \"):\");")
    print("        Console.WriteLine(BitConverter.ToString(saltBytes));")
    print()
    print("        Console.WriteLine(\"\\nKey Bytes (\" + keyBytes.Length + \"):\");")
    print("        Console.WriteLine(BitConverter.ToString(keyBytes));")
    print("    }")
    print("}")
    print("```")
    print()

if __name__ == "__main__":
    debug_encryption()
