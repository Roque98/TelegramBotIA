# 📋 PLAN FASE 3 - Features Avanzadas del Sistema de Tools

Plan detallado con objetivos graduales e incrementales para la FASE 3.

**Versión:** 1.0
**Fecha:** 2025-11-27
**Estado:** Planificación
**Pre-requisito:** FASE 1 ✅ y FASE 2 ✅ completadas

---

## 🎯 Visión General

**Objetivo:** Transformar el sistema de Tools de "funcional" a "inteligente y escalable"

**Principio:** Desarrollo incremental - cada paso agrega valor inmediato

**Duración total:** 3-4 semanas (dividido en 8 hitos graduales)

---

## 📊 Estrategia de Implementación

### Enfoque Gradual (Recomendado):
```
Hito 1 → Valor inmediato → Validar → Continuar
Hito 2 → Más valor → Validar → Continuar
...
```

**Ventajas:**
- ✅ Cada hito es funcional y deployable
- ✅ Feedback temprano guía desarrollo
- ✅ Menor riesgo de sobre-ingeniería
- ✅ Puede detenerse en cualquier punto con valor entregado

---

## 🎯 Hito 1: Auto-selección Básica con LLM (3-4 días)

**Objetivo:** LLM decide entre QueryTool, HelpTool y StatsTool

### Valor Entregado:
```
Usuario: "¿Cuántos usuarios hay?"
Sistema: Detecta automáticamente → usa QueryTool
Sin necesidad de escribir /ia
```

### Tareas:

**Día 1: Infraestructura básica**
- [ ] Crear `src/orchestrator/tool_selector.py`
- [ ] Implementar clase `ToolSelector`
- [ ] Método `select_tool(user_query: str) -> str`
- [ ] Integrar con PromptManager

**Día 2: Prompt de selección**
- [ ] Crear prompt template para selección
- [ ] Formato de respuesta estructurado del LLM
- [ ] Validación de respuesta
- [ ] Manejo de errores

**Día 3: Integración**
- [ ] Integrar en UniversalHandler
- [ ] Detectar queries sin comando
- [ ] Llamar a ToolSelector
- [ ] Ejecutar tool seleccionado

**Día 4: Testing y ajustes**
- [ ] Tests unitarios de ToolSelector
- [ ] Tests de integración
- [ ] Pruebas con usuarios
- [ ] Ajustar prompts según resultados

### Archivos a Crear:
```
src/orchestrator/
├── __init__.py
└── tool_selector.py       # ~150 líneas

tests/orchestrator/
└── test_tool_selector.py  # ~100 líneas
```

### Criterios de Éxito:
- ✅ Detecta correctamente 80%+ de queries
- ✅ Tiempo de selección <500ms
- ✅ Fallback graceful si falla

### Ejemplo de Implementación:
```python
# src/orchestrator/tool_selector.py
class ToolSelector:
    """Selecciona el tool apropiado usando LLM."""

    async def select_tool(self, user_query: str) -> Optional[str]:
        """
        Analizar query y seleccionar tool.

        Returns:
            Nombre del tool o None si no hay coincidencia
        """
        prompt = self.prompt_manager.get_prompt(
            'tool_selection',
            query=user_query,
            available_tools=self._get_tools_descriptions()
        )

        response = await self.llm_provider.generate(prompt)
        tool_name = self._parse_tool_name(response)

        return tool_name
```

---

## 🎯 Hito 2: Implementar HelpTool y StatsTool (2-3 días)

**Objetivo:** Comandos básicos como tools para tener más opciones de selección

### Valor Entregado:
```
Usuario: "¿Qué comandos puedo usar?"
Sistema: Auto-selecciona HelpTool → Muestra ayuda

Usuario: "Dame estadísticas del sistema"
Sistema: Auto-selecciona StatsTool → Muestra stats
```

### Tareas:

**Día 1: HelpTool**
- [ ] Crear `src/tools/builtin/help_tool.py`
- [ ] Implementar metadata y parámetros
- [ ] Método `execute()` que lee del registry
- [ ] Auto-generar ayuda desde tools registrados
- [ ] Formatear respuesta markdown

