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
