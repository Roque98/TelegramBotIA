# 🗺️ Roadmap del Proyecto - Bot Telegram IA

> **Última actualización:** 2025-11-26
> **Versión actual:** v0.1.0-base
> **Estado general:** 🟢 Base funcional - Refactoring completado

---

## 📊 Resumen Ejecutivo

| Categoría | Completados | Pendientes | Total | Progreso |
|-----------|-------------|------------|-------|----------|
| 🔴 Críticos | 0 | 2 | 2 | 0% |
| 🟠 Altos | 3 | 1 | 4 | 75% |
| 🟡 Medios | 0 | 4 | 4 | 0% |
| 🟢 Bajos | 0 | 4 | 4 | 0% |
| **TOTAL** | **3** | **11** | **14** | **21%** |

**Progreso del proyecto:** Sprint 3-5 completado (Refactoring Arquitectónico)
**Siguiente fase:** Sprint 1-2 (Seguridad y Funcionalidad Básica)

---

## ✅ Completado (Sprint 3-5)

### 1. Refactorizar LLMAgent - Separación de Responsabilidades ✅
- **Prioridad:** 🟠 ALTO
- **Estado:** ✅ COMPLETADO
- **Impacto:** Mantenibilidad, Testabilidad, Extensibilidad

**Archivos creados:**
```
✅ src/agent/providers/base_provider.py
✅ src/agent/providers/openai_provider.py
✅ src/agent/providers/anthropic_provider.py
✅ src/agent/classifiers/query_classifier.py
✅ src/agent/sql/sql_generator.py
✅ src/agent/sql/sql_validator.py
✅ src/agent/formatters/response_formatter.py
```

**Logros:**
- ✅ Aplicación de Strategy Pattern para LLM providers
- ✅ Aplicación de Adapter Pattern para diferentes APIs
- ✅ LLMAgent refactorizado como orquestador (234 → 197 líneas)
- ✅ Inyección de dependencias implementada
- ✅ Validación de SQL mejorada con regex y blacklist
- ✅ Formateo de respuestas modular

---

### 2. Arquitectura de Handlers Modular ✅
- **Prioridad:** 🟠 ALTO
- **Estado:** ✅ COMPLETADO
- **Impacto:** Escalabilidad, Separación de concerns

**Archivos creados:**
```
✅ src/bot/handlers/command_handlers.py
✅ src/bot/handlers/query_handlers.py
✅ src/bot/keyboards/main_keyboard.py
✅ src/bot/keyboards/inline_keyboards.py
✅ src/bot/middleware/logging_middleware.py
```

**Logros:**
- ✅ Handlers modulares y testeables por separado
- ✅ Keyboards reutilizables (reply e inline)
- ✅ Middleware de logging y performance
- ✅ telegram_bot.py ahora solo hace routing (92 → 99 líneas)
- ✅ Soporte para mensajes largos con paginación automática
- ✅ Mejores mensajes de ayuda con markdown

---

### 3. Sistema de Prompts Modular y Versionado ✅
- **Prioridad:** 🟠 ALTO
- **Estado:** ✅ COMPLETADO
- **Impacto:** Mantenibilidad, A/B Testing

**Archivos creados:**
```
✅ src/agent/prompts/prompt_templates.py (336 líneas)
✅ src/agent/prompts/prompt_manager.py (341 líneas)
✅ src/agent/prompts/config_example.py
✅ src/agent/prompts/README.md
✅ docs/prompts/BEST_PRACTICES.md
```

**Logros:**
- ✅ 8 versiones de prompts implementadas
- ✅ Sistema de A/B testing con 3 estrategias (weighted, random, round_robin)
- ✅ Tracking automático de métricas por versión
- ✅ Configuración por entorno (dev/staging/prod/testing)
- ✅ Templates con variables y condicionales Jinja2
- ✅ Singleton pattern para gestión centralizada
- ✅ Documentación completa con ejemplos prácticos

---

### 4. Configuración y Variables de Entorno ✅
- **Estado:** ✅ COMPLETADO
- **Logros:**
- ✅ Carga correcta del archivo .env del proyecto
- ✅ Prioridad al .env local sobre variables de sistema
- ✅ Configuración con pydantic-settings y dotenv

