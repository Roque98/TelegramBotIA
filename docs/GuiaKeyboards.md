# 📱 Guía Visual de Keyboards del Bot

> Ejemplos visuales de cómo el usuario ve los keyboards en Telegram

---

## 🎹 Tipos de Keyboards Implementados

Hay **dos tipos** de keyboards en nuestro bot:

1. **Reply Keyboards** - Aparecen en la parte inferior, reemplazan el teclado del teléfono
2. **Inline Keyboards** - Aparecen como botones dentro del mensaje

---

## 1️⃣ Reply Keyboards

### ¿Cómo se ven?

Los **Reply Keyboards** aparecen en la **parte inferior de la pantalla**, donde normalmente está el teclado del teléfono.

```
┌─────────────────────────────────────┐
│  💬 Chat con el Bot                 │
├─────────────────────────────────────┤
│                                     │
│  Bot:                               │
│  ¡Hola Juan! 👋                     │
│                                     │
│  Soy tu asistente de base de datos │
│  inteligente...                     │
│                                     │
│  ¿En qué puedo ayudarte?            │
│                                     │
├─────────────────────────────────────┤
│ ┌─────────────┬─────────────┐       │  ← Keyboard aparece aquí
│ │ 📊 Estadí... │ ❓ Ayuda    │       │
│ ├─────────────┼─────────────┤       │
│ │ 📝 Ejemplos │ 🔧 Config   │       │
│ └─────────────┴─────────────┘       │
│ Escribe tu consulta...              │  ← Placeholder
└─────────────────────────────────────┘
```

### Ejemplo 1: Keyboard Principal (Main Keyboard)

**Código que lo genera:**
```python
from src.bot.keyboards import get_main_keyboard

keyboard = get_main_keyboard()
await update.message.reply_text(
    "¿En qué puedo ayudarte?",
    reply_markup=keyboard
)
```

**Lo que ve el usuario:**
```
┌──────────────────┬──────────────────┐
│  📊 Estadísticas │    ❓ Ayuda      │  ← Fila 1
├──────────────────┼──────────────────┤
│ 📝 Ejemplos de   │  🔧 Configuración│  ← Fila 2
│    consultas     │                  │
└──────────────────┴──────────────────┘
```

**Interacción:**
- Al tocar **"📊 Estadísticas"** → Se envía el texto "📊 Estadísticas" como mensaje
- Al tocar **"❓ Ayuda"** → Se envía el texto "❓ Ayuda" como mensaje
- El bot recibe estos textos y puede responder en consecuencia

---

### Ejemplo 2: Keyboard de Ejemplos

**Código que lo genera:**
```python
from src.bot.keyboards import get_examples_keyboard

keyboard = get_examples_keyboard()
await update.message.reply_text(
    "Selecciona un ejemplo:",
    reply_markup=keyboard
)
```

**Lo que ve el usuario:**
```
┌────────────────────────────────────┐
│  ¿Cuántos usuarios hay?            │  ← Botón 1
├────────────────────────────────────┤
│  Muéstrame los últimos 5 pedidos   │  ← Botón 2
├────────────────────────────────────┤
│  ¿Cuál es el producto más vendido? │  ← Botón 3
├────────────────────────────────────┤
│  Lista las ventas del último mes   │  ← Botón 4
├────────────────────────────────────┤
│  🔙 Volver al menú principal       │  ← Botón 5
└────────────────────────────────────┘
```

**Interacción:**
- Al tocar cualquier botón, se **envía el texto del botón** como mensaje
- El bot procesa esa consulta automáticamente
- **Ventaja:** El usuario no tiene que escribir, solo tocar

---

## 2️⃣ Inline Keyboards

### ¿Cómo se ven?

Los **Inline Keyboards** aparecen como **botones dentro del mensaje**, justo debajo del texto.

```
┌─────────────────────────────────────┐
│  💬 Chat con el Bot                 │
├─────────────────────────────────────┤
│  Bot:                               │
│  📊 Resultados encontrados: 50      │
│                                     │
│  1. Usuario: Juan - ID: 1           │
│  2. Usuario: María - ID: 2          │
│  ...                                │
│  10. Usuario: Pedro - ID: 10        │
│                                     │
│  ┌──────┬──────────┬──────────┐     │  ← Botones inline
│  │ ⏮️ 1 │ ◀️ Ant   │ 📄 1/5   │     │     dentro del
│  ├──────┼──────────┼──────────┤     │     mensaje
│  │ ▶️ Sig│ ⏭️ 5     │          │     │
│  └──────┴──────────┴──────────┘     │
│                                     │
├─────────────────────────────────────┤
│ Escribe un mensaje...               │
└─────────────────────────────────────┘
```

### Ejemplo 1: Paginación

**Código que lo genera:**
```python
from src.bot.keyboards import get_pagination_keyboard

keyboard = get_pagination_keyboard(
    current_page=1,
    total_pages=5,
    callback_prefix="page"
)

await update.message.reply_text(
    "📊 Resultados encontrados: 50\n\n"
    "1. Usuario: Juan...\n"
    "2. Usuario: María...\n",
    reply_markup=keyboard
)
```

