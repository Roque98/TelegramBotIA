# Iris Bot - Índice de Contexto

**Última actualización**: 2026-03-28
**Rama principal**: `develop`
**Estado**: Arquitectura ReAct activa — migración completada

## Archivos de Contexto

| Archivo | Descripción | Elementos |
|---------|-------------|-----------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Estructura de `src/` y flujo principal | 9 módulos |
| [HANDLERS.md](HANDLERS.md) | Handlers de Telegram | 9 comandos |
| [TOOLS.md](TOOLS.md) | Sistema de herramientas ReAct | 5 tools |
| [DATABASE.md](DATABASE.md) | Tablas y queries | 15+ tablas |
| [AGENTS.md](AGENTS.md) | Agentes LLM | ReActAgent (principal) |
| [PROMPTS.md](PROMPTS.md) | Sistema de prompts | ReAct prompts |
| [MEMORY.md](MEMORY.md) | Sistema de memoria | MemoryService |

---

## Resumen Ejecutivo

**Iris** es un bot de Telegram conversacional que usa un agente ReAct (Reasoning + Acting) para responder consultas en lenguaje natural. Se conecta a SQL Server, tiene base de conocimiento empresarial y memoria persistente por usuario.

También expone un **API REST** (Flask) en `src/api/` para integración con plataformas externas (autenticación por token encriptado).

## Stack Tecnológico

```
Backend:     Python 3.13
Bot:         python-telegram-bot 20.x
LLM:         OpenAI GPT-4o (configurable)
Database:    SQL Server
Validation:  Pydantic 2.x
API REST:    Flask + flask-cors
```

## Estructura de `src/`

```
src/
├── api/            ← Entrypoints REST (Flask): chat_endpoint.py
├── bot/            ← Entrypoints Telegram: handlers/, keyboards/, middleware/
├── gateway/        ← Normalización multi-canal: MessageGateway
├── pipeline/       ← Orquestación del flujo: MainHandler + factory
├── agents/         ← Motor LLM: base/, react/, providers/, tools/
├── domain/         ← Lógica de negocio pura
│   ├── auth/       ← user_entity, user_repository, user_service
│   ├── memory/     ← memory_entity, memory_repository, memory_service
│   └── knowledge/  ← knowledge_entity, knowledge_repository, knowledge_service
├── infra/          ← Servicios técnicos de soporte
│   ├── database/   ← connection, sql_validator
│   ├── events/     ← bus
│   └── observability/ ← metrics, tracing
├── config/         ← settings, personality
└── utils/          ← encryption, rate_limiter, retry, input_validator, status_message
```

## Flujo Principal

```
Telegram Update / REST Request
        │
        ▼
MessageGateway.from_telegram() / from_api()
        │
        ▼ ConversationEvent
MainHandler._process_event()
        │
        ├── MemoryService.get_context(user_id) → UserContext
        │
        ▼
ReActAgent.execute(query, context)
        │
        ├─ Loop: Thought → Action → Observation (max 10 iter.)
        │  ├── database_query → DatabaseManager.execute_query()
        │  ├── knowledge_search → KnowledgeService.search()
        │  ├── calculate → expr. matemáticas
        │  ├── get_datetime → fecha/hora actual
        │  └── finish → respuesta final
        │
        ▼ AgentResponse
MainHandler._record_interaction() [async]
        │
        ▼
Respuesta al usuario
```

## Comandos Disponibles

| Comando | Handler | Auth |
|---------|---------|------|
| `/start` | command_handlers.py | No |
| `/help` | command_handlers.py | No |
| `/stats` | command_handlers.py | Sí |
| `/cancel` | command_handlers.py | No |
| `/ia <query>` | tools_handlers.py | Sí |
| `/query <query>` | tools_handlers.py | Sí |
| `/register` | registration_handlers.py | No |
| `/verify` | registration_handlers.py | No |
| `/resend` | registration_handlers.py | No |

## Métricas del Proyecto

| Métrica | Valor |
|---------|-------|
| Archivos Python | ~65 |
| Módulos `src/` | 9 carpetas de primer nivel |
| Tools ReAct | 5 (database_query, knowledge_search, calculate, get_datetime, save_preference) |
| Tablas BD | 15+ |
| Handlers Telegram | 9 comandos + 1 message handler |