---

### 5. GitFlow y Control de Versiones ✅
- **Estado:** ✅ COMPLETADO
- **Logros:**
- ✅ Rama master con commit inicial
- ✅ Rama develop creada
- ✅ Tag v0.1.0-base para versión template
- ✅ Documentación completa de GitFlow
- ✅ Guías de commits con Conventional Commits

---

## 🔴 CRÍTICOS - Pendientes (Bloquean producción)

### TODO #1: Sistema de Autenticación/Autorización
- **Prioridad:** 🔴🔴🔴 CRÍTICO
- **Esfuerzo:** 1-2 sprints
- **Impacto:** Seguridad - Bot sin control de acceso

**Problema:** Cualquier usuario puede usar el bot y consultar la base de datos sin restricciones.

**Archivos a crear:**
```
❌ src/auth/user_manager.py
❌ src/auth/permission_checker.py
❌ src/auth/registration.py
❌ src/bot/middleware/auth_middleware.py
❌ src/bot/handlers/registration_handlers.py
❌ src/bot/handlers/admin_handlers.py
❌ src/bot/keyboards/admin_keyboard.py
```

**Tareas:**
- [ ] Crear módulo de gestión de usuarios Telegram
- [ ] Implementar verificación de permisos
- [ ] Crear flujo de registro de usuarios
- [ ] Integrar con stored procedures existentes:
  - [ ] sp_VerificarPermisoOperacion
  - [ ] sp_ObtenerOperacionesUsuario
  - [ ] sp_RegistrarLogOperacion
- [ ] Validar permisos antes de procesar queries
- [ ] Crear handlers para administración

**Referencia:** Sistema de permisos ya diseñado en `docs/sql/00 ResumenEstructura.sql`

---

### TODO #2: Modelos SQLAlchemy para Sistema de Permisos
- **Prioridad:** 🔴🔴🔴 CRÍTICO
- **Esfuerzo:** 1 sprint
- **Impacto:** Funcionalidad - Sistema de permisos no utilizado

**Problema:** El sistema de permisos existe en BD pero no está integrado con el código Python.

**Archivos a crear:**
```
❌ src/database/models.py
❌ src/database/queries.py
```

**Tareas:**
- [ ] Crear modelos SQLAlchemy para 14 tablas:
  - [ ] Usuario, UsuarioTelegram
  - [ ] Roles, RolesIA, UsuariosRolesIA
  - [ ] Gerencias, GerenciaUsuarios, AreaAtendedora, GerenciasRolesIA
  - [ ] Modulos, Operaciones, RolesOperaciones, UsuariosOperaciones
  - [ ] LogOperaciones
- [ ] Definir relaciones entre modelos (ForeignKey)
- [ ] Crear repositorio pattern en queries.py
- [ ] Crear funciones helper para queries complejas
- [ ] Escribir tests unitarios para modelos

**Referencia:** `docs/sql/00 ResumenEstructura.sql`

---

## 🟠 ALTOS - Pendientes

### TODO #5: Sistema de Logging Estructurado con Loguru
- **Prioridad:** 🟠🟠 ALTO
- **Esfuerzo:** 0.5 sprint
- **Impacto:** Observabilidad, Debugging, Auditoría

**Problema:** Logging básico, no se usa Loguru que ya está instalado.

**Archivos a crear:**
```
❌ src/utils/logger.py
```

**Tareas:**
- [ ] Crear configuración Loguru centralizada
- [ ] Configurar rotación de logs (100 MB, 30 días)
- [ ] Configurar compresión de logs antiguos
- [ ] Añadir niveles de log por entorno (dev/prod)
- [ ] Implementar logging estructurado con contexto
- [ ] Integrar con tabla LogOperaciones de BD
- [ ] Configurar logging de requests/responses del LLM
- [ ] Añadir correlation IDs para tracing

---

## 🟡 MEDIOS - Pendientes

### TODO #7: Implementar Caching Inteligente
- **Prioridad:** 🟡 MEDIO
- **Esfuerzo:** 0.5 sprint
- **Impacto:** Performance, Reducción de costos API

