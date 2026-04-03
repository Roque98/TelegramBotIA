# PLAN: Encriptación segura con estándares modernos

> **Objetivo**: Migrar el módulo de encriptación a parámetros criptográficos seguros
> **Rama**: `feature/sec-01-encriptacion`
> **Prioridad**: 🔴 Crítica
> **Progreso**: 0% (0/6)

---

## Contexto

`src/utils/encryption_util.py` usa parámetros heredados del sistema C# para mantener compatibilidad:

- **MD5** como algoritmo hash (obsoleto desde 2010)
- **2 iteraciones** PBKDF2 (moderno: mínimo 100,000)
- **IV estático** para AES-CBC (permite análisis de patrones entre mensajes)
- **Constantes hardcodeadas** en código fuente: `PASSWORD`, `SALT_VALUE`, `INITIAL_VECTOR`

Con 2 iteraciones PBKDF2-MD5, un atacante moderno puede bruteforcear la clave en milisegundos.

---

## Problema de compatibilidad

La encriptación actual **debe permanecer compatible** con el sistema C# existente que genera los tokens. Por eso el enfoque es:

1. Mantener la clase `Encrypt` actual (renombrada a `EncryptLegacy`) para validar tokens externos
2. Crear una nueva clase `EncryptSecure` para uso interno del bot (nuevos tokens generados por Python)
3. Mover las constantes a `.env`

---

## Archivos involucrados

- `src/utils/encryption_util.py` — refactorizar
- `src/bot/middleware/token_middleware.py` — usar nueva clase donde aplique
- `.env` / `.env.example` — agregar variables de configuración
- `src/config/settings.py` — leer nuevas variables

---

## Tareas

- [ ] **1.1** Leer código actual y documentar comportamiento exacto de compatibilidad C#
- [ ] **1.2** Mover `PASSWORD`, `SALT_VALUE`, `INITIAL_VECTOR` a `.env` y leerlos desde `settings.py`
- [ ] **1.3** Renombrar clase `Encrypt` → `EncryptLegacy` con docstring que explique que es solo para compatibilidad C#
- [ ] **1.4** Crear clase `EncryptSecure` con SHA256 + 100,000 iteraciones PBKDF2 + IV aleatorio por mensaje
- [ ] **1.5** Actualizar `token_middleware.py` para usar `EncryptLegacy` al validar tokens entrantes y `EncryptSecure` al generar tokens desde Python
- [ ] **1.6** Agregar tests unitarios para ambas clases

---

## Criterios de aceptación

- Las constantes criptográficas no están en código fuente
- `EncryptLegacy` sigue desencriptando correctamente tokens generados por el sistema C#
- `EncryptSecure` usa SHA256 + mínimo 100,000 iteraciones + IV aleatorio
- Tests pasan al 100%
