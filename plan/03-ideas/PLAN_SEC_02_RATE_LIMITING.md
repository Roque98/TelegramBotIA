# PLAN: Rate limiting en verificación de cuenta

> **Objetivo**: Proteger el código de verificación contra ataques de fuerza bruta
> **Rama**: `feature/sec-02-rate-limiting`
> **Prioridad**: 🔴 Crítica
> **Progreso**: 0% (0/5)

---

## Contexto

`src/auth/user_service.py` genera códigos de verificación de 6 dígitos (1,000,000 combinaciones). Con 5 intentos máximos (`MAX_VERIFICATION_ATTEMPTS = 5`) y sin backoff, un atacante puede:

- Crear múltiples cuentas de Telegram e intentar bruteforcear
- Hacer 5 intentos por segundo sin penalización de tiempo
- No hay expiración del bloqueo, pero tampoco mecanismo claro de desbloqueo

---

## Archivos involucrados

- `src/auth/user_service.py` — lógica de verificación
- `src/auth/user_repository.py` — queries de intentos y bloqueo
- `src/auth/user_entity.py` — posible campo `locked_until`
- `src/bot/handlers/registration_handlers.py` — mostrar mensajes de espera al usuario

---

## Tareas

- [ ] **2.1** Agregar campo `locked_until` (datetime) en la tabla de cuentas Telegram (migration SQL)
- [ ] **2.2** Implementar backoff exponencial en `user_service.py`:
  - Intento 1-2: sin espera
  - Intento 3: esperar 30 segundos
  - Intento 4: esperar 5 minutos
  - Intento 5: bloqueo de 24 horas
- [ ] **2.3** Actualizar `user_repository.py` con query para leer y escribir `locked_until`
- [ ] **2.4** En `registration_handlers.py` mostrar tiempo restante de bloqueo al usuario
- [ ] **2.5** Agregar tests para cada nivel de backoff

---

## Criterios de aceptación

- Un atacante no puede hacer más de 2 intentos por minuto sin penalización de tiempo
- El usuario ve claramente cuánto tiempo debe esperar antes de reintentar
- El bloqueo de 24h se registra en BD y persiste entre reinicios del bot
