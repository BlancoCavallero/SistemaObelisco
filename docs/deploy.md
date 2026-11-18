# Deploy

Produccion corre en un contenedor unico: Django sirve la API, la sesion y el build de
React desde el mismo origen. Base en Neon, imagenes y backups en Cloudflare R2, deploy a
Cloud Run por GitHub Actions. **Costo: $0** dentro de los planes gratuitos.

## Lo que ya esta verificado

El contenedor se probo localmente contra Postgres 16 antes de escribir esta guia:

| Verificacion | Resultado |
|---|---|
| Migraciones al arrancar | OK |
| `GET /health/` | 200 con la version |
| `GET /` (SPA) | 200 |
| `GET /catalogo` (fallback del SPA) | 200 |
| `GET /api/catalogo/` | 200 |
| Assets con gzip | 242 KB → 75 KB |
| Login con CSRF detras de proxy | 400 con el mensaje correcto, o sea CSRF paso |
| Redirect a HTTPS | Activo, y se desactiva con `X-Forwarded-Proto: https` |

## Lo que solo puede hacer el dueno del repositorio

Son cuentas y secretos. El agente no las crea ni las recibe.

### 1. Base de datos (Neon, gratis) — verificado contra el servidor real

1. Crear un proyecto en <https://neon.tech>.
2. Copiar **dos** cadenas de conexion:
   - la del **pooler** (el host contiene `-pooler`) → `DATABASE_URL`
   - la **directa** → `DATABASE_URL_DIRECT`

> **No uses `neon init` ni `neon deploy`.** Esas instrucciones son para una app Node con
> `neon.ts`. Este proyecto es Django sobre Cloud Run y crea su propio esquema con
> migraciones al arrancar.

La cadena trae `?sslmode=require&channel_binding=require`. **Esos parametros se conservan:**
el parser los pasa como `OPTIONS` a psycopg. Perderlos degradaria la conexion a `prefer`,
que acepta texto plano si el servidor lo permite.

Verificado contra el servidor real: Neon corre **PostgreSQL 18.7** y Django conecta con
`sslmode=require` y `channel_binding=require` aplicados.

> Las dos son necesarias. `pg_dump` no funciona a traves del pooler y el backup fallaria
> en silencio.

### 2. Imagenes y backups — dos opciones, ambas S3

El proyecto soporta cualquier almacenamiento compatible con S3. Se elige por variables de
entorno, sin tocar codigo.

**Opcion A — Neon Object Storage** (misma cuenta que la base, sin cuenta nueva).
**Verificado**: se escribio, leyo y borro un archivo a traves de Django.

| Secret | De donde | Valor de este proyecto |
|---|---|---|
| `AWS_ENDPOINT_URL_S3` | Neon Console → Storage → el endpoint | `https://br-muddy-snow-be0mrchr.storage.c-9.us-east-2.aws.neon.tech` |
| `AWS_STORAGE_BUCKET_NAME` | Neon Console → Storage → Buckets | `uploads` |
| `AWS_ACCESS_KEY_ID` | Token generado en Storage → API keys | `nak_live_...` |
| `AWS_SECRET_ACCESS_KEY` | Se muestra una sola vez | `nsk_live_...` |
| `AWS_REGION` | La region del endpoint | `us-east-2` |

El bucket **no se inventa**: ya existe uno llamado `uploads` en la cuenta. Si hace falta
otro, `python -c "import boto3,os; boto3.client('s3',endpoint_url=os.environ['AWS_ENDPOINT_URL_S3'],region_name=os.environ['AWS_REGION']).create_bucket(Bucket='obelisco-media')"`
con las mismas credenciales en el entorno.

**Opcion B — Cloudflare R2**:

| Secret | De donde |
|---|---|
| `R2_ACCOUNT_ID` | Panel de R2 |
| `R2_BUCKET` | Bucket, por ejemplo `obelisco-media` |
| `R2_ACCESS_KEY_ID` | Token de API de R2 |
| `R2_SECRET_ACCESS_KEY` | Secreto del token |

