# PLAN_ARQ_33 — Instrucciones de uso de tools dinámicas en system prompt

**ID**: ARQ-33
**Tipo**: Arquitectura / Calidad
**Rama**: `develop`
**Estado**: Completado
**Creado**: 2026-04-08
**Completado**: 2026-04-08

---

## Problema

`REACT_SYSTEM_PROMPT` en `prompts.py` tiene instrucciones de uso **hardcodeadas** que
mencionan tools por nombre (líneas 59–63):

```
2. Para datos de negocio... debes llamar a "database_query"
3. Para políticas/procedimientos: Usa "knowledge_search"
4. Para cálculos: Usa "calculate"
5. Para fechas: Usa "datetime"
```

Aunque `{tools_description}` se filtra por permisos del usuario, estas líneas siempre
se incluyen en el system prompt. Resultado: el LLM conoce el nombre de tools desactivadas
y las intenta usar (comportamiento observado con `knowledge_search` desactivada).

---

## Solución

Cada tool declara su propio `usage_hint` — una instrucción de cuándo usarla.
El registry genera la lista de hints solo para las tools visibles del usuario.
El system prompt inyecta esa lista dinámica en lugar de las instrucciones hardcodeadas.

### Flujo resultante

```
ToolDefinition.usage_hint         → definido por cada tool (opcional)
ToolRegistry.get_usage_hints()    → filtra por permisos, retorna lista de hints
build_system_prompt(hints=...)    → inyecta como {usage_hints} en el prompt
agent.execute()                   → pasa hints del registry filtrado
```

---

## Tareas

### Fase 1 — Modelo [ 2/2 ]
- [x] `tools/base.py`: agregar campo `usage_hint: Optional[str] = None` a `ToolDefinition`
- [x] `tools/registry.py`: agregar método `get_usage_hints(user_context)` que retorna
      los hints de las tools visibles, con numeración automática

### Fase 2 — Tools [ 7/7 ]
Agregar `usage_hint` en el `definition` de cada tool relevante.
`reload_permissions_tool.py` es una tool interna — no necesita usage_hint.
- [x] `database_tool.py` — "Para datos de negocio (ventas, reportes, usuarios): usa `database_query`. **Obligatorio** antes de responder con cifras."
- [x] `knowledge_tool.py` — "Para políticas, procedimientos o preguntas sobre la empresa: usa `knowledge_search`"
- [x] `calculate_tool.py` — "Para cálculos matemáticos: usa `calculate`"
- [x] `datetime_tool.py` — "Para fechas, horas o diferencias de tiempo: usa `datetime`"
- [x] `save_memory_tool.py` — "Para recordar datos del usuario entre sesiones: usa `save_memory`"
- [x] `read_attachment_tool.py` — "Para leer archivos adjuntos enviados por el usuario: usa `read_attachment`"
- [x] `preference_tool.py` — "Para guardar preferencias del usuario (idioma, formato, alias): usa `save_preference`"

### Fase 3 — Prompt [ 3/3 ]
- [x] `prompts.py`: reemplazar instrucciones hardcodeadas (2–5) con `{usage_hints}`
- [x] `prompts.py`: reemplazar el ejemplo "Consulta de datos" (usaba `database_query` hardcodeado) con un ejemplo de `calculate` que siempre aplica
- [x] `build_system_prompt()`: aceptar parámetro `usage_hints: str` e inyectarlo

### Fase 4 — Agent [ 1/1 ]
- [x] `agent.py`: pasar `usage_hints` desde el registry al construir el system prompt

---

## Resultado esperado

Con `database_query` y `knowledge_search` desactivadas en `BotIAv2_Recurso`,
el system prompt de un usuario que solo tiene `calculate`, `datetime`, `save_memory`,
`reload_permissions` y `read_attachment` **no contendrá ninguna mención** a
`database_query` ni `knowledge_search`.

El LLM no podrá intentar usar tools que no conoce.
