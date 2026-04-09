# Iris Bot

Bot conversacional con LLM para Telegram. Permite a los empleados hacer consultas en lenguaje
natural sobre datos de negocio, políticas y procedimientos de la empresa.

## Inicio rápido

```bash
pip install -r requirements.txt
cp .env.example .env       # configurar con credenciales reales
python check_config.py     # verificar conexión a BD y token Telegram
python main.py             # arrancar el bot
```

Ver [docs/dev/setup.md](docs/dev/setup.md) para el setup completo.

## Documentación

La documentación está en `docs/` organizada en dos enfoques:

- **[docs/uso/](docs/uso/README.md)** — Para usuarios, administradores e integradores
- **[docs/codigo/](docs/codigo/README.md)** — Para desarrolladores que trabajan en el código
- **[docs/dev/](docs/dev/README.md)** — Para configurar el entorno de desarrollo

El índice completo está en **[docs/index.md](docs/index.md)**.

## GitFlow

- `master` — producción
- `develop` — integración activa
- `feature/*` — trabajo en progreso

Ver [docs/dev/gitflow.md](docs/dev/gitflow.md) para convenciones de commits y PR.
