# Sistema Obelisco

Sistema de stock para un negocio familiar multi-rubro: muebles, electrodomesticos,
decoracion, colchones, sillones, articulos de verano y oficina.

El relevamiento completo, las decisiones y el diseno estan en [`docs/relevamiento/`](docs/relevamiento/).

## Como correrlo

Con Docker (recomendado, igual que produccion):

```bash
docker compose up --build
```

Local, sin Docker:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
cp .env.example .env
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

Sin `DATABASE_URL` la aplicacion usa SQLite, para que los tests corran sin base externa.

## Tests y lint

```bash
.venv/bin/python -m pytest -q
.venv/bin/ruff check .
```

## Secrets del repositorio

El pipeline de CI corre sin configuracion. El deploy y el backup quedan **desactivados**
hasta que existan las variables de repositorio `DEPLOY_ENABLED=true` y `BACKUP_ENABLED=true`.

| Nombre | Uso |
|---|---|
| `DJANGO_SECRET_KEY` | Clave secreta de Django en produccion |
| `DATABASE_URL` | Cadena de conexion a Postgres **con pooler** (la usa la aplicacion) |
| `DATABASE_URL_DIRECT` | Cadena **sin pooler**, solo para el backup (`pg_dump` no funciona a traves del pooler) |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por coma |
| `R2_ACCOUNT_ID` | Cuenta de Cloudflare R2 |
| `R2_ACCESS_KEY_ID` | Credencial de R2 |
| `R2_SECRET_ACCESS_KEY` | Credencial de R2 |
| `R2_BUCKET` | Bucket donde viven las imagenes y los backups |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Identidad federada de GitHub hacia Google Cloud |
| `GCP_SERVICE_ACCOUNT` | Cuenta de servicio que despliega en Cloud Run |

Variables de repositorio (no secretas): `DEPLOY_ENABLED`, `BACKUP_ENABLED`, `GCP_REGION`.
