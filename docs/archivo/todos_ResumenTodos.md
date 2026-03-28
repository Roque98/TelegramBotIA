# 📋 Resumen de TODOs - Bot Telegram GPT5

> **Última actualización:** 2025-11-01
> **Estado general:** 🟡 Refactoring arquitectónico completado - Pendientes críticos de seguridad

---

## 📊 Resumen Ejecutivo

| Categoría | Pendientes | En Progreso | Completados | Total |
|-----------|------------|-------------|-------------|-------|
| 🔴 Críticos | 2 | 0 | 0 | 2 |
| 🟠 Altos | 1 | 0 | 3 | 4 |
| 🟡 Medios | 4 | 0 | 0 | 4 |
| 🟢 Bajos | 4 | 0 | 0 | 4 |
| **TOTAL** | **11** | **0** | **3** | **14** |

**Estimación total de esfuerzo:** 6-10 sprints (3-5 meses)
**Progreso actual:** Sprint 3-5 completado (refactoring arquitectónico ✅)

---

## 🔴 CRÍTICOS - Bloquean producción

### 1. Sistema de Autenticación/Autorización
- **Estado:** ❌ No iniciado
- **Prioridad:** 🔴🔴🔴 CRÍTICO
- **Esfuerzo:** 1-2 sprints
- **Impacto:** Seguridad - Bot sin control de acceso
- **Archivos afectados:**
  - `src/bot/telegram_bot.py`
  - `src/database/connection.py`
- **Tareas:**
  - [ ] Crear módulo `src/auth/user_manager.py`
  - [ ] Crear módulo `src/auth/permission_checker.py`
  - [ ] Crear módulo `src/auth/registration.py`
  - [ ] Implementar middleware de autenticación
  - [ ] Integrar con stored procedures existentes:
    - [ ] `sp_VerificarPermisoOperacion`
    - [ ] `sp_ObtenerOperacionesUsuario`
    - [ ] `sp_RegistrarLogOperacion`
  - [ ] Crear flujo de registro de usuarios Telegram
  - [ ] Validar permisos antes de procesar queries
- **Referencia:** `docs/todos/DetalleCompleto.md` - Sección 5.1.A

---

### 2. Modelos SQLAlchemy para Sistema de Permisos
- **Estado:** ❌ No iniciado
- **Prioridad:** 🔴🔴🔴 CRÍTICO
- **Esfuerzo:** 1 sprint
- **Impacto:** Funcionalidad - Sistema de permisos no utilizado
- **Archivos afectados:**
  - `src/database/models.py` ❌ NO EXISTE
  - `src/database/queries.py` ❌ NO EXISTE
- **Tareas:**
  - [ ] Crear `src/database/models.py` con 14 modelos:
    - [ ] Usuario, UsuarioTelegram
    - [ ] Roles, RolesIA, UsuariosRolesIA
    - [ ] Gerencias, GerenciaUsuarios, AreaAtendedora, GerenciasRolesIA
    - [ ] Modulos, Operaciones, RolesOperaciones, UsuariosOperaciones
    - [ ] LogOperaciones
  - [ ] Definir relaciones entre modelos (ForeignKey)
  - [ ] Crear `src/database/queries.py` con repositorio pattern
  - [ ] Crear funciones helper para queries complejas
  - [ ] Escribir tests unitarios para modelos
- **Referencia:** `docs/todos/DetalleCompleto.md` - Sección 5.1.B
- **SQL Schema:** `docs/sql/00 ResumenEstructura.sql`

---

## 🟠 ALTOS - Mejora sustancial de arquitectura

