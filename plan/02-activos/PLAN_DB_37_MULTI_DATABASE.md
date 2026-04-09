# PLAN_DB_37 — Multi-Database Connection Manager

**ID**: DB-37
**Tipo**: Infraestructura / Base de datos
**Rama**: `feature/db-37-multi-database`
**Estado**: En progreso
**Creado**: 2026-04-09

---

## Contexto

El sistema conecta a una sola BD hardcodeada. Se quiere que `database_tool`
pueda ejecutar queries en distintas bases de datos SQL Server, configurables
desde `.env`, sin cambiar comportamiento actual (backward-compat total).

## Diseño

```
.env
  DB_CONNECTIONS=core,ventas       ← alias activos
  DB_CORE_HOST=...                 ← vars por alias (las actuales pasan a ser "core")
  DB_VENTAS_HOST=...               ← nueva conexión

DatabaseRegistry                   ← instancia lazy un DatabaseManager por alias
  └── get("core")  → DatabaseManager
  └── get("ventas") → DatabaseManager

DatabaseTool(registry)
  action_input: {description: "...", db: "ventas"}   ← parámetro opcional
  default: "core"
```

---

## Fases

### Fase 1 — Settings: soporte para N conexiones
- [x] Crear `DbConnectionConfig` (Pydantic BaseModel) con campos de una conexión
- [x] `Settings.get_db_connections()` → `dict[str, DbConnectionConfig]`
- [x] Backward-compat: vars `DB_HOST/PORT/NAME/...` mapean a alias "core"
- [x] Actualizar `.env.example`

### Fase 2 — DatabaseRegistry
- [x] Crear `src/infra/database/registry.py` con `DatabaseRegistry`
- [x] `DatabaseManager.__init__` acepta `DbConnectionConfig` opcional
- [x] Lazy init: manager se crea al primer `get(alias)`
- [x] `close_all()` para shutdown

### Fase 3 — DatabaseTool: parámetro `db`
- [x] Recibe `DatabaseRegistry` en lugar de `db_manager` directo
- [x] Agregar parámetro `db` opcional (default: "core")
- [x] `usage_hint` muestra las conexiones disponibles dinámicamente
- [x] Validar alias antes de ejecutar

### Fase 4 — Factory y bot
- [x] `factory.py`: construir `DatabaseRegistry`, pasarlo a `DatabaseTool`
- [x] `telegram_bot.py`: `registry.close_all()` en shutdown

### Fase 5 — Docs
- [x] Actualizar `.env.example`
- [x] Actualizar `docs/uso/configuracion.md`

---

## Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `src/config/settings.py` | `DbConnectionConfig` + `get_db_connections()` |
| `src/infra/database/registry.py` | Nuevo — `DatabaseRegistry` |
| `src/infra/database/connection.py` | `__init__` acepta config opcional |
| `src/infra/database/__init__.py` | Exportar `DatabaseRegistry` |
| `src/agents/tools/database_tool.py` | Parámetro `db`, recibe registry |
| `src/pipeline/factory.py` | Construir y pasar `DatabaseRegistry` |
| `src/bot/telegram_bot.py` | `registry.close_all()` en shutdown |
| `.env.example` | Nuevo formato multi-DB |
| `docs/uso/configuracion.md` | Documentar conexiones múltiples |
