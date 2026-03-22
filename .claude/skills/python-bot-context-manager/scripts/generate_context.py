#!/usr/bin/env python3
"""
Python Bot Context Generator
Genera archivos de contexto para bots de Telegram con LLMs
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
import ast


class PythonBotContextGenerator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.context_dir = self.project_root / ".claude" / "context"
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def generate_all(self):
        """Genera todos los archivos de contexto"""
        print("🚀 Generando contexto del bot de Telegram...")
        
        # Crear estructura
        self.context_dir.mkdir(parents=True, exist_ok=True)
        
        # Analizar proyecto
        project_info = self._analyze_project()
        
        # Generar archivos
        self._generate_index(project_info)
        self._generate_architecture(project_info)
        self._generate_handlers(project_info)
        self._generate_database(project_info)
        self._generate_prompts(project_info)
        self._generate_llm_integration(project_info)
        self._generate_config(project_info)
        self._generate_skills(project_info)
        
        print(f"✅ Contexto generado en: {self.context_dir}")
        
    def _analyze_project(self) -> Dict:
        """Analiza estructura del proyecto Python"""
        print("🔍 Analizando proyecto...")
        
        info = {
            'name': self.project_root.name,
            'python_files': [],
            'handlers': [],
            'models': [],
            'prompts': [],
            'dependencies': {},
            'has_telegram': False,
            'has_openai': False,
            'has_anthropic': False,
            'has_langchain': False,
            'has_sqlalchemy': False,
        }
        
        # Analizar requirements.txt
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            info['dependencies'] = self._parse_requirements(req_file)
            info['has_telegram'] = 'python-telegram-bot' in info['dependencies']
            info['has_openai'] = 'openai' in info['dependencies']
            info['has_anthropic'] = 'anthropic' in info['dependencies']
            info['has_langchain'] = any('langchain' in dep for dep in info['dependencies'])
            info['has_sqlalchemy'] = 'sqlalchemy' in info['dependencies']
        
        # Buscar archivos Python
        for py_file in self.project_root.rglob("*.py"):
            if self._should_ignore(py_file):
                continue
                
            info['python_files'].append(str(py_file.relative_to(self.project_root)))
            
            # Analizar contenido
            self._analyze_python_file(py_file, info)
        
        # Buscar prompts (archivos .jinja2, .j2, .txt en carpeta prompts/)
        prompt_dirs = list(self.project_root.rglob("prompts"))
        for prompt_dir in prompt_dirs:
            if prompt_dir.is_dir():
                for prompt_file in prompt_dir.rglob("*"):
                    if prompt_file.suffix in ['.jinja2', '.j2', '.txt', '.md']:
                        info['prompts'].append(str(prompt_file.relative_to(self.project_root)))
        
        return info
    
    def _parse_requirements(self, req_file: Path) -> Dict[str, str]:
        """Parsea requirements.txt"""
        deps = {}
        try:
            content = req_file.read_text()
            for line in content.split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Parsear nombre==versión o nombre>=versión
                match = re.match(r'([a-zA-Z0-9\-_]+)([=<>!]+)(.+)', line)
                if match:
                    name, operator, version = match.groups()
                    deps[name] = version.strip()
                else:
                    # Sin versión
                    deps[line] = 'latest'
        except Exception as e:
            print(f"⚠️ Error parseando requirements: {e}")
        
        return deps
    
    def _should_ignore(self, path: Path) -> bool:
        """Verifica si debe ignorar un archivo"""
        ignore_patterns = [
            '__pycache__',
            '.venv',
            'venv',
            'env',
            '.git',
            'node_modules',
            '.pytest_cache',
            'dist',
            'build',
            '*.pyc'
        ]
        
        path_str = str(path)
        return any(pattern in path_str for pattern in ignore_patterns)
    
    def _analyze_python_file(self, py_file: Path, info: Dict):
        """Analiza un archivo Python para extraer handlers, modelos, etc."""
        try:
            content = py_file.read_text(encoding='utf-8')
            
            # Detectar handlers de Telegram
            if 'CommandHandler' in content or 'MessageHandler' in content or 'CallbackQueryHandler' in content:
                # Extraer funciones async que parecen handlers
                handlers = re.findall(r'async def (\w+)\s*\(update.*?context', content)
                for handler in handlers:
                    info['handlers'].append({
                        'name': handler,
                        'file': str(py_file.relative_to(self.project_root))
                    })
            
            # Detectar modelos SQLAlchemy
            if 'Base' in content and '__tablename__' in content:
                # Buscar clases que heredan de Base
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Verificar si hereda de Base o tiene __tablename__
                        has_tablename = any(
                            isinstance(item, ast.Assign) and 
                            any(t.id == '__tablename__' for t in item.targets if isinstance(t, ast.Name))
                            for item in node.body
                        )
                        if has_tablename:
                            info['models'].append({
                                'name': node.name,
                                'file': str(py_file.relative_to(self.project_root))
                            })
                            
        except Exception as e:
            print(f"⚠️ Error analizando {py_file.name}: {e}")
    
    def _generate_index(self, info: Dict):
        """Genera INDEX.md"""
        content = f"""# {info['name']} - Índice de Contexto

