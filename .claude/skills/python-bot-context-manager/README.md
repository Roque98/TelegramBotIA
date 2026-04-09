# Python Bot Context Manager 🤖

Skill para generar y mantener contexto estructurado de bots de Telegram con LLMs, reduciendo costos de tokens en Claude Code.

## 🎯 Diseñado para tu stack

- ✅ **python-telegram-bot** - Handlers, comandos, callbacks
- ✅ **OpenAI + Anthropic** - Múltiples LLMs
- ✅ **LangChain** - Chains y memoria
- ✅ **SQLAlchemy 2.0** - ORM async con SQL Server
- ✅ **Jinja2** - Sistema modular de prompts
- ✅ **Pydantic** - Configuración y validación

## 📦 Instalación rápida

```bash
# 1. Copiar al proyecto
cp -r python-bot-context-manager /ruta/tu/bot/.claude/skills/

# 2. Generar contexto
cd /ruta/tu/bot
python .claude/skills/python-bot-context-manager/scripts/generate_context.py

# 3. ¡Listo!
```

## 📁 Archivos generados

```
.claude/context/
├── INDEX.md              # Punto de entrada
├── ARCHITECTURE.md       # Stack y patrones
├── HANDLERS.md           # Comandos de Telegram
├── DATABASE.md           # Modelos SQLAlchemy
├── PROMPTS.md            # Sistema de prompts Jinja2
├── LLM_INTEGRATION.md    # OpenAI/Anthropic/LangChain
├── CONFIG.md             # Settings y .env
└── SKILLS.md             # Templates de código
```

## 🚀 Uso en Claude Code

### Crear un nuevo comando

```
User: Crea un comando /stats que muestre estadísticas del usuario usando la skill telegram-handler

Claude: [lee HANDLERS.md y SKILLS.md]
        [genera handler siguiendo tu patrón async]
```

### Crear un nuevo prompt

```
User: Crea un prompt para analizar el sentimiento de un mensaje usando la skill prompt-engineering

Claude: [lee PROMPTS.md]
        [crea template Jinja2 modular]
```

### Agregar modelo de DB

```
User: Crea un modelo Conversation con user_id, content y timestamp usando la skill database-operations

Claude: [lee DATABASE.md]
        [genera modelo SQLAlchemy async]
```

## 💡 Skills incluidas

### 1. telegram-handler
**Para**: Nuevos comandos, callbacks, conversaciones

**Template de comando**:
```python
async def comando_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        
        async with AsyncSessionLocal() as session:
            # DB operations
            pass
        
        await update.message.reply_text("✅ Respuesta")
        logger.info(f"Comando ejecutado: {user_id}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Error")
```

### 2. prompt-engineering
**Para**: Prompts modulares con Jinja2

**Template**:
```jinja2
{# prompts/tasks/mi_tarea.jinja2 #}
{% include 'base/system.jinja2' %}

Tu tarea: {{ task }}

Contexto del usuario:
{{ user_context }}

Responde en {{ language }}.
```

### 3. database-operations
**Para**: Modelos y queries SQLAlchemy

**Modelo**:
```python
class MiModelo(Base):
    __tablename__ = 'mi_tabla'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {'id': self.id, ...}
```

### 4. llm-integration
**Para**: Llamadas a OpenAI/Anthropic con reintentos

**Con reintentos**:
```python
@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=4, max=10))
async def call_llm(prompt: str) -> str:
    response = await client.chat.completions.create(...)
    return response.choices[0].message.content
```

## 📊 Lo que detecta automáticamente

El script analiza tu proyecto y detecta:

✅ **Dependencias** de requirements.txt  
✅ **Handlers** (funciones async con Update/Context)  
✅ **Modelos** SQLAlchemy (clases con \_\_tablename\_\_)  
✅ **Prompts** (archivos .jinja2, .j2 en carpeta prompts/)  
✅ **Configuración** de LLMs (OpenAI, Anthropic, LangChain)  

## 🔄 Actualización

Después de agregar nuevos handlers o modelos:

```bash
python .claude/skills/python-bot-context-manager/scripts/generate_context.py
```

O crea un script de actualización selectiva (ver proyecto .NET para inspiración).

## 📈 Ahorro esperado

