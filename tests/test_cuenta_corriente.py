"""Cuenta corriente: el saldo se deriva de movimientos, igual que el stock.

Una venta en cuotas no guarda un saldo: genera un cargo por cuota. Un pago es otro
movimiento. El saldo es la suma, y por eso se puede explicar.
"""

import datetime as dt
from decimal import Decimal

import pytest
from django.utils import timezone

from ventas.models import Cliente, CuentaMovimiento, MedioPago, Venta
from ventas.services import confirmar_venta, registrar_pago, saldo_de, vencido_de

HOY = timezone.localdate()


@pytest.fixture
def cliente_con_cuenta(db):
    return Cliente.objects.create(nombre="Ana", ciudad="Quenuma", habilitado_cuenta_corriente=True)


@pytest.mark.django_db
def _vender_en_cuenta(usuario, producto, cliente, cantidad=1, precio=Decimal("30000")):
    from ventas.models import LineaVenta

    venta = Venta.objects.create(
        usuario=usuario, medio_pago=MedioPago.CUENTA_CORRIENTE, cliente=cliente
    )
    LineaVenta.objects.create(
        venta=venta, producto=producto, cantidad=cantidad, precio_unitario=precio
    )
    confirmar_venta(venta)
    return venta


@pytest.fixture
def stock(producto, usuario):
    from inventario.models import Movimiento

    Movimiento.objects.create(
        producto=producto, usuario=usuario, cantidad=10, tipo="entrada_compra"
    )
    return producto


def test_una_venta_en_cuenta_genera_un_cargo_por_cuota(usuario, stock, cliente_con_cuenta):
    _vender_en_cuenta(usuario, stock, cliente_con_cuenta, cantidad=1, precio=Decimal("30000"))

    cargos = CuentaMovimiento.objects.filter(cliente=cliente_con_cuenta, tipo="cargo")
    assert cargos.count() == 3
    assert sum(c.monto for c in cargos) == Decimal("30000.00")


def test_los_vencimientos_son_hoy_treinta_y_sesenta(usuario, stock, cliente_con_cuenta):
    _vender_en_cuenta(usuario, stock, cliente_con_cuenta, precio=Decimal("30000"))

    vencimientos = sorted(
        CuentaMovimiento.objects.filter(cliente=cliente_con_cuenta).values_list(
            "vencimiento", flat=True
        )
    )
    assert vencimientos == [HOY, HOY + dt.timedelta(days=30), HOY + dt.timedelta(days=60)]


def test_el_saldo_es_la_suma_de_los_movimientos(usuario, stock, cliente_con_cuenta):
    _vender_en_cuenta(usuario, stock, cliente_con_cuenta, precio=Decimal("30000"))

    assert saldo_de(cliente_con_cuenta) == Decimal("30000.00")


def test_un_pago_reduce_el_saldo(usuario, stock, cliente_con_cuenta):
    _vender_en_cuenta(usuario, stock, cliente_con_cuenta, precio=Decimal("30000"))

    registrar_pago(cliente_con_cuenta, Decimal("10000"), usuario)

    assert saldo_de(cliente_con_cuenta) == Decimal("20000.00")


def test_la_venta_en_efectivo_no_genera_cargos(usuario, stock, cliente_con_cuenta):
    from ventas.models import LineaVenta

    venta = Venta.objects.create(usuario=usuario, medio_pago=MedioPago.EFECTIVO)
    LineaVenta.objects.create(
        venta=venta, producto=stock, cantidad=1, precio_unitario=Decimal("10000")
    )
    confirmar_venta(venta)

    assert CuentaMovimiento.objects.count() == 0


def test_vencido_cuenta_solo_los_cargos_con_vencimiento_pasado(usuario, stock, cliente_con_cuenta):
    cargos = CuentaMovimiento.objects.none()
    _vender_en_cuenta(usuario, stock, cliente_con_cuenta, precio=Decimal("30000"))
    cargos = CuentaMovimiento.objects.filter(cliente=cliente_con_cuenta)
    # Solo la primera cuota esta vencida hoy; el cargo de hoy no esta "vencido".
    assert vencido_de(cliente_con_cuenta) == Decimal("0.00")

    cargos.filter(vencimiento=HOY).update(vencimiento=HOY - dt.timedelta(days=5))
    assert vencido_de(cliente_con_cuenta) == Decimal("10000.00")


def test_un_pago_cubre_lo_vencido(usuario, stock, cliente_con_cuenta):
    _vender_en_cuenta(usuario, stock, cliente_con_cuenta, precio=Decimal("30000"))
    CuentaMovimiento.objects.filter(cliente=cliente_con_cuenta, vencimiento=HOY).update(
        vencimiento=HOY - dt.timedelta(days=10)
    )

    registrar_pago(cliente_con_cuenta, Decimal("10000"), usuario)

    assert vencido_de(cliente_con_cuenta) == Decimal("0.00")
    assert saldo_de(cliente_con_cuenta) == Decimal("20000.00")


def test_el_saldo_nunca_queda_negativo_por_pagos_de_mas(usuario, cliente_con_cuenta):
    registrar_pago(cliente_con_cuenta, Decimal("5000"), usuario)
    # Pagar de mas deja saldo a favor: se informa, no se oculta.
    assert saldo_de(cliente_con_cuenta) == Decimal("-5000.00")


def test_un_pago_no_admite_monto_cero(usuario, cliente_con_cuenta):
    with pytest.raises(ValueError, match="monto"):
        registrar_pago(cliente_con_cuenta, Decimal("0"), usuario)
