# Configuración y despliegue

---

## Variables de entorno

Creá un archivo `.env` en la raíz del proyecto basándote en `.env.example`.
Todas las variables son leídas por `src/config/settings.py` usando Pydantic Settings.

### Requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram (BotFather) | `7123456789:AAFxyz...` |
| `OPENAI_API_KEY` | API key de OpenAI | `sk-proj-...` |
| `DB_NAME` | Nombre de la base de datos | `abcmasplus` |
| `DB_USER` | Usuario de SQL Server | `sa` |
| `DB_PASSWORD` | Contraseña de SQL Server | `MiPassword123` |

### Opcionales con valores por defecto

| Variable | Default | Descripción |
|----------|---------|-------------|
| `DB_HOST` | `localhost` | Host de SQL Server |
| `DB_PORT` | `1433` | Puerto TCP/IP de SQL Server |
| `DB_INSTANCE` | *(vacío)* | Instancia nombrada (ej: `SQLEXPRESS`) |
| `DB_TYPE` | `mssql` | Motor: `mssql`, `mysql`, `postgresql` |
| `OPENAI_LOOP_MODEL` | `gpt-5.4-mini` | Modelo para el loop ReAct |
| `OPENAI_DATA_MODEL` | `gpt-5.4` | Modelo para generación de SQL |
| `LOG_LEVEL` | `INFO` | Nivel de logging: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `ENVIRONMENT` | `development` | Entorno: `development`, `production` |
| `RETRY_LLM_MAX_ATTEMPTS` | `3` | Reintentos máximos para llamadas al LLM |
| `RETRY_LLM_MIN_WAIT` | `2` | Espera mínima entre reintentos LLM (segundos) |
| `RETRY_LLM_MAX_WAIT` | `30` | Espera máxima entre reintentos LLM (segundos) |
| `RETRY_DB_MAX_ATTEMPTS` | `3` | Reintentos máximos para operaciones de BD |
| `RETRY_DB_MIN_WAIT` | `1` | Espera mínima entre reintentos BD (segundos) |
| `RETRY_DB_MAX_WAIT` | `15` | Espera máxima entre reintentos BD (segundos) |

### Ejemplo de `.env`

```dotenv
# Telegram
TELEGRAM_BOT_TOKEN=7123456789:AAFxyz_mi_token_del_bot

# OpenAI
OPENAI_API_KEY=sk-proj-mi_api_key_de_openai

# Base de datos (SQL Server con instancia nombrada)
DB_HOST=192.168.1.10
DB_INSTANCE=SQLEXPRESS
DB_NAME=abcmasplus
DB_USER=botuser
DB_PASSWORD=SecurePass123!

# Entorno
ENVIRONMENT=production
LOG_LEVEL=INFO
```

---

## Conexión a SQL Server

El driver requerido es **ODBC Driver 17 for SQL Server**.

### Instalar el driver (Windows)

Descargar e instalar desde Microsoft:
`Microsoft ODBC Driver 17 for SQL Server`

### Instalar el driver (Ubuntu/Debian)

```bash
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

### Verificar la conexión

```bash
python check_config.py
```

Este script verifica que todas las variables de entorno estén configuradas y que la
conexión a la base de datos sea exitosa.

---

## Arranque del bot

### Modo normal

```bash
# Activar virtualenv
source ~/.virtualenvs/GPT5-Cxk5mELR/Scripts/activate  # Windows
# o
source ~/.virtualenvs/GPT5-Cxk5mELR/bin/activate       # Linux/Mac

# Iniciar el bot
python main.py
```

### Modo desarrollo (hot reload)

```bash
python run_dev.py
```

El modo dev reinicia el bot automáticamente cuando detecta cambios en archivos `.py`.

### Iniciar solo el API REST

```bash
python -m src.api.chat_endpoint
```

Por defecto escucha en `localhost:5000`.

---

## Migraciones de base de datos

Los scripts de migración están en `database/migrations/`. Deben ejecutarse en orden:

```bash
# Listar migraciones disponibles
ls database/migrations/

# Ejecutar en SQL Server Management Studio o sqlcmd
sqlcmd -S servidor -d abcmasplus -i database/migrations/10_BotPermisos.sql
```

El orden recomendado para instalación desde cero:

```
01_initial_schema.sql
02_knowledge_base.sql
...
10_BotPermisos.sql
11_BotPermisos_DatosIniciales.sql
```

---

## Estructura del directorio

```
GPT5/
├── main.py                  ← Punto de entrada del bot
├── run_dev.py               ← Modo desarrollo
├── check_config.py          ← Verificación de configuración
├── .env                     ← Variables de entorno (no versionar)
├── .env.example             ← Plantilla de variables
├── requirements.txt         ← Dependencias Python
├── src/                     ← Código fuente
├── database/
│   └── migrations/          ← Scripts SQL de migración
├── scripts/                 ← Scripts de utilidad y prueba
├── tests/                   ← Tests unitarios
├── logs/                    ← Logs locales (si LOG_LEVEL=DEBUG)
└── docs/                    ← Esta documentación
```

---

**← Anterior** [Guía del API REST](guia-api.md) · [Índice](README.md)
