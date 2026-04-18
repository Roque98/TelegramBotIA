[Docs](../index.md) › [Código](README.md) › Cómo extender el sistema

# Cómo extender el sistema

Recetas concretas para los casos de extensión más comunes.

---

## Receta 1: Nueva tool

### Paso 1 — Crear la clase

```python
# src/agents/tools/mi_tool.py
from src.agents.tools.base import BaseTool, ToolDefinition, ToolCategory, ToolParameter, ToolResult

class MiTool(BaseTool):

    def __init__(self, servicio_externo=None):
        self.servicio = servicio_externo

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="mi_tool",                                    # nombre que usa el LLM
            description="Descripción clara de qué hace",       # aparece en el prompt
            category=ToolCategory.UTILITY,
            parameters=[
                ToolParameter(
                    name="param1",
                    type="string",
                    description="Descripción del parámetro",
                    required=True,
                )
            ],
            usage_hint="Para [caso de uso concreto]: usa `mi_tool`",
            # usage_hint aparece en instrucciones de uso si el usuario tiene permiso
        )

    async def execute(
        self,
        param1: str,
        user_id: str = None,
        context=None,
        **kwargs,
    ) -> ToolResult:
        try:
            resultado = await self.servicio.hacer_algo(param1)
            return ToolResult(
                success=True,
                data={"resultado": str(resultado)},
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))
```

### Paso 2 — Registrar en la factory

Agregar una entrada en `_build_tool_catalog()` dentro de [`src/pipeline/factory.py`](../../src/pipeline/factory.py).
El valor debe ser un **lambda** que retorne la instancia (o `None` si falta alguna
dependencia — la factory omite silenciosamente las tools que retornan `None`):

```python
# src/pipeline/factory.py → _build_tool_catalog()
from src.agents.tools.mi_tool import MiTool

return {
    # ... tools existentes ...
    "mi_tool": lambda: MiTool(servicio_externo=mi_servicio) if mi_servicio else None,
}
```

La clave debe coincidir exactamente con el sufijo del campo `recurso` en `BotIAv2_Recurso`
(formato `tool:<clave>`). La factory instancia solo las tools cuya clave aparece en BD
con `activo=1`.

Si la tool necesita acceso a otra base de datos, usar `db_registry.get("alias")` en
lugar de `db_manager`:

```python
"mi_tool": lambda: MiTool(
    db=db_registry.get("mi_alias")
) if (db_registry is not None and db_registry.is_configured("mi_alias")) else None,
```

### Paso 3 — Registrar el recurso en BD

```sql
INSERT INTO abcmasplus..BotIAv2_Recurso (recurso, tipoRecurso, descripcion, esPublico)
VALUES ('tool:mi_tool', 'tool', 'Descripción de la tool', 0);
```

### Paso 4 — Agregar permisos

```sql
-- Permitir para todos los usuarios autenticados con rol Gerente (idRol=2)
DECLARE @idRecurso INT = (SELECT idRecurso FROM BotIAv2_Recurso WHERE recurso = 'tool:mi_tool');
DECLARE @idAuth INT = (SELECT idTipoEntidad FROM BotIAv2_TipoEntidad WHERE nombre = 'autenticado');

INSERT INTO BotIAv2_Permisos (idTipoEntidad, idEntidad, idRecurso, idRolRequerido, permitido)
VALUES (@idAuth, 0, @idRecurso, 2, 1);
```

### Paso 5 — Verificar

```bash
python scripts/test_message.py "probá mi nueva tool"
```

---

## Receta 2: Nuevo comando Telegram

### Paso 1 — Agregar el handler

```python
# src/bot/handlers/command_handlers.py

async def mi_comando(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para /micomando."""
    user = context.user_data.get("telegram_user")
    if not user:
        await update.message.reply_text("Necesitás registrarte primero. Usá /register.")
        return

    # lógica del comando
    await update.message.reply_text("Respuesta del comando")
```

### Paso 2 — Registrar en TelegramBot

```python
# src/bot/telegram_bot.py → setup()
application.add_handler(
    CommandHandler("micomando", mi_comando)
)
```

### Paso 3 — Agregar a AuthMiddleware si requiere auth

```python
# src/bot/middleware/auth_middleware.py
COMANDOS_PUBLICOS = {"/start", "/help", "/register", "/verify", "/resend", "/micomando"}
# Si NO está en la lista, el middleware exige que el usuario esté registrado
```

### Paso 4 — Registrar recurso en BD (si es un comando controlado por permisos)

```sql
INSERT INTO BotIAv2_Recurso (recurso, tipoRecurso, descripcion, esPublico)
VALUES ('cmd:/micomando', 'cmd', 'Descripción del comando', 0);
```

---

## Receta 3: Nuevo subdominio

Cuando necesitás agregar un área de negocio nueva (ej: módulo de inventario propio).

### Estructura mínima

```
src/domain/inventario/
├── __init__.py
├── inventario_entity.py         ← Entidades Pydantic
├── inventario_repository.py     ← Acceso a BD (solo DB, sin lógica)
└── inventario_service.py        ← Lógica de negocio
```

### inventario_entity.py

