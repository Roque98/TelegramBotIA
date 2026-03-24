# PLAN: Soporte multimedia en el bot

> **Objetivo**: Permitir que el bot reciba y procese imágenes, documentos y audio de los usuarios
> **Rama**: `feature/fun-23-multimedia`
> **Prioridad**: 🟢 Funcional
> **Progreso**: 0% (0/8)

---

## Contexto

El bot actualmente solo procesa mensajes de texto. Casos de uso reales que requieren multimedia:

- **Imágenes**: Usuario manda foto de un error de sistema ("¿qué significa este error?")
- **Documentos PDF**: Usuario sube un recibo para solicitar reembolso
- **Audio/voz**: Usuario manda nota de voz en lugar de escribir
- **Screenshots**: Usuario manda captura de pantalla de un problema en algún sistema

OpenAI GPT-4 Vision ya soporta imágenes. Whisper soporta transcripción de audio.

---

## Tipos de multimedia a soportar

| Tipo | Handler Telegram | API OpenAI | Caso de uso |
|------|-----------------|------------|-------------|
| Imagen (JPG/PNG) | `MessageHandler(filters.PHOTO)` | GPT-4 Vision | Identificar errores en pantallas |
| Documento PDF | `MessageHandler(filters.Document.PDF)` | Extraer texto + GPT | Procesar recibos |
| Audio/voz | `MessageHandler(filters.VOICE)` | Whisper → texto | Transcribir nota de voz |
| Documento general | `MessageHandler(filters.Document.ALL)` | Según tipo | Contexto adicional |

---

## Archivos involucrados

- `src/bot/handlers/` — nuevos handlers multimedia
- `src/agents/providers/openai_provider.py` — agregar soporte de Vision y Whisper
- `src/agents/tools/` — posible herramienta `ImageAnalysisTool`
- `src/config/settings.py` — `MULTIMEDIA_ENABLED`, tamaño máximo de archivo

---

## Tareas

- [ ] **23.1** Agregar método `analyze_image(image_bytes, prompt)` en `openai_provider.py` usando GPT-4 Vision
- [ ] **23.2** Agregar método `transcribe_audio(audio_bytes)` en `openai_provider.py` usando Whisper
- [ ] **23.3** Crear `src/bot/handlers/media_handlers.py` con:
  - Handler para fotos: descarga + analiza con Vision + responde
  - Handler para audio/voz: descarga + transcribe + procesa como texto
  - Handler para documentos PDF: extrae texto + resume
- [ ] **23.4** Registrar los nuevos handlers en la aplicación principal
- [ ] **23.5** Agregar validación de tamaño máximo de archivo (default: 10MB)
- [ ] **23.6** Agregar `MULTIMEDIA_ENABLED` en `settings.py` (para activar/desactivar fácilmente)
- [ ] **23.7** Manejar el caso donde el modelo configurado no soporta Vision (ej. gpt-4o-mini vs gpt-4o)
- [ ] **23.8** Agregar tests con archivos multimedia de prueba (fixtures)

---

## Criterios de aceptación

- El bot responde a fotos analizando su contenido
- Las notas de voz son transcritas y procesadas como texto
- Los documentos PDF son resumidos o analizados según la pregunta del usuario
- Archivos mayores a 10MB son rechazados con mensaje claro
- Si `MULTIMEDIA_ENABLED=false`, el bot responde "no puedo procesar multimedia" en lugar de ignorar
