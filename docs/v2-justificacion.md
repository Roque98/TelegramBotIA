# Por qué se migró a Iris Bot v2

Este documento explica las limitaciones que llevaron a reescribir el bot desde cero
y cómo cada decisión de diseño en v2 responde a un problema concreto de v1.

---

## Contexto

La primera versión del bot (`TelegramBotIA_GS`) fue construida como una prueba de concepto:
un asistente que recibía un mensaje, clasificaba su intención y generaba una respuesta.
Funcionó bien para consultas simples, pero mostró sus límites cuando los requerimientos
crecieron: más herramientas, más usuarios, distintos roles, trazabilidad de costos y
comportamientos diferenciados por área.

---

## Limitaciones de v1 y su solución en v2

### 1. El agente solo sabía hacer una cosa por mensaje

**Problema v1**: El flujo era lineal — clasifica → genera SQL o busca en Knowledge → responde.
Si la respuesta requería combinar información de dos fuentes, o hacer un cálculo sobre el resultado
de una consulta, el agente no podía hacerlo en un solo mensaje.

**Solución v2**: Se adoptó el paradigma **ReAct** (Reasoning + Acting). El agente razona paso a paso
y puede invocar múltiples herramientas en secuencia antes de dar la respuesta final. Por ejemplo:
puede consultar la BD, calcular un porcentaje sobre el resultado y formatearlo, todo en una sola
conversación.

---

### 2. Agregar una herramienta nueva requería modificar código

**Problema v1**: Las herramientas (`/ia`, `/alertas`) estaban implementadas como handlers de Telegram.
Añadir una nueva requería escribir código en varios archivos, hacer deploy y reiniciar el bot.

**Solución v2**: Las herramientas son clases independientes que se registran en un `ToolRegistry`.
El agente las descubre dinámicamente desde el catálogo `BotIAv2_Recurso` en BD.
Agregar una tool nueva es: crear la clase, registrarla en `factory.py`, insertar una fila en BD.
No hay que tocar handlers ni lógica del agente.

---

### 3. El comportamiento del agente era hardcoded

**Problema v1**: El system prompt, la temperatura, las instrucciones y los ejemplos vivían en
archivos de código (plantillas Jinja2). Ajustar el tono o el enfoque del bot requería
un pull request y un redeploy.

**Solución v2**: Cada agente está definido en la tabla `BotIAv2_AgenteDef`. El system prompt,
temperatura y máximo de iteraciones se editan directamente en BD. Los cambios toman efecto
en el siguiente mensaje, sin tocar código. El historial de versiones de cada prompt
se guarda automáticamente vía trigger.

---

### 4. No había memoria entre sesiones

**Problema v1**: Cada mensaje era independiente. El bot no recordaba que un usuario
había preguntado lo mismo ayer, ni sus preferencias, ni su contexto laboral.

**Solución v2**: Se implementó `UserMemoryProfiles` con tres capas de memoria:
- **Contexto laboral**: quién es el usuario y de qué área
- **Temas recientes**: sobre qué ha estado preguntando
- **Historial breve**: resumen de sus últimas interacciones

Además, los usuarios pueden guardar preferencias explícitas (`save_preference`):
alias, formato de respuesta preferido, idioma, etc.

---

### 5. Los permisos eran todo o nada por comando

**Problema v1**: Un usuario tenía permiso para `/alertas` o no lo tenía.
No había forma de decir "solo usuarios de Gerencia de Infraestructura pueden ver alertas críticas"
sin escribir código adicional.

**Solución v2**: El sistema SEC-01 introduce permisos por **entidad** con jerarquía de resolución:

```
usuario individual  →  override definitivo (puede denegar aunque el rol permita)
rol                 →  permisivo (si el rol permite, pasa)
gerencia            →  permisivo (si la gerencia permite, pasa)
dirección           →  permisivo
sin regla           →  denegado por defecto
```

Cada permiso puede tener fecha de expiración. Se administra desde BD sin tocar código.

---

### 6. No había visibilidad de costos ni de lo que hacía el agente

**Problema v1**: Se sabía si una operación fue exitosa o falló, pero no cuántos tokens consumió,
cuánto costó en USD, cuántos pasos dio el agente ni qué herramienta usó.

**Solución v2**: Se registran tres niveles de trazabilidad:

| Tabla | Qué guarda |
|-------|-----------|
| `BotIAv2_InteractionLogs` | Resumen del request: tokens, costo, latencia por etapa, agente usado |
| `BotIAv2_InteractionSteps` | Cada paso del loop ReAct: thought, tool, observación, tokens |
| `BotIAv2_CostSesiones` | Costo USD por sesión desglosado por modelo |
| `BotIAv2_AgentRouting` | Decisión del clasificador: qué agente eligió y con qué confianza |

Esto permite auditar exactamente qué hizo el bot, detectar abusos y controlar el gasto.

---

### 7. Un solo agente para todos los casos de uso

**Problema v1**: El mismo agente respondía consultas de datos, preguntas de RRHH, alertas
de monitoreo y conversación casual. Compartían el mismo prompt y la misma configuración,
lo que hacía difícil optimizar cada flujo sin afectar los otros.

**Solución v2**: Se implementó un sistema multi-agente con `IntentClassifier`.
Cada agente tiene su propio prompt, temperatura y conjunto de herramientas:

- **Agente de datos**: optimizado para SQL y análisis numérico
- **Agente de conocimiento**: orientado a buscar en la base institucional
- **Agente casual**: respuestas conversacionales sin tools
- **Generalista**: fallback cuando ningún agente especializado aplica

El clasificador elige el agente con base en la intención del mensaje. Si no encuentra
un agente adecuado, cae al generalista.

---

### 8. Todo el acceso a BD era SQL directo en el código

**Problema v1**: Los queries de autenticación, permisos y operaciones vivían como strings SQL
en los archivos Python. Cambiar la estructura de una tabla implicaba buscar en todo el código
dónde se usaba.

**Solución v2**: Se centralizó todo en **28 stored procedures** con prefijo homologado `BotIAv2_sp_*`.
El código Python solo llama `EXEC BotIAv2_sp_NombreDeProcedimiento @param = :valor`.
Los detalles de las tablas quedan encapsulados en el SP. Si cambia la estructura interna,
solo se actualiza el SP, no el código de la aplicación.

---

## Tabla resumen

| Área | V1 | V2 |
|------|----|----|
| Paradigma del agente | Clasificar → responder | ReAct: razonar → actuar → observar |
| Herramientas | 2 (hardcoded como comandos) | 10 (extensibles, registradas en BD) |
| Comportamiento configurable | Solo via código + deploy | System prompt y parámetros editables en BD |
| Memoria | Sin persistencia | Summaries + historial + preferencias |
| Permisos | Por comando, binario | Por recurso, entidad y jerarquía |
| Observabilidad | Log básico | Tokens, costos, pasos y ruteo registrados |
| Multi-agente | No | Sí, con clasificador de intención |
| Acceso a BD | SQL directo en código | 28 stored procedures homologados |
| Agentes en producción | 1 | N (configurable desde BD) |

---

## Lo que se mantuvo

No todo cambió. La base sólida de v1 se conservó:

- **python-telegram-bot** como framework de integración con Telegram
- **SQLAlchemy** como ORM y gestor de conexiones
- **Pydantic v2** para validación y configuración
- **Strategy pattern** para proveedores LLM (intercambiables)
- **Pool de conexiones** con reconexión automática y soporte multi-BD
- **Middlewares** de autenticación y logging sobre handlers de Telegram
- El concepto de `ToolRegistry` (mejorado y generalizado)