**Última actualización**: {self.timestamp}
**Tipo**: Bot de Telegram con LLMs
**Stack**: Python, python-telegram-bot, OpenAI, Anthropic, LangChain, SQLAlchemy

## Navegación rápida

| Archivo | Descripción | Última actualización |
|---------|-------------|---------------------|
| [HANDLERS.md](./HANDLERS.md) | Comandos y callbacks del bot | {self.timestamp} |
| [PROMPTS.md](./PROMPTS.md) | Sistema de prompts modulares | {self.timestamp} |
| [DATABASE.md](./DATABASE.md) | Modelos SQLAlchemy y queries | {self.timestamp} |
| [LLM_INTEGRATION.md](./LLM_INTEGRATION.md) | Integración con LLMs | {self.timestamp} |
| [CONFIG.md](./CONFIG.md) | Variables de entorno y settings | {self.timestamp} |
| [SKILLS.md](./SKILLS.md) | Skills específicas del bot | {self.timestamp} |

## Resumen ejecutivo

Bot de Telegram que integra múltiples LLMs (OpenAI, Anthropic, LangChain) con persistencia en SQL Server.

**Componentes principales**:
- 🤖 **Handlers**: {len(info['handlers'])} comandos/callbacks detectados
- 🗄️ **Database**: {len(info['models'])} modelos SQLAlchemy
- 💬 **Prompts**: {len(info['prompts'])} templates de prompts
- 🧠 **LLMs**: {'OpenAI' if info['has_openai'] else ''}{'Anthropic' if info['has_anthropic'] else ''}{'LangChain' if info['has_langchain'] else ''}

## Dependencias principales

"""
        
        # Listar dependencias más importantes
        important_deps = [
            'python-telegram-bot', 'openai', 'anthropic', 'langchain',
            'sqlalchemy', 'pyodbc', 'pydantic', 'loguru', 'tenacity'
        ]
        
        for dep in important_deps:
            if dep in info['dependencies']:
                version = info['dependencies'][dep]
                content += f"- **{dep}**: {version}\n"
        
        content += f"""
## Skills disponibles

- `telegram-handler`: Crear comandos y callbacks
- `prompt-engineering`: Sistema de prompts modulares
- `database-operations`: Modelos y queries SQLAlchemy
- `llm-integration`: Integración con OpenAI/Anthropic

## Estructura del proyecto

```
{info['name']}/
├── handlers/          # Command handlers y callbacks
├── models/            # Modelos SQLAlchemy
├── prompts/           # Templates de prompts (Jinja2)
├── database/          # Configuración de DB
├── utils/             # Utilidades
└── requirements.txt
```

