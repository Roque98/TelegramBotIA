# PLAN: Refactorización - Patrón Repository + Service

> **Objetivo**: Estandarizar el proyecto con el patrón Repository + Service en todos los módulos
> **Rama**: `feature/refactor-repository-pattern`
> **Prioridad**: Media
> **Progreso**: 0% (0/29)

---

## Contexto

El proyecto ya tiene el patrón repository implementado parcialmente:
- `src/memory/` — tiene `repository.py` + `service.py` ✅
- `src/knowledge/` — tiene `knowledge_repository.py` + `knowledge_manager.py` ✅
- `src/auth/` — `user_manager.py` mezcla queries de BD con lógica de negocio ❌

Además, las entidades (dataclasses) están dispersas dentro de los mismos archivos de repository/manager.

**Meta final**: Estructura uniforme en todos los módulos, con sufijo que indica el rol del archivo:
```
src/<modulo>/
├── <modulo>_entity.py     # Dataclasses / modelos de BD
├── <modulo>_repository.py # Solo consultas a BD
└── <modulo>_service.py    # Lógica de negocio
```

---

## Estructura Objetivo

```
src/
├── auth/
│   ├── user_entity.py                 # TelegramUser, UserStats
│   ├── user_repository.py             # Queries: get, create, update
│   └── user_service.py                # Lógica: autenticación, permisos, registro
│
├── memory/
│   ├── memory_entity.py               # UserProfile, Interaction (mover desde repository.py)
│   ├── memory_repository.py           # Renombrar repository.py → memory_repository.py
│   └── memory_service.py              # Renombrar service.py → memory_service.py
│
├── knowledge/
│   ├── knowledge_entity.py            # KnowledgeEntry, KnowledgeCategory (mover desde company_knowledge.py)
│   ├── knowledge_repository.py        # (ya existe ✅)
│   └── knowledge_service.py           # Renombrar knowledge_manager.py → knowledge_service.py
│
├── utils/
│   └── encryption_util.py             # Mover y renombrar desde auth/encryption.py
│
└── bot/
    └── middleware/
        └── token_middleware.py        # Mover desde auth/token_middleware.py
```

### Archivos que se reubican o eliminan

| Archivo actual | Destino | Razón |
|----------------|---------|-------|
| `src/auth/registration.py` | Lógica absorbida por `user_service.py` | Es lógica de negocio, no es ni repo ni entidad |
| `src/auth/permission_checker.py` | Lógica absorbida por `user_service.py` | Es lógica de negocio, no es ni repo ni entidad |
| `src/auth/encryption.py` | `src/utils/encryption_util.py` | Es utilidad genérica — `src/utils/` ya existe con otras utilidades |
| `src/auth/token_middleware.py` | `src/bot/middleware/token_middleware.py` | Es middleware del bot, no de auth |
| `src/memory/repository.py` | `src/memory/memory_repository.py` | Añadir sufijo para consistencia |
| `src/memory/service.py` | `src/memory/memory_service.py` | Añadir sufijo para consistencia |
| `src/knowledge/company_knowledge.py` | Entidades absorbidas por `knowledge_entity.py` | Centralizar entidades con sufijo |
| `src/knowledge/knowledge_categories.py` | Enum absorbido por `knowledge_entity.py` | Centralizar todas las definiciones del módulo |
| `src/knowledge/knowledge_manager.py` | `src/knowledge/knowledge_service.py` | Renombrar a sufijo `_service` |

---

## Fases

### Fase 0 — Preparación (1 tarea)
- [ ] **0.1** Crear rama `feature/refactor-repository-pattern` desde `develop`

---

### Fase 1 — Módulo `auth/` (12 tareas)
> Es el módulo con mayor deuda técnica. `user_manager.py` hace todo y hay archivos huérfanos.

- [ ] **1.1** Crear `src/auth/user_entity.py`
  - Mover dataclasses: `TelegramUser`, `UserStats` desde `user_manager.py`
  - Mantener imports en `user_manager.py` temporalmente para no romper nada

- [ ] **1.2** Crear `src/auth/user_repository.py`
  - Extraer métodos de solo BD desde `user_manager.py`:
    - `get_user_by_chat_id()`
    - `get_user_by_id()`
    - `is_user_registered()`
    - `get_registration_info()`
    - `update_last_activity()`
    - `get_user_stats()`
    - `get_all_user_telegram_accounts()`

- [ ] **1.3** Crear `src/auth/user_service.py`
  - Absorber lógica de `user_manager.py`, `registration.py` y `permission_checker.py`
  - Usa `UserRepository` internamente
  - Métodos de alto nivel: autenticación, validaciones, permisos, registro

- [ ] **1.4** Mover `src/auth/encryption.py` → `src/utils/encryption_util.py`
  - Actualizar todos los imports que la usen

- [ ] **1.5** Mover `src/auth/token_middleware.py` → `src/bot/middleware/token_middleware.py`
  - La carpeta `src/bot/middleware/` ya existe
  - Actualizar todos los imports que lo usen

- [ ] **1.6** Eliminar `registration.py` (lógica absorbida por `user_service.py`)

- [ ] **1.7** Eliminar `permission_checker.py` (lógica absorbida por `user_service.py`)

