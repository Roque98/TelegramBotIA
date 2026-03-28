# Documentación — IRIS Bot

> **Última actualización:** 2026-03-28
> **Arquitectura:** ReAct Agent activo

---

## Inicio rápido

```bash
pip install -r requirements.txt
cp .env.example .env   # editar con tus credenciales
python main.py         # bot Telegram
python src/api/chat_endpoint.py  # API REST (opcional)
```

---

## `docs/api/` — API REST e integración

| Documento | Descripción |
|-----------|-------------|
| [CHAT_API_GUIDE.md](api/CHAT_API_GUIDE.md) | Guía completa de integración con el API REST |
| [API_ENDPOINTS.md](api/API_ENDPOINTS.md) | Especificación de endpoints |
| [ENCRYPTION_COMPATIBILITY.md](api/ENCRYPTION_COMPATIBILITY.md) | Encriptación AES compatible con C# legacy |
| [GENERAR_TOKENS_PLATAFORMA.md](api/GENERAR_TOKENS_PLATAFORMA.md) | Cómo generar tokens desde tu plataforma C# |
| [USO_DESENCRIPTACION.md](api/USO_DESENCRIPTACION.md) | Script CLI para encriptar/desencriptar |

---

## `docs/modulos/` — Módulos del bot

| Documento | Descripción |
|-----------|-------------|
| [SISTEMA_AUTENTICACION.md](modulos/SISTEMA_AUTENTICACION.md) | Registro, verificación y permisos por rol |
| [KNOWLEDGE_BASE_PERMISSIONS.md](modulos/KNOWLEDGE_BASE_PERMISSIONS.md) | Control de acceso a la base de conocimiento |
| [GUIA_KEYBOARDS.md](modulos/GUIA_KEYBOARDS.md) | Keyboards de Telegram (reply e inline) |

---

## `docs/desarrollador/` — Para contribuidores

| Documento | Descripción |
|-----------|-------------|
| [GUIA_DESARROLLADOR.md](desarrollador/GUIA_DESARROLLADOR.md) | Guía completa del proyecto |
| [ESTRUCTURA_PROYECTO.md](desarrollador/ESTRUCTURA_PROYECTO.md) | Árbol de directorios y módulos |
| [DIAGRAMA_FLUJO_ACTUAL.md](desarrollador/DIAGRAMA_FLUJO_ACTUAL.md) | Flujos de la arquitectura ReAct |
| [QUICK_START_TOOLS.md](desarrollador/QUICK_START_TOOLS.md) | Cómo usar y crear tools |
| [TESTING_TOOLS.md](desarrollador/TESTING_TOOLS.md) | Guía de testing con pytest |
| [PROMPTS_BEST_PRACTICES.md](desarrollador/PROMPTS_BEST_PRACTICES.md) | Buenas prácticas para el system prompt |
| [COMMIT_GUIDELINES.md](desarrollador/COMMIT_GUIDELINES.md) | Convenciones de commits |
| [GITFLOW.md](desarrollador/GITFLOW.md) | Estrategia de branches y versionado |

---

## `docs/onenote/` — Historial de progreso

Snapshots de avance del proyecto en cada milestone.

---

## Contexto vivo (`.claude/context/`)

Archivos que Claude lee al inicio de cada sesión — siempre actualizados con el código real:

| Archivo | Qué contiene |
|---------|-------------|
| [INDEX.md](../.claude/context/INDEX.md) | Índice de módulos y flujo general |
| [ARCHITECTURE.md](../.claude/context/ARCHITECTURE.md) | Capas, patrones y flujos detallados |
| [AGENTS.md](../.claude/context/AGENTS.md) | ReActAgent y contratos base |
| [TOOLS.md](../.claude/context/TOOLS.md) | 5 tools disponibles |
| [HANDLERS.md](../.claude/context/HANDLERS.md) | Comandos Telegram registrados |
| [MEMORY.md](../.claude/context/MEMORY.md) | Sistema de memoria y contexto |
| [PROMPTS.md](../.claude/context/PROMPTS.md) | System prompt y schemas |

---

## `docs/archivo/` — Histórico

Documentos de versiones anteriores del proyecto (arquitectura pre-ReAct, planes completados, etc.).