**Lo que ve el usuario (página 1/5):**
```
Resultados encontrados: 50

1. Usuario: Juan - ID: 1
2. Usuario: María - ID: 2
...

┌──────────┬──────────┬──────────┬──────────┐
│ 📄 1/5   │ ▶️ Siguiente       │ ⏭️ Última│
└──────────┴────────────────────┴──────────┘
```

**Lo que ve el usuario (página 3/5):**
```
Resultados encontrados: 50

21. Usuario: Carlos - ID: 21
22. Usuario: Ana - ID: 22
...

┌──────┬──────────┬──────────┬──────────┬──────┐
│⏮️ 1ra│◀️ Ant    │ 📄 3/5   │▶️ Sig    │⏭️ 5ta│
└──────┴──────────┴──────────┴──────────┴──────┘
```

**Interacción:**
- Al tocar **"▶️ Siguiente"** → Se envía callback_data: `"page:4"`
- El bot recibe el callback y **actualiza el mensaje** con la página 4
- **NO se envía un mensaje nuevo**, solo se actualiza el existente
- **Ventaja:** Navegación fluida sin spam de mensajes

---

### Ejemplo 2: Confirmación

**Código que lo genera:**
```python
from src.bot.keyboards import get_confirmation_keyboard

keyboard = get_confirmation_keyboard(
    confirm_callback="delete:confirm",
    cancel_callback="delete:cancel"
)

await update.message.reply_text(
    "⚠️ ¿Estás seguro de eliminar este registro?",
    reply_markup=keyboard
)
```

**Lo que ve el usuario:**
```
⚠️ ¿Estás seguro de eliminar este registro?

┌────────────────┬────────────────┐
│ ✅ Confirmar   │  ❌ Cancelar   │
└────────────────┴────────────────┘
```

**Interacción:**
- Al tocar **"✅ Confirmar"** → callback_data: `"delete:confirm"`
- Al tocar **"❌ Cancelar"** → callback_data: `"delete:cancel"`
- El bot puede ejecutar la acción correspondiente

---

### Ejemplo 3: Menú Inline

**Código que lo genera:**
```python
from src.bot.keyboards import get_menu_keyboard

keyboard = get_menu_keyboard()

await update.message.reply_text(
    "📋 **Menú Principal**\n\nSelecciona una opción:",
    reply_markup=keyboard,
    parse_mode='Markdown'
)
```

**Lo que ve el usuario:**
```
📋 Menú Principal

Selecciona una opción:

┌────────────────┬────────────────┐
│ 📊 Estadísticas│   ❓ Ayuda     │
├────────────────┼────────────────┤
│ 📝 Ejemplos    │   🔧 Config    │
├────────────────┴────────────────┤
│       ℹ️ Acerca de              │
└─────────────────────────────────┘
```

**Interacción:**
- Cada botón envía un callback diferente: `"menu:stats"`, `"menu:help"`, etc.
- El bot puede responder con información específica

---

### Ejemplo 4: Botón de Volver

**Código que lo genera:**
```python
from src.bot.keyboards import get_back_button

keyboard = get_back_button(callback_data="menu:main")

await update.message.reply_text(
    "ℹ️ **Acerca del Bot**\n\n"
    "Versión 0.2.0-alpha\n"
    "Desarrollado con Python...",
    reply_markup=keyboard,
    parse_mode='Markdown'
)
```

**Lo que ve el usuario:**
```
ℹ️ Acerca del Bot

Versión 0.2.0-alpha
Desarrollado con Python...

┌─────────────┐
│  🔙 Volver  │
└─────────────┘
```

---

## 🔄 Comparación: Reply vs Inline

| Característica | Reply Keyboard | Inline Keyboard |
|----------------|----------------|-----------------|
| **Ubicación** | Parte inferior (reemplaza teclado) | Dentro del mensaje |
| **Tipo de acción** | Envía texto como mensaje | Envía callback_data silencioso |
| **Actualización** | No se puede actualizar | Se puede actualizar el mismo mensaje |
| **Visibilidad** | Siempre visible mientras esté activo | Solo visible en ese mensaje |
| **Uso común** | Menús permanentes, ejemplos | Paginación, confirmaciones, acciones |
| **Ejemplo** | Menú principal del bot | Botones "Anterior/Siguiente" |

---

## 📸 Ejemplo Completo: Flujo de Usuario

### 1. Usuario inicia el bot

```
Usuario: /start

Bot: ¡Hola Juan! 👋
     Soy tu asistente de base de datos...

     ¿En qué puedo ayudarte?

     ┌──────────────────┬──────────────────┐
     │  📊 Estadísticas │    ❓ Ayuda      │  ← Reply Keyboard
     ├──────────────────┼──────────────────┤     aparece abajo
     │ 📝 Ejemplos de   │  🔧 Configuración│
     │    consultas     │                  │
     └──────────────────┴──────────────────┘
```

### 2. Usuario toca "📝 Ejemplos de consultas"