**Tareas:**
- [ ] Implementar cache de esquema de BD (TTL: 1 hora)
- [ ] Implementar cache de clasificaciones de queries
- [ ] Implementar cache de resultados frecuentes
- [ ] Evaluar Redis vs cache en memoria
- [ ] Configurar TTL por tipo de cache
- [ ] Implementar invalidación de cache
- [ ] Añadir métricas de hit/miss ratio

---

### TODO #8: Mejorar Formateo de Respuestas con Features de Telegram
- **Prioridad:** 🟡 MEDIO
- **Esfuerzo:** 1 sprint
- **Impacto:** UX, Usabilidad

**Tareas:**
- [ ] Implementar formateo con Markdown/HTML avanzado
- [ ] Crear inline keyboards para paginación mejorada
- [ ] Añadir botones para acciones rápidas
- [ ] Implementar tablas formateadas con Unicode
- [ ] Crear paginación inteligente (> 10 resultados)
- [ ] Implementar gráficos básicos con matplotlib
- [ ] Añadir ASCII charts para agregaciones
- [ ] Optimizar para pantallas móviles

---

### TODO #9: Implementar Retry Logic con Tenacity
- **Prioridad:** 🟡 MEDIO
- **Esfuerzo:** 0.3 sprint
- **Impacto:** Resiliencia, Manejo de errores

**Nota:** Tenacity ya está instalado (tenacity==9.0.0)

**Tareas:**
- [ ] Añadir decorador @retry a llamadas LLM
- [ ] Configurar estrategia exponential backoff
- [ ] Configurar max_attempts por tipo de operación
- [ ] Implementar retry para errores de BD transitorios
- [ ] Diferenciar errores retriables vs no retriables
- [ ] Añadir logging de reintentos
- [ ] Configurar timeouts por operación

---

### TODO #10: Mejorar Manejo de Errores
- **Prioridad:** 🟡 MEDIO
- **Esfuerzo:** 0.5 sprint
- **Impacto:** UX, Debugging

**Tareas:**
- [ ] Crear jerarquía de excepciones personalizadas
- [ ] Diferenciar errores de usuario vs sistema
- [ ] Implementar mensajes de error específicos
- [ ] Añadir sugerencias de corrección en errores
- [ ] Implementar error tracking (Sentry/similar)
- [ ] Añadir contexto a logs de error
- [ ] Crear respuestas de error user-friendly

---

## 🟢 BAJOS - Pendientes

### TODO #11: Migrar a Async Database (Opcional)
- **Prioridad:** 🟢 BAJO
- **Esfuerzo:** 1 sprint
- **Impacto:** Performance en alta concurrencia

**Tareas:**
- [ ] Evaluar drivers async por BD:
  - [ ] asyncpg para PostgreSQL
  - [ ] aiomysql para MySQL
  - [ ] Evaluar asyncio-odbc para SQL Server
- [ ] Migrar a create_async_engine
- [ ] Migrar a AsyncSession
- [ ] Refactorizar queries a async
- [ ] Actualizar tests
- [ ] Benchmark performance async vs sync

**Nota:** SQL Server puede mantenerse sync (aceptable)

---

### TODO #12: Schema Analyzer Inteligente
- **Prioridad:** 🟢 BAJO
- **Esfuerzo:** 1 sprint
- **Impacto:** Calidad de SQL generado por LLM

**Archivos a crear:**
```
❌ src/database/schema_analyzer.py
```

**Tareas:**
- [ ] Detectar relaciones (foreign keys)
- [ ] Identificar índices y primary keys
- [ ] Incluir ejemplos de datos (LIMIT 3)
- [ ] Detectar tipos de datos complejos
- [ ] Generar descripción enriquecida de esquema
- [ ] Optimizar tamaño de descripción para LLM
- [ ] Cachear análisis de esquema

---

### TODO #13: Métricas y Monitoreo
- **Prioridad:** 🟢 BAJO
- **Esfuerzo:** 1-2 sprints
- **Impacto:** Observabilidad, Optimización

**Tareas:**
- [ ] Instrumentar con Prometheus/OpenTelemetry
- [ ] Métricas a implementar:
  - [ ] Tiempo de respuesta por query
  - [ ] Tasa de errores
  - [ ] Uso de API LLM (tokens, costo)
  - [ ] Queries más frecuentes
  - [ ] Hit/miss ratio de cache
  - [ ] Conexiones activas a BD
