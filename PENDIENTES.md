# 📝 Lista de Pendientes del Proyecto

> **Actualizado:** 2025-11-26
> **Versión base:** v0.1.0-base
> **Progreso general:** 21% completado (3/14 TODOs)

---

## 🎯 Resumen por Prioridad

| Prioridad | Completados | Pendientes | Total |
|-----------|-------------|------------|-------|
| 🔴 Críticos | 0 | 2 | 2 |
| 🟠 Altos | 3 | 1 | 4 |
| 🟡 Medios | 0 | 4 | 4 |
| 🟢 Bajos | 0 | 4 | 4 |
| **TOTAL** | **3** | **11** | **14** |

---

## 🔴 CRÍTICOS (Bloquean Producción)

### 1. Sistema de Autenticación y Autorización
**Problema:** El bot acepta consultas de CUALQUIER usuario sin restricciones

**Archivos a crear:**
- [ ] `src/auth/user_manager.py` - Gestión de usuarios
- [ ] `src/auth/permission_checker.py` - Verificación de permisos
- [ ] `src/auth/registration.py` - Flujo de registro
- [ ] `src/bot/middleware/auth_middleware.py` - Middleware de autenticación
- [ ] `src/bot/handlers/registration_handlers.py` - Handlers de registro
- [ ] `src/bot/handlers/admin_handlers.py` - Handlers administrativos
- [ ] `src/bot/keyboards/admin_keyboard.py` - Teclados para admin

**Integraciones pendientes:**
- [ ] Conectar con stored procedures de BD (sp_VerificarPermisoOperacion, sp_ObtenerOperacionesUsuario)
- [ ] Validar permisos antes de procesar queries
- [ ] Registrar operaciones en LogOperaciones

**Estimación:** 1-2 sprints (2-4 semanas)

---

### 2. Modelos SQLAlchemy para Sistema de Permisos
**Problema:** El sistema de permisos existe en BD pero NO está integrado con Python

**Archivos a crear:**
- [ ] `src/database/models.py` - 14 modelos SQLAlchemy
  - Usuario, UsuarioTelegram
  - Roles, RolesIA, UsuariosRolesIA
  - Gerencias, GerenciaUsuarios, AreaAtendedora, GerenciasRolesIA
  - Modulos, Operaciones, RolesOperaciones, UsuariosOperaciones
  - LogOperaciones
- [ ] `src/database/queries.py` - Repositorio pattern

**Tareas:**
- [ ] Definir relaciones (ForeignKeys) entre modelos
- [ ] Crear funciones helper para queries complejas
- [ ] Escribir tests unitarios

**Estimación:** 1 sprint (1-2 semanas)

---

## 🟠 ALTOS

### 3. Sistema de Logging Estructurado
**Problema:** Se usa logging básico, Loguru está instalado pero no se usa

**Archivos a crear:**
- [ ] `src/utils/logger.py` - Configuración centralizada de Loguru

**Tareas:**
- [ ] Configurar rotación de logs (100 MB, 30 días)
- [ ] Configurar compresión automática
- [ ] Niveles de log por entorno (dev/prod)
- [ ] Logging estructurado con contexto
- [ ] Integrar con LogOperaciones de BD
- [ ] Logging de requests/responses LLM
- [ ] Correlation IDs para tracing

**Estimación:** 0.5 sprint (3-5 días)

---

## 🟡 MEDIOS

### 4. Caching Inteligente
**Impacto:** Reducir costos de API y mejorar performance

**Tareas:**
- [ ] Cache de esquema de BD (TTL: 1 hora)
- [ ] Cache de clasificaciones de queries
- [ ] Cache de resultados frecuentes
- [ ] Evaluar Redis vs cache en memoria
- [ ] Métricas de hit/miss ratio

**Estimación:** 0.5 sprint (3-5 días)

---

### 5. Mejorar Formateo de Respuestas
**Impacto:** Mejor experiencia de usuario

**Tareas:**
- [ ] Formateo avanzado con Markdown/HTML
- [ ] Inline keyboards mejorados para paginación
- [ ] Botones para acciones rápidas
- [ ] Tablas formateadas con Unicode
- [ ] Gráficos básicos con matplotlib
- [ ] ASCII charts para agregaciones

**Estimación:** 1 sprint (1-2 semanas)

---

### 6. Retry Logic con Tenacity
**Impacto:** Mayor resiliencia ante fallos

**Nota:** Tenacity ya está instalado

**Tareas:**
- [ ] Decorador @retry para llamadas LLM
- [ ] Exponential backoff
- [ ] Retry para errores de BD transitorios
- [ ] Diferenciar errores retriables vs no retriables
- [ ] Logging de reintentos

**Estimación:** 0.3 sprint (2-3 días)

---

### 7. Mejorar Manejo de Errores
**Impacto:** Mejor debugging y UX

**Tareas:**
- [ ] Jerarquía de excepciones personalizadas
- [ ] Diferenciar errores de usuario vs sistema
- [ ] Mensajes de error específicos
- [ ] Sugerencias de corrección
- [ ] Error tracking (Sentry)
- [ ] Respuestas user-friendly

**Estimación:** 0.5 sprint (3-5 días)

---

## 🟢 BAJOS

### 8. Schema Analyzer Inteligente
**Impacto:** Mejor calidad de SQL generado por LLM

**Archivos a crear:**
- [ ] `src/database/schema_analyzer.py`

