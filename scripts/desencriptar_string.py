"""
Script para desencriptar strings encriptados con el sistema C#/Python.

Uso:
    python desencriptar_string.py "ICqKPRWYKVg5pZLA7ZQCKA=="
    python desencriptar_string.py --encrypt "usrmon"
    python desencriptar_string.py --help
"""
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.auth.encryption import encriptar, desencriptar
import argparse


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='Encriptar o desencriptar strings usando el sistema compatible con C#',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Desencriptar un string
  python desencriptar_string.py "ICqKPRWYKVg5pZLA7ZQCKA=="

  # Encriptar un string
  python desencriptar_string.py --encrypt "usrmon"

  # Modo interactivo
  python desencriptar_string.py --interactive
        """
    )

    parser.add_argument(
        'texto',
        nargs='?',
        help='Texto a desencriptar (Base64). Si no se proporciona, usa modo interactivo.'
    )

    parser.add_argument(
        '-e', '--encrypt',
        action='store_true',
        help='Encriptar en lugar de desencriptar'
    )

    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Modo interactivo'
    )

    parser.add_argument(
        '-b', '--batch',
        action='store_true',
        help='Modo batch: leer múltiples líneas desde stdin'
    )

    args = parser.parse_args()

    # Modo batch
    if args.batch:
        print("Modo batch activado. Ingresa strings (uno por línea). Ctrl+C o EOF para salir.")
        print("Formato: [E|D] <texto>")
        print("  E texto_plano     -> Encriptar")
        print("  D texto_cifrado   -> Desencriptar")
        print("-" * 70)

        try:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue

                parts = line.split(maxsplit=1)
                if len(parts) != 2:
                    print(f"ERROR: Formato invalido: {line}")
                    continue

                operation, texto = parts

                if operation.upper() == 'E':
                    resultado = encriptar(texto)
                    print(f"Encriptado: {resultado}")
                elif operation.upper() == 'D':
                    resultado = desencriptar(texto)
                    if resultado is None:
                        print(f"ERROR: No se pudo desencriptar: {texto}")
                    else:
                        print(f"Desencriptado: {resultado}")
                else:
                    print(f"ERROR: Operacion invalida: {operation} (usa E o D)")
        except KeyboardInterrupt:
            print("\n\nBatch interrumpido.")
        return

    # Modo interactivo
    if args.interactive or args.texto is None:
        print("=" * 70)
        print(" ENCRIPTACION/DESENCRIPTACION INTERACTIVA")
        print("=" * 70)
        print()
        print("Comandos:")
        print("  e <texto>    - Encriptar texto")
        print("  d <texto>    - Desencriptar texto")
        print("  exit         - Salir")
        print()

        while True:
            try:
                comando = input(">>> ").strip()

                if comando.lower() in ['exit', 'quit', 'q']:
                    print("Adios!")
                    break

                if not comando:
                    continue

                parts = comando.split(maxsplit=1)
                if len(parts) != 2:
                    print("ERROR: Formato invalido. Usa: e <texto> o d <texto>")
                    continue

                operation, texto = parts

                if operation.lower() == 'e':
                    resultado = encriptar(texto)
                    print(f"Encriptado: {resultado}")
                elif operation.lower() == 'd':
                    resultado = desencriptar(texto)
                    if resultado is None:
                        print(f"ERROR: No se pudo desencriptar")
                    else:
                        print(f"Desencriptado: {resultado}")
                else:
                    print(f"ERROR: Comando invalido: {operation} (usa 'e' o 'd')")

                print()

            except KeyboardInterrupt:
                print("\n\nInterrumpido. Usa 'exit' para salir.")
            except EOFError:
                print("\n\nAdios!")
                break
        return

    # Modo simple (un solo valor)
    if args.encrypt:
        # Encriptar
        resultado = encriptar(args.texto)
        print(resultado)
    else:
        # Desencriptar
        resultado = desencriptar(args.texto)
        if resultado is None:
            print("ERROR: No se pudo desencriptar el texto", file=sys.stderr)
            sys.exit(1)
        else:
            print(resultado)


if __name__ == "__main__":
    main()