- **Tokens**: 60-75% reducción por sesión
- **De**: ~12-15K tokens (mapeo completo)
- **A**: ~3-5K tokens (lectura selectiva)
- **Costo mensual**: ~70% menos

## 🎓 Ejemplo de flujo completo

### 1. Usuario pide crear comando de estadísticas

```
User: Crea un comando /stats que muestre:
      - Total de conversaciones del usuario
      - Promedio de mensajes por día
      - Último mensaje
      
      Usa las skills apropiadas
```

### 2. Claude lee el contexto

```
Claude: [lee INDEX.md → HANDLERS.md → DATABASE.md → SKILLS.md]
        [entiende estructura de tu proyecto]
        [conoce tus patrones de código]
```

### 3. Claude genera código completo

```python
# handlers/stats.py
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from loguru import logger
from database import AsyncSessionLocal
from database.queries import get_user_stats
from datetime import datetime

async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra estadísticas del usuario
    
    Usage: /stats
    """
    try:
        user_id = update.effective_user.id
        
        async with AsyncSessionLocal() as session:
            stats = await get_user_stats(session, user_id)
            
            if not stats:
                await update.message.reply_text("No hay datos disponibles")
                return
            
            message = f"""
📊 *Tus Estadísticas*

💬 Total conversaciones: {stats['total_conversations']}
📈 Promedio mensajes/día: {stats['avg_messages_per_day']:.1f}
🕒 Último mensaje: {stats['last_message_date']}
            """
            
            await update.message.reply_text(
                message,
                parse_mode="Markdown"
            )
            
        logger.info(f"/stats ejecutado por {user_id}")
        
    except Exception as e:
        logger.error(f"Error en /stats: {e}")
        await update.message.reply_text("⚠️ Error obteniendo estadísticas")

# Registrar
application.add_handler(CommandHandler("stats", stats_handler))
```

**¡Y también genera la query de DB!**

```python
# database/queries.py
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, Conversation
from datetime import datetime, timedelta

async def get_user_stats(session: AsyncSession, telegram_id: int):
    """Obtiene estadísticas del usuario"""
    
    # Total conversaciones
    total_result = await session.execute(
        select(func.count(Conversation.id))
        .join(User)
        .where(User.telegram_id == telegram_id)
    )
    total_conversations = total_result.scalar()
    
    # Promedio por día
    first_conv_result = await session.execute(
        select(func.min(Conversation.created_at))
        .join(User)
        .where(User.telegram_id == telegram_id)
    )
    first_date = first_conv_result.scalar()
    
    if first_date:
        days = (datetime.utcnow() - first_date).days or 1
        avg_per_day = total_conversations / days
    else:
        avg_per_day = 0
    
    # Último mensaje
    last_result = await session.execute(
        select(Conversation.created_at)
        .join(User)
        .where(User.telegram_id == telegram_id)
        .order_by(Conversation.created_at.desc())
        .limit(1)
    )
    last_date = last_result.scalar()
    
    return {
        'total_conversations': total_conversations,
        'avg_messages_per_day': avg_per_day,
        'last_message_date': last_date.strftime('%Y-%m-%d %H:%M') if last_date else 'N/A'
    }
```

## 🛠 Personalización

Los archivos generados son **puntos de partida**. Puedes editarlos para:

- Agregar más detalles de tu arquitectura
- Documentar flujos específicos de tu bot
- Crear skills personalizadas para tus casos de uso
- Agregar ejemplos de código específicos de tu dominio

## 📚 Archivos incluidos

- **SKILL.md** - Documentación completa de la skill
- **scripts/generate_context.py** - Generador de contexto
- **README.md** - Este archivo
- **python-bot-context-manager.skill** - Metadatos

## ⚡ Próximos pasos

1. ✅ Descarga e instala la skill
2. ✅ Genera el contexto de tu bot
3. ✅ Revisa y personaliza los archivos generados
4. ✅ Usa en Claude Code con frases como:
   - "Usa la skill telegram-handler para..."
   - "Según la arquitectura del proyecto..."
   - "Siguiendo los patrones en DATABASE.md..."

## 🤝 Contribuciones

Si mejoras esta skill para tu caso de uso, comparte tus mejoras.

---

**Desarrollado específicamente para**: Bots de Telegram con OpenAI, Anthropic, LangChain y SQLAlchemy  
**Inspirado en**: Optimización de contexto para LLMs
