# Preguntas de prueba — Tools del agente

Archivo de referencia para validar manualmente que cada tool responde correctamente.
Enviar estas preguntas al bot y verificar el comportamiento esperado.

---

## CalculateTool

**Objetivo**: verificar que usa la tool `calculate` y que la respuesta es directa (sin estructura).

| # | Pregunta | Resultado esperado | Formato esperado |
|---|----------|--------------------|-----------------|
| 1 | ¿Cuánto es el 15% de 8,450? | 1,267.5 | Una línea |
| 2 | ¿Cuánto es el 21% de 12,000? | 2,520 | Una línea |
| 3 | Si tengo 3 vendedores con comisiones de 1,200, 980 y 1,540 ¿cuál es el total? | 3,720 | Una línea |
| 4 | ¿Cuánto es la raíz cuadrada de 144? | 12 | Una línea |
| 5 | Si vendo 250 unidades a $38.50 cada una ¿cuánto es el total? | 9,625 | Una línea |
| 6 | ¿Cuánto es 2 elevado a la 10? | 1,024 | Una línea |

---

## DateTimeTool

**Objetivo**: verificar que usa `datetime` y devuelve fechas correctas.

| # | Pregunta | Comportamiento esperado |
|---|----------|------------------------|
| 1 | ¿Qué día es hoy? | Fecha actual (ej: martes 7 de abril de 2026) |
| 2 | ¿Qué hora es? | Hora actual |
| 3 | ¿Cuántos días faltan para el 31 de diciembre? | Número de días correcto |
| 4 | ¿En qué fecha cae el próximo viernes? | Fecha correcta |
| 5 | ¿Cuántos días han pasado desde el 1 de enero? | Número correcto |
| 6 | ¿Qué fecha era hace 30 días? | Fecha correcta |

---

## KnowledgeTool

**Objetivo**: verificar que usa `knowledge_search` y devuelve información de la base de conocimiento (no inventa).

> Ajustar las preguntas según el contenido real cargado en la BD.

| # | Pregunta | Comportamiento esperado |
|---|----------|------------------------|
| 1 | ¿Cómo solicito vacaciones? | Respuesta desde knowledge base |
| 2 | ¿Cuál es la política de uso del sistema? | Respuesta desde knowledge base |
| 3 | ¿A quién contacto si tengo un problema técnico? | Respuesta desde knowledge base |
| 4 | ¿Qué procedimiento sigo para reportar un error en facturación? | Respuesta desde knowledge base |
| 5 | ¿Cómo me registro al sistema? | Respuesta desde knowledge base |

**Caso negativo**:
| # | Pregunta | Comportamiento esperado |
|---|----------|------------------------|
| 6 | ¿Cuál es la receta del mole poblano? | No encontré información sobre eso en la base de conocimiento |

---

## SavePreferenceTool

**Objetivo**: verificar que persiste preferencias y las respeta en la misma sesión.

| # | Pregunta | Comportamiento esperado |
|---|----------|------------------------|
| 1 | Llámame Roque en lugar de Angel | Confirma que guardó el alias |
| 2 | Prefiero que me respondas siempre en inglés | Confirma y responde en inglés desde ese punto |
| 3 | Prefiero respuestas en formato de lista cuando sean datos | Confirma preferencia |

**Verificación post-guardado**:
| # | Pregunta | Comportamiento esperado |
|---|----------|------------------------|
| 4 | *(después del #1)* ¿Cómo me llamo? | Responde "Roque" |
| 5 | *(después del #2)* What time is it? | Responde en inglés |

---

## SaveMemoryTool

**Objetivo**: verificar que guarda hechos y los usa más adelante en la conversación.

| # | Pregunta | Comportamiento esperado |
|---|----------|------------------------|
| 1 | Recuerda que estoy trabajando en el cierre del mes de marzo | Confirma que lo recordó |
| 2 | Anota que necesito revisar los números de ventas de Monterrey | Confirma |
| 3 | *(después del #1)* ¿En qué estoy trabajando? | Menciona el cierre de marzo |

---

## ReloadPermissionsTool

**Objetivo**: verificar que ejecuta la recarga y reporta las capacidades disponibles.
> Requiere rol Administrador.

| # | Pregunta | Comportamiento esperado |
|---|----------|------------------------|
| 1 | Recarga mis permisos | Confirma recarga y lista las capacidades disponibles |
| 2 | Actualiza los permisos del sistema | Mismo comportamiento |

---

## ReadAttachmentTool

**Objetivo**: verificar lectura de archivos adjuntos.

| # | Acción | Comportamiento esperado |
|---|--------|------------------------|
| 1 | Enviar imagen + "¿Qué dice esta imagen?" | Describe el contenido |
| 2 | Enviar PDF + "Resume este documento" | Resumen del contenido |
| 3 | Enviar imagen + "¿Qué número aparece aquí?" | Extrae el número |

---

## Combinadas (multi-tool)

**Objetivo**: verificar que el agente encadena tools correctamente.

| # | Pregunta | Tools esperadas | Comportamiento esperado |
|---|----------|-----------------|------------------------|
| 1 | ¿Qué hora es y cuánto es el 20% de 5,000? | datetime + calculate | Ambas respuestas en un mensaje |
| 2 | Recuerda que mi meta mensual es 50,000 y calcúlame el 30% | save_memory + calculate | Guarda y calcula |
| 3 | ¿Cuántos días faltan para fin de año y cuánto es el 10% de 120,000? | datetime + calculate | Ambas respuestas |

---

## Casos límite / negativos

| # | Pregunta | Comportamiento esperado |
|---|----------|------------------------|
| 1 | ¿Cuánto es "hola" por 5? | Error amigable: no es una expresión válida |
| 2 | ¿Qué pasó en la segunda guerra mundial? | Responde desde conocimiento general o dice que no tiene esa info |
| 3 | Divide 10 entre 0 | Maneja división por cero con mensaje claro |