**Tareas:**
- [ ] Detectar relaciones (foreign keys)
- [ ] Identificar índices y primary keys
- [ ] Incluir ejemplos de datos
- [ ] Descripción enriquecida de esquema
- [ ] Cachear análisis

**Estimación:** 1 sprint (1-2 semanas)

---

### 9. Métricas y Monitoreo
**Impacto:** Observabilidad completa del sistema

**Tareas:**
- [ ] Instrumentar con Prometheus/OpenTelemetry
- [ ] Métricas: tiempo de respuesta, tasa de errores, uso de API
- [ ] Dashboard en Grafana
- [ ] Alertas automáticas
- [ ] Health checks
- [ ] Endpoint /metrics

**Estimación:** 1-2 sprints (2-4 semanas)

---

### 10. Suite de Tests Completa
**Impacto:** Calidad de código y confianza en deploys

**Estado actual:** Solo fixtures, sin tests reales

**Archivos a crear:**
- [ ] `tests/test_bot.py`
- [ ] `tests/test_database.py`
- [ ] `tests/test_auth.py`
- [ ] `tests/test_prompts.py`

**Tareas:**
- [ ] Tests unitarios (LLMAgent, handlers, BD)
- [ ] Tests de integración (flujo completo)
- [ ] Tests end-to-end (bot simulado)
- [ ] Coverage >80%
- [ ] CI/CD con tests automáticos

**Estimación:** 2 sprints (2-4 semanas)

---

### 11. Migrar a Async Database (Opcional)
**Impacto:** Performance en alta concurrencia

**Tareas:**
- [ ] Evaluar drivers async (asyncpg, aiomysql)
- [ ] Migrar a create_async_engine
- [ ] Refactorizar queries a async
- [ ] Benchmark performance

**Nota:** SQL Server puede mantenerse sync

**Estimación:** 1 sprint (1-2 semanas)

---

## 🔒 Riesgos de Seguridad

### SEC-1: Inyección SQL Indirecta (🟡 Media)
**Mitigaciones pendientes:**
- [ ] Parsear SQL con sqlparse
- [ ] Blacklist de keywords (DROP, DELETE, UPDATE, ALTER)
- [ ] Transacciones read-only
- [ ] Timeouts de queries

---

### SEC-2: Exposición de Esquema Completo (🟡 Media)
**Mitigaciones pendientes:**
- [ ] Filtrar tablas sensibles
- [ ] Ocultar columnas sensibles (passwords, tokens)
- [ ] Whitelist de tablas consultables

---

### SEC-3: Rate Limiting (🟡 Media)
**Mitigaciones pendientes:**
- [ ] Rate limiting por usuario (10 queries/minuto)
- [ ] Rate limiting global
- [ ] Alertas por uso anómalo

---

## 📋 Orden de Implementación Recomendado

### Fase 1: Seguridad (Sprint 1-2) - 2-4 semanas
1. ✅ Sistema de Autenticación (#1)
2. ✅ Modelos SQLAlchemy (#2)
3. ✅ Logging Estructurado (#3)
4. ✅ Mitigaciones de seguridad (SEC-1, SEC-2, SEC-3)

**Bloqueo:** Estos TODOs son críticos y bloquean producción

---

### Fase 2: Optimización (Sprint 3-4) - 2-4 semanas
1. ✅ Caching Inteligente (#4)
2. ✅ Retry Logic (#6)
3. ✅ Manejo de Errores (#7)

**Objetivo:** Sistema robusto y resiliente

---

### Fase 3: UX y Testing (Sprint 5-6) - 2-4 semanas
1. ✅ Mejorar Formateo (#5)
2. ✅ Suite de Tests (#10)

**Objetivo:** Experiencia de usuario mejorada y código bien testeado

---

### Fase 4: Features Avanzadas (Sprint 7-9) - 3-6 semanas
1. ✅ Schema Analyzer (#8)
2. ✅ Métricas y Monitoreo (#9)
3. ✅ Async Database (#11) - Opcional

**Objetivo:** Sistema production-ready con observabilidad

---

## 🎯 Siguiente Tarea Recomendada

**Comenzar con:** TODO #1 - Sistema de Autenticación

**Justificación:**
- 🔴 Crítico para seguridad
- Bloquea el uso en producción
- Habilita el resto del sistema de permisos
- Base para auditoría empresarial

**Comando para crear branch:**
```bash
git checkout develop
git checkout -b feature/sistema-autenticacion
```

---

## 📊 Estimación Total

| Fase | Duración | TODOs |
|------|----------|-------|
| Fase 1: Seguridad | 2-4 semanas | #1, #2, #3 + SEC |
| Fase 2: Optimización | 2-4 semanas | #4, #6, #7 |
| Fase 3: UX y Testing | 2-4 semanas | #5, #10 |
| Fase 4: Features Avanzadas | 3-6 semanas | #8, #9, #11 |
| **TOTAL** | **9-18 semanas** | **11 TODOs** |

**Estimación conservadora:** 3-5 meses para completar todos los TODOs

---

## ✅ Ya Completado (v0.1.0-base)

- ✅ Refactorizar LLMAgent (TODO #3)
- ✅ Arquitectura de Handlers Modular (TODO #4)
- ✅ Sistema de Prompts Versionado (TODO #6)
- ✅ GitFlow y Control de Versiones
- ✅ Configuración de Variables de Entorno

**Ver:** [ROADMAP.md](ROADMAP.md) para detalles completos

---

**Generado:** 2025-11-26
**Versión:** 1.0
