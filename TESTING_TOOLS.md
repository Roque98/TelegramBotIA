# 🧪 Guía de Pruebas - Sistema de Tools

Esta guía explica cómo probar el sistema de orquestación de Tools implementado en las FASES 1 y 2.

## 📋 Tipos de Pruebas

### 1. Tests Unitarios (Pytest)

Tests automatizados que verifican componentes individuales.

**Ubicación:** `tests/tools/`

**Tests disponibles:**
- `test_tool_base.py` - Clases base, parámetros, validación
- `test_tool_registry.py` - Registry singleton, búsquedas, filtrado
- `test_query_tool.py` - QueryTool, validación, ejecución
- `test_integration.py` - Flujos end-to-end completos

**Ejecutar todos los tests:**
```bash
# Instalar pytest si no está instalado
pip install pytest pytest-asyncio

# Ejecutar todos los tests
pytest tests/tools/ -v

# Ejecutar con coverage
pytest tests/tools/ -v --cov=src/tools --cov-report=html

# Ejecutar un archivo específico
pytest tests/tools/test_query_tool.py -v

# Ejecutar un test específico
pytest tests/tools/test_query_tool.py::TestQueryTool::test_execute_success -v
```

**Resultados esperados:**
```
tests/tools/test_tool_base.py ............... (15 tests) ✅
tests/tools/test_tool_registry.py ........... (20 tests) ✅
tests/tools/test_query_tool.py .............. (12 tests) ✅
tests/tools/test_integration.py ............. (10 tests) ✅

Total: 57 tests passed
Coverage: >90%
```

---

### 2. Pruebas Manuales (Script Interactivo)

Script que ejecuta el sistema completo con queries reales al LLM y base de datos.

**Ubicación:** `test_tools_manual.py`

**Pre-requisitos:**
1. Archivo `.env` configurado con API keys válidas
2. Base de datos accesible
3. Conexión a internet (para LLM)

**Ejecutar:**
```bash
python test_tools_manual.py
```

**Tests incluidos:**

**Test 1: Inicialización de Tools**
- ✅ Verifica registro de QueryTool
- ✅ Confirma comandos disponibles (/ia, /query)
- ✅ Muestra resumen de tools

**Test 2: QueryTool Directo**
- ✅ Ejecuta query directamente sin orquestador
- ✅ Verifica integración con LLMAgent
- ✅ Muestra tiempo de ejecución

**Test 3: Flujo con Orquestador**
- ✅ Ejecuta múltiples queries
- ✅ Verifica autenticación y validación
- ✅ Muestra estadísticas de ejecución

**Test 4: Validación de Parámetros**
- ✅ Query muy corta (debe fallar)
- ✅ Query válida (debe pasar)
- ✅ Query muy larga (debe fallar)

**Test 5: Manejo de Errores**
- ✅ Context sin LLMAgent
- ✅ Comando inexistente
- ✅ Errores de LLM

**Salida esperada:**
```
🧪 SUITE DE PRUEBAS MANUALES - SISTEMA DE TOOLS
================================================================
Provider LLM: gpt-4o-mini
Base de datos: postgresql://...
================================================================

TEST 1: Inicialización de Tools
================================================================
✅ Tools registrados: 1
✅ Comandos disponibles: /ia, /query

TEST 2: QueryTool - Ejecución Directa
================================================================
🔍 Ejecutando query: ¿Cuántos usuarios hay registrados?
✅ Query ejecutada exitosamente
⏱️  Tiempo de ejecución: 1234.56ms
📊 Respuesta:
------------------------------------------------------------
Hay 5 usuarios registrados en el sistema.
------------------------------------------------------------

... (más tests) ...

📊 RESUMEN DE PRUEBAS
================================================================
✅ PASÓ - Inicialización de Tools
✅ PASÓ - QueryTool Directo
✅ PASÓ - Flujo con Orquestador
✅ PASÓ - Validación de Parámetros
✅ PASÓ - Manejo de Errores
================================================================

Resultado final: 5/5 tests pasaron
Tasa de éxito: 100.0%

🎉 ¡Todos los tests pasaron exitosamente!
```

---

### 3. Pruebas con Bot de Telegram (En Vivo)

Probar el sistema integrado en el bot de Telegram real.

**Pre-requisitos:**
1. Bot de Telegram configurado
2. Sistema de Tools integrado en `telegram_bot.py`
3. Usuario registrado y con permisos

**Pasos:**

**1. Integrar Tools en el bot:**

