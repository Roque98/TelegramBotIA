"""
Script para verificar compatibilidad Python ↔ C#.

Genera valores encriptados en Python que pueden ser copiados a C#
para verificar que la desencriptación funciona correctamente.
"""
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domain.auth.encryption import Encrypt


def generar_valores_para_csharp():
    """Generar valores de prueba para verificar en C#."""
    print("\n" + "=" * 70)
    print(" VALORES PARA VERIFICAR COMPATIBILIDAD PYTHON -> C#")
    print("=" * 70)
    print()

    encrypt = Encrypt()

    # Valores de prueba
    test_cases = [
        ("admin", "Password del administrador"),
        ("password123", "Password común"),
        ("user@example.com", "Email"),
        ("Hola Mundo", "Texto con espacios"),
        ("ñoño123!@#", "Caracteres especiales"),
        ("", "String vacío"),
        ("A" * 100, "Texto largo"),
    ]

    print("Copiar este código C# para verificar:\n")
    print("```csharp")
    print("using System;")
    print("using Consola_Monitoreo;\n")
    print("class Program {")
    print("    static void Main() {")
    print("        var encrypt = new Encrypt();\n")

    for texto_plano, descripcion in test_cases:
        encrypted = encrypt.encriptar(texto_plano)

        # Escapar string para C#
        texto_plano_escaped = texto_plano.replace("\\", "\\\\").replace('"', '\\"')

        print(f"        // Test: {descripcion}")
        print(f'        string encrypted{test_cases.index((texto_plano, descripcion))} = "{encrypted}";')
        print(f'        string decrypted{test_cases.index((texto_plano, descripcion))} = encrypt.Desencriptar(encrypted{test_cases.index((texto_plano, descripcion))});')
        print(f'        string expected{test_cases.index((texto_plano, descripcion))} = "{texto_plano_escaped}";')
        print(f'        Console.WriteLine($"Test {test_cases.index((texto_plano, descripcion)) + 1}: {{(decrypted{test_cases.index((texto_plano, descripcion))} == expected{test_cases.index((texto_plano, descripcion))} ? "PASS" : "FAIL")}}");')
        print()

    print("    }")
    print("}")
    print("```\n")


def generar_tabla_comparativa():
    """Generar tabla con valores encriptados para comparación."""
    print("\n" + "=" * 70)
    print(" TABLA DE VALORES ENCRIPTADOS")
    print("=" * 70)
    print()

    encrypt = Encrypt()

    test_values = [
        "admin",
        "password123",
        "user@example.com",
        "test",
        "12345",
    ]

    print(f"{'Texto Plano':<25} {'Texto Encriptado (Base64)':<45}")
    print("-" * 70)

    for value in test_values:
        encrypted = encrypt.encriptar(value)
        print(f"{value:<25} {encrypted:<45}")

    print()


def verificar_desencriptacion_desde_csharp():
    """
    Verificar que Python puede desencriptar valores generados por C#.

    ⚠️ Agregar valores reales de C# cuando estén disponibles.
    """
    print("\n" + "=" * 70)
    print(" VERIFICACIÓN: DESENCRIPTAR VALORES DE C#")
    print("=" * 70)
    print()

    encrypt = Encrypt()

    # TODO: Agregar valores REALES generados por C#
    # Formato: (texto_plano_esperado, texto_encriptado_por_csharp)
    csharp_values = [
        # Ejemplo (reemplazar con valores reales):
        # ("admin", "xyz123abc..."),
        # ("password123", "abc789xyz..."),
    ]

    if not csharp_values:
        print("WARNING: NO HAY VALORES DE C# PARA VERIFICAR")
        print()
        print("Para completar esta verificacion:")
        print("1. Ejecutar este script para generar valores Python")
        print("2. Copiar valores a C# y verificar que desencriptan correctamente")
        print("3. Generar valores EN C# usando Encriptar()")
        print("4. Agregar esos valores a csharp_values[] en este script")
        print("5. Ejecutar de nuevo para verificar compatibilidad bidireccional")
        print()
        return

    print(f"{'Esperado':<20} {'Encriptado (C#)':<40} {'Resultado':<15}")
    print("-" * 75)

    all_passed = True
    for expected, encrypted_by_csharp in csharp_values:
        decrypted = encrypt.desencriptar(encrypted_by_csharp)
        passed = decrypted == expected
        all_passed = all_passed and passed

        status = "[OK] PASS" if passed else f"[FAIL] (got: {decrypted})"
        print(f"{expected:<20} {encrypted_by_csharp:<40} {status:<15}")

    print()
    if all_passed:
        print("[SUCCESS] TODOS LOS TESTS PASARON - Compatibilidad verificada")
    else:
        print("[ERROR] ALGUNOS TESTS FALLARON - Revisar implementacion")
    print()


def main():
    """Ejecutar todas las verificaciones."""
    print("\n")
    print("+" + "=" * 68 + "+")
    print("|" + " " * 15 + "VERIFICACION DE COMPATIBILIDAD PYTHON <-> C#" + " " * 10 + "|")
    print("+" + "=" * 68 + "+")

    generar_valores_para_csharp()
    generar_tabla_comparativa()
    verificar_desencriptacion_desde_csharp()

    print("=" * 70)
    print(" SIGUIENTE PASO:")
    print("=" * 70)
    print()
    print("1. Copiar el código C# generado arriba")
    print("2. Ejecutar en Visual Studio / .NET")
    print("3. Verificar que todos los tests pasan")
    print("4. Si alguno falla, revisar parámetros de encriptación")
    print()


if __name__ == "__main__":
    main()
