"""Test para verificar que se carga correctamente el .env"""
import os
from pathlib import Path
from src.config.settings import settings

print("=" * 60)
print("TEST DE CARGA DE VARIABLES DE ENTORNO")
print("=" * 60)

# Verificar el archivo .env
project_root = Path(__file__).parent
env_file = project_root / ".env"
print(f"\nArchivo .env: {env_file}")
print(f"Existe: {env_file.exists()}")

# Mostrar el valor de la API key desde settings
api_key = settings.openai_api_key
print(f"\nOPENAI_API_KEY desde settings:")
print(f"  Primeros 20 chars: {api_key[:20] if api_key else 'NO ENCONTRADA'}")
print(f"  Ultimos 10 chars: {api_key[-10:] if api_key else 'NO ENCONTRADA'}")
print(f"  Longitud total: {len(api_key) if api_key else 0}")

# Leer directamente del archivo .env para comparar
print(f"\nValor en el archivo .env:")
with open(env_file, 'r') as f:
    for line in f:
        if line.startswith('OPENAI_API_KEY='):
            env_value = line.strip().split('=', 1)[1]
            print(f"  Primeros 20 chars: {env_value[:20]}")
            print(f"  Ultimos 10 chars: {env_value[-10:]}")
            print(f"  Longitud total: {len(env_value)}")

            # Comparar
            if api_key == env_value:
                print("\n[OK] La API key de settings coincide con el archivo .env")
            else:
                print("\n[ERROR] La API key NO coincide!")
                print(f"  Settings: {api_key[:30]}...")
                print(f"  .env:     {env_value[:30]}...")
            break

print("\n" + "=" * 60)
