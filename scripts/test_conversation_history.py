"""
Script de prueba para el sistema de historial conversacional.

Demuestra cómo el bot mantiene contexto de los últimos mensajes.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.conversation_history import ConversationHistory


def test_conversation_history():
    """Probar el sistema de historial conversacional."""
    print("=" * 80)
    print("PRUEBA DE HISTORIAL CONVERSACIONAL")
    print("=" * 80)

    # Crear gestor de historial
    history = ConversationHistory(max_messages=3)

    # Simular una conversación
    user_id = 1
    print(f"\nSimulando conversacion del usuario {user_id}:\n")

    # Mensaje 1
    print("Usuario: ¿Cuántos usuarios hay?")
    history.add_user_message(user_id, "¿Cuántos usuarios hay?")
    history.add_bot_response(user_id, "Hay 150 usuarios registrados en el sistema.")

    # Mensaje 2
    print("Iris: Hay 150 usuarios registrados en el sistema.\n")
    print("Usuario: ¿Y cuántos están activos?")
    history.add_user_message(user_id, "¿Y cuántos están activos?")
    history.add_bot_response(user_id, "De esos 150 usuarios, 120 están activos actualmente.")

    # Mensaje 3
    print("Iris: De esos 150 usuarios, 120 están activos actualmente.\n")
    print("Usuario: Muéstrame los últimos 5")
    history.add_user_message(user_id, "Muéstrame los últimos 5")

    # Obtener contexto
    print("\n" + "=" * 80)
    print("CONTEXTO QUE RECIBIRÁ EL LLM:")
    print("=" * 80)
    context = history.get_context_string(user_id, include_last_n=2)
    print(context)

    # Estadísticas
    print("=" * 80)
    print("ESTADÍSTICAS DEL HISTORIAL:")
    print("=" * 80)
    stats = history.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Mostrar mensajes completos
    print("\n" + "=" * 80)
    print("MENSAJES ALMACENADOS:")
    print("=" * 80)
    messages = history.get_recent_messages(user_id)
    for i, msg in enumerate(messages, 1):
        role = "Iris" if msg.is_bot_response else "Usuario"
        print(f"{i}. [{msg.timestamp.strftime('%H:%M:%S')}] {role}: {msg.message[:50]}...")

    print("\n" + "=" * 80)
    print("PRUEBA COMPLETADA")
    print("=" * 80)


if __name__ == "__main__":
    test_conversation_history()
