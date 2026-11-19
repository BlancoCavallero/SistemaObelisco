"""Settings driven by environment variables: one module for dev, CI and production."""

import os
from pathlib import Path
from urllib.parse import parse_qs, urlparse

BASE_DIR = Path(__file__).resolve().parent.parent


def env(name, default=None):
    return os.environ.get(name, default)


def parse_lista(raw, default=None):
    """Comma separated env var to list. An empty value falls back to `default`.

    This matters in production: an unset ALLOWED_HOSTS must not leave the app
    rejecting every request, which is what an empty list would do.
    """
    valores = [valor.strip() for valor in (raw or "").split(",") if valor.strip()]
    return valores or list(default or [])


def env_bool(name, default=False):
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


DEBUG = env_bool("DEBUG", False)
SECRET_KEY = env("SECRET_KEY", "dev-insecure-key-change-me")
ALLOWED_HOSTS = parse_lista(env("ALLOWED_HOSTS"), default=["*"])
CSRF_TRUSTED_ORIGINS = parse_lista(env("CSRF_TRUSTED_ORIGINS"))

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "storages",
    "core",
    "catalogo",
    "inventario",
    "ventas",
    "proveedores",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


def parse_database_url(url):
    """Turn a Postgres URL into a Django DATABASES entry.

    The query string is not decoration. Neon hands out `?sslmode=require&
    channel_binding=require`, and dropping it silently downgrades the connection:
    psycopg defaults to sslmode=prefer, which falls back to plaintext if the server
    allows it.
    """
    parsed = urlparse(url)
    opciones = {}
    for clave in ("sslmode", "channel_binding"):
        valor = parse_qs(parsed.query).get(clave)
        if valor:
            opciones[clave] = valor[-1]

    configuracion = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": parsed.path.lstrip("/") or "obelisco",
        "USER": parsed.username or "",
        "PASSWORD": parsed.password or "",
        "HOST": parsed.hostname or "",
        "PORT": str(parsed.port or ""),
        "CONN_MAX_AGE": 0,
    }
    if opciones:
        configuracion["OPTIONS"] = opciones
    return configuracion


def database_config():
    """Parse DATABASE_URL, falling back to SQLite so tests run without Docker."""
    url = env("DATABASE_URL")
    if not url:
        return {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
    return parse_database_url(url)


def s3_config(entorno):
    """Storage for a generic S3-compatible endpoint: Cloudflare R2 or Neon Storage.

    Both speak S3, so the only difference is the endpoint and the credential names.
    """
    endpoint = (
        f"https://{entorno['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com"
        if entorno.get("R2_ACCOUNT_ID")
        else entorno.get("AWS_ENDPOINT_URL_S3")
    )
    bucket = entorno.get("AWS_STORAGE_BUCKET_NAME") or entorno.get("R2_BUCKET")
    clave = entorno.get("R2_ACCESS_KEY_ID") or entorno.get("AWS_ACCESS_KEY_ID")
    secreto = entorno.get("R2_SECRET_ACCESS_KEY") or entorno.get("AWS_SECRET_ACCESS_KEY")

    if not (endpoint and bucket and clave and secreto):
        return None

    return {
        "AWS_S3_ENDPOINT_URL": endpoint,
        "AWS_STORAGE_BUCKET_NAME": bucket,
        "AWS_ACCESS_KEY_ID": clave,
        "AWS_SECRET_ACCESS_KEY": secreto,
        "AWS_S3_REGION_NAME": entorno.get("AWS_REGION") or "auto",
        "AWS_QUERYSTRING_AUTH": True,
        "AWS_DEFAULT_ACL": None,
    }


DATABASES = {"default": database_config()}

AUTH_USER_MODEL = "core.Usuario"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
]

LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Sessions stay open for 90 days on purpose: a login prompt between two sales makes
# people share one account and the audit trail dies. See design D-03.
SESSION_COOKIE_AGE = 60 * 60 * 24 * 90
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Vite already hashes its output. A manifest storage would hash it a second time and the
# index.html reference would break, because Django never rewrites that file.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

FRONTEND_DIST = Path(env("FRONTEND_DIST", BASE_DIR / "frontend" / "dist"))
if (FRONTEND_DIST / "assets").is_dir():
    STATICFILES_DIRS = [FRONTEND_DIST]

_almacenamiento = s3_config(os.environ)
if _almacenamiento:
    for _clave, _valor in _almacenamiento.items():
        globals()[_clave] = _valor
    STORAGES["default"] = {"BACKEND": "storages.backends.s3.S3Storage"}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Injected by the release workflow. "dev" means the code is not a release.
APP_VERSION = env("APP_VERSION", "dev")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": None,
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 0 if DEBUG else 31536000
