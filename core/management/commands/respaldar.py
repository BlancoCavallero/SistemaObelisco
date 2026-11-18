"""Respaldo de la base al almacenamiento configurado.

Es la misma operacion que hace el workflow de backup, pero ejecutable desde cualquier
lado y sin esperar a que el workflow exista en la rama principal.
"""

import os
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError

PREFIJO = "backups"


def nombre_de_backup(momento=None):
    """Timestamp ordenable lexicograficamente, para poder podar por antiguedad."""
    momento = momento or datetime.now(UTC)
    return f"obelisco-{momento.strftime('%Y-%m-%dT%H-%M-%SZ')}.dump"


def a_conservar(nombres, conservar):
    """Cuales borrar: todos menos los `conservar` mas nuevos."""
    ordenados = sorted(nombres)
    if len(ordenados) <= conservar:
        return []
    return ordenados[: len(ordenados) - conservar]


class Command(BaseCommand):
    help = "Vuelca la base con pg_dump y sube el archivo al almacenamiento."

    def add_arguments(self, parser):
        parser.add_argument(
            "--conservar", type=int, default=30, help="Cuantos respaldos mantener (30)."
        )
        parser.add_argument(
            "--solo-local",
            action="store_true",
            help="Deja el archivo en disco sin subirlo al almacenamiento.",
        )

    def handle(self, *args, **opciones):
        # Un typo en --conservar no puede borrar todos los respaldos, incluido el que
        # se acaba de crear. La funcion a_conservar es literal; la guarda vive aca.
        if opciones["conservar"] < 1:
            raise CommandError("--conservar tiene que ser 1 o mas.")

        url = os.environ.get("DATABASE_URL_DIRECT")
        if not url:
            url = os.environ.get("DATABASE_URL")
            if not url:
                raise CommandError("Falta DATABASE_URL_DIRECT o DATABASE_URL en el entorno.")
            self.stdout.write(
                self.style.WARNING(
                    "Usando DATABASE_URL: si es la cadena con pooler, pg_dump puede fallar. "
                    "Neon entrega una cadena directa sin -pooler para esto."
                )
            )

        nombre = nombre_de_backup()
        destino = Path(tempfile.gettempdir()) / nombre

        self.stdout.write(f"Volcando a {destino} ...")
        resultado = subprocess.run(
            ["pg_dump", url, "--no-owner", "--no-privileges", "-Fc", "-f", str(destino)],
            capture_output=True,
            text=True,
            check=False,
        )
        if resultado.returncode != 0:
            raise CommandError(f"pg_dump fallo: {resultado.stderr.strip()[:300]}")

        tamano_mb = destino.stat().st_size / 1048576
        self.stdout.write(self.style.SUCCESS(f"Volcado listo: {tamano_mb:.1f} MB"))

        if opciones["solo_local"]:
            self.stdout.write(f"Archivo local: {destino}")
            return

        if settings.STORAGES["default"]["BACKEND"].endswith("FileSystemStorage"):
            raise CommandError(
                "El almacenamiento es disco local: subir el respaldo ahi no protege nada. "
                "Configura el storage S3 o usa --solo-local."
            )

        with destino.open("rb") as archivo:
            guardado = default_storage.save(f"{PREFIJO}/{nombre}", File(archivo))
        self.stdout.write(self.style.SUCCESS(f"Subido: {guardado}"))
        destino.unlink(missing_ok=True)

        _, archivos = default_storage.listdir(PREFIJO)
        sobrantes = a_conservar(
            [a for a in archivos if a.endswith(".dump")], opciones["conservar"]
        )
        for viejo in sobrantes:
            default_storage.delete(f"{PREFIJO}/{viejo}")
        self.stdout.write(
            f"Respaldos guardados: {len(archivos) - len(sobrantes)} "
            f"(se borraron {len(sobrantes)} por antiguedad)"
        )
