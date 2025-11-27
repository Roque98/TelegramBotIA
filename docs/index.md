# Documentación del Proyecto - Agente de Base de Datos con Telegram

## Índice

1. [Introducción](#introducción)
2. [Estructura del Proyecto](estructura.md)
3. [Configuración](#configuración)
4. [Componentes Principales](#componentes-principales)
5. [Guías de Uso](#guías-de-uso)

---

## Introducción

Este proyecto implementa un bot de Telegram que funciona como un agente inteligente capaz de:
- Interpretar consultas en lenguaje natural
- Traducirlas a consultas SQL
- Ejecutarlas en una base de datos
- Devolver los resultados de manera conversacional

## Configuración

### Variables de Entorno

Copiar `.env.example` a `.env` y configurar:

- **TELEGRAM_BOT_TOKEN**: Token del bot de Telegram (obtener de @BotFather)
- **OPENAI_API_KEY** o **ANTHROPIC_API_KEY**: Clave API del LLM
- **DB_***: Credenciales de la base de datos

### Instalación de Dependencias

```bash
pip install -r requirements.txt
```

## Componentes Principales

### 1. Bot de Telegram (`src/bot/`)
Maneja la comunicación con los usuarios a través de Telegram.

### 2. Agente LLM (`src/agent/`)
Interpreta las consultas del usuario y las convierte en consultas SQL.

### 3. Base de Datos (`src/database/`)
Gestiona las conexiones y ejecución de consultas en la base de datos.

### 4. Configuración (`src/config/`)
Centraliza la configuración del proyecto.

## Guías de Uso

### Iniciar el Bot

```bash
python main.py
```

### Ejemplo de Conversación

```
Usuario: ¿Cuántos usuarios tenemos registrados?
Bot: Consultando la base de datos...
Bot: Actualmente hay 1,234 usuarios registrados en el sistema.

Usuario: Muéstrame los 5 últimos usuarios
Bot: Aquí están los 5 últimos usuarios registrados:
     1. Juan Pérez - 2024-01-15
     2. María González - 2024-01-14
     ...
```

---

## Enlaces Útiles

- [Estructura del Proyecto](estructura.md) - Detalles sobre la organización de carpetas
- [README principal](../README.md) - Información general del proyecto
