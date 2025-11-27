# 🎯 Plan de Implementación: Sistema de Orquestación de Tools

> **Fecha de creación:** 2025-11-26
> **Versión:** 1.0
> **Estado:** Pendiente de implementación
> **Prioridad:** ALTA

---

## 📋 Tabla de Contenidos

- [Visión General](#visión-general)
- [Objetivos](#objetivos)
- [Arquitectura Propuesta](#arquitectura-propuesta)
- [Fases de Implementación](#fases-de-implementación)
- [Beneficios Esperados](#beneficios-esperados)
- [Riesgos y Mitigaciones](#riesgos-y-mitigaciones)
- [Referencias](#referencias)

---

## 🎨 Visión General

### Situación Actual

El bot tiene una arquitectura modular sólida pero carece de un sistema de orquestación de "tools" (capacidades/funcionalidades). Actualmente:

- ✅ Handlers bien separados
- ✅ Patrones de diseño aplicados (Strategy, Adapter, Orchestrator)
- ❌ No hay registro centralizado de capacidades
- ❌ Difícil agregar nuevas funcionalidades (5+ archivos por feature)
- ❌ No hay introspección de capacidades disponibles
- ❌ No se pueden habilitar/deshabilitar features dinámicamente

### Visión Futura

Implementar un **sistema de orquestación de Tools** que permita:

- ✅ Agregar features con 1 solo archivo (~80 líneas)
- ✅ Descubrimiento automático de capacidades
- ✅ Hot-reload de funcionalidades
- ✅ Auto-documentación
- ✅ Testing simplificado
- ✅ Plugin system para extensiones externas

---

## 🎯 Objetivos

### Objetivos Principales

1. **Extensibilidad:** Reducir complejidad de agregar features de 5+ archivos a 1 archivo
2. **Descubrimiento:** Sistema auto-documentado de capacidades disponibles
3. **Seguridad:** Centralizar autenticación y autorización
4. **Testing:** Facilitar testing unitario de features aisladas
5. **Mantenibilidad:** Reducir acoplamiento entre componentes

### Métricas de Éxito

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Archivos por feature | 5+ | 1 | 80% |
| Líneas de código | 200+ | 80 | 60% |
| Tiempo de desarrollo | 4-6h | 1-2h | 66% |
| Cobertura de tests | ~0% | >80% | +80pp |
| Tiempo de onboarding | Alto | Bajo | Significativo |

---

## 🏗️ Arquitectura Propuesta

### Estructura de Directorios

```
src/
├── tools/                      # Sistema de Tools (NUEVO)
│   ├── __init__.py
│   ├── tool_base.py           # Clases base abstractas
│   ├── tool_registry.py       # Registro centralizado (Singleton)
│   ├── tool_loader.py         # Carga dinámica de tools
│   ├── tool_config.py         # Configuración de tools
│   └── builtin/               # Tools incorporados
│       ├── __init__.py
│       ├── query_tool.py      # Consultas BD (migrado)
│       ├── help_tool.py       # Sistema de ayuda
│       ├── stats_tool.py      # Estadísticas
│       ├── registration_tool.py # Registro de usuarios
│       └── example_tool.py    # Plantilla para nuevos tools
│
├── orchestrator/              # Orquestación (NUEVO)
│   ├── __init__.py
│   ├── orchestrator.py        # Orquestador principal
│   ├── execution_context.py   # Contexto de ejecución
│   ├── tool_selector.py       # Selección inteligente (Fase 3)
│   └── chain_executor.py      # Ejecución encadenada (Fase 3)
│
├── services/                  # Service Layer (NUEVO)
│   ├── __init__.py
│   ├── auth_service.py        # Lógica de autenticación
│   ├── permission_service.py  # Lógica de permisos
│   ├── query_service.py       # Lógica de queries
│   └── notification_service.py # Notificaciones (futuro)
│
└── bot/
    └── handlers/
        └── universal_handler.py # Handler universal (NUEVO)
```

### Componentes Clave

#### 1. BaseTool (Clase Base)

```python
class BaseTool(ABC):
    """Clase base abstracta para todos los tools."""

    @abstractmethod
    def get_metadata(self) -> ToolMetadata:
        """Metadatos: nombre, descripción, comandos, permisos."""

    @abstractmethod
    def get_parameters(self) -> List[ToolParameter]:
        """Parámetros que acepta el tool."""

    @abstractmethod
    async def execute(
        self,
        user_id: int,
        params: Dict[str, Any],
        context: ExecutionContext
    ) -> ToolResult:
        """Lógica de ejecución del tool."""
```

**Responsabilidades:**
- Definir interface consistente
- Validación automática de parámetros
- Metadata autodocumentada

#### 2. ToolRegistry (Singleton)

```python
class ToolRegistry:
    """Registro centralizado de tools."""

    def register(self, tool: BaseTool) -> None
    def unregister(self, tool_name: str) -> None
    def get_tool_by_name(self, name: str) -> Optional[BaseTool]
    def get_tool_by_command(self, command: str) -> Optional[BaseTool]
    def get_all_tools(self) -> List[BaseTool]
    def get_tools_by_category(self, category: str) -> List[BaseTool]
    def get_user_available_tools(self, user_id: int) -> List[BaseTool]
```

**Responsabilidades:**
- Punto central de registro de tools
- Descubrimiento de capacidades
- Filtrado por permisos de usuario

#### 3. ToolOrchestrator

```python
class ToolOrchestrator:
    """Orquestador de ejecución de tools."""

    async def execute_command(
        self,
        user_id: int,
        command: str,
        params: Dict[str, Any],
        context: ExecutionContext
    ) -> ToolResult:
        """
        Flujo de ejecución:
        1. Buscar tool por comando
        2. Verificar autenticación
        3. Verificar permisos
        4. Validar parámetros
        5. Ejecutar tool
        6. Auditar operación
        """
```

**Responsabilidades:**
- Orquestar ejecución de tools
- Manejar auth/permisos consistentemente
- Auditoría automática
- Manejo centralizado de errores

#### 4. ExecutionContext

```python
class ExecutionContext:
    """Contexto de ejecución para tools."""

    telegram_update: Update
    telegram_context: ContextTypes.DEFAULT_TYPE
    db_manager: DatabaseManager
    llm_agent: LLMAgent

    def get_service(self, name: str) -> Any
    def get_user_id(self) -> int
    def get_chat_id(self) -> int
```

**Responsabilidades:**
- Proveer dependencias a tools
- Desacoplar tools de Telegram
- Facilitar testing con mocks

---

## 📅 Fases de Implementación

### FASE 1: Fundamentos del Sistema (1-2 semanas)

**Objetivo:** Crear la infraestructura base del sistema de Tools

#### 1.1 Crear Clases Base (3-4 días)

**Archivos a crear:**
```
src/tools/
    __init__.py
    tool_base.py         # BaseTool, ToolMetadata, ToolParameter, ToolResult
```

**Tareas:**
- [ ] Definir `ToolMetadata` (Pydantic model)
- [ ] Definir `ToolParameter` (Pydantic model)
- [ ] Definir `ToolResult` (Pydantic model)
- [ ] Implementar `BaseTool` (clase abstracta)
- [ ] Agregar validación de parámetros
- [ ] Escribir tests unitarios

**Entregable:** Clases base documentadas y testeadas

**Referencia:** Ver sección "Componentes Clave" para detalles de implementación

---

#### 1.2 Implementar ToolRegistry (2-3 días)

**Archivos a crear:**
```
src/tools/
    tool_registry.py     # ToolRegistry singleton
```

**Tareas:**
- [ ] Implementar patrón Singleton
- [ ] Método `register(tool)`
- [ ] Método `unregister(tool_name)`
- [ ] Método `get_tool_by_command(command)`
- [ ] Método `get_user_available_tools(user_id, permission_checker)`
- [ ] Método `get_tools_by_category(category)`
- [ ] Escribir tests unitarios
- [ ] Documentar API pública

**Entregable:** Registry funcional con tests

---

#### 1.3 Crear Service Layer (2-3 días)

**Archivos a crear:**
```
src/services/
    __init__.py
    auth_service.py      # Lógica de autenticación
    permission_service.py # Lógica de permisos
```

**Tareas:**
- [ ] Extraer lógica de `UserManager` a `AuthService`
- [ ] Extraer lógica de `PermissionChecker` a `PermissionService`
- [ ] Implementar `QueryService` (preparación para Fase 2)
- [ ] Definir interfaces claras
- [ ] Escribir tests unitarios
- [ ] Documentar services

**Entregable:** Service layer desacoplado de handlers

---

#### 1.4 Implementar Orquestador (2-3 días)

**Archivos a crear:**
```
src/orchestrator/
    __init__.py
    orchestrator.py      # ToolOrchestrator
    execution_context.py # ExecutionContext
```

**Tareas:**
- [ ] Implementar `ExecutionContext`
- [ ] Implementar `ToolOrchestrator.execute_command()`
- [ ] Integrar con `AuthService` y `PermissionService`
- [ ] Implementar auditoría automática
- [ ] Manejo de errores centralizado
- [ ] Escribir tests unitarios
- [ ] Documentar flujo de ejecución

**Entregable:** Orquestador completo y testeado

---

#### 1.5 Escribir Tests de Integración (1-2 días)

**Archivos a crear:**
```
tests/
    test_tools_integration.py
    test_orchestrator.py
```

**Tareas:**
- [ ] Test de registro de tools
- [ ] Test de ejecución completa
- [ ] Test de validación de permisos
- [ ] Test de manejo de errores
- [ ] Test de auditoría

**Entregable:** Suite de tests >80% coverage en componentes nuevos

---

### FASE 2: Migración de Funcionalidad Existente (2-3 semanas)

**Objetivo:** Migrar handlers existentes al sistema de Tools

#### 2.1 Migrar QueryHandler a QueryTool (3-4 días)

**Archivos a crear:**
```
src/tools/builtin/
    __init__.py
    query_tool.py        # QueryTool (migrado de query_handlers.py)
```

**Tareas:**
- [ ] Crear `QueryTool` heredando de `BaseTool`
- [ ] Implementar `get_metadata()`
- [ ] Implementar `get_parameters()`
- [ ] Migrar lógica de `query_handlers.py` a `execute()`
- [ ] Integrar con `StatusMessage`
- [ ] Escribir tests unitarios
- [ ] Probar en paralelo con handler actual

**Entregable:** QueryTool funcional en paralelo con handler actual

**Notas:**
- Mantener `query_handlers.py` temporalmente
- Probar ambos en paralelo antes de eliminar handler antiguo

---

#### 2.2 Crear UniversalHandler (2-3 días)

**Archivos a crear:**
```
src/bot/handlers/
    universal_handler.py  # Handler que usa orquestador
```

**Tareas:**
- [ ] Implementar `UniversalHandler`
- [ ] Integrar con `ToolOrchestrator`
- [ ] Detectar comandos vs texto libre
- [ ] Integrar con `StatusMessage`
- [ ] Manejo de errores
- [ ] Escribir tests

**Entregable:** Handler universal que delega a orquestador

---

#### 2.3 Migrar Command Handlers (3-4 días)

**Archivos a crear:**
```
src/tools/builtin/
    help_tool.py         # /help
    stats_tool.py        # /stats
    start_tool.py        # /start
```

**Tareas:**
- [ ] Crear `HelpTool` (auto-genera ayuda desde registry)
- [ ] Crear `StatsTool`
- [ ] Crear `StartTool`
- [ ] Registrar tools en registry
- [ ] Escribir tests unitarios

**Entregable:** Comandos básicos como tools

---

#### 2.4 Migrar Registration Handlers (2-3 días)

**Archivos a crear:**
```
src/tools/builtin/
    registration_tool.py  # /register, /verify
```

**Tareas:**
- [ ] Migrar flujo de registro a RegistrationTool
- [ ] Manejar estado de conversación
- [ ] Integrar con `AuthService`
- [ ] Escribir tests

**Entregable:** Sistema de registro como tool

---

#### 2.5 Actualizar TelegramBot (1-2 días)

**Archivos a modificar:**
```
src/bot/telegram_bot.py
```

**Tareas:**
- [ ] Integrar `ToolOrchestrator` en inicialización
- [ ] Registrar `UniversalHandler`
- [ ] Registrar todos los builtin tools
- [ ] Mantener compatibilidad con handlers antiguos (temporal)
- [ ] Escribir tests de integración

**Entregable:** Bot usando sistema de tools

---

#### 2.6 Testing End-to-End y Migración Final (2-3 días)

**Tareas:**
- [ ] Tests E2E de flujos completos
- [ ] Validar en entorno de staging
- [ ] Comparar resultados con handlers antiguos
- [ ] Eliminar handlers antiguos (si todo funciona)
- [ ] Actualizar documentación
- [ ] Crear tag de release

**Entregable:** Sistema de Tools funcionando en producción

---

### FASE 3: Features Avanzadas (3-4 semanas)

**Objetivo:** Agregar capacidades avanzadas al sistema de Tools

#### 3.1 Auto-selección de Tool por LLM (1 semana)

**Archivos a crear:**
```
src/orchestrator/
    tool_selector.py     # Selección inteligente
```

**Concepto:**
El LLM decide qué tool usar basado en la consulta del usuario.

**Ejemplo:**
```
Usuario: "Muéstrame las ventas del mes y crea un ticket si hay problemas"

LLM detecta:
1. Usar QueryTool para "ventas del mes"
2. Usar TicketTool para "crear ticket"
3. Encadenar resultados
```

**Tareas:**
- [ ] Crear prompt para selección de tool
- [ ] Implementar `ToolSelector`
- [ ] Integrar con `PromptManager`
- [ ] Manejar múltiples tools en una consulta
- [ ] Escribir tests

**Entregable:** Sistema que selecciona tools automáticamente

---

#### 3.2 Chaining de Tools (1 semana)

**Archivos a crear:**
```
src/orchestrator/
    chain_executor.py    # Ejecución encadenada
```

**Concepto:**
Ejecutar múltiples tools en secuencia, pasando resultados entre ellos.

**Ejemplo:**
```
1. QueryTool → obtener ventas
2. AnalysisTool → analizar datos
3. ReportTool → generar reporte
4. EmailTool → enviar reporte
```

**Tareas:**
- [ ] Implementar `ChainExecutor`
- [ ] Definir sintaxis de cadenas
- [ ] Manejar paso de datos entre tools
- [ ] Manejo de errores en cadenas
- [ ] Escribir tests

**Entregable:** Sistema de chaining funcional

---

#### 3.3 Configuración de Tools (3-4 días)

**Archivos a crear:**
```
src/tools/
    tool_config.py       # Configuración por entorno
```

**Concepto:**
Configurar tools por entorno (dev/staging/prod).

**Ejemplo:**
```yaml
# config/tools/query_tool.yaml
dev:
  enabled: true
  max_results: 10
  cache_enabled: false

prod:
  enabled: true
  max_results: 100
  cache_enabled: true
  cache_ttl: 3600
```

**Tareas:**
- [ ] Sistema de configuración por entorno
- [ ] Hot-reload de configuración
- [ ] Validación con Pydantic
- [ ] Escribir tests

**Entregable:** Tools configurables por entorno

---

#### 3.4 Sistema de Plugins (1-2 semanas)

**Archivos a crear:**
```
src/tools/
    tool_loader.py       # Carga dinámica desde paquetes
    plugin_manager.py    # Gestión de plugins
```

**Concepto:**
Cargar tools desde paquetes externos.

**Estructura de plugin:**
```
my_plugin/
    __init__.py
    tool.py              # MyCustomTool
    requirements.txt
    README.md
```

**Tareas:**
- [ ] Sistema de descubrimiento de plugins
- [ ] Carga dinámica de módulos Python
- [ ] Validación de plugins
- [ ] Sandboxing de plugins (seguridad)
- [ ] Marketplace de plugins (documentación)
- [ ] Escribir tests

**Entregable:** Sistema de plugins funcional

---

#### 3.5 Tool Versioning (3-4 días)

**Concepto:**
Múltiples versiones de un tool coexistiendo.

**Ejemplo:**
```python
registry.register(QueryToolV1())  # Para usuarios antiguos
registry.register(QueryToolV2())  # Nueva versión
registry.set_default_version('query', 'v2')
```

**Tareas:**
- [ ] Soporte para versiones múltiples
- [ ] Migración gradual de usuarios
- [ ] A/B testing de versiones
- [ ] Deprecation warnings
- [ ] Escribir tests

**Entregable:** Sistema de versionado de tools

---

### FASE 4: Ecosystem y Optimización (2-3 semanas)

**Objetivo:** Crear un ecosistema completo alrededor de Tools

#### 4.1 Tool Analytics (1 semana)

**Archivos a crear:**
```
src/tools/
    tool_analytics.py    # Métricas de uso
```

**Métricas a trackear:**
- Frecuencia de uso por tool
- Tasa de éxito/error
- Tiempo de ejecución promedio
- Usuarios activos por tool
- Queries más frecuentes

**Tareas:**
- [ ] Implementar tracking de métricas
- [ ] Integrar con sistema de logging
- [ ] Dashboard de métricas (opcional)
- [ ] Alertas automáticas
- [ ] Escribir tests

**Entregable:** Sistema de analytics completo

---

#### 4.2 Tool Composition (1 semana)

**Concepto:**
Crear tools complejos combinando tools simples.

**Ejemplo:**
```python
class SalesReportTool(CompositeTool):
    """Tool compuesto de QueryTool + AnalysisTool + ReportTool."""

    def __init__(self):
        self.steps = [
            QueryTool(),
            AnalysisTool(),
            ReportTool()
        ]
```

**Tareas:**
- [ ] Implementar `CompositeTool`
- [ ] Definir DSL para composición
- [ ] Validación de composiciones
- [ ] Escribir tests

**Entregable:** Sistema de composición de tools

---

#### 4.3 Tool Marketplace (1 semana)

**Concepto:**
Directorio público de tools disponibles.

**Características:**
- Búsqueda de tools
- Ratings y reviews
- Instalación con 1 comando
- Documentación generada automáticamente

**Tareas:**
- [ ] Crear directorio de tools
- [ ] Sistema de búsqueda
- [ ] Generación automática de docs
- [ ] CLI para instalación
- [ ] Sitio web de marketplace (opcional)

**Entregable:** Marketplace funcional

---

## 🎁 Beneficios Esperados

### Beneficios Técnicos

1. **Extensibilidad 10x**
   - De 5+ archivos a 1 archivo por feature
   - De 200+ líneas a ~80 líneas
   - De 4-6 horas a 1-2 horas

2. **Testing Mejorado**
   - Tests unitarios aislados por tool
   - Mocks fáciles de crear
   - Coverage >80% alcanzable

3. **Mantenibilidad**
   - Código más organizado
   - Menos acoplamiento
   - Cambios localizados

4. **Seguridad**
   - Auth/permisos centralizados
   - Auditoría automática
   - Validación consistente

### Beneficios de Negocio

1. **Time-to-Market**
   - Nuevas features en horas, no días
   - Iteración más rápida
   - Feedback más rápido

2. **Escalabilidad**
   - Fácil agregar capacidades
   - Sistema de plugins para terceros
   - Marketplace de extensiones

3. **Developer Experience**
   - Onboarding más fácil
   - Documentación auto-generada
   - Menos curva de aprendizaje

4. **Calidad**
   - Menos bugs por feature
   - Testing más completo
   - Código más confiable

---

## ⚠️ Riesgos y Mitigaciones

### Riesgo 1: Complejidad Inicial

**Descripción:** El sistema de Tools agrega complejidad arquitectónica.

**Probabilidad:** ALTA
**Impacto:** MEDIO

**Mitigación:**
- Implementar en fases incrementales
- Mantener handlers antiguos en paralelo temporalmente
- Documentación extensa con ejemplos
- Training para equipo

---

### Riesgo 2: Migración Incompleta

**Descripción:** Quedar con dos sistemas en paralelo indefinidamente.

**Probabilidad:** MEDIA
**Impacto:** ALTO

**Mitigación:**
- Definir fecha límite para migración
- Plan de migración detallado
- Tests E2E para validar paridad
- Deprecation warnings en handlers antiguos

---

### Riesgo 3: Performance

**Descripción:** El overhead del orquestador puede afectar performance.

**Probabilidad:** BAJA
**Impacto:** MEDIO

**Mitigación:**
- Benchmarks antes/después
- Optimización de paths críticos
- Caching donde sea posible
- Monitoreo de performance

---

### Riesgo 4: Breaking Changes

**Descripción:** Cambios pueden romper funcionalidad existente.

**Probabilidad:** MEDIA
**Impacto:** ALTO

**Mitigación:**
- Tests E2E exhaustivos
- Staging environment
- Rollback plan
- Feature flags para nueva funcionalidad

---

## 📚 Referencias

### Documentos Relacionados

- [ROADMAP.md](ROADMAP.md) - Roadmap general del proyecto
- [PENDIENTES.md](PENDIENTES.md) - Lista de pendientes
- [COMMIT_GUIDELINES.md](COMMIT_GUIDELINES.md) - Guías de commits
- [GITFLOW.md](GITFLOW.md) - Estrategia de branches

### Análisis Técnico

Este plan está basado en el análisis arquitectónico detallado realizado el 2025-11-26. El análisis completo incluye:

- Revisión de 47 archivos Python (~8,000+ líneas)
- Identificación de patrones de diseño existentes
- Comparación con mejores prácticas de la industria
- Estimaciones de esfuerzo basadas en experiencia

### Patrones de Diseño Utilizados

- **Strategy Pattern:** Para LLM providers
- **Adapter Pattern:** Para APIs de LLM
- **Singleton Pattern:** Para ToolRegistry
- **Factory Pattern:** Para creación de tools
- **Template Method:** En BaseTool
- **Dependency Injection:** En ExecutionContext
- **Service Layer:** Para lógica de negocio

### Inspiración de Proyectos

- LangChain Tools System
- OpenAI Function Calling
- Rasa Action Server
- Botpress Skills
- Microsoft Bot Framework Dialogs

---

## 📊 Estimación Total

### Esfuerzo por Fase

| Fase | Duración | Complejidad | Riesgo |
|------|----------|-------------|--------|
| Fase 1: Fundamentos | 1-2 semanas | ALTA | MEDIO |
| Fase 2: Migración | 2-3 semanas | MEDIA | ALTO |
| Fase 3: Features Avanzadas | 3-4 semanas | ALTA | MEDIO |
| Fase 4: Ecosystem | 2-3 semanas | MEDIA | BAJO |
| **TOTAL** | **8-12 semanas** | - | - |

### Recursos Necesarios

- **Desarrollador Senior:** Full-time
- **Code Reviews:** 2-3 horas/semana
- **Testing:** 20% del tiempo de desarrollo
- **Documentación:** 10% del tiempo de desarrollo

### Dependencies

**Técnicas:**
- Python 3.10+
- python-telegram-bot >= 20.0
- Pydantic >= 2.0
- SQLAlchemy >= 2.0

**De Negocio:**
- Aprobación para cambios arquitectónicos
- Tiempo de staging/testing
- Training para equipo

---

## 🚀 Próximos Pasos

### Inmediatos (Esta Semana)

1. ✅ Revisar este plan con el equipo
2. ✅ Obtener aprobación para Fase 1
3. ✅ Crear branch `feature/tools-system-fase1`
4. ✅ Setup de ambiente de desarrollo

### Fase 1 - Semana 1

1. ✅ Implementar `tool_base.py`
2. ✅ Escribir tests para clases base
3. ✅ Implementar `tool_registry.py`
4. ✅ Escribir tests para registry

### Fase 1 - Semana 2

1. ✅ Crear service layer
2. ✅ Implementar orquestador
3. ✅ Tests de integración
4. ✅ Code review y merge a develop

---

## 📝 Notas de Implementación

### Convenciones de Código

- Seguir PEP 8
- Type hints obligatorios
- Docstrings en formato Google
- Tests unitarios para todo código nuevo
- Coverage mínimo: 80%

### Commits

Seguir [Conventional Commits](COMMIT_GUIDELINES.md):
```
feat(tools): agregar BaseTool y ToolMetadata
fix(orchestrator): corregir validación de permisos
docs(tools): documentar sistema de plugins
test(tools): agregar tests de integración
```

### Code Review

- Todos los PRs requieren revisión
- Checklist de PR en template
- Tests deben pasar antes de merge
- Documentación actualizada

### Deployment

- Fase 1: Solo en develop
- Fase 2: Staging primero, luego producción gradual
- Fase 3+: Feature flags para habilitar gradualmente

---

## 🎯 KPIs de Éxito

### Métricas Técnicas

- ✅ Coverage de tests >80%
- ✅ Tiempo de desarrollo de feature <2 horas
- ✅ Líneas de código por feature <100
- ✅ Tiempo de respuesta sin degradación
- ✅ 0 regresiones en funcionalidad existente

### Métricas de Producto

- ✅ 5+ nuevas features implementadas usando tools
- ✅ Documentación auto-generada completa
- ✅ 0 incidentes relacionados con migración
- ✅ Developer satisfaction score >8/10

---

**Documento vivo - Se actualizará conforme avance la implementación**

**Última actualización:** 2025-11-26
**Próxima revisión:** Después de completar Fase 1
