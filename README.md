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

## Ramas y versionado

| Rama | Para que |
|---|---|
| `main` | Solo releases. Cada merge aca publica una version. |
| `develop` | Integracion. Todo el trabajo va aca. |
| `feat/*` | Trabajo en curso, se mergea a `develop` por PR. |

El flujo es: `feat/*` → PR → `develop` → CI verde → PR → `main` → **release automatico**.

La version sale de los mensajes de commit ([Conventional Commits](https://www.conventionalcommits.org/)),
nunca se escribe a mano:

| Commits desde el ultimo tag | Sube |
|---|---|
| `feat:` | minor (`0.2.0`) |
| `fix:`, `docs:`, `test:`, cualquier otro | patch (`0.1.1`) |
| `feat!:` o `BREAKING CHANGE:` en el cuerpo | major (`2.0.0`) |

Antes de `1.0.0` un cambio incompatible sube **minor**, no major: el proyecto todavia no
tiene contrato que romper. El calculo vive en `scripts/version.py` y tiene sus propios tests
(`tests/test_version.py`), para que el numero no dependa de una accion de terceros.

Al mergear a `main` el workflow `Release` calcula la version, crea el tag `vX.Y.Z`, publica
un GitHub Release y recien despues despliega. `GET /health/` devuelve la version que esta
corriendo, asi se verifica que lo desplegado es lo que se etiqueto.

## Quien empuja

**Autorizacion vigente (2026-11-18):** el agente puede publicar commits en **`develop`** en este
repositorio sin pedir permiso en cada uno.

**No incluye, y se sigue pidiendo:**

- publicar en `main`, mergear o abrir PRs
- forzar la actualizacion de una rama ya publicada (reescritura de historia)
- borrar ramas
- crear tags o releases (el release dispara el deploy)
- commitear secretos, credenciales o archivos que superen el limite de tamano

Recomendado: proteger `main` en GitHub exigiendo PR y CI verde. Asi el permiso de publicacion
no puede tocar la rama que publica versiones.

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
