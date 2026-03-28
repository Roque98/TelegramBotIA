"""
Script para generar tokens de autenticación desde línea de comandos.

Útil para desarrollo, testing e integración con otras plataformas.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from datetime import datetime, timedelta
from src.domain.auth.token_middleware import generar_token, validar_token


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='Generar o validar tokens de autenticación para el Chat API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Generar token para empleado
  python generar_token.py 12345

  # Validar token existente
  python generar_token.py --validate "ICqKPRWYKVg5pZLA7ZQCKA=="

  # Generar múltiples tokens
  python generar_token.py 12345 54321 99999

  # Mostrar información detallada
  python generar_token.py --verbose 12345
        """
    )

    parser.add_argument(
        'numero_empleado',
        nargs='*',
        type=int,
        help='Número(s) de empleado para generar token(s)'
    )

    parser.add_argument(
        '-v', '--validate',
        metavar='TOKEN',
        help='Validar un token existente en lugar de generar uno nuevo'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Mostrar información detallada del token'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Salida en formato JSON'
    )

    args = parser.parse_args()

    # Modo validación
    if args.validate:
        validar_token_cmd(args.validate, args.verbose, args.json)
        return

    # Modo generación
    if not args.numero_empleado:
        parser.print_help()
        print("\nERROR: Debe proporcionar al menos un número de empleado")
        sys.exit(1)

    for numero in args.numero_empleado:
        generar_token_cmd(numero, args.verbose, args.json)


def generar_token_cmd(numero_empleado: int, verbose: bool = False, json_output: bool = False):
    """
    Generar token para un empleado.

    Args:
        numero_empleado: Número de empleado
        verbose: Mostrar información detallada
        json_output: Salida en formato JSON
    """
    try:
        # Generar token
        token = generar_token(numero_empleado)

        if json_output:
            import json
            ahora = datetime.now()
            valido_hasta = ahora + timedelta(minutes=3)

            output = {
                "success": True,
                "token": token,
                "numero_empleado": numero_empleado,
                "timestamp": ahora.isoformat(),
                "valido_hasta": valido_hasta.isoformat(),
                "duracion_minutos": 3
            }
            print(json.dumps(output, indent=2))
        elif verbose:
            print("=" * 70)
            print(f" TOKEN GENERADO PARA EMPLEADO {numero_empleado}")
            print("=" * 70)
            print()
            print(f"Token:")
            print(f"  {token}")
            print()
            print(f"Información:")
            print(f"  Empleado: {numero_empleado}")
            print(f"  Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Válido hasta: {(datetime.now() + timedelta(minutes=3)).strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Duración: 3 minutos")
            print()
            print("Uso (cURL):")
            print(f'  curl -X POST http://localhost:5000/api/chat \\')
            print(f'    -H "Content-Type: application/json" \\')
            print(f'    -d \'{{"token": "{token}", "message": "Hola"}}\'')
            print()
        else:
            # Salida simple (solo el token)
            print(token)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def validar_token_cmd(token: str, verbose: bool = False, json_output: bool = False):
    """
    Validar un token existente.

    Args:
        token: Token a validar
        verbose: Mostrar información detallada
        json_output: Salida en formato JSON
    """
    try:
        # Validar token
        valido, datos, error = validar_token(token)

        if json_output:
            import json
            if valido:
                edad_segundos = int((datetime.now() - datos['timestamp_parsed']).total_seconds())
                output = {
                    "success": True,
                    "valid": True,
                    "numero_empleado": datos['numero_empleado'],
                    "timestamp": datos['timestamp'],
                    "edad_segundos": edad_segundos
                }
            else:
                output = {
                    "success": True,
                    "valid": False,
                    "error": error
                }
            print(json.dumps(output, indent=2))

        elif verbose:
            print("=" * 70)
            print(" VALIDACIÓN DE TOKEN")
            print("=" * 70)
            print()
            print(f"Token: {token[:30]}...")
            print()

            if valido:
                print("[OK] Token VÁLIDO")
                print()
                print("Información:")
                print(f"  Empleado: {datos['numero_empleado']}")
                print(f"  Timestamp: {datos['timestamp']}")

                edad = datetime.now() - datos['timestamp_parsed']
                edad_segundos = int(edad.total_seconds())
                edad_minutos = edad_segundos // 60

                print(f"  Edad: {edad_minutos} minutos, {edad_segundos % 60} segundos")

                tiempo_restante = timedelta(minutes=3) - edad
                tiempo_restante_segundos = int(tiempo_restante.total_seconds())

                if tiempo_restante_segundos > 0:
                    print(f"  Tiempo restante: {tiempo_restante_segundos // 60} minutos, {tiempo_restante_segundos % 60} segundos")
                else:
                    print(f"  Estado: EXPIRADO")
            else:
                print("[ERROR] Token INVÁLIDO")
                print()
                print(f"Error: {error}")

            print()

        else:
            # Salida simple
            if valido:
                print(f"VÁLIDO - Empleado: {datos['numero_empleado']}")
            else:
                print(f"INVÁLIDO - {error}")

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
