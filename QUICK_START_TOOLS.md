# 🚀 Quick Start - Sistema de Tools

Guía rápida para probar el sistema de Tools implementado.

## ✅ Sistema Validado

El sistema de Tools ha sido probado exitosamente:
- ✅ 63/63 tests unitarios pasando (100%)
- ✅ QueryTool funciona con queries reales
- ✅ Integración con LLMAgent verificada
- ✅ Tiempo de respuesta: ~15 segundos por query

## 🎯 Opción 1: Probar con Bot de Telegram (Recomendado)

### Paso 1: Iniciar el bot

```bash
python main.py
```

**Salida esperada:**
```
INFO - Inicializando TelegramBot...
INFO - Inicializando sistema de Tools...
INFO - Tool registrado: query (comandos: ['/ia', '/query'])
INFO - Sistema de Tools inicializado correctamente
INFO - TelegramBot inicializado exitosamente con LLM provider: OpenAI
INFO - Bot iniciado. Presiona Ctrl+C para detener.
```

### Paso 2: Probar en Telegram

Envía estos comandos a tu bot:

**Query de base de datos:**
```
/ia ¿Cuántos usuarios hay registrados?
```

**Query general:**
```
/ia ¿Qué es Python?
```

**Comando alternativo:**
```
/query Dame un resumen del sistema
```

**Query sin comando (implícita):**
```
¿Qué tablas tiene la base de datos?
```

### Respuesta Esperada

```
🔍 Analizando tu consulta...
🤖 Procesando con IA...

**Resultados encontrados:** 1

total_registered_users: 30
```

---

## 📊 Opción 2: Tests Unitarios (Más Rápido)

```bash
# Tests rápidos (~1 segundo)
pytest tests/tools/ -v

# Con coverage
pytest tests/tools/ --cov=src/tools --cov-report=html
```

**Resultado esperado:**
```
===== 63 passed in 0.40s =====
```

---

## 🧪 Opción 3: Script de Prueba Manual

Para probar sin Telegram:

```bash
python test_tools_manual.py
```

**Lo que hace:**
- Inicializa el sistema de Tools
- Ejecuta QueryTool con queries reales
- Valida el ToolOrchestrator
- Verifica manejo de errores
- Muestra estadísticas

---

## 🔍 Verificar que Funciona

### Indicadores de éxito:

✅ **En los logs del bot:**
```
INFO - Sistema de Tools inicializado correctamente
INFO - Tool registrado: query (comandos: ['/ia', '/query'])
```

✅ **En Telegram:**
- Bot responde a `/ia` con queries
- Mensajes de estado aparecen (`🔍 Analizando...`)
- Respuestas bien formateadas
- Sin errores visibles

✅ **En tests:**
- 63/63 tests pasando
- Sin errores ni warnings
- Tiempo de ejecución <1 segundo

---

## 🐛 Problemas Comunes

### Error: "Comando no encontrado: /ia"

**Causa:** Tools no inicializados

**Solución:**
```python
# Verificar que telegram_bot.py tiene:
from src.tools import initialize_builtin_tools
initialize_builtin_tools()
```

### Error: "LLMAgent no disponible"

**Causa:** ExecutionContext sin LLMAgent

**Solución:** Ya está integrado en telegram_bot.py ✅

### Error: API key inválida

**Causa:** .env no configurado

**Solución:**
```bash
# Verificar .env
cat .env | grep API_KEY

# Debe tener:
OPENAI_API_KEY=sk-...
# O
ANTHROPIC_API_KEY=sk-ant-...
```

---

## 📈 Siguiente Paso

Una vez que el bot funcione correctamente:

### FASE 3: Implementar más Tools

```bash
# Crear nueva feature branch
git checkout -b feature/tools-fase3

# Implementar:
# - HelpTool (/help con sistema de Tools)
# - StatsTool (/stats con métricas)
# - RegistrationTool (/register refactorizado)
```

### Migrar handlers existentes

Reemplazar handlers tradicionales con Tools:
- command_handlers.py → HelpTool, StatsTool
- registration_handlers.py → RegistrationTool
- query_handlers.py → (Ya migrado a QueryTool) ✅

---

## 📚 Documentación Completa

- [TESTING_TOOLS.md](TESTING_TOOLS.md) - Guía completa de testing
- [PLAN_ORQUESTADOR_TOOLS.md](PLAN_ORQUESTADOR_TOOLS.md) - Plan de implementación
- [ROADMAP.md](ROADMAP.md) - Roadmap del proyecto

---

## 🎯 Estado Actual

**Versión:** 0.2.0
**FASE 1:** ✅ Completada - Fundamentos
**FASE 2:** ✅ Completada - QueryTool
**FASE 3:** ⏳ Pendiente - Más tools

**Sistema:** ✅ Funcional y testeado
**Integración:** ✅ Bot de Telegram integrado
**Tests:** ✅ 63/63 pasando

---

**¡Sistema listo para usar!** 🎉

Ejecuta `python main.py` y prueba el comando `/ia` en tu bot de Telegram.
