"""
Script de diagnóstico para verificar configuración.
"""
import os
import sys
from pathlib import Path

def check_env_file():
    """Verificar que existe el archivo .env"""
    env_path = Path(".env")
    print(f"Verificando archivo .env...")
    print(f"Ruta: {env_path.absolute()}")

    if env_path.exists():
        print("✓ Archivo .env encontrado")
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"✓ Contiene {len(lines)} líneas")

            # Mostrar variables (sin valores sensibles)
            print("\nVariables en .env:")
            #for line in lines:
            #    line = line.strip()
            #    if line and not line.startswith('#'):
            #        key = line.split('=')[0]
            #        if 'KEY' in key or 'TOKEN' in key or 'PASSWORD' in key:
            #            print(f"  - {key}=***")
            #        else:
            #            print(f"  - {line}")
        return True
    else:
        print("✗ Archivo .env NO encontrado")
        return False

def check_settings():
    """Verificar que settings carga correctamente"""
    print("\n" + "="*60)
    print("Verificando carga de Settings...")
    print("="*60)

    try:
        from src.config.settings import settings
        print("✓ Settings importado correctamente")

        print("\nConfiguración cargada:")
        print(f"  - OPENAI_API_KEY:" + settings.openai_api_key)
        print(f"  - OPENAI_MODEL: {settings.openai_model}")
        print(f"  - ANTHROPIC_API_KEY: {'Configurado' if settings.anthropic_api_key else 'NO CONFIGURADO'}")
        print(f"  - TELEGRAM_BOT_TOKEN: {'***' + settings.telegram_bot_token[-8:] if settings.telegram_bot_token else 'NO CONFIGURADO'}")
        print(f"  - DB_TYPE: {settings.db_type}")
        print(f"  - DB_NAME: {settings.db_name}")
        print(f"  - LOG_LEVEL: {settings.log_level}")

        return True
    except Exception as e:
        print(f"✗ Error cargando settings: {e}")
        return False

def check_openai_client():
    """Verificar que el cliente OpenAI se puede inicializar"""
    print("\n" + "="*60)
    print("Verificando cliente OpenAI...")
    print("="*60)

    try:
        from src.config.settings import settings
        from openai import OpenAI

        if not settings.openai_api_key:
            print("✗ No hay API key de OpenAI configurada")
            return False

        client = OpenAI(api_key=settings.openai_api_key)
        print("✓ Cliente OpenAI creado correctamente")
        print(f"✓ API Key: {settings.openai_api_key[:8]}...{settings.openai_api_key[-4:]}")
        print(f"✓ Modelo configurado: {settings.openai_model}")

        return True
    except Exception as e:
        print(f"✗ Error creando cliente OpenAI: {e}")
        return False

def test_openai_connection():
    """Intentar una llamada de prueba al API de OpenAI"""
    print("\n" + "="*60)
    print("Probando conexión con OpenAI...")
    print("="*60)

    try:
        from src.config.settings import settings
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)

        print(f"Intentando llamada al modelo: {settings.openai_model}")
        print("Endpoint: /responses")

        # Intentar una llamada simple
        response = client.responses.create(
            model=settings.openai_model,
            input="Di solo 'OK'"
        )

        print(f"✓ Respuesta recibida: {response.output_text}")
        return True

    except Exception as e:
        print(f"✗ Error en llamada de prueba: {e}")
        print(f"   Tipo de error: {type(e).__name__}")
        if hasattr(e, 'status_code'):
            print(f"   Código de estado: {e.status_code}")
        if hasattr(e, 'response'):
            print(f"   Respuesta: {e.response}")
        return False

def main():
    """Ejecutar todos los diagnósticos"""
    print("="*60)
    print("DIAGNÓSTICO DE CONFIGURACIÓN")
    print("="*60)
    print(f"Python: {sys.version}")
    print(f"Directorio: {os.getcwd()}")
    print("="*60)

    results = []

    results.append(("Archivo .env", check_env_file()))
    results.append(("Carga de Settings", check_settings()))
    results.append(("Cliente OpenAI", check_openai_client()))
    results.append(("Conexión OpenAI", test_openai_connection()))

    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    for name, result in results:
        status = "✓ OK" if result else "✗ FALLÓ"
        print(f"{status:10} {name}")

    print("="*60)

    if all(result for _, result in results):
        print("✓ Todas las verificaciones pasaron correctamente")
        return 0
    else:
        print("✗ Algunas verificaciones fallaron")
        return 1

if __name__ == "__main__":
    sys.exit(main())
