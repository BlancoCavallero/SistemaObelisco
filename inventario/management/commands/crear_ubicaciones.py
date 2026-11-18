"""Create the initial warehouse layout.

Two stores: the one that serves the public and the showroom. Codes are neutral on
purpose: the category is data assigned to a position, never part of its code, so moving
furniture around does not force a renumbering.
"""

from django.core.management.base import BaseCommand

from inventario.models import Almacen, Posicion, Sector

ESQUEMA = {
    ("ALM-01", "Local Tres Lomas"): ["SEC-01", "SEC-02", "SEC-03"],
    ("ALM-02", "Exhibicion"): ["SEC-01", "SEC-02"],
}
POSICIONES_POR_SECTOR = 5


class Command(BaseCommand):
    help = "Crea los almacenes, sectores y posiciones iniciales. Es idempotente."

    def handle(self, *args, **opciones):
        creados = {"almacenes": 0, "sectores": 0, "posiciones": 0}

        for (codigo, nombre), sectores in ESQUEMA.items():
            almacen, nuevo = Almacen.objects.get_or_create(
                codigo=codigo, defaults={"nombre": nombre}
            )
            creados["almacenes"] += int(nuevo)

            for codigo_sector in sectores:
                sector, nuevo = Sector.objects.get_or_create(almacen=almacen, codigo=codigo_sector)
                creados["sectores"] += int(nuevo)

                for numero in range(1, POSICIONES_POR_SECTOR + 1):
                    _, nuevo = Posicion.objects.get_or_create(
                        sector=sector, codigo=f"POS-{numero:02d}"
                    )
                    creados["posiciones"] += int(nuevo)

        self.stdout.write(
            f"Almacenes creados: {creados['almacenes']} · "
            f"sectores: {creados['sectores']} · posiciones: {creados['posiciones']}"
        )
        self.stdout.write("Esquema: " + ", ".join(codigo for codigo, _ in ESQUEMA))