### 3. Refactorizar LLMAgent (Separación de Responsabilidades) ✅
- **Estado:** ✅ COMPLETADO
- **Prioridad:** 🟠🟠 ALTO
- **Esfuerzo:** 1-2 sprints
- **Impacto:** Mantenibilidad, Testabilidad, Extensibilidad
- **Archivo afectado:** `src/agent/llm_agent.py` (refactorizado de 234 a 197 líneas)
- **Tareas:**
  - [x] Crear estructura de módulos:
    - [x] `src/agent/providers/base_provider.py` (interfaz abstracta)
    - [x] `src/agent/providers/openai_provider.py`
    - [x] `src/agent/providers/anthropic_provider.py`
    - [x] `src/agent/classifiers/query_classifier.py`
    - [x] `src/agent/sql/sql_generator.py`
    - [x] `src/agent/sql/sql_validator.py`
    - [x] `src/agent/formatters/response_formatter.py`
  - [x] Aplicar Strategy Pattern para LLM providers
  - [x] Aplicar Adapter Pattern para diferentes APIs
  - [x] Refactorizar `llm_agent.py` como orquestador
  - [x] Implementar inyección de dependencias
  - [ ] Escribir tests unitarios por componente (pendiente TODO #14)
- **Referencia:** `docs/todos/DetalleCompleto.md` - Sección 5.2.C
- **Logros:**
  - ✅ Separación completa de responsabilidades
  - ✅ Código más mantenible y testeable
  - ✅ Fácil agregar nuevos proveedores LLM
  - ✅ Validación de SQL mejorada con regex y blacklist
  - ✅ Formateo de respuestas modular

---

### 4. Implementar Arquitectura de Handlers Modular ✅
- **Estado:** ✅ COMPLETADO
- **Prioridad:** 🟠🟠 ALTO
- **Esfuerzo:** 1 sprint
- **Impacto:** Escalabilidad, Separación de concerns
- **Archivo afectado:** `src/bot/telegram_bot.py` (refactorizado de 92 a 99 líneas)
- **Tareas:**
  - [x] Crear estructura de handlers:
    - [x] `src/bot/handlers/command_handlers.py` (/start, /help, /stats, /cancel)
    - [x] `src/bot/handlers/query_handlers.py` (consultas naturales con clase QueryHandler)
    - [ ] `src/bot/handlers/admin_handlers.py` (pendiente - requiere TODO #1)
    - [ ] `src/bot/handlers/registration_handlers.py` (pendiente - requiere TODO #1)
  - [x] Crear keyboards:
    - [x] `src/bot/keyboards/main_keyboard.py` (keyboard principal y ejemplos)
    - [x] `src/bot/keyboards/inline_keyboards.py` (paginación, confirmación, menú)
    - [ ] `src/bot/keyboards/admin_keyboard.py` (pendiente - requiere TODO #1)
  - [x] Crear middleware:
    - [x] `src/bot/middleware/logging_middleware.py` (LoggingMiddleware + PerformanceMiddleware)
    - [ ] `src/bot/middleware/auth_middleware.py` (pendiente - requiere TODO #1)
    - [ ] `src/bot/middleware/rate_limiting_middleware.py` (pendiente - TODO futuro)
  - [x] Refactorizar `telegram_bot.py` como solo routing
- **Referencia:** `docs/todos/DetalleCompleto.md` - Sección 5.2.D
- **Logros:**
  - ✅ Separación completa de responsabilidades en el bot
  - ✅ Handlers modulares y testeable por separado
  - ✅ Keyboards reutilizables (reply e inline)
  - ✅ Middleware de logging y performance
  - ✅ telegram_bot.py ahora solo hace routing (99 líneas vs 92 original)
  - ✅ Soporte para mensajes largos con paginación automática
  - ✅ Mejores mensajes de ayuda con markdown

---

### 5. Sistema de Logging Estructurado con Loguru
- **Estado:** ❌ No iniciado
- **Prioridad:** 🟠🟠 ALTO
- **Esfuerzo:** 0.5 sprint
- **Impacto:** Observabilidad, Debugging, Auditoría
- **Archivos afectados:**
  - `main.py:14-19` (logging básico)
  - `src/utils/logger.py` ❌ NO EXISTE
- **Tareas:**
  - [ ] Crear `src/utils/logger.py` con configuración Loguru
  - [ ] Configurar rotación de logs (100 MB, 30 días)
  - [ ] Configurar compresión de logs antiguos
  - [ ] Añadir niveles de log por entorno (dev/prod)
  - [ ] Implementar logging estructurado con contexto
  - [ ] Integrar con tabla `LogOperaciones` de BD
  - [ ] Configurar logging de requests/responses del LLM
  - [ ] Añadir correlation IDs para tracing
- **Referencia:** `docs/todos/DetalleCompleto.md` - Sección 5.2.E

---

### 6. Sistema de Prompts Modular y Versionado ✅
- **Estado:** ✅ COMPLETADO
- **Prioridad:** 🟠 ALTO
- **Esfuerzo:** 0.5 sprint
- **Impacto:** Mantenibilidad, A/B Testing
- **Archivos afectados:**
  - `src/agent/llm_agent.py` (refactorizado de 197 a 190 líneas)
  - `src/agent/classifiers/query_classifier.py` (refactorizado para usar PromptManager)
  - `src/agent/sql/sql_generator.py` (refactorizado para usar PromptManager)
- **Tareas:**
  - [x] Crear `src/agent/prompts/prompt_templates.py` (336 líneas)
  - [x] Crear `src/agent/prompts/prompt_manager.py` (341 líneas)
  - [x] Migrar prompts hardcoded a plantillas Jinja2
  - [x] Implementar versionado de prompts (v1, v2, v3)
  - [x] Añadir sistema de variables en prompts con Jinja2
  - [x] Crear repositorio de prompts reutilizables
  - [x] Implementar A/B testing de prompts (3 estrategias)
  - [x] Documentar mejores prácticas de prompts
  - [x] Crear config_example.py para diferentes entornos
  - [x] Agregar jinja2>=3.1.0 a dependencias
- **Referencia:** `docs/todos/DetalleCompleto.md` - Sección 4.5
- **Logros:**
  - ✅ 8 versiones de prompts implementadas (classification v1-v2, sql_generation v1-v3, general_response v1-v2)
  - ✅ Sistema de A/B testing con 3 estrategias (weighted, random, round_robin)
  - ✅ Tracking automático de métricas por versión
  - ✅ Configuración por entorno (dev/staging/prod/testing)
  - ✅ Documentación completa con ejemplos prácticos
  - ✅ Templates con variables y condicionales Jinja2
  - ✅ Singleton pattern para gestión centralizada

---

## 🟡 MEDIOS - Optimización y mejora de UX

### 7. Implementar Caching Inteligente
- **Estado:** ❌ No iniciado
- **Prioridad:** 🟡 MEDIO
- **Esfuerzo:** 0.5 sprint
- **Impacto:** Performance, Reducción de costos API
- **Archivos afectados:**
  - `src/database/connection.py:42-68` (get_schema sin cache)
  - `src/agent/llm_agent.py:32-74` (clasificación sin cache)
- **Tareas:**
  - [ ] Implementar cache de esquema de BD (TTL: 1 hora)
  - [ ] Implementar cache de clasificaciones de queries
  - [ ] Implementar cache de resultados frecuentes
  - [ ] Evaluar Redis vs cache en memoria
  - [ ] Configurar TTL por tipo de cache
  - [ ] Implementar invalidación de cache
  - [ ] Añadir métricas de hit/miss ratio
- **Referencia:** `docs/todos/DetalleCompleto.md` - Sección 5.3.F

---

### 8. Mejorar Formateo de Respuestas con Features de Telegram
- **Estado:** ❌ No iniciado
- **Prioridad:** 🟡 MEDIO
- **Esfuerzo:** 1 sprint
- **Impacto:** UX, Usabilidad
- **Archivos afectados:**
  - `src/agent/llm_agent.py:203-233` (formateo primitivo)
- **Tareas:**
  - [ ] Implementar formateo con Markdown/HTML
  - [ ] Crear inline keyboards para paginación
  - [ ] Añadir botones para acciones rápidas
  - [ ] Implementar tablas formateadas con Unicode
  - [ ] Crear paginación inteligente (> 10 resultados)
  - [ ] Implementar gráficos básicos con matplotlib
  - [ ] Añadir ASCII charts para agregaciones
  - [ ] Optimizar para pantallas móviles
- **Referencia:** `docs/todos/DetalleCompleto.md` - Sección 5.3.G

---

### 9. Implementar Retry Logic con Tenacity
- **Estado:** ❌ No iniciado
- **Prioridad:** 🟡 MEDIO
- **Esfuerzo:** 0.3 sprint
- **Impacto:** Resiliencia, Manejo de errores
- **Archivos afectados:**
  - `src/agent/llm_agent.py` (llamadas LLM sin retry)
  - `src/database/connection.py` (queries sin retry)
- **Tareas:**
  - [ ] Añadir decorador `@retry` a llamadas LLM
  - [ ] Configurar estrategia exponential backoff
  - [ ] Configurar max_attempts por tipo de operación
  - [ ] Implementar retry para errores de BD transitorios
  - [ ] Diferenciar errores retriables vs no retriables
  - [ ] Añadir logging de reintentos
  - [ ] Configurar timeouts por operación
- **Referencia:** `docs/todos/DetalleCompleto.md` - Sección 5.3.H
- **Dependencia:** `tenacity==9.0.0` ✅ Ya instalada

---

### 10. Mejorar Manejo de Errores
- **Estado:** ❌ No iniciado
- **Prioridad:** 🟡 MEDIO
- **Esfuerzo:** 0.5 sprint
- **Impacto:** UX, Debugging
- **Archivos afectados:**
  - `src/bot/telegram_bot.py:75-86` (catch genérico)
  - `src/agent/llm_agent.py:150-152` (error handling básico)
- **Tareas:**
  - [ ] Crear jerarquía de excepciones personalizadas
  - [ ] Diferenciar errores de usuario vs sistema
  - [ ] Implementar mensajes de error específicos
  - [ ] Añadir sugerencias de corrección en errores
  - [ ] Implementar error tracking (Sentry/similar)
  - [ ] Añadir contexto a logs de error
  - [ ] Crear respuestas de error user-friendly
- **Referencia:** `docs/todos/DetalleCompleto.md` - Sección 4.4

---

## 🟢 BAJOS - Features avanzadas y optimizaciones

### 11. Migrar a Async Database (Opcional)
- **Estado:** ❌ No iniciado
- **Prioridad:** 🟢 BAJO
- **Esfuerzo:** 1 sprint
- **Impacto:** Performance en alta concurrencia
- **Archivos afectados:**
  - `src/database/connection.py` (usa `asyncio.to_thread()`)
- **Tareas:**
  - [ ] Evaluar drivers async por BD:
    - [ ] `asyncpg` para PostgreSQL
    - [ ] `aiomysql` para MySQL
    - [ ] Evaluar `asyncio-odbc` para SQL Server
  - [ ] Migrar a `create_async_engine`
  - [ ] Migrar a `AsyncSession`
  - [ ] Refactorizar queries a async
  - [ ] Actualizar tests
  - [ ] Benchmark performance async vs sync
- **Referencia:** `docs/todos/DetalleCompleto.md` - Sección 5.4.I
- **Nota:** SQL Server puede mantenerse sync (aceptable)

---

### 12. Schema Analyzer Inteligente
- **Estado:** ❌ No iniciado
- **Prioridad:** 🟢 BAJO
- **Esfuerzo:** 1 sprint
- **Impacto:** Calidad de SQL generado por LLM
- **Archivos afectados:**
  - `src/database/schema_analyzer.py` ❌ NO EXISTE
  - `src/database/connection.py:42-68` (esquema básico)
- **Tareas:**
  - [ ] Crear `src/database/schema_analyzer.py`
  - [ ] Detectar relaciones (foreign keys)
  - [ ] Identificar índices y primary keys
  - [ ] Incluir ejemplos de datos (LIMIT 3)
  - [ ] Detectar tipos de datos complejos
  - [ ] Generar descripción enriquecida de esquema
  - [ ] Optimizar tamaño de descripción para LLM
  - [ ] Cachear análisis de esquema
- **Referencia:** `docs/todos/DetalleCompleto.md` - Sección 5.4.J

---

### 13. Métricas y Monitoreo
- **Estado:** ❌ No iniciado
- **Prioridad:** 🟢 BAJO
- **Esfuerzo:** 1-2 sprints
- **Impacto:** Observabilidad, Optimización
- **Archivos afectados:** Todos
- **Tareas:**
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
- **Referencia:** `docs/todos/DetalleCompleto.md` - Sección 5.4.K

---

### 14. Suite de Tests Completa
- **Estado:** ❌ Fixtures sin tests reales
- **Prioridad:** 🟢 BAJO (pero importante)
- **Esfuerzo:** 2 sprints
- **Impacto:** Calidad de código, Confianza en deploys
- **Archivos afectados:**
  - `tests/test_agent.py` (solo fixtures)
  - `tests/test_bot.py` ❌ NO EXISTE
  - `tests/test_database.py` ❌ NO EXISTE
- **Tareas:**
  - [ ] Tests unitarios:
    - [ ] `test_agent.py` - LLMAgent, clasificación, SQL generation
    - [ ] `test_database.py` - DatabaseManager, queries
    - [ ] `test_bot.py` - Handlers, comandos
    - [ ] `test_auth.py` - Autenticación, permisos
  - [ ] Tests de integración:
    - [ ] Flujo completo: mensaje → SQL → respuesta
    - [ ] Integración con BD de prueba
    - [ ] Integración con mock LLM
  - [ ] Tests end-to-end:
    - [ ] Bot simulado con pytest-telegram
  - [ ] Configurar coverage report (objetivo >80%)
  - [ ] Configurar CI/CD con tests automáticos
- **Referencia:** `docs/todos/DetalleCompleto.md` - Sección 5.4.L

---

## 🔧 Tareas de Refactoring Técnico

### Problemas de Diseño Arquitectónico

#### A. Abstracción de Proveedores LLM
- **Estado:** ❌ Código con if/elif hardcoded
- **Archivo:** `src/agent/llm_agent.py:52-74, 92-111, 183-197`
- **Solución:** Implementar Adapter Pattern
- **Incluido en:** TODO #3 (Refactorizar LLMAgent)

#### B. Inyección de Dependencias
- **Estado:** ❌ Instancias hardcoded
- **Archivo:** `src/agent/llm_agent.py:16-19`
- **Solución:** Constructor con DI
- **Incluido en:** TODO #3 (Refactorizar LLMAgent)

#### C. Separación Infraestructura/Dominio
- **Estado:** ❌ Lógica de negocio mezclada
- **Solución:** Aplicar Clean Architecture / Hexagonal
- **Esfuerzo:** 3-4 sprints (refactoring mayor)
- **Referencia:** `docs/todos/DetalleCompleto.md` - Sección 6.3

---

## 🔒 Riesgos de Seguridad

### SEC-1: Inyección SQL Indirecta
- **Severidad:** 🟡 MEDIA
- **Estado:** ❌ Mitigación parcial
- **Ubicación:** `src/database/connection.py:84-86`
- **Problema:** Solo verifica `startswith("SELECT")`
- **Mitigaciones adicionales necesarias:**
  - [ ] Parsear SQL con `sqlparse` para validar AST
  - [ ] Blacklist de keywords: DROP, DELETE, UPDATE, ALTER, TRUNCATE
  - [ ] Ejecutar queries en transacción read-only
  - [ ] Limitar tiempo de ejecución de queries
- **Referencia:** `docs/todos/DetalleCompleto.md` - Sección 7.1

### SEC-2: Exposición de Esquema Completo
- **Severidad:** 🟡 MEDIA
- **Estado:** ❌ Sin filtrado
- **Ubicación:** `src/database/connection.py:42-68`
- **Problema:** Expone TODAS las tablas y columnas al LLM
- **Mitigaciones necesarias:**
  - [ ] Filtrar tablas sensibles (sesiones, logs internos)
  - [ ] Ocultar columnas sensibles (passwords, tokens)
  - [ ] Implementar whitelist de tablas consultables
- **Referencia:** `docs/todos/DetalleCompleto.md` - Sección 7.2

### SEC-3: Ausencia de Rate Limiting
- **Severidad:** 🟡 MEDIA
- **Estado:** ❌ No implementado
- **Ubicación:** `src/bot/telegram_bot.py`
- **Problema:** Spam de queries → costos elevados
- **Mitigaciones necesarias:**
  - [ ] Rate limiting por usuario (ej: 10 queries/minuto)
  - [ ] Rate limiting global
  - [ ] Usar built-in rate limiting de python-telegram-bot
  - [ ] Alertas por uso anómalo
- **Referencia:** `docs/todos/DetalleCompleto.md` - Sección 7.3

---

## 📈 Roadmap de Implementación

### Sprint 1-2: Seguridad y Funcionalidad Básica 🔴
- [ ] TODO #1: Sistema de Autenticación/Autorización
- [ ] TODO #2: Modelos SQLAlchemy
- [ ] TODO #5: Logging Estructurado
- [ ] SEC-1, SEC-2, SEC-3: Mitigaciones de seguridad

### Sprint 3-5: Refactoring Arquitectónico 🟠
- [x] TODO #3: Refactorizar LLMAgent ✅
- [x] TODO #4: Arquitectura de Handlers Modular ✅
- [x] TODO #6: Sistema de Prompts Modular ✅

### Sprint 6-7: Optimización y Testing 🟡
- [ ] TODO #7: Caching Inteligente
- [ ] TODO #8: Mejorar Formateo de Respuestas
- [ ] TODO #9: Retry Logic
- [ ] TODO #10: Mejorar Manejo de Errores
- [ ] TODO #14: Suite de Tests Completa

### Sprint 8-10: Features Avanzadas 🟢
- [ ] TODO #12: Schema Analyzer Inteligente
- [ ] TODO #13: Métricas y Monitoreo
- [ ] TODO #11: Migrar a Async Database (opcional)

---

## 📝 Notas

### Archivos Planificados pero NO Implementados
```
❌ src/database/models.py
❌ src/database/queries.py
❌ src/database/schema_analyzer.py
❌ src/utils/logger.py
❌ src/utils/validators.py
❌ tests/test_bot.py
❌ tests/test_database.py
❌ tests/test_prompts.py
```

### Archivos Implementados Recientemente
```
✅ src/bot/handlers/command_handlers.py (TODO #4)
✅ src/bot/handlers/query_handlers.py (TODO #4)
✅ src/bot/keyboards/main_keyboard.py (TODO #4)
✅ src/bot/keyboards/inline_keyboards.py (TODO #4)
✅ src/bot/middleware/logging_middleware.py (TODO #4)
✅ src/agent/providers/base_provider.py (TODO #3)
✅ src/agent/providers/openai_provider.py (TODO #3)
✅ src/agent/providers/anthropic_provider.py (TODO #3)
✅ src/agent/classifiers/query_classifier.py (TODO #3)
✅ src/agent/sql/sql_generator.py (TODO #3)
✅ src/agent/sql/sql_validator.py (TODO #3)
✅ src/agent/formatters/response_formatter.py (TODO #3)
✅ src/agent/prompts/prompt_templates.py (TODO #6)
✅ src/agent/prompts/prompt_manager.py (TODO #6)
✅ src/agent/prompts/config_example.py (TODO #6)
✅ docs/prompts/BEST_PRACTICES.md (TODO #6)
```

### Dependencias Instaladas y su Estado
```
✅ jinja2>=3.1.0 - EN USO (sistema de prompts, TODO #6)
⚠️ loguru==0.7.3 - Instalado, no usado (se usa logging estándar, pendiente TODO #5)
⚠️ tenacity==9.0.0 - Instalado, no usado (pendiente TODO #9)
⚠️ langchain==0.3.7 - Instalado, no usado
⚠️ langchain-community==0.3.7 - Instalado, no usado
```

### Métricas de Calidad Actual
| Métrica | Actual | Objetivo | Progreso |
|---------|--------|----------|----------|
| Cobertura de tests | ~0% | >80% | 🔴 |
| Archivos planificados | 65% | 100% | 🟡 |
| Deuda técnica | Media-Baja | Baja | 🟢 |
| Sistema de permisos | 0% integrado | 100% | 🔴 |
| Refactoring arquitectónico | 75% | 100% | 🟢 |

---

## 🔗 Referencias

- **Análisis Detallado:** `docs/todos/DetalleCompleto.md`
- **Arquitectura Planificada:** `docs/estructura.md`
- **TODOs Original:** `docs/todos.md`
- **Schema SQL:** `docs/sql/00 ResumenEstructura.sql`
- **Código Principal:**
  - `main.py` - Entry point
  - `src/bot/telegram_bot.py` - Bot principal
  - `src/agent/llm_agent.py` - Agente LLM
  - `src/database/connection.py` - Gestor BD
  - `src/config/settings.py` - Configuración

---

**Generado:** 2025-10-29
**Proyecto:** GPT5 - Bot Telegram con Agente LLM
**Versión:** 1.0
