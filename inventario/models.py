"""Warehouse locations and the immutable movement ledger."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Almacen(models.Model):
    codigo = models.CharField(max_length=16, unique=True)
    nombre = models.CharField(max_length=64)

    class Meta:
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Sector(models.Model):
    """A physical sector. Its code must NOT encode the category.

    If the code says "MUE", it lies the day the furniture moves to another sector and
    forces a renumbering of exactly what was meant to be stable. The category is data
    assigned to a position, not the meaning of its code. See design D-02 / A14.
    """

    almacen = models.ForeignKey(Almacen, on_delete=models.PROTECT, related_name="sectores")
    codigo = models.CharField(max_length=16)

    class Meta:
        ordering = ["almacen__codigo", "codigo"]
        constraints = [
            models.UniqueConstraint(fields=["almacen", "codigo"], name="sector_unico_por_almacen")
        ]

    def __str__(self):
        return f"{self.almacen.codigo}/{self.codigo}"


class Posicion(models.Model):
    sector = models.ForeignKey(Sector, on_delete=models.PROTECT, related_name="posiciones")
    codigo = models.CharField(max_length=16)

    class Meta:
        ordering = ["sector__codigo", "codigo"]
        constraints = [
            models.UniqueConstraint(fields=["sector", "codigo"], name="posicion_unica_por_sector")
        ]

    def __str__(self):
        return f"{self.sector}/{self.codigo}"


class EstadoArticulo(models.TextChoices):
    """Whether the item is still boxed or already assembled and displayable.

    Furniture arrives flat-packed, so the same product can exist in two states. The
    total stock is unaffected by assembly; only this dimension changes.
    """

    EN_CAJA = "en_caja", "En caja"
    LISTO = "listo", "Listo para exhibir"


class TipoMovimiento(models.TextChoices):
    ENTRADA_COMPRA = "entrada_compra", "Entrada por compra"
    ENTRADA_INVENTARIO_INICIAL = "entrada_inventario_inicial", "Entrada por inventario inicial"
    ARMADO = "armado", "Armado"
    VENTA = "venta", "Venta"
    DEVOLUCION_CLIENTE = "devolucion_cliente", "Devolucion de cliente"
    DEVOLUCION_PROVEEDOR = "devolucion_proveedor", "Devolucion a proveedor"
    AJUSTE = "ajuste", "Ajuste"
    TRANSFERENCIA = "transferencia", "Transferencia"


class MovimientoQuerySet(models.QuerySet):
    def stock_por_producto(self):
        """Current stock per product id, derived from the ledger."""
        return self.values("producto").annotate(total=Sum("cantidad")).order_by()

    def stock_por_estado(self):
        """Stock split by product and state. The sum over states equals the total."""
        return self.values("producto", "estado").annotate(total=Sum("cantidad")).order_by()


class Movimiento(models.Model):
    """The single source of truth for stock. Append-only.

    A wrong movement is corrected with a compensating movement, never by editing or
    deleting it: that is what makes a future audit possible without a rewrite.
    """

    producto = models.ForeignKey(
        "catalogo.Producto", on_delete=models.PROTECT, related_name="movimientos"
    )
    cantidad = models.IntegerField()
    tipo = models.CharField(max_length=32, choices=TipoMovimiento.choices)
    estado = models.CharField(
        max_length=16, choices=EstadoArticulo.choices, default=EstadoArticulo.LISTO
    )
    fecha = models.DateTimeField(default=timezone.now)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="movimientos"
    )
    motivo = models.TextField(blank=True, default="")
    posicion = models.ForeignKey(
        Posicion, on_delete=models.PROTECT, null=True, blank=True, related_name="movimientos"
    )
    referencia = models.CharField(max_length=64, blank=True, default="")
    proveedor = models.ForeignKey(
        "proveedores.Proveedor",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="movimientos",
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    objects = MovimientoQuerySet.as_manager()

    class Meta:
        ordering = ["-fecha", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(cantidad=0), name="movimiento_cantidad_no_cero"
            )
        ]
        verbose_name = "movimiento"
        verbose_name_plural = "movimientos"

    def __str__(self):
        return f"{self.get_tipo_display()} {self.cantidad:+d} de {self.producto_id}"

    def save(self, *args, **kwargs):
        if self.cantidad == 0:
            raise ValidationError("La cantidad de un movimiento no puede ser cero.")
        if self.pk is not None and type(self).objects.filter(pk=self.pk).exists():
            raise ValidationError(
                "Un movimiento no se edita: se corrige con otro movimiento de ajuste."
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Un movimiento no se borra: se corrige con un ajuste.")
