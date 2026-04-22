[Docs](../index.md) › [Uso](README.md) › Guía de usuario — Telegram

# Guía de usuario — Telegram

Esta guía explica cómo registrarse y usar el bot desde Telegram.

---

## Requisitos previos

- Tener Telegram instalado (móvil o desktop)
- Ser empleado activo con número de legajo
- Haber sido habilitado por el administrador del sistema

---

## Registro

El bot requiere autenticación antes de responder consultas. El proceso es:

### 1. Iniciar el bot

Buscá el bot en Telegram o abrí el link que te compartió el administrador.
Enviá el comando:

```
/start
```

Si tu cuenta no está registrada, el bot te indicará que uses `/register`.

### 2. Registrar tu cuenta

```
/register
```

El bot te pedirá tu número de legajo. Ingresalo como texto simple:

```
4521
```

Si el número existe en el sistema, recibirás un código de verificación de 6 dígitos
por el canal configurado (email o mensaje interno).

### 3. Verificar el código

```
/verify 482951
```

Reemplazá `482951` por el código que recibiste. Una vez verificado, tu cuenta queda
activa y podés empezar a hacer consultas.

Si el código venció o no lo recibiste:

```
/resend
```

---

## Comandos disponibles

| Comando | Descripción |
|---------|-------------|
| `/start` | Mensaje de bienvenida con ejemplos de consultas |
| `/help` | Guía de uso y funciones disponibles |
| `/ia <consulta>` | Consulta explícita al asistente |
| `/query <consulta>` | Alias de `/ia` |
| `/register` | Iniciar el registro de cuenta |
| `/verify <código>` | Verificar el código de activación |
| `/resend` | Reenviar código de verificación |
| `/cancel` | Cancelar operación en curso |

---

## Hacer consultas

No es necesario usar un comando especial. Podés escribir tu consulta directamente
como un mensaje de texto:

```
¿Cuántas ventas hubo ayer?
```

```
Dame el total facturado por sucursal este mes
```

```
¿Cuál es la política de devoluciones?
```

Iris procesará el mensaje y responderá con los datos o información solicitada.

Si preferís usar comando explícito:

```
/ia cuántos pedidos están pendientes de despacho
```

---

## Consejos para mejores resultados

**Sé específico con las fechas**

```
# Vago
¿Cuántas ventas hubo?

# Preciso
¿Cuántas ventas hubo en marzo de 2026?
```

**Especificá el filtro cuando sea relevante**

```
# Vago
¿Cuál es el stock?

# Preciso
¿Cuál es el stock actual del producto "Aceite 1L"?
```

**Para cálculos, dá los números exactos**

```
# Bueno
¿Cuánto es el 21% de IVA sobre $8.450?

# Mejor (el bot puede combinar con datos reales)
¿Cuál es el total de ventas de ayer con IVA incluido?
```

---

## Formato de respuestas

Iris usa formato Markdown de Telegram:

- **Negrita** para títulos de sección y valores clave
- _Cursiva_ para notas secundarias
- `código inline` para IDs y nombres de campo
- Bloques de código para SQL o estructuras de datos
- Listas para 3 o más elementos del mismo tipo

Las respuestas de datos siempre terminan con una oferta de seguimiento:
"¿Querés ver el detalle por producto o sucursal?"

---

## Solución de problemas

| Problema | Causa probable | Solución |
|----------|---------------|---------|
| El bot no responde | No estás registrado | Usá `/register` |
| "No tenés permisos" | Tu rol no tiene acceso a esa función | Contactar al administrador |
| Respuesta lenta | El LLM está procesando | Esperá unos segundos |
| Resultado incorrecto | La consulta fue ambigua | Reformulá con más detalle |
| Código de verificación no llegó | Email incorrecto en sistema | Contactar RRHH |

---

**← Anterior** [Qué puede hacer](que-puede-hacer.md) · [Índice](README.md) · **Siguiente →** [Guía de administrador](guia-administrador.md)
