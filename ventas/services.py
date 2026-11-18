"""Confirming a sale: validate stock, freeze the total and move the ledger."""

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from core.models import Parametro
from inventario.models import Movimiento, TipoMovimiento
from inventario.stock import stock_de


def _descuento(medio_pago, fecha):
    if medio_pago != "efectivo":
        return Decimal("0")
    vigente = Parametro.valor_vigente("descuento_efectivo", fecha) or {}
    return Decimal(str(vigente.get("porcentaje", 0)))


@transaction.atomic
def confirmar_venta(venta):
    """Confirm a sale. Idempotence is not allowed: a sale is confirmed once."""
    if venta.confirmada:
        raise ValueError("Esta venta ya fue confirmada.")

    lineas = list(venta.lineas.select_related("producto"))
    if not lineas:
        raise ValueError("Una venta necesita al menos una linea.")

    if venta.medio_pago == "cuenta_corriente":
        if venta.cliente is None:
            raise ValueError("La cuenta corriente necesita un cliente.")
        if not venta.cliente.habilitado_cuenta_corriente:
            raise ValueError("Ese cliente no esta habilitado para cuenta corriente.")

    for linea in lineas:
        disponible = stock_de(linea.producto)
        if linea.cantidad > disponible:
            raise ValueError(
                f"No hay stock suficiente de {linea.producto.nombre}: "
                f"hay {disponible} y se intentan vender {linea.cantidad}."
            )

    fecha = timezone.localdate()
    venta.descuento_porcentaje = _descuento(venta.medio_pago, fecha)
    bruto = venta.subtotal()
    venta.total = (bruto * (Decimal("1") - venta.descuento_porcentaje)).quantize(
        Decimal("0.01")
    )
    venta.confirmada = True
    venta.save(update_fields=["descuento_porcentaje", "total", "confirmada"])

    for linea in lineas:
        Movimiento.objects.create(
            producto=linea.producto,
            cantidad=-linea.cantidad,
            tipo=TipoMovimiento.VENTA,
            usuario=venta.usuario,
            referencia=f"venta:{venta.pk}",
        )

    return venta
