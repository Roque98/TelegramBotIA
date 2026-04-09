"""
Ejemplos de uso del Chat API Middleware.

Muestra cómo integrar el chat de IRIS en plataformas externas usando tokens encriptados.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from datetime import datetime
from src.domain.auth.token_middleware import generar_token, validar_token


# URL base del API (cambiar según ambiente)
BASE_URL = "http://localhost:5000/api"


def ejemplo_1_generar_y_usar_token():
    """Ejemplo 1: Generar token y enviar mensaje al chat."""
    print("=" * 70)
    print(" EJEMPLO 1: Generar Token y Enviar Mensaje")
    print("=" * 70)
    print()

    # 1. Generar token para un empleado
    numero_empleado = 12345
    token = generar_token(numero_empleado)

    print(f"Token generado para empleado {numero_empleado}:")
    print(f"  {token}")
    print()

    # 2. Enviar mensaje al chat
    mensaje = "Hola, necesito ayuda con mi orden"

    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "token": token,
            "message": mensaje
        }
    )

    # 3. Procesar respuesta
    print(f"Status Code: {response.status_code}")
    print()

    if response.status_code == 200:
        data = response.json()
        print("[SUCCESS] Respuesta del bot:")
        print(f"  {data['response']}")
        print()
        print(f"Empleado: {data['numero_empleado']}")
        print(f"Timestamp: {data['timestamp']}")
    else:
        data = response.json()
        print(f"[ERROR] {data.get('error_code', 'UNKNOWN')}: {data.get('error', 'Error desconocido')}")

    print()


def ejemplo_2_validar_token_antes_de_usar():
    """Ejemplo 2: Validar token antes de enviar mensaje."""
    print("=" * 70)
    print(" EJEMPLO 2: Validar Token Antes de Enviar")
    print("=" * 70)
    print()

    # 1. Generar token
    token = generar_token(54321)
    print(f"Token generado: {token[:30]}...")
    print()

    # 2. Validar token usando el endpoint
    response = requests.post(
        f"{BASE_URL}/chat/validate-token",
        json={"token": token}
    )

    if response.status_code == 200:
        data = response.json()

        if data['valid']:
            print("[OK] Token válido")
            print(f"  Empleado: {data['numero_empleado']}")
            print(f"  Timestamp: {data['timestamp_token']}")
            print(f"  Edad: {data['edad_segundos']} segundos")
            print()

            # 3. Ahora sí enviar mensaje
            print("Enviando mensaje...")
            chat_response = requests.post(
                f"{BASE_URL}/chat",
                json={
                    "token": token,
                    "message": "¿Cuál es el estado de mi orden?"
                }
            )

            if chat_response.status_code == 200:
                print(f"Respuesta: {chat_response.json()['response']}")
        else:
            print(f"[ERROR] Token inválido: {data['error']}")

    print()


def ejemplo_3_token_expirado():
    """Ejemplo 3: Demostrar manejo de token expirado."""
    print("=" * 70)
    print(" EJEMPLO 3: Token Expirado")
    print("=" * 70)
    print()

    # Crear token con timestamp antiguo (más de 3 minutos)
    import json
    from src.domain.auth.encryption import encriptar
    from datetime import timedelta

    # Timestamp de hace 5 minutos
    timestamp_viejo = (datetime.now() - timedelta(minutes=5)).isoformat()

    token_data = {
        "numero_empleado": 99999,
        "timestamp": timestamp_viejo
    }

    token_expirado = encriptar(json.dumps(token_data))

    print(f"Token con timestamp de hace 5 minutos:")
    print(f"  {token_expirado[:30]}...")
    print()

    # Intentar usar token expirado
    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "token": token_expirado,
            "message": "Hola"
        }
    )

    print(f"Status Code: {response.status_code}")
    print()

    if response.status_code == 401:
        data = response.json()
        print(f"[ESPERADO] Token rechazado:")
        print(f"  Error: {data['error']}")
        print(f"  Código: {data['error_code']}")
    else:
        print("[INESPERADO] Token aceptado (debería haber expirado)")

    print()


def ejemplo_4_validacion_local():
    """Ejemplo 4: Validar token localmente (sin llamar al API)."""
    print("=" * 70)
    print(" EJEMPLO 4: Validación Local de Token")
    print("=" * 70)
    print()

    # 1. Generar token
    numero_empleado = 11111
    token = generar_token(numero_empleado)

    print(f"Token generado: {token[:30]}...")
    print()

    # 2. Validar localmente (sin llamar al API)
    valido, datos, error = validar_token(token)

    if valido:
        print("[OK] Token válido (validación local)")
        print(f"  Empleado: {datos['numero_empleado']}")
        print(f"  Timestamp: {datos['timestamp']}")

        # Calcular edad
        edad = (datetime.now() - datos['timestamp_parsed']).total_seconds()
        print(f"  Edad: {int(edad)} segundos")
    else:
        print(f"[ERROR] Token inválido: {error}")

    print()


def ejemplo_5_generar_token_desde_api():
    """Ejemplo 5: Generar token usando el API (solo desarrollo)."""
    print("=" * 70)
    print(" EJEMPLO 5: Generar Token desde API")
    print("=" * 70)
    print()
    print("[WARNING] Este endpoint solo debe usarse en desarrollo")
    print()

    # Generar token usando el endpoint
    response = requests.post(
        f"{BASE_URL}/chat/generate-token",
        json={"numero_empleado": 77777}
    )

    if response.status_code == 200:
        data = response.json()
        print("[SUCCESS] Token generado:")
        print(f"  Token: {data['token'][:30]}...")
        print(f"  Empleado: {data['numero_empleado']}")
        print(f"  Generado: {data['timestamp']}")
        print(f"  Válido hasta: {data['valido_hasta']}")
        print(f"  Duración: {data['duracion_minutos']} minutos")
        print()

        # Usar el token generado
        print("Usando el token generado...")
        chat_response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "token": data['token'],
                "message": "Hola desde el token generado por API"
            }
        )

        if chat_response.status_code == 200:
            print(f"Respuesta: {chat_response.json()['response']}")
    else:
        print(f"[ERROR] No se pudo generar token: {response.status_code}")

    print()


def ejemplo_6_integracion_javascript():
    """Ejemplo 6: Mostrar cómo integrar desde JavaScript."""
    print("=" * 70)
    print(" EJEMPLO 6: Integración desde JavaScript")
    print("=" * 70)
    print()

    # Generar token para mostrar en el ejemplo
    token = generar_token(12345)

    print("Código JavaScript para integración:")
    print()
    print("```javascript")
    print("// 1. Obtener token del backend")
    print("// (el token debe ser generado por tu backend usando Python)")
    print(f"const token = '{token}';")
    print()
    print("// 2. Enviar mensaje al chat")
    print("async function enviarMensaje(mensaje) {")
    print("  try {")
    print(f"    const response = await fetch('{BASE_URL}/chat', {{")
    print("      method: 'POST',")
    print("      headers: {")
    print("        'Content-Type': 'application/json'")
    print("      },")
    print("      body: JSON.stringify({")
    print("        token: token,")
    print("        message: mensaje")
    print("      })")
    print("    });")
    print()
    print("    const data = await response.json();")
    print()
    print("    if (data.success) {")
    print("      console.log('Respuesta:', data.response);")
    print("      return data.response;")
    print("    } else {")
    print("      console.error('Error:', data.error);")
    print("      return null;")
    print("    }")
    print("  } catch (error) {")
    print("    console.error('Error de red:', error);")
    print("    return null;")
    print("  }")
    print("}")
    print()
    print("// 3. Usar la función")
    print("enviarMensaje('Hola, necesito ayuda').then(respuesta => {")
    print("  if (respuesta) {")
    print("    document.getElementById('chat-response').innerText = respuesta;")
    print("  }")
    print("});")
    print("```")
    print()


def ejemplo_7_health_check():
    """Ejemplo 7: Verificar que el API está funcionando."""
    print("=" * 70)
    print(" EJEMPLO 7: Health Check")
    print("=" * 70)
    print()

    response = requests.get(f"{BASE_URL}/health")

    print(f"Status Code: {response.status_code}")
    print()

    if response.status_code == 200:
        data = response.json()
        print("[OK] API funcionando correctamente")
        print(f"  Status: {data['status']}")
        print(f"  Timestamp: {data['timestamp']}")
    else:
        print("[ERROR] API no responde correctamente")

    print()


def main():
    """Ejecutar todos los ejemplos."""
    print()
    print("+" + "=" * 68 + "+")
    print("|" + " " * 15 + "EJEMPLOS DE USO - CHAT API MIDDLEWARE" + " " * 15 + "|")
    print("+" + "=" * 68 + "+")
    print()
    print("[NOTA] Asegúrate de que el servidor esté corriendo:")
    print("       python src/api/chat_endpoint.py")
    print()

    try:
        # Verificar que el API esté disponible
        ejemplo_7_health_check()

        # Ejecutar ejemplos
        ejemplo_1_generar_y_usar_token()
        ejemplo_2_validar_token_antes_de_usar()
        ejemplo_3_token_expirado()
        ejemplo_4_validacion_local()
        ejemplo_5_generar_token_desde_api()
        ejemplo_6_integracion_javascript()

        print("=" * 70)
        print(" TODOS LOS EJEMPLOS COMPLETADOS")
        print("=" * 70)

    except requests.exceptions.ConnectionError:
        print()
        print("[ERROR] No se pudo conectar al servidor")
        print("Asegúrate de ejecutar primero:")
        print("  python src/api/chat_endpoint.py")
        print()


if __name__ == "__main__":
    main()
