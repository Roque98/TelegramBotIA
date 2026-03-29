# GitFlow — Estrategia de Branches

---

## Estructura de ramas

```
master          ← producción (protegida)
│
└── develop     ← desarrollo activo (protegida)
    │
    ├── feature/*   ← nuevas funcionalidades
    ├── release/*   ← preparación de release
    └── hotfix/*    ← correcciones urgentes de producción
```

| Rama | Base | Merge a | Vida |
|------|------|---------|------|
| `feature/*` | `develop` | `develop` | Temporal |
| `release/*` | `develop` | `master` + `develop` | Temporal |
| `hotfix/*` | `master` | `master` + `develop` | Temporal |

---

## Nueva feature

```bash
# 1. Partir desde develop actualizado
git checkout develop
git pull origin develop
git checkout -b feature/nombre-descriptivo

# 2. Desarrollar con commits descriptivos
git add src/...
git commit -m "feat(scope): descripción"

# 3. Merge a develop
git checkout develop
git pull origin develop
git merge --no-ff feature/nombre-descriptivo
git push origin develop

# 4. Limpiar
git branch -d feature/nombre-descriptivo
```

## Preparar release

```bash
git checkout develop && git pull origin develop
git checkout -b release/v1.0.0

# Bump version, CHANGELOG, ajustes finales
git commit -m "chore(release): preparar v1.0.0"

# Merge a master + tag
git checkout master && git merge --no-ff release/v1.0.0
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin master && git push origin v1.0.0

# Sync a develop
git checkout develop && git merge --no-ff release/v1.0.0
git push origin develop

git branch -d release/v1.0.0
```

## Hotfix urgente

```bash
git checkout master && git pull origin master
git checkout -b hotfix/descripcion-bug

# Corregir
git commit -m "fix(scope): corrección urgente"

# Merge a master + tag
git checkout master && git merge --no-ff hotfix/descripcion-bug
git tag -a v1.0.1 -m "Hotfix v1.0.1"
git push origin master && git push origin v1.0.1

# Sync a develop
git checkout develop && git merge --no-ff hotfix/descripcion-bug
git push origin develop

git branch -d hotfix/descripcion-bug
```

---

## Versionado semántico

`MAJOR.MINOR.PATCH`

| Tipo de cambio | Ejemplo |
|----------------|---------|
| Bug fix / hotfix | `v1.2.3 → v1.2.4` |
| Nueva feature compatible | `v1.2.4 → v1.3.0` |
| Breaking change | `v1.3.0 → v2.0.0` |

---

## Comandos útiles

```bash
# Ver ramas y su estado
git branch -v
git branch --merged       # ramas ya mergeadas

# Limpiar ramas mergeadas (locales)
git branch --merged | grep -v "develop\|master" | xargs git branch -d

# Limpiar referencias remotas obsoletas
git fetch --prune

# Ver historial gráfico
git log --graph --oneline --all --decorate
```

---

## Protección de ramas (GitHub)

En **Settings → Branches**, configurar para `master` y `develop`:

- Require pull request reviews before merging
- Require status checks to pass
- Include administrators

---

## Referencias

- [A successful Git branching model](https://nvie.com/posts/a-successful-git-branching-model/)
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