**Día 2: StatsTool**
- [ ] Crear `src/tools/builtin/stats_tool.py`
- [ ] Obtener estadísticas del ToolOrchestrator
- [ ] Obtener estadísticas de la base de datos
- [ ] Formatear respuesta con métricas clave
- [ ] Gráficos ASCII opcionales

**Día 3: Integración y testing**
- [ ] Registrar ambos tools en initializer
- [ ] Tests unitarios
- [ ] Tests de integración con ToolSelector
- [ ] Documentación

### Archivos a Crear:
```
src/tools/builtin/
├── help_tool.py           # ~100 líneas
└── stats_tool.py          # ~120 líneas

tests/tools/
├── test_help_tool.py      # ~80 líneas
└── test_stats_tool.py     # ~80 líneas
```

### Criterios de Éxito:
- ✅ HelpTool muestra todos los tools disponibles
- ✅ StatsTool muestra métricas en tiempo real
- ✅ ToolSelector los detecta correctamente

### Ejemplo de Implementación:
```python
# src/tools/builtin/help_tool.py
class HelpTool(BaseTool):
    """Tool que genera ayuda dinámica desde el registry."""

    async def execute(self, user_id, params, context):
        registry = get_registry()
        tools = registry.get_all_tools()

        # Auto-generar ayuda
        help_text = "**Comandos disponibles:**\n\n"
        for tool in tools:
            help_text += f"**{tool.commands[0]}** - {tool.description}\n"

        return ToolResult.success_result(help_text)
```

---

## 🎯 Hito 3: Multi-Tool Selection (2-3 días)

**Objetivo:** LLM puede seleccionar múltiples tools para una consulta

### Valor Entregado:
```
Usuario: "Muéstrame estadísticas y ayuda"
Sistema: Detecta 2 tools → ejecuta StatsTool + HelpTool
```

### Tareas:

**Día 1: Actualizar ToolSelector**
- [ ] Modificar prompt para selección múltiple
- [ ] Retornar lista de tools en lugar de uno solo
- [ ] Ordenar tools por prioridad
- [ ] Validación de combinaciones válidas

**Día 2: Actualizar ToolOrchestrator**
- [ ] Método `execute_multiple_tools()`
- [ ] Ejecutar tools en paralelo o secuencia
- [ ] Agregar resultados de múltiples tools
- [ ] Formateo combinado de respuestas

**Día 3: Testing**
- [ ] Tests de selección múltiple
- [ ] Tests de ejecución múltiple
- [ ] Verificar performance
- [ ] Ajustar prompts

### Archivos a Modificar:
```
src/orchestrator/tool_selector.py     # +50 líneas
src/tools/tool_orchestrator.py        # +80 líneas
tests/orchestrator/test_tool_selector.py  # +60 líneas
```

### Criterios de Éxito:
- ✅ Detecta correctamente múltiples intents
- ✅ Ejecuta tools en orden lógico
- ✅ Combina respuestas coherentemente

---

## 🎯 Hito 4: Chaining Básico (3-4 días)

**Objetivo:** Pasar resultados de un tool a otro

### Valor Entregado:
```
Usuario: "Consulta usuarios y genera estadísticas"
Sistema:
  1. QueryTool → datos de usuarios
  2. StatsTool recibe datos → calcula stats
```

### Tareas:

**Día 1: Diseño de interfaces**
- [ ] Definir formato de paso de datos entre tools
- [ ] Interfaz `ChainableToolResult`
- [ ] Metadata de compatibilidad entre tools
- [ ] Documentar contratos de datos

**Día 2: Implementar ChainExecutor**
- [ ] Crear `src/orchestrator/chain_executor.py`
- [ ] Clase `ChainExecutor`
- [ ] Método `execute_chain(tools, initial_params)`
- [ ] Validar compatibilidad entre steps

