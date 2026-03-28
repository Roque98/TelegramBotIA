# Documentación — IRIS Bot

> **Última actualización:** 2026-03-28
> **Arquitectura:** ReAct Agent activo

---

## Documentación Técnica

| Documento | Descripción |
|-----------|-------------|
| [estructura.md](estructura.md) | Árbol de directorios completo y variables de entorno |
| [SISTEMA_AUTENTICACION.md](SISTEMA_AUTENTICACION.md) | Sistema de registro, permisos y middleware auth |
| [CHAT_API_GUIDE.md](CHAT_API_GUIDE.md) | Guía de uso de la API REST con autenticación AES |
| [API_ENDPOINTS.md](API_ENDPOINTS.md) | Especificación de endpoints REST |
| [resumen.md](resumen.md) | Resumen ejecutivo del proyecto |

---

## Documentación de Desarrollo

| Documento | Descripción |
|-----------|-------------|
| [desarrollador/GUIA_DESARROLLADOR.md](desarrollador/GUIA_DESARROLLADOR.md) | Guía completa para contribuidores |
| [desarrollador/DIAGRAMA_FLUJO_ACTUAL.md](desarrollador/DIAGRAMA_FLUJO_ACTUAL.md) | Diagramas de flujo de la arquitectura ReAct |
| [desarrollador/COMMIT_GUIDELINES.md](desarrollador/COMMIT_GUIDELINES.md) | Convenciones de commits |
| [desarrollador/GITFLOW.md](desarrollador/GITFLOW.md) | Estrategia de branches y versionado |

---

## Contexto Vivo del Proyecto

Los archivos en `.claude/context/` reflejan el estado actual del código:

| Archivo | Qué contiene |
|---------|-------------|
| [INDEX.md](../.claude/context/INDEX.md) | Índice de módulos y flujo general |
| [ARCHITECTURE.md](../.claude/context/ARCHITECTURE.md) | Capas, patrones y flujos detallados |
| [AGENTS.md](../.claude/context/AGENTS.md) | ReActAgent, contratos base |
| [TOOLS.md](../.claude/context/TOOLS.md) | 5 tools disponibles y cómo crear nuevas |
| [HANDLERS.md](../.claude/context/HANDLERS.md) | Comandos Telegram registrados |
| [MEMORY.md](../.claude/context/MEMORY.md) | Sistema de memoria y contexto |
| [PROMPTS.md](../.claude/context/PROMPTS.md) | System prompt y schemas de respuesta |

---

## Inicio Rápido

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar entorno
cp .env.example .env
# Editar .env con tus credenciales

# Arrancar bot Telegram
python main.py

# Arrancar API REST (opcional)
python src/api/chat_endpoint.py
```

---

## Archivo Histórico

Documentos obsoletos (arquitectura anterior) en [`docs/archivo/`](archivo/).

