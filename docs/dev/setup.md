[Docs](../index.md) › [Dev](README.md) › Setup local

# Setup local

---

## Requisitos

- Python 3.11+
- ODBC Driver 17 for SQL Server (ver [configuracion.md](../uso/configuracion.md))
- Acceso a la base de datos `abcmasplus`
- Token de bot de Telegram (BotFather)
- API key de OpenAI

---

## Configurar el entorno

### 1. Clonar el repositorio

```bash
git clone https://github.com/Roque98/TelegramBotIA.git
cd TelegramBotIA
git checkout develop
```

### 2. Crear el virtualenv

Este proyecto usa `pipenv` con virtualenv en `~/.virtualenvs/`:

```bash
pip install pipenv
pipenv install --dev
```

O con pip directamente:

```bash
python -m venv venv
source venv/bin/activate           # Linux/Mac
venv\Scripts\activate              # Windows
pip install -r requirements.txt
```

El virtualenv activo del proyecto se llama `GPT5-Cxk5mELR` en `~/.virtualenvs/`.
Para activarlo manualmente:

```bash
# Windows (bash/Git Bash)
source ~/.virtualenvs/GPT5-Cxk5mELR/Scripts/activate

# Linux/Mac
source ~/.virtualenvs/GPT5-Cxk5mELR/bin/activate
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con las credenciales reales. Ver [configuracion.md](../uso/configuracion.md)
para la referencia completa de variables.

### 4. Verificar la configuración

```bash
python check_config.py
```

Verifica que:
- Todas las variables requeridas están definidas
- La conexión a SQL Server es exitosa
- El token de Telegram es válido

### 5. Primer arranque

```bash
python main.py
```

El bot debería responder en Telegram en ~5 segundos.

---

## Modo desarrollo

```bash
python run_dev.py
```

Reinicia automáticamente cuando detecta cambios en archivos `.py`.
Útil durante el desarrollo activo.

---

## Estructura del proyecto

```
GPT5/
├── main.py                      ← Punto de entrada
├── run_dev.py                   ← Arranque con hot reload
├── check_config.py              ← Verificación de entorno
├── src/
│   ├── agents/                  ← ReActAgent, tools, providers
│   │   ├── base/                ← Contratos: AgentResponse, UserContext, ConversationEvent
│   │   ├── react/               ← ReActAgent, prompts, scratchpad, schemas
│   │   ├── tools/               ← Tools + ToolRegistry
│   │   ├── orchestrator/        ← AgentOrchestrator, IntentClassifier
│   │   ├── factory/             ← AgentBuilder
│   │   └── providers/           ← OpenAIProvider
│   ├── bot/
│   │   ├── handlers/            ← Comandos y mensajes de Telegram
│   │   ├── keyboards/           ← Teclados inline y de respuesta
│   │   ├── middleware/          ← Auth, logging, token
│   │   └── telegram_bot.py      ← Arranque del bot
│   ├── api/
│   │   └── chat_endpoint.py     ← REST API Flask
│   ├── gateway/
│   │   └── message_gateway.py   ← Normalización de canales
│   ├── pipeline/
│   │   ├── handler.py           ← MainHandler
│   │   └── factory.py           ← Composición de dependencias
│   ├── domain/
│   │   ├── auth/                ← Usuarios, permisos
│   │   ├── memory/              ← Contexto conversacional
│   │   ├── knowledge/           ← Base de conocimiento
│   │   ├── cost/                ← Tracking de costos LLM
│   │   ├── alerts/              ← Módulo de alertas PRTG
│   │   └── agent_config/        ← Configuración dinámica de agentes
│   ├── infra/
│   │   ├── database/            ← DatabaseManager, SQLValidator
│   │   ├── observability/       ← Tracer, Metrics, SQLRepository
│   │   ├── notifications/       ← notify_admin, fire_admin_notify (AdminNotifier)
│   │   └── events/              ← EventBus
│   ├── config/
│   │   ├── settings.py          ← Pydantic Settings
│   │   └── logging_config.py    ← Configuración de logging
│   └── utils/                   ← encryption, rate_limiter, retry, etc.
├── database/
│   └── migrations/              ← Scripts SQL en orden numérico
├── scripts/                     ← Utilidades y scripts de prueba
├── tests/                       ← Tests unitarios (pytest)
├── docs/                        ← Esta documentación
├── .claude/context/             ← Contexto para Claude Code (siempre actualizado)
└── plan/                        ← Planes del proyecto
```

---

[Índice](README.md) · **Siguiente →** [GitFlow del proyecto](gitflow.md)