```
Usuario: 📝 Ejemplos de consultas  ← Texto enviado automáticamente

Bot: Selecciona un ejemplo:

     ┌────────────────────────────────────┐
     │  ¿Cuántos usuarios hay?            │  ← Reply Keyboard
     ├────────────────────────────────────┤     cambió
     │  Muéstrame los últimos 5 pedidos   │
     ├────────────────────────────────────┤
     │  ¿Cuál es el producto más vendido? │
     ├────────────────────────────────────┤
     │  Lista las ventas del último mes   │
     ├────────────────────────────────────┤
     │  🔙 Volver al menú principal       │
     └────────────────────────────────────┘
```

### 3. Usuario toca "¿Cuántos usuarios hay?"

```
Usuario: ¿Cuántos usuarios hay?  ← Texto enviado automáticamente

Bot: (escribiendo...)  ← Indicador de typing

Bot: 📊 Resultados encontrados: 1

     UsuarioID: 145
     Nombre: Sistema
     ...

     ┌────────────────────────────────┐
     │  🔙 Volver a ejemplos          │  ← Inline Keyboard
     └────────────────────────────────┘     dentro del mensaje
```

### 4. Usuario escribe pregunta personalizada

```
Usuario: Muéstrame los usuarios creados hoy  ← Usuario escribe

Bot: (escribiendo...)

Bot: 📊 Resultados encontrados: 15

     1. Usuario: Juan - Creado: 10:30
     2. Usuario: María - Creado: 11:45
     ...
     10. Usuario: Pedro - Creado: 15:20

     ┌──────┬──────────┬──────────┬──────────┐
     │ 📄 1/2│ ▶️ Siguiente       │ ⏭️ Última│  ← Inline Keyboard
     └──────┴────────────────────┴──────────┘     para paginación
```

---

## 💡 Tips de Diseño de Keyboards

### ✅ Buenos Ejemplos

```python
# 1. Botones claros y concisos
┌────────────┬────────────┐
│ ✅ Aceptar │ ❌ Rechazar│  ← Claro y directo
└────────────┴────────────┘

# 2. Uso de emojis para mejorar UX
┌────────────────┐
│ 📊 Estadísticas│  ← Emoji ayuda a identificar rápido
│ ❓ Ayuda       │
│ 🔧 Config      │
└────────────────┘

# 3. Agrupación lógica
┌──────────┬──────────┐
│ ◀️ Ant   │ ▶️ Sig   │  ← Navegación junta
├──────────┴──────────┤
│    🔙 Volver        │  ← Acción separada
└─────────────────────┘
```

### ❌ Evitar

```python
# 1. Texto muy largo en botones
┌────────────────────────────────────────┐
│ Presiona aquí para ver las estadísti...│  ← Se corta
└────────────────────────────────────────┘

# 2. Demasiados botones
┌──────┬──────┬──────┬──────┬──────┐
│ Btn1 │ Btn2 │ Btn3 │ Btn4 │ Btn5 │  ← Confuso
├──────┼──────┼──────┼──────┼──────┤
│ Btn6 │ Btn7 │ Btn8 │ Btn9 │ Btn10│
└──────┴──────┴──────┴──────┴──────┘

# 3. Sin organización
┌──────────┬────────────┐
│ Ayuda    │ Anterior   │  ← No tiene sentido
├──────────┼────────────┤     la agrupación
│ Eliminar │ Siguiente  │
└──────────┴────────────┘
```

---

## 🎯 Cuándo Usar Cada Tipo

### Usa Reply Keyboards cuando:
- ✅ Necesitas un **menú permanente** (siempre disponible)
- ✅ Quieres **ejemplos de texto** que el usuario puede enviar
- ✅ El usuario necesita **escribir variaciones** del texto del botón
- ✅ Es una **opción principal** del bot

### Usa Inline Keyboards cuando:
- ✅ Necesitas **paginación** de resultados
- ✅ Quieres **confirmaciones** (Sí/No, Aceptar/Cancelar)
- ✅ La acción debe **actualizar el mensaje actual**
- ✅ Son **acciones contextuales** a un mensaje específico
- ✅ No quieres que el texto del botón aparezca en el chat

---

## 📝 Código de Ejemplo Completo

```python
from telegram import Update
from telegram.ext import ContextTypes
from src.bot.keyboards import (
    get_main_keyboard,
    get_examples_keyboard,
    get_pagination_keyboard
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start con keyboard principal."""
    keyboard = get_main_keyboard()

    await update.message.reply_text(
        "¡Hola! ¿En qué puedo ayudarte?",
        reply_markup=keyboard
    )

async def show_examples(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar ejemplos de consultas."""
    keyboard = get_examples_keyboard()

    await update.message.reply_text(
        "Selecciona un ejemplo o escribe tu propia consulta:",
        reply_markup=keyboard
    )

async def show_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar resultados con paginación."""
    keyboard = get_pagination_keyboard(
        current_page=1,
        total_pages=5,
        callback_prefix="results"
    )

    results = "1. Usuario: Juan\n2. Usuario: María\n..."

    await update.message.reply_text(
        f"📊 Resultados:\n\n{results}",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )
```

---

**¿Necesitas más ejemplos o quieres probar algún keyboard específico?**
