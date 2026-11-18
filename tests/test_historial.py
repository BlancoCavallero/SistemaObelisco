"""Historial de movimientos de un producto.

Es la respuesta a "por que hay 3 y no 7": sin esta vista, el ajuste de conteo es un
numero magico y el sistema pierde credibilidad la primera vez que falta algo.
"""

import datetime as dt
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from inventario.models import Movimiento


@pytest.fixture
def cliente(usuario):
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


def _mov(producto, usuario, cantidad, tipo, cuando=None, motivo=""):
    kwargs = {"motivo": motivo}
    if cuando:
        kwargs["fecha"] = cuando
    return Movimiento.objects.create(
        producto=producto, usuario=usuario, cantidad=cantidad, tipo=tipo, **kwargs
    )


def test_historial_devuelve_los_movimientos_con_su_autor(cliente, usuario, producto):
    _mov(producto, usuario, 10, "entrada_compra")
    _mov(producto, usuario, -3, "venta")

    respuesta = cliente.get(f"/api/productos/{producto.pk}/movimientos/")

    assert respuesta.status_code == 200
    assert [m["cantidad"] for m in respuesta.data["movimientos"]] == [-3, 10]
    assert respuesta.data["movimientos"][0]["usuario"] == "diego"
    assert respuesta.data["total"] == 7


def test_el_historial_muestra_el_efecto_acumulado(cliente, usuario, producto):
    """Cada fila dice en cuanto quedo el stock despues de ese movimiento."""
    _mov(producto, usuario, 10, "entrada_compra")
    _mov(producto, usuario, -3, "venta")
    _mov(producto, usuario, -2, "ajuste", motivo="conteo: faltaban dos")

    respuesta = cliente.get(f"/api/productos/{producto.pk}/movimientos/")

    acumulados = [m["saldo_acumulado"] for m in respuesta.data["movimientos"]]
    assert acumulados == [5, 7, 10]


def test_el_historial_incluye_el_motivo_del_ajuste(cliente, usuario, producto):
    _mov(producto, usuario, 5, "entrada_compra")
    _mov(producto, usuario, -2, "ajuste", motivo="conteo fisico: dos rotos")

    respuesta = cliente.get(f"/api/productos/{producto.pk}/movimientos/")

    assert respuesta.data["movimientos"][0]["motivo"] == "conteo fisico: dos rotos"


def test_el_historial_respeta_el_orden_cronologico(cliente, usuario, producto):
    _mov(producto, usuario, 1, "entrada_compra", dt.datetime(2026, 1, 1, tzinfo=dt.UTC))
    _mov(producto, usuario, 2, "entrada_compra", dt.datetime(2026, 3, 1, tzinfo=dt.UTC))

    respuesta = cliente.get(f"/api/productos/{producto.pk}/movimientos/")

    assert [m["cantidad"] for m in respuesta.data["movimientos"]] == [2, 1]


def test_un_producto_sin_movimientos_devuelve_total_cero(cliente, producto):
    respuesta = cliente.get(f"/api/productos/{producto.pk}/movimientos/")

    assert respuesta.status_code == 200
    assert respuesta.data["movimientos"] == []
    assert respuesta.data["total"] == 0


def test_el_historial_requiere_sesion(producto):
    assert APIClient().get(f"/api/productos/{producto.pk}/movimientos/").status_code in (
        401,
        403,
    )


def test_producto_inexistente_devuelve_404(cliente):
    assert cliente.get("/api/productos/999999/movimientos/").status_code == 404


def test_una_venta_enlaza_la_referencia(cliente, usuario, producto):
    from ventas.models import LineaVenta, Venta
    from ventas.services import confirmar_venta

    _mov(producto, usuario, 10, "entrada_compra")
    venta = Venta.objects.create(usuario=usuario, medio_pago="efectivo")
    LineaVenta.objects.create(
        venta=venta, producto=producto, cantidad=2, precio_unitario=Decimal("1000")
    )
    confirmar_venta(venta)

    respuesta = cliente.get(f"/api/productos/{producto.pk}/movimientos/")

    venta_mov = next(m for m in respuesta.data["movimientos"] if m["tipo"] == "venta")
    assert venta_mov["referencia"] == f"venta:{venta.pk}"