**Día 3: Integración**
- [ ] Actualizar tools para soportar chaining
- [ ] Modificar ToolOrchestrator para usar ChainExecutor
- [ ] Detección automática de oportunidades de chain

**Día 4: Testing**
- [ ] Tests unitarios de ChainExecutor
- [ ] Tests de chains específicos
- [ ] Performance testing
- [ ] Documentación de ejemplos

### Archivos a Crear:
```
src/orchestrator/
├── chain_executor.py      # ~200 líneas
└── chain_types.py         # ~50 líneas (tipos)

tests/orchestrator/
└── test_chain_executor.py # ~150 líneas
```

### Criterios de Éxito:
- ✅ Chain de 2-3 tools funciona correctamente
- ✅ Manejo de errores en medio del chain
- ✅ Performance aceptable (<3s por chain)

### Ejemplo:
```python
# src/orchestrator/chain_executor.py
class ChainExecutor:
    """Ejecuta tools en cadena pasando resultados."""

    async def execute_chain(
        self,
        tools: List[BaseTool],
        initial_params: Dict
    ) -> ToolResult:
        result = None

        for i, tool in enumerate(tools):
            # Primer tool usa parámetros iniciales
            if i == 0:
                params = initial_params
            else:
                # Tools subsecuentes usan resultado anterior
                params = self._transform_result_to_params(
                    result,
                    tool
                )

            result = await tool.execute(params)

            if not result.success:
                break  # Detener chain si falla

        return result
```

---

## 🎯 Hito 5: Configuración de Tools por Entorno (2-3 días)

**Objetivo:** Configurar comportamiento de tools según entorno

### Valor Entregado:
```yaml
# Dev: Debugging habilitado, límites bajos
QueryTool:
  max_results: 10
  debug: true

# Prod: Performance optimizada, límites altos
QueryTool:
  max_results: 100
  cache_enabled: true
```

### Tareas:

**Día 1: Sistema de configuración**
- [ ] Crear `src/tools/tool_config.py`
- [ ] Cargar configs desde YAML/JSON
- [ ] Modelo Pydantic para validación
- [ ] Configs por entorno (dev/staging/prod)

**Día 2: Integración en tools**
- [ ] Modificar BaseTool para leer config
- [ ] Actualizar QueryTool con configuración
- [ ] Aplicar configs en otros tools
- [ ] Hot-reload de configuración (opcional)

**Día 3: Testing y documentación**
- [ ] Tests de carga de configuración
- [ ] Tests de validación
- [ ] Documentar estructura de configs
- [ ] Ejemplos de configuración

### Archivos a Crear:
```
src/tools/
└── tool_config.py         # ~150 líneas

config/tools/
├── dev.yaml               # Configs dev
├── staging.yaml           # Configs staging
└── prod.yaml              # Configs prod

tests/tools/
└── test_tool_config.py    # ~100 líneas
```

### Criterios de Éxito:
- ✅ Configs se cargan correctamente por entorno
- ✅ Validación previene configuraciones inválidas
- ✅ Tools respetan sus configuraciones

---

## 🎯 Hito 6: Optimización de Selección (2 días)

**Objetivo:** Mejorar velocidad y precisión del ToolSelector

### Valor Entregado:
```
Antes: 1-2 segundos para seleccionar
Después: <500ms para seleccionar
Precisión: 80% → 90%+
```

### Tareas:

**Día 1: Optimizaciones**
- [ ] Cache de selecciones frecuentes
- [ ] Prompts más eficientes (menos tokens)
- [ ] Clasificador rápido pre-LLM
- [ ] Paralelizar donde sea posible

**Día 2: Mejora de precisión**
- [ ] Recopilar casos de error de selección
- [ ] Ajustar prompts con ejemplos
- [ ] Few-shot learning en prompt
- [ ] Validación de selección

### Archivos a Modificar:
```
src/orchestrator/tool_selector.py     # +100 líneas
tests/orchestrator/test_tool_selector.py  # +50 líneas
```

