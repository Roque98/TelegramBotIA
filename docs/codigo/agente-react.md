# Agente ReAct

El `ReActAgent` es el componente central del sistema. Implementa el patrón
Think-Act-Observe: el LLM alterna entre razonar, llamar tools y observar resultados
hasta tener suficiente información para responder.

**Archivo**: `src/agents/react/agent.py`

---

## Componentes internos

| Componente | Archivo | Responsabilidad |
|------------|---------|-----------------|
| `ReActAgent` | `react/agent.py` | Orquesta el loop completo |
| `Scratchpad` | `react/scratchpad.py` | Acumula pasos thought/action/observation |
| `ReActResponse` | `react/schemas.py` | Schema Pydantic de la respuesta del LLM |
| `build_system_prompt` | `react/prompts.py` | Construye el prompt del sistema |
| `build_user_prompt` | `react/prompts.py` | Construye el prompt inicial |
| `build_continue_prompt` | `react/prompts.py` | Construye el prompt post-observación |
| `build_synthesis_prompt` | `react/prompts.py` | Construye el prompt de síntesis parcial |

---

## Dos modelos LLM

El agente usa dos instancias de `OpenAIProvider` con modelos distintos:

| Modelo | Variable | Uso |
|--------|----------|-----|
| `gpt-5.4-mini` | `openai_loop_model` | Loop ReAct: razonamiento, selección de tool, respuesta final |
| `gpt-5.4` | `openai_data_model` | `DatabaseTool`: generación de SQL complejo |

El modelo más económico maneja el loop (muchas llamadas). El modelo más capaz se reserva
para la tarea que requiere mayor precisión: traducir lenguaje natural a SQL.

---

## El system prompt

El system prompt define la identidad, el formato esperado y las instrucciones de uso.
Se construye dinámicamente en cada request via `build_system_prompt()`.

### Secciones del prompt

1. **Personalidad de Amber**: tono, idioma, uso de emojis
2. **Formato de mensajes Telegram**: cuándo usar negrita, listas, bloques de código
3. **Regla crítica**: nunca revelar el proceso interno al usuario
4. **Cómo razonar**: descripción del loop Think-Act-Observe
5. **Herramientas disponibles** (`{tools_description}`): lista dinámica filtrada por permisos
6. **Instrucciones importantes**:
   - `{usage_hints}`: cuándo usar cada tool (dinámico, filtrado por permisos)
   - Reglas de contexto conversacional
7. **Formato de respuesta**: JSON estructurado obligatorio
8. **Ejemplos**: casos de uso concretos

### Inyección dinámica (ARQ-33)

```python
# src/agents/react/agent.py (~línea 167)
system_prompt = build_system_prompt(
    tools_description=self.tools.get_tools_prompt(user_context=context),
    usage_hints=self.tools.get_usage_hints(user_context=context),
)
```

Ambos valores son generados por `ToolRegistry` filtrando por los permisos del usuario.
Si una tool está deshabilitada (`permisos["tool:X"] == False`), ni su descripción ni
su `usage_hint` aparecen en el prompt — el LLM no puede invocarla porque no sabe que existe.

---

## El formato de respuesta del LLM

El LLM siempre debe responder con este JSON:

```json
{
  "thought": "Mi razonamiento sobre qué hacer ahora",
  "action": "nombre_de_la_accion",
  "action_input": {"param": "valor"},
  "final_answer": null
}
```

Cuando termina:

```json
{
  "thought": "Ya tengo la información. Puedo responder.",
  "action": "finish",
  "action_input": {},
  "final_answer": "La respuesta formateada para el usuario"
}
```

El schema `ReActResponse` (Pydantic) valida esta estructura. Si el LLM genera JSON
malformado, el agente reintenta con `generate_structured()` del provider.

---

## El scratchpad

El `Scratchpad` acumula el historial de pasos como texto para incluirlo en el siguiente
prompt. Cada paso se ve así en el prompt:

```
Thought: Necesito consultar la base de datos para las ventas de ayer
Action: database_query
Action Input: {"query": "ventas de ayer"}
Observation: Se encontraron 45 ventas por un total de $127.500

Thought: Ya tengo los datos. Puedo formular la respuesta.
Action: finish
```

El `UserContext.working_memory` (últimas interacciones) también se incluye en el
`user_prompt` para dar continuidad conversacional entre sesiones.

---

## Síntesis parcial

Si el loop alcanza `max_iterations` (10) sin llegar a "finish", el agente no falla
silenciosamente. En su lugar, llama a `synthesize_partial()`:

```python
# build_synthesis_prompt incluye:
# - el scratchpad acumulado (todo lo que investigó)
# - la consulta original
# El LLM genera una respuesta parcial pero útil
```

---

## Filtrado de tools por permisos

La lógica de filtrado está en `ToolRegistry`:

```python
# src/agents/tools/registry.py

def get_tools_prompt(self, user_context=None) -> str:
    """Genera lista de tools visibles para este usuario."""
    if permisos_loaded:
        # Mostrar solo tools autorizadas
        visible = [t for t in self._tools.values()
                   if permisos.get(f"tool:{t.name}", False)]
    else:
        # Sin permisos cargados: solo las siempre visibles
        _ALWAYS_VISIBLE = {"reload_permissions", "finish"}
        visible = [t for t in self._tools.values()
                   if t.name in _ALWAYS_VISIBLE]
    ...

def get_usage_hints(self, user_context=None) -> str:
    """Genera instrucciones de uso solo para tools visibles."""
    # Misma lógica de filtrado
    hints = [t.definition.usage_hint for t in visible if t.definition.usage_hint]
    return "\n".join(f"{i+2}. {hint}" for i, hint in enumerate(hints))
```

---

## Excepciones

```python
# src/agents/base/exceptions.py
class AgentException(Exception): ...
class LLMException(AgentException): ...        # Error en la llamada al LLM
class ToolException(AgentException): ...       # Error al ejecutar una tool
class MaxIterationsException(AgentException): ...  # Se alcanzó max_iterations
class AgentTimeoutException(AgentException): ... # Timeout global del agente
```

Los errores de LLM y BD tienen retry automático configurado en `settings.py`
(`RETRY_LLM_MAX_ATTEMPTS`, `RETRY_DB_MAX_ATTEMPTS`).

---

**← Anterior** [Flujos del sistema](flujos.md) · [Índice](README.md) · **Siguiente →** [Sistema de tools](tools.md)