- [ ] Configurar Grafana dashboard
- [ ] Configurar alertas (tasa errores, latencia)
- [ ] Implementar health checks
- [ ] Crear endpoint /metrics

---

### TODO #14: Suite de Tests Completa
- **Prioridad:** 🟢 BAJO (pero importante)
- **Esfuerzo:** 2 sprints
- **Impacto:** Calidad de código, Confianza en deploys

**Estado actual:** Solo fixtures en test_agent.py

**Archivos a crear:**
```
❌ tests/test_bot.py
❌ tests/test_database.py
❌ tests/test_auth.py
❌ tests/test_prompts.py
```

**Tareas:**
- [ ] Tests unitarios:
  - [ ] test_agent.py - LLMAgent, clasificación, SQL generation
  - [ ] test_database.py - DatabaseManager, queries
  - [ ] test_bot.py - Handlers, comandos
  - [ ] test_auth.py - Autenticación, permisos
  - [ ] test_prompts.py - Sistema de prompts
- [ ] Tests de integración:
  - [ ] Flujo completo: mensaje → SQL → respuesta
  - [ ] Integración con BD de prueba
  - [ ] Integración con mock LLM
- [ ] Tests end-to-end:
  - [ ] Bot simulado con pytest-telegram
- [ ] Configurar coverage report (objetivo >80%)
- [ ] Configurar CI/CD con tests automáticos

---

## 🔒 Riesgos de Seguridad Pendientes

### SEC-1: Inyección SQL Indirecta
- **Severidad:** 🟡 MEDIA
- **Estado:** ❌ Mitigación parcial

**Problema:** Solo se valida que el SQL empiece con "SELECT"

**Mitigaciones necesarias:**
- [ ] Parsear SQL con sqlparse para validar AST
- [ ] Blacklist de keywords: DROP, DELETE, UPDATE, ALTER, TRUNCATE
- [ ] Ejecutar queries en transacción read-only
- [ ] Limitar tiempo de ejecución de queries

---

### SEC-2: Exposición de Esquema Completo
- **Severidad:** 🟡 MEDIA
- **Estado:** ❌ Sin filtrado

**Problema:** Se exponen TODAS las tablas y columnas al LLM

**Mitigaciones necesarias:**
- [ ] Filtrar tablas sensibles (sesiones, logs internos)
- [ ] Ocultar columnas sensibles (passwords, tokens)
- [ ] Implementar whitelist de tablas consultables

---

### SEC-3: Ausencia de Rate Limiting
- **Severidad:** 🟡 MEDIA
- **Estado:** ❌ No implementado

**Problema:** Spam de queries → costos elevados

**Mitigaciones necesarias:**
- [ ] Rate limiting por usuario (ej: 10 queries/minuto)
- [ ] Rate limiting global
- [ ] Usar built-in rate limiting de python-telegram-bot
- [ ] Alertas por uso anómalo

---

## 📈 Plan de Implementación Sugerido

### Sprint 1-2: Seguridad y Funcionalidad Básica 🔴
**Duración:** 2-4 semanas

1. [ ] TODO #1: Sistema de Autenticación/Autorización
2. [ ] TODO #2: Modelos SQLAlchemy
3. [ ] TODO #5: Logging Estructurado
4. [ ] SEC-1, SEC-2, SEC-3: Mitigaciones de seguridad

**Entregable:** Bot con autenticación funcional y sistema de permisos integrado

---

### Sprint 3-5: Refactoring Arquitectónico 🟠
**Duración:** 3-6 semanas
**Estado:** ✅ COMPLETADO

1. [x] TODO #3: Refactorizar LLMAgent ✅
2. [x] TODO #4: Arquitectura de Handlers Modular ✅
3. [x] TODO #6: Sistema de Prompts Modular ✅

**Entregable:** Arquitectura modular y extensible

---

### Sprint 6-7: Optimización y Testing 🟡
**Duración:** 2-4 semanas

1. [ ] TODO #7: Caching Inteligente
2. [ ] TODO #8: Mejorar Formateo de Respuestas
3. [ ] TODO #9: Retry Logic
4. [ ] TODO #10: Mejorar Manejo de Errores
5. [ ] TODO #14: Suite de Tests Completa

