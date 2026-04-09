# Documentación de Código

Esta sección está orientada a desarrolladores que necesitan entender, mantener o extender el sistema.
Asume familiaridad con Python async/await, patrones de diseño y SQL Server.

## Índice

| Documento | Qué cubre |
|-----------|-----------|
| [Arquitectura](arquitectura.md) | Las 5 capas del sistema, patrones de diseño, contratos clave |
| [Flujos del sistema](flujos.md) | Paso a paso: mensaje Telegram, request API, loop ReAct |
| [Agente ReAct](agente-react.md) | Cómo razona el LLM: prompts, scratchpad, filtrado de tools |
| [Sistema de tools](tools.md) | Las 8 tools disponibles, ToolRegistry, cómo crear nuevas |
| [Pipeline y factory](pipeline.md) | MainHandler, composición de dependencias, gateway |
| [Dominio](dominio.md) | Auth, Memory, Knowledge, Cost — lógica de negocio |
| [Infraestructura](infraestructura.md) | BD, observabilidad, eventos, utilidades |
| [Base de datos](base-de-datos.md) | Esquema completo de tablas `BotIAv2_*` y relaciones |
| [Cómo extender](como-extender.md) | Recetas: nueva tool, nuevo comando, nuevo dominio |

## Punto de entrada recomendado

Si es la primera vez que lees el código, el orden sugerido es:

1. [Arquitectura](arquitectura.md) — mapa general
2. [Flujos del sistema](flujos.md) — cómo fluye una consulta de punta a punta
3. [Agente ReAct](agente-react.md) — el corazón del sistema
4. El módulo específico que necesitas modificar
