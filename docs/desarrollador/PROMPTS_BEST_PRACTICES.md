# Buenas Prácticas — Sistema de Prompts (ReAct)

> **Última actualización:** 2026-03-28
> **Sistema:** ReAct Agent — `src/agents/react/prompts.py`

---

## Dónde viven los prompts

```
src/agents/react/
├── prompts.py    ← REACT_SYSTEM_PROMPT, REACT_USER_PROMPT
└── schemas.py    ← ReActResponse (schema JSON que devuelve el LLM)
```

El `REACT_SYSTEM_PROMPT` se rellena una vez con `{tools_description}` (generado por `ToolRegistry.get_tools_prompt()`).
El `REACT_USER_PROMPT` se rellena en cada iteración del loop con `{user_context}`, `{scratchpad}` y `{query}`.

---

## Principios del System Prompt

### 1. Identidad antes que instrucciones
Define quién es el bot (nombre, tono, empresa) en el primer párrafo. El LLM ancla su comportamiento a esta identidad.

```python
# Bien
REACT_SYSTEM_PROMPT = """Eres Iris, asistente virtual de Empresa S.A.
Responde siempre en español, con tono profesional pero amigable...

# Evitar
REACT_SYSTEM_PROMPT = """Sigue estas instrucciones:
1. Responde en español
2. Sé profesional...
```

### 2. Regla crítica: nunca revelar el proceso interno
El usuario **nunca** debe ver el JSON de razonamiento ni los pasos del loop.

```
REGLA CRÍTICA: Nunca muestres al usuario tu proceso de razonamiento,
los pasos "thought/action/observation", ni el JSON de respuesta.
Solo muestra el contenido de "final_answer".
```

### 3. Instrucciones de uso de tools con ejemplos
Para cada tool, describe **cuándo usarla** con ejemplos concretos de la empresa.

```
- database_query: úsala cuando el usuario pida datos específicos
  (ventas, clientes, inventario). Ejemplos: "¿cuántas ventas hubo?",
  "muéstrame los clientes del mes"
- knowledge_search: úsala para políticas, procesos y procedimientos.
  Ejemplos: "¿cómo solicito vacaciones?", "¿cuál es el proceso de..."
- finish: úsala directamente para saludos, agradecimientos o cuando
  ya tienes toda la información necesaria
```

### 4. Reglas SQL explícitas
Siempre incluir las restricciones de seguridad SQL:

```
REGLAS SQL OBLIGATORIAS:
- Solo consultas SELECT, WITH, o EXEC de stored procedures
- Nunca generar INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE
- Si el usuario pide modificar datos, responde que no tienes ese permiso
```

### 5. Formato de respuesta para Telegram

```
FORMATO DE RESPUESTA:
- Usa Markdown compatible con Telegram (*negrita*, _cursiva_, `código`)
- Respuestas concisas (máximo 3-4 párrafos para consultas simples)
- Para datos tabulares, usa listas con viñetas
- No uses HTML ni LaTeX
```

---

## Cómo modificar el System Prompt

### Cambiar personalidad del bot
```python
# src/config/personality.py
BOT_PERSONALITY = {
    "nombre": "Iris",
    "empresa": "Empresa S.A.",
    "tono": "profesional pero amigable",
}
```

### Agregar contexto de dominio
Añadir una sección al final de `REACT_SYSTEM_PROMPT`:

```python
## Contexto de la Empresa
- Base de datos: sistema de ventas con tablas Ventas, Clientes, Productos
- Knowledge base: políticas de RRHH, procesos operativos, FAQs
- Los usuarios son empleados internos con distintos roles y permisos
```

### Agregar ejemplos de queries (mejora la precisión)
```python
## Ejemplos de Consultas Frecuentes
Usuario: "¿Cuántas ventas hubo ayer?"
→ Usa database_query con "ventas de ayer"

Usuario: "¿Cómo solicito mis vacaciones?"
→ Usa knowledge_search con "solicitar vacaciones"
```

---

## Cómo modificar el User Prompt

El `REACT_USER_PROMPT` se construye en cada iteración del loop en `ReActAgent.execute()`.

```python
REACT_USER_PROMPT = """
## Contexto del usuario
{user_context}          # nombre, rol, historial reciente

## Historial de razonamiento
{scratchpad}            # pasos anteriores del loop (vacío en primera iteración)

## Consulta
{query}

Responde en JSON válido:
{
    "thought": "...",
    "action": "nombre_tool o finish",
    "action_input": {...},
    "final_answer": "solo cuando action == finish"
}
"""
```

> No cambiar el formato JSON — `ReActResponse` (Pydantic) valida exactamente esa estructura.

---

## Debugging de prompts

### Síntomas y causas comunes

| Síntoma | Causa probable | Fix |
|---------|---------------|-----|
| LLM usa tool incorrecta | Descripción de tool ambigua | Agregar ejemplos en el system prompt |
| LLM revela JSON al usuario | Falta la regla crítica | Agregar "REGLA CRÍTICA: no revelar proceso" |
| LLM genera SQL con INSERT | Falta restricción SQL | Agregar reglas SQL explícitas |
| Respuestas muy largas | Sin guía de formato | Agregar límites de longitud |
| Loop no termina | LLM no llega a "finish" | Agregar ejemplo de cuándo usar finish |

---

## Schema de respuesta

```python
# src/agents/react/schemas.py
class ReActResponse(BaseModel):
    thought: str                   # razonamiento interno (no visible al usuario)
    action: str                    # "finish" o nombre exacto de una tool
    action_input: dict             # parámetros para la tool
    final_answer: Optional[str]    # solo cuando action == "finish"
```

Si el LLM devuelve JSON malformado, `OpenAIProvider.generate_structured()` reintenta automáticamente antes de lanzar excepción.
