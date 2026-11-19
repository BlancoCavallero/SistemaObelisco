"""Entregar: la venta descuenta al confirmar, la entrega es logistica (D-07).

Mientras la mercaderia vendida sigue en el deposito, el sistema dice una cosa y el piso
otra. Marcar la entrega cierra esa brecha, y es lo que hace que el conteo pueda restar lo
vendido: sin eso, contar lo que hay crea stock vendible que ya esta vendido y esas
unidades se pueden vender dos veces.
"""

import datetime as dt
import importlib
from decimal import Decimal

import pytest
from django.apps import apps as registro
from django.db import migrations
from rest_framework.test import APIClient

from catalogo.models import PrecioLista
from inventario.models import Movimiento
from ventas.models import LineaVenta, Venta


@pytest.fixture
def cliente(usuario):
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


@pytest.fixture
def con_stock_y_precio(producto, usuario):
    PrecioLista.objects.create(
        producto=producto, valor=Decimal("10000"), vigente_desde=dt.date(2026, 1, 1)
    )
    Movimiento.objects.create(
        producto=producto, usuario=usuario, cantidad=5, tipo="entrada_compra"
    )
    return producto


def _vender(cliente, producto, cantidad=2):
    respuesta = cliente.post(
        "/api/ventas/",
        {"medio_pago": "efectivo", "lineas": [{"producto": producto.pk, "cantidad": cantidad}]},
        format="json",
    )
    assert respuesta.status_code == 201, respuesta.data
    return respuesta.data["id"]


def test_marcar_la_entrega_no_mueve_el_stock(cliente, con_stock_y_precio):
    """La entrega es logistica: el numero ya lo movio la venta (D-07)."""
    venta = _vender(cliente, con_stock_y_precio, 2)

    respuesta = cliente.post(f"/api/ventas/{venta}/entregar/", {}, format="json")

    assert respuesta.status_code == 200
    assert respuesta.data == {"venta": venta, "lineas": 1}
    assert Venta.objects.get(pk=venta).lineas.get().entregada is True
    assert Movimiento.objects.filter(producto=con_stock_y_precio).count() == 2


def test_las_pendientes_listan_solo_lo_no_entregado(cliente, con_stock_y_precio):
    primera = _vender(cliente, con_stock_y_precio, 1)
    segunda = _vender(cliente, con_stock_y_precio, 2)
    cliente.post(f"/api/ventas/{primera}/entregar/", {}, format="json")

    respuesta = cliente.get("/api/ventas/pendientes/")

    assert respuesta.status_code == 200
    assert [v["id"] for v in respuesta.data["ventas"]] == [segunda]
    assert respuesta.data["ventas"][0]["lineas"][0]["cantidad"] == 2


def test_no_se_entrega_una_venta_sin_confirmar(cliente, usuario, producto):
    sin_confirmar = Venta.objects.create(usuario=usuario, medio_pago="efectivo")

    respuesta = cliente.post(f"/api/ventas/{sin_confirmar.pk}/entregar/", {}, format="json")

    assert respuesta.status_code == 400
    assert "detail" in respuesta.data


def test_entregar_dos_veces_no_cambia_nada(cliente, con_stock_y_precio):
    venta = _vender(cliente, con_stock_y_precio, 2)
    cliente.post(f"/api/ventas/{venta}/entregar/", {}, format="json")

    respuesta = cliente.post(f"/api/ventas/{venta}/entregar/", {}, format="json")

    assert respuesta.status_code == 200
    assert respuesta.data["lineas"] == 0
    assert Venta.objects.get(pk=venta).lineas.get().entregada is True


def test_entregar_una_venta_que_no_existe(cliente, usuario):
    respuesta = cliente.post("/api/ventas/9999/entregar/", {}, format="json")

    assert respuesta.status_code == 404



# --- la columna nueva no puede dejar todo lo vendido como pendiente -----------


def _marcar_historicas():
    """Corre la funcion de datos de la migracion con el registry real de modelos."""
    modulo = importlib.import_module("ventas.migrations.0003_lineaventa_entregada")
    operacion = next(
        op for op in modulo.Migration.operations if isinstance(op, migrations.RunPython)
    )
    return operacion.code(registro, None)


def _linea(usuario, producto, cantidad, confirmada=True):
    venta = Venta.objects.create(usuario=usuario, medio_pago="efectivo", confirmada=confirmada)
    return LineaVenta.objects.create(
        venta=venta, producto=producto, cantidad=cantidad, precio_unitario="10000"
    )


def test_la_migracion_marca_lo_ya_vendido_como_entregado(usuario, producto):
    """`default=False` solo vale para lo nuevo: lo historico ya salio del deposito.

    Sin esto, en una base desplegada cada venta vieja se suma al fisico del conteo y un
    conteo real escribe un ajuste negativo que borra stock.
    """
    historica = _linea(usuario, producto, 2)

    _marcar_historicas()

    assert LineaVenta.objects.get(pk=historica.pk).entregada is True


def test_una_linea_creada_despues_de_la_migracion_sigue_pendiente(usuario, producto):
    _marcar_historicas()

    nueva = _linea(usuario, producto, 1)

    assert LineaVenta.objects.get(pk=nueva.pk).entregada is False


def test_un_borrador_no_se_marca_entregado(usuario, producto):
    """Un borrador que se confirme despues tiene que seguir contando como pendiente."""
    borrador = _linea(usuario, producto, 1, confirmada=False)

    _marcar_historicas()

    assert LineaVenta.objects.get(pk=borrador.pk).entregada is False