**Entregable:** Sistema robusto, optimizado y bien testeado

---

### Sprint 8-10: Features Avanzadas 🟢
**Duración:** 3-6 semanas

1. [ ] TODO #12: Schema Analyzer Inteligente
2. [ ] TODO #13: Métricas y Monitoreo
3. [ ] TODO #11: Migrar a Async Database (opcional)

**Entregable:** Sistema production-ready con observabilidad completa

---

## 📝 Archivos Implementados vs Planificados

### ✅ Archivos Implementados (Nuevos en v0.1.0-base)

```
✅ src/agent/providers/base_provider.py
✅ src/agent/providers/openai_provider.py
✅ src/agent/providers/anthropic_provider.py
✅ src/agent/classifiers/query_classifier.py
✅ src/agent/sql/sql_generator.py
✅ src/agent/sql/sql_validator.py
✅ src/agent/formatters/response_formatter.py
✅ src/agent/prompts/prompt_templates.py
✅ src/agent/prompts/prompt_manager.py
✅ src/agent/prompts/config_example.py
✅ src/agent/prompts/README.md
✅ src/bot/handlers/command_handlers.py
✅ src/bot/handlers/query_handlers.py
✅ src/bot/keyboards/main_keyboard.py
✅ src/bot/keyboards/inline_keyboards.py
✅ src/bot/middleware/logging_middleware.py
✅ docs/prompts/BEST_PRACTICES.md
✅ COMMIT_GUIDELINES.md
✅ GITFLOW.md
```

### ❌ Archivos Pendientes

```
❌ src/auth/user_manager.py
❌ src/auth/permission_checker.py
❌ src/auth/registration.py
❌ src/database/models.py
❌ src/database/queries.py
❌ src/database/schema_analyzer.py
❌ src/utils/logger.py
❌ src/utils/validators.py
❌ src/bot/middleware/auth_middleware.py
❌ src/bot/middleware/rate_limiting_middleware.py
❌ src/bot/handlers/registration_handlers.py
❌ src/bot/handlers/admin_handlers.py
❌ src/bot/keyboards/admin_keyboard.py
❌ tests/test_bot.py
❌ tests/test_database.py
❌ tests/test_auth.py
❌ tests/test_prompts.py
```

---

## 📊 Métricas del Proyecto

| Métrica | Actual | Objetivo | Estado |
|---------|--------|----------|--------|
| Cobertura de tests | ~0% | >80% | 🔴 |
| Archivos planificados | 65% | 100% | 🟡 |
| Deuda técnica | Media-Baja | Baja | 🟢 |
| Sistema de permisos | 0% integrado | 100% | 🔴 |
| Refactoring arquitectónico | 75% | 100% | 🟢 |
| Documentación | 80% | 100% | 🟢 |

---

## 🔗 Referencias

- **Documentación Técnica:**
  - [COMMIT_GUIDELINES.md](COMMIT_GUIDELINES.md) - Guía de commits
  - [GITFLOW.md](GITFLOW.md) - Estrategia de branches
  - [docs/estructura.md](docs/estructura.md) - Arquitectura del proyecto
  - [docs/todos/ResumenTodos.md](docs/todos/ResumenTodos.md) - TODOs detallados
  - [docs/todos/DetalleCompleto.md](docs/todos/DetalleCompleto.md) - Análisis completo

- **SQL Schema:**
  - [docs/sql/00 ResumenEstructura.sql](docs/sql/00 ResumenEstructura.sql)
  - [docs/sql/01 EstructuraUsuarios.sql](docs/sql/01 EstructuraUsuarios.sql)
  - [docs/sql/02 EstructuraPermisos.sql](docs/sql/02 EstructuraPermisos.sql)

- **Código Principal:**
  - `main.py` - Entry point
  - `src/bot/telegram_bot.py` - Bot principal
  - `src/agent/llm_agent.py` - Agente LLM
  - `src/database/connection.py` - Gestor BD
  - `src/config/settings.py` - Configuración

---

**Versión del Roadmap:** 2.0
**Fecha:** 2025-11-26
**Tag de referencia:** v0.1.0-base
