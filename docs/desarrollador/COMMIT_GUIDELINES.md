# Convenciones de Commits

Este proyecto sigue el estándar [Conventional Commits](https://www.conventionalcommits.org/).

---

## Formato

```
<tipo>(<alcance>): <descripción corta>

[cuerpo opcional]

[nota al pie opcional]
```

- **tipo**: categoría del cambio (obligatorio)
- **alcance**: área del código afectada (opcional)
- **descripción**: resumen conciso en presente imperativo, sin mayúscula inicial, sin punto final
- **cuerpo**: explicación del "por qué", no del "qué" (opcional)

---

## Tipos

| Tipo | Cuándo usarlo |
|------|---------------|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de bug |
| `refactor` | Cambio de código que no agrega ni corrige nada |
| `docs` | Cambios en documentación |
| `test` | Tests nuevos o modificados |
| `chore` | Tareas de mantenimiento (deps, configs) |
| `perf` | Mejora de rendimiento |
| `style` | Formato, espacios (no afecta lógica) |
| `ci` | CI/CD |
| `revert` | Revertir un commit anterior |

## Scopes del proyecto

| Scope | Área |
|-------|------|
| `agent` | `src/agents/` — ReActAgent, tools |
| `bot` | `src/bot/` — handlers de Telegram |
| `db` | `src/infra/database/` |
| `auth` | `src/domain/auth/` |
| `memory` | `src/domain/memory/` |
| `knowledge` | `src/domain/knowledge/` |
| `api` | `src/api/` — REST endpoint |
| `config` | `src/config/` |
| `prompts` | `src/agents/react/prompts.py` |

---

## Ejemplos

### Commit simple
```bash
git commit -m "feat(bot): agregar comando /estadisticas"
```

### Commit con cuerpo
```bash
git commit -m "fix(db): corregir timeout en consultas largas

El timeout de 15s era insuficiente para queries con múltiples JOINs.
Se aumenta a 60s y se agrega log de duración.

Fixes #123"
```

### Breaking change
```bash
git commit -m "feat(agent)!: cambiar schema de ReActResponse

BREAKING CHANGE: el campo 'response' ahora es 'final_answer'.
Actualizar todo código que deserialice ReActResponse."
```

---

## Buenas prácticas

- Escribir en presente imperativo: `agregar`, `corregir`, `actualizar` (no `agregado`, `agregué`)
- Máximo 50 caracteres en la descripción
- Un commit por cambio lógico — no mezclar features con refactors
- Nunca commitear `.env`, tokens, contraseñas ni bases de datos locales
- Usar `--amend` solo antes de hacer push

---

## Flujo estándar

```bash
git status                          # ver qué cambió
git add src/agents/react_agent.py   # agregar archivos específicos
git diff --staged                   # revisar lo que se va a commitear
git commit -m "feat(agent): ..."    # crear commit
git log --oneline -5                # verificar historial
git push                            # publicar
```