## Cómo usar este contexto

1. **Nueva sesión**: Lee este INDEX.md primero
2. **Tarea específica**: Navega al archivo relevante
3. **Skills**: Usa las skills en SKILLS.md para tareas comunes
4. **Actualización**: Regenera cuando agregues handlers/modelos

---
*Generado automáticamente por Python Bot Context Manager*
"""
        
        self._write_file("INDEX.md", content)
    
    def _generate_architecture(self, info: Dict):
        """Genera ARCHITECTURE.md"""
        content = f"""# Arquitectura del Bot

## Stack tecnológico

- **Lenguaje**: Python 3.x
- **Bot Framework**: python-telegram-bot {info['dependencies'].get('python-telegram-bot', 'N/A')}
- **LLMs**:
  - OpenAI: {info['dependencies'].get('openai', 'N/A') if info['has_openai'] else 'No configurado'}
  - Anthropic: {info['dependencies'].get('anthropic', 'N/A') if info['has_anthropic'] else 'No configurado'}
  - LangChain: {info['dependencies'].get('langchain', 'N/A') if info['has_langchain'] else 'No configurado'}
- **Database**: SQLAlchemy {info['dependencies'].get('sqlalchemy', 'N/A')} + SQL Server
- **Configuración**: Pydantic Settings + python-dotenv
- **Logging**: Loguru
- **Reintentos**: Tenacity

## Patrón arquitectónico

```
┌─────────────────┐
│  Telegram Bot   │
└────────┬────────┘
         │
    ┌────▼────┐
    │ Handlers│ ◄── Comandos, Callbacks
    └────┬────┘
         │
    ┌────▼─────────┐
    │  LLM Layer   │ ◄── OpenAI, Anthropic, LangChain
    │   + Prompts  │
    └────┬─────────┘
         │
    ┌────▼────────┐
    │  Database   │ ◄── SQLAlchemy + SQL Server
    └─────────────┘
```

## Flujo de una petición

1. **Usuario** envía comando/mensaje a Telegram
2. **Handler** procesa el update
3. **Database** consulta/guarda datos del usuario
4. **Prompts** se renderizan con contexto
5. **LLM** procesa y genera respuesta
6. **Handler** envía respuesta a Telegram
7. **Database** guarda la conversación

## Módulos principales

### handlers/
Contiene los command handlers, callback handlers y conversation handlers.

### models/
Modelos SQLAlchemy para la base de datos.

### prompts/
Templates de prompts modulares usando Jinja2.

### database/
Configuración de conexión, sesiones async y utilities.

### utils/
Funciones auxiliares, helpers, decoradores.

## Configuración

Variables de entorno en `.env`:
- `TELEGRAM_BOT_TOKEN`: Token del bot
- `OPENAI_API_KEY`: API key de OpenAI
- `ANTHROPIC_API_KEY`: API key de Anthropic
- `DATABASE_URL`: Connection string de SQL Server

## Patrones de diseño

- **Async/Await**: Todo el bot es asíncrono
- **Dependency Injection**: Settings via Pydantic
- **Template Method**: Prompts con Jinja2
- **Retry Pattern**: Tenacity para llamadas a APIs
- **Repository Pattern**: Abstracción de DB con SQLAlchemy

---
*Última actualización: {self.timestamp}*
"""
        
        self._write_file("ARCHITECTURE.md", content)
    
    def _generate_handlers(self, info: Dict):
        """Genera HANDLERS.md"""
        content = f"""# Telegram Bot Handlers

## Handlers detectados

Total: {len(info['handlers'])} handlers

"""
        
        for handler in info['handlers'][:20]:  # Primeros 20
            content += f"""### {handler['name']}
- **Archivo**: `{handler['file']}`
- **Tipo**: {'Command' if 'command' in handler['name'].lower() else 'Callback' if 'callback' in handler['name'].lower() else 'Message'} handler

"""
        
        content += """
