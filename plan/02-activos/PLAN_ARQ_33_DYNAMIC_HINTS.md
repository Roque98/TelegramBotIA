# PLAN_ARQ_33 — Instrucciones de uso de tools dinámicas en system prompt

**ID**: ARQ-33
**Tipo**: Arquitectura / Calidad
**Rama**: `develop`
**Estado**: En progreso
**Creado**: 2026-04-08

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

### Fase 1 — Modelo [ 0/2 ]
- [ ] `tools/base.py`: agregar campo `usage_hint: Optional[str] = None` a `ToolDefinition`
- [ ] `tools/registry.py`: agregar método `get_usage_hints(user_context)` que retorna
      los hints de las tools visibles, con numeración automática

### Fase 2 — Tools [ 0/6 ]
Agregar `usage_hint` en el `definition` de cada tool relevante:
- [ ] `database_tool.py` — "Para datos de negocio (ventas, reportes, usuarios): usa `database_query`. **Obligatorio** antes de responder con cifras."
- [ ] `knowledge_tool.py` — "Para políticas, procedimientos o preguntas sobre la empresa: usa `knowledge_search`"
- [ ] `calculate_tool.py` — "Para cálculos matemáticos: usa `calculate`"
- [ ] `datetime_tool.py` — "Para fechas, horas o diferencias de tiempo: usa `datetime`"
- [ ] `save_memory_tool.py` — "Para recordar datos del usuario entre sesiones: usa `save_memory`"
- [ ] `read_attachment_tool.py` — "Para leer archivos adjuntos enviados por el usuario: usa `read_attachment`"

### Fase 3 — Prompt [ 0/2 ]
- [ ] `prompts.py`: reemplazar instrucciones hardcodeadas (2–5) con `{usage_hints}`
- [ ] `build_system_prompt()`: aceptar parámetro `usage_hints: str` e inyectarlo

### Fase 4 — Agent [ 0/1 ]
- [ ] `agent.py`: pasar `usage_hints` desde el registry al construir el system prompt

---

## Resultado esperado

Con `database_query` y `knowledge_search` desactivadas en `BotIAv2_Recurso`,
el system prompt de un usuario que solo tiene `calculate`, `datetime`, `save_memory`,
`reload_permissions` y `read_attachment` **no contendrá ninguna mención** a
`database_query` ni `knowledge_search`.

El LLM no podrá intentar usar tools que no conoce.
