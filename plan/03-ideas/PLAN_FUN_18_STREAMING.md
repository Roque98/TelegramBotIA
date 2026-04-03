# PLAN: Streaming de respuestas en Telegram

> **Objetivo**: Mostrar la respuesta del LLM de forma progresiva en lugar de esperar a que termine
> **Rama**: `feature/fun-18-streaming`
> **Prioridad**: 🟢 Funcional
> **Progreso**: 0% (0/7)

---

## Contexto

Actualmente el bot espera a que el LLM genere toda la respuesta (~2-5 segundos) y luego envía un solo mensaje. El usuario ve "escribiendo..." por varios segundos sin feedback.

Con streaming, el bot puede editar el mensaje en tiempo real mientras el LLM genera texto, similar a cómo funciona ChatGPT. Esto mejora percepción de velocidad sin cambiar la latencia real.

---

## Componentes necesarios

1. **OpenAI streaming**: `openai` SDK ya soporta `stream=True`
2. **Telegram message editing**: `bot.edit_message_text()` para actualizar el mensaje
3. **Throttle de ediciones**: Telegram tiene límite de ~20 ediciones/segundo — editar cada 500ms es suficiente
4. **Fallback**: Si streaming falla, caer al modo normal

---

## Archivos involucrados

- `src/agents/providers/openai_provider.py` — agregar modo streaming
- `src/agents/react/agent.py` — pasar callback de streaming
- `src/gateway/handler.py` — manejar respuesta streaming en Telegram
- `src/config/settings.py` — `LLM_STREAMING_ENABLED`

---

## Tareas

- [ ] **18.1** Agregar método `stream_completion(prompt, callback)` en `openai_provider.py` usando `stream=True`
- [ ] **18.2** Crear `StreamingBuffer` en `gateway/handler.py` que acumule chunks y edite el mensaje cada 500ms
- [ ] **18.3** Modificar `handler.py` para enviar primero un mensaje placeholder y luego editarlo progresivamente
- [ ] **18.4** Agregar indicador visual mientras se genera: mostrar `▌` al final del texto en progreso
- [ ] **18.5** Implementar fallback automático a modo normal si falla la edición del mensaje
- [ ] **18.6** Agregar `LLM_STREAMING_ENABLED` en `settings.py` para activar/desactivar
- [ ] **18.7** Agregar tests con mock del provider para verificar que los chunks se acumulan correctamente

---

## Criterios de aceptación

- El usuario ve el texto aparecer progresivamente en Telegram
- Las ediciones del mensaje no exceden el límite de rate de Telegram
- Si el streaming falla, el bot cae a modo normal sin error visible al usuario
- El streaming es activable/desactivable desde config
