"""Product catalog. Identity is derived, never typed: this is what prevents duplicates."""

from decimal import ROUND_HALF_UP, Decimal

from django.db import models
from django.utils import timezone

COLORES = [
    ("blanco", "Blanco"),
    ("negro", "Negro"),
    ("gris", "Gris"),
    ("beige", "Beige"),
    ("marron", "Marron"),
    ("natural", "Natural"),
    ("rojo", "Rojo"),
    ("azul", "Azul"),
    ("verde", "Verde"),
    ("celeste", "Celeste"),
    ("bordo", "Bordo"),
    ("rosa", "Rosa"),
    ("amarillo", "Amarillo"),
    ("turquesa", "Turquesa"),
    ("multicolor", "Multicolor"),
]


class Categoria(models.Model):
    nombre = models.CharField(max_length=64, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "categoria"
        verbose_name_plural = "categorias"

    def __str__(self):
        return self.nombre


class TipoProducto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="tipos")
    nombre = models.CharField(max_length=96)

    class Meta:
        ordering = ["categoria__nombre", "nombre"]
        constraints = [
            models.UniqueConstraint(fields=["categoria", "nombre"], name="tipo_unico_por_categoria")
        ]
        verbose_name = "tipo de producto"
        verbose_name_plural = "tipos de producto"

    def __str__(self):
        return f"{self.categoria.nombre} / {self.nombre}"


class Producto(models.Model):
    """One row per article type, not per physical unit: identical items share stock.

    The visible name is derived from the attributes on purpose. If it were typed,
    "Sillon gris 180" and "Sillon Gris 1.80" would become two rows, stock would split
    in two, and nobody would know the real total.
    """

    tipo = models.ForeignKey(TipoProducto, on_delete=models.PROTECT, related_name="productos")
    color = models.CharField(max_length=32, choices=COLORES)
    alto_cm = models.PositiveSmallIntegerField()
    ancho_cm = models.PositiveSmallIntegerField()
    largo_cm = models.PositiveSmallIntegerField()
    modelo = models.CharField(max_length=64, blank=True, default="")
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["tipo__nombre", "color"]
        constraints = [
            models.UniqueConstraint(
                fields=["tipo", "color", "alto_cm", "ancho_cm", "largo_cm", "modelo"],
                name="producto_atributos_unicos",
            )
        ]
        verbose_name = "producto"
        verbose_name_plural = "productos"

    def __str__(self):
        return self.nombre

    @property
    def nombre(self):
        partes = [self.tipo.nombre, self.get_color_display(), self.medidas]
        if self.modelo.strip():
            partes.append(self.modelo.strip())
        return " - ".join(partes)

    @property
    def medidas(self):
        return f"{self.alto_cm}x{self.ancho_cm}x{self.largo_cm}"

    def costo_vigente(self, fecha=None):
        """Factory list cost in effect on `fecha` (default: today), or None."""
        fecha = fecha or timezone.localdate()
        return (
            self.precios_lista.filter(vigente_desde__lte=fecha)
            .order_by("-vigente_desde")
            .values_list("valor", flat=True)
            .first()
        )

    def precio_venta(self, fecha=None):
        """Cost x (1 + category margin), rounded to the nearest hundred.

        Never stored: it is computed from two versioned values so that changing the
        margin today cannot rewrite the price of yesterday's sale.
        """
        from core.models import Parametro

        costo = self.costo_vigente(fecha)
        if costo is None:
            return None

        margen = Parametro.margen_para(self.tipo.categoria.nombre, fecha)
        bruto = Decimal(costo) * (Decimal("1") + margen)
        # Decimal("1E2") has exponent 2: rounds to the nearest hundred. Decimal("100")
        # would have exponent 0 and round to the nearest unit, silently.
        return bruto.quantize(Decimal("1E2"), rounding=ROUND_HALF_UP)

    @property
    def id_visible(self):
        if self.pk is None:
            return None
        prefijo = self.tipo.categoria.nombre[:3].upper()
        return f"{prefijo}-{self.pk:04d}"


class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="imagenes")
    archivo = models.ImageField(upload_to="productos/%Y/%m/")
    orden = models.PositiveSmallIntegerField(default=0)
    principal = models.BooleanField(default=False)
    subida_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-principal", "orden"]
        verbose_name = "imagen de producto"
        verbose_name_plural = "imagenes de producto"

    def __str__(self):
        return f"Imagen de {self.producto_id}"


class PrecioLista(models.Model):
    """Factory list cost for a product, with an effective date.

    Rows are append-only: a new list means a new row, never an update. Rewriting the cost
    would silently change the price of every past sale, which is exactly the problem this
    table exists to avoid.
    """

    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="precios_lista")
    valor = models.DecimalField(max_digits=14, decimal_places=2)
    vigente_desde = models.DateField()
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-vigente_desde"]
        constraints = [
            models.UniqueConstraint(
                fields=["producto", "vigente_desde"], name="precio_lista_unico_por_fecha"
            )
        ]
        verbose_name = "precio de lista"
        verbose_name_plural = "precios de lista"

    def __str__(self):
        return f"{self.producto_id} ${self.valor} desde {self.vigente_desde}"
