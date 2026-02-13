# 📋 Iris Bot - Migración a Arquitectura ReAct

## 📝 Descripción
Migración del bot conversacional Iris desde una arquitectura monolítica (LLMAgent de 544 líneas) hacia una arquitectura moderna basada en un único agente ReAct (Reasoning + Acting) que razona paso a paso y ejecuta herramientas según la complejidad de cada consulta.

## 🏷️ Tipo de Proyecto
- Desarrollo
- Bot/Automatización
- API
- Base de Datos

## 📊 Status
- [x] ⚙️ En proceso

## 📈 Avance
- Tareas completadas / Total tareas: 2 / 47
- Porcentaje: 4%

## 📅 Cronología
- **Semana de inicio**: Semana 7 - 13/02/2024
- **Semana de fin**: En curso
- **Deadline crítico**: N/A

## 👥 Solicitantes

| Nombre | Correo | Área | Extensión/Celular |
|--------|--------|------|-------------------|
| Angel | [correo@ejemplo.com] | Desarrollo | N/A |

## 👨‍💻 Recursos Asignados

**Admin:**
- Angel - Tech Lead

**Desarrollo:**
- Claude - Asistente IA / Desarrollo

## 🔧 Actividades

### ✅ Realizadas
- ✔️ **Estructura de carpetas**: Creación de directorio `plan/` para documentación del proyecto
- ✔️ **Plan de migración**: Documentación consolidada en `PLAN_REACT_MIGRATION.md` con 6 fases y 47 tareas

### 📋 Por hacer
- ⏳ **Fase 1 - Foundation**: Implementar contratos base (BaseAgent, AgentResponse, UserContext, EventBus)
- ⏳ **Fase 2 - Tools**: Implementar sistema de herramientas (DatabaseTool, KnowledgeTool, CalculateTool)
- ⏳ **Fase 3 - ReAct Agent**: Implementar agente principal con loop Think-Act-Observe
- ⏳ **Fase 4 - Memory Service**: Implementar servicio de memoria para contexto de usuario
- ⏳ **Fase 5 - Integration**: Conectar con Telegram y sistema actual
- ⏳ **Fase 6 - Polish**: Observabilidad, métricas y optimización

## ⚠️ Impedimentos y Deadlines

### 🚧 Bloqueadores Activos
N/A - No hay bloqueadores activos

## 📦 Entregables
- [ ] 📖 **Documentación técnica**: [PLAN_REACT_MIGRATION.md](../../plan/PLAN_REACT_MIGRATION.md)
- [ ] 🔧 **TFS actualizado**: N/A
- [ ] 📅 **Planner actualizado**: N/A
- [ ] 📓 **OneNote actualizado**: Este documento
- [x] 📝 **CLAUDE.md configurado**: [CLAUDE.md](../../CLAUDE.md)

## 🔗 URLs

### 📊 Repositorio
- [GitHub - TelegramBotIA](https://github.com/Roque98/TelegramBotIA)

### 🖥️ Ramas Git
- `feature/react-agent-migration` - Rama principal de migración
- `feature/react-fase1-foundation` - Rama actual (Fase 1)

## 🔧 Información Técnica

### 🗄️ Objetos BD

**Tablas:**
- `UserMemoryProfiles`: Almacena resúmenes de memoria a largo plazo por usuario
- `LogOperaciones`: Registro de interacciones usuario-bot

**Stored Procedures:**
- N/A - Se usará ORM para acceso a datos

### 💻 Estructura de Código
```
src/agents/
├── base/           # Contratos base (BaseAgent, AgentResponse)
├── react/          # ReAct Agent (único agente)
└── tools/          # Herramientas (Database, Knowledge, Calculate)
```

### 🌐 Endpoints
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| POST | /api/chat | Endpoint de chat | Sí |

### 🖥️ Servidores/Deploy
- **Ambiente**: DEV
- **Servidor**: Local
- **Ruta**: D:\proyectos\gs\GPT5

### ⏰ Jobs
N/A - El bot responde bajo demanda

## 📋 Órdenes de Cambio

| OC | Descripción | Status | Fecha |
|----|-------------|--------|-------|
| N/A | Sin OCs registradas | - | - |

---

*Documento generado: 13/02/2024*
*Última actualización: 13/02/2024*
