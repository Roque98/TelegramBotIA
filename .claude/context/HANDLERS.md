# Handlers de Telegram

## Resumen

| Tipo | Cantidad |
|------|----------|
| CommandHandlers | 9 |
| MessageHandlers | 1 (QueryHandler) |
| ConversationHandlers | 1 (registro) |

**Dependencia principal**: `pipeline/handler.py` → `MainHandler` (ReActAgent)

---

## TelegramBot (Arranque)

**Archivo**: `src/bot/telegram_bot.py`

```python
class TelegramBot:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.main_handler = create_main_handler(self.db_manager)  # pipeline/factory
        self.application = Application.builder().token(...).build()

    def setup(self):
        # Inyecta dependencias en bot_data (disponibles en todos los handlers)
        self.application.bot_data['main_handler'] = self.main_handler
        self.application.bot_data['db_manager'] = self.db_manager

        # Registra handlers
        register_command_handlers(application)
        register_query_handlers(application, self.main_handler)
        register_registration_handlers(application, self.db_manager)
        register_tools_handlers(application)

        # Middlewares
        setup_logging_middleware(application)
        setup_auth_middleware(application)

    def run(self):
        self.application.run_polling()
```

---

## Comandos Registrados

### /start
- **Archivo**: `src/bot/handlers/command_handlers.py`
- **Función**: `start_command`
- **Descripción**: Genera mensaje de bienvenida dinámico desde BD (categorías y ejemplos filtrados por rol)
- **Requiere auth**: No

### /help
- **Archivo**: `src/bot/handlers/command_handlers.py`
- **Función**: `help_command`
- **Descripción**: Genera guía de uso dinámicamente desde BD
- **Requiere auth**: No

### /stats
- **Archivo**: `src/bot/handlers/command_handlers.py`
- **Función**: `stats_command`
- **Descripción**: Estadísticas de uso (placeholder — pendiente implementar)
- **Requiere auth**: Sí

### /cancel
- **Archivo**: `src/bot/handlers/command_handlers.py`
- **Función**: `cancel_command`
- **Descripción**: Cancela operación en curso (útil en flujos conversacionales)
- **Requiere auth**: No

### /ia
- **Archivo**: `src/bot/handlers/tools_handlers.py`
- **Función**: `handle_ia_command`
- **Descripción**: Consulta inteligente — delega a `MainHandler.handle_telegram()` (ReActAgent)
- **Requiere auth**: Sí

### /query
- **Archivo**: `src/bot/handlers/tools_handlers.py`
- **Función**: `handle_query_command`
- **Descripción**: Alias de /ia
- **Requiere auth**: Sí

### /register
- **Archivo**: `src/bot/handlers/registration_handlers.py`
- **Función**: `RegistrationHandlers.cmd_register`
- **Descripción**: Inicia proceso de registro (solicita número de empleado)
- **Flujo**: ConversationHandler

### /verify
- **Archivo**: `src/bot/handlers/registration_handlers.py`
- **Función**: `RegistrationHandlers.cmd_verify`
- **Uso**: `/verify <código>`

### /resend
- **Archivo**: `src/bot/handlers/registration_handlers.py`
- **Función**: `RegistrationHandlers.cmd_resend`
- **Descripción**: Regenera código de verificación

---

## Message Handler: QueryHandler

**Archivo**: `src/bot/handlers/query_handlers.py`
**Filtro**: `filters.TEXT & ~filters.COMMAND`
**Descripción**: Procesa mensajes de texto libres (sin comando) como consultas al ReActAgent

```python
class QueryHandler:
    def __init__(self, main_handler: MainHandler)

    async def handle_text_message(update, context)
```

**Flujo**:
```
1. Obtener telegram_user del context (cacheado por auth_middleware)
   └── Si no está: UserService.get_user_by_chat_id(chat_id) desde BD
2. Validar que usuario está registrado y activo
3. Verificar permiso para consultas (/ia)
4. main_handler.handle_telegram(update, context) → respuesta
5. Enviar respuesta (split si > 4000 chars)
```

**Dependencias**:
- `pipeline/handler.py` → `MainHandler`
- `domain/auth` → `UserService`
- `utils/status_message.py` → `StatusMessage`

---

## ConversationHandler: Registro

**Archivo**: `src/bot/handlers/registration_handlers.py`

```
Estados:
┌─────────────────────────────────────┐
│        WAITING_FOR_EMPLOYEE_ID      │
└────────────────┬────────────────────┘
                 │
     Usuario envía número de empleado
                 │
                 ▼
     ┌──────────────────────┐
     │  UserService.        │
     │  validate_employee() │
     └──────────┬───────────┘
                │
     ┌──────────┴──────────┐
     │                     │
     ▼                     ▼
❌ No existe           ✅ Existe
(solicitar reintento)  (enviar código, END)
```

```python
class RegistrationHandlers:
    def __init__(self, db_manager: DatabaseManager)

    async def cmd_register(update, context)
    async def handle_employee_id(update, context)
    async def cmd_verify(update, context)
    async def cmd_resend(update, context)
    async def cmd_cancel(update, context)
```

---

## Middlewares

**Archivos**: `src/bot/middleware/`

### AuthMiddleware (`auth_middleware.py`)
- Intercepta todos los mensajes antes de los handlers
- Verifica autenticación con `UserService`
- Cachea `telegram_user` en `context.user_data`
- Rechaza usuarios no registrados con mensaje apropiado

### LoggingMiddleware (`logging_middleware.py`)
- Registra todas las interacciones (user_id, comando, duración)
- No bloquea el flujo

### TokenMiddleware (`token_middleware.py`)
- Usado exclusivamente por el API REST (`src/api/chat_endpoint.py`)
- Valida tokens AES encriptados con `numero_empleado` + `timestamp`
- TTL configurable (por defecto 3 minutos)

---

## Dependencias por Handler

```
command_handlers.py
├── start_command → domain/knowledge/KnowledgeRepository, domain/auth/UserService
├── help_command  → domain/knowledge/KnowledgeRepository, domain/auth/UserService
├── stats_command → (placeholder)
└── cancel_command → (ninguna)

query_handlers.py (QueryHandler)
├── pipeline/handler.py → MainHandler
└── domain/auth → UserService

tools_handlers.py
├── handle_ia_command → context.bot_data['main_handler'] (MainHandler)
└── handle_query_command → handle_ia_command

registration_handlers.py (RegistrationHandlers)
├── domain/auth → UserService
└── infra/database → DatabaseManager

telegram_bot.py (TelegramBot)
├── pipeline/factory.py → create_main_handler
└── infra/database → DatabaseManager
```
