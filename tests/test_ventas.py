"""Venta con varias lineas: el precio se congela y el stock sale del ledger.

Decisiones: el consumidor puede ser anonimo, y un juego es una venta con varias lineas
sin precio propio (D-13).
"""

import datetime as dt
from decimal import Decimal

import pytest

from catalogo.models import PrecioLista
from inventario.models import Movimiento
from ventas.models import Cliente, LineaVenta, MedioPago, Venta
from ventas.services import confirmar_venta

HOY = dt.date(2026, 3, 1)


@pytest.fixture
def con_precio(producto):
    PrecioLista.objects.create(
        producto=producto, valor=Decimal("10000"), vigente_desde=dt.date(2026, 1, 1)
    )
    return producto


@pytest.fixture
def stock(producto, usuario):
    Movimiento.objects.create(
        producto=producto, usuario=usuario, cantidad=10, tipo="entrada_compra"
    )
    return producto


def _venta(usuario, medio=MedioPago.EFECTIVO, cliente=None):
    return Venta.objects.create(usuario=usuario, medio_pago=medio, cliente=cliente)


def test_el_consumidor_puede_ser_anonimo(usuario, producto, usuario_stock=None):
    venta = _venta(usuario)
    assert venta.cliente is None


def test_venta_en_efectivo_descuenta_stock(usuario, stock):
    venta = _venta(usuario)
    LineaVenta.objects.create(
        venta=venta, producto=stock, cantidad=3, precio_unitario=Decimal("11000")
    )

    confirmar_venta(venta)

    assert venta.confirmada is True
    assert Movimiento.objects.get(tipo="venta").cantidad == -3


def test_un_juego_es_una_venta_con_varias_lineas(usuario, stock, tipo, producto):
    from catalogo.models import Producto

    mesa = Producto.objects.create(tipo=tipo, color="negro", alto_cm=75, ancho_cm=90, largo_cm=150)
    Movimiento.objects.create(producto=mesa, usuario=usuario, cantidad=2, tipo="entrada_compra")

    venta = _venta(usuario)
    LineaVenta.objects.create(
        venta=venta, producto=stock, cantidad=1, precio_unitario=Decimal("11000")
    )
    LineaVenta.objects.create(
        venta=venta, producto=mesa, cantidad=2, precio_unitario=Decimal("5000")
    )

    confirmar_venta(venta)

    assert venta.total == Decimal("21000.00")
    assert Movimiento.objects.filter(tipo="venta").count() == 2


def test_el_precio_se_congela_en_la_linea(usuario, stock):
    venta = _venta(usuario)
    linea = LineaVenta.objects.create(
        venta=venta, producto=stock, cantidad=1, precio_unitario=Decimal("11000")
    )
    confirmar_venta(venta)

    PrecioLista.objects.create(
        producto=stock, valor=Decimal("50000"), vigente_desde=dt.date(2026, 6, 1)
    )

    linea.refresh_from_db()
    venta.refresh_from_db()
    assert linea.precio_unitario == Decimal("11000")
    assert venta.total == Decimal("11000.00")


def test_no_se_puede_vender_mas_de_lo_que_hay(usuario, stock):
    venta = _venta(usuario)
    LineaVenta.objects.create(
        venta=venta, producto=stock, cantidad=11, precio_unitario=Decimal("11000")
    )

    with pytest.raises(ValueError, match="stock"):
        confirmar_venta(venta)

    assert Movimiento.objects.filter(tipo="venta").count() == 0


def test_una_venta_no_confirmada_no_mueve_stock(usuario, stock):
    venta = _venta(usuario)
    LineaVenta.objects.create(
        venta=venta, producto=stock, cantidad=1, precio_unitario=Decimal("11000")
    )

    assert venta.confirmada is False
    assert Movimiento.objects.filter(tipo="venta").count() == 0


def test_efectivo_aplica_el_descuento_del_parametro(usuario, stock):
    from core.models import Parametro

    Parametro.objects.create(
        clave="descuento_efectivo", valor={"porcentaje": 0.05}, vigente_desde=dt.date(2026, 1, 1)
    )
    venta = _venta(usuario, medio=MedioPago.EFECTIVO)
    LineaVenta.objects.create(
        venta=venta, producto=stock, cantidad=2, precio_unitario=Decimal("10000")
    )

    confirmar_venta(venta)

    assert venta.total == Decimal("19000.00")


def test_tarjeta_no_aplica_descuento(usuario, stock):
    from core.models import Parametro

    Parametro.objects.create(
        clave="descuento_efectivo", valor={"porcentaje": 0.05}, vigente_desde=dt.date(2026, 1, 1)
    )
    venta = _venta(usuario, medio=MedioPago.TARJETA)
    LineaVenta.objects.create(
        venta=venta, producto=stock, cantidad=2, precio_unitario=Decimal("10000")
    )

    confirmar_venta(venta)

    assert venta.total == Decimal("20000.00")


def test_cuenta_corriente_exige_cliente(usuario, stock):
    venta = _venta(usuario, medio=MedioPago.CUENTA_CORRIENTE)
    LineaVenta.objects.create(
        venta=venta, producto=stock, cantidad=1, precio_unitario=Decimal("1000")
    )

    with pytest.raises(ValueError, match="cliente"):
        confirmar_venta(venta)


def test_cuenta_corriente_exige_cliente_habilitado(usuario, stock):
    cliente = Cliente.objects.create(
        nombre="Ana", ciudad="Tres Lomas", habilitado_cuenta_corriente=False
    )
    venta = _venta(usuario, medio=MedioPago.CUENTA_CORRIENTE, cliente=cliente)
    LineaVenta.objects.create(
        venta=venta, producto=stock, cantidad=1, precio_unitario=Decimal("1000")
    )

    with pytest.raises(ValueError, match="habilitad"):
        confirmar_venta(venta)


def test_cuenta_corriente_con_cliente_habilitado_y_ciudad(usuario, stock):
    cliente = Cliente.objects.create(
        nombre="Ana", ciudad="Quenuma", habilitado_cuenta_corriente=True
    )
    venta = _venta(usuario, medio=MedioPago.CUENTA_CORRIENTE, cliente=cliente)
    LineaVenta.objects.create(
        venta=venta, producto=stock, cantidad=1, precio_unitario=Decimal("1000")
    )

    confirmar_venta(venta)

    assert venta.total == Decimal("1000.00")
    assert venta.cliente.ciudad == "Quenuma"


def test_una_venta_vacia_no_se_confirma(usuario):
    venta = _venta(usuario)

    with pytest.raises(ValueError, match="linea"):
        confirmar_venta(venta)


def test_no_se_puede_confirmar_dos_veces(usuario, stock):
    venta = _venta(usuario)
    LineaVenta.objects.create(
        venta=venta, producto=stock, cantidad=1, precio_unitario=Decimal("1000")
    )
    confirmar_venta(venta)

    with pytest.raises(ValueError, match="confirmada"):
        confirmar_venta(venta)

    assert Movimiento.objects.filter(tipo="venta").count() == 1
