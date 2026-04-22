# Plan: Tool — template_search_by_name

> **Estado**: ⚪ No iniciado
> **Última actualización**: 2026-04-21
> **Rama Git**: feature/tool-template-search

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: Repositorio | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 2: Tool Python | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 3: Registro en factory | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 4: Migración SQL | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 5: Prompt del agente | ░░░░░░░░░░ 0% | ⏳ Pendiente |

**Progreso Total**: ░░░░░░░░░░ 0% (0/13 tareas)

---

## Descripción

Agregar la tool `template_search_by_name` que permite al agente encontrar templates
buscando por nombre parcial de aplicación. Consulta en paralelo banco (`Template_GetByNombre`)
y EKT (`Template_GetByNombre_ekt`), etiquetando cada resultado con su origen (`instancia`).

Esto habilita flujos como:
> *"¿Cuál es la matriz de escalamiento de ppServicios?"*
1. Agente llama `template_search_by_name(nombre="ppServicios")` → recibe `id=15037, instancia="BAZ"`
2. Agente llama `get_escalation_matrix(template_id=15037, usar_ekt=False)`

---

## Fase 1: Repositorio

**Objetivo**: Agregar `get_templates_by_nombre()` al `AlertRepository`.
**Archivo**: `src/domain/alerts/alert_repository.py`
**Dependencias**: Ninguna

### Contexto
- SPs: `EXEC ABCMASplus.dbo.Template_GetByNombre @nombre = :nombre` (banco)
  y `EXEC ABCMASplus.dbo.Template_GetByNombre_ekt @nombre = :nombre` (EKT).
- Columnas retornadas: `id`, `idAplicacion`, `Aplicacion`, `GerenciaAtendedora`,
  `GerenciaDesarrollo`, `ambiente`, `Negocio`, `TipoTemplate`, `Pais`, `ArquitecturaPersonalizada`.
- A diferencia de `get_template_by_id` (fallback), aquí se consultan **ambas en paralelo** porque
  el mismo nombre puede existir en banco Y en EKT y el usuario no sabe en cuál está.
- Cada resultado lleva `instancia = "BAZ"` o `"EKT"` para que el agente lo use en llamadas posteriores.
- La entidad `Template` ya tiene el campo `instancia: str` en `alert_entity.py`.

### Tareas

- [ ] **Agregar `get_templates_by_nombre(nombre: str) -> list[Template]`** en `AlertRepository`
  - Archivo: `src/domain/alerts/alert_repository.py`
  - Llamar ambos SPs con `asyncio.gather`, capturando excepciones individualmente
  - Rows BAZ → `Template.model_validate({**row, "instancia": "BAZ"})`
  - Rows EKT → `Template.model_validate({**row, "instancia": "EKT"})`
  - Si un SP falla → `logger.warning(...)` y lista vacía para esa instancia (no propagar)
  - Retornar lista combinada, ordenada por `aplicacion`

### Entregables
- [ ] Método implementado y correctamente tipado

---

## Fase 2: Tool Python

**Objetivo**: Crear `TemplateSearchByNameTool` siguiendo el patrón de `get_template_by_id_tool.py`.
**Archivo**: `src/agents/tools/template_search_by_name_tool.py`
**Dependencias**: Fase 1

### Parámetros

| Parámetro | Tipo | Req | Descripción |
|-----------|------|-----|-------------|
| `nombre` | string | ✅ | Nombre parcial de la aplicación (mín. 2 caracteres) |

### Retorno

```json
{
  "templates": [
    { "id": 15037, "aplicacion": "ppServicios", "instancia": "BAZ",
      "gerencia_atendedora": "...", "gerencia_desarrollo": "...",
      "ambiente": "PRD", "negocio": "...", "tipo_template": "..." }
  ],
  "total": 1,
  "mensaje": "Se encontraron 1 template(s) para 'ppServicios'."
}
```

### Instrucción clave en `description`
La descripción debe indicar al LLM que:
- Si hay **un único resultado** → usar su `id` e `instancia` directamente en la siguiente llamada
- Si hay **varios resultados** → mostrarlos al usuario para que elija
- `instancia = "EKT"` → pasar `usar_ekt=true` a `get_escalation_matrix` o `get_template_by_id`
- `instancia = "BAZ"` → pasar `usar_ekt=false`

