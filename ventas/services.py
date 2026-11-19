"""Confirming a sale: validate stock, freeze the total and move the ledger."""

import datetime as dt
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from catalogo.models import Producto
from core.models import Parametro
from inventario.models import Movimiento, TipoMovimiento
from inventario.stock import stock_de
from ventas.models import CuentaMovimiento, LineaVenta


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
    venta.total = (bruto * (Decimal("1") - venta.descuento_porcentaje)).quantize(Decimal("0.01"))
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

    if venta.medio_pago == "cuenta_corriente":
        _generar_cuotas(venta, fecha)

    return venta


def _cuotas_y_dias():
    cuotas = Parametro.valor_vigente("cuotas_cuenta_corriente") or {}
    return int(cuotas.get("cuotas", 3)), int(cuotas.get("dias_entre_cuotas", 30))


def _generar_cuotas(venta, fecha):
    """One charge per installment. The sum always equals the sale total."""
    cantidad_cuotas, dias = _cuotas_y_dias()
    monto_cuota = (venta.total / cantidad_cuotas).quantize(Decimal("0.01"))
    diferencia = venta.total - monto_cuota * cantidad_cuotas

    for numero in range(cantidad_cuotas):
        monto = monto_cuota + (diferencia if numero == cantidad_cuotas - 1 else Decimal("0"))
        CuentaMovimiento.objects.create(
            cliente=venta.cliente,
            tipo="cargo",
            monto=monto,
            vencimiento=fecha + dt.timedelta(days=dias * numero),
            venta=venta,
            usuario=venta.usuario,
            motivo=f"Cuota {numero + 1} de {cantidad_cuotas}",
        )


def saldo_de(cliente):
    """What the customer owes today. Negative means credit in their favour."""
    montos = CuentaMovimiento.objects.filter(cliente=cliente).aggregate(
        cargos=Sum("monto", filter=models_q("tipo", "cargo")),
        pagos=Sum("monto", filter=models_q("tipo", "pago")),
        ajustes=Sum("monto", filter=models_q("tipo", "ajuste")),
    )
    cargos = montos["cargos"] or Decimal("0.00")
    pagos = montos["pagos"] or Decimal("0.00")
    ajustes = montos["ajustes"] or Decimal("0.00")
    return (cargos - pagos - ajustes).quantize(Decimal("0.01"))


def models_q(campo, valor):
    from django.db.models import Q

    return Q(**{campo: valor})


def vencido_de(cliente):
    """Overdue part of the balance.

    Simplification, on purpose: payments are not imputed to a specific installment,
    they reduce the overdue amount in order of age. Per-installment imputation needs
    the payment-allocation rule the business has not defined yet.
    """
    hoy = timezone.localdate()
    vencidos = CuentaMovimiento.objects.filter(
        cliente=cliente, tipo="cargo", vencimiento__lt=hoy
    ).aggregate(total=Sum("monto"))["total"] or Decimal("0.00")

    pagado = CuentaMovimiento.objects.filter(cliente=cliente, tipo="pago").aggregate(
        total=Sum("monto")
    )["total"] or Decimal("0.00")

    vencido = vencidos - pagado
    return vencido.quantize(Decimal("0.01")) if vencido > 0 else Decimal("0.00")


def registrar_pago(cliente, monto, usuario, motivo=""):
    monto = Decimal(str(monto)).quantize(Decimal("0.01"))
    if monto <= 0:
        raise ValueError("El monto de un pago debe ser mayor a cero.")
    return CuentaMovimiento.objects.create(
        cliente=cliente, tipo="pago", monto=monto, usuario=usuario, motivo=motivo
    )


def unidades_sin_entregar():
    """Unidades ya vendidas que siguen fisicamente en el deposito, por producto.

    La venta descuenta cuando se confirma (D-07); la mercaderia sale cuando se marca la
    entrega. Hasta entonces el ledger dice "disponible" y el piso dice "esta aca": el
    conteo tiene que comparar contra el piso, no contra lo disponible, o convierte el
    conteo en stock vendible que ya esta vendido.
    """
    return {
        fila["producto"]: fila["total"]
        for fila in LineaVenta.objects.filter(venta__confirmada=True, entregada=False)
        .values("producto")
        .annotate(total=Sum("cantidad"))
    }


@transaction.atomic
def marcar_entrega(venta):
    """La entrega es logistica: no toca el ledger. Devuelve cuantas lineas cerro.

    Toma el lock del producto, el mismo que usa el conteo para leer las pendientes: sin el,
    una entrega que commitea en el medio del conteo deja al conteo con pendientes viejas y
    el 409 no las ve.
    """
    if not venta.confirmada:
        raise ValueError("Una venta sin confirmar no se entrega.")

    ids = sorted(set(venta.lineas.values_list("producto_id", flat=True)))
    list(Producto.objects.select_for_update().filter(pk__in=ids).order_by("pk"))
    return venta.lineas.filter(entregada=False).update(entregada=True)
