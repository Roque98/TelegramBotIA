# Sistema de Prompts

## Ubicación

```
src/agents/react/prompts.py   ← Prompts del ReAct Agent (activos)
src/config/personality.py     ← Personalidad del bot
```

---

## ReAct System Prompt

**Archivo**: `src/agents/react/prompts.py`
**Variable**: `REACT_SYSTEM_PROMPT`

El prompt del sistema define a **"Iris"** (nombre que usa el bot en el API REST / contexto genérico). En Telegram el bot puede presentarse distinto según `personality.py`.

**Estructura del prompt**:
```
1. Definición de identidad y personalidad
   - Nombre: Iris
   - Tono: cálida, profesional, español
   - REGLA CRÍTICA: nunca revelar proceso interno al usuario

2. Instrucciones de razonamiento (interno — no visible al usuario)
   - Thought → Action → Observation → Repeat
   - Usar "finish" para respuesta final

3. Herramientas disponibles
   - Generadas dinámicamente con {tools_description}
   - Incluye nombre, descripción y parámetros de cada tool

4. Instrucciones de uso
   - finish directamente para saludos / conversación casual
   - Cuándo usar cada tool
   - Reglas de seguridad SQL (solo SELECT)
   - Formato de respuesta
```

**Plantilla**:
```python
REACT_SYSTEM_PROMPT = """Eres Iris, una asistente virtual...

## Herramientas Disponibles
{tools_description}

- **finish**: Termina el razonamiento y da tu respuesta final
  - Parameters: {"answer": "Tu respuesta al usuario"}
...
"""
```

---

## Prompt de Usuario (cada turno del loop)

**Variable**: `REACT_USER_PROMPT`

```python
REACT_USER_PROMPT = """
## Contexto del usuario
{user_context}

## Historial de razonamiento (si aplica)
{scratchpad}

## Consulta del usuario
{query}

Responde en JSON:
{
    "thought": "...",
    "action": "nombre_de_tool o finish",
    "action_input": {...},
    "final_answer": "solo si action es finish"
}
"""
```

El agente llama a `OpenAIProvider.generate_structured()` con este prompt y el schema `ReActResponse` para obtener JSON validado por Pydantic.

---

## Generación Dinámica de `tools_description`

**Archivo**: `src/agents/tools/registry.py` → `ToolRegistry.get_tools_prompt()`

Genera automáticamente la lista de tools para incluir en el system prompt:

```
- **database_query**: Ejecuta consultas SQL en lenguaje natural
  - query (string, required): La consulta en lenguaje natural

- **knowledge_search**: Busca en la base de conocimiento empresarial
  - query (string, required): Término o pregunta a buscar

- **calculate**: Evalúa expresiones matemáticas
  - expression (string, required): Expresión matemática

- **get_datetime**: Obtiene fecha y hora actual
  (sin parámetros)

- **save_preference**: Guarda preferencia del usuario
  - key (string, required): Nombre de la preferencia
  - value (string, required): Valor de la preferencia
```

---

## Personalidad del Bot

**Archivo**: `src/config/personality.py`

```python
BOT_PERSONALITY = {
    "nombre": "Iris",
    "empresa": "Tu Empresa",
    "descripcion": "Asistente virtual inteligente",
    "tono": "profesional pero amigable",
    "caracteristicas": [
        "Responde de forma concisa",
        "Usa emojis con moderación",
        "Es honesto cuando no sabe algo"
    ],
    "idioma": "español"
}

def get_personality_prompt() -> str:
    """Genera string de personalidad para incluir en prompts."""
```

> **Nota**: El API REST usa "Iris" (hardcodeado en `react/prompts.py`). El bot de Telegram usa "Iris" vía `personality.py`. Estos pueden unificarse en el futuro.

---

## Schema de Respuesta del LLM

**Archivo**: `src/agents/react/schemas.py`

```python
class ActionType(str, Enum):
    FINISH = "finish"
    # (nombres de tools se validan contra el registry)

class ReActResponse(BaseModel):
    thought: str                   # Razonamiento interno
    action: str                    # "finish" o nombre de tool
    action_input: dict             # Parámetros para la tool
    final_answer: Optional[str]    # Solo cuando action == "finish"

class ReActStep(BaseModel):
    thought: str
    action: str
    action_input: dict
    observation: str               # Resultado de la tool
    timestamp: datetime
```

---

## Prácticas de Modificación

### Para cambiar la personalidad del bot
Editar `src/config/personality.py` y/o el `REACT_SYSTEM_PROMPT` en `src/agents/react/prompts.py`.

### Para agregar instrucciones específicas de dominio
Modificar `REACT_SYSTEM_PROMPT` — agregar sección con contexto empresarial, restricciones de negocio, ejemplos de queries, etc.

### Para cambiar el formato de respuesta del LLM
Modificar `ReActResponse` en `schemas.py` y actualizar las referencias en `react/agent.py`.
