# 📋 Iris Bot - Retry con Backoff Exponencial

## 📝 Descripcion
Implementacion de mecanismo de retry automatico con backoff exponencial para proteger las llamadas a OpenAI API y base de datos contra errores transitorios. Utiliza la libreria `tenacity` (v9.0.0) que ya estaba instalada pero no se usaba.

## 🏷️ Tipo de Proyecto
- Desarrollo
- Bot/Automatizacion

## 📊 Status
- [x] ⚙️ En proceso

## 📈 Avance
- Tareas completadas / Total tareas: 12 / 14
- Porcentaje: 86%

## 📅 Cronologia
- **Semana de inicio**: Semana 8 - 16/02/2026
- **Semana de fin**: En curso
- **Deadline critico**: N/A

## 👥 Solicitantes

| Nombre | Correo | Area | Extension/Celular |
|--------|--------|------|-------------------|
| Angel | [correo@ejemplo.com] | Desarrollo | N/A |

## 👨‍💻 Recursos Asignados

**Admin:**
- Angel - Tech Lead

**Desarrollo:**
- Claude - Asistente IA / Desarrollo

## 🔧 Actividades

### ✅ Realizadas

**Fase 1 - Retry en LLM providers (5/5 completada):**
- ✔️ **Crear retry helper**: `src/utils/retry.py` con decoradores `llm_retry()` y `db_retry()` reutilizables
- ✔️ **Proteger OpenAI provider**: `@llm_retry` en `generate()` y `generate_structured()`
- ✔️ **Proteger Anthropic provider**: `@llm_retry` en `generate()` y `generate_structured()`
- ✔️ **Proteger ReActAgent**: Retry aplicado via OpenAI provider (capa mas baja)
- ✔️ **Agregar logging de retry**: `before_sleep_log` con WARNING en cada reintento

**Fase 2 - Retry en base de datos (5/5 completada):**
- ✔️ **Proteger execute_query()**: `@db_retry` en `src/database/connection.py`
- ✔️ **Proteger execute_non_query()**: `@db_retry` en `src/database/connection.py`
- ✔️ **Proteger get_schema()**: `@db_retry` en `src/database/connection.py`
- ✔️ **Verificar MemoryRepository**: Sin doble retry - retry solo en capa de connection.py
- ✔️ **Configuracion por entorno**: 6 variables en `settings.py` para max_attempts, min/max_wait

**Fase 3 - Tests y validacion (2/4 en progreso):**
- ✔️ **Tests unitarios**: `tests/utils/test_retry.py` - 12/12 tests pasando
- ✔️ **Tests integracion LLM**: Mock OpenAI con RateLimitError, verificada recuperacion

### 📋 Por hacer
- ⏳ **Tests integracion BD**: Mock session con OperationalError, verificar retry
- ⏳ **Validacion manual**: Probar bot real, verificar logs de retry

## ⚠️ Impedimentos y Deadlines

### 🚧 Bloqueadores Activos
N/A - No hay bloqueadores activos

## 📦 Entregables
- [x] 📖 **Plan de retry**: [PLAN_RETRY_RESILIENCE.md](../../plan/02-activos/PLAN_RETRY_RESILIENCE.md)
- [x] 📓 **OneNote actualizado**: Este documento
- [x] 🔧 **Modulo de retry**: `src/utils/retry.py`
- [x] 🧪 **Tests de retry**: `tests/utils/test_retry.py` (12 tests pasando)

## 🔗 URLs

### 📊 Repositorio
- [GitHub - TelegramBotIA](https://github.com/Roque98/TelegramBotIA)

### 🖥️ Ramas Git
- `feature/react-fase6-polish` - Rama donde se implemento

### 📝 Commits Relevantes
| Commit | Descripcion | Fecha |
|--------|-------------|-------|
| `98b427f` | feat(resilience): implement retry with exponential backoff using tenacity | 16/02/2026 |

## 🔧 Informacion Tecnica

### 💻 Cobertura de Retry

| Componente | Archivo | Errores Transitorios | Retry |
|------------|---------|----------------------|-------|
| OpenAI Provider | `src/agent/providers/openai_provider.py` | RateLimitError, APIConnectionError, Timeout | ✅ |
| Anthropic Provider | `src/agent/providers/anthropic_provider.py` | RateLimitError, APIConnectionError, Timeout | ✅ |
| DB execute_query | `src/database/connection.py` | OperationalError, TimeoutError | ✅ |
| DB execute_non_query | `src/database/connection.py` | OperationalError, TimeoutError | ✅ |
| DB get_schema | `src/database/connection.py` | OperationalError, TimeoutError | ✅ |

### 💻 Archivos Creados/Modificados

```
src/utils/retry.py                          # NUEVO - Decoradores llm_retry() y db_retry()
src/config/settings.py                      # MODIFICADO - 6 settings de retry
src/agent/providers/openai_provider.py      # MODIFICADO - @llm_retry en generate()
src/agent/providers/anthropic_provider.py   # MODIFICADO - @llm_retry en generate()
src/database/connection.py                  # MODIFICADO - @db_retry en 3 metodos
tests/utils/test_retry.py                   # NUEVO - 12 tests
```

### 💻 Estrategia de Retry

```python
# LLM calls: 3 intentos, espera 2s -> 4s -> 8s (max 30s)
@llm_retry(max_attempts=3, min_wait=2, max_wait=30)

# Database calls: 3 intentos, espera 1s -> 2s -> 4s (max 15s)
@db_retry(max_attempts=3, min_wait=1, max_wait=15)
```

### 💻 Configuracion en settings.py
```python
retry_llm_max_attempts: int = 3
retry_llm_min_wait: int = 2      # segundos
retry_llm_max_wait: int = 30     # segundos
retry_db_max_attempts: int = 3
retry_db_min_wait: int = 1       # segundos
retry_db_max_wait: int = 15      # segundos
```

### 🧪 Tests
| Suite | Tests | Estado |
|-------|-------|--------|
| TestLLMRetry | 6/6 | ✅ Pasando |
| TestDBRetry | 6/6 | ✅ Pasando |
| **Total** | **12/12** | ✅ **100%** |

### 🗄️ Dependencias
- `tenacity==9.0.0` (ya estaba instalada)

### 🖥️ Servidores/Deploy
- **Ambiente**: DEV
- **Servidor**: Local
- **Ruta**: D:\proyectos\gs\GPT5

## 📋 Ordenes de Cambio

| OC | Descripcion | Status | Fecha |
|----|-------------|--------|-------|
| N/A | Sin OCs registradas | - | - |

---

*Documento generado: 16/02/2026*
*Ultima actualizacion: 16/02/2026*