> R2 pide tarjeta para activarse aunque el plan sea gratuito. Neon Storage usa la cuenta
> que ya tenes.
>
> **Sin ninguna de las dos, las imagenes se guardan en el disco del contenedor y
> desaparecen en cada deploy.** No falla: pierde datos.

### 3. Hosting (Cloud Run, gratis con tope)

1. Crear un proyecto en Google Cloud y **habilitar facturacion**. El consumo se queda en
   el nivel gratuito (2 M de requests por mes), pero la cuenta de facturacion es
   obligatoria. **Cloud Run no funciona sin tarjeta.**
2. Habilitar las APIs: Cloud Run, Artifact Registry, IAM.
3. Crear una cuenta de servicio con rol *Cloud Run Admin* y *Service Account User*.
4. Configurar Workload Identity Federation para GitHub, o crear una clave JSON.

> Sin tarjeta, el plan B es Render gratuito con el mismo codigo y la misma imagen. Se
> duerme a los 15 minutos: la primera venta del dia tarda 30–50 s.

### 4. Secretos en GitHub

Settings → Secrets and variables → Actions → **Secrets**:

| Secret | De donde sale |
|---|---|
| `DJANGO_SECRET_KEY` | `python -c "import secrets;print(secrets.token_urlsafe(64))"` · *el nombre del secret es DJANGO_SECRET_KEY, pero la app lo lee como `SECRET_KEY`; el workflow hace el mapeo* |
| `DATABASE_URL` | Neon, con pooler |
| `DATABASE_URL_DIRECT` | Neon, sin pooler |
| `ALLOWED_HOSTS` | El dominio de Cloud Run, **despues del primer deploy** |
| `CSRF_TRUSTED_ORIGINS` | `https://<dominio>` |
| `AWS_ENDPOINT_URL_S3` | Neon Storage u otro S3 |
| `AWS_STORAGE_BUCKET_NAME` | El bucket |
| `AWS_ACCESS_KEY_ID` | Credencial S3 |
| `AWS_SECRET_ACCESS_KEY` | Credencial S3 |
| `AWS_REGION` | `us-east-2` |
| *(o bien)* `R2_*` | Alternativa Cloudflare |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Google Cloud |
| `GCP_SERVICE_ACCOUNT` | Google Cloud |

**Variables** (no secretas):

| Variable | Valor |
|---|---|
| `DEPLOY_ENABLED` | `true` — sin esto el deploy se saltea y el CI queda verde |
| `BACKUP_ENABLED` | `true` — sin esto el backup diario se saltea |
| `GCP_REGION` | `us-central1` |

## Como se dispara

```
feat/*  →  PR  →  develop  →  CI verde  →  PR  →  main  →  release  →  deploy
```

El merge a `main` calcula la version desde los conventional commits, crea el tag, publica
el GitHub Release y recien despues despliega. `GET /health/` devuelve esa version, asi se
verifica que lo desplegado es lo que se etiqueto.

## Primer deploy, en orden

1. Cargar los secretos de Neon, Django y R2.
2. Dejar `DEPLOY_ENABLED` en `false` y mergear a `main`: se publica el release **sin**
   desplegar. Eso valida el versionado.
3. Poner `DEPLOY_ENABLED=true` y volver a mergear.
4. Copiar el dominio de Cloud Run y cargarlo en `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS`.
5. Crear el primer usuario administrador:
   ```bash
   gcloud run services proxy obelisco --region us-central1
   # en otra terminal
   python manage.py createsuperuser
   ```
6. Cargar la infraestructura minima:
   ```bash
   python manage.py crear_ubicaciones
   ```
7. Ejecutar el primer backup a mano: Actions → Backup → Run workflow.

## Lo que no esta verificado

- **El deploy real nunca corrio.** Todo lo de arriba es la configuracion; el primer
  deploy lo va a estrenar el dueno del repositorio.
- **La restauracion del backup nunca se probo.** Un backup sin restaurar es una
  esperanza. Hay que hacerlo una vez, a mano, antes de confiar en el.
