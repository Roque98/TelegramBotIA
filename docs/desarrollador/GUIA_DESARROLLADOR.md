# Guía del Desarrollador — IRIS Bot

> **Arquitectura:** ReAct Agent
> **Última actualización:** 2026-03-28
> **Rama activa:** develop

Esta guía es el punto de entrada para desarrolladores. Cubre lo esencial para entender, configurar y contribuir al proyecto. Para detalles técnicos específicos, cada sección apunta al documento especializado.

---

## Índice

1. [¿Qué es IRIS?](#1-qué-es-iris)
2. [Arquitectura](#2-arquitectura)
3. [Stack tecnológico](#3-stack-tecnológico)
4. [Configuración del entorno](#4-configuración-del-entorno)
5. [Componentes clave](#5-componentes-clave)
6. [Patrones de diseño](#6-patrones-de-diseño)
7. [Troubleshooting](#7-troubleshooting)
8. [Documentación relacionada](#8-documentación-relacionada)

---

## 1. ¿Qué es IRIS?

Bot de Telegram con un agente de IA que permite a empleados:

- Consultar bases de datos en lenguaje natural (SQL generado automáticamente)
- Buscar en una base de conocimiento empresarial
- Interactuar vía Telegram o una API REST para integración multicanal

Ejemplo de uso:
```
Usuario: /ia ¿Cuántas ventas hubo del producto Laptop en enero?
Bot:     Encontré 47 ventas del producto Laptop en enero de 2026.
```

---

## 2. Arquitectura

El sistema usa el paradigma **ReAct** (Reasoning + Acting): el agente razona paso a paso y llama herramientas cuando lo necesita.

```
Telegram / API REST
        │
        ▼
   AuthMiddleware          ← verifica identidad y permisos
        │
        ▼
   MessageGateway          ← normaliza el canal (Telegram o HTTP)
        │
        ▼
   MainHandler             ← coordina el flujo
        │
        ▼
   MemoryService           ← recupera contexto del usuario
        │
        ▼
   ReActAgent              ← loop: Thought → Action → Observation
     ├── database_query    ← genera SQL, valida, ejecuta
     ├── knowledge_search  ← busca en la base de conocimiento
     ├── calculate         ← operaciones matemáticas
     ├── format_table      ← formatea resultados como tabla
     └── get_db_schema     ← describe tablas disponibles
        │
        ▼
   MemoryService           ← guarda la interacción
        │
        ▼
   Respuesta al usuario
```

Para diagramas de flujo detallados, ver [DIAGRAMA_FLUJO_ACTUAL.md](DIAGRAMA_FLUJO_ACTUAL.md).
Para la estructura completa de `src/`, ver [ESTRUCTURA_PROYECTO.md](ESTRUCTURA_PROYECTO.md).

---

## 3. Stack tecnológico

| Categoría | Tecnología | Versión | Uso |
|-----------|-----------|---------|-----|
| Lenguaje | Python | 3.9+ | Base |
| Bot | python-telegram-bot | 21.7 | Interfaz Telegram |
| LLM (principal) | openai | 2.6.1 | GPT-5-nano |
| LLM (alternativo) | anthropic | 0.39.0 | Claude |
| ORM | SQLAlchemy | 2.0+ | Manejo de BD |
| DB Driver | pyodbc | 5.2.0 | SQL Server |
| Validación | Pydantic | 2.10.2 | Settings y schemas |
| Config | python-dotenv | 1.0.1 | Variables de entorno |
| Logging | Loguru | 0.7.3 | Logs estructurados |
| Retry | tenacity | 9.0.0 | Reintentos automáticos |
| Templates | Jinja2 | 3.1.0+ | Prompts dinámicos |
| API REST | Flask | — | Endpoint multicanal |

**Bases de datos soportadas:** SQL Server (principal), PostgreSQL, MySQL, SQLite.

---

## 4. Configuración del entorno

### Instalación

```bash
git clone https://github.com/Roque98/TelegramBotIA.git
cd TelegramBotIA
git checkout develop

python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### Variables de entorno

```bash
cp .env.example .env
```

Variables requeridas en `.env`:

```ini
# LLM
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5-nano-2025-08-07

# Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCdef...

# Base de datos
DB_HOST=localhost
DB_PORT=1433
DB_NAME=abcmasplus
DB_USER=usuario
DB_PASSWORD=contraseña
DB_TYPE=mssql          # mssql | postgresql | mysql | sqlite

# App
LOG_LEVEL=INFO         # DEBUG | INFO | WARNING | ERROR
ENVIRONMENT=development
```

### Ejecutar

```bash
python main.py                       # Bot Telegram (polling)
python src/api/chat_endpoint.py      # API REST (opcional)
python check_config.py               # Verificar configuración
```

---

## 5. Componentes clave

### ReActAgent (`src/agents/react/`)

Motor central del sistema. Recibe un mensaje, razona en pasos y decide qué tool llamar. El resultado se empaqueta en `ReActResponse` (Pydantic).

```python
from src.agents.react.agent import ReActAgent

agent = ReActAgent(provider=openai_provider, db_manager=db_manager)
response = await agent.run(user_message="¿Cuántas ventas hay?", context=memory_ctx)
```

### Tools (`src/agents/tools/`)

Cada tool hereda de `BaseTool` e implementa `execute()`. Se registran en `ToolRegistry` (singleton).

```python
from src.agents.tools.base import BaseTool
from src.agents.tools.registry import ToolRegistry

class MyTool(BaseTool):
    name = "my_tool"
    description = "Descripción para el LLM"

    async def execute(self, params: dict) -> str:
        ...

ToolRegistry.get_instance().register(MyTool())
```

Ver [QUICK_START_TOOLS.md](QUICK_START_TOOLS.md) para guía completa.

### MainHandler (`src/pipeline/handler.py`)

Orquesta el flujo: autenticación → memoria → agente → respuesta. Punto de entrada único para todos los canales.

### MemoryService (`src/domain/memory/`)

Persiste y recupera el historial conversacional del usuario desde la base de datos.

### AuthMiddleware (`src/bot/middleware.py`)

Verifica que el usuario esté registrado y tenga los permisos necesarios antes de procesar cualquier mensaje.

---

## 6. Patrones de diseño

| Patrón | Dónde | Para qué |
|--------|-------|---------|
| Strategy | `src/agents/providers/` | Intercambiar OpenAI / Anthropic sin tocar el agente |
| Singleton | `ToolRegistry`, `DatabaseManager` | Una sola instancia compartida |
| Repository | `src/domain/*/repository.py` | Abstraer el acceso a datos |
| Service | `src/domain/*/service.py` | Lógica de negocio desacoplada del ORM |
| Factory | `src/pipeline/factory.py` | Construir el grafo de dependencias en el arranque |
| Middleware | `src/bot/middleware.py` | Cross-cutting concerns (auth, logging) |

---

## 7. Troubleshooting

| Síntoma | Causa probable | Solución |
|---------|----------------|----------|
| `Connection refused` al iniciar | BD no disponible o credenciales incorrectas | Verificar `DB_*` en `.env` |
| `Invalid API key` | `OPENAI_API_KEY` vacío o expirado | Actualizar en `.env` |
| Bot no responde comandos | `TELEGRAM_BOT_TOKEN` incorrecto | Verificar con `@BotFather` |
| `Tool not found` | Tool no registrada en el arranque | Revisar `src/pipeline/factory.py` |
| Respuestas lentas (>30s) | LLM saturado o timeout de BD | Reducir `max_iterations` del agente o aumentar timeout de BD |
| `PermissionError` en Telegram | Usuario no registrado o sin permisos | Revisar tabla de usuarios y roles |

Para diagnóstico completo:
```bash
python check_config.py
python scripts/diagnose_memory.py
LOG_LEVEL=DEBUG python main.py
```

---

## 8. Documentación relacionada

| Documento | Contenido |
|-----------|-----------|
| [ESTRUCTURA_PROYECTO.md](ESTRUCTURA_PROYECTO.md) | Árbol completo de `src/` con descripción de cada módulo |
| [DIAGRAMA_FLUJO_ACTUAL.md](DIAGRAMA_FLUJO_ACTUAL.md) | Flujos detallados de la arquitectura ReAct |
| [QUICK_START_TOOLS.md](QUICK_START_TOOLS.md) | Cómo usar y crear herramientas del agente |
| [TESTING_TOOLS.md](TESTING_TOOLS.md) | Guía de testing con pytest |
| [PROMPTS_BEST_PRACTICES.md](PROMPTS_BEST_PRACTICES.md) | Cómo modificar el system prompt |
| [COMMIT_GUIDELINES.md](COMMIT_GUIDELINES.md) | Convenciones de commits |
| [GITFLOW.md](GITFLOW.md) | Estrategia de branches y releases |
| [../modulos/SISTEMA_AUTENTICACION.md](../modulos/SISTEMA_AUTENTICACION.md) | Registro, verificación y roles |
| [../api/CHAT_API_GUIDE.md](../api/CHAT_API_GUIDE.md) | Integración vía API REST |