- [ ] **1.8** Actualizar todos los archivos que importan desde `src.auth`
  - `src/bot/middleware/auth_middleware.py` — `UserManager` → `UserService`
  - `src/bot/handlers/command_handlers.py` — `UserManager` → `UserService`
  - `src/bot/handlers/query_handlers.py` — `PermissionChecker`, `UserManager` → `UserService`
  - `src/bot/handlers/registration_handlers.py` — `RegistrationManager`, `UserManager` → `UserService`
  - `src/api/chat_endpoint.py` — `TokenMiddleware` → nueva ruta en `src.bot.middleware`

- [ ] **1.9** Actualizar `src/auth/__init__.py`
  - Eliminar exports de `UserManager`, `PermissionChecker`, `RegistrationManager`
  - Exportar `UserService` desde `user_service.py`

- [ ] **1.10** Eliminar `user_manager.py`

- [ ] **1.11** Actualizar tests de `auth/` si existen

- [ ] **1.12** Smoke test: flujo de registro y autenticación funciona

---

### Fase 2 — Módulo `memory/` (6 tareas)
> Ya tiene la estructura correcta, solo limpiar entidades

- [ ] **2.1** Crear `src/memory/memory_entity.py`
  - Mover dataclasses: `UserProfile`, `Interaction` desde `repository.py`

- [ ] **2.2** Renombrar `repository.py` → `memory_repository.py`
  - Actualizar imports hacia `memory_entity.py`

- [ ] **2.3** Renombrar `service.py` → `memory_service.py`
  - Actualizar imports hacia `memory_repository.py` y `memory_entity.py`

- [ ] **2.4** Absorber `context_builder.py` dentro de `memory_service.py`
  - Mover lógica de construcción de contexto como métodos de `MemoryService`
  - Eliminar `context_builder.py`
  - Actualizar `src/gateway/factory.py` que importa `ContextBuilder` directamente

- [ ] **2.5** Actualizar `src/memory/__init__.py`
  - Eliminar exports de `ContextBuilder`, `MemoryRepository` (nombre viejo), `repository.py`
  - Exportar desde `memory_entity.py`, `memory_repository.py`, `memory_service.py`

- [ ] **2.6** Smoke test: memoria de usuario se guarda y recupera correctamente

---

### Fase 3 — Módulo `knowledge/` (6 tareas)
> Renombrar `knowledge_manager.py` y mover entidades

- [ ] **3.1** Crear `src/knowledge/knowledge_entity.py`
  - Mover dataclasses: `KnowledgeEntry`, `KnowledgeCategory` desde `company_knowledge.py`
  - Absorber enum `KnowledgeCategory` desde `knowledge_categories.py`
  - Eliminar `company_knowledge.py` y `knowledge_categories.py`

- [ ] **3.2** Actualizar `knowledge_repository.py` para importar desde `knowledge_entity.py`

- [ ] **3.3** Renombrar `knowledge_manager.py` → `knowledge_service.py`
  - Actualizar clase interna: `KnowledgeManager` → `KnowledgeService`

- [ ] **3.4** Actualizar todos los archivos que importan desde `src.knowledge`
  - `src/gateway/factory.py` — `KnowledgeManager` → `KnowledgeService`
  - `src/agents/tools/knowledge_tool.py` — `KnowledgeCategory` desde `knowledge_categories` → `knowledge_entity`

- [ ] **3.5** Actualizar `src/knowledge/__init__.py`
  - Eliminar exports de `KnowledgeManager`, `KnowledgeCategory` (vieja ruta), `KnowledgeEntry` (vieja ruta)
  - Exportar desde `knowledge_entity.py`, `knowledge_repository.py`, `knowledge_service.py`

- [ ] **3.6** Smoke test: búsqueda de knowledge base funciona correctamente

---

### Fase 4 — Limpieza Final (4 tareas)

- [ ] **4.1** Verificar que no queden queries SQL directas fuera de los repositories
  - Revisar `src/bot/handlers/` y cualquier otro módulo
  - Nota: `src/agents/tools/database_tool.py` queda excluido — sus queries son dinámicas generadas por la IA y requieren acceso directo a BD

- [ ] **4.2** Actualizar `plan/README.md` con este plan

- [ ] **4.3** Hacer merge a `develop`

- [ ] **4.4** Documentar la estructura final en este plan

---

## Resumen de Tareas

| Fase | Descripción | Tareas | Estado |
|------|-------------|--------|--------|
| 0 | Preparación | 1 | ⬜ Pendiente |
| 1 | Módulo auth/ | 12 | ⬜ Pendiente |
| 2 | Módulo memory/ | 6 | ⬜ Pendiente |
| 3 | Módulo knowledge/ | 6 | ⬜ Pendiente |
| 4 | Limpieza final | 4 | ⬜ Pendiente |
| **Total** | | **29** | **0%** |

---

## Reglas del Refactor

1. **No romper funcionalidad** — cada fase termina con un smoke test
2. **Commits atómicos** — un commit por sub-tarea importante
3. **Sin lógica en repositories** — solo queries a BD, sin validaciones de negocio
4. **Sin queries en services** — toda BD va por el repository
5. **Entidades son dataclasses** — no deben tener métodos de negocio ni BD

---

## Convención de Nombres

| Tipo | Nombre | Ejemplo |
|------|--------|---------|
| Entidad | `<Modelo>` | `TelegramUser`, `UserProfile` |
| Repository | `<Modulo>Repository` | `UserRepository`, `MemoryRepository` |
| Service | `<Modulo>Service` | `UserService`, `MemoryService` |
| Archivo entidad | `<modulo>_entity.py` | `user_entity.py` |
| Archivo repository | `<modulo>_repository.py` | `user_repository.py` |
| Archivo service | `<modulo>_service.py` | `user_service.py` |