### Criterios de Éxito:
- ✅ Tiempo de selección <500ms en 90% casos
- ✅ Precisión >90% en casos comunes
- ✅ Cache hit rate >60%

---

## 🎯 Hito 7: Sistema de Plugins Básico (4-5 días)

**Objetivo:** Cargar tools desde paquetes externos

### Valor Entregado:
```python
# Plugin externo instalable
pip install weather-tool-plugin

# Auto-descubrimiento y registro
# El bot ahora tiene WeatherTool disponible
```

### Tareas:

**Día 1: Estructura de plugins**
- [ ] Definir estructura estándar de plugin
- [ ] Template de plugin de ejemplo
- [ ] Documentar API de plugins
- [ ] Crear plugin de ejemplo (WeatherTool)

**Día 2: Sistema de carga**
- [ ] Crear `src/tools/plugin_manager.py`
- [ ] Auto-descubrimiento de plugins
- [ ] Carga dinámica de módulos
- [ ] Validación de plugins

**Día 3: Seguridad y sandboxing**
- [ ] Validar plugins antes de cargar
- [ ] Sandbox básico para ejecución
- [ ] Límites de recursos
- [ ] Blacklist/whitelist de plugins

**Día 4-5: Testing y documentación**
- [ ] Tests de plugin manager
- [ ] Tests con plugins de ejemplo
- [ ] Guía de creación de plugins
- [ ] Marketplace documentation

### Archivos a Crear:
```
src/tools/
├── plugin_manager.py      # ~250 líneas
└── plugin_validator.py    # ~100 líneas

plugins/examples/
└── weather_tool/          # Plugin de ejemplo
    ├── __init__.py
    ├── tool.py
    └── README.md

docs/
└── PLUGIN_DEVELOPMENT.md  # Guía de desarrollo
```

### Criterios de Éxito:
- ✅ Plugin de ejemplo funciona
- ✅ Auto-descubrimiento funciona
- ✅ Validación previene plugins maliciosos

---

## 🎯 Hito 8: Tool Versioning (2-3 días)

**Objetivo:** Múltiples versiones de tools coexistiendo

### Valor Entregado:
```python
# Migración gradual sin downtime
registry.register(QueryToolV1())  # Legacy
registry.register(QueryToolV2())  # Nueva versión

# Usuario X sigue usando V1
# Usuario Y usa V2 automáticamente
```

### Tareas:

**Día 1: Sistema de versiones**
- [ ] Modificar ToolRegistry para soportar versiones
- [ ] Metadata de versión en tools
- [ ] API para registrar múltiples versiones
- [ ] Estrategia de resolución de versión

**Día 2: Migración de usuarios**
- [ ] Tabla de versiones por usuario
- [ ] API para cambiar versión de usuario
- [ ] Migración gradual automática
- [ ] Rollback si hay problemas

**Día 3: Testing**
- [ ] Tests de coexistencia de versiones
- [ ] Tests de migración
- [ ] Tests de rollback
- [ ] Documentación

### Archivos a Modificar/Crear:
```
src/tools/tool_registry.py         # +150 líneas
src/tools/version_manager.py       # ~200 líneas (nuevo)
tests/tools/test_versioning.py     # ~150 líneas (nuevo)
```

### Criterios de Éxito:
- ✅ 2+ versiones de un tool coexisten
- ✅ Migración de usuarios funciona
- ✅ Rollback funciona en <5 minutos

---

## 📅 Cronograma Sugerido

### Ruta Rápida (Valor Inmediato) - 2 semanas:
```
Semana 1:
├── Hito 1: Auto-selección básica (3-4 días)
└── Hito 2: HelpTool + StatsTool (2-3 días)

Semana 2:
├── Hito 3: Multi-tool selection (2-3 días)
└── Hito 4: Chaining básico (3-4 días)

PAUSA: Validar en producción 1-2 semanas
```