## Patrón de desarrollo - Command Handler

```python
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from loguru import logger
from database import AsyncSessionLocal
from models import User

async def comando_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    \"\"\"
    Descripción del comando
    
    Usage: /comando [argumentos]
    \"\"\"
    try:
        # 1. Datos del usuario
        user_id = update.effective_user.id
        username = update.effective_user.username
        
        # 2. Argumentos
        args = context.args
        
        # 3. Interacción con DB
        async with AsyncSessionLocal() as session:
            # Queries aquí
            pass
        
        # 4. Responder
        await update.message.reply_text(
            "✅ Respuesta",
            parse_mode="Markdown"
        )
        
        logger.info(f"/comando ejecutado por {username}")
        
    except Exception as e:
        logger.error(f"Error en /comando: {e}")
        await update.message.reply_text("⚠️ Error procesando comando")

# Registrar
application.add_handler(CommandHandler("comando", comando_handler))
```

## Patrón - Callback Handler

```python
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    \"\"\"Maneja callbacks de inline buttons\"\"\"
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("action_"):
        action = data.replace("action_", "")
        
        # Lógica según acción
        
        await query.edit_message_text(
            text=f"Acción: {action}",
            reply_markup=None
        )

application.add_handler(CallbackQueryHandler(callback_handler, pattern="^action_"))
```

## Patrón - Conversation Handler

```python
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters

# Estados
ESTADO_1, ESTADO_2, ESTADO_3 = range(3)

async def start_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pregunta inicial")
    return ESTADO_1

async def estado_1_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Guardar respuesta
    context.user_data['respuesta_1'] = update.message.text
    
    await update.message.reply_text("Segunda pregunta")
    return ESTADO_2

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Conversación cancelada")
    return ConversationHandler.END

# Definir conversation handler
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start_conversation)],
    states={
        ESTADO_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, estado_1_handler)],
        ESTADO_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, estado_2_handler)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

application.add_handler(conv_handler)
```

---
*Última actualización: {self.timestamp}*
"""
        
        self._write_file("HANDLERS.md", content)
    
    def _generate_database(self, info: Dict):
        """Genera DATABASE.md"""
        content = f"""# Base de Datos

## Configuración

- **Motor**: SQL Server
- **ORM**: SQLAlchemy {info['dependencies'].get('sqlalchemy', '2.0')}
- **Driver**: pyodbc
- **Async**: SQLAlchemy Async

## Modelos detectados

Total: {len(info['models'])} modelos

"""
        
        for model in info['models']:
            content += f"""### {model['name']}
- **Archivo**: `{model['file']}`

"""
        
        content += """
## Patrón de configuración

```python
# database/config.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

# Connection string
DATABASE_URL = settings.DATABASE_URL

# Engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base para modelos
Base = declarative_base()
```

## Patrón de modelo

```python
# models/user.py
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    \"\"\"Usuario de Telegram\"\"\"
    __tablename__ = 'users'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Telegram data
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username='{self.username}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'telegram_id': self.telegram_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
```

## Patrón de queries (CRUD)

```python
# database/queries.py
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models import User
from loguru import logger

async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int):
    \"\"\"Obtener usuario por telegram_id\"\"\"
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()

async def create_user(session: AsyncSession, telegram_id: int, **kwargs):
    \"\"\"Crear nuevo usuario\"\"\"
    try:
        user = User(telegram_id=telegram_id, **kwargs)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        logger.info(f"Usuario creado: {telegram_id}")
        return user
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creando usuario: {e}")
        raise

async def update_user(session: AsyncSession, user_id: int, **kwargs):
    \"\"\"Actualizar usuario\"\"\"
    await session.execute(
        update(User).where(User.id == user_id).values(**kwargs)
    )
    await session.commit()

async def get_or_create_user(session: AsyncSession, telegram_id: int, **defaults):
    \"\"\"Get or create pattern\"\"\"
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        user = await create_user(session, telegram_id, **defaults)
    return user
```

