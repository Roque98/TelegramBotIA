# Iris Bot — Documentación

Iris Bot (Amber) es un asistente virtual para Telegram impulsado por LLM. Permite a los empleados
de la empresa hacer consultas en lenguaje natural sobre datos de negocio, políticas internas y
procedimientos, sin necesidad de conocer SQL ni sistemas internos.

## Stack tecnológico

| Componente | Tecnología |
|------------|------------|
| Interfaz principal | Telegram Bot API |
| Interfaz secundaria | REST API (Flask) |
| Agente LLM | ReAct (Think-Act-Observe) |
| Modelos LLM | GPT-5.4-mini (loop) / GPT-5.4 (datos) |
| Base de datos | SQL Server (`abcmasplus`) |
| Lenguaje | Python 3.11+ async/await |
| Validación | Pydantic v2 |

---

## Migración desde v1

- [Por qué se migró a Iris Bot v2](v2-justificacion.md) — Limitaciones de la versión anterior y cómo las resuelve esta arquitectura

---

## Enfoques de documentación

### [Uso](uso/README.md) — Para usuarios, administradores e integradores

Para quienes operan o consumen el sistema sin necesidad de leer código:

- [Qué puede hacer el bot](uso/que-puede-hacer.md)
- [Guía de usuario Telegram](uso/guia-usuario-telegram.md)
- [Guía de administrador](uso/guia-administrador.md)
- [Guía del API REST](uso/guia-api.md)
- [Configuración y despliegue](uso/configuracion.md)

### [Código](codigo/README.md) — Para desarrolladores y mantenedores

Para quienes entienden, mantienen o extienden el código:

- [Arquitectura](codigo/arquitectura.md)
- [Flujos del sistema](codigo/flujos.md)
- [Agente ReAct](codigo/agente-react.md)
- [Sistema de tools](codigo/tools.md)
- [Pipeline y factory](codigo/pipeline.md)
- [Dominio](codigo/dominio.md)
- [Infraestructura](codigo/infraestructura.md)
- [Base de datos](codigo/base-de-datos.md)
- [Cómo extender el sistema](codigo/como-extender.md)

### [Dev](dev/README.md) — Para configurar el entorno de desarrollo

- [Setup local](dev/setup.md)
- [GitFlow del proyecto](dev/gitflow.md)
- [Testing](dev/testing.md)