### Ruta Completa (Features Avanzadas) - 4 semanas:
```
Semana 1-2: Hitos 1-4 (como arriba)

Semana 3:
├── Hito 5: Configuración (2-3 días)
└── Hito 6: Optimización (2 días)

Semana 4:
├── Hito 7: Plugins (4-5 días)
└── Hito 8: Versioning (2-3 días)
```

---

## 🎯 Puntos de Decisión

Después de cada hito, evaluar:

**¿Continuar al siguiente hito?**
- ✅ SI: Hito actual funciona bien + hay necesidad
- ⏸️ PAUSAR: Validar en producción primero
- ❌ DETENER: Ya tenemos suficiente valor

**Señales para continuar:**
- ✅ Tests pasan >95%
- ✅ Performance es aceptable
- ✅ Usuarios están satisfechos
- ✅ Hay casos de uso claros para siguiente hito

**Señales para pausar:**
- ⚠️ Bugs importantes sin resolver
- ⚠️ Performance degradada
- ⚠️ Complejidad aumentando mucho
- ⚠️ No hay casos de uso claros

---

## 📊 Métricas de Éxito por Hito

| Hito | Métrica Clave | Target |
|------|---------------|--------|
| 1 | Precisión de selección | >80% |
| 1 | Tiempo de selección | <500ms |
| 2 | Tools adicionales | 2+ tools |
| 3 | Multi-tool accuracy | >75% |
| 4 | Chains exitosos | >85% |
| 4 | Tiempo de chain | <3s |
| 5 | Config load time | <100ms |
| 6 | Selection time | <300ms |
| 7 | Plugins cargados | 1+ |
| 8 | Versiones activas | 2+ |

---

## 🛠️ Stack Tecnológico

**Nuevos componentes:**
```
src/orchestrator/        # Lógica de orquestación
├── tool_selector.py     # Selección inteligente
└── chain_executor.py    # Ejecución en cadena

src/tools/
├── plugin_manager.py    # Gestión de plugins
├── tool_config.py       # Configuración
└── version_manager.py   # Versionado

config/tools/            # Configuraciones
├── dev.yaml
├── staging.yaml
└── prod.yaml

plugins/                 # Plugins externos
└── examples/
```

---

## 🔄 Integración con GitFlow

Cada hito = feature branch:
```bash
# Hito 1
git checkout -b feature/tools-auto-selection
# ... implementar ...
git commit -m "feat(orchestrator): auto-selección básica"
git push && merge to develop

# Hito 2
git checkout -b feature/tools-help-stats
# ... implementar ...
git commit -m "feat(tools): HelpTool y StatsTool"
git push && merge to develop

# Y así sucesivamente...
```

---

## 📚 Documentación a Crear

- [ ] `TOOL_SELECTOR_GUIDE.md` - Cómo funciona auto-selección
- [ ] `CHAINING_GUIDE.md` - Crear y usar chains
- [ ] `TOOL_CONFIG_GUIDE.md` - Configurar tools
- [ ] `PLUGIN_DEVELOPMENT.md` - Crear plugins
- [ ] `VERSIONING_GUIDE.md` - Gestionar versiones

---

## ⚡ Quick Wins (Valor Rápido)

Si tienes tiempo limitado, prioriza:

**1. Hito 1 + 2 (1 semana):**
- Auto-selección + más tools
- Mayor impacto en UX
- Usuarios no necesitan recordar comandos

**2. Hito 3 + 4 (1 semana):**
- Multi-tool + chaining
- Automatización de workflows
- Valor para power users

**3. El resto según necesidad**

---

## 🎯 Estado de FASE 3

**Actualmente:** Planificación
**Pre-requisitos:** FASE 1 ✅ FASE 2 ✅
**Próximo paso:** Decidir si implementar y desde qué hito empezar

**Opciones:**
1. ✅ Empezar con Hito 1 (auto-selección)
2. ⏸️ Validar FASE 2 en producción primero
3. 📋 Planificar más detalle de hitos específicos

---

**Documento vivo - Se actualizará durante implementación**

**Última actualización:** 2025-11-27
**Versión:** 1.0
**Autor:** Sistema de Planning