## Uso en handlers

```python
from database import AsyncSessionLocal
from database.queries import get_or_create_user

async def comando_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    
    async with AsyncSessionLocal() as session:
        user = await get_or_create_user(
            session,
            telegram_id=telegram_id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name
        )
        
        # Usar el user
        logger.info(f"Usuario: {user.username}")
```

---
*Última actualización: {self.timestamp}*
"""
        
        self._write_file("DATABASE.md", content)
    
    def _generate_prompts(self, info: Dict):
        """Genera PROMPTS.md"""
        content = f"""# Sistema de Prompts

## Prompts detectados

Total: {len(info['prompts'])} archivos de prompts

"""
        
        for prompt in info['prompts'][:15]:
            content += f"- `{prompt}`\n"
        
        content += """
## Arquitectura modular con Jinja2

```
prompts/
├── base/
│   ├── system.jinja2          # System prompt base
│   └── guidelines.jinja2      # Guías generales
├── tasks/
│   ├── summarize.jinja2       # Resumir
│   ├── analyze.jinja2         # Analizar
│   └── generate.jinja2        # Generar
└── responses/
    └── format.jinja2           # Formato de respuesta
```

## Configuración de Jinja2

```python
# utils/prompts.py
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

# Configurar environment
env = Environment(
    loader=FileSystemLoader('prompts'),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True
)

def render_prompt(template_name: str, **kwargs) -> str:
    \"\"\"
    Renderiza un template de prompt
    
    Args:
        template_name: Nombre del template (ej: 'tasks/summarize.jinja2')
        **kwargs: Variables para el template
    
    Returns:
        Prompt renderizado
    \"\"\"
    template = env.get_template(template_name)
    return template.render(**kwargs)
```

## Template base de sistema

```jinja2
{# prompts/base/system.jinja2 #}
Eres un asistente inteligente de {{ bot_name }}.

Tu objetivo es ayudar al usuario de manera útil, precisa y amigable.

{% if user_context %}
Información del usuario:
- Telegram ID: {{ user_context.telegram_id }}
- Username: @{{ user_context.username }}
- Nombre: {{ user_context.first_name }}
{% endif %}

{% include 'base/guidelines.jinja2' %}

{{ additional_instructions }}
```

## Template de tarea

```jinja2
{# prompts/tasks/summarize.jinja2 #}
{% include 'base/system.jinja2' %}

Tu tarea es resumir la siguiente conversación de manera concisa.

Conversación:
{% for msg in messages %}
{% if msg.role == 'user' %}
👤 Usuario: {{ msg.content }}
{% else %}
🤖 Asistente: {{ msg.content }}
{% endif %}
{% endfor %}

Proporciona un resumen en {{ language }} de máximo {{ max_words }} palabras.
```

## Uso en código

```python
from utils.prompts import render_prompt

# Renderizar prompt
prompt = render_prompt(
    'tasks/summarize.jinja2',
    bot_name="Mi Bot",
    user_context={
        'telegram_id': 12345,
        'username': 'usuario',
        'first_name': 'Juan'
    },
    messages=[
        {'role': 'user', 'content': 'Hola'},
        {'role': 'assistant', 'content': 'Hola, ¿en qué puedo ayudarte?'}
    ],
    language='español',
    max_words=50
)

# Enviar a LLM
response = await call_llm(prompt)
```

## Mejores prácticas

1. **Modularidad**: Usa `{% include %}` para reutilizar bloques comunes
2. **Versionado**: Mantén versiones de prompts importantes
3. **Variables tipadas**: Documenta qué variables espera cada template
4. **Defaults**: Usa filtros de Jinja2 para valores por defecto: `{{ variable | default('valor') }}`
5. **Testing**: Prueba diferentes combinaciones de variables