### Tareas

- [ ] **Crear `TemplateSearchByNameTool`**
  - Archivo: `src/agents/tools/template_search_by_name_tool.py`
  - `is_read_only=True`, `is_destructive=False`, `is_concurrency_safe=True`
  - Constructor: `def __init__(self, repo: AlertRepository)`
  - `definition.name = "template_search_by_name"`
  - `definition.category = ToolCategory.MONITORING`
  - En `execute()`: validar `len(nombre.strip()) >= 2`
  - Llamar `await self._repo.get_templates_by_nombre(nombre)`
  - Serializar y retornar con `ToolResult.success_result()`

### Entregables
- [ ] Archivo creado, tipado correctamente, sin imports circulares

---

## Fase 3: Registro en factory

**Objetivo**: Registrar la tool en `tool_factory.py`.
**Archivo**: `src/bootstrap/tool_factory.py`
**Dependencias**: Fase 2

### Tareas

- [ ] **Agregar al catálogo en `_build_tool_catalog()`**
  - Importar `TemplateSearchByNameTool` junto a los otros imports de tools
  - Agregar entrada:
    ```python
    "template_search_by_name": lambda: TemplateSearchByNameTool(repo=r) if (r := _monitoreo_repo()) else None,
    ```
  - Colocarla junto a `get_template_by_id` para agrupar tools relacionadas

### Entregables
- [ ] Tool instanciable desde el factory sin errores

---

## Fase 4: Migración SQL

**Objetivo**: Crear el script `017_template_search_by_name_tool.sql` con todos los cambios de BD.
**Archivo**: `scripts/migrations/017_template_search_by_name_tool.sql`
**Dependencias**: Ninguna (puede ejecutarse en paralelo con Fases 1-3)

### Estructura del script (idempotente)

**Paso 1 — Registrar recurso** en `BotIAv2_Recurso`:
```sql
IF NOT EXISTS (SELECT 1 FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:template_search_by_name')
    INSERT INTO abcmasplus..BotIAv2_Recurso (recurso, tipoRecurso, esPublico, descripcion, activo)
    VALUES ('tool:template_search_by_name', 'tool', 0,
            'Busca templates por nombre de aplicación en banco y EKT. Retorna id e instancia para consultas posteriores.', 1);
```

**Paso 2 — Copiar permisos** desde `get_template_by_id` (mismo patrón que migración 013):
```sql
DECLARE @idRecursoNuevo INT = (SELECT idRecurso FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:template_search_by_name');
DECLARE @idTipoEntidad INT = (SELECT TOP 1 idTipoEntidad FROM abcmasplus..BotIAv2_Permisos
    WHERE idRecurso = (SELECT idRecurso FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:get_template_by_id'));

INSERT INTO abcmasplus..BotIAv2_Permisos (idTipoEntidad, idEntidad, idRecurso, idRolRequerido, permitido, activo)
SELECT @idTipoEntidad, 0, @idRecursoNuevo, p.idRolRequerido, 1, 1
FROM abcmasplus..BotIAv2_Permisos p
JOIN abcmasplus..BotIAv2_Recurso r ON p.idRecurso = r.idRecurso
WHERE r.recurso = 'tool:get_template_by_id'
  AND NOT EXISTS (
    SELECT 1 FROM abcmasplus..BotIAv2_Permisos
    WHERE idRecurso = @idRecursoNuevo AND idRolRequerido = p.idRolRequerido AND activo = 1
  );
```

**Paso 3 — Agregar tool al agente** en `BotIAv2_AgenteTools`:
```sql
DECLARE @idAgente INT = (SELECT idAgente FROM abcmasplus..BotIAv2_AgenteDef WHERE nombre = 'alertas');
IF @idAgente IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM abcmasplus..BotIAv2_AgenteTools
    WHERE idAgente = @idAgente AND nombreTool = 'template_search_by_name')
    INSERT INTO abcmasplus..BotIAv2_AgenteTools (idAgente, nombreTool, activo)
    VALUES (@idAgente, 'template_search_by_name', 1);
```

**Paso 4 — Verificación** final con SELECTs de confirmación.

### Tareas

