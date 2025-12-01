# Guía Completa del Desarrollador - Bot Telegram IA

**Versión del Proyecto:** v0.3.0
**Última Actualización:** 2025-11-30
**Rama Actual:** develop

---

## Tabla de Contenidos

1. [Introducción](#1-introducción)
2. [Arquitectura del Proyecto](#2-arquitectura-del-proyecto)
3. [Estructura de Directorios](#3-estructura-de-directorios)
4. [Stack Tecnológico](#4-stack-tecnológico)
5. [Configuración del Entorno](#5-configuración-del-entorno)
6. [Componentes Principales](#6-componentes-principales)
7. [Flujos de Ejecución](#7-flujos-de-ejecución)
8. [Sistema de Tools](#8-sistema-de-tools)
9. [Base de Conocimiento](#9-base-de-conocimiento)
10. [Base de Datos](#10-base-de-datos)
11. [Patrones de Diseño](#11-patrones-de-diseño)
12. [Testing](#12-testing)
13. [GitFlow y Versionado](#13-gitflow-y-versionado)
14. [Guía de Contribución](#14-guía-de-contribución)
15. [Troubleshooting](#15-troubleshooting)
16. [Roadmap y Próximos Pasos](#16-roadmap-y-próximos-pasos)

---

## 1. Introducción

### 1.1 ¿Qué es este proyecto?

Bot de Telegram con capacidades de agente de IA que funciona como asistente inteligente para:

- **Consultas a Base de Datos en Lenguaje Natural**: Los usuarios pueden hacer preguntas en español que se traducen automáticamente a SQL y se ejecutan de forma segura.
- **Base de Conocimiento Empresarial**: Sistema de búsqueda semántica sobre políticas, procesos y procedimientos de la empresa.
- **Sistema Extensible de Tools**: Arquitectura modular que permite agregar nuevas capacidades fácilmente.

### 1.2 Características Principales

- Interfaz conversacional mediante Telegram
- Soporte para múltiples proveedores de LLM (OpenAI, Anthropic)
- Generación y validación segura de SQL
- Sistema de prompts versionado con A/B testing
- Arquitectura basada en patrones de diseño (Strategy, Singleton, Factory, etc.)
- Modular y extensible
- Logging centralizado
- Autenticación y middleware

### 1.3 Casos de Uso

```
Usuario: /ia ¿Cuántas ventas hay del producto Laptop?
Bot: Encontré 15 ventas del producto Laptop

Usuario: /ia ¿Cómo solicito vacaciones?
Bot: Para solicitar vacaciones, debes...

Usuario: /ia ¿Qué tablas hay en la base de datos?
Bot: La base de datos contiene las siguientes tablas:
- Ventas
- Productos
- Clientes
...
```

---

## 2. Arquitectura del Proyecto

### 2.1 Vista General

```
┌─────────────────────────────────────────────┐
│          Usuario Telegram                    │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│     Bot de Telegram (python-telegram-bot)   │
│  - Command Handlers                          │
│  - Query Handlers                            │
│  - Registration Handlers                     │
│  - Middleware (Auth, Logging)                │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│      Tool Orchestrator                       │
│  - Selección de Tool                         │
│  - Validación de parámetros                  │
│  - Ejecución de Tools                        │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│      LLM Agent (Orquestador Principal)       │
│  - Clasificación de Consultas                │
│  - Generación de SQL                         │
│  - Búsqueda en Knowledge Base                │
│  - Formateo de Respuestas                    │
└───┬─────────────┬────────────────┬──────────┘
    │             │                │
┌───▼───┐   ┌─────▼─────┐   ┌──────▼──────┐
│ OpenAI│   │ Anthropic │   │  Knowledge  │
│Provider│   │  Provider │   │   Manager   │
└───────┘   └───────────┘   └──────┬──────┘
                                   │
                            ┌──────▼──────┐
                            │  Knowledge  │
                            │ Repository  │
                            └──────┬──────┘
                                   │
                            ┌──────▼──────┐
                            │  Base de    │
                            │   Datos     │
                            └─────────────┘
```

### 2.2 Arquitectura en Capas

| Capa | Responsabilidad | Componentes |
|------|-----------------|-------------|
| **Presentación** | Interfaz con usuario | TelegramBot, Handlers, Keyboards |
| **Aplicación** | Lógica de negocio | ToolOrchestrator, LLMAgent |
| **Dominio** | Entidades y reglas | Tools, Providers, Knowledge |
| **Infraestructura** | Acceso a datos | DatabaseManager, KnowledgeRepository |
| **Configuración** | Settings globales | Settings (Pydantic) |

### 2.3 Flujo de Datos Simplificado

```
Mensaje Usuario → Handler → Tool Orchestrator → Tool (QueryTool)
                                                    ↓
                                               LLM Agent
                                                    ↓
                                    ┌───────────────┼───────────────┐
                                    ▼               ▼               ▼
                              Clasificador    SQL Generator   Knowledge Manager
                                    ↓               ↓               ↓
                              QueryType        SQL Query      Knowledge Entry
                                    ↓               ↓               ↓
                              Router          Validator       Response
                                    ↓               ↓
                              Execute         Database
                                    ↓               ↓
                              Response Formatter ←─┘
                                    ↓
                              Usuario Telegram
```

---

## 3. Estructura de Directorios

```
D:\proyectos\gs\AgenteCodigoAutomatico\GPT5/
│
├── src/                              # Código fuente (3,727 líneas Python)
│   ├── agent/                        # Módulo de IA/LLM
│   │   ├── llm_agent.py              # Orquestador principal
│   │   ├── providers/                # Proveedores de LLM
│   │   │   ├── base_provider.py      # Interfaz abstracta
│   │   │   ├── openai_provider.py    # Implementación OpenAI
│   │   │   └── anthropic_provider.py # Implementación Anthropic
│   │   ├── classifiers/              # Clasificación de consultas
│   │   │   └── query_classifier.py
│   │   ├── knowledge/                # Sistema de conocimiento
│   │   │   ├── knowledge_manager.py
│   │   │   ├── knowledge_repository.py
│   │   │   ├── company_knowledge.py
│   │   │   └── knowledge_categories.py
│   │   ├── sql/                      # Generación SQL
│   │   │   ├── sql_generator.py
│   │   │   └── sql_validator.py
│   │   ├── formatters/               # Formateo de respuestas
│   │   │   └── response_formatter.py
│   │   └── prompts/                  # Sistema de prompts
│   │       ├── prompt_manager.py
│   │       └── prompt_templates.py
│   │
│   ├── bot/                          # Módulo de Telegram
│   │   ├── telegram_bot.py           # Clase principal
│   │   ├── handlers/                 # Manejadores de eventos
│   │   │   ├── command_handlers.py
│   │   │   ├── query_handlers.py
│   │   │   ├── registration_handlers.py
│   │   │   ├── tools_handlers.py
│   │   │   └── universal_handler.py
│   │   ├── keyboards/                # Teclados personalizados
│   │   │   ├── main_keyboard.py
│   │   │   └── inline_keyboards.py
│   │   └── middleware/               # Middleware
│   │       ├── auth_middleware.py
│   │       └── logging_middleware.py
│   │
│   ├── tools/                        # Sistema de Tools
│   │   ├── tool_base.py              # Clases base
│   │   ├── tool_registry.py          # Registro (Singleton)
│   │   ├── tool_orchestrator.py      # Orquestador
│   │   ├── execution_context.py      # Contexto de ejecución
│   │   ├── tool_initializer.py       # Inicializador
│   │   └── builtin/                  # Tools incorporados
│   │       └── query_tool.py
│   │
│   ├── orchestrator/                 # Orquestación avanzada
│   │   └── tool_selector.py          # Selección con LLM
│   │
│   ├── database/                     # Base de datos
│   │   ├── connection.py             # Gestor de conexiones
│   │   └── migrations/               # Migraciones
│   │
│   ├── auth/                         # Autenticación
│   │   ├── user_manager.py
│   │   ├── permission_checker.py
│   │   └── registration.py
│   │
│   ├── config/                       # Configuración
│   │   └── settings.py               # Pydantic Settings
│   │
│   └── utils/                        # Utilidades
│       ├── status_message.py
│       └── logger.py
│
├── tests/                            # Testing
│   ├── agent/
│   ├── handlers/
│   ├── orchestrator/
│   └── tools/
│
├── docs/                             # Documentación
│   ├── estructura.md
│   ├── prompts/
│   ├── sql/
│   └── guia del desarrollador/       # Guías HTML
│
├── database/                         # Archivos de BD
│   └── migrations/
│
├── Ejemplos/                         # Ejemplos de uso
│
├── main.py                           # Punto de entrada
├── requirements.txt                  # Dependencias
├── Pipfile / Pipfile.lock           # Configuración Pipenv
├── .env.example                      # Template de variables
├── .gitignore
├── README.md
│
└── Documentos de Planificación
    ├── DIAGRAMA_FLUJO_ACTUAL.md
    ├── GITFLOW.md
    ├── COMMIT_GUIDELINES.md
    ├── PENDIENTES.md
    ├── ROADMAP.md
    ├── QUICK_START_TOOLS.md
    ├── TESTING_TOOLS.md
    ├── PLAN_ORQUESTADOR_TOOLS.md
    └── PLAN_KNOWLEDGE_BASE_RAG.md
```

---

## 4. Stack Tecnológico

### 4.1 Tecnologías Core

| Categoría | Tecnología | Versión | Propósito |
|-----------|-----------|---------|----------|
| **Lenguaje** | Python | 3.9+ | Lenguaje base |
| **Bot Framework** | python-telegram-bot | 21.7 | Interfaz con Telegram |
| **LLM - OpenAI** | openai | 2.6.1 | GPT-5-nano |
| **LLM - Anthropic** | anthropic | 0.39.0 | Claude |
| **LLM Framework** | LangChain | 0.3.7 | Orquestación |
| **ORM** | SQLAlchemy | 2.0.0+ | Manejo de BD |
| **DB Driver** | pyodbc | 5.2.0 | SQL Server |
| **Validación** | Pydantic | 2.10.2 | Settings y schemas |
| **Config** | python-dotenv | 1.0.1 | Variables de entorno |
| **Logging** | Loguru | 0.7.3 | Logging avanzado |
| **Async** | nest-asyncio | 1.6.0 | Event loops anidados |
| **Retry** | tenacity | 9.0.0 | Reintentos automáticos |
| **Templates** | Jinja2 | 3.1.0+ | Plantillas de prompts |

### 4.2 Bases de Datos Soportadas

- **SQL Server** (Principal)
- PostgreSQL
- MySQL
- SQLite

### 4.3 Características Técnicas

- **Async/Await**: Soporte completo para operaciones asincrónicas
- **Connection Pool**: 5 conexiones base + 10 adicionales
- **Type Hints**: Tipado completo en Python
- **Dependency Injection**: Inyección en componentes
- **Environment-based Config**: .env para configuración

---

## 5. Configuración del Entorno

### 5.1 Instalación Inicial

```bash
# 1. Clonar el repositorio
git clone https://github.com/Roque98/TelegramBotIA.git
cd TelegramBotIA

# 2. Checkout a develop
git checkout develop
git pull origin develop

# 3. Crear entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# Alternativa con Pipenv
pipenv install
pipenv shell
```

### 5.2 Configuración de Variables de Entorno

Crear archivo `.env` desde `.env.example`:

```bash
cp .env.example .env
```

Contenido de `.env`:

```ini
# ============================================
# LLM APIs
# ============================================
OPENAI_MODEL=gpt-5-nano-2025-08-07
OPENAI_API_KEY=sk-...

ANTHROPIC_API_KEY=sk-ant-...

# ============================================
# Telegram
# ============================================
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# ============================================
# Base de Datos
# ============================================
DB_HOST=localhost
DB_PORT=1433
DB_INSTANCE=SQLEXPRESS          # Para SQL Server con instancia nombrada
DB_NAME=abcmasplus
DB_USER=usuario
DB_PASSWORD=contraseña
DB_TYPE=mssql                   # Opciones: mssql, sqlserver, postgresql, mysql, sqlite

# ============================================
# Aplicación
# ============================================
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR, CRITICAL
ENVIRONMENT=development         # development, staging, production
```

### 5.3 Verificar Configuración

```bash
# Test de carga de variables
python test_env_loading.py

# Test de conexión a BD
python test_db_connection.py
python test_db_final.py

# Verificar configuración completa
python check_config.py
```

### 5.4 Ejecutar el Bot

```bash
# Ejecutar
python main.py

# Salida esperada:
# INFO - Inicializando TelegramBot...
# INFO - Inicializando sistema de Tools...
# INFO - Tool registrado: query (comandos: ['/ia', '/query'])
# INFO - Sistema de Tools inicializado correctamente
# INFO - TelegramBot inicializado exitosamente con LLM provider: OpenAI
# INFO - Bot iniciado y esperando mensajes...
```

---

## 6. Componentes Principales

### 6.1 LLMAgent (src/agent/llm_agent.py)

**Orquestador principal del sistema.**

#### Responsabilidades

- Clasificar consultas (DATABASE, KNOWLEDGE, GENERAL)
- Procesar consultas de base de datos
- Buscar en la base de conocimiento
- Generar respuestas generales
- Coordinar providers de LLM

#### Métodos Principales

```python
class LLMAgent:
    async def process_query(self, query: str) -> str:
        """Procesa una consulta completa."""

    async def _process_database_query(self, query: str) -> str:
        """Procesa consultas de base de datos."""

    async def _process_knowledge_query(self, query: str, matches: List) -> str:
        """Procesa consultas de conocimiento."""

    async def _process_general_query(self, query: str) -> str:
        """Procesa consultas generales."""
```

#### Ejemplo de Uso

```python
from src.agent.llm_agent import LLMAgent
from src.agent.providers.openai_provider import OpenAIProvider
from src.database.connection import DatabaseManager
from src.config.settings import Settings

settings = Settings()
provider = OpenAIProvider(settings)
db_manager = DatabaseManager(settings)
agent = LLMAgent(provider, db_manager)

response = await agent.process_query("¿Cuántas ventas hay?")
```

### 6.2 Proveedores de LLM (src/agent/providers/)

**Strategy Pattern para intercambiar LLMs.**

#### BaseProvider (Interfaz)

```python
from abc import ABC, abstractmethod

class BaseProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Genera texto."""
        pass

    @abstractmethod
    async def generate_structured(self, prompt: str, response_model: Type[T]) -> T:
        """Genera salida estructurada con Pydantic."""
        pass
```

#### OpenAIProvider

```python
class OpenAIProvider(BaseProvider):
    def __init__(self, settings: Settings):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def generate(self, prompt: str, max_tokens: int = 500) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
```

#### Cambiar de Provider

```python
# En main.py o donde se inicializa

# Opción 1: OpenAI
from src.agent.providers.openai_provider import OpenAIProvider
provider = OpenAIProvider(settings)

# Opción 2: Anthropic
from src.agent.providers.anthropic_provider import AnthropicProvider
provider = AnthropicProvider(settings)

# Usar el mismo código
agent = LLMAgent(provider, db_manager)
```

### 6.3 Sistema de Prompts (src/agent/prompts/)

#### PromptTemplates (Versionado)

```python
from src.agent.prompts.prompt_templates import PromptTemplates

# Obtener versión específica
prompt = PromptTemplates.SQL_GENERATION_V2

# Obtener última versión
prompt = PromptTemplates.SQL_GENERATION_LATEST
```

#### PromptManager (A/B Testing)

```python
from src.agent.prompts.prompt_manager import PromptManager, ABTestConfig

# Configurar A/B testing
ab_config = ABTestConfig(
    enabled=True,
    variants={1: 0.3, 2: 0.5, 3: 0.2},  # Pesos de distribución
    strategy='weighted'  # random, weighted, round_robin
)

manager = PromptManager(ab_config=ab_config)

# Obtener prompt (con A/B testing)
prompt = manager.get_prompt("SQL_GENERATION")

# Renderizar con contexto
rendered = manager.render_prompt(prompt, {"schema": "..."})
```

### 6.4 Clasificador de Consultas (src/agent/classifiers/query_classifier.py)

**Clasifica consultas en tres categorías.**

```python
from enum import Enum

class QueryType(Enum):
    DATABASE = "database"      # Consultas a BD
    KNOWLEDGE = "knowledge"    # Información empresarial
    GENERAL = "general"        # Respuestas generales
```

```python
from src.agent.classifiers.query_classifier import QueryClassifier

classifier = QueryClassifier(llm_provider, knowledge_manager)

# Clasificar
query_type, matches = await classifier.classify_query("¿Cuántas ventas hay?")

if query_type == QueryType.DATABASE:
    # Procesar como consulta SQL
    ...
elif query_type == QueryType.KNOWLEDGE:
    # Buscar en knowledge base
    ...
else:
    # Respuesta general
    ...
```

### 6.5 Generador SQL (src/agent/sql/sql_generator.py)

```python
from src.agent.sql.sql_generator import SQLGenerator

generator = SQLGenerator(llm_provider)

sql_query = await generator.generate_sql(
    user_query="¿Cuántas ventas hay?",
    schema="CREATE TABLE Ventas (id INT, producto VARCHAR, cantidad INT)"
)

# Resultado: "SELECT COUNT(*) FROM Ventas"
```

### 6.6 Validador SQL (src/agent/sql/sql_validator.py)

**Seguridad contra inyecciones SQL.**

```python
from src.agent.sql.sql_validator import SQLValidator

validator = SQLValidator()

# Validar query
is_valid = validator.validate(sql_query)

if not is_valid:
    raise ValueError("SQL query no permitido")
```

**Reglas de Validación:**

- Solo permite `SELECT`
- Blacklist: `DROP`, `DELETE`, `INSERT`, `UPDATE`, `TRUNCATE`, `ALTER`, `CREATE`, `EXEC`, `EXECUTE`
- Previene comentarios SQL (`--`, `/*`)

### 6.7 Formateador de Respuestas (src/agent/formatters/response_formatter.py)

```python
from src.agent.formatters.response_formatter import ResponseFormatter

formatter = ResponseFormatter(llm_provider)

# Formatear resultados
formatted = await formatter.format_results(
    query="¿Cuántas ventas hay?",
    results=[(15,)],
    max_results=10
)

# Resultado: "Encontré 15 ventas en total."
```

---

## 7. Flujos de Ejecución

### 7.1 Flujo Completo de una Consulta `/ia`

```
Usuario: /ia ¿Cuántas ventas del producto Laptop?
    ↓
┌───────────────────────────────────────────────┐
│ TelegramBot recibe mensaje                    │
└───────────────┬───────────────────────────────┘
                ↓
┌───────────────────────────────────────────────┐
│ Handler: tools_handlers.py                    │
│ - Extrae comando y parámetros                 │
└───────────────┬───────────────────────────────┘
                ↓
┌───────────────────────────────────────────────┐
│ ToolOrchestrator                              │
│ - Obtiene QueryTool del Registry              │
│ - Construye ExecutionContext                  │
│ - Valida parámetros                           │
└───────────────┬───────────────────────────────┘
                ↓
┌───────────────────────────────────────────────┐
│ QueryTool.execute()                           │
│ - Envía mensaje de estado: "Analizando..."   │
└───────────────┬───────────────────────────────┘
                ↓
┌───────────────────────────────────────────────┐
│ LLMAgent.process_query()                      │
└───────────────┬───────────────────────────────┘
                ↓
┌───────────────────────────────────────────────┐
│ QueryClassifier.classify_query()              │
│ - Busca primero en Knowledge Base             │
│ - Si no hay match, clasifica con LLM          │
│ → Resultado: QueryType.DATABASE               │
└───────────────┬───────────────────────────────┘
                ↓
┌───────────────────────────────────────────────┐
│ LLMAgent._process_database_query()            │
│ - Mensaje: "Generando consulta SQL..."        │
└───────────────┬───────────────────────────────┘
                ↓
┌───────────────────────────────────────────────┐
│ SQLGenerator.generate_sql()                   │
│ - Obtiene schema de BD                        │
│ - Genera prompt con PromptManager             │
│ - LLM genera SQL                              │
│ - Limpia respuesta (remueve markdown)         │
│ → SELECT COUNT(*) FROM Ventas                 │
│    WHERE product_name='Laptop'                │
└───────────────┬───────────────────────────────┘
                ↓
┌───────────────────────────────────────────────┐
│ SQLValidator.validate()                       │
│ - Verifica que sea SELECT                     │
│ - Verifica blacklist (no DROP, DELETE, etc)   │
│ → Validación OK                               │
└───────────────┬───────────────────────────────┘
                ↓
┌───────────────────────────────────────────────┐
│ DatabaseManager.execute_query()               │
│ - Mensaje: "Ejecutando consulta..."           │
│ - Obtiene sesión del pool                     │
│ - Ejecuta SQL                                 │
│ → Resultados: [(15,)]                         │
└───────────────┬───────────────────────────────┘
                ↓
┌───────────────────────────────────────────────┐
│ ResponseFormatter.format_results()            │
│ - Mensaje: "Formateando respuesta..."         │
│ - LLM resume resultados en lenguaje natural   │
│ → "Encontré 15 ventas del producto Laptop"   │
└───────────────┬───────────────────────────────┘
                ↓
┌───────────────────────────────────────────────┐
│ Respuesta al Usuario                          │
└───────────────────────────────────────────────┘
```

### 7.2 Flujo de Consulta de Conocimiento

```
Usuario: /ia ¿Cómo solicito vacaciones?
    ↓
QueryClassifier.classify_query()
    ↓
KnowledgeManager.search("¿Cómo solicito vacaciones?")
    ↓
┌───────────────────────────────────────────────┐
│ Algoritmo de Scoring:                         │
│ - Keywords: +3 puntos por match               │
│ - Prioridad: entrada.priority                 │
│ - Similitud: cosine_similarity(query, entry)  │
│ → Score total = keywords + priority + sim     │
└───────────────┬───────────────────────────────┘
                ↓
KnowledgeRepository.load_entries()
    ↓
┌───────────────────────────────────────────────┐
│ Lee de Base de Datos:                         │
│ - knowledge_categories                        │
│ - knowledge_entries                           │
│ Fallback a código si error                    │
└───────────────┬───────────────────────────────┘
                ↓
Retorna matches ordenados por score
    ↓
LLMAgent._process_knowledge_query()
    ↓
Genera respuesta contextual con LLM
    ↓
Usuario recibe respuesta
```

### 7.3 Flujo de Inicialización del Bot

```
main.py
    ↓
┌───────────────────────────────────────────────┐
│ Settings.load()                               │
│ - Lee .env                                    │
│ - Valida con Pydantic                         │
└───────────────┬───────────────────────────────┘
                ↓
┌───────────────────────────────────────────────┐
│ DatabaseManager.init()                        │
│ - Crea connection pool                        │
│ - Configura SQLAlchemy                        │
└───────────────┬───────────────────────────────┘
                ↓
┌───────────────────────────────────────────────┐
│ Provider.init()                               │
│ - OpenAIProvider o AnthropicProvider          │
└───────────────┬───────────────────────────────┘
                ↓
┌───────────────────────────────────────────────┐
│ LLMAgent.init()                               │
│ - Inyecta provider y db_manager               │
└───────────────┬───────────────────────────────┘
                ↓
┌───────────────────────────────────────────────┐
│ ToolInitializer.initialize()                  │
│ - Instancia QueryTool                         │
│ - Registra en ToolRegistry                    │
└───────────────┬───────────────────────────────┘
                ↓
┌───────────────────────────────────────────────┐
│ TelegramBot.init()                            │
│ - Configura Application                       │
│ - Añade handlers                              │
│ - Configura middleware                        │
│ - Inyecta dependencias en bot_data            │
└───────────────┬───────────────────────────────┘
                ↓
┌───────────────────────────────────────────────┐
│ Application.run_polling()                     │
│ - Bot activo esperando mensajes               │
└───────────────────────────────────────────────┘
```

---

## 8. Sistema de Tools

### 8.1 Conceptos Clave

**Tool**: Capacidad o funcionalidad que el bot puede ejecutar (consultar BD, buscar ayuda, estadísticas, etc.)

**ToolRegistry**: Singleton que mantiene registro centralizado de todos los tools.

**ToolOrchestrator**: Orquesta la ejecución de tools, valida parámetros y gestiona contexto.

**ExecutionContext**: Contexto de ejecución que contiene usuario, mensaje, dependencias.

### 8.2 Arquitectura de Tools

```
┌─────────────────────────────────────────────┐
│           BaseTool (ABC)                    │
│  - execute(context)                         │
│  - get_info()                               │
│  - validate_parameters(params)              │
└─────────────────┬───────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼─────────┐  ┌──────▼──────┐
│   QueryTool     │  │  HelpTool   │  ... (Más tools)
│   /ia, /query   │  │  /help      │
└─────────────────┘  └─────────────┘
```

### 8.3 Crear un Nuevo Tool

#### Paso 1: Definir el Tool

```python
# src/tools/builtin/help_tool.py
from src.tools.tool_base import BaseTool, ToolInfo, ToolCategory, ToolParameter, ParameterType
from src.tools.execution_context import ExecutionContext

class HelpTool(BaseTool):
    """Tool para mostrar ayuda de comandos."""

    def get_info(self) -> ToolInfo:
        return ToolInfo(
            name="help",
            description="Muestra información de ayuda sobre comandos disponibles",
            category=ToolCategory.SYSTEM,
            commands=["/help", "/ayuda"],
            parameters=[
                ToolParameter(
                    name="topic",
                    description="Tema de ayuda (opcional)",
                    param_type=ParameterType.STRING,
                    required=False
                )
            ]
        )

    async def execute(self, context: ExecutionContext) -> str:
        """Ejecuta el tool de ayuda."""
        topic = context.parameters.get("topic")

        if topic:
            # Ayuda específica
            return f"Ayuda sobre: {topic}"
        else:
            # Ayuda general
            return "Comandos disponibles:\n/ia - Consultar base de datos\n/help - Ayuda"
```

#### Paso 2: Registrar el Tool

```python
# src/tools/tool_initializer.py
from src.tools.builtin.help_tool import HelpTool

def initialize_tools(registry: ToolRegistry, agent: LLMAgent, db_manager: DatabaseManager):
    """Inicializa y registra todos los tools."""

    # QueryTool
    query_tool = QueryTool()
    registry.register_tool(query_tool)

    # HelpTool
    help_tool = HelpTool()
    registry.register_tool(help_tool)

    logger.info("Sistema de Tools inicializado")
```

#### Paso 3: Configurar Handler (Opcional)

Si usa comando específico, ya está manejado por `universal_handler.py`.

Si necesita lógica especial, crear handler específico:

```python
# src/bot/handlers/help_handler.py
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para /help."""
    orchestrator = context.bot_data["tool_orchestrator"]

    exec_context = ExecutionContextBuilder() \
        .with_user(update.effective_user) \
        .with_message(update.message) \
        .with_parameters({"topic": None}) \
        .build()

    result = await orchestrator.execute_tool("help", exec_context)
    await update.message.reply_text(result)
```

### 8.4 QueryTool (Ejemplo Completo)

```python
# src/tools/builtin/query_tool.py
class QueryTool(BaseTool):
    """Tool para consultas de base de datos en lenguaje natural."""

    def get_info(self) -> ToolInfo:
        return ToolInfo(
            name="query",
            description="Consultar base de datos en lenguaje natural",
            category=ToolCategory.DATABASE,
            commands=["/ia", "/query"],
            parameters=[
                ToolParameter(
                    name="user_input",
                    description="Consulta en lenguaje natural",
                    param_type=ParameterType.STRING,
                    required=True
                )
            ]
        )

    async def execute(self, context: ExecutionContext) -> str:
        """Ejecuta consulta de base de datos."""
        user_input = context.parameters["user_input"]
        agent = context.get_dependency("agent")

        # Enviar mensajes de estado
        status_msg = await context.message.reply_text("🔍 Analizando tu consulta...")

        try:
            # Procesar con LLMAgent
            result = await agent.process_query(user_input)

            # Actualizar mensaje de estado
            await status_msg.edit_text("✅ Consulta procesada")

            return result
        except Exception as e:
            await status_msg.edit_text("❌ Error al procesar")
            raise
```

---

## 9. Base de Conocimiento

### 9.1 Arquitectura

```
┌─────────────────────────────────────────────┐
│        KnowledgeManager                     │
│  - search(query)                            │
│  - get_all_entries()                        │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│      KnowledgeRepository                    │
│  - load_entries()                           │
│  - fallback a company_knowledge.py          │
└─────────────────┬───────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼─────────┐  ┌──────▼──────────────┐
│  Base de Datos  │  │  Código (Fallback)  │
│  - categories   │  │  COMPANY_KNOWLEDGE  │
│  - entries      │  │  (24 entradas)      │
└─────────────────┘  └─────────────────────┘
```

### 9.2 Entidades

```python
from dataclasses import dataclass
from typing import List

@dataclass
class KnowledgeCategory:
    """Categoría de conocimiento."""
    id: int
    name: str
    description: str

@dataclass
class KnowledgeEntry:
    """Entrada de conocimiento."""
    question: str
    answer: str
    category: str
    keywords: List[str]
    priority: int = 1  # 1-5, mayor = más importante
```

### 9.3 Agregar Nueva Entrada de Conocimiento

#### Opción 1: Agregar a Base de Datos

```sql
-- 1. Crear categoría si no existe
INSERT INTO knowledge_categories (name, description)
VALUES ('Recursos Humanos', 'Políticas y procesos de RRHH');

-- 2. Agregar entrada
INSERT INTO knowledge_entries (
    question,
    answer,
    category_id,
    keywords,
    priority
)
VALUES (
    '¿Cómo solicito un día libre?',
    'Para solicitar un día libre: 1. Ingresar al sistema...',
    (SELECT id FROM knowledge_categories WHERE name = 'Recursos Humanos'),
    'dia libre,solicitud,permiso',
    3
);
```

#### Opción 2: Agregar al Fallback (Código)

```python
# src/agent/knowledge/company_knowledge.py
COMPANY_KNOWLEDGE = [
    KnowledgeEntry(
        question="¿Cómo solicito un día libre?",
        answer="Para solicitar un día libre: 1. Ingresar al sistema...",
        category="recursos_humanos",
        keywords=["dia libre", "solicitud", "permiso"],
        priority=3
    ),
    # ... más entradas
]
```

### 9.4 Algoritmo de Búsqueda

```python
def search(self, query: str, top_k: int = 3) -> List[KnowledgeEntry]:
    """
    Busca entradas relevantes usando scoring compuesto:

    Score = keyword_matches * 3 + priority + similarity

    - keyword_matches: Número de keywords que aparecen en query
    - priority: Prioridad de la entrada (1-5)
    - similarity: Similitud semántica (básica)
    """
    entries = self.repository.load_entries()
    scores = []

    for entry in entries:
        score = 0

        # Keywords
        for keyword in entry.keywords:
            if keyword.lower() in query.lower():
                score += 3

        # Prioridad
        score += entry.priority

        # Similitud básica (puede mejorarse con embeddings)
        similarity = calculate_similarity(query, entry.question)
        score += similarity

        scores.append((entry, score))

    # Ordenar y retornar top_k
    sorted_entries = sorted(scores, key=lambda x: x[1], reverse=True)
    return [entry for entry, score in sorted_entries[:top_k] if score > 0]
```

---

## 10. Base de Datos

### 10.1 DatabaseManager

```python
from src.database.connection import DatabaseManager
from src.config.settings import Settings

settings = Settings()
db_manager = DatabaseManager(settings)

# Obtener sesión
async with db_manager.get_session() as session:
    result = await session.execute("SELECT * FROM Ventas")
    rows = result.fetchall()

# Ejecutar query (método simplificado)
results = await db_manager.execute_query("SELECT COUNT(*) FROM Ventas")
```

### 10.2 Configuración de Conexión

**SQL Server con Instancia Nombrada:**

```ini
DB_HOST=localhost
DB_PORT=1433
DB_INSTANCE=SQLEXPRESS
DB_NAME=abcmasplus
DB_TYPE=mssql
```

**Connection String Generada:**

```
mssql+pyodbc://usuario:contraseña@localhost:1433/SQLEXPRESS/abcmasplus?driver=ODBC+Driver+17+for+SQL+Server
```

### 10.3 Pool de Conexiones

```python
# Configuración del pool
engine = create_async_engine(
    database_url,
    pool_size=5,              # Conexiones base
    max_overflow=10,          # Conexiones adicionales
    pool_pre_ping=True,       # Verificar conexión antes de usar
    echo=False                # No loggear SQL queries
)
```

### 10.4 Migraciones

**Ubicación:** `database/migrations/`

**Estructura:**

```sql
-- V001__crear_knowledge_base.sql
CREATE TABLE knowledge_categories (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NOT NULL,
    description NVARCHAR(500)
);

CREATE TABLE knowledge_entries (
    id INT PRIMARY KEY IDENTITY(1,1),
    question NVARCHAR(500) NOT NULL,
    answer NVARCHAR(MAX) NOT NULL,
    category_id INT FOREIGN KEY REFERENCES knowledge_categories(id),
    keywords NVARCHAR(500),
    priority INT DEFAULT 1
);
```

**Ejecutar Migraciones:**

Actualmente manual. Ejecutar scripts SQL en orden.

---

## 11. Patrones de Diseño

### 11.1 Patrones Implementados

| Patrón | Ubicación | Propósito |
|--------|-----------|----------|
| **Strategy** | `providers/` | Intercambiar LLM providers |
| **Adapter** | `providers/` | Adaptar diferentes APIs |
| **Singleton** | `ToolRegistry`, `PromptManager` | Instancia única global |
| **Factory** | `ToolInitializer` | Crear tools |
| **Builder** | `ExecutionContextBuilder` | Construir contexto |
| **Decorator** | `middleware/` | Decorar handlers |
| **Repository** | `KnowledgeRepository` | Acceso a datos |
| **Dependency Injection** | `telegram_bot.py` | Inyectar dependencias |
| **Command** | `Tools` | Encapsular acciones |

### 11.2 Strategy Pattern (Providers)

```python
# Interfaz
class BaseProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass

# Implementaciones
class OpenAIProvider(BaseProvider):
    async def generate(self, prompt: str) -> str:
        # Lógica OpenAI
        ...

class AnthropicProvider(BaseProvider):
    async def generate(self, prompt: str) -> str:
        # Lógica Anthropic
        ...

# Uso polimórfico
provider: BaseProvider = OpenAIProvider(settings)
# O
provider: BaseProvider = AnthropicProvider(settings)

# Mismo código funciona con ambos
agent = LLMAgent(provider, db_manager)
```

### 11.3 Singleton Pattern (ToolRegistry)

```python
class ToolRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools = {}
        return cls._instance

    def register_tool(self, tool: BaseTool):
        self._tools[tool.get_info().name] = tool

# Uso
registry = ToolRegistry()  # Siempre la misma instancia
registry.register_tool(query_tool)
```

### 11.4 Builder Pattern (ExecutionContext)

```python
context = ExecutionContextBuilder() \
    .with_user(user) \
    .with_message(message) \
    .with_parameters({"user_input": "query"}) \
    .with_dependency("agent", agent) \
    .with_dependency("db_manager", db_manager) \
    .build()
```

### 11.5 Dependency Injection

```python
# En telegram_bot.py
async def initialize(self):
    # Inyectar dependencias en bot_data
    self.application.bot_data["tool_orchestrator"] = self.tool_orchestrator
    self.application.bot_data["agent"] = self.agent
    self.application.bot_data["db_manager"] = self.db_manager

# En handlers
async def ia_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    orchestrator = context.bot_data["tool_orchestrator"]  # Inyectado
    agent = context.bot_data["agent"]  # Inyectado
```

---

## 12. Testing

### 12.1 Estructura de Tests

```
tests/
├── agent/
│   ├── test_llm_agent.py
│   ├── test_providers.py
│   ├── test_classifiers.py
│   └── knowledge/
│       ├── test_knowledge_manager.py
│       └── test_knowledge_repository.py
├── handlers/
│   ├── test_command_handlers.py
│   └── test_query_handlers.py
├── orchestrator/
│   └── test_tool_selector.py
└── tools/
    ├── test_tool_registry.py
    ├── test_tool_orchestrator.py
    └── test_query_tool.py
```

### 12.2 Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests específicos
pytest tests/tools/ -v
pytest tests/agent/ -v

# Con coverage
pytest --cov=src --cov-report=html

# Tests rápidos (parar al primer error)
pytest -x --tb=short

# Tests en paralelo
pytest -n auto
```

### 12.3 Ejemplo de Test

```python
# tests/tools/test_query_tool.py
import pytest
from src.tools.builtin.query_tool import QueryTool
from src.tools.execution_context import ExecutionContextBuilder

@pytest.fixture
def query_tool():
    return QueryTool()

@pytest.fixture
def execution_context(agent_mock, message_mock):
    return ExecutionContextBuilder() \
        .with_user(user_mock) \
        .with_message(message_mock) \
        .with_parameters({"user_input": "¿Cuántas ventas?"}) \
        .with_dependency("agent", agent_mock) \
        .build()

@pytest.mark.asyncio
async def test_query_tool_execute(query_tool, execution_context):
    """Test ejecución de QueryTool."""
    result = await query_tool.execute(execution_context)

    assert result is not None
    assert isinstance(result, str)
```

### 12.4 Mocking

```python
from unittest.mock import AsyncMock, MagicMock

# Mock de LLM Provider
@pytest.fixture
def provider_mock():
    mock = AsyncMock()
    mock.generate.return_value = "SELECT COUNT(*) FROM Ventas"
    return mock

# Mock de DatabaseManager
@pytest.fixture
def db_manager_mock():
    mock = AsyncMock()
    mock.execute_query.return_value = [(15,)]
    return mock
```

---

## 13. GitFlow y Versionado

### 13.1 Estructura de Ramas

```
master (main)
  ├── v0.3.0 (tag)
  ├── v0.2.0 (tag)
  └── v0.1.0-base (tag template)

develop (integración)
  ├── feature/nueva-funcionalidad-1
  ├── feature/nueva-funcionalidad-2
  └── bugfix/correccion-error

hotfix/arreglo-critico (desde master)
```

### 13.2 Workflow Completo

#### Crear Feature

```bash
# 1. Actualizar develop
git checkout develop
git pull origin develop

# 2. Crear feature branch
git checkout -b feature/mi-funcionalidad

# 3. Trabajar
git add .
git commit -m "feat(scope): descripción"

# 4. Actualizar con develop regularmente
git fetch origin
git rebase origin/develop

# 5. Push
git push -u origin feature/mi-funcionalidad

# 6. Crear Pull Request en GitHub
# → Hacia develop
# → Pedir code review
# → Esperar aprobación
```

#### Merge a Develop

```bash
# En GitHub:
# 1. Aprobar PR
# 2. Merge (usa --no-ff automáticamente)
# 3. Borrar branch feature

# Local:
git checkout develop
git pull origin develop
git branch -d feature/mi-funcionalidad
```

#### Crear Release

```bash
# 1. Crear release branch desde develop
git checkout develop
git pull origin develop
git checkout -b release/v1.0.0

# 2. Ajustes finales
# - Actualizar versión en archivos
# - Testing final
# - Documentación

# 3. Merge a master
git checkout master
git merge --no-ff release/v1.0.0
git tag -a v1.0.0 -m "Release v1.0.0: Descripción"

# 4. Merge de vuelta a develop
git checkout develop
git merge --no-ff release/v1.0.0

# 5. Push
git push origin master develop --tags

# 6. Borrar release branch
git branch -d release/v1.0.0
git push origin --delete release/v1.0.0
```

#### Hotfix Urgente

```bash
# 1. Crear hotfix desde master
git checkout master
git checkout -b hotfix/arreglo-critico

# 2. Hacer fix
git add .
git commit -m "fix(scope): descripción del arreglo"

# 3. Merge a master
git checkout master
git merge --no-ff hotfix/arreglo-critico
git tag -a v1.0.1 -m "Hotfix: arreglo crítico"

# 4. Merge a develop
git checkout develop
git merge --no-ff hotfix/arreglo-critico

# 5. Push
git push origin master develop --tags

# 6. Borrar hotfix branch
git branch -d hotfix/arreglo-critico
```

### 13.3 Convenciones de Commits (Conventional Commits)

**Formato:**

```
<tipo>(<scope>): <descripción breve>

[cuerpo opcional]

[footer opcional]
```

**Tipos:**

- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Documentación
- `style`: Formato (no afecta código)
- `refactor`: Refactorización
- `test`: Tests
- `chore`: Mantenimiento

**Scopes:**

- `agent`: Cambios en módulo agent
- `bot`: Cambios en módulo bot
- `tools`: Sistema de tools
- `database`: Base de datos
- `config`: Configuración
- `docs`: Documentación

**Ejemplos:**

```bash
git commit -m "feat(tools): implementar HelpTool con auto-documentación"
git commit -m "fix(agent): corregir clasificación de consultas KNOWLEDGE"
git commit -m "docs(readme): actualizar instrucciones de instalación"
git commit -m "refactor(providers): extraer lógica común a BaseProvider"
git commit -m "test(tools): agregar tests para ToolRegistry"
```

### 13.4 Versionado Semántico

**Formato:** `MAJOR.MINOR.PATCH`

- **MAJOR**: Cambios incompatibles de API
- **MINOR**: Nueva funcionalidad compatible
- **PATCH**: Correcciones de bugs

**Ejemplos:**

- `v0.1.0-base`: Versión template inicial
- `v0.2.0`: Agregado sistema de Tools (nueva funcionalidad)
- `v0.3.0`: Agregada Knowledge Base (nueva funcionalidad)
- `v0.3.1`: Fix en clasificación de queries (bug fix)

---

## 14. Guía de Contribución

### 14.1 Proceso de Contribución

1. **Fork** del repositorio (o trabajar en feature branch si tienes acceso)
2. **Crear feature branch** desde `develop`
3. **Hacer cambios** siguiendo convenciones
4. **Escribir tests** para nueva funcionalidad
5. **Commit** con Conventional Commits
6. **Push** y crear Pull Request hacia `develop`
7. **Code Review** y ajustes
8. **Merge** tras aprobación

### 14.2 Estándares de Código

#### Python Style Guide

- **PEP 8**: Seguir convenciones de Python
- **Type Hints**: Usar type hints en todos los métodos
- **Docstrings**: Documentar todas las clases y métodos públicos
- **Nombres**: En español para nombres de dominio, en inglés para código

```python
class QueryTool(BaseTool):
    """Tool para consultas de base de datos en lenguaje natural.

    Este tool permite a los usuarios hacer consultas a la base de datos
    usando lenguaje natural. Internamente traduce la consulta a SQL,
    la valida y ejecuta de forma segura.

    Attributes:
        name: Nombre del tool
        description: Descripción del tool
    """

    async def execute(self, context: ExecutionContext) -> str:
        """Ejecuta una consulta de base de datos.

        Args:
            context: Contexto de ejecución con parámetros y dependencias

        Returns:
            Respuesta en lenguaje natural con los resultados

        Raises:
            ValueError: Si la consulta es inválida
            DatabaseError: Si hay error en la ejecución
        """
        ...
```

#### Estructura de Archivos

- **Un módulo por archivo** cuando sea posible
- **Imports agrupados**: Standard library → Third-party → Local
- **Orden de definiciones**: Constants → Classes → Functions

```python
# Standard library
import os
from typing import List, Dict

# Third-party
from pydantic import BaseModel
from openai import AsyncOpenAI

# Local
from src.config.settings import Settings
from src.agent.providers.base_provider import BaseProvider
```

### 14.3 Checklist para Pull Requests

- [ ] Código sigue PEP 8
- [ ] Type hints en todos los métodos
- [ ] Docstrings en clases y métodos públicos
- [ ] Tests escritos y pasando
- [ ] Documentación actualizada
- [ ] Commits siguen Conventional Commits
- [ ] Sin conflictos con `develop`
- [ ] Sin archivos de configuración sensibles (.env, etc)

### 14.4 Code Review

**Para Revisores:**

- Verificar que el código sea claro y mantenible
- Verificar tests adecuados
- Verificar que no haya security issues
- Sugerir mejoras constructivamente

**Para Contribuyentes:**

- Responder a comentarios
- Hacer ajustes solicitados
- Ser receptivo a feedback

---

## 15. Troubleshooting

### 15.1 Problemas Comunes

#### Bot no responde

**Síntoma:** El bot no responde a mensajes

**Causas posibles:**

1. Token de Telegram inválido
2. Bot no tiene permisos
3. Error en inicialización

**Solución:**

```bash
# Verificar token
echo $TELEGRAM_BOT_TOKEN

# Verificar logs
tail -f logs/bot.log

# Reiniciar bot
python main.py
```

#### Error de conexión a BD

**Síntoma:** `Cannot connect to database`

**Causas posibles:**

1. Credenciales incorrectas
2. SQL Server no acepta conexiones remotas
3. Driver ODBC no instalado

**Solución:**

```bash
# Verificar variables
python test_db_connection.py

# Verificar SQL Server
# - SQL Server Configuration Manager
# - Enable TCP/IP
# - Restart SQL Server service

# Instalar ODBC Driver 17
# Windows: Descargar desde Microsoft
# Linux: apt-get install msodbcsql17
```

#### LLM genera SQL inválido

**Síntoma:** SQL query es rechazado por validador

**Causas posibles:**

1. Schema incorrecto en prompt
2. Prompt no optimizado
3. LLM no entendió la consulta

**Solución:**

```python
# Verificar schema
schema = await db_manager.get_schema()
print(schema)

# Probar prompt manualmente
from src.agent.prompts.prompt_manager import PromptManager
manager = PromptManager()
prompt = manager.get_prompt("SQL_GENERATION")
print(prompt)

# Cambiar versión de prompt
manager = PromptManager(default_versions={"SQL_GENERATION": 2})
```

### 15.2 Debugging

#### Habilitar Logging Detallado

```ini
# .env
LOG_LEVEL=DEBUG
```

#### Logs del Sistema

```bash
# Ver logs en tiempo real
tail -f logs/bot.log

# Buscar errores
grep ERROR logs/bot.log

# Buscar por módulo
grep "llm_agent" logs/bot.log
```

#### Debugging en IDE

**VSCode launch.json:**

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Bot",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
```

### 15.3 Performance

#### Consultas Lentas

**Síntoma:** Respuestas tardan mucho

**Optimizaciones:**

```python
# 1. Cache de schema (TTL 1 hora)
@cache(ttl=3600)
async def get_schema():
    ...

# 2. Timeout en LLM calls
response = await provider.generate(prompt, timeout=10)

# 3. Limitar resultados
SELECT TOP 100 * FROM ...
```

#### Alto Uso de Memoria

**Optimizaciones:**

```python
# 1. Cerrar sesiones de BD
async with db_manager.get_session() as session:
    # Uso de sesión
    pass  # Se cierra automáticamente

# 2. Limitar tamaño de respuestas
max_results = 10
```

---

## 16. Roadmap y Próximos Pasos

### 16.1 Estado Actual (v0.3.0)

**Completado:**

- ✅ Bot básico funcionando
- ✅ Consultas de BD en lenguaje natural
- ✅ Knowledge Base empresarial
- ✅ Sistema de Tools extensible
- ✅ Múltiples proveedores LLM
- ✅ Sistema de prompts versionado

**En Desarrollo:**

- 🔄 Auto-selección de tools con LLM
- 🔄 Más tools (Help, Stats, etc)

### 16.2 Próximas Versiones

#### v0.4.0 - Sistema de Tools Completo

- [ ] HelpTool: Documentación dinámica
- [ ] StatsTool: Estadísticas de uso
- [ ] RegistrationTool: Registro de usuarios
- [ ] Auto-selección de tools refinada

#### v0.5.0 - Autenticación Robusta

- [ ] Sistema de roles completo
- [ ] Permisos granulares
- [ ] Auditoría de operaciones
- [ ] Registro multi-paso

#### v0.6.0 - Mejoras de Producción

- [ ] Logging con Loguru
- [ ] Métricas de uso
- [ ] Rate limiting
- [ ] Caching inteligente

#### v1.0.0 - Release de Producción

- [ ] Todas las características críticas completas
- [ ] Testing exhaustivo
- [ ] Documentación completa
- [ ] Despliegue automatizado

### 16.3 Futuro (Post v1.0)

- [ ] Integración WhatsApp
- [ ] Dashboard web
- [ ] Notificaciones por email
- [ ] Backup automático
- [ ] Multilenguaje
- [ ] RAG avanzado con embeddings

---

## Apéndices

### A. Glosario

- **LLM**: Large Language Model (Modelo de Lenguaje Grande)
- **RAG**: Retrieval-Augmented Generation
- **ORM**: Object-Relational Mapping
- **ABC**: Abstract Base Class
- **DI**: Dependency Injection
- **TTL**: Time To Live

### B. Referencias

**Documentación Externa:**

- [Telegram Bot API](https://core.telegram.org/bots)
- [python-telegram-bot](https://python-telegram-bot.readthedocs.io/)
- [OpenAI API](https://platform.openai.com/docs/api-reference)
- [Anthropic Claude](https://docs.anthropic.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/)

**Documentación Interna:**

- `DIAGRAMA_FLUJO_ACTUAL.md`: Flujos del sistema
- `GITFLOW.md`: Estrategia de branches
- `COMMIT_GUIDELINES.md`: Convenciones de commits
- `ROADMAP.md`: Hoja de ruta
- `QUICK_START_TOOLS.md`: Guía rápida de tools
- `TESTING_TOOLS.md`: Guía de testing

### C. Contacto y Soporte

**Para Issues:**
- Crear issue en GitHub con template

**Para Preguntas:**
- Revisar documentación primero
- Preguntar en canales internos

---

**Versión del Documento:** 1.0
**Última Actualización:** 2025-11-30
**Mantenido por:** Equipo de Desarrollo

---

Esta guía está viva y se actualiza constantemente. Si encuentras errores o tienes sugerencias, por favor contribuye.