---
*Última actualización: {self.timestamp}*
"""
        
        self._write_file("PROMPTS.md", content)
    
    def _generate_llm_integration(self, info: Dict):
        """Genera LLM_INTEGRATION.md"""
        # Este archivo ya está bien definido en la SKILL.md
        # Lo copiamos directo
        content = """# Integración con LLMs

## Providers configurados

### OpenAI
- **Modelos**: gpt-4, gpt-4-turbo, gpt-3.5-turbo
- **Uso**: Conversaciones, análisis, generación

### Anthropic (Claude)
- **Modelos**: claude-sonnet-4-5, claude-opus-4-5
- **Uso**: Razonamiento complejo, análisis profundo

### LangChain
- **Chains**: ConversationChain, LLMChain
- **Memoria**: ConversationBufferMemory
- **Tools**: [Si usas agents]

## Patrón de llamada con reintentos

```python
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

# OpenAI
client_openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def call_openai(prompt: str, model: str = "gpt-4") -> str:
    try:
        response = await client_openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error OpenAI: {e}")
        raise

# Anthropic
client_anthropic = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

async def call_anthropic(prompt: str, model: str = "claude-sonnet-4-5") -> str:
    try:
        message = await client_anthropic.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        logger.error(f"Error Anthropic: {e}")
        raise
```

## Control de costos

```python
import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Antes de llamar
tokens = count_tokens(prompt)
if tokens > 8000:
    logger.warning(f"Prompt largo: {tokens} tokens")
```

---
*Última actualización generada automáticamente*
"""
        
        self._write_file("LLM_INTEGRATION.md", content)
    
    def _generate_config(self, info: Dict):
        """Genera CONFIG.md"""
        content = f"""# Configuración

## Variables de entorno (.env)

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=tu_token_aquí

# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Database
DATABASE_URL=mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+17+for+SQL+Server

# Configuración
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## Pydantic Settings

```python
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    
    # LLMs
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str = Field(..., env="ANTHROPIC_API_KEY")
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    
    # General
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Singleton
settings = Settings()
```

## Uso

```python
from config import settings

# En cualquier parte del código
token = settings.TELEGRAM_BOT_TOKEN
```

---
*Última actualización: {self.timestamp}*
"""
        
        self._write_file("CONFIG.md", content)
    
    def _generate_skills(self, info: Dict):
        """Genera SKILLS.md - versión resumida, la completa está en SKILL.md"""
        content = f"""# Skills del Bot

## telegram-handler
**Cuándo usar**: Crear nuevos comandos o callbacks

Ver templates completos en archivo principal SKILL.md

## prompt-engineering
**Cuándo usar**: Crear o modificar prompts modulares

Estructura modular con Jinja2 en carpeta `prompts/`

## database-operations
**Cuándo usar**: Crear modelos SQLAlchemy o queries

Patrón async con SQLAlchemy 2.0

## llm-integration
**Cuándo usar**: Integrar llamadas a LLMs

Con reintentos automáticos usando tenacity

---

**Para ver los templates completos de cada skill, consulta el archivo SKILL.md**

*Última actualización: {self.timestamp}*
"""
        
        self._write_file("SKILLS.md", content)
    
    def _write_file(self, filename: str, content: str):
        """Escribe archivo en contexto"""
        filepath = self.context_dir / filename
        filepath.write_text(content, encoding='utf-8')
        print(f"  ✓ {filename}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Genera contexto para bot de Telegram')
    parser.add_argument('--path', default='.', help='Ruta del proyecto')
    
    args = parser.parse_args()
    
    generator = PythonBotContextGenerator(args.path)
    generator.generate_all()
    
    print("\n✨ ¡Contexto generado!")
    print(f"\n📁 Ubicación: {generator.context_dir}")
    print("\n💡 Próximos pasos:")
    print("  1. Revisa INDEX.md")
    print("  2. Personaliza SKILLS.md con tus patrones")
    print("  3. Usa en Claude Code")


if __name__ == "__main__":
    main()
