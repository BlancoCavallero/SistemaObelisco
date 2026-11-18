"""Sales. The price is frozen on each line; the consumer may be anonymous."""

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class Cliente(models.Model):
    """Customer record. The city is the routing key, not a mailing detail."""

    nombre = models.CharField(max_length=120)
    ciudad = models.CharField(max_length=80)
    direccion = models.CharField(max_length=200, blank=True, default="")
    telefono = models.CharField(max_length=40, blank=True, default="")
    habilitado_cuenta_corriente = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "cliente"
        verbose_name_plural = "clientes"

    def __str__(self):
        return f"{self.nombre} ({self.ciudad})"


class MedioPago(models.TextChoices):
    EFECTIVO = "efectivo", "Efectivo"
    TRANSFERENCIA = "transferencia", "Transferencia"
    TARJETA = "tarjeta", "Tarjeta"
    CUENTA_CORRIENTE = "cuenta_corriente", "Cuenta corriente"


class Venta(models.Model):
    """A sale, not a cart. Until it is confirmed nothing moves."""

    fecha = models.DateTimeField(default=timezone.now)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="ventas"
    )
    cliente = models.ForeignKey(
        Cliente, on_delete=models.PROTECT, null=True, blank=True, related_name="ventas"
    )
    medio_pago = models.CharField(max_length=32, choices=MedioPago.choices)
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal("0"))
    total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    confirmada = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-id"]
        verbose_name = "venta"
        verbose_name_plural = "ventas"

    def __str__(self):
        return f"Venta {self.pk} por ${self.total}"

    def subtotal(self):
        return sum(
            (linea.subtotal() for linea in self.lineas.all()), start=Decimal("0.00")
        )


class LineaVenta(models.Model):
    """One line. `precio_unitario` is a snapshot: it is never recalculated."""

    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="lineas")
    producto = models.ForeignKey(
        "catalogo.Producto", on_delete=models.PROTECT, related_name="lineas_venta"
    )
    cantidad = models.PositiveSmallIntegerField()
    precio_unitario = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        ordering = ["id"]
        verbose_name = "linea de venta"
        verbose_name_plural = "lineas de venta"

    def __str__(self):
        return f"{self.cantidad} x {self.producto_id}"

    def subtotal(self):
        return Decimal(self.cantidad) * Decimal(self.precio_unitario)
