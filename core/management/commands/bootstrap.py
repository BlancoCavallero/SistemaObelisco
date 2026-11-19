"""Deja el sistema listo para usarse, sin entrar por shell a ningun lado.

Hace dos cosas, las dos idempotentes:

1. Crea el primer administrador si no existe ninguno, a partir de
   DJANGO_SUPERUSER_USERNAME y DJANGO_SUPERUSER_PASSWORD.
2. Crea el esquema de almacenes si no hay ninguno.

Nunca cambia la contrasena de un usuario existente: si ya hay administradores, no toca
nada. Eso permite dejarlo en el arranque del contenedor sin miedo a un redeploy.
"""

import os

from django.core.management import call_command
from django.core.management.base import BaseCommand

from core.models import Rol, Usuario
from inventario.models import Almacen

VARIABLES = ("DJANGO_SUPERUSER_USERNAME", "DJANGO_SUPERUSER_PASSWORD")


def faltantes(entorno):
    """Variables del administrador que estan ausentes o vacias."""
    return [nombre for nombre in VARIABLES if not (entorno.get(nombre) or "").strip()]


class Command(BaseCommand):
    help = "Crea el primer administrador y el esquema de almacenes, si faltan."

    def handle(self, *args, **opciones):
        self._administrador()
        self._almacenes()

    def _administrador(self):
        if Usuario.objects.filter(is_superuser=True).exists():
            self.stdout.write("Ya hay un administrador: no se toca.")
            return

        sin_definir = faltantes(os.environ)
        if sin_definir:
            self.stdout.write(
                "Sin administradores y sin " + ", ".join(sin_definir) + ": no se crea nada."
            )
            return

        usuario = Usuario.objects.create_superuser(
            username=os.environ["DJANGO_SUPERUSER_USERNAME"].strip(),
            email=(os.environ.get("DJANGO_SUPERUSER_EMAIL") or "").strip(),
            password=os.environ["DJANGO_SUPERUSER_PASSWORD"],
        )
        usuario.rol = Rol.ADMIN
        usuario.save(update_fields=["rol"])
        self.stdout.write(self.style.SUCCESS(f"Administrador creado: {usuario.username}"))
        self.stdout.write(
            self.style.WARNING(
                "Cambia esa contrasena y quita DJANGO_SUPERUSER_PASSWORD del entorno: "
                "mientras este, cualquiera con acceso al servicio la puede leer."
            )
        )

    def _almacenes(self):
        if Almacen.objects.exists():
            self.stdout.write("El esquema de almacenes ya existe: no se toca.")
            return
        call_command("crear_ubicaciones", stdout=self.stdout)
