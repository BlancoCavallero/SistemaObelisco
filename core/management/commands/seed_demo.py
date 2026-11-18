"""Datos de demostracion para mirar la interfaz.

Solo desarrollo: crea un usuario con clave conocida y articulos con costo y stock.
Nunca debe correr contra una base real.
"""

from decimal import Decimal
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from catalogo.models import Categoria, ImagenProducto, PrecioLista, Producto, TipoProducto
from core.models import Usuario
from inventario.models import Almacen, Movimiento, Posicion
from ventas.models import Cliente

# (categoria, tipo, color, alto, ancho, largo, costo)
ARTICULOS = [
    ("Muebles", "Sillon 3 cuerpos", "gris", 85, 90, 180, "480000"),
    ("Muebles", "Sillon 2 cuerpos", "beige", 85, 90, 140, "360000"),
    ("Muebles", "Mesa ratona", "natural", 45, 60, 110, "145000"),
    ("Muebles", "Mesa de comedor", "marron", 75, 90, 160, "320000"),
    ("Muebles", "Silla de comedor", "negro", 95, 45, 50, "58000"),
    ("Muebles", "Placard 4 puertas", "blanco", 210, 60, 180, "420000"),
    ("Electrodomesticos", "Heladera no frost", "blanco", 170, 70, 70, "890000"),
    ("Electrodomesticos", "Lavarropas 8kg", "blanco", 85, 60, 60, "610000"),
    ("Electrodomesticos", "Microondas 25L", "negro", 30, 50, 40, "185000"),
    ("Blanqueria", "Juego de sabanas 2 plazas", "blanco", 30, 20, 25, "32000"),
    ("Blanqueria", "Acolchado 2 plazas", "gris", 40, 30, 30, "48000"),
    ("Verano", "Reposera plegable", "celeste", 60, 55, 90, "42000"),
    ("Verano", "Sombrilla 2,4m", "beige", 240, 20, 20, "68000"),
    ("Decoracion", "Lampara de pie", "natural", 160, 40, 40, "74000"),
    ("Oficina", "Escritorio 1,20m", "blanco", 75, 60, 120, "195000"),
]

PALETA = {
    "Muebles": ((243, 230, 212), (206, 184, 158)),
    "Electrodomesticos": ((227, 234, 240), (186, 200, 212)),
    "Blanqueria": ((247, 241, 230), (226, 213, 192)),
    "Verano": ((228, 240, 242), (186, 214, 219)),
    "Decoracion": ((240, 234, 226), (214, 200, 184)),
    "Oficina": ((236, 239, 241), (200, 208, 214)),
}


def _placeholder(nombre, categoria, archivo):
    """Retrato generico: sin fotos reales, el catalogo igual se puede mirar."""
    from PIL import Image, ImageDraw

    arriba, abajo = PALETA.get(categoria, ((240, 235, 228), (210, 200, 190)))
    alto, ancho = 800, 600
    imagen = Image.new("RGB", (ancho, alto))
    dibujo = ImageDraw.Draw(imagen)

    for y in range(alto):
        mezcla = y / alto
        color = tuple(int(arriba[i] + (abajo[i] - arriba[i]) * mezcla) for i in range(3))
        dibujo.line([(0, y), (ancho, y)], fill=color)

    # Silueta simple, no un dibujo del mueble.
    dibujo.rectangle(
        [ancho * 0.18, alto * 0.42, ancho * 0.82, alto * 0.78], outline=(150, 135, 118), width=3
    )
    dibujo.text((24, alto - 40), nombre[:44], fill=(120, 108, 95))

    buffer = BytesIO()
    imagen.save(buffer, format="JPEG", quality=82, optimize=True)
    return ContentFile(buffer.getvalue(), name=archivo)


class Command(BaseCommand):
    help = "Carga datos de demostracion y un usuario con clave conocida. Solo desarrollo."

    def add_arguments(self, parser):
        parser.add_argument("--clave", default="demo-1234")

    def handle(self, *args, **opciones):
        clave = opciones["clave"]

        admin, _ = Usuario.objects.get_or_create(
            username="demo", defaults={"rol": "admin", "first_name": "Demo"}
        )
        admin.set_password(clave)
        admin.is_staff = True
        admin.save()

        if not Almacen.objects.exists():
            from django.core.management import call_command

            call_command("crear_ubicaciones", stdout=self.stdout)

        almacen = Almacen.objects.get(codigo="ALM-01")
        posicion = Posicion.objects.filter(sector__almacen=almacen).first()

        Cliente.objects.get_or_create(
            nombre="Ana Perez", ciudad="Quenuma", defaults={"habilitado_cuenta_corriente": True}
        )

        creados = 0
        for categoria_nombre, tipo_nombre, color, alto, ancho, largo, costo in ARTICULOS:
            categoria, _ = Categoria.objects.get_or_create(nombre=categoria_nombre)
            tipo, _ = TipoProducto.objects.get_or_create(categoria=categoria, nombre=tipo_nombre)
            producto, nuevo = Producto.objects.get_or_create(
                tipo=tipo,
                color=color,
                alto_cm=alto,
                ancho_cm=ancho,
                largo_cm=largo,
                modelo="",
            )
            if not nuevo:
                continue
            creados += 1

            PrecioLista.objects.get_or_create(
                producto=producto,
                vigente_desde=timezone.localdate(),
                defaults={"valor": Decimal(costo)},
            )
            Movimiento.objects.create(
                producto=producto,
                usuario=admin,
                cantidad=6,
                tipo="entrada_inventario_inicial",
                posicion=posicion,
                motivo="Carga de demostracion",
            )
            archivo = f"{producto.id_visible.lower()}.jpg"
            ImagenProducto.objects.create(
                producto=producto,
                archivo=_placeholder(producto.nombre, categoria_nombre, archivo),
                principal=True,
            )

        media = Path(settings.MEDIA_ROOT)
        self.stdout.write(self.style.SUCCESS(f"Articulos creados: {creados}"))
        self.stdout.write(f"Usuario: demo / {clave}  (solo desarrollo)")
        self.stdout.write(f"Media: {media}")
