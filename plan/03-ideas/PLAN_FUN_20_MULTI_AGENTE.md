# PLAN: Sistema multi-agente con especialistas

> **Objetivo**: Implementar agentes especializados por dominio para mejorar calidad de respuestas
> **Rama**: `feature/fun-20-multi-agente`
> **Prioridad**: 🟢 Funcional
> **Progreso**: 0% (0/8)

---

## Contexto

El agente ReAct actual es generalista: responde preguntas de RRHH, IT, finanzas, consultas de BD, etc. con el mismo prompt y las mismas herramientas. Esto tiene limitaciones:

- El prompt del sistema se vuelve muy largo para cubrir todos los dominios
- Las herramientas disponibles no varían según el tipo de pregunta
- No hay especialización en terminología de cada dominio

La solución es un **orquestador** que clasifica la pregunta y la delega al agente especialista correcto.

---

## Arquitectura propuesta

```
Usuario: "¿Cuánto tiempo de vacaciones tengo disponible?"
          ↓
    OrchestratorAgent
    (clasifica: RRHH)
          ↓
    HRAgent (herramientas: DB de empleados, knowledge RRHH)
          ↓
    Respuesta especializada
```

### Agentes especialistas propuestos

| Agente | Dominio | Herramientas |
|--------|---------|-------------|
| `HRAgent` | RRHH, vacaciones, empleados | BD empleados + knowledge RRHH |
| `ITAgent` | Sistemas, software, accesos | BD sistemas + knowledge IT |
| `FinanceAgent` | Gastos, reembolsos, pagos | BD finanzas + knowledge finanzas |
| `GeneralAgent` | Preguntas generales | Todas las herramientas (actual) |

---

## Archivos involucrados

- `src/agents/` — nuevo subdirectorio `specialists/`
- `src/agents/react/agent.py` — base para agentes especialistas
- `src/agents/orchestrator/` — nuevo módulo orquestador
- `src/gateway/factory.py` — crear y configurar agentes especialistas
- `src/gateway/handler.py` — usar orquestador en lugar de agente único

---

## Tareas

- [ ] **20.1** Diseñar interfaz `BaseSpecialistAgent` con método `can_handle(query) -> float` (confianza 0-1)
- [ ] **20.2** Crear `OrchestratorAgent` que:
  - Recibe la query
  - Pregunta a cada agente su `can_handle()`
  - Delega al agente con mayor confianza
- [ ] **20.3** Implementar `HRAgent` con prompt especializado en RRHH y herramientas filtradas
- [ ] **20.4** Implementar `ITAgent` con prompt especializado en sistemas
- [ ] **20.5** Implementar `FinanceAgent` con prompt especializado en finanzas
- [ ] **20.6** Mantener `GeneralAgent` como fallback si ningún especialista tiene >60% de confianza
- [ ] **20.7** Actualizar `factory.py` para inicializar todos los agentes especialistas
- [ ] **20.8** Agregar tests del orquestador con queries de cada dominio

---

## Criterios de aceptación

- Una pregunta de RRHH es respondida por `HRAgent`, no por el agente generalista
- Si la pregunta no es reconocida, `GeneralAgent` responde como fallback
- El orquestador tarda menos de 200ms en clasificar y delegar
- Cada agente especialista tiene su propio prompt optimizado para su dominio