- [ ] **Crear `scripts/migrations/017_template_search_by_name_tool.sql`** con los 4 pasos anteriores
  - Idempotente (usar IF NOT EXISTS en cada INSERT)
  - Incluir sección de verificación al final
  - Seguir el estilo de migración 013

### Entregables
- [ ] Script SQL creado, revisado y listo para ejecutar

---

## Fase 5: Prompt del agente

**Objetivo**: Actualizar el system prompt y la descripción del agente `alertas` para incorporar la nueva tool.
**Dependencias**: Fase 4 (la migración SQL es el canal de actualización del prompt)

### Cambios necesarios en el prompt

**Agregar en "Cuándo usar cada tool":**
```
- **template_search_by_name**: cuando el usuario menciona el nombre de una aplicación
  pero NO tiene el idTemplate. Ej: "la matriz de escalamiento de ppServicios",
  "¿quién atiende ppServicios?", "busca el template de <nombre>".
  Retorna una lista con id e instancia ("BAZ" o "EKT").
```

**Agregar en "Reglas":**
```
- Para preguntas de escalamiento por nombre de aplicación (no por IP):
  1. Llama template_search_by_name(nombre="<aplicación>")
  2. Si hay un único resultado → usa su id e instancia en get_escalation_matrix
     (instancia="EKT" → usar_ekt=true, instancia="BAZ" → usar_ekt=false)
  3. Si hay varios resultados → muéstralos al usuario y pide que elija
```

**Actualizar descripción del agente** para que el intent classifier la enrute:
```
Añadir: "buscar templates por nombre de aplicación, qué template corresponde a una app"
```

### Tareas

- [ ] **Agregar paso 5 al script `017_template_search_by_name_tool.sql`**: UPDATE del system prompt
  - Mantener todas las tools existentes
  - Añadir sección de `template_search_by_name` en "Cuándo usar cada tool"
  - Añadir regla de flujo nombre → id → escalamiento
  - Incrementar `version = version + 1`

- [ ] **Agregar paso 6**: UPDATE de `descripcion` del agente
  - Añadir "buscar templates por nombre de aplicación" a la descripción existente
  - Incrementar `version = version + 1`

- [ ] **Guardar snapshot en historial**:
  ```sql
  INSERT INTO abcmasplus..BotIAv2_AgentePromptHistorial
      (idAgente, systemPrompt, version, razonCambio, modificadoPor)
  SELECT idAgente, systemPrompt, version, 'Agrega tool template_search_by_name', 'migración 017'
  FROM abcmasplus..BotIAv2_AgenteDef WHERE nombre = 'alertas';
  ```

### Entregables
- [ ] Prompt actualizado con instrucciones para la nueva tool
- [ ] Snapshot guardado en historial antes de la actualización

---

## Tarea final: Commit y push

- [ ] `feat(tools): agregar tool template_search_by_name con soporte banco y EKT`
  - Incluye: `alert_repository.py`, `template_search_by_name_tool.py`, `tool_factory.py`, `017_template_search_by_name_tool.sql`

---

## Criterios de Éxito

- [ ] *"Dame la matriz de escalamiento de ppServicios"* → el agente llama `template_search_by_name` + `get_escalation_matrix` sin intervención manual
- [ ] Si el template existe en EKT → `usar_ekt=true` se pasa correctamente
- [ ] Si hay múltiples coincidencias → el agente presenta la lista al usuario
- [ ] Si no hay resultados en ninguna instancia → mensaje claro al usuario
- [ ] Script SQL es idempotente (se puede ejecutar más de una vez sin errores)

---

## Notas de Diseño

**¿Por qué paralelo y no fallback?**
`get_template_by_id` usa fallback porque el ID es único. Con búsqueda por nombre puede haber
aplicaciones homónimas en banco y en EKT; el usuario necesita ver todas para elegir.

**¿Por qué el prompt guía el flujo nombre→id?**
`get_escalation_matrix` recibe `template_id` (int). Sin `template_search_by_name`, el agente
no tiene forma de resolver el nombre a un ID y generaría alucinaciones o pediría el ID al usuario.

**Validación mínima de 2 caracteres:**
Evita `@nombre = 'a'` que devolvería cientos de filas sin utilidad.

---

## Historial de Cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-04-21 | Creación del plan (fases 1-3) | Claude |
| 2026-04-21 | Agregar fases 4-5: migración SQL, permisos y prompt | Claude |
