# Estructura del Proyecto

> **Última actualización:** 2025-10-29
> **Estado:** Refactorizado con arquitectura modular (TODO #3 completado)

---

## Árbol de Directorios

```
GPT5/
│
├── src/                        # Código fuente principal
│   ├── __init__.py
│   │
│   ├── bot/                    # Módulo del bot de Telegram
│   │   ├── __init__.py
│   │   ├── telegram_bot.py     # ✅ Clase principal del bot
│   │   ├── handlers.py         # ❌ TODO: Manejadores de comandos (separados)
│   │   └── keyboards.py        # ❌ TODO: Teclados personalizados
│   │
│   ├── agent/                  # Módulo del agente LLM
│   │   ├── __init__.py
│   │   ├── llm_agent.py        # ✅ Orquestador principal (refactorizado)
│   │   │
│   │   ├── providers/          # ✅ Proveedores de LLM (Strategy Pattern)
│   │   │   ├── __init__.py
│   │   │   ├── base_provider.py     # ✅ Interfaz abstracta (ABC)
│   │   │   ├── openai_provider.py   # ✅ Implementación OpenAI
│   │   │   └── anthropic_provider.py # ✅ Implementación Anthropic
│   │   │
│   │   ├── classifiers/        # ✅ Clasificadores de consultas
│   │   │   ├── __init__.py
│   │   │   └── query_classifier.py  # ✅ Clasifica queries (DB vs General)
│   │   │
│   │   ├── sql/                # ✅ Generación y validación de SQL
│   │   │   ├── __init__.py
│   │   │   ├── sql_generator.py     # ✅ Genera SQL desde lenguaje natural
│   │   │   └── sql_validator.py     # ✅ Validación de seguridad de SQL
│   │   │
│   │   ├── formatters/         # ✅ Formateadores de respuestas
│   │   │   ├── __init__.py
│   │   │   └── response_formatter.py # ✅ Formatea respuestas para usuario
│   │   │
│   │   └── prompts.py          # ❌ TODO: Plantillas de prompts (versionadas)
│   │
│   ├── database/               # Módulo de base de datos
│   │   ├── __init__.py
│   │   ├── connection.py       # ✅ Gestión de conexiones y pool
│   │   ├── models.py           # ❌ TODO: Modelos SQLAlchemy (14 tablas)
│   │   ├── queries.py          # ❌ TODO: Funciones de consulta (repositorio)
│   │   └── schema_analyzer.py  # ❌ TODO: Análisis inteligente del esquema
│   │
│   ├── config/                 # Configuración
│   │   ├── __init__.py
│   │   └── settings.py         # ✅ Configuración con Pydantic Settings
│   │
│   ├── auth/                   # ❌ TODO: Autenticación y autorización
│   │   ├── __init__.py
│   │   ├── user_manager.py     # ❌ TODO: Gestión de usuarios
│   │   ├── permission_checker.py # ❌ TODO: Verificación de permisos
│   │   └── registration.py     # ❌ TODO: Flujo de registro
│   │
│   └── utils/                  # Utilidades
│       ├── __init__.py
│       ├── logger.py           # ❌ TODO: Configuración de Loguru
│       └── validators.py       # ❌ TODO: Validadores de datos
│
├── tests/                      # Tests unitarios e integración
│   ├── __init__.py
│   ├── test_agent.py           # ⚠️ Solo fixtures, sin tests reales
│   ├── test_bot.py             # ❌ TODO: Tests del bot
│   └── test_database.py        # ❌ TODO: Tests de BD
│
├── docs/                       # Documentación del proyecto
│   ├── index.md                # Índice de documentación
│   ├── estructura.md           # ✅ Este archivo (actualizado)
│   ├── todos.md                # Lista de TODOs original
│   ├── todos/                  # ✅ Análisis detallado de TODOs
│   │   ├── DetalleCompleto.md  # ✅ Análisis arquitectónico completo
│   │   └── ResumenTodos.md     # ✅ Resumen ejecutivo de TODOs
│   └── sql/                    # Scripts SQL de estructura
│       ├── 00 ResumenEstructura.sql
│       ├── 01 EstructuraUsuarios.sql
│       ├── 02 EstructuraPermisos.sql
│       └── 03 EstructuraVerificacion.sql
│
├── Ejemplos/                   # Ejemplos de uso
│   ├── EjemploSimple.py
│   └── SalidaEstructurada.py
│
├── data/                       # Datos locales (no versionados)
│   └── .gitkeep
│
├── logs/                       # Archivos de log (no versionados)
│   └── .gitkeep
│
├── main.py                     # ✅ Punto de entrada de la aplicación
├── requirements.txt            # ✅ Dependencias de Python
├── Pipfile                     # ✅ Configuración Pipenv
├── Pipfile.lock
├── .env.example                # ✅ Ejemplo de variables de entorno
├── .gitignore                  # ✅ Archivos ignorados por git
└── README.md                   # Documentación principal
```

**Leyenda:**
- ✅ = Implementado y funcional
- ⚠️ = Parcialmente implementado
- ❌ = Pendiente de implementación

---

## Descripción de Componentes

### `/src/` - Código Fuente

#### `src/bot/` - Bot de Telegram
Contiene toda la lógica relacionada con la interfaz de Telegram:

**Implementado:**
- **telegram_bot.py** ✅: Clase principal que inicializa y ejecuta el bot, contiene handlers básicos

**Pendiente:**
- **handlers.py** ❌: Funciones separadas que manejan comandos (`/start`, `/help`, `/stats`) y mensajes
- **keyboards.py** ❌: Define teclados personalizados inline y reply para mejorar UX

---

#### `src/agent/` - Agente LLM (REFACTORIZADO)
Implementa la inteligencia artificial que procesa las consultas usando arquitectura modular:

**Orquestador:**
- **llm_agent.py** ✅: Núcleo del agente que coordina todos los componentes (197 líneas, reducido de 234)
  - Implementa inyección de dependencias
  - Orquesta flujo: clasificación → generación → validación → ejecución → formateo

**Proveedores LLM (Strategy Pattern):**
- **providers/base_provider.py** ✅: Interfaz abstracta (ABC) que define el contrato para todos los providers
  - Métodos: `generate()`, `generate_structured()`, `get_provider_name()`, `get_model_name()`
- **providers/openai_provider.py** ✅: Implementación para OpenAI usando Responses API
  - Soporta salida estructurada con Pydantic
- **providers/anthropic_provider.py** ✅: Implementación para Anthropic Claude
  - Emula salida estructurada con prompt engineering

**Clasificadores:**
- **classifiers/query_classifier.py** ✅: Clasifica consultas como DATABASE o GENERAL
  - Usa LLM para determinar si requiere acceso a BD
  - Enum `QueryType` para tipos de consulta

**Generación y Validación SQL:**
- **sql/sql_generator.py** ✅: Genera consultas SQL desde lenguaje natural
  - Limpia respuestas de markdown
  - Maneja casos donde no hay datos suficientes
- **sql/sql_validator.py** ✅: Validación de seguridad avanzada
  - Blacklist de keywords (DROP, DELETE, UPDATE, ALTER, etc.)
  - Detección de múltiples statements
  - Validación de comentarios sospechosos
  - Regex con word boundaries para precisión

**Formateadores:**
- **formatters/response_formatter.py** ✅: Formatea resultados para usuarios
  - Formato detallado para 1 resultado
  - Formato de lista para múltiples resultados
  - Limitación configurable de resultados mostrados
  - Manejo de valores NULL

**Pendiente:**
- **prompts.py** ❌: Sistema de plantillas de prompts con versionado (Jinja2)

---

#### `src/database/` - Base de Datos
Gestiona todas las operaciones con la base de datos:

**Implementado:**
- **connection.py** ✅: Pool de conexiones y gestión de sesiones
  - Connection pooling optimizado (pool_size=5, max_overflow=10)
  - Pool pre-ping para detectar conexiones muertas
  - Soporte multi-BD (SQLite, PostgreSQL, MySQL, SQL Server)
  - Introspección de esquema con SQLAlchemy Inspector

**Pendiente:**
- **models.py** ❌: Modelos ORM (SQLAlchemy) para 14 tablas del sistema de permisos
- **queries.py** ❌: Repositorio con funciones helper para consultas complejas
- **schema_analyzer.py** ❌: Análisis inteligente de esquema (relaciones, índices, ejemplos)

---

#### `src/config/` - Configuración
Centraliza la configuración de la aplicación:

- **settings.py** ✅: Carga variables de entorno y define configuraciones usando Pydantic Settings
  - Validación automática de tipos
  - Construcción dinámica de database_url
  - Soporte para instancias nombradas de SQL Server
  - Variables: API keys, BD, logging, environment

---

#### `src/auth/` - Autenticación y Autorización (TODO)
**Módulo completo pendiente de implementación:**

- **user_manager.py** ❌: Gestión de usuarios de Telegram
- **permission_checker.py** ❌: Verificación de permisos usando stored procedures
- **registration.py** ❌: Flujo de registro y verificación de usuarios

---

#### `src/utils/` - Utilidades
Funciones auxiliares reutilizables:

**Pendiente:**
- **logger.py** ❌: Configuración centralizada de Loguru (rotación, compresión, niveles)
- **validators.py** ❌: Validación de entradas y datos

---

### `/tests/` - Tests
Contiene pruebas unitarias y de integración:

**Estado actual:**
- **test_agent.py** ⚠️: Solo tiene fixtures, sin tests reales
- **test_bot.py** ❌: Pendiente
- **test_database.py** ❌: Pendiente

**Nota:** Existen scripts de testing de conexión a BD fuera de tests/ (test_db_connection.py, etc.)

---

### `/docs/` - Documentación
Documentación técnica y guías:

**Implementado:**
- **estructura.md** ✅: Este archivo con arquitectura actualizada
- **todos/DetalleCompleto.md** ✅: Análisis arquitectónico de 1000+ líneas
- **todos/ResumenTodos.md** ✅: Resumen ejecutivo de 14 TODOs con estados
- **sql/** ✅: 4 archivos con estructura completa de BD (14 tablas + SPs)

---

### `/data/` y `/logs/`
- **data/**: Directorio para bases de datos SQLite o archivos de cache
- **logs/**: Almacenará logs cuando se implemente Loguru

---

### Archivos Raíz

- **main.py** ✅: Punto de entrada que inicia el bot
- **requirements.txt** ✅: 13 dependencias (OpenAI, Anthropic, Telegram, SQLAlchemy, etc.)
- **Pipfile** ✅: Configuración de Pipenv para Python 3.13
- **.env.example** ✅: Plantilla con 11 variables de entorno
- **.gitignore** ✅: Excluye .env, __pycache__, logs, data
- **README.md**: Documentación general del proyecto

---

## Flujo de Datos (Actualizado)

### Flujo Completo con Arquitectura Refactorizada:

```
Usuario envía mensaje via Telegram
    ↓
[telegram_bot.py] - Recibe mensaje
    ↓
[llm_agent.py] - Orquestador principal
    ↓
[query_classifier.py] - Clasifica consulta
    ↓
    ├─→ Si es GENERAL:
    │       ↓
    │   [openai_provider.py / anthropic_provider.py]
    │       ↓
    │   [response_formatter.py]
    │       ↓
    │   Respuesta al usuario
    │
    └─→ Si es DATABASE:
            ↓
        [connection.py] - Obtiene esquema
            ↓
        [sql_generator.py] - Genera SQL
            ↓
        [sql_validator.py] - Valida seguridad
            ↓
        [connection.py] - Ejecuta query
            ↓
        [response_formatter.py] - Formatea resultados
            ↓
        Respuesta al usuario via Telegram
```

### Flujo Simplificado:

```
Usuario (Telegram)
    ↓
TelegramBot.handle_message()
    ↓
LLMAgent.process_query()
    ├─→ QueryClassifier.classify()
    │   ├─→ LLMProvider.generate()
    │
    ├─→ DatabaseManager.get_schema()
    ├─→ SQLGenerator.generate_sql()
    ├─→ SQLValidator.validate()
    ├─→ DatabaseManager.execute_query()
    └─→ ResponseFormatter.format_query_results()
    ↓
Usuario (Telegram)
```

---

## Patrones de Diseño Implementados

### 1. Strategy Pattern
**Ubicación:** `src/agent/providers/`
- Permite intercambiar entre OpenAI, Anthropic o futuros providers
- Interfaz común: `LLMProvider` (ABC)

### 2. Adapter Pattern
**Ubicación:** `src/agent/providers/`
- Adapta APIs diferentes (OpenAI Responses vs Anthropic Messages) a interfaz común

### 3. Repository Pattern (Pendiente)
**Ubicación:** `src/database/queries.py` (TODO)
- Abstracción para operaciones de BD

### 4. Dependency Injection
**Ubicación:** `src/agent/llm_agent.py`
- Constructor acepta `db_manager` y `llm_provider` opcionales
- Facilita testing con mocks

### 5. Singleton Pattern (Implícito)
**Ubicación:** `src/config/settings.py`
- Instancia global `settings` compartida

---

## Convenciones de Código

1. **Nombres de archivos**: snake_case
2. **Clases**: PascalCase
3. **Funciones y variables**: snake_case
4. **Constantes**: UPPER_CASE
5. **Imports**: Organizados en grupos (stdlib, third-party, local)
6. **Type hints**: Obligatorios en todas las funciones públicas
7. **Docstrings**: Formato Google Style para clases y métodos públicos

---

## Extensibilidad

La estructura refactorizada facilita:

### Agregar nuevo proveedor LLM:
1. Crear clase heredando de `LLMProvider`
2. Implementar métodos abstractos: `generate()`, `generate_structured()`
3. Añadir lógica en `_initialize_llm_provider()`

### Agregar nueva validación SQL:
1. Añadir keyword a `FORBIDDEN_KEYWORDS` en `sql_validator.py`
2. O crear método de validación adicional

### Agregar nuevo tipo de clasificación:
1. Extender enum `QueryType` en `query_classifier.py`
2. Actualizar lógica de clasificación

### Agregar nuevo formato de respuesta:
1. Añadir método en `response_formatter.py`
2. Llamar desde `llm_agent.py`

---

## Arquitectura de Base de Datos

El proyecto incluye un sistema completo de gestión de permisos (SQL Server):

**14 Tablas:**
- Gestión de Usuarios: `Roles`, `RolesIA`, `Usuarios`, `UsuariosTelegram`
- Gestión de Gerencias: `Gerencias`, `GerenciaUsuarios`, `AreaAtendedora`, `GerenciasRolesIA`
- Sistema de Permisos: `Modulos`, `Operaciones`, `RolesOperaciones`, `UsuariosOperaciones`, `LogOperaciones`
- Relaciones: `UsuariosRolesIA`

**Stored Procedures:**
- `sp_VerificarPermisoOperacion` - Verifica permisos antes de ejecutar
- `sp_ObtenerOperacionesUsuario` - Lista operaciones disponibles
- `sp_RegistrarLogOperacion` - Auditoría completa

**Estado:** Diseñado pero NO integrado con el código Python (TODO #2)

---

## Métricas del Proyecto

| Métrica | Valor |
|---------|-------|
| Archivos Python | 21 |
| Archivos implementados | 13 (62%) |
| Archivos pendientes | 8 (38%) |
| Líneas de código (estimado) | ~1500 |
| Cobertura de tests | ~0% |
| Dependencias | 13 |
| TODOs completados | 1/14 (7%) |
| TODOs críticos pendientes | 2 |

---

## Próximos Pasos

Según `docs/todos/ResumenTodos.md`:

### Prioridad Crítica 🔴
1. **Sistema de Autenticación/Autorización** - Crear `src/auth/`
2. **Modelos SQLAlchemy** - Crear `src/database/models.py`

### Prioridad Alta 🟠
3. ✅ **Refactorizar LLMAgent** - COMPLETADO
4. **Arquitectura de Handlers Modular** - Crear `src/bot/handlers/`
5. **Logging Estructurado** - Implementar `src/utils/logger.py`
6. **Sistema de Prompts** - Crear `src/agent/prompts.py`

---

## Referencias

- **Análisis completo:** `docs/todos/DetalleCompleto.md`
- **Resumen de TODOs:** `docs/todos/ResumenTodos.md`
- **Schema SQL:** `docs/sql/00 ResumenEstructura.sql`
- **Configuración:** `.env.example`

---

**Generado:** 2025-10-29
**Versión del proyecto:** 0.2.0-alpha (post-refactoring)
**Estado:** En desarrollo activo
