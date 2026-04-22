# Plan: Tool — template_search_by_name

> **Estado**: ⚪ No iniciado
> **Última actualización**: 2026-04-21
> **Rama Git**: feature/tool-template-search

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: Repositorio | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 2: Tool | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 3: Registro y BD | ░░░░░░░░░░ 0% | ⏳ Pendiente |

**Progreso Total**: ░░░░░░░░░░ 0% (0/8 tareas)

---

## Descripción

Agregar la tool `template_search_by_name` que permite al agente encontrar templates
buscando por nombre parcial de aplicación. Consulta en paralelo banco (`Template_GetByNombre`)
y EKT (`Template_GetByNombre_ekt`), etiquetando cada resultado con su origen (`instancia`).

Esto permite que el agente responda preguntas como:
> *"¿Cuál es la matriz de escalamiento de ppServicios?"*

El flujo esperado:
1. Agente llama `template_search_by_name(nombre="ppServicios")`
2. Tool retorna lista con `id`, `aplicacion`, `instancia` (BAZ o EKT)
3. Agente llama `get_escalation_matrix(template_id=X, usar_ekt=<según instancia>)`

---

## Fase 1: Repositorio

**Objetivo**: Agregar `get_templates_by_nombre()` al `AlertRepository`.
**Archivo**: `src/domain/alerts/alert_repository.py`
**Dependencias**: Ninguna

### Contexto de implementación

- Los SPs existentes son: `Template_GetByNombre @nombre` (BAZ) y `Template_GetByNombre_ekt @nombre` (EKT).
- Columnas que retornan ambos SPs: `id`, `idAplicacion`, `Aplicacion`, `GerenciaAtendedora`,
  `GerenciaDesarrollo`, `ambiente`, `Negocio`, `TipoTemplate`, `Pais`, `ArquitecturaPersonalizada`.
- A diferencia de `get_template_by_id` (fallback), aquí se consultan **ambas instancias en paralelo**
  y se retornan todos los resultados juntos, ya que el usuario puede no saber en cuál está el template.
- Cada resultado se marca con `instancia = "BAZ"` o `instancia = "EKT"` antes de retornar.

### Firma del método

```python
async def get_templates_by_nombre(self, nombre: str) -> list[Template]:
    """
    Busca templates cuyo nombre de aplicación coincida parcialmente.
    Consulta banco y EKT en paralelo y combina resultados etiquetados con instancia.
    """
```

### Tareas

- [ ] **Agregar método `get_templates_by_nombre()`** en `AlertRepository`
  - Archivo: `src/domain/alerts/alert_repository.py`
  - Llamar ambos SPs en paralelo con `asyncio.gather`
  - Usar `EXEC ABCMASplus.dbo.Template_GetByNombre @nombre = :nombre`
  - Usar `EXEC ABCMASplus.dbo.Template_GetByNombre_ekt @nombre = :nombre`
  - Para cada row BAZ → `Template.model_validate({**row, "instancia": "BAZ"})`
  - Para cada row EKT → `Template.model_validate({**row, "instancia": "EKT"})`
  - Si un SP falla → loggear warning y retornar lista vacía para esa instancia (no lanzar)
  - Retornar lista combinada ordenada por `aplicacion`

- [ ] **Verificar que `Template` entity ya tiene campo `instancia`**
  - Archivo: `src/domain/alerts/alert_entity.py`
  - Si no existe, agregarlo: `instancia: str = Field(default="")`

### Entregables
- [ ] Método `get_templates_by_nombre()` implementado y sin errores de tipo

---

## Fase 2: Tool

**Objetivo**: Crear `template_search_by_name_tool.py` siguiendo el patrón de `get_template_by_id_tool.py`.
**Archivo**: `src/agents/tools/template_search_by_name_tool.py`
**Dependencias**: Fase 1

### Parámetros de la tool

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `nombre` | string | ✅ | Nombre parcial de la aplicación a buscar |

### Retorno esperado

```json
{
  "templates": [
    {
      "id": 15037,
      "aplicacion": "ppServicios",
      "instancia": "BAZ",
      "gerencia_atendedora": "...",
      "gerencia_desarrollo": "...",
      "ambiente": "PRD",
      "negocio": "...",
      "tipo_template": "..."
    }
  ],
  "total": 1,
  "mensaje": "Se encontraron 1 templates para 'ppServicios'"
}
```

### Comportamiento del agente

La descripción de la tool debe instruir al agente que:
- Si encuentra un único resultado → puede proceder directamente a consultas posteriores
- Si encuentra varios → debe mostrarlos al usuario para que elija (con `id` e `instancia`)
- El campo `instancia` debe pasarse como `usar_ekt=True/False` en `get_template_by_id` o `get_escalation_matrix`

### Tareas

- [ ] **Crear `TemplateSearchByNameTool`** en `src/agents/tools/template_search_by_name_tool.py`
  - Hereda de `BaseTool`
  - Constructor: `def __init__(self, repo: AlertRepository)`
  - `definition.name = "template_search_by_name"`
  - `definition.category = ToolCategory.MONITORING`
  - Parámetro: `nombre` (string, required)
  - En `execute()`: validar que `nombre` tenga al menos 2 caracteres
  - Llamar `self._repo.get_templates_by_nombre(nombre)`
  - Retornar lista serializada con `ToolResult.success_result()`

### Entregables
- [ ] Archivo `template_search_by_name_tool.py` creado y tipado correctamente

---

## Fase 3: Registro y BD

**Objetivo**: Registrar la tool en el factory y habilitarla para el agente.
**Dependencias**: Fase 2

### Tareas

- [ ] **Registrar en `tool_factory.py`**
  - Archivo: `src/bootstrap/tool_factory.py`
  - Importar `TemplateSearchByNameTool`
  - Agregar al catálogo: `"template_search_by_name": lambda: TemplateSearchByNameTool(repo=_alert_repo())`
  - Usar el mismo `_alert_repo()` que ya usa `get_template_by_id`

- [ ] **Agregar tool al agente en BD**
  - Tabla: `BotIAv2_AgenteTools`
  - Identificar el agente que maneja consultas de monitoreo/alertas
  - Ejecutar:
    ```sql
    INSERT INTO abcmasplus..BotIAv2_AgenteTools (idAgente, nombreTool, activo)
    VALUES (<id_agente_monitoreo>, 'template_search_by_name', 1)
    ```

- [ ] **Commit y push**
  - Mensaje: `feat(tools): agregar tool template_search_by_name con soporte banco y EKT`

### Entregables
- [ ] Tool disponible en el registry del agente
- [ ] Cambios pusheados a `develop`

---

## Criterios de Éxito

- [ ] Al preguntar *"dame los templates de ppServicios"*, el agente llama la tool correctamente
- [ ] El agente usa el campo `instancia` para pasar `usar_ekt` correcto en consultas posteriores
- [ ] Si el template no existe en ninguna instancia, retorna mensaje claro

---

## Notas de Diseño

**¿Por qué paralelo y no fallback?**
Con `get_template_by_id` se usa fallback porque el ID es único entre instancias.
Con búsqueda por nombre, puede haber templates homónimos en banco Y en EKT; el usuario
necesita ver todos para elegir el correcto.

**Validación mínima de 2 caracteres:**
Evita llamadas con `@nombre = 'a'` que podrían retornar cientos de filas.

---

## Historial de Cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-04-21 | Creación del plan | Claude |
