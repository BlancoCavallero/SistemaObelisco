"""Comprueba que la configuracion de produccion este completa y funcione.

Existe porque las dos fallas mas caras de este proyecto son silenciosas: sin
DATABASE_URL la app arranca con SQLite, y sin storage arranca guardando imagenes en el
disco del contenedor. En los dos casos funciona, responde y no guarda nada.

Uso:
    DEBUG=False SECRET_KEY=... DATABASE_URL=... manage.py verificar_configuracion
"""

import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

REQUERIDAS = (
    "SECRET_KEY",
    "DATABASE_URL",
    "AWS_ENDPOINT_URL_S3",
    "AWS_STORAGE_BUCKET_NAME",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_REGION",
)

OPCIONALES_POST_DEPLOY = ("ALLOWED_HOSTS", "CSRF_TRUSTED_ORIGINS")


def variables_faltantes(entorno):
    """Nombres requeridos que estan ausentes o vacios."""
    return [nombre for nombre in REQUERIDAS if not (entorno.get(nombre) or "").strip()]


class Command(BaseCommand):
    help = "Verifica variables, base de datos y almacenamiento antes de desplegar."

    def handle(self, *args, **opciones):
        fallas = []
        avisos = []

        self.stdout.write(self.style.MIGRATE_HEADING("1. Variables"))
        faltantes = variables_faltantes(os.environ)
        if faltantes:
            fallas.append("Faltan variables: " + ", ".join(faltantes))
            for nombre in faltantes:
                self.stdout.write(self.style.ERROR(f"   FALTA  {nombre}"))
        else:
            self.stdout.write(self.style.SUCCESS("   Todas las obligatorias estan"))
        for nombre in OPCIONALES_POST_DEPLOY:
            if not (os.environ.get(nombre) or "").strip():
                avisos.append(f"{nombre} vacia: solo es correcto antes del primer deploy")

        self.stdout.write(self.style.MIGRATE_HEADING("2. Base de datos"))
        motor = settings.DATABASES["default"]["ENGINE"]
        if motor.endswith("sqlite3"):
            fallas.append("La base es SQLite: falta DATABASE_URL o es invalida")
            self.stdout.write(self.style.ERROR("   SQLite: no sirve para produccion"))
        else:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("select current_database(), current_user, version()")
                    base, usuario, version = cursor.fetchone()
                    cursor.execute("select count(*) from information_schema.tables "
                                   "where table_schema='public'")
                    tablas = cursor.fetchone()[0]
                self.stdout.write(self.style.SUCCESS(f"   {base} como {usuario}"))
                self.stdout.write(f"   {version.split(',')[0]}")
                self.stdout.write(f"   tablas en public: {tablas}")
                if tablas == 0:
                    avisos.append("La base esta vacia: las migraciones corren al arrancar")
                opciones = settings.DATABASES["default"].get("OPTIONS", {})
                if opciones.get("sslmode"):
                    self.stdout.write(f"   sslmode={opciones['sslmode']}")
                else:
                    avisos.append("La conexion no fija sslmode")
            except Exception as error:  # noqa: BLE001 - se reporta, no se propaga
                fallas.append(f"No se pudo conectar a la base: {error}")
                self.stdout.write(self.style.ERROR(f"   {str(error)[:120]}"))

        self.stdout.write(self.style.MIGRATE_HEADING("3. Almacenamiento"))
        backend = settings.STORAGES["default"]["BACKEND"]
        if backend.endswith("FileSystemStorage"):
            fallas.append(
                "El almacenamiento es disco local: las imagenes se pierden en cada deploy"
            )
            self.stdout.write(self.style.ERROR("   FileSystemStorage: no sirve para produccion"))
        else:
            try:
                nombre = default_storage.save(
                    "verificacion/conexion.txt", ContentFile(b"ok")
                )
                with default_storage.open(nombre) as archivo:
                    contenido = archivo.read()
                default_storage.delete(nombre)
                if contenido != b"ok":
                    raise ValueError("se leyo un contenido distinto al escrito")
                self.stdout.write(self.style.SUCCESS(f"   {backend.split('.')[-1]} operativo"))
                self.stdout.write(f"   bucket: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '?')}")
                self.stdout.write("   se escribio, leyo y borro un archivo")
            except Exception as error:  # noqa: BLE001
                fallas.append(f"El almacenamiento no respondio: {error}")
                self.stdout.write(self.style.ERROR(f"   {str(error)[:120]}"))

        self.stdout.write("")
        for aviso in avisos:
            self.stdout.write(self.style.WARNING(f"AVISO: {aviso}"))

        if fallas:
            for falla in fallas:
                self.stderr.write(self.style.ERROR(f"FALLA: {falla}"))
            raise CommandError(f"{len(fallas)} problema(s) bloquean el deploy")

        self.stdout.write(self.style.SUCCESS("Todo listo para desplegar."))
