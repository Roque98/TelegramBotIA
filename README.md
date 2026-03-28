# Agente de Base de Datos con Telegram

Bot de Telegram con capacidades de agente LLM para realizar consultas a bases de datos mediante lenguaje natural.

## Características

- Comunicación mediante Telegram
- Agente LLM que interpreta consultas en lenguaje natural
- Conexión a base de datos para ejecutar consultas
- Respuestas contextuales y conversacionales
- **Mensajes de estado progresivo** - Feedback visual en tiempo real del procesamiento

## Instalación

1. Clonar el repositorio
2. Crear entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Configurar variables de entorno:
   ```bash
   cp .env.example .env
   # Editar .env con tus credenciales
   ```

## Uso

```bash
python main.py
```

## Documentación

### Para Desarrolladores

**[docs/desarrollador/](docs/desarrollador/)** - Documentación completa para desarrolladores:

- **[GUIA_DESARROLLADOR.md](docs/desarrollador/GUIA_DESARROLLADOR.md)** - Guía completa del proyecto
  - Arquitectura y stack tecnológico
  - Componentes principales y flujos
  - Sistema de Tools y Knowledge Base
  - Patrones de diseño y testing
  - GitFlow y guía de contribución

- **[QUICK_START_TOOLS.md](docs/desarrollador/QUICK_START_TOOLS.md)** - Inicio rápido con el sistema de Tools
- **[TESTING_TOOLS.md](docs/desarrollador/TESTING_TOOLS.md)** - Guía de testing
- **[COMMIT_GUIDELINES.md](docs/desarrollador/COMMIT_GUIDELINES.md)** - Convenciones de commits
- **[GITFLOW.md](docs/desarrollador/GITFLOW.md)** - Estrategia de branches y versionado
- **[DIAGRAMA_FLUJO_ACTUAL.md](docs/desarrollador/DIAGRAMA_FLUJO_ACTUAL.md)** - Diagramas de flujo

### Planificación y Features

**[docs/futuros-features/](docs/futuros-features/)** - Roadmap y planificación:

- **[RESUMEN.md](docs/futuros-features/RESUMEN.md)** - Resumen de features completados y pendientes
- **[ROADMAP.md](docs/futuros-features/ROADMAP.md)** - Hoja de ruta del proyecto
- **[PENDIENTES.md](docs/futuros-features/PENDIENTES.md)** - Lista de TODOs priorizados
- **[PLAN_FASE3_TOOLS.md](docs/futuros-features/PLAN_FASE3_TOOLS.md)** - Plan del sistema de Tools
- **[PLAN_ORQUESTADOR_TOOLS.md](docs/futuros-features/PLAN_ORQUESTADOR_TOOLS.md)** - Plan del orquestador
- **[PLAN_KNOWLEDGE_BASE_RAG.md](docs/futuros-features/PLAN_KNOWLEDGE_BASE_RAG.md)** - Plan de Knowledge Base + RAG

### Documentación Técnica

- [docs/desarrollador/ESTRUCTURA_PROYECTO.md](docs/desarrollador/ESTRUCTURA_PROYECTO.md) - Estructura detallada del código
- [docs/modulos/SISTEMA_AUTENTICACION.md](docs/modulos/SISTEMA_AUTENTICACION.md) - Sistema de autenticación
- [docs/modulos/GUIA_KEYBOARDS.md](docs/modulos/GUIA_KEYBOARDS.md) - Guía de teclados de Telegram
- [docs/api/CHAT_API_GUIDE.md](docs/api/CHAT_API_GUIDE.md) - API REST e integración

## 🔄 Flujo de Trabajo (GitFlow)

Este proyecto utiliza GitFlow para el manejo de branches y versiones.

### Ramas Principales

- **`master`**: Código en producción, protegida
- **`develop`**: Desarrollo activo, donde se integran las features

### Trabajar en el Proyecto

```bash
# 1. Clonar el repositorio
git clone https://github.com/Roque98/TelegramBotIA.git
cd TelegramBotIA

# 2. Crear feature desde develop
git checkout develop
git pull origin develop
git checkout -b feature/mi-nueva-funcionalidad

# 3. Hacer cambios y commits (seguir Conventional Commits)
git add .
git commit -m "feat(bot): agregar nueva funcionalidad"

# 4. Push y crear Pull Request
git push origin feature/mi-nueva-funcionalidad
```

### Usar como Template/Base

Esta versión está etiquetada como `v0.1.0-base` y puede usarse como template:

```bash
# Opción 1: Comenzar desde la versión base
git clone https://github.com/Roque98/TelegramBotIA.git
git checkout v0.1.0-base
git checkout -b develop-mi-proyecto

# Opción 2: Fork del repositorio en GitHub
```

### Documentación Completa

- **[COMMIT_GUIDELINES.md](docs/desarrollador/COMMIT_GUIDELINES.md)**: Guía de commits y convenciones
- **[GITFLOW.md](docs/desarrollador/GITFLOW.md)**: Estrategia completa de branches y versionado

## 🤝 Contribuir

1. Fork del proyecto
2. Crear feature branch desde `develop` (`git checkout -b feature/AmazingFeature`)
3. Commit con mensajes descriptivos siguiendo [Conventional Commits](docs/desarrollador/COMMIT_GUIDELINES.md)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request hacia `develop`

## 📋 Versiones

- **v0.1.0-base**: Versión base/template del proyecto
- Ver [GITFLOW.md](docs/desarrollador/GITFLOW.md) para información sobre versionado semántico