Editar `src/bot/telegram_bot.py` para inicializar tools:

```python
from src.tools import initialize_builtin_tools

class TelegramBot:
    def __init__(self):
        # ... código existente ...

        # Inicializar sistema de Tools
        initialize_builtin_tools()
        logger.info("Sistema de Tools inicializado")
```

**2. Ejecutar el bot:**
```bash
python main.py
```

**3. Probar comandos:**

En Telegram, enviar:
```
/ia ¿Cuántos usuarios hay registrados?
```

**Respuesta esperada:**
```
🔍 Analizando tu consulta...
🤖 Procesando con IA...

Hay 5 usuarios registrados en el sistema.
```

**Comandos para probar:**
- `/ia ¿Cuántos usuarios hay?` - Query de base de datos
- `/ia ¿Qué es Python?` - Query general (sin BD)
- `/query Dame un resumen del sistema` - Comando alternativo
- `¿Qué tablas tiene la BD?` - Query implícita (sin comando)

---

## 🔍 Debugging

### Ver logs detallados

```bash
# Configurar nivel de log en .env
LOG_LEVEL=DEBUG

# Ejecutar con logs
python test_tools_manual.py 2>&1 | tee test_output.log
```

### Componentes a verificar

**1. ToolRegistry:**
```python
from src.tools import get_registry, get_tool_summary

registry = get_registry()
print(f"Tools registrados: {registry.get_tools_count()}")
print(f"Comandos: {registry.get_commands_list()}")

summary = get_tool_summary()
print(summary)
```

**2. QueryTool:**
```python
from src.tools import get_registry

tool = get_registry().get_tool_by_name("query")
print(f"Tool: {tool.name}")
print(f"Comandos: {tool.commands}")
print(f"Parámetros: {tool.get_parameters()}")
```

**3. LLMAgent:**
```python
from src.agent.llm_agent import LLMAgent

agent = LLMAgent()
response = await agent.process_query("¿Cuántos usuarios hay?")
print(response)
```

---

## ⚠️ Problemas Comunes

### Error: "Tool 'query' no encontrado"

**Causa:** Tools no inicializados

**Solución:**
```python
from src.tools import initialize_builtin_tools
initialize_builtin_tools()
```

### Error: "LLMAgent no disponible"

**Causa:** ExecutionContext sin LLMAgent

**Solución:**
```python
from src.tools import ExecutionContextBuilder

context = (
    ExecutionContextBuilder()
    .with_llm_agent(llm_agent)
    .build()
)
```

### Error: API key no válida

**Causa:** Variables de entorno no configuradas

**Solución:**
```bash
# Verificar .env
cat .env | grep API_KEY

# Configurar keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Tests fallan con "Connection refused"

**Causa:** Base de datos no accesible

**Solución:**
```bash
# Verificar conexión
python test_db_connection.py

# Verificar URL en .env
DATABASE_URL=postgresql://user:pass@localhost:5432/db
```

---

## 📊 Métricas de Éxito

### Tests Unitarios
- ✅ >90% de tests pasan
- ✅ Coverage >90%
- ✅ Sin warnings de pytest
- ✅ Tiempo de ejecución <30 segundos

### Pruebas Manuales
- ✅ 5/5 tests pasan
- ✅ Queries se ejecutan en <5 segundos
- ✅ Errores manejados correctamente
- ✅ Sin excepciones no capturadas

### Pruebas con Bot
- ✅ Comandos responden en <10 segundos
- ✅ Mensajes de estado funcionan
- ✅ Respuestas bien formateadas
- ✅ Validación de permisos funciona

---

## 🚀 Próximos Pasos

Una vez que todas las pruebas pasen:

1. **FASE 3:** Implementar HelpTool, StatsTool, RegistrationTool
2. **Migración:** Reemplazar handlers tradicionales con Tools
3. **Auto-selección:** Implementar selección automática de tools con LLM
4. **Chaining:** Permitir encadenar múltiples tools

---

## 📚 Referencias

- [PLAN_ORQUESTADOR_TOOLS.md](PLAN_ORQUESTADOR_TOOLS.md) - Plan completo
- [src/tools/](src/tools/) - Código fuente
- [tests/tools/](tests/tools/) - Tests unitarios
- [ROADMAP.md](ROADMAP.md) - Roadmap general del proyecto

---

**Última actualización:** 2025-11-27
**Versión:** 0.2.0
**Estado:** FASE 1 y FASE 2 completadas ✅