```python
from pydantic import BaseModel

class ProductoInventario(BaseModel):
    id: int
    nombre: str
    stock: int
    precio: float
```

### inventario_repository.py

```python
class InventarioRepository:
    def __init__(self, db_manager):
        self.db = db_manager

    def get_stock(self, producto_id: int) -> Optional[ProductoInventario]:
        rows = self.db.execute_query(
            "SELECT id, nombre, stock, precio FROM Inventario WHERE id = :id",
            {"id": producto_id},
        )
        return ProductoInventario(**rows[0]) if rows else None
```

### inventario_service.py

```python
class InventarioService:
    def __init__(self, repository: InventarioRepository):
        self.repo = repository

    def get_stock(self, producto_id: int) -> Optional[ProductoInventario]:
        return self.repo.get_stock(producto_id)
```

### Inyectar en la factory

```python
# src/pipeline/factory.py → create_main_handler()
from src.domain.inventario.inventario_service import InventarioService
from src.domain.inventario.inventario_repository import InventarioRepository

inventario_service = InventarioService(InventarioRepository(db))
```

Si el subdominio necesita una tool asociada, seguir también la Receta 1.

---

## Receta 4: Nuevo agente especializado

El sistema de orquestación dinámica (ARQ-35) carga los agentes desde BD al arrancar.
Agregar un nuevo agente no requiere tocar código Python — solo BD y un reload.

### Paso 1 — Insertar en `BotIAv2_AgenteDef`

```sql
INSERT INTO abcmasplus..BotIAv2_AgenteDef
    (nombre, descripcion, systemPrompt, temperatura, maxIteraciones, esGeneralista, activo)
VALUES (
    'mi_agente',
    'Descripción usada por IntentClassifier para rutear — ser específico y diferenciador',
    N'Eres Amber, una asistente especializada en [dominio].

## Tu Personalidad
...

## Herramientas Disponibles
{tools_description}

- **finish**: Termina con tu respuesta final
  - Parameters: {"answer": "Tu respuesta al usuario"}

## Instrucciones
1. **Para saludos**: Usa "finish" directamente
{usage_hints}

## Formato de Respuesta
SIEMPRE responde con este JSON:
```json
{
  "thought": "Tu razonamiento",
  "action": "nombre_accion",
  "action_input": {},
  "final_answer": null
}
```',
    0.1,   -- temperatura
    10,    -- maxIteraciones
    0,     -- esGeneralista: 0 = especialista (respeta tool_scope)
    1      -- activo
);
```

Campos clave:
- `nombre`: identificador único; el `IntentClassifier` lo retorna como nombre de ruta.
- `descripcion`: texto corto que el clasificador usa para decidir el ruteo. Ser específico sobre el dominio.
- `systemPrompt`: debe contener `{tools_description}` y `{usage_hints}` (requerido).
- `esGeneralista`: `0` para especialistas (usa `tool_scope`), `1` para el agente de fallback (no filtrar tools).
- `modeloOverride`: dejar `NULL` para usar `openai_loop_model` del sistema, o especificar un modelo diferente.

### Paso 2 — Asignar tools en `BotIAv2_AgenteTools`

```sql
INSERT INTO abcmasplus..BotIAv2_AgenteTools (idAgente, nombreTool)
SELECT idAgente, tool
FROM abcmasplus..BotIAv2_AgenteDef
CROSS JOIN (VALUES ('database_query'), ('calculate'), ('datetime')) AS t(tool)
WHERE nombre = 'mi_agente';
```

Las `nombreTool` deben coincidir con las claves del catálogo en `_build_tool_catalog()`.
El `AgentBuilder` construye el `tool_scope` a partir de esta lista e intersecciona con
los permisos del usuario en cada request.

### Paso 3 — Recargar sin reiniciar el bot

El agente administrador puede enviar el comando al bot:

```
/ia reload_agent_config
```

O ejecutar la tool `reload_agent_config` vía mensaje natural (requiere rol Admin).
Esto llama a `AgentConfigService.invalidate_cache()` + `AgentBuilder.clear_instance_cache()`,
forzando que la próxima consulta lea la nueva configuración desde BD.

### Paso 4 — Verificar el ruteo

Enviar una consulta del dominio del nuevo agente y revisar los logs:

```
Orchestrator: 'consulta de prueba' → 'mi_agente' (classify=45ms, confidence=0.95, fallback=False)
```

Si `fallback=True`, el `IntentClassifier` no reconoció el agente — revisar que la
`descripcion` en BD sea lo suficientemente específica y diferenciada de los otros agentes.

---

## Checklist de extensión

Antes de hacer merge de cualquier extensión:

- [ ] La nueva tool o handler está cubierta por al menos un test en `tests/`
- [ ] El recurso existe en `BotIAv2_Recurso` con `esPublico` correctamente configurado
- [ ] La factory inyecta la nueva dependencia
- [ ] Se actualizó `.claude/context/` con los archivos correspondientes (TOOLS.md, HANDLERS.md, etc.)
- [ ] Commit con tipo correcto: `feat(tools)`, `feat(bot)`, etc.

---

**← Anterior** [Base de datos](base-de-datos.md) · [Índice](README.md)
