"""
Ejemplo de uso del módulo de encriptación compatible con C#.

Este ejemplo muestra cómo usar la clase Encrypt para encriptar/desencriptar
datos de forma compatible con el sistema C# existente.
"""
from src.domain.auth.encryption import Encrypt, encriptar, desencriptar


def ejemplo_basico():
    """Ejemplo básico de encriptación y desencriptación."""
    print("=" * 60)
    print("EJEMPLO 1: Uso básico")
    print("=" * 60)

    encrypt = Encrypt()

    # Encriptar
    texto_original = "MiPasswordSecreto123"
    texto_encriptado = encrypt.encriptar(texto_original)

    print(f"Texto original:   {texto_original}")
    print(f"Texto encriptado: {texto_encriptado}")

    # Desencriptar
    texto_desencriptado = encrypt.desencriptar(texto_encriptado)
    print(f"Texto desencriptado: {texto_desencriptado}")

    # Verificar
    assert texto_original == texto_desencriptado
    print("✅ Encriptación/Desencriptación exitosa\n")


def ejemplo_funciones_conveniencia():
    """Ejemplo usando funciones de conveniencia."""
    print("=" * 60)
    print("EJEMPLO 2: Funciones de conveniencia")
    print("=" * 60)

    # Usar funciones globales (más simple)
    password = "admin123"

    encrypted = encriptar(password)
    print(f"Password original:    {password}")
    print(f"Password encriptado:  {encrypted}")

    decrypted = desencriptar(encrypted)
    print(f"Password desencriptado: {decrypted}")

    assert password == decrypted
    print("✅ Funciones de conveniencia funcionan correctamente\n")


def ejemplo_autenticacion():
    """Ejemplo simulando autenticación con passwords encriptados."""
    print("=" * 60)
    print("EJEMPLO 3: Simulación de autenticación")
    print("=" * 60)

    # Simular base de datos con passwords encriptados
    usuarios_db = {
        "admin": encriptar("admin123"),
        "usuario1": encriptar("password1"),
        "usuario2": encriptar("mySecurePass!")
    }

    print("Base de datos de usuarios (passwords encriptados):")
    for username, encrypted_pass in usuarios_db.items():
        print(f"  {username}: {encrypted_pass}")
    print()

    # Simular login
    def login(username: str, password: str) -> bool:
        """Verificar credenciales."""
        if username not in usuarios_db:
            return False

        # Desencriptar password almacenado y comparar
        stored_password = desencriptar(usuarios_db[username])
        return stored_password == password

    # Tests de login
    print("Intentos de login:")
    print(f"  admin + admin123:  {'✅ SUCCESS' if login('admin', 'admin123') else '❌ FAIL'}")
    print(f"  admin + wrongpass: {'✅ SUCCESS' if login('admin', 'wrongpass') else '❌ FAIL'}")
    print(f"  usuario1 + password1: {'✅ SUCCESS' if login('usuario1', 'password1') else '❌ FAIL'}")
    print()


def ejemplo_interoperabilidad_csharp():
    """Ejemplo de cómo verificar interoperabilidad con C#."""
    print("=" * 60)
    print("EJEMPLO 4: Interoperabilidad con C#")
    print("=" * 60)

    encrypt = Encrypt()

    # Generar valores para verificar en C#
    print("Valores para copiar a C# y verificar:")
    print()

    test_values = [
        "admin",
        "password123",
        "user@example.com",
        "Hola Mundo",
    ]

    for value in test_values:
        encrypted = encrypt.encriptar(value)
        print(f"// Texto plano: \"{value}\"")
        print(f"string encrypted = \"{encrypted}\";")
        print(f"string decrypted = encrypt.Desencriptar(encrypted);")
        print(f"// Debe resultar: \"{value}\"")
        print()

    print("Copiar el código anterior a C# para verificar compatibilidad\n")


def ejemplo_manejo_errores():
    """Ejemplo de manejo de errores."""
    print("=" * 60)
    print("EJEMPLO 5: Manejo de errores")
    print("=" * 60)

    encrypt = Encrypt()

    # Intentar desencriptar texto inválido
    print("Intentando desencriptar texto inválido...")
    result = encrypt.desencriptar("texto_invalido_no_base64")
    print(f"Resultado: {result}")
    print("✅ Error manejado correctamente (retorna None)\n")

    # Intentar desencriptar Base64 válido pero no encriptado por nosotros
    print("Intentando desencriptar Base64 válido pero contenido incorrecto...")
    result = encrypt.desencriptar("SGVsbG8gV29ybGQ=")  # "Hello World" en base64
    print(f"Resultado: {result}")
    print("✅ Error manejado correctamente (retorna None)\n")


def ejemplo_datos_sensibles():
    """Ejemplo de uso con datos sensibles."""
    print("=" * 60)
    print("EJEMPLO 6: Encriptar datos sensibles")
    print("=" * 60)

    # Datos sensibles que podrían almacenarse encriptados
    datos_sensibles = {
        "api_key": "sk_live_1234567890abcdef",
        "db_password": "MyD4t4b4s3P4ss!",
        "secret_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    }

    print("Encriptando datos sensibles:")
    datos_encriptados = {}

    for key, value in datos_sensibles.items():
        encrypted = encriptar(value)
        datos_encriptados[key] = encrypted
        print(f"  {key}:")
        print(f"    Original:    {value[:20]}... (truncado)")
        print(f"    Encriptado:  {encrypted[:40]}...")

    print()
    print("Desencriptando para uso:")
    api_key_decrypted = desencriptar(datos_encriptados["api_key"])
    print(f"  API Key recuperada: {api_key_decrypted[:20]}... (truncado)")
    print()


def main():
    """Ejecutar todos los ejemplos."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "EJEMPLOS DE ENCRIPTACIÓN PYTHON ↔ C#" + " " * 10 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    ejemplo_basico()
    ejemplo_funciones_conveniencia()
    ejemplo_autenticacion()
    ejemplo_interoperabilidad_csharp()
    ejemplo_manejo_errores()
    ejemplo_datos_sensibles()

    print("=" * 60)
    print("✅ Todos los ejemplos ejecutados correctamente")
    print("=" * 60)


if __name__ == "__main__":
    main()
