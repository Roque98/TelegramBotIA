# Agente de Base de Datos con Telegram

Bot de Telegram con capacidades de agente LLM para realizar consultas a bases de datos mediante lenguaje natural.

## Características

- Comunicación mediante Telegram
- Agente LLM que interpreta consultas en lenguaje natural
- Conexión a base de datos para ejecutar consultas
- Respuestas contextuales y conversacionales

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

Ver la carpeta `docs/` para documentación detallada sobre la estructura del proyecto y guías de uso.

## Estructura

Ver [docs/estructura.md](docs/estructura.md) para detalles sobre la organización del proyecto.

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

- **[COMMIT_GUIDELINES.md](COMMIT_GUIDELINES.md)**: Guía de commits y convenciones
- **[GITFLOW.md](GITFLOW.md)**: Estrategia completa de branches y versionado

## 🤝 Contribuir

1. Fork del proyecto
2. Crear feature branch desde `develop` (`git checkout -b feature/AmazingFeature`)
3. Commit con mensajes descriptivos siguiendo [Conventional Commits](COMMIT_GUIDELINES.md)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request hacia `develop`

## 📋 Versiones

- **v0.1.0-base**: Versión base/template del proyecto
- Ver [GITFLOW.md](GITFLOW.md) para información sobre versionado semántico
